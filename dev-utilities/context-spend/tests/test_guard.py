from __future__ import annotations

import errno
import json
import os
import stat

import pytest
from conftest import usage_entry, write_transcript
from ctxlib import guard
from ctxlib.guard import default_state_dir, guard_message, statusline_text


def make_transcript(tmp_path, tokens, name="t.jsonl"):
    path = write_transcript(tmp_path, [usage_entry("m", tokens, 0, 0, 1)])
    target = tmp_path / name
    path.replace(target)
    return target


def payload(session, path):
    return json.dumps({"session_id": session, "transcript_path": str(path)})


@pytest.fixture
def state(tmp_path):
    return tmp_path / "state"


def test_below_threshold_is_silent(tmp_path, state):
    path = make_transcript(tmp_path, 1000)
    assert guard_message(payload("s1", path), 5000, state) is None


def test_first_crossing_returns_message_naming_compact_and_context_size(tmp_path, state):
    path = make_transcript(tmp_path, 150_000)
    msg = guard_message(payload("s1", path), 100_000, state)
    assert msg is not None
    assert "150K" in msg
    assert "/compact" in msg.splitlines()
    assert "/clear" in msg.splitlines()
    assert len(msg) < 300


def test_second_call_in_same_session_is_silent(tmp_path, state):
    path = make_transcript(tmp_path, 150_000)
    assert guard_message(payload("s1", path), 100_000, state) is not None
    assert guard_message(payload("s1", path), 100_000, state) is None


def test_recrossing_after_drop_warns_again(tmp_path, state):
    high = make_transcript(tmp_path, 150_000)
    assert guard_message(payload("s1", high), 100_000, state) is not None
    low = make_transcript(tmp_path, 1000, "low.jsonl")
    assert guard_message(payload("s1", low), 100_000, state) is None
    assert guard_message(payload("s1", high), 100_000, state) is not None


def test_sessions_are_tracked_independently(tmp_path, state):
    path = make_transcript(tmp_path, 150_000)
    assert guard_message(payload("a", path), 100_000, state) is not None
    assert guard_message(payload("b", path), 100_000, state) is not None
    assert guard_message(payload("a", path), 100_000, state) is None


def test_bad_json_is_silent(state):
    assert guard_message("{not json", 1, state) is None
    assert guard_message("[1]", 1, state) is None
    assert guard_message(json.dumps({"session_id": 1, "transcript_path": "x"}), 1, state) is None


def test_missing_transcript_is_silent(tmp_path, state):
    assert guard_message(payload("s1", tmp_path / "nope.jsonl"), 1, state) is None


@pytest.mark.parametrize("bad", ["../evil", "a/b", "", "x" * 65])
def test_unsafe_session_id_is_silent(tmp_path, state, bad):
    path = make_transcript(tmp_path, 150_000)
    assert guard_message(payload(bad, path), 100_000, state) is None
    assert not (tmp_path / "evil").exists()


def test_state_dir_created_with_mode_0700(tmp_path, state):
    path = make_transcript(tmp_path, 150_000)
    guard_message(payload("s1", path), 100_000, state)
    assert stat.S_IMODE(state.stat().st_mode) == 0o700
    assert (state / "warned" / "s1").is_file()


def test_read_error_leaves_marker_and_warns_nothing(tmp_path, state):
    marker = state / "warned" / "s1"
    marker.parent.mkdir(parents=True)
    marker.write_text("1")
    assert guard_message(payload("s1", tmp_path / "nope.jsonl"), 100_000, state) is None
    assert marker.exists()


@pytest.mark.parametrize("threshold", [0, -1])
def test_non_positive_threshold_disables_guard(tmp_path, state, threshold):
    path = make_transcript(tmp_path, 150_000)
    assert guard_message(payload("s1", path), threshold, state) is None
    assert not (state / "warned" / "s1").exists()


def test_zero_context_never_warns(tmp_path, state):
    path = tmp_path / "empty.jsonl"
    path.write_text("")
    assert guard_message(payload("s1", path), 1, state) is None


def test_lost_marker_race_is_silent(tmp_path, state):
    path = make_transcript(tmp_path, 150_000)
    marker = state / "warned" / "s1"
    marker.parent.mkdir(parents=True)
    marker.write_text("1")
    assert guard_message(payload("s1", path), 100_000, state) is None


def test_marker_create_os_error_is_silent(tmp_path, state, monkeypatch):
    path = make_transcript(tmp_path, 150_000)

    def deny(*args, **kwargs):
        raise PermissionError

    monkeypatch.setattr(guard.os, "open", deny)
    assert guard_message(payload("s1", path), 100_000, state) is None


def test_deeply_nested_stdin_is_silent(state):
    assert guard_message("[" * 100000, 1, state) is None
    assert statusline_text("[" * 100000, 1000) == ""


def test_statusline_percent_of_window(tmp_path):
    path = make_transcript(tmp_path, 76_000)
    assert statusline_text(payload("s1", path), 200_000) == "ctx 38%"


def test_statusline_empty_on_bad_input(tmp_path):
    assert statusline_text("nope", 200_000) == ""
    assert statusline_text(payload("s1", tmp_path / "missing"), 200_000) == ""
    assert statusline_text(json.dumps({"session_id": "s"}), 200_000) == ""
    assert statusline_text(payload("s1", make_transcript(tmp_path, 5)), 0) == ""


def test_default_state_dir_uses_xdg(monkeypatch, tmp_path):
    monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path))
    assert default_state_dir() == tmp_path / "ctx-spend"


def test_default_state_dir_falls_back_to_home(monkeypatch, tmp_path):
    monkeypatch.delenv("XDG_STATE_HOME", raising=False)
    monkeypatch.setenv("HOME", str(tmp_path))
    assert default_state_dir() == tmp_path / ".local" / "state" / "ctx-spend"


class FailingHandle:
    def __init__(self, fd):
        self.fd = fd

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        os.close(self.fd)
        return False

    def write(self, text):
        raise OSError(errno.ENOSPC, "no space")


def test_failed_marker_write_removes_marker_and_returns_false(monkeypatch, tmp_path):
    marker = tmp_path / "state" / "warned" / "s1"
    monkeypatch.setattr(guard.os, "fdopen", lambda fd, mode: FailingHandle(fd))
    assert guard._create_marker(marker, 5) is False
    assert not marker.exists()


def test_successful_marker_write_keeps_token_text(tmp_path):
    marker = tmp_path / "state" / "warned" / "s1"
    assert guard._create_marker(marker, 5) is True
    assert marker.read_text() == "5"
