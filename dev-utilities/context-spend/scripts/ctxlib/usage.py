from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Turn:
    model: str
    input: int
    cache_write: int
    cache_read: int
    output: int

    @property
    def context(self) -> int:
        return self.input + self.cache_write + self.cache_read


def _parse_line(line: str) -> dict | None:
    try:
        entry = json.loads(line)
    except (ValueError, RecursionError):
        return None
    return entry if isinstance(entry, dict) else None


def _to_turn(entry: dict) -> Turn | None:
    message = entry.get("message")
    usage = message.get("usage") if isinstance(message, dict) else None
    if entry.get("type") != "assistant" or entry.get("isSidechain") is True:
        return None
    if not isinstance(usage, dict):
        return None
    turn = Turn(
        model=str(message.get("model", "")),
        input=usage.get("input_tokens") or 0,
        cache_write=usage.get("cache_creation_input_tokens") or 0,
        cache_read=usage.get("cache_read_input_tokens") or 0,
        output=usage.get("output_tokens") or 0,
    )
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


def load_turns(path: Path) -> list[Turn]:
    text = path.read_text(encoding="utf-8", errors="replace")
    entries = [e for e in map(_parse_line, text.split("\n")) if e is not None]
    pairs = [(_call_key(e), _to_turn(e)) for e in entries]
    return _dedupe([(k, t) for k, t in pairs if t is not None])


def latest_context(path: Path) -> int:
    turns = load_turns(path)
    return turns[-1].context if turns else 0
