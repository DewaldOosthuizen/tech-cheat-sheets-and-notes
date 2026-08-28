"""Tests for Programming/Java section structure (issues #271, #273).

Verifies that:
  - docs/programming/java/files/ has the domain-page structure
  - mkdocs.yml has a "Programming" nav group with a "Java" subgroup
  - README.md's "Current Content" table has a Programming row
"""

from __future__ import annotations

from pathlib import Path
from typing import ClassVar

import pytest
import yaml
from conftest import REPO_ROOT

MKDOCS_YML = REPO_ROOT / "mkdocs.yml"
README_MD = REPO_ROOT / "README.md"

# Path fragments — Java domain files
_PROG = Path("docs") / "programming" / "java" / "files"

DOMAIN_FILES = {
    "language-fundamentals": _PROG / "language-fundamentals" / "language-fundamentals.md",
    "oop": _PROG / "oop" / "oop.md",
    "functional-programming": _PROG / "functional-programming" / "functional-programming.md",
    "persistence": _PROG / "persistence" / "persistence.md",
    "collections": _PROG / "collections" / "collections.md",
    "abbreviations": _PROG / "abbreviations" / "abbreviations.md",
    "exams": _PROG / "exams" / "exams.md",
}

REQUIRED_HEADINGS = {
    "language-fundamentals": "# LANGUAGE FUNDAMENTALS",
    "oop": "# OOP",
    "functional-programming": "# FUNCTIONAL PROGRAMMING",
    "persistence": "# PERSISTENCE",
    "collections": "# COLLECTIONS",
    "abbreviations": "# ABBREVIATIONS",
    "exams": "# Exam Track Index",
}

REQUIRED_SECTIONS_PER_FILE = {
    "language-fundamentals": [
        "## Language Basics & Keywords",
        "## String Manipulation",
        "## Java 21 LTS — New in this Release",
    ],
    "oop": ["## Core OOP Concepts"],
    "functional-programming": ["## Lambda & Functional Interfaces"],
    "persistence": ["## JDBC", "## JPA"],
    "collections": [],
}


@pytest.fixture(scope="module")
def mkdocs_config():
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


@pytest.fixture(scope="module")
def domain_texts():
    return {k: v.read_text(encoding="utf-8") for k, v in DOMAIN_FILES.items()}


# ── Domain file existence and content ──────────────────────────────────────────


class TestJavaDomainFiles:
    """Verify Java domain files exist with correct headings and sections."""

    @pytest.mark.parametrize("key", DOMAIN_FILES.keys())
    def test_file_exists(self, key):
        assert DOMAIN_FILES[key].exists(), f"{DOMAIN_FILES[key]} does not exist"

    @pytest.mark.parametrize("key", DOMAIN_FILES.keys())
    def test_heading_present(self, domain_texts, key):
        expected = REQUIRED_HEADINGS[key]
        assert expected in domain_texts[key], (
            f"Expected heading '{expected}' not found in {key}"
        )

    @pytest.mark.parametrize("key, sections", REQUIRED_SECTIONS_PER_FILE.items())
    def test_sections_present(self, domain_texts, key, sections):
        for section in sections:
            assert section in domain_texts[key], (
                f"Expected section '{section}' not found in {key}"
            )

    def test_java21_mentioned(self, domain_texts):
        combined = "\n".join(domain_texts.values())
        assert "Java 21" in combined, "Java 21 should be mentioned somewhere in the domain files"


# ── Mkdocs Programming nav ─────────────────────────────────────────────────────


