---
name: explain-diff-html
description: Use when the user asks for a rich explanation of a code change, diff, branch, or PR (including a stack of related PRs). Produces a single HTML page with a scrollspy sidebar and per-section "mark as read" collapsing, and by default includes an independent critic review plus tests that prove the critic's findings (opt out by asking for just the explanation).
---

# Explain Diff

Make a rich, interactive explanation of the specified code change as one self-contained HTML page.

By default the page has six sections: Background, Intuition, Code walkthrough, Critic review,
Tests that prove the findings, Quiz. The critic review and proof-tests are standard parts of the
deliverable. Skip them only when the user explicitly opts out ("just explain it", "no review",
"skip the critic"). An ambiguous request is not an opt-out: run them rather than asking.

## Workflow

1. **Get the change.** Resolve the target to a commit SHA and a diff.
   - PR: `gh pr view`, `gh pr diff`. Check `git log` and `git branch -vv` first, since the working tree may already sit on the commit you need.
   - Branch: diff against its merge base with the default branch.
   - Uncommitted work: `git diff HEAD`, and note that the page describes unpublished changes.
   - Several PRs: see "Stacked PRs".
2. **Explore** the surrounding code broadly for the Background section.
3. **Run the critic** (see "Critic review") while you draft the narrative sections.
4. **Write and run proof-tests** (see "Tests that prove the findings").
5. **Build the page** by copying `assets/template.html` and filling it in (see "Building the page").
6. **Validate** with `scripts/validate.py` and fix every failure.
7. **Report** the output path, and ask before cleaning up the test worktree.

## The narrative sections

- **Background**: the existing system relevant to the change. The reader's knowledge is unknown, so give a deep beginner background (marked skippable) in one subsection, then a narrow one directly relevant to the change in another.
- **Intuition**: the essence of the change, not the full details. Use concrete toy data and diagrams liberally.
- **Code walkthrough**: a high-level walk through the changes, grouped and ordered so they are understandable.
- **Quiz**: five medium-difficulty multiple-choice questions that need real understanding of the change to answer, with no gotchas. Clicking an option reveals whether it was right, with feedback. Draw questions from the whole change, not just its most recent part.

## Stacked PRs

When given more than one PR, explain the **combined result**, not each PR in isolation.

- Fetch metadata and diffs for every PR and work out the stack order (which is based on which).
- Narrate the stack as a sequence: what the first built, what the second changed and why.
- In Intuition, look for one unifying theme across the stack. It usually explains more than a flat list of diffs.
- Give each PR its own pill in the Code section headers (`<span class="pill pr1">`, `pr2`, `pr3`) so the reader knows which change they are in.

## Critic review (default)

Add a **Critic review** section to the page, not just a chat report.

- **Run the critic as a fresh, read-only subagent** (Agent tool). A critic handed your conclusions tends to confirm them. Give it the repo path, the commit SHA, how to get the diff, and the output format below. Do not give it your findings, your intuition summary, or the PR description's claims. Tell it not to modify or commit anything.
- Review the **combined, current state** of the code (whatever is actually checked out) and say so to the critic.
- Ask for concrete findings with `file:line`, a failure scenario per finding, a severity (Blocker/Major/Medium/Low), and an overall verdict. If the change's context matters (POC vs. production), ask for a verdict appropriate to it.
- Verify each cited `file:line` against the real file yourself before it goes on the page.
- Render a verdict box, then finding cards grouped by severity, then a callout on what the review checked and ruled out. A one-sided list of problems reads as less credible.
- On a clean result, still include the section: a verdict box saying so plus the ruled-out callout. A skipped section looks like the review never ran.
- The section sits after Code walkthrough and before Quiz.

## Tests that prove the findings (default)

Runs whenever the critic produced findings. If it found nothing, skip the section and say so in one line.

**Where the tests live.** Write them in a throwaway git worktree, never in the user's working tree:

```bash
git worktree add --detach "${TMPDIR:-/tmp}/explain-diff-<slug>" <reviewed-sha>
```

- For an unmerged PR, fetch its head first (`git fetch origin pull/<n>/head`) and use that SHA.
- For uncommitted work, apply it in the worktree with `git diff HEAD | git -C <worktree> apply`.
- If the worktree cannot build (it needs untracked local setup), tell the user and ask before writing into their tree.
- **Never commit** in the worktree or anywhere else. Never push.
- **Ask before cleanup.** At the end, list the test files and the worktree path, and ask whether to keep the worktree or run `git worktree remove`. Never remove it unprompted. The page states the path and which files the author can copy into their PR.

**Test quality.** Write them as the tests the author would adopt, not throwaways.

