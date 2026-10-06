---
description: Run a CodeRabbit audit scoped to uncommitted changes, a path, a PR, a branch, or the full repo, and summarize the findings
argument-hint: "[path|branch|#PR|full repo] [--limit N] (all optional; defaults to uncommitted changes, limit 100)"
allowed-tools: Bash, Read
---

Run a CodeRabbit review via the `coderabbitFullAudit` script (installed as part of the `local` dotfiles package) and report the results. The script resolves the same five scopes this command does and keeps every review call under CodeRabbit's free-tier file-count ceiling (100 files) by batching into multiple calls when a scope has more files than the limit allows. When CodeRabbit reports a rate limit, the script sleeps for the reported wait time (usually under an hour, plus a 1-minute margin) and retries, up to 6 times per call; do not cancel a run that looks idle.

### Step 1: Preconditions
1. Confirm the `coderabbit` CLI is on `PATH` (`command -v coderabbit`) and authenticated (`coderabbit auth status` or equivalent). If not installed, tell the user to run the `personal` profile's `setup.sh`, which installs it; if not authenticated, tell them to run `coderabbit auth login`.
2. Confirm `coderabbitFullAudit` is on `PATH` (`command -v coderabbitFullAudit`). It's installed as part of the `local` dotfiles package; if missing, tell the user to (re-)run `dotfiles-setup install`.
3. Only for the full-repo and path scopes — confirm the current directory is a git repository and `.coderabbit.yaml` is tracked on the current branch. If either is missing, stop and tell the user what's missing; `coderabbitFullAudit` also checks this itself and exits with a clear error.

### Step 2: Resolve scope and limit from `$ARGUMENTS`
If `$ARGUMENTS` contains `--limit <N>` (anywhere in the string), pull it out and remember it as `LIMIT`; it's forwarded to `coderabbitFullAudit --limit <N>` in Step 3 regardless of scope. Leave it out entirely to use the script's own default (100, CodeRabbit's free-tier ceiling — values above it are clamped down).

Resolve whatever remains of `$ARGUMENTS` to a target in this order — stop at the first match:

1. **Nothing left** → run `git status --porcelain`. If it's empty, tell the user there are no uncommitted changes to audit and stop — do not fall back to a full-repo audit. Otherwise scope to uncommitted changes.
2. **A filesystem path** (file or directory that exists on disk) → scope to that path.
3. **A PR reference** (a number, or a `github.com/.../pull/N` URL) → scope to that pull request.
4. **A branch name** (matches an existing local or remote ref) → scope to that branch's diff.
5. **`full repo` / `repo`** → the entire repo is in scope.

### Step 3: Run the audit
Run `coderabbitFullAudit` via Bash from the repo root with the flag matching the resolved scope, plus `--limit <LIMIT>` if Step 2 found one:

- **Uncommitted changes**: `coderabbitFullAudit --uncommitted`.
- **A path**: `coderabbitFullAudit --path <path>` — a full-content audit of just that path, not a diff, so it surfaces pre-existing issues in untouched code too (the opposite trade-off from the uncommitted/PR/branch scopes).
- **A PR reference**: `coderabbitFullAudit --pr <number-or-url>` — tries CodeRabbit's existing review of that PR first (fast), and only falls back to a live diff review if none exists.
- **A branch name**: `coderabbitFullAudit --branch <branch>`, reviewing the current checkout's diff against that branch.
- **Full repo**: `coderabbitFullAudit` (no scope flag) — this is the scope most likely to exceed the file limit and get batched, and can take several minutes on a large repo; do not cancel early.

Every scope writes to `~/.claude/scratches/handoff/coderabbit_audit.md`; a batched run appends each batch's findings there under its own `## Batch N/M (k files)` heading.

### Step 4: Summarize
Read `~/.claude/scratches/handoff/coderabbit_audit.md` and present the findings grouped by severity (blocker/critical first), each with the file:line it applies to and a one-line fix suggestion. Do not restate findings CodeRabbit marked as nitpicks unless the user asks for them. If the file has multiple `## Batch` sections, summarize across all of them, not just the first.
