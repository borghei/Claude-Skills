---
name: senior-cloud-architect
description: >
  Cloud architecture decisions across AWS, GCP and Azure: topology, DR tier by RTO/RPO,
  commitment mix, IAM and network posture. Use when designing, costing, migrating or
  auditing cloud infrastructure.
license: MIT + Commons Clause
metadata:
  version: 1.1.0
  author: borghei
  category: engineering
  domain: cloud-architecture
  updated: 2026-11-08
  tags: [cloud, aws, gcp, azure, architecture, infrastructure, terraform]
---
# Senior Cloud Architect

Expert cloud architecture and infrastructure design across AWS, GCP, and Azure — production-grade VPC/compute/database topologies, cost optimization, disaster recovery, and security posture auditing.

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

Before designing the architecture, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Target cloud(s):** AWS / GCP / Azure or multi-cloud (every topology, service mapping, and Terraform differs).
- **Workload profile & scale:** traffic, statefulness, and compute type (drives the VPC / compute / database topology and sizing).
- **RTO/RPO targets:** recovery objectives (selects Backup / Pilot Light / Warm Standby / Multi-Site DR).
- **Budget / cost constraint:** the spend ceiling (drives right-sizing and Reserved vs Savings Plan vs Spot).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Decision Rules

These are the calls this skill exists to make well; the references hold the Terraform and
service detail. Every number below is a starting heuristic, so state it as one and adjust to
the workload's measurements.

**DR tier from RTO/RPO** [RECOMMENDED]

| Target | Tier | What it costs you |
|--------|------|-------------------|
| RTO hours, RPO up to 24h | Backup and restore (cross-region snapshots) | Lowest; restore time must be rehearsed |
| RTO under an hour, RPO minutes | Pilot light (replicated data, minimal compute off) | Data replication plus IaC to bring compute up |
| RTO minutes, RPO seconds | Warm standby (scaled-down live copy) | A second, smaller running environment |
| RTO near zero, RPO near zero | Multi-site active-active | Roughly double, plus conflict handling in the data layer |

Pick the cheapest tier that meets the target, then prove it: a DR plan is unverified until a
failover drill has met the RTO on a clock.

**Commitment mix** [RECOMMENDED]
- Commit (savings plans / reserved / committed-use) only to the steady baseline: the floor of
  the last 30-60 days of usage, not the average.
- Put interruptible, stateless or batch work on spot/preemptible capacity with a fallback.
- Leave growth and spiky load on on-demand until it has been stable for a quarter.
- Right-size before committing; a commitment locks in an oversized instance.

**Availability and blast radius** [PROVEN]
- Production spans at least two availability zones; single-AZ is a dev/test choice.
- Multi-region only when the RTO, latency or data-residency requirement demands it; it
  multiplies cost and operational load.
- Separate accounts/projects per environment, with least-privilege roles and no long-lived
  access keys for humans.

**Verify before calling it done**
- `terraform plan` is clean and reviewed; state is remote and locked.
- Cost estimate for the design exists (provider calculator or `infracost`), with the
  assumptions written down and an "as of" date, since prices change.
- Security baseline checked (CIS benchmark or the provider's security hub), public exposure
  limited to the load balancer or CDN.
- For DR: the last failover drill's measured RTO/RPO is recorded.

## Workflow

1. Settle the Clarify First inputs; write the RTO/RPO, budget and data-residency constraints at the top of the design.
2. Choose the DR tier and commitment mix with the rules above, and the topology (AZs, regions, accounts).
3. Write the infrastructure as Terraform modules (see `references/cloud-architecture-playbooks.md`).
4. Validate before handing over:
   ```bash
   terraform fmt -check && terraform validate && terraform plan -out plan.tfplan
   infracost breakdown --path plan.tfplan   # cost estimate, if infracost is available
   ```
5. Record the cost assumptions with an as-of date, the security baseline result, and the date of the next failover drill.

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

| Skill | Use for |
|-------|---------|
| `aws-solution-architect`, `azure-cloud-architect`, `gcp-cloud-architect` | Provider-specific implementation detail |
| `terraform-patterns` | Module design and Terraform security scanning |
| `senior-devops` | CI/CD and deployment onto the provisioned infrastructure |

## Anti-Patterns

### Designing for Hypothetical Scale
**Mistake:** Multi-region, multi-cloud and Kubernetes for a workload that fits one region and a managed container service.
**Why it happens:** The target architecture diagrams of large companies look like best practice.
**Instead:** Size to current load with headroom and a documented scale-up path. Complexity is paid for every day; scale arrives later, if at all.

### Committing Before Right-Sizing
**Mistake:** Buying a three-year commitment to cut the bill, then discovering the instances were twice the needed size.
**Why it happens:** Commitments show an immediate percentage saving.
**Instead:** Right-size from utilisation data first, commit to the measured floor, and review coverage quarterly.

### An Untested DR Plan
**Mistake:** Treating cross-region replication as a disaster recovery plan.
**Why it happens:** Replication is visible in the console; failover is not.
**Instead:** Run a failover drill, time it against the RTO, and fix what broke (DNS TTLs, secrets, hard-coded endpoints) before calling DR done.

## Files

| File | Purpose |
|------|---------|
| `references/cloud-architecture-playbooks.md` | Platform comparison, AWS architecture, cost, DR and security workflows with Terraform/IAM code, Well-Architected checklist |
| `references/cloud-operations.md` | Troubleshooting table and success criteria |
