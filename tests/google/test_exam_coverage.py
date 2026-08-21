"""Tests for Google Cloud exam coverage pages.

Verifies that:
  - docs/index.md contains prose link to Google Cloud Exam Track Index
  - docs/google/files/exams/exams.md exists with correct Google exam coverage matrix
  - mkdocs.yml registers the Google Exam Coverage page
"""

import pytest
from conftest import REPO_ROOT

INDEX_MD = REPO_ROOT / "docs" / "index.md"
GOOGLE_EXAMS_MD = REPO_ROOT / "docs" / "google" / "files" / "exams" / "exams.md"
MKDOCS_YML = REPO_ROOT / "mkdocs.yml"


@pytest.fixture(scope="module")
def index_text():
    return INDEX_MD.read_text()


@pytest.fixture(scope="module")
def google_exams_text():
    return GOOGLE_EXAMS_MD.read_text()


@pytest.fixture(scope="module")
def mkdocs_text():
    return MKDOCS_YML.read_text()


# ── index.md ───────────────────────────────────────────────────────────────────


class TestIndexGoogleInlineTableRemoved:
    """index.md must not contain the inline Google exam coverage table."""

    def test_google_inline_table_header_absent(self, index_text):
        assert "| Cloud Digital Leader |" not in index_text

    def test_google_prose_link_present(self, index_text):
        assert "See the [Google Cloud Exam Track Index](google/files/exams/exams.md)" in index_text


# ── google/files/exams/exams.md ────────────────────────────────────────────────


class TestGoogleExamsFileExists:
    """docs/google/files/exams/exams.md must exist."""

    def test_google_exams_file_exists(self):
        assert GOOGLE_EXAMS_MD.exists(), "docs/google/files/exams/exams.md does not exist"


class TestGoogleExamsFileContent:
    """docs/google/files/exams/exams.md must contain the correct exam coverage matrix."""

    def test_heading_present(self, google_exams_text):
        assert "# Exam Track Index" in google_exams_text

    def test_table_header_cdl(self, google_exams_text):
        assert "Cloud Digital Leader" in google_exams_text

    def test_table_header_ace(self, google_exams_text):
        assert "Associate Cloud Engineer" in google_exams_text

    def test_table_header_pca(self, google_exams_text):
        assert "Professional Cloud Architect" in google_exams_text

    def test_table_header_pde(self, google_exams_text):
        assert "Professional Data Engineer" in google_exams_text

    def test_table_header_pdoe(self, google_exams_text):
        assert "Professional DevOps Engineer" in google_exams_text

    def test_abbreviations_row_present(self, google_exams_text):
        assert "[Abbreviations]" in google_exams_text

    def test_compute_row_present(self, google_exams_text):
        assert "[Compute]" in google_exams_text

    def test_networking_row_present(self, google_exams_text):
        assert "[Networking]" in google_exams_text

    def test_storage_row_present(self, google_exams_text):
        assert "[Storage]" in google_exams_text

    def test_identity_row_present(self, google_exams_text):
        assert "[Identity & Access]" in google_exams_text

    def test_security_row_present(self, google_exams_text):
        assert "[Security]" in google_exams_text

    def test_monitoring_row_present(self, google_exams_text):
        assert "Monitoring" in google_exams_text

    def test_messaging_row_present(self, google_exams_text):
        assert "Messaging" in google_exams_text

    def test_governance_row_present(self, google_exams_text):
        assert "[Governance]" in google_exams_text

    def test_ha_dr_row_present(self, google_exams_text):
        assert "High Availability" in google_exams_text

    def test_waf_row_present(self, google_exams_text):
        assert "Well-Architected" in google_exams_text

    def test_twelve_data_rows(self, google_exams_text):
        # 11 domain rows + 1 abbreviations row = 12 total data rows
        data_rows = [
            line
            for line in google_exams_text.splitlines()
            if line.strip().startswith("|") and "---" not in line and "Section" not in line
        ]
        assert len(data_rows) == 12, f"Expected 12 data rows, got {len(data_rows)}"

    def test_table_rows_use_single_pipe_prefix(self, google_exams_text):
        """Every table row must begin with exactly one pipe, not || or |||."""
        for line in google_exams_text.splitlines():
            stripped = line.strip()
            if stripped.startswith("|") and "---" not in stripped and "Section" not in stripped:
                # Data rows must start with exactly "| " (pipe + space)
                assert stripped.startswith("| "), (
                    f"Row does not use single-pipe prefix: {stripped!r}"
                )


# ── mkdocs.yml ─────────────────────────────────────────────────────────────────


class TestMkdocsGoogleExamCoverage:
    """mkdocs.yml must register google/files/exams/exams.md under the Google nav section."""

    def test_google_exam_coverage_entry_present(self, mkdocs_text):
        assert "Exam Coverage: google/files/exams/exams.md" in mkdocs_text
