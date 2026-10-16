# Identity & Access

## Entra ID (Azure AD) Concepts

| Concept | Description |
| --- | --- |
| **Tenant** | Dedicated Entra ID instance for org |
| **User** | Human identity |
| **Service Principal** | App identity (manual credential management) |
| **Managed Identity** | Azure-managed service principal — no credentials |
| **System-Assigned MI** | Tied to resource lifecycle, auto-deleted |
| **User-Assigned MI** | Independent lifecycle, shared across resources |
| **Groups** | Security or M365, for role assignment |
| **App Registration** | Define an application in Entra ID |

### System Identity Type Decision Flow

```mermaid
--8<-- "azure/diagrams/identity/system-identity-type-decision-flow.mmd"
```

> **Exam tip:** Prefer Managed Identity over Service Principal whenever the
> workload runs in Azure and supports Entra-based managed identity auth.

## Entra Identity Scenarios

| Scenario | Solution | Tenant Type |
| --- | --- | --- |
| Employee / workforce identity | Entra ID (workforce tenant) | Workforce |
| Partner / vendor B2B access | Entra B2B (guest users) | Workforce |
| Customer-facing app identity | Entra External ID (external tenant) | External / CIAM |

> **Exam tip:** Entra External ID is the successor to Azure AD B2C for new customer identity
> (CIAM) projects. Existing B2C tenants continue to be supported, but new designs should target
> Entra External ID (external tenant). Do not confuse B2B guest users (workforce tenant) with
> External ID (separate external tenant).

### Entra Identity Scenario Decision Flow

```mermaid
--8<-- "azure/diagrams/identity/entra-identity-scenario-decision-flow.mmd"
```

## MSAL Authentication Flows (AZ-204)

| Service | Flow | Use Case | Key Feature |
| --- | --- | --- | --- |
| MSAL | Authorization Code + PKCE | Interactive sign-in from a browser SPA or native app | PKCE eliminates the need for a client secret in public clients; most secure interactive flow |
| MSAL | Client Credentials | Daemon or service-to-service call with no signed-in user | Uses app identity (client ID + secret or certificate); no user context |
| MSAL | On-Behalf-Of (OBO) | Middle-tier API calls a downstream API on behalf of the signed-in user | Middle tier exchanges its access token for a new token scoped to the downstream API |
| MSAL | Device Code | Input-constrained devices (CLI tools, smart TVs, IoT) | Device displays a code; user authenticates on a separate browser |

> **Exam tip:** On-behalf-of (OBO) is the correct flow when a middle-tier web API receives a token from a client and must call another downstream API using the signed-in user's identity — it propagates the user context through the call chain. Client credentials is for daemon apps or background services where no user is involved. Authorization code + PKCE is the secure flow for browser-based or native apps.

## DefaultAzureCredential Resolution Chain

`DefaultAzureCredential` (azure-identity) attempts credentials in the following order, stopping at the first that succeeds:

1. `EnvironmentCredential` — reads `AZURE_CLIENT_ID`, `AZURE_CLIENT_SECRET` / `AZURE_CLIENT_CERTIFICATE_PATH`, `AZURE_TENANT_ID`
2. `WorkloadIdentityCredential` — federated identity in Kubernetes (AKS workload identity)
3. `ManagedIdentityCredential` — Azure-hosted compute (App Service, Functions, VMs, ACI, AKS pod identity)
4. `VisualStudioCredential` — signed-in identity in Visual Studio (Windows)
5. `AzureCliCredential` — `az login` credential on the local machine
6. `AzurePowerShellCredential` — `Connect-AzAccount` credential
7. `InteractiveBrowserCredential` — browser-based interactive login (disabled by default in `DefaultAzureCredential`)

> **Exam tip:** `DefaultAzureCredential` lets the same application code run locally (resolves to Azure CLI credentials via `az login`) and in production on Azure (resolves to the managed identity assigned to the hosting resource) without any environment-specific branching or secret management. This is the recommended pattern for all Azure SDK clients.

## App Registration: Scopes vs Application Roles

| Service | Type | Best For | Key Feature |
| --- | --- | --- | --- |
| Delegated Scopes (OAuth2 Permissions) | Permission Type | APIs called on behalf of a signed-in user | Require user consent or admin pre-consent; user identity is present in the token |
| Application Roles (App Permissions) | Permission Type | Daemon apps and service-to-service calls with no user context | Granted to the app's own identity; used with the client credentials flow; require admin consent |

