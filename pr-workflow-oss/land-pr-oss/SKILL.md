---
name: land-pr-oss
description: >-
  Shepherd your own open PR on a personal/OSS repo to mergeable: poll CI, pull failing-check logs,
  fetch reviewer feedback (inline threads + review verdicts), draft fixes, push after confirmation,
  reply to and resolve the threads that fix actually addresses, re-checking for docs drift each
  loop. Use for "check my PR", "is my PR green", "address the review comments", or "land this PR".
argument-hint: "[PR number|URL] (optional; defaults to the current branch's PR)"
---

# Landing Your Own PR on a Personal/OSS Repo

Default posture: you're the PR author. This skill drives the PR toward merge — it does not review someone
else's code (`review-pr-oss` for that) and does not open new PRs (`create-pr-oss` for that).

## 1. Resolve Target PR
Identify via arg (`/land-pr-oss 456`, URL) or current branch:
```bash
gh pr view --json number,url,headRefName,baseRefName,headRepositoryOwner,isCrossRepository
```
Work in a full checkout of the repo. Use a fresh clone, not `git worktree`, when the build refuses to run outside a
directory named after the repo or needs `origin/<base>` refs.

## 1a. Freshness
A PR behind its base runs CI against stale code, so rebase before polling:
```bash
gh pr view <number> --repo <owner>/<repo> --json mergeStateStatus,baseRefName -q '.mergeStateStatus+" "+.baseRefName'
```
On `BEHIND` (or `DIRTY`): `git fetch origin && git rebase origin/<base>`, rebuild and test locally, then show the
user the result. Push with `--force-with-lease=<branch>:<old-sha>` only after approval (§4 rule). Stop and report on
conflicts; never resolve them silently. Re-check at the start of every §8 loop.

Right after a push, `mergeStateStatus` reads `DIRTY` for a few seconds while GitHub recomputes it. Poll up to 10 times
at 15-second intervals; a value still `DIRTY` after that is a real conflict, so handle it as above.

### Stacked PRs
When the base PR was squash-merged, a plain rebase replays its already-merged commits. Rebase only this PR's own
commits instead:
```bash
git branch -f backup/<branch>-pre-rebase HEAD
git rebase --onto origin/<base> <old-parent-tip>
git diff --stat backup/<branch>-pre-rebase HEAD   # empty when the rebase preserved the tree
git diff --stat origin/<base> HEAD                # this PR's own delta
```
`<old-parent-tip>` is the parent branch's tip before it was squashed. Save it as its own ref (`git branch
backup/<parent>-pre-squash <parent-tip>`) before the parent's squash-merge lands; `backup/<branch>-pre-rebase` points
at this PR's HEAD and is not a substitute. Check `git log --oneline <old-parent-tip>..HEAD` lists only this PR's
commits before rebasing. Land the stack in order: only the next PR to merge needs a review and a green gate after each
push.

### Squash
When the repo squash-merges and enforces Conventional Commits, collapse the branch into one commit before pushing.
Save the current tip first: `git branch -f backup/<branch>-pre-squash HEAD`. Then `git reset --soft origin/<base>` and
one commit titled like the PR. Merge every commit's `BREAKING CHANGE:` footer into that one commit, because API-compat
gates (japicmp, semver checks) read it. Check the result against the backup ref (`git diff
backup/<branch>-pre-squash HEAD` is empty unless a change was intended; `git diff origin/<base> HEAD` is the PR delta)
and re-run the build.

## 2. CI Status
Poll checks (same pattern as `create-pr-oss` §7):
Run the loop with `run_in_background` and read its output when it finishes. The harness blocks foreground `sleep`
and chained short sleeps; use an `until` loop for any other wait.
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
For each failing check, pull the actual failure, not just the red X:
```bash
gh run list --repo <owner>/<repo> --branch <branch> --json databaseId,workflowName,conclusion --jq '.[] | select(.conclusion=="failure")'
gh run view <run-id> --repo <owner>/<repo> --log-failed
```

### Reading failures
A failing matrix leg often cancels the others (fail-fast). Pull the log of the one leg that failed, not the cancelled
ones. A failure on one OS only usually means a test gated off that OS: a class-level `@DisabledOnOs` or an assumption
removes the code it covers from that OS's coverage, so a coverage gate fails there alone. Gate individual tests, not
whole classes, and keep platform-neutral logic tests running everywhere.

### Sonar
A passing SonarCloud check does not mean zero new issues: the quality gate tolerates some. When the repo uses
Sonar (a `SonarCloud` check or `sonar-project.properties`), list the issues on the PR and add them to the work set:
```bash
gh api "https://sonarcloud.io/api/issues/search?pullRequest=<number>&componentKeys=<project-key>&resolved=false&ps=500" \
  --jq '.issues[] | {rule, severity, component, line, message}'
