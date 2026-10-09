#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from auditlib import auditr, budget, cron, deps, findings, issues, ledger, plan, report, stack, state  # noqa: E402

CONFIG_PATH = Path.home() / ".config" / "audit" / "config.json"
ALL_LANES = ("ci", "docs", "deps", "security", "arch", "tests")
LANES_HELP = "ci,docs,deps,security,arch,tests|all"
EXCLUDED_DIRS = (".audit/", ".auditor/")


def load_config() -> dict:
    return json.loads(CONFIG_PATH.read_text()) if CONFIG_PATH.exists() else {}


def audit_dir(root: Path) -> Path:
    return root / ".audit"


def state_path(root: Path) -> Path:
    return audit_dir(root) / "state.json"


def _root(a) -> Path:
    return Path(a.path).resolve()


def _load_state(root: Path) -> dict:
    st = state.load(state_path(root))
    if not st:
        raise ValueError("no plan found, run `plan` first")
    return st


def _per_token(st: dict) -> float:
    return st.get("unit_per_token", 1.0)


def parse_lanes(text: str) -> list[str]:
    lanes = list(ALL_LANES) if text == "all" else [x for x in text.split(",") if x]
    unknown = [x for x in lanes if x not in ALL_LANES]
    if unknown:
        raise ValueError(f"unknown lanes: {unknown}; choose from {ALL_LANES} or all")
    return lanes


def parse_with(items: list[str]) -> dict:
    pairs = [i.split("=", 1) for i in items]
    if any(len(p) != 2 for p in pairs):
        raise ValueError("--with expects skill=args")
    return {k: v for k, v in pairs}


def _account(a) -> str:
    return budget.detect_account(os.environ) if a.account == "auto" else a.account


def _unit_per_token(resolved: dict, config: dict) -> float:
    if resolved["unit"] == "tokens":
        return 1.0
    price = config.get("usd_per_mtok")
    if not price:
        raise ValueError(
            "USD budgets need usd_per_mtok (blended USD per million tokens) in ~/.config/audit/config.json"
        )
    return float(price) / 1_000_000


def _head_bytes(root: Path, rel: str) -> bytes:
    with (root / rel).open("rb") as fh:
        return fh.read(512)


def _is_source(root: Path, rel: str) -> bool:
    head = _head_bytes(root, rel)
    text = head.decode("utf-8", errors="ignore")
    return not plan.is_binary(head) and not plan.is_generated(text)


def _exclude_path(root: Path) -> Path:
    cmd = ["git", "-C", str(root), "rev-parse", "--git-path", "info/exclude"]
    r = subprocess.run(cmd, capture_output=True, text=True)
    return root / r.stdout.strip() if r.returncode == 0 and r.stdout.strip() else root / ".git" / "info" / "exclude"


def ensure_git_excluded(root: Path) -> None:
    exclude = _exclude_path(root)
    if not exclude.parent.is_dir():
        return
    current = exclude.read_text() if exclude.exists() else ""
    missing = [e for e in EXCLUDED_DIRS if e not in current.splitlines()]
    if not missing:
        return
    sep = "" if not current or current.endswith("\n") else "\n"
    exclude.write_text(current + sep + "\n".join(missing) + "\n")


def _auditignore(root: Path) -> list[str]:
    path = root / ".auditignore"
    return [l.strip() for l in path.read_text().splitlines() if l.strip()] if path.exists() else []


def _eligible(root: Path, a) -> list[tuple[str, int]]:
    globs = [*a.exclude, *_auditignore(root)]
    files = [(p, s) for p, s in plan.tracked_files(root) if not plan.is_excluded(p, globs)]
    files = [(p, s) for p, s in files if _is_source(root, p)]
    if a.since:
        changed = set(plan.changed_since(root, a.since))
        files = [x for x in files if x[0] in changed]
    return files


