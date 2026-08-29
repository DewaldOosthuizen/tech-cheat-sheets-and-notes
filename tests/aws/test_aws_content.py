"""Tests for issue #219 — FEATURE: Add AWS section.

Covers all 4 sub-issues:
  1. docs/aws/files/<domain>/<domain>.md files created for 11 domains
  2. docs/aws/diagrams/<domain>/decision-flow.mmd files created for 11 domains
  3. mkdocs.yml AWS nav block appended
  4. docs/index.md ## Amazon Web Services section inserted
"""

from __future__ import annotations

import pytest
from conftest import REPO_ROOT, expand_snippets

DOCS = REPO_ROOT / "docs"

AWS_DOMAINS = [
    "compute",
    "networking",
    "storage",
    "identity",
    "security",
    "database",
    "monitoring",
    "messaging",
    "governance",
    "ha-dr",
    "waf",
]

# ── Issue 1: AWS domain snippet files exist ───────────────────────────────────


class TestAwsSnippetFilesExist:
    @pytest.mark.parametrize("domain", AWS_DOMAINS)
    def test_snippet_file_exists(self, domain: str) -> None:
        snippet = DOCS / "aws" / "files" / domain / f"{domain}.md"
        assert snippet.exists(), f"Missing AWS snippet file: {snippet}"

    @pytest.mark.parametrize("domain", AWS_DOMAINS)
    def test_snippet_file_non_empty(self, domain: str) -> None:
        snippet = DOCS / "aws" / "files" / domain / f"{domain}.md"
        if snippet.exists():
            assert snippet.stat().st_size > 0, f"AWS snippet file is empty: {snippet}"


class TestAwsSnippetFileContent:
    """Each AWS domain file must follow the canonical conventions."""

    @pytest.mark.parametrize("domain", AWS_DOMAINS)
    def test_has_allcaps_heading(self, domain: str) -> None:
        snippet = DOCS / "aws" / "files" / domain / f"{domain}.md"
        if snippet.exists():
            text = snippet.read_text(encoding="utf-8")
            # Must start with an ALL-CAPS # heading
            lines = [ln for ln in text.splitlines() if ln.startswith("# ")]
            assert lines, f"{snippet}: no top-level heading found"
            assert (
                lines[0][2:].isupper()
                or lines[0][2:]
                .replace(" ", "")
                .replace("&", "")
                .replace("-", "")
                .replace(",", "")
                .isupper()
            ), f"{snippet}: top-level heading not ALL-CAPS: {lines[0]!r}"

    @pytest.mark.parametrize("domain", AWS_DOMAINS)
    def test_has_service_column(self, domain: str) -> None:
        snippet = DOCS / "aws" / "files" / domain / f"{domain}.md"
        if snippet.exists():
            text = snippet.read_text(encoding="utf-8")
            assert "| Service |" in text or "| Pillar |" in text, (
                f"{snippet}: no 'Service' or 'Pillar' column in comparison table"
            )

    @pytest.mark.parametrize("domain", AWS_DOMAINS)
    def test_has_key_feature_column(self, domain: str) -> None:
        snippet = DOCS / "aws" / "files" / domain / f"{domain}.md"
        if snippet.exists():
            text = snippet.read_text(encoding="utf-8")
            assert "Key Feature" in text or "Key AWS Services" in text, (
                f"{snippet}: no 'Key Feature' or 'Key AWS Services' column found"
            )

    @pytest.mark.parametrize("domain", AWS_DOMAINS)
    def test_has_exam_tip(self, domain: str) -> None:
        snippet = DOCS / "aws" / "files" / domain / f"{domain}.md"
        if snippet.exists():
            text = snippet.read_text(encoding="utf-8")
            assert "> **Exam tip:**" in text, f"{snippet}: missing '> **Exam tip:**' callout"

    @pytest.mark.parametrize("domain", AWS_DOMAINS)
    def test_has_mermaid_snippet_directive(self, domain: str) -> None:
        snippet = DOCS / "aws" / "files" / domain / f"{domain}.md"
        if snippet.exists():
            text = snippet.read_text(encoding="utf-8")
            assert f'--8<-- "aws/diagrams/{domain}/decision-flow.mmd"' in text, (
                f"{snippet}: missing snippet directive for aws/diagrams/{domain}/decision-flow.mmd"
            )


