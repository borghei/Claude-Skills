---
name: senior-cloud-architect
description: Expert cloud architecture covering AWS, GCP, Azure, multi-cloud strategy, cost optimization, and cloud-native design.
version: 1.0.0
author: Claude Skills
category: engineering
tags: [cloud, aws, gcp, azure, architecture, infrastructure]
---

# Senior Cloud Architect

Expert-level cloud architecture and infrastructure design.

## Core Competencies

- Multi-cloud architecture
- AWS, GCP, Azure platforms
- Cloud-native design patterns
- Cost optimization
- Security and compliance
- Migration strategies
- Disaster recovery
- Infrastructure automation

## Cloud Platform Comparison

| Service | AWS | GCP | Azure |
|---------|-----|-----|-------|
| Compute | EC2, ECS, EKS | GCE, GKE | VMs, AKS |
| Serverless | Lambda | Cloud Functions | Azure Functions |
| Storage | S3 | Cloud Storage | Blob Storage |
| Database | RDS, DynamoDB | Cloud SQL, Spanner | SQL DB, CosmosDB |
| ML | SageMaker | Vertex AI | Azure ML |
| CDN | CloudFront | Cloud CDN | Azure CDN |

## AWS Architecture

### Well-Architected Framework

**Pillars:**

1. **Operational Excellence**
   - Infrastructure as Code
   - Monitoring and observability
   - Incident response
   - Continuous improvement

2. **Security**
   - Identity and access management
   - Data protection
   - Infrastructure protection
   - Incident response

3. **Reliability**
   - Fault tolerance
   - Disaster recovery
   - Change management
   - Failure testing

4. **Performance Efficiency**
   - Right-sizing resources
   - Monitoring performance
   - Trade-off decisions
   - Keeping current

5. **Cost Optimization**
   - Cost awareness
   - Right-sizing
   - Reserved capacity
   - Efficient resources

6. **Sustainability**
   - Region selection
   - Efficient algorithms
   - Hardware utilization
   - Data management

### Reference Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Route 53 (DNS)                       │
└─────────────────────────────┬───────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────┐
│                    CloudFront (CDN)                         │
│                    WAF (Web Application Firewall)           │
└─────────────────────────────┬───────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────┐
│                Application Load Balancer                     │
└──────────┬───────────────────────────────────┬──────────────┘
           │                                   │
┌──────────▼──────────┐             ┌──────────▼──────────┐
│   ECS/EKS Cluster   │             │   ECS/EKS Cluster   │
│   (AZ-a)            │             │   (AZ-b)            │
└──────────┬──────────┘             └──────────┬──────────┘
           │                                   │
┌──────────▼───────────────────────────────────▼──────────┐
│                    ElastiCache (Redis)                   │
└─────────────────────────────┬───────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────┐
│                    RDS Multi-AZ                          │
│                    (Primary + Standby)                   │
└─────────────────────────────────────────────────────────┘
```

### Terraform AWS Module

```hcl
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"

  name = "${var.project}-${var.environment}"
  cidr = var.vpc_cidr

  azs             = ["${var.region}a", "${var.region}b", "${var.region}c"]
  private_subnets = var.private_subnets
  public_subnets  = var.public_subnets

  enable_nat_gateway     = true
  single_nat_gateway     = var.environment != "production"
  enable_dns_hostnames   = true
  enable_dns_support     = true

  tags = local.common_tags
}

module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 19.0"

  cluster_name    = "${var.project}-${var.environment}"
  cluster_version = "1.28"

  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets

  cluster_endpoint_public_access  = true
  cluster_endpoint_private_access = true

  eks_managed_node_groups = {
    main = {
      instance_types = var.node_instance_types
      min_size       = var.node_min_size
      max_size       = var.node_max_size
      desired_size   = var.node_desired_size
    }
  }

  tags = local.common_tags
}

