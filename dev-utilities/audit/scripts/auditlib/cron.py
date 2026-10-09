from __future__ import annotations

import shlex

DEFAULT_TOOLS = (
    "Read",
    "Grep",
    "Glob",
    "Skill",
    "Agent",
    "Bash(python3 *audit.py *)",
    "Bash(git log *)",
    "Bash(git diff *)",
    "Bash(git ls-files *)",
)
ALLOWED_ACTS = ("report", "issues")


class CronError(ValueError):
    pass


def _check(schedule: str, act: str) -> None:
    if len(schedule.split()) != 5:
        raise CronError(f"schedule must have 5 fields: {schedule!r}")
    if act not in ALLOWED_ACTS:
        raise CronError(f"scheduled runs may only use {ALLOWED_ACTS}, not {act!r}")


def _escape_cron_percent(text: str) -> str:
    return text.replace("%", "\\%")


def build_entry(
    schedule: str, repo: str, budget: str, act: str = "report", tools: tuple[str, ...] = DEFAULT_TOOLS
) -> str:
    _check(schedule, act)
    prompt = f"/audit --act {act} --resume --new-window --budget {budget}"
    allowed = " ".join(shlex.quote(t) for t in tools)
    command = f"cd {shlex.quote(repo)} && claude -p {shlex.quote(prompt)} --allowedTools {allowed} >> .audit/cron.log 2>&1"
    return f"{schedule} {_escape_cron_percent(command)} # audit:{_escape_cron_percent(repo)}"


def merge(existing: str, entry: str, repo: str) -> str:
    marker = f"# audit:{_escape_cron_percent(repo)}"
    kept = [line for line in existing.splitlines() if not line.endswith(marker)]
    return "\n".join([*kept, entry]) + "\n"
