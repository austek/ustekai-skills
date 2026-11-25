import json

from conftest import usage_entry
from ctxlib.usage import Turn, latest_context, load_turns


def test_load_turns_reads_usage_fields(transcript):
    path = transcript([usage_entry("opus", 1, 2, 3, 4)])
    assert load_turns(path) == [Turn("opus", 1, 2, 3, 4)]


def test_context_sums_input_and_cache_fields():
    assert Turn("m", 1, 20, 300, 4000).context == 321


def test_entries_without_usage_are_skipped(transcript):
    path = transcript(
        [
            {"type": "user", "message": {"content": "hi"}},
            {"type": "assistant", "message": {"model": "m"}},
            usage_entry("m", 1, 1, 1, 1),
        ]
    )
    assert len(load_turns(path)) == 1


def test_truncated_last_line_is_ignored(transcript):
    path = transcript([usage_entry("m", 1, 1, 1, 1), '{"type": "assis'])
    assert len(load_turns(path)) == 1


def test_empty_file_gives_no_turns(transcript):
    assert load_turns(transcript([])) == []


def test_latest_context_is_last_turn(transcript):
    path = transcript([usage_entry("m", 1, 1, 1, 1), usage_entry("m", 10, 20, 30, 1)])
    assert latest_context(path) == 60


def test_latest_context_zero_for_empty(transcript):
    assert latest_context(transcript([])) == 0


def test_unicode_line_separator_in_text_keeps_turn(transcript):
    entry = usage_entry("m", 1, 2, 3, 4)
    entry["message"]["content"] = "a b\u0085c\x0bd\x0ce"
    assert load_turns(transcript([entry])) == [Turn("m", 1, 2, 3, 4)]


def test_truncated_multibyte_tail_does_not_crash(tmp_path):
    good = json.dumps(usage_entry("m", 1, 2, 3, 4)).encode()
    partial = '{"text": "é'.encode()[:-1]
    path = tmp_path / "t.jsonl"
    path.write_bytes(good + b"\n" + partial)
    assert load_turns(path) == [Turn("m", 1, 2, 3, 4)]


def test_sidechain_entries_are_skipped(transcript):
    side = usage_entry("m", 9, 9, 9, 9)
    side["isSidechain"] = True
    path = transcript([usage_entry("m", 1, 1, 1, 1), side])
    assert latest_context(path) == 3


def test_zero_context_entries_are_skipped(transcript):
    path = transcript([usage_entry("m", 1, 1, 1, 1), usage_entry("m", 0, 0, 0, 0)])
    assert len(load_turns(path)) == 1
    assert latest_context(path) == 3
