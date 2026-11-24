#!/usr/bin/env python3
"""Fail when docs/catalog.md and the marketplace disagree.

Missing: a plugin, skill or command has no backtick-quoted mention in the catalog.
Stale: a table's first column names something the marketplace no longer has.
Names joined by commas or slashes inside one code span count as separate mentions.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PANE_COMMAND = re.compile(r"^const \w+_COMMAND = '([^']+)'", re.MULTILINE)
CODE_SPAN = re.compile(r"`([^`\n]+)`")


def skill_names(plugin: dict) -> set[str]:
    return {Path(s).name for s in plugin.get("skills", [])}


def command_names(plugin: dict) -> set[str]:
    return {p.stem for p in (ROOT / plugin["source"] / "commands").glob("*.md")}


def pane_command_names(register_source: str) -> set[str]:
    return set(PANE_COMMAND.findall(register_source))


def expected_names(plugins: list[dict], pane_commands: set[str]) -> set[str]:
    names = {p["name"] for p in plugins} | pane_commands
    for plugin in plugins:
        names |= skill_names(plugin) | command_names(plugin)
    return names


def tokens(text: str) -> set[str]:
    return {
        part.strip().lstrip("/")
        for span in CODE_SPAN.findall(text)
        for part in re.split(r"[,/]\s*", span)
        if part.strip()
    }


def first_column_tokens(text: str) -> set[str]:
    cells = (line.split("|")[1] for line in text.splitlines() if line.startswith("|"))
    return set().union(*(tokens(cell) for cell in cells))


def check(expected: set[str], catalog: str) -> list[str]:
    missing = sorted(expected - tokens(catalog))
    stale = sorted(first_column_tokens(catalog) - expected)
    problems = {
        "missing from docs/catalog.md": missing,
        "in docs/catalog.md but not in the marketplace": stale,
    }
    return [f"{label}: {', '.join(names)}" for label, names in problems.items() if names]


def main() -> int:
    plugins = json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text())["plugins"]
    register = (ROOT / "babysit-pane" / "hooks" / "register.tsx").read_text()
    pane_commands = pane_command_names(register)
    if not pane_commands:
        print("no *_COMMAND constants found in babysit-pane/hooks/register.tsx")
        return 1
    problems = check(expected_names(plugins, pane_commands), (ROOT / "docs" / "catalog.md").read_text())
    print("\n".join(problems))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
