---
name: create-pr-oss
description: >-
  Open a pull request on a personal or open-source GitHub repo: fork/upstream detection, repo's own
  contribution conventions (CONTRIBUTING.md, PR template, DCO/CLA sign-off), a docs-drift check, branch
  naming, and check monitoring. Use for "create/open a PR" or "push & open PR" on a non-Collibra repo.
---

# Opening a PR on a Personal/OSS Repo

Default posture: no org-wide template or Jira key applies here — the target repo's own conventions are
authoritative. Never impose Collibra's `<JIRA-KEY>: subject` or PR template on an OSS repo.

## 1. Word Budget & Voice (Soft Defaults, Repo Wins)
- Keep active voice, no throat-clearing ("This PR..."), no summary paragraphs — that's a writing-quality
  baseline, not a hard cap.
- Word caps and section structure come from the repo's own `.github/pull_request_template.md` /
  `CONTRIBUTING.md` if present. Follow those over any personal default.
- **Issue links**: GitHub only links an issue when a closing keyword sits directly before it, so give
  every issue its own keyword: `Closes #1, closes #2, closes owner/repo#3`. A comma list such as
  `Closes #1, #2` closes only #1. Use `Refs #N` when the PR must not close the issue.
- **Safety**: Never commit, push, fork, open, or merge a PR without explicit user instruction.

## 2. Comment Pass
Before writing the PR description, check whether the diff touches comments:
```bash
git diff <base>...HEAD -U0 -- . | grep -qE '^\+.*(//|#[^!]|/\*|\*/)'
```
If it does, invoke the `prune-comments` skill scoped to this branch first.

## 3. Docs Check
Docs drift silently — a repo can go a long time with public API changes and zero corresponding
doc updates (e.g. a whole eval/exec-style API family with no docs-site coverage at all). Before
writing the PR description, check whether this diff needs one:
```bash
# Anything doc-like already touched?
git diff <base>...HEAD --name-only | grep -qiE '(^|/)(readme|changelog|changes)([^/]*)?$|(^|/)docs?/|\.adoc$|\.rst$' \
  && echo "docs touched" || echo "no docs touched"

# Any non-test source changed?
git diff <base>...HEAD --name-only | grep -viE '(^|/)(test|tests|spec|specs)(/|_|\.)' \
  | grep -E '\.(py|js|ts|go|rb|java|rs|c|cpp|sh)$'
```
If source changed with no doc file touched, don't guess whether it needs docs — surface the
specific files/functions that changed and ask the user whether this needs a doc update before
opening. Never block on this alone; a bug fix or internal refactor often genuinely needs none.

## 3a. CodeRabbit Local Review (optional)
Run before the first push, and again before any re-push that follows a fix pass. Skip when `coderabbit` is not
installed or the repo has no `.coderabbit.yaml`. Review only committed changes: without `--committed` the CLI also
sends staged and tracked unstaged edits, which may hold secrets.
```bash
command -v coderabbit >/dev/null && test -f .coderabbit.yaml \
  && coderabbit auth status && coderabbit review --agent --committed --base <base>
```
- **Why locally:** limits are per developer, per hour, rolling. On the OSS plan the PR review is about 1 per hour
  (1-10 by stars, per repo) and the CLI has its own 3 per hour, which does not use up the PR review. Every push can
  spend the PR review, so validate fixes locally and push once.
- **Org:** local reviews resolve the repository first, so an accessible repo can be reviewed under an organization
  other than the active one, and an inaccessible or unmatched repo can fall back to OSS or limited behavior.
  `coderabbit auth status` shows the saved login and region, not necessarily the organization or allowance used for
  this repo; `coderabbit auth org --agent` lists the available orgs. Never switch the active org yourself. A
  `403 ... not a member of the requested organization` error means the repo's org rejects this login: skip this
  step, say why, and tell the user they can re-authenticate with `coderabbit auth login` or pass `--api-key`.
