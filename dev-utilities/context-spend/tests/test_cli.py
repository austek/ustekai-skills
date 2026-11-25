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


def write_session(tmp_path, agents):
    project = tmp_path / "claude" / "projects" / "p"
    (project / "sess" / "subagents").mkdir(parents=True)
    main = project / "sess.jsonl"
    main.write_text(json.dumps(usage_entry("claude-opus-5-5", 25_000, 0, 0, 0)))
    for name, entry in agents.items():
        (project / "sess" / "subagents" / name).write_text(json.dumps(entry))
    return main


def test_report_prints_parent_subagents_and_total(tmp_path):
    main = write_session(
        tmp_path,
        {
            "agent-a.jsonl": usage_entry("claude-sonnet-5-5", 250_000, 0, 0, 0, sidechain=True),
            "agent-b.jsonl": usage_entry(
                "claude-opus-5-5", 0, 60_000, 0, 0, cache_1h=40_000, sidechain=True
            ),
        },
    )
    _, out = ctxspend.main(["report", "--transcript", str(main)], "")
    assert "parent: $0.10" in out.splitlines()
    assert "subagents: $0.92 (2 agents)" in out.splitlines()
    assert "total: $1.02" in out.splitlines()


def test_report_without_subagent_directory_prints_zero_agents(transcript):
    path = transcript([usage_entry("claude-opus-5-5", 25_000, 0, 0, 0)])
    _, out = ctxspend.main(["report", "--transcript", str(path)], "")
    assert "subagents: $0.00 (0 agents)" in out.splitlines()
    assert "total: $0.10" in out.splitlines()


def test_report_marks_unknown_subagent_model_as_estimated(tmp_path):
    main = write_session(
        tmp_path, {"agent-a.jsonl": usage_entry("mystery", 1, 0, 0, 0, sidechain=True)}
    )
    _, out = ctxspend.main(["report", "--transcript", str(main)], "")
    lines = out.splitlines()
    assert not any(line.startswith("parent:") and "estimated" in line for line in lines)
    assert any(line.startswith("subagents:") and "(estimated)" in line for line in lines)
    assert any(line.startswith("total:") and "(estimated)" in line for line in lines)


def test_report_labels_parent_only_figures(tmp_path):
    main = write_session(tmp_path, {})
    _, out = ctxspend.main(["report", "--transcript", str(main)], "")
    for label in ("context (parent):", "fixed (parent):", "growth (parent):", "crossing turn (parent):"):
        assert label in out


def test_guard_ignores_subagent_files(tmp_path, monkeypatch):
    monkeypatch.setenv("CTX_GUARD_THRESHOLD", "1000")
    main = write_session(
        tmp_path, {"agent-a.jsonl": usage_entry("claude-opus-5-5", 9000, 0, 0, 0, sidechain=True)}
    )
    main.write_text(json.dumps(usage_entry("claude-opus-5-5", 500, 0, 0, 0)))
    assert ctxspend.main(["guard"], hook_json(main)) == (0, "")


def test_report_loads_context_and_cost_from_one_read(transcript, monkeypatch):
    path = transcript([usage_entry("claude-opus-5-5", 25_000, 0, 0, 0)])
    reads = []
    real = Path.read_text

    def spy(self, *args, **kwargs):
        reads.append(self)
        return real(self, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", spy)
    ctxspend.main(["report", "--transcript", str(path)], "")
    assert reads.count(path) == 1


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
    assert "estimated saving if compacted there (parent): n/a" in out


def test_bad_env_falls_back_to_default(transcript, monkeypatch):
    monkeypatch.setenv("CTX_GUARD_THRESHOLD", "abc")
    path = transcript([usage_entry("claude-opus-5-5", 5000, 0, 0, 1)])
    assert ctxspend.main(["guard"], hook_json(path)) == (0, "")


def test_unknown_subcommand_exits_nonzero_with_usage():
    code, out = ctxspend.main(["bogus"], "")
    assert code != 0
    assert "usage" in out.lower()
