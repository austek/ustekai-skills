from __future__ import annotations

import hashlib
import json
import re
import subprocess

from auditlib import plan

_MARKER = re.compile(r"<!-- audit-fp:([0-9a-f]+) -->")


class TrackerError(RuntimeError):
    pass


def unit_label(unit: str) -> str:
    return "audit-fp:" + hashlib.sha256(f"unit:{unit}".encode()).hexdigest()[:12]


def group(items: list[dict], owner: dict | None = None) -> dict[str, list[dict]]:
    mapping = owner or {}
    out: dict[str, list[dict]] = {}
    for item in items:
        key = mapping.get(item["file"]) or plan.shard_key(item["file"])
        out.setdefault(key, []).append(item)
    return out


def render(unit: str, items: list[dict]) -> dict:
    rows = "\n".join(
        f"- `{i['file']}` [{i['severity']}] {i['summary']} <!-- audit-fp:{i['fingerprint']} -->" for i in items
    )
    rules = ", ".join(sorted({i["rule"] for i in items}))
    ac = f"Given `{unit}` is re-audited, when rules {rules} run, then none of the findings above is reported."
    return {
        "unit": unit,
        "title": f"Audit: {len(items)} findings in {unit}",
        "body": f"### Findings\n\n{rows}\n\n### Acceptance criteria\n\n{ac}",
        "label": unit_label(unit),
    }


def _known(entries: list[dict]) -> set[str]:
    return set().union(*(set(_MARKER.findall(e["body"])) for e in entries))


def decide(existing: list[dict], new_fps: set[str]) -> str:
    opened = [e for e in existing if e["state"].upper() == "OPEN"]
    if opened:
        return "skip" if new_fps <= _known(opened) else "update"
    return "regression" if new_fps & _known(existing) else "create"


def detect_tracker(remote_url: str) -> str:
    return "jira" if "collibra" in remote_url.lower() else "github"


class GitHub:
    def __init__(self, runner=subprocess.run):
        self._runner = runner

    def _gh(self, *args: str) -> str:
        try:
            result = self._runner(["gh", *args], capture_output=True, text=True)
        except FileNotFoundError as e:
            raise TrackerError("gh CLI not found") from e
        if result.returncode:
            raise TrackerError(result.stderr.strip() or "gh failed")
        return result.stdout

    def search(self, label: str) -> list[dict]:
        out = self._gh("issue", "list", "--label", label, "--state", "all", "--json", "number,state,body")
        return json.loads(out or "[]")

    def create(self, title: str, body: str, label: str) -> None:
        self._gh("label", "create", label, "--force")
        self._gh("issue", "create", "--title", title, "--body", body, "--label", label)

    def edit(self, number: int, body: str) -> None:
        self._gh("issue", "edit", str(number), "--body", body)


def _action(unit: str, items: list[dict], tracker) -> dict:
    rendered = render(unit, items)
    existing = tracker.search(rendered["label"])
    verdict = decide(existing, {i["fingerprint"] for i in items})
    return {**rendered, "action": verdict, "existing": existing}


def plan_actions(groups: dict[str, list[dict]], tracker, max_issues: int) -> list[dict]:
    actions: list[dict] = []
    remaining = max_issues
    for unit, items in groups.items():
        action = _action(unit, items, tracker)
        if action["action"] == "skip":
            actions.append(action)
        elif remaining > 0:
            actions.append(action)
            remaining -= 1
    return actions


def apply_actions(actions: list[dict], tracker) -> None:
    for a in actions:
        if a["action"] in ("create", "regression"):
            prefix = "Regression: " if a["action"] == "regression" else ""
            tracker.create(prefix + a["title"], a["body"], a["label"])
        elif a["action"] == "update":
            number = next(e["number"] for e in a["existing"] if e["state"].upper() == "OPEN")
            tracker.edit(number, a["body"])
