"""Tests for issue #271 (original: Add Programming section and Java) and
issue #273 (enhancement: split Java into domain pages).

Verifies that:
  - docs/programming/ has the domain-page structure (language-fundamentals,
    oop, functional-programming, persistence, collections) plus abbreviations
    and exam coverage pages.
  - mkdocs.yml has a "Programming" nav group with the 7 domain entries,
    alphabetically ordered before "Cloud Service Providers".
  - README.md's "Current Content" table has a Programming row.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml
from conftest import REPO_ROOT

MKDOCS_YML = REPO_ROOT / "mkdocs.yml"
README_MD = REPO_ROOT / "README.md"

# Path fragments
_PROG = Path("docs") / "programming"
_FILES = _PROG / "files"
_LF = _FILES / "language-fundamentals" / "language-fundamentals.md"
_OOP = _FILES / "oop" / "oop.md"
_FP = _FILES / "functional-programming" / "functional-programming.md"
_PERS = _FILES / "persistence" / "persistence.md"
_COL = _FILES / "collections" / "collections.md"

DOMAIN_FILES = {
    "language-fundamentals": _LF,
    "oop": _OOP,
    "functional-programming": _FP,
    "persistence": _PERS,
    "collections": _COL,
}

REQUIRED_SECTIONS_PER_FILE = {
    "language-fundamentals": [
        "## Language Basics & Keywords",
        "## String Manipulation",
    ],
    "oop": [
        "## Core OOP Concepts",
    ],
    "functional-programming": [
        "## Lambda & Functional Interfaces",
    ],
    "persistence": [
        "## JDBC",
        "## JPA",
    ],
    "collections": [],
}

REQUIRED_HEADINGS = {
    "language-fundamentals": "# LANGUAGE FUNDAMENTALS",
    "oop": "# OOP",
    "functional-programming": "# FUNCTIONAL PROGRAMMING",
    "persistence": "# PERSISTENCE",
    "collections": "# COLLECTIONS",
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


class TestDomainFilesExist:
    @pytest.mark.parametrize("key", DOMAIN_FILES.keys())
    def test_file_exists(self, key):
        assert DOMAIN_FILES[key].exists(), f"{DOMAIN_FILES[key]} does not exist"


class TestDomainHeadings:
    @pytest.mark.parametrize("key", DOMAIN_FILES.keys())
    def test_heading_present(self, domain_texts, key):
        expected = REQUIRED_HEADINGS[key]
        assert expected in domain_texts[key], f"Expected heading '{expected}' not found in {key}"


class TestDomainSections:
    @pytest.mark.parametrize("key,sections", REQUIRED_SECTIONS_PER_FILE.items())
    def test_sections_present(self, domain_texts, key, sections):
        for section in sections:
            assert section in domain_texts[key], f"Expected section '{section}' not found in {key}"


class TestJava21Mentioned:
    def test_mentions_java_21(self, domain_texts):
        combined = "\n".join(domain_texts.values())
        assert "Java 21" in combined, "Java 21 should be mentioned somewhere in the domain files"


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

    def test_domain_entries_present_under_programming(self, mkdocs_config):
        programming_section = next(
            (item["Programming"] for item in mkdocs_config["nav"] if "Programming" in item),
            None,
        )
        assert programming_section is not None, "Programming nav section missing"
        entry_keys = [next(iter(e.keys())) for e in programming_section]
        expected_entries = [
            "Abbreviations",
            "Exam Coverage",
            "Language Fundamentals",
            "OOP",
            "Functional Programming",
            "Persistence",
            "Collections",
        ]
        for expected in expected_entries:
            assert expected in entry_keys, f"Expected nav entry '{expected}' not found"

    def test_domain_entry_points_to_correct_files(self, mkdocs_config):
        programming_section = next(
            (item["Programming"] for item in mkdocs_config["nav"] if "Programming" in item),
            None,
        )
        expected_paths = {
            "Abbreviations": "programming/files/abbreviations/abbreviations.md",
            "Exam Coverage": "programming/files/exams/exams.md",
            "Language Fundamentals": "programming/files/language-fundamentals/"
            "language-fundamentals.md",
            "OOP": "programming/files/oop/oop.md",
            "Functional Programming": "programming/files/functional-programming/"
            "functional-programming.md",
            "Persistence": "programming/files/persistence/persistence.md",
            "Collections": "programming/files/collections/collections.md",
        }
        for entry in programming_section:
            key = next(iter(entry.keys()))
            expected_path = expected_paths.get(key)
            if expected_path:
                assert entry[key] == expected_path, (
                    f"Nav entry '{key}' points to '{entry[key]}', expected '{expected_path}'"
                )


class TestReadmeCurrentContent:
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
