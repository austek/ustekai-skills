---
name: context-spend
description: Use when the context is heavy, token spend is climbing, the user asks what the session costs, wants to compact, clear, or hand off to a fresh session. Reports cost split, estimated saving from compacting, and the plugin overhead ranking.
argument-hint: "[check|handoff|compact]"
---

# context-spend

A `UserPromptSubmit` hook warns once per threshold crossing when context passes `CTX_GUARD_THRESHOLD` (default 150000 tokens) and re-arms when context drops back below it. This skill acts on that warning.

A skill cannot run `/compact` or `/clear`. Print the line for the user to type.

## check

Run `python3 "${CLAUDE_SKILL_DIR}/scripts/ctxspend.py" report` (add `--session <id>`, `--threshold <N>` or `--transcript <path>` when asked) and quote the numbers: context size, total, fixed vs growth cost, crossing turn, estimated saving (`n/a` when the session started above the threshold), top overhead items. Say "estimated" when the output does.

## handoff

1. Tell the user the exact path `${CLAUDE_CONFIG_DIR:-~/.claude}/scratches/handoff-<date>-<HHMM>.md` (resolved) and a summary of the note's contents (goal, decisions, open items, files touched, next step), then ask before writing it. Write only after the user agrees.
2. Print `/clear`, then tell the user to paste the note path; or print `claude --resume <session id>` to continue this session elsewhere.

## compact

Propose a focus string naming what must survive (goal, open decisions, files in play), then print `/compact <focus>` for the user to run.

## Environment

- `CTX_GUARD_THRESHOLD`: warning threshold in tokens (default 150000). A value of 0 or less disables the guard.
- `CTX_WINDOW_TOKENS`: window size for the `statusline` percentage (default 1000000).
- An unparseable value falls back to the default.

## Status line

Plugins cannot set `statusLine`, so add it to your own settings:

```json
{"statusLine": {"type": "command", "command": "python3 <path to ctxspend.py> statusline"}}
```

It prints `ctx N%` of `CTX_WINDOW_TOKENS`.

## Limits

- Prices come from the `claude-api` skill, read 2026-11-25. Every dollar figure is an estimate; unknown models are priced as Opus and the report says "estimated".
- Overhead token figures are approximate (characters / 4); quoted frontmatter values slightly overcount (the quote characters count) and multi-line block scalars undercount.
- MCP server size is not estimated, and `.mcp.json` servers supplied by plugins are not listed.
- The warning appears as a `systemMessage` shown to the user.
