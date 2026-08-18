"""Tests for issue #224: Wire up MMD_FILES_VALIDATE in Makefile and extend
CI mermaid-check job to cover AWS diagrams.

Verifies that:
  - Makefile's MMD_FILES_VALIDATE find covers both docs/azure/diagrams and
    docs/aws/diagrams
  - Makefile's mermaid-check target forwards $(MMD_FILES_VALIDATE) to
    scripts/validate_mermaid.py alongside $(MD_FILES_VALIDATE)
  - .github/workflows/lint.yml "Validate Mermaid diagrams" step's find
    invocations cover both docs/azure/{files,diagrams} and
    docs/aws/{files,diagrams}
"""

import re

from conftest import REPO_ROOT

MAKEFILE = REPO_ROOT / "Makefile"
LINT_YML = REPO_ROOT / ".github" / "workflows" / "lint.yml"


class TestMakefileMmdFilesValidate:
    """MMD_FILES_VALIDATE must cover azure and aws diagrams, and be wired in."""

    def test_mmd_files_validate_covers_aws_diagrams(self):
        content = MAKEFILE.read_text()
        m = re.search(r"MMD_FILES_VALIDATE\s*:=\s*\$\(shell find ([^)]*?)-name '\*\.mmd'", content)
        assert m, "Could not locate MMD_FILES_VALIDATE definition in Makefile"
        find_paths = m.group(1)
        assert "docs/azure/diagrams" in find_paths
        assert "docs/aws/diagrams" in find_paths

    def test_mermaid_check_forwards_mmd_files_validate(self):
        content = MAKEFILE.read_text()
        m = re.search(r"mermaid-check:.*?validate_mermaid\.py ([^\n]*)", content, re.S)
        assert m, "Could not locate validate_mermaid.py invocation in mermaid-check target"
        invocation_args = m.group(1)
        assert "$(MD_FILES_VALIDATE)" in invocation_args
        assert "$(MMD_FILES_VALIDATE)" in invocation_args


class TestCiMermaidCheckAwsCoverage:
    """CI 'Validate Mermaid diagrams' step must include docs/aws paths."""

    def _step_block(self) -> str:
        content = LINT_YML.read_text()
        m = re.search(
            r"Validate Mermaid diagrams.*?(?=\n\s*- name:|\Z)",
            content,
            re.S,
        )
        assert m, "Could not locate 'Validate Mermaid diagrams' step in lint.yml"
        return m.group(0)

    def test_md_find_covers_aws_files(self):
        block = self._step_block()
        assert "docs/azure/files" in block
        assert "docs/aws/files" in block

    def test_mmd_find_covers_aws_diagrams(self):
        block = self._step_block()
        assert "docs/azure/diagrams" in block
        assert "docs/aws/diagrams" in block
