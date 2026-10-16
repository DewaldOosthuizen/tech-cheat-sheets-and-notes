# COMPUTE

## Compute Options

| Service | Type | Best For | Key Feature |
| --- | --- | --- | --- |
| **Compute Engine** | IaaS VM | Full OS control, custom images, lift-and-shift | Persistent disks, SSH access, custom machine types, sole tenancy |
| **Google Kubernetes Engine (GKE)** | Managed Kubernetes | Container orchestration at scale | Autopilot, standard mode, multi-cluster ingress, built-in service mesh (Istio) |
| **Cloud Run** | Serverless containers | Event-driven, HTTP-serving containers with scale-to-zero | Per-request billing, Knative-based, any language/runtime in a container |
| **Cloud Functions** | Serverless functions | Event-driven, single-purpose code | 1st gen (lightweight triggers), 2nd gen (Cloud Run-based, longer timeouts, more memory) |
| **App Engine** | PaaS | Standard web frameworks, zero-ops deployment | Standard environment (sandboxed, fast scale) and Flexible environment (custom Docker) |

> **Exam tip:** Choose Compute Engine when the requirement mentions custom OS, kernel-level tuning, or running existing binary workloads without containerisation. Choose GKE when Kubernetes-native orchestration, custom CNI, or complex microservice deployment topologies are needed. Choose Cloud Run when you need scale-to-zero for HTTP or event-driven containers without managing servers. Choose Cloud Functions when the workload is a single-purpose function reacting to events (pub/sub, storage, HTTP webhook). Choose App Engine when the application uses a supported standard framework (Python, Java, Go, Node, Ruby, .NET) and you want zero infrastructure management.

## Compute Decision Flow

```mermaid
--8<-- "google/diagrams/compute/compute-decision.mmd"
```

> **Exam tip:** Start from the control plane question — full OS (Compute Engine) vs container orchestration (GKE) vs serverless containers (Cloud Run) vs functions (Cloud Functions) vs PaaS web app (App Engine). Containerised workloads that do not need the full Kubernetes API surface default to Cloud Run unless scale-to-zero is not required and steady-state capacity must be reserved — in that case GKE Autopilot is the more cost-efficient choice for predictable load.

## Compute Engine Machine Families

| Family | Optimised For | Example Use Case |
| --- | --- | --- |
| **General Purpose (N2, N2D, E2)** | Balanced CPU/memory | Web servers, application servers, dev/test |
| **Compute Optimised (C2, C2D)** | High-performance CPU | Batch processing, game servers, simulation |
| **Memory Optimised (M1, M2)** | Large in-memory datasets | In-memory caches, databases, SAP |
| **Accelerator (GPU, TPU)** | ML training/inference, graphics | GPU (NVIDIA), TPU for TensorFlow/ML workloads |

> **Exam tip:** E2 instances are cost-optimised general-purpose VMs with shared-core options — choose them for non-latency-sensitive dev/test. N2/N2D offer configurable vCPU and memory ratios. C2/C2D deliver the highest performance per core for tightly coupled compute. TPU is the answer when the requirement specifically mentions TensorFlow or JAX training at scale.

## GKE Autopilot vs Standard

| Dimension | Autopilot | Standard |
| --- | --- | --- |
| **Node management** | Fully managed — Google provisions and manages nodes | Customer manages node pools, upgrades, and sizing |
| **Pod resource model** | Declare pod CPU/memory requests; system handles the rest | Full control over node shape, taints, tolerations, daemonsets |
| **Scaling trigger** | Cluster autoscaler on pod pending | Cluster autoscaler on node pool; HPA on pods |
| **Best for** | Teams that want Kubernetes without node ops | Teams that need custom node configuration, GPU/node-level tuning, or daemonsets |

> **Exam tip:** GKE Autopilot is the safer default for greenfield Kubernetes workloads — it removes node-level operational burden. Choose Standard when you need node-level customisation (custom images, specific OS, GPU node pools, daemonsets, or node taints/tolerations for specialised workloads).

## Cloud Run vs Cloud Functions

| Dimension | Cloud Run | Cloud Functions (2nd gen) |
| --- | --- | --- |
| **Unit of deployment** | Container image (any runtime) | Source code or container (function framework) |
| **Invocation** | HTTP request, Cloud Pub/Sub, Cloud Events | Event triggers, HTTP |
| **Max execution** | 60 minutes | 60 minutes (2nd gen) |
| **Concurrency** | Multiple requests per instance (configurable) | One request per instance |
| **Scale-to-zero** | Yes | Yes |

> **Exam tip:** Choose Cloud Run when the workload needs a custom runtime, multiple requests per instance, or an existing container image. Choose Cloud Functions when the workload is a small, event-driven piece of code with minimal dependencies and the built-in trigger integrations (Storage, Pub/Sub, Firestore) are sufficient.
