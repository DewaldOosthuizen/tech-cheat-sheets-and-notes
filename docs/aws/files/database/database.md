# DATABASE

## Database Service Comparison

| Service | Type | Best For | Key Feature |
| --- | --- | --- | --- |
| **RDS** | Relational (managed) | MySQL, PostgreSQL, MariaDB, Oracle, SQL Server | Automated backups, Multi-AZ, read replicas |
| **Aurora** | Relational (cloud-native) | High-throughput MySQL/PostgreSQL workloads | 5x MySQL perf, serverless option, global DB |
| **DynamoDB** | NoSQL key-value / document | Single-digit ms at any scale | Serverless, global tables, DAX caching |
| **ElastiCache** | In-memory cache | Session store, leaderboard, real-time cache | Redis (rich data structures) or Memcached |
| **Redshift** | Data warehouse | OLAP analytics, BI reporting | Columnar storage, Redshift Spectrum for S3 |
| **Neptune** | Graph database | Highly connected datasets, social graphs | Property graph (Gremlin) and RDF (SPARQL) |

> **Exam tip:** DynamoDB is the default answer for serverless NoSQL at scale.
> Choose Aurora over RDS when the requirement mentions high performance or
> cloud-native relational workloads. Redshift is exclusively OLAP — not a
> transactional database.

## Database Decision Flow

```mermaid
--8<-- "aws/diagrams/database/decision-flow.mmd"
```

## RDS High Availability Options

| Option | RTO | RPO | Key Feature |
| --- | --- | --- | --- |
| **Multi-AZ standby** | Minutes | Near zero | Synchronous replication, automatic failover |
| **Read replica (cross-region)** | Manual promote | Minutes | Asynchronous, used for read scale and DR |
| **Aurora Global Database** | Under 1 min | Under 1 s | Dedicated replication layer, 5 read regions |
| **Aurora Serverless v2** | Seconds scale | N/A | Auto-scales ACUs per workload demand |

> **Exam tip:** Multi-AZ is for HA and automatic failover, not for read
> scaling. Read replicas are for read scaling — they can be promoted for DR
> but require manual action.
>
> Operating PostgreSQL itself — indexing, query plans, VACUUM, locking, backup, and
> replication — is covered in the [PostgreSQL Operations & Performance](../../../programming/files/persistence/postgresql.md)
> reference, independent of which managed service hosts the instance.
