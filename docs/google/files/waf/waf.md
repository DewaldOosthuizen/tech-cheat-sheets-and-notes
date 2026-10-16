# Well-Architected Framework

> **Exam Focus:** Use WAF pillars to *justify* design decisions in
> case-study questions — not just to name the correct service.
> Relevant for **Professional Cloud Architect** and **Professional DevOps Engineer**.

## Six Pillars Overview

| Pillar | Goal | Key GCP Services / Patterns | Exam Focus |
| --- | --- | --- | --- |
| **Operational Excellence** | Run and monitor systems to deliver business value | Cloud Build, Cloud Deploy, Cloud Logging, Cloud Monitoring, Cloud Trace, Cloud Debugger, Error Reporting | CI/CD pipelines, observability strategy, SRE practices |
| **Security** | Protect data, identities, and workloads | Cloud IAM, Cloud KMS, Secret Manager, SCC, VPC Service Controls, Binary Authorization, Cloud Armor | Zero Trust (Beyond Corp), defence-in-depth, data exfiltration prevention |
| **Reliability** | Recover from failures and meet demand | Multi-zone/region architectures, Cloud Load Balancing, Cloud SQL HA, Cloud Spanner, Backup and DR | RTO/RPO targets, region vs zone failure, backup strategies |
| **Performance Efficiency** | Use resources efficiently as demand changes | Cloud Run autoscaling, GKE autoscaling (HPA/Cluster Autoscaler), Cloud CDN, Persistent Disk types, machine families | Right-sizing, caching, autoscaling, choosing the right storage class |
| **Cost Optimization** | Maximise value; eliminate waste | Commited Use Discounts, Sustained Use Discounts, Preemptible/Spot VMs, Budget alerts, Cloud Monitoring cost metrics, right-sizing | Commitment vs on-demand trade-offs, storage class selection, idle resource elimination |
| **Sustainability** | Minimise environmental impact | Carbon footprint tracking, efficient regions, right-sizing | Region carbon intensity, resource efficiency, waste reduction |

> **Cross-reference:** See [High Availability & Disaster Recovery](../ha-dr/ha-dr.md) for Reliability patterns, [Security](../security/security.md) for defence-in-depth, [Networking — CDN](../networking/networking.md) for Cloud CDN/Front Door, [Compute](../compute/compute.md) for autoscaling and machine family selection, [Governance](../governance/governance.md) for cost control tooling.

## Reliability — SLA Target Mapping

| SLA Target | Recommended Deployment Pattern | Notes |
| --- | --- | --- |
| **99.9%** | Single region, multi-zone | Survives a single zone failure; appropriate for non-critical workloads |
| **99.99%** | Multi-zone or multi-region depending on service | Cloud SQL HA, regional Persistent Disk, multi-zone GKE node pools |
| **99.999%** | Multi-region active-active | Cloud Spanner multi-region, Cloud Storage multi-region, global HTTP(S) LB with multi-region backends |

> **Exam tip:** A single zone failure is survivable with regional redundancy (multi-zone). A full region failure requires multi-region deployment. Know which services support which redundancy modes — for example, Cloud SQL HA is regional only; Cloud Spanner multi-region is the option for global strong consistency.

## Cost Optimization — Pricing Model Selection

| Option | Best For | Commitment | Risk |
| --- | --- | --- | --- |
| **On-demand** | Unpredictable workloads, short-term dev/test | None | None |
| **Committed Use Discounts (CUDs)** | Steady-state, 24/7 production workloads | 1 or 3 years | None (capacity not reserved, only discount committed) |
| **Sustained Use Discounts** | Automatic discount for VMs running most of the month | None (automatic) | None |
| **Spot/Preemptible VMs** | Fault-tolerant batch jobs, HPC, dev/test | None | Yes (preemption after 24h max, or earlier) |
| **Savings Plans (Compute Engine)** | Commitment to spend amount rather than specific VMs | 1 or 3 years | None (flexible across instance families and regions) |

