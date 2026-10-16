# Compute

## Compute Options

| Service | Type | Use Case |
| --- | --- | --- |
| **Azure Virtual Machines** | IaaS | Full OS control, lift-and-shift |
| **VM Scale Sets (VMSS)** | IaaS autoscale | Stateless workloads needing horizontal scale |
| **Azure App Service** | PaaS | Web apps, APIs, mobile backends |
| **Azure Functions** | Serverless | Event-driven, short-duration tasks |
| **Azure Container Instances (ACI)** | Container | Quick burst containers, no orchestration |
| **Azure Kubernetes Service (AKS)** | Container orchestration | Microservices, complex container workloads |
| **Azure Container Apps** | Serverless containers | Microservices without K8s complexity |
| **Azure Batch** | HPC jobs | Large parallel compute jobs |
| **Azure Spring Apps** | PaaS Java | Spring Boot microservices |
| **Azure Service Fabric** | Microservices runtime | Stateful/stateless distributed services and containers |

> **Exam tip:** SLA guarantee requirements usually eliminate dev/test tiers or
> single-instance designs. When the scenario says "guaranteed uptime", choose
> a production tier and design for redundancy (multiple instances/zones/regions).

## Compute Decision Flow

```mermaid
--8<-- "azure/diagrams/compute/compute-decision-flow.mmd"
```

> **Exam tip:** Start with OS control (VM), then container vs. code, then
> serverless vs. always-on. ACA is the default for containerised
> microservices when you do not need full Kubernetes API access.

## App Service Plans (Tiers)

| Tier | Category | Instances | Deployment Slots | Key Features |
| --- | --- | --- | --- | --- |
| **Free / Shared (F1/D1)** | Dev/Test | Shared | None | No SLA, no custom domain SSL, shared infrastructure |
| **Basic (B1–B3)** | Dev/Test | Dedicated, up to 3 (manual) | None | Dedicated VMs, manual scale only, no auto-scale |
| **Standard (S1–S3)** | Production | Up to 10 (auto-scale) | 5 | Auto-scale, custom domain, SSL certificates |
| **Premium v2 (P1v2–P3v2)** | Production | Up to 30 (auto-scale) | 20 | VNet integration, higher RAM/CPU, cost-optimised vs. v3 |
| **Premium v3 (P1v3–P3v3)** | Production | Up to 30 (auto-scale) | 20 | Zone redundancy, highest RAM/CPU ratio, VNet integration |
| **Isolated v2 / ASEv3 (I1v2–I3v2)** | Mission-critical | Up to 100 | 20 | Dedicated App Service Environment, full VNet isolation, no public endpoint |

> Deployment slots only available on **Standard** tier and above.

> **SLA note:** Free/Shared tiers carry no SLA. Basic provides a single-instance SLA only.
> Standard and above with two or more instances provide the full 99.95% SLA.

> **Exam tip:** Tier selection signal chain — start from the strongest constraint and work down.
>
> VNet isolation / regulatory compliance (PCI-DSS, HIPAA, dedicated egress IP) → **Isolated v2 (ASEv3)**.
> ASEv3 is the current-generation App Service Environment; it removes the forced-tunnelling requirement of ASEv2.
>
> VNet integration, 20 deployment slots, or zone redundancy required → **Premium v3** (P1v3–P3v3).
> Premium v2 is the cost-optimised alternative where zone redundancy is not required.
>
> Auto-scale and up to 5 deployment slots with no VNet requirement → **Standard** (S1–S3).
>
> Dedicated compute, predictable load, no auto-scale needed → **Basic** (B1–B3).
>
> No production SLA, pure development or prototype → **Free / Shared** (F1/D1).

> **Exam tip:** Deployment slots run inside the same App Service Plan. On slot swap, IIS/Node warm-up completes before traffic is routed — eliminating cold starts. Sticky (slot) settings are NOT swapped; non-sticky settings are swapped with the slot. Use `routingRules` to send a percentage of production traffic to a staging slot for canary testing. Auto-swap immediately promotes the slot after a successful warm-up — use it for continuous deployment pipelines where manual approval is not required.

### App Service Tier Selection Flow

```mermaid
--8<-- "azure/diagrams/compute/app-service-tier-selection-flow.mmd"
```

## Azure Functions Hosting Plans

| Plan | Scale | Cold Start | Use Case |
| --- | --- | --- | --- |
| **Consumption** | Auto (0 to N) | Yes | Sporadic, unpredictable traffic |
| **Premium** | Pre-warmed instances | No | No cold start, VNet, longer execution |
| **Dedicated (App Service)** | Manual / autoscale | No | Predictable load, reuse existing plan |

