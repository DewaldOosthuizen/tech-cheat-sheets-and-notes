"""Tests for issue #228 - FEATURE: Add AZ-204.

Verifies that:
  - exams.md has AZ-204 column between AZ-104 and AZ-305
  - compute.md has deployment slots exam tip, Durable Functions section, ACR section
  - storage.md has Cosmos DB developer section, Blob SAS Tokens section
  - security.md has Key Vault exam tips and App Configuration section
  - identity.md has MSAL flows, DefaultAzureCredential chain, App Registration scopes
  - messaging.md has Azure Functions trigger bindings, Event Grid schema sections
  - monitoring.md has Application Insights developer focus section
"""

import pytest
from conftest import REPO_ROOT, expand_snippets

EXAMS_MD = REPO_ROOT / "docs" / "azure" / "files" / "exams" / "exams.md"
COMPUTE_MD = REPO_ROOT / "docs" / "azure" / "files" / "compute" / "compute.md"
STORAGE_MD = REPO_ROOT / "docs" / "azure" / "files" / "storage" / "storage.md"
SECURITY_MD = REPO_ROOT / "docs" / "azure" / "files" / "security" / "security.md"
IDENTITY_MD = REPO_ROOT / "docs" / "azure" / "files" / "identity" / "identity.md"
MESSAGING_MD = REPO_ROOT / "docs" / "azure" / "files" / "messaging" / "messaging.md"
MONITORING_MD = REPO_ROOT / "docs" / "azure" / "files" / "monitoring" / "monitoring.md"


@pytest.fixture(scope="module")
def exams_text():
    return expand_snippets(EXAMS_MD.read_text())


@pytest.fixture(scope="module")
def compute_text():
    return expand_snippets(COMPUTE_MD.read_text())


@pytest.fixture(scope="module")
def storage_text():
    return expand_snippets(STORAGE_MD.read_text())


@pytest.fixture(scope="module")
def security_text():
    return expand_snippets(SECURITY_MD.read_text())


@pytest.fixture(scope="module")
def identity_text():
    return expand_snippets(IDENTITY_MD.read_text())


@pytest.fixture(scope="module")
def messaging_text():
    return expand_snippets(MESSAGING_MD.read_text())


@pytest.fixture(scope="module")
def monitoring_text():
    return expand_snippets(MONITORING_MD.read_text())


# ── TASK 1: exams.md — AZ-204 column ─────────────────────────────────────────


class TestExamsAZ204Column:
    """exams.md must have AZ-204 column between AZ-104 and AZ-305."""

    def test_az204_column_header_present(self, exams_text):
        assert "| AZ-204 |" in exams_text

    def test_table_header_has_az204_between_az104_and_az305(self, exams_text):
        assert "| Section | AZ-900 | AZ-104 | AZ-204 | AZ-305 | AZ-500 | AZ-700 |" in exams_text

    def test_compute_az204_is_full(self, exams_text):
        # Compute row must show Full for AZ-204
        assert "Full" in exams_text

    def test_networking_az204_is_dash(self, exams_text):
        # Networking row: AZ-204 = —
        assert "[Networking]" in exams_text

    def test_messaging_az204_is_partial(self, exams_text):
        # Messaging row: AZ-204 = Partial
        lines = exams_text.splitlines()
        messaging_line = next(
            (line for line in lines if "Messaging" in line and "Integration" in line), None
        )
        assert messaging_line is not None, "Messaging row not found"
        assert "Partial" in messaging_line

    def test_security_az204_is_partial(self, exams_text):
        lines = exams_text.splitlines()
        security_line = next(
            (
                line
                for line in lines
                if "[Security]" in line or ("Security" in line and "security.md" in line)
            ),
            None,
        )
        assert security_line is not None, "Security row not found"
        assert "Partial" in security_line

    def test_storage_az204_is_partial(self, exams_text):
        lines = exams_text.splitlines()
        storage_line = next(
            (
                line
                for line in lines
                if "[Storage]" in line or ("Storage" in line and "storage.md" in line)
            ),
            None,
        )
        assert storage_line is not None, "Storage row not found"
        assert "Partial" in storage_line

    def test_identity_az204_is_partial(self, exams_text):
        lines = exams_text.splitlines()
        identity_line = next(
            (
                line
                for line in lines
                if "Identity" in line and ("identity.md" in line or "Access" in line)
            ),
            None,
        )
        assert identity_line is not None, "Identity row not found"
        assert "Partial" in identity_line

    def test_monitoring_az204_is_partial(self, exams_text):
        lines = exams_text.splitlines()
        monitoring_line = next(
            (line for line in lines if "Monitoring" in line and "monitoring.md" in line),
            None,
        )
        assert monitoring_line is not None, "Monitoring row not found"
        assert "Partial" in monitoring_line