> **Exam tip:** Delegated scopes (OAuth2 permissions) require a signed-in user — the token contains both the user and the app identity. Application roles (app permissions) are assigned to the application's own service principal and are used in the client credentials flow where no user is present. If the scenario describes a background job, scheduler, or daemon calling an API, the answer is application roles + client credentials.

## Hybrid Identity

| Service | Purpose | Protocol | Use Case | Key Feature |
| --- | --- | --- | --- | --- |
| **Entra Connect** | Sync on-prem AD identities to Entra ID | LDAP → OAuth/OIDC | Hybrid orgs needing SSO across on-prem and cloud | Password hash sync, pass-through auth, federation |
| **Entra Domain Services** | Managed domain services in Azure (no DCs to run) | LDAP / Kerberos / NTLM | Lift-and-shift apps requiring legacy auth in Azure | Fully managed, integrates with Entra ID tenant |
| **Entra ID-only** | Cloud-native identity with no on-prem dependency | OAuth 2.0 / OIDC / SAML | Greenfield cloud workloads | No infrastructure to manage |

> **Exam tip:** Choose Entra Domain Services when a lift-and-shift workload requires LDAP or
> Kerberos authentication in Azure and you do not want to deploy and manage domain controllers.
> Choose Entra Connect when the requirement is to sync existing on-premises Active Directory
> accounts to the cloud for SSO or hybrid authentication.

## RBAC

| Concept | Description |
| --- | --- |
| **Role Definition** | Set of allowed actions (e.g. Contributor) |
| **Role Assignment** | Assign role to principal at a scope |
| **Scope levels** | Management Group > Subscription > Resource Group > Resource |
| **Built-in roles** | Owner, Contributor, Reader, User Access Administrator |
| **Custom Roles** | Define your own action list |
| **Deny Assignments** | Block actions regardless of role (used by Blueprints) |

> **⚠️ Deprecation warning:** Vault Access Policies (Key Vault) and legacy Storage access
> policies are superseded by **Azure RBAC**. RBAC is Entra-native, auditable, and centrally
> managed. Migrate new and existing resources to RBAC.

## PIM Key Concepts

| Feature | Detail |
| --- | --- |
| **Eligible Assignment** | Role not active until user activates |
| **Active Assignment** | Role always active |
| **Activation** | User requests role, optionally requires MFA + justification |
| **Approval Workflow** | Require approver before activation |
| **Access Reviews** | Periodic certify that users still need roles |

> **Exam tip (AZ-500):** AZ-500 tests PIM activation depth — know the difference
> between eligible (requires activation) and active (always on) role assignments.
> Access Reviews are the recurring compliance mechanism; PIM is the just-in-time
> access mechanism. Conditional Access is the Zero Trust policy enforcement point
> — combine it with Identity Protection risk signals to auto-block risky sign-ins.

## Entra ID Join Types

| Service | Type | Best For | Key Feature |
| --- | --- | --- | --- |
| **Entra ID Join (AAD Join)** | Cloud-only join | New cloud-only devices | No on-prem dependency; MDM enrolled |
| **Hybrid Entra ID Join** | Hybrid join | Existing domain-joined devices | Joined to both on-prem AD and Entra ID |
| **Entra ID Registered** | Personal device | BYOD | Minimal IT control; user account registered |

> **Exam tip:** Hybrid Entra ID Join requires line-of-sight to a domain controller or Azure AD Connect for initial join. It is used for existing corporate devices that need both on-prem GPO and cloud SSO.

### Entra ID Join Type Decision Flow

```mermaid
--8<-- "azure/diagrams/identity/entra-id-join-type-decision-flow.mmd"
```

## RBAC Built-in Roles

| Service | Layer | Scope | Use Case | Key Feature |
| --- | --- | --- | --- | --- |
| **Owner** | Full control | Any | Full resource management including access | Can assign roles; includes all Contributor perms |
| **Contributor** | Resource management | Any | Create and manage resources | Cannot assign roles or manage access |
| **Reader** | Read-only | Any | View resources, audit, monitoring | No create/update/delete; no role assignments |
| **User Access Administrator** | Access management | Any | Manage role assignments only | Cannot modify resources; only access control |

> **Exam tip:** User Access Administrator can grant Owner to others — this is a powerful role. Use it carefully and prefer just-in-time elevation via PIM over permanent assignment.

### RBAC Role Assignment Decision Flow

