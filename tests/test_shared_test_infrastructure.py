"""Tests for shared pytest infrastructure conventions."""

from __future__ import annotations

import importlib
import inspect
import sys
from pathlib import Path

import conftest
import validate_mermaid

TEST_MERMAID_VALIDATION = Path(__file__).parent / "test_mermaid_validation.py"


class TestSharedScriptsBootstrap:
    """Suite-wide bootstrap belongs in tests/conftest.py."""

    def test_validate_mermaid_imports_via_shared_bootstrap(self):
        scripts_file = (conftest.REPO_ROOT / "scripts" / "validate_mermaid.py").resolve()
        assert Path(validate_mermaid.__file__).resolve() == scripts_file

    def test_conftest_bootstrap_uses_absolute_scripts_dir_once(self):
        scripts_dir = str(conftest.REPO_ROOT / "scripts")
        importlib.reload(conftest)
        assert Path(scripts_dir).is_absolute()
        assert scripts_dir in sys.path
        assert sys.path.count(scripts_dir) == 1

    def test_conftest_does_not_keep_obsolete_cwd_relative_bootstrap_literal(self):
        src = inspect.getsource(conftest)
        assert 'sys.path.insert(0, "scripts")' not in src


class TestMermaidValidationBootstrapOwnership:
    """validate_mermaid tests must rely on shared bootstrap only."""

    def test_mermaid_validation_has_no_local_scripts_bootstrap(self):
        src = TEST_MERMAID_VALIDATION.read_text(encoding="utf-8")
        assert 'sys.path.insert(0, "scripts")' not in src
        assert "\nimport sys\n" not in src
