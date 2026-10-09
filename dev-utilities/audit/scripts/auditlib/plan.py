from __future__ import annotations

import fnmatch
import posixpath
import re
import subprocess
from collections import Counter
from collections.abc import Mapping
from pathlib import Path

BYTES_PER_TOKEN = 4
ANALYSIS_MULTIPLIER = 6
SMALL_REPO_BYTES = 150_000
SHARD_CAP_TOKENS = 120_000
CONTAINERS = ("src", "lib", "packages", "modules", "apps", "services", "internal", "cmd")
_VENDOR_DIRS = {"vendor", "node_modules", "third_party", "dist", "build", "target"}
_LOCKFILES = {
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "Cargo.lock",
    "poetry.lock",
    "Pipfile.lock",
    "gradle.lockfile",
}
_GENERATED_MARKERS = ("DO NOT EDIT", "@generated", "Code generated", "auto-generated")
_BINARY_SUFFIXES = {
    ".png", ".jpg", ".jpeg", ".gif", ".ico", ".webp", ".svg", ".bmp",
    ".woff", ".woff2", ".ttf", ".otf", ".eot",
    ".zip", ".gz", ".tgz", ".bz2", ".xz", ".7z", ".jar", ".war", ".class",
    ".pdf", ".mp3", ".mp4", ".mov", ".so", ".dll", ".exe", ".bin",
}


def is_excluded(path: str, globs=()) -> bool:
    parts = path.split("/")
    name = parts[-1]
    return (
        bool(_VENDOR_DIRS.intersection(parts[:-1]))
        or name in _LOCKFILES
        or ".min." in name
        or posixpath.splitext(name)[1].lower() in _BINARY_SUFFIXES
        or any(fnmatch.fnmatch(path, g) for g in globs)
    )


def is_binary(head: bytes) -> bool:
    return b"\0" in head


def is_generated(head: str) -> bool:
    return any(marker in head for marker in _GENERATED_MARKERS)


def shard_key(path: str) -> str:
    parts = path.split("/")
    if len(parts) == 1:
        return "."
    return "/".join(parts[:2]) if parts[0] in CONTAINERS and len(parts) > 2 else parts[0]


def parse_churn(log: str) -> Counter:
    return Counter(p for p in re.split(r"[\0\n]", log) if p.strip())


def _tokens(size: int) -> int:
    return max(1, size // BYTES_PER_TOKEN)


def _group(files: list[tuple[str, int]]) -> dict[str, list[tuple[str, int]]]:
    groups: dict[str, list[tuple[str, int]]] = {}
    for path, size in files:
        groups.setdefault(shard_key(path), []).append((path, size))
    return groups


def _score(entries: list[tuple[str, int]], churn: Mapping[str, int]) -> int:
    return (1 + sum(churn.get(p, 0) for p, _ in entries)) * sum(s for _, s in entries)


def _chunks(entries: list[tuple[str, int]], cap_tokens: int) -> list[list[tuple[str, int]]]:
    out: list[list[tuple[str, int]]] = []
    cur: list[tuple[str, int]] = []
    used = 0
    for path, size in sorted(entries):
        t = _tokens(size)
        if cur and used + t > cap_tokens:
            out.append(cur)
            cur, used = [], 0
        cur.append((path, size))
        used += t
    return [*out, cur] if cur else out


def _unit(name: str, entries: list[tuple[str, int]], score: int, cap_tokens: int) -> dict:
    tokens = sum(_tokens(s) for _, s in entries)
    return {
        "unit": name,
        "files": [p for p, _ in entries],
        "est_tokens": tokens,
        "est_cost": tokens * ANALYSIS_MULTIPLIER,
        "score": score,
        "oversize": len(entries) == 1 and tokens > cap_tokens,
    }


def _split(key: str, entries: list[tuple[str, int]], score: int, cap_tokens: int) -> list[dict]:
    chunks = _chunks(entries, cap_tokens)
    names = [key if i == 0 else f"{key}#{i + 1}" for i in range(len(chunks))]
    return [_unit(n, c, score, cap_tokens) for n, c in zip(names, chunks)]


def build_plan(
    files: list[tuple[str, int]],
    churn: Mapping[str, int],
    small_repo_bytes: int = SMALL_REPO_BYTES,
    cap_tokens: int = SHARD_CAP_TOKENS,
) -> list[dict]:
    if not files:
        return []
    if sum(s for _, s in files) < small_repo_bytes:
        return [_unit(".", sorted(files), _score(files, churn), cap_tokens)]
    ranked = sorted(_group(files).items(), key=lambda kv: (-_score(kv[1], churn), kv[0]))
    return [u for k, e in ranked for u in _split(k, e, _score(e, churn), cap_tokens)]


def tracked_files(root: Path, runner=subprocess.run) -> list[tuple[str, int]]:
    out = runner(
        ["git", "-C", str(root), "ls-files", "-z"], capture_output=True, text=True, check=True
    ).stdout
    paths = [p for p in out.split("\0") if p and (root / p).is_file()]
    return [(p, (root / p).stat().st_size) for p in paths]


def churn(root: Path, runner=subprocess.run, days: int = 180) -> Counter:
    cmd = [
        "git", "-C", str(root), "log",
        f"--since={days}.days", "--name-only", "--relative", "-z", "--pretty=format:",
    ]
    result = runner(cmd, capture_output=True, text=True)
    return parse_churn(result.stdout) if result.returncode == 0 else Counter()


def changed_since(root: Path, ref: str, runner=subprocess.run) -> list[str]:
    cmd = ["git", "-C", str(root), "diff", "--name-only", "--relative", "-z", f"{ref}..HEAD"]
    result = runner(cmd, capture_output=True, text=True, check=True)
    return [p for p in result.stdout.split("\0") if p]
