# HIGH AVAILABILITY & DISASTER RECOVERY

## Key Concepts

| Term | Definition |
| --- | --- |
| **RTO** | Recovery Time Objective — maximum acceptable downtime |
| **RPO** | Recovery Point Objective — maximum acceptable data loss (measured in time) |
| **SLA** | Service Level Agreement — uptime commitment per service |
| **Region** | Geographic deployment zone (e.g. us-central1, europe-west1) |
| **Zone** | Isolated failure domain within a region (e.g. us-central1-a, us-central1-b, us-central1-c) |
| **Regional resource** | Scoped to a single region (e.g. Cloud SQL instance, Persistent Disk) |
| **Multi-regional resource** | Replicated across multiple regions (e.g. Cloud Storage multi-region, Cloud Spanner multi-region) |
| **Region pair** | Google-paired regions for DR (not always symmetric — check pairing) |

> **Exam tip:** A regional resource (Cloud SQL, Persistent Disk, Cloud Run region) survives zone failure if it is configured for regional redundancy, but not a full region failure. A multi-regional resource (Cloud Storage multi-region, Spanner multi-region) survives a full region failure. Know the difference — it is a common discriminator.

## High Availability Patterns

| Pattern | Scope | Best For | Key Feature |
| --- | --- | --- | --- |
| **Multi-zone (within a region)** | Regional, multiple zones | Surviving a single zone failure | Regional Cloud SQL, Cross-zone Load Balancing, Regional Persistent Disk |
| **Multi-region (active-active)** | Multiple regions, both serving traffic | Near-zero RTO/RPO, global user base | Cloud Load Balancing global anycast, Cloud Spanner multi-region, Cloud Storage multi-region |
| **Multi-region (active-passive)** | Primary region active, secondary on standby | Controlled cost, recovery within minutes to hours | Cloud DNS failover, Traffic Director multi-cluster, VM image replication |
| **Backup and Restore** | Scheduled backups, restore when needed | Cost-optimised DR, smallest RPO/RTO requirements | Cloud SQL automated backups, Persistent Disk snapshots, Cloud Storage object versioning and lifecycle |
|| **Pilot Light** | Minimal standby | Hours RTO, cost-optimised | Core data replicated, services off until needed |

> **Exam tip:** Multi-zone within a region protects against a single zone failure. Multi-region active-active protects against a full region failure. Backup and Restore is the cheapest DR pattern — it provides recoverability but with the longest RTO (restore time). Match the pattern to the stated RTO and RPO.

## Cloud Load Balancing Failover

| Scenario | Mechanism |
| --- | --- |
| **Global HTTP(S) LB** | Anycast IP routes to the nearest healthy backend; if a region’s backends are unhealthy, traffic automatically routes to the next healthy region |
| **Cross-region failover** | Health checks on backend buckets or instance groups trigger failover; no DNS change required for HTTP(S) traffic |
| **Internal TCP/UDP LB** | Regional only — does not provide cross-region failover by itself; combine with Cloud DNS failover or Traffic Director |

> **Exam tip:** The global HTTP(S) Load Balancer provides automatic regional failover based on health checks — no DNS changes needed. This is the answer when the requirement mentions seamless failover for HTTP/S traffic across regions. For TCP/UDP workloads, you need a different approach — Cloud DNS failover or Traffic Director.

## Cloud DNS Failover

| Feature | Detail |
| --- | --- |
| **Health-checked failover** | Cloud DNS monitors the health of primary and secondary endpoints; returns the primary IP if healthy, otherwise the secondary |
| **TTL** | Low TTL (e.g. 60 seconds) recommended for fast failover; clients re-resolve DNS |
| **Geolocation-based routing** | Return different IPs based on client location — not failover per se, but can direct users to the nearest region |

> **Exam tip:** Cloud DNS failover is the answer when the requirement mentions DNS-based failover to a secondary region — it works for any protocol (not only HTTP/S) because it operates at the DNS level. For automatic, health-check-driven failover of HTTP/S traffic, the global HTTP(S) LB is preferred (no DNS dependency).

## Persistent Disk and Snapshot DR

| Mechanism | Scope | RPO | RTO |
| --- | --- | --- | --- |
| **Regional Persistent Disk** | Synchronous replication across two zones in a region | Near zero (synchronous) | Automatic failover within the region |
| **Persistent Disk snapshots** | Asynchronous, stored in Cloud Storage | Depends on snapshot schedule | Restore by creating a new disk from snapshot — minutes to hours |
| **Snapshot schedule** | Automated recurring snapshots | Controlled by schedule frequency | Same as manual snapshot restore |

> **Exam tip:** Regional Persistent Disk provides synchronous replication across two zones — it survives a zone failure with near-zero RPO and automatic failover. Snapshots are asynchronous — they provide a point-in-time copy for DR but with RPO depending on the schedule. Snapshots stored in Cloud Storage can be restored in another region to support region-level DR.

## Cloud SQL DR

| Option | Scope | RPO | RTO |
| --- | --- | --- | --- |
| **HA configuration (regional)** | Same region, standby in another zone | Near zero (synchronous) | Automatic failover, seconds to minutes |
| **Read replica (cross-region)** | Async replica in another region | Seconds to minutes (async) | Promote replica to primary — minutes |
| **Backups and restore** | Backup stored in Cloud Storage | Depends on backup schedule | Restore to a new instance — minutes to hours |

> **Exam tip:** Cloud SQL HA configuration provides automatic zone-failure failover within a region. Cross-region read replicas can be promoted for region-level DR, but RPO is not zero because replication is asynchronous. For strict RPO requirements, choose synchronous replication (regional HA or Cloud Spanner multi-region).

## Cloud Spanner Replication

| Configuration | Scope | Consistency | Use Case |
| --- | --- | --- | --- |
| **Regional** | Single region, three zones | Strong | Regional OLTP with high availability |
| **Dual-region** | Two regions | Strong (synchronous) | Low-latency multi-region OLTP within a continent |
| **Multi-region** | Three or more regions | Strong (synchronous) | Global OLTP with strongest consistency |

> **Exam tip:** Cloud Spanner is the only GCP relational database that provides globally synchronous replication with strong consistency — it is the answer when the requirement mentions global OLTP with strong consistency across regions. The trade-off is higher cost and write latency (synchronous replication across regions adds round-trip time).

## Cloud Storage DR

| Replication | Scope | Durability | Availability |
| --- | --- | --- | --- |
| **Regional** | Single region, multiple zones | 99.999999999% (11 9s) within region | Survives zone failure |
| **Dual-region** | Two regions in same continent | 11 9s | Survives one region failure; low-latency read from either region |
| **Multi-region** | Three or more regions globally | 11 9s | Highest availability; global read access; eventual consistency for overwrites across regions |

> **Exam tip:** Cloud Storage multi-region provides the highest availability and durability — it survives a full region failure. For DR planning, ensure the bucket is configured as multi-region or dual-region if the requirement mentions surviving a region outage. Object versioning and lifecycle policies provide an additional layer of protection against accidental deletion or overwrite.