> **SLA note:** Consumption is optimized for elastic execution and can include
> cold starts. For strict uptime or latency guarantees, exam scenarios typically
> favour Premium or Dedicated hosting with warm capacity.

## Durable Functions Orchestration Patterns

| Service | Pattern | Use Case | Key Feature |
| --- | --- | --- | --- |
| Durable Functions | Function Chaining | Sequential pipeline — output of one function feeds the next | Guaranteed execution order; state persisted between steps |
| Durable Functions | Fan-out / Fan-in | Parallel processing of multiple work items, then aggregate results | Activity functions run in parallel; orchestrator awaits all completions |
| Durable Functions | Async HTTP API (Human Interaction) | Long-running workflow requiring human approval or external event | Orchestrator suspends; resumes on external event or timer expiry |
| Durable Functions | Eternal Orchestration | Continuous monitoring loop (e.g. price watch, health check) | Uses `ContinueAsNew` to restart the orchestration — avoids history bloat |
| Durable Functions | Timer / Monitor | Polling or scheduled delay within an orchestration | Durable timer via `CreateTimer`; survives app restarts |

> **Exam tip:** Use fan-out/fan-in when work items can be processed in parallel and results must be aggregated. Use eternal orchestration (with `ContinueAsNew`) for recurring monitors — do NOT use a plain `while(true)` loop as it bloats the history. Use human interaction when a workflow must pause for an external approval; the orchestrator suspends via `WaitForExternalEvent` and resumes when the event arrives or a timer expires.

> **Exam tip:** WebJobs (continuous or triggered) run inside an existing App Service Plan and share its compute — no cold start and no separate billing unit. Prefer WebJobs when the workload must run in-process with a web app and you do not want the overhead of a separate Functions host.

## Runtime & Language Fit (Functions vs Logic Apps vs App Service)

| Service | Code Model | Common Languages / Runtime Options | Best Fit |
| --- | --- | --- | --- |
| **Azure Functions** | Code-first serverless functions with triggers/bindings | C#, JavaScript/TypeScript, Python, Java, PowerShell, custom handlers (for other runtimes) | Event-driven workloads and short units of compute |
| **Logic Apps** | Low-code workflow orchestration with connectors | No primary app-language requirement; optional inline code for small transforms; can call Functions for full custom code | Integration workflows, B2B, SaaS orchestration |
| **Azure App Service** | Always-on web/API hosting (code or container) | .NET, Node.js, Java, Python, PHP, Ruby, or custom container images | Web apps and APIs with full framework/runtime control |

```mermaid
--8<-- "azure/diagrams/compute/runtime-language-fit-functions-vs-logic-apps-vs-app-service.mmd"
```

> **Exam tip:** If the requirement starts with "which language can I run?",
> Functions and App Service are runtime-first choices; Logic Apps is primarily
> workflow-first and typically uses connectors plus optional inline code or
> Function calls for custom logic.

## Serverless / Event-Driven Selection

```mermaid
--8<-- "azure/diagrams/compute/serverless-event-driven-selection.mmd"
```

> **Exam tip:** Use Azure Functions (Consumption) for short-lived, stateless, code-first triggers.
> Use Durable Functions (Premium/Dedicated) for stateful orchestration or fan-out patterns.
> Use Logic Apps Consumption for simple enterprise/B2B workflows with low-code connectors.
> Use Logic Apps Standard when you need ISE-like VNet isolation or single-tenant deployment.
> Use Azure Container Apps when execution duration exceeds Functions limits or you need a custom runtime.

## Azure Container Apps vs AKS vs ACI

| Dimension | ACI | ACA | AKS |
| --- | --- | --- | --- |
| **Control plane** | None — single container group | Managed (Envoy/KEDA/Dapr hidden) | Full K8s API access |
| **Scale trigger** | Manual / ARM template | KEDA (HTTP, queue, cron, custom) | HPA / KEDA (self-managed) |
| **Dapr integration** | No | Native sidecar injection | Manual Dapr install |
| **Revision management** | No | Yes — traffic split across revisions | Rolling deploy via K8s |
| **VNet integration** | Yes (inject into subnet) | Yes (environment-level) | Yes (CNI plugin) |
| **Cost model** | Per second, vCPU + memory | Per vCPU-s + memory-s (scale to zero) | Node pool VMs (always on) |
| **Ops overhead** | Minimal | Low | High (cluster upgrades, node pools) |

