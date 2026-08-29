"""Tests for Azure exam coverage pages.

Verifies that:
  - docs/index.md links to the Azure Exam Track Index
  - docs/azure/files/exams/exams.md remains unchanged with correct AZ-X columns
"""

import pytest
from conftest import REPO_ROOT

INDEX_MD = REPO_ROOT / "docs" / "index.md"
AZURE_EXAMS_MD = REPO_ROOT / "docs" / "azure" / "files" / "exams" / "exams.md"

@pytest.fixture(scope="module")
def index_text():
    return INDEX_MD.read_text()

@pytest.fixture(scope="module")
def azure_exams_text():
    return AZURE_EXAMS_MD.read_text()

# ── index.md — Azure exam coverage link ──────────────────────────────────────


class TestIndexAzureInlineTableRemoved:
    """index.md must not contain the inline Azure exam coverage table."""

    def test_azure_inline_table_header_absent(self, index_text):
        assert "| AZ-900 | AZ-104 | AZ-305 | AZ-500 | AZ-700 |" not in index_text

    def test_azure_exam_coverage_heading_absent(self, index_text):
        assert "| AZ-900 |" not in index_text

    def test_azure_prose_link_present(self, index_text):
        assert "[Azure Exam Track Index](azure/index.md)" in index_text

    def test_azure_prose_link_certification_text(self, index_text):
        assert "for full certification coverage" in index_text


# ── azure/files/exams/exams.md validation ────────────────────────────────────


class TestAzureExamsUnchanged:
    """docs/azure/files/exams/exams.md must have correct structure with all AZ exams."""

    def test_azure_exams_has_az204_column(self, azure_exams_text):
        assert "AZ-204" in azure_exams_text

    def test_azure_exams_has_seven_columns(self, azure_exams_text):
        header = next(
            (line for line in azure_exams_text.splitlines() if "Section" in line), None
        )
        assert header is not None
        assert header.count("|") >= 8

    def test_azure_exams_has_networking_section(self, azure_exams_text):
        assert "Networking" in azure_exams_text

    def test_azure_exams_has_security_section(self, azure_exams_text):
        assert "Security" in azure_exams_text

    def test_azure_exams_has_storage_section(self, azure_exams_text):
        assert "Storage" in azure_exams_text

    def test_azure_exams_has_monitoring_section(self, azure_exams_text):
        assert "Monitoring & Observability" in azure_exams_text

    def test_azure_exams_has_compute_section(self, azure_exams_text):
        assert "Compute" in azure_exams_text

    def test_azure_exams_has_database_section(self, azure_exams_text):
        assert "Database" in azure_exams_text

    def test_azure_exams_has_identity_section(self, azure_exams_text):
        assert "Identity & Access" in azure_exams_text

    def test_azure_exams_has_hadr_section(self, azure_exams_text):
        assert "High Availability & Disaster Recovery" in azure_exams_text

    def test_azure_exams_has_governance_section(self, azure_exams_text):
        assert "Governance" in azure_exams_text

    def test_azure_exams_has_messaging_section(self, azure_exams_text):
        assert "Messaging & Integration" in azure_exams_text

    def test_azure_exams_has_waf_section(self, azure_exams_text):
        assert "Well-Architected Framework" in azure_exams_text
