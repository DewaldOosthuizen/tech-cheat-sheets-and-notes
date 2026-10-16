# Well-Architected Framework

> **Exam Focus:** Use WAF pillars to *justify* design decisions in
> case-study questions — not just to name the correct service.
> Relevant for **AZ-305** only; not assessed in AZ-900 or AZ-104.

## Five-Pillar Summary

| Pillar | Goal | Key Azure Services / Patterns | Exam Focus |
| --- | --- | --- | --- |
| Reliability | Survive failures; meet SLA targets | Availability Zones, Traffic Manager, Azure Site Recovery | AZ vs AS vs Multi-Region; RTO/RPO targets |
| Security | Protect data, identities, and workloads | Microsoft Entra ID, Defender for Cloud, Key Vault, DDoS | Zero Trust; defence-in-depth layers |
| Cost Optimization | Maximise value; eliminate waste | Reserved Instances, Spot VMs, Azure Advisor, Cost Budgets | RI vs Spot vs On-Demand trade-offs |
| Operational Excellence | Safe deployments; observable operations | Azure Monitor, Log Analytics, Deployment Slots, IaC | Blue/green deploys; alerting strategy |
| Performance Efficiency | Scale to meet demand; minimise latency | Azure CDN, Front Door, VMSS, Cosmos DB, Redis Cache | Horizontal vs vertical scale; caching layers |

> **Cross-reference:** See [High Availability & Disaster Recovery](../ha-dr/ha-dr.md) for Reliability patterns, [Security](../security/security.md) for defence-in-depth, [Networking — CDN](../networking/networking.md#content-delivery-cdn) for CDN/Front Door, [Compute — Caching](../compute/compute.md#caching) for Redis tier selection, [Networking](../networking/networking.md) for DDoS, and [Governance](../governance/governance.md) for cost control tooling.

```mermaid
--8<-- "azure/diagrams/waf/five-pillar-summary.mmd"
```

### Decision Flow — Pillar Trade-off Navigator

```mermaid
--8<-- "azure/diagrams/waf/decision-flow-pillar-trade-off-navigator.mmd"
```

## Reliability — SLA Target Mapping

| SLA Target | Recommended Deployment Pattern | Notes |
| --- | --- | --- |
| 99.9 % | Single region, Availability Set | Protects against rack/host failure; no zone fault |
| 99.95 % | Single region, Availability Zones | Protects against datacenter-level failure |
| 99.99 %+ | Multi-region (active-active/passive) | Requires Traffic Manager or Front Door for routing |

> **Exam tip:** Availability Zones ≠ Availability Sets. AZs span separate
> datacenters; AS only separate fault/update domains within one datacenter.

### Composite SLA Calculation

Composite SLA = SLA₁ × SLA₂ × … × SLAₙ (serial dependencies multiply downward).

**Worked example:** App Service 99.95 % × SQL Database 99.99 % = **99.94 %**
(monthly downtime budget drops from ~4.4 min to ~26 min).

Adding redundant independent paths raises the composite SLA:
Composite = 1 − (1 − SLA₁) × (1 − SLA₂) for parallel components.

### Multi-Region Failover Patterns

| Pattern | RTO | RPO | Azure Implementation | Key Feature |
| --- | --- | --- | --- | --- |
| Active-Active | Near zero | Near zero | Front Door + globally distributed backends | Traffic split across regions; no failover lag |
| Active-Passive (warm) | Minutes | Seconds–minutes | Traffic Manager + pre-provisioned standby region | Standby receives replication but serves no live traffic |
| Active-Passive (cold) | Hours | Minutes–hours | Azure Site Recovery + on-demand provisioning | Lowest cost; longest recovery time |

> **Exam tip:** Choose active-active when the requirement states RTO ≈ 0 or
> "no downtime tolerated". Choose active-passive (warm) when cost must be
> controlled but recovery must complete within minutes. Use composite SLA
> multiplication to verify the architecture meets the stated SLA target.

## Cost Optimization — Compute Pricing Model Selection

| Option | Best For | Commitment | Interruption Risk |
| --- | --- | --- | --- |
| On-Demand (Pay-as-go) | Unpredictable workloads, short-term dev/test | None | None |
| Reserved Instances | Steady-state, 24/7 production workloads | 1 or 3 years | None |
| Spot VMs | Fault-tolerant batch jobs, HPC, dev/test | None | Yes (eviction) |
| Azure Hybrid Benefit | Existing Windows Server / SQL Server licences | Bring own licence | None |

> **Tools:** Azure Advisor surfaces rightsizing and idle resource
> recommendations. Azure Budgets + Cost Alerts prevent spend overruns.
> See [Governance](../governance/governance.md) for Policy and Budget configuration patterns.

> **Exam tip:** In case-study questions, every design decision maps to at
> least one WAF pillar. When asked *why* a solution is recommended, frame
> your answer using the pillar: "This satisfies the **Reliability** pillar
> because it adds zone redundancy, raising the composite SLA above 99.95 %."

*Last updated for AZ-305 exam preparation — review official Microsoft Learn documentation for latest service updates.*

## Cost Management & Tagging

| Service | Type | Best For | Key Feature |
| --- | --- | --- | --- |
| **Tags** | Metadata | Cost allocation, filtering | Key-value pairs; up to 50 per resource |
| **Azure Policy - Tag Enforcement** | Governance | Require tags on resources | Deny untagged resources; inherit parent tags |
| **Cost Management Budgets** | Cost control | Spending alerts and limits | Alert at % of budget; action groups supported |
| **Cost Alerts** | Notification | Anomaly detection, budget thresholds | Credit, budget, department quota alerts |
| **Cost Analysis** | Analysis | Ad-hoc spend review | Filter by tag, resource group, subscription |

> **Exam tip:** Tags do NOT inherit from parent scopes (RG to resource) by default. Use Azure Policy with the `Inherit a tag from the resource group` initiative to enforce tag inheritance automatically.

### Tag Inheritance Architecture

```mermaid
--8<-- "azure/diagrams/waf/tag-inheritance-architecture.mmd"
```

### Cost Management Decision Flow

```mermaid
--8<-- "azure/diagrams/waf/cost-management-decision-flow.mmd"
```