class TestMkdocsProgrammingNav:
    """Verify mkdocs.yml Programming nav structure."""

    EXPECTED_JAVA_NAV_ENTRIES: ClassVar[list[str]] = [
        "Abbreviations",
        "Exam Coverage",
        "Language Fundamentals",
        "OOP",
        "Functional Programming",
        "Persistence",
        "Spring Boot",
        "Collections",
    ]

    EXPECTED_PATHS: ClassVar[dict[str, str]] = {
        "Abbreviations": "programming/java/files/abbreviations/abbreviations.md",
        "Exam Coverage": "programming/java/files/exams/exams.md",
        "Language Fundamentals": (
            "programming/java/files/language-fundamentals/language-fundamentals.md"
        ),
        "OOP": "programming/java/files/oop/oop.md",
        "Functional Programming": (
            "programming/java/files/functional-programming/functional-programming.md"
        ),
        "Persistence": "programming/java/files/persistence/persistence.md",
        "Spring Boot": "programming/java/files/spring-boot/spring-boot.md",
        "Collections": "programming/java/files/collections/collections.md",
    }

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

    def test_java_subgroup_present(self, mkdocs_config):
        programming_section = next(
            (item["Programming"] for item in mkdocs_config["nav"] if "Programming" in item),
            None,
        )
        assert programming_section is not None, "Programming nav section missing"
        java_entry = next((e for e in programming_section if "Java" in e), None)
        assert java_entry is not None, "Java subgroup not found under Programming"
        java_section = java_entry["Java"]
        assert isinstance(java_section, list), "Java nav entry should be a list of sub-entries"

    def test_java_subgroup_is_list_not_string(self, mkdocs_config):
        programming_section = next(
            (item["Programming"] for item in mkdocs_config["nav"] if "Programming" in item),
            None,
        )
        assert programming_section is not None, "Programming nav section missing"
        java_entry = next((e for e in programming_section if "Java" in e), None)
        assert java_entry is not None and "Java" in java_entry, (
            "Java entry should exist under Programming"
        )
        assert isinstance(java_entry["Java"], list), (
            "Java should be a subgroup (list), not a flat nav entry (string)"
        )

    def test_all_java_nav_entries_in_order(self, mkdocs_config):
        programming_section = next(
            (item["Programming"] for item in mkdocs_config["nav"] if "Programming" in item),
            None,
        )
        assert programming_section is not None, "Programming nav section missing"
        java_entry = next((e for e in programming_section if "Java" in e), None)
        assert java_entry is not None, "Java subgroup not found"
        java_section = java_entry["Java"]
        entry_keys = [next(iter(e.keys())) for e in java_section]
        assert entry_keys == self.EXPECTED_JAVA_NAV_ENTRIES, (
            f"Java nav entries not in approved order: {entry_keys}"
        )

    def test_java_domain_entry_paths(self, mkdocs_config):
        programming_section = next(
            (item["Programming"] for item in mkdocs_config["nav"] if "Programming" in item),
            None,
        )
        assert programming_section is not None, "Programming nav section missing"
        java_entry = next((e for e in programming_section if "Java" in e), None)
        assert java_entry is not None, "Java subgroup not found"
        java_section = java_entry["Java"]

        for entry in java_section:
            key = next(iter(entry.keys()))
            expected_path = self.EXPECTED_PATHS.get(key)
            if expected_path:
                assert entry[key] == expected_path, (
                    f"Nav entry '{key}' points to '{entry[key]}', expected '{expected_path}'"
                )

    def test_python_coming_soon_present(self, mkdocs_config):
        programming_section = next(
            (item["Programming"] for item in mkdocs_config["nav"] if "Programming" in item),
            None,
        )
        assert programming_section is not None, "Programming nav section missing"
        entry_keys = [next(iter(e.keys())) for e in programming_section]
        assert "Python (Coming soon)" in entry_keys, "Python (Coming soon) entry not found"


# ── README current content ─────────────────────────────────────────────────────


class TestReadmeProgrammingRow:
    """Verify README.md has Programming in Current Content table."""

    def test_programming_row_present(self, readme_text):
        lines = readme_text.splitlines()
        data_rows = [
            ln
            for ln in lines
            if ln.strip().startswith("|") and "---" not in ln and "Topic" not in ln
        ]
        assert any("Programming" in row for row in data_rows), (
            "Expected a Programming row in README.md's Current Content table"
        )
