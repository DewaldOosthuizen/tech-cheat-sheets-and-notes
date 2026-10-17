"""Tests for pull-request and full-pipeline dead-link auditing."""

from __future__ import annotations

import re

from conftest import REPO_ROOT

MAKEFILE = REPO_ROOT / "Makefile"
PR_GATE = REPO_ROOT / ".github" / "workflows" / "pr-gate.yml"


def test_pr_gate_runs_link_check_independently() -> None:
    content = PR_GATE.read_text(encoding="utf-8")
    job = re.search(r"^  link-check:\n(.*?)(?=^  [\w-]+:|\Z)", content, re.M | re.S)

    assert job, "PR Gate must define an independent link-check job"
    assert "needs:" not in job.group(1), "link-check must run independently of the job chain"
    assert "uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1" in job.group(1)
    assert "run: make link-check" in job.group(1)


def test_pr_gate_summary_requires_and_checks_link_check() -> None:
    content = PR_GATE.read_text(encoding="utf-8")
    summary = re.search(r"^  pr-gate-summary:\n(.*)\Z", content, re.M | re.S)

    assert summary, "PR Gate must define the summary job"
    expected_needs = (
        "needs: [markdownlint, python-lint, mermaid-check, python-test, "
        "npm-audit, check-docs-deps, link-check]"
    )
    assert expected_needs in summary.group(1)
    assert 'needs.link-check.result }}" != "success"' in summary.group(1)


def test_pr_gate_job_order_documents_link_check() -> None:
    content = PR_GATE.read_text(encoding="utf-8")

    assert "# 7. link-check (independent; runs in parallel with the other checks)" in content
    assert "# 8. pr-gate-summary (needs: all above; if: always() to report status)" in content


def test_ci_full_includes_ci_and_link_check() -> None:
    content = MAKEFILE.read_text(encoding="utf-8")

    assert re.search(r"^ci-full:\s+ci\s+link-check\s*$", content, re.M), (
        "ci-full must depend on both ci and link-check"
    )
