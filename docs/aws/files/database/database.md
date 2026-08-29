# DATABASE

## Database Service Comparison

| Service | Type | Best For | Key Feature |
| --- | --- | --- |
| **RDS** | Relational (managed) | MySQL, PostgreSQL, MariaDB, Oracle, SQL Server | Automated backups, Multi-AZ, read replicas |
| **Aurora** | Relational (cloud-native) | High-throughput MySQL/PostgreSQL workloads | 5x MySQL perf, serverless option, global DB |
| **DynamoDB** | NoSQL key-value / document | Single-digit ms at any scale | Serverless, global tables, DAX caching |
| **ElastiCache** | In-memory cache | Session store, leaderboard, real-time cache | Redis (rich data structures) or Memcached |
| **Redshift** | Data warehouse | OLAP analytics, BI reporting | Columnar storage, Redshift Spectrum for S3 |
| **Neptune** | Graph database | Highly connected datasets, social graphs | Property graph (Gremlin) and RDF (SPARQL) |

> **Source metadata:** Service capabilities, performance claims, and feature availability reflect AWS documentation as of the verification date below. Cloud product limits, performance figures, and feature sets change frequently — always confirm against current vendor documentation before making a production decision. The "5x MySQL perf" figure for Aurora is a marketing claim that varies by workload, configuration, and version; treat it as an indicator of cloud-native architectural differences rather than a guaranteed benchmark.
>
> **Last verified:** 2026-08-29
> **Primary sources:** [AWS RDS documentation](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/), [AWS Aurora documentation](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/), [AWS DynamoDB documentation](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/), [AWS ElastiCache documentation](https://docs.aws.amazon.com/AmazonElastiCache/latest/userguide/), [AWS Redshift documentation](https://docs.aws.amazon.com/redshift/latest/dg/), [AWS Neptune documentation](https://docs.aws.amazon.com/neptune/latest/userguide/)

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
> **Source metadata:** RTO/RPO figures are approximate and configuration-dependent. Multi-AZ failover typically completes within a few minutes but is not SLA-guaranteed at a specific RTO; "Near zero" RPO reflects synchronous replication but does not eliminate the possibility of transactional loss under some failure scenarios. Aurora Global Database replication lag is typically under one second but is not zero — treat "Under 1 s" as a typical range, not a hard bound. Cross-region read replica promotion is manual and requires operator action; the "Minutes" RTO reflects typical promotion time, not an SLA.
>
> **Last verified:** 2026-08-29
> **Primary sources:** [AWS RDS Multi-AZ documentation](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Concepts.MultiAZ.html), [AWS RDS read replicas documentation](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_ReadRepl.html), [AWS Aurora Global Database documentation](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/aurora-global-database.html), [AWS Aurora Serverless v2 documentation](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/aurora-serverless-v2.html)

## Decision Criteria

The decision flow asks whether you need a specific database engine before
considering cloud-native performance. Read the answers as mutually exclusive
branches:

- **Engine compatibility first.** If the workload must run on Oracle, SQL Server,
  or MariaDB, RDS is the managed option. Aurora does not support those engines.
- **MySQL or PostgreSQL with cloud-native needs → Aurora.** Aurora MySQL and
  Aurora PostgreSQL are MySQL- and PostgreSQL-compatible, but they are not
  identical to standard RDS engines. Prefer Aurora when the requirement calls for
  higher throughput, serverless scaling, global read replicas, or faster failover
  than standard RDS can provide. Confirm compatible editions and feature differences
  before treating Aurora as a drop-in replacement.
- **MySQL or PostgreSQL without cloud-native needs → RDS.** Use RDS for MySQL or
  RDS for PostgreSQL when standard managed persistence, Multi-AZ HA, read replicas,
  and familiar tooling are enough.
- **MariaDB, Oracle, or SQL Server → RDS.** RDS is the managed home for these
  engines. There is no Aurora equivalent for them.
- **Migration or portability constraints.** When migrating an existing workload,
  check RDS engine support, version compatibility, and any DMS or schema-conversion
  requirements before choosing Aurora. Engine or feature dependencies can rule out
  Aurora even when the workload looks like a good fit on paper.
- **NoSQL and caching are separate branches.** DynamoDB covers key-value and
  document workloads. ElastiCache covers Redis and Memcached. Neither replaces a
  relational database when queries, joins, or ACID semantics are required.
- **OLAP is Redshift.** Redshift is exclusively analytical. It is not a
  transactional database.
