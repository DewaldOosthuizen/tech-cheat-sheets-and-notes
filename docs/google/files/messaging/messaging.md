# MESSAGING & INTEGRATION

## Messaging and Event Services

| Service | Type | Best For | Key Feature |
| --- | --- | --- | --- |
| **Pub/Sub** | Asynchronous messaging | Event ingestion, fan-out, decoupling, streaming pipelines | At-least-once delivery, message ordering per ordering key, push and pull delivery, replay (retention 1–365 days), exactly-once delivery (with subscription-levelack deadline extension) |
| **Eventarc** | Event ingestion and delivery | Bring your own event sources; deliver to Cloud Run, GKE, Workflows, Cloud Functions | Pre-built triggers for GCP event sources; third-party event sources; CloudEvents schema |
| **Workflows** | Workflow orchestration (serverless) | Multi-step sequences calling GCP APIs and services | YAML-based definitions, retry policies, GET/POST/HTTP calls, parallel execution |
| **Cloud Tasks** | HTTP task queue | Managed retryable HTTP work, rate limiting, dispatch | Task queue with retry, HEAD/GET/POST/PUT/PATCH/DELETE targets, rate controls, dispatch deadline |
| **API Gateway** | API management | REST API front-end with auth, quotas, traffic management | OpenAPI spec, request/response transformation, API keys, Cloud Monitoring integration |

> **Exam tip:** Choose Pub/Sub when the requirement mentions high-throughput asynchronous messaging, event ingestion, or decoupled producers and consumers with replay capability. Choose Eventarc when the requirement mentions ingesting events from GCP services or third-party SaaS and delivering them to serverless targets with CloudEvents formatting. Choose Workflows when the requirement mentions orchestrating a multi-step process that coordinates calls to GCP APIs or HTTP endpoints — it is YAML-based and serverless, not a code-based orchestrator. Choose Cloud Tasks when the requirement mentions dispatching and retrying HTTP requests with rate limiting — it is a managed Task Queue for HTTP targets. Choose API Gateway when the requirement mentions exposing a REST API with request validation, API keys, and quota enforcement.

## Pub/Sub Characteristics

| Feature | Detail |
| --- | --- |
| **Delivery guarantee** | At-least-once (default); exactly-once with subscription-level acknowledgement deadline extension and dead-lettering |
| **Ordering** | Ordering keys — messages with the same ordering key are delivered in order; one ordering key per publisher/ subscriber combination |
| **Retention and replay** | Retain acknowledged messages for 1–365 days; replay by seeking the subscription cursor |
| **Push vs pull** | Push — Pub/Sub HTTP pushes messages to subscribers; Pull — subscriber polls with lease management |
| **Dead-lettering** | Messages that exceed max delivery attempts or dead-letter explicitly move to a dead-letter topic |

> **Exam tip:** Pub/Sub ordering keys guarantee per-key FIFO ordering — but only within a single publisher and subscriber; ordering is not global. For global ordering, you must partition by ordering key and process each partition sequentially. Exactly-once delivery is supported with additional configuration — it is not the default; the default is at-least-once with possible duplicates, so subscribers should be idempotent.

## Eventarc

| Feature | Detail |
| --- | --- |
| **GCP event sources** | Pre-built triggers for Cloud Storage, Pub/Sub, Firestore, BigQuery, and many other GCP services |
| **Third-party events** | Partner and custom event sources via CloudEvents schema |
| **Targets** | Cloud Run, GKE (with CloudEvents sink), Cloud Functions, Workflows |
| **CloudEvents** | Standardised event format (type, source, id, subject, data) |

> **Exam tip:** Eventarc is the answer when the requirement mentions reacting to GCP service events (e.g. a file uploaded to Cloud Storage, a Firestore document created) without writing custom polling or trigger integration — Eventarc provides pre-built triggers for many GCP services. Eventarc uses CloudEvents as the standard event schema, making it interoperable with non-GCP consumers.

## Workflows

| Feature | Detail |
| --- | --- |
| **Definition** | YAML-based workflow definition — steps, conditions, retries, parallelism |
| **Integration** | Call Google Cloud APIs (Compute Engine, Cloud SQL, BigQuery, etc.), HTTP endpoints, serverless targets |
| **State management** | Built-in state; results from one step can feed the next |
| **Error handling** | Retry policies, conditional error branches, exception handling |

> **Exam tip:** Workflows is the answer when the requirement mentions orchestrating a multi-step business process that spans GCP services and/or HTTP endpoints in a serverless, YAML-defined workflow — not a message-driven choreographed architecture. It is not a Kubernetes-native orchestrator (use Cloud Composer / Airflow for that) and not a code-based function orchestrator (use Cloud Functions or Cloud Run with Dapr or custom logic).

## Cloud Tasks

| Feature | Detail |
| --- | --- |
| **Task queue** | Queues of HTTP tasks with retry, rate limiting, and dispatch deadline |
| **Target** | Any HTTP endpoint — can be Cloud Run, GKE, Compute Engine, or external |
| **Rate controls** | Concurrency limit, rate limit (tasks per second) |
| **Retry** | Configurable retry count, max interval, min interval, backoff |

> **Exam tip:** Cloud Tasks is the answer when the requirement mentions a managed queue for retryable HTTP work — for example, sending emails, calling webhooks, or dispatching jobs to a fleet of workers with rate control. Unlike Pub/Sub, Cloud Tasks targets a specific HTTP endpoint directly and supports sophisticated retry and rate-limit configurations.

## Pub/Sub vs Eventarc vs Cloud Tasks

| Dimension | Pub/Sub | Eventarc | Cloud Tasks |
| --- | --- | --- | --- |
| **Model** | Asynchronous messaging — producer pushes to topic, subscribers consume | Event ingestion — sources fire events, Eventarc routes to targets | HTTP task queue — enqueue HTTP requests, workers dequeue and process |
| **Replay** | Yes — seek subscription cursor | No — events are delivered once | No — tasks are consumed and deleted on success or dead-lettered |
| **Topologies** | Many-to-many pub/sub | Many-to-one or many-to-many event routing | One-to-one task dispatch |
| **Protocols** | gRPC streaming, HTTP push/pull | CloudEvents over HTTP/webhook | HTTP target (outbound from Cloud Tasks) |
| **Best for** | High-throughput event streaming, replay, buffering | Reacting to GCP or SaaS events with pre-built triggers | Dispatching and retrying HTTP work with rate control |

> **Exam tip:** The three services are complementary, not competing. Pub/Sub is for high-volume event streaming with replay. Eventarc is for reacting to GCP and SaaS events with minimal glue code. Cloud Tasks is for dispatch and retry of HTTP work. If the requirement mentions replay, choose Pub/Sub. If it mentions reacting to a GCP service event without custom polling, choose Eventarc. If it mentions dispatching HTTP requests with retry and rate control, choose Cloud Tasks.
