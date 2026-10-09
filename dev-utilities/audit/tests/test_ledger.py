import json
from datetime import datetime
from zoneinfo import ZoneInfo

from auditlib import ledger

LONDON = ZoneInfo("Europe/London")


def entry(mid, i, o, cc=0, cr=0):
    usage = {
        "input_tokens": i,
        "output_tokens": o,
        "cache_creation_input_tokens": cc,
        "cache_read_input_tokens": cr,
    }
    return {"type": "assistant", "message": {"id": mid, "usage": usage}}


def write(path, entries):
    path.write_text("\n".join(json.dumps(e) for e in entries))


def test_usage_dedupes_repeated_ids_and_ignores_cache_reads(tmp_path):
    f = tmp_path / "s.jsonl"
    write(f, [entry("m1", 10, 5), entry("m1", 10, 5), entry("m2", 1, 1, cc=3, cr=1000)])
    assert ledger.usage_tokens([f]) == 15 + 5


def test_usage_keeps_largest_streamed_snapshot(tmp_path):
    f = tmp_path / "s.jsonl"
    write(f, [entry("m1", 10, 5), entry("m1", 10, 7)])
    assert ledger.usage_tokens([f]) == 17


def test_usage_ignores_non_assistant_and_bad_lines(tmp_path):
    f = tmp_path / "s.jsonl"
    f.write_text('{"type":"user"}\nnot json\n' + json.dumps(entry("m", 2, 2)))
    assert ledger.usage_tokens([f]) == 4


def test_session_files_include_subagent_transcripts(tmp_path):
    (tmp_path / "abc.jsonl").write_text("")
    (tmp_path / "abc" / "sub").mkdir(parents=True)
    (tmp_path / "abc" / "sub" / "x.jsonl").write_text("")
    names = sorted(p.name for p in ledger.session_files(tmp_path, "abc"))
    assert names == ["abc.jsonl", "x.jsonl"]


def test_decision():
    assert ledger.decision(spent=0, est=10, budget=100) == "run"
    assert ledger.decision(spent=95, est=1, budget=100) == "stop"
    assert ledger.decision(spent=50, est=60, budget=100) == "skip"


def state(spent=0, budget=100, units=None):
    units = units or {"a": "pending", "b": "pending"}
    return {"budget": {"unit": "tokens", "amount": budget}, "spent": spent, "units": units}


def test_next_unit_skips_oversized_then_runs_smaller():
    assert ledger.next_unit(state(), {"a": 500, "b": 50}) == ("run", "b")


def test_next_unit_exhausted_when_nothing_fits():
    assert ledger.next_unit(state(), {"a": 500, "b": 600}) == ("exhausted", "")


def test_next_unit_stops_at_soft_limit():
    assert ledger.next_unit(state(spent=95), {"a": 1, "b": 1}) == ("stop", "")


def test_next_unit_done_when_nothing_pending():
    st = state(units={"a": "done"})
    assert ledger.next_unit(st, {"a": 1}) == ("done", "")


def test_reset_same_day():
    now = datetime(2026, 10, 9, 1, 0, tzinfo=LONDON)
    got = ledger.find_reset("You've hit your session limit · resets 2:50am (Europe/London)", now)
    assert got == [datetime(2026, 10, 9, 2, 50, tzinfo=LONDON)]


def test_reset_rolls_to_next_day():
    now = datetime(2026, 10, 9, 5, 0, tzinfo=LONDON)
    got = ledger.find_reset("resets 3:50am (Europe/London)", now)
    assert got[0].day == 10 and got[0].hour == 3


def test_reset_pm_without_minutes():
    now = datetime(2026, 10, 9, 5, 0, tzinfo=LONDON)
    got = ledger.find_reset("resets 4pm (Europe/London)", now)
    assert (got[0].hour, got[0].minute) == (16, 0)


def test_reset_no_match_returns_empty():
    assert ledger.find_reset("all good", datetime(2026, 10, 9, 5, 0, tzinfo=LONDON)) == []
