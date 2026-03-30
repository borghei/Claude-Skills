---
name: senior-cloud-architect
description: 
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: engineering
  domain: cloud-architecture
  updated: 2026-03-31
  tags: [cloud, aws, gcp, azure, architecture, infrastructure, terraform]
---
# Senior Cloud Architect

Expert cloud architecture and infrastructure design across AWS, GCP, and Azure.

## Keywords

cloud, aws, gcp, azure, terraform, infrastructure, vpc, eks, ecs, lambda,
cost-optimization, disaster-recovery, multi-region, iam, security, migration

---

## Quick Start

```bash
# Analyze infrastructure costs
python scripts/cost_analyzer.py --account production --period monthly

# Run DR validation
python scripts/dr_test.py --region us-west-2 --type failover

# Audit security posture
python scripts/security_audit.py --framework cis --output report.html

# Generate resource inventory
python scripts/inventory.py --accounts all --format csv
```

---

## Tools

| Script | Purpose |
|--------|---------|
| `scripts/cost_analyzer.py` | Analyze cloud spend by service, environment, and tag |
| `scripts/dr_test.py` | Validate disaster recovery failover procedures |
| `scripts/security_audit.py` | Audit against CIS benchmarks and compliance frameworks |
| `scripts/inventory.py` | Inventory all resources across accounts and regions |

---

## Cloud Platform Comparison

| Service | AWS | GCP | Azure |
|---------|-----|-----|-------|
| Compute | EC2, ECS, EKS | GCE, GKE | VMs, AKS |
| Serverless | Lambda | Cloud Functions | Azure Functions |
| Storage | S3 | Cloud Storage | Blob Storage |
| Database | RDS, DynamoDB | Cloud SQL, Spanner | SQL DB, CosmosDB |
| ML | SageMaker | Vertex AI | Azure ML |
| CDN | CloudFront | Cloud CDN | Azure CDN |

---

## Workflow 1: Design a Production AWS Architecture

1. **Define requirements** -- Identify compute, storage, database, and networking needs. Determine RTO/RPO targets.
2. **Provision VPC with Terraform:**
   ```hcl
   module "vpc" {
     source  = "terraform-aws-modules/vpc/aws"
     version = "~> 5.0"
     name    = "${var.project}-${var.environment}"
     cidr    = var.vpc_cidr
     azs             = ["${var.region}a", "${var.region}b", "${var.region}c"]
     private_subnets = var.private_subnets
     public_subnets  = var.public_subnets
     enable_nat_gateway   = true
     single_nat_gateway   = var.environment != "production"
     enable_dns_hostnames = true
     tags = local.common_tags
   }
   ```
3. **Deploy compute** -- ECS/EKS in private subnets behind an ALB in public subnets. Use at least 2 AZs for redundancy.
4. **Configure database** -- RDS Multi-AZ for production, single-AZ for staging. Set backup retention to 30 days (production) or 7 days (non-production).
5. **Add caching layer** -- ElastiCache (Redis) between application and database.
6. **Layer security** -- WAF on CloudFront, NACLs on subnets, security groups on instances. Apply least-privilege IAM.
7. **Validate** -- Run `python scripts/security_audit.py --framework cis` and resolve all high-severity findings.

### Reference Architecture

```
Route 53 (DNS) -> CloudFront + WAF -> ALB
  -> ECS/EKS Cluster (AZ-a) + ECS/EKS Cluster (AZ-b)
    -> ElastiCache (Redis)
      -> RDS Multi-AZ (Primary + Standby)
```

## Workflow 2: Optimize Cloud Costs

1. **Audit current spend** -- `python scripts/cost_analyzer.py --account production --period monthly`
2. **Right-size instances** -- Identify instances with avg CPU <10% and max CPU <30% as downsize candidates:
   ```python
   # Pseudocode for right-sizing logic
   if avg_cpu < 10 and max_cpu < 30:
       recommendation = 'downsize'
   elif avg_cpu > 80:
       recommendation = 'upsize'
   else:
       recommendation = 'optimal'
   ```
3. **Convert steady-state workloads** to Reserved Instances or Savings Plans:
   | Type | Discount | Commitment | Use Case |
   |------|----------|------------|----------|
   | On-Demand | 0% | None | Variable workloads |
   | Reserved | 30-72% | 1-3 years | Steady-state |
   | Savings Plans | 30-72% | 1-3 years | Flexible compute |
   | Spot | 60-90% | None | Fault-tolerant batch |
4. **Enforce cost allocation tags** -- Require `Environment`, `Project`, `Owner`, `CostCenter` on all resources. Alert on untagged resources after 24 hours.
5. **Validate** -- Re-run cost analyzer and confirm savings target achieved.

## Workflow 3: Plan Disaster Recovery

1. **Select DR strategy** based on RTO/RPO requirements:
   | Strategy | RTO | RPO | Cost |
   |----------|-----|-----|------|
   | Backup & Restore | Hours | Hours | $ |
   | Pilot Light | Minutes | Minutes | $$ |
   | Warm Standby | Minutes | Seconds | $$$ |
   | Multi-Site Active | Seconds | Near-zero | $$$$ |
