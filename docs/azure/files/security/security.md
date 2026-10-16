# Security

## Microsoft Defender for Cloud

| Plan | Covers | Key Feature |
| --- | --- | --- |
| **Defender for Servers** | VMs, Arc servers | Vulnerability assessment, JIT VM access |
| **Defender for Storage** | Blob, Files, ADLS | Malware scanning, anomaly detection |
| **Defender for SQL** | Azure SQL, SQL Server | SQL injection detection, anomalous access |
| **Defender for Containers** | AKS, ACR, Arc K8s | Image scanning, runtime threat detection |
| **Defender for App Service** | Web apps | Threat detection, malicious domain alerts |
| **Defender for Key Vault** | Key Vault | Suspicious access pattern alerts |
| **Defender for DNS** | DNS layer | Detect C2 communication |
| **Defender CSPM** | Cloud posture | Attack path analysis, governance |

> **⚠️ Deprecation warning:** "Security Center" and "Azure Defender" are legacy names.
> The current product is **Microsoft Defender for Cloud**. Older exam questions may still
> use the former names.

> **Exam tip (AZ-500):** JIT VM Access (under Defender for Servers) locks down management
> ports and opens them only on approved request; choose it when the requirement mentions
> reducing the attack surface on VM management ports.

## Azure Key Vault

| Feature | Detail |
| --- | --- |
| **Secrets** | Connection strings, passwords, API keys |
| **Keys** | Encryption keys (RSA, EC) — HSM-backed option |
| **Certificates** | Manage TLS/SSL lifecycle |
| **Soft Delete** | Retain deleted objects for 7–90 days |
| **Purge Protection** | Prevent permanent deletion during retention |
| **RBAC vs Access Policies** | RBAC preferred (granular, Azure AD-native) |
| **Private Endpoint** | Restrict Key Vault to VNet-only access |

> Exam tip: Always use **Managed Identity** to access Key Vault — never store credentials in app config.

## Key Vault Access Models

| Service | Access Model | Audit | Granularity | Key Feature |
| --- | --- | --- | --- | --- |
| **Key Vault** | Vault Access Policies (legacy) | Per-vault log; no per-operation identity trail | Coarse — get/list/set apply to all secrets | Simple setup; max 1024 policies per vault |
| **Key Vault** | Azure RBAC | Full Azure Activity Log + Entra audit trail | Fine-grained — role assignment per secret/key/cert | Entra-native; supports PIM, Conditional Access |

> **⚠️ Deprecation warning:** Vault Access Policies are the legacy authorization model for
> Key Vault. Microsoft recommends migrating to **Azure RBAC** for new and existing vaults.
> RBAC provides Entra-native granularity, PIM support, and a unified audit trail.

> **Exam tip:** Choose Azure RBAC for Key Vault when the requirement mentions
> Entra integration, Privileged Identity Management (PIM), per-resource
> granularity, or migration away from legacy Access Policies.

```mermaid
--8<-- "azure/diagrams/security/key-vault-access-decision-flow.mmd"
```

Use **Managed Identity** bound to an Azure RBAC role (e.g. Key Vault Secrets User)
as the credential-free pattern — no secrets stored in application configuration.

> **Exam tip:** Access Key Vault from code using `DefaultAzureCredential` (azure-identity) with `SecretClient` (azure-keyvault-secrets). No credentials are stored in application configuration — `DefaultAzureCredential` resolves through: environment variables → workload identity → managed identity → Visual Studio → Azure CLI → Azure PowerShell → interactive browser. In production the managed identity is used automatically; locally the Azure CLI credential is used — the same code runs in both environments without modification.

> **Exam tip:** Certificate auto-rotation: Key Vault monitors certificate expiry and triggers renewal via the configured CA issuer (DigiCert or GlobalSign) or a self-signed renewal policy. The application retrieves the updated certificate on the next polling interval or receives a near-expiry notification via Event Grid (`Microsoft.KeyVault.CertificateNearExpiry`). The app does not need to be redeployed — it re-reads the certificate from Key Vault on the next request or on the Event Grid event.

## App Configuration

| Service | Type | Best For | Key Feature |
| --- | --- | --- | --- |
| App Configuration Feature Flags | Feature | Runtime feature toggling without redeployment | Boolean flags with audience-targeting filters; integrated with .NET, Java, Python SDKs |
| App Configuration Key Vault References | Configuration | Centralised secret consumption without copying secret values | Stores only the Key Vault secret URI; actual value fetched from Key Vault at runtime |
| App Configuration Label-based Config | Configuration | Environment-specific configuration (dev, staging, prod) in one store | Labels act as a filter on key-value pairs; the app selects the label at startup |

