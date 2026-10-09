import json

from auditlib import deps

NPM = json.dumps(
    {
        "vulnerabilities": {
            "lodash": {"name": "lodash", "severity": "high", "range": "<4.17.21", "fixAvailable": True},
            "minimist": {"name": "minimist", "severity": "moderate", "range": "<1.2.6", "fixAvailable": False},
        }
    }
)
PIP = json.dumps(
    {
        "dependencies": [
            {"name": "django", "version": "3.0", "vulns": [{"id": "PYSEC-1", "fix_versions": ["3.2"]}]},
            {"name": "ok", "version": "1.0", "vulns": []},
        ]
    }
)
CARGO = json.dumps(
    {
        "vulnerabilities": {
            "list": [
                {
                    "advisory": {"id": "RUSTSEC-2020-0001", "title": "bad"},
                    "package": {"name": "x", "version": "1.0"},
                }
            ]
        }
    }
)


def test_parse_npm_maps_severity_and_fixability():
    got = {f["anchor"]: f for f in deps.parse_npm_audit(NPM)}
    assert got["lodash"]["severity"] == "high" and got["lodash"]["fixable"] is True
    assert got["lodash"]["effort"] == "S" and got["lodash"]["file"] == "package.json"
    assert got["minimist"]["severity"] == "medium" and got["minimist"]["effort"] == "M"


def test_parse_pip_skips_clean_packages():
    got = deps.parse_pip_audit(PIP)
    assert [f["anchor"] for f in got] == ["django:PYSEC-1"]


def test_parse_cargo():
    got = deps.parse_cargo_audit(CARGO)
    assert got[0]["file"] == "Cargo.toml" and got[0]["anchor"] == "x:RUSTSEC-2020-0001"


def test_missing_tool_is_skipped(tmp_path):
    def runner(cmd, **kw):
        raise FileNotFoundError(cmd[0])

    assert deps.run_deps(["node"], tmp_path, runner) == ([], ["node"])


def test_nonzero_exit_still_parses_stdout(tmp_path):
    class Result:
        stdout = NPM
        returncode = 1

    found, skipped = deps.run_deps(["node"], tmp_path, lambda cmd, **kw: Result())
    assert len(found) == 2 and skipped == []


def test_unparseable_output_is_skipped(tmp_path):
    class Result:
        stdout = "not json"
        returncode = 0

    assert deps.run_deps(["python"], tmp_path, lambda cmd, **kw: Result()) == ([], ["python"])


def test_unsupported_stack_is_skipped(tmp_path):
    assert deps.run_deps(["c"], tmp_path, lambda cmd, **kw: None) == ([], ["c"])


def test_pip_audit_targets_requirements_file_when_present(tmp_path):
    (tmp_path / "requirements.txt").write_text("django\n")
    assert deps.command_for("python", tmp_path) == ["pip-audit", "-r", "requirements.txt", "--format", "json"]


def test_pip_audit_targets_project_dir_otherwise(tmp_path):
    assert deps.command_for("python", tmp_path) == ["pip-audit", ".", "--format", "json"]