2. **Configure cross-region replication** -- Database replication to secondary region. S3 cross-region replication for object storage.
3. **Set up Route 53 failover routing** -- Health checks on primary. Automatic DNS failover to secondary.
4. **Define backup policy:**
   - Database: continuous replication, 35-day retention, cross-region, encrypted
   - Application data: daily, 90-day retention, lifecycle to IA at 30d, Glacier at 90d
   - Configuration: on-change via git + S3, unlimited retention
5. **Test** -- `python scripts/dr_test.py --region us-west-2 --type failover` and confirm RTO/RPO targets met.

## Workflow 4: Audit Security Posture

1. **Run audit** -- `python scripts/security_audit.py --framework cis --output report.html`
2. **Review network segmentation** -- Public subnets contain only NAT GW, ALB, bastion. Private subnets contain application tier. Data subnets contain RDS, Redis, Elasticsearch.
3. **Enforce least-privilege IAM** -- Every policy scoped to specific resources and conditions:
   ```json
   {
     "Effect": "Allow",
     "Action": ["s3:GetObject", "s3:PutObject"],
     "Resource": "arn:aws:s3:::my-bucket/uploads/*",
     "Condition": {
       "StringEquals": { "aws:PrincipalTag/Team": "engineering" },
       "IpAddress": { "aws:SourceIp": ["10.0.0.0/8"] }
     }
   }
   ```
4. **Verify encryption** -- Data encrypted at rest (KMS) and in transit (TLS 1.2+).
5. **Validate** -- Re-run audit and confirm all critical and high findings resolved.

---

## AWS Well-Architected Pillars (Decision Checklist)

- **Operational Excellence**: IaC everywhere? Monitoring and alerting? Runbooks for incidents?
- **Security**: Least-privilege IAM? Encryption at rest and in transit? VPC segmentation?
- **Reliability**: Multi-AZ? Auto-scaling? DR tested?
- **Performance**: Right-sized instances? Caching layer? CDN for static assets?
- **Cost Optimization**: Reserved capacity for steady-state? Spot for batch? Unused resources cleaned?
- **Sustainability**: Efficient regions? Right-sized compute? Data lifecycle policies?

---

## Reference Materials

| Document | Path |
|----------|------|
| AWS Patterns | [references/aws_patterns.md](references/aws_patterns.md) |
| GCP Patterns | [references/gcp_patterns.md](references/gcp_patterns.md) |
| Multi-Cloud Strategies | [references/multi_cloud.md](references/multi_cloud.md) |
| Cost Optimization Guide | [references/cost_optimization.md](references/cost_optimization.md) |

---

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| Cross-region latency exceeds 200ms | No regional caching or CDN configured | Deploy CloudFront/Cloud CDN with edge locations closest to user base; enable regional API Gateway caches |
| Terraform state lock conflicts across teams | Shared state backend without proper locking | Use DynamoDB (AWS) or GCS (GCP) state locking with per-team state file partitioning via workspaces |
| Multi-cloud DNS failover not triggering | Health check thresholds too lenient or misconfigured endpoints | Set health check interval to 10s, failure threshold to 3, and verify endpoint returns 200 on the exact path monitored |
| IAM permission errors after cross-account migration | Trust policies not updated for new account IDs | Update AssumeRole trust policies with correct account principals and external IDs; validate with `aws sts assume-role` |
| Cloud costs spike unexpectedly after scaling event | Auto-scaling max limits set too high or no budget alerts | Set hard max instance counts per ASG, configure billing alerts at 80%/100%/120% thresholds, and review Spot fallback behavior |
| VPC peering routes not propagating between clouds | Route tables missing entries for peered CIDR ranges | Add explicit route entries in both VPCs pointing peered CIDRs to the peering connection; verify no overlapping CIDRs |
| DR failover test fails with data inconsistency | Replication lag between primary and secondary regions | Switch to synchronous replication for critical databases or implement application-level consistency checks pre-failover |

---

## Success Criteria

- **99.99% availability SLA met** across all production workloads with documented uptime reports
- **Cost optimization savings above 25%** compared to on-demand baseline through Reserved Instances, Savings Plans, and right-sizing
- **RTO < 15 minutes and RPO < 1 minute** validated through quarterly DR failover tests
- **Zero critical CIS benchmark findings** in production accounts after security audit remediation
- **Infrastructure drift < 2%** measured by Terraform plan diffs on scheduled compliance scans
- **Cross-region failover completes within 60 seconds** with automated Route 53 health check validation
- **100% resource tagging compliance** enforced via automated policy checks with no untagged resources older than 24 hours

---

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

---

## Integration Points

| Skill | Integration | Data Flow |
|-------|-------------|-----------|
| `senior-devops` | Infrastructure provisioning feeds into CI/CD deployment pipelines | Terraform outputs (endpoints, ARNs) → deployment configs |
| `senior-secops` | Security audit findings inform cloud hardening decisions | CIS benchmark results → security remediation tasks |
| `senior-architect` | Application architecture requirements drive cloud resource selection | Capacity requirements → compute/storage/network sizing |
| `aws-solution-architect` | AWS-specific deep dives complement multi-cloud strategy | Cloud platform comparison → AWS implementation details |
| `ra-qm-team/soc2-compliance` | Compliance requirements shape infrastructure security controls | Compliance matrices → IAM policies, encryption configs, audit logging |
| `senior-fullstack` | Fullstack application stacks deploy onto cloud infrastructure | Application stack definitions → ECS/EKS task definitions, RDS configs |
