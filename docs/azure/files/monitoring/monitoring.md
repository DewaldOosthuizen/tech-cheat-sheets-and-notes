# Monitoring & Observability

## Azure Monitor Ecosystem

```mermaid
--8<-- "azure/diagrams/monitoring/azure-monitor-ecosystem.mmd"
```

## Key Services

| Service | Purpose | Key Concepts |
| --- | --- | --- |
| **Azure Monitor** (umbrella: Activity Log, Metrics, Alerts, Diagnostic Settings, Insights family) | Central telemetry platform | Metrics, Logs, Alerts, Workbooks |
| **Log Analytics Workspace** (contains: KQL engine, retention tiers; fed via Diagnostic Settings) | Store and query logs (KQL) | Retention (30–730 days), data export |
| **Application Insights** (contains: Live Metrics, Availability Tests, Dependency Tracking, Smart Detection) | APM for apps | Live metrics, dependency tracking, availability tests |
| **VM Insights** | Perf + map for VMs | Relies on Log Analytics agent/AMA |
| **Container Insights** | AKS monitoring | Pod/node metrics, log collection |
| **Network Watcher** | Network diagnostics | Packet capture, flow logs, connection monitor |
| **Azure Advisor** | Best practice recommendations | Cost, security, reliability, performance |
| **Service Health** | Azure platform health | Planned maintenance, incidents |
| **Resource Health** | Your resource health | Is *your* resource healthy right now |

## Alerts

| Type | Trigger | Use Case |
| --- | --- | --- |
| **Metric Alert** | Threshold on metric value | CPU > 80%, response time > 2s |
| **Log Alert** | KQL query result count/value | Error count in last 5 min > 10 |
| **Activity Log Alert** | Azure control-plane events | Who deleted a resource, policy assignment (Activity Log is a sub-component of Azure Monitor, routed to Log Analytics via Diagnostic Settings) |
| **Smart Detection** | AI-based anomaly in App Insights | Failure rate spikes, perf degradation |

> **Action Groups** decouple alert routing from alert rules. One action group → multiple rules.

> **Exam tip:** When an answer option names a specific sub-component (e.g. Activity Log,
> Live Metrics, Smart Detection), prefer it over the umbrella service (e.g. Azure Monitor,
> Application Insights). Select the umbrella only when the sub-component is absent from
> the options.

## Diagnostic Settings

- Send to: **Log Analytics Workspace**, **Storage Account**, **Event Hub**, **Partner solution**
- Configure per resource (or via Azure Policy at scale)
- Categories: AllMetrics, Audit, Operational, **Activity Log** (control-plane events), etc.
- Activity Log is a sub-component of Azure Monitor routed to Log Analytics Workspace via Diagnostic Settings — not a standalone service.

| Service | Type | Best For | Key Feature |
| --- | --- | --- | --- |
| **Log Analytics Workspace** (fed via Diagnostic Settings; contains Activity Log data, KQL engine) | Destination | Query, alerting, dashboards | Kusto (KQL) queries; retention config |
| **Azure Storage Account** | Destination | Long-term archive, compliance | Low cost; no real-time query |
| **Event Hub** | Destination | SIEM integration, streaming | Real-time export to Splunk, Sentinel |
| **Partner Solutions** | Destination | Third-party observability | Datadog, Elastic natively integrated |

> **Exam tip:** Diagnostic Settings must be configured per resource. Use Azure Policy with DeployIfNotExists effect to automatically configure diagnostic settings at scale across subscriptions.

> **Exam tip (AZ-500):** Diagnostic Settings are the bridge between Azure
> resources and Microsoft Sentinel. Route Activity Logs, Entra audit logs, and
> resource diagnostic logs to a Log Analytics Workspace that Sentinel reads from.
> Without Diagnostic Settings configured, Sentinel data connectors receive no data.

### Diagnostic Settings Routing

```mermaid
--8<-- "azure/diagrams/monitoring/diagnostic-settings-routing.mmd"
```

> **Exam tip:** Activity Log is a sub-component of Azure Monitor, not a standalone service.
> Route it to Log Analytics Workspace via Diagnostic Settings to enable KQL querying and
> long-term retention. For AZ-104, use Azure Policy (DeployIfNotExists) to enforce
> Diagnostic Settings at scale.

## Log Analytics Retention & Cost Tiers

