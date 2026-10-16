"""Stale reference detection across documentation and tests.

Verifies that file paths referenced in CONTRIBUTING.md, AGENTS.md, and README.md
actually exist in the repository. This catches the class of bug where
documentation or tests reference files that have been renamed, moved, or
deleted.

Issue #127 and the AZ-305_CheatSheet.md assertion failure (Sep 2026) are
examples of what this test prevents: documentation referenced a path that
no longer existed, and the corresponding test was not updated.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

# Match inline code references that look like repo-relative file paths:
#   `path/to/file.ext`
# Requires at least one / (directory structure) and a known file extension.
_INLINE_CODE_RE = re.compile(r"`([\w/.\-]+\.(?:md|py|yml|yaml|json|txt|mmd|html|css|scss|ts|js))`")

# Prefixes that indicate a path is NOT a repo-relative reference
_EXCLUDE_PREFIXES = (
    "http://",
    "https://",
    "github.com/",
    "www.",
    "pypi.org/",
    "files.pythonhosted.org/",
    "/tmp/",
    "/home/",
    "/var/",
    "/usr/",
    "/etc/",
    "/opt/",
    "/root/",
    "/mnt/",
    "/srv/",
    "/proc/",
    "/sys/",
    "/dev/",
    "/run/",
    "/boot/",
    "/media/",
)


def _is_repo_relative(path: str) -> bool:
    """Check if a path looks like a repo-relative file reference.

    A repo-relative path must:
    - Contain at least one / (directory structure)
    - Not start with a URL scheme or absolute path prefix
    """
    if "/" not in path:
        return False
    return not any(path.startswith(prefix) for prefix in _EXCLUDE_PREFIXES)


def _extract_repo_paths(text: str) -> list[str]:
    """Extract repo-relative file paths from inline code references."""
    paths = []
    for match in _INLINE_CODE_RE.finditer(text):
        candidate = match.group(1)
        if _is_repo_relative(candidate):
            paths.append(candidate)
    return paths


def test_contributing_referenced_paths_exist():
    """All repo-relative file paths in CONTRIBUTING.md must exist."""
    md_path = REPO_ROOT / "CONTRIBUTING.md"
    text = md_path.read_text(encoding="utf-8")
    paths = _extract_repo_paths(text)

    missing = []
    for rel_path in paths:
        full_path = REPO_ROOT / rel_path
        if not full_path.exists():
            missing.append(rel_path)

    assert not missing, (
        f"CONTRIBUTING.md references {len(missing)} path(s) that do not exist: "
        + ", ".join(missing)
        + "\nRun: git log --oneline -5 -- <path> to check if they were moved/renamed."
    )


def test_agents_referenced_paths_exist():
    """All repo-relative file paths in AGENTS.md must exist."""
    md_path = REPO_ROOT / "AGENTS.md"
    text = md_path.read_text(encoding="utf-8")
    paths = _extract_repo_paths(text)

    missing = []
    for rel_path in paths:
        full_path = REPO_ROOT / rel_path
        if not full_path.exists():
            missing.append(rel_path)

    assert not missing, (
        f"AGENTS.md references {len(missing)} path(s) that do not exist: "
        + ", ".join(missing)
        + "\nRun: git log --oneline -5 -- <path> to check if they were moved/renamed."
    )


def test_readme_referenced_paths_exist():
    """All repo-relative file paths in README.md must exist."""
    md_path = REPO_ROOT / "README.md"
    text = md_path.read_text(encoding="utf-8")
    paths = _extract_repo_paths(text)

    missing = []
    for rel_path in paths:
        full_path = REPO_ROOT / rel_path
        if not full_path.exists():
            missing.append(rel_path)

    assert not missing, (
        f"README.md references {len(missing)} path(s) that do not exist: "
        + ", ".join(missing)
        + "\nRun: git log --oneline -5 -- <path> to check if they were moved/renamed."
    )
