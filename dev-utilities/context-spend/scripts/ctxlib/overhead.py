from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

CHARS_PER_TOKEN = 4
FRONTMATTER_KEYS = ("name", "description")
BLOCK_INDICATOR = re.compile(r"[|>][+-]?\d*|[|>]\d*[+-]?")


@dataclass(frozen=True)
class OverheadItem:
    name: str
    kind: str
    tokens: int


def read_json(path: Path) -> dict:
    try:
        data = json.loads(path.read_text())
    except (OSError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def frontmatter_chars(path: Path) -> int:
    try:
        lines = path.read_text().splitlines()
    except (OSError, UnicodeDecodeError):
        return 0
    if not lines or lines[0].strip() != "---":
        return 0
    total = 0
    body = lines[1:]
    for index, line in enumerate(body):
        if line.strip() == "---":
            break
        key, _, value = line.partition(":")
        if key.strip() in FRONTMATTER_KEYS:
            total += _value_chars(value.strip(), body[index + 1 :])
    return total


def _value_chars(value: str, following: list[str]) -> int:
    if not BLOCK_INDICATOR.fullmatch(value):
        return len(value)
    total = 0
    for line in following:
        if line.strip() and not line[0].isspace():
            break
        total += len(line.strip())
    return total


def latest_version_dir(plugin_dir: Path) -> Path | None:
    versions = [p for p in plugin_dir.glob("*") if p.is_dir()]
    return max(versions, key=lambda p: p.stat().st_mtime, default=None)


def plugin_files(root: Path) -> list[Path]:
    return [
        *root.rglob("SKILL.md"),
        *root.glob("commands/*.md"),
        *root.glob("agents/*.md"),
    ]


def installed_path(claude_dir: Path, key: str) -> Path | None:
    plugins = read_json(claude_dir / "plugins" / "installed_plugins.json").get("plugins")
    installs = plugins.get(key) if isinstance(plugins, dict) else None
    first = installs[0] if isinstance(installs, list) and installs else None
    value = first.get("installPath") if isinstance(first, dict) else None
    path = Path(value) if isinstance(value, str) and value else None
    return path if path is not None and path.is_dir() else None


def plugin_tokens(claude_dir: Path, key: str) -> int | None:
    plugin, _, marketplace = key.partition("@")
    cache = claude_dir / "plugins" / "cache"
    root = installed_path(claude_dir, key) or latest_version_dir(cache / marketplace / plugin)
    if root is None:
        return None
    chars = sum(frontmatter_chars(f) for f in plugin_files(root))
    return -(-chars // CHARS_PER_TOKEN)


def enabled_plugins(claude_dir: Path) -> list[str]:
    plugins = read_json(claude_dir / "settings.json").get("enabledPlugins")
    if not isinstance(plugins, dict):
        return []
    return [key for key, on in plugins.items() if on is True]


def mcp_names(claude_dir: Path) -> list[str]:
    candidates = [claude_dir / ".claude.json"]
    if claude_dir.name == ".claude":
        candidates.append(claude_dir.parent / ".claude.json")
    for path in candidates:
        servers = read_json(path).get("mcpServers")
        if isinstance(servers, dict):
            return list(servers)
    return []


def rank_overhead(claude_dir: Path) -> list[OverheadItem]:
    items = []
    for key in enabled_plugins(claude_dir):
        tokens = plugin_tokens(claude_dir, key)
        if tokens is not None:
            items.append(OverheadItem(key, "plugin", tokens))
    items.extend(OverheadItem(name, "mcp", 0) for name in mcp_names(claude_dir))
    return sorted(items, key=lambda i: (-i.tokens, i.name))