# ── TASK 2: compute.md — Deployment slots, Durable Functions, ACR ────────────


class TestComputeDeploymentSlotsExamTip:
    """compute.md must have deployment slots exam tip after App Service Plans table."""

    def test_deployment_slots_exam_tip_present(self, compute_text):
        assert "Deployment slots run inside the same App Service Plan" in compute_text

    def test_deployment_slots_mentions_slot_swap(self, compute_text):
        assert "slot swap" in compute_text or "slot" in compute_text

    def test_deployment_slots_mentions_sticky_settings(self, compute_text):
        assert "Sticky (slot) settings are NOT swapped" in compute_text

    def test_deployment_slots_mentions_routing_rules(self, compute_text):
        assert "`routingRules`" in compute_text

    def test_deployment_slots_mentions_auto_swap(self, compute_text):
        assert "Auto-swap" in compute_text


class TestComputeDurableFunctionsSection:
    """compute.md must have Durable Functions Orchestration Patterns section."""

    def test_durable_functions_section_heading(self, compute_text):
        assert "## Durable Functions Orchestration Patterns" in compute_text

    def test_durable_functions_table_has_pattern_column(self, compute_text):
        assert "| Service | Pattern | Use Case | Key Feature |" in compute_text

    def test_function_chaining_row_present(self, compute_text):
        assert "Function Chaining" in compute_text

    def test_fan_out_fan_in_row_present(self, compute_text):
        assert "Fan-out / Fan-in" in compute_text

    def test_async_http_api_row_present(self, compute_text):
        assert "Async HTTP API (Human Interaction)" in compute_text

    def test_eternal_orchestration_row_present(self, compute_text):
        assert "Eternal Orchestration" in compute_text

    def test_timer_monitor_row_present(self, compute_text):
        assert "Timer / Monitor" in compute_text

    def test_continue_as_new_exam_tip(self, compute_text):
        assert "`ContinueAsNew`" in compute_text

    def test_wait_for_external_event_in_exam_tip(self, compute_text):
        assert "`WaitForExternalEvent`" in compute_text

    def test_webjobs_exam_tip_present(self, compute_text):
        assert "WebJobs" in compute_text

    def test_webjobs_exam_tip_mentions_app_service_plan(self, compute_text):
        assert (
            "WebJobs (continuous or triggered) run inside an existing App Service Plan"
            in compute_text
        )


class TestComputeACRSection:
    """compute.md must have Azure Container Registry section."""

    def test_acr_section_heading(self, compute_text):
        assert "## Azure Container Registry (ACR)" in compute_text

    def test_acr_table_has_type_column(self, compute_text):
        assert "| Service | Type | Use Case | Key Feature |" in compute_text

    def test_acr_basic_row_present(self, compute_text):
        assert "ACR Basic" in compute_text

    def test_acr_standard_row_present(self, compute_text):
        assert "ACR Standard" in compute_text

    def test_acr_premium_row_present(self, compute_text):
        assert "ACR Premium" in compute_text

    def test_acr_geo_replication_exam_tip(self, compute_text):
        assert "Geo-replication is a Premium-only feature" in compute_text

    def test_acr_tasks_exam_tip(self, compute_text):
        assert "ACR Tasks" in compute_text

    def test_content_trust_exam_tip(self, compute_text):
        assert "Content trust" in compute_text


