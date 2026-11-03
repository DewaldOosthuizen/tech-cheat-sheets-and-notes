"""Regression tests for the pre-commit Markdown lint scope (issue #390).

These tests assert that the pre-commit `markdownlint-cli2` hook's `files`
pattern covers exactly the same Markdown files that the Makefile
`markdownlint` target and the GitHub Actions workflows lint.

Current CI Markdown scope (Makefile line 40, pr-gate.yml, release.yml):
    docs/**/*.md, README.md, AGENTS.md, CONTRIBUTING.md

A future change that widens or narrows one scope (for example dropping
CONTRIBUTING.md from the pre-commit hook, or adding a new Markdown target
to a workflow) fails one of these tests before it ever reaches CI.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml
from conftest import REPO_ROOT

# CI Markdown targets, mirroring the Makefile's MD_GLOBS (line 40).
CI_MARKDOWN_GLOBS = (
    "docs/**/*.md",
    "README.md",
    "AGENTS.md",
    "CONTRIBUTING.md",
)

_PRE_COMMIT_CONFIG = REPO_ROOT / ".pre-commit-config.yaml"


def _discover_ci_markdown_targets() -> set[Path]:
    """Return the set of Markdown files the CI lint scope resolves to.

    Each glob in CI_MARKDOWN_GLOBS is resolved against the repository root;
    the result is a set of paths relative to REPO_ROOT (pre-commit passes
    filenames relative to the repository root to the hook's files pattern).
    """
    targets: set[Path] = set()
    for pattern in CI_MARKDOWN_GLOBS:
        for path in REPO_ROOT.glob(pattern):
            targets.add(path.relative_to(REPO_ROOT))
    return targets


def _pre_commit_files_pattern() -> re.Pattern[str]:
    """Return the compiled `files` regex of the markdownlint-cli2 hook."""
    with open(_PRE_COMMIT_CONFIG, encoding="utf-8") as fh:
        config = yaml.safe_load(fh)
    for repo in config["repos"]:
        for hook in repo.get("hooks", []):
            if hook.get("id") == "markdownlint-cli2":
                return re.compile(hook["files"])
    raise AssertionError("markdownlint-cli2 hook not found in .pre-commit-config.yaml")


def _pre_commit_files_regex() -> str:
    """Return the raw `files` regex string of the markdownlint-cli2 hook."""
    with open(_PRE_COMMIT_CONFIG, encoding="utf-8") as fh:
        config = yaml.safe_load(fh)
    for repo in config["repos"]:
        for hook in repo.get("hooks", []):
            if hook.get("id") == "markdownlint-cli2":
                return hook["files"]
    raise AssertionError("markdownlint-cli2 hook not found in .pre-commit-config.yaml")


def _all_markdown_paths() -> set[Path]:
    """Return every Markdown file in the repository (excluding hidden dirs).

    Hidden directories such as .venv, .git, .pytest_cache and node_modules are
    skipped so the discovery is limited to files that could plausibly be
    linted. This keeps the cross-check deterministic without relying on
    .gitignore state. Paths are relative to REPO_ROOT.
    """
    markdown: set[Path] = set()
    for path in REPO_ROOT.rglob("*.md"):
        if path.is_file() and not any(part.startswith(".") for part in path.parts):
            markdown.add(path.relative_to(REPO_ROOT))
    return markdown


class TestPreCommitCoversCiMarkdownScope:
    """Every tracked CI Markdown target must be covered by the pre-commit hook."""

    @pytest.mark.parametrize(
        "target",
        sorted(_discover_ci_markdown_targets(), key=lambda p: str(p)),
    )
    def test_ci_target_matches_pre_commit_pattern(self, target: Path) -> None:
        """A CI Markdown target must match the pre-commit hook's files pattern."""
        pattern = _pre_commit_files_pattern()
        assert pattern.match(str(target)), (
            f"CI Markdown target {target} is not covered by the pre-commit hook "
            f"pattern {pattern.pattern!r}"
        )


class TestPreCommitDoesNotLintOutsideCiScope:
    """The pre-commit hook must not match any Markdown file outside the CI set."""

    def test_no_markdown_outside_scope_matches_pre_commit_pattern(self) -> None:
        """No Markdown file outside the CI scope may match the hook pattern."""
        ci_targets = _discover_ci_markdown_targets()
        pattern = _pre_commit_files_pattern()
        all_markdown = _all_markdown_paths()
        outside = all_markdown - ci_targets
        for path in sorted(outside, key=lambda p: str(p)):
            assert not pattern.match(str(path)), (
                f"pre-commit hook pattern matches Markdown file outside the CI "
                f"scope: {path}\n"
                f"  pattern: {pattern.pattern!r}\n"
                f"  CI scope: {sorted(ci_targets, key=lambda p: str(p))}"
            )
