# ustekai-skills

Personal Claude Code skills and commands, packaged as a plugin marketplace.

## Install

In Claude Code:

```
/plugin marketplace add austek/ustekai-skills
```

Then enable whichever plugins you want:

- `language-personas` — Java/Python/Rust/Scala coding-standards, testing, and
  tooling personas, plus a JVM systems mentor and a polyglot tutor.
- `pr-workflow-oss` — open/review/land a PR on a personal or open-source repo.
- `architecture` — deep-module design, domain modeling, and architecture
  improvement skills.
- `productivity` — plan-sharpening interviews, agent handoffs, and
  questionnaire generation.
- `dev-utilities` — misc skills: IDE MCP tool selection, comment
  cleanup, code-claim verification, business analysis.

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

Note: `analysis`, `pr`, and `story` commands (in `dev-utilities`) read voice
and style rules from your own project's `CLAUDE.md`. Without one, they fall
back to sensible defaults.
