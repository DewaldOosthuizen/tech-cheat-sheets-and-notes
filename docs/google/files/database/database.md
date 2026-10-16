# DATABASE

Quick-reference cheat sheet for Google Cloud database services — Cloud SQL, AlloyDB, Cloud Spanner, Firestore, Cloud Bigtable, Memorystore, and BigQuery. Comparison-oriented: which service for which workload, and why.

## Database Service Comparison

||| Service | Type | Best For | Key Feature |
||| --- | --- | --- | --- |
||| **Cloud SQL** | Managed relational (MySQL, PostgreSQL, SQL Server) | Regional OLTP with familiar SQL engines | Managed backups, read replicas, HA configuration, VPC integration |
||| **AlloyDB** | PostgreSQL-compatible, high-performance | Analytical and high-throughput OLTP over the same data | Columnar storage for analytics, low-latency transactional processing, PostgreSQL ecosystem |
||| **Cloud Spanner** | Globally distributed, horizontally scalable relational | Global OLTP with strong consistency and horizontal write scaling | Synchronous replication across regions, SQL semantics, automatic sharding, externally consistent transactions |
||| **Cloud Bigtable** | Wide-column NoSQL | High-throughput, low-latency key-value and time-series | Single-digit-millisecond latency, scales to billions of rows, no secondary indexes |
||| **Firestore** | Document NoSQL | Mobile/web app backends, real-time sync | Offline persistence, real-time listeners, automatic scaling, limited querying with single-field and composite indexes |
||| **Memorystore** | In-memory cache (Redis or Memcached) | Session stores, leaderboards, real-time caching | Managed Redis or Memcached, VPC-native, high throughput and low latency |
||| **BigQuery** | Serverless data warehouse | SQL analytics over petabytes without infrastructure management | On-demand or flat-rate pricing, separation of compute and storage, BI Engine for low-latency, Omni for cross-cloud queries |

> **Source metadata:** Service capabilities, limits, and feature availability in this page reflect Google Cloud documentation as of the verification date below. Cloud product limits and SLAs change frequently — always confirm against current vendor documentation before making a production decision.
>
> **Last verified:** 2026-08-29
> **Primary sources:** [Google Cloud database documentation](https://cloud.google.com/docs/database), [Cloud SQL documentation](https://cloud.google.com/sql/docs), [AlloyDB documentation](https://cloud.google.com/alloydb/docs), [Cloud Spanner documentation](https://cloud.google.com/spanner/docs), [Firestore documentation](https://cloud.google.com/firestore/docs), [Cloud Bigtable documentation](https://cloud.google.com/bigtable/docs), [Memorystore documentation](https://cloud.google.com/memorystore/docs), [BigQuery documentation](https://cloud.google.com/bigquery/docs)

> **Exam tip:** Choose Cloud SQL when you need a managed PostgreSQL/MySQL instance in a single region with familiar tooling. Choose AlloyDB when you need PostgreSQL compatibility with integrated analytical query performance over the same data. Choose Spanner when the requirement mentions global scale, strong consistency across regions, or horizontal write scaling — Spanner is the only option that provides globally synchronous replication with SQL semantics.
>
> Choose Bigtable for large-scale time-series, IoT, or analytics workloads where low-latency key access is critical — it is not a general-purpose document store. Choose Firestore when the workload is a web or mobile application requiring real-time document sync and offline support. BigQuery is the answer for any requirement that mentions SQL analytics at scale without infrastructure management.

## Relational Databases — Decision Criteria

- **Cloud SQL** is the default for single-region managed MySQL, PostgreSQL, or SQL Server. It is the closest match to a traditional managed relational database when global distribution and horizontal write scaling are not required.
- **AlloyDB** is PostgreSQL-compatible and optimised for workloads that need both transactional and analytical query performance over the same data. Prefer AlloyDB over Cloud SQL when analytical queries on transactional data are a first-class requirement and PostgreSQL compatibility is sufficient.
- **Spanner** is the only Google Cloud service that provides globally synchronous replication with SQL semantics. Choose Spanner when the requirement explicitly mentions global scale, strong consistency across regions, horizontal write scaling, or externally consistent transactions. Spanner is not a drop-in PostgreSQL or MySQL replacement — the SQL dialect, schema model, and operational model differ from Cloud SQL and AlloyDB.
- **Compatibility trade-offs.** Cloud SQL and AlloyDB share the PostgreSQL ecosystem; Spanner uses its own SQL dialect and data model. If an existing application expects standard PostgreSQL behaviour, Cloud SQL or AlloyDB is the safer fit. If the requirement demands global strong consistency and horizontal scale, Spanner's trade-offs are usually acceptable.

## NoSQL and Caching — Decision Criteria

- **Bigtable** is the right choice for high-throughput, low-latency key-value and time-series workloads at scale. It does not support secondary indexes or complex queries; direct key access is the primary access pattern.
- **Firestore** is the right choice for web and mobile application backends that need real-time document sync, offline persistence, and automatic scaling. Querying is supported but limited compared to a relational database; composite indexes must be created explicitly.
- **Memorystore** is the right choice for managed in-memory caching. Use Redis when richer data structures, persistence options, or Pub/Sub-style patterns are needed; use Memcached when a simple distributed cache is sufficient.

## Analytics Warehouse — Decision Criteria

- **BigQuery** is the default answer for serverless SQL analytics over large datasets. Use on-demand pricing for variable workloads and flat-rate slots for predictable, sustained workloads. BigQuery Omni allows querying data stored in AWS S3 or Azure Blob Storage from BigQuery.

## Database Decision Flow

```mermaid
--8<-- "google/diagrams/database/decision-flow.mmd"
```
