# Agent rules

## Layout

Each plugin is a top-level directory. `.claude-plugin/marketplace.json` is the registry. Do not commit `.serena/` or `.superpowers/`.

## Plugin versions

Every plugin directory has a `version` in `.claude-plugin/marketplace.json`. Bump it in the same PR as any change under that directory.

- Minor: new behavior, new flags or skills, changed defaults.
- Patch: bug fixes, docs, tests, internal refactors.
- Plugins: `language-personas`, `pr-workflow-oss`, `babysit-pane`, `architecture`, `productivity`, `dev-utilities`.
- `babysit-pane` also declares the version in `babysit-pane/.claude-plugin/plugin.json`; keep both equal.
- Bump once per PR, from the version on `origin/main`. A follow-up commit on the same PR does not bump again.
- A PR touching several plugins bumps each of them.
- CodeRabbit flags a PR that changes a plugin without a bump.

## Commits and branches

- Commit subject: `<type>[(<scope>)]: <subject> (NO_ISSUE)`, or `(#<issue>)` when an issue exists. Recent history uses `<plugin>: <subject> (NO_ISSUE)`.
- Branch: `<type>/<ID>_<snake_case_description>`, for example `feature/NO_ISSUE_claude_remote_account_with`.
- No `Co-Authored-By` trailers, "Generated with" footers or any AI-authorship line in commits, PR text or comments.

## Skills

- Every `SKILL.md` has frontmatter `name` and a `description` that states when the skill triggers.
- Section references (`§N`) match the headings they cite; argument tables and checklists match the body.
- A step that pushes, posts, merges or deletes needs an approval gate or an explicit, bounded exception.
- When a plugin gains or changes a skill, update its entry in `README.md`.

## Tests and lint

- `claude-remote`: `python3 -m pytest dev-utilities/claude-remote/tests -q`.
- `audit`: tests live in `dev-utilities/audit/tests`; new behavior needs one.
- Shell scripts pass `shellcheck`; Python passes `ruff`.

## claude-remote

- A flag change goes in `scripts/claude-remote`, the `SKILL.md` argument-hint, usage line and body, and the tests.
- Line 2 of the script is the usage comment; `--help` prints it.
- `--install-boot` runs a copy at `~/.local/share/claude-remote/claude-remote`, so installed units need `--install-boot` rerun to pick up script changes.

## Comments

- No comments by default; a comment states a consequence the code cannot show.
- Run `pr-review-toolkit:comment-analyzer` on the diff before opening or updating a PR that adds or changes comments.
