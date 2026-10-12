"""
Tests for issue #195: Pin Python dev dependency versions in pyproject.toml.

Verifies that:
  - pyproject.toml carries upper-bound caps on all three dev dependencies
  - .github/workflows/release.yml python-lint job installs via editable install
  - .github/workflows/release.yml python-test job installs via editable install
  - CONTRIBUTING.md Section 5 directs contributors to pip install -e '.[dev]'
"""

import json
import os
import re
import subprocess
import tempfile

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


class TestReleaseVersionInputSafety:
    """Manual release versions must be isolated and validated before use."""

    @staticmethod
    def _compute_step() -> str:
        content = RELEASE_YML.read_text()
        match = re.search(
            r"^      - name: Compute CalVer tag(?P<step>.*?)(?=^      - name: |\Z)",
            content,
            re.M | re.S,
        )
        assert match, "Could not locate the Compute CalVer tag step"
        return match.group("step")

    def test_dispatch_version_is_mapped_to_environment_not_shell_source(self):
        step = self._compute_step()
        assert "VERSION_INPUT: ${{ github.event.inputs.version }}" in step, (
            "manual version must be mapped through the compute step environment"
        )
        run_script = step.split("        run: |\n", maxsplit=1)[1]
        assert "${{ github.event.inputs.version }}" not in run_script, (
            "manual version must not be interpolated into the shell script"
        )
        assert 'VERSION_ARG="$VERSION_INPUT"' in run_script

    def test_calver_validation_precedes_tag_output(self):
        run_script = self._compute_step().split("        run: |\n", maxsplit=1)[1]
        validation = run_script.index('if [[ ! "$TAG" =~ ^[0-9]{4}')
        tag_output = run_script.index('echo "tag=${TAG}" >> "$GITHUB_OUTPUT"')
        assert validation < tag_output, "tag output must not be published before CalVer validation"

    def test_calver_validation_accepts_valid_versions_and_rejects_invalid_input(self):
        run_script = self._compute_step().split("        run: |\n", maxsplit=1)[1]
        match = re.search(
            r'(?ms)^          if \[\[ ! "\$TAG" =~ .*?'
            r'^          echo "tag=\$\{TAG\}" >> "\$GITHUB_OUTPUT"$',
            run_script,
        )
        assert match, "Could not extract CalVer validation and tag-output logic"
        validation_script = "\n".join(
            line.removeprefix("          ") for line in match.group().splitlines()
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, "github-output")
            marker_path = os.path.join(temp_dir, "injected")

            def validate(tag: str) -> subprocess.CompletedProcess:
                with open(output_path, "w", encoding="utf-8"):
                    pass
                result = subprocess.run(
                    ["bash", "-euo", "pipefail", "-c", validation_script],
                    env={**os.environ, "TAG": tag, "GITHUB_OUTPUT": output_path},
                    capture_output=True,
                    text=True,
                    check=False,
                )
                return result

            def read_output() -> str:
                with open(output_path, encoding="utf-8") as output_file:
                    return output_file.read()

            for valid_tag in ("2026.10.12", "2026.10.12.3"):
                result = validate(valid_tag)
                assert result.returncode == 0, result.stderr
                assert read_output() == f"tag={valid_tag}\n"

            invalid_tags = (
                "2026.10.12; touch " + marker_path,
                "2026.10.12.$(touch " + marker_path + ")",
                "2026.10.12.extra",
                "2026.1.12",
            )
            for invalid_tag in invalid_tags:
                result = validate(invalid_tag)
                assert result.returncode != 0, f"accepted invalid tag: {invalid_tag!r}"
                assert read_output() == "", "invalid version must fail before writing a tag output"
            assert not os.path.exists(marker_path), "shell-shaped version input was executed"

    def test_downstream_tag_steps_use_validated_version_output(self):
        content = RELEASE_YML.read_text()
        expected_tag_source = 'TAG="${{ steps.version.outputs.tag }}"'
        for step_name in (
            "Verify tag does not already exist",
            "Create tag and push",
            "Create GitHub Release",
        ):
            match = re.search(
                rf"^      - name: {re.escape(step_name)}(?P<step>.*?)(?=^      - name: |\Z)",
                content,
                re.M | re.S,
            )
            assert match, f"Could not locate downstream step: {step_name}"
            assert expected_tag_source in match.group("step"), (
                f"{step_name} must consume the validated version step output"
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
