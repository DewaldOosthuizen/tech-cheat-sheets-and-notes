"""Tests for issue #196 - FEATURE: Add structured Governance section decision flowchart.

Verifies that:
  - A '## Governance Enforcement Decision Flow' subsection exists in governance.md
  - The subsection contains a flowchart TD Mermaid diagram
  - All four primary decision branches are present in the diagram
  - The fifth legacy-Blueprints migration branch is present
  - An exam-tip callout follows the diagram covering Policy vs Locks vs Management Groups
  - The subsection appears between the Blueprints deprecation block and ## Cost Management
  - The diagram directive is exactly 'flowchart TD' (not 'graph TD')
"""

import re

import pytest
from conftest import REPO_ROOT, expand_snippets

GOVERNANCE = REPO_ROOT / "docs" / "azure" / "files" / "governance" / "governance.md"


@pytest.fixture(scope="module")
def governance_text():
    # Expand --8<-- snippet directives so diagram content is visible to assertions.
    return expand_snippets(GOVERNANCE.read_text())


@pytest.fixture(scope="module")
def governance_section(governance_text):
    """Extract the GOVERNANCE section text for narrower assertions."""
    # The governance file IS the governance section now — use its full content.
    return governance_text


class TestGovernanceDecisionFlowSubsectionExists:
    """The '## Governance Enforcement Decision Flow' subsection must exist."""

    def test_subsection_heading_present(self, governance_section):
        assert "## Governance Enforcement Decision Flow" in governance_section

    def test_subsection_uses_h2_not_h3(self, governance_text):
        # Must be ## not ###
        assert "## Governance Enforcement Decision Flow" in governance_text
        assert "### Governance Enforcement Decision Flow" not in governance_text


class TestGovernanceDecisionFlowDiagramDirective:
    """The diagram must use 'flowchart TD', not 'graph TD'."""

    def test_flowchart_td_directive_present(self, governance_section):
        # Extract the decision-flow subsection specifically
        match = re.search(
            r"## Governance Enforcement Decision Flow(.*?)(?=\n## |\Z)",
            governance_section,
            re.DOTALL,
        )
        assert match, "Governance Enforcement Decision Flow subsection body not found"
        body = match.group(1)
        assert "flowchart TD" in body, "Diagram must use 'flowchart TD' directive"

    def test_no_graph_td_in_decision_flow(self, governance_section):
        match = re.search(
            r"## Governance Enforcement Decision Flow(.*?)(?=\n## |\Z)",
            governance_section,
            re.DOTALL,
        )
        assert match
        body = match.group(1)
        assert "graph TD" not in body, "Decision flow must not use 'graph TD'"


class TestGovernanceDecisionFlowBranches:
    """All four decision branches must be present in the diagram."""

    def _diagram_body(self, governance_section):
        match = re.search(
            r"## Governance Enforcement Decision Flow(.*?)(?=\n## |\Z)",
            governance_section,
            re.DOTALL,
        )
        assert match
        return match.group(1)

    def test_branch_azure_policy(self, governance_section):
        body = self._diagram_body(governance_section)
        assert "Azure Policy" in body, "Branch for Azure Policy must be present"

    def test_branch_management_groups(self, governance_section):
        body = self._diagram_body(governance_section)
        assert "Management Groups" in body, "Branch for Management Groups must be present"

    def test_branch_template_specs(self, governance_section):
        body = self._diagram_body(governance_section)
        assert "Template Specs" in body, "Branch for Template Specs must be present"

    def test_branch_budgets_cost_management(self, governance_section):
        body = self._diagram_body(governance_section)
        assert "Budgets" in body and "Cost Management" in body, (
            "Branch for Budgets + Cost Management must be present"
        )

    def test_branch_blueprints_migration(self, governance_section):
        """Fifth branch: legacy Blueprints migration path."""
        body = self._diagram_body(governance_section)
        assert "Blueprints" in body, "Legacy Blueprints migration branch must be present"


class TestGovernanceDecisionFlowExamTip:
    """An exam-tip callout distinguishing Policy vs Locks vs Management Groups must follow."""

    def test_exam_tip_present_after_diagram(self, governance_section):
        match = re.search(
            r"## Governance Enforcement Decision Flow(.*?)(?=\n## |\Z)",
            governance_section,
            re.DOTALL,
        )
        assert match
        body = match.group(1)
        assert "> **Exam tip:**" in body, (
            "Exam tip callout must follow the Governance Enforcement Decision Flow diagram"
        )

    def test_exam_tip_mentions_locks(self, governance_section):
        match = re.search(
            r"## Governance Enforcement Decision Flow(.*?)(?=\n## |\Z)",
            governance_section,
            re.DOTALL,
        )
        assert match
        body = match.group(1)
        assert "Locks" in body, "Exam tip must clarify that Locks are not an enforcement tool"

    def test_exam_tip_mentions_policy(self, governance_section):
        match = re.search(
            r"## Governance Enforcement Decision Flow(.*?)(?=\n## |\Z)",
            governance_section,
            re.DOTALL,
        )
        assert match
        body = match.group(1)
        # Azure Policy must appear in the exam-tip region (not just the diagram)
        assert "Azure Policy" in body


class TestGovernanceDecisionFlowPlacement:
    """The new subsection must appear between the Blueprints block and ## Cost Management."""

    def test_decision_flow_before_cost_management(self, governance_section):
        idx_flow = governance_section.find("## Governance Enforcement Decision Flow")
        idx_cost = governance_section.find("## Cost Management")
        assert idx_flow != -1, "Governance Enforcement Decision Flow subsection not found"
        assert idx_cost != -1, "Cost Management subsection not found"
        assert idx_flow < idx_cost, (
            "Governance Enforcement Decision Flow must appear before ## Cost Management"
        )

    def test_decision_flow_after_blueprints_deprecation(self, governance_section):
        idx_dep = governance_section.find("Blueprints is retired")
        idx_flow = governance_section.find("## Governance Enforcement Decision Flow")
        assert idx_dep != -1, "Blueprints deprecation warning not found"
        assert idx_flow != -1, "Governance Enforcement Decision Flow subsection not found"
        assert idx_dep < idx_flow, (
            "Governance Enforcement Decision Flow must appear after "
            "the Blueprints deprecation block"
        )
