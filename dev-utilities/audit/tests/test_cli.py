import json
import subprocess
import sys
from pathlib import Path

AUDIT = Path(__file__).resolve().parents[1] / "scripts" / "audit.py"


def run(root, *args):
    return subprocess.run([sys.executable, str(AUDIT), *args], capture_output=True, text=True, cwd=root)


def populate(root, git):
    for d in ("hot", "cold"):
        (root / d).mkdir()
        (root / d / "a.js").write_text("x" * 1000)
    git("add", ".")
    git("commit", "-qm", "init")


def test_help_lists_every_flag_with_a_hint():
    out = run(".", "plan", "--help").stdout
    for flag in ("--act", "--budget", "--lanes", "--since", "--max-shards", "--with", "--resume", "--exclude"):
        assert flag in out


def test_plan_on_repo_without_commits_exits_zero(repo):
    root, _ = repo
    r = run(root, "plan", "--budget", "1M")
    assert r.returncode == 0
    assert state_units(root) == {}


def state_units(root):
    return json.loads((root / ".audit" / "state.json").read_text())["units"]


def test_plan_ranks_and_hides_audit_dir_from_git(repo):
    root, git = repo
    populate(root, git)
    assert run(root, "plan", "--budget", "1M", "--small-repo-bytes", "1").returncode == 0
    assert set(state_units(root)) == {"hot", "cold"}
    status = subprocess.run(["git", "-C", str(root), "status", "--porcelain"], capture_output=True, text=True)
    assert ".audit" not in status.stdout


def test_next_record_cycle_runs_each_unit_once(repo):
    root, git = repo
    populate(root, git)
    run(root, "plan", "--budget", "1M", "--small-repo-bytes", "1")
    seen = []
    for _ in range(2):
        out = json.loads(run(root, "next").stdout)
        assert out["verdict"] == "run"
        seen.append(out["unit"])
        run(root, "record", "--unit", out["unit"], "--status", "done", "--spent", "100")
    assert sorted(seen) == ["cold", "hot"]
    assert json.loads(run(root, "next").stdout)["verdict"] == "done"


def test_budget_below_smallest_shard_is_exhausted(repo):
    root, git = repo
    populate(root, git)
    run(root, "plan", "--budget", "10", "--small-repo-bytes", "1")
    assert json.loads(run(root, "next").stdout)["verdict"] == "exhausted"


def test_resume_keeps_existing_state(repo):
    root, git = repo
    populate(root, git)
    run(root, "plan", "--budget", "1M", "--small-repo-bytes", "1")
    run(root, "record", "--unit", "hot", "--status", "done", "--spent", "50")
    run(root, "plan", "--budget", "1M", "--small-repo-bytes", "1", "--resume")
    st = json.loads((root / ".audit" / "state.json").read_text())
    assert st["spent"] == 50 and st["units"]["hot"] == "done"


def test_stale_tmp_does_not_break_resume(repo):
    root, git = repo
    populate(root, git)
    run(root, "plan", "--budget", "1M", "--small-repo-bytes", "1")
    (root / ".audit" / "state.json.tmp").write_text("{broken")
    assert json.loads(run(root, "next").stdout)["verdict"] == "run"


def test_unsupported_shard_axis_errors_clearly(repo):
    root, _ = repo
    r = run(root, "plan", "--budget", "1M", "--shard", "journey:login")
    assert r.returncode == 2 and "only --shard dir" in r.stderr


def test_percent_budget_without_ceiling_errors(repo, tmp_path):
    root, _ = repo
    r = subprocess.run(
        [sys.executable, str(AUDIT), "plan", "--budget", "30%"],
        capture_output=True,
        text=True,
        cwd=root,
        env={"HOME": str(tmp_path), "PATH": "/usr/bin:/bin"},
    )
    assert r.returncode == 2 and "plan_ceiling_tokens" in r.stderr


def test_act_writes_drafts_then_fails_when_gh_missing(repo, tmp_path):
    root, git = repo
    populate(root, git)
    run(root, "plan", "--budget", "1M", "--small-repo-bytes", "1")
    finding = [{"rule": "r", "file": "hot/a.js", "anchor": "x", "severity": "high",
                "confidence": 0.9, "effort": "S", "fixable": True, "summary": "s"}]
    src = tmp_path / "f.json"
    src.write_text(json.dumps(finding))
    run(root, "record", "--unit", "hot", "--status", "done", "--spent", "1", "--findings", str(src))
    r = subprocess.run(
        [sys.executable, str(AUDIT), "act", "--tracker", "github"],
        capture_output=True,
        text=True,
        cwd=root,
        env={"HOME": str(tmp_path), "PATH": ""},
    )
    assert r.returncode == 2
    assert (root / ".audit" / "issues.drafts.json").exists()


def test_report_renders_markdown(repo):
    root, git = repo
    populate(root, git)
    run(root, "plan", "--budget", "1M", "--small-repo-bytes", "1")
    assert run(root, "report").returncode == 0
    assert "# Repository Health & Quality Audit Report" in (root / ".audit" / "report.md").read_text()


