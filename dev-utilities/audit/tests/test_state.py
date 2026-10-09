import os
from auditlib import state


def test_atomic_write_roundtrip_preserves_unit_order(tmp_path):
    path = tmp_path / ".audit" / "state.json"
    st = state.new_state(["z", "a", "m"], {"unit": "tokens", "amount": 100})
    state.atomic_write(path, st)
    assert list(state.load(path)["units"]) == ["z", "a", "m"]


def test_load_missing_returns_empty(tmp_path):
    assert state.load(tmp_path / "nope.json") == {}


def test_stale_tmp_file_is_ignored(tmp_path):
    path = tmp_path / "state.json"
    state.atomic_write(path, {"spent": 1})
    (tmp_path / "state.json.tmp").write_text("{broken")
    assert state.load(path) == {"spent": 1}


def test_mark_is_pure_and_accumulates():
    st = state.new_state(["a", "b"], {"unit": "tokens", "amount": 10})
    st2 = state.mark(st, "a", "done", 4)
    assert st["spent"] == 0 and st2["spent"] == 4
    assert state.pending(st2) == ["b"]


def test_atomic_write_fsyncs_before_replace(tmp_path, monkeypatch):
    calls = []
    real = os.fsync
    monkeypatch.setattr(os, "fsync", lambda fd: (calls.append(fd), real(fd))[1])
    state.atomic_write(tmp_path / "s.json", {"a": 1})
    assert calls
