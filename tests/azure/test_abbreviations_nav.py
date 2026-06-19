"""Tests for Azure abbreviations content and navigation.

Verifies that:
  - docs/azure/files/abbreviations/abbreviations.md exists with # ABBREVIATIONS heading
  - docs/azure/files/abbreviations/abbreviations.md contains a table with
    Abbreviation and Definition columns
  - mkdocs.yml has Abbreviations nav entry as first child under Azure (before Exam Coverage)
  - docs/azure/files/exams/exams.md has Abbreviations as first data row in the table
"""

import pytest
import yaml
from conftest import REPO_ROOT

AZURE_ABBREV_MD = REPO_ROOT / "docs" / "azure" / "files" / "abbreviations" / "abbreviations.md"
MKDOCS_YML = REPO_ROOT / "mkdocs.yml"
AZURE_EXAMS_MD = REPO_ROOT / "docs" / "azure" / "files" / "exams" / "exams.md"

# Key abbreviations that must appear in the Azure abbreviations table
AZURE_REQUIRED_ABBREVIATIONS = [
    "AAD",
    "ACR",
    "AKS",
    "APIM",
    "ARM",
    "CDN",
    "DNS",
    "GRS",
    "NSG",
    "RBAC",
    "SLA",
    "SQL",
    "UDR",
    "VNet",
    "VPN",
    "WAF",
]


# ── Fixtures ─────────────────────────────────────────────────────────────────


@pytest.fixture(scope="module")
def azure_abbrev_text():
    return AZURE_ABBREV_MD.read_text()


@pytest.fixture(scope="module")
def mkdocs_config():
    # mkdocs.yml uses !!python/name: tags that yaml.safe_load cannot handle.
    # Register a constructor that treats unknown python/* tags as plain strings.
    loader_class = yaml.SafeLoader

    def _python_name_constructor(loader, tag_suffix, node):
        return loader.construct_scalar(node)

    loader_class.add_multi_constructor(
        "tag:yaml.org,2002:python/name:",
        _python_name_constructor,
    )
    return yaml.load(MKDOCS_YML.read_text(), Loader=loader_class)


@pytest.fixture(scope="module")
def azure_exams_text():
    return AZURE_EXAMS_MD.read_text()


# ── Azure abbreviations file tests ───────────────────────────────────────────


class TestAzureAbbreviationsFileExists:
    """docs/azure/files/abbreviations/abbreviations.md must exist."""

    def test_file_exists(self):
        assert AZURE_ABBREV_MD.exists(), (
            f"{AZURE_ABBREV_MD} does not exist — create it with # ABBREVIATIONS heading"
        )


class TestAzureAbbreviationsHeading:
    """The Azure abbreviations file must start with # ABBREVIATIONS."""

    def test_heading_present(self, azure_abbrev_text):
        assert "# ABBREVIATIONS" in azure_abbrev_text


class TestAzureAbbreviationsTableStructure:
    """The Azure abbreviations file must contain a two-column Markdown table."""

    def test_table_header_present(self, azure_abbrev_text):
        assert "| Abbreviation | Definition |" in azure_abbrev_text

    def test_table_separator_present(self, azure_abbrev_text):
        assert "| --- | --- |" in azure_abbrev_text

    def test_table_has_data_rows(self, azure_abbrev_text):
        lines = azure_abbrev_text.splitlines()
        data_rows = [
            ln
            for ln in lines
            if ln.strip().startswith("|") and "---" not in ln and "Abbreviation" not in ln
        ]
        assert len(data_rows) >= 10, f"Expected at least 10 abbreviation rows, got {len(data_rows)}"


class TestAzureAbbreviationsAlphaOrder:
    """Abbreviations must appear in alphabetical order (first column)."""

    def test_alphabetically_sorted(self, azure_abbrev_text):
        lines = azure_abbrev_text.splitlines()
        abbrevs = []
        for ln in lines:
            if ln.strip().startswith("|") and "---" not in ln and "Abbreviation" not in ln:
                first_col = ln.split("|")[1].strip()
                abbrevs.append(first_col)
        assert abbrevs == sorted(abbrevs), f"Abbreviations are not sorted: {abbrevs}"