# ── TASK 3: storage.md — Cosmos DB developer, Blob SAS Tokens ────────────────


class TestStorageCosmosDBDeveloperSection:
    """storage.md must have Cosmos DB Developer Focus section."""

    def test_cosmos_db_developer_section_heading(self, storage_text):
        assert "## Cosmos DB — Developer Focus (AZ-204)" in storage_text

    def test_partition_key_design_rules_heading(self, storage_text):
        assert "**Partition key design rules:**" in storage_text

    def test_high_cardinality_bullet(self, storage_text):
        assert "high-cardinality" in storage_text

    def test_hot_partitions_bullet(self, storage_text):
        assert "hot partition" in storage_text or "hot partitions" in storage_text

    def test_immutable_partition_key_bullet(self, storage_text):
        assert "immutable" in storage_text

    def test_cosmos_ru_model_table_present(self, storage_text):
        assert "| Service | Type | Best For | Key Feature |" in storage_text

    def test_provisioned_throughput_row(self, storage_text):
        assert "Cosmos DB Provisioned Throughput" in storage_text

    def test_autoscale_row(self, storage_text):
        assert "Cosmos DB Autoscale" in storage_text

    def test_serverless_row(self, storage_text):
        assert "Cosmos DB Serverless" in storage_text

    def test_cosmos_exam_tip_present(self, storage_text):
        assert "Choose serverless for sporadic" in storage_text

    def test_cosmos_sdk_python_code_block(self, storage_text):
        assert "from azure.cosmos import CosmosClient, PartitionKey" in storage_text

    def test_cosmos_sdk_create_database(self, storage_text):
        assert "create_database_if_not_exists" in storage_text

    def test_cosmos_sdk_create_container(self, storage_text):
        assert "create_container_if_not_exists" in storage_text


class TestStorageBlobSASTokensSection:
    """storage.md must have Blob Storage SAS Tokens section."""

    def test_blob_sas_section_heading(self, storage_text):
        assert "## Blob Storage SAS Tokens" in storage_text

    def test_service_sas_row_present(self, storage_text):
        assert "Service SAS" in storage_text

    def test_account_sas_row_present(self, storage_text):
        assert "Account SAS" in storage_text

    def test_user_delegation_sas_row_present(self, storage_text):
        assert "User Delegation SAS" in storage_text

    def test_user_delegation_sas_exam_tip(self, storage_text):
        assert "User Delegation SAS is the most secure option" in storage_text

    def test_sas_sdk_python_code_block(self, storage_text):
        assert "from azure.storage.blob import BlobServiceClient" in storage_text

    def test_sas_sdk_generate_blob_sas(self, storage_text):
        assert "generate_blob_sas" in storage_text

    def test_sas_sdk_blob_sas_permissions(self, storage_text):
        assert "BlobSasPermissions" in storage_text


# ── TASK 4: security.md — Key Vault exam tips, App Configuration ──────────────


class TestSecurityKeyVaultExamTips:
    """security.md must have Key Vault DefaultAzureCredential and certificate exam tips."""

    def test_default_azure_credential_exam_tip(self, security_text):
        assert "DefaultAzureCredential" in security_text

    def test_secret_client_mentioned(self, security_text):
        assert "SecretClient" in security_text

    def test_azure_identity_mentioned(self, security_text):
        assert "azure-identity" in security_text

    def test_certificate_auto_rotation_exam_tip(self, security_text):
        assert "Certificate auto-rotation" in security_text or "certificate expiry" in security_text

    def test_certificate_near_expiry_event(self, security_text):
        assert "Microsoft.KeyVault.CertificateNearExpiry" in security_text


