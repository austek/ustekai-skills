from __future__ import annotations

SEVERITY_ORDER = {"blocker": 0, "high": 1, "medium": 2, "low": 3}
PRIORITY = {
    "blocker": "[P0 - Blocker]",
    "high": "[P1 - High]",
    "medium": "[P2 - Medium]",
    "low": "[P3 - Low]",
}
METRICS = (
    "Test Coverage (Line / Branch)",
    "Code Duplication",
    "Bugs / Blocker Issues",
    "Security Vulnerabilities (SAST/Deps)",
    "Linter / Compiler Warnings",
)
STANDARDS_PREFIXES = ("standards/", "arch/")


def status(items: list[dict]) -> str:
    severities = {i["severity"] for i in items}
    if "blocker" in severities:
        return "FAILED"
    return "WARNING" if "high" in severities else "PASSED"


def _ordered(items: list[dict]) -> list[dict]:
    return sorted(items, key=lambda i: (SEVERITY_ORDER[i["severity"]], -i["confidence"], i["file"]))


def _bullets(items: list[dict]) -> str:
    lines = [
        f"- `{i['file']}` ({i['severity']}, conf {i['confidence']:.2f}, effort {i['effort']}): {i['summary']}"
        for i in _ordered(items)
    ]
    return "\n".join(lines) or "- none"


def _matrix(metrics: dict) -> str:
    rows = "\n".join(f"| **{m}** | {metrics.get(m, 'not measured')} |" for m in METRICS)
    return "| Metric | Current Value |\n| :--- | :--- |\n" + rows


def _roadmap(items: list[dict]) -> str:
    lines = [
        f"{n}. `{PRIORITY[i['severity']]}` `{i['file']}`: {i['summary']}"
        for n, i in enumerate(_ordered(items), 1)
    ]
    return "\n".join(lines) or "1. nothing to remediate"


def _usage(spent: float, budget: dict) -> str:
    if budget["unit"] == "usd":
        return f"${spent:,.2f} / ${budget['amount']:,.2f}"
    return f"{spent:,.0f} / {budget['amount']:,.0f} tokens"


def _summary(items: list[dict], budget: dict, spent: float) -> str:
    return (
        f"- **Overall Status**: `{status(items)}`\n"
        f"- **Findings**: {len(items)}\n"
        f"- **Budget used**: {_usage(spent, budget)}"
    )


def render(items: list[dict], budget: dict, spent: float, metrics: dict) -> str:
    standards = [i for i in items if i["rule"].startswith(STANDARDS_PREFIXES)]
    others = [i for i in items if i not in standards]
    summary = _summary(items, budget, spent)
    return "\n\n".join(
        [
            "# Repository Health & Quality Audit Report",
            "## 1. Executive Summary & Quality Gate\n\n" + summary,
            "## 2. Quantitative Metrics Matrix\n\n" + _matrix(metrics),
            "## 3. Custom Standards & Architectural Compliance\n\n" + _bullets(standards),
            "## 4. Correctness, Robustness & Edge-Case Findings\n\n" + _bullets(others),
            "## 5. Prioritized Remediation Roadmap\n\n" + _roadmap(items),
        ]
    )
