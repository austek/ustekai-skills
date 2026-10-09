from __future__ import annotations

import json
import re
from collections.abc import Iterator, Mapping
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

SOFT_LIMIT = 0.9
_COUNTED = ("input_tokens", "output_tokens", "cache_creation_input_tokens")
_RESET = re.compile(r"resets\s+(\d{1,2})(?::(\d{2}))?\s*(am|pm)(?:\s*\(([^)]+)\))?", re.I)


def _entries(path: Path) -> Iterator[tuple[str, dict]]:
    for n, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines()):
        try:
            yield f"{path}:{n}", json.loads(line)
        except json.JSONDecodeError:
            continue


def _usage(key: str, entry: dict) -> list[tuple[str, int]]:
    msg = entry.get("message")
    if entry.get("type") != "assistant" or not isinstance(msg, dict) or not msg.get("usage"):
        return []
    total = sum(msg["usage"].get(k, 0) for k in _COUNTED)
    return [(msg.get("id") or key, total)]


def usage_tokens(paths: list[Path]) -> int:
    largest_usage_by_message_id: dict[str, int] = {}
    for path in paths:
        for key, entry in _entries(path):
            for mid, total in _usage(key, entry):
                largest_usage_by_message_id[mid] = max(largest_usage_by_message_id.get(mid, 0), total)
    return sum(largest_usage_by_message_id.values())


def session_files(project_dir: Path, session_id: str) -> list[Path]:
    main = project_dir / f"{session_id}.jsonl"
    nested = sorted((project_dir / session_id).rglob("*.jsonl"))
    return [p for p in [main, *nested] if p.exists()]


def decision(spent: float, est: float, budget: float) -> str:
    if spent >= budget * SOFT_LIMIT:
        return "stop"
    return "skip" if spent + est > budget else "run"


def next_unit(state: dict, est: Mapping[str, int]) -> tuple[str, str]:
    pending = [u for u, s in state["units"].items() if s == "pending"]
    if not pending:
        return ("done", "")
    for unit in pending:
        verdict = decision(state["spent"], est[unit], state["budget"]["amount"])
        if verdict == "stop":
            return ("stop", "")
        if verdict == "run":
            return ("run", unit)
    return ("exhausted", "")


def _zone(name: str, fallback):
    try:
        return ZoneInfo(name) if name else fallback
    except ZoneInfoNotFoundError:
        return fallback


def find_reset(message: str, now: datetime) -> list[datetime]:
    m = _RESET.search(message)
    if not m:
        return []
    local = now.astimezone(_zone(m[4], now.tzinfo))
    hour = int(m[1]) % 12 + (12 if m[3].lower() == "pm" else 0)
    target = local.replace(hour=hour, minute=int(m[2] or 0), second=0, microsecond=0)
    return [target if target > local else target + timedelta(days=1)]
