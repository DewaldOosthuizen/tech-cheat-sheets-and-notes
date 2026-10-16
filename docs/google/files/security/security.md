# SECURITY

## Core Security Services

| Service | Type | Best For | Key Feature |
| --- | --- | --- | --- |
| **Security Command Center (SCC)** | Security posture & threat detection | Asset discovery, vulnerability scanning, threat detection | Standard tier (free asset discovery, basic findings); Premium tier (Event Threat Detection, Threat Intelligence, SCC Insights) |
| **Cloud KMS** | Key management | Encryption key lifecycle, CMEK for GCP services | Symmetric, asymmetric (RSA, EC), HMAC keys; key rotation; HSM-backed (Cloud HSM) |
| **Secret Manager** | Secret storage | API keys, passwords, certificates, credentials | Versioning, IAM-controlled access, audit logging, OTP generation |
| **Binary Authorization** | Container sign & verify | Enforce signed images before deployment | Signer attestations; policy per cluster; blocks unsigned or untrusted images |
| **VPC Service Controls** | Data exfiltration perimeter | Restrict data access to a defined network perimeter | Private Google Access within perimeter; avoid public internet for data egress; supported services list |
| **Cloud Armor** | WAF & DDoS protection | L7 security at the edge (HTTP/S LB) | WAF rules (OWASP CRS), IP allow/block lists, DDoS protection, adaptive protection |
| **Cloud HSM** | Hardware security module | FIPS 140-2 Level 3 key storage | Dedicated HSM partition; integration with Cloud KMS |
|| **Cloud IAM** | Access control | Identity-based permissions | Covered in [Identity & Access](../identity/identity.md) |

> **Exam tip:** Security Command Center is the central security and risk management platform — Standard tier covers asset discovery and basic vulnerability findings. Premium tier adds Event Threat Detection (suspicious activity in logs), Threat Intelligence (known-bad indicators), and SCC Insights (identity and data risk analysis). Cloud Armor attaches to the HTTP(S) Load Balancer for WAF and IP-based protection at the edge. VPC Service Controls create a security perimeter around projects — data cannot leave the perimeter via supported services over the public internet.

## Security Command Center Tiers

| Tier | Covers | Key Feature |
| --- | --- | --- |
| **Standard** | Asset discovery, basic security findings, fundamential vulnerability scanning | Always on; no cost for the core tier (there may be charges for optional services) |
| **Premium** | All Standard features + Event Threat Detection, Threat Intelligence, SCC Insights | Advanced threat detection using built-in analytics on log data; threat intel feeds |

> **Exam tip:** Choose SCC Standard for continuous asset inventory and basic vulnerability/discovery findings. Choose SCC Premium when the requirement mentions threat detection from log-based analytics, threat intelligence feeds, or identity and data risk analysis.

## Encryption Options

| Mechanism | Scope | Key Owned By |
| --- | --- | --- |
| **Google-managed encryption (GMEK)** | Default for all GCP services | Google — lowest overhead |
| **Customer-managed encryption keys (CMEK)** | Storage, SQL, BigQuery, etc. | Customer in Cloud KMS — auditable, rotatable |
| **Customer-supplied encryption keys (CSEK)** | Cloud Storage only | Customer provides key per request — not persisted by Google |
| **Cloud HSM** | FIPS 140-2 Level 3 HSMs | Customer controls the HSM partition |

> **Exam tip:** CMEK is the most common compliance answer — you retain control of the key in Cloud KMS, with full audit logging and automatic rotation. CSEK is rarely chosen because Google does not store the key — every request must supply the key, which adds operational burden. Cloud HSM satisfies requirements that mandate a FIPS 140-2 Level 3 hardware boundary for key material.

## Binary Authorization

| Policy | Behaviour |
| --- | --- |
| **Require signature by attested signer** | Container image must be signed by a designated signer before deployment to a cluster |
| **Attestors** | Verify that an image was signed by a trusted authority (e.g. CI/CD pipeline) |
| **Cluster-level enforcement** | Policy is applied per GKE cluster; unsigned images are blocked at deploy time |

> **Exam tip:** Binary Authorization is the answer when the requirement mentions supply-chain security for containers — ensuring only images built and signed by an approved pipeline can be deployed. It protects against unauthorised or tampered images reaching production GKE clusters.

## VPC Service Controls

| Feature | Detail |
| --- | --- |
| **Security perimeter** | Groups projects and services into a boundary; data cannot leave via supported services over the public internet |
| **Private Google Access** | Within the perimeter, instances without external IPs can reach Google APIs privately |
| **Supported services** | Cloud Storage, BigQuery, Bigtable, Cloud SQL, Pub/Sub, and others (growing list) |
| **Access levels** | Can restrict access to resources within the perimeter based on context (IP, device attributes) |

> **Exam tip:** VPC Service Controls are the answer when the requirement mentions preventing data exfiltration over the public internet for sensitive data workloads. VPC-SC does not replace firewall rules or IAM — it operates at the service perimeter layer, blocking data egress paths that IAM alone cannot control.