def cmd_preflight(a) -> int:
    root, account = _root(a), _account(a)
    resolved = budget.resolve_budget(a.budget, account, load_config())
    out = {
        "root": str(root),
        "stacks": stack.detect_stack(root),
        "account": account,
        "budget": resolved,
        "budget_mismatch": budget.mismatch(resolved, account),
        "lanes": parse_lanes(a.lanes),
    }
    print(json.dumps(out, indent=2))
    return 0


def _new_plan_state(root: Path, a, units: list[dict], resolved: dict) -> dict:
    meta_keys = ("files", "est_cost", "score", "oversize")
    base = state.new_state([u["unit"] for u in units], resolved)
    return {
        **base,
        "root": str(root),
        "units_meta": {u["unit"]: {k: u[k] for k in meta_keys} for u in units},
        "lanes": parse_lanes(a.lanes),
        "lanes_done": [],
        "act": a.act,
        "with": parse_with(a.with_),
        "stacks": stack.detect_stack(root),
        "ratios": [],
    }


def _resume_existing(root: Path, a) -> bool:
    existing = state.load(state_path(root))
    if not (a.resume and existing and state.pending(existing)):
        return False
    kept = {**existing, "spent": 0} if a.new_window else existing
    state.atomic_write(state_path(root), kept)
    print(json.dumps({"resumed": True, "spent": kept["spent"], "pending": len(state.pending(kept))}))
    return True


def _summary(units: list[dict], resolved: dict, per_token: float) -> dict:
    total = sum(u["est_cost"] for u in units) * per_token
    return {"units": len(units), "estimated_cost": total, "budget": resolved,
            "fits_budget": total <= resolved["amount"]}


def _fresh_plan(root: Path, a) -> int:
    config = load_config()
    resolved = budget.resolve_budget(a.budget, _account(a), config)
    per_token = _unit_per_token(resolved, config)
    units = plan.build_plan(_eligible(root, a), plan.churn(root), a.small_repo_bytes)
    units = units[: a.max_shards] if a.max_shards else units
    st = {**_new_plan_state(root, a, units, resolved), "unit_per_token": per_token}
    state.atomic_write(state_path(root), st)
    ensure_git_excluded(root)
    print(json.dumps(_summary(units, resolved, per_token), indent=2))
    return 0


def cmd_plan(a) -> int:
    root = _root(a)
    if a.shard != "dir":
        raise ValueError("only --shard dir is implemented in v1")
    if _resume_existing(root, a):
        return 0
    return _fresh_plan(root, a)


def _ratio(st: dict) -> float:
    ratios = st.get("ratios", [])
    return sum(ratios) / len(ratios) if ratios else 1.0


def _estimates(st: dict) -> dict:
    scale = _ratio(st) * _per_token(st)
    return {u: m["est_cost"] * scale for u, m in st["units_meta"].items()}


def _candidates(root: Path, unit: str) -> list[dict]:
    path = audit_dir(root) / "auditr" / f"{findings.slug(unit)}.json"
    return json.loads(path.read_text()) if path.exists() else []


def _shard_view(root: Path, st: dict, unit: str) -> dict:
    return {
        "unit": unit,
        "files": st["units_meta"].get(unit, {}).get("files", []),
        "candidates": _candidates(root, unit) if unit else [],
        "with": st["with"],
    }


def _progress_view(st: dict) -> dict:
    amount = st["budget"]["amount"]
    return {
        "spent": st["spent"],
        "budget": st["budget"],
        "budget_left": amount - st["spent"],
        "lane_ok": st["spent"] < amount * ledger.SOFT_LIMIT,
        "lanes_pending": [x for x in st["lanes"] if x not in st.get("lanes_done", [])],
    }


def cmd_next(a) -> int:
    root = _root(a)
    st = _load_state(root)
    verdict, unit = ledger.next_unit(st, _estimates(st))
    print(json.dumps({"verdict": verdict, **_shard_view(root, st, unit), **_progress_view(st)}))
    return 0


def _ratios_after(st: dict, a) -> list[float]:
    old = st.get("ratios", [])
    if a.status != "done":
        return old
    return [*old, a.spent / max(1, st["units_meta"][a.unit]["est_cost"])]


