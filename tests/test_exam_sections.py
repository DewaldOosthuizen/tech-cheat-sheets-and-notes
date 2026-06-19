"""Tests for issue #213 — FEATURE: Add additional exam sections.

Covers all 6 sub-issues:
  1. Snippet files extracted from cheat sheets
  2. .mmd files renamed to exam-agnostic slugs
  3. mkdocs.yml not_in_nav block added
  4. conftest.py expand_snippets made recursive
  5. Makefile MD_FILES_VALIDATE glob-based
  6. Documentation updates (CONTRIBUTING, AGENTS, index.md)
"""

from __future__ import annotations

from pathlib import Path

import pytest
from conftest import REPO_ROOT

DOCS = REPO_ROOT / "docs"

# ── helpers ───────────────────────────────────────────────────────────────────

DOMAINS = [
    "networking",
    "security",
    "storage",
    "monitoring",
    "compute",
    "identity",
    "ha-dr",
    "governance",
    "messaging",
    "waf",
]


# ── Issue 1: Snippet files exist ──────────────────────────────────────────────


class TestSnippetFilesExist:
    @pytest.mark.parametrize("domain", DOMAINS)
    def test_snippet_file_exists(self, domain: str) -> None:
        snippet = DOCS / "azure" / "files" / domain / f"{domain}.md"
        assert snippet.exists(), f"Missing snippet file: {snippet}"

    @pytest.mark.parametrize("domain", DOMAINS)
    def test_snippet_file_non_empty(self, domain: str) -> None:
        snippet = DOCS / "azure" / "files" / domain / f"{domain}.md"
        if snippet.exists():
            assert snippet.stat().st_size > 0, f"Snippet file is empty: {snippet}"


class TestSnippetFileContent:
    """Snippet files should have content and no 'Also relevant for:' callouts."""

    @pytest.mark.parametrize("domain", DOMAINS)
    def test_no_also_relevant_for_in_snippet(self, domain: str) -> None:
        snippet = DOCS / "azure" / "files" / domain / f"{domain}.md"
        if snippet.exists():
            text = snippet.read_text(encoding="utf-8")
            assert "> Also relevant for:" not in text, (
                f"{snippet}: 'Also relevant for:' callout should not appear in snippet"
            )

    def test_networking_snippet_has_load_balancers(self) -> None:
        snippet = DOCS / "azure" / "files" / "networking" / "networking.md"
        if snippet.exists():
            text = snippet.read_text(encoding="utf-8")
            assert "## Load Balancers" in text or "Load Balancer" in text

    def test_security_snippet_has_defender(self) -> None:
        snippet = DOCS / "azure" / "files" / "security" / "security.md"
        if snippet.exists():
            text = snippet.read_text(encoding="utf-8")
            assert "Defender" in text

    def test_storage_snippet_has_redundancy(self) -> None:
        snippet = DOCS / "azure" / "files" / "storage" / "storage.md"
        if snippet.exists():
            text = snippet.read_text(encoding="utf-8")
            assert "LRS" in text or "redundancy" in text.lower()

    def test_compute_snippet_has_functions(self) -> None:
        snippet = DOCS / "azure" / "files" / "compute" / "compute.md"
        if snippet.exists():
            text = snippet.read_text(encoding="utf-8")
            assert "Azure Functions" in text or "Functions" in text

    def test_identity_snippet_has_rbac(self) -> None:
        snippet = DOCS / "azure" / "files" / "identity" / "identity.md"
        if snippet.exists():
            text = snippet.read_text(encoding="utf-8")
            assert "RBAC" in text or "Entra" in text

    def test_governance_snippet_has_policy(self) -> None:
        snippet = DOCS / "azure" / "files" / "governance" / "governance.md"
        if snippet.exists():
            text = snippet.read_text(encoding="utf-8")
            assert "Policy" in text

    def test_waf_snippet_has_pillars(self) -> None:
        snippet = DOCS / "azure" / "files" / "waf" / "waf.md"
        if snippet.exists():
            text = snippet.read_text(encoding="utf-8")
            assert "Reliability" in text or "pillar" in text.lower()


