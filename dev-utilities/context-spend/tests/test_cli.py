from __future__ import annotations

import json
import os
from pathlib import Path

import ctxspend
import pytest
from conftest import usage_entry


@pytest.fixture(autouse=True)
def isolated(tmp_path, monkeypatch):
    monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path / "state"))
    monkeypatch.setenv("CLAUDE_CONFIG_DIR", str(tmp_path / "claude"))
    monkeypatch.delenv("CTX_GUARD_THRESHOLD", raising=False)
    monkeypatch.delenv("CTX_WINDOW_TOKENS", raising=False)


def hook_json(path, session="s1"):
    return json.dumps({"session_id": session, "transcript_path": str(path)})


def test_guard_exit_zero_and_json_system_message_on_crossing(transcript, monkeypatch):
    monkeypatch.setenv("CTX_GUARD_THRESHOLD", "1000")
    path = transcript([usage_entry("claude-opus-5-5", 5000, 0, 0, 1)])
    code, out = ctxspend.main(["guard"], hook_json(path))
    assert code == 0
    assert "/compact" in json.loads(out)["systemMessage"]


def test_guard_prints_nothing_when_silent(transcript):
    path = transcript([usage_entry("claude-opus-5-5", 5000, 0, 0, 1)])
    assert ctxspend.main(["guard"], hook_json(path)) == (0, "")


def test_guard_never_fails_on_garbage_input():
    assert ctxspend.main(["guard"], "not json") == (0, "")


def test_statusline_prints_percent(transcript, monkeypatch):
    monkeypatch.setenv("CTX_WINDOW_TOKENS", "10000")
    path = transcript([usage_entry("claude-opus-5-5", 5000, 0, 0, 1)])
    assert ctxspend.main(["statusline"], hook_json(path)) == (0, "ctx 50%")


def test_statusline_empty_on_garbage_input():
    assert ctxspend.main(["statusline"], "nope") == (0, "")


def test_report_lists_cost_split_and_overhead(tmp_path, transcript):
    cache = tmp_path / "claude" / "plugins" / "cache" / "mkt" / "plug" / "1.0"
    (cache / "skills" / "a").mkdir(parents=True)
    (cache / "skills" / "a" / "SKILL.md").write_text(
        "---\nname: a\ndescription: does things\n---\nbody"
    )
    (tmp_path / "claude" / "settings.json").write_text(
        json.dumps({"enabledPlugins": {"plug@mkt": True}})
    )
    path = transcript([usage_entry("claude-opus-5-5", 5000, 0, 0, 1)])
    code, out = ctxspend.main(["report", "--session", "x", "--transcript", str(path)], "")
    assert code == 0
    for word in ("fixed", "growth", "total", "plug@mkt"):
        assert word in out


def test_report_labels_estimate(transcript):
    path = transcript([usage_entry("mystery-model", 5000, 0, 0, 1)])
    _, out = ctxspend.main(["report", "--transcript", str(path)], "")
    assert "estimated" in out


def test_report_reports_missing_session():
    code, out = ctxspend.main(["report", "--session", "nope"], "")
    assert code == 1
    assert "no session" in out


def test_report_rejects_bad_session_id():
    code, _ = ctxspend.main(["report", "--session", "../etc"], "")
    assert code == 1


def test_find_session_by_id(tmp_path):
    target = tmp_path / "claude" / "projects" / "p" / "abc-1.jsonl"
    target.parent.mkdir(parents=True)
    target.write_text("")
    assert ctxspend.find_session(tmp_path / "claude", "abc-1", tmp_path) == target


def test_find_session_by_id_prefers_newest_duplicate(tmp_path):
    older = tmp_path / "claude" / "projects" / "a" / "dup.jsonl"
    newer = tmp_path / "claude" / "projects" / "b" / "dup.jsonl"
    for path, mtime in ((older, 100), (newer, 200)):
        path.parent.mkdir(parents=True)
        path.write_text("")
        os.utime(path, (mtime, mtime))
    assert ctxspend.find_session(tmp_path / "claude", "dup", tmp_path) == newer


def test_find_session_newest_for_cwd(tmp_path):
    cwd = tmp_path / "work" / ".repo"
    project = tmp_path / "claude" / "projects" / ctxspend.project_dir_name(cwd)
    project.mkdir(parents=True)
    (project / "old.jsonl").write_text("")
    new = project / "new.jsonl"
    new.write_text("")
    os.utime(project / "old.jsonl", (1, 1))
    assert ctxspend.find_session(tmp_path / "claude", None, cwd) == new


def test_project_dir_name_replaces_slash_and_dot():
    assert ctxspend.project_dir_name(Path("/home/a/.dot/b")) == "-home-a--dot-b"


def test_project_dir_name_replaces_every_non_alphanumeric():
    assert ctxspend.project_dir_name(Path("/home/a b/my_proj")) == "-home-a-b-my-proj"


def test_report_prints_na_when_saving_is_not_applicable(transcript, monkeypatch):
    monkeypatch.setenv("CTX_GUARD_THRESHOLD", "1000")
    path = transcript([usage_entry("claude-opus-5-5", 5000, 0, 0, 1)])
    _, out = ctxspend.main(["report", "--transcript", str(path)], "")
    assert "estimated saving if compacted there: n/a" in out


def test_bad_env_falls_back_to_default(transcript, monkeypatch):
    monkeypatch.setenv("CTX_GUARD_THRESHOLD", "abc")
    path = transcript([usage_entry("claude-opus-5-5", 5000, 0, 0, 1)])
    assert ctxspend.main(["guard"], hook_json(path)) == (0, "")


def test_unknown_subcommand_exits_nonzero_with_usage():
    code, out = ctxspend.main(["bogus"], "")
    assert code != 0
    assert "usage" in out.lower()