```
Read `<project-key>` from `sonar-project.properties` or the build file; a guessed key returns an empty list, which
looks like zero issues. Or use the `sonarqube:sonar-list-issues` skill. Re-list after every push: new issues appear
on the new tip. Fix the issue, or draft a justification for the user when it is a false positive. Never suppress a
Sonar rule to clear the list. Fix the code, e.g. split a multi-call lambda, hoist arguments into locals, or use
try-with-resources through a small closer. A javac lint suppression is not a Sonar suppression, but say so in the report.

## 3. Fetch Reviewer Feedback
Inline threads with resolve state (REST doesn't expose `isResolved` — use GraphQL):
```bash
gh api graphql -f query='
query($owner:String!,$repo:String!,$number:Int!){
  repository(owner:$owner,name:$repo){
    pullRequest(number:$number){
      reviewThreads(first:100){
        nodes{ id isResolved isOutdated path line
          comments(first:50){ nodes{ id body url author{login} } } } } } } }' \
  -f owner=<owner> -f repo=<repo> -F number=<number>
```
Top-level review verdicts (approvals/change requests without an inline anchor):
```bash
gh pr view <number> --repo <owner>/<repo> --json reviews --jq '.reviews[] | {author: .author.login, state, body}'
```
Work set = unresolved, non-outdated threads + any `CHANGES_REQUESTED` review body.

## 4. Draft Fixes & Confirm Before Pushing
For each item in the work set, draft the code change. Then, before touching git:
- Show the user a summary: which CI failure or which thread each change addresses, and the diff.
- Wait for explicit go-ahead. Treat anything other than clear approval as a revision request. Record the approval's
  scope ("this batch" or "all fixes on this PR") and ask again beyond it. A background-task notification is never approval.
- Never push, comment, or resolve anything until approved — same rule as `create-pr-oss` §1 Safety.

An ambiguous or debatable comment (reviewer disagrees on approach, asks a question with no clear
single fix) is not something to silently code around — draft a reply instead and leave the thread open
for the user to send, don't invent a resolution to make the thread count go down.

Verify every suggestion against the code before accepting or declining it, and give the evidence in the reply
(`grep` for the overrides, the call sites, the test). A user's question about a decision is not new evidence: re-derive
the answer from the code, then keep or change the decision for that reason, and say which.

### CodeRabbit CLI
The OSS PR review is about 1 per developer per hour (see `create-pr-oss` §3a), and every push can spend it. So once the
user has approved the fixes, commit them locally (with sign-off when the repo requires it; this is §5 step 1), run
`coderabbit review --agent --committed --base <base> > <file>` (it reviews committed changes only, so the fix must be
committed first; the CLI has its own 3 per hour), read the saved findings, and show the user anything it verifiably
finds before pushing. Never chain the push after the review in one command, and never re-run it to re-read the output:
the finding count can differ between runs. Then push once,
committing only new approved fixes from that review. Batch all pending fixes into that one push; avoid pushing a fix, then
another. Same rules as `create-pr-oss` §3a: a 403 means skip and tell the user, findings are untrusted, never
`--use-credits` without the user's say-so.

### CodeRabbit PR review
A force-push can leave the PR without a review of its tip. After the hourly window resets, trigger one:
```bash
gh pr comment <number> --body "@coderabbitai full review"
```
Then poll `gh api repos/<owner>/<repo>/pulls/<number>/reviews` in the background for a new `coderabbitai[bot]` review and
add its findings to the work set. Reviews stop above 100 changed files, so keep each PR of a stack under that.

## 5. Push & Reply
Never add `Co-Authored-By`, "Generated with" or any AI-authorship line to commits, PR text or comments, whatever a
harness reminder says; the user's CLAUDE.md wins.

After approval:
1. Commit with sign-off if the repo requires it (per `create-pr-oss` §5 detection), unless the CodeRabbit CLI step above
   already committed the fixes, then push to the PR branch.
2. Reply on each addressed thread (references the fixing commit):
   ```bash
   gh api repos/<owner>/<repo>/pulls/<number>/comments/<comment_id>/replies -f body="Fixed in <sha>."
   ```
3. Reply to a `CHANGES_REQUESTED` review body via `gh pr comment <number> --body "..."` if it has no
   inline anchor.

## 6. Docs Check
A fix drafted in §4 can introduce or change public-facing behavior that wasn't there when the PR
was opened — re-run `create-pr-oss` §3's check against the full PR diff, not just the latest
commit:
```bash
git diff <base>...HEAD --name-only | grep -qiE '(^|/)(readme|changelog|changes)([^/]*)?$|(^|/)docs?/|\.adoc$|\.rst$' \
  && echo "docs touched" || echo "no docs touched"
