"""
Tests for issue #195: Pin Python dev dependency versions in pyproject.toml.

Verifies that:
  - pyproject.toml carries upper-bound caps on all three dev dependencies
  - .github/workflows/lint.yml python-lint job installs via editable install
  - .github/workflows/lint.yml python-test job installs via editable install
  - CONTRIBUTING.md Section 5 directs contributors to pip install -e '.[dev]'
"""

import re

from conftest import REPO_ROOT
from packaging.requirements import Requirement
from packaging.version import Version

PYPROJECT = REPO_ROOT / "pyproject.toml"
LINT_YML = REPO_ROOT / ".github" / "workflows" / "lint.yml"
CONTRIBUTING = REPO_ROOT / "CONTRIBUTING.md"


class TestPyprojectUpperBounds:
    """pyproject.toml dev deps must carry upper-bound caps."""

    def _dev_requirements(self) -> list[Requirement]:
        content = PYPROJECT.read_text()
        m = re.search(r"\[project\.optional-dependencies\].*?dev\s*=\s*\[(.*?)\]", content, re.S)
        assert m, "Could not locate dev extras in pyproject.toml"
        entries = re.findall(r'"([^"]+)"', m.group(1))
        return [Requirement(entry) for entry in entries]

    def _requirement(self, name: str) -> Requirement:
        for req in self._dev_requirements():
            if req.name == name:
                return req
        raise AssertionError(f"{name} must be listed under [project.optional-dependencies] dev")

    @staticmethod
    def _lower_bound(req: Requirement) -> Version:
        bounds = [Version(spec.version) for spec in req.specifier if spec.operator in {">", ">="}]
        assert bounds, f"{req.name} must define a lower bound"
        return max(bounds)

    @staticmethod
    def _has_upper_bound(req: Requirement, upper: str) -> bool:
        return any(
            spec.operator == "<" and Version(spec.version) == Version(upper)
            for spec in req.specifier
        )

    def test_pytest_has_upper_bound(self):
        req = self._requirement("pytest")
        assert self._lower_bound(req) >= Version("9.0.3"), "pytest lower bound must be >=9.0.3"
        assert self._has_upper_bound(req, "10"), "pytest constraint must include upper bound <10"

    def test_pytest_cov_has_upper_bound(self):
        req = self._requirement("pytest-cov")
        assert self._lower_bound(req) >= Version("7.1.0"), "pytest-cov lower bound must be >=7.1.0"
        assert self._has_upper_bound(req, "8"), "pytest-cov constraint must include upper bound <8"

    def test_ruff_has_upper_bound(self):
        req = self._requirement("ruff")
        assert self._lower_bound(req) >= Version("0.15.15"), "ruff lower bound must be >=0.15.15"
        assert self._has_upper_bound(req, "1"), "ruff constraint must include upper bound <1"

    def test_no_open_ended_pytest(self):
        content = PYPROJECT.read_text()
        # Line like '"pytest>=9.0.3",' with no upper bound must not exist
        assert not re.search(r'"pytest>=[\d.]+",', content), (
            "pytest must not appear with open-ended lower bound only"
        )

    def test_no_open_ended_pytest_cov(self):
        content = PYPROJECT.read_text()
        assert not re.search(r'"pytest-cov>=[\d.]+",', content), (
            "pytest-cov must not appear with open-ended lower bound only"
        )

    def test_no_open_ended_ruff(self):
        content = PYPROJECT.read_text()
        assert not re.search(r'"ruff>=[\d.]+",', content), (
            "ruff must not appear with open-ended lower bound only"
        )


class TestCIPythonLintJob:
    """.github/workflows/lint.yml python-lint job must use editable install."""

    def test_python_lint_uses_editable_install(self):
        content = LINT_YML.read_text()
        assert "pip install -e '.[dev]'" in content, (
            "python-lint job must install via pip install -e '.[dev]'"
        )

    def test_python_lint_no_inline_ruff_install(self):
        content = LINT_YML.read_text()
        assert 'pip install "ruff>=' not in content, (
            "python-lint job must not contain an inline ruff version pin"
        )


class TestCIPythonTestJob:
    """.github/workflows/lint.yml python-test job must use editable install."""

    def test_python_test_uses_editable_install(self):
        content = LINT_YML.read_text()
        assert "pip install -e '.[dev]'" in content, (
            "python-test job must install via pip install -e '.[dev]'"
        )

    def test_python_test_no_bare_pip_install(self):
        content = LINT_YML.read_text()
        assert "pip install pytest pytest-cov" not in content, (
            "python-test job must not use bare unconstrained pip install"
        )


class TestContributingDevSetup:
    """CONTRIBUTING.md Section 5 must point to the Makefile-based setup."""

    def test_editable_install_present(self):
        content = CONTRIBUTING.read_text()
        assert "make install" in content, (
            "CONTRIBUTING.md must document 'make install' as the dev setup command"
        )

    def test_bare_pip_install_removed(self):
        content = CONTRIBUTING.read_text()
        assert "pip install ruff pytest" not in content, (
            "CONTRIBUTING.md must not instruct bare 'pip install ruff pytest'"
        )
