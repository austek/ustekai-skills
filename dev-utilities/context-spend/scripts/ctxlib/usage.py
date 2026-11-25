from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

COUNTER_KEYS = (
    "input_tokens",
    "cache_creation_input_tokens",
    "cache_read_input_tokens",
    "output_tokens",
)


@dataclass(frozen=True)
class Turn:
    model: str
    input: int
    cache_write: int
    cache_read: int
    output: int
    cache_write_1h: int = 0

    @property
    def context(self) -> int:
        return self.input + self.cache_write + self.cache_read


def _parse_line(line: str) -> dict | None:
    try:
        entry = json.loads(line)
    except (ValueError, RecursionError):
        return None
    return entry if isinstance(entry, dict) else None


def _valid_counter(value: object) -> bool:
    return type(value) is int and value >= 0


def _counters(usage: dict) -> list[int] | None:
    raw = [usage.get(k) for k in COUNTER_KEYS]
    if not all(v is None or _valid_counter(v) for v in raw):
        return None
    return [v or 0 for v in raw]


def _one_hour_tokens(usage: dict, cache_write: int) -> int:
    creation = usage.get("cache_creation")
    value = creation.get("ephemeral_1h_input_tokens") if isinstance(creation, dict) else None
    return min(value, cache_write) if _valid_counter(value) else 0


def _to_turn(entry: dict, include_sidechain: bool) -> Turn | None:
    message = entry.get("message")
    usage = message.get("usage") if isinstance(message, dict) else None
    if entry.get("type") != "assistant" or not isinstance(usage, dict):
        return None
    if entry.get("isSidechain") is True and not include_sidechain:
        return None
    counters = _counters(usage)
    if counters is None:
        return None
    turn = Turn(str(message.get("model", "")), *counters, _one_hour_tokens(usage, counters[1]))
    return turn if turn.context > 0 else None


def _call_key(entry: dict) -> str | None:
    message = entry.get("message")
    for value in (message.get("id") if isinstance(message, dict) else None, entry.get("requestId")):
        if isinstance(value, str) and value:
            return value
    return None


def _dedupe(pairs: list[tuple[str | None, Turn]]) -> list[Turn]:
    slots: list[Turn] = []
    index: dict[str, int] = {}
    for key, turn in pairs:
        if key is not None and key in index:
            slots[index[key]] = turn
            continue
        if key is not None:
            index[key] = len(slots)
        slots.append(turn)
    return slots


def load_turns(path: Path, include_sidechain: bool = False) -> list[Turn]:
    text = path.read_text(encoding="utf-8", errors="replace")
    entries = [e for e in map(_parse_line, text.split("\n")) if e is not None]
    pairs = [(_call_key(e), _to_turn(e, include_sidechain)) for e in entries]
    return _dedupe([(k, t) for k, t in pairs if t is not None])


def load_subagent_turns(transcript: Path) -> list[list[Turn]]:
    folder = transcript.with_suffix("") / "subagents"
    return [load_turns(f, include_sidechain=True) for f in sorted(folder.glob("agent-*.jsonl"))]


def context_of(turns: list[Turn]) -> int:
    return turns[-1].context if turns else 0


def latest_context(path: Path) -> int:
    return context_of(load_turns(path))