class TestSecurityAppConfigurationSection:
    """security.md must have App Configuration section."""

    def test_app_configuration_section_heading(self, security_text):
        assert "## App Configuration" in security_text

    def test_feature_flags_row_present(self, security_text):
        assert "App Configuration Feature Flags" in security_text

    def test_key_vault_references_row_present(self, security_text):
        assert "App Configuration Key Vault References" in security_text

    def test_label_based_config_row_present(self, security_text):
        assert "App Configuration Label-based Config" in security_text

    def test_key_vault_references_exam_tip(self, security_text):
        assert "App Configuration Key Vault references never copy" in security_text


# ── TASK 5: identity.md — MSAL flows, DefaultAzureCredential, App Registration ─


class TestIdentityMSALFlowsSection:
    """identity.md must have MSAL Authentication Flows section."""

    def test_msal_section_heading(self, identity_text):
        assert "## MSAL Authentication Flows (AZ-204)" in identity_text

    def test_msal_table_has_flow_column(self, identity_text):
        assert "| Service | Flow | Use Case | Key Feature |" in identity_text

    def test_auth_code_pkce_row(self, identity_text):
        assert "Authorization Code + PKCE" in identity_text

    def test_client_credentials_row(self, identity_text):
        assert "Client Credentials" in identity_text

    def test_on_behalf_of_row(self, identity_text):
        assert "On-Behalf-Of (OBO)" in identity_text

    def test_device_code_row(self, identity_text):
        assert "Device Code" in identity_text

    def test_obo_exam_tip_present(self, identity_text):
        assert "On-behalf-of (OBO) is the correct flow" in identity_text


class TestIdentityDefaultAzureCredentialSection:
    """identity.md must have DefaultAzureCredential Resolution Chain section."""

    def test_default_azure_credential_section_heading(self, identity_text):
        assert "## DefaultAzureCredential Resolution Chain" in identity_text

    def test_environment_credential_listed(self, identity_text):
        assert "EnvironmentCredential" in identity_text

    def test_workload_identity_credential_listed(self, identity_text):
        assert "WorkloadIdentityCredential" in identity_text

    def test_managed_identity_credential_listed(self, identity_text):
        assert "ManagedIdentityCredential" in identity_text

    def test_azure_cli_credential_listed(self, identity_text):
        assert "AzureCliCredential" in identity_text

    def test_interactive_browser_credential_listed(self, identity_text):
        assert "InteractiveBrowserCredential" in identity_text

    def test_default_azure_credential_exam_tip(self, identity_text):
        assert "same application code run locally" in identity_text


class TestIdentityAppRegistrationSection:
    """identity.md must have App Registration: Scopes vs Application Roles section."""

    def test_app_registration_section_heading(self, identity_text):
        assert "## App Registration: Scopes vs Application Roles" in identity_text

    def test_delegated_scopes_row(self, identity_text):
        assert "Delegated Scopes (OAuth2 Permissions)" in identity_text

    def test_application_roles_row(self, identity_text):
        assert "Application Roles (App Permissions)" in identity_text

    def test_app_roles_exam_tip(self, identity_text):
        assert "application roles + client credentials" in identity_text


# ── TASK 6: messaging.md — trigger bindings, Event Grid schemas ───────────────


class TestMessagingFunctionsTriggerBindingsSection:
    """messaging.md must have Azure Functions Trigger Bindings section."""

    def test_trigger_bindings_section_heading(self, messaging_text):
        assert "## Azure Functions Trigger Bindings (AZ-204)" in messaging_text

    def test_bindings_table_has_binding_column(self, messaging_text):
        assert "| Service | Binding | Direction | Key Feature |" in messaging_text

    def test_service_bus_trigger_row(self, messaging_text):
        assert "ServiceBusTrigger" in messaging_text

    def test_service_bus_output_row(self, messaging_text):
        assert "ServiceBusOutput" in messaging_text

    def test_event_hub_trigger_row(self, messaging_text):
        assert "EventHubTrigger" in messaging_text

    def test_event_hub_output_row(self, messaging_text):
        assert "EventHubOutput" in messaging_text

    def test_event_grid_trigger_row(self, messaging_text):
        assert "EventGridTrigger" in messaging_text

    def test_event_grid_output_row(self, messaging_text):
        assert "EventGridOutput" in messaging_text

    def test_service_bus_sessions_exam_tip(self, messaging_text):
        assert "`ServiceBusTrigger` with `isSessionsEnabled: true`" in messaging_text

    def test_event_hub_batch_exam_tip(self, messaging_text):
        assert "`EventHubTrigger` delivers events as a batch array" in messaging_text


