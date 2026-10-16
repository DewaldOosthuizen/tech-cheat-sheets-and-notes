# High Availability & Disaster Recovery

## Key Concepts

| Term | Definition |
| --- | --- |
| **RTO** | Recovery Time Objective — max acceptable downtime |
| **RPO** | Recovery Point Objective — max acceptable data loss (time) |
| **SLA** | Uptime guarantee; VMs need 2+ instances for 99.9%+ |
| **Availability Set** | Fault + update domain spread within a datacenter |
| **Availability Zone** | Physically separate datacenter in same region |
| **Region Pair** | Microsoft-paired regions for geo-replication |

```mermaid
--8<-- "azure/diagrams/ha-dr/key-concepts.mmd"
```

## Azure Site Recovery (ASR)

| Feature | Detail |
| --- | --- |
| **Purpose** | Replicate VMs to secondary region for DR |
| **RPO** | As low as 30 seconds (crash-consistent) |
| **RTO** | Minutes (orchestrated failover) |
| **Test Failover** | Validate DR without impacting production |
| **Supported sources** | Azure VMs, VMware, Hyper-V, Physical servers |

## Azure Backup

| Workload | Vault Type | Key Feature |
| --- | --- | --- |
| Azure VMs | Recovery Services Vault | App-consistent snapshots |
| Azure SQL | Recovery Services Vault | Full/diff/log backup, PITR |
| Azure Files | Recovery Services Vault | Share-level snapshots |
| Azure Blobs | Backup Vault | Operational backup (no vault egress) |
| PostgreSQL / MySQL | Backup Vault | Managed DB backup |

> **⚠️ Deprecation warning:** Recovery Services Vault is the legacy backup store (VMs, SQL
> in VM, Azure Files). For new PaaS-based backup targets (Blobs, managed databases), use
> **Backup Vault** — Microsoft's current backup store model.

## Azure Backup vs Azure Site Recovery

| Service | Type | Best For | Key Feature |
| --- | --- | --- | --- |
| **Azure Backup** | Data backup | Files, VMs, databases, blobs | Point-in-time restore; policy-based scheduling |
| **Azure Site Recovery** | Replication/DR | VM failover to secondary region | Near-zero RPO; orchestrated failover/failback |
| **Backup Center** | Management | Centralized backup governance | Single pane for all vaults across subscriptions |

> **Exam tip:** Azure Backup protects against data loss (accidental deletion, corruption). Azure Site Recovery protects against VM/region failure. They are complementary — use both for full protection.

### HA & DR Decision Flow

```mermaid
--8<-- "azure/diagrams/ha-dr/ha-dr-decision-flow.mmd"
```

## Recovery Services Vault Structure

```mermaid
--8<-- "azure/diagrams/ha-dr/recovery-services-vault-structure.mmd"
```

> **⚠️ Deprecation warning:** Recovery Services Vault is the legacy backup store (VMs, SQL
> in VM, Azure Files). For new PaaS-based backup targets (Blobs, managed databases), use
> **Backup Vault** — Microsoft's current backup store model.
