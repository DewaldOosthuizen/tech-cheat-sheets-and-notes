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

import pytest
import yaml
from conftest import REPO_ROOT
from packaging.requirements import Requirement
from packaging.version import Version

PYPROJECT = REPO_ROOT / "pyproject.toml"
RELEASE_YML = REPO_ROOT / ".github" / "workflows" / "release.yml"
PR_GATE_YML = REPO_ROOT / ".github" / "workflows" / "pr-gate.yml"
MAKEFILE = REPO_ROOT / "Makefile"
CONTRIBUTING = REPO_ROOT / "CONTRIBUTING.md"
PACKAGE_JSON = REPO_ROOT / "package.json"
VERCEL_JSON = REPO_ROOT / "vercel.json"
SUPPORTED_PYTHON_VERSIONS = ("3.11", "3.12", "3.13")


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


README_MD = REPO_ROOT / "README.md"

# AGENTS.md is excluded: it is a harness-protected agent-instruction file that
# requires one-operation human approval, which is unavailable in a one-shot run.
# README.md is the writable documentation surface that states the support policy.
SUPPORT_POLICY_DOCS = (README_MD,)


def _declared_supported_versions(text: str) -> tuple[str, ...]:
    """Return the Python versions named as supported by a documentation file.

    Extracts every semver ``3.x`` token from the file's supported-version
    statement, so the value is parsed from the policy text itself rather than
    copied from a literal that could drift away from the documentation.
    """
    match = re.search(r"(?im)^[^\n]*supported python versions?[^\n]*$", text)
    assert match, "documentation must declare the supported Python versions"
    return tuple(dict.fromkeys(re.findall(r"\b3\.\d+\b", match.group())))


@pytest.mark.parametrize(
    "doc_path",
    SUPPORT_POLICY_DOCS,
    ids=tuple(doc.name for doc in SUPPORT_POLICY_DOCS),
)
def test_documented_python_support_matches_ci_versions(doc_path):
    """The documented support policy must equal the CI test matrix versions."""
    assert _declared_supported_versions(doc_path.read_text()) == SUPPORTED_PYTHON_VERSIONS, (
        f"{doc_path.name} must declare exactly {', '.join(SUPPORTED_PYTHON_VERSIONS)} "
        "as the supported Python versions"
    )


@pytest.mark.parametrize("workflow", (PR_GATE_YML, RELEASE_YML))
def test_python_test_workflow_matrix_covers_supported_versions(workflow):
    lines = workflow.read_text().splitlines()
    job_start = lines.index("  python-test:")
    job_lines = []
    for line in lines[job_start + 1 :]:
        if line.startswith("  ") and not line.startswith("    "):
            break
        job_lines.append(line)

    matrix_line = next(
        (line.strip() for line in job_lines if line.strip().startswith("python-version: [")),
        None,
    )
    assert matrix_line, f"python-test in {workflow.name} must declare a version matrix"
    versions_text = matrix_line.partition("[")[2].partition("]")[0]
    versions = tuple(value.strip().strip('"') for value in versions_text.split(","))
    assert versions == SUPPORTED_PYTHON_VERSIONS
    assert any(line.strip() == "python-version: ${{ matrix.python-version }}" for line in job_lines)


def test_makefile_python_test_all_matches_supported_versions():
    content = MAKEFILE.read_text()
    aggregate = next(
        (line for line in content.splitlines() if line.startswith("python-test-all:")), None
    )
    assert aggregate, "Makefile must define python-test-all"
    assert set(aggregate.partition(":")[2].split()) == {
        "python-test-311",
        "python-test-312",
        "python-test-313",
    }


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


