"""Tests for issue #273: FEATURE: Enhance Java section.

Verifies that:
  - docs/programming/ has a multi-page structure matching cloud-provider convention:
    Abbreviations, Exam Coverage, Language Fundamentals, OOP, Functional Programming,
    Persistence, Collections.
  - mkdocs.yml Programming nav has the 7 alphabetically-ordered entries.
  - The new domain files exist with expected headings.
  - The old java.md is removed.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml
from conftest import REPO_ROOT

MKDOCS_YML = REPO_ROOT / "mkdocs.yml"

# Path fragments
_PROG = Path("docs") / "programming"
_FILES = _PROG / "files"
_ABB = _FILES / "abbreviations" / "abbreviations.md"
_EXM = _FILES / "exams" / "exams.md"
_LF = _FILES / "language-fundamentals" / "language-fundamentals.md"
_OOP = _FILES / "oop" / "oop.md"
_FP = _FILES / "functional-programming" / "functional-programming.md"
_PERS = _FILES / "persistence" / "persistence.md"
_COL = _FILES / "collections" / "collections.md"

DOMAIN_FILES = {
    "abbreviations": _ABB,
    "exams": _EXM,
    "language-fundamentals": _LF,
    "oop": _OOP,
    "functional-programming": _FP,
    "persistence": _PERS,
    "collections": _COL,
}

OLD_JAVA_MD = _FILES / "java" / "java.md"

EXPECTED_NAV_ENTRIES = [
    "Abbreviations",
    "Exam Coverage",
    "Language Fundamentals",
    "OOP",
    "Functional Programming",
    "Persistence",
    "Collections",
    "PostgreSQL Operations & Performance",
]

REQUIRED_HEADINGS = {
    "abbreviations": "# ABBREVIATIONS",
    "exams": "# Exam Track Index",
    "language-fundamentals": "# LANGUAGE FUNDAMENTALS",
    "oop": "# OOP",
    "functional-programming": "# FUNCTIONAL PROGRAMMING",
    "persistence": "# PERSISTENCE",
    "collections": "# COLLECTIONS",
}

REQUIRED_SECTIONS_LANG_FUND = [
    "## Language Basics & Keywords",
    "## String Manipulation",
]

REQUIRED_SECTIONS_OOP = [
    "## Core OOP Concepts",
]

REQUIRED_SECTIONS_FUNCTIONAL = [
    "## Lambda & Functional Interfaces",
]

REQUIRED_SECTIONS_PERSISTENCE = [
    "## JDBC",
    "## JPA",
]

REQUIRED_SECTIONS_COLLECTIONS = []


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
def domain_texts():
    return {k: v.read_text(encoding="utf-8") for k, v in DOMAIN_FILES.items()}


class TestDomainFilesExist:
    @pytest.mark.parametrize("key", DOMAIN_FILES.keys())
    def test_file_exists(self, key):
        assert DOMAIN_FILES[key].exists(), f"{DOMAIN_FILES[key]} does not exist"


class TestOldJavaFileRemoved:
    def test_java_md_removed(self):
        assert not OLD_JAVA_MD.exists(), f"{OLD_JAVA_MD} should have been removed"


class TestDomainHeadings:
    @pytest.mark.parametrize("key", DOMAIN_FILES.keys())
    def test_heading_present(self, domain_texts, key):
        expected = REQUIRED_HEADINGS[key]
        assert expected in domain_texts[key], f"Expected heading '{expected}' not found in {key}"


class TestLanguageFundamentalsSections:
    @pytest.mark.parametrize("section", REQUIRED_SECTIONS_LANG_FUND)
    def test_section_present(self, domain_texts, section):
        assert section in domain_texts["language-fundamentals"], (
            f"Expected section '{section}' not found"
        )


class TestOopSections:
    @pytest.mark.parametrize("section", REQUIRED_SECTIONS_OOP)
    def test_section_present(self, domain_texts, section):
        assert section in domain_texts["oop"], f"Expected section '{section}' not found"


class TestFunctionalProgrammingSections:
    @pytest.mark.parametrize("section", REQUIRED_SECTIONS_FUNCTIONAL)
    def test_section_present(self, domain_texts, section):
        assert section in domain_texts["functional-programming"], (
            f"Expected section '{section}' not found"
        )


class TestPersistenceSections:
    @pytest.mark.parametrize("section", REQUIRED_SECTIONS_PERSISTENCE)
    def test_section_present(self, domain_texts, section):
        assert section in domain_texts["persistence"], f"Expected section '{section}' not found"


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

    def test_all_nav_entries_present(self, mkdocs_config):
        programming_section = next(
            (item["Programming"] for item in mkdocs_config["nav"] if "Programming" in item),
            None,
        )
        assert programming_section is not None, "Programming nav section missing"
        entry_keys: list[str] = [next(iter(e.keys())) for e in programming_section]
        for expected in EXPECTED_NAV_ENTRIES:
            assert expected in entry_keys, f"Expected nav entry '{expected}' not found"

    def test_nav_entries_ordered(self, mkdocs_config):
        programming_section = next(
            (item["Programming"] for item in mkdocs_config["nav"] if "Programming" in item),
            None,
        )
        entry_keys: list[str] = [next(iter(e.keys())) for e in programming_section]
        assert entry_keys == EXPECTED_NAV_ENTRIES, (
            f"Programming nav entries not in approved order: {entry_keys}"
        )

    def test_no_java_single_entry(self, mkdocs_config):
        programming_section = next(
            (item["Programming"] for item in mkdocs_config["nav"] if "Programming" in item),
            None,
        )
        entry_keys: list[str] = [next(iter(e.keys())) for e in programming_section]
        assert "Java" not in entry_keys, (
            "Old single 'Java' entry should not exist — replaced by 7 domain pages"
        )
