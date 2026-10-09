from __future__ import annotations

from pathlib import Path

MARKERS = {
    "node": ("package.json",),
    "jvm": ("pom.xml", "build.gradle", "build.gradle.kts", "gradlew"),
    "scala": ("build.sbt",),
    "python": ("pyproject.toml", "setup.cfg", "requirements.txt", "Pipfile"),
    "rust": ("Cargo.toml",),
    "c": ("CMakeLists.txt", "configure.ac", "configure"),
}
_SKIP_DIRS = {"node_modules", "vendor", "target", "build", "dist"}


def _scan_dirs(root: Path) -> list[Path]:
    kids = [p for p in root.iterdir() if p.is_dir()]
    return [root, *(p for p in kids if not p.name.startswith(".") and p.name not in _SKIP_DIRS)]


def _names(root: Path) -> set[str]:
    return {child.name for d in _scan_dirs(root) for child in d.iterdir()}


def detect_stack(root: Path) -> list[str]:
    names = _names(root)
    return sorted(k for k, marks in MARKERS.items() if names.intersection(marks))
