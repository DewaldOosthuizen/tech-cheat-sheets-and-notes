# Messaging & Integration

## Service Comparison

| Service | Pattern | Ordering | Replay | Use Case |
| --- | --- | --- | --- | --- |
| **Service Bus Queue** | Message (P2P) | FIFO optional | No | Reliable command delivery |
| **Service Bus Topic** | Message (pub/sub) | FIFO optional | No | Fan-out with filters |
| **Event Grid** | Event (reactive) | No | No | Resource change reactions |
| **Event Hub** | Stream (telemetry) | Per-partition | Yes (retention) | IoT, log ingestion |
| **Storage Queue** | Message (P2P) | Best-effort | No | Simple, cheap async |

> **SLA note:** Service Bus SKUs are used when the requirement explicitly calls
> for enterprise messaging guarantees and broker features. Storage Queue is cost-
> efficient and simple, but exam scenarios that stress stronger delivery contracts
> generally point to Service Bus.

## Decision Flowchart

```mermaid
--8<-- "azure/diagrams/messaging/decision-flowchart.mmd"
```

## Logic Apps vs Azure Functions vs Durable Functions

| Service | Best For | Trigger Model | State | Pricing Model |
| --- | --- | --- | --- | --- |
| **Logic Apps** | Low-code workflow automation, SaaS connectors | Event / Schedule / HTTP | Stateful (built-in) | Per-action / consumption |
| **Azure Functions** | Stateless compute, event-driven microservices | Many triggers (HTTP, queue, timer, etc.) | Stateless by default | Consumption / Premium |
| **Durable Functions** | Long-running, stateful orchestrations in code | Orchestrator / Activity / Entity | Stateful (via storage) | Consumption (includes storage cost) |

```mermaid
--8<-- "azure/diagrams/messaging/logic-apps-vs-azure-functions-vs-durable-functions.mmd"
```

> **Exam tip:** Choose Logic Apps when the requirement mentions low-code orchestration or pre-built SaaS connectors. Choose Durable Functions for long-running, stateful, or fan-out/fan-in patterns written in code. Choose Azure Functions for stateless, event-driven compute with no orchestration requirement.

## Exam Tips

> **Dead-Letter Queues (DLQ):** Messages are moved to the DLQ when TTL expires, max delivery count is exceeded, or the message is explicitly dead-lettered by the receiver. Monitor DLQ depth via Azure Monitor metrics or Service Bus Explorer — a growing DLQ indicates poison messages or consumer failures.

> **Sessions & Partitioning:** Enable sessions on a Service Bus queue/topic to guarantee ordered processing per session key — all messages with the same session ID are delivered to the same consumer in order. Enable partitioning to distribute load across multiple message brokers and increase throughput; note that sessions and partitioning can be combined but partitioned entities have a 1 GB size limit per partition.

> **Consumer Groups & Retention (Event Hub):** Each consumer group maintains its own independent offset/cursor, allowing multiple downstream systems to read the same stream at their own pace without interference. Configure retention (1–90 days, up to 7 days on Standard tier) to enable event replay for late-joining consumers, reprocessing after failures, or auditing.

> **Avro & Schema Registry (Event Hub):** Event Hubs Capture writes events to Azure Blob or
> Data Lake Storage in **Avro** format by default — a compact binary format with embedded schema.
> Event Hubs Schema Registry enforces producer/consumer schema contracts (Avro or JSON Schema),
> preventing incompatible messages from breaking downstream consumers. Choose Avro when
> the requirement mentions Event Hubs Capture, Schema Registry, or compact binary serialisation
> for streaming pipelines.

## Service Bus vs Storage Queues

| Service | Type | Best For | Key Feature |
| --- | --- | --- | --- |
| **Storage Queue** | Simple queue | Large volume, simple FIFO | Up to 500 TB; HTTP-based; minimal features |
| **Service Bus Queue** | Broker queue | Reliable delivery, ordering | Dead-letter queue; duplicate detection; sessions |
| **Service Bus Topic** | Pub/sub | Fan-out to multiple consumers | Multiple subscriptions per topic; filters |

> **Exam tip:** Use Service Bus when you need message ordering, dead-lettering, duplicate detection, or transactions. Use Storage Queue when you need >80 GB storage, simple REST polling, or audit logs.

### Service Bus Namespace SKUs

