---
name: senior-cloud-architect
description: 
license: MIT + Commons Clause
metadata:
  version: 1.1.0
  author: borghei
  category: engineering
  domain: cloud-architecture
  updated: 2026-06-17
  tags: [cloud, aws, gcp, azure, architecture, infrastructure, terraform]
---
# Senior Cloud Architect

Expert cloud architecture and infrastructure design across AWS, GCP, and Azure — production-grade VPC/compute/database topologies, cost optimization, disaster recovery, and security posture auditing.

## Keywords

cloud, aws, gcp, azure, terraform, infrastructure, vpc, eks, ecs, lambda,
cost-optimization, disaster-recovery, multi-region, iam, security, migration

## Core Capabilities

- **Production architecture design** — Terraform VPC, multi-AZ ECS/EKS behind ALB, RDS Multi-AZ, ElastiCache, layered WAF/NACL/SG security.
- **Multi-cloud comparison** — map equivalent compute, serverless, storage, database, ML, and CDN services across AWS, GCP, and Azure.
- **Cost optimization** — right-sizing, Reserved Instances/Savings Plans/Spot selection, cost-allocation tagging, budget alerting.
- **Disaster recovery** — Backup/Pilot Light/Warm Standby/Multi-Site strategy selection against RTO/RPO, cross-region replication, Route 53 failover.
- **Security posture** — CIS benchmark audits, network segmentation, least-privilege IAM with conditions, encryption at rest and in transit.
- **Well-Architected reviews** — checklist across all six pillars (operational excellence, security, reliability, performance, cost, sustainability).

## When to Use

- Designing a new production cloud architecture or migration.
- Reducing cloud spend or planning reserved capacity.
- Planning or testing disaster recovery and failover.
- Auditing security posture against CIS benchmarks.
- Comparing AWS / GCP / Azure for a workload.

## Clarify First

Before designing the architecture, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Target cloud(s)** — AWS / GCP / Azure or multi-cloud (every topology, service mapping, and Terraform differs)
- [ ] **Workload profile & scale** — traffic, statefulness, and compute type (drives the VPC / compute / database topology and sizing)
- [ ] **RTO/RPO targets** — recovery objectives (selects Backup / Pilot Light / Warm Standby / Multi-Site DR)
- [ ] **Budget / cost constraint** — the spend ceiling (drives right-sizing and Reserved vs Savings Plan vs Spot)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## References

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/cloud-architecture-playbooks.md](references/cloud-architecture-playbooks.md)** — quick-start commands, the cloud platform comparison matrix, the four end-to-end workflows (AWS architecture, cost optimization, DR planning, security audit) with Terraform/IAM/cost code, and the AWS Well-Architected checklist. Read when designing, optimizing, or auditing an architecture.
- **[references/cloud-operations.md](references/cloud-operations.md)** — troubleshooting table (latency, state locks, failover, IAM, cost spikes, peering, replication) and the architecture success criteria. Read when diagnosing an issue or defining the quality bar.

## Scope & Limitations

**This skill covers:**
- Multi-cloud architecture design and comparison across AWS, GCP, and Azure
- Infrastructure-as-Code with Terraform including VPC, compute, database, and networking
- Disaster recovery planning, cross-region replication, and failover strategies
- Cloud cost optimization, right-sizing, and reserved capacity planning

**This skill does NOT cover:**
- Application-level code architecture or microservice design patterns (see `senior-architect`)
- Kubernetes cluster internals, pod scheduling, or service mesh configuration (see `senior-devops`)
- Security compliance frameworks beyond CIS benchmarks such as SOC 2, HIPAA, or GDPR (see `ra-qm-team/` compliance skills)
- CI/CD pipeline design, build automation, or deployment workflows (see `senior-devops`)

## Integration Points

| Skill | Integration | Data Flow |
|-------|-------------|-----------|
| `senior-devops` | Infrastructure provisioning feeds into CI/CD deployment pipelines | Terraform outputs (endpoints, ARNs) → deployment configs |
| `senior-secops` | Security audit findings inform cloud hardening decisions | CIS benchmark results → security remediation tasks |
| `senior-architect` | Application architecture requirements drive cloud resource selection | Capacity requirements → compute/storage/network sizing |
| `aws-solution-architect` | AWS-specific deep dives complement multi-cloud strategy | Cloud platform comparison → AWS implementation details |
| `ra-qm-team/soc2-compliance` | Compliance requirements shape infrastructure security controls | Compliance matrices → IAM policies, encryption configs, audit logging |
| `senior-fullstack` | Fullstack application stacks deploy onto cloud infrastructure | Application stack definitions → ECS/EKS task definitions, RDS configs |
