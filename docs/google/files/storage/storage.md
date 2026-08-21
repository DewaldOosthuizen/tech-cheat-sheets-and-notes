# STORAGE

## Cloud Storage Classes

| Class | Use Case | Min Retention | Retrieval Latency |
| --- | --- | --- | --- |
| **Standard** | Frequently accessed, hot data | None | Milliseconds |
| **Nearline** | Infrequent access — backup, monthly access | 30 days | Milliseconds |
| **Coldline** | Rare access — quarterly backup, disaster recovery | 90 days | Milliseconds |
| **Archive** | Long-term retention, compliance | 365 days | Hours (rehydration required) |

> **Exam tip:** Choose Standard for active data. Choose Nearline for data accessed once a month. Choose Coldline for data accessed once a quarter. Choose Archive for data that must be retained for years and rarely accessed. Accessing data before the minimum retention period incurs an early deletion charge.

## Cloud Storage vs Persistent Disk vs Filestore

| Service | Protocol/Type | Scope | Best For |
| --- | --- | --- | --- |
| **Cloud Storage** | Object (REST/HTTP) | Regional, dual-region, or multi-region | Unstructured data, backups, data lake, static hosting |
| **Persistent Disk** | Block (attached to VM) | Regional or zonal | VM boot and data disks, databases |
| **Filestore** | File (NFS v3/4.1) | Regional | Lift-and-shift file shares, shared config |

> **Exam tip:** Cloud Storage is object storage — it does not provide a filesystem interface to VMs. Persistent Disk is block storage — attachable to Compute Engine VMs as a mounted disk. Filestore is NFS — mountable by multiple VMs simultaneously. For shared read/write file access across many VMs, use Filestore. For durable VM-attached disks, use Persistent Disk. For unstructured object data, use Cloud Storage.

## Relational Database Options

| Service | Type | Best For | Key Feature |
| --- | --- | --- | --- |
| **Cloud SQL** | Managed relational (MySQL, PostgreSQL, SQL Server) | Regional OLTP workloads | Managed backups, replication, high availability (HA) configuration |
| **AlloyDB** | PostgreSQL-compatible, high-performance | Analytical and high-throughput OLTP | Columnar storage for analytics, low-latency transactional processing |
| **Cloud Spanner** | Globally distributed, horizontally scalable relational | Global OLTP with strong consistency | Synchronous replication across regions, SQL queries, automatic sharding |

> **Exam tip:** Choose Cloud SQL when you need a managed PostgreSQL/MySQL instance in a single region with familiar tooling. Choose AlloyDB when you need PostgreSQL compatibility with integrated analytical query performance over the same data. Choose Spanner when the requirement mentions global scale, strong consistency across regions, or horizontal write scaling — Spanner is the only option that provides globally synchronous replication with SQL semantics.

## NoSQL Options

| Service | Type | Best For | Key Feature |
| --- | --- | --- | --- |
| **Cloud Bigtable** | Wide-column NoSQL | High-throughput, low-latency key-value and time-series | Single-digit-millisecond latency, scales to billions of rows |
| **Firestore** | Document NoSQL | Mobile/web app backend, real-time sync | Offline persistence, real-time listeners, automatic scaling |

> **Exam tip:** Choose Bigtable for large-scale time-series, IoT, or analytics workloads where low-latency key access is critical — it is not a general-purpose document store. Choose Firestore when the workload is a web or mobile application requiring real-time document sync and offline support. Bigtable does not support secondary indexes or complex queries; Firestore supports limited querying with single-field indexes and composite indexes you create explicitly.

## Analytics Data Warehouse

| Service | Type | Best For | Key Feature |
| --- | --- | --- | --- |
| **BigQuery** | Serverless data warehouse | SQL analytics over petabytes | On-demand pricing or flat-rate slots, separation of compute and storage, BI Engine for low-latency |

> **Exam tip:** BigQuery is the answer for any requirement that mentions SQL analytics at scale without infrastructure management. For streaming inserts, use BigQuery streaming API or load from Cloud Storage, Pub/Sub, or Dataflow. BigQuery Omni allows querying data stored in AWS S3 or Azure Blob Storage from BigQuery.

## Storage Decision Flow

```mermaid
--8<-- "google/diagrams/storage/storage-decision.mmd"
```

## Cloud Storage Replication

| Replication | Scope | Use Case |
| --- | --- | --- |
| **Regional** | Single region, multiple zones | Same-region durability, lowest cost |
| **Dual-region** | Two regions in same continent | Low-latency multi-region access within a continent |
| **Multi-region** | Three or more regions globally | Highest availability, global read access |

> **Exam tip:** Multi-region Cloud Storage provides the highest durability (11 9s) but at higher cost and with eventual consistency for overwrites across regions. For strong consistency within a single region, choose regional storage.
