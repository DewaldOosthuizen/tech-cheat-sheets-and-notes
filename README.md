# Tech Cheat Sheets And Notes

[![Lint](https://github.com/DewaldOosthuizen/tech-cheat-sheets-and-notes/actions/workflows/lint.yml/badge.svg?branch=main&event=push)](https://github.com/DewaldOosthuizen/tech-cheat-sheets-and-notes/actions/workflows/lint.yml)
[![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg)](https://www.paypal.com/paypalme/DewaldOosthuizen1)

You can view the live site at [![Live Site](https://img.shields.io/badge/Live%20Site-tech--cheat--sheets--and--notes.vercel.app-black?logo=vercel&logoColor=white)](https://tech-cheat-sheets-and-notes.vercel.app)

A growing collection of technology cheat sheets — quick-reference study notes organised by topic
and certification track. Comparisons between services, decision flows, and Mermaid diagrams that
answer "which one and why?" — not step-by-step tutorials or portal walkthroughs.

## Current Content

|| Topic |
||-------|
|| [Microsoft Azure](docs/azure/index.md) |
|| [Amazon Web Services](docs/aws/index.md) |
|| [Google Cloud](docs/google/index.md) |
|| [Programming (Java)](docs/programming/java/index.md) |

More topics (other cloud providers, DevOps tooling, architecture patterns) will be added over time.
Each new topic lives under its own subdirectory inside `docs/`.

### Microsoft Azure

|| Domain | Content |
||-------|-------|
|| [Networking](docs/azure/files/networking/networking.md) | Load balancers, APIM, VNet, DNS, NSG, DDoS, CDN |
|| [Security](docs/azure/files/security/security.md) | Defender for Cloud, Key Vault, Sentinel, Encryption |
|| [Database](docs/azure/files/database/database.md) | SQL DB, SQL MI, SQL on VM, PostgreSQL, MySQL, Cosmos DB, Synapse, ADX, AI Search, Redis, Table, Arc |
|| [Storage](docs/azure/files/storage/storage.md) | Blob, Files, Disk, redundancy |
|| [Compute](docs/azure/files/compute/compute.md) | VMs, App Service, Functions, AKS, ACI, Batch |
|| [Identity & Access](docs/azure/files/identity/identity.md) | Entra ID, RBAC, PIM, Hybrid Identity |
|| [Monitoring & Observability](docs/azure/files/monitoring/monitoring.md) | Azure Monitor, Log Analytics, Alerts, Agents |
|| [Messaging & Integration](docs/azure/files/messaging/messaging.md) | Service Bus, Event Grid, Logic Apps, Functions |
|| [Governance](docs/azure/files/governance/governance.md) | Policy, Blueprints, Management Groups, Cost |
|| [High Availability & DR](docs/azure/files/ha-dr/ha-dr.md) | ASR, Azure Backup, Availability Zones |
|| [Well-Architected Framework](docs/azure/files/waf/waf.md) | Five pillars, trade-off navigator |

### Amazon Web Services

|| Domain | Content |
||-------|-------|
|| [Compute](docs/aws/files/compute/compute.md) | EC2, Lambda, ECS, EKS, Elastic Beanstalk |
|| [Networking](docs/aws/files/networking/networking.md) | VPC, Route 53, CloudFront, ELB, API Gateway |
|| [Storage](docs/aws/files/storage/storage.md) | S3, EBS, EFS, Glacier, Storage Gateway |
|| [Identity & Access](docs/aws/files/identity/identity.md) | IAM, Organizations, SSO, Cognito |
|| [Security](docs/aws/files/security/security.md) | GuardDuty, Security Hub, WAF, Shield, KMS |
|| [Database](docs/aws/files/database/database.md) | RDS, Aurora, DynamoDB, ElastiCache, Redshift |
|| [Monitoring & Observability](docs/aws/files/monitoring/monitoring.md) | CloudWatch, CloudTrail, X-Ray, Config |
|| [Messaging & Integration](docs/aws/files/messaging/messaging.md) | SQS, SNS, EventBridge, Step Functions |
|| [Governance](docs/aws/files/governance/governance.md) | Organizations, SCPs, Control Tower, Budgets |
|| [High Availability & DR](docs/aws/files/ha-dr/ha-dr.md) | Multi-AZ, Multi-Region, AWS Backup, Route 53 |
|| [Well-Architected Framework](docs/aws/files/waf/waf.md) | Six pillars, trade-off navigator |

### Google Cloud

|| Domain | Content |
||-------|-------|
|| [Compute](docs/google/files/compute/compute.md) | Compute Engine, GKE, Cloud Run, Cloud Functions, App Engine |
|| [Networking](docs/google/files/networking/networking.md) | VPC, Cloud Load Balancing, Cloud CDN, Cloud DNS, Cloud NAT, Cloud Armor |
|| [Storage](docs/google/files/storage/storage.md) | Cloud Storage, Persistent Disk, Filestore |
|| [Database](docs/google/files/database/database.md) | Cloud SQL, AlloyDB, Spanner, Firestore, Bigtable, Memorystore, BigQuery |
|| [Identity & Access](docs/google/files/identity/identity.md) | Cloud IAM, Cloud Identity, Workload Identity, Service Accounts, IAP |
|| [Security](docs/google/files/security/security.md) | SCC, Secret Manager, Cloud KMS, Binary Authorization, VPC Service Controls, Cloud Armor |
|| [Monitoring & Observability](docs/google/files/monitoring/monitoring.md) | Cloud Monitoring, Cloud Logging, Cloud Trace, Cloud Profiler, Cloud Debugger |
|| [Messaging & Integration](docs/google/files/messaging/messaging.md) | Pub/Sub, Eventarc, Workflows, Cloud Tasks, API Gateway |
|| [Governance](docs/google/files/governance/governance.md) | Organization Policy, Resource Manager, Cloud Asset Inventory, Billing Budgets, Policy Troubleshooter |
|| [High Availability & DR](docs/google/files/ha-dr/ha-dr.md) | Regional vs multi-regional, Cloud DNS failover, Cloud Load Balancing global failover, Backup for GCE, Spanner replication |
|| [Well-Architected Framework](docs/google/files/waf/waf.md) | Six pillars, trade-off navigator |

### Programming (Java)

|| Domain | Content |
||-------|-------|
|| [Language Fundamentals](docs/programming/java/files/language-fundamentals/language-fundamentals.md) | Syntax, keywords, types, strings |
|| [OOP](docs/programming/java/files/oop/oop.md) | Encapsulation, inheritance, polymorphism, abstraction |
|| [Functional Programming](docs/programming/java/files/functional-programming/functional-programming.md) | Lambdas, streams, functional interfaces |
|| [Persistence](docs/programming/java/files/persistence/persistence.md) | JDBC, JPA, ORM trade-offs |
|| [Spring Boot](docs/programming/java/files/spring-boot/spring-boot.md) | Auto-configuration, starters, DI, actuator, profiles, observability, native images |
|| [Collections](docs/programming/java/files/collections/collections.md) | List, Set, Map, concurrent collections |

## Repository Structure

```
docs/
  azure/
    files/
      <domain>/<domain>.md       — One page per domain (networking, security, …)
    diagrams/<section>/         — standalone Mermaid diagram sources (one per file)
      <slug>.mmd                — exam-agnostic slug
    files/<section>/            — shared section snippet files
      <section>.md              — e.g. networking/networking.md
  aws/
    files/
      <domain>/<domain>.md       — One page per domain (compute, networking, …)
    diagrams/<section>/
      <slug>.mmd
  google/
    files/
      <domain>/<domain>.md       — One page per domain (compute, networking, …)
    diagrams/<section>/
      <slug>.mmd
  index.md                      — MkDocs site home page
mkdocs.yml                      — MkDocs Material site configuration
```

Section directories under `docs/azure/diagrams/` and `docs/azure/files/`:
`networking`, `security`, `storage`, `monitoring`, `compute`, `identity`,
`ha-dr`, `governance`, `messaging`, `waf`

## Local Setup

Requirements: Python 3.11+, Node/npm on PATH.

```bash
# One-time per clone: creates .venv, installs Python + Node deps
make install

# Install pre-commit hooks (optional but recommended)
.venv/bin/pip install pre-commit
.venv/bin/pre-commit install
```

## Viewing the Documentation Site

Serve it locally with hot-reload:

```bash
make start   # opens http://127.0.0.1:8000
```

Build a static copy:

```bash
make docs-build   # output in site/
```

GitHub also renders Mermaid natively in Markdown files. VS Code users can
install `Markdown Preview Mermaid Support` to render diagrams in the editor
preview.

## Running CI Locally

```bash
make ci
```

Runs in order: markdownlint, Mermaid validation, ruff lint + format check,
pytest with coverage, and a strict MkDocs build. A failing `make ci` means
the GitHub Actions pipeline will also fail — fix it before opening a PR.

For dead-link checking, run:

```bash
make link-check
```

`make link-check` bootstraps a pinned Lychee binary into `.tools/` on first
use, so no global Lychee installation is required.

## Contributing

Contributions are welcome. Please read [CONTRIBUTING.md](CONTRIBUTING.md) for
the full workflow: picking up an issue, branch naming, content style, coding
standards, and the pull request process.

## License

This project is licensed under the [`GPL-3.0`](LICENSE).