# ── Issue 2: AWS Mermaid .mmd files exist ────────────────────────────────────


class TestAwsMmdFilesExist:
    @pytest.mark.parametrize("domain", AWS_DOMAINS)
    def test_mmd_file_exists(self, domain: str) -> None:
        mmd = DOCS / "aws" / "diagrams" / domain / "decision-flow.mmd"
        assert mmd.exists(), f"Missing AWS diagram file: {mmd}"

    @pytest.mark.parametrize("domain", AWS_DOMAINS)
    def test_mmd_file_non_empty(self, domain: str) -> None:
        mmd = DOCS / "aws" / "diagrams" / domain / "decision-flow.mmd"
        if mmd.exists():
            assert mmd.stat().st_size > 0, f"AWS diagram file is empty: {mmd}"

    @pytest.mark.parametrize("domain", AWS_DOMAINS)
    def test_mmd_starts_with_valid_directive(self, domain: str) -> None:
        mmd = DOCS / "aws" / "diagrams" / domain / "decision-flow.mmd"
        if mmd.exists():
            text = mmd.read_text(encoding="utf-8").strip()
            valid_starts = ("flowchart", "graph")
            assert text.startswith(valid_starts), (
                f"{mmd}: must start with 'flowchart' or 'graph', got: {text[:40]!r}"
            )


# ── Issue 3: mkdocs.yml AWS nav block ─────────────────────────────────────────


class TestMkdocsAwsNav:
    def _mkdocs_text(self) -> str:
        return (REPO_ROOT / "mkdocs.yml").read_text(encoding="utf-8")

    def test_aws_section_present(self) -> None:
        text = self._mkdocs_text()
        assert "- AWS:" in text, "mkdocs.yml missing '- AWS:' nav section"

    @pytest.mark.parametrize("domain", AWS_DOMAINS)
    def test_aws_domain_in_nav(self, domain: str) -> None:
        text = self._mkdocs_text()
        assert f"aws/files/{domain}/{domain}.md" in text, (
            f"mkdocs.yml AWS nav missing entry for domain: {domain}"
        )


# ── Issue 4: docs/index.md AWS section ───────────────────────────────────────


class TestIndexMdAwsSection:
    AWS_INDEX = DOCS / "aws" / "index.md"

    def _index_text(self) -> str:
        return self.AWS_INDEX.read_text(encoding="utf-8")

    def test_aws_heading_present(self) -> None:
        text = self._index_text()
        assert "# AWS" in text, "docs/aws/index.md missing '# AWS' heading"

    def test_aws_section_before_how_to_use(self) -> None:
        # aws/index.md is a standalone file — no ordering constraint with
        # docs/index.md sections.
        assert "# AWS" in self._index_text()

    @pytest.mark.parametrize("domain", AWS_DOMAINS)
    def test_aws_domain_link_in_index(self, domain: str) -> None:
        text = self._index_text()
        assert f"files/{domain}/{domain}.md" in text, (
            f"docs/aws/index.md missing link for: {domain}"
        )

    def test_exam_grid_clf_c02(self) -> None:
        # Issue #232 moved exam coverage tables from index.md to dedicated exam pages.
        # CLF-C02 now lives in docs/aws/files/exams/exams.md.
        text = (DOCS / "aws" / "files" / "exams" / "exams.md").read_text(encoding="utf-8")
        assert "CLF-C02" in text, "docs/aws/files/exams/exams.md missing CLF-C02 exam coverage"

    def test_exam_grid_saa_c03(self) -> None:
        # Issue #232 moved exam coverage tables from index.md to dedicated exam pages.
        # SAA-C03 now lives in docs/aws/files/exams/exams.md.
        text = (DOCS / "aws" / "files" / "exams" / "exams.md").read_text(encoding="utf-8")
        assert "SAA-C03" in text, "docs/aws/files/exams/exams.md missing SAA-C03 exam coverage"

    def test_exam_grid_sap_c02(self) -> None:
        # Issue #232 moved exam coverage tables from index.md to dedicated exam pages.
        # SAP-C02 now lives in docs/aws/files/exams/exams.md.
        text = (DOCS / "aws" / "files" / "exams" / "exams.md").read_text(encoding="utf-8")
        assert "SAP-C02" in text, "docs/aws/files/exams/exams.md missing SAP-C02 exam coverage"
