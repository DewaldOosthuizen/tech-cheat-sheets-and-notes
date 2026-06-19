"""Shared pytest fixtures and helpers for the tech-cheat-sheets-and-notes  test suite."""

from __future__ import annotations

import re
import sys
from pathlib import Path

# The PyMdown Snippets base_path as configured in mkdocs.yml.
# Snippet paths inside cheat-sheet files are relative to docs/, e.g.
#   --8<-- "azure/diagrams/networking/decision-flow.mmd"
# resolves to  <repo>/docs/azure/diagrams/networking/decision-flow.mmd
REPO_ROOT = Path(__file__).parent.parent
SNIPPET_BASE = REPO_ROOT / "docs"
SCRIPTS_DIR = str(REPO_ROOT / "scripts")

if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

_SNIPPET_RE = re.compile(r"""--8<--\s+["']([^"']+)["']""")

_MAX_EXPAND_DEPTH = 10


def expand_snippets(text: str, base: Path = SNIPPET_BASE) -> str:
    """Replace every --8<-- "path" directive in *text* with the file's content.

    Paths are resolved relative to *base* (default: ``<repo>/docs/``), matching
    the ``base_path`` configured in mkdocs.yml for ``pymdownx.snippets``.

    Expansion is applied recursively until the text stabilises or _MAX_EXPAND_DEPTH
    passes are exhausted. This mirrors how PyMdown Snippets handles nested includes
    (e.g. a section snippet that itself contains a --8<-- directive pointing to a
    .mmd file).

    Directives that reference a missing file are left unexpanded so tests that
    assert on the directive itself are not accidentally broken.
    """

    def _replace(m: re.Match) -> str:
        rel = m.group(1)
        abs_path = (base / rel).resolve()
        if not abs_path.is_relative_to(base.resolve()):
            return m.group(0)  # reject path traversal outside docs/
        try:
            return abs_path.read_text(encoding="utf-8")
        except OSError:
            return m.group(0)  # leave unexpanded on error

    for _ in range(_MAX_EXPAND_DEPTH):
        expanded = _SNIPPET_RE.sub(_replace, text)
        if expanded == text:
            break
        text = expanded
    return text
