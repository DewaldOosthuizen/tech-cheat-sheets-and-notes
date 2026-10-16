# Governance

## Management Hierarchy

```mermaid
--8<-- "azure/diagrams/governance/management-hierarchy.mmd"
```

| Scope | Purpose |
| --- | --- |
| **Root Management Group** | Apply policies across entire tenant |
| **Management Group** | Group subscriptions, inherit policies |
| **Subscription** | Billing boundary, policy scope |
| **Resource Group** | Lifecycle boundary — deploy/delete together |

## Azure Blueprints vs ARM Templates vs Terraform

| Tool | Purpose | Drift Detection | State | Status |
| --- | --- | --- | --- | --- |
| **ARM Templates** | Deploy resources declaratively | No | Stateless | Active |
| **Bicep** | ARM simplified syntax | No | Stateless | Active |
| **Terraform** | Multi-cloud IaC | Yes (plan) | Stateful | Active |
| **Azure Blueprints** | Governance packages (policy + RBAC + ARM) | Partial (locking) | Artifact-tracked | **RETIRED July 2026** |

> **⚠️ Deprecation warning:** Azure Blueprints is retired (11 July 2026). Migrate to:
>
> - **ARM/Bicep Template Specs** — for reusable, versioned IaC artifacts.
> - **Azure Policy** — for compliance rules and auto-remediation.
> - **RBAC** — for role assignments and least-privilege access.
> Use all three together to replicate what a Blueprint provided as a single package.
>
> See: [Microsoft retirement announcement](https://azure.microsoft.com/en-us/updates/azure-blueprints-is-being-retired-on-11-july-2026/)

> **Exam tip:** Questions about Blueprints reference legacy or existing environments. For new governance designs always specify Template Specs + Policy + RBAC as the replacement pattern.

## Governance Enforcement Decision Flow

```mermaid
--8<-- "azure/diagrams/governance/governance-enforcement-decision-flow.mmd"
```

> **Exam tip:** When a question mentions enforcing a rule that blocks or auto-remediates
> non-compliant resources across subscriptions, the answer is Azure Policy — not Locks
> (which only prevent delete/write) and not Management Groups (which are the scope, not the
> enforcement tool).

## Cost Management

| Tool | Purpose |
| --- | --- |
| **Azure Cost Management** | View, analyze, alert on spending |
| **Budgets** | Set spend thresholds, trigger alerts/actions |
| **Azure Advisor (Cost)** | Right-sizing and reservation recommendations |
| **Reserved Instances** | 1 or 3 year commit — up to 72% savings |
| **Spot VMs** | Evictable — up to 90% savings for fault-tolerant workloads |
| **Azure Hybrid Benefit** | Use existing Windows Server / SQL licenses |

## Tags

- Applied at: Resource, Resource Group, Subscription level
- Inherited? **No** — tags don't inherit by default (use Azure Policy to enforce inheritance)
- Max: 50 tags per resource
- Use cases: cost center, environment, owner, project

## Resource Locks

Resource locks prevent accidental modification or deletion of Azure resources.
They are applied at subscription, resource group, or resource scope and inherited
by all child resources. Locks are ARM-level controls — they apply to any principal
regardless of RBAC role, except that only **Owner** and **User Access Administrator**
(or a custom role with `Microsoft.Authorization/locks/write`) can create or remove them.
The built-in **Contributor** role cannot manage locks.

| Lock Type | Prevents | Allows |
| --- | --- | --- |
| **CanNotDelete** | Delete operations only | All read and write (update) operations |
| **ReadOnly** | All write and delete operations | Read operations only |

### CanNotDelete Lock

The resource can be read and modified freely but not deleted. This is the safer default
for production resources — it allows operational actions (scale, config update, restart)
while blocking accidental or malicious deletion.

Common targets: production databases, storage accounts, Key Vaults, VNets, NSGs.

Does NOT prevent: tag updates, SKU changes, scale events, data-plane operations.

### ReadOnly Lock

The resource can only be read. No create, update, or delete ARM operations are
permitted on the locked resource or its children. Has several non-obvious side effects
that frequently appear in exam scenarios:

- `listKeys` on a storage account is classified as a write — applications calling it
  will receive `AuthorizationFailed` under a ReadOnly lock.
- Starting or stopping a VM is a write operation — ReadOnly-locked VMs cannot be
  started or deallocated.
- Moving resources out of a ReadOnly-locked resource group is blocked.
- Adding a subnet to a ReadOnly-locked VNet is blocked.

Common targets: shared networking infrastructure, reference configurations, hub VNets.

Does NOT prevent: data-plane reads (blob data, SQL queries via existing connections)
— the lock only controls ARM management-plane operations.

### Lock Inheritance and Scope

| Scope | Applies To |
| --- | --- |
| **Subscription** | All resource groups and resources in the subscription |
| **Resource Group** | All resources within the resource group |
| **Resource** | That resource only |

Locks applied at a parent scope cannot be overridden by child resources. A Contributor
at the child scope cannot remove a lock placed by an Owner at the parent scope.

> **Exam tip:** CanNotDelete is the standard choice for protecting production resources —
> it blocks accidental deletion while preserving operational flexibility. ReadOnly is more
> restrictive and has non-obvious ARM side effects (storage listKeys, VM start/stop).
> Contributor cannot remove locks — Owner is required. This is a common AZ-104/AZ-500
> scenario. Locks do NOT enforce configuration compliance — use Azure Policy for that.
> Locks guard against specific ARM operations; Policy guards against configuration drift.

## Azure Policy Types

Azure uses the word "policy" across many services. Each refers to a distinct control
mechanism with a different scope, enforcement model, and configuration surface.

| Policy Type | Layer | Service | Purpose |
| --- | --- | --- | --- |
| **Azure Policy** | ARM / Governance | All Azure resources | Enforce, audit, or auto-remediate resource configuration compliance |
| **Azure Firewall Policy** | Network | Azure Firewall | Centrally manage DNAT, network, and application rule collections |
| **WAF Policy** | Network / App | App Gateway, Front Door | Block OWASP-based web attacks; custom rules; rate limiting |
| **Key Vault Access Policy** | Security | Azure Key Vault | Legacy per-principal permission grants for secrets, keys, certificates |
| **Conditional Access Policy** | Identity | Microsoft Entra ID | Enforce sign-in conditions: MFA, device compliance, location, risk |
| **DDoS Protection Policy** | Network | Azure DDoS Protection | Adaptive L3/L4 attack mitigation linked to a VNet |
| **Service Endpoint Policy** | Network | Virtual Network | Restrict service endpoint traffic to specific approved storage accounts |
| **Private Endpoint Policy** | Network | Virtual Network | Enable NSG and UDR enforcement on private endpoint subnets |

### Azure Policy (Governance)

The core governance control plane. Evaluates resources against defined rules at creation,
update, and on-demand. Assigned at management group, subscription, or resource group scope.

Policy effects, from most to least restrictive:

| Effect | Behaviour | Use Case |
| --- | --- | --- |
| **Disabled** | No evaluation | Temporarily suspend a rule |
| **Deny** | Block non-compliant create or update | Prevent unapproved SKUs, regions, configurations |
| **Audit** | Allow but flag as non-compliant | Visibility without blocking; stepping stone before Deny |
| **Modify** | Auto-add or update resource properties | Enforce tag inheritance, enforce minimum TLS version |
| **Append** | Append fields to the resource definition | Add allowed IP rules to storage accounts |
| **AuditIfNotExists** | Audit if a companion resource is absent | Flag VMs without a monitoring agent extension |
| **DeployIfNotExists** | Deploy a companion resource if absent | Auto-deploy diagnostic settings, Azure Monitor agent |

Initiatives (Policy Sets) bundle related policies under one assignment. Pre-built regulatory
initiatives include CIS, NIST SP 800-53, ISO 27001, PCI-DSS, and HIPAA. DeployIfNotExists
requires a managed identity on the policy assignment to perform remediation.

### Azure Firewall Policy

A hierarchical, centrally managed rule set that configures one or more Azure Firewall
instances. Supports parent/child policy inheritance for hub-and-spoke topologies — the
hub policy holds baseline rules; spoke policies extend or override them.

| Rule Collection Type | Protocol | Use Case |
| --- | --- | --- |
| **DNAT rules** | Any | Inbound NAT — translate public IP to a private backend |
| **Network rules** | L4 (IP / port / protocol) | East-west and egress filtering |
| **Application rules** | L7 (FQDN / URL / category) | Egress web traffic control |

- Threat Intelligence mode: Alert or Deny for known malicious IPs and domains.
- DNS Proxy: required for FQDN-based rules to resolve correctly.
- Premium SKU adds IDPS, TLS inspection, and URL-category filtering.

> **Exam tip:** Firewall Policy replaces the legacy "classic" rules model. Use it when
> the requirement mentions centralising rules across multiple firewalls or hub-and-spoke.
> Policy supports parent/child inheritance; classic rules do not.

### WAF Policy (Web Application Firewall)

Attached to Azure Application Gateway (regional) or Azure Front Door (global). Defines
detection/prevention mode, OWASP CRS version, custom rules, exclusions, and rate limits.

| Mode | Behaviour |
| --- | --- |
| **Detection** | Log matched rules without blocking |
| **Prevention** | Block and log requests matching rules |

Custom rules support IP allow/block lists, geo-filtering, rate limiting, and
header/URI string matching. Exclusions suppress specific request attributes from
evaluation (for example, a legitimate auth header that triggers a false positive).

> **Exam tip:** WAF on Application Gateway is regional; WAF on Front Door is global edge.
> Choose Front Door WAF for global, multi-region workloads. Choose Application Gateway WAF
> for single-region workloads requiring path-based routing combined with WAF.

### Key Vault Access Policy (Legacy)

A per-principal permission model for Key Vault that predates Azure RBAC. Grants
get/list/set/delete permissions independently for secrets, keys, and certificates.
Maximum 1,024 access policies per vault.

| Operation Group | Operations |
| --- | --- |
| **Read** | Get, List |
| **Write** | Set, Create, Import |
| **Lifecycle** | Delete, Purge, Recover, Backup, Restore |

Permissions are vault-scoped — one policy entry covers all secrets in the vault,
not individual secrets. Azure RBAC can scope permissions to individual secrets, keys,
or certificates and is the recommended model for new deployments.

> **Exam tip:** Key Vault Access Policy is legacy — Microsoft recommends migrating to
> Azure RBAC. RBAC provides Entra audit trails, PIM support, and per-resource granularity.
> Access Policy appears in exam scenarios referencing existing environments or migrations.

### Conditional Access Policy

Entra ID policies that evaluate sign-in signals and enforce conditions before issuing
tokens. Evaluated on every authentication event against all matching policies.

| Signal Category | Examples |
| --- | --- |
| **User / Group** | All users, admin roles, specific groups |
| **Application** | Specific app registrations (e.g. Azure Portal) |
| **Location** | Named IP ranges, countries |
| **Device** | Intune-compliant, Hybrid Entra joined |
| **Risk** | Sign-in risk or user risk (requires Entra ID P2) |

| Grant Control | Effect |
| --- | --- |
| **Block** | Deny access entirely |
| **Require MFA** | Prompt for a second factor |
| **Require compliant device** | Enforce Intune device compliance |
| **Require approved client app** | MAM-managed app only |
| **Require app protection policy** | Intune App Protection Policy |

> **Exam tip:** Conditional Access requires Entra ID P1 (basic conditions) or P2
> (risk-based conditions via Identity Protection). Emergency break-glass accounts
> must be excluded to prevent admin lockout. Named Locations can mark corporate
> IP ranges as trusted to skip MFA from those IPs.

### DDoS Protection Policy

Linked to one or more VNets to activate Azure DDoS Network Protection. Provides
adaptive per-resource mitigation tuned to observed normal traffic baselines.

| Plan | Scope | Cost Model |
| --- | --- | --- |
| **DDoS IP Protection** | Single public IP | Per protected public IP address |
| **DDoS Network Protection** | All public IPs in linked VNets | Fixed monthly fee + data; includes rapid response support |

Infrastructure Protection (free, always-on) defends the Azure platform but provides
no telemetry, custom alerting, or cost guarantees to individual workloads.

> **Exam tip:** Choose DDoS Network Protection when the requirement mentions SLA,
> attack telemetry, mitigation reports, or the cost guarantee (Azure credits for
> scale-out costs incurred during an attack). Basic/Infrastructure Protection is
> always on but provides none of those guarantees.

### Service Endpoint Policy

Applied to a subnet's service endpoint configuration to restrict which specific
resources (e.g. individual storage accounts) are reachable via the endpoint.
Without a Service Endpoint Policy, the endpoint allows access to all resources
of that service type in the region.

Supported services: Azure Storage (GA), Azure Cosmos DB (preview).

> **Exam tip:** Service Endpoint Policy narrows the destination — not the path.
> Traffic still routes over the Microsoft backbone with the VNet private IP as
> source. It is not the same as Private Endpoint, which removes the resource from
> the public internet entirely. Use Private Endpoint when full network isolation
> is required; use Service Endpoint Policy when filtering destination within an
> existing service-endpoint-based design.

### Private Endpoint Policy

Enables NSG rules and User-Defined Routes (UDRs) to be applied to private endpoint
network interfaces. By default, NSGs and UDRs are bypassed for private endpoint
traffic on a subnet.

Enabled per subnet by setting `PrivateEndpointNetworkPolicies = Enabled` on the subnet.
Required when you need NSG deny rules or custom routing to control private endpoint traffic.

> **Exam tip:** If an NSG attached to a subnet containing private endpoints is not
> blocking expected traffic, the most likely cause is that Private Endpoint Network
> Policies are disabled (the default). Enable them on the subnet to restore NSG
> and UDR enforcement for private endpoint NICs.

## Azure Lighthouse

Azure Lighthouse enables **cross-tenant management** — a service provider (MSP) or central IT
team can manage customer or subsidiary tenant resources from their own tenant without switching
directories or maintaining guest accounts.

| Service | Type | Best For | Key Feature |
| --- | --- | --- | --- |
| **Azure Lighthouse** | Cross-tenant delegation | MSP managing multiple customer tenants; enterprise hub managing subsidiaries | Azure Resource Manager delegation; no credential sharing; full Azure RBAC applies |

> **Exam tip:** Choose Azure Lighthouse when the requirement mentions an MSP or central IT team
> managing resources across multiple Azure tenants without separate logins. Lighthouse uses
> Azure Delegated Resource Management — the customer retains ownership; the provider sees and
> acts on customer resources from their own tenant. Distinguish from Azure B2B guest access,
> which is per-user and not suited for at-scale managed service operations.

## Azure Policy Assignment Scopes

| Service | Layer | Scope | Use Case | Key Feature |
| --- | --- | --- | --- | --- |
| **Policy at Management Group** | Governance | All subscriptions below | Org-wide standards | Inherits down to all child subscriptions/RGs |
| **Policy at Subscription** | Governance | All RGs in subscription | Subscription-level compliance | Overrides MG exclusions for that subscription |
| **Policy at Resource Group** | Governance | RG only | Scoped enforcement | Most granular assignment scope |
| **Initiative (Policy Set)** | Governance | Any scope | Group related policies | Single assignment; compliance aggregated |

> **Exam tip:** Policy effects in priority order: Disabled > Audit > Deny > Modify > DeployIfNotExists > AuditIfNotExists. DeployIfNotExists requires a managed identity on the assignment to remediate.

### Policy Assignment Scope Hierarchy

```mermaid
--8<-- "azure/diagrams/governance/policy-assignment-scope-hierarchy.mmd"
```

## Management Groups & Subscriptions

| Service | Type | Best For | Key Feature |
| --- | --- | --- | --- |
| **Management Group** | Org hierarchy | Policy and RBAC at scale | Up to 6 levels deep; root MG always present |
| **Subscription** | Billing + access | Resource isolation, billing boundary | RBAC root; limits apply per subscription |
| **Resource Group** | Logical grouping | Lifecycle management | All resources must belong to one RG |

> **Exam tip:** You can move a subscription between Management Groups but you cannot move a Management Group into another tenant. RBAC assigned at MG level is inherited by all subscriptions below it.

### Management Hierarchy Decision Flow

```mermaid
--8<-- "azure/diagrams/governance/management-hierarchy-decision-flow.mmd"
```
