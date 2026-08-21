# MONITORING & OBSERVABILITY

## Core Observability Services

| Service | Type | Best For | Key Feature |
| --- | --- | --- | --- |
| **Cloud Monitoring** | Metrics, dashboards, alerting | Resource and application metrics, uptime checks, alerting policies | Metrics Explorer, dashboards, uptime checks, alert policies with notification channels |
| **Cloud Logging** | Log aggregation, search, sinks | Centralised log collection, exclusion, export | Log Explorer, log-based metrics, exclusion filters, export sinks to Pub/Sub, GCS, BigQuery |
| **Cloud Trace** | Distributed tracing | Latency analysis across service boundaries | Latency distribution, trace spans, integration with Cloud Run, GKE, App Engine |
| **Cloud Profiler** | CPU and memory profiling | Production performance analysis without stopping service | CPU and heap profiles, flame graphs, low overhead agent |
| **Cloud Debugger** | Production state inspection | Inspect variables and call stack without stopping the service | Snapshot and logpoints, no code redeploy needed |

> **Exam tip:** Cloud Monitoring answers "what is happening with my resources and apps right now" — metrics, dashboards, uptime. Cloud Logging answers "what did my system emit" — log aggregation, query, export. Cloud Trace answers "which call is slow" — distributed latency across microservices. Cloud Profiler answers "where is CPU/memory going" — production flame graphs. Cloud Debugger answers "what are the variables at this line" — without redeploying or stopping the service.

## Cloud Monitoring Metrics

| Metric Type | Scope | Use Case |
| --- | --- | --- |
| **System metrics** | Resource-level (CPU, memory, disk, network) | Infrastructure health monitoring |
| **Custom metrics** | Application-defined | Business KPIs, queue depth, custom events |
| **Log-based metrics** | Derived from Cloud Logging | Count/aggregation of log entries matching a filter |
| **Uptime checks** | Endpoint reachability | HTTP, TCP, HTTPS, gRPC probes from multiple locations |

> **Exam tip:** Uptime checks are the most direct answer when the requirement mentions verifying that a service is reachable from outside — they probe the endpoint from multiple global locations and trigger alerts on failure. Custom metrics let you monitor application-level signals (e.g. order count, queue depth) that are not exposed by system metrics.

## Alerting

| Component | Detail |
| --- | --- |
| **Alert policy** | Condition on a metric or log-based metric; threshold or absence trigger |
| **Notification channels** | Email, SMS, PagerDuty, Slack, Pub/Sub, webhook |
| **Alerting on logs** | Log-based metric → alert policy — count of matching log entries exceeding threshold |
| **Multi-condition alerts** | Combine multiple conditions with AND/OR logic |

> **Exam tip:** Alerting policies can be based on metrics (numeric thresholds) or on the absence of metric data (detects a stopped exporter). Log-based metrics let you alert on specific log patterns — for example, count of error log entries exceeding a threshold in a time window.

## Cloud Logging Architecture

| Component | Role |
| --- | --- |
| **Log sinks** | Export log entries to Cloud Storage, BigQuery, Pub/Sub |
| **Exclusion filters** | Drop noisy log entries before ingestion billing |
| **Log-based metrics** | Create counter or distribution metrics from log filters |
| **Log Explorer** | Query and analyse log entries (routing, severity, resource) |

> **Exam tip:** Log sinks are the answer when the requirement mentions exporting logs for long-term retention (Cloud Storage), analysis at scale (BigQuery), or streaming to a SIEM (Pub/Sub). Exclusion filters reduce ingestion cost by dropping high-volume, low-value logs before they are billed — use them for verbose debug logs in production.

## Cloud Trace

| Feature | Detail |
| --- | --- |
| **Latency distribution** | View the distribution of request latency across a service |
| **Trace spans** | Break down latency by downstream call (HTTP, gRPC, Cloud Run, GKE) |
| **Integration** | Auto-instrumented for Cloud Run, App Engine, GKE (with proxy); instrumented SDK for custom code |

> **Exam tip:** Cloud Trace is the correct answer when the requirement mentions identifying latency bottlenecks across microservices. It does not replace application-level logging — it complements it with end-to-end latency context.

## Cloud Profiler and Debugger

| Service | Use Case |
| --- | --- |
| **Cloud Profiler** | Find where CPU or memory is being consumed in a running service; low-overhead agent, flame graph output |
| **Cloud Debugger** | Inspect the state (variables, call stack) of a running production service at a specific point — snapshot (one-time) or logpoint (log expression without stopping) |

> **Exam tip:** Cloud Profiler is chosen when the requirement mentions understanding where CPU time or memory is being spent in a production service. Cloud Debugger is chosen when the requirement mentions inspecting production state without redeploying — snapshots capture the state at a point, logpoints let you log expressions without modifying code or redeploying.
