"""Tests for Programming/Python section structure (issue #348)."""

from __future__ import annotations

import yaml
from conftest import REPO_ROOT

MKDOCS_YML = REPO_ROOT / "mkdocs.yml"
INDEX_MD = REPO_ROOT / "docs" / "programming" / "python" / "index.md"


def test_python_index_exists():
    assert INDEX_MD.exists()


def test_python_nav_entries_resolve():
    loader = yaml.SafeLoader

    def _python_name_constructor(loader, tag_suffix, node):
        return loader.construct_scalar(node)

    loader.add_multi_constructor("tag:yaml.org,2002:python/name:", _python_name_constructor)
    cfg = yaml.load(MKDOCS_YML.read_text(), Loader=loader)
    programming = next((i["Programming"] for i in cfg["nav"] if "Programming" in i), None)
    assert programming is not None
    py_entry = next((e for e in programming if "Python" in e), None)
    assert py_entry is not None
    for entry in py_entry["Python"]:
        key = next(iter(entry.keys()))
        p = REPO_ROOT / "docs" / entry[key]
        assert p.exists(), f"Missing: {entry[key]}"
