import pytest

from auditlib import cron


def test_entry_is_read_only_report_and_resumes():
    e = cron.build_entry("0 3 * * *", "/repo", "2M")
    assert "--act report" in e and "--resume" in e and "--budget 2M" in e
    assert e.endswith("# audit:/repo")


def test_entry_quotes_repo_with_spaces():
    e = cron.build_entry("0 3 * * *", "/my repo", "2M")
    assert "cd '/my repo'" in e


@pytest.mark.parametrize("bad", ["every day", "* * * *", "* * * * * *", ""])
def test_rejects_bad_schedule(bad):
    with pytest.raises(cron.CronError):
        cron.build_entry(bad, "/repo", "2M")


@pytest.mark.parametrize("act", ["fix", "pr"])
def test_rejects_mutating_acts(act):
    with pytest.raises(cron.CronError):
        cron.build_entry("0 3 * * *", "/repo", "2M", act=act)


def test_issues_act_never_carries_confirm():
    e = cron.build_entry("0 3 * * *", "/repo", "2M", act="issues")
    assert "--act issues" in e and "--confirm" not in e


def test_merge_is_idempotent_and_replaces_same_repo():
    first = cron.merge("", cron.build_entry("0 3 * * *", "/repo", "2M"), "/repo")
    second = cron.merge(first, cron.build_entry("0 4 * * *", "/repo", "1M"), "/repo")
    assert second.count("# audit:/repo") == 1 and "0 4 * * *" in second


def test_merge_preserves_other_lines():
    existing = "MAILTO=me\n30 1 * * * backup.sh\n"
    merged = cron.merge(existing, cron.build_entry("0 3 * * *", "/repo", "2M"), "/repo")
    assert "MAILTO=me" in merged and "backup.sh" in merged


def test_percent_budget_is_escaped_for_crontab():
    e = cron.build_entry("0 3 * * *", "/repo", "30%")
    assert "30\\%" in e and "30%" not in e.replace("30\\%", "")


def test_allowed_tools_never_include_bare_bash():
    assert "Bash" not in cron.DEFAULT_TOOLS
    assert any(t.startswith("Bash(") for t in cron.DEFAULT_TOOLS)


def test_entry_starts_a_new_window_each_run():
    assert "--new-window" in cron.build_entry("0 3 * * *", "/repo", "2M")


def test_merge_finds_entries_with_escaped_percent_in_repo_path():
    entry = cron.build_entry("0 3 * * *", "/r%epo", "2M")
    twice = cron.merge(cron.merge("", entry, "/r%epo"), entry, "/r%epo")
    assert twice.count("# audit:") == 1
