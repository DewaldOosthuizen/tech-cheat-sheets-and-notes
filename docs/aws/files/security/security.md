# SECURITY

## Core Security Services

| Service | Type | Best For | Key Feature |
| --- | --- | --- | --- |
| **GuardDuty** | Threat detection | Anomaly and threat monitoring | ML-based, analyzes CloudTrail/DNS/VPC flow logs |
| **Security Hub** | Posture management | Unified findings across accounts | Aggregates GuardDuty, Inspector, Macie, etc. |
| **AWS WAF** | Web application firewall | L7 DDoS and injection protection | Custom rules, rate limiting, Bot Control |
| **AWS Shield Standard** | DDoS protection | All AWS customers, automatic | Layer 3/4 protection at no extra cost |
| **AWS Shield Advanced** | DDoS protection | Critical workloads, SLA protection | 24/7 DRT support, cost protection, advanced metrics |
| **Amazon Macie** | Data classification | PII and sensitive data discovery in S3 | ML-based content scanning |
| **AWS KMS** | Key management | Encryption key lifecycle management | CMKs, automatic rotation, CloudTrail audit |

> **Exam tip:** GuardDuty detects threats after the fact (detective). AWS WAF
> and Shield prevent attacks in real time (preventive). Security Hub aggregates
> findings but does not act on them.

## Security Decision Flow

```mermaid
--8<-- "aws/diagrams/security/decision-flow.mmd"
```

## Encryption at Rest vs In Transit

| Scenario | Service | Key Feature |
| --- | --- | --- |
| **S3 server-side encryption** | SSE-S3 / SSE-KMS / SSE-C | KMS gives full audit trail and rotation |
| **EBS encryption** | KMS CMK | Transparent to OS, all snapshots encrypted |
| **RDS encryption** | KMS CMK | Must be enabled at creation time |
| **TLS in transit** | ACM certificates | Free managed certs, auto-renews |
| **Secrets rotation** | Secrets Manager | Automatic rotation via Lambda |

> **Exam tip:** ACM certificates are free and auto-renew but can only be used
> with AWS services (ALB, CloudFront, API Gateway). For on-prem or EC2 direct
> TLS termination, import your own certificate or use ACM Private CA.
