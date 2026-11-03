"""The command-line interface; business logic lives in focused modules."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import sys

from . import __version__
from .catalog import Catalog, skill_name
from .gitstore import GitStore
from . import project
from .storage import FleetError, atomic_write, encoded, file_bytes, mutex, read_json, recover, rollback, safe_path

ROOT = Path(__file__).resolve().parent.parent


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Pinned agent skills, independent projects, reviewed updates.")
    p.add_argument("--version", action="version", version=__version__)
    p.add_argument("--catalog", type=Path, default=ROOT, help="SkillFleet checkout (not a project registry).")
    p.add_argument("--cache", type=Path, default=Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache")) / "skillfleet")
    p.add_argument("--offline", action="store_true", help="Use only local/cached Git objects.")
    commands = p.add_subparsers(dest="command", required=True)
    for command in ("init", "sync", "check", "update", "doctor", "rollback", "recover", "add", "remove"):
        sub = commands.add_parser(command)
        sub.add_argument("--project", type=Path, default=Path.cwd())
        if command == "init":
            sub.add_argument("--profile", action="append", default=[], help="Repeat for multiple profiles; default: auto-detect.")
            sub.add_argument("--agent", action="append", choices=sorted(project.AGENT_PATHS), default=[])
        if command == "update":
            sub.add_argument("--apply", action="store_true", help="Apply the previously generated proposal.")
        if command in {"add", "remove"}:
            sub.add_argument("skills", nargs="+")
        if command == "check":
            sub.add_argument("--json", action="store_true")
    commands.add_parser("list").add_argument("--profile", help="Show only one profile and core.")
    cat = commands.add_parser("catalog")
    cat.add_argument("action", choices=["validate", "check", "refresh", "audit"])
    cat.add_argument("--json", action="store_true")
    return p


def print_updates(result: dict, as_json: bool) -> None:
    if as_json:
        print(encoded(result).decode(), end="")
        return
    for update in result["updates"]:
        state = "UPDATE" if update["changed"] else "current"
        print(f"{state:7} {update['url'][:-4]} {update['pinned'][:12]} -> {update['latest'][:12]}")
        if update["changed"]:
            print(f"        {update['compare']}")
    print("Source changes do not modify installed skills. Central catalog review comes first.")


def catalog_command(args: argparse.Namespace, catalog: Catalog, store: GitStore) -> int:
    catalog.validate()
    if args.action == "refresh":
        with mutex(catalog.root / ".catalog-operation.lock"):
            catalog.refresh(store)
        print("Updated registry/catalog.lock.json. Review the upstream compare links before committing.")
    elif args.action == "check":
        print_updates(catalog.check(store), args.json)
    elif args.action == "audit":
        lock = catalog.lock()
        count = 0
        for key in lock["skills"]:
            spec = catalog.project_spec(key, lock)
            files = catalog.materialize(key, spec, store)
            if skill_name(files) != key:
                raise FleetError(f"Invalid skill name: {key}")
            count += 1
            print(f"OK {key} ({len(files)} files)")
        print(f"Verified {count} complete bundles at pinned versions; upstream scripts were not executed.")
    else:
        catalog.lock()
        print(f"Valid: {len(catalog.data['skills'])} skills, {len(catalog.data['profiles'])} profiles.")
    return 0


def run(args: argparse.Namespace) -> int:
    catalog = Catalog(args.catalog.resolve())
    store = GitStore(args.cache.resolve(), args.offline)
    if args.command == "catalog":
        return catalog_command(args, catalog, store)
    if args.command == "list":
        ids = catalog.selected({"profiles": [args.profile]}) if args.profile else sorted(catalog.data["skills"])
        for key in ids:
            spec = catalog.data["skills"][key]
            print(f"{key:38} {spec['description']}")
        print("\nProfiles: " + ", ".join(catalog.data["profiles"]))
        return 0
    root = args.project.expanduser().resolve()
    if not root.is_dir():
        raise FleetError(f"Project directory does not exist: {root}")
    if root == catalog.root:
        raise FleetError("Connect a project directory, not the central SkillFleet checkout.")
    if args.command == "doctor":
        config, lock = project.manifest(root), project.installed_lock(root)
        issues = project.problems(root, lock)
        if lock is None:
            issues.append("Missing project lock; run sync.")
        else:
            if sorted(lock["skills"]) != catalog.selected(config) or lock["agents"] != config["agents"]:
                issues.append("Selection differs from the lock; run sync.")
            project.hooks(root, config["agents"])
        if safe_path(root, ".skillfleet/transaction.json").exists():
            issues.append("Interrupted transaction; run recover.")
        if not shutil.which("git"):
            issues.append("Git is missing from PATH.")
        for issue in issues:
            print(issue)
        if issues:
            return 1
        size = sum(len(file_bytes(root, path) or b"") for path in lock["installed"] if path.endswith("/SKILL.md"))
        print(f"Healthy: {len(lock['skills'])} pinned skills, {len(lock['installed'])} files, {size:,} bytes of SKILL.md bodies.")
        print("Only descriptions are normally discovered eagerly; actual token use depends on the agent.")
        return 0
    if args.command == "check":
        lock = project.installed_lock(root)
        if lock is None:
            raise FleetError("No project lock. Run init or sync first.")
        print_updates(catalog.check(store, lock), args.json)
        return 0
    operation = safe_path(root, ".skillfleet/operation.lock")
    with mutex(operation):
        if args.command == "recover":
            recover(root)
            print("Restored the state before the interrupted operation.")
            return 0
        if safe_path(root, ".skillfleet/transaction.json").exists():
            raise FleetError("An interrupted operation exists. Run recover first.")
        if args.command == "rollback":
            rollback(root)
            print("Restored the previous local snapshot.")
            return 0
        if args.command == "init":
            if file_bytes(root, "skillfleet.json") is not None or project.installed_lock(root):
                raise FleetError("Project is already connected. Edit skillfleet.json, then run sync.")
            profiles = args.profile or project.detect_profiles(root)
            config = {"schema": 1, "profiles": profiles, "agents": args.agent or ["codex"], "skills": [], "exclude": []}
            config.update(skills=catalog.selected(config), selection_mode="explicit")
            target = project.resolve(catalog, config, None)
            lock = project.install(root, catalog, store, target, None, encoded(config))
            print(f"Connected {root}: profiles {', '.join(profiles)}; {len(lock['skills'])} skills.")
        elif args.command in {"add", "remove"}:
            config = project.manifest(root)
            unknown = set(args.skills) - catalog.data["skills"].keys()
            if unknown:
                raise FleetError(f"Unknown skills: {', '.join(sorted(unknown))}")
            requested = set(args.skills)
            selected, excluded = set(config.get("skills", [])), set(config.get("exclude", []))
            if args.command == "add":
                selected.update(requested)
                excluded.difference_update(requested)
            else:
                selected.difference_update(requested)
                excluded.update(requested)
            config.update(skills=sorted(selected), exclude=sorted(excluded))
            old = project.installed_lock(root)
            lock = project.install(root, catalog, store, project.resolve(catalog, config, old), old, encoded(config))
            print(f"Selection saved in this project: {len(lock['skills'])} skills.")
        elif args.command == "sync":
            lock = project.sync(root, catalog, store)
            print(f"Restored {len(lock['skills'])} skills from this project's pins.")
        elif args.command == "update":
            if args.apply:
                lock = project.apply_proposal(root, catalog, store)
                print(f"Applied reviewed proposal: {len(lock['skills'])} skills. Run project checks before committing.")
            else:
                proposal = project.propose(root, catalog, store)
                print(f"Proposal: {len(proposal['changed_files'])} changed skill files.")
                print(f"Review {root / '.skillfleet/update.diff'}, then run update --apply.")
    return 0


def main(argv: list[str] | None = None) -> int:
    try:
        return run(parser().parse_args(argv))
    except (FleetError, OSError, KeyError, TypeError, ValueError) as exc:
        print(f"skillfleet: {exc}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print("skillfleet: interrupted; installed files are recoverable with recover.", file=sys.stderr)
        return 130
