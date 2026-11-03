"""Fetch pinned Git data without checkout, hooks, or upstream code execution."""
from __future__ import annotations

import os
from pathlib import Path
import re
import subprocess

from .storage import FleetError, digest, mutex, relative_path

SHA = re.compile(r"[a-f0-9]{40}\Z")
MAX_BUNDLE = 64 * 1024 * 1024


def github_url(url: str) -> str:
    if not isinstance(url, str) or not re.fullmatch(
        r"https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+\.git", url
    ):
        raise FleetError(f"Only credential-free GitHub HTTPS source URLs are supported: {url!r}")
    return url


def commit_sha(value: str) -> str:
    if not isinstance(value, str) or not SHA.fullmatch(value):
        raise FleetError(f"Expected a full 40-character commit SHA: {value!r}")
    return value


def git(*arguments: str, cwd: Path | None = None, offline: bool = False, input: bytes | None = None) -> bytes:
    environment = {**os.environ, "GIT_TERMINAL_PROMPT": "0"}
    if offline:
        environment["GIT_NO_LAZY_FETCH"] = "1"
    try:
        result = subprocess.run(
            ["git", "-c", "core.hooksPath=", *arguments], cwd=cwd, env=environment,
            capture_output=True, timeout=60, check=False, input=input,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise FleetError(f"Git could not finish: {exc}") from exc
    if result.returncode:
        message = result.stderr.decode(errors="replace").strip()
        raise FleetError(f"Git failed: {message}")
    return result.stdout


class GitStore:
    def __init__(self, cache: Path, offline: bool = False):
        self.cache = cache
        self.offline = offline

    def repository(self, url: str) -> Path:
        github_url(url)
        return self.cache / (digest(url.encode())[:24] + ".git")

    def head(self, url: str, ref: str) -> str:
        github_url(url)
        if self.offline:
            raise FleetError("Remote checks need network access; omit --offline.")
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_./-]*", ref) or ".." in ref:
            raise FleetError(f"Unsafe source branch: {ref!r}")
        output = git("ls-remote", "--exit-code", url, f"refs/heads/{ref}").decode().split()
        if not output:
            raise FleetError(f"Source branch not found: {url} {ref}")
        return commit_sha(output[0])

    def ensure(self, url: str, commit: str) -> Path:
        commit_sha(commit)
        repo = self.repository(url)
        if repo.exists():
            try:
                git("cat-file", "-e", f"{commit}^{{commit}}", cwd=repo)
                return repo
            except FleetError:
                pass
        if self.offline:
            raise FleetError(f"Pinned source is not cached: {url}@{commit[:12]}")
        self.cache.mkdir(parents=True, exist_ok=True)
        with mutex(self.cache / (repo.name + ".lock")):
            if not repo.exists():
                git("init", "--bare", str(repo))
                git("config", "remote.origin.url", url, cwd=repo)
                git("config", "remote.origin.promisor", "true", cwd=repo)
                git("config", "remote.origin.partialclonefilter", "blob:none", cwd=repo)
            git("fetch", "--no-tags", "--depth=1", "--filter=blob:none", "origin", commit, cwd=repo)
            git("cat-file", "-e", f"{commit}^{{commit}}", cwd=repo)
        return repo

    def tree(self, url: str, commit: str, path: str) -> str:
        relative_path(path)
        repo = self.ensure(url, commit)
        kind = git("cat-file", "-t", f"{commit}:{path}", cwd=repo).decode().strip()
        if kind != "tree":
            raise FleetError(f"Skill directory not found at pinned commit: {path}")
        return git("rev-parse", f"{commit}:{path}", cwd=repo).decode().strip()

    def bundle(self, spec: dict) -> dict[str, bytes]:
        url, commit, path = spec["url"], spec["commit"], relative_path(spec["path"])
        repo = self.ensure(url, commit)
        if self.tree(url, commit, path) != spec["tree"]:
            raise FleetError(f"Pinned tree mismatch: {path}")
        listing = git("ls-tree", "-r", "-z", f"{commit}:{path}", cwd=repo, offline=self.offline)
        names = {}
        for record in filter(None, listing.split(b"\0")):
            metadata, name = record.split(b"\t", 1)
            mode, kind, sha = metadata.split()
            if mode not in {b"100644", b"100755"} or kind != b"blob":
                raise FleetError(f"Skill contains a symlink or submodule: {path}")
            names[relative_path(name.decode("utf-8"))] = sha
        licenses = spec.get("license_paths", [])
        for item in licenses:
            relative_path(item)
        if licenses:
            records = git("ls-tree", "-z", commit, "--", *licenses, cwd=repo, offline=self.offline)
            found = set()
            for record in filter(None, records.split(b"\0")):
                metadata, name = record.split(b"\t", 1)
                mode, kind, sha = metadata.split()
                if mode not in {b"100644", b"100755"} or kind != b"blob":
                    raise FleetError("License path is not a regular file.")
                original = relative_path(name.decode("utf-8"))
                found.add(original)
                if not original.startswith(path + "/"):
                    names[".skillfleet-licenses/" + original.replace("/", "_")] = sha
            if found != set(licenses):
                raise FleetError(f"Missing pinned license file: {sorted(set(licenses) - found)}")
        object_input = b"\n".join(sorted(set(names.values()))) + b"\n"
        # Fetch only this bundle's missing blobs, in one round trip.
        def object_info():
            return git("cat-file", "--batch-check", cwd=repo, offline=True, input=object_input).splitlines()
        missing = [row.split()[0] for row in object_info() if row.endswith(b" missing")]
        if missing:
            if self.offline:
                raise FleetError(f"Pinned bundle has uncached blobs: {path}")
            with mutex(self.cache / (repo.name + ".lock")):
                git("fetch", "--no-tags", "--no-write-fetch-head", "--stdin", "origin", cwd=repo,
                    input=b"\n".join(missing) + b"\n")
        sizes = object_info()
        if any(row.endswith(b" missing") for row in sizes):
            raise FleetError(f"Pinned bundle has missing Git objects: {path}")
        object_sizes = {row.split()[0]: int(row.split()[2]) for row in sizes}
        if sum(object_sizes[sha] for sha in names.values()) > MAX_BUNDLE:
            raise FleetError(f"Skill exceeds 64 MiB bundle limit: {path}")
        # Read raw blobs, not git archive: export attributes must not omit files
        # or cause hidden attribute fetches in a partial clone.
        response = git("cat-file", "--batch", cwd=repo, offline=True, input=object_input)
        blobs = {}
        offset = 0
        for sha in sorted(set(names.values())):
            end = response.index(b"\n", offset)
            header = response[offset:end].split()
            size = object_sizes[sha]
            if header != [sha, b"blob", str(size).encode()]:
                raise FleetError("Unexpected Git blob response.")
            blobs[sha] = response[end + 1:end + 1 + size]
            if len(blobs[sha]) != size or response[end + 1 + size:end + 2 + size] != b"\n":
                raise FleetError("Truncated Git blob response.")
            offset = end + size + 2
        if offset != len(response):
            raise FleetError("Unexpected trailing Git blob data.")
        files = {name: blobs[sha] for name, sha in names.items()}
        if "SKILL.md" not in files:
            raise FleetError(f"Missing SKILL.md: {path}")
        return files
