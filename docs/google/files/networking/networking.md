# NETWORKING

## Core Networking Services

| Service | Layer | Scope | Use Case | Key Feature |
| --- | --- | --- | --- | --- |
| **VPC** | L3 | Global (each VPC spans all regions) | Isolated virtual network, subnets per region | Global private network, firewall rules per VPC |
| **Cloud Load Balancing** | L4/L7 | Global (HTTP/S) or regional (TCP/UDP) | Distribute traffic across backends | Global anycast IP for HTTP(S), health-checked backends |
| **Cloud CDN** | L7 CDN | Global edge | Cache static/dynamic content close to users | Integrated with Cloud Load Balancing, cache modes |
| **Cloud DNS** | DNS | Global | Authoritative public or private DNS | Low-latency, managed, IAM-integrated |
| **Cloud NAT** | NAT | Regional | Outbound internet from private instances | Managed SNAT, no external IP on VM |
| **Cloud VPN** | IPSec VPN | Regional (gateways) | Secure tunnel to on-premises | Classic VPN (route-based), HA VPN (99.99% SLA) |
| **Cloud Interconnect** | Dedicated link | Global | Private, high-bandwidth on-prem connection | Dedicated Interconnect (colocation), Partner Interconnect |
| **Cloud Armor** | L7 security | Global (edge) | DDoS, WAF, IP allow/block lists | Security policy attached to HTTP(S) LB |
| **Private Service Connect** | Private access | Regional | Private access to Google APIs and services | No public internet egress for API traffic |

> **Exam tip:** Cloud Load Balancing provides a single anycast IP for HTTP(S) traffic globally — choose it when the requirement mentions global HTTP load balancing with a single IP. For TCP/UDP traffic, use the regional TCP/UDP LB. Cloud CDN reduces latency and origin load for cacheable content — attach it to the HTTP(S) LB backend. For hybrid connectivity, choose Cloud VPN (modest bandwidth, no colocation) or Cloud Interconnect (high bandwidth, SLA-backed, colocation required). Private Service Connect removes the need for public internet access to Google APIs — preferred for data-exfiltration-sensitive environments.

## Networking Decision Flow

```mermaid
--8<-- "google/diagrams/networking/networking-decision.mmd"
```

## VPC and Subnet Design

| Concept | Detail |
| --- | --- |
| **VPC scope** | Global — a single VPC spans all regions; subnets are regional |
| **Subnet mode** | Auto mode (one subnet per region, auto-created) or custom mode (full control) |
| **IP ranges** | Primary range + secondary alias IP ranges (used for GKE pods/services) |
| **Firewall rules** | Stateful, VPC-scoped; allow rules only (default deny ingress/egress) |
| **Shared VPC** | Host project owns VPC; service projects attach subnets for centralised networking |

> **Exam tip:** Custom mode VPC is preferred for production — it avoids surprise auto-created subnets in regions you do not use. Alias IP ranges let GKE assign pod IPs from a secondary range without NAT — critical for VPC-native clusters. Firewall rules are stateful: an allow rule for a return packet is not needed.

## Load Balancer Selection

| Scenario | LB Type | Scope | Protocol |
| --- | --- | --- | --- |
| **Global HTTP/S traffic** | Global HTTP(S) LB | Global frontend, regional backends | HTTP, HTTPS, HTTP/2, gRPC |
| **TCP/UDP — regional** | Regional TCP/UDP LB | Regional | TCP, UDP, SSL (proxy) |
| **Internal HTTP/S** | Internal HTTP(S) LB | Regional | HTTP, HTTPS (private VPC only) |
| **Internal TCP/UDP** | Internal TCP/UDP LB | Regional | TCP, UDP (private VPC only) |
| **SSL proxy** | SSL Proxy LB | Regional | SSL/TLS (non-HTTP) |

> **Exam tip:** Only the global HTTP(S) LB provides a single anycast IP across all regions. Internal load balancers are for east-west traffic inside a VPC — they are not reachable from the internet. Cloud CDN can only be enabled on a global HTTP(S) LB backend.

## VPC Connectivity Options

| Option | Use Case | Key Feature |
| --- | --- | --- |
| **Cloud VPN** | Encrypted on-prem tunnel over internet | Classic VPN (single tunnel) or HA VPN (two tunnels, 99.99% SLA) |
| **Cloud Interconnect (Dedicated)** | High-bandwidth, low-latency private link | Requires colocation at a Google peering point; SLA-backed |
| **Cloud Interconnect (Partner)** | Private connectivity via a network service provider | No colocation — provider handles the physical link |
| **Cloud NAT** | Outbound internet from private subnets | Managed, no external IP on instances, SNAT only |
| **VPC Network Peering** | VPC-to-VPC private connectivity | Non-transitive; peered VPCs cannot route through each other to a third VPC |
| **Private Service Connect** | Private access to Google APIs and managed services | No internet egress; IAM-controlled |

> **Exam tip:** HA VPN is required when the requirement mentions an SLA for VPN connectivity — classic VPN has no SLA. VPC Network Peering is non-transitive: if A peers with B and B peers with C, A cannot reach C through B. For hub-and-spoke at scale, use a Shared VPC host project or a network connectivity centre.

## Cloud DNS

| Type | Scope | Use Case |
| --- | --- | --- |
| **Public zone** | Internet-facing | Public-facing domain resolution |
| **Private zone** | VPC-scoped | Internal DNS for VPC resources; DNS peering across VPCs |
| **Forwarding zone** | VPC-scoped | Forward queries to on-premises DNS servers via VPN/Interconnect |

> **Exam tip:** Private DNS zones resolve names only from the associated VPC — they are not visible on the public internet. Use Cloud DNS peering to let one VPC resolve names from another VPC's private zone.

## Cloud NAT

| Scenario | Configuration |
| --- | --- |
| **Scale** | Cloud NAT auto-scales — no pre-provisioned capacity |
| **Egress only** | SNAT — no inbound connections are allowed through NAT |
| **Ports** | Ephemeral port allocation; configured per NAT IP |
| **Logging** | Flow logs available for egress audit |

> **Exam tip:** Cloud NAT lets instances without external IPs reach the internet (for updates, APIs) without a bastion. It does not allow inbound connections — use an external HTTP(S) LB or bastion for inbound access.
