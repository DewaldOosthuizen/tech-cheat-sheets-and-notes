# NETWORKING

## Core Networking Services

| Service | Layer | Scope | Use Case | Key Feature |
| --- | --- | --- | --- | --- |
| **VPC** | L3 | Regional | Isolated virtual network | Custom CIDR, subnets, route tables |
| **Route 53** | DNS | Global | DNS resolution, health checks | Routing policies: latency, weighted, failover |
| **CloudFront** | L7 CDN | Global | Static/dynamic content delivery | Edge caching, WAF integration, HTTPS |
| **ALB** | L7 | Regional | HTTP/S load balancing | Path-based routing, WebSocket, Lambda targets |
| **NLB** | L4 | Regional | TCP/UDP load balancing | Ultra-low latency, static IP, TLS termination |
| **API Gateway** | L7 | Regional | REST / WebSocket / HTTP APIs | Auth, throttling, caching, Lambda proxy |

> **Exam tip:** Use ALB for HTTP/S path-based or host-based routing. Use NLB
> when you need a static IP, ultra-low latency, or non-HTTP protocols.
> CloudFront sits at the edge for global caching — it is not a load balancer.

## Networking Decision Flow

```mermaid
--8<-- "aws/diagrams/networking/decision-flow.mmd"
```

## VPC Connectivity Options

| Option | Use Case | Key Feature |
| --- | --- | --- |
| **Internet Gateway** | Public subnet internet access | Stateful, 1:1 to VPC |
| **NAT Gateway** | Private subnet outbound internet | Managed, no inbound |
| **VPC Peering** | Connect two VPCs | Non-transitive, same or cross-account |
| **Transit Gateway** | Hub-and-spoke multi-VPC | Transitive routing, route tables |
| **AWS Direct Connect** | Dedicated on-prem link | Consistent bandwidth, private connectivity |
| **VPN (Site-to-Site)** | Encrypted on-prem tunnel | IPSec over internet |

> **Exam tip:** VPC Peering is non-transitive — traffic cannot flow A → B → C
> unless A→C is also peered. For hub-and-spoke at scale, Transit Gateway is the
> correct answer.
