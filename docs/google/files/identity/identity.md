# IDENTITY & ACCESS

## Core Identity Services

| Service | Type | Best For | Key Feature |
| --- | --- | --- | --- |
| **Cloud IAM** | Access control | Fine-grained permissions across GCP resources | Predefined and custom roles, IAM Conditions, deny policies |
| **Cloud Identity** | User and device management | Workforce identity, device policy enforcement | Directory sync, SSO, endpoint management, no Google Workspace licence required |
| **Service Account** | Workload identity | Application and service-to-service authentication | JSON key (legacy) or workload identity federation; no human credential |
| **Workload Identity** | GKE workload auth | Map Kubernetes service accounts to IAM service accounts | No node-level service account key; pod-level identity; least-privilege per deployment |
| **Identity-Aware Proxy (IAP)** | Zero-trust access | Secure access to internal apps without VPN | Context-aware access, Beyond Corp model, no network perimeter |

> **Exam tip:** Choose Cloud IAM for any access control requirement — it is the central authorisation plane for all GCP resources. Prefer predefined roles over custom roles unless the requirement explicitly needs a tailored permission set. Service accounts are the correct identity for workloads; never use personal user credentials for application auth. Workload Identity is the preferred pattern for GKE workloads — it eliminates service account key management on nodes.

## Cloud IAM Roles

| Role Type | Description | Example |
| --- | --- | --- |
| **Primitive roles** | Broad, legacy roles at project level | Viewer, Editor, Owner |
| **Predefined roles** | Service-specific, granular permissions | Compute Admin, Storage Object Viewer |
| **Custom roles** | Tailored permission set (if predefined is insufficient) | Subset of permissions for a specific job function |
| **Deny policies** | Explicitly deny actions regardless of allow roles | Block region, block action type, block Public IP creation |

> **Exam tip:** Primitive roles (Viewer, Editor, Owner) grant overly broad permissions — use predefined or custom roles for production. IAM Conditions let you restrict role grants by attribute (e.g. request time window, IP range, resource tag). Deny policies are evaluated first — an explicit deny overrides any allow.

## Service Account vs Workload Identity

| Dimension | Service Account (key-based) | Workload Identity (GKE) |
| --- | --- | --- |
| **Credential type** | JSON key file (long-lived) | Underlying IAM SA mapped from K8s SA |
| **Key rotation** | Manual (key expiry) | Automatic — no key to rotate |
| **Granularity** | Node-level SA or per-pod key | Per-pod, per-deployment identity |
| **Security posture** | Keys can be leaked, over-privileged | No keys; pod identity tied to K8s SA |

> **Exam tip:** Workload Identity is the recommended authentication pattern for GKE workloads. Avoid long-lived service account keys — they are a security risk (hard to rotate, can be exfiltrated). Use Workload Identity or workload identity federation for workloads running outside GCP.

## Cloud Identity

| Use Case | Feature |
| --- | --- |
| **Workforce SSO** | Integrate with existing IdP via SAML or OIDC, or use Cloud Identity as the directory |
| **Device management** | Enforce screen lock, encryption, compliance policies on endpoints |
| **Directory sync** | Google Cloud Directory Sync (GCDS) syncs on-prem AD/LDAP to Cloud Identity |
| **No Workspace licence required** | Cloud Identity is a standalone identity and device management product — a Workspace licence is not required for workforce SSO and device policy |

> **Exam tip:** Cloud Identity is the answer when the requirement mentions workforce identity with device management but does not require Google Workspace collaboration features (Drive, Gmail, Calendar). Cloud Identity provides SSO, directory sync, and endpoint management without a Workspace subscription.

## Identity-Aware Proxy (IAP)

| Scenario | How IAP Helps |
| --- | --- |
| **Access internal web apps** | Users authenticate once via Google identity; no VPN required |
| **Access Compute Engine / GKE / Cloud Run** | TCP or HTTP(S) tunnel to private instances with identity-based policy |
| **Beyond Corp zero-trust** | Access decisions based on user identity and context, not network location |

> **Exam tip:** IAP satisfies requirements that mention accessing internal applications without exposing them to the public internet and without a VPN. IAP is the Google Cloud implementation of the Beyond Corp zero-trust access model — network location does not grant access; identity + context does.
