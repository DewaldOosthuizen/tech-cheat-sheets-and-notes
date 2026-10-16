"""Tests for issue #153 - FEATURE: Indicate related concepts in domain pages."""

import pytest
from conftest import REPO_ROOT, expand_snippets

MONITORING = REPO_ROOT / "docs" / "azure" / "files" / "monitoring" / "monitoring.md"


@pytest.fixture(scope="module")
def monitoring_text():
    # Monitoring snippet contains all the content these tests assert on.
    return expand_snippets(MONITORING.read_text())


@pytest.fixture(scope="module")
def az104_text():
    # AZ-104 content is the same domain file — no separate wrapper.
    return expand_snippets(MONITORING.read_text())


class TestAZ305AzureMonitorAnnotation:
    """Task 1: Azure Monitor Service cell annotated with umbrella components."""

    def test_azure_monitor_umbrella_annotation(self, monitoring_text):
        needle = "umbrella: Activity Log, Metrics, Alerts, Diagnostic Settings, Insights family"
        assert needle in monitoring_text


class TestAZ305LogAnalyticsAnnotation:
    """Task 2: Log Analytics Workspace Service cell annotated."""

    def test_log_analytics_annotation(self, monitoring_text):
        needle = "contains: KQL engine, retention tiers; fed via Diagnostic Settings"
        assert needle in monitoring_text


class TestAZ305AppInsightsAnnotation:
    """Task 3: Application Insights Service cell annotated."""

    def test_app_insights_annotation(self, monitoring_text):
        needle = "contains: Live Metrics, Availability Tests, Dependency Tracking, Smart Detection"
        assert needle in monitoring_text


class TestAZ305ActivityLogAlertExpanded:
    """Task 4: Activity Log Alert Use Case cell expanded."""

    def test_activity_log_alert_use_case_expanded(self, monitoring_text):
        needle = (
            "Activity Log is a sub-component of Azure Monitor, "
            "routed to Log Analytics via Diagnostic Settings"
        )
        assert needle in monitoring_text


class TestAZ305ExamTipAfterActionGroups:
    """Task 5: Exam tip inserted after Action Groups note."""

    def test_exam_tip_sub_component_preference(self, monitoring_text):
        assert "prefer it over the umbrella service" in monitoring_text

    def test_exam_tip_mentions_activity_log_and_live_metrics(self, monitoring_text):
        assert "Activity Log" in monitoring_text
        assert "Live Metrics" in monitoring_text
        assert "Smart Detection" in monitoring_text

    def test_exam_tip_appears_before_diagnostic_settings_section(self, monitoring_text):
        tip_pos = monitoring_text.find("prefer it over the umbrella service")
        diag_pos = monitoring_text.find("## Diagnostic Settings")
        assert tip_pos != -1
        assert diag_pos != -1
        assert tip_pos < diag_pos


class TestAZ305DiagnosticSettingsCategories:
    """Task 6: Categories bullet updated with Activity Log."""

    def test_activity_log_category_listed(self, monitoring_text):
        assert "**Activity Log** (control-plane events)" in monitoring_text

    def test_activity_log_not_standalone_bullet(self, monitoring_text):
        needle = (
            "Activity Log is a sub-component of Azure Monitor routed to "
            "Log Analytics Workspace via Diagnostic Settings"
        )
        assert needle in monitoring_text


class TestAZ305MermaidDiagram:
    """Task 7: Mermaid diagram updated with ActivityLog node and Diagnostic Settings edge."""

    def test_activity_log_node_exists(self, monitoring_text):
        assert 'ActivityLog["Activity Log' in monitoring_text

    def test_activity_log_feeds_monitor(self, monitoring_text):
        assert "ActivityLog" in monitoring_text
        assert "--> Monitor" in monitoring_text

    def test_diagnostic_settings_edge_label(self, monitoring_text):
        assert "via Diagnostic Settings" in monitoring_text

    def test_no_bare_monitor_to_logs_edge(self, monitoring_text):
        # The old plain edge "Monitor --> Logs[Log Analytics" should be replaced
        assert "Monitor --> Logs[Log Analytics" not in monitoring_text


class TestAZ104LogAnalyticsAnnotation:
    """Task 9: Log Analytics Workspace in AZ-104 Diagnostic Settings table annotated."""

    def test_log_analytics_annotation_az104(self, az104_text):
        assert "fed via Diagnostic Settings; contains Activity Log data, KQL engine" in az104_text


class TestAZ104ExamTip:
    """Task 10: Exam tip inserted after Diagnostic Settings Routing diagram in AZ-104."""

    def test_exam_tip_activity_log_sub_component(self, az104_text):
        needle = "Activity Log is a sub-component of Azure Monitor, not a standalone service"
        assert needle in az104_text

    def test_exam_tip_mentions_deployifnotexists(self, az104_text):
        assert "DeployIfNotExists" in az104_text

    def test_exam_tip_appears_after_routing_diagram(self, az104_text):
        diagram_pos = az104_text.find("Diagnostic Settings Routing")
        needle = "Activity Log is a sub-component of Azure Monitor, not a standalone service"
        tip_pos = az104_text.find(needle)
        assert diagram_pos != -1
        assert tip_pos != -1
        assert tip_pos > diagram_pos
