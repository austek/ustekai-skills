from __future__ import annotations

import pytest
from ctxlib import cost
from ctxlib.cost import Price, build_report, turn_cost
from ctxlib.usage import Turn

M = 1_000_000


@pytest.fixture(autouse=True)
def price_table(monkeypatch):
    monkeypatch.setattr(
        cost,
        "PRICES",
        {"m-a": Price(1.0, 2.0, 0.5, 10.0), "m-b": Price(2.0, 4.0, 1.0, 20.0)},
    )
    monkeypatch.setattr(cost, "DEFAULT_PRICE", Price(3.0, 3.0, 3.0, 3.0))


def reads(model: str, tokens: int) -> Turn:
    return Turn(model, 0, 0, tokens, 0)


def test_turn_cost_applies_each_rate():
    assert turn_cost(Turn("m-a", M, M, M, M)) == pytest.approx(13.5)
    assert turn_cost(Turn("m-b", M, M, M, M)) == pytest.approx(27.0)


def test_unknown_model_uses_default_and_flags_estimated():
    report = build_report([Turn("mystery", M, 0, 0, 0)], threshold=10 * M)
    assert report.total == pytest.approx(3.0)
    assert report.estimated is True
    assert build_report([reads("m-a", M)], threshold=10 * M).estimated is False


def test_fixed_cost_is_first_turn_context_at_cache_read_rate():
    report = build_report([reads("m-a", M), reads("m-a", 3 * M)], threshold=10 * M)
    assert report.fixed == pytest.approx(1.0)


def test_growth_is_total_minus_fixed():
    report = build_report([reads("m-a", M), reads("m-a", 3 * M)], threshold=10 * M)
    assert report.total == pytest.approx(2.0)
    assert report.growth == pytest.approx(1.0)
    assert report.turns == 2


def test_crossing_turn_is_first_turn_at_or_above_threshold():
    turns = [reads("m-a", n) for n in (M, 1_500_000, 2 * M, 3 * M)]
    assert build_report(turns, threshold=2 * M).crossing_turn == 2


def test_no_crossing_gives_none_and_zero_saving():
    report = build_report([reads("m-a", M), reads("m-a", 2 * M)], threshold=10 * M)
    assert report.crossing_turn is None
    assert report.saving_if_compacted == 0.0


def test_saving_counts_turns_after_crossing_against_post_compact_context():
    turns = [reads("m-a", M)] + [reads("m-a", 5 * M)] * 4
    report = build_report(turns, threshold=5 * M)
    assert report.crossing_turn == 1
    assert report.saving_if_compacted == pytest.approx(3 * 1.995 - 2.02)


SESSION = [3 * M, M, 5 * M, 5 * M, 5 * M, 5 * M]


def test_base_is_smallest_context_not_first_turn():
    report = build_report([reads("m-a", n) for n in SESSION], threshold=5 * M)
    assert report.fixed == pytest.approx(6 * 0.5)
    assert report.crossing_turn == 2
    assert report.saving_if_compacted == pytest.approx(3 * 1.995 - 2.02)


def test_first_turn_at_or_above_threshold_makes_saving_not_applicable():
    report = build_report([reads("m-a", n) for n in SESSION], threshold=3 * M)
    assert report.crossing_turn == 0
    assert report.saving_if_compacted is None


def test_long_context_tier_applies_above_its_limit(monkeypatch):
    monkeypatch.setattr(cost, "LONG_CONTEXT", {"m-a": (2 * M, Price(10.0, 20.0, 5.0, 100.0))})
    assert turn_cost(Turn("m-a", 2 * M, 0, 0, 0)) == pytest.approx(2.0)
    assert turn_cost(Turn("m-a", 2 * M + 1, 0, 0, 0)) == pytest.approx(20.00001)
    assert turn_cost(Turn("m-b", 3 * M, 0, 0, 0)) == pytest.approx(6.0)
    assert turn_cost(Turn("m-a", 0, 0, 3 * M, M)) == pytest.approx(15.0 + 100.0)
