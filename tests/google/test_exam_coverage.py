"""Tests for Google Cloud exam coverage pages.

Verifies that:
  - docs/index.md links to the Google Cloud Exam Track Index
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
        assert "[Google Cloud Exam Track Index](google/index.md)" in index_text

    def test_google_prose_link_certification_text(self, index_text):
        assert "for full certification coverage" in index_text

    def test_google_exam_track_index_link(self, index_text):
        assert "google/index.md" in index_text
