import shlex
import shutil
import subprocess
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "claude-remote"
RECORD_TMUX = '#!/bin/sh\n[ "$1" = has-session ] && exit 1\nprintf "%s\\n" "$@" > "$TMUX_LOG"\n'


def _executable(path: Path, body: str = "#!/bin/sh\n") -> None:
    path.write_text(body)
    path.chmod(0o755)


def _start(tmp_path, *, loop_on_path=False, loop_in_home=False, extra=()):
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    _executable(fake_bin / "tmux", RECORD_TMUX)
    home = tmp_path / "home"
    (home / ".dotfiles" / "bin").mkdir(parents=True)
    if loop_on_path:
        _executable(fake_bin / "claude-pane-loop")
    if loop_in_home:
        _executable(home / ".dotfiles" / "bin" / "claude-pane-loop")
    repo = tmp_path / "my repo"
    repo.mkdir()
    env = {
        "PATH": f"{fake_bin}:/usr/bin:/bin",
        "HOME": str(home),
        "TMUX_LOG": str(tmp_path / "tmux.log"),
        "CLAUDE_REMOTE_SETTINGS": str(tmp_path / "missing.json"),
    }
    result = subprocess.run(
        [str(SCRIPT), *extra, str(repo)], env=env, capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, result.stderr
    argv = (tmp_path / "tmux.log").read_text().splitlines()
    return shlex.split(argv[-1]), home, fake_bin


def test_claude_runs_under_the_pane_loop_found_on_path(tmp_path):
    command, _, fake_bin = _start(tmp_path, loop_on_path=True)
    assert command == ["env", "-u", "CLAUDE_CONFIG_DIR", str(fake_bin / "claude-pane-loop"), "claude", "--remote-control", "my repo"]


def test_claude_runs_under_the_pane_loop_in_the_dotfiles_bin(tmp_path):
    command, home, _ = _start(tmp_path, loop_in_home=True)
    assert command[:4] == ["env", "-u", "CLAUDE_CONFIG_DIR", str(home / ".dotfiles" / "bin" / "claude-pane-loop")]


def test_a_relative_path_entry_still_yields_an_absolute_loop_path(tmp_path):
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    _executable(fake_bin / "tmux", RECORD_TMUX)
    _executable(fake_bin / "claude-pane-loop")
    (tmp_path / "my repo").mkdir()
    env = {
        "PATH": "bin:/usr/bin:/bin",
        "HOME": str(tmp_path / "home"),
        "TMUX_LOG": str(tmp_path / "tmux.log"),
        "CLAUDE_REMOTE_SETTINGS": str(tmp_path / "missing.json"),
    }
    subprocess.run(
        [str(SCRIPT), str(tmp_path / "my repo")], env=env, cwd=tmp_path, capture_output=True, text=True, check=True,
    )
    command = shlex.split((tmp_path / "tmux.log").read_text().splitlines()[-1])
    assert command[3] == str(fake_bin / "claude-pane-loop")


def test_without_a_pane_loop_claude_runs_bare(tmp_path):
    command, _, _ = _start(tmp_path)
    assert command == ["env", "-u", "CLAUDE_CONFIG_DIR", "claude", "--remote-control", "my repo"]


def test_the_account_env_stays_outside_the_loop_so_a_resumed_claude_keeps_it(tmp_path):
    config_dir = tmp_path / "acct"
    config_dir.mkdir()
    command, _, fake_bin = _start(tmp_path, loop_on_path=True, extra=("--config-dir", str(config_dir)))
    assert command[:3] == ["env", f"CLAUDE_CONFIG_DIR={config_dir}", str(fake_bin / "claude-pane-loop")]


@pytest.mark.skipif(shutil.which("shellcheck") is None, reason="shellcheck not installed")
def test_script_passes_shellcheck():
    result = subprocess.run(["shellcheck", str(SCRIPT)], capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stdout
