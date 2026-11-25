from __future__ import annotations

import json

import pytest
from conftest import usage_entry
from ctxlib.usage import Turn, latest_context, load_subagent_turns, load_turns

COUNTERS = ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens", "output_tokens")


@pytest.mark.parametrize("field", COUNTERS)
@pytest.mark.parametrize("bad", ["5", -1, True, 1.5])
def test_entry_with_invalid_counter_is_skipped(transcript, field, bad):
    broken = usage_entry("m", 1, 1, 1, 1)
    broken["message"]["usage"][field] = bad
    path = transcript([broken, usage_entry("m", 2, 0, 0, 1)])
    assert load_turns(path) == [Turn("m", 2, 0, 0, 1)]


def test_null_counter_counts_as_zero(transcript):
    entry = usage_entry("m", 1, 1, 1, 1)
    entry["message"]["usage"]["output_tokens"] = None
    assert load_turns(transcript([entry])) == [Turn("m", 1, 1, 1, 0)]


def test_cache_write_1h_is_parsed_from_cache_creation(transcript):
    path = transcript([usage_entry("m", 1, 10, 0, 1, cache_1h=6)])
    assert load_turns(path) == [Turn("m", 1, 10, 0, 1, 6)]


@pytest.mark.parametrize("bad", ["6", -1, True, 1.5, None])
def test_invalid_cache_write_1h_counts_as_zero(transcript, bad):
    path = transcript([usage_entry("m", 1, 10, 0, 1, cache_1h=bad)])
    assert load_turns(path) == [Turn("m", 1, 10, 0, 1, 0)]


def test_cache_write_1h_is_capped_at_cache_write(transcript):
    path = transcript([usage_entry("m", 1, 10, 0, 1, cache_1h=50)])
    assert load_turns(path)[0].cache_write_1h == 10


def test_cache_creation_that_is_not_an_object_counts_as_zero(transcript):
    entry = usage_entry("m", 1, 10, 0, 1)
    entry["message"]["usage"]["cache_creation"] = "x"
    assert load_turns(transcript([entry])) == [Turn("m", 1, 10, 0, 1, 0)]


def test_sidechain_entries_are_skipped_by_default(transcript):
    path = transcript([usage_entry("m", 1, 0, 0, 1, sidechain=True), usage_entry("m", 2, 0, 0, 1)])
    assert load_turns(path) == [Turn("m", 2, 0, 0, 1)]


def test_include_sidechain_keeps_sidechain_entries(transcript):
    path = transcript([usage_entry("m", 1, 0, 0, 1, sidechain=True), usage_entry("m", 2, 0, 0, 1)])
    assert len(load_turns(path, include_sidechain=True)) == 2


def write_agent(tmp_path, name, entries):
    folder = tmp_path / "sess" / "subagents"
    folder.mkdir(parents=True, exist_ok=True)
    (folder / name).write_text("\n".join(json.dumps(e) for e in entries))


def test_load_subagent_turns_reads_each_agent_file(tmp_path):
    main = tmp_path / "sess.jsonl"
    main.write_text("")
    write_agent(tmp_path, "agent-a.jsonl", [usage_entry("m", 1, 0, 0, 1, sidechain=True)])
    write_agent(tmp_path, "agent-b.jsonl", [usage_entry("m", 2, 0, 0, 1, sidechain=True)])
    (tmp_path / "sess" / "subagents" / "agent-a.meta.json").write_text("{}")
    assert load_subagent_turns(main) == [[Turn("m", 1, 0, 0, 1)], [Turn("m", 2, 0, 0, 1)]]


def test_load_subagent_turns_empty_without_directory(tmp_path):
    main = tmp_path / "sess.jsonl"
    main.write_text("")
    assert load_subagent_turns(main) == []


def test_latest_context_ignores_subagent_files(tmp_path):
    main = tmp_path / "sess.jsonl"
    main.write_text(json.dumps(usage_entry("m", 7, 0, 0, 1)))
    write_agent(tmp_path, "agent-a.jsonl", [usage_entry("m", 9000, 0, 0, 1, sidechain=True)])
    assert latest_context(main) == 7


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


def test_entries_sharing_message_id_count_once(transcript):
    same = [usage_entry("m", 1, 2, 3, 4, message_id="a") for _ in range(3)]
    assert load_turns(transcript(same)) == [Turn("m", 1, 2, 3, 4)]


def test_different_message_ids_count_separately(transcript):
    path = transcript(
        [usage_entry("m", 1, 1, 1, 1, "a"), usage_entry("m", 2, 2, 2, 2, "b")]
    )
    assert len(load_turns(path)) == 2


def test_request_id_is_the_fallback_key(transcript):
    path = transcript(
        [
            usage_entry("m", 1, 1, 1, 1, request_id="r"),
            usage_entry("m", 1, 1, 1, 1, request_id="r"),
            usage_entry("m", 1, 1, 1, 1, request_id="s"),
        ]
    )
    assert len(load_turns(path)) == 2


def test_entries_without_ids_are_all_kept(transcript):
    path = transcript([usage_entry("m", 1, 1, 1, 1)] * 3)
    assert len(load_turns(path)) == 3


def test_last_entry_per_id_wins_in_first_seen_order(transcript):
    path = transcript(
        [
            usage_entry("m", 1, 0, 0, 1, "a"),
            usage_entry("m", 2, 0, 0, 1, "b"),
            usage_entry("m", 3, 0, 0, 9, "a"),
        ]
    )
    assert load_turns(path) == [Turn("m", 3, 0, 0, 9), Turn("m", 2, 0, 0, 1)]


def test_deeply_nested_line_is_skipped(transcript):
    path = transcript([usage_entry("m", 1, 1, 1, 1), "[" * 100000])
    assert len(load_turns(path)) == 1


def test_zero_context_entries_are_skipped(transcript):
    path = transcript([usage_entry("m", 1, 1, 1, 1), usage_entry("m", 0, 0, 0, 0)])
    assert len(load_turns(path)) == 1
    assert latest_context(path) == 3
