from __future__ import annotations

import re
from collections.abc import Mapping

_SUFFIX = {"k": 1_000, "m": 1_000_000, "": 1}
_ENTERPRISE_ENV = (
    "ANTHROPIC_API_KEY",
    "ANTHROPIC_AUTH_TOKEN",
    "CLAUDE_CODE_USE_BEDROCK",
    "CLAUDE_CODE_USE_VERTEX",
)
DEFAULT_PERCENT = "25%"
DEFAULT_TOKENS = 2_000_000
DEFAULT_USD = 5.0


class BudgetError(ValueError):
    pass


def detect_account(env: Mapping) -> str:
    return "enterprise" if any(env.get(k) for k in _ENTERPRISE_ENV) else "subscription"


def _usd(rest: str) -> dict:
    try:
        return {"unit": "usd", "amount": float(rest)}
    except ValueError as e:
        raise BudgetError(f"unparseable usd budget: ${rest}") from e


def _percent(number: str, ceiling: int | None) -> dict:
    if not ceiling:
        raise BudgetError("percent budgets need plan_ceiling_tokens in ~/.config/audit/config.json")
    return {"unit": "tokens", "amount": int(ceiling * float(number) / 100)}


def parse_budget(text: str, ceiling: int | None = None) -> dict:
    t = text.strip().lower()
    if t.startswith("$"):
        return _usd(t[1:])
    if t.endswith("%"):
        return _percent(t[:-1], ceiling)
    m = re.fullmatch(r"(\d+(?:\.\d+)?)([km]?)", t)
    if not m:
        raise BudgetError(f"unparseable budget: {text!r}")
    return {"unit": "tokens", "amount": int(float(m[1]) * _SUFFIX[m[2]])}


def resolve_budget(arg: str, account: str, config: dict) -> dict:
    if arg:
        return parse_budget(arg, config.get("plan_ceiling_tokens"))
    if account == "enterprise":
        return {"unit": "usd", "amount": float(config.get("default_usd", DEFAULT_USD))}
    ceiling = config.get("plan_ceiling_tokens")
    if not ceiling:
        return {"unit": "tokens", "amount": DEFAULT_TOKENS}
    return parse_budget(DEFAULT_PERCENT, ceiling)


def mismatch(resolved: dict, account: str) -> bool:
    return resolved["unit"] == "usd" and account == "subscription"
