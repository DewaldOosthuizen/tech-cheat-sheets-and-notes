"""Tests for issue #294 — documentation dependency resolution is unified and locked.

The authoritative source for documentation build dependencies is the `docs`
optional dependency group in pyproject.toml. requirements-docs.txt is
generated from uv.lock via `uv export --extra docs --no-dev` and must match
the committed file.
"""

from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
REQUIREMENTS_DOCS = REPO_ROOT / "requirements-docs.txt"


def _uv_available() -> bool:
    """Check whether `uv` is on PATH."""
    try:
        subprocess.run(
            ["uv", "--version"],
            capture_output=True,
            timeout=10,
            check=True,
            stdin=subprocess.DEVNULL,
        )
        return True
    except (FileNotFoundError, subprocess.CalledProcessError, OSError):
        return False


def _uv_export(path: Path) -> None:
    """Run `uv export --format requirements.txt --output-file <path> --extra docs
    --no-dev --no-header --python 3.12` to match `make update-docs-reqs`."""
    subprocess.run(
        [
            "uv",
            "export",
            "--format",
            "requirements.txt",
            "--output-file",
            str(path),
            "--extra",
            "docs",
            "--no-dev",
            "--no-header",
            "--python",
            "3.12",
        ],
        cwd=REPO_ROOT,
        check=True,
        timeout=120,
    )


def _normalize(req_text: str) -> list[str]:
    """Strip comment-only lines and blank lines, return remaining non-empty lines."""
    lines = []
    for line in req_text.splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            lines.append(stripped)
    return lines


def test_docs_deps_match_uv_export(tmp_path: Path):
    """requirements-docs.txt must match `uv export --extra docs --no-dev` output line-for-line."""
    if not _uv_available():
        pytest.skip("uv not on PATH — cannot verify docs dependency lock")

    generated_path = tmp_path / "requirements-docs-generated.txt"
    _uv_export(generated_path)

    committed = REQUIREMENTS_DOCS.read_text()
    generated = generated_path.read_text()

    committed_lines = _normalize(committed)
    generated_lines = _normalize(generated)

    assert committed_lines == generated_lines, (
        "requirements-docs.txt does not match `uv export --extra docs --no-dev` output.\n"
        "Regenerate with: uv export --format requirements.txt --output-file "
        "requirements-docs.txt --extra docs --no-dev --no-header\n"
        "Then run `make check-docs-deps` before committing."
    )


def _extract_update_docs_reqs_recipe() -> str:
    """Extract the recipe commands for update-docs-reqs from the Makefile."""
    makefile = (REPO_ROOT / "Makefile").read_text(encoding="utf-8")
    match = re.search(r"update-docs-reqs:.*?\n((?:\t[^\n]*\n?)+)", makefile)
    assert match, "Could not locate update-docs-reqs recipe in Makefile"
    commands = [
        line.removeprefix("\t").lstrip("@")
        for line in match.group(1).splitlines()
        if line.strip()
    ]
    return "\n".join(commands)


def test_update_docs_reqs_recipe_uses_atomic_staging():
    """Makefile update-docs-reqs recipe must use staging file and atomic replace."""
    recipe = _extract_update_docs_reqs_recipe()
    assert "requirements-docs.txt.tmp" in recipe
    assert "mv requirements-docs.txt.tmp requirements-docs.txt" in recipe
    assert "rm -f requirements-docs.txt.tmp" in recipe
    assert "> requirements-docs.txt\n" not in recipe


def test_update_docs_reqs_failed_export_preserves_file(tmp_path: Path):
    """A failed uv export must leave requirements-docs.txt unchanged and clean up temp files."""
    sh_bin = shutil.which("sh") or shutil.which("bash")
    if not sh_bin:
        pytest.skip("POSIX shell (sh/bash) not available to execute Makefile recipe")

    req_file = tmp_path / "requirements-docs.txt"
    original_content = b"# Existing valid requirements\npackage==1.0.0\n"
    req_file.write_bytes(original_content)

    mock_uv = tmp_path / "mock_uv"
    mock_uv.write_text("#!/bin/sh\nexit 1\n", encoding="utf-8")
    mock_uv.chmod(0o755)

    recipe_script = _extract_update_docs_reqs_recipe()
    run_script = recipe_script.replace("$(UV)", str(mock_uv).replace("\\", "/"))

    result = subprocess.run(
        [sh_bin, "-c", run_script],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
        stdin=subprocess.DEVNULL,
    )

    assert result.returncode != 0, f"Recipe unexpectedly succeeded: {result.stdout}"
    assert req_file.read_bytes() == original_content, (
        "requirements-docs.txt was modified despite failed export"
    )
    temp_file = tmp_path / "requirements-docs.txt.tmp"
    assert not temp_file.exists(), (
        f"Temporary staging file {temp_file} was not cleaned up after failure"
    )


def test_update_docs_reqs_successful_export_replaces_atomically(tmp_path: Path):
    """Successful uv export replaces requirements-docs.txt atomically and removes temp file."""
    sh_bin = shutil.which("sh") or shutil.which("bash")
    if not sh_bin:
        pytest.skip("POSIX shell (sh/bash) not available to execute Makefile recipe")

    req_file = tmp_path / "requirements-docs.txt"
    original_content = b"# Old requirements\nold-pkg==0.1.0\n"
    req_file.write_bytes(original_content)

    mock_uv = tmp_path / "mock_uv"
    mock_uv.write_text("#!/bin/sh\necho 'new-pkg==2.0.0 --hash=sha256:1234'\n", encoding="utf-8")
    mock_uv.chmod(0o755)

    recipe_script = _extract_update_docs_reqs_recipe()
    run_script = recipe_script.replace("$(UV)", str(mock_uv).replace("\\", "/"))

    result = subprocess.run(
        [sh_bin, "-c", run_script],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
        stdin=subprocess.DEVNULL,
    )

    assert result.returncode == 0, f"Recipe failed: {result.stderr}"
    new_content = req_file.read_bytes()
    assert b"new-pkg==2.0.0" in new_content
    assert b"# Minimal Python dependencies" in new_content
    temp_file = tmp_path / "requirements-docs.txt.tmp"
    assert not temp_file.exists(), (
        f"Temporary staging file {temp_file} was not removed after successful completion"
    )
