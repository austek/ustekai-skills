import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SUBCOMMANDS = ("preflight", "plan", "next", "record", "record-lane", "deps", "auditr", "act", "report", "usage", "reset", "schedule")


def frontmatter(path: Path) -> dict:
    text = path.read_text()
    block = re.match(r"---\n(.*?)\n---\n", text, re.S).group(1)
    return dict(line.split(": ", 1) for line in block.splitlines() if ": " in line)


def test_skill_has_name_description_and_hint():
    fm = frontmatter(ROOT / "audit" / "SKILL.md")
    assert fm["name"] == "audit"
    assert fm["description"] and fm["argument-hint"]


def test_skill_documents_every_cli_subcommand():
    text = (ROOT / "audit" / "SKILL.md").read_text()
    for sub in SUBCOMMANDS:
        assert f"AUDIT {sub}" in text, sub


def test_command_has_hint_and_forwards_arguments():
    path = ROOT / "commands" / "audit.md"
    assert frontmatter(path)["argument-hint"]
    assert "$ARGUMENTS" in path.read_text()


def test_full_audit_is_a_thin_alias():
    text = (ROOT / "commands" / "full-audit.md").read_text()
    assert "--lanes all" in text and "$ARGUMENTS" in text
    assert len(text.splitlines()) < 20


def test_marketplace_lists_audit_skill_and_bumped_version():
    market = json.loads((ROOT.parent / ".claude-plugin" / "marketplace.json").read_text())
    entry = next(p for p in market["plugins"] if p["name"] == "dev-utilities")
    assert "./audit" in entry["skills"]
    assert entry["version"] != "1.2.0"