def _read_findings(path: str) -> list[dict]:
    return json.loads(Path(path).read_text())


def cmd_record(a) -> int:
    root = _root(a)
    st = _load_state(root)
    if a.unit not in st["units_meta"]:
        raise ValueError(f"unknown unit {a.unit!r}")
    if a.findings:
        findings.write_unit(audit_dir(root) / "findings", a.unit, _read_findings(a.findings))
    updated = state.mark(st, a.unit, a.status, a.spent * _per_token(st))
    state.atomic_write(state_path(root), {**updated, "ratios": _ratios_after(st, a)})
    print(json.dumps({"spent": updated["spent"]}))
    return 0


def cmd_record_lane(a) -> int:
    root = _root(a)
    st = _load_state(root)
    if a.lane not in st["lanes"]:
        raise ValueError(f"lane {a.lane!r} is not in the plan: {st['lanes']}")
    if a.findings:
        findings.write_unit(audit_dir(root) / "findings", f"lane-{a.lane}", _read_findings(a.findings))
    updated = state.mark_lane(st, a.lane, a.spent * _per_token(st))
    state.atomic_write(state_path(root), updated)
    print(json.dumps({"spent": updated["spent"], "lanes_done": updated["lanes_done"]}))
    return 0


def cmd_deps(a) -> int:
    root = _root(a)
    st = _load_state(root)
    found, skipped = deps.run_deps(st["stacks"], root)
    findings.write_unit(audit_dir(root) / "findings", "lane-deps", found)
    if "deps" in st["lanes"]:
        state.atomic_write(state_path(root), state.mark_lane(st, "deps", 0))
    print(json.dumps({"findings": len(found), "skipped": skipped}))
    return 0


def _owner(st: dict) -> dict:
    return {f: unit for unit, meta in st["units_meta"].items() for f in meta["files"]}


def _by_unit(st: dict, items: list[dict]) -> dict[str, list[dict]]:
    owner = _owner(st)
    grouped: dict[str, list[dict]] = {}
    for item in items:
        if item["file"] in owner:
            grouped.setdefault(owner[item["file"]], []).append(item)
    return grouped


def _write_auditr(root: Path, st: dict, items: list[dict]) -> None:
    auto, candidates = auditr.split_judged(items)
    for unit, group in _by_unit(st, auto).items():
        findings.write_unit(audit_dir(root) / "findings", f"auditr-{unit}", group)
    for unit, group in _by_unit(st, candidates).items():
        findings.write_unit(audit_dir(root) / "auditr", unit, group)


def cmd_auditr(a) -> int:
    root = _root(a)
    st = _load_state(root)
    if not auditr.available():
        print(json.dumps({"available": False, "findings": 0}))
        return 0
    try:
        items = auditr.scan(root)
    except auditr.AuditrUnavailable as e:
        print(json.dumps({"available": False, "findings": 0, "error": str(e)}))
        return 0
    _write_auditr(root, st, items)
    auto, candidates = auditr.split_judged(items)
    print(json.dumps({"available": True, "findings": len(auto), "candidates": len(candidates)}))
    return 0


