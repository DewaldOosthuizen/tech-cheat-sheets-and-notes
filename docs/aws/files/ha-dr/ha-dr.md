# HIGH AVAILABILITY & DR

## HA and DR Strategies

| Service | Type | Best For | Key Feature |
| --- | --- | --- | --- |
| **Multi-AZ (RDS, ALB, EKS)** | Zone redundancy | Single-region HA | Synchronous standby, auto-failover |
| **Multi-Region Active-Active** | Geographic redundancy | Near-zero RTO/RPO | Route 53 latency/failover routing |
| **Multi-Region Warm Standby** | Reduced-capacity standby | Minutes RTO | Scaled-down replica ready to promote |
| **Pilot Light** | Minimal standby | Hours RTO, cost-optimised | Core data replicated, services off until needed |
| **Backup and Restore** | Scheduled backups | Cheapest, hours RPO/RTO acceptable | AWS Backup, S3 cross-region copy |
| **AWS Backup** | Centralised backup | Multi-service policy-driven backup | Supports RDS, EFS, DynamoDB, EC2, EBS |

> **Exam tip:** Know the four DR patterns in order of cost and speed:
> Backup/Restore (cheapest, slowest) → Pilot Light → Warm Standby →
> Active-Active (most expensive, fastest). Match the pattern to the stated
> RTO and RPO in the question.

## High Availability & DR Decision Flow

```mermaid
--8<-- "aws/diagrams/ha-dr/decision-flow.mmd"
```

## RTO vs RPO Reference

| Metric | Definition | Key Feature |
| --- | --- | --- |
| **RTO** | Recovery Time Objective — max tolerable downtime | Drives architecture tier choice |
| **RPO** | Recovery Point Objective — max tolerable data loss | Drives replication frequency |
| **MTTR** | Mean Time To Recover | Operational measure, not an SLA input |
| **MTBF** | Mean Time Between Failures | Reliability measure for component selection |

> **Exam tip:** RTO maps to downtime tolerance; RPO maps to data loss
> tolerance. A question asking for "no data loss" implies RPO = 0,
> which requires synchronous replication (Multi-AZ or Aurora Global).