class TestSnippetDiagramPaths:
    """Diagram references inside snippets must use new exam-agnostic paths."""

    @pytest.mark.parametrize("domain", DOMAINS)
    def test_no_az305_prefix_in_snippet(self, domain: str) -> None:
        snippet = DOCS / "azure" / "files" / domain / f"{domain}.md"
        if snippet.exists():
            text = snippet.read_text(encoding="utf-8")
            assert "diagrams/" + domain + "/az305-" not in text, (
                f"{snippet}: old az305-prefixed diagram reference found"
            )

    @pytest.mark.parametrize("domain", DOMAINS)
    def test_no_az104_prefix_in_snippet(self, domain: str) -> None:
        snippet = DOCS / "azure" / "files" / domain / f"{domain}.md"
        if snippet.exists():
            text = snippet.read_text(encoding="utf-8")
            assert "diagrams/" + domain + "/az104-" not in text, (
                f"{snippet}: old az104-prefixed diagram reference found"
            )


# ── Issue 2: .mmd files renamed to exam-agnostic slugs ───────────────────────

OLD_MMD = [
    "compute/az104-availability-decision-flow.mmd",
    "compute/az104-vm-family-decision-flow.mmd",
    "compute/az305-aks-scaling-mechanisms.mmd",
    "compute/az305-azure-cache-for-redis.mmd",
    "compute/az305-azure-container-apps-vs-aks-vs-aci.mmd",
    "compute/az305-compute-decision-flow.mmd",
    "compute/az305-runtime-language-fit-functions-vs-logic-apps-vs-app-service.mmd",
    "compute/az305-serverless-event-driven-selection.mmd",
    "governance/az104-management-hierarchy-decision-flow.mmd",
    "governance/az104-policy-assignment-scope-hierarchy.mmd",
    "governance/az305-governance-enforcement-decision-flow.mmd",
    "governance/az305-management-hierarchy.mmd",
    "ha-dr/az104-ha-dr-decision-flow.mmd",
    "ha-dr/az104-recovery-services-vault-structure.mmd",
    "ha-dr/az305-key-concepts.mmd",
    "identity/az104-entra-id-join-type-decision-flow.mmd",
    "identity/az104-rbac-role-assignment-decision-flow.mmd",
    "identity/az305-entra-identity-scenario-decision-flow.mmd",
    "identity/az305-system-identity-type-decision-flow.mmd",
    "messaging/az104-messaging-decision-flow.mmd",
    "messaging/az104-service-bus-sku-decision-flow.mmd",
    "messaging/az305-decision-flowchart.mmd",
    "messaging/az305-logic-apps-vs-azure-functions-vs-durable-functions.mmd",
    "monitoring/az104-agent-selection-decision-flow.mmd",
    "monitoring/az104-diagnostic-settings-routing.mmd",
    "monitoring/az305-azure-monitor-ecosystem.mmd",
    "networking/az104-load-balancer-sku-decision-flow.mmd",
    "networking/az104-nsg-rule-evaluation.mmd",
    "networking/az104-vnet-connectivity-decision-flow.mmd",
    "networking/az305-connectivity-patterns.mmd",
    "networking/az305-decision-flow-api-gateway-selection.mmd",
    "networking/az305-decision-flow.mmd",
    "networking/az305-decision-flow-network-security-selection.mmd",
    "networking/az305-virtual-networks-vnet.mmd",
    "security/az104-defender-for-cloud-coverage.mmd",
    "security/az104-key-vault-access-decision-flow.mmd",
    "storage/az104-managed-disk-selection.mmd",
    "storage/az104-storage-replication-decision-flow.mmd",
    "storage/az305-blob-storage-access-tiers.mmd",
    "storage/az305-storage-redundancy.mmd",
    "waf/az104-cost-management-decision-flow.mmd",
    "waf/az104-tag-inheritance-architecture.mmd",
    "waf/az305-decision-flow-pillar-trade-off-navigator.mmd",
    "waf/az305-five-pillar-summary.mmd",
]

