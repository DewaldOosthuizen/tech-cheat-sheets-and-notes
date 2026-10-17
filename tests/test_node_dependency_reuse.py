"""Tests for installed Node dependency reuse in CI and the Makefile."""

from __future__ import annotations

import re
import subprocess

import yaml
from conftest import REPO_ROOT

MAKEFILE = REPO_ROOT / "Makefile"
PR_GATE_YML = REPO_ROOT / ".github" / "workflows" / "pr-gate.yml"


class TestPrGateNodeModulesCache:
    """The Mermaid job should restore only an exact Node manifest cache."""

    def test_mermaid_job_uses_manifest_sensitive_node_modules_cache(self) -> None:
        workflow = yaml.safe_load(PR_GATE_YML.read_text())
        steps = workflow["jobs"]["mermaid-check"]["steps"]
        cache_steps = [step for step in steps if step.get("id") == "node-modules-cache"]

        assert len(cache_steps) == 1, "Mermaid job must define one installed-dependencies cache"
        cache_step = cache_steps[0]
        assert re.fullmatch(r"actions/cache@[0-9a-f]{40}", cache_step["uses"])
        assert cache_step["with"]["path"] == "node_modules"
        assert cache_step["with"]["key"] == (
            "${{ runner.os }}-node-${{ env.NODE_VERSION }}-"
            "${{ hashFiles('package.json', 'package-lock.json') }}"
        )

        setup_node = next(step for step in steps if step.get("name") == "Setup Node")
        assert setup_node["with"]["cache"] == "npm"

    def test_mermaid_install_runs_only_on_installed_dependencies_cache_miss(self) -> None:
        workflow = yaml.safe_load(PR_GATE_YML.read_text())
        steps = workflow["jobs"]["mermaid-check"]["steps"]
        install_steps = [step for step in steps if step.get("name") == "Install dependencies"]

        assert len(install_steps) == 1
        assert install_steps[0]["run"] == "npm ci"
        assert install_steps[0]["if"] == "steps.node-modules-cache.outputs.cache-hit != 'true'"


class TestMakefileNodeDependencyReuse:
    """Node-dependent local targets must share one clean-install prerequisite."""

    def test_mermaid_and_audit_depend_on_shared_npm_install(self) -> None:
        content = MAKEFILE.read_text()

        phony_declarations = re.search(r"(?ms)^\.PHONY:.*?(?=^[^ \t]|\Z)", content)
        assert phony_declarations and "npm-deps" in phony_declarations.group()
        assert re.search(r"(?m)^npm-deps:(?: ## .*)?\n\tnpm ci$", content)
        assert re.search(r"(?m)^mermaid-check: .*\bnpm-deps\b", content)
        assert re.search(r"(?m)^npm-audit: npm-deps(?: ## .*)?$", content)
        assert content.count("\tnpm ci\n") == 2, (
            "npm ci should remain for install and live in the shared npm-deps prerequisite"
        )

    def test_make_ci_requests_the_shared_install_once(self) -> None:
        result = subprocess.run(
            ["make", "--dry-run", "ci"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )

        assert result.stdout.count("npm ci") == 1

    def test_direct_node_dependent_targets_still_install_dependencies(self) -> None:
        for target in ("mermaid-check", "npm-audit"):
            result = subprocess.run(
                ["make", "--dry-run", target],
                cwd=REPO_ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            assert result.stdout.count("npm ci") == 1, (
                f"Direct {target} invocation must perform one npm ci"
            )
