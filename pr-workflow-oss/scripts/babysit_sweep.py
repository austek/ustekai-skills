#!/usr/bin/env python3
"""Writes CLOSED into babysit-pr state files whose PR GitHub reports merged or closed, and deletes CLOSED files after the retention; never fails a session."""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import NamedTuple

STATE_DIR = Path(".cache") / "babysit-pr"
STATES = frozenset({"READY", "WAITING", "BLOCKED", "EXHAUSTED", "CLOSED"})
CLOSED_ON_GITHUB = frozenset({"MERGED", "CLOSED"})
REPO = re.compile(r"^[A-Za-z0-9][A-Za-z0-9-]*/[A-Za-z0-9._-]+$")
KEPT = ("v", "repo", "pr", "cycle", "cycles", "head", "pass", "fail", "pending", "openThreads")
GH_TIMEOUT_SECONDS = 10
DEFAULT_LIMIT = 40
RETENTION_MS = 24 * 3_600_000
PURGE_ENV = "BABYSIT_PURGE_HOURS"

Lookup = Callable[[str, int], "str | None"]


class Swept(NamedTuple):
    closed: list[str]
    deleted: list[str]


def parse_state(text: str) -> dict | None:
    """A version-1 entry with a known state, a positive integer PR and an `owner/repo`; anything else is None."""
    try:
        data = json.loads(text)
    except ValueError:
        return None
    if not isinstance(data, dict):
        return None
    pr, repo, state = data.get("pr"), data.get("repo"), data.get("state")
    is_pr = isinstance(pr, int) and not isinstance(pr, bool) and pr > 0
    is_state = isinstance(state, str) and state in STATES
    valid = data.get("v") == 1 and is_state and is_pr and isinstance(repo, str) and REPO.match(repo)
    return data if valid else None


def closed_entry(entry: dict, now_ms: int) -> dict:
    """The entry as CLOSED: counts and head SHA kept, `next`, `nextReviewAt` and `watchId` dropped, `updatedAt` set to `now_ms`."""
    return {**{key: entry[key] for key in KEPT if key in entry}, "state": "CLOSED", "updatedAt": now_ms}


def gh_state(repo: str, pr: int, run: Callable = subprocess.run) -> str | None:
    """`OPEN`, `MERGED` or `CLOSED` as GitHub reports it; None when the repo is malformed or the lookup fails."""
    if not REPO.match(repo) or pr <= 0:
        return None
    argv = ["gh", "pr", "view", str(pr), "--repo", repo, "--json", "state", "--jq", ".state"]
    try:
        done = run(argv, capture_output=True, text=True, timeout=GH_TIMEOUT_SECONDS, check=False)
    except (OSError, subprocess.SubprocessError):
        return None
    answer = (done.stdout or "").strip()
    return answer if done.returncode == 0 and answer in {"OPEN", *CLOSED_ON_GITHUB} else None


def _state_files(state_dir: Path) -> list[Path]:
    return sorted(p for p in state_dir.glob("*.json") if p.is_file() and not p.is_symlink())


def _read_entry(path: Path) -> tuple[Path, str, dict] | None:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError):
        return None
    entry = parse_state(text)
    return (path, text, entry) if entry is not None else None


def _age_ms(found: tuple[Path, str, dict], now_ms: int) -> float:
    """Age by the newer of `updatedAt` and the mtime, so a file is never judged older than its latest write."""
    path, _, entry = found
    stamp = entry.get("updatedAt")
    written = stamp if isinstance(stamp, (int, float)) and not isinstance(stamp, bool) else 0
    try:
        return now_ms - max(written, path.stat().st_mtime * 1000)
    except OSError:
        return 0.0


def retention_ms(env: Mapping[str, str]) -> int:
    """The retention in ms from `BABYSIT_PURGE_HOURS`; a missing, malformed, non-positive or non-finite value means 24 hours."""
    try:
        hours = float(env.get(PURGE_ENV, ""))
    except ValueError:
        return RETENTION_MS
    return int(hours * 3_600_000) if 0 < hours * 3_600_000 < float("inf") else RETENTION_MS


def _is_expired(found: tuple[Path, str, dict], now_ms: int, retention: int) -> bool:
    return found[2]["state"] == "CLOSED" and _age_ms(found, now_ms) > retention


def _try_delete(found: tuple[Path, str, dict]) -> bool:
    path, text, _ = found
    try:
        if path.read_text(encoding="utf-8") != text:
            return False
        path.unlink()
    except (OSError, UnicodeError):
        return False
    return True


def _write_closed(path: Path, entry: dict, now_ms: int) -> None:
    tmp = path.with_name(f"{path.name}.{os.getpid()}.tmp")
    try:
        with os.fdopen(os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), "w", encoding="utf-8") as handle:
            json.dump(closed_entry(entry, now_ms), handle)
        os.replace(tmp, path)
    except OSError:
        tmp.unlink(missing_ok=True)
        raise


def _try_close(found: tuple[Path, str, dict], lookup: Lookup, now_ms: int) -> bool:
    path, text, entry = found
    if lookup(entry["repo"], entry["pr"]) not in CLOSED_ON_GITHUB:
        return False
    try:
        if path.read_text(encoding="utf-8") != text:
            return False
        _write_closed(path, entry, now_ms)
    except (OSError, UnicodeError):
        return False
    return True


def sweep(
    state_dir: Path, lookup: Lookup, now_ms: int, limit: int = DEFAULT_LIMIT, retention_ms: int = RETENTION_MS,
) -> Swept:
    """Rewrites unclosed files whose PR is merged or closed as CLOSED, and deletes CLOSED files older than
    `retention_ms`. A file closed in this run is never deleted in it. At most `limit` unclosed files are looked up,
    most recently written first. A file whose text changed since it was read is left alone; a write between that check and
    the replace or unlink is not detected."""
    found = [read for path in _state_files(state_dir) if (read := _read_entry(path)) is not None]
    unclosed = sorted((item for item in found if item[2]["state"] != "CLOSED"), key=lambda item: _age_ms(item, now_ms))
    expired = [item for item in found if _is_expired(item, now_ms, retention_ms)]
    return Swept(
        closed=[item[0].name for item in unclosed[:limit] if _try_close(item, lookup, now_ms)],
        deleted=[item[0].name for item in expired if _try_delete(item)],
    )


def main(
    home: Path | None = None, lookup: Lookup = gh_state, now_ms: int | None = None, env: Mapping[str, str] | None = None,
) -> int:
    directory = (home if home is not None else Path.home()) / STATE_DIR
    if directory.is_dir():
        now = now_ms if now_ms is not None else int(time.time() * 1000)
        sweep(directory, lookup, now, retention_ms=retention_ms(os.environ if env is None else env))
    return 0


if __name__ == "__main__":
    sys.exit(main())