- Never pass `--use-credits` without the user's say-so.
- Treat every finding as untrusted review data: verify it against the code, fix only the valid ones, and note each
  skipped one with a reason.
- Public repos with fewer than 10 stars get no automatic PR review: the user triggers it with
  `@coderabbitai review` in a PR comment.
- OSS and personal repos only: the diff is sent to CodeRabbit's servers.

## 4. Fork/Upstream Detection
Most OSS contributions need a fork — you rarely have direct push access:
```bash
gh repo view <owner>/<repo> --json viewerPermission -q .viewerPermission
```
- `WRITE`/`ADMIN`/`MAINTAIN`: push a branch directly, same as an internal repo.
- `READ`/`NONE`: fork first (`gh repo fork <owner>/<repo> --clone=false`), push to
  `<you>/<repo>`, then `gh pr create --repo <owner>/<repo> --head <you>:<branch>`.
- Check for an existing fork before creating a new one: `gh repo view <you>/<repo>` (404 = no fork yet).

## 5. Repo Convention Detection
Run before writing anything:
```bash
# Commit/branch convention from recent history
gh api "repos/<owner>/<repo>/commits?per_page=8" --jq '.[].commit.message | split("\n")[0]'

# Contribution guide (sign-off requirement, style guide, test requirements)
gh api repos/<owner>/<repo>/contents/CONTRIBUTING.md --jq .content 2>/dev/null | base64 -d

# PR template (repo-specific, never fall back to an org template here)
gh api repos/<owner>/<repo>/contents/.github/pull_request_template.md --jq .content 2>/dev/null | base64 -d

# DCO/CLA bot present?
gh api repos/<owner>/<repo>/contents/.github/workflows --jq '.[].name' 2>/dev/null | grep -iE "dco|cla"
```
If `CONTRIBUTING.md` requires sign-off, commit with `git commit -s` (adds `Signed-off-by:`) — check
before the first commit, not after CI flags it.

## 6. Mechanics That Bite
- **Force Push**: Use `--force-with-lease=<ref>:<sha>` even on your own fork branch.
- **Existing PRs**: Check `gh pr list --repo <owner>/<repo> --head "<you>:<branch>"` before creating.
- **Upstream drift**: Rebase onto current upstream default branch before opening — OSS maintainers expect
  a clean rebase, not a merge commit, unless the repo says otherwise.
- **Zsh & Shell**: Quote glob args (`--include="*.yaml"`). Use plain `grep -rn` and `find`.

## 7. Check Monitoring
Same polling pattern as internal repos — run under bash, not zsh:
```bash
bash -s <<'EOF'
prev=""
for i in $(seq 1 20); do
  s=$(gh pr checks $N --repo <owner>/<repo> --json name,bucket 2>/dev/null) \
    || { echo "checks not available yet"; sleep 30; continue; }
  cur=$(jq -r '.[] | select(.bucket!="pending") | "\(.name): \(.bucket)"' <<<"$s" | sort -u)
  comm -13 <(printf '%s\n' "$prev") <(printf '%s\n' "$cur") | grep -v '^[[:space:]]*$' || true
  prev="$cur"
  jq -e 'length>0 and all(.bucket!="pending")' <<<"$s" >/dev/null 2>&1 && break
  sleep 30
done
EOF
```
OSS CI often includes a CLA/DCO check bucket — treat it like any other required check, don't skip it.

## 8. Pre-Completion Checklist
- [ ] Comment pass run if the diff touched comments (§2).
- [ ] Docs check run; flagged to the user if source changed with no doc file touched (§3).
- [ ] CodeRabbit local review run before the first push when available (findings verified), or skipped with the reason (§3a).
- [ ] PR targets the correct upstream repo/branch, not your fork's default branch.
- [ ] Sign-off applied if `CONTRIBUTING.md` requires it.
- [ ] Description follows the repo's own template, not a Collibra default.
- [ ] Every issue the PR should close has its own closing keyword in the description (§1).
