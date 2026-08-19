"""Tests for issue #271: FEATURE: Add Programming section and add Java.

Verifies that:
  - docs/programming/files/java/java.md exists with # JAVA heading and the
    required sub-sections (Language Basics & Keywords, Core OOP Concepts,
    Lambda & Functional Interfaces, String Manipulation, JDBC, JPA, Lombok).
  - mkdocs.yml has a new top-level "Programming" nav group, alphabetically
    ordered before "Cloud Service Providers", with a "Java" entry pointing to
    programming/files/java/java.md.
  - README.md's "Current Content" table has a Programming/Java row.
"""

from __future__ import annotations

import pytest
import yaml
from conftest import REPO_ROOT

JAVA_MD = REPO_ROOT / "docs" / "programming" / "files" / "java" / "java.md"
MKDOCS_YML = REPO_ROOT / "mkdocs.yml"
README_MD = REPO_ROOT / "README.md"

REQUIRED_SECTIONS = [
    "## Language Basics & Keywords",
    "## Core OOP Concepts",
    "## Lambda & Functional Interfaces",
    "## String Manipulation",
    "## JDBC",
    "## JPA",
    "## Lombok",
]


@pytest.fixture(scope="module")
def java_text():
    return JAVA_MD.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def mkdocs_config():
    # mkdocs.yml uses !!python/name: tags that yaml.safe_load cannot handle.
    loader_class = yaml.SafeLoader

    def _python_name_constructor(loader, tag_suffix, node):
        return loader.construct_scalar(node)

    loader_class.add_multi_constructor(
        "tag:yaml.org,2002:python/name:",
        _python_name_constructor,
    )
    return yaml.load(MKDOCS_YML.read_text(), Loader=loader_class)


@pytest.fixture(scope="module")
def readme_text():
    return README_MD.read_text(encoding="utf-8")


class TestJavaFileExists:
    def test_file_exists(self):
        assert JAVA_MD.exists(), f"{JAVA_MD} does not exist — create it with # JAVA heading"


class TestJavaHeading:
    def test_heading_present(self, java_text):
        assert "# JAVA" in java_text


class TestJavaRequiredSections:
    @pytest.mark.parametrize("section", REQUIRED_SECTIONS)
    def test_section_present(self, java_text, section):
        assert section in java_text, f"Expected section '{section}' not found in java.md"


class TestJavaMentionsLTS:
    def test_mentions_java_21(self, java_text):
        assert "Java 21" in java_text


class TestMkdocsProgrammingNav:
    def test_programming_group_present(self, mkdocs_config):
        keys = [next(iter(item.keys())) for item in mkdocs_config["nav"] if isinstance(item, dict)]
        assert "Programming" in keys, "Programming nav group not found"

    def test_programming_before_cloud_service_providers(self, mkdocs_config):
        keys = [next(iter(item.keys())) for item in mkdocs_config["nav"] if isinstance(item, dict)]
        programming_idx = keys.index("Programming")
        csp_idx = keys.index("Cloud Service Providers")
        assert programming_idx < csp_idx, (
            "Programming nav group must come before Cloud Service Providers "
            "(alphabetical top-level ordering)"
        )

    def test_java_entry_present_under_programming(self, mkdocs_config):
        programming_section = next(
            (item["Programming"] for item in mkdocs_config["nav"] if "Programming" in item),
            None,
        )
        assert programming_section is not None, "Programming nav section missing"
        entry_keys = [next(iter(e.keys())) for e in programming_section]
        assert "Java" in entry_keys

    def test_java_entry_points_to_correct_file(self, mkdocs_config):
        programming_section = next(
            (item["Programming"] for item in mkdocs_config["nav"] if "Programming" in item),
            None,
        )
        java_entry = next(
            (e["Java"] for e in programming_section if "Java" in e),
            None,
        )
        assert java_entry == "programming/files/java/java.md"


class TestReadmeCurrentContent:
    def test_java_row_present(self, readme_text):
        lines = readme_text.splitlines()
        data_rows = [
            ln
            for ln in lines
            if ln.strip().startswith("|") and "---" not in ln and "Topic" not in ln
        ]
        assert any("Java" in row or "Programming" in row for row in data_rows), (
            "Expected a Programming/Java row in README.md's Current Content table"
        )
