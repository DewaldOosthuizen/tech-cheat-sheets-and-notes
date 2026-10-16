# ABBREVIATIONS

Centralised reference for every capitalised abbreviation used across the Azure
cheat-sheet sections (networking, security, storage, monitoring, compute,
identity, ha-dr, governance, messaging, waf).

| Abbreviation | Definition |
| --- | --- |
| AAD | Azure Active Directory — legacy name for Microsoft Entra ID |
| ACA | Azure Container Apps — serverless container hosting service |
| ACI | Azure Container Instances — on-demand single-container hosting without orchestration |
| ACL | Access Control List — rules that grant or deny traffic at the network or storage layer |
| ACR | Azure Container Registry — private Docker/OCI image registry |
| ADF | Azure Data Factory — managed ETL and data integration service |
| ADLS | Azure Data Lake Storage — hierarchical namespace storage built on Blob |
| AKS | Azure Kubernetes Service — managed Kubernetes cluster service |
| AM | Azure Migrate — central hub for discovery, assessment, and migration of on-premises workloads to Azure |
| AMA | Azure Monitor Agent — unified agent replacing MMA and WAD for telemetry collection |
| APIM | Azure API Management — managed API gateway with policies and developer portal |
| APM | Application Performance Monitoring — observability of application response times and errors |
| ARM | Azure Resource Manager — deployment and management layer for all Azure resources |
| ASE | App Service Environment — isolated, dedicated App Service plan in a VNet |
| ASG | Application Security Group — groups VMs for NSG rule simplification |
| ASMA | App Service Migration Assistant — tool for assessing and migrating IIS web apps to Azure App Service |
| ASR | Azure Site Recovery — disaster recovery replication and failover service |
| AZ | Availability Zone — physically separate datacenter within an Azure region |
| BGP | Border Gateway Protocol — dynamic routing protocol used in ExpressRoute and VPN Gateway |
| BYOD | Bring Your Own Device — policy allowing personal devices to access corporate resources |
| CA | Certificate Authority — trusted entity that issues TLS/SSL certificates |
| CDN | Content Delivery Network — globally distributed edge cache for static and dynamic content |
| CIAM | Customer Identity and Access Management — identity platform for external/consumer users |
| CIDR | Classless Inter-Domain Routing — IP address range notation used in VNet and subnet definitions |
| CMK | Customer-Managed Key — encryption key stored in Key Vault and controlled by the customer |
| CNCF | Cloud Native Computing Foundation — standards body for Kubernetes and cloud-native projects |
| CNI | Container Network Interface — plugin specification for container networking (used in AKS) |
| CPU | Central Processing Unit — primary compute processor |
| CSPM | Cloud Security Posture Management — continuous assessment of cloud resource configurations |
| DCR | Data Collection Rule — configuration object that controls log and metric routing in Azure Monitor |
| DLQ | Dead-Letter Queue — holding queue for undeliverable messages in Service Bus and Event Hubs |
| DMS | Azure Database Migration Service — managed service for online and offline database migration to Azure |
| DNS | Domain Name System — resolves hostnames to IP addresses; Azure provides Azure DNS and Private DNS |
| DR | Disaster Recovery — strategies and services to restore operations after a catastrophic failure |
| DTU | Database Transaction Unit — blended compute, memory, and I/O capacity unit for Azure SQL Basic/Standard/Premium tiers |
| ETL | Extract, Transform, Load — pipeline pattern for moving data between systems |
| FIFO | First In, First Out — message ordering guarantee supported by Service Bus queues |
| FPGA | Field-Programmable Gate Array — reconfigurable hardware accelerator available in some Azure VM SKUs |
| FQDN | Fully Qualified Domain Name — complete domain name including all labels (e.g. app.contoso.com) |
| GPO | Group Policy Object — Active Directory policy container applied to users and computers |
| GPU | Graphics Processing Unit — parallel compute accelerator used for AI, ML, and HPC workloads |
| GRS | Geo-Redundant Storage — replication to a secondary Azure region for disaster recovery |
| GZRS | Geo-Zone-Redundant Storage — replication across availability zones in the primary region and to a secondary region |
| HA | High Availability — design pattern that eliminates single points of failure for continuous operation |
| HDD | Hard Disk Drive — magnetic spinning disk; used for low-cost, infrequently accessed storage |
| HPA | Horizontal Pod Autoscaler — Kubernetes controller that scales pod replicas based on metrics |
| HPC | High Performance Computing — workloads requiring large-scale parallel processing |
| HSM | Hardware Security Module — dedicated cryptographic device for key generation and storage |
| IDPS | Intrusion Detection and Prevention System — monitors and blocks malicious network traffic |
| IKE | Internet Key Exchange — protocol used to establish IPSec VPN tunnels |
| IOPS | Input/Output Operations Per Second — storage throughput performance metric |
| JIT | Just-In-Time — access model that grants elevated permissions only when explicitly requested |
| JWT | JSON Web Token — compact, signed token format used in OAuth 2.0 and OIDC flows |
| KEDA | Kubernetes Event-Driven Autoscaling — open-source scaler for event-source-driven pod scaling |
| KQL | Kusto Query Language — query language used in Azure Monitor Logs and Microsoft Sentinel |
| LDAP | Lightweight Directory Access Protocol — protocol for querying and modifying directory services |
| LRS | Locally Redundant Storage — three synchronous copies within a single datacenter |
| MDE | Microsoft Defender for Endpoint — EDR solution integrated with Defender for Servers |
| MDM | Mobile Device Management — platform for managing and enforcing policy on devices |
| MFA | Multi-Factor Authentication — authentication requiring two or more verification factors |
| MI | Managed Identity — Azure-managed service principal that eliminates the need for credentials in code |
| ML | Machine Learning — AI workloads; Azure ML is the managed training and inference platform |
| MMA | Microsoft Monitoring Agent — legacy Log Analytics agent replaced by AMA |
| MPI | Message Passing Interface — parallel computing communication standard used in HPC clusters |
| MSAL | Microsoft Authentication Library — SDK for acquiring tokens from the Microsoft identity platform |
| MSP | Managed Service Provider — third-party company that manages Azure resources on behalf of customers |
| NAT | Network Address Translation — maps private IP addresses to a public IP for outbound internet access |
| NIC | Network Interface Card — virtual network adapter attached to a VM |
| NIST | National Institute of Standards and Technology — US standards body; NIST frameworks used in Azure Policy |
| NSG | Network Security Group — stateful L4 packet filter applied to subnets or NICs |
| NTLM | NT LAN Manager — legacy Windows challenge-response authentication protocol |
| NVA | Network Virtual Appliance — third-party firewall or router VM deployed in a VNet |
| OBO | On-Behalf-Of — OAuth 2.0 flow where a middle-tier API exchanges a token on behalf of a user |
| OIDC | OpenID Connect — identity layer on top of OAuth 2.0 for authentication |
| OLAP | Online Analytical Processing — query workload optimised for aggregation and reporting |
| OLTP | Online Transaction Processing — query workload optimised for high-frequency read/write operations |
| OMS | Operations Management Suite — legacy name for the suite now known as Azure Monitor and Log Analytics |
| PITR | Point-In-Time Restore — database recovery to a specific timestamp |
| PKCE | Proof Key for Code Exchange — OAuth 2.0 extension that prevents authorization code interception in public clients |
| PMK | Platform-Managed Key — encryption key generated and managed entirely by Microsoft |
| POSIX | Portable Operating System Interface — standard for file system semantics; required by ADLS Gen2 |
| RA | Read Access — prefix indicating read-access geo-redundancy (e.g. RA-GRS, RA-GZRS) |
| RBAC | Role-Based Access Control — authorization model granting permissions via role assignments |
| RDMA | Remote Direct Memory Access — low-latency network communication bypassing the CPU, used in HPC VMs |
| RDP | Remote Desktop Protocol — protocol for remote graphical desktop access to Windows VMs |
| RPO | Recovery Point Objective — maximum acceptable data loss window measured in time |
| RSA | Rivest–Shamir–Adleman — asymmetric encryption algorithm used in Key Vault RSA keys |
| RTO | Recovery Time Objective — maximum acceptable downtime window after a failure |
| RU | Request Unit — capacity unit in Azure Cosmos DB representing the cost of a database operation |
| SAML | Security Assertion Markup Language — XML-based federation protocol for SSO |
| SAS | Shared Access Signature — time-limited, scoped URL granting delegated access to Azure Storage |
| SIEM | Security Information and Event Management — platform for log aggregation, correlation, and alerting |
| SKU | Stock Keeping Unit — product tier or size identifier for Azure services |
| SLA | Service Level Agreement — Microsoft's uptime and connectivity commitments per service |
| SMB | Server Message Block — file-sharing protocol used by Azure Files |
| SMS | Storage Migration Service — Windows feature that inventories, transfers, and cuts over file server shares to Azure Files |
| SNAT | Source Network Address Translation — translates outbound private IP to a public IP |
| SOAR | Security Orchestration, Automation, and Response — automated incident response via playbooks |
| SPA | Single-Page Application — browser-based app using OAuth 2.0 Authorization Code + PKCE flow |
| SQL | Structured Query Language — query language used by relational databases |
| SSD | Solid-State Drive — flash storage; used for high-performance managed disks |
| SSE | Server-Side Encryption — storage service encrypts data before writing to disk |
| SSH | Secure Shell — encrypted protocol for remote command-line access to Linux VMs |
| SSO | Single Sign-On — authentication mechanism allowing one login to access multiple services |
| SSPR | Self-Service Password Reset — Entra ID feature allowing users to reset their own passwords |
| TLS | Transport Layer Security — cryptographic protocol enforcing encryption in transit |
| TTL | Time to Live — duration a DNS record or cache entry is valid |
| UDR | User-Defined Route — custom route table entry that overrides Azure default routing |
| UEBA | User and Entity Behavior Analytics — Sentinel feature detecting anomalous user/resource behaviour |
| URI | Uniform Resource Identifier — string identifying a resource; used in Key Vault references and OAuth scopes |
| VMSS | Virtual Machine Scale Set — automatically scales a group of identical VMs |
| VNet | Virtual Network — isolated, software-defined network in Azure |
| VPN | Virtual Private Network — encrypted tunnel connecting on-premises or remote networks to Azure |
| WAD | Windows Azure Diagnostics — legacy diagnostics agent replaced by AMA |
| WAF | Web Application Firewall — L7 filter protecting web apps from OWASP Top 10 attacks |
| WAN | Wide Area Network — large-scale network; Azure Virtual WAN is the managed hub-and-spoke topology |
| ZRS | Zone-Redundant Storage — three synchronous copies across three availability zones in one region |
