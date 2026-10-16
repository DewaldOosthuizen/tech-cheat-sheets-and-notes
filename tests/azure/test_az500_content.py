"""Tests for issue #134 - FEATURE: Expand cheat sheet with AZ-500 Security Engineer content."""

from conftest import REPO_ROOT, expand_snippets

SNIPPETS_DIR = REPO_ROOT / "docs" / "azure" / "files"


def _content():
    """Concatenate all expanded snippet files into a single string for assertion."""
    parts = []
    for snippet in sorted(SNIPPETS_DIR.glob("*/*.md")):
        parts.append(expand_snippets(snippet.read_text(encoding="utf-8")))
    return "\n".join(parts)


class TestAZ500ExamTips:
    """Verify at least 5 AZ-500 exam tip callouts exist across all domain pages."""

    def test_at_least_five_az500_exam_tips(self):
        count = _content().count("> **Exam tip (AZ-500):**")
        assert count >= 5, (
            f"Expected at least 5 occurrences of '> **Exam tip (AZ-500):**', found {count}"
        )
