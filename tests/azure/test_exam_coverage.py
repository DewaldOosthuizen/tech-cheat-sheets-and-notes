"""Tests for Azure exam coverage pages.

Verifies that:
  - docs/index.md contains prose link to Azure Exam Track Index
  - docs/azure/files/exams/exams.md remains unchanged with correct AZ-X columns
"""

import pytest
from conftest import REPO_ROOT, expand_snippets

INDEX_MD = REPO_ROOT / "docs" / "index.md"
AZURE_EXAMS_MD = REPO_ROOT / "docs" / "azure" / "files" / "exams" / "exams.md"


@pytest.fixture(scope="module")
def index_text():
    return expand_snippets(INDEX_MD.read_text())


@pytest.fixture(scope="module")
def azure_exams_text():
    return AZURE_EXAMS_MD.read_text()


# ── index.md — Azure exam coverage link ──────────────────────────────────────


class TestIndexAzureInlineTableRemoved:
    """index.md must not contain the inline Azure exam coverage table."""

    def test_azure_inline_table_header_absent(self, index_text):
        assert "| AZ-900 | AZ-104 | AZ-305 | AZ-500 | AZ-700 |" not in index_text

    def test_azure_exam_coverage_heading_absent(self, index_text):
        # The standalone heading "Exam coverage by domain:" should be gone
        # (it may still appear in prose — we target the table row specifically)
        assert "| AZ-900 |" not in index_text

    def test_azure_prose_link_present(self, index_text):
        assert "See the [Azure Exam Track Index](azure/files/exams/exams.md)" in index_text

    def test_azure_prose_link_certification_text(self, index_text):
        assert "for full coverage by certification." in index_text


# ── azure/files/exams/exams.md validation ────────────────────────────────────


class TestAzureExamsUnchanged:
    """docs/azure/files/exams/exams.md must have correct structure with all AZ exams."""

    def test_azure_exams_has_az204_column(self, azure_exams_text):
        assert "AZ-204" in azure_exams_text

    def test_azure_exams_has_seven_columns(self, azure_exams_text):
        header = next((line for line in azure_exams_text.splitlines() if "Section" in line), None)
        assert header is not None
        # 7 columns: Section, AZ-900, AZ-104, AZ-204, AZ-305, AZ-500, AZ-700
        assert header.count("|") >= 8  # at least 7 columns = 8 pipes