NEW_MMD = [
    "compute/availability-decision-flow.mmd",
    "compute/vm-family-decision-flow.mmd",
    "compute/aks-scaling-mechanisms.mmd",
    "compute/azure-cache-for-redis.mmd",
    "compute/azure-container-apps-vs-aks-vs-aci.mmd",
    "compute/compute-decision-flow.mmd",
    "compute/runtime-language-fit-functions-vs-logic-apps-vs-app-service.mmd",
    "compute/serverless-event-driven-selection.mmd",
    "governance/management-hierarchy-decision-flow.mmd",
    "governance/policy-assignment-scope-hierarchy.mmd",
    "governance/governance-enforcement-decision-flow.mmd",
    "governance/management-hierarchy.mmd",
    "ha-dr/ha-dr-decision-flow.mmd",
    "ha-dr/recovery-services-vault-structure.mmd",
    "ha-dr/key-concepts.mmd",
    "identity/entra-id-join-type-decision-flow.mmd",
    "identity/rbac-role-assignment-decision-flow.mmd",
    "identity/entra-identity-scenario-decision-flow.mmd",
    "identity/system-identity-type-decision-flow.mmd",
    "messaging/messaging-decision-flow.mmd",
    "messaging/service-bus-sku-decision-flow.mmd",
    "messaging/decision-flowchart.mmd",
    "messaging/logic-apps-vs-azure-functions-vs-durable-functions.mmd",
    "monitoring/agent-selection-decision-flow.mmd",
    "monitoring/diagnostic-settings-routing.mmd",
    "monitoring/azure-monitor-ecosystem.mmd",
    "networking/load-balancer-sku-decision-flow.mmd",
    "networking/nsg-rule-evaluation.mmd",
    "networking/vnet-connectivity-decision-flow.mmd",
    "networking/connectivity-patterns.mmd",
    "networking/decision-flow-api-gateway-selection.mmd",
    "networking/decision-flow.mmd",
    "networking/decision-flow-network-security-selection.mmd",
    "networking/virtual-networks-vnet.mmd",
    "security/defender-for-cloud-coverage.mmd",
    "security/key-vault-access-decision-flow.mmd",
    "storage/managed-disk-selection.mmd",
    "storage/storage-replication-decision-flow.mmd",
    "storage/blob-storage-access-tiers.mmd",
    "storage/storage-redundancy.mmd",
    "waf/cost-management-decision-flow.mmd",
    "waf/tag-inheritance-architecture.mmd",
    "waf/decision-flow-pillar-trade-off-navigator.mmd",
    "waf/five-pillar-summary.mmd",
]

DIAGRAMS = DOCS / "azure" / "diagrams"


class TestMmdFilesRenamed:
    @pytest.mark.parametrize("rel", OLD_MMD)
    def test_old_mmd_does_not_exist(self, rel: str) -> None:
        old_path = DIAGRAMS / rel
        assert not old_path.exists(), f"Old exam-prefixed .mmd file still exists: {old_path}"

    @pytest.mark.parametrize("rel", NEW_MMD)
    def test_new_mmd_exists(self, rel: str) -> None:
        new_path = DIAGRAMS / rel
        assert new_path.exists(), f"New exam-agnostic .mmd file missing: {new_path}"


# ── Issue 3: mkdocs.yml nav uses domain pages ─────────────────────────────────


class TestMkdocsNavDomainPages:
    def _mkdocs_text(self) -> str:
        return (REPO_ROOT / "mkdocs.yml").read_text(encoding="utf-8")

    @pytest.mark.parametrize("domain", DOMAINS)
    def test_domain_in_nav(self, domain: str) -> None:
        text = self._mkdocs_text()
        assert f"azure/files/{domain}/{domain}.md" in text, (
            f"mkdocs.yml nav missing direct entry for: {domain}"
        )

    def test_exam_coverage_page_in_nav(self) -> None:
        text = self._mkdocs_text()
        assert "azure/files/exams/exams.md" in text, (
            "mkdocs.yml nav missing Exam Coverage index page"
        )

    def test_not_in_nav_removed(self) -> None:
        text = self._mkdocs_text()
        assert "not_in_nav:" not in text, "not_in_nav: key should be removed now files are in nav"


# ── Issue 4: conftest.py recursive expand_snippets ────────────────────────────