```mermaid
--8<-- "azure/diagrams/compute/azure-container-apps-vs-aks-vs-aci.mmd"
```

> **Exam tip:** ACA uses KEDA under the hood and supports **scale-to-zero** for HTTP and
> queue-based triggers — similar to Consumption plan Functions but for containerised workloads.
> Choose ACA over Functions when you need a custom runtime, Dapr service invocation, or
> revision-based traffic splitting. Choose AKS when the scenario requires direct Kubernetes
> API access, custom admission webhooks, or specific CNI configuration.
> Choose App Service Containers for simple, single-container web apps that benefit from
> built-in deployment slots and App Service features without microservice overhead.
> Use ACI for one-off batch jobs or CI/CD pipeline steps that need an isolated container burst.

## Azure Service Fabric

Azure Service Fabric is a distributed systems platform for building and operating reliable,
scalable microservices and container applications. Unlike AKS (which orchestrates containers)
or ACA (which hides the runtime), Service Fabric provides a full application model including
service lifecycle, state management, partitioning, and cluster health management.

### Service Programming Models

| Model | Type | Description | Use Case |
| --- | --- | --- | --- |
| **Reliable Services** | Stateless or stateful | First-class SF programming model; stateful services use Reliable Collections (replicated, transactional data structures) | Business logic services that must own and persist partitioned state without an external database |
| **Reliable Actors** | Stateful (actor pattern) | Single-threaded virtual actors; state automatically persisted per actor instance | Per-entity state machines, IoT device shadows, session state at large scale |
| **Guest Executables** | Existing binary | Run any existing executable (Java, Node, Python, .NET) as a SF service without code changes | Lift-and-shift existing processes into a managed cluster without rewriting |
| **Guest Containers** | Container | Run Docker containers as SF services | Containerised workloads that benefit from SF placement policies and health monitoring |

Reliable Collections are the key differentiator: a replicated `IReliableDictionary<K,V>` or
`IReliableQueue<T>` that behaves like an in-memory data structure but is persisted and
replicated across the service's replicas, enabling stateful services with no external database.

### Cluster Types

| Cluster Type | Hosting | Management | Use Case |
| --- | --- | --- | --- |
| **Managed Cluster** | Azure only | Azure manages the underlying VMSS and networking | Recommended for new Azure deployments; simpler lifecycle, node type management via ARM |
| **Classic Cluster** | Azure | Customer manages VMSS, LB, NSG | Legacy; full low-level control; more operational overhead |
| **Standalone Cluster** | On-premises or any cloud | Customer fully managed | Air-gapped or regulatory environments requiring on-premises deployment |

### Cluster Concepts

Fault domains and upgrade domains are the two placement constraints that control availability:

| Concept | What It Represents | Purpose |
| --- | --- | --- |
| **Fault Domain (FD)** | Physical failure boundary (rack, power unit, network switch) | SF spreads replicas across FDs so a hardware failure does not take all replicas of a partition |
| **Upgrade Domain (UD)** | Logical group for rolling upgrades | SF upgrades one UD at a time; services in different UDs continue serving traffic during a cluster upgrade |
| **Node Type** | VMSS-backed pool of identical nodes | Primary node type hosts SF system services; additional node types isolate workload classes |
| **Partition** | Horizontal data shard of a stateful service | Each partition has a primary replica and N secondary replicas; partitioning key range determined at service creation |
| **Replica** | Copy of a partition's state | SF maintains a target replica set size (e.g., 3 or 5); primary handles writes and coordinates replication to secondaries |

### Service Fabric vs AKS vs ACA

| Dimension | Service Fabric | AKS | Azure Container Apps |
| --- | --- | --- | --- |
| **State model** | Built-in Reliable Collections (replicated in-memory) | External (Redis, DB) | External |
| **Programming model** | Reliable Services, Reliable Actors, Guest EXE, containers | Any container | Any container |
| **Cluster management** | Managed cluster (recommended) or classic/standalone | Managed control plane | Fully managed (no cluster) |
| **Partition-local state** | Yes — native, low latency | No | No |
| **Upgrade model** | Rolling upgrade with FD/UD awareness | Rolling deploy, node drain | Revision-based traffic split |
| **Ops overhead** | Medium (cluster health, node types) | High (node pools, add-ons) | Low |
| **Typical workload** | Stateful microservices, actor-per-entity patterns | General container orchestration | Event-driven, serverless containers |

