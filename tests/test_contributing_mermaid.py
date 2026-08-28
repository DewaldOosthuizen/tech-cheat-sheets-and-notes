"""Tests for CONTRIBUTING.md Mermaid Diagrams subsection (issue #127).

Verifies that:
  - CONTRIBUTING.md §9 contains a "### Mermaid Diagrams" subsection
  - The directive-selection table is present with all three rows
  - Heading convention and placement guidance are documented
  - Local validation command is documented
  - TOC has a Mermaid Diagrams entry
"""

from __future__ import annotations

from pathlib import Path

from conftest import REPO_ROOT

CONTRIBUTING = REPO_ROOT / "CONTRIBUTING.md"


class TestContributingMermaidDiagrams:
    """Verify CONTRIBUTING.md §9 Mermaid Diagrams subsection."""

    def _contributing_text(self) -> str:
        return CONTRIBUTING.read_text(encoding="utf-8")

    def test_mermaid_diagrams_subsection_heading_present(self) -> None:
        text = self._contributing_text()
        assert "### Mermaid Diagrams" in text, (
            "CONTRIBUTING.md missing '### Mermaid Diagrams' subsection heading"
        )

    def test_directive_selection_table_present(self) -> None:
        text = self._contributing_text()
        assert "| Purpose                    | Directive       |" in text, (
            "CONTRIBUTING.md missing directive-selection table header"
        )
        assert "| Decision flows (if/else)   | `flowchart TD`  |" in text, (
            "CONTRIBUTING.md missing flowchart TD row"
        )
        assert "| Hierarchy / ecosystem maps | `graph TD`      |" in text, (
            "CONTRIBUTING.md missing graph TD row"
        )
        assert "| Connectivity / network     | `graph LR`      |" in text, (
            "CONTRIBUTING.md missing graph LR row"
        )

    def test_heading_convention_documented(self) -> None:
        text = self._contributing_text()
        assert "### Decision Flow" in text, (
            "CONTRIBUTING.md missing heading convention (### Decision Flow)"
        )
        assert "immediately after the relevant table" in text, (
            "CONTRIBUTING.md missing heading placement guidance"
        )

    def test_local_validation_command_documented(self) -> None:
        text = self._contributing_text()
        assert "python3 scripts/validate_mermaid.py docs/AZ-305_CheatSheet.md" in text, (
            "CONTRIBUTING.md missing per-file validation command"
        )

    def test_mermaid_diagrams_subsection_is_in_section_9(self) -> None:
        """The new subsection must appear before the --- separator that ends §9 (before §10)."""
        text = self._contributing_text()
        section_9_mermaid_idx = text.find("### Mermaid Diagrams")
        section_separator_idx = text.find("\n---\n\n## 10. Deprecation")
        assert section_9_mermaid_idx > 0, "Mermaid Diagrams subsection not found"
        assert section_separator_idx > 0, "§9/§10 separator not found"
        assert section_9_mermaid_idx < section_separator_idx, (
            "Mermaid Diagrams subsection must appear before the §9/§10 separator"
        )

    def test_toc_has_mermaid_diagrams_entry(self) -> None:
        text = self._contributing_text()
        assert "- [Mermaid Diagrams](#mermaid-diagrams)" in text, (
            "Table of Contents missing Mermaid Diagrams entry under §9"
        )
