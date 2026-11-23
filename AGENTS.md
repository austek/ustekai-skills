# Agent rules

## Plugin versions

Every plugin directory has a `version` in `.claude-plugin/marketplace.json`. Bump it in the same PR as any change under that directory.

- Minor: new behavior, new flags or skills, changed defaults.
- Patch: bug fixes, docs, tests, internal refactors.
- Plugins: `language-personas`, `pr-workflow-oss`, `babysit-pane`, `architecture`, `productivity`, `dev-utilities`.
- `babysit-pane` also declares the version in `babysit-pane/.claude-plugin/plugin.json`; keep both equal.
- Bump once per PR, from the version on `origin/main`. A follow-up commit on the same PR does not bump again.
- A PR touching several plugins bumps each of them.
- Commit the bump with the change; CodeRabbit flags a PR that changes a plugin without one.
