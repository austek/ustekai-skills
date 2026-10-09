from __future__ import annotations

import hashlib
import json
import posixpath
import re
from pathlib import Path

REQUIRED = ("rule", "file", "anchor", "severity", "confidence", "effort", "fixable", "summary")
SEVERITIES = ("blocker", "high", "medium", "low")
EFFORTS = ("S", "M", "L")


class FindingError(ValueError):
    pass


def normalize_path(path: str) -> str:
    unified = re.sub(r"^/{2,}", "/", path.replace("\\", "/"))
    return posixpath.normpath(unified)


def fingerprint(rule: str, file: str, anchor: str) -> str:
    raw = "\0".join((rule, normalize_path(file), anchor))
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def _check(finding: dict) -> None:
    missing = [k for k in REQUIRED if k not in finding]
    if missing:
        raise FindingError(f"missing fields: {missing}")
    if finding["severity"] not in SEVERITIES:
        raise FindingError(f"bad severity: {finding['severity']!r}")
    if finding["effort"] not in EFFORTS:
        raise FindingError(f"bad effort: {finding['effort']!r}")
    if not 0 <= finding["confidence"] <= 1:
        raise FindingError(f"bad confidence: {finding['confidence']!r}")


def validate(finding: dict) -> dict:
    _check(finding)
    fp = fingerprint(finding["rule"], finding["file"], finding["anchor"])
    return {**finding, "file": normalize_path(finding["file"]), "fingerprint": fp}


def slug(unit: str) -> str:
    clean = re.sub(r"[^A-Za-z0-9._-]+", "_", unit).strip("_")
    if clean and clean == unit:
        return clean
    digest = hashlib.sha1(unit.encode()).hexdigest()[:6]
    return f"{clean or 'root'}-{digest}"


def write_unit(findings_dir: Path, unit: str, items: list[dict]) -> Path:
    path = findings_dir / f"{slug(unit)}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps([validate(i) for i in items], indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def _load_file(path: Path) -> list[dict]:
    try:
        return [validate(f) for f in json.loads(path.read_text(encoding="utf-8"))]
    except (FindingError, KeyError, TypeError) as e:
        raise FindingError(f"{path.name}: {e}") from e


def load_all(findings_dir: Path) -> list[dict]:
    return [f for p in sorted(findings_dir.glob("*.json")) for f in _load_file(p)]
