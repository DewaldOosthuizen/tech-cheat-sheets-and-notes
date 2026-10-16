# IDENTITY & ACCESS

## IAM and Identity Services

| Service | Type | Best For | Key Feature |
| --- | --- | --- | --- |
| **IAM** | Access control | Users, roles, policies for AWS resources | Fine-grained permissions, resource policies |
| **IAM Identity Center (SSO)** | Workforce SSO | Centralised single sign-on across accounts | SAML/OIDC, built-in directory or external IdP |
| **Cognito User Pools** | App identity | End-user authentication for web/mobile apps | OAuth 2.0, MFA, social federation |
| **Cognito Identity Pools** | Federated credentials | Temporary AWS credentials for app users | Maps identity to IAM role |
| **AWS Organizations** | Multi-account | Account governance and SCPs | Hierarchical OUs, consolidated billing |

> **Exam tip:** IAM roles with STS AssumeRole are the correct answer for
> cross-account access and service-to-service auth. Never use IAM user
> long-term access keys for EC2 or Lambda — attach an IAM role instead.

## Identity & Access Decision Flow

```mermaid
--8<-- "aws/diagrams/identity/decision-flow.mmd"
```

## IAM Policy Evaluation Order

| Step | Action | Key Feature |
| --- | --- | --- |
| **1. Explicit Deny** | Any policy denies → request denied | Overrides all allows |
| **2. SCP check** | Organization SCP denies → denied | Applies before identity policies |
| **3. Resource policy** | Resource-based policy allows → allowed | S3 bucket policies, KMS key policies |
| **4. Identity policy** | IAM policy allows → allowed | User, group, or role policies |
| **5. Permissions boundary** | Must also allow → intersection | Limits max permissions of an entity |

> **Exam tip:** Explicit Deny always wins. When an SCP denies an action,
> no IAM policy in that account can override it, including the root user
> (except for a small set of root-only actions).
