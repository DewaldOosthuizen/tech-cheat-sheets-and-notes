"""Content contract tests for AWS storage domain page."""

from __future__ import annotations

import pytest
from conftest import REPO_ROOT, expand_snippets

CONTENT_MD = REPO_ROOT / "docs" / "aws" / "files" / "storage" / "storage.md"


@pytest.fixture(scope="module")
def text():
    return expand_snippets(CONTENT_MD.read_text())


class TestAwsStorageContent:
    def test_heading(self, text):
        assert "# STORAGE" in text

    def test_table_header(self, text):
        assert "| Service |" in text

    def test_exam_tip(self, text):
        assert "> **Exam tip:**" in text


class TestDiagramPresence:
    def test_mermaid_diagram_present(self, text):
        assert "```mermaid" in text

    def test_diagram_directive_present(self):
        assert ".mmd" in CONTENT_MD.read_text()
