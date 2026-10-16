# MESSAGING & INTEGRATION

## Messaging Service Comparison

| Service | Type | Best For | Key Feature |
| --- | --- | --- | --- |
| **SQS** | Queue | Decoupled point-to-point messaging | At-least-once delivery, DLQ, FIFO option |
| **SNS** | Pub/sub | Fan-out notifications to multiple subscribers | Push to SQS, Lambda, email, HTTP endpoints |
| **EventBridge** | Event bus | Event-driven routing from AWS services and SaaS | Schema registry, cross-account event routing |
| **Step Functions** | Orchestration | Multi-step serverless workflow coordination | State machine, visual workflow, error handling |
| **Kinesis Data Streams** | Streaming | Real-time data ingestion at high throughput | Ordered, replayable, shard-based |
| **Kinesis Firehose** | Streaming ETL | Load streaming data to S3, Redshift, OpenSearch | Fully managed, no consumers to write |

> **Exam tip:** SQS decouples producers and consumers — choose it when
> reliability and retry matter. SNS fans out to multiple endpoints. Use
> EventBridge when events originate from AWS service changes or third-party SaaS.
> Step Functions orchestrates workflows that span multiple Lambda functions or
> AWS services.

## Messaging Decision Flow

```mermaid
--8<-- "aws/diagrams/messaging/decision-flow.mmd"
```

## SQS Queue Types

| Type | Ordering | Deduplication | Key Feature |
| --- | --- | --- | --- |
| **Standard** | Best-effort | Not guaranteed | Nearly unlimited throughput |
| **FIFO** | Strict | Built-in (5 min window) | Exactly-once processing, 300 TPS default |

> **Exam tip:** SQS FIFO queues guarantee order and deduplication but have a
> throughput cap. Standard queues offer higher throughput with best-effort
> ordering. Lambda cannot poll FIFO queues in batches larger than 10.