class TestExpandSnippetsRecursive:
    def _conftest_text(self) -> str:
        return (REPO_ROOT / "tests" / "conftest.py").read_text(encoding="utf-8")

    def test_max_expand_depth_defined(self) -> None:
        text = self._conftest_text()
        assert "_MAX_EXPAND_DEPTH" in text, "conftest.py missing _MAX_EXPAND_DEPTH constant"

    def test_expand_snippets_has_loop(self) -> None:
        text = self._conftest_text()
        assert "for _ in range(_MAX_EXPAND_DEPTH)" in text, (
            "conftest.py expand_snippets missing depth-limited loop"
        )

    def test_expand_snippets_stabilizes(self) -> None:
        """A snippet that references another snippet is fully expanded."""
        import tempfile

        from tests.conftest import expand_snippets

        with tempfile.TemporaryDirectory() as tmpdir:
            base = Path(tmpdir)
            inner = base / "inner.md"
            inner.write_text("INNER CONTENT", encoding="utf-8")
            outer = base / "outer.md"
            outer.write_text('--8<-- "inner.md"', encoding="utf-8")

            result = expand_snippets('--8<-- "outer.md"', base=base)
            assert result == "INNER CONTENT", f"Recursive expansion failed; got: {result!r}"

    def test_expand_snippets_missing_file_left_unexpanded(self) -> None:
        """Missing snippet references are left as-is (not raised as error)."""
        from tests.conftest import expand_snippets

        original = '--8<-- "nonexistent/file.md"'
        result = expand_snippets(original)
        assert result == original


# ── Issue 5: Makefile glob-based MD_FILES_VALIDATE ────────────────────────────


class TestMakefileMdFilesValidate:
    def _makefile_text(self) -> str:
        return (REPO_ROOT / "Makefile").read_text(encoding="utf-8")

    def test_md_files_validate_uses_find(self) -> None:
        text = self._makefile_text()
        assert "find docs" in text, (
            "Makefile MD_FILES_VALIDATE should use 'find docs' glob, not a static list"
        )

    def test_md_files_validate_excludes_diagrams(self) -> None:
        text = self._makefile_text()
        assert "docs/diagrams" in text or "'docs/diagrams/*'" in text or "docs/diagrams" in text, (
            "Makefile MD_FILES_VALIDATE should exclude docs/diagrams/ paths"
        )

    def test_static_list_removed(self) -> None:
        text = self._makefile_text()
        assert "cheat_sheets/AZ-305.md" not in text, (
            "Makefile still references old cheat_sheets wrapper files"
        )


# ── Issue 6: Documentation updates ───────────────────────────────────────────


class TestContributingMdUpdated:
    def _contributing_text(self) -> str:
        return (REPO_ROOT / "CONTRIBUTING.md").read_text(encoding="utf-8")

    def test_exam_agnostic_slug_mentioned(self) -> None:
        text = self._contributing_text()
        assert "<slug>.mmd" in text, (
            "CONTRIBUTING.md should document exam-agnostic <slug>.mmd naming"
        )

    def test_no_exam_prefix_in_file_naming_rule(self) -> None:
        """The old <exam>-<slug> naming rule should be replaced."""
        text = self._contributing_text()
        # The old rule "az305-<slug>.mmd" / "az104-<slug>.mmd" in the rules section
        # should be replaced with just <slug>.mmd
        assert "az305-<slug>.mmd" not in text and "az104-<slug>.mmd" not in text, (
            "CONTRIBUTING.md still contains old az305-/az104- prefix naming rule"
        )

    def test_section_snippet_subsection_present(self) -> None:
        text = self._contributing_text()
        assert "snippet" in text.lower() or "section snippet" in text.lower(), (
            "CONTRIBUTING.md missing section on section snippet files"
        )


class TestAgentsMdUpdated:
    def _agents_text(self) -> str:
        return (REPO_ROOT / "AGENTS.md").read_text(encoding="utf-8")

    def test_section_snippet_paths_in_layout(self) -> None:
        text = self._agents_text()
        # Should mention the new docs/<section>/<section>.md pattern
        assert (
            "docs/<section>" in text
            or "section>.md" in text
            or "networking/networking.md" in text
            or "<section>/<section>.md" in text
        ), "AGENTS.md repository layout should mention section snippet files"

    def test_exam_agnostic_mmd_convention(self) -> None:
        text = self._agents_text()
        # Old pattern az305-<slug>.mmd / az104-<slug>.mmd replaced
        assert "az305-<slug>.mmd" not in text and "az104-<slug>.mmd" not in text, (
            "AGENTS.md Mermaid section still mentions old exam-prefixed .mmd convention"
        )
