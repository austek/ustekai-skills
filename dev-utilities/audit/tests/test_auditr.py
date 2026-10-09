import json

import pytest

from auditlib import auditr


def report(findings, file="src/a.py"):
    return json.dumps({"files": [{"file": file, "findings": findings}, {"file": "src/clean.py", "findings": []}], "totals": {}})


def finding(**over):
    base = {
        "rule_id": "PY-X",
        "severity": "blocking",
        "verdict_kind": "auto",
        "line": 3,
        "message": "bad call",
        "evidence": "  eval(x)  ",
        "suggestion": "use ast.literal_eval",
    }
    return {**base, **over}


def test_severity_and_confidence_mapping():
    got = auditr.parse_report(
        report(
            [
                finding(),
                finding(rule_id="PY-Y", severity="suggestion", verdict_kind="candidate", suggestion=None),
            ]
        )
    )
    assert [(f["severity"], f["confidence"], f["fixable"]) for f in got] == [
        ("blocker", 0.9, True),
        ("low", 0.4, False),
    ]


def test_rule_is_namespaced_and_clean_files_yield_nothing():
    got = auditr.parse_report(report([finding()]))
    assert [f["rule"] for f in got] == ["auditr/PY-X"]
    assert all(f["file"] == "src/a.py" for f in got)


def test_anchor_ignores_line_number_and_whitespace():
    a = auditr.parse_report(report([finding(line=3, evidence="eval(x)")]))[0]["anchor"]
    b = auditr.parse_report(report([finding(line=40, evidence="  eval(x) ")]))[0]["anchor"]
    assert a == b


def test_anchor_falls_back_to_message_when_no_evidence():
    got = auditr.parse_report(report([finding(evidence="")]))
    assert got[0]["anchor"] == "bad call"


def test_unknown_severity_degrades_to_low():
    got = auditr.parse_report(report([finding(severity="weird")]))
    assert got[0]["severity"] == "low"


def test_missing_binary_raises_unavailable(tmp_path):
    def runner(cmd, **kw):
        raise FileNotFoundError("auditr")

    with pytest.raises(auditr.AuditrUnavailable):
        auditr.scan(tmp_path, runner)


def test_unparseable_output_raises_unavailable(tmp_path):
    class Result:
        stdout = "oops"
        returncode = 2

    with pytest.raises(auditr.AuditrUnavailable):
        auditr.scan(tmp_path, lambda cmd, **kw: Result())


def test_nonzero_exit_with_valid_report_is_accepted(tmp_path):
    class Result:
        stdout = report([finding()])
        returncode = 1

    assert len(auditr.scan(tmp_path, lambda cmd, **kw: Result())) == 1


def test_absolute_paths_are_made_relative_to_root():
    text = report([finding()], file="/r/src/a.py")
    assert auditr.parse_report(text, "/r")[0]["file"] == "src/a.py"


def test_split_judged_separates_auto_from_candidates():
    items = auditr.parse_report(report([finding(), finding(rule_id="B", verdict_kind="candidate")]))
    auto, candidates = auditr.split_judged(items)
    assert [i["rule"] for i in auto] == ["auditr/PY-X"]
    assert [i["rule"] for i in candidates] == ["auditr/B"]
