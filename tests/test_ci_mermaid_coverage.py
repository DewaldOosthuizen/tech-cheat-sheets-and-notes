"""Tests for Makefile and CI Mermaid coverage (issue #224).

Verifies that:
  - Makefile's MMD_FILES_VALIDATE delegates to scripts/validate_mermaid.py
  - Makefile's mermaid-check target invokes validate_mermaid.py without inline file lists
  - CI 'Validate Mermaid diagrams' step delegates discovery to validate_mermaid.py
"""

from __future__ import annotations

import re

from conftest import REPO_ROOT

MAKEFILE = REPO_ROOT / "Makefile"
RELEASE_YML = REPO_ROOT / ".github" / "workflows" / "release.yml"


class TestMakefileMermaidCoverage:
    """MMD_FILES_VALIDATE must be derived from validate_mermaid.py discovery."""

    def test_mmd_files_validate_uses_script_discovery(self) -> None:
        content = MAKEFILE.read_text()
        m = re.search(
            r"MMD_FILES_VALIDATE\s*:=\s*\$\(shell "
            r"(\$\(PY\) scripts/validate_mermaid\.py --discover-mmd)\)",
            content,
        )
        assert m, (
            "MMD_FILES_VALIDATE must be derived from scripts/validate_mermaid.py --discover-mmd"
        )

    def test_md_files_validate_uses_script_discovery(self) -> None:
        content = MAKEFILE.read_text()
        m = re.search(
            r"MD_FILES_VALIDATE\s*:=\s*\$\(shell "
            r"(\$\(PY\) scripts/validate_mermaid\.py --discover-md)\)",
            content,
        )
        assert m, "MD_FILES_VALIDATE must be derived from scripts/validate_mermaid.py --discover-md"

    def test_mermaid_check_invokes_validate_mermaid_without_file_lists(self) -> None:
        content = MAKEFILE.read_text()
        m = re.search(r"mermaid-check:.*?validate_mermaid\.py ([^\n]*)", content, re.S)
        assert m, "Could not locate validate_mermaid.py invocation in mermaid-check target"
        invocation_args = m.group(1)
        assert "$(MD_FILES_VALIDATE)" not in invocation_args, (
            "mermaid-check must not pass $(MD_FILES_VALIDATE) — script self-discovers"
        )
        assert "$(MMD_FILES_VALIDATE)" not in invocation_args, (
            "mermaid-check must not pass $(MMD_FILES_VALIDATE) — script self-discovers"
        )


class TestCiMermaidCoverage:
    """CI 'Validate Mermaid diagrams' step must delegate discovery to validate_mermaid.py."""

    def _step_block(self) -> str:
        content = RELEASE_YML.read_text()
        m = re.search(
            r"Validate Mermaid diagrams.*?(?=\n\s*- name:|\Z)",
            content,
            re.S,
        )
        assert m, "Could not locate 'Validate Mermaid diagrams' step in release.yml"
        return m.group(0)

    def test_md_find_covers_all_docs(self) -> None:
        block = self._step_block()
        assert "python scripts/validate_mermaid.py" in block, (
            "CI mermaid-check must invoke validate_mermaid.py"
        )
        assert "find docs" not in block, (
            "CI mermaid-check must not inline find commands — "
            "discovery moved to validate_mermaid.py"
        )

    def test_mmd_find_covers_all_docs(self) -> None:
        block = self._step_block()
        assert "python scripts/validate_mermaid.py" in block, (
            "CI mermaid-check must invoke validate_mermaid.py"
        )
        assert "find docs" not in block, (
            "CI mermaid-check must not inline find commands — "
            "discovery moved to validate_mermaid.py"
        )
