"""Stale PyMdown snippet reference detection in documentation content files.

Verifies that every ``--8<-- "path"`` directive embedded in the documentation
content files under ``docs/<provider>/files/`` resolves to an existing file,
resolved relative to ``docs/`` exactly as ``pymdownx.snippets`` is configured
in ``mkdocs.yml`` (see conftest ``REPO_ROOT`` / snippet ``base_path``).

This catches renames/deletions of referenced diagrams (or any other snippet
target) during the test phase instead of only during ``mkdocs build --strict``.

The ``_SNIPPET_RE`` regex is the authoritative source defined in
``scripts/validate_mermaid.py``; it is imported here rather than redefined
(per ``tests/test_shared_test_infrastructure.py`` contract).
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
from conftest import _SNIPPET_RE, REPO_ROOT

SCRIPTS_DIR = str(REPO_ROOT / "scripts")
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

DOCS_DIR = REPO_ROOT / "docs"
SNIPPET_BASE = DOCS_DIR  # pymdownx.snippets base_path in mkdocs.yml

# Paths (relative to REPO_ROOT) that are intentionally broken/placeholder
# references and must not be asserted against. Each entry carries a reason.
_EXCLUDED_PLACEHOLDERS: set[str] = {
    # programming/python/README.md references a diagram that does not exist yet
    # (planned future content); intentionally left as a placeholder.
    "docs/programming/python/README.md",
}


def _content_files() -> list[Path]:
    """Discover all Markdown content files under docs/<provider>/files/."""
    result: list[Path] = []
    for md_path in DOCS_DIR.rglob("*.md"):
        if "diagrams" in md_path.parts:
            continue
        if "overrides" in md_path.parts:
            continue
        rel = md_path.relative_to(REPO_ROOT)
        if str(rel) in _EXCLUDED_PLACEHOLDERS:
            continue
        # Only content files under a files/ directory.
        if "files" not in md_path.parts:
            continue
        result.append(md_path)
    return sorted(result)


def _extract_snippet_paths(text: str) -> list[str]:
    """Extract all ``--8<-- "path"`` directive targets using ``_SNIPPET_RE``."""
    return [m.group(1) for m in _SNIPPET_RE.finditer(text)]


@pytest.mark.parametrize(
    "content_file",
    _content_files(),
    ids=lambda p: str(p.relative_to(REPO_ROOT)),
)
def test_content_file_snippet_paths_exist(content_file: Path) -> None:
    text = content_file.read_text(encoding="utf-8")
    snippet_paths = _extract_snippet_paths(text)
    if not snippet_paths:
        return
    missing: list[str] = []
    for rel in snippet_paths:
        target = (SNIPPET_BASE / rel).resolve()
        if not target.exists():
            missing.append(rel)
    assert not missing, (
        f"{content_file.relative_to(REPO_ROOT)} references {len(missing)} "
        f"snippet path(s) that do not exist: " + ", ".join(missing)
    )