> **Exam tip:** Choose Service Fabric when the requirement explicitly mentions stateful
> microservices with partition-local, low-latency state access — Reliable Collections
> eliminate the need for an external cache or database for hot data. The Reliable Actors
> model is the answer when the scenario describes per-entity state at scale (millions of
> devices, users, or sessions). Service Fabric is also the answer when the question
> mentions running existing executables (Guest Executable model) alongside new services
> in the same cluster with unified health monitoring and placement.
>
> Managed Cluster is the recommended cluster type for new Azure deployments — it removes
> the need to manage the underlying VMSS, load balancer, and NSG directly.
>
> Fault domains and upgrade domains work together: FDs protect against simultaneous
> hardware failure of all replicas; UDs ensure rolling upgrades never take all replicas
> offline at the same time. SF places replicas to maximise FD and UD spread automatically.

## AKS Scaling Mechanisms

| Service | Layer | Scope | Use Case | Key Feature |
| --- | --- | --- | --- | --- |
| **Horizontal Pod Autoscaler (HPA)** | Pod | Namespace | Scale pod replicas based on CPU/memory or custom metrics | Built-in K8s controller; works with KEDA for custom metrics |
| **Cluster Autoscaler** | Node | Node pool | Add or remove VM nodes when pods cannot be scheduled | Integrated with AKS node pools; respects PodDisruptionBudgets |
| **Virtual Nodes (Virtual Kubelet)** | Node (virtual) | Cluster | Burst overflow pods to Azure Container Instances instantly | No node provisioning delay; serverless burst; ACI pricing |

```mermaid
--8<-- "azure/diagrams/compute/aks-scaling-mechanisms.mmd"
```

> **Exam tip:** HPA scales pods; Cluster Autoscaler scales nodes. Virtual Nodes
> (Virtual Kubelet) burst workloads to ACI with no node-provisioning delay — choose
> this when the requirement mentions instant scale-out or cost-optimised spikes.

## CI/CD — Azure Pipelines Agent

| Service | Layer | Scope | Use Case | Key Feature |
| --- | --- | --- | --- | --- |
| **Microsoft-hosted agent** | Managed PaaS | Public internet | Standard builds with no VNet or private resource access | Fresh VM per job; no maintenance; limited to public endpoints |
| **Self-hosted agent** | IaaS / container | Customer VNet | Builds needing private registry, on-prem artifact feeds, or VNet-isolated resources | Agent runs as a service on a VM or container; persists between jobs |

> **Exam tip:** Choose a self-hosted Azure Pipelines agent when the build must access resources
> inside a private VNet (e.g. Azure Container Registry with private endpoint, on-prem NuGet feed,
> or private AKS API server). Microsoft-hosted agents run outside your VNet and cannot reach
> private endpoints without additional networking configuration.

## Azure Container Registry (ACR)

| Service | Type | Use Case | Key Feature |
| --- | --- | --- | --- |
| ACR Basic | Registry SKU | Dev/test image storage; low throughput | Shared capacity; no geo-replication; no content trust |
| ACR Standard | Registry SKU | Production CI/CD pipelines; moderate pull throughput | Increased storage and throughput over Basic; webhook support |
| ACR Premium | Registry SKU | Enterprise multi-region deployments; security-sensitive workloads | Geo-replication, private endpoints, content trust (DCT), dedicated throughput |

> **Exam tip:** Geo-replication is a Premium-only feature that pushes images to paired regions — reduces pull latency and provides regional failover. ACR Tasks automate image builds on `git push` or base-image update without requiring a local Docker daemon. Content trust (Docker Content Trust / Notary) signs images at push time; pull fails unless the image signature is verified — use this for supply-chain security requirements.

## Caching

### Azure Cache for Redis

| Tier | Replication | Clustering | Use Case | Key Feature |
|---|---|---|---|---|
| Basic | No | No | Dev/test only | Single node, no SLA |
| Standard | Yes (primary + replica) | No | Production general | 99.9% SLA, failover |
| Premium | Yes | Yes (up to 10 shards) | High throughput, persistence | VNet, geo-replication, RDB/AOF |
| Enterprise | Yes | Yes (OSS Redis cluster) | Ultra-low latency, RediSearch | Active geo-replication, 99.999% SLA |
| Enterprise Flash | Yes | Yes | Large datasets, cost optimisation | NVMe + DRAM tiering |

> **Exam tip:** Choose Premium when VNet injection or geo-replication is required.
> Choose Enterprise when active-active multi-region or RediSearch/RedisBloom modules are needed.

