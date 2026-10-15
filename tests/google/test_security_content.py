"""Content contract tests for Google security domain page."""

from __future__ import annotations

import pytest
from conftest import REPO_ROOT, expand_snippets

CONTENT_MD = REPO_ROOT / "docs" / "google" / "files" / "security" / "security.md"


@pytest.fixture(scope="module")
def text():
    return expand_snippets(CONTENT_MD.read_text())


class TestGoogleSecurityContent:
    def test_heading(self, text):
        assert "# SECURITY" in text

    def test_table_header(self, text):
        assert "| Service |" in text

    def test_exam_tip(self, text):
        assert "> **Exam tip:**" in text
