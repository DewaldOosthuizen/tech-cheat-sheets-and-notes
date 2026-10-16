# Storage

## Storage Account Types

| Type | Supported Services | Supported Replication | Use Case |
| --- | --- | --- | --- |
| **Standard GPv2** | Blob, File, Queue, Table | LRS, ZRS, GRS, RA-GRS, GZRS, RA-GZRS | General purpose, most scenarios |
| **Premium Block Blobs** | Block Blob only | LRS, ZRS | Low-latency blob I/O, analytics |
| **Premium File Shares** | Azure Files only | LRS, ZRS | High-performance SMB/NFS shares |
| **Premium Page Blobs** | Page Blob only | LRS only | Unmanaged VM disks |

> **Exam tip:** Premium storage accounts support LRS and ZRS only — geo-redundancy
> (GRS / GZRS) is not available. Standard GPv2 supports all six replication tiers.
>
> **Source metadata:** Storage account type names, supported replication tiers, and premium
> storage constraints reflect Azure documentation as of the verification date below. Storage
> account features, replication options, and premium tier constraints can change — always confirm
> against current vendor documentation before making a production decision.
>
> **Last verified:** 2026-08-29
> **Primary sources:** [Azure storage account documentation](https://learn.microsoft.com/azure/storage/common/storage-account-overview),
> [Azure storage redundancy documentation](https://learn.microsoft.com/azure/storage/common/storage-redundancy)

## Blob Storage Access Tiers

| Service | Type | Best For | Key Feature |
| --- | --- | --- | --- |
| **Hot** | Blob access tier | Frequently accessed data; no minimum retention | Lowest access cost; highest storage cost |
| **Cool** | Blob access tier | Infrequently accessed data; min 30-day retention | Lower storage cost; higher per-operation cost |
| **Cold** | Blob access tier | Rarely accessed data; min 90-day retention | Lower storage cost than Cool; higher access cost |
| **Archive** | Blob access tier | Long-term archival; min 180-day retention | Lowest storage cost; requires rehydration (hours) before read |

> **Exam tip:** Use Lifecycle Management policies to auto-transition blobs
> through tiers. Archive blobs must be rehydrated to Hot or Cool before access;
> plan for rehydration latency in recovery scenarios.
>
> **Source metadata:** Blob access tier names, minimum retention periods, and relative cost
> characteristics reflect Azure documentation as of the verification date below. Access tier
> pricing, minimum retention periods, and rehydration behavior can change — always confirm
> against current vendor documentation before making a production decision.
>
> **Last verified:** 2026-08-29
> **Primary sources:** [Azure Blob storage access tiers documentation](https://learn.microsoft.com/azure/storage/blobs/storage-blob-tier-overview)

```mermaid
--8<-- "azure/diagrams/storage/blob-storage-access-tiers.mmd"
```

## Storage Redundancy

| Service | Type | Best For | Key Feature |
| --- | --- | --- | --- |
| **LRS** | Storage redundancy | Dev/test; lowest cost; no zone/regional DR requirement | 3 copies in one datacenter; 99.9999999% durability |
| **ZRS** | Storage redundancy | Regional HA; zone-failure tolerance; no cross-region DR | 3 copies across 3 AZs in one region; no data loss on zone outage |
| **GRS** | Storage redundancy | Cross-region DR; secondary readable only after failover | 6 copies (3 primary + 3 secondary region); RPO < 15 min |
| **RA-GRS** | Storage redundancy | Cross-region DR with continuous read access to secondary | GRS + secondary endpoint always readable; 99.99% read SLA |
| **GZRS** | Storage redundancy | HA + cross-region DR without secondary read requirement | 3 AZs primary + geo-replicated secondary; highest resilience |
| **RA-GZRS** | Storage redundancy | Maximum durability with continuous secondary read access | GZRS + secondary endpoint always readable; 99.99% read SLA |

```mermaid
--8<-- "azure/diagrams/storage/storage-redundancy.mmd"
```

> **Exam tip:** Choose RA-GRS when zone resilience in the primary region is
> not required but continuous read access to the secondary is. Choose GZRS
> (or RA-GZRS) when you need both zone-level resilience in the primary region
> and geo-redundancy — GZRS is strictly more resilient than RA-GRS for the
> same read-availability requirement.
>
> **Source metadata:** Replication tier names, copy counts, durability figures, RPO, and
> read SLA claims reflect Azure documentation as of the verification date below. Durability
> figures are design targets, not guarantees; RPO for geo-replication is approximate and
> can vary under some failure scenarios; read SLAs apply to the secondary endpoint only when
> it is available and do not cover data loss. Always confirm against current vendor documentation
> before relying on these figures for production SLA calculations.
>
> **Last verified:** 2026-08-29
> **Primary sources:** [Azure storage redundancy documentation](https://learn.microsoft.com/azure/storage/common/storage-redundancy),
> [Azure storage SLA documentation](https://learn.microsoft.com/azure/support/legal/sla/storage-v2)

## Azure Files vs Blob vs Disk vs NetApp

| Service | Protocol | Use Case |
| --- | --- | --- |
| **Azure Blob** | REST/HTTP | Unstructured data, backups, media, data lake |
| **Azure Files** | SMB 3.0 / NFS 4.1 | Lift-and-shift file shares, shared app config |
| **Azure NetApp Files** | NFS / SMB | High-perf enterprise workloads, SAP HANA |
| **Azure Managed Disks** | iSCSI (internal) | VM OS and data disks |
| **Azure Queue Storage** | REST | Decoupled async messaging (simple) |
| **Azure Table Storage** | REST | NoSQL key-value, schema-less |

## Data Integration & Movement

| Service | Type | Best For | Key Feature |
| --- | --- | --- | --- |
| **Azure Data Factory** | Cloud ETL / orchestration | Batch data pipelines between cloud and on-prem stores | 90+ connectors, pipeline scheduling, data flows |
| **Azure Databricks** | Lakehouse analytics | Large-scale Spark engineering, Delta Lake, ML pipelines | Managed Apache Spark with collaborative notebooks and autoscaling clusters |
| **Azure-SSIS Integration Runtime** | Lift-and-shift ETL | Running existing SSIS packages in ADF without rewrite | Managed SSIS runtime inside ADF; supports Azure SQL and Azure SQL MI as SSISDB host |
| **Azure Data Box** | Offline bulk transfer | Initial migration of large datasets (TB–PB) to Azure when bandwidth is constrained | Physical device shipped by Microsoft; encrypted, tamper-evident |
| **Azure Data Box Gateway** | Edge ingestion | Continuous data upload from on-prem to Azure Blob/Files | Virtual appliance; no physical device needed |
| **Azure Data Box Edge** | Edge compute + transfer | Data processing and inference at the edge before upload | Runs Azure IoT Edge modules and FPGA-accelerated ML inference |

> **Exam tip:** Choose Azure Data Factory when the requirement mentions pipeline orchestration,
> scheduled data movement, or running SSIS packages in the cloud (via Azure-SSIS IR). Choose
> Data Box (physical) for offline migrations where internet transfer would take weeks. Choose
> Data Box Gateway for ongoing edge-to-cloud ingestion without a physical device.

> **Exam tip:** Choose Azure Databricks when the requirement emphasizes Spark-native
> data engineering, Delta Lake, collaborative notebooks, or large-scale ML data
> processing. Choose Synapse when a unified SQL + Spark analytics workspace is the
> stronger requirement.

## Hybrid File Sync

| Service | Type | Best For | Key Feature |
| --- | --- | --- | --- |
| **Azure File Sync Agent** | Hybrid tiering | On-prem Windows Server local cache for an Azure Files share | Cloud tiering stubs cold files locally and retrieves them on access; multiple server endpoints per sync group |

> **Exam tip:** Choose Azure File Sync when the requirement mentions keeping on-prem Windows
> file server access while centralising storage in Azure Files. Cloud tiering frees local disk
> by replacing infrequently accessed files with stubs that are transparently fetched from Azure.

## Azure SQL Purchasing Models

| **vCore model** | Provisioned or Serverless | New deployments, Azure Hybrid Benefit, Managed Instance | Decouples compute and storage; supports Serverless tier; required for SQL MI |
| **DTU model** | Bundled compute+storage | Legacy workloads, simple cost predictability | Fixed ratio of CPU/memory/IO; Basic/Standard/Premium tiers; not available on SQL MI |

> **Exam tip:** Prefer vCore when you need Azure Hybrid Benefit (bring your own SQL Server
> licence), Serverless auto-pause, or are deploying SQL Managed Instance (DTU not supported).
> DTU is simpler but less flexible — expect AZ-305 questions to favour vCore for new
> cloud-native designs.

## Cosmos DB Consistency Levels (strong → weak)

| Level | Guarantee | Latency | Use Case |
| --- | --- | --- | --- |
| **Strong** | Linearizable reads | Higher | Financial transactions |
| **Bounded Staleness** | Lag bounded by ops/time | Moderate | Global apps, bounded lag OK |
| **Session** | Consistent within session | Low | Per-user data (default) |
| **Consistent Prefix** | No out-of-order reads | Low | Social media feeds |
| **Eventual** | No ordering guarantee | Lowest | High availability, non-critical |

## Cosmos DB — Developer Focus (AZ-204)

**Partition key design rules:**

- Choose a high-cardinality key (many distinct values) to distribute RUs and storage uniformly across logical partitions.
- Avoid hot partitions — a key that concentrates most reads/writes on one partition causes throttling (429 errors).
- The partition key must be immutable — it cannot be changed after the item is created.
- Include the partition key in all queries; without it, Cosmos DB performs a cross-partition fan-out, increasing RU cost and latency.

| Service | Type | Best For | Key Feature |
| --- | --- | --- | --- |
| Cosmos DB Provisioned Throughput | RU Model | Predictable, steady-state workloads with defined peak load | Fixed RU/s ceiling; most cost-effective when utilisation is consistently high |
| Cosmos DB Autoscale | RU Model | Variable workloads with bounded but unpredictable peaks | Scales between 10% and 100% of the configured max RU/s; you pay for peak consumed |
| Cosmos DB Serverless | RU Model | Intermittent or unpredictable workloads; development/test | Billed per RU consumed per operation; no pre-provisioned capacity; no SLA for throughput |

> **Exam tip:** Choose serverless for sporadic or unpredictable access patterns where pre-provisioning RUs would be wasteful. Choose autoscale when the workload is variable but has a defined maximum. Choose provisioned (manual) throughput when the load is predictable and steady — it gives a hard cost ceiling and the best price per RU at sustained utilisation.

SDK access pattern (Python — azure-cosmos v4):

```python
from azure.cosmos import CosmosClient, PartitionKey

client = CosmosClient(url=COSMOS_ENDPOINT, credential=COSMOS_KEY)
database = client.create_database_if_not_exists(id="MyDatabase")
container = database.create_container_if_not_exists(
    id="MyContainer",
    partition_key=PartitionKey(path="/category"),
    offer_throughput=400,
)
container.create_item(body={"id": "item1", "category": "gear", "name": "Helmet"})
```

## Blob Storage SAS Tokens

| Service | Type | Best For | Key Feature |
| --- | --- | --- | --- |
| Service SAS | SAS Token | Delegating access to a specific Blob, Queue, Table, or File resource | Signed with the storage account key; scoped to one service type |
| Account SAS | SAS Token | Delegating access across multiple storage services in one token | Signed with the storage account key; broadest scope — use with caution |
| User Delegation SAS | SAS Token | Delegated external access without exposing the account key | Signed with Entra ID (Azure AD) credentials; requires Storage Blob Delegator RBAC role |

> **Exam tip:** User Delegation SAS is the most secure option — it is signed with Entra credentials, not the storage account key. The caller must hold the Storage Blob Delegator role on the storage account. Use it whenever you need to grant time-limited external access without distributing account keys.

SDK pattern (Python — azure-storage-blob v12):

```python
from azure.storage.blob import BlobServiceClient, BlobSasPermissions, generate_blob_sas
from datetime import datetime, timedelta, timezone

sas_token = generate_blob_sas(
    account_name=ACCOUNT_NAME,
    container_name="mycontainer",
    blob_name="report.pdf",
    account_key=ACCOUNT_KEY,  # omit and pass user_delegation_key for User Delegation SAS
    permission=BlobSasPermissions(read=True),
    expiry=datetime.now(timezone.utc) + timedelta(hours=1),
)
```

## Azure Blob Storage Immutable Policies

Immutable storage for Azure Blob (WORM — Write Once, Read Many) prevents blobs from being
modified or deleted for a user-specified interval. Designed to satisfy compliance regimes
that mandate non-erasable records: SEC 17a-4(f), CFTC 1.31, FINRA, and HIPAA audit trails.

### Policy Types

| Policy | Mechanism | Duration | Deletable Before Expiry | Lock Behaviour |
| --- | --- | --- | --- | --- |
| **Time-Based Retention** | Blocks delete/overwrite for a fixed period | 1 day – 146,000 days | No | Unlocked: intervals can be extended or shortened. Locked: intervals can only be extended — never shortened or removed |
| **Legal Hold** | Blocks delete/overwrite until all hold tags cleared | Indefinite (tag-based) | No | No lock state — active while any hold tag exists; cleared only by removing every tag |

> **Exam tip:** A time-based retention policy in **Unlocked** state can be shortened or
> removed — it is mutable. Once **Locked**, the retention interval can only be **extended**,
> never reduced and never removed. For SEC 17a-4 compliance, the policy must be Locked.
> Legal Hold does not use a time interval at all — it persists until every tag is explicitly
> cleared, regardless of how much time has passed.

### Policy Scope

| Scope | Requires | Granularity | When to Use |
| --- | --- | --- | --- |
| **Container-level (version-independent)** | No extra feature | All blobs in the container | Uniform retention for an entire container; simpler setup; classic approach |
| **Version-level** | Blob versioning enabled on the storage account | Individual blob versions | Different retention periods per version; allows overwrite while keeping immutable prior versions |

> **Exam tip:** Version-level immutability requires blob versioning to be enabled first — a
> common setup trap. Without versioning, only container-level policies are available.
> Version-level lets you write a new version while the old version remains WORM-protected;
> container-level prevents all writes once a policy is active.

### Immutable Policy vs Soft Delete vs Resource Locks

| Mechanism | Scope | Reversible | Who Can Override | Primary Purpose |
| --- | --- | --- | --- | --- |
| **Time-Based Retention (Locked)** | Container or blob version | No | Nobody — not even Owner or Microsoft Support | Regulatory compliance (WORM) |
| **Legal Hold** | Container or blob version | Yes — when all tags cleared | Storage account contributor with tag permission | Litigation / investigation hold |
| **Soft Delete** | Blob, Container, File Share | Yes — restore within retention window | Storage contributor | Accidental-deletion recovery |
| **Resource Lock (Delete)** | ARM resource (storage account or RG) | Yes — Owner / User Access Admin | Owner or User Access Administrator | Prevent ARM-level deletion of the resource |

> **Exam tip:** WORM and Soft Delete are complementary, not alternatives. WORM prevents
> intentional or malicious overwrite/delete at the data plane. Soft Delete is a recycle bin
> for accidental operations. A secure regulatory deployment uses both. Resource Locks protect
> the storage account itself from ARM-level deletion but do NOT protect individual blobs from
> overwrite — do not confuse them with immutable policies.

## Managed Disk Types

| Service | Type | Best For | Key Feature |
| --- | --- | --- | --- |
| **Standard HDD** | Magnetic | Dev/test, infrequent access | Lowest cost; up to 2000 IOPS/500 MBps |
| **Standard SSD** | SSD | Web servers, lightly used apps | Consistent latency vs HDD; up to 6000 IOPS |
| **Premium SSD** | SSD | Production databases, critical apps | Up to 20000 IOPS/900 MBps per disk |
| **Premium SSD v2** | SSD | High-perf workloads with tunable IOPS | Independently set IOPS, throughput, capacity |
| **Ultra Disk** | NVMe SSD | Latency-sensitive: SAP HANA, top-tier SQL | Sub-millisecond latency; up to 160000 IOPS |

> **Exam tip:** Ultra Disk requires VM series that support it (e.g., Esv3, Dsv3) and must be in the same Availability Zone as the VM. It cannot be used as OS disk.

### Managed Disk Selection

```mermaid
--8<-- "azure/diagrams/storage/managed-disk-selection.mmd"
```

## Storage Account Replication

| Service | Type | Best For | Key Feature |
| --- | --- | --- | --- |
| **LRS** | Local redundancy | Dev/test, low cost | 3 copies in one datacenter |
| **ZRS** | Zone redundancy | High availability, same region | 3 copies across 3 AZs in one region |
| **GRS** | Geo redundancy | DR; secondary read only on failover | LRS primary + async copy to secondary region |
| **RA-GRS** | Geo redundancy + read | DR with read access to secondary | GRS + read endpoint on secondary region |
| **GZRS** | Geo-zone redundancy | Max HA + DR | ZRS primary + async copy to secondary region |
| **RA-GZRS** | Geo-zone + read | Max HA + DR + read | GZRS + read endpoint on secondary region |

> **Exam tip:** RA-GRS and RA-GZRS provide a secondary read endpoint (use `-secondary` suffix in storage URL). The secondary is always read-only unless a failover is initiated.

### Storage Replication Decision Flow

```mermaid
--8<-- "azure/diagrams/storage/storage-replication-decision-flow.mmd"
```