**Eviction policies (exam-relevant):**

- `volatile-lru` — evict least-recently-used keys that have a TTL set (default safe choice)
- `allkeys-lru` — evict any LRU key (use when all keys are equally expendable)
- `noeviction` — return errors when memory is full (use for session stores where data loss is unacceptable)

#### Tier Selection Decision Flow

```mermaid
--8<-- "azure/diagrams/compute/azure-cache-for-redis.mmd"
```

## Availability Sets vs Availability Zones

| Service | Layer | Scope | Use Case | Key Feature |
| --- | --- | --- | --- | --- |
| **Availability Set** | VM grouping | Single datacenter | Protect from hardware/rack failures | Fault domains (2-3) + Update domains (up to 20) |
| **Availability Zone** | VM placement | Zonal (3 zones) | Protect from datacenter failures | Physically separate DCs with independent power |
| **VM Scale Set - Flexible** | VM grouping | Zonal or regional | Auto-scale across zones | Supports mix of manual and auto-scaled VMs |

> **Exam tip:** Availability Sets protect against hardware failures within a single datacenter. Availability Zones protect against full datacenter outages. VMs in an Availability Set get a 99.95% SLA; VMs in different AZs get 99.99% SLA.

> **SLA note:** Single-instance VM designs do not satisfy higher SLA targets.
> For guaranteed uptime questions, expect at least Availability Set or
> Availability Zone based designs.

### Availability Decision Flow

```mermaid
--8<-- "azure/diagrams/compute/availability-decision-flow.mmd"
```

## Virtual Machine Families

| Service | Layer | Scope | Use Case | Key Feature |
| --- | --- | --- | --- | --- |
| **D-series (General Purpose)** | Balanced | General | Web servers, dev/test, small databases | Balanced CPU:memory ratio |
| **E-series (Memory Optimized)** | High RAM | Memory | SAP, in-memory databases, caches | High memory:CPU ratio |
| **F-series (Compute Optimized)** | High CPU | Compute | Batch, gaming, web front-ends | High CPU:memory ratio |
| **N-series (GPU)** | GPU | GPU | ML training, rendering, visualization | NVIDIA GPU; NC/ND/NV variants |
| **L-series (Storage Optimized)** | High throughput | Storage | Cassandra, MongoDB, big data | High local disk IOPS/throughput |
| **M-series (Large Memory)** | High RAM | Memory | SAP HANA, largest in-memory workloads | Largest memory SKUs; up to 12 TiB RAM |
| **B-series (Burstable)** | Burstable | General | Dev/test, low-sustained CPU tasks | CPU credits; cost-effective for bursty workloads |
| **H-series (HPC)** | HPC | Compute | MPI workloads, tightly coupled HPC | InfiniBand RDMA; high CPU clock speed |
| **HB-series (HPC Memory-Bandwidth)** | HPC | Compute | Memory-bandwidth-intensive HPC (CFD, weather) | AMD EPYC; high memory bandwidth; InfiniBand RDMA |
| **HC-series (HPC Dense Compute)** | HPC | Compute | Dense compute HPC (molecular dynamics, FEA) | Intel Xeon; high core count; InfiniBand RDMA |
| **ND-series (GPU HPC)** | GPU / HPC | GPU | GPU-to-GPU AI training, large model training | NVIDIA A100/H100; NVLink; InfiniBand RDMA |

## HPC Networking — RDMA

Remote Direct Memory Access (RDMA) enables VM-to-VM communication that bypasses the OS kernel,
delivering microsecond latency and high throughput for tightly coupled HPC and AI training
workloads. RDMA-capable VM sizes (H-series, HB-series, HC-series, ND-series) must be deployed
in an **InfiniBand-enabled** cluster via a Placement Group or proximity placement group.

> **Exam tip:** Choose RDMA-capable VM sizes (H, HB, HC, ND series) when the requirement
> mentions MPI workloads, tightly coupled HPC, or GPU-to-GPU training that cannot tolerate
> standard Ethernet latency. RDMA is not available on general-purpose D/E-series VMs.

> **Exam tip:** For SAP HANA workloads use M-series (memory optimized, largest RAM). For high-throughput NVMe workloads use Lsv3. The "s" suffix (e.g., Dsv5) indicates Premium SSD support.

### VM Family Decision Flow

```mermaid
--8<-- "azure/diagrams/compute/vm-family-decision-flow.mmd"
```
