import json
import os
import re
from pathlib import Path

from ctxlib.usage import latest_context

SESSION_ID = re.compile(r"[A-Za-z0-9_-]{1,64}")


def default_state_dir() -> Path:
    base = os.environ.get("XDG_STATE_HOME") or str(Path.home() / ".local" / "state")
    return Path(base) / "ctx-spend"


def _parse(stdin_json: str) -> tuple[str, Path] | None:
    try:
        data = json.loads(stdin_json)
    except ValueError:
        return None
    if not isinstance(data, dict):
        return None
    session, path = data.get("session_id"), data.get("transcript_path")
    if not isinstance(session, str) or not isinstance(path, str):
        return None
    return session, Path(path)


def _context(path: Path) -> int:
    try:
        return latest_context(path)
    except (OSError, TypeError, ValueError):
        return 0


def _format(tokens: int) -> str:
    return f"{round(tokens / 1000)}K"


def _message(tokens: int) -> str:
    return (
        f"Context is {_format(tokens)} tokens; every turn re-reads it. Consider:\n"
        "/compact\n"
        "/clear"
    )


def _record(marker: Path, tokens: int) -> bool:
    try:
        for directory in (marker.parent.parent, marker.parent):
            directory.mkdir(parents=True, exist_ok=True, mode=0o700)
            directory.chmod(0o700)
        marker.write_text(str(tokens))
    except OSError:
        return False
    return True


def _rearm(marker: Path) -> None:
    try:
        marker.unlink()
    except OSError:
        pass


def guard_message(stdin_json: str, threshold: int, state_dir: Path) -> str | None:
    parsed = _parse(stdin_json)
    if parsed is None or not SESSION_ID.fullmatch(parsed[0]):
        return None
    session, path = parsed
    tokens = _context(path)
    marker = state_dir / "warned" / session
    if tokens < threshold:
        _rearm(marker)
        return None
    if marker.exists():
        return None
    return _message(tokens) if _record(marker, tokens) else None


def statusline_text(stdin_json: str, window: int) -> str:
    parsed = _parse(stdin_json)
    if parsed is None or window <= 0:
        return ""
    tokens = _context(parsed[1])
    return f"ctx {min(999, tokens * 100 // window)}%" if tokens else ""
