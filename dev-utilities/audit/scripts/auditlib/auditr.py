from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

ANCHOR_LEN = 80
AUTO_CONFIDENCE = 0.9
_SEVERITY = {"blocking": "blocker", "high": "high", "medium": "medium", "low": "low", "suggestion": "low"}
_CONFIDENCE = {"auto": 0.9, "candidate": 0.4}


class AuditrUnavailable(Exception):
    pass


def available() -> bool:
    return shutil.which("auditr") is not None


def _anchor(item: dict) -> str:
    text = item.get("evidence") or item.get("message") or ""
    return " ".join(text.split())[:ANCHOR_LEN]


def _finding(file: str, item: dict) -> dict:
    return {
        "rule": f"auditr/{item['rule_id']}",
        "file": file,
        "anchor": _anchor(item),
        "severity": _SEVERITY.get(item.get("severity", ""), "low"),
        "confidence": _CONFIDENCE.get(item.get("verdict_kind", ""), 0.4),
        "effort": "S",
        "fixable": bool(item.get("suggestion")),
        "summary": item["message"],
        "evidence": item.get("evidence", ""),
    }


def _relative(file: str, root: str) -> str:
    prefix = root.rstrip("/") + "/"
    return file[len(prefix):] if root and file.startswith(prefix) else file


def parse_report(text: str, root: str = "") -> list[dict]:
    files = json.loads(text)["files"]
    return [_finding(_relative(f["file"], root), x) for f in files for x in f.get("findings", [])]


def split_judged(items: list[dict]) -> tuple[list[dict], list[dict]]:
    auto = [i for i in items if i["confidence"] >= AUTO_CONFIDENCE]
    return auto, [i for i in items if i["confidence"] < AUTO_CONFIDENCE]


def scan(root: Path, runner=subprocess.run) -> list[dict]:
    try:
        out = runner(["auditr", "scan", str(root), "-f", "json"], capture_output=True, text=True).stdout
        return parse_report(out, str(root))
    except (FileNotFoundError, json.JSONDecodeError, KeyError, TypeError) as e:
        raise AuditrUnavailable(str(e)) from e