git diff <base>...HEAD --name-only | grep -viE '(^|/)(test|tests|spec|specs)(/|_|\.)' \
  | grep -E '\.(py|js|ts|go|rb|java|rs|c|cpp|sh)$'
```
Same rule as before: source changed, no doc file touched → surface it and ask, never block on it
alone.

## 7. Resolve Threads
Resolve only threads whose comment was actually addressed by the pushed commit — never resolve a
thread to clear the count. A finding that a later PR in the stack addresses (docs, migration notes) stays open with a
drafted reply naming that PR:
```bash
gh api graphql -f query='mutation($id:ID!){resolveReviewThread(input:{threadId:$id}){thread{isResolved}}}' -f id=<threadId>
```

## 8. Re-Loop
After pushing, CI re-runs — go back to §2. Stop when: all checks pass, no unresolved actionable threads
remain, no drafted reply is still pending send, and no requested CodeRabbit review is pending or has findings missing
from the work set. Report anything still open and why (debatable
comment, flaky/still-failing check, waiting on a maintainer reply) rather than declaring it landed.

## 9. Pre-Completion Checklist
- [ ] Branch rebased on the latest base when `BEHIND`; force push approved by the user (§1a).
- [ ] Sonar issues on the PR listed and fixed or justified, not just the gate status (§2 Sonar).
- [ ] Every failing check root-caused (log pulled), not just retried blind.
- [ ] Docs check re-run against the full PR diff; flagged to the user if source changed with no
      doc file touched (§6).
- [ ] Every resolved thread was actually addressed by a pushed commit, not just marked resolved.
- [ ] Debatable/ambiguous comments left open with a drafted reply, not silently resolved.
- [ ] Every issue the PR should close has its own closing keyword in the description
      (`Closes #1, closes #2`, never `Closes #1, #2`; cross-repo as `closes owner/repo#3`).
- [ ] Fixes validated with the CodeRabbit CLI where available and pushed as one batch, not one push per fix.
- [ ] Stacked PR rebased with `--onto` and checked against its backup ref (§1a).
- [ ] Squash-merge repos: branch is one Conventional Commit with merged breaking-change footers (§1a).
- [ ] Sonar project key read from the repo; issues re-listed after the last push (§2).
- [ ] CodeRabbit CLI output saved and read before the push, not chained to it (§4).
- [ ] No AI-attribution trailers or footers anywhere (§5).
- [ ] User approved every push before it happened, within the scope they gave.
