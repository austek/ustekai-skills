from __future__ import annotations

import json
import os

import pytest
from ctxlib.overhead import OverheadItem, frontmatter_chars, rank_overhead


def write_settings(claude_dir, plugins):
    claude_dir.mkdir(parents=True, exist_ok=True)
    (claude_dir / "settings.json").write_text(json.dumps({"enabledPlugins": plugins}))


def add_skill(claude_dir, marketplace, plugin, name, description, version="1.0.0"):
    skill_dir = claude_dir / "plugins" / "cache" / marketplace / plugin / version / name
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        f"---\nname: {name}\ndescription: {description}\n---\nbody text ignored\n"
    )


def test_plugin_tokens_estimate_from_skill_frontmatter_chars(tmp_path):
    write_settings(tmp_path, {"p@m": True})
    add_skill(tmp_path, "m", "p", "abcd", "x" * 13)
    items = rank_overhead(tmp_path)
    assert items == [OverheadItem("p@m", "plugin", 5)]


def write_md(tmp_path, body):
    path = tmp_path / "x.md"
    path.write_text(body)
    return path


def test_literal_block_scalar_counts_indented_lines(tmp_path):
    path = write_md(tmp_path, "---\nname: ab\ndescription: |\n  hello\n  world!\n---\nbody\n")
    assert frontmatter_chars(path) == 2 + 5 + 6


def test_folded_block_scalar_counts_indented_lines(tmp_path):
    path = write_md(tmp_path, "---\nname: ab\ndescription: >-\n  hello\n  world!\n---\n")
    assert frontmatter_chars(path) == 2 + 5 + 6


def test_single_line_value_unchanged(tmp_path):
    path = write_md(tmp_path, "---\nname: ab\ndescription: hello\nother: zzzz\n---\n")
    assert frontmatter_chars(path) == 7


def test_block_scalar_ends_where_indentation_ends(tmp_path):
    path = write_md(tmp_path, "---\ndescription: |\n  hello\n\n  there\nother: zzzz\n  nope\n---\n")
    assert frontmatter_chars(path) == 5 + 5


def test_command_and_agent_frontmatter_counts(tmp_path):
    write_settings(tmp_path, {"p@m": True})
    root = tmp_path / "plugins" / "cache" / "m" / "p" / "1.0.0"
    (root / "commands").mkdir(parents=True)
    (root / "agents").mkdir()
    (root / "commands" / "c.md").write_text("---\nname: cc\ndescription: dddd\n---\n")
    (root / "agents" / "a.md").write_text("---\nname: aa\ndescription: bbbb\n---\n")
    assert rank_overhead(tmp_path)[0].tokens == 3


def test_disabled_plugin_is_excluded(tmp_path):
    write_settings(tmp_path, {"p@m": False})
    add_skill(tmp_path, "m", "p", "abcd", "x" * 12)
    assert rank_overhead(tmp_path) == []


def test_missing_cache_dir_gives_empty_list(tmp_path):
    write_settings(tmp_path, {"p@m": True})
    assert rank_overhead(tmp_path) == []


def test_missing_settings_gives_empty_list(tmp_path):
    assert rank_overhead(tmp_path) == []


def test_ranking_is_descending(tmp_path):
    write_settings(tmp_path, {"small@m": True, "big@m": True})
    add_skill(tmp_path, "m", "small", "s", "d")
    add_skill(tmp_path, "m", "big", "b" * 40, "d" * 40)
    names = [i.name for i in rank_overhead(tmp_path)]
    assert names == ["big@m", "small@m"]


def test_mcp_servers_listed_with_zero_tokens(tmp_path):
    write_settings(tmp_path, {})
    (tmp_path / ".claude.json").write_text(json.dumps({"mcpServers": {"idea": {"env": {"K": "v"}}}}))
    assert rank_overhead(tmp_path) == [OverheadItem("idea", "mcp", 0)]


def test_parent_claude_json_is_used_only_for_a_dot_claude_dir(tmp_path):
    (tmp_path / ".claude.json").write_text(json.dumps({"mcpServers": {"home": {}}}))
    for name, expected in ((".claude", ["home"]), ("custom", [])):
        directory = tmp_path / name
        directory.mkdir()
        write_settings(directory, {})
        assert [i.name for i in rank_overhead(directory)] == expected


def test_ties_sort_by_name(tmp_path):
    write_settings(tmp_path, {"b@m": True, "a@m": True})
    add_skill(tmp_path, "m", "b", "s", "d")
    add_skill(tmp_path, "m", "a", "s", "d")
    (tmp_path / ".claude.json").write_text(json.dumps({"mcpServers": {"z": {}, "c": {}}}))
    names = [i.name for i in rank_overhead(tmp_path)]
    assert names == ["a@m", "b@m", "c", "z"]


def two_versions(tmp_path):
    write_settings(tmp_path, {"p@m": True})
    add_skill(tmp_path, "m", "p", "abcd", "x" * 13, version="1.0.0")
    add_skill(tmp_path, "m", "p", "abcd", "x" * 33, version="2.0.0")
    base = tmp_path / "plugins" / "cache" / "m" / "p"
    os.utime(base / "1.0.0", (100, 100))
    os.utime(base / "2.0.0", (200, 200))
    return base


def write_installed(tmp_path, content):
    (tmp_path / "plugins" / "installed_plugins.json").write_text(content)


def test_installed_plugins_install_path_wins_over_newest_mtime(tmp_path):
    base = two_versions(tmp_path)
    install = {"plugins": {"p@m": [{"installPath": str(base / "1.0.0")}]}}
    write_installed(tmp_path, json.dumps(install))
    assert rank_overhead(tmp_path) == [OverheadItem("p@m", "plugin", 5)]


@pytest.mark.parametrize(
    "content",
    [
        None,
        "{not json",
        "[]",
        json.dumps({"plugins": {}}),
        json.dumps({"plugins": {"p@m": []}}),
        json.dumps({"plugins": {"p@m": [{}]}}),
        json.dumps({"plugins": {"p@m": [{"installPath": 7}]}}),
        json.dumps({"plugins": {"p@m": [{"installPath": "/does/not/exist"}]}}),
    ],
)
def test_falls_back_to_newest_version_directory(tmp_path, content):
    two_versions(tmp_path)
    if content is not None:
        write_installed(tmp_path, content)
    assert rank_overhead(tmp_path) == [OverheadItem("p@m", "plugin", 10)]


def test_install_path_outside_the_cache_is_honoured(tmp_path):
    two_versions(tmp_path)
    elsewhere = tmp_path / "elsewhere"
    (elsewhere / "skills" / "s").mkdir(parents=True)
    (elsewhere / "skills" / "s" / "SKILL.md").write_text("---\nname: s\ndescription: abcd\n---\n")
    write_installed(tmp_path, json.dumps({"plugins": {"p@m": [{"installPath": str(elsewhere)}]}}))
    assert rank_overhead(tmp_path) == [OverheadItem("p@m", "plugin", 2)]


def test_malformed_files_give_empty_list(tmp_path):
    tmp_path.joinpath("settings.json").write_text("{not json")
    tmp_path.joinpath(".claude.json").write_text("[")
    assert rank_overhead(tmp_path) == []