module "rds" {
  source  = "terraform-aws-modules/rds/aws"
  version = "~> 6.0"

  identifier = "${var.project}-${var.environment}"

  engine               = "postgres"
  engine_version       = "15"
  family               = "postgres15"
  major_engine_version = "15"
  instance_class       = var.db_instance_class

  allocated_storage     = var.db_allocated_storage
  max_allocated_storage = var.db_max_allocated_storage

  db_name  = var.db_name
  username = var.db_username
  port     = 5432

  multi_az               = var.environment == "production"
  db_subnet_group_name   = module.vpc.database_subnet_group
  vpc_security_group_ids = [module.security_group.security_group_id]

  backup_retention_period = var.environment == "production" ? 30 : 7
  skip_final_snapshot     = var.environment != "production"

  tags = local.common_tags
}
```

## Cost Optimization

### Reserved vs On-Demand vs Spot

| Type | Discount | Commitment | Use Case |
|------|----------|------------|----------|
| On-Demand | 0% | None | Variable workloads |
| Reserved | 30-72% | 1-3 years | Steady-state |
| Savings Plans | 30-72% | 1-3 years | Flexible compute |
| Spot | 60-90% | None | Fault-tolerant |

### Cost Optimization Strategies

**Right-sizing:**
```python
def analyze_utilization(instance_id: str, days: int = 14):
    """Analyze CPU/memory utilization for right-sizing recommendations."""
    cloudwatch = boto3.client('cloudwatch')

    metrics = cloudwatch.get_metric_statistics(
        Namespace='AWS/EC2',
        MetricName='CPUUtilization',
        Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
        StartTime=datetime.now() - timedelta(days=days),
        EndTime=datetime.now(),
        Period=3600,
        Statistics=['Average', 'Maximum']
    )

    avg_cpu = sum(p['Average'] for p in metrics['Datapoints']) / len(metrics['Datapoints'])
    max_cpu = max(p['Maximum'] for p in metrics['Datapoints'])

    if avg_cpu < 10 and max_cpu < 30:
        return 'downsize'
    elif avg_cpu > 80:
        return 'upsize'
    else:
        return 'optimal'
```

**Cost Allocation Tags:**
```yaml
required_tags:
  - Environment: production|staging|development
  - Project: project-name
  - Owner: team-name
  - CostCenter: cost-center-id

automation:
  - Untagged resources alert after 24 hours
  - Auto-terminate development resources after 7 days
  - Weekly cost reports by tag
```

### Cost Dashboard

```
┌─────────────────────────────────────────────────────────────┐
│                    Monthly Cost Summary                      │
├─────────────────────────────────────────────────────────────┤
│  Total: $45,231     vs Last Month: +5%                      │
│                                                              │
│  By Service:                    By Environment:              │
│  ├── EC2: $18,500 (41%)        ├── Production: $38,000      │
│  ├── RDS: $12,000 (27%)        ├── Staging: $4,500          │
│  ├── S3: $3,200 (7%)           └── Development: $2,731      │
│  ├── Lambda: $1,800 (4%)                                     │
│  └── Other: $9,731 (21%)       Savings Opportunity: $8,200   │
│                                                              │
│  Recommendations:                                            │
│  • Convert 12 instances to Reserved (save $4,200/mo)        │
│  • Delete 5 unused EBS volumes (save $180/mo)               │
│  • Resize 8 over-provisioned instances (save $1,800/mo)     │
└─────────────────────────────────────────────────────────────┘
```

## Disaster Recovery

### DR Strategies

| Strategy | RTO | RPO | Cost |
|----------|-----|-----|------|
| Backup & Restore | Hours | Hours | $ |
| Pilot Light | Minutes | Minutes | $$ |
| Warm Standby | Minutes | Seconds | $$$ |
| Multi-Site Active | Seconds | Near-zero | $$$$ |

### Multi-Region Architecture

```
┌────────────────────────────────────────────────────────────┐
│                      Global Load Balancer                   │
│                      (Route 53 / Cloud DNS)                 │
└──────────────┬─────────────────────────────┬───────────────┘
               │                             │
