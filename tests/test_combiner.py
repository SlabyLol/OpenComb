"""Tests for CodeCombiner and ConfigMerger."""

from pathlib import Path

import pytest
import yaml

from opencomb.combiner import CodeCombiner, ConfigMerger


def test_combine_files(tmp_path: Path):
    a = tmp_path / "a.py"
    b = tmp_path / "b.py"
    a.write_text("import os\n\ndef foo():\n    return 1\n")
    b.write_text("import sys\n\ndef bar():\n    return 2\n")

    combiner = CodeCombiner()
    result = combiner.combine_files([a, b])

    assert "def foo()" in result
    assert "def bar()" in result
    assert "import os" in result
    assert "import sys" in result


def test_combine_snippets():
    combiner = CodeCombiner()
    result = combiner.combine_snippets(
        ["x = 1", "y = 2"],
        names=["first", "second"],
    )
    assert "x = 1" in result
    assert "y = 2" in result
    assert "first" in result


def test_config_merge_deep(tmp_path: Path):
    base = tmp_path / "base.yaml"
    override = tmp_path / "override.yaml"

    base.write_text(
        yaml.dump({"db": {"host": "localhost", "port": 5432}, "debug": False})
    )
    override.write_text(yaml.dump({"db": {"port": 5433}, "debug": True}))

    merger = ConfigMerger()
    result = merger.merge_files([base, override])

    assert result["db"]["host"] == "localhost"
    assert result["db"]["port"] == 5433
    assert result["debug"] is True


def test_config_merge_shallow(tmp_path: Path):
    base = tmp_path / "base.yaml"
    override = tmp_path / "override.yaml"

    base.write_text(yaml.dump({"a": {"x": 1}, "b": 2}))
    override.write_text(yaml.dump({"a": {"y": 2}}))

    merger = ConfigMerger()
    result = merger.merge_files([base, override], strategy="shallow")

    # shallow replaces the whole "a" key
    assert result["a"] == {"y": 2}
    assert result["b"] == 2


def test_config_save_and_load(tmp_path: Path):
    merger = ConfigMerger()
    data = {"name": "OpenComb", "version": "0.1.0", "features": ["combine", "merge"]}

    out = tmp_path / "out.yaml"
    merger.save(data, out)
    loaded = merger._load(out)
    assert loaded == data