def test_reset_prints_iso_time():
    r = run(".", "reset", "--message", "resets 3:50am (Europe/London)")
    assert r.returncode == 0 and "T03:50" in r.stdout


def run_env(root, env, *args):
    return subprocess.run([sys.executable, str(AUDIT), *args], capture_output=True, text=True, cwd=root, env=env)


def test_auditr_missing_binary_skips_cleanly(repo, tmp_path):
    root, git = repo
    populate(root, git)
    run(root, "plan", "--budget", "1M", "--small-repo-bytes", "1")
    r = run_env(root, {"HOME": str(tmp_path), "PATH": ""}, "auditr")
    assert r.returncode == 0 and json.loads(r.stdout)["available"] is False


def test_auditr_findings_are_split_per_shard(repo, tmp_path):
    root, git = repo
    populate(root, git)
    run(root, "plan", "--budget", "1M", "--small-repo-bytes", "1")
    payload = {"files": [{"file": "hot/a.js", "findings": [{
        "rule_id": "JS-X", "severity": "high", "verdict_kind": "auto", "line": 1,
        "message": "m", "evidence": "e", "suggestion": None}]}], "totals": {}}
    bindir = tmp_path / "bin"
    bindir.mkdir()
    script = bindir / "auditr"
    script.write_text("#!/bin/sh\ncat <<'EOF'\n" + json.dumps(payload) + "\nEOF\n")
    script.chmod(0o755)
    env = {"HOME": str(tmp_path), "PATH": f"{bindir}:/usr/bin:/bin"}
    r = run_env(root, env, "auditr")
    assert r.returncode == 0 and json.loads(r.stdout)["findings"] == 1
    written = json.loads((root / ".audit" / "findings" / "auditr-hot.json").read_text())
    assert written[0]["rule"] == "auditr/JS-X"
    assert not (root / ".audit" / "findings" / "auditr-cold.json").exists()


def test_binary_files_are_not_planned(repo):
    root, git = repo
    populate(root, git)
    (root / "hot" / "blob.dat").write_bytes(b"\x00\x01\x02" * 400)
    git("add", ".")
    git("commit", "-qm", "blob")
    run(root, "plan", "--budget", "1M", "--small-repo-bytes", "1")
    meta = json.loads((root / ".audit" / "state.json").read_text())["units_meta"]
    assert all("blob.dat" not in f for m in meta.values() for f in m["files"])


def home_env(tmp_path, config=None):
    cfg = tmp_path / ".config" / "audit"
    cfg.mkdir(parents=True, exist_ok=True)
    if config is not None:
        (cfg / "config.json").write_text(json.dumps(config))
    return {"HOME": str(tmp_path), "PATH": "/usr/bin:/bin"}


def test_usd_budget_without_price_is_rejected(repo, tmp_path):
    root, git = repo
    populate(root, git)
    r = run_env(root, home_env(tmp_path), "plan", "--budget", "$5", "--small-repo-bytes", "1")
    assert r.returncode == 2 and "usd_per_mtok" in r.stderr


def test_usd_budget_converts_tokens_with_configured_price(repo, tmp_path):
    root, git = repo
    populate(root, git)
    env = home_env(tmp_path, {"usd_per_mtok": 10})
    assert run_env(root, env, "plan", "--budget", "$5", "--small-repo-bytes", "1").returncode == 0
    assert json.loads(run_env(root, env, "next").stdout)["verdict"] == "run"
    run_env(root, env, "record", "--unit", "hot", "--status", "done", "--spent", "100000")
    st = json.loads((root / ".audit" / "state.json").read_text())
    assert abs(st["spent"] - 1.0) < 1e-9


def test_default_budget_works_on_a_fresh_install(repo, tmp_path):
    root, git = repo
    populate(root, git)
    r = run_env(root, home_env(tmp_path), "plan", "--account", "subscription", "--small-repo-bytes", "1")
    assert r.returncode == 0


def test_failed_shard_counts_spend_but_not_ratio(repo):
    root, git = repo
    populate(root, git)
    run(root, "plan", "--budget", "1M", "--small-repo-bytes", "1")
    run(root, "record", "--unit", "hot", "--status", "failed", "--spent", "700")
    st = json.loads((root / ".audit" / "state.json").read_text())
    assert st["spent"] == 700 and st["ratios"] == []


def test_record_lane_counts_spend_and_clears_pending(repo, tmp_path):
    root, git = repo
    populate(root, git)
    run(root, "plan", "--budget", "1M", "--small-repo-bytes", "1", "--lanes", "deps,docs")
    before = json.loads(run(root, "next").stdout)
    assert before["lanes_pending"] == ["deps", "docs"]
    src = tmp_path / "docs.json"
    src.write_text(json.dumps([{"rule": "docs/x", "file": "README.md", "anchor": "a", "severity": "low",
                                "confidence": 0.8, "effort": "S", "fixable": True, "summary": "s"}]))
    r = run(root, "record-lane", "--lane", "docs", "--spent", "250", "--findings", str(src))
    assert r.returncode == 0
    after = json.loads(run(root, "next").stdout)
    assert after["lanes_pending"] == ["deps"] and after["spent"] == 250
    assert run(root, "report").returncode == 0


