"""Tests for the issue #367 module split.

The Mermaid validator is split across three modules with one responsibility
each:

  - ``mermaid_discovery`` — file discovery and snippet extraction
  - ``mermaid_validation`` — mmdc subprocess invocation
  - ``validate_mermaid`` — CLI orchestration, re-exporting the historical
    public surface of the pre-split module

These tests pin the boundaries and the backward-compatible re-exports, so the
split cannot silently drift back into a single module or drop a name that the
rest of the suite still imports.
"""

from __future__ import annotations

import ast
import inspect

import pytest

import mermaid_discovery
import mermaid_validation
import validate_mermaid


class TestModuleBoundaries:
    """Each responsibility lives in exactly one owning module."""

    @staticmethod
    def _module_imports(module) -> set[str]:
        """Return the module-level dotted names imported by *module*."""
        tree = ast.parse(inspect.getsource(module))
        names: set[str] = set()
        for node in tree.body:
            if isinstance(node, ast.Import):
                names.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                names.add(node.module)
        return names

    def test_discovery_module_imports_only_discovery_dependencies(self):
        """mermaid_discovery must not pull in the mmdc machinery."""
        assert self._module_imports(mermaid_discovery) == {"re", "pathlib"}

    def test_validation_module_imports_only_validation_dependencies(self):
        """mermaid_validation owns the subprocess/env machinery."""
        assert self._module_imports(mermaid_validation) == {
            "os",
            "subprocess",
            "sys",
            "tempfile",
            "time",
            "pathlib",
        }

    def test_wrapper_imports_only_orchestration_dependencies(self):
        """The CLI wrapper must not import the mmdc machinery itself."""
        assert self._module_imports(validate_mermaid) == {
            "argparse",
            "shutil",
            "sys",
            "pathlib",
            "mermaid_discovery",
            "mermaid_validation",
        }

    def test_discovery_owns_snippet_expansion(self):
        assert mermaid_discovery.expand_snippets is not validate_mermaid.expand_snippets
        assert mermaid_discovery.expand_snippets.__module__ == "mermaid_discovery"

    def test_validation_owns_mmdc_invocation(self):
        assert mermaid_validation._run_mmdc.__module__ == "mermaid_validation"
        assert mermaid_validation.validate_block.__module__ == "mermaid_validation"

    def test_wrapper_owns_orchestration(self):
        for name in ("run", "main", "parse_args"):
            assert getattr(validate_mermaid, name).__module__ == "validate_mermaid"


class TestReExportSurface:
    """The wrapper re-exports the complete pre-split public surface."""

    def test_all_declares_fourteen_names(self):
        assert validate_mermaid.__all__ == [
            "MIN_VALID_SVG_SIZE_BYTES",
            "PUPPETEER_CONFIG",
            "_FENCE_SNIPPET_RE",
            "_MAX_EXPAND_DEPTH",
            "_SNIPPET_RE",
            "_expand_snippet",
            "_extract_from_text",
            "_repo_root",
            "_run_mmdc",
            "_validate_mmd_file",
            "discover_files",
            "expand_snippets",
            "extract_mermaid_blocks",
            "validate_block",
        ]

    def test_reexported_names_resolve(self):
        for name in validate_mermaid.__all__:
            assert hasattr(validate_mermaid, name), f"validate_mermaid is missing {name}"

    @pytest.mark.parametrize(
        "name",
        [
            "discover_files",
            "expand_snippets",
            "extract_mermaid_blocks",
            "_repo_root",
            "_FENCE_SNIPPET_RE",
            "_SNIPPET_RE",
            "_MAX_EXPAND_DEPTH",
            "_extract_from_text",
            "_expand_snippet",
        ],
    )
    def test_discovery_names_are_mermaid_discovery_objects(self, name):
        assert getattr(validate_mermaid, name) is getattr(mermaid_discovery, name)

    @pytest.mark.parametrize(
        "name",
        [
            "validate_block",
            "_run_mmdc",
            "_validate_mmd_file",
            "MIN_VALID_SVG_SIZE_BYTES",
            "PUPPETEER_CONFIG",
        ],
    )
    def test_validation_names_are_mermaid_validation_objects(self, name):
        assert getattr(validate_mermaid, name) is getattr(mermaid_validation, name)

    def test_pinned_discovery_names_resolve_to_expected_values(self):
        assert validate_mermaid._MAX_EXPAND_DEPTH == mermaid_discovery._MAX_EXPAND_DEPTH == 10
        assert validate_mermaid.MIN_VALID_SVG_SIZE_BYTES == mermaid_validation.MIN_VALID_SVG_SIZE_BYTES


class TestOwningModuleLookupRule:
    """Patch targets must be the module where the calling code looks a name up."""

    def test_run_resolves_discovery_names_in_wrapper_globals(self):
        source = inspect.getsource(validate_mermaid.run)
        assert "_repo_root" in source
        assert "extract_mermaid_blocks" in source
        assert "_validate_mmd_file" in source

    def test_main_resolves_discovery_in_wrapper_globals(self):
        assert "discover_files" in inspect.getsource(validate_mermaid.main)

    def test_run_mmdc_resolves_its_dependencies_in_validation_module(self):
        source = inspect.getsource(mermaid_validation._run_mmdc)
        assert "subprocess.run" in source
        assert "PUPPETEER_CONFIG" in source
        assert "MIN_VALID_SVG_SIZE_BYTES" in source

    def test_extract_mermaid_blocks_resolves_helpers_in_discovery_module(self):
        source = inspect.getsource(mermaid_discovery.extract_mermaid_blocks)
        assert "expand_snippets" in source
        assert "_extract_from_text" in source
        assert "_expand_snippet" in source