| Tier | Type | Best For | Key Feature |
| --- | --- | --- | --- |
| **Analytics** | Interactive (30–730 days) | Active investigation, alerting | Full KQL, per-GB ingestion cost |
| **Basic** | Interactive (8 days) | High-volume, low-value logs | Limited KQL, lower per-GB cost |
| **Archive** | Cold (up to 12 years) | Compliance, audit, cold storage | Search jobs only, lowest per-GB cost |

> **Exam tip:** Choose Basic tier for noisy, rarely queried logs (e.g. verbose diagnostics)
> to reduce cost. Use Archive when retention beyond 730 days is required for compliance;
> queries against archived data run as Search Jobs, not interactive KQL.

## Azure Monitor Agents

| Service | Layer | Scope | Use Case | Key Feature |
| --- | --- | --- | --- | --- |
| **Azure Monitor Agent (AMA)** | OS-level | VM, VMSS, Arc | Recommended; replaces legacy agents | Data Collection Rules (DCR); multi-workspace |
| **MMA / OMS Agent (legacy)** | OS-level | VM | Being retired (Aug 2024) | Single workspace; no DCR support |
| **Diagnostics Extension (WAD/LAD)** | OS-level | VM | Guest OS metrics/logs to Azure Storage | XML config; not Log Analytics native |
| **Dependency Agent** | Network | VM | Service Map, VM Insights connectivity | Requires AMA or MMA; maps processes |

> **⚠️ Deprecation warning:** The MMA/OMS (Microsoft Monitoring Agent / OMS Agent) is retired
> (August 2024). Migrate all VM monitoring deployments to **Azure Monitor Agent (AMA)** with
> Data Collection Rules (DCR).

> **Exam tip:** The MMA/OMS agent is retired. For AZ-104, always choose AMA with Data Collection Rules for new deployments. DCRs allow filtering and routing to multiple destinations.

### Agent Selection Decision Flow

```mermaid
--8<-- "azure/diagrams/monitoring/agent-selection-decision-flow.mmd"
```

## Application Insights — Developer Focus (AZ-204)

| Service | Type | Best For | Key Feature |
| --- | --- | --- | --- |
| TelemetryClient | SDK Class | Manual, code-level telemetry instrumentation | Root class for all manual Track* calls; initialised once per app with the instrumentation key or connection string |
| TrackEvent | SDK Method | Custom business events (user actions, domain milestones) | Recorded with custom properties and measurements; queryable in Logs as `customEvents` table |
| TrackMetric | SDK Method | Custom numeric metrics (queue depth, cache hit rate) | Aggregated before sending to reduce bandwidth; queryable in `customMetrics` table |
| TrackDependency | SDK Method | Outbound calls (HTTP, SQL, Redis, Service Bus) | Records target, duration, and success; links to the parent operation via Operation ID |
| TrackException | SDK Method | Caught exceptions requiring structured telemetry | Records exception type, message, and stack trace; queryable in `exceptions` table |
| TrackRequest | SDK Method | Server-side request telemetry for non-auto-instrumented hosts | Records URL, duration, response code, and success; queryable in `requests` table |

> **Exam tip:** Application Insights injects W3C trace context headers (`traceparent` / `tracestate`) on outbound calls, propagating the Operation ID across service boundaries. Use `TrackDependency` for any outbound HTTP, database, or messaging call not already captured by auto-instrumentation. All telemetry sharing the same Operation ID is linked in the end-to-end transaction view — this is the distributed tracing model tested by AZ-204.

| Service | Type | Best For | Key Feature |
| --- | --- | --- | --- |
| Adaptive Sampling | Sampling Strategy | Default SDK behaviour; general-purpose telemetry volume control | Dynamically adjusts the sampling rate to keep volume within the daily telemetry cap; no configuration required |
| Fixed-rate Sampling | Sampling Strategy | Consistent, predictable sample fraction for statistical analysis | Configured in the SDK; client and server sampling rates must match for accurate correlation |
| Ingestion Sampling | Sampling Strategy | Last-resort volume reduction at the Azure ingestion endpoint | Applied after telemetry arrives at Azure — does NOT reduce SDK-side volume or network bandwidth |

> **Exam tip:** Adaptive sampling is the default and requires no configuration — it adjusts automatically to stay within volume limits. Ingestion sampling is a portal-side filter applied after data arrives at Azure; it does not reduce bandwidth or SDK overhead. Fixed-rate sampling is used when you need a consistent, known fraction for statistical queries. If the exam asks which strategy reduces SDK-side bandwidth, the answer is adaptive or fixed-rate sampling — NOT ingestion sampling.

