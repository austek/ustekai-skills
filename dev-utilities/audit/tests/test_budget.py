import pytest

from auditlib import budget


@pytest.mark.parametrize(
    "text,expected",
    [
        ("2M", {"unit": "tokens", "amount": 2_000_000}),
        ("500k", {"unit": "tokens", "amount": 500_000}),
        ("1200", {"unit": "tokens", "amount": 1200}),
        ("$5", {"unit": "usd", "amount": 5.0}),
    ],
)
def test_parse_plain(text, expected):
    assert budget.parse_budget(text) == expected


def test_percent_uses_ceiling():
    assert budget.parse_budget("30%", 1_000_000) == {"unit": "tokens", "amount": 300_000}


def test_percent_without_ceiling_fails():
    with pytest.raises(budget.BudgetError):
        budget.parse_budget("30%")


@pytest.mark.parametrize("text", ["lots", "$abc", ""])
def test_garbage_fails(text):
    with pytest.raises(budget.BudgetError):
        budget.parse_budget(text)


def test_detect_account():
    assert budget.detect_account({"ANTHROPIC_API_KEY": "x"}) == "enterprise"
    assert budget.detect_account({"CLAUDE_CODE_USE_BEDROCK": "1"}) == "enterprise"
    assert budget.detect_account({}) == "subscription"


def test_resolve_defaults():
    assert budget.resolve_budget("", "enterprise", {"default_usd": 3}) == {"unit": "usd", "amount": 3.0}
    got = budget.resolve_budget("", "subscription", {"plan_ceiling_tokens": 4_000_000})
    assert got == {"unit": "tokens", "amount": 1_000_000}


def test_resolve_explicit_wins():
    assert budget.resolve_budget("10k", "enterprise", {}) == {"unit": "tokens", "amount": 10_000}


def test_usd_budget_on_subscription_is_flagged():
    assert budget.mismatch({"unit": "usd", "amount": 5.0}, "subscription")
    assert not budget.mismatch({"unit": "tokens", "amount": 5}, "subscription")


def test_default_budget_without_ceiling_falls_back_to_two_million_tokens():
    assert budget.resolve_budget("", "subscription", {}) == {"unit": "tokens", "amount": 2_000_000}
