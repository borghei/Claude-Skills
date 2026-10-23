# Cloud Architecture Playbooks

Read this when designing a cloud architecture, optimizing cost, planning disaster recovery, or auditing security posture — the quick-start commands, platform comparison, the four end-to-end workflows, and the Well-Architected checklist.

## Quick Start

This skill ships no scripts of its own. For the jobs below, use the tools in the sibling cloud skills or your provider's native tooling:

```bash
# Cost estimate for a planned workload (Azure, GCP)
python ../azure-cloud-architect/scripts/azure_cost_estimator.py --workload-config workload.yaml
python ../gcp-cloud-architect/scripts/gcp_cost_estimator.py --workload-config workload.yaml

# Security posture of an exported resource inventory (fails on high-severity findings)
python ../cloud-security/scripts/posture_auditor.py --input inventory.json --fail-on high
```

## Tools

| Job | Where it lives |
|-----|----------------|
| Cost estimation | `engineering/azure-cloud-architect/` (`azure_cost_estimator.py`), `engineering/gcp-cloud-architect/` (`gcp_cost_estimator.py`) |
| Security posture audit | `engineering/cloud-security/` (`posture_auditor.py`, `iam_least_privilege.py`) |
| Architecture review | `engineering/azure-cloud-architect/` (`azure_architecture_validator.py`), `engineering/gcp-cloud-architect/` (`gcp_architecture_validator.py`) |
| Resource inventory | The provider's own inventory service (AWS Config, Azure Resource Graph, Google Cloud Asset Inventory) |
| Disaster-recovery testing | A scheduled failover drill run from your runbooks and infrastructure code; no script can validate it for you |

## Cloud Platform Comparison

| Service | AWS | GCP | Azure |
|---------|-----|-----|-------|
| Compute | EC2, ECS, EKS | GCE, GKE | VMs, AKS |
| Serverless | Lambda | Cloud Functions | Azure Functions |
| Storage | S3 | Cloud Storage | Blob Storage |
| Database | RDS, DynamoDB | Cloud SQL, Spanner | SQL DB, CosmosDB |
| ML | SageMaker | Vertex AI | Azure ML |
| CDN | CloudFront | Cloud CDN | Azure CDN |

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
7. **Validate** -- Run `python ../cloud-security/scripts/posture_auditor.py --input inventory.json --fail-on high` on an inventory export and resolve all high-severity findings.

### Reference Architecture

```
Route 53 (DNS) -> CloudFront + WAF -> ALB
  -> ECS/EKS Cluster (AZ-a) + ECS/EKS Cluster (AZ-b)
    -> ElastiCache (Redis)
      -> RDS Multi-AZ (Primary + Standby)
```

## Workflow 2: Optimize Cloud Costs

1. **Audit current spend** -- Pull a month of spend by service, environment and tag from the provider's billing export (AWS Cost Explorer, Azure Cost Management, Google Cloud Billing).
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
5. **Test** -- Run a failover drill into the recovery region and confirm the RTO/RPO targets were met.

## Workflow 4: Audit Security Posture

1. **Run audit** -- `python ../cloud-security/scripts/posture_auditor.py --input inventory.json --format json` on a resource inventory export.
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

## AWS Well-Architected Pillars (Decision Checklist)

- **Operational Excellence**: IaC everywhere? Monitoring and alerting? Runbooks for incidents?
- **Security**: Least-privilege IAM? Encryption at rest and in transit? VPC segmentation?
- **Reliability**: Multi-AZ? Auto-scaling? DR tested?
- **Performance**: Right-sized instances? Caching layer? CDN for static assets?
- **Cost Optimization**: Reserved capacity for steady-state? Spot for batch? Unused resources cleaned?
- **Sustainability**: Efficient regions? Right-sized compute? Data lifecycle policies?
