# GOVERNANCE

## Core Governance Services

| Service | Type | Best For | Key Feature |
| --- | --- | --- | --- |
| **Organization Policy** | Constraint enforcement | Enforce GCP resource configuration rules at org/folder/project level | Predefined constraints (e.g. restrict regions, disable APIs, enforce VM IM) and custom constraints (via Common Expression Language) |
| **Resource Manager** | Resource hierarchy | Organise projects into folders and organisations; IAM inheritance | Organisation → Folder → Project hierarchy; IAM policies inherited down the tree |
| **Cloud Asset Inventory** | Resource and policy inventory | Audit, compliance, and cost analysis across projects | Export current asset state to Cloud Storage, BigQuery, or Pub/Sub; asset search API |
| **Billing Budgets** | Cost alerts and actions | Set spend thresholds; trigger notifications and actions when exceeded | Percentage thresholds (e.g. 50%, 90%, 100%); notification channels; programmatic actions via Cloud Functions/webhooks |
| **Policy Troubleshooter** | IAM grant/deny diagnosis | Understand why a principal can or cannot access a resource | Shows which roles, conditions, and deny policies affect a specific permission decision |
| **IAM Recommender** | Unused permission insight | Reduce overly broad roles | Role recommendations based on actual API usage; permissions·강세 analysis |

> **Exam tip:** Organization Policy constraints are the answer when the requirement mentions enforcing a rule that blocks or audits resource configurations across projects or folders — for example, restricting resource locations to specific regions, disabling public IP on VMs, or enforcing that all VMs use a specific service account. Resource Manager provides the hierarchy; IAM policies inherit down the tree (organisation → folder → project). Cloud Asset Inventory provides a point-in-time or continuous inventory of all resources and IAM policies — it is the foundation for audit and compliance tooling.

## Organization Policy Constraints

| Constraint Type | Example | Description |
| --- | --- | --- |
| **List constraint** | `constraints/compute.trustedImageProjects` | Allow or deny a list of values (e.g. allowed image projects) |
| **Boolean constraint** | `constraints/compute.disableNestedVirtualization` | On/off toggle for a feature |
| **Custom constraint** | CEL expression on resource fields | Define your own condition (e.g. all VMs must have a firewall rule allowing only approved ports) |
| **Override** | Per-folder or per-project exemption | Allow a child scope to override a constraint inherited from above |

> **Exam tip:** List constraints enumerate allowed or denied values; boolean constraints toggle a feature. Custom constraints use the Common Expression Language (CEL) to express conditions on resource properties — they are more powerful but also more complex. If a constraint is set at the organisation level, it applies to all projects and folders unless overridden at a child scope.

## Resource Hierarchy

| Level | Purpose |
| --- | --- |
| **Organisation** | Root of the hierarchy — represents the company; organisation-level IAM and org policies apply to all |
| **Folder** | Intermediate grouping — organise by department, environment, or team; inherit IAM and policies from parent |
| **Project** | Lowest-level billable and IAM-scoped unit — resources live inside projects; project-level IAM and policies apply to resources in that project |

> **Exam tip:** IAM policies inherit from parent to child — an organisation-level role grant is inherited by all folders and projects below it. A deny policy at any level overrides any allow at any level. Use folders to group projects by lifecycle, team, or environment for scalable policy and IAM management.

## Billing Budgets

| Feature | Detail |
| --- | --- |
| **Threshold alerts** | Trigger at 50%, 90%, 100%, or custom percentage of budget |
| **Notification channels** | Email, Pub/Sub, webhook |
| **Programmatic actions** | Trigger a Cloud Function or webhook when a threshold is crossed — for example, shut down non-essential resources, alert an on-call engineer |
| **Budget scope** | Apply to a billing account or to specific projects |

> **Exam tip:** Billing budgets are the answer when the requirement mentions alerting when spend exceeds a threshold or taking automated action when a budget limit is approached. Budgets can drive actions via Pub/Sub + Cloud Functions — for example, automatically stopping non-production VMs when spend hits 90% of budget.

## Cloud Asset Inventory

| Capability | Detail |
| --- | --- |
| **Export** | Export current asset state to Cloud Storage (bulk), BigQuery (queryable), or Pub/Sub (streaming) |
| **Search** | Query assets by type, name, labels, and IAM policy |
| **Coverage** | Includes resources, IAM policies, and VPC service controls perimeters |

> **Exam tip:** Cloud Asset Inventory is the answer when the requirement mentions auditing resources or IAM policies across multiple projects — it provides a unified export that can be queried in BigQuery or exported to Cloud Storage for compliance storage. Asset Inventory does not enforce policy — it is a read-only inventory and search tool. Policy enforcement is done by Organization Policy.

## IAM Recommender and Policy Troubleshooter

| Service | What It Does |
| --- | --- |
| **IAM Recommender** | Analyzes actual API usage over a window and recommends removing unused permissions or replacing overly broad roles with narrower predefined roles |
| **Policy Troubleshooter** | Answers "why can this principal access (or not access) this resource?" — shows which roles, conditions, and deny policies contributed to the decision |

> **Exam tip:** Use IAM Recommender to right-size permissions and move toward least privilege. Use Policy Troubleshooter when a user reports access issues — it shows the exact allow/deny path so you can fix the policy without guessing.
