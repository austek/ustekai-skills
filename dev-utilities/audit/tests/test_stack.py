from auditlib import stack


def test_detects_node_and_python(tmp_path):
    (tmp_path / "package.json").write_text("{}")
    (tmp_path / "svc").mkdir()
    (tmp_path / "svc" / "pyproject.toml").write_text("")
    assert stack.detect_stack(tmp_path) == ["node", "python"]


def test_empty_repo_has_no_stack(tmp_path):
    assert stack.detect_stack(tmp_path) == []


def test_node_modules_markers_are_ignored(tmp_path):
    (tmp_path / "node_modules").mkdir()
    (tmp_path / "node_modules" / "Cargo.toml").write_text("")
    assert stack.detect_stack(tmp_path) == []