def _remote(root: Path) -> str:
    r = subprocess.run(["git", "-C", str(root), "remote", "get-url", "origin"], capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else ""


def _drafts(groups: dict) -> list[dict]:
    return [issues.render(unit, items) for unit, items in groups.items()]


def cmd_act(a) -> int:
    root = _root(a)
    st = _load_state(root)
    groups = issues.group(findings.load_all(audit_dir(root) / "findings"), _owner(st))
    tracker = issues.detect_tracker(_remote(root)) if a.tracker == "auto" else a.tracker
    name = "issues.jira.json" if tracker == "jira" else "issues.drafts.json"
    (audit_dir(root) / name).write_text(json.dumps(_drafts(groups), indent=2))
    if tracker == "jira":
        print(f"jira drafts written to {audit_dir(root) / name}; file them with the collibra-jira-ticket skill")
        return 0
    return _file_github(groups, a)


def _file_github(groups: dict, a) -> int:
    gh = issues.GitHub()
    actions = issues.plan_actions(groups, gh, a.max_issues)
    print(json.dumps([{k: x[k] for k in ("unit", "title", "action")} for x in actions], indent=2))
    if a.confirm:
        issues.apply_actions(actions, gh)
    else:
        print("dry run: pass --confirm to file", file=sys.stderr)
    return 0


def cmd_report(a) -> int:
    root = _root(a)
    st = _load_state(root)
    metrics_path = audit_dir(root) / "metrics.json"
    metrics = json.loads(metrics_path.read_text()) if metrics_path.exists() else {}
    items = findings.load_all(audit_dir(root) / "findings")
    out = audit_dir(root) / "report.md"
    out.write_text(report.render(items, st["budget"], st["spent"], metrics))
    print(out)
    return 0


def cmd_usage(a) -> int:
    paths = [Path(p) for p in a.transcripts]
    files = [f for p in paths for f in ([p] if p.is_file() else sorted(p.rglob("*.jsonl")))]
    print(ledger.usage_tokens(files))
    return 0


def cmd_reset(a) -> int:
    found = ledger.find_reset(a.message, datetime.now().astimezone())
    print(found[0].isoformat() if found else "")
    return 0 if found else 1


def cmd_schedule(a) -> int:
    root = _root(a)
    entry = cron.build_entry(a.cron, str(root), a.budget, a.act)
    if not a.install:
        print(entry)
        return 0
    current = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
    existing = current.stdout if current.returncode == 0 else ""
    subprocess.run(["crontab", "-"], input=cron.merge(existing, entry, str(root)), text=True, check=True)
    print(f"installed: {entry}")
    return 0


def _add_common(p) -> None:
    p.add_argument("path", nargs="?", default=".", help="repo root (default: .)")


def _add_budget(p) -> None:
    p.add_argument("--budget", default="", metavar="2M|500k|30%|$5",
                   help="spend cap: tokens, percent of plan ceiling, or USD needing usd_per_mtok in config "
                        "(default: 25%% of plan_ceiling_tokens, else 2M tokens; enterprise: default_usd)")
    p.add_argument("--account", default="auto", choices=["auto", "subscription", "enterprise"],
                   help="how to interpret the budget (default: auto-detect from env)")


def _add_plan_selection(p) -> None:
    p.add_argument("--since", default="", metavar="REF", help="delta mode: only files changed since REF")
    p.add_argument("--max-shards", type=int, default=0, metavar="N", help="cap shard count (default: no cap)")
    p.add_argument("--exclude", action="append", default=[], metavar="GLOB",
                   help="extra exclude glob, repeatable; .auditignore is also read")
    p.add_argument("--small-repo-bytes", type=int, default=plan.SMALL_REPO_BYTES, metavar="BYTES",
                   help="below this total size the repo is one shard")


def _add_plan_scope(p) -> None:
    p.add_argument("--act", default="report", choices=["report", "issues", "fix", "pr"],
                   help="autonomy level (default: report)")
    p.add_argument("--lanes", default="deps", metavar=LANES_HELP, help="repo-wide lanes to run (default: deps)")
    p.add_argument("--shard", default="dir", metavar="dir", help="shard axis; only dir is implemented in v1")
    p.add_argument("--with", dest="with_", action="append", default=[], metavar="skill=args",
                   help="forward args to a sub-skill, repeatable (e.g. code-review=high)")


def _build_plan_parser(sub) -> None:
    p = sub.add_parser("plan", help="shard the repo, rank by churn x size, write .audit/state.json")
    _add_common(p)
    _add_budget(p)
    _add_plan_selection(p)
    _add_plan_scope(p)
    p.add_argument("--resume", action="store_true",
                   help="continue pending shards from .audit/state.json; replans when none are pending")
    p.add_argument("--new-window", action="store_true",
                   help="with --resume: reset spend to 0 for a new budget window, keeping shard progress")
    p.set_defaults(handler=cmd_plan)


def _build_basic_parsers(sub) -> None:
    pre = sub.add_parser("preflight", help="detect stack, account and budget; print summary")
    _add_common(pre)
    _add_budget(pre)
    pre.add_argument("--lanes", default="deps", metavar=LANES_HELP, help="lanes to validate")
    pre.set_defaults(handler=cmd_preflight)
    for name, handler, text in (("next", cmd_next, "print the next shard to run, or why to stop"),
                                ("deps", cmd_deps, "run the deps lane and write findings"),
                                ("auditr", cmd_auditr, "optional zero-token pre-pass: run auditr, split per shard"),
                                ("report", cmd_report, "render .audit/report.md")):
        p = sub.add_parser(name, help=text)
        _add_common(p)
        p.set_defaults(handler=handler)


def _build_record_parsers(sub) -> None:
    rec = sub.add_parser("record", help="record a finished shard and its spend")
    _add_common(rec)
    rec.add_argument("--unit", required=True, help="shard name from `next`")
    rec.add_argument("--status", default="done", choices=["done", "failed"], help="shard outcome")
    rec.add_argument("--spent", type=float, required=True,
                     help="tokens spent, including on failure (converted to the budget unit)")
    rec.add_argument("--findings", default="", metavar="FILE", help="JSON array of findings for this shard")
    rec.set_defaults(handler=cmd_record)
    lane = sub.add_parser("record-lane", help="record a finished lane, its findings and spend")
    _add_common(lane)
    lane.add_argument("--lane", required=True, choices=ALL_LANES, help="lane name from `next.lanes_pending`")
    lane.add_argument("--spent", type=float, default=0, help="tokens spent (converted to the budget unit)")
    lane.add_argument("--findings", default="", metavar="FILE", help="JSON array of findings for this lane")
    lane.set_defaults(handler=cmd_record_lane)


def _build_act_parser(sub) -> None:
    act = sub.add_parser("act", help="turn findings into issues (dry-run unless --confirm)")
    _add_common(act)
    act.add_argument("--tracker", default="auto", choices=["auto", "github", "jira"], help="auto: jira for collibra remotes")
    act.add_argument("--confirm", action="store_true", help="actually file issues")
    act.add_argument("--max-issues", type=int, default=10, metavar="N",
                     help="cap on issues created or updated per run (default: 10)")
    act.set_defaults(handler=cmd_act)


def _build_util_parsers(sub) -> None:
    usage = sub.add_parser("usage", help="sum token usage from transcript files or directories")
    usage.add_argument("transcripts", nargs="+", metavar="PATH")
    usage.set_defaults(handler=cmd_usage)
    reset = sub.add_parser("reset", help="parse a rate-limit message into the reset time")
    reset.add_argument("--message", required=True)
    reset.set_defaults(handler=cmd_reset)


def _build_schedule_parser(sub) -> None:
    sched = sub.add_parser("schedule", help="print or install a read-only cron entry")
    _add_common(sched)
    sched.add_argument("--cron", required=True, metavar='"0 3 * * *"', help="five-field cron schedule")
    sched.add_argument("--budget", default="2M", metavar="2M|$5", help="budget passed to each scheduled run")
    sched.add_argument("--act", default="report", choices=["report", "issues"], help="scheduled runs never fix or open PRs")
    sched.add_argument("--install", action="store_true", help="merge into the user crontab")
    sched.set_defaults(handler=cmd_schedule)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="audit", description="Budgeted, sharded repo audit.")
    sub = parser.add_subparsers(dest="command", required=True)
    _build_plan_parser(sub)
    _build_basic_parsers(sub)
    _build_record_parsers(sub)
    _build_act_parser(sub)
    _build_util_parsers(sub)
    _build_schedule_parser(sub)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.handler(args)
    except (budget.BudgetError, issues.TrackerError, cron.CronError, ValueError,
            FileNotFoundError, subprocess.CalledProcessError) as e:
        print(f"audit: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
