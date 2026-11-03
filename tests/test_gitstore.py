"""Exercise real Git bundles, pinned trees, paths and offline behavior."""
from pathlib import Path
import tempfile
import unittest

from skillfleet.catalog import skill_name
from skillfleet.gitstore import GitStore, git, github_url
from skillfleet.storage import FleetError, relative_path


class GitStoreTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        base = Path(self.temp.name)
        self.source = base / "source"
        git("init", "--initial-branch=main", str(self.source))
        git("config", "user.name", "Test", cwd=self.source)
        git("config", "user.email", "test@example.invalid", cwd=self.source)
        git("config", "core.autocrlf", "false", cwd=self.source)
        directory = self.source / "skills/example"
        directory.mkdir(parents=True)
        (directory / "SKILL.md").write_bytes(b"---\nname: example\ndescription:\n  A multiline description.\n---\nGuidance.\n")
        (directory / "references").mkdir()
        (directory / "references/read.md").write_bytes(b"Read this reference.\n")
        (directory / "asset.bin").write_bytes(b"\0\nbinary\xff\n")
        (self.source / "LICENSE").write_bytes(b"MIT fixture license.\n")
        self.store = GitStore(base / "cache", offline=True)
        self.url = "https://github.com/example/skills.git"
        self.commit()

    def commit(self):
        git("add", ".", cwd=self.source)
        git("commit", "--allow-empty", "-m", "Fixture", cwd=self.source)
        self.store.cache.mkdir(exist_ok=True)
        repo = self.store.repository(self.url)
        if repo.exists():
            git("fetch", str(self.source), "main", cwd=repo)
        else:
            git("clone", "--bare", str(self.source), str(repo))
        commit = git("rev-parse", "HEAD", cwd=self.source).decode().strip()
        self.spec = {"url": self.url, "commit": commit, "path": "skills/example",
                     "tree": git("rev-parse", "HEAD:skills/example", cwd=self.source).decode().strip(),
                     "license_paths": ["LICENSE"]}

    def test_complete_bundle_and_root_license_are_retained(self):
        files = self.store.bundle(self.spec)
        self.assertEqual("example", skill_name(files))
        self.assertIn("references/read.md", files)
        self.assertEqual(b"\0\nbinary\xff\n", files["asset.bin"])
        self.assertEqual(b"MIT fixture license.\n", files[".skillfleet-licenses/LICENSE"])

    def test_tampered_tree_is_rejected(self):
        with self.assertRaisesRegex(FleetError, "tree mismatch"):
            self.store.bundle({**self.spec, "tree": "0" * 40})

    def test_symlink_bundle_is_rejected(self):
        link = self.source / "skills/example/reference-link"
        try:
            link.symlink_to("references/read.md")
        except OSError:
            self.skipTest("OS does not allow test symlinks")
        self.commit()
        with self.assertRaisesRegex(FleetError, "symlink or submodule"):
            self.store.bundle(self.spec)

    def test_offline_never_fetches_an_uncached_commit(self):
        with self.assertRaisesRegex(FleetError, "not cached"):
            self.store.ensure(self.url, "0" * 40)

    def test_offline_missing_blobs_fail_without_lazy_fetch(self):
        blob = git("rev-parse", "HEAD:skills/example/references/read.md", cwd=self.source).decode().strip()
        repo = self.store.repository(self.url)
        object_path = repo / "objects" / blob[:2] / blob[2:]
        self.assertTrue(object_path.is_file())
        object_path.chmod(0o600)
        object_path.unlink()
        with self.assertRaisesRegex(FleetError, "uncached blobs"):
            self.store.bundle(self.spec)

    def test_sources_must_be_credential_free_github_https(self):
        for url in ("file:///tmp/source", "https://example.com/repo.git", "https://token@github.com/a/b.git", "-x"):
            with self.subTest(url=url), self.assertRaises(FleetError):
                github_url(url)

    def test_nonportable_and_traversal_paths_are_rejected(self):
        for path in ("../secret", "/tmp/secret", "a/../../b", "a\\b", "a/NUL.txt", "a:ref", "a/file?", "a/line\nbreak"):
            with self.subTest(path=path), self.assertRaises(FleetError):
                relative_path(path)


if __name__ == "__main__":
    unittest.main()
