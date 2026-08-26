# Tech Cheat Sheets And Notes

[![Lint](https://github.com/DewaldOosthuizen/tech-cheat-sheets-and-notes/actions/workflows/lint.yml/badge.svg?branch=main&event=push)](https://github.com/DewaldOosthuizen/tech-cheat-sheets-and-notes/actions/workflows/lint.yml)
[![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg)](https://www.paypal.com/paypalme/DewaldOosthuizen1)

Quick-reference study notes for technology certifications and architecture decisions.
Each sheet answers *which service, which pattern, and why* — not how to click through a portal.
Content is comparison-oriented: tables, decision flowcharts, and Mermaid diagrams side-by-side.

---

## Cloud Service Providers

### Microsoft Azure

Organised by domain. Each section covers service selection and architectural trade-offs.

| Domain | Content |
|--------|---------|
| [Networking](azure/files/networking/networking.md) | Load balancers, APIM, VNet, DNS, NSG, DDoS, CDN |
| [Security](azure/files/security/security.md) | Defender for Cloud, Key Vault, Sentinel, Encryption |
| [Storage](azure/files/storage/storage.md) | Blob, Files, Disk, SQL, Cosmos DB, redundancy |
| [Migration](azure/files/migration/migration.md) | Azure Migrate, DMS, Data Box, ASR, ASMA, SMS, Arc |
| [Monitoring & Observability](azure/files/monitoring/monitoring.md) | Azure Monitor, Log Analytics, Alerts, Agents |
| [Compute](azure/files/compute/compute.md) | VMs, App Service, Functions, AKS, ACI, Batch |
| [Identity & Access](azure/files/identity/identity.md) | Entra ID, RBAC, PIM, Hybrid Identity |
| [High Availability & DR](azure/files/ha-dr/ha-dr.md) | ASR, Azure Backup, Availability Zones |
| [Governance](azure/files/governance/governance.md) | Policy, Blueprints, Management Groups, Cost |
| [Messaging & Integration](azure/files/messaging/messaging.md) | Service Bus, Event Grid, Logic Apps, Functions |
| [Well-Architected Framework](azure/files/waf/waf.md) | Five pillars, trade-off navigato

See the [Azure Exam Track Index](azure/files/exams/exams.md) for full coverage by certification.

### Amazon Web Services

Organised by domain. Each section covers service selection and architectural trade-offs.

|| Domain | Content |
||--------|---------|
|| [Compute](aws/files/compute/compute.md) | EC2, Lambda, ECS, EKS, Elastic Beanstalk |
|| [Networking](aws/files/networking/networking.md) | VPC, Route 53, CloudFront, ELB, API Gateway |
|| [Storage](aws/files/storage/storage.md) | S3, EBS, EFS, Glacier, Storage Gateway |
|| [Identity & Access](aws/files/identity/identity.md) | IAM, Organizations, SSO, Cognito |
|| [Security](aws/files/security/security.md) | GuardDuty, Security Hub, WAF, Shield, KMS |
|| [Database](aws/files/database/database.md) | RDS, Aurora, DynamoDB, ElastiCache, Redshift |
|| [Monitoring & Observability](aws/files/monitoring/monitoring.md) | CloudWatch, CloudTrail, X-Ray, Config |
|| [Messaging & Integration](aws/files/messaging/messaging.md) | SQS, SNS, EventBridge, Step Functions |
|| [Governance](aws/files/governance/governance.md) | Organizations, SCPs, Control Tower, Budgets |
|| [High Availability & DR](aws/files/ha-dr/ha-dr.md) | Multi-AZ, Multi-Region, AWS Backup, Route 53 |
|| [Well-Architected Framework](aws/files/waf/waf.md) | Six pillars, trade-off navigator |

See the [AWS Exam Track Index](aws/files/exams/exams.md) for full coverage by certification.

### Google Cloud

Organised by domain. Each section covers service selection and architectural trade-offs.

|| Domain | Content |
||--------|---------|
|| [Compute](google/files/compute/compute.md) | Compute Engine, GKE, Cloud Run, Cloud Functions, App Engine |
|| [Networking](google/files/networking/networking.md) | VPC, Cloud Load Balancing, Cloud CDN, Cloud DNS, Cloud NAT, Cloud Armor |
|| [Storage](google/files/storage/storage.md) | Cloud Storage, Persistent Disk, Filestore, Bigtable, Spanner, Firestore, BigQuery |
|| [Identity & Access](google/files/identity/identity.md) | Cloud IAM, Cloud Identity, Workload Identity, Service Accounts, IAP |
|| [Security](google/files/security/security.md) | SCC, Secret Manager, Cloud KMS, Binary Authorization, VPC Service Controls, Cloud Armor |
|| [Monitoring & Observability](google/files/monitoring/monitoring.md) | Cloud Monitoring, Cloud Logging, Cloud Trace, Cloud Profiler, Cloud Debugger |
|| [Messaging & Integration](google/files/messaging/messaging.md) | Pub/Sub, Eventarc, Workflows, Cloud Tasks, API Gateway |
|| [Governance](google/files/governance/governance.md) | Organization Policy, Resource Manager, Cloud Asset Inventory, Billing Budgets, Policy Troubleshooter |
|| [High Availability & DR](google/files/ha-dr/ha-dr.md) | Regional vs multi-regional, Cloud DNS failover, Cloud Load Balancing global failover, Backup for GCE, Spanner replication |
|| [Well-Architected Framework](google/files/waf/waf.md) | Six pillars, trade-off navigator |

See the [Google Cloud Exam Track Index](google/files/exams/exams.md) for full coverage by certification.

---

## Programming

Quick-reference sheets for Java language fundamentals and the Spring Boot framework.

|| Domain | Content |
||--------|---------|
|| [Abbreviations](programming/files/abbreviations/abbreviations.md) | Java and Spring Boot acronyms |
|| [Exam Coverage](programming/files/exams/exams.md) | Java certification exam mapping by topic |
|| [Language Fundamentals](programming/files/language-fundamentals/language-fundamentals.md) | Syntax, keywords, types, strings |
|| [OOP](programming/files/oop/oop.md) | Encapsulation, inheritance, polymorphism, abstraction |
|| [Functional Programming](programming/files/functional-programming/functional-programming.md) | Lambdas, streams, functional interfaces |
|| [Persistence](programming/files/persistence/persistence.md) | JDBC, JPA, ORM trade-offs |
|| [Spring Boot](programming/files/spring-boot/spring-boot.md) | Auto-configuration, starters, DI, actuator, profiles, observability, native images |
|| [Collections](programming/files/collections/collections.md) | List, Set, Map, concurrent collections |

---

## How to Use These Sheets

The cheat sheets are not meant to be read cover-to-cover. Jump to the section relevant to what
you are studying. Each section contains:

- A comparison table of services in that domain
- Exam-tip callouts that highlight common decision points in exam questions
- One or more Mermaid decision flowcharts for branching "which service?" scenarios
- Deprecation notices where a service has been retired or superseded

The live site renders all diagrams inline. To browse locally, run `make docs-serve`.

---

## Contributing

See [CONTRIBUTING.md](https://github.com/DewaldOosthuizen/tech-cheat-sheets-and-notes/blob/main/CONTRIBUTING.md)
for the full contributor workflow.

## License

This project is licensed under the [`GPL-3.0`](https://github.com/DewaldOosthuizen/tech-cheat-sheets-and-notes/blob/main/LICENSE).
