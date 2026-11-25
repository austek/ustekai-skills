import importlib.util
import json
import os
import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "babysit_sweep.py"
NOW = 1_800_000_000_000


def _load():
    spec = importlib.util.spec_from_file_location("babysit_sweep", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


sweep_mod = _load()


def _entry(**over):
    return {
        "v": 1, "repo": "austek/dotfiles", "pr": 180, "state": "BLOCKED", "cycle": 0, "cycles": 1,
        "head": "45dd125", "pass": 2, "fail": 0, "pending": 5, "openThreads": 1,
        "nextReviewAt": NOW + 1000, "next": "approve the reply", "watchId": "w1", "updatedAt": NOW - 5_000_000,
        **over,
    }


def _write(directory, name, entry):
    path = directory / name
    path.write_text(json.dumps(entry))
    path.chmod(0o600)
    return path


def _read(path):
    return json.loads(path.read_text())


def test_parse_state_accepts_a_version_1_entry_and_rejects_the_rest():
    assert sweep_mod.parse_state(json.dumps(_entry()))["pr"] == 180
    bad = [
        "not json", "[]", "null", json.dumps(_entry(v=2)), json.dumps(_entry(state="DONE")),
        json.dumps(_entry(pr=0)), json.dumps(_entry(pr="1")), json.dumps(_entry(repo="")),
        json.dumps(_entry(repo="--evil/x")), json.dumps(_entry(repo="a/b/c")),
        json.dumps(_entry(state=[])), json.dumps(_entry(state={})), json.dumps(_entry(state=None)),
    ]
    assert [sweep_mod.parse_state(text) for text in bad] == [None] * len(bad)


def test_closed_entry_keeps_the_counts_and_drops_the_wake_up_fields():
    closed = sweep_mod.closed_entry(_entry(), NOW)
    assert (closed["state"], closed["updatedAt"]) == ("CLOSED", NOW)
    assert (closed["repo"], closed["pr"], closed["head"], closed["pass"], closed["pending"]) == (
        "austek/dotfiles", 180, "45dd125", 2, 5,
    )
    assert not {"next", "nextReviewAt", "watchId"} & closed.keys()


def test_sweep_marks_merged_and_closed_prs_closed(tmp_path):
    merged = _write(tmp_path, "austek__dotfiles__180.json", _entry())
    closed = _write(tmp_path, "austek__dotfiles__181.json", _entry(pr=181))
    answers = {180: "MERGED", 181: "CLOSED"}
    done = sweep_mod.sweep(tmp_path, lambda repo, pr: answers[pr], NOW)
    assert sorted(done.closed) == ["austek__dotfiles__180.json", "austek__dotfiles__181.json"]
    assert done.deleted == []
    assert _read(merged)["state"] == "CLOSED" and _read(closed)["state"] == "CLOSED"


def test_sweep_leaves_open_prs_and_failed_lookups_alone(tmp_path):
    first = _write(tmp_path, "austek__dotfiles__1.json", _entry(pr=1))
    second = _write(tmp_path, "austek__dotfiles__2.json", _entry(pr=2))
    answers = {1: "OPEN", 2: None}
    assert sweep_mod.sweep(tmp_path, lambda repo, pr: answers[pr], NOW) == ([], [])
    assert _read(first) == _entry(pr=1) and _read(second) == _entry(pr=2)


def test_sweep_does_not_look_up_a_file_that_is_already_closed(tmp_path):
    _write(tmp_path, "austek__dotfiles__180.json", _entry(state="CLOSED"))
    calls = []
    sweep_mod.sweep(tmp_path, lambda repo, pr: calls.append(pr), NOW)
    assert calls == []


def test_sweep_skips_symlinks_other_files_and_malformed_json(tmp_path):
    target = tmp_path / "elsewhere.txt"
    target.write_text(json.dumps(_entry()))
    (tmp_path / "link.json").symlink_to(target)
    (tmp_path / "notes.txt").write_text(json.dumps(_entry()))
    (tmp_path / "broken.json").write_text("{")
    calls = []
    sweep_mod.sweep(tmp_path, lambda repo, pr: calls.append(pr) or "MERGED", NOW)
    assert calls == []
    assert _read(target)["state"] == "BLOCKED"


def test_sweep_does_not_overwrite_a_file_a_live_writer_changed_during_the_lookup(tmp_path):
    path = _write(tmp_path, "austek__dotfiles__180.json", _entry())
    newer = _entry(state="WAITING", updatedAt=NOW - 10)

    def lookup(repo, pr):
        path.write_text(json.dumps(newer))
        return "MERGED"

    assert sweep_mod.sweep(tmp_path, lookup, NOW).closed == []
    assert _read(path) == newer


def test_sweep_keeps_the_file_mode_and_leaves_no_temp_files(tmp_path):
    path = _write(tmp_path, "austek__dotfiles__180.json", _entry())
    sweep_mod.sweep(tmp_path, lambda repo, pr: "MERGED", NOW)
    assert path.stat().st_mode & 0o777 == 0o600
    assert [p.name for p in tmp_path.iterdir()] == ["austek__dotfiles__180.json"]


def test_sweep_looks_at_no_more_than_the_limit(tmp_path):
    for number in range(1, 6):
        _write(tmp_path, f"austek__dotfiles__{number}.json", _entry(pr=number))
    calls = []
    sweep_mod.sweep(tmp_path, lambda repo, pr: calls.append(pr) or "OPEN", NOW, limit=3)
    assert len(calls) == 3


def _aged(path, entry, ms_ago):
    """A CLOSED file whose `updatedAt` and mtime both read `ms_ago` before NOW."""
    path.write_text(json.dumps({**entry, "state": "CLOSED", "updatedAt": NOW - ms_ago}))
    seconds = (NOW - ms_ago) / 1000
    os.utime(path, (seconds, seconds))
    return path


def test_sweep_deletes_a_closed_file_older_than_the_retention_without_asking_github(tmp_path):
    old = _aged(tmp_path / "austek__dotfiles__1.json", _entry(pr=1), sweep_mod.RETENTION_MS + 1000)
    calls = []
    done = sweep_mod.sweep(tmp_path, lambda repo, pr: calls.append(pr), NOW)
    assert done.deleted == ["austek__dotfiles__1.json"]
    assert not old.exists() and calls == []


@pytest.mark.parametrize(("value", "expected_hours"), [("48", 48), ("0.5", 0.5), (" 6 ", 6)])
def test_retention_reads_hours_from_babysit_purge_hours(value, expected_hours):
    assert sweep_mod.retention_ms({"BABYSIT_PURGE_HOURS": value}) == expected_hours * 3_600_000


@pytest.mark.parametrize("value", [None, "", "abc", "0", "-3", "nan", "inf", "1e999"])
def test_retention_falls_back_to_24_hours_for_a_missing_or_unusable_value(value):
    env = {} if value is None else {"BABYSIT_PURGE_HOURS": value}
    assert sweep_mod.retention_ms(env) == sweep_mod.RETENTION_MS == 24 * 3_600_000


def test_sweep_uses_the_retention_it_is_given(tmp_path):
    two_hours = 2 * 3_600_000
    path = _aged(tmp_path / "austek__dotfiles__1.json", _entry(pr=1), two_hours)
    assert sweep_mod.sweep(tmp_path, lambda repo, pr: None, NOW).deleted == []
    assert sweep_mod.sweep(tmp_path, lambda repo, pr: None, NOW, retention_ms=3_600_000).deleted == [path.name]


def test_sweep_keeps_a_closed_file_inside_the_retention(tmp_path):
    fresh = _aged(tmp_path / "austek__dotfiles__1.json", _entry(pr=1), sweep_mod.RETENTION_MS - 1000)
    assert sweep_mod.sweep(tmp_path, lambda repo, pr: None, NOW).deleted == []
    assert fresh.exists()


def test_sweep_keeps_a_closed_file_whose_mtime_is_newer_than_its_updated_at(tmp_path):
    path = _aged(tmp_path / "austek__dotfiles__1.json", _entry(pr=1), sweep_mod.RETENTION_MS + 1000)
    os.utime(path, (NOW / 1000, NOW / 1000))
    assert sweep_mod.sweep(tmp_path, lambda repo, pr: None, NOW).deleted == []
    assert path.exists()


def test_a_file_closed_in_this_run_is_not_deleted_in_it(tmp_path):
    path = _write(tmp_path, "austek__dotfiles__180.json", _entry(updatedAt=NOW - sweep_mod.RETENTION_MS * 3))
    os.utime(path, (NOW / 1000 - 3 * sweep_mod.RETENTION_MS / 1000,) * 2)
    done = sweep_mod.sweep(tmp_path, lambda repo, pr: "MERGED", NOW)
    assert (done.closed, done.deleted) == (["austek__dotfiles__180.json"], [])
    assert path.exists()


def test_sweep_never_deletes_symlinks_other_files_or_unreadable_state(tmp_path):
    target = _aged(tmp_path / "target.txt", _entry(), sweep_mod.RETENTION_MS + 1000)
    (tmp_path / "link.json").symlink_to(target)
    _aged(tmp_path / "notes.txt", _entry(), sweep_mod.RETENTION_MS + 1000)
    (tmp_path / "broken.json").write_text("{")
    assert sweep_mod.sweep(tmp_path, lambda repo, pr: None, NOW).deleted == []
    assert sorted(p.name for p in tmp_path.iterdir()) == ["broken.json", "link.json", "notes.txt", "target.txt"]


def test_sweep_looks_at_the_most_recently_written_files_first_when_it_must_choose(tmp_path):
    for number, minutes_ago in ((1, 500), (2, 5), (3, 90), (4, 30)):
        stamp = NOW - minutes_ago * 60_000
        path = _write(tmp_path, f"austek__dotfiles__{number}.json", _entry(pr=number, updatedAt=stamp))
        os.utime(path, (stamp / 1000, stamp / 1000))
    calls = []
    sweep_mod.sweep(tmp_path, lambda repo, pr: calls.append(pr) or "OPEN", NOW, limit=2)
    assert calls == [2, 4]


def test_gh_state_runs_gh_with_a_fixed_argument_list_and_a_timeout():
    seen = {}

    def run(argv, **kwargs):
        seen["argv"], seen["kwargs"] = argv, kwargs
        return SimpleNamespace(returncode=0, stdout="MERGED\n")

    assert sweep_mod.gh_state("austek/dotfiles", 180, run=run) == "MERGED"
    assert seen["argv"] == ["gh", "pr", "view", "180", "--repo", "austek/dotfiles", "--json", "state", "--jq", ".state"]
    assert seen["kwargs"]["timeout"] > 0


@pytest.mark.parametrize("outcome", [
    SimpleNamespace(returncode=1, stdout="MERGED"),
    SimpleNamespace(returncode=0, stdout="weird"),
    SimpleNamespace(returncode=0, stdout=""),
    OSError("no gh"),
    subprocess.TimeoutExpired("gh", 1),
])
def test_gh_state_reads_a_failure_or_an_odd_answer_as_unknown(outcome):
    def run(argv, **kwargs):
        if isinstance(outcome, Exception):
            raise outcome
        return outcome

    assert sweep_mod.gh_state("austek/dotfiles", 180, run=run) is None


def test_gh_state_never_runs_gh_for_a_repo_that_could_be_read_as_an_option():
    calls = []
    assert sweep_mod.gh_state("--evil/x", 1, run=lambda *a, **k: calls.append(a)) is None
    assert calls == []


def test_the_session_start_hook_runs_the_sweep_in_the_background_on_start_and_resume():
    hooks = json.loads((SCRIPT.parents[1] / "hooks" / "hooks.json").read_text())
    group = hooks["hooks"]["SessionStart"][0]
    command = group["hooks"][0]["command"]
    assert group["matcher"] == "startup|resume"
    assert '"${CLAUDE_PLUGIN_ROOT}/scripts/babysit_sweep.py"' in command
    assert command.rstrip().endswith("&")
    assert (SCRIPT.parents[1] / "scripts" / "babysit_sweep.py").is_file()


def test_main_exits_zero_when_the_state_directory_is_missing(tmp_path):
    assert sweep_mod.main(home=tmp_path, lookup=lambda repo, pr: "MERGED", now_ms=NOW, env={}) == 0


def test_main_deletes_expired_closed_files_under_home(tmp_path):
    directory = tmp_path / ".cache/babysit-pr"
    directory.mkdir(parents=True)
    old = _aged(directory / "austek__dotfiles__1.json", _entry(pr=1), sweep_mod.RETENTION_MS + 1000)
    assert sweep_mod.main(home=tmp_path, lookup=lambda repo, pr: None, now_ms=NOW, env={}) == 0
    assert not old.exists()


def test_main_takes_the_retention_from_the_environment(tmp_path):
    directory = tmp_path / ".cache/babysit-pr"
    directory.mkdir(parents=True)
    path = _aged(directory / "austek__dotfiles__1.json", _entry(pr=1), 2 * 3_600_000)
    assert sweep_mod.main(home=tmp_path, lookup=lambda r, p: None, now_ms=NOW, env={}) == 0
    assert path.exists()
    assert sweep_mod.main(home=tmp_path, lookup=lambda r, p: None, now_ms=NOW, env={"BABYSIT_PURGE_HOURS": "1"}) == 0
    assert not path.exists()


def test_main_sweeps_the_state_directory_under_home(tmp_path):
    directory = tmp_path / ".cache/babysit-pr"
    directory.mkdir(parents=True)
    path = _write(directory, "austek__dotfiles__180.json", _entry())
    assert sweep_mod.main(home=tmp_path, lookup=lambda repo, pr: "MERGED", now_ms=NOW, env={}) == 0
    assert _read(path)["state"] == "CLOSED"
