"""
Tests for issue #195: Pin Python dev dependency versions in pyproject.toml.

Verifies that:
  - pyproject.toml carries upper-bound caps on all three dev dependencies
  - .github/workflows/release.yml python-lint job installs via editable install
  - .github/workflows/release.yml python-test job installs via editable install
  - CONTRIBUTING.md Section 5 directs contributors to pip install -e '.[dev]'
"""

import json
import re

import pytest
from conftest import REPO_ROOT
from packaging.requirements import Requirement
from packaging.version import Version

PYPROJECT = REPO_ROOT / "pyproject.toml"
RELEASE_YML = REPO_ROOT / ".github" / "workflows" / "release.yml"
CONTRIBUTING = REPO_ROOT / "CONTRIBUTING.md"
PACKAGE_JSON = REPO_ROOT / "package.json"
VERCEL_JSON = REPO_ROOT / "vercel.json"


def _package_json_dev_deps():
    """Return the devDependencies dict from package.json."""
    data = json.loads(PACKAGE_JSON.read_text())
    return data.get("devDependencies", {})


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
    """.github/workflows/release.yml python-lint job must use editable install."""

    def test_python_lint_uses_editable_install(self):
        content = RELEASE_YML.read_text()
        assert "pip install -e '.[dev]'" in content, (
            "python-lint job must install via pip install -e '.[dev]'"
        )

    def test_python_lint_no_inline_ruff_install(self):
        content = RELEASE_YML.read_text()
        assert 'pip install "ruff>=' not in content, (
            "python-lint job must not contain an inline ruff version pin"
        )


class TestCIPythonTestJob:
    """.github/workflows/release.yml python-test job must use editable install."""

    def test_python_test_uses_editable_install(self):
        content = RELEASE_YML.read_text()
        assert "pip install -e '.[dev]'" in content, (
            "python-test job must install via pip install -e '.[dev]'"
        )

    def test_python_test_no_bare_pip_install(self):
        content = RELEASE_YML.read_text()
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


# ── Issues #293, #295, #296: Pin dependency versions and enforce strict builds ──


class TestPuppeteerExactVersion:
    """package.json must declare Puppeteer with an exact version."""

    def test_puppeteer_is_declared(self):
        deps = _package_json_dev_deps()
        assert "puppeteer" in deps, "puppeteer must be listed in devDependencies"

    def test_puppeteer_has_exact_version(self):
        deps = _package_json_dev_deps()
        version = deps["puppeteer"]
        assert re.match(r"^\d+\.\d+\.\d+$", version), (
            f"puppeteer must be an exact semver version, got: {version!r}"
        )

    def test_no_caret_or_wildcard_puppeteer(self):
        content = PACKAGE_JSON.read_text()
        assert not re.search(r'"puppeteer"\s*:\s*~?\^?[><=*]?\s*\d', content), (
            "puppeteer must not appear with a caret, tilde, or wildcard range"
        )


class TestVercelCliPinned:
    """Vercel CLI must be pinned exactly and not installed via @latest in prod deploy."""

    def test_prod_deploy_no_vercel_latest(self):
        content = RELEASE_YML.read_text()
        assert "vercel@latest" not in content, "release.yml must not install vercel@latest"

    def test_prod_deploy_pins_exact_vercel_version(self):
        content = RELEASE_YML.read_text()
        assert re.search(r"npm install --global vercel@\d+\.\d+\.\d+", content), (
            "release.yml must install a pinned exact Vercel CLI version"
        )


class TestVercelStrictMkdocs:
    """Vercel production build must use mkdocs build --strict."""

    def test_vercel_json_has_build_command(self):
        data = json.loads(VERCEL_JSON.read_text())
        assert "buildCommand" in data, "vercel.json must define buildCommand"

    def test_build_command_includes_strict(self):
        data = json.loads(VERCEL_JSON.read_text())
        cmd = data["buildCommand"]
        assert "mkdocs build --strict" in cmd, (
            f"buildCommand must include 'mkdocs build --strict', got: {cmd!r}"
        )

    def test_build_command_installs_requirements_docs(self):
        data = json.loads(VERCEL_JSON.read_text())
        cmd = data["buildCommand"]
        assert "requirements-docs.txt" in cmd, (
            "buildCommand must install requirements-docs.txt before building"
        )

    def test_no_vercel_latest_in_vercel_json(self):
        data = json.loads(VERCEL_JSON.read_text())
        cmd = data.get("buildCommand", "")
        assert "vercel@latest" not in cmd, (
            "vercel.json buildCommand must not reference vercel@latest"
        )


