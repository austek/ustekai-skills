import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from ctxlib.cost import SpendReport, build_report
from ctxlib.guard import SESSION_ID, default_state_dir, guard_message, statusline_text
from ctxlib.overhead import rank_overhead
from ctxlib.usage import latest_context, load_turns

DEFAULT_THRESHOLD = 150_000
DEFAULT_WINDOW = 1_000_000
OVERHEAD_ROWS = 10
USAGE = "usage: ctxspend.py {report [--session ID] [--threshold N] | guard | statusline}"


def env_int(name: str, default: int) -> int:
    try:
        return int(os.environ[name])
    except (KeyError, ValueError):
        return default


def claude_dir() -> Path:
    return Path(os.environ.get("CLAUDE_CONFIG_DIR") or Path.home() / ".claude")


def project_dir_name(cwd: Path) -> str:
    return str(cwd).replace("/", "-").replace(".", "-")


def find_session(claude: Path, session_id: str | None, cwd: Path) -> Path | None:
    if session_id is not None:
        if not SESSION_ID.fullmatch(session_id):
            return None
        return next(iter(sorted((claude / "projects").glob(f"*/{session_id}.jsonl"))), None)
    project = claude / "projects" / project_dir_name(cwd)
    files = sorted(project.glob("*.jsonl"), key=lambda p: p.stat().st_mtime)
    return files[-1] if files else None


def money(value: float) -> str:
    return f"${value:,.2f}"


def format_report(report: SpendReport, context: int, items: list) -> str:
    lines = [
        f"turns: {report.turns}",
        f"context: {context:,} tokens",
        f"total: {money(report.total)}" + (" (estimated)" if report.estimated else ""),
        f"fixed: {money(report.fixed)}",
        f"growth: {money(report.growth)}",
        f"crossing turn: {report.crossing_turn if report.crossing_turn is not None else 'none'}",
        f"estimated saving if compacted there: {money(report.saving_if_compacted)}",
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
    report = build_report(load_turns(path), threshold)
    items = rank_overhead(claude_dir())
    return 0, format_report(report, latest_context(path), items)


def guard_cmd(stdin: str) -> tuple[int, str]:
    message = guard_message(stdin, env_int("CTX_GUARD_THRESHOLD", DEFAULT_THRESHOLD), default_state_dir())
    return 0, json.dumps({"systemMessage": message}) if message else ""


def statusline_cmd(stdin: str) -> tuple[int, str]:
    return 0, statusline_text(stdin, env_int("CTX_WINDOW_TOKENS", DEFAULT_WINDOW))


def safely(command, stdin: str) -> tuple[int, str]:
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
        return safely(guard_cmd, stdin)
    if argv[:1] == ["statusline"]:
        return safely(statusline_cmd, stdin)
    if argv[:1] != ["report"]:
        return 2, USAGE
    try:
        args = parser().parse_args(argv)
    except (argparse.ArgumentError, SystemExit):
        return 2, USAGE
    return report_cmd(args)


if __name__ == "__main__":
    data = "" if sys.stdin.isatty() else sys.stdin.read()
    code, out = main(sys.argv[1:], data)
    if out:
        print(out)
    sys.exit(code)
