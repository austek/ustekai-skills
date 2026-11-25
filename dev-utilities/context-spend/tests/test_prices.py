from __future__ import annotations

import pytest
from ctxlib.cost import turn_cost
from ctxlib.usage import Turn

HAIKU = "claude-haiku-5-5"


def test_haiku_at_the_limit_uses_base_rates():
    assert turn_cost(Turn(HAIKU, 100_000, 0, 0, 1_000_000)) == pytest.approx(0.01 + 0.50)


def test_haiku_above_the_limit_uses_long_context_rates():
    turn = Turn(HAIKU, 100_000, 1, 1, 1_000_000)
    assert turn_cost(turn) == pytest.approx(0.05 + 0.625e-6 + 0.05e-6 + 2.50)


def test_other_models_are_unchanged_above_100k():
    assert turn_cost(Turn("claude-sonnet-5-5", 200_000, 0, 0, 0)) == pytest.approx(0.4)