> **Exam tip:** App Configuration Key Vault references never copy or cache the secret value inside App Configuration — only the Key Vault URI is stored. When the secret rotates in Key Vault, the updated value is returned on the next runtime fetch without any change to App Configuration. This is the recommended pattern for secret rotation transparency.

## Encryption

| Type | Description | Service |
| --- | --- | --- |
| **Encryption at rest** | Data encrypted on disk | Default in Azure Storage, SQL, etc. |
| **CMK (Customer-Managed Keys)** | You control key in Key Vault | Stricter compliance, storage + SQL |
| **PMK (Platform-Managed Keys)** | Microsoft manages key | Default, lower admin overhead |
| **Double Encryption** | Two layers of encryption | Azure Storage, Disks |
| **Encryption in transit** | TLS enforced | All Azure services |
| **Azure Disk Encryption** | BitLocker (Windows) / dm-crypt (Linux) | VM OS and data disks |
| **SSE (Server-Side Encryption)** | Storage service encrypts before writing | Azure Blob, Files, Queues |

## Azure SQL Encryption

Three distinct mechanisms control how Azure SQL protects data. They operate at
different layers, have different key ownership models, and are not interchangeable.

| Mechanism | Protection Layer | DB Engine Sees Plaintext | Keys Owned By | Use Case | Key Feature |
| --- | --- | --- | --- | --- | --- |
| **Transparent Data Encryption (TDE)** | Data files at rest (disk) | Yes — plaintext in memory | Microsoft (PMK default) or customer (CMK via Key Vault) | Compliance baseline; protects against physical media or backup file theft | Enabled by default on Azure SQL and SQL MI; zero application change required |
| **Always Encrypted** | Column-level; client driver | No — ciphertext only | Client application (Column Master Key never leaves client) | Highly sensitive columns (PII, PAN, PHI) where DBAs and cloud operators must not see data | Encryption and decryption happen inside the client driver; SQL engine only stores and returns ciphertext |
| **Dynamic Data Masking (DDM)** | Query result display layer | Yes — data stored unmasked | N/A (not encryption) | Limit sensitive data exposure for non-privileged users without schema changes | Masking rules defined per column; privileged users with `UNMASK` permission bypass masking automatically |

### How Each One Works

#### Transparent Data Encryption (TDE)

Encrypts the entire database, its backups, and transaction log files at rest
using AES-256. The encryption and decryption are handled by the SQL engine
transparently — no application change is needed. By default Azure manages the
key (PMK). For compliance scenarios requiring key ownership, you can bring your
own key (BYOK/CMK) stored in Azure Key Vault.

- Protects against: stolen backup files, physical disk removal, storage media disposal.
- Does NOT protect against: a compromised DBA, an SQL injection attack, or any
  threat that queries data through the engine (data is decrypted in memory for normal queries).

#### Always Encrypted

Encrypts specific columns before data leaves the client application. The SQL
engine stores and returns only ciphertext and never has access to the plaintext
or the encryption keys. Key material (Column Master Key) is held in a trusted
store such as Azure Key Vault or the Windows Certificate Store. The client
driver (e.g. ADO.NET, JDBC) handles encryption/decryption transparently.

Two encryption types within Always Encrypted:

| Type | Supports Equality Queries | Use Case |
| --- | --- | --- |
| **Deterministic** | Yes (same plaintext → same ciphertext) | Columns used in WHERE, JOIN, GROUP BY |
| **Randomized** | No (same plaintext → different ciphertext each time) | Maximum confidentiality; columns not used in filtering |

- Protects against: compromised DBAs, SQL injection returning column data, cloud
  operator access.
- Limitation: randomized columns cannot be used in WHERE clauses or indexes.
  Computations (e.g. range queries, sorting) on encrypted columns require
  Always Encrypted with secure enclaves (SQL Server 2019+ / Azure SQL with enclaves).

#### Dynamic Data Masking (DDM)

Applies obfuscation rules to column values at query time. The underlying data
is stored and processed unmasked. Users with elevated permissions (sysadmin,
db_owner, or the `UNMASK` permission) always see full data.

Built-in masking functions:

| Function | Example Output | Typical Column |
| --- | --- | --- |
| `default()` | `XXXX` or `0` | Any sensitive field |
| `email()` | `aXXX@XXXX.com` | Email addresses |
| `partial(n, padding, m)` | `XnXXXXm` | Phone, ID numbers |
| `random(low, high)` | Random integer in range | Numeric columns |

- Protects against: accidental over-exposure of sensitive data to support staff
  or low-privilege application roles.
- Does NOT protect against: any user who holds `UNMASK`, a DBA, or an attacker
  who has obtained a privileged connection.

> **Exam tip:** TDE, Always Encrypted, and DDM are complementary, not competing.
> A production Azure SQL deployment commonly uses all three simultaneously:
> TDE for at-rest file protection (always on by default), Always Encrypted for
> the most sensitive PII columns where even DBAs must not see the data, and DDM
> to restrict what support or reporting roles see in query results.
> When an exam scenario says "the DBA must not be able to read the data" or
> "data must be encrypted before reaching the server", the answer is Always Encrypted.
> When it says "encrypt backups and data files at rest", the answer is TDE.
> When it says "hide part of a credit card number from support staff", the answer is DDM.

## Policy & Compliance

| Concept | Description |
| --- | --- |
| **Azure Policy** | Enforce, audit, or remediate resource configurations |
| **Policy Initiative** | Group of policies (e.g., CIS benchmark) |
| **Deny Effect** | Block non-compliant resource creation |
| **Audit Effect** | Flag non-compliance without blocking |
| **DeployIfNotExists** | Auto-remediate — deploy missing configs |
| **Modify Effect** | Auto-add tags or properties |
| **Compliance Dashboard** | See % compliance across subscriptions |
| **Regulatory Compliance** | Pre-built initiatives: NIST, ISO 27001, PCI-DSS |

> Exam tip: **DeployIfNotExists** requires a managed identity for the policy assignment to execute remediation.

## Authentication & Password Security

| Feature | Description | Use Case |
| --- | --- | --- |
| **MFA** | Multi-factor authentication | All users, especially admins |
| **Passwordless** | FIDO2 key, Microsoft Authenticator, Windows Hello | Zero-password auth |
| **Conditional Access** | Policy-based access decisions | Enforce MFA by location/risk/device |
| **Identity Protection** | Risk-based sign-in/user risk policies | Auto-block risky sign-ins |
| **SSPR (Self-Service Password Reset)** | Users reset their own passwords | Reduce helpdesk load |
| **Password Protection** | Block weak/known-bad passwords | On-prem AD + Azure AD |
| **PIM (Privileged Identity Management)** | Just-in-time privileged access | Admin roles activated on demand |
| **Access Reviews** | Periodic review of group/role membership | Compliance, least-privilege enforcement |

## Microsoft Sentinel

| Component | Purpose |
| --- | --- |
| **Data Connectors** | Ingest logs from Azure, M365, 3rd party |
| **Analytics Rules** | Detect threats from log patterns |
| **Playbooks (Logic Apps)** | Auto-respond to incidents |
| **Workbooks** | Visualize security data |
| **UEBA** | User and entity behavior analytics |
| **Threat Intelligence** | Feed-based IOC matching |

> Sentinel = SIEM + SOAR. Defender for Cloud = CSPM + workload protection. They integrate but serve different roles.

> **Exam tip (AZ-500):** Sentinel is a cloud-native SIEM + SOAR; Defender for
> Cloud is CSPM + workload protection. AZ-500 questions that mention "incident
> response automation" or "playbook" point to Sentinel. Questions that mention
> "secure score" or "recommendations" point to Defender for Cloud.

## Defender for Cloud

| Service | Layer | Scope | Use Case | Key Feature |
| --- | --- | --- | --- | --- |
| **Defender CSPM (Free)** | Posture | Subscription | Secure Score, recommendations | Always on; no cost |
| **Defender CSPM (Paid)** | Posture | Subscription | Advanced posture, attack paths | Governance rules, regulatory compliance |
| **Defender for Servers** | Workload | VM/Arc | Threat detection on VMs | MDE integration, vulnerability assessment |
| **Defender for Storage** | Workload | Storage Account | Malware scanning, anomaly detection | Per-storage-account enablement |

> **Exam tip:** Enabling Defender for Cloud at the subscription level automatically covers all existing and future resources. Use the "Enhanced Security" toggle per workload plan to control cost.

### Defender for Cloud Coverage

```mermaid
--8<-- "azure/diagrams/security/defender-for-cloud-coverage.mmd"
```
