---
name: audit
description: Budget-fenced, sharded repo audit that can report, file issues, fix in worktrees or open PRs. Use for "audit this repo", "improve this repo", "full audit", or scheduled repo-health runs.
argument-hint: "[path] [--act report|issues|fix|pr] [--budget 2M|30%|$5] [--lanes ci,docs,deps,security,arch,tests|all] [--since REF] [--max-shards N] [--with skill=args] [--resume] [--schedule CRON]"
---

# audit

Run the deterministic phases through `audit.py` and spend LLM tokens only on shards and lanes. `AUDIT` below is `python3 <this skill's base directory>/scripts/audit.py`.

## 0. Ground rules

- Default `--act report`. `issues` is a dry run until the user passes `--confirm`. `fix` edits worktrees and never commits. Do not open PRs (`pr`) until the user confirms.
- Never commit, push or open PRs unless the user asked. No `Co-Authored-By`, no AI-authorship footers in commits, PRs or issues.
- Unattended (cron) runs only `report` or dry-run `issues`.
- Never read or modify `.audit/state.json` by hand; use the subcommands.

## 1. Standards ingestion (once)

Detect stacks with `AUDIT preflight <path>`. For each detected stack, load the user's standards if present: `.claude/commands/{jvm,scala,python,rust,c}.md`, `~/.claude/commands/...`, and the persona skills `{java,python,rust,scala}-{coding-standards,testing,tooling}`. Treat their rules as audit criteria with rule ids prefixed `standards/`.

## 2. Plan and cost gate

```
AUDIT preflight <path> --budget <B> --lanes <L>
AUDIT plan <path> --budget <B> --lanes <L> --act <A> [--since REF] [--max-shards N] [--with skill=args ...] [--resume]
```

- If `budget_mismatch` is true, tell the user a USD budget cannot be enforced on a subscription account and ask for a token budget.
- If `fits_budget` is false, say how many shards will run before the budget stops the loop, then continue.
- Zero units means nothing to audit; still run lanes and report.

## 3. Shard loop

Optional pre-pass, zero tokens: run `AUDIT auditr <path>` once after planning. If it reports `"available": true`, its deterministic (`auto`) findings are already recorded as findings, and its unjudged `candidate` findings (confidence 0.4) are returned per shard in `AUDIT next` under `candidates`. Give the candidates to the sub-agent: it confirms real ones into its findings array and drops the rest, so unjudged candidates never reach the report or issues. If `"available": false`, continue silently.

Repeat until `verdict` is not `run`:

1. `AUDIT next <path>` returns `{verdict, unit, files, candidates, with, spent, budget, budget_left, lane_ok, lanes_pending}`.
2. `verdict` `stop`, `exhausted` or `done`: leave the loop and go to section 5. Say which one.
3. Otherwise review only `files` for that unit with one sub-agent. Lenses: correctness via `/code-review <args>` scoped to those files, where `<args>` is `with["code-review"]` if set, otherwise `high --max-findings all` (always pass `--max-findings` explicitly because the setting is sticky across sessions; never default to `max`), the stack's standards rules from section 1, and the stack's `*-testing` rules for the unit's tests.
4. The agent writes a JSON array of findings (schema below) to a temp file. Measure its spend with `AUDIT usage <transcript dirs>` before and after, and take the difference.
5. `AUDIT record <path> --unit <unit> --status done --spent <delta> --findings <file>`. If the agent died, record `--status failed` with the tokens it actually burned: failed runs still count against the budget, and only `done` runs calibrate future estimates. `--spent` is always tokens; the CLI converts to USD for USD budgets.
6. On a 429 or session-limit message, run `AUDIT reset --message "<text>"`. If it prints nothing and exits 1, the wording is not recognised (for example a weekly limit): do not guess a time; interactive runs wait 30 minutes and retry `AUDIT next`, unattended runs stop. Interactive: sleep until that time then continue the loop. Unattended: stop; the next scheduled run uses `--resume`.

Finding fields: `rule`, `file`, `anchor` (symbol name or hunk hash, never a line number), `severity` (`blocker|high|medium|low`), `confidence` (0-1), `effort` (`S|M|L`), `fixable` (bool), `summary`, optional `evidence`.

## 4. Lanes

Run each lane in `lanes_pending` (from `AUDIT next`) once, after the shards, only while `lane_ok` is true. A lane that would start after the soft limit is skipped and reported as skipped:

| Lane | How |
|---|---|
| deps | `AUDIT deps <path>` (script; triage the findings by reachability) |
| ci | read the CI config; on Collibra repos use `collibra-jenkins` |
| docs | `technical-documentation` against README and docs |
| security | `/security-review` plus secrets and injection checks |
| arch | `architecture:codebase-design`; Python repos also `python-clean-architecture:review-architecture` |
| tests | coverage by module, flaky or slow tests, pyramid balance, missing e2e journeys, using the stack's `*-testing` skill |

Record each lane with `AUDIT record-lane <path> --lane <name> --spent <tokens> --findings <file>`. It validates the findings, counts the spend toward the budget and removes the lane from `lanes_pending`. `AUDIT deps` marks the `deps` lane itself. Never write files under `.audit/findings/` by hand. Write measured numbers to `.audit/metrics.json` keyed by exactly these names (any other key renders as "not measured"): `Test Coverage (Line / Branch)`, `Code Duplication`, `Bugs / Blocker Issues`, `Security Vulnerabilities (SAST/Deps)`, `Linter / Compiler Warnings`.

## 5. Act

- `report`: `AUDIT report <path>` and show the path.
- `issues`: `AUDIT act <path> --tracker auto --max-issues N`. Show the dry-run table. File only after the user confirms, then re-run with `--confirm`. For `jira` the script writes `.audit/issues.jira.json`; create the stories with `collibra-jira-ticket`, one per draft, each carrying its `audit-fp:` label.
- `fix`: one git worktree per shard with fixable findings, apply fixes, run the project's tests and lint, leave edits uncommitted, summarize per worktree.
- `pr`: only with `--confirm`: as `fix`, then one PR per shard via `create-pr-collibra` or `create-pr-oss`.

Always finish with `AUDIT report <path>` and the budget summary.

## 6. Forwarding args to other skills

`--with skill=args` values are returned by `next` under `with`. Pass them verbatim as that skill's arguments (for example `code-review=max --max-findings all` on a hot shard). Skills' own `argument-hint` text is the authority for valid args; do not invent flags.

## 7. Scheduling

`--schedule "<cron>"` runs `AUDIT schedule <path> --cron "<cron>" --budget <B>` to print the entry, and `--install` to merge it into the crontab. Scheduled runs use `--act report` or dry-run `issues` only (never `fix` or `pr`), start a new budget window each run (`--resume --new-window`: pending shards continue, spend resets, and a finished plan is replanned), and only allow scoped Bash patterns, never bare `Bash`.
