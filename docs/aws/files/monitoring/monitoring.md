# MONITORING & OBSERVABILITY

## Core Observability Services

| Service | Type | Best For | Key Feature |
| --- | --- | --- | --- |
| **CloudWatch Metrics** | Metrics | Resource and custom application metrics | Alarms, dashboards, anomaly detection |
| **CloudWatch Logs** | Log management | Centralised log aggregation and search | Log groups, Logs Insights query language |
| **CloudWatch Alarms** | Alerting | Threshold-based or anomaly alerts | SNS, Auto Scaling, EC2 actions |
| **CloudTrail** | API audit | Track who did what in your AWS account | Management events, data events, S3 export |
| **AWS X-Ray** | Distributed tracing | Microservice latency and dependency mapping | Service map, subsegment traces, filter expressions |
| **AWS Config** | Configuration history | Track resource changes, compliance rules | Config rules, conformance packs, remediations |

> **Exam tip:** CloudTrail answers "who changed what and when." CloudWatch
> answers "what is the system doing right now." X-Ray answers "why is this
> request slow." Config answers "has this resource drifted from desired state."

## Monitoring Decision Flow

```mermaid
--8<-- "aws/diagrams/monitoring/decision-flow.mmd"
```

## CloudWatch Alarm States

| State | Meaning | Key Feature |
| --- | --- | --- |
| **OK** | Metric within threshold | No action triggered |
| **ALARM** | Metric breached threshold | SNS notification, Auto Scaling action |
| **INSUFFICIENT_DATA** | Not enough data points yet | Often seen on newly created alarms |

> **Exam tip:** CloudWatch does not natively monitor application-level logs or
> custom metrics — you must install the CloudWatch Agent or use the PutMetricData
> API to push custom metrics. Without the agent, EC2 memory and disk utilisation
> are not visible in CloudWatch.