class TestReleaseNpmAuditGate:
    """The release validation gate must require a high-severity npm audit."""

    @staticmethod
    def _job_block(content: str, job_name: str) -> str:
        match = re.search(
            rf"(?ms)^  {re.escape(job_name)}:\n(?P<block>.*?)(?=^  [\w-]+:\n|\Z)", content
        )
        assert match, f"Could not locate {job_name} job in release.yml"
        return match.group("block")

    def test_release_npm_audit_job_installs_dependencies_before_auditing(self):
        content = RELEASE_YML.read_text()
        job_block = self._job_block(content, "npm-audit")

        install_index = job_block.index("run: npm ci")
        audit_index = job_block.index("run: npm audit --audit-level=high")
        assert install_index < audit_index, "npm audit must run after npm ci"

    def test_validation_gate_requires_npm_audit_success(self):
        content = RELEASE_YML.read_text()
        gate_block = self._job_block(content, "validation-gate")
        needs_match = re.search(r"(?m)^    needs: \[(.*?)\]$", gate_block)

        assert needs_match, "validation-gate must declare its required jobs"
        assert "npm-audit" in needs_match.group(1), "validation-gate must depend on npm-audit"
        assert "needs.npm-audit.result" in gate_block, (
            "validation-gate must check the npm-audit result"
        )
        assert re.search(r'needs\.npm-audit\.result\s*}}\s*"\s*!=\s*"success"', gate_block), (
            "validation-gate must fail unless npm-audit succeeds"
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

    def test_write_permissions_are_limited_to_version_tag_release(self):
        workflow = yaml.safe_load(RELEASE_YML.read_text())
        jobs = workflow["jobs"]

        assert workflow["permissions"] == {"contents": "read"}
        assert jobs["version-tag-release"]["permissions"] == {"contents": "write"}
        for job_name, job in jobs.items():
            if job_name == "version-tag-release":
                continue
            assert all(access != "write" for access in job.get("permissions", {}).values()), (
                f"{job_name} must not grant write permissions"
            )

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
        deploy = self._job(RELEASE_YML.read_text(), "deploy")
        condition = re.search(r"(?m)^    if: \$\{\{ (?P<expr>.+) }}$", deploy)
        assert condition, "deploy must have an explicit condition"
        expression = condition.group("expr")
        parsed_condition = re.fullmatch(
            r"github\.ref == '([^']+)' && !inputs\.([a-z_]+)", expression
        )
        assert parsed_condition, f"Unsupported deploy condition: {expression!r}"
        main_ref, skip_input_name = parsed_condition.groups()
        assert main_ref == "refs/heads/main"
        assert skip_input_name == "skip_deploy"

        if event == "push":
            assert skip_deploy is None, "Push events do not provide workflow_dispatch inputs"
            dispatch_inputs = {}
        else:
            assert event == "workflow_dispatch"
            dispatch_inputs = {} if skip_deploy is None else {skip_input_name: skip_deploy}

        evaluated = ref == main_ref and not bool(dispatch_inputs.get(skip_input_name))
        assert evaluated is expected_deploy

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

    def test_release_workflow_concurrency_is_scoped_to_ref(self):
        content = RELEASE_YML.read_text()
        assert re.search(
            r"(?m)^concurrency:\n  group: \$\{\{ github\.workflow }}-\$\{\{ github\.ref }}$",
            content,
        )
        assert re.search(r"(?m)^  cancel-in-progress: true$", content)


class TestReleaseActionPinning:
    """All third-party GitHub Actions in release.yml must be pinned to a full SHA."""

    def test_all_action_refs_use_full_commit_sha(self):
        import re

        content = RELEASE_YML.read_text()
        uses_values = re.findall(r"(?m)^\s*uses:\s*(.+?)\s*$", content)
        assert uses_values, "release.yml must contain uses: references"
        for value in uses_values:
            value = value.strip()
            if value.startswith("./") or value.startswith(".\\"):
                continue
            assert "@" in value, f"Unpinned action reference: {value!r}"
            action, rest = value.split("@", 1)
            ref = rest.split()[0]
            assert re.fullmatch(r"[0-9a-f]{40}", ref), (
                f"Action {action!r} must be pinned to a 40-char SHA, got {ref!r}"
            )
            assert re.search(r"#\s*v\S+", rest), (
                f"Action {action!r} must include a trailing version comment, got {value!r}"
            )


class TestPRGateWorkflowPermissions:
    """The PR Gate declares only the minimum read-only permissions."""

    PR_GATE_YML = REPO_ROOT / ".github" / "workflows" / "pr-gate.yml"

    def test_workflow_level_permissions_are_readonly(self):
        content = self.PR_GATE_YML.read_text()
        workflow = yaml.safe_load(content)
        assert workflow["permissions"] == {"contents": "read"}, (
            "PR Gate must declare read-only workflow-level permissions"
        )

    def test_no_job_grants_write_permission(self):
        content = self.PR_GATE_YML.read_text()
        workflow = yaml.safe_load(content)
        jobs = workflow["jobs"]
        assert jobs, "PR Gate must declare at least one job"
        for job_name, job in jobs.items():
            assert all(access != "write" for access in job.get("permissions", {}).values()), (
                f"{job_name} must not grant write permissions"
            )
