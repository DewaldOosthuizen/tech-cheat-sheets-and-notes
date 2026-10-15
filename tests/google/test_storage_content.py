"""Content contract tests for Google storage domain page."""

from __future__ import annotations

import pytest
from conftest import REPO_ROOT, expand_snippets

CONTENT_MD = REPO_ROOT / "docs" / "google" / "files" / "storage" / "storage.md"


@pytest.fixture(scope="module")
def text():
    return expand_snippets(CONTENT_MD.read_text())


class TestGoogleStorageContent:
    def test_heading(self, text):
        assert "# STORAGE" in text

    def test_table_header(self, text):
        assert "| Service |" in text or "| Class |" in text or "**Cloud Storage**" in text

    def test_exam_tip(self, text):
        assert "> **Exam tip:**" in text
