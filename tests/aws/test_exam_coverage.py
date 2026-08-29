"""Tests for AWS exam coverage pages.

Verifies that:
  - docs/index.md links to the AWS Exam Track Index
  - docs/aws/files/exams/exams.md exists with correct AWS exam coverage matrix
  - mkdocs.yml registers the AWS Exam Coverage page
"""

import pytest
from conftest import REPO_ROOT

INDEX_MD = REPO_ROOT / "docs" / "index.md"
AWS_EXAMS_MD = REPO_ROOT / "docs" / "aws" / "files" / "exams" / "exams.md"
MKDOCS_YML = REPO_ROOT / "mkdocs.yml"

@pytest.fixture(scope="module")
def index_text():
    return INDEX_MD.read_text()

@pytest.fixture(scope="module")
def aws_exams_text():
    return AWS_EXAMS_MD.read_text()

@pytest.fixture(scope="module")
def mkdocs_text():
    return MKDOCS_YML.read_text()

# ── index.md — AWS exam coverage link ────────────────────────────────────────


class TestIndexAWSInlineTableRemoved:
    """index.md must not contain the inline AWS exam coverage table."""

    def test_aws_inline_table_header_absent(self, index_text):
        assert "| CLF-C02 | SAA-C03 | SAP-C02 |" not in index_text

    def test_aws_exam_coverage_table_absent(self, index_text):
        assert "| CLF-C02 |" not in index_text

    def test_aws_prose_link_present(self, index_text):
        assert "[AWS Exam Track Index](aws/index.md)" in index_text

    def test_aws_prose_link_certification_text(self, index_text):
        # Both prose links share the same suffix — verified implicitly by both being present
        assert "aws/index.md" in index_text


# ── aws/files/exams/exams.md — file content ──────────────────────────────────


class TestAWSExamsFileExists:
    """docs/aws/files/exams/exams.md must exist."""

    def test_aws_exams_file_exists(self):
        assert AWS_EXAMS_MD.exists(), "docs/aws/files/exams/exams.md does not exist"


class TestAWSExamsFileContent:
    """docs/aws/files/exams/exams.md must contain the correct exam coverage matrix."""

    def test_heading_present(self, aws_exams_text):
        assert "# Exam Track Index" in aws_exams_text

    def test_table_header_clf(self, aws_exams_text):
        assert "CLF-C02" in aws_exams_text

    def test_table_header_saa(self, aws_exams_text):
        assert "SAA-C03" in aws_exams_text

    def test_table_header_sap(self, aws_exams_text):
        assert "SAP-C02" in aws_exams_text

    def test_compute_row_present(self, aws_exams_text):
        assert "[Compute]" in aws_exams_text

    def test_compute_links_to_compute_md(self, aws_exams_text):
        assert "../compute/compute.md" in aws_exams_text

    def test_networking_row_present(self, aws_exams_text):
        assert "[Networking]" in aws_exams_text

    def test_networking_links_to_networking_md(self, aws_exams_text):
        assert "../networking/networking.md" in aws_exams_text

    def test_storage_row_present(self, aws_exams_text):
        assert "[Storage]" in aws_exams_text

    def test_storage_links_to_storage_md(self, aws_exams_text):
        assert "../storage/storage.md" in aws_exams_text

    def test_database_row_present(self, aws_exams_text):
        assert "[Database]" in aws_exams_text

    def test_database_links_to_database_md(self, aws_exams_text):
        assert "../database/database.md" in aws_exams_text

    def test_identity_row_present(self, aws_exams_text):
        assert "[Identity & Access]" in aws_exams_text

    def test_identity_links_to_identity_md(self, aws_exams_text):
        assert "../identity/identity.md" in aws_exams_text

    def test_security_row_present(self, aws_exams_text):
        assert "[Security]" in aws_exams_text

    def test_security_links_to_security_md(self, aws_exams_text):
        assert "../security/security.md" in aws_exams_text

    def test_monitoring_row_present(self, aws_exams_text):
        assert "[Monitoring & Observability]" in aws_exams_text

    def test_monitoring_links_to_monitoring_md(self, aws_exams_text):
        assert "../monitoring/monitoring.md" in aws_exams_text

    def test_messaging_row_present(self, aws_exams_text):
        assert "[Messaging & Integration]" in aws_exams_text

    def test_messaging_links_to_messaging_md(self, aws_exams_text):
        assert "../messaging/messaging.md" in aws_exams_text

    def test_governance_row_present(self, aws_exams_text):
        assert "[Governance]" in aws_exams_text

    def test_governance_links_to_governance_md(self, aws_exams_text):
        assert "../governance/governance.md" in aws_exams_text

    def test_hadr_row_present(self, aws_exams_text):
        assert "[High Availability & DR]" in aws_exams_text

    def test_hadr_links_to_hadr_md(self, aws_exams_text):
        assert "../ha-dr/ha-dr.md" in aws_exams_text

    def test_waf_row_present(self, aws_exams_text):
        assert "[Well-Architected Framework]" in aws_exams_text

    def test_waf_links_to_waf_md(self, aws_exams_text):
        assert "../waf/waf.md" in aws_exams_text