class TestProductionReleaseWorkflow:
    """Production release workflow is restricted to main and handles inputs safely."""

    @staticmethod
    def _job(content: str, name: str) -> str:
        match = re.search(
            rf"(?ms)^  {re.escape(name)}:\n(?P<body>.*?)(?=^  [\w-]+:|\Z)",
            content,
        )
        assert match, f"Workflow job {name!r} must exist"
        return match.group("body")

    def test_push_and_manual_dispatch_triggers_are_retained(self):
        content = RELEASE_YML.read_text()
        triggers = re.search(r'(?ms)^"on":\n(?P<body>.*?)(?=^permissions:)', content)
        assert triggers, "Release workflow must define its triggers"
        assert re.search(r"(?m)^  push:\n    branches:\n      - main$", triggers.group("body"))
        assert re.search(r"(?m)^  workflow_dispatch:$", triggers.group("body"))

    def test_non_main_ref_check_is_a_validation_gate_dependency(self):
        content = RELEASE_YML.read_text()
        ref_check = self._job(content, "release-ref-check")
        assert "if: ${{ github.ref != 'refs/heads/main' }}" in ref_check
        assert "Production releases can only run from refs/heads/main" in ref_check
        assert "exit 1" in ref_check

        gate = self._job(content, "validation-gate")
        assert re.search(r"(?m)^    needs:.*\brelease-ref-check\b", gate)
        assert re.search(r"(?m)^    if: always\(\)$", gate)
        assert "${{ needs.release-ref-check.result }}" in gate
        assert '!= "success"' in gate

        build = self._job(content, "build")
        version_release = self._job(content, "version-tag-release")
        deploy = self._job(content, "deploy")
        assert "needs: validation-gate" in build
        assert "needs: build" in version_release
        assert "needs: version-tag-release" in deploy

    def test_mutating_jobs_have_explicit_main_ref_guards(self):
        content = RELEASE_YML.read_text()
        for job_name in ("version-tag-release", "deploy"):
            job = self._job(content, job_name)
            assert "github.ref == 'refs/heads/main'" in job

    @pytest.mark.parametrize(
        ("event", "ref", "skip_deploy", "expected_deploy"),
        [
            ("workflow_dispatch", "refs/heads/main", None, True),
            ("workflow_dispatch", "refs/heads/main", False, True),
            ("workflow_dispatch", "refs/heads/main", True, False),
            ("push", "refs/heads/main", None, True),
            ("workflow_dispatch", "refs/heads/feature", False, False),
        ],
    )
    def test_deploy_eligibility(self, event, ref, skip_deploy, expected_deploy):
        del event  # The typed input is absent on push events and defaults to false.
        deploy = self._job(RELEASE_YML.read_text(), "deploy")
        condition = re.search(r"(?m)^    if: \$\{\{ (?P<expr>.+) }}$", deploy)
        assert condition, "deploy must have an explicit condition"
        expression = condition.group("expr")
        assert "github.ref == 'refs/heads/main'" in expression
        assert "!inputs.skip_deploy" in expression
        eligible = ref == "refs/heads/main" and not bool(skip_deploy)
        assert eligible is expected_deploy

    def test_default_skip_changelog_keeps_custom_changelog_generator(self):
        content = RELEASE_YML.read_text()
        assert re.search(r"(?m)^\s+skip_changelog:[\s\S]*?^\s+default: false$", content)
        release_step = re.search(
            r"(?ms)^      - name: Create GitHub Release\n(?P<body>.*?)(?=^      - name:|\Z)",
            content,
        )
        assert release_step, "GitHub Release creation step must exist"
        assert "scripts/generate_changelog.py --output CHANGELOG.md" in release_step.group("body")
        assert "--notes-file CHANGELOG.md" in release_step.group("body")

    def test_skip_changelog_with_prior_tag_uses_previous_tag_as_notes_baseline(self):
        content = RELEASE_YML.read_text()
        skip_check = self._job(content, "version-tag-release")
        release_step = re.search(
            r"(?ms)^      - name: Create GitHub Release\n(?P<body>.*?)(?=^      - name:|\Z)",
            skip_check,
        )
        assert release_step, "GitHub Release creation step must exist"
        assert "last_tag=${LAST_TAG}" in skip_check
        assert skip_check.index('echo "last_tag=${LAST_TAG}"') < skip_check.index(
            'git push origin "$TAG"'
        )
        assert "--generate-notes" in release_step.group("body")
        assert '"${{ inputs.skip_changelog }}" == "true"' in release_step.group("body")
        assert '--notes-start-tag "$BASELINE_TAG"' in release_step.group("body")
        assert "steps.skip-check.outputs.last_tag" in release_step.group("body")

    def test_skip_changelog_without_baseline_omits_notes_start_tag(self):
        content = RELEASE_YML.read_text()
        release_step = re.search(
            r"(?ms)^      - name: Create GitHub Release\n(?P<body>.*?)(?=^      - name:|\Z)",
            content,
        )
        assert release_step, "GitHub Release creation step must exist"
        body = release_step.group("body")
        assert '"${{ inputs.skip_changelog }}" == "true"' in body
        assert re.search(r"(?s)if \[ -n \"\$BASELINE_TAG\" \].*?--notes-start-tag", body)
        assert re.search(r"(?s)else\s+gh release create.*?--generate-notes", body)
        assert re.search(
            r"(?s)else\s+gh release create.*?--generate-notes(?!.*--notes-start-tag)",
            body,
        )

    def test_release_workflow_concurrency_configuration_is_unchanged(self):
        content = RELEASE_YML.read_text()
        assert re.search(r"(?m)^concurrency:\n  group: \$\{\{ github\.workflow }}$", content)
        assert re.search(r"(?m)^  cancel-in-progress: true$", content)