- For each finding, decide whether it is naturally one deterministic assertion ("silent overflow", "missing validation", "wrong formula at an edge"). Findings like "dead code" or "no test exists for X" are not. Say so on the page rather than forcing a fake test.
- Assert the **desired, correct** behavior. The test is red today and green once someone fixes the bug.
- Where a finding has a counterpart across a trust or language boundary (a formula duplicated in TypeScript and Java), write a test on each side.
- When a language's arithmetic genuinely does not reproduce the bug (JS doubles vs. Java `long`), that side may be a **passing** reference cross-check. Say so and use it as the "what it should have said" baseline.
- Follow the existing test file's conventions: same class, same assertion library, same setup style.
- If the target side has no test runner, adding a minimal standard one (e.g. `vitest`) in the worktree is fine. Keep it small.
- To exercise a pure function, export it with a one-line behavior-preserving change rather than duplicating its logic in the test.
- Use the project's pinned toolchain (mise, asdf, sdkman) rather than hunting for a system install.
- **Run every test and capture the real output before writing anything up.** Quote the real assertion error with the real numbers. If a test does not fail as expected, investigate. Never edit the test to force a failure.

**The section.** A summary table (finding, layer, test, PASS/FAIL badge), then a card per test with the real code and the real output, most interesting finding first. Close with an honest note on what the tests do not prove (a validation-gap test is not a load test proving a real DoS).

## Linking references

Every citation of a specific external item is a real `<a href>` to the exact item, never bare text. This applies most to the critic and proof-tests sections, where `file:line` is evidence the reader should be able to click.

- **Files and lines**: `https://github.com/<owner>/<repo>/blob/<commit-sha>/<path>#L<start>-L<end>` (`#L<n>` for one line). Use the commit SHA you reviewed, never a branch name that will move. Open the file and confirm the line number against its current content before linking.
- **PRs and issues**: `https://github.com/<owner>/<repo>/pull/<n>` or `/issues/<n>`. Use real URLs from the source material, including PRs in other repos.
- **Jira**: `https://<instance>.atlassian.net/browse/<KEY>`. Take the host from links already in the repo or PR content. Never guess it.
- **Confluence**: link only a URL you were given or found. Never invent one; ask.
- **Do not link** diagram box labels or literal code inside `<pre>`.
- The validator rejects `href="#"` and `href=""`.

## Building the page

Copy `assets/template.html` and fill it in. The CSS, sidebar, scrollspy, mark-as-read and quiz scripts in it are tested scaffolding. Do not rewrite or "improve" them per page.

- **Replace every `{{PLACEHOLDER}}`.** `{{SLUG}}` becomes a page-unique slug (for example `<repo>-pr<n>`), because it keys the reader's saved progress in `localStorage`.
- **Sections** are `<section class="page-section" id="sec-X" data-section="X">`, with a `.section-header` holding `<h2 id="X">` and a button, and a `.section-body`. Optional `<h3>` subsections follow the same pattern one level down (`subsec-X`, `data-subsection`). Every `<h2>` and `<h3>` carries its own bare `id`. The sidebar links resolve against it, not against the `sec-` wrapper id.
- **Sidebar**: one `<li class="sidebar-item">` per section, in page order, with a `.sidebar-dot` span. Add, remove, or renumber sections and sidebar items together, and keep the `<h2>` numbers sequential.
- **Optional sections**: delete the Critic and Proof-tests sections and their sidebar items together on an opt-out.
- Use the template's classes for callouts, `.pill`, `.badge`, `.card`, `.verdict`, and the `.diagram`/`.flow`/`.box` family. Do not add a separate table of contents.

## Format

- One self-contained HTML file (CSS and JavaScript inline), one long page navigated by the sidebar. No tabs at the top level. Readable on a phone.
- **Output location**: `${EXPLAIN_DIFF_DIR:-$HOME/notes/pr-reviews}/`, created if missing. Keep it outside the code repo. The filename starts with today's date: `YYYY-MM-DD-explanation-<slug>.html`.
- Write with the clarity and flow of Martin Kleppmann: engaging, classic style, smooth transitions between sections.
- Diagrams: pick a small number of diagram families and reuse them. Useful kinds are a simplified version of the UI the user sees, and a system diagram of data flow with example data. Build them from HTML, not ASCII. Use HTML lists for lists.
- Code blocks use `<pre>`. A custom div used for code must set `white-space: pre-wrap`.
- Use callouts for key concepts, definitions, and edge cases.
- Critic and proof-test items use severity/result badges and bordered cards with a matching left border, so the reader can scan for the verdict.
- **Large HTML in one `Write` call can hang** with no output and no prompt. If it does, do not retry the same call. Build the file with `cat >> file <<'EOF'` appends, or fill the template in pieces.

## Validate

Run before reporting:

```bash
python3 -I <skill-dir>/scripts/validate.py <page.html>
```

It checks tag balance, `node --check` on every script block, sidebar links against ids, `id`/`data-*` consistency, h2 numbering, leftover placeholders and placeholder hrefs, the storage-key slug, and custom code-block CSS. Fix every `FAIL` and rerun until it prints `OK`.

The validator is static and cannot exercise the page's JavaScript. Do not install a browser-automation tool to compensate. Run an interactive check only if the user asks or a working Playwright is already installed.