```mermaid
--8<-- "azure/diagrams/identity/rbac-role-assignment-decision-flow.mmd"
```

## Microsoft Entra Enterprise Applications

> **⚠️ Deprecation warning:** The name "Azure AD Enterprise Applications" is retired (October 2023).
> This feature is now **Microsoft Entra Enterprise Applications** under Microsoft Entra ID.
> Portal functionality and APIs are unchanged — only the branding has moved.
> See: [Microsoft Entra ID rename announcement](https://www.microsoft.com/en-us/security/business/identity-access/microsoft-entra-id)

| Concept | Description |
| --- | --- |
| **Enterprise Application** | Tenant-specific service principal created when an app is registered or consented to |
| **Gallery App** | Pre-integrated SaaS apps (Salesforce, ServiceNow, Workday) with SAML/OIDC templates |
| **Non-gallery App** | Custom or unlisted apps — add manually and configure the SSO protocol |
| **SSO Modes** | SAML 2.0, OpenID Connect, Password-based (form-fill), Linked (redirect only) |
| **User / Group Assignment** | Controls who can access the app; enforced when "Assignment required" is enabled |
| **Provisioning (SCIM)** | Automatic user and group sync from Entra ID to the SaaS app over SCIM 2.0 |
| **Conditional Access** | Access policies (MFA, compliant device, location) scoped to a specific application |

> **Exam tip:** Enterprise Applications manages the tenant-level service principal for an app;
> App Registration defines the app identity and API surface. For a multi-tenant app the
> App Registration lives in the home tenant, while an Enterprise Application (service principal)
> is created in every tenant that consents to the app.

## Microsoft Entra Application Proxy

> **⚠️ Deprecation warning:** The name "Azure AD Application Proxy" is retired (October 2023).
> This feature is now **Microsoft Entra application proxy** under Microsoft Entra ID.
> The service itself remains fully supported, but for new hybrid remote-access designs
> Microsoft recommends evaluating **Microsoft Entra Private Access** (zero-trust network access)
> as the strategic successor.
> See: [Microsoft Entra ID rename announcement](https://www.microsoft.com/en-us/security/business/identity-access/microsoft-entra-id)

| Component | Layer | Scope | Use Case | Key Feature |
| --- | --- | --- | --- | --- |
| **Application Proxy Connector** | On-premises agent | On-premises | Outbound HTTPS tunnel to Entra ID cloud service | No inbound firewall ports required; connectors grouped for HA |
| **Application Proxy Service** | Cloud relay | Global | Routes external requests to the on-prem connector | Entra ID pre-authentication before traffic reaches the internal app |
| **Pre-authentication** | Security | Per-app | Enforce Entra ID sign-in before granting app access | Supports Conditional Access, MFA, and token-based auth |
| **Microsoft Entra Private Access** | ZTNA | Global | Zero-trust per-resource access; strategic successor to App Proxy | Per-app segmentation; no full network tunnel; part of Global Secure Access |

> **Exam tip:** Application Proxy requires only an outbound TCP 443 connection from the on-premises
> connector to Azure — no inbound firewall rules are needed on the corporate network.
> Pre-authentication means only Entra ID-authenticated users (with optional MFA via Conditional
> Access) can reach the internal application. Deploy multiple connectors in a connector group
> for high availability.

## Microsoft Entra ID License Comparison

Entra ID is available in four editions. Each edition is a strict superset of the one below it
(except Governance, which is an add-on). Features not listed here are available across all tiers.

### Feature Matrix

| Feature | Free | P1 | P2 | Governance |
| --- | :---: | :---: | :---: | :---: |
| **Core directory (users, groups, devices)** | ✓ | ✓ | ✓ | ✓ |
| **Basic MFA (per-user MFA, Security Defaults)** | ✓ | ✓ | ✓ | ✓ |
| **B2B guest collaboration** | ✓ | ✓ | ✓ | ✓ |
| **Application SSO — limited (10 apps / user)** | ✓ | — | — | — |
| **Application SSO — unlimited** | — | ✓ | ✓ | ✓ |
| **Self-Service Password Reset — cloud only** | ✓ | ✓ | ✓ | ✓ |
| **Self-Service Password Reset — on-prem writeback** | — | ✓ | ✓ | ✓ |
| **Conditional Access policies** | — | ✓ | ✓ | ✓ |
| **Dynamic groups (attribute-based membership)** | — | ✓ | ✓ | ✓ |
| **Microsoft Entra Application Proxy** | — | ✓ | ✓ | ✓ |
| **Group-based application assignment** | — | ✓ | ✓ | ✓ |
| **SharePoint Limited Access** | — | ✓ | ✓ | ✓ |
| **SLA 99.99%** | — | ✓ | ✓ | ✓ |
| **Identity Protection (risk-based sign-in / user risk)** | — | — | ✓ | ✓ |
| **Risk-based Conditional Access** | — | — | ✓ | ✓ |
| **Privileged Identity Management (PIM)** | — | — | ✓ | ✓ |
| **Access Reviews (basic)** | — | — | ✓ | ✓ |
| **Entitlement Management (access packages)** | — | — | — | ✓ |
| **Lifecycle Workflows (joiner / mover / leaver)** | — | — | — | ✓ |
| **PIM for Groups** | — | — | — | ✓ |
| **Advanced Access Reviews (machine-assisted)** | — | — | — | ✓ |
| **My Access portal for request approvals** | — | — | — | ✓ |

> Note: Governance is a paid add-on that requires an existing P1 or P2 licence per user.
> It is not a standalone tier.

### Tier Descriptions

#### Free

Included with any Azure subscription or Microsoft 365 licence. Covers core cloud identity:
user accounts, group management, device registration, basic MFA via Security Defaults,
B2B guest access, and SSO to up to 10 apps per user (gallery apps). No Conditional Access,
no risk-based features, no dynamic groups. SSPR is cloud-only — no writeback to on-premises AD.

#### P1 (Entra ID Plan 1)

Included with Microsoft 365 E3, EMS E3, and Microsoft 365 Business Premium.
Adds the full Conditional Access engine (location, device compliance, app, sign-in risk with
Named Locations), unlimited SSO, SSPR with on-prem password writeback, dynamic groups,
Application Proxy for on-prem app publishing, and group-based application assignment.
P1 is sufficient for most production Zero Trust designs that do not require PIM or risk signals.

#### P2 (Entra ID Plan 2)

Included with Microsoft 365 E5, EMS E5, and Microsoft 365 E5 Security.
Superset of P1. Adds Entra ID Identity Protection (real-time risk scoring of sign-ins and
users), risk-based Conditional Access policies (block or require MFA when risk is Medium/High),
Privileged Identity Management (just-in-time role activation, approval workflows, activation
alerts), and basic Access Reviews (periodic certification of role and group membership).

#### Entra ID Governance (add-on)

Requires P1 or P2 per user as a prerequisite — not a standalone tier.
Adds identity lifecycle automation: Entitlement Management (access packages with approval
workflows and expiry), Lifecycle Workflows (automated tasks on join/move/leave events such as
provisioning accounts or revoking access), PIM for Groups (just-in-time group membership),
advanced machine-assisted Access Reviews (AI reviewer recommendations), and the My Access
portal for end-user entitlement requests.

### License Selection Decision Flow

```mermaid
--8<-- "azure/diagrams/identity/entra-license-selection-decision-flow.mmd"
```

> **Exam tip — PIM requires P2:**
> Privileged Identity Management is a P2-only feature. Any scenario that mentions
> just-in-time role activation, activation approval workflows, PIM alerts, or eligible
> vs active role assignments requires P2 (or Governance). P1 Conditional Access cannot
> substitute for PIM — CA enforces sign-in policy; PIM controls role elevation.

> **Exam tip — Identity Protection requires P2:**
> Risk-based Conditional Access (sign-in risk policy, user risk policy) requires
> Identity Protection, which is P2-only. P1 Conditional Access policies can enforce
> MFA by location or device, but they cannot consume Identity Protection risk signals
> (Low / Medium / High). If the scenario mentions blocking risky sign-ins automatically
> or requiring MFA when sign-in risk is Medium, the answer is P2 + Identity Protection.

> **Exam tip — SSPR writeback requires P1:**
> Self-Service Password Reset is available in the Free tier for cloud-only accounts.
> But if users must be able to reset passwords that sync back to on-premises Active
> Directory, password writeback (via Entra Connect) is required — and that requires P1.

> **Exam tip — Governance vs P2:**
> Access Reviews exist in both P2 (basic) and Governance (advanced with AI recommendations).
> Entitlement Management (access packages) and Lifecycle Workflows are Governance-only.
> If the scenario involves automating the joiner/mover/leaver process or building a
> self-service access request catalogue, the answer is Entra ID Governance, not P2.
