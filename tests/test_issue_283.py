"""Tests for issue #283: FEATURE: Add a Spring Boot architecture and
production practices cheat sheet.

Verifies that:
  - mkdocs.yml Programming nav contains a Spring Boot entry pointing to
    programming/files/spring-boot/spring-boot.md, placed between Persistence
    and Collections.
  - docs/index.md contains a Programming summary table with a Spring Boot row.
  - docs/programming/files/exams/exams.md contains a Spring Boot row with N/A
    coverage cells.
  - docs/programming/files/spring-boot/spring-boot.md exists with the required
    heading, sections, and at least one flowchart TD Mermaid block.
"""

from __future__ import annotations

import pytest
import yaml
from conftest import REPO_ROOT

MKDOCS_YML = REPO_ROOT / "mkdocs.yml"
INDEX_MD = REPO_ROOT / "docs" / "index.md"
EXAMS_MD = REPO_ROOT / "docs" / "programming" / "files" / "exams" / "exams.md"
SPRING_BOOT_MD = REPO_ROOT / "docs" / "programming" / "files" / "spring-boot" / "spring-boot.md"

EXPECTED_NAV_ORDER = [
    "Abbreviations",
    "Exam Coverage",
    "Language Fundamentals",
    "OOP",
    "Functional Programming",
    "Persistence",
    "Spring Boot",
    "Collections",
]

REQUIRED_HEADINGS = [
    "# SPRING BOOT",
]

REQUIRED_SECTIONS = [
    "## Auto-Configuration & Starters",
    "## Externalised Configuration",
    "## Profiles",
    "## Dependency Injection",
    "## Validation",
    "## Actuator & Observability",
    "## Configuration Properties",
    "## MVC vs WebFlux",
    "## Decision Flow",
    "## Native Images",
    "## Component Stereotype Decision Table",
]


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
def spring_boot_text():
    assert SPRING_BOOT_MD.exists(), f"{SPRING_BOOT_MD} does not exist"
    return SPRING_BOOT_MD.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def index_text():
    return INDEX_MD.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def exams_text():
    return EXAMS_MD.read_text(encoding="utf-8")


class TestMkdocsSpringBootNav:
    def test_spring_boot_entry_present(self, mkdocs_config):
        programming_section = next(
            (item["Programming"] for item in mkdocs_config["nav"] if "Programming" in item),
            None,
        )
        assert programming_section is not None, "Programming nav section missing"
        entry_keys = [next(iter(e.keys())) for e in programming_section]
        assert "Spring Boot" in entry_keys, "Spring Boot nav entry not found"

    def test_spring_boot_nav_path(self, mkdocs_config):
        programming_section = next(
            (item["Programming"] for item in mkdocs_config["nav"] if "Programming" in item),
            None,
        )
        for entry in programming_section:
            if "Spring Boot" in entry:
                path = entry["Spring Boot"]
                assert path == "programming/files/spring-boot/spring-boot.md", (
                    f"Spring Boot nav entry points to '{path}', expected "
                    "'programming/files/spring-boot/spring-boot.md'"
                )
                return
        raise AssertionError("Spring Boot entry not found in nav")

    def test_spring_boot_between_persistence_and_collections(self, mkdocs_config):
        programming_section = next(
            (item["Programming"] for item in mkdocs_config["nav"] if "Programming" in item),
            None,
        )
        entry_keys = [next(iter(e.keys())) for e in programming_section]
        persistence_idx = entry_keys.index("Persistence")
        spring_boot_idx = entry_keys.index("Spring Boot")
        collections_idx = entry_keys.index("Collections")
        assert persistence_idx < spring_boot_idx < collections_idx, (
            f"Spring Boot must sit between Persistence and Collections; order is {entry_keys}"
        )

    def test_all_nav_entries_in_order(self, mkdocs_config):
        programming_section = next(
            (item["Programming"] for item in mkdocs_config["nav"] if "Programming" in item),
            None,
        )
        entry_keys = [next(iter(e.keys())) for e in programming_section]
        assert entry_keys == EXPECTED_NAV_ORDER, (
            f"Programming nav entries not in approved order: {entry_keys}"
        )


class TestSpringBootDomainFile:
    def test_file_exists(self):
        assert SPRING_BOOT_MD.exists(), f"{SPRING_BOOT_MD} does not exist"

    def test_top_level_heading(self, spring_boot_text):
        for heading in REQUIRED_HEADINGS:
            assert heading in spring_boot_text, (
                f"Expected heading '{heading}' not found in spring-boot.md"
            )

    @pytest.mark.parametrize("section", REQUIRED_SECTIONS)
    def test_required_sections_present(self, spring_boot_text, section):
        assert section in spring_boot_text, (
            f"Expected section '{section}' not found in spring-boot.md"
        )

    def test_mermaid_flowchart_present(self, spring_boot_text):
        from conftest import expand_snippets

        expanded = expand_snippets(spring_boot_text)
        assert "```mermaid" in spring_boot_text, "Expected a mermaid code fence in spring-boot.md"
        assert "flowchart TD" in expanded, (
            "Expected at least one 'flowchart TD' Mermaid block in spring-boot.md "
            "after snippet expansion"
        )


class TestIndexProgrammingSummary:
    def test_programming_summary_table_present(self, index_text):
        assert "## Programming" in index_text, "Expected '## Programming' section in docs/index.md"

    def test_spring_boot_row_in_summary(self, index_text):
        assert "Spring Boot" in index_text, "Expected Spring Boot row in Programming summary table"
        assert "programming/files/spring-boot/spring-boot.md" in index_text, (
            "Expected Spring Boot link to programming/files/spring-boot/spring-boot.md in index.md"
        )


class TestExamsSpringBootRow:
    def test_spring_boot_row_present(self, exams_text):
        assert "Spring Boot" in exams_text, "Expected Spring Boot row in exams.md exam track index"

    def test_spring_boot_na_coverage(self, exams_text):
        assert "| [Spring Boot]" in exams_text, (
            "Expected Spring Boot row starting with '| [Spring Boot]' in exams.md"
        )
        lines = exams_text.splitlines()
        for line in lines:
            if line.strip().startswith("| [Spring Boot]"):
                cells = [c.strip() for c in line.split("|")]
                # cells[0] is empty (leading |), cells[1] is the section link,
                # cells[2:-1] are the four exam columns, cells[-1] is empty
                # (trailing |)
                exam_cells = cells[2:-1]
                for cell in exam_cells:
                    assert cell == "N/A", (
                        f"Expected N/A coverage cells for Spring Boot, got '{cell}'"
                    )
                return
        raise AssertionError("Spring Boot row not found in exams.md")
