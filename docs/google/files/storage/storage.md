# STORAGE

## Cloud Storage Classes

|| Class | Use Case | Min Retention | Retrieval Latency |
|| --- | --- | --- | --- |
|| **Standard** | Frequently accessed, hot data | None | Milliseconds |
|| **Nearline** | Infrequent access — backup, monthly access | 30 days | Milliseconds |
|| **Coldline** | Rare access — quarterly backup, disaster recovery | 90 days | Milliseconds |
|| **Archive** | Long-term retention, compliance | 365 days | Hours (rehydration required) |

> **Exam tip:** Choose Standard for active data. Choose Nearline for data accessed once a month. Choose Coldline for data accessed once a quarter. Choose Archive for data that must be retained for years and rarely accessed. Accessing data before the minimum retention period incurs an early deletion charge.
>
> **Source metadata:** Storage class names, minimum retention periods, and retrieval latencies reflect Google Cloud documentation as of the verification date below. Cloud product limits and pricing tiers change frequently — always confirm against current vendor documentation before making a production decision.
>
> **Last verified:** 2026-08-29  
> **Primary sources:** [Google Cloud storage documentation](https://cloud.google.com/storage/docs), [Cloud Storage storage classes](https://cloud.google.com/storage/docs/storage-classes)

## Cloud Storage vs Persistent Disk vs Filestore

|| Service | Protocol/Type | Scope | Best For |
|| --- | --- | --- | --- |
|| **Cloud Storage** | Object (REST/HTTP) | Regional, dual-region, or multi-region | Unstructured data, backups, data lake, static hosting |
|| **Persistent Disk** | Block (attached to VM) | Regional or zonal | VM boot and data disks, databases |
|| **Filestore** | File (NFS v3/4.1) | Regional | Lift-and-shift file shares, shared config |

> **Exam tip:** Cloud Storage is object storage — it does not provide a filesystem interface to VMs. Persistent Disk is block storage — attachable to Compute Engine VMs as a mounted disk. Filestore is NFS — mountable by multiple VMs simultaneously. For shared read/write file access across many VMs, use Filestore. For durable VM-attached disks, use Persistent Disk. For unstructured object data, use Cloud Storage.

## Cloud Storage Replication

|| Replication | Scope | Use Case |
|| --- | --- | --- |
|| **Regional** | Single region, multiple zones | Same-region durability, lowest cost |
|| **Dual-region** | Two regions in same continent | Low-latency multi-region access within a continent |
|| **Multi-region** | Three or more regions globally | Highest availability, global read access |

> **Exam tip:** Multi-region Cloud Storage provides the highest durability (11 9s) but at higher cost and with eventual consistency for overwrites across regions. For strong consistency within a single region, choose regional storage.
>
> **Source metadata:** Replication scope and durability claims reflect Google Cloud documentation as of the verification date below. Durability figures and consistency guarantees for multi-region storage can be configuration- and region-dependent — confirm against current vendor documentation for production SLAs.
>
> **Last verified:** 2026-08-29  
> **Primary sources:** [Google Cloud storage documentation](https://cloud.google.com/storage/docs), [Cloud Storage replication](https://cloud.google.com/storage/docs/overview)

## Database, NoSQL, and Analytics Services

Google Cloud database services have their own dedicated page. For service selection across relational, document, wide-column, cache, and analytics workloads, see the [Google Cloud Database page](../database/database.md).

Key distinctions at a glance:

- **Cloud Storage** is object storage — use it for unstructured data, backups, data lakes, and static hosting. It is not a database.
- **Persistent Disk** is block storage — attach it to Compute Engine VMs for boot and data disks.
- **Filestore** is NFS file storage — use it for shared file access across multiple VMs.
- **Cloud SQL, AlloyDB, Spanner, Bigtable, Firestore, Memorystore, and BigQuery** are database and analytics services. See the [Database page](../database/database.md) for comparison and decision criteria.

The [Google Cloud Database page](../database/database.md) contains comparison tables and decision criteria for Cloud SQL, AlloyDB, Spanner, Firestore, Bigtable, Memorystore, and BigQuery.