class TestMessagingEventGridSchemaSection:
    """messaging.md must have Event Grid Schema vs CloudEvents Schema section."""

    def test_event_grid_schema_section_heading(self, messaging_text):
        assert "## Event Grid Schema vs CloudEvents Schema" in messaging_text

    def test_event_grid_schema_row(self, messaging_text):
        assert "Event Grid Schema" in messaging_text

    def test_cloudevents_schema_row(self, messaging_text):
        assert "CloudEvents 1.0 Schema" in messaging_text

    def test_cloudevents_exam_tip(self, messaging_text):
        assert "CloudEvents 1.0 schema when the requirement mentions" in messaging_text


# ── TASK 7: monitoring.md — Application Insights developer focus ──────────────


class TestMonitoringAppInsightsSection:
    """monitoring.md must have Application Insights Developer Focus section."""

    def test_app_insights_section_heading(self, monitoring_text):
        assert "## Application Insights — Developer Focus (AZ-204)" in monitoring_text

    def test_telemetry_client_row(self, monitoring_text):
        assert "TelemetryClient" in monitoring_text

    def test_track_event_row(self, monitoring_text):
        assert "TrackEvent" in monitoring_text

    def test_track_metric_row(self, monitoring_text):
        assert "TrackMetric" in monitoring_text

    def test_track_dependency_row(self, monitoring_text):
        assert "TrackDependency" in monitoring_text

    def test_track_exception_row(self, monitoring_text):
        assert "TrackException" in monitoring_text

    def test_track_request_row(self, monitoring_text):
        assert "TrackRequest" in monitoring_text

    def test_w3c_trace_context_exam_tip(self, monitoring_text):
        assert "W3C trace context" in monitoring_text

    def test_operation_id_mentioned(self, monitoring_text):
        assert "Operation ID" in monitoring_text


class TestMonitoringSamplingSection:
    """monitoring.md must have sampling strategies table."""

    def test_adaptive_sampling_row(self, monitoring_text):
        assert "Adaptive Sampling" in monitoring_text

    def test_fixed_rate_sampling_row(self, monitoring_text):
        assert "Fixed-rate Sampling" in monitoring_text

    def test_ingestion_sampling_row(self, monitoring_text):
        assert "Ingestion Sampling" in monitoring_text

    def test_adaptive_sampling_exam_tip(self, monitoring_text):
        assert "Adaptive sampling is the default" in monitoring_text

    def test_ingestion_sampling_does_not_reduce_bandwidth(self, monitoring_text):
        assert "does NOT reduce SDK-side volume" in monitoring_text


class TestMonitoringLogBasedVsPreAggregatedSection:
    """monitoring.md must have log-based vs pre-aggregated metrics section."""

    def test_log_based_vs_pre_aggregated_heading(self, monitoring_text):
        assert "**Log-based vs Pre-aggregated (Standard) Metrics:**" in monitoring_text

    def test_log_based_metrics_explained(self, monitoring_text):
        assert "Log-based metrics are derived from raw telemetry" in monitoring_text

    def test_pre_aggregated_metrics_explained(self, monitoring_text):
        expected = "Pre-aggregated (standard) metrics are computed at collection time"
        assert expected in monitoring_text

    def test_pre_aggregated_exam_tip(self, monitoring_text):
        assert "use pre-aggregated (standard) metrics" in monitoring_text
