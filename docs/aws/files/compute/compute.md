# COMPUTE

## EC2 vs Alternatives

| Service | Type | Best For | Key Feature |
| --- | --- | --- | --- |
| **EC2** | IaaS VM | Full OS control, custom AMIs | Broad instance family, spot/reserved pricing |
| **Lambda** | Serverless | Event-driven, short-lived functions | No server management, pay-per-invocation |
| **ECS (Fargate)** | Container (serverless) | Containerised workloads, no cluster ops | Task-level billing, integrates with IAM |
| **EKS** | Managed Kubernetes | Kubernetes-native orchestration | AWS-managed control plane |
| **Elastic Beanstalk** | PaaS | Rapid deployment, managed runtime | Auto-scaling, health monitoring, zero K8s ops |

> **Exam tip:** Choose Lambda when the requirement mentions event triggers or
> millisecond-billed compute. Choose ECS Fargate when containers are required but
> cluster management must be avoided.

## Compute Decision Flow

```mermaid
--8<-- "aws/diagrams/compute/decision-flow.mmd"
```

## EC2 Instance Families

| Family | Optimised For | Example Types |
| --- | --- | --- |
| **General Purpose (M, T)** | Balanced CPU/memory | t3.micro, m6i.large |
| **Compute Optimised (C)** | High-performance CPU | c6i.xlarge |
| **Memory Optimised (R, X)** | Large in-memory datasets | r6i.2xlarge |
| **Storage Optimised (I, D)** | High-throughput local NVMe | i3.large |
| **Accelerated Computing (P, G)** | GPU / ML workloads | p3.2xlarge |

> **Exam tip:** Spot instances save up to 90% but can be interrupted. Reserve
> instances for predictable baseline workloads; use Spot for fault-tolerant
> batch or stateless compute layers.