class TestAzureRequiredAbbreviations:
    """Key Azure abbreviations must be present in the table."""

    @pytest.mark.parametrize("abbrev", AZURE_REQUIRED_ABBREVIATIONS)
    def test_abbreviation_present(self, azure_abbrev_text, abbrev):
        assert abbrev in azure_abbrev_text, (
            f"Expected abbreviation '{abbrev}' not found in azure abbreviations.md"
        )


# ── Azure navigation tests ───────────────────────────────────────────────────


class TestAzureAbbreviationsNav:
    """Abbreviations must be the first child under Azure with correct file path."""

    def test_abbreviations_nav_entry_present(self, mkdocs_config):
        csp_section = next(
            (
                item["Cloud Service Providers"]
                for item in mkdocs_config["nav"]
                if "Cloud Service Providers" in item
            ),
            None,
        )
        azure_section = next(
            (item["Azure"] for item in csp_section if "Azure" in item),
            None,
        )
        entry_keys = [next(iter(e.keys())) for e in azure_section]
        assert "Abbreviations" in entry_keys, "Abbreviations entry not found in Azure nav"

    def test_abbreviations_points_to_correct_file(self, mkdocs_config):
        csp_section = next(
            (
                item["Cloud Service Providers"]
                for item in mkdocs_config["nav"]
                if "Cloud Service Providers" in item
            ),
            None,
        )
        azure_section = next(
            (item["Azure"] for item in csp_section if "Azure" in item),
            None,
        )
        abbrev_entry = next(
            (e["Abbreviations"] for e in azure_section if "Abbreviations" in e),
            None,
        )
        assert abbrev_entry == "azure/files/abbreviations/abbreviations.md", (
            f"Azure Abbreviations nav points to '{abbrev_entry}', expected "
            "'azure/files/abbreviations/abbreviations.md'"
        )

    def test_abbreviations_before_exam_coverage(self, mkdocs_config):
        csp_section = next(
            (
                item["Cloud Service Providers"]
                for item in mkdocs_config["nav"]
                if "Cloud Service Providers" in item
            ),
            None,
        )
        azure_section = next(
            (item["Azure"] for item in csp_section if "Azure" in item),
            None,
        )
        entry_keys = [next(iter(e.keys())) for e in azure_section]
        abbrev_idx = entry_keys.index("Abbreviations")
        exam_idx = entry_keys.index("Exam Coverage")
        assert abbrev_idx < exam_idx, (
            f"Abbreviations (index {abbrev_idx}) must come before "
            f"Exam Coverage (index {exam_idx}) in Azure nav"
        )


# ── Azure exams.md tests ─────────────────────────────────────────────────────


class TestAzureExamsAbbreviationsRow:
    """docs/azure/files/exams/exams.md must have Abbreviations as first data row."""

    def test_abbreviations_row_present(self, azure_exams_text):
        assert "[Abbreviations](../abbreviations/abbreviations.md)" in azure_exams_text

    def test_abbreviations_is_first_data_row(self, azure_exams_text):
        lines = azure_exams_text.splitlines()
        data_rows = [
            ln
            for ln in lines
            if ln.strip().startswith("|") and "---" not in ln and "Section" not in ln
        ]
        assert len(data_rows) > 0, "No data rows found in azure exams.md table"
        assert "[Abbreviations]" in data_rows[0], (
            f"First data row must be Abbreviations, got: {data_rows[0]}"
        )

    def test_abbreviations_row_has_dash_placeholders(self, azure_exams_text):
        lines = azure_exams_text.splitlines()
        for ln in lines:
            if "[Abbreviations]" in ln and ln.strip().startswith("|"):
                assert ln.count("| — |") >= 5 or ln.count("— |") >= 5, (
                    f"Expected dash placeholders in abbreviations row: {ln}"
                )
                break
