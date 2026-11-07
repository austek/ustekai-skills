---
name: claude-remote
description: Start a Claude Code session with Remote Control in a detached tmux session targeting a git repo under a workspace root or any directory, optionally auto-accepting the folder-trust prompt and installing a systemd user service so it starts on boot. Use for "start a remote session on <repo>", "open claude remote in <repo>", "spin up claude for <repo> I can reach from my phone", or "run claude remote on boot".
argument-hint: "[repo-name | /full/path] [--root DIR] [--name NAME] [--config-dir DIR] [--trust] [--install-boot | --uninstall-boot]"
---

# claude-remote

Run `${CLAUDE_SKILL_DIR}/scripts/claude-remote [--root DIR] [--name NAME] [--config-dir DIR] [--trust] [--install-boot | --uninstall-boot] <repo-name | /full/path>`.

- A bare name (or fragment) is matched against git repos within 3 levels of the root. Root defaults to `~/Workspace`; override with `--root DIR` or `CLAUDE_REMOTE_ROOT`.
- An argument containing `/` (or `.`, `..`, `~/...`) is used directly as the working directory; no `.git` required.
- `--name NAME` sets the Remote Control name shown on claude.ai (default: the directory name). It may contain only letters, digits, `_` and `-`; other names exit 64. The tmux session becomes `claude-<name>-<path-hash>`.
- `--config-dir DIR` sets the Claude account (`CLAUDE_CONFIG_DIR`) the session runs in. Default: the invoking shell's `CLAUDE_CONFIG_DIR`, so the session uses the account you ran the skill from; unset means Claude's default account. The tmux server does not inherit the caller's environment, so the script launches `claude` through `env`, which sets (or unsets) `CLAUDE_CONFIG_DIR` explicitly. A relative DIR is made absolute without resolving symlinks, so the session and unit names stay stable if a symlink is retargeted. Sessions started before this flag existed keep the account of the tmux server that created them and are reused under the same name: `tmux kill-session` them and rerun. A nonexistent DIR exits 66, except with `--uninstall-boot`. The boot unit name includes the account, so run `--uninstall-boot` from the same account as `--install-boot`; units installed before this flag existed need `env -u CLAUDE_CONFIG_DIR` in front of the command.
- `--trust` answers the "trust this folder" dialog on a new session by sending Down+Enter to the pane. Claude Code persists the answer per directory, so it only matters on first run. Pass it only when the user asked to trust that directory.
- `--install-boot` writes `~/.config/systemd/user/claude-remote-<name>-<path-hash>.service`, runs `loginctl enable-linger $USER` so the user manager starts at boot without a login, and enables the unit now. The unit captures the current `PATH` and `CLAUDE_REMOTE_SETTINGS` and bakes the resolved config dir into `ExecStart`, so run it from a shell where `claude` and `node` resolve. Combine with `--name` and `--trust` to bake them into the unit.
- `--uninstall-boot` disables and removes that unit; the tmux session keeps running.
- The session runs `claude --remote-control <name> --settings $CLAUDE_REMOTE_SETTINGS`. The variable defaults to `~/.config/dotfiles/claude-profiles/claude_personal.json`; a nonexistent path omits `--settings`.

Outcomes:

- Exit 0: report the session name, repo path, and the `tmux attach -t <session>` line from the output.
- Exit 2 (ambiguous): show the candidate paths and ask which one, then rerun with the full path.
- Exit 66 (config dir missing): tell the user the `--config-dir` path does not exist; do not ask about repos.
- Exit 1 (no match): list repos with `find <root> -maxdepth 3 -name .git -prune -printf '%h\n'` and ask which was meant.

The command is idempotent: an existing `claude-<name>-<path-hash>` tmux session (the hash is the first 6 hex of the SHA-1 of the resolved path plus the config dir when set, so same-named repos and different accounts get separate sessions) is reused, not duplicated.
Boot failures: `journalctl --user -u claude-remote-<name>-<path-hash>`.
Stop a session with `tmux kill-session -t <session>` (name printed by the script; `tmux ls` lists them).
Never start the session inside the current terminal; the tmux session must stay detached.
Requires `tmux`; `--install-boot` also requires systemd.
