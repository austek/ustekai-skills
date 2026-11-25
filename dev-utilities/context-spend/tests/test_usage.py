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
