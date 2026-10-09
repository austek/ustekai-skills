---
name: claude-remote
description: Start a Claude Code session with Remote Control in a detached tmux session targeting a git repo under a workspace root or any directory. Use for "start a remote session on <repo>", "open claude remote in <repo>", or "spin up claude for <repo> I can reach from my phone".
argument-hint: "[repo-name | /full/path] [--root DIR] (workspace root defaults to ~/Workspace)"
---

# claude-remote

Run `${CLAUDE_SKILL_DIR}/scripts/claude-remote [--root DIR] <repo-name | /full/path>`.

- A bare name (or fragment) is matched against git repos within 3 levels of the root. Root defaults to `~/Workspace`; override with `--root DIR` or `CLAUDE_REMOTE_ROOT`.
- An argument containing `/` (or `.`, `..`, `~/...`) is used directly as the working directory; no `.git` required.
- The session runs `claude --remote-control <name> --settings $CLAUDE_REMOTE_SETTINGS`. The variable defaults to `~/.config/dotfiles/claude-profiles/claude_personal.json`; a nonexistent path omits `--settings`.

Outcomes:

- Exit 0: report the session name, repo path, and the `tmux attach -t <session>` line from the output.
- Exit 2 (ambiguous): show the candidate paths and ask which one, then rerun with the full path.
- Exit 1 (no match): list repos with `find <root> -maxdepth 3 -name .git -prune -printf '%h\n'` and ask which was meant.

The command is idempotent: an existing `claude-<repo>-<path-hash>` tmux session (the hash is the first 6 hex of the SHA-1 of the resolved path, so same-named repos get separate sessions) is reused, not duplicated.
Stop a session with `tmux kill-session -t <session>` (name printed by the script; `tmux ls` lists them).
Never start the session inside the current terminal; the tmux session must stay detached.
Requires `tmux`.
