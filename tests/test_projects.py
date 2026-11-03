"""Real filesystem/Git tests for the operations most likely to lose user work."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from skillfleet.catalog import Catalog, bundle_digest, local_bundle
from skillfleet.cli import main
from skillfleet.gitstore import GitStore, git
from skillfleet import project
from skillfleet.storage import FleetError, encoded, read_json, recover, rollback, transaction


class ProjectTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.catalog_root = self.base / "central"
        self.catalog_root.mkdir()
        self.root = self.base / "application"
        self.root.mkdir()
        self.store = GitStore(self.base / "cache", offline=True)
        git("init", "--initial-branch=main", str(self.catalog_root))
        git("config", "user.name", "Test", cwd=self.catalog_root)
        git("config", "user.email", "test@example.invalid", cwd=self.catalog_root)
        git("config", "core.autocrlf", "false", cwd=self.catalog_root)
        self.data = {"schema": 1, "sources": {}, "skills": {}, "profiles": {
            "core": {"skills": ["alpha"], "description": "Core"},
            "extra": {"skills": ["beta"], "description": "Extra"}}}
        for name in ("alpha", "beta"):
            self.data["skills"][name] = {"source": "builtin", "path": f"skills/{name}",
                                         "description": name, "license": "MIT"}
            directory = self.catalog_root / "skills" / name
            directory.mkdir(parents=True)
            (directory / "SKILL.md").write_text(f"---\nname: {name}\ndescription: A real test skill.\n---\n\nVersion one.\n")
            (directory / "references").mkdir()
            (directory / "references" / "detail.md").write_text("Keep complete references.\n")
        (self.catalog_root / "registry").mkdir()
        self.save_catalog()
        self.config = {"schema": 1, "profiles": ["core"], "skills": ["alpha"], "exclude": [],
                       "selection_mode": "explicit", "agents": ["codex"]}

    def save_catalog(self):
        (self.catalog_root / "registry/catalog.json").write_bytes(encoded(self.data))
        lock = {"schema": 1, "sources": {}, "skills": {}}
        for name, spec in self.data["skills"].items():
            lock["skills"][name] = {k: spec[k] for k in ("source", "path", "license")}
            lock["skills"][name]["digest"] = bundle_digest(local_bundle(self.catalog_root, spec["path"]))
        (self.catalog_root / "registry/catalog.lock.json").write_bytes(encoded(lock))
        git("add", ".", cwd=self.catalog_root)
        git("commit", "--allow-empty", "-m", "Fixture version", cwd=self.catalog_root)
        self.catalog = Catalog(self.catalog_root)

    def connect(self):
        target = project.resolve(self.catalog, self.config, None)
        return project.install(self.root, self.catalog, self.store, target, None, encoded(self.config))

    def test_complete_install_and_idempotent_restore(self):
        lock = self.connect()
        self.assertTrue((self.root / ".agents/skills/alpha/references/detail.md").is_file())
        before = (self.root / "skillfleet.lock.json").read_bytes()
        project.sync(self.root, self.catalog, self.store)
        self.assertEqual(before, (self.root / "skillfleet.lock.json").read_bytes())
        self.assertEqual([], project.problems(self.root, lock))
        self.assertEqual(1, (self.root / "AGENTS.md").read_text().count(project.BEGIN))

    def test_existing_instructions_are_preserved_byte_for_byte(self):
        original = "# Our rules\r\n\r\nمتن فارسی\r\n".encode()
        (self.root / "AGENTS.md").write_bytes(original)
        self.connect()
        self.assertTrue((self.root / "AGENTS.md").read_bytes().startswith(original))
        with (self.root / "AGENTS.md").open("ab") as stream:
            stream.write(b"\nA later project-specific instruction.\n")
        project.sync(self.root, self.catalog, self.store)
        self.assertIn("later project-specific", (self.root / "AGENTS.md").read_text())

    def test_modified_skill_is_never_overwritten(self):
        self.connect()
        path = self.root / ".agents/skills/alpha/SKILL.md"
        path.write_text("A local customization")
        with self.assertRaisesRegex(FleetError, "Modified"):
            project.sync(self.root, self.catalog, self.store)
        self.assertEqual("A local customization", path.read_text())

    def test_untracked_managed_directory_file_is_preserved(self):
        self.connect()
        path = self.root / ".agents/skills/alpha/notes.txt"
        path.write_text("User work")
        with self.assertRaisesRegex(FleetError, "Untracked"):
            project.sync(self.root, self.catalog, self.store)
        self.assertEqual("User work", path.read_text())

    def test_unmanaged_collision_is_not_adopted(self):
        path = self.root / ".agents/skills/alpha"
        path.mkdir(parents=True)
        (path / "custom.txt").write_text("User work")
        with self.assertRaisesRegex(FleetError, "not managed"):
            self.connect()
        self.assertFalse((self.root / "skillfleet.json").exists())

    def test_add_and_remove_only_managed_skill_files(self):
        old = self.connect()
        other = self.root / ".agents/skills/user-owned"
        other.mkdir()
        (other / "SKILL.md").write_text("User skill")
        self.config["skills"] = ["beta"]
        target = project.resolve(self.catalog, self.config, old)
        project.install(self.root, self.catalog, self.store, target, old, encoded(self.config))
        self.assertFalse((self.root / ".agents/skills/alpha/SKILL.md").exists())
        self.assertTrue((self.root / ".agents/skills/beta/SKILL.md").is_file())
        self.assertEqual("User skill", (other / "SKILL.md").read_text())

    def test_central_changes_do_not_update_a_project_on_sync(self):
        original = self.connect()
        old_file = (self.root / ".agents/skills/alpha/SKILL.md").read_bytes()
        (self.catalog_root / "skills/alpha/SKILL.md").write_text("---\nname: alpha\ndescription: Test.\n---\nVersion two.\n")
        self.save_catalog()
        # Seed the old central commit so exact restoration works without network.
        url = original["skills"]["alpha"]["url"]
        git("clone", "--bare", str(self.catalog_root), str(self.store.repository(url)))
        restored = project.sync(self.root, self.catalog, self.store)
        self.assertEqual(original["skills"], restored["skills"])
        self.assertEqual(old_file, (self.root / ".agents/skills/alpha/SKILL.md").read_bytes())

    def test_profile_changes_do_not_change_frozen_selection(self):
        self.connect()
        self.data["profiles"]["core"]["skills"].append("beta")
        self.save_catalog()
        restored = project.sync(self.root, self.catalog, self.store)
        self.assertEqual(["alpha"], sorted(restored["skills"]))

    def test_review_apply_and_rollback(self):
        self.connect()
        before = (self.root / ".agents/skills/alpha/SKILL.md").read_bytes()
        path = self.catalog_root / "skills/alpha/SKILL.md"
        path.write_text(path.read_text().replace("Version one", "Version two"))
        self.save_catalog()
        proposal = project.propose(self.root, self.catalog, self.store)
        self.assertIn(".agents/skills/alpha/SKILL.md", proposal["changed_files"])
        self.assertEqual(before, (self.root / ".agents/skills/alpha/SKILL.md").read_bytes())
        project.apply_proposal(self.root, self.catalog, self.store)
        self.assertIn("Version two", (self.root / ".agents/skills/alpha/SKILL.md").read_text())
        rollback(self.root)
        self.assertEqual(before, (self.root / ".agents/skills/alpha/SKILL.md").read_bytes())

    def test_stale_update_is_rejected(self):
        self.connect()
        project.propose(self.root, self.catalog, self.store)
        self.config["exclude"] = ["alpha"]
        (self.root / "skillfleet.json").write_bytes(encoded(self.config))
        with self.assertRaisesRegex(FleetError, "changed after review"):
            project.apply_proposal(self.root, self.catalog, self.store)

    def test_tampered_proposal_hashes_are_rejected(self):
        self.connect()
        value = project.propose(self.root, self.catalog, self.store)
        value["target"]["installed"][".skillfleet/INSTRUCTIONS.md"] = "0" * 64
        (self.root / ".skillfleet/proposal.json").write_bytes(encoded(value))
        with self.assertRaisesRegex(FleetError, "integrity"):
            project.apply_proposal(self.root, self.catalog, self.store)

    def test_rollback_does_not_destroy_later_user_edits(self):
        self.connect()
        (self.root / "AGENTS.md").write_text("New project rules")
        with self.assertRaisesRegex(FleetError, "Local changes"):
            rollback(self.root)

    def test_mid_operation_error_restores_original_files(self):
        self.connect()
        from skillfleet import storage
        real = storage.atomic_write
        failed = False

        def fail_once(path, data):
            nonlocal failed
            if path.name == "skillfleet.json" and not failed:
                failed = True
                raise OSError("simulated disk failure")
            return real(path, data)

        before = (self.root / "AGENTS.md").read_bytes()
        with patch("skillfleet.storage.atomic_write", side_effect=fail_once):
            with self.assertRaisesRegex(OSError, "simulated"):
                transaction(self.root, {"AGENTS.md": b"Changed", "skillfleet.json": b"{}"})
        self.assertEqual(before, (self.root / "AGENTS.md").read_bytes())
        self.assertFalse((self.root / ".skillfleet/transaction.json").exists())

    def test_crash_recovery_uses_journal(self):
        self.connect()
        before = (self.root / "AGENTS.md").read_bytes()
        from skillfleet import storage
        real = storage.os.replace

        def simulate_crash(source, target):
            if str(target).endswith(".json") and "history" in str(target):
                raise OSError("crash before snapshot finalization")
            return real(source, target)

        with patch("skillfleet.storage.os.replace", side_effect=simulate_crash):
            with self.assertRaises(OSError):
                transaction(self.root, {"AGENTS.md": b"Changed"})
        recover(self.root)
        self.assertEqual(before, (self.root / "AGENTS.md").read_bytes())

    def test_agent_targets_do_not_duplicate_shared_directories(self):
        self.config["agents"] = ["codex", "cursor", "claude-code"]
        lock = self.connect()
        self.assertEqual(2, len(lock["directories"]))
        self.assertTrue((self.root / ".claude/skills/alpha/SKILL.md").is_file())
        self.assertIn(project.HOOK, (self.root / "CLAUDE.md").read_text())

    def test_symlink_target_is_rejected(self):
        outside = self.base / "outside"
        outside.mkdir()
        try:
            (self.root / ".agents").symlink_to(outside, target_is_directory=True)
        except OSError:
            self.skipTest("OS does not allow test symlinks")
        with self.assertRaisesRegex(FleetError, "symlink"):
            self.connect()
        self.assertEqual([], list(outside.iterdir()))

    def test_cli_reports_doctor_and_duplicate_init(self):
        args = ["--catalog", str(self.catalog_root), "--cache", str(self.base / "cache"), "--offline"]
        self.assertEqual(0, main([*args, "init", "--profile", "core", "--project", str(self.root)]))
        self.assertEqual(0, main([*args, "doctor", "--project", str(self.root)]))
        self.assertEqual(2, main([*args, "init", "--project", str(self.root)]))

    def test_uncommitted_builtin_is_not_pinned_to_old_commit(self):
        path = self.catalog_root / "skills/alpha/SKILL.md"
        path.write_text(path.read_text() + "A change\n")
        lock = read_json(self.catalog.lock_path)
        lock["skills"]["alpha"]["digest"] = bundle_digest(local_bundle(self.catalog_root, "skills/alpha"))
        self.catalog.lock_path.write_bytes(encoded(lock))
        with self.assertRaisesRegex(FleetError, "Commit local"):
            self.connect()


if __name__ == "__main__":
    unittest.main()
