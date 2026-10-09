from auditlib import report

BUDGET = {"unit": "tokens", "amount": 100}


def f(sev="high", rule="correctness/x", file="a.js", conf=0.9):
    return {
        "severity": sev,
        "rule": rule,
        "file": file,
        "confidence": conf,
        "effort": "S",
        "summary": "s",
        "fixable": True,
        "anchor": "x",
    }


def test_status_levels():
    assert report.status([f("blocker")]) == "FAILED"
    assert report.status([f("high")]) == "WARNING"
    assert report.status([f("low")]) == "PASSED"
    assert report.status([]) == "PASSED"


def test_roadmap_has_priorities_in_order():
    md = report.render([f("low"), f("blocker")], BUDGET, 40, {})
    assert md.index("[P0 - Blocker]") < md.index("[P3 - Low]")


def test_unmeasured_metrics_are_labelled():
    assert "not measured" in report.render([], BUDGET, 0, {})


def test_metrics_values_appear():
    md = report.render([], BUDGET, 0, {"Code Duplication": "3.1%"})
    assert "3.1%" in md


def test_empty_findings_still_render_all_sections():
    md = report.render([], BUDGET, 0, {})
    for n in range(1, 6):
        assert f"## {n}." in md


def test_standards_findings_go_to_section_three():
    md = report.render([f(rule="standards/naming", file="std.js")], BUDGET, 0, {})
    section3 = md.split("## 3.")[1].split("## 4.")[0]
    assert "std.js" in section3


def test_budget_usage_is_reported():
    assert "40 / 100 tokens" in report.render([], BUDGET, 40, {})


def test_budget_amounts_are_human_readable():
    md = report.render([], {"unit": "tokens", "amount": 2_000_000}, 1500, {})
    assert "1,500 / 2,000,000 tokens" in md
    usd = report.render([], {"unit": "usd", "amount": 5.0}, 1.25, {})
    assert "$1.25 / $5.00" in usd
