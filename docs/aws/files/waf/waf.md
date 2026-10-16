# WELL-ARCHITECTED FRAMEWORK

## Six Pillars Overview

| Pillar | Focus | Key AWS Services |
| --- | --- | --- |
| **Operational Excellence** | Run and monitor systems to deliver business value | CloudFormation, Config, CloudTrail, Systems Manager |
| **Security** | Protect information and systems | IAM, KMS, GuardDuty, WAF, Security Hub |
| **Reliability** | Recover from failures and meet demand | Multi-AZ, Auto Scaling, Route 53, AWS Backup |
| **Performance Efficiency** | Use resources efficiently as demand changes | Lambda, Fargate, ElastiCache, CloudFront |
| **Cost Optimization** | Avoid unnecessary costs | Cost Explorer, Savings Plans, Spot Instances, Trusted Advisor |
| **Sustainability** | Minimise environmental impact | Graviton instances, Spot, efficient region selection |

> **Exam tip:** The AWS Well-Architected Framework has six pillars as of 2022
> (Sustainability was added). Questions often ask which pillar a specific design
> decision supports — map cost savings to Cost Optimization, encryption to
> Security, auto-scaling to Reliability or Performance Efficiency.

## Well-Architected Framework Decision Flow

```mermaid
--8<-- "aws/diagrams/waf/decision-flow.mmd"
```

## AWS Well-Architected Tool

| Capability | Use Case | Key Feature |
| --- | --- | --- |
| **Workload review** | Assess workload against framework | Question-based review per pillar |
| **Lens** | Domain-specific reviews | Serverless, SaaS, Analytics, IoT lenses |
| **Milestones** | Track improvement over time | Snapshot reviews at different dates |
| **Trusted Advisor** | Automated checks | 5 categories: Cost, Performance, Security, Fault Tolerance, Service Limits |

> **Exam tip:** AWS Trusted Advisor provides automated real-time checks.
> The Well-Architected Tool requires a guided manual review. Trusted Advisor
> free tier covers only 7 core checks; Business and Enterprise support unlock
> all checks.
