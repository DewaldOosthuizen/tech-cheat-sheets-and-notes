# STORAGE

## Storage Service Comparison

| Service | Type | Best For | Key Feature |
| --- | --- | --- | --- |
| **S3** | Object storage | Unstructured data, backups, static hosting | 11 9s durability, storage classes, lifecycle |
| **EBS** | Block storage | EC2 OS volumes, databases | Low-latency, persistent, AZ-scoped |
| **EFS** | Managed NFS | Shared file access across EC2 instances | Elastic scale, POSIX-compliant |
| **S3 Glacier** | Archive | Long-term regulatory retention | Retrieval tiers: Expedited, Standard, Bulk |
| **Storage Gateway** | Hybrid | On-premises access to S3/EBS | File, Volume, Tape gateway modes |

> **Exam tip:** EBS volumes are AZ-scoped and attach to a single EC2 instance.
> EFS is region-scoped and can be mounted by multiple instances simultaneously.
> For cross-region object replication, use S3 Cross-Region Replication (CRR).

## Storage Decision Flow

```mermaid
--8<-- "aws/diagrams/storage/decision-flow.mmd"
```

## S3 Storage Classes

| Class | Use Case | Retrieval | Key Feature |
| --- | --- | --- | --- |
| **S3 Standard** | Frequently accessed | Milliseconds | High availability, no min duration |
| **S3 Intelligent-Tiering** | Unknown or changing access | Milliseconds | Auto-moves between tiers, no retrieval fee |
| **S3 Standard-IA** | Infrequent access | Milliseconds | Lower cost, 30-day min, retrieval charge |
| **S3 One Zone-IA** | Re-creatable infrequent data | Milliseconds | Single AZ, cheapest non-archive |
| **S3 Glacier Instant** | Archives needing fast retrieval | Milliseconds | Low cost, 90-day min |
| **S3 Glacier Flexible** | Compliance archives | Minutes to hours | 90-day min, restore required |
| **S3 Glacier Deep Archive** | Long-term retention | 12–48 hours | Cheapest, 180-day min |

> **Exam tip:** S3 Intelligent-Tiering is the safest default when access
> patterns are unpredictable — it eliminates retrieval fees while automating
> tier transitions.
