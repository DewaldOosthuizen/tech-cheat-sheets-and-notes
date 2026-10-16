"""Shared pytest fixtures and helpers for the tech-cheat-sheets-and-notes  test suite."""

from __future__ import annotations

import sys
from pathlib import Path

# The PyMdown Snippets base_path as configured in mkdocs.yml.
# Snippet paths inside cheat-sheet files are relative to docs/, e.g.
#   --8<-- "azure/diagrams/networking/decision-flow.mmd"
# resolves to  <repo>/docs/azure/diagrams/networking/decision-flow.mmd
REPO_ROOT = Path(__file__).parent.parent
SCRIPTS_DIR = str(REPO_ROOT / "scripts")

if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

# Re-export the canonical snippet expansion implementation from scripts/
# so test files can use `from conftest import expand_snippets` without
# importing validate_mermaid directly.
from validate_mermaid import _MAX_EXPAND_DEPTH, _SNIPPET_RE, expand_snippets  # noqa: E402,F401
