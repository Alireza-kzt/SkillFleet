"""Bounded paths, deterministic hashes, and recoverable project transactions."""
from __future__ import annotations

import base64
from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import time


class FleetError(Exception):
    """An actionable error that can be shown without a traceback."""


def encoded(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode()


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise FleetError(f"Cannot read JSON: {path}: {exc}") from exc
    if not isinstance(value, dict) or value.get("schema") != 1:
        raise FleetError(f"Unsupported document schema: {path}")
    return value


def relative_path(value: str) -> str:
    if not isinstance(value, str) or not value or any(c in value for c in '\\:<>"|?*') or any(ord(c) < 32 for c in value):
        raise FleetError(f"Unsafe relative path: {value!r}")
    path = PurePosixPath(value)
    if path.is_absolute() or any(p in {"", ".", ".."} for p in value.split("/")):
        raise FleetError(f"Unsafe relative path: {value!r}")
    if any(p.rstrip(" .") != p or p.split(".")[0].upper() in {
        "CON", "PRN", "AUX", "NUL", *(f"COM{i}" for i in range(1, 10)),
        *(f"LPT{i}" for i in range(1, 10))
    } for p in path.parts):
        raise FleetError(f"Nonportable path: {value!r}")
    return path.as_posix()


def identifier(value: str) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", value):
        raise FleetError(f"Invalid identifier: {value!r}")
    return value


def safe_path(root: Path, relative: str) -> Path:
    relative_path(relative)
    target = root / relative
    for item in [root, *target.parents, target]:
        if item == root.parent:
            continue
        if item.is_symlink():
            raise FleetError(f"Refusing symlink: {item}")
    if not target.resolve().is_relative_to(root.resolve()):
        raise FleetError(f"Path escapes project: {relative}")
    return target


def file_bytes(root: Path, relative: str) -> bytes | None:
    path = safe_path(root, relative)
    if not path.exists():
        return None
    if not path.is_file():
        raise FleetError(f"Expected a regular file: {path}")
    return path.read_bytes()


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    try:
        with temporary.open("xb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


@contextmanager
def mutex(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as exc:
        raise FleetError(f"Another operation owns {path}. If it crashed, confirm it ended before removing the lock.") from exc
    try:
        os.write(descriptor, str(os.getpid()).encode())
        os.close(descriptor)
        yield
    finally:
        path.unlink(missing_ok=True)


def writable_path(value: str) -> bool:
    return value in {"skillfleet.json", "skillfleet.lock.json", "AGENTS.md", "CLAUDE.md",
                     ".skillfleet/INSTRUCTIONS.md", ".skillfleet/.gitignore"} or any(
        value.startswith(prefix) for prefix in (".agents/skills/", ".claude/skills/")
    )


def _restore(root: Path, records: dict) -> None:
    for relative, record in records.items():
        if not writable_path(relative):
            raise FleetError(f"Journal contains an unmanaged path: {relative}")
        current = file_bytes(root, relative)
        current_hash = digest(current) if current is not None else None
        if current_hash not in {record["before_hash"], record["after_hash"]}:
            raise FleetError(f"Local changes prevent recovery: {relative}")
    for relative, record in reversed(list(records.items())):
        path = safe_path(root, relative)
        if record["before"] is None:
            path.unlink(missing_ok=True)
        else:
            atomic_write(path, base64.b64decode(record["before"], validate=True))


def transaction(root: Path, changes: dict[str, bytes | None]) -> int:
    pending = safe_path(root, ".skillfleet/transaction.json")
    if pending.exists():
        raise FleetError("An interrupted transaction exists. Run recover first.")
    records = {}
    for relative, after in changes.items():
        if not writable_path(relative):
            raise FleetError(f"Unmanaged write requested: {relative}")
        before = file_bytes(root, relative)
        if before == after:
            continue
        records[relative] = {
            "before": base64.b64encode(before).decode() if before is not None else None,
            "before_hash": digest(before) if before is not None else None,
            "after_hash": digest(after) if after is not None else None,
        }
    if not records:
        return 0
    journal = {"schema": 1, "files": records}
    atomic_write(pending, encoded(journal))
    try:
        for relative in records:
            path = safe_path(root, relative)
            after = changes[relative]
            if after is None:
                path.unlink(missing_ok=True)
            else:
                atomic_write(path, after)
    except BaseException:
        _restore(root, records)
        pending.unlink()
        raise
    history = safe_path(root, f".skillfleet/history/{time.time_ns()}.json")
    history.parent.mkdir(parents=True, exist_ok=True)
    os.replace(pending, history)
    return len(records)


def recover(root: Path) -> None:
    pending = safe_path(root, ".skillfleet/transaction.json")
    if not pending.exists():
        raise FleetError("No interrupted transaction to recover.")
    _restore(root, read_json(pending)["files"])
    pending.unlink()


def rollback(root: Path) -> None:
    history = safe_path(root, ".skillfleet/history")
    snapshots = sorted(history.glob("[0-9]*.json")) if history.exists() else []
    snapshots = [p for p in snapshots if not p.name.endswith(".rolled-back.json")]
    if not snapshots:
        raise FleetError("No local snapshot to roll back. Git history can restore committed configuration.")
    snapshot = snapshots[-1]
    records = read_json(snapshot)["files"]
    for relative, record in records.items():
        current = file_bytes(root, relative)
        if (digest(current) if current is not None else None) != record["after_hash"]:
            raise FleetError(f"Local changes prevent rollback: {relative}")
    # Use the same recovery journal as installation, including for a process crash.
    pending = safe_path(root, ".skillfleet/transaction.json")
    if pending.exists():
        raise FleetError("Run recover before rollback.")
    atomic_write(pending, encoded({"schema": 1, "files": records}))
    _restore(root, records)
    snapshot.rename(snapshot.with_suffix(".rolled-back.json"))
    pending.unlink()
