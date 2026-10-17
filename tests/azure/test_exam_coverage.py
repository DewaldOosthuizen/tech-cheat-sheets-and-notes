"""Tests for Azure exam coverage pages.

Verifies that:
  - docs/index.md links to the Azure Exam Track Index
  - docs/azure/files/exams/exams.md remains unchanged with correct AZ-X columns
"""

import pytest
from conftest import (
    REPO_ROOT,
    assert_text_contains,
    assert_text_not_contains,
)

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
        assert_text_not_contains(index_text, "| AZ-900 | AZ-104 | AZ-305 | AZ-500 | AZ-700 |")

    def test_azure_exam_coverage_heading_absent(self, index_text):
        assert_text_not_contains(index_text, "| AZ-900 |")

    def test_azure_prose_link_present(self, index_text):
        assert_text_contains(index_text, "[Azure Exam Track Index](azure/index.md)")

    def test_azure_prose_link_certification_text(self, index_text):
        assert_text_contains(index_text, "for full certification coverage")


# ── azure/files/exams/exams.md validation ────────────────────────────────────


class TestAzureExamsUnchanged:
    """docs/azure/files/exams/exams.md must have correct structure with all AZ exams."""

    def test_azure_exams_has_az204_column(self, azure_exams_text):
        assert_text_contains(azure_exams_text, "AZ-204")

    def test_azure_exams_has_seven_columns(self, azure_exams_text):
        header = next((line for line in azure_exams_text.splitlines() if "Section" in line), None)
        assert header is not None
        assert header.count("|") >= 8

    def test_azure_exams_has_networking_section(self, azure_exams_text):
        assert_text_contains(azure_exams_text, "Networking")

    def test_azure_exams_has_security_section(self, azure_exams_text):
        assert_text_contains(azure_exams_text, "Security")

    def test_azure_exams_has_storage_section(self, azure_exams_text):
        assert_text_contains(azure_exams_text, "Storage")

    def test_azure_exams_has_monitoring_section(self, azure_exams_text):
        assert_text_contains(azure_exams_text, "Monitoring & Observability")

    def test_azure_exams_has_compute_section(self, azure_exams_text):
        assert_text_contains(azure_exams_text, "Compute")

    def test_azure_exams_has_database_section(self, azure_exams_text):
        assert_text_contains(azure_exams_text, "Database")

    def test_azure_exams_has_identity_section(self, azure_exams_text):
        assert_text_contains(azure_exams_text, "Identity & Access")

    def test_azure_exams_has_hadr_section(self, azure_exams_text):
        assert_text_contains(azure_exams_text, "High Availability & Disaster Recovery")

    def test_azure_exams_has_governance_section(self, azure_exams_text):
        assert_text_contains(azure_exams_text, "Governance")

    def test_azure_exams_has_messaging_section(self, azure_exams_text):
        assert_text_contains(azure_exams_text, "Messaging & Integration")

    def test_azure_exams_has_waf_section(self, azure_exams_text):
        assert_text_contains(azure_exams_text, "Well-Architected Framework")
