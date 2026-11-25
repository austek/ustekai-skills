from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from ctxlib.cost import SpendReport, SubagentSpend, build_report, build_subagent_spend
from ctxlib.guard import SESSION_ID, default_state_dir, guard_message, statusline_text
from ctxlib.overhead import rank_overhead
from ctxlib.usage import context_of, load_subagent_turns, load_turns

DEFAULT_THRESHOLD = 150_000
DEFAULT_WINDOW = 1_000_000
OVERHEAD_ROWS = 10
USAGE = "usage: ctxspend.py {report [--session ID] [--threshold N] [--transcript PATH] | guard | statusline}"


def env_int(name: str, default: int) -> int:
    try:
        return int(os.environ[name])
    except (KeyError, ValueError):
        return default


def claude_dir() -> Path:
    return Path(os.environ.get("CLAUDE_CONFIG_DIR") or Path.home() / ".claude")


def project_dir_name(cwd: Path) -> str:
    return re.sub(r"[^A-Za-z0-9]", "-", str(cwd))


def find_session(claude: Path, session_id: str | None, cwd: Path) -> Path | None:
    if session_id is not None:
        if not SESSION_ID.fullmatch(session_id):
            return None
        matches = (claude / "projects").glob(f"*/{session_id}.jsonl")
        return max(matches, key=lambda p: p.stat().st_mtime, default=None)
    project = claude / "projects" / project_dir_name(cwd)
    files = sorted(project.glob("*.jsonl"), key=lambda p: p.stat().st_mtime)
    return files[-1] if files else None


def money(value: float) -> str:
    return f"${value:,.2f}"


def saving_text(saving: float | None) -> str:
    return "n/a" if saving is None else money(saving)


def estimated_suffix(estimated: bool) -> str:
    return " (estimated)" if estimated else ""


def spend_lines(report: SpendReport, subagents: SubagentSpend) -> list[str]:
    total = report.total + subagents.total
    return [
        f"parent: {money(report.total)}{estimated_suffix(report.estimated)}",
        f"subagents: {money(subagents.total)} ({subagents.agents} agents)"
        + estimated_suffix(subagents.estimated),
        f"total: {money(total)}{estimated_suffix(report.estimated or subagents.estimated)}",
    ]


def format_report(report: SpendReport, subagents: SubagentSpend, context: int, items: list) -> str:
    crossing = report.crossing_turn if report.crossing_turn is not None else "none"
    lines = [
        f"turns (parent): {report.turns}",
        f"context (parent): {context:,} tokens",
        *spend_lines(report, subagents),
        f"fixed (parent): {money(report.fixed)}",
        f"growth (parent): {money(report.growth)}",
        f"crossing turn (parent): {crossing}",
        f"estimated saving if compacted there (parent): {saving_text(report.saving_if_compacted)}",
        "overhead (approximate tokens):",
    ]
    lines += [f"  {i.tokens:>7,}  {i.kind}  {i.name}" for i in items[:OVERHEAD_ROWS]]
    return "\n".join(lines)


def report_cmd(args: argparse.Namespace) -> tuple[int, str]:
    path = Path(args.transcript) if args.transcript else find_session(
        claude_dir(), args.session, Path.cwd()
    )
    if path is None or not path.is_file():
        return 1, "no session transcript found"
    threshold = args.threshold or env_int("CTX_GUARD_THRESHOLD", DEFAULT_THRESHOLD)
    turns = load_turns(path)
    report = build_report(turns, threshold)
    subagents = build_subagent_spend(load_subagent_turns(path))
    return 0, format_report(report, subagents, context_of(turns), rank_overhead(claude_dir()))


def guard_cmd(stdin: str) -> tuple[int, str]:
    message = guard_message(stdin, env_int("CTX_GUARD_THRESHOLD", DEFAULT_THRESHOLD), default_state_dir())
    return 0, json.dumps({"systemMessage": message}) if message else ""


def statusline_cmd(stdin: str) -> tuple[int, str]:
    return 0, statusline_text(stdin, env_int("CTX_WINDOW_TOKENS", DEFAULT_WINDOW))


def never_fail(command, stdin: str) -> tuple[int, str]:
    try:
        return command(stdin)
    except Exception:  # noqa: BLE001
        return 0, ""


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="ctxspend.py", usage=USAGE, exit_on_error=False)
    sub = p.add_subparsers(dest="cmd", required=True)
    rep = sub.add_parser("report")
    rep.add_argument("--session")
    rep.add_argument("--threshold", type=int)
    rep.add_argument("--transcript")
    sub.add_parser("guard")
    sub.add_parser("statusline")
    return p


def main(argv: list[str], stdin: str) -> tuple[int, str]:
    if argv[:1] == ["guard"]:
        return never_fail(guard_cmd, stdin)
    if argv[:1] == ["statusline"]:
        return never_fail(statusline_cmd, stdin)
    if argv[:1] != ["report"]:
        return 2, USAGE
    try:
        args = parser().parse_args(argv)
    except (argparse.ArgumentError, SystemExit):
        return 2, USAGE
    return report_cmd(args)


if __name__ == "__main__":
    reads_stdin = sys.argv[1:2] in (["guard"], ["statusline"])
    data = sys.stdin.read() if reads_stdin else ""
    code, out = main(sys.argv[1:], data)
    if out:
        print(out)
    sys.exit(code)
