from __future__ import annotations

import json
import subprocess
from pathlib import Path

_NPM_SEVERITY = {"critical": "blocker", "high": "high", "moderate": "medium", "low": "low", "info": "low"}
COMMANDS = {
    "node": ["npm", "audit", "--json"],
    "python": ["pip-audit", "--format", "json"],
    "rust": ["cargo", "audit", "--json"],
}


class Skipped(Exception):
    pass


def _finding(rule: str, file: str, anchor: str, severity: str, fixable: bool, summary: str) -> dict:
    return {
        "rule": rule,
        "file": file,
        "anchor": anchor,
        "severity": severity,
        "confidence": 0.9,
        "effort": "S" if fixable else "M",
        "fixable": fixable,
        "summary": summary,
    }


def parse_npm_audit(text: str) -> list[dict]:
    vulns = json.loads(text)["vulnerabilities"]
    return [
        _finding(
            "deps/npm-advisory",
            "package.json",
            name,
            _NPM_SEVERITY.get(v.get("severity", "low"), "low"),
            bool(v.get("fixAvailable")),
            f"{name} {v.get('severity', '')}: {v.get('range', '')}".strip(),
        )
        for name, v in vulns.items()
    ]


def parse_pip_audit(text: str) -> list[dict]:
    packages = json.loads(text)["dependencies"]
    return [
        _finding(
            "deps/pip-advisory",
            "requirements.txt",
            f"{p['name']}:{v['id']}",
            "medium",
            bool(v.get("fix_versions")),
            f"{p['name']} {p['version']} affected by {v['id']}",
        )
        for p in packages
        for v in p.get("vulns", [])
    ]


def parse_cargo_audit(text: str) -> list[dict]:
    listed = json.loads(text)["vulnerabilities"]["list"]
    return [
        _finding(
            "deps/cargo-advisory",
            "Cargo.toml",
            f"{v['package']['name']}:{v['advisory']['id']}",
            "high",
            False,
            f"{v['package']['name']} {v['package']['version']}: {v['advisory']['title']}",
        )
        for v in listed
    ]


def command_for(stack: str, root: Path) -> list[str]:
    if stack != "python":
        return COMMANDS[stack]
    target = ["-r", "requirements.txt"] if (root / "requirements.txt").is_file() else ["."]
    return ["pip-audit", *target, "--format", "json"]


PARSERS = {"node": parse_npm_audit, "python": parse_pip_audit, "rust": parse_cargo_audit}


def _run_one(stack: str, root: Path, runner) -> list[dict]:
    if stack not in COMMANDS:
        raise Skipped(stack)
    try:
        out = runner(command_for(stack, root), cwd=root, capture_output=True, text=True).stdout
        return PARSERS[stack](out)
    except (FileNotFoundError, json.JSONDecodeError, KeyError, TypeError) as e:
        raise Skipped(stack) from e


def run_deps(stacks: list[str], root: Path, runner=subprocess.run) -> tuple[list[dict], list[str]]:
    found: list[dict] = []
    skipped: list[str] = []
    for stack in stacks:
        try:
            found.extend(_run_one(stack, root, runner))
        except Skipped:
            skipped.append(stack)
    return found, skipped