def test_record_lane_rejects_lane_not_in_plan(repo):
    root, git = repo
    populate(root, git)
    run(root, "plan", "--budget", "1M", "--small-repo-bytes", "1")
    assert run(root, "record-lane", "--lane", "docs", "--spent", "1").returncode == 2


def test_resume_replans_when_nothing_is_pending(repo):
    root, git = repo
    populate(root, git)
    run(root, "plan", "--budget", "1M", "--small-repo-bytes", "1")
    for unit in ("hot", "cold"):
        run(root, "record", "--unit", unit, "--status", "done", "--spent", "10")
    run(root, "plan", "--budget", "1M", "--small-repo-bytes", "1", "--resume")
    st = json.loads((root / ".audit" / "state.json").read_text())
    assert st["spent"] == 0 and set(st["units"].values()) == {"pending"}


def test_new_window_resets_spend_but_keeps_progress(repo):
    root, git = repo
    populate(root, git)
    run(root, "plan", "--budget", "1M", "--small-repo-bytes", "1")
    run(root, "record", "--unit", "hot", "--status", "done", "--spent", "10")
    run(root, "plan", "--budget", "1M", "--small-repo-bytes", "1", "--resume", "--new-window")
    st = json.loads((root / ".audit" / "state.json").read_text())
    assert st["spent"] == 0 and st["units"]["hot"] == "done" and st["units"]["cold"] == "pending"


def test_errors_exit_two_with_a_message(repo):
    root, git = repo
    populate(root, git)
    assert run(root, "act").returncode == 2
    run(root, "plan", "--budget", "1M", "--small-repo-bytes", "1")
    assert run(root, "record", "--unit", "nope", "--spent", "1").returncode == 2
    bad = run(root, "plan", "--budget", "1M", "--since", "no-such-ref")
    assert bad.returncode == 2 and "audit:" in bad.stderr


def test_auditr_candidates_are_withheld_from_findings(repo, tmp_path):
    root, git = repo
    populate(root, git)
    run(root, "plan", "--budget", "1M", "--small-repo-bytes", "1")
    payload = {"files": [{"file": str(root / "hot/a.js"), "findings": [
        {"rule_id": "A", "severity": "high", "verdict_kind": "auto", "line": 1, "message": "m", "evidence": "e", "suggestion": None},
        {"rule_id": "C", "severity": "high", "verdict_kind": "candidate", "line": 2, "message": "m2", "evidence": "e2", "suggestion": None}]}], "totals": {}}
    bindir = tmp_path / "bin"
    bindir.mkdir()
    script = bindir / "auditr"
    script.write_text("#!/bin/sh\ncat <<'EOF'\n" + json.dumps(payload) + "\nEOF\n")
    script.chmod(0o755)
    env = {"HOME": str(tmp_path), "PATH": f"{bindir}:/usr/bin:/bin"}
    assert run_env(root, env, "auditr").returncode == 0
    kept = json.loads((root / ".audit" / "findings" / "auditr-hot.json").read_text())
    assert [f["rule"] for f in kept] == ["auditr/A"]
    run_env(root, env, "record", "--unit", "cold", "--status", "done", "--spent", "1")
    nxt = json.loads(run_env(root, env, "next").stdout)
    assert nxt["unit"] == "hot"
    assert [c["rule"] for c in nxt["candidates"]] == ["auditr/C"]


def test_audit_dir_is_hidden_from_git_inside_a_worktree(repo, tmp_path):
    root, git = repo
    populate(root, git)
    wt = tmp_path / "wt"
    git("worktree", "add", "-q", str(wt))
    assert run(wt, "plan", "--budget", "1M", "--small-repo-bytes", "1").returncode == 0
    status = subprocess.run(["git", "-C", str(wt), "status", "--porcelain"], capture_output=True, text=True)
    assert ".audit" not in status.stdout


def test_reset_prints_nothing_and_exits_one_for_unknown_wording():
    r = run(".", "reset", "--message", "weekly limit reached, try again next week")
    assert r.returncode == 1 and r.stdout.strip() == ""


def test_plan_excludes_both_audit_and_auditr_dirs_from_git(repo):
    root, git = repo
    populate(root, git)
    run(root, "plan", "--budget", "1M", "--small-repo-bytes", "1")
    (root / ".auditor").mkdir()
    (root / ".auditor" / ".status.json").write_text("{}")
    status = subprocess.run(["git", "-C", str(root), "status", "--porcelain"], capture_output=True, text=True)
    assert ".audit" not in status.stdout
