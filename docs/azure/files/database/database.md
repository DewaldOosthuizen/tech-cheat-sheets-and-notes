# DATABASE

> **Source metadata:** Service capabilities, limits, and architectural trade-offs in this page
> reflect Azure documentation as of the verification date below. Cloud product limits, SLAs, and
> feature sets change frequently — always confirm against current vendor documentation before
> making a production decision.
>
> **Last verified:** 2026-08-29
> **Primary sources:** [Azure SQL Database documentation](https://learn.microsoft.com/azure/azure-sql/database/sql-database-paas-overview),
> [Azure SQL Managed Instance documentation](https://learn.microsoft.com/azure/azure-sql/managed-instance/sql-managed-instance-paas-overview),
> [Azure Cosmos DB documentation](https://learn.microsoft.com/azure/cosmos-db/),
> [Azure Database for PostgreSQL documentation](https://learn.microsoft.com/azure/postgresql/),
> [Azure Database for MySQL documentation](https://learn.microsoft.com/azure/mysql/),
> [Azure Synapse Analytics documentation](https://learn.microsoft.com/azure/synapse-analytics/),
> [Azure Data Explorer documentation](https://learn.microsoft.com/azure/data-explorer/),
> [Azure AI Search documentation](https://learn.microsoft.com/azure/search/),
> [Azure Cache for Redis documentation](https://learn.microsoft.com/azure/azure-cache-for-redis/),
> [Azure SQL Edge documentation](https://learn.microsoft.com/azure/azure-sql/sql-edge/),
> [Azure Arc documentation](https://learn.microsoft.com/azure/azure-arc/),
> [Azure SLA documentation](https://learn.microsoft.com/azure/support/legal/sla/)

## Database Service Comparison

| Service | Type | Best For | Key Feature |
| --- | --- | --- |
| **Azure SQL Database** | Relational PaaS (SQL Server) | Cloud-native OLTP without OS management | Serverless compute, elastic pools, Hyperscale up to 100 TB |
| **SQL Managed Instance** | Relational PaaS (SQL Server) | SQL Server lift-and-shift with near-100% compatibility | SQL Agent, CLR, cross-database queries, VNet injection |
| **SQL Server on Azure VM** | Relational IaaS (SQL Server) | Full OS and SQL Server control | Customer manages OS and SQL patches; widest feature surface |
| **Azure Database for PostgreSQL** | Relational PaaS (PostgreSQL) | OSS PostgreSQL workloads | Flexible Server, HA zone-redundant standby, read replicas |
| **Azure Database for MySQL** | Relational PaaS (MySQL) | OSS MySQL/MariaDB workloads | Flexible Server, HA zone-redundant standby, read replicas |
| **Azure Cosmos DB** | NoSQL multi-model | Globally distributed, low-latency, multi-API workloads | Multi-region writes, 5 APIs (Core SQL, MongoDB, Cassandra, Gremlin, Table), SLA-backed availability |
| **Azure Synapse Analytics** | Analytics warehouse (SQL + Spark) | OLAP at scale, big data integration | Serverless SQL Pool (query data in place), Dedicated SQL Pool (DWU), Spark Pool |
| **Azure Data Explorer (ADX)** | Time-series / log analytics | Real-time telemetry, logs, IoT at scale | Kusto Query Language (KQL), high-throughput ingestion, fast ad-hoc queries over append-only data |
| **Azure AI Search** | Full-text / vector search | Semantic and hybrid search over documents and embeddings | AI enrichment pipeline, vector index, semantic ranker, integrated with Azure OpenAI |
| **Azure Cache for Redis** | In-memory cache | Session state, cache-aside, pub/sub, leaderboards | Sub-millisecond latency; Enterprise tier supports active geo-replication and RediSearch |
| **Azure Table Storage** | NoSQL key-value (part of Storage) | Simple schemaless data at very low cost | No server to manage; single-digit-millisecond latency at modest scale; not a substitute for Cosmos DB at scale |
| **Azure SQL Edge** | Relational IoT/edge | Constrained edge devices, OPC-UA streaming | ARM64 / x64 container; T-SQL with built-in time-series streaming; offline-first |
| **Azure Database for MariaDB** | Relational PaaS (MariaDB) | OSS MariaDB workloads | Flexible Server, backups, read replicas; confirm [MariaDB feature parity](https://learn.microsoft.com/azure/mariadb/features) for production migration constraints |
| **Azure Arc-enabled SQL / PostgreSQL / MySQL** | Hybrid / edge (managed from Azure) | On-prem, multi-cloud, or edge databases managed via Azure control plane | Same Azure CLI/Portal/Policy experience for on-prem and cloud; not a PaaS replacement for cloud-native deployments |

> **Source metadata:** Service capabilities, limits, and architectural trade-offs in this
> page reflect Azure documentation as of the verification date below. Cloud product limits, SLAs,
> and feature sets change frequently — always confirm against current vendor documentation before
> making a production decision.
>
> **Last verified:** 2026-08-29
> **Primary sources:** [Azure SQL Database documentation](https://learn.microsoft.com/azure/azure-sql/database/sql-database-paas-overview),
> [Azure SQL Managed Instance documentation](https://learn.microsoft.com/azure/azure-sql/managed-instance/sql-managed-instance-paas-overview),
> [Azure Cosmos DB documentation](https://learn.microsoft.com/azure/cosmos-db/),
> [Azure Database for PostgreSQL documentation](https://learn.microsoft.com/azure/postgresql/),
> [Azure Database for MySQL documentation](https://learn.microsoft.com/azure/mysql/),
> [Azure Synapse Analytics documentation](https://learn.microsoft.com/azure/synapse-analytics/),
> [Azure Data Explorer documentation](https://learn.microsoft.com/azure/data-explorer/),
> [Azure AI Search documentation](https://learn.microsoft.com/azure/search/),
> [Azure Cache for Redis documentation](https://learn.microsoft.com/azure/azure-cache-for-redis/),
> [Azure SQL Edge documentation](https://learn.microsoft.com/azure/azure-sql/sql-edge/),
> [Azure Arc documentation](https://learn.microsoft.com/azure/azure-arc/),
> [Azure SLA documentation](https://learn.microsoft.com/azure/support/legal/sla/)

> **Exam tip:** Choose Azure SQL Database when the requirement mentions a cloud-native SQL Server workload
> without OS-level access — serverless, elastic pools, and Hyperscale are differentiators. Choose SQL Managed
> Instance when the requirement mentions SQL Server feature parity (SQL Agent, CLR, cross-database queries) or
> lift-and-shift with VNet placement. Choose SQL Server on Azure VM when the requirement mentions OS-level
> access, custom extensions, or full control over patches. For OSS relational, prefer the managed PostgreSQL/MySQL
> service over an IaaS VM when managed backups, HA, and patching are required. Cosmos DB is the default answer for
> globally distributed NoSQL with SLA-backed availability and multi-region writes. Synapse is the answer for OLAP
> or big-data analytics — it is not a transactional OLTP database. Azure AI Search is not a database — it indexes
> backing stores and should not be chosen as the system of record. Azure Table Storage is the low-cost key-value
> option only for modest-scale workloads already tied to a storage account.

## Relational Databases — Decision Criteria

- **SQL Server workloads.** The next signal is control level: OS-level access → SQL Server on Azure VM;
  SQL Server feature parity (SQL Agent, CLR, cross-database, VNet injection) without OS access → SQL Managed Instance;
  cloud-native new design without those constraints → Azure SQL Database. Azure SQL Database is also the only
  option that supports Serverless auto-pause (General Purpose vCore only) and Hyperscale.
- **PostgreSQL workloads.** Azure Database for PostgreSQL (Flexible Server) is the managed option. Use an Azure VM
  only when the requirement needs OS-level access or extensions not supported by the managed service.
- **MySQL workloads.** Azure Database for MySQL (Flexible Server) is the managed option; use an Azure VM only when
  feature parity or OS-level control is required.
- **MariaDB workloads.** Azure Database for MariaDB (Flexible Server, community-supported) is the managed option;
  confirm feature parity and any migration constraints before choosing it for production. For the full MariaDB feature
  surface, an Azure VM may be required.
- **Mixed environments.** If the same architecture must run on-prem and in Azure under a single control plane,
  Azure Arc-enabled SQL/PostgreSQL/MySQL is the hybrid option — it is not a replacement for cloud-native PaaS
  when the workload is deployed only in Azure.
- **Compatibility caveats.** Managed PostgreSQL, MySQL, and MariaDB services do not expose every engine feature
  that an IaaS VM or on-prem instance would. Before choosing the managed option, confirm extension support, version
  availability, and any feature parity gaps documented by Microsoft.

## NoSQL and Caching — Decision Criteria

- **Cosmos DB** is the default answer for globally distributed NoSQL with SLA-backed availability and multi-region writes.
  Choose the API that matches the existing data model or client — Core SQL, MongoDB, Cassandra, Gremlin, or Table.
  If the requirement mentions session consistency only, the Session consistency level is the most cost-effective
  default; use Strong only when the requirement explicitly demands linearizable reads.
- **Azure Cache for Redis** is the caching answer — session state, cache-aside, leaderboards, pub/sub.
  Choose the Enterprise tier only when active geo-replication, RediSearch, or other Enterprise features are required;
  the Basic/Standard tiers cover most caching scenarios.
- **Azure Table Storage** is a low-cost key-value store inside a Storage Account. It is not a substitute for Cosmos DB
  at scale — there is no multi-region write, no SLA-backed availability beyond the storage account, and no managed
  throughput scaling. Use it for simple, modest-scale key-value scenarios where the existing storage account already
  provides the backing store.
- **Polyglot persistence.** Many architectures combine Cosmos DB (system of record for document/wide-column workloads)
  with Azure Cache for Redis (hot cache) and Azure SQL Database or another relational service. When the requirement
  mentions multiple data access patterns, the answer is often a combination, not a single service.

## Analytics and Search — Decision Criteria

- **Synapse** is the answer for OLAP and big data analytics — not for transactional OLTP. Choose Serverless SQL Pool
  when the requirement mentions querying data in place over ADLS Gen2 with no ETL; choose Dedicated SQL Pool (DWU)
  when the workload has predictable query patterns and defined capacity needs; choose the Spark Pool when the workload
  is big data engineering, Delta Lake, or ML data pipelines.
- **Azure Data Explorer (ADX)** is the answer for real-time telemetry, logs, and IoT data at scale when the primary
  query pattern is ad-hoc KQL over append-only, high-ingestion data. It is not a general-purpose warehouse.
- **Azure AI Search** is the answer when the requirement mentions full-text, semantic, or vector search over documents,
  embeddings, or indexed data. It indexes backing stores — it is not a transactional database and should not be the
  system of record.

## Database Decision Flow

```mermaid
--8<-- "azure/diagrams/database/decision-flow.mmd"
```

> **Exam tip:** Start with the workload domain: relational, NoSQL, analytics, search, or caching. Within
> relational, the next signal is control level (OS access → VM; SQL Server feature parity → SQL MI; cloud-native
> new design → SQL DB). For OSS relational, prefer the managed PostgreSQL/MySQL service over an IaaS VM unless
> OS-level access or an unsupported feature is required. For NoSQL, match the API to the data model and note
> that Azure Table Storage is the low-cost option only when the workload is modest-scale and already tied to a
> storage account. For analytics, Synapse is OLAP — not OLTP. For search, Azure AI Search indexes backing stores
> and is not a system of record.
