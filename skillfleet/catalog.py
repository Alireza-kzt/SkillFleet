"""Shared catalog and immutable upstream version records."""
from __future__ import annotations

from pathlib import Path
import re

from .gitstore import GitStore, commit_sha, github_url, git
from .storage import FleetError, atomic_write, digest, encoded, identifier, read_json, relative_path


def local_bundle(root: Path, relative: str) -> dict[str, bytes]:
    directory = root / relative_path(relative)
    if not directory.is_dir() or directory.is_symlink():
        raise FleetError(f"Missing local skill directory: {directory}")
    files = {}
    for path in sorted(directory.rglob("*")):
        if path.is_symlink():
            raise FleetError(f"Skill contains a symlink: {path}")
        if path.is_file():
            name = relative_path(path.relative_to(directory).as_posix())
            files[name] = path.read_bytes()
    return files


def bundle_digest(files: dict[str, bytes]) -> str:
    return digest(encoded({name: digest(value) for name, value in sorted(files.items())}))


def skill_name(files: dict[str, bytes]) -> str:
    try:
        text = files["SKILL.md"].decode("utf-8-sig")
    except (KeyError, UnicodeDecodeError) as exc:
        raise FleetError("Skill needs a UTF-8 SKILL.md.") from exc
    # Deliberately not a general YAML parser. Read only the standard scalar name;
    # the complete YAML remains untouched for the agent's native skill loader.
    match = re.match(r"---\r?\n(.*?)\r?\n---(?:\r?\n|$)", text, re.S)
    if not match:
        raise FleetError("SKILL.md needs YAML frontmatter.")
    name = re.search(r"^name:\s*['\"]?([a-z0-9]+(?:-[a-z0-9]+)*)['\"]?\s*$", match[1], re.M)
    if not name or not re.search(r"^description:\s*\S", match[1], re.M):
        raise FleetError("SKILL.md needs a scalar name and a nonempty description.")
    return identifier(name[1])


class Catalog:
    def __init__(self, root: Path):
        self.root = root
        self.data = read_json(root / "registry/catalog.json")
        self.lock_path = root / "registry/catalog.lock.json"

    def validate(self) -> None:
        for source_id, source in self.data["sources"].items():
            identifier(source_id)
            github_url(source["url"])
            if not source.get("ref"):
                raise FleetError(f"Source has no branch: {source_id}")
        names = set()
        for key, spec in self.data["skills"].items():
            identifier(key)
            relative_path(spec["path"])
            if spec.get("source") not in {*self.data["sources"], "builtin"}:
                raise FleetError(f"Unknown source for {key}")
            if not spec.get("description") or not spec.get("license"):
                raise FleetError(f"Missing catalog metadata: {key}")
            if spec.get("source") == "builtin":
                actual = skill_name(local_bundle(self.root, spec["path"]))
                if actual != key:
                    raise FleetError(f"Skill name differs from catalog ID: {key} != {actual}")
            for license_path in spec.get("license_paths", []):
                relative_path(license_path)
            names.add(key)
        for profile, spec in self.data["profiles"].items():
            identifier(profile)
            unknown = set(spec["skills"]) - names
            if unknown:
                raise FleetError(f"Unknown skills in {profile}: {sorted(unknown)}")

    def selected(self, manifest: dict) -> list[str]:
        profiles = manifest.get("profiles", [])
        ids = list(manifest.get("skills", []))
        for profile in ([] if manifest.get("selection_mode") == "explicit" else ["core", *profiles]):
            if profile not in self.data["profiles"]:
                raise FleetError(f"Unknown profile: {profile}")
            ids.extend(self.data["profiles"][profile]["skills"])
        ids = sorted(set(ids) - set(manifest.get("exclude", [])))
        unknown = set(ids) - self.data["skills"].keys()
        if unknown:
            raise FleetError(f"Unknown skills: {', '.join(sorted(unknown))}")
        return ids

    def validate_lock(self, lock: dict) -> None:
        if set(lock["skills"]) != set(self.data["skills"]):
            raise FleetError("Catalog and lock contain different skills. Refresh the catalog lock.")
        for key, current in self.data["skills"].items():
            spec = lock["skills"][key]
            if spec["path"] != current["path"] or spec["source"] != current["source"]:
                raise FleetError(f"Stale catalog lock: {key}")
            if spec["source"] == "builtin":
                if bundle_digest(local_bundle(self.root, spec["path"])) != spec["digest"]:
                    raise FleetError(f"Local skill changed without lock refresh: {key}")
            else:
                commit_sha(spec["commit"])
                commit_sha(spec["tree"])
                if spec["url"] != self.data["sources"][spec["source"]]["url"]:
                    raise FleetError(f"Source URL differs from catalog: {key}")

    def lock(self) -> dict:
        lock = read_json(self.lock_path)
        self.validate_lock(lock)
        return lock

    def refresh(self, store: GitStore) -> dict:
        self.validate()
        sources = {}
        for key, source in self.data["sources"].items():
            sources[key] = {**source, "commit": store.head(source["url"], source["ref"])}
        skills = {}
        for key, spec in self.data["skills"].items():
            base = {k: spec[k] for k in ("source", "path", "license", "license_paths") if k in spec}
            if spec["source"] == "builtin":
                base["digest"] = bundle_digest(local_bundle(self.root, spec["path"]))
            else:
                source = sources[spec["source"]]
                base.update({k: source[k] for k in ("url", "ref", "commit")})
                base["tree"] = store.tree(source["url"], source["commit"], spec["path"])
            skills[key] = base
        lock = {"schema": 1, "sources": sources, "skills": skills}
        atomic_write(self.lock_path, encoded(lock))
        return lock

    def check(self, store: GitStore, lock: dict | None = None) -> dict:
        pins = lock if lock is not None else self.lock()
        sources = {}
        for skill in pins["skills"].values():
            if skill["source"] != "builtin":
                sources[(skill["url"], skill["ref"])] = skill["commit"]
        result = []
        for (url, ref), old in sorted(sources.items()):
            new = store.head(url, ref)
            result.append({"url": url, "ref": ref, "pinned": old, "latest": new, "changed": old != new,
                           "compare": f"{url[:-4]}/compare/{old}...{new}"})
        return {"schema": 1, "updates": result}

    def project_spec(self, key: str, lock: dict) -> dict:
        spec = dict(lock["skills"][key])
        if spec["source"] == "builtin":
            if git("status", "--porcelain", "--", spec["path"], cwd=self.root):
                raise FleetError(f"Commit local skill changes before connecting projects: {key}")
            try:
                commit = git("rev-parse", "HEAD", cwd=self.root).decode().strip()
            except FleetError as exc:
                raise FleetError("Commit the SkillFleet checkout before connecting projects.") from exc
            spec.update(url=self.data.get("repository", "https://github.com/Alireza-kzt/SkillFleet.git"), commit=commit,
                        tree=git("rev-parse", f"{commit}:{spec['path']}", cwd=self.root).decode().strip(),
                        ref="main")
        return spec

    def materialize(self, key: str, spec: dict, store: GitStore) -> dict[str, bytes]:
        if spec["source"] == "builtin":
            local = local_bundle(self.root, spec["path"])
            if bundle_digest(local) == spec["digest"]:
                files = local
            else:
                files = store.bundle(spec)
                if bundle_digest(files) != spec["digest"]:
                    raise FleetError(f"Built-in skill integrity mismatch: {key}")
        else:
            files = store.bundle(spec)
        if skill_name(files) != key:
            raise FleetError(f"Skill name does not match installation directory: {key}")
        return files
