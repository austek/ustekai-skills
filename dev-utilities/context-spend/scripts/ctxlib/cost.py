from dataclasses import dataclass

from ctxlib.usage import Turn

PER_MILLION = 1_000_000
POST_COMPACT_OVERHEAD = 10_000


@dataclass(frozen=True)
class Price:
    input: float
    cache_write: float
    cache_read: float
    output: float


PRICES: dict[str, Price] = {
    "claude-fable-5-2": Price(8.00, 10.00, 0.20, 40.00),
    "claude-opus-5-5": Price(4.00, 5.00, 0.20, 20.00),
    "claude-sonnet-5-5": Price(2.00, 2.50, 0.10, 10.00),
    "claude-haiku-5-5": Price(0.10, 0.125, 0.01, 0.50),
}

DEFAULT_PRICE = PRICES["claude-opus-5-5"]


@dataclass(frozen=True)
class SpendReport:
    total: float
    fixed: float
    growth: float
    turns: int
    crossing_turn: int | None
    saving_if_compacted: float
    estimated: bool


def is_known_model(model: str) -> bool:
    return model in PRICES


def price_for(model: str) -> Price:
    return PRICES.get(model, DEFAULT_PRICE)


def turn_cost(turn: Turn) -> float:
    p = price_for(turn.model)
    paid = (
        turn.input * p.input
        + turn.cache_write * p.cache_write
        + turn.cache_read * p.cache_read
        + turn.output * p.output
    )
    return paid / PER_MILLION


def _fixed_cost(turns: list[Turn]) -> float:
    base = turns[0].context if turns else 0
    return sum(
        min(base, t.context) * price_for(t.model).cache_read for t in turns
    ) / PER_MILLION


def _crossing_turn(turns: list[Turn], threshold: int) -> int | None:
    return next((i for i, t in enumerate(turns) if t.context >= threshold), None)


def _saving(turns: list[Turn], crossing: int | None) -> float:
    if crossing is None:
        return 0.0
    post = turns[0].context + POST_COMPACT_OVERHEAD
    avoided = sum(
        max(t.context - post, 0) * price_for(t.model).cache_read
        for t in turns[crossing + 1 :]
    )
    rewrite = post * price_for(turns[crossing].model).cache_write
    return max((avoided - rewrite) / PER_MILLION, 0.0)


def build_report(turns: list[Turn], threshold: int) -> SpendReport:
    total = sum(turn_cost(t) for t in turns)
    fixed = _fixed_cost(turns)
    crossing = _crossing_turn(turns, threshold)
    return SpendReport(
        total=total,
        fixed=fixed,
        growth=total - fixed,
        turns=len(turns),
        crossing_turn=crossing,
        saving_if_compacted=_saving(turns, crossing),
        estimated=not all(is_known_model(t.model) for t in turns),
    )