┌──────────────▼──────────────┐ ┌────────────▼──────────────┐
│      Primary Region         │ │     Secondary Region       │
│      (us-east-1)           │ │     (us-west-2)           │
│                            │ │                            │
│  ┌──────────────────────┐  │ │  ┌──────────────────────┐  │
│  │   Application Layer  │  │ │  │   Application Layer  │  │
│  │   (Active)          │  │ │  │   (Standby/Active)   │  │
│  └──────────┬───────────┘  │ │  └──────────┬───────────┘  │
│             │              │ │             │              │
│  ┌──────────▼───────────┐  │ │  ┌──────────▼───────────┐  │
│  │   Database           │──┼─┼──│   Database           │  │
│  │   (Primary)         │  │ │  │   (Read Replica)     │  │
│  └──────────────────────┘  │ │  └──────────────────────┘  │
└────────────────────────────┘ └────────────────────────────┘
                    │
                    │ Cross-Region Replication
                    ▼
        ┌──────────────────────┐
        │     S3 Backup        │
        │   (Multi-Region)     │
        └──────────────────────┘
```

### Backup Strategy

```yaml
backup_policy:
  database:
    frequency: continuous
    retention: 35 days
    cross_region: true
    encryption: aws/rds

  application_data:
    frequency: daily
    retention: 90 days
    versioning: enabled
    lifecycle:
      - transition_to_ia: 30 days
      - transition_to_glacier: 90 days
      - expiration: 365 days

  configuration:
    frequency: on_change
    retention: unlimited
    storage: git + s3
```

## Security Architecture

### Network Security

```
┌─────────────────────────────────────────────────────────────┐
│                           VPC                                │
│  ┌───────────────────────────────────────────────────────┐  │
│  │                    Public Subnet                       │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌───────────────┐  │  │
│  │  │   NAT GW    │  │     ALB     │  │   Bastion     │  │  │
│  │  └─────────────┘  └─────────────┘  └───────────────┘  │  │
│  └───────────────────────────────────────────────────────┘  │
│                              │                               │
│  ┌───────────────────────────▼───────────────────────────┐  │
│  │                   Private Subnet                       │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌───────────────┐  │  │
│  │  │   App Tier  │  │   App Tier  │  │   App Tier    │  │  │
│  │  └─────────────┘  └─────────────┘  └───────────────┘  │  │
│  └───────────────────────────────────────────────────────┘  │
│                              │                               │
│  ┌───────────────────────────▼───────────────────────────┐  │
│  │                   Data Subnet                          │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌───────────────┐  │  │
│  │  │     RDS     │  │    Redis    │  │  Elasticsearch│  │  │
│  │  └─────────────┘  └─────────────┘  └───────────────┘  │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### IAM Best Practices

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "LeastPrivilegeExample",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject"
      ],
      "Resource": "arn:aws:s3:::my-bucket/uploads/*",
      "Condition": {
        "StringEquals": {
          "aws:PrincipalTag/Team": "engineering"
        },
        "IpAddress": {
          "aws:SourceIp": ["10.0.0.0/8"]
        }
      }
    }
  ]
}
```

## Reference Materials

- `references/aws_patterns.md` - AWS architecture patterns
- `references/gcp_patterns.md` - GCP architecture patterns
- `references/multi_cloud.md` - Multi-cloud strategies
- `references/cost_optimization.md` - Cost optimization guide

## Scripts

```bash
# Infrastructure cost analyzer
python scripts/cost_analyzer.py --account production --period monthly

# DR validation
python scripts/dr_test.py --region us-west-2 --type failover

# Security audit
python scripts/security_audit.py --framework cis --output report.html

# Resource inventory
python scripts/inventory.py --accounts all --format csv
```
