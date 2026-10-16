# ABBREVIATIONS

Centralised reference for every capitalised abbreviation used across the AWS
cheat-sheet sections (compute, networking, storage, identity, security,
database, monitoring, messaging, governance, ha-dr, waf).

| Abbreviation | Definition |
| --- | --- |
| ACL | Access Control List — rules controlling inbound and outbound traffic; used in VPC Network ACLs |
| ACM | AWS Certificate Manager — managed TLS/SSL certificate provisioning and renewal service |
| ALB | Application Load Balancer — L7 HTTP/HTTPS load balancer with content-based routing |
| AMI | Amazon Machine Image — pre-configured virtual machine template used to launch EC2 instances |
| ARN | Amazon Resource Name — unique identifier string for every AWS resource |
| AZ | Availability Zone — physically isolated datacenter within an AWS Region |
| CDN | Content Delivery Network — globally distributed edge cache; delivered by Amazon CloudFront |
| CIDR | Classless Inter-Domain Routing — IP address range notation used in VPC and subnet definitions |
| CMK | Customer-Managed Key — KMS key created and managed by the customer |
| CPU | Central Processing Unit — primary compute processor |
| CRR | Cross-Region Replication — automatic S3 object replication to a bucket in another region |
| DAX | DynamoDB Accelerator — in-memory cache for DynamoDB reducing read latency to microseconds |
| DLQ | Dead-Letter Queue — SQS or SNS queue for undeliverable messages after maximum receive attempts |
| DNS | Domain Name System — resolves hostnames to IP addresses; delivered by Amazon Route 53 |
| DR | Disaster Recovery — strategies for restoring workloads after a catastrophic failure |
| DRT | DDoS Response Team — AWS Shield Advanced team providing 24/7 attack support |
| EBS | Elastic Block Store — persistent block storage volumes attached to EC2 instances |
| EC2 | Elastic Compute Cloud — scalable virtual machine service |
| ECS | Elastic Container Service — fully managed container orchestration service |
| EFS | Elastic File System — fully managed, elastic NFS file system for Linux workloads |
| EKS | Elastic Kubernetes Service — managed Kubernetes cluster service |
| ETL | Extract, Transform, Load — pipeline pattern for moving data; delivered by AWS Glue |
| FIFO | First In, First Out — message ordering and deduplication guarantee for SQS FIFO queues |
| GPU | Graphics Processing Unit — parallel compute accelerator used in EC2 P and G instance families |
| HA | High Availability — design pattern eliminating single points of failure for continuous operation |
| IA | Infrequent Access — S3 and EFS storage class optimised for data accessed less than once per month |
| IAM | Identity and Access Management — AWS service for managing users, roles, and permissions |
| KMS | Key Management Service — managed service for creating and controlling encryption keys |
| MFA | Multi-Factor Authentication — authentication requiring two or more verification factors |
| ML | Machine Learning — AI workloads; Amazon SageMaker is the managed training and inference platform |
| MTBF | Mean Time Between Failures — average time between system failures; reliability metric |
| MTTR | Mean Time To Recovery — average time to restore service after a failure |
| NAT | Network Address Translation — maps private IP addresses to a public IP for outbound internet traffic |
| NFS | Network File System — file-sharing protocol used by Amazon EFS |
| NLB | Network Load Balancer — L4 TCP/UDP load balancer for ultra-high throughput and static IP support |
| OIDC | OpenID Connect — identity federation protocol used with IAM Identity Center and IRSA on EKS |
| OLAP | Online Analytical Processing — analytical query workload; served by Amazon Redshift |
| OU | Organizational Unit — container within AWS Organizations for grouping accounts and applying SCPs |
| PII | Personally Identifiable Information — sensitive data subject to privacy regulations |
| RDS | Relational Database Service — managed relational database engine hosting MySQL, PostgreSQL, SQL Server and others |
| RPO | Recovery Point Objective — maximum acceptable data loss window measured in time |
| RTO | Recovery Time Objective — maximum acceptable downtime window after a failure |
| S3 | Simple Storage Service — scalable, durable object storage service |
| SAML | Security Assertion Markup Language — XML-based federation protocol used in IAM Identity Center SSO |
| SCP | Service Control Policy — organization-wide permission guardrails applied via AWS Organizations |
| SIEM | Security Information and Event Management — log aggregation and threat detection platform |
| SLA | Service Level Agreement — AWS's uptime and availability commitments per service |
| SNS | Simple Notification Service — managed pub/sub messaging and mobile push service |
| SQL | Structured Query Language — query language used by relational databases including Amazon RDS and Redshift |
| SQS | Simple Queue Service — managed message queue for decoupling distributed application components |
| SSE | Server-Side Encryption — storage service encrypts data at rest before writing |
| SSO | Single Sign-On — authentication allowing one login to access multiple services; delivered via IAM Identity Center |
| STS | Security Token Service — issues temporary, scoped credentials for IAM role assumption |
| TCP | Transmission Control Protocol — connection-oriented L4 transport protocol |
| TLS | Transport Layer Security — cryptographic protocol enforcing encryption in transit |
| TPS | Transactions Per Second — throughput capacity metric for databases and messaging services |
| UDP | User Datagram Protocol — connectionless L4 transport protocol for low-latency workloads |
| VPC | Virtual Private Cloud — logically isolated virtual network in AWS |
| VPN | Virtual Private Network — encrypted tunnel connecting on-premises networks to a VPC |
| WAF | Web Application Firewall — L7 filter protecting web apps from OWASP Top 10 attacks; delivered by AWS WAF |
