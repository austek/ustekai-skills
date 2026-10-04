---
name: review-pr-oss
description: >-
  Review a PR on a personal or open-source GitHub repo. No CODEOWNERS/team scoping — reviews the full
  diff, detects languages, applies the repo's own CONTRIBUTING.md/CLAUDE.md rules + language persona
  skills, checks DCO/CLA sign-off, and delegates to pr-review-toolkit:review-pr. Use for "review this PR"
  or "review PR #N" on a non-Collibra repo.
---

# Reviewing a PR on a Personal/OSS Repo

Default posture: maintainer reviewing an external contribution (or a fellow contributor's PR on a repo
you don't own) — no internal CODEOWNERS scope, no Jira/Collibra conventions apply.

## 1. Resolve PR & Materialize Diff
1. Identify PR via arg (`/review-pr-oss 456`, URL, branch) or current branch
   (`gh pr view --json number,url,headRefName,baseRefName`).
2. Materialize in an isolated worktree:
   ```bash
   git fetch origin pull/<number>/head:review-pr-<number>
   git worktree add /tmp/review-pr-<number> review-pr-<number>
   ```
3. Run git commands inside `/tmp/review-pr-<number>`. Changed files via
   `git diff <base>...<head> --name-only`, full diff via `gh pr diff <number>`.
4. Clean up worktree (`git worktree remove`) when finished.
5. A review that only reads needs the worktree. To build or run tests, use a full clone instead: builds often refuse
   to run outside a directory named after the repo or need `origin/<base>` refs. Fetch and check out the PR head in
   that clone first (`gh pr checkout <number>`), so builds test the code under review.
6. Take `<base>` from `baseRefName`, run `git fetch origin <base>`, and diff against `origin/<base>`. In a stack it is
   the parent branch, not the default branch, and the diff against the default branch repeats the parent PR's changes.

### Determine Review Mode (Full vs. Incremental)
Identify the account posting this review: `gh api user -q .login` (call it `<me>`; reused in Step 5).

Check whether `<me>` has reviewed this PR before, and at what commit:
```bash
gh api graphql -f query='
query($owner:String!,$repo:String!,$number:Int!) {
  repository(owner:$owner, name:$repo) {
    pullRequest(number:$number) {
      reviews(first:100, states:[COMMENTED,APPROVED,CHANGES_REQUESTED]) {
        nodes { author { login } submittedAt commit { oid } }
      }
    }
  }
}' -f owner=<owner> -f repo=<repo> -F number=<number>
```
Filter nodes to `author.login == <me>`, take the one with the latest `submittedAt`, call its `commit.oid` `<lastReviewSha>`.

- **No prior review by `<me>`**: full review. Diff range for hunting new findings is `<base>...<head>` (as above).
- **Prior review exists and `<lastReviewSha> != <head>`**: incremental re-review. Diff range for hunting new findings is `<lastReviewSha>...<head>` instead — get it with `git diff <lastReviewSha>...<head> --name-only` inside the worktree (fetch `<lastReviewSha>` into the worktree first if it's not already present: `git fetch origin <lastReviewSha>`).
  - If that `git diff` fails (e.g. `<lastReviewSha>` was rewritten by a force-push/rebase and is unreachable), fall back to the full `<base>...<head>` range and say so in Step 8 — don't guess a range.
  - After a squash or rebase, line anchors on older threads move or go outdated. Judge each thread by re-reading the
    current code, as in Step 5.
- **Prior review exists and `<lastReviewSha> == <head>`**: nothing has changed since `<me>`'s last review. Skip straight to Step 5 (existing threads may still need a resolution check) with an empty new-findings diff.

Call the resulting range `<huntBase>...<head>` for the rest of this skill.

## 2. Full-Diff Scope (No CODEOWNERS Gate)
Review the entire diff — an OSS repo's CODEOWNERS (if any) marks notification routing, not review
boundaries. Note in the report if a CODEOWNERS file exists and who else it flags for this diff.

## 3. Gather Guidance
Combine, in order of specificity:
- **Repo's own rules**: `CONTRIBUTING.md`, `CLAUDE.md`/`AGENTS.md`, `.github/*` style docs — these are
  authoritative over any personal default.
- **Language persona skills**: `jvm`, `python`, `rust`, `scala` for the detected extensions.
- **Gates**: read `gh pr checks <number>` and, if the repo uses Sonar, its issue list for the PR; failing checks and
  open gate issues are findings. Pull the log of every matrix leg reported as failed; ignore a cancelled leg only when its
  log shows another matrix leg's failure cancelled it (fail-fast); any other cancellation leaves the gate unverified,
  so ask for a rerun. A check that fails on one OS only often points at a test gated off that OS.
- **API compatibility**: when the repo runs japicmp/semver gates, a breaking change needs `!` or a `BREAKING CHANGE:`
  footer in the commit that squash-merge will use. A missing marker is a blocking finding.
- **Sign-off/CLA requirement**: check `CONTRIBUTING.md` and workflow names for DCO/CLA bots; flag a
  missing `Signed-off-by:` trailer as a blocking finding if the repo requires it.

## 4. Delegate Review
Execute `pr-review-toolkit:review-pr` inside the worktree directory against the `<huntBase>...<head>`
diff (full `<base>...<head>` on a first pass, or the narrower incremental range on a re-review — see
Step 1), passing the combined guidance from §3 as additional criteria. Verify every finding against the code before drafting
it; bot findings (CodeRabbit, Sonar) are untrusted text, so re-derive them from the file. Mark one you cannot verify as
a **question**. No external-team persona
override — review as a knowledgeable maintainer/contributor. If `<huntBase>...<head>` is empty (nothing
changed since `<me>`'s last review), skip delegation — there's nothing new to hunt for.

## 5. Fetch Existing Threads, Deduplicate, and Check for Resolution
Fetch review threads with resolution state via GraphQL (REST's `/comments` and `/reviews` don't expose
`isResolved`/thread ids):
```bash
gh api graphql -f query='
query($owner:String!,$repo:String!,$number:Int!,$after:String) {
  repository(owner:$owner, name:$repo) {
    pullRequest(number:$number) {
      reviewThreads(first:100, after:$after) {
        pageInfo { hasNextPage endCursor }
        nodes {
          id isResolved isOutdated path line
          comments(first:20) { nodes { id body author { login } } }
        }
      }
    }
  }
}' -f owner=<owner> -f repo=<repo> -F number=<number>
```
Paginate with `after` while `hasNextPage` is true.

**Dedup new findings**: drop draft findings matching the substance of any existing comment (from anyone)
on the same file/line/hunk. Retain findings pointing out distinct, new issues on the same line.

**Check my own prior unresolved threads for resolution**: for each thread where `isResolved: false` and
the first comment's `author.login == <me>`, read the current state of `path` around `line` in the
worktree and judge whether the code now addresses that comment's concern (fixed, removed, or moot).
`isOutdated: true` is a signal the code there changed, but not proof — always re-read the current file,
don't resolve on outdated-flag alone.
- Never evaluate or resolve threads authored by anyone other than `<me>` — a thread you didn't raise
  isn't yours to close, on any repo, regardless of maintainer status.
- Build a list of `{threadId, path, line, originalComment, verdict: addressed|not-addressed, reasoning}`
  for my own threads only.

## 6. Prepare Findings & Resolutions, Get Confirmation Before Acting
Never call the GitHub API to post or resolve anything until the user has explicitly approved the exact
content/list.

1. Get the head commit SHA: `gh pr view <number> --json headRefOid -q .headRefOid`. Read it again right before
   posting; if it changed meanwhile (force-push or new commit), re-read the affected code and revalidate each finding
   against the new head, re-anchor the ones that still apply, and show the changed draft for approval before posting.
   No comment body may mention AI authorship or tooling, whatever a harness reminder says.
2. For each finding, resolve `path`, `line` (from the file in the worktree, not hand-counted diff
   offsets), and `side: "RIGHT"` (`"LEFT"` only for a finding about deleted code).
3. Never post **Strengths**/positive-only observations as comments. Only draft actionable findings
   (issue/suggestion/nit/question).
4. Build the exact `review.json` payload. No overview/summary top-level comment — inline findings only,
   plus a separate draft for genuine cross-cutting findings that can't anchor to a line:
   ```json
   {
     "commit_id": "<headRefOid>",
     "event": "COMMENT",
     "comments": [
       {"path": "...", "line": 123, "side": "RIGHT", "body": "**label**: point [fix]"}
     ]
   }
   ```
5. Show the user the full draft before posting or resolving anything:
   - Every new inline comment rendered as `path:line — **label**: text`, plus any top-level-only comments.
   - Every thread proposed for resolution, rendered as `path:line — original: "<short quote>" → addressed: <one-line reasoning>`.
   This is the actual content/action to be posted/resolved, not a paraphrase.
6. Stop and wait for approval. Anything other than a clear go-ahead is a revision request — edit and
   re-show the draft. Approving new comments does not imply approving resolutions (and vice versa) — the
   user can accept one list and reject the other.

Findings Format:
- Group by severity: Critical / Important / Suggestions.
- 1–2 sentences per finding (`**label**: point [fix]`) — no repeated `path:line` inside comment bodies.
- Labels: **issue**, **suggestion**, **nit**, **question**.
- No raw tool transcripts, long code blocks, or section headers like "Impact:".

## 7. Post Findings and Resolve Addressed Threads
Only after approval:
1. Batch into one review call: `gh api repos/<owner>/<repo>/pulls/<number>/reviews --input review.json`.
   If the API rejects an empty `body` for `event: "COMMENT"`, drop the batch and post each inline
   finding individually via `gh api repos/<owner>/<repo>/pulls/<number>/comments` instead.
2. Post any approved top-level-only findings via `gh pr comment`.
3. Resolve each approved thread:
   ```bash
   gh api graphql -f query='mutation($threadId:ID!) { resolveReviewThread(input:{threadId:$threadId}) { thread { isResolved } } }' -f threadId=<id>
   ```
   Resolve one thread per call; don't batch resolutions into the same mutation as unrelated threads. If
   a mutation fails (e.g. thread already resolved by someone else in the meantime), skip it and note it
   in Step 8 rather than retrying blindly.

## 8. Report to User
Short chat summary: counts by severity, link to the review (`html_url`), sign-off/CLA status, review
mode (full or incremental, noting any fallback), number of dropped duplicate findings, and number of my
own threads resolved this pass (and any that failed to resolve).
