# GOVERNANCE

## Governance and Policy Services

| Service | Type | Best For | Key Feature |
| --- | --- | --- | --- |
| **AWS Organizations** | Account management | Multi-account structure, billing consolidation | OUs, SCPs, consolidated billing |
| **Service Control Policies (SCPs)** | Permission guardrails | Maximum permission boundaries per OU/account | Deny-override, no effect on management account |
| **AWS Control Tower** | Landing zone | Automated multi-account baseline with guardrails | Preventive (SCP) and detective (Config) controls |
| **AWS Service Catalog** | Product governance | Pre-approved infrastructure templates for teams | Portfolios, constraints, launch roles |
| **AWS Budgets** | Cost control | Spend alerts and forecasting | Alert on actual or forecasted cost/usage |
| **AWS Cost Anomaly Detection** | Cost monitoring | ML-based unexpected spend detection | Custom monitors per service or linked account |

> **Exam tip:** SCPs restrict what IAM policies CAN allow — they do not grant
> permissions. Even if an IAM policy allows an action, an SCP denying that
> action in the OU prevents it. The management account is never restricted
> by SCPs.

## Governance Decision Flow

```mermaid
--8<-- "aws/diagrams/governance/decision-flow.mmd"
```

## Control Tower Guardrails

| Type | Mechanism | Key Feature |
| --- | --- | --- |
| **Preventive** | SCP | Blocks non-compliant actions before they occur |
| **Detective** | AWS Config rule | Identifies non-compliant resources after creation |
| **Proactive** | CloudFormation hooks | Validates resources before stack deployment |

> **Exam tip:** Control Tower Preventive guardrails use SCPs and cannot be
> worked around by any IAM principal in a governed account. Detective
> guardrails use Config rules and alert after the fact — they do not block.
