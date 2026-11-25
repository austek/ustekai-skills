---
name: context-spend
description: Use when the context is heavy, token spend is climbing, the user asks what the session costs, wants to compact, clear, or hand off to a fresh session. Reports cost split, estimated saving from compacting, and the plugin overhead ranking.
argument-hint: "[check|handoff|compact]"
---

# context-spend

A `UserPromptSubmit` hook warns once per session when context crosses `CTX_GUARD_THRESHOLD` (default 150000 tokens). This skill acts on that warning.

A skill cannot run `/compact` or `/clear`. Print the line for the user to type.

## check

Run `python3 "${CLAUDE_PLUGIN_ROOT}/context-spend/scripts/ctxspend.py" report` (add `--session <id>` or `--threshold <N>` when asked) and quote the numbers: context size, total, fixed vs growth cost, crossing turn, estimated saving, top overhead items. Say "estimated" when the output does.

## handoff

1. Write a note to `~/.claude/scratches/handoff-<date>.md`: goal, decisions, open items, files touched, next step.
2. Print `/clear`, then tell the user to paste the note path; or print `claude --resume <session id>` to continue this session elsewhere.

## compact

Propose a focus string naming what must survive (goal, open decisions, files in play), then print `/compact <focus>` for the user to run.

## Environment

- `CTX_GUARD_THRESHOLD`: warning threshold in tokens (default 150000).
- `CTX_WINDOW_TOKENS`: window size for the `statusline` percentage (default 1000000).
- An unparseable value falls back to the default.

## Limits

- Prices come from the `claude-api` skill, read 2026-11-25. Every dollar figure is an estimate; unknown models are priced as Opus and the report says "estimated".
- Overhead token figures are approximate (characters / 4); multi-line and quoted frontmatter values slightly undercount.
- MCP server size is not estimated, and `.mcp.json` servers supplied by plugins are not listed.
- The warning appears as a `systemMessage` shown to the user.
