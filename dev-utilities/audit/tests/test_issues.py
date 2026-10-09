import json

import pytest

from auditlib import issues


def f(file, fp="abc", sev="high"):
    return {
        "file": file,
        "severity": sev,
        "fingerprint": fp,
        "summary": "s",
        "rule": "r",
        "confidence": 0.9,
        "effort": "S",
        "fixable": True,
        "anchor": "x",
    }


class Result:
    def __init__(self, stdout="", returncode=0, stderr=""):
        self.stdout, self.returncode, self.stderr = stdout, returncode, stderr


class Fake:
    def __init__(self, listing="[]", rc=0):
        self.calls, self.listing, self.rc = [], listing, rc

    def __call__(self, cmd, **kw):
        self.calls.append(cmd)
        if cmd[1:3] == ["issue", "list"]:
            return Result(self.listing, self.rc, "not logged in" if self.rc else "")
        return Result("", 0)


def test_group_one_issue_per_shard():
    groups = issues.group([f("src/a.js"), f("src/b.js", fp="d"), f("lib/c.js", fp="e")])
    assert sorted(groups) == ["lib", "src"]


def test_render_embeds_markers_label_and_acceptance_criteria():
    r = issues.render("src", [f("src/a.js", fp="abc")])
    assert "<!-- audit-fp:abc -->" in r["body"]
    assert r["label"] == issues.unit_label("src") and r["label"].startswith("audit-fp:")
    assert "Given `src` is re-audited" in r["body"]


def test_unit_label_is_stable_and_distinct():
    assert issues.unit_label("src") == issues.unit_label("src")
    assert issues.unit_label("src") != issues.unit_label("lib")


def marker(fp):
    return f"<!-- audit-fp:{fp} -->"


def test_decide_create_when_none():
    assert issues.decide([], {"a"}) == "create"


def test_decide_skip_when_open_issue_covers_all():
    assert issues.decide([{"state": "OPEN", "body": marker("a")}], {"a"}) == "skip"


def test_decide_update_when_open_issue_misses_new_fingerprints():
    assert issues.decide([{"state": "OPEN", "body": marker("a")}], {"a", "b"}) == "update"


def test_decide_regression_when_closed_issue_had_the_fingerprint():
    assert issues.decide([{"state": "CLOSED", "body": marker("a")}], {"a"}) == "regression"


def test_decide_create_when_closed_issue_has_other_fingerprints():
    assert issues.decide([{"state": "CLOSED", "body": marker("z")}], {"a"}) == "create"


def test_detect_tracker():
    assert issues.detect_tracker("git@github.com:collibra/dgc.git") == "jira"
    assert issues.detect_tracker("https://github.com/austek/x.git") == "github"


def test_plan_actions_is_read_only_and_capped():
    run = Fake()
    groups = {"a": [f("a/x.js", "1")], "b": [f("b/y.js", "2")], "c": [f("c/z.js", "3")]}
    acts = issues.plan_actions(groups, issues.GitHub(run), max_issues=2)
    assert [a["unit"] for a in acts] == ["a", "b"]
    assert all(a["action"] == "create" for a in acts)
    assert not any(c[1:3] == ["issue", "create"] for c in run.calls)


def test_apply_creates_with_label_and_regression_prefix():
    run = Fake(listing=json.dumps([{"number": 7, "state": "CLOSED", "body": marker("abc")}]))
    gh = issues.GitHub(run)
    issues.apply_actions(issues.plan_actions({"src": [f("src/a.js")]}, gh, 5), gh)
    create = next(c for c in run.calls if c[1:3] == ["issue", "create"])
    assert create[create.index("--title") + 1].startswith("Regression: ")
    assert issues.unit_label("src") in create


def test_unauthenticated_tracker_raises_before_any_write():
    run = Fake(rc=1)
    with pytest.raises(issues.TrackerError):
        issues.plan_actions({"src": [f("src/a.js")]}, issues.GitHub(run), 5)
    assert not any(c[1:3] == ["issue", "create"] for c in run.calls)


def test_missing_gh_binary_raises_tracker_error():
    def runner(cmd, **kw):
        raise FileNotFoundError("gh")

    with pytest.raises(issues.TrackerError):
        issues.GitHub(runner).search("audit-fp:x")


class PerLabel:
    def __init__(self, by_label):
        self.calls, self.by_label = [], by_label

    def __call__(self, cmd, **kw):
        self.calls.append(cmd)
        if cmd[1:3] == ["issue", "list"]:
            label = cmd[cmd.index("--label") + 1]
            return Result(json.dumps(self.by_label.get(label, [])), 0)
        return Result("", 0)


def test_update_edits_the_body_instead_of_commenting():
    label = issues.unit_label("src")
    run = PerLabel({label: [{"number": 4, "state": "OPEN", "body": marker("a")}]})
    gh = issues.GitHub(run)
    acts = issues.plan_actions({"src": [f("src/a.js", "a"), f("src/b.js", "b")]}, gh, 5)
    issues.apply_actions(acts, gh)
    edits = [c for c in run.calls if c[1:3] == ["issue", "edit"]]
    assert len(edits) == 1 and edits[0][3] == "4"
    assert not any(c[1:3] == ["issue", "comment"] for c in run.calls)


def test_max_issues_counts_only_actionable_issues():
    label_a = issues.unit_label("a")
    run = PerLabel({label_a: [{"number": 1, "state": "OPEN", "body": marker("1")}]})
    groups = {"a": [f("a/x.js", "1")], "b": [f("b/y.js", "2")], "c": [f("c/z.js", "3")]}
    acts = issues.plan_actions(groups, issues.GitHub(run), max_issues=1)
    assert [a["unit"] for a in acts if a["action"] != "skip"] == ["b"]


def test_group_uses_plan_unit_owner_when_given():
    groups = issues.group([f("a/x.js"), f("b/y.js", "z")], owner={"a/x.js": ".", "b/y.js": "."})
    assert list(groups) == ["."]
