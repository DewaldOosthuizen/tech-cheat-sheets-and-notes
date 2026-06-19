"""Tests for shared pytest infrastructure conventions."""

from __future__ import annotations

import inspect
from pathlib import Path

import conftest

TEST_MERMAID_VALIDATION = Path(__file__).parent / "test_mermaid_validation.py"


class TestSharedScriptsBootstrap:
    """Suite-wide bootstrap belongs in tests/conftest.py."""

    def test_conftest_bootstraps_validate_mermaid_imports(self):
        src = inspect.getsource(conftest)
        local_bootstrap_literal = 'sys.path.insert(0, ' + '"scripts")'
        assert "import sys" in src
        assert 'SCRIPTS_DIR = str(REPO_ROOT / "scripts")' in src
        assert "if SCRIPTS_DIR not in sys.path:" in src
        assert "sys.path.insert(0, SCRIPTS_DIR)" in src
        assert local_bootstrap_literal in src


class TestMermaidValidationBootstrapOwnership:
    """validate_mermaid tests must rely on shared bootstrap only."""

    def test_mermaid_validation_has_no_local_scripts_bootstrap(self):
        src = TEST_MERMAID_VALIDATION.read_text(encoding="utf-8")
        local_bootstrap_literal = 'sys.path.insert(0, ' + '"scripts")'
        assert local_bootstrap_literal not in src
        assert "\nimport sys\n" not in src
