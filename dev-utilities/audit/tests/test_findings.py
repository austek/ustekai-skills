import json
import pytest

from auditlib import findings


def make(**over):
    base = {
        "rule": "deps/npm-advisory",
        "file": "package.json",
        "anchor": "lodash",
        "severity": "high",
        "confidence": 0.9,
        "effort": "S",
        "fixable": True,
        "summary": "lodash high",
    }
    return {**base, **over}


def test_fingerprint_ignores_path_spelling():
    a = findings.fingerprint("r", "./src/a.js", "fn")
    b = findings.fingerprint("r", "src//a.js", "fn")
    assert a == b


def test_fingerprint_changes_with_anchor():
    assert findings.fingerprint("r", "a.js", "x") != findings.fingerprint("r", "a.js", "y")


def test_validate_adds_fingerprint():
    assert len(findings.validate(make())["fingerprint"]) == 16


@pytest.mark.parametrize("bad", [{"severity": "huge"}, {"effort": "XL"}, {"confidence": 1.5}])
def test_validate_rejects_bad_values(bad):
    with pytest.raises(findings.FindingError):
        findings.validate(make(**bad))


def test_validate_rejects_missing_fields():
    broken = make()
    del broken["rule"]
    with pytest.raises(findings.FindingError):
        findings.validate(broken)


def test_unit_roundtrip_handles_slashes_and_spaces(tmp_path):
    findings.write_unit(tmp_path, "src/my dir", [make(file="src/my dir/a b.js")])
    loaded = findings.load_all(tmp_path)
    assert [f["file"] for f in loaded] == ["src/my dir/a b.js"]


def test_unicode_paths_roundtrip(tmp_path):
    findings.write_unit(tmp_path, "ünï", [make(file="ünï/ファイル.js")])
    assert findings.load_all(tmp_path)[0]["file"] == "ünï/ファイル.js"


def test_slug_does_not_collide_for_non_ascii_or_chunk_names():
    assert findings.slug("日本") != findings.slug("中文")
    assert findings.slug("src/a#2") != findings.slug("src/a_2")
    assert findings.slug("hot") == "hot"


def test_load_all_adds_missing_fingerprints(tmp_path):
    raw = make()
    (tmp_path / "lane-docs.json").write_text(json.dumps([raw]))
    assert len(findings.load_all(tmp_path)[0]["fingerprint"]) == 16


def test_load_all_names_the_broken_file(tmp_path):
    (tmp_path / "lane-docs.json").write_text(json.dumps([{"rule": "x"}]))
    with pytest.raises(findings.FindingError, match="lane-docs.json"):
        findings.load_all(tmp_path)


def test_leading_double_slash_is_collapsed():
    assert findings.normalize_path("//a/b.js") == "/a/b.js"
    assert findings.fingerprint("r", "//a/b.js", "x") == findings.fingerprint("r", "/a/b.js", "x")
