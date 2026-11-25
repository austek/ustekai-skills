# ustekai-skills

Personal Claude Code skills and commands, packaged as a plugin marketplace.

## Install

In Claude Code:

```
/plugin marketplace add austek/ustekai-skills
```

Not sure what you need? See the [catalog](docs/catalog.md): a flowchart that
maps what you are doing to the right skill, plus pros and cons per plugin.

Then enable whichever plugins you want:

- `language-personas` — Java/Kotlin/Python/Rust/Scala coding-standards, testing,
  and tooling personas. The `jvm-*` skills hold rules shared by Java, Kotlin and
  Scala; `spring-standards` and `ktor-standards` hold framework rules. Also a JVM
  systems mentor and a polyglot tutor.
- `pr-workflow-oss` — open/review/land a PR on a personal or open-source repo,
  and babysit your open PRs across a repo, user, or org (`/babysit-pr-oss`,
  which leaves checks that also fail on the base branch or at the same step on
  two other open PRs alone
  and reports them as environmental). A session-start hook marks the state
  file of a merged or closed PR `CLOSED`, so the pane drops it, and deletes
  `CLOSED` files after `BABYSIT_PURGE_HOURS` hours (default 24).
- `babysit-pane` — a pane and commands (`/babysit-pane` prints the state,
  `/babysit-panel` shows or hides the pane) for the PRs `/babysit-pr-oss`
  watches. Each open PR has a "run now" button that submits
  `/babysit-pr-oss <repo>#<N> --cycles 1`. It needs `pr-workflow-oss` 1.10.0 or later, which writes the state
  files, and shows only in the terminal; web and mobile get the printed text.
- `architecture` — deep-module design, domain modeling, architecture
  improvement, spikes, design docs, and scaffolding a repo from a reference.
- `productivity` — plan-sharpening interviews, agent handoffs, and
  questionnaire generation.
- `dev-utilities` — misc skills: IDE MCP tool selection, comment
  cleanup, code-claim verification, business analysis, HTML diff explanations,
  starting remote Claude sessions in tmux, budgeted sharded repo audits
  (`/audit`, `/full-audit`), and `context-spend` (context cost report plus a
  once-per-session `UserPromptSubmit` warning at `CTX_GUARD_THRESHOLD`).

## Update

Refresh the marketplace, then update each installed plugin. Restart Claude Code
afterwards.

```
/plugin marketplace update ustekai-skills
```

or from a shell:

```
claude plugin marketplace update ustekai-skills
claude plugin update dev-utilities@ustekai-skills
```

Claude Code caches each plugin by the `version` in `.claude-plugin/marketplace.json`.
A skill or command change is not picked up until that plugin's version is
bumped, so bump it in the same commit as the change.

Some skills in `architecture` and `productivity` are adapted from
[mattpocock/skills](https://github.com/mattpocock/skills) (MIT) — see
`THIRD-PARTY-LICENSES.md`.

`dev-utilities/explain-diff-html` is adapted from the original skill by Dan Hoizner.

Note: `analysis`, `pr`, and `story` commands (in `dev-utilities`) read voice
and style rules from your own project's `CLAUDE.md`. Without one, they fall
back to sensible defaults.