**Log-based vs Pre-aggregated (Standard) Metrics:**

Log-based metrics are derived from raw telemetry stored in the Logs table — they support arbitrary KQL queries and full-dimension filtering but have higher alert evaluation latency (query must run on each evaluation). Pre-aggregated (standard) metrics are computed at collection time and stored in the Metrics store — they support near real-time alerting and are lower cost to query.

> **Exam tip:** For alerting on response time, failure rate, or request count, use pre-aggregated (standard) metrics — they support near real-time alerts and are cheaper to evaluate. Log-based metric alerts run as KQL queries on the Logs table and have higher latency; use them only when you need custom dimensions or filters not available in standard metrics.

## Application Insights Built-in Features

Application Insights ships a set of built-in tools on top of the core telemetry pipeline.
Each solves a distinct observability problem — the exam tests which feature to choose
for a given scenario.

```mermaid
--8<-- "azure/diagrams/monitoring/app-insights-features-overview.mmd"
```

| Feature | What it does | Key detail |
| --- | --- | --- |
| **Application Map** | Automatically visualizes the topology of your distributed application — each component (App Service, SQL, Service Bus, external calls) becomes a node; edges show call volume, response times, and failure rates | Built from `TrackDependency` telemetry; no configuration required after instrumentation |
| **Live Metrics** | Real-time telemetry stream with sub-second latency (requests/sec, failure rate, CPU, dependency calls) | Read-only stream; does NOT store data; ideal for watching a deployment roll out |
| **Availability Tests** | Scheduled external URL probes from up to 16 Azure PoP locations worldwide | Three probe types: URL ping (basic), Standard (TLS check, custom headers), Custom TrackAvailability (scripted multi-step via Azure Functions) |
| **Smart Detection** | AI-powered anomaly detection that fires alerts when failure rates, response times, or dependency call patterns deviate from the learned baseline | Zero configuration; alert rules created automatically; separate from Metric Alerts |
| **Profiler** | Attaches a sampling profiler to live production workloads and captures CPU flame graphs (call stacks) without code changes | Requires App Service or AKS with Application Insights agent; data retained 5 days |
| **Snapshot Debugger** | Captures a memory snapshot (locals, call stack, parameters) the moment a handled or unhandled exception is thrown in production | Requires the Snapshot Collector SDK NuGet package or Application Insights agent; snapshots retained 15 days |
| **Usage Analytics** | Three interconnected tools — **Users** (unique users over time), **Sessions** (session count and duration), **Events** (custom `TrackEvent` call frequency) | All backed by `customEvents` and `pageViews` tables; supports cohort and funnel analysis |

### Application Map — How it works

Application Map is built entirely from the `cloud_RoleName` property stamped on every telemetry
item and from `TrackDependency` calls (auto-instrumented HTTP, SQL, gRPC, Service Bus, etc.).
Each unique role becomes a node. Edges carry aggregated call count, average duration, and
failure percentage. A red node indicates a failure rate above the component's learned baseline.

You can override the node name via `TelemetryClient.Context.Cloud.RoleName` — this is how
multiple instances of the same service appear as a single node rather than N separate nodes.

> **Exam tip:** Application Map is the correct answer when the question asks how to visualize
> dependencies between microservices or identify which component in a distributed system is
> causing elevated failure rates. It is NOT a manually configured diagram — it is generated
> automatically from instrumentation telemetry. Smart Detection is for anomaly alerting, not
> topology visualization.

### Availability Tests — Probe Types

| Type | Scope | How to create | Max locations |
| --- | --- | --- | --- |
| URL Ping | Single HTTP/HTTPS endpoint | Portal, no code | 16 |
| Standard | Single endpoint + TLS cert validation + custom request headers | Portal, no code | 16 |
| Custom TrackAvailability | Multi-step scripted transaction (login → search → checkout) | Azure Function calling `TelemetryClient.TrackAvailability()` | Unlimited |

> **Exam tip:** Standard availability tests are the correct choice when you need TLS certificate
> expiry alerting or custom HTTP request headers. Use Custom TrackAvailability (via Azure
> Functions) when you need a multi-step, stateful transaction test — for example, a login flow
> that requires session cookies. URL Ping tests do NOT support multi-step flows or
> TLS validation.