> **Exam tip:** Committed Use Discounts provide a discount for committed usage without reserving specific capacity — choose them for steady-state production workloads where the VM family and region are predictable. Sustained Use Discounts apply automatically when a VM runs most of the month — they are not a separate purchase. Spot/Preemptible VMs are the cheapest but can be terminated at any time — use only for fault-tolerant workloads.

## Security Pillar — Defence-in-Depth Summary

| Layer | GCP Control |
| --- | --- |
| **Identity** | Cloud IAM (least privilege), MFA, IAP, workload identity |
| **Data** | CMEK (Cloud KMS), Secret Manager, VPC Service Controls, encryption at rest/transit |
| **Network** | VPC firewall rules, Cloud NAT, Private Google Access, Cloud Armor, VPC Service Controls perimeter |
| **Workload** | Binary Authorization, Container Analysis, SCC vulnerability scanning, secure boot |
| **Monitoring** | Cloud Logging, Cloud Monitoring, SCC (Standard and Premium), audit logs |

> **Exam tip:** Defence-in-depth means applying controls at every layer — identity, data, network, workload, monitoring. A single control (e.g. IAM) is not enough for a production security posture. VPC Service Controls add a data exfiltration layer that IAM alone cannot provide.

## Operational Excellence — CI/CD and Observability

| Capability | GCP Service |
| --- | --- |
| **CI/CD** | Cloud Build (CI), Cloud Deploy (CD to GKE, Cloud Run, Anthos), Artifact Registry |
| **Infrastructure as Code** | Terraform, Deployment Manager (legacy), Config Connector |
| **Logging** | Cloud Logging — centralised log aggregation, sinks, exclusion |
| **Metrics and alerting** | Cloud Monitoring — metrics, dashboards, uptime checks, alert policies |
| **Tracing** | Cloud Trace — distributed latency analysis |
| **Profiling** | Cloud Profiler — CPU and memory profiling of production services |
| **Debugging** | Cloud Debugger — inspect production state without redeploy |
| **Error reporting** | Error Reporting — aggregates and groups errors from Cloud Logging |

> **Exam tip:** Cloud Build is the CI service; Cloud Deploy is the CD service for GKE, Cloud Run, and Anthos. Cloud Deploy uses Skaffold under the hood for GKE deployments. For observability, Cloud Logging and Cloud Monitoring are the foundational services; Cloud Trace, Profiler, Debugger, and Error Reporting are the specialised tooling on top.

## Performance Efficiency — Autoscaling

| Service | Autoscaling Mechanism |
| --- | --- |
| **Cloud Run** | Scale-to-zero and per-request scaling; concurrency configurable |
| **GKE** | Horizontal Pod Autoscaler (HPA), Vertical Pod Autoscaler (VPA), Cluster Autoscaler, Node Auto-Provisioning |
| **Compute Engine** | Managed instance group autoscaling based on CPU, loadBalancer, custom metrics |
| **App Engine** | Automatic scaling (standard) or manual / basic scaling |

> **Exam tip:** Cloud Run provides the simplest autoscaling model — scale to zero when idle, scale out per request. GKE provides the most flexible autoscaling (HPA, VPA, Cluster Autoscaler, node auto-provisioning) but also the most operational complexity. For predictable, always-on capacity, Managed Instance Groups with autoscaling based on CPU or load balancer capacity is the choice.

## Sustainability

| Practice | GCP Feature |
| --- | --- |
| **Carbon footprint tracking** | Carbon Footprint report in Cloud Console — shows emissions by project/region |
| **Region selection** | Choose regions with lower carbon intensity |
| **Right-sizing** | Use right-sizing recommendations to reduce idle or over-provisioned resources |
| **Efficient machine types** | E2 instances (shared-core), C2D (AMD Eco), Spot/Preemptible for batch workloads |

> **Exam tip:** Sustainability is part of the Google Cloud Well-Architected Framework. Key practices are choosing low-carbon regions, right-sizing resources, using efficient machine types (E2, C2D), and using preemptible/spot VMs for batch workloads where the preemption risk is acceptable.