| Service | Type | Best For | Key Feature |
| --- | --- | --- | --- |
| **Basic SKU** | Namespace tier | Simple queues only | No topics, sessions, or duplicate detection |
| **Standard SKU** | Namespace tier | Variable throughput | Topics, subscriptions, shared capacity |
| **Premium SKU** | Namespace tier | Predictable performance | Dedicated capacity units; VNet integration; large messages up to 100 MB |

> **Exam tip:** Premium SKU is required for VNet service endpoints, private endpoints, and geo-disaster recovery (Geo-DR paired namespaces).

> **SLA note:** Messaging scenarios that emphasize strict reliability,
> predictable throughput, and isolation generally indicate Service Bus Premium.

## Message Size Limits

| Service | Type | Best For | Key Feature |
| --- | --- | --- | --- |
| **Service Bus** | Basic / Standard | Fixed-size command or control messages | Max **256 KB** per message; fixed, not configurable |
| **Service Bus** | Premium | Large payload or document delivery | Default **1 MB**; configurable up to **100 MB** per message via namespace setting |
| **Storage Queue** | Standard (no sub-tiers) | Simple async task offloading | Max **64 KB** per message; fixed, not configurable |
| **Event Hubs** | Basic / Standard | High-throughput telemetry and log streaming | Max **1 MB** per individual event or batch; fixed ceiling; Basic/Standard namespaces cannot be upgraded to Premium |
| **Event Hubs** | Premium / Dedicated | Large event streaming | Default **1 MB**; increase to **20 MB** available via Azure support request |
| **Event Grid** | All resource types | Lightweight reactive event notification | Max **1 MB** per event or batch; fixed; events > 64 KB billed as multiple 64 KB units (e.g. 130 KB event = 3 billing units) |

> **Exam tip:** Service Bus Premium is the only tier that supports messages beyond 256 KB —
> default 1 MB, configurable up to 100 MB. Storage Queue has the tightest cap at 64 KB
> and is unsuitable for large payloads. Event Hubs and Event Grid both cap at 1 MB but
> serve different patterns: Event Hubs is a partitioned stream (ordered per partition,
> replay-capable); Event Grid is a push-delivery notification bus (no replay, no ordering
> guarantee). If a scenario requires messages larger than 256 KB with dead-lettering and
> ordering, the answer is Service Bus Premium.

## Azure Functions Trigger Bindings (AZ-204)

| Service | Binding | Direction | Key Feature |
| --- | --- | --- | --- |
| Service Bus | ServiceBusTrigger | In (trigger) | Invoked on message arrival; supports sessions (`isSessionsEnabled: true`) for FIFO ordering |
| Service Bus | ServiceBusOutput | Out (output) | Sends a message to a queue or topic from within a function |
| Event Hubs | EventHubTrigger | In (trigger) | Receives events as an array (batch) by default; one function invocation per batch per partition |
| Event Hubs | EventHubOutput | Out (output) | Publishes events to an event hub; supports batch send |
| Event Grid | EventGridTrigger | In (trigger) | Invoked by Event Grid push delivery; handles validation handshake automatically |
| Event Grid | EventGridOutput | Out (output) | Publishes custom events to an Event Grid topic |

> **Exam tip:** `ServiceBusTrigger` with `isSessionsEnabled: true` processes messages in session order (FIFO within a session) — required when message ordering is a stated requirement. `EventHubTrigger` delivers events as a batch array by default — iterate the array inside the function to maximise throughput and avoid partial-batch re-processing.

## Event Grid Schema vs CloudEvents Schema

| Service | Type | Best For | Key Feature |
| --- | --- | --- | --- |
| Event Grid Schema | Event Schema | Azure-native event routing; no interoperability requirement | Default schema for all Azure first-party event sources; uses `eventType`, `subject`, `data` fields |
| CloudEvents 1.0 Schema | Event Schema | Cross-platform or multi-cloud event pipelines; CNCF compliance | Vendor-neutral CNCF standard; uses `type`, `source`, `datacontenttype` fields; compatible with non-Azure consumers |

> **Exam tip:** Choose CloudEvents 1.0 schema when the requirement mentions cross-platform interoperability, CNCF compliance, or integration with non-Azure event consumers. Event Grid schema is the Azure-native default and requires no additional configuration — choose it for pure Azure-to-Azure routing.

### Messaging Decision Flow

```mermaid
--8<-- "azure/diagrams/messaging/messaging-decision-flow.mmd"
```

### Service Bus SKU Decision Flow

```mermaid
--8<-- "azure/diagrams/messaging/service-bus-sku-decision-flow.mmd"
```
