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
    except json.JSONDecodeError:
        return None
    return entry if isinstance(entry, dict) else None


def _to_turn(entry: dict) -> Turn | None:
    message = entry.get("message")
    usage = message.get("usage") if isinstance(message, dict) else None
    if entry.get("type") != "assistant" or not isinstance(usage, dict):
        return None
    return Turn(
        model=str(message.get("model", "")),
        input=usage.get("input_tokens") or 0,
        cache_write=usage.get("cache_creation_input_tokens") or 0,
        cache_read=usage.get("cache_read_input_tokens") or 0,
        output=usage.get("output_tokens") or 0,
    )


def load_turns(path: Path) -> list[Turn]:
    entries = (_parse_line(line) for line in path.read_text().splitlines())
    turns = (_to_turn(e) for e in entries if e is not None)
    return [t for t in turns if t is not None]


def latest_context(path: Path) -> int:
    turns = load_turns(path)
    return turns[-1].context if turns else 0
