---
name: aws-solution-architect
description: Design AWS architectures for startups using serverless patterns and IaC templates. Use when asked to design serverless architecture, create CloudFormation templates, optimize AWS costs, set up CI/CD pipelines, or migrate to AWS. Covers Lambda, API Gateway, DynamoDB, ECS, Aurora, and cost optimization.
---

# AWS Solution Architect

Design scalable, cost-effective AWS architectures for startups with infrastructure-as-code templates.

---

## Table of Contents

- [Trigger Terms](#trigger-terms)
- [Workflow](#workflow)
- [Tools](#tools)
- [Quick Start](#quick-start)
- [Input Requirements](#input-requirements)
- [Output Formats](#output-formats)

---

## Trigger Terms

Use this skill when you encounter:

| Category | Terms |
|----------|-------|
| **Architecture Design** | serverless architecture, AWS architecture, cloud design, microservices, three-tier |
| **IaC Generation** | CloudFormation, CDK, Terraform, infrastructure as code, deploy template |
| **Serverless** | Lambda, API Gateway, DynamoDB, Step Functions, EventBridge, AppSync |
| **Containers** | ECS, Fargate, EKS, container orchestration, Docker on AWS |
| **Cost Optimization** | reduce AWS costs, optimize spending, right-sizing, Savings Plans |
| **Database** | Aurora, RDS, DynamoDB design, database migration, data modeling |
| **Security** | IAM policies, VPC design, encryption, Cognito, WAF |
| **CI/CD** | CodePipeline, CodeBuild, CodeDeploy, GitHub Actions AWS |
| **Monitoring** | CloudWatch, X-Ray, observability, alarms, dashboards |
| **Migration** | migrate to AWS, lift and shift, replatform, DMS |

---

## Workflow

### Step 1: Gather Requirements

Collect application specifications:

```
- Application type (web app, mobile backend, data pipeline, SaaS)
- Expected users and requests per second
- Budget constraints (monthly spend limit)
- Team size and AWS experience level
- Compliance requirements (GDPR, HIPAA, SOC 2)
- Availability requirements (SLA, RPO/RTO)
```

### Step 2: Design Architecture

Run the architecture designer to get pattern recommendations:

```bash
python scripts/architecture_designer.py --input requirements.json
```

Select from recommended patterns:
- **Serverless Web**: S3 + CloudFront + API Gateway + Lambda + DynamoDB
- **Event-Driven Microservices**: EventBridge + Lambda + SQS + Step Functions
- **Three-Tier**: ALB + ECS Fargate + Aurora + ElastiCache
- **GraphQL Backend**: AppSync + Lambda + DynamoDB + Cognito

See `references/architecture_patterns.md` for detailed pattern specifications.

### Step 3: Generate IaC Templates

Create infrastructure-as-code for the selected pattern:

```bash
# Serverless stack (CloudFormation)
python scripts/serverless_stack.py --app-name my-app --region us-east-1

# Output: CloudFormation YAML template ready to deploy
```

### Step 4: Review Costs

Analyze estimated costs and optimization opportunities:

```bash
python scripts/cost_optimizer.py --resources current_setup.json --monthly-spend 2000
```

Output includes:
- Monthly cost breakdown by service
- Right-sizing recommendations
- Savings Plans opportunities
- Potential monthly savings

### Step 5: Deploy

Deploy the generated infrastructure:

```bash
# CloudFormation
aws cloudformation create-stack \
  --stack-name my-app-stack \
  --template-body file://template.yaml \
  --capabilities CAPABILITY_IAM

# CDK
cdk deploy

# Terraform
terraform init && terraform apply
```

### Step 6: Validate

Verify deployment and set up monitoring:

```bash
# Check stack status
aws cloudformation describe-stacks --stack-name my-app-stack

# Set up CloudWatch alarms
aws cloudwatch put-metric-alarm --alarm-name high-errors ...
```

---

## Tools

### architecture_designer.py

Generates architecture patterns based on requirements.

```bash
python scripts/architecture_designer.py --input requirements.json --output design.json
```

**Input:** JSON with app type, scale, budget, compliance needs
**Output:** Recommended pattern, service stack, cost estimate, pros/cons

### serverless_stack.py

Creates serverless CloudFormation templates.

```bash
python scripts/serverless_stack.py --app-name my-app --region us-east-1
```

**Output:** Production-ready CloudFormation YAML with:
- API Gateway + Lambda
- DynamoDB table
- Cognito user pool
- IAM roles with least privilege
- CloudWatch logging

### cost_optimizer.py

Analyzes costs and recommends optimizations.

```bash
python scripts/cost_optimizer.py --resources inventory.json --monthly-spend 5000
```

**Output:** Recommendations for:
- Idle resource removal
- Instance right-sizing
- Reserved capacity purchases
- Storage tier transitions
- NAT Gateway alternatives

---

## Quick Start

### MVP Architecture (< $100/month)

```
Ask: "Design a serverless MVP backend for a mobile app with 1000 users"

Result:
- Lambda + API Gateway for API
- DynamoDB pay-per-request for data
- Cognito for authentication
- S3 + CloudFront for static assets
- Estimated: $20-50/month
```

### Scaling Architecture ($500-2000/month)

```
Ask: "Design a scalable architecture for a SaaS platform with 50k users"

Result:
- ECS Fargate for containerized API
- Aurora Serverless for relational data
- ElastiCache for session caching
- CloudFront for CDN
- CodePipeline for CI/CD
- Multi-AZ deployment
```

### Cost Optimization

```
Ask: "Optimize my AWS setup to reduce costs by 30%. Current spend: $3000/month"

Provide: Current resource inventory (EC2, RDS, S3, etc.)

Result:
- Idle resource identification
- Right-sizing recommendations
- Savings Plans analysis
- Storage lifecycle policies
- Target savings: $900/month
```

### IaC Generation

```
Ask: "Generate CloudFormation for a three-tier web app with auto-scaling"

Result:
- VPC with public/private subnets
- ALB with HTTPS
- ECS Fargate with auto-scaling
- Aurora with read replicas
- Security groups and IAM roles
```

---

## Input Requirements

Provide these details for architecture design:

| Requirement | Description | Example |
|-------------|-------------|---------|
| Application type | What you're building | SaaS platform, mobile backend |
| Expected scale | Users, requests/sec | 10k users, 100 RPS |
| Budget | Monthly AWS limit | $500/month max |
| Team context | Size, AWS experience | 3 devs, intermediate |
| Compliance | Regulatory needs | HIPAA, GDPR, SOC 2 |
| Availability | Uptime requirements | 99.9% SLA, 1hr RPO |

**JSON Format:**

```json
{
  "application_type": "saas_platform",
  "expected_users": 10000,
  "requests_per_second": 100,
  "budget_monthly_usd": 500,
  "team_size": 3,
  "aws_experience": "intermediate",
  "compliance": ["SOC2"],
  "availability_sla": "99.9%"
}
```

---

## Output Formats

### Architecture Design

- Pattern recommendation with rationale
- Service stack diagram (ASCII)
- Configuration specifications
- Monthly cost estimate
- Scaling characteristics
- Trade-offs and limitations

### IaC Templates

- **CloudFormation YAML**: Production-ready SAM/CFN templates
- **CDK TypeScript**: Type-safe infrastructure code
- **Terraform HCL**: Multi-cloud compatible configs

### Cost Analysis

- Current spend breakdown
- Optimization recommendations with savings
- Priority action list (high/medium/low)
- Implementation checklist

---

## Reference Documentation

| Document | Contents |
|----------|----------|
| `references/architecture_patterns.md` | 6 patterns: serverless, microservices, three-tier, data processing, GraphQL, multi-region |
| `references/service_selection.md` | Decision matrices for compute, database, storage, messaging |
| `references/best_practices.md` | Serverless design, cost optimization, security hardening, scalability |

---

## Limitations

- Lambda: 15-minute execution, 10GB memory max
- API Gateway: 29-second timeout, 10MB payload
- DynamoDB: 400KB item size, eventually consistent by default
- Regional availability varies by service
- Some services have AWS-specific lock-in

---

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| Lambda cold starts exceed 500ms | Function package too large or VPC-attached Lambda without provisioned concurrency | Reduce deployment package size, use Lambda layers, enable provisioned concurrency for latency-sensitive endpoints, or move to Fargate for consistent performance |
| CloudFormation stack stuck in `ROLLBACK_IN_PROGRESS` | Resource creation failed mid-deploy and rollback also failed (e.g., non-empty S3 bucket) | Check CloudFormation events for the root cause, manually delete the blocking resource, then delete the stack; use `DeletionPolicy: Retain` for stateful resources |
| Monthly AWS bill significantly exceeds estimate | Untagged resources, forgotten dev/staging environments, or NAT Gateway data transfer costs | Enable Cost Explorer, set up AWS Budgets with 50%/80%/100% alerts, run `cost_optimizer.py` against current inventory, and audit resources with missing tags |
| DynamoDB throttling errors (ProvisionedThroughputExceededException) | Read/write capacity insufficient for traffic spikes, or hot partition key | Switch to on-demand billing mode, redesign partition key for even distribution, or enable DynamoDB Auto Scaling with appropriate min/max settings |
| API Gateway returns 504 Gateway Timeout | Backend Lambda or integration exceeds the 29-second API Gateway limit | Optimize Lambda execution time, offload long tasks to Step Functions or SQS, increase Lambda memory (which also increases CPU), or use asynchronous invocation patterns |
| Cross-region replication lag causes stale reads | DynamoDB Global Tables or Aurora Global Database replication latency under heavy write load | Design for eventual consistency, route reads to the write-primary region for strong consistency, or use conflict resolution strategies documented in `references/architecture_patterns.md` |
| IAM permission denied errors after deployment | Least-privilege policies missing required actions, or trust policy not updated for new services | Review CloudTrail logs for denied API calls, add the specific missing actions to the IAM policy, and validate with IAM Policy Simulator before deploying |

---

## Success Criteria

- **Cost accuracy**: Monthly AWS bill stays within 10% of the architecture estimate produced by `cost_optimizer.py`.
- **Availability**: Production workloads meet or exceed the target SLA (99.9% uptime for three-tier, 99.95% for multi-region).
- **Recovery time**: RTO under 4 hours and RPO under 1 hour for all production architectures with disaster recovery configured.
- **Deployment speed**: Infrastructure provisioned from generated IaC templates in under 30 minutes for serverless stacks and under 60 minutes for three-tier stacks.
- **Security posture**: Zero critical findings in AWS Security Hub within 30 days of deployment; all resources encrypted at rest and in transit.
- **Scaling response**: Auto-scaling responds to traffic spikes within 2 minutes, handling 10x baseline load without manual intervention.
- **Operational overhead**: Team spends less than 4 hours per week on infrastructure operations after initial deployment.

---

## Scope & Limitations

**This skill covers:**
- AWS architecture design for startups and growth-stage companies (serverless, three-tier, microservices, data pipelines, IoT, multi-region patterns)
- Infrastructure-as-code generation for CloudFormation (SAM), CDK (TypeScript), and Terraform (HCL)
- Cost analysis, right-sizing recommendations, and Savings Plans evaluation
- Service selection guidance for compute, database, storage, networking, and security

**This skill does NOT cover:**
- Multi-cloud or hybrid-cloud architectures (Azure, GCP) -- see `engineering/cloud-migration-specialist/` for cross-cloud strategies
- Application-level code, business logic, or framework-specific implementation -- see `engineering-team/senior-fullstack/` for fullstack development
- Compliance audit execution or regulatory evidence collection -- see `ra-qm-team/` for SOC 2, HIPAA, GDPR, and ISO compliance skills
- AWS account management, organization policies, or billing disputes -- see AWS Support or `engineering-team/ms365-tenant-manager/` for tenant administration patterns

---

## Integration Points

| Skill | Integration | Data Flow |
|-------|-------------|-----------|
| `engineering-team/senior-devops` | CI/CD pipeline configuration for deploying generated IaC templates | Architecture templates flow into DevOps deployment pipelines and monitoring setup |
| `engineering-team/senior-secops` | Security hardening of generated architectures (IAM policies, WAF rules, GuardDuty) | Architecture design feeds into security review; SecOps findings feed back as architecture constraints |
| `ra-qm-team/soc2-compliance` | Compliance validation of AWS architectures against SOC 2 Trust Services Criteria | Architecture resource inventory feeds into compliance audit; audit findings drive architecture changes |
| `engineering-team/senior-backend` | Backend service implementation that runs on the designed AWS infrastructure | Architecture patterns define the runtime environment; backend requirements inform service selection |
| `engineering-team/tech-stack-evaluator` | Technology selection decisions that influence architecture pattern choice | Stack evaluation outputs (database, compute, messaging choices) feed into architecture requirements JSON |
| `c-level-advisor/cto-advisor` | Strategic infrastructure decisions, build-vs-buy, and cloud budget planning | Cost analysis from `cost_optimizer.py` informs CTO budget decisions; CTO constraints flow back as architecture requirements |

---

## Tool Reference

### architecture_designer.py

**Purpose:** Generates architecture pattern recommendations based on application requirements. Analyzes app type, expected scale, budget, team experience, and compliance needs to recommend the optimal AWS architecture pattern with full service configurations and cost estimates.

**Usage:**

```python
from scripts.architecture_designer import ArchitectureDesigner

designer = ArchitectureDesigner(requirements)
pattern = designer.recommend_architecture_pattern()
checklist = designer.generate_service_checklist()
```

**Constructor Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `requirements` | `dict` | Yes | -- | Dictionary containing all application requirements (see fields below) |

**Requirements Dictionary Fields:**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `application_type` | `str` | `"web_application"` | One of: `web_application`, `mobile_backend`, `data_pipeline`, `microservices`, `saas_platform`, `iot_platform` |
| `expected_users` | `int` | `1000` | Expected number of users (or devices for IoT) |
| `requests_per_second` | `int` | `10` | Expected peak requests per second |
| `budget_monthly_usd` | `float` | `500` | Maximum monthly AWS budget in USD |
| `team_size` | `int` | `3` | Number of engineers on the team |
| `aws_experience` | `str` | `"beginner"` | Team AWS experience level |
| `compliance` | `list` | `[]` | List of compliance frameworks (e.g., `["SOC2", "HIPAA"]`) |
| `data_size_gb` | `int` | `10` | Expected data volume in GB |

**Methods:**

| Method | Returns | Description |
|--------|---------|-------------|
| `recommend_architecture_pattern()` | `dict` | Returns recommended pattern with services, cost estimate, pros/cons, and scaling characteristics |
| `generate_service_checklist()` | `list[dict]` | Returns phased implementation checklist (Planning, Foundation, Core Services, Security, Monitoring, CI/CD) |

**Example:**

```python
from scripts.architecture_designer import ArchitectureDesigner

requirements = {
    "application_type": "saas_platform",
    "expected_users": 10000,
    "requests_per_second": 100,
    "budget_monthly_usd": 500,
    "team_size": 3,
    "aws_experience": "intermediate",
    "compliance": ["SOC2"],
    "data_size_gb": 50
}

designer = ArchitectureDesigner(requirements)
result = designer.recommend_architecture_pattern()
print(result['pattern_name'])       # "Serverless Web Application"
print(result['estimated_cost'])     # {"monthly_usd": ..., "breakdown": {...}}
print(result['services'])           # Full service stack with configurations
```

**Output Format:** Returns a dictionary with keys: `pattern_name`, `description`, `use_case`, `services` (nested service configurations), `estimated_cost` (with `monthly_usd` and `breakdown`), `pros`, `cons`, and `scaling_characteristics`.

**Supported Patterns:**
- Serverless Web Application (< 10k users)
- Modern Three-Tier Application (10k-100k users)
- Multi-Region High Availability (100k+ users)
- Serverless Mobile Backend (mobile app type)
- Event-Driven Microservices (microservices type)
- Real-Time Data Pipeline (data pipeline type)
- IoT Platform (IoT type)

---

### serverless_stack.py

**Purpose:** Generates production-ready infrastructure-as-code templates for serverless applications. Produces CloudFormation (SAM), CDK (TypeScript), and Terraform (HCL) configurations with API Gateway, Lambda, DynamoDB, Cognito, IAM roles, and CloudWatch logging preconfigured.

**Usage:**

```python
from scripts.serverless_stack import ServerlessStackGenerator

generator = ServerlessStackGenerator(app_name, requirements)
cfn_template = generator.generate_cloudformation_template()
cdk_stack = generator.generate_cdk_stack()
terraform_config = generator.generate_terraform_configuration()
```

**Constructor Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `app_name` | `str` | Yes | -- | Application name (used for resource naming; auto-lowercased, spaces replaced with hyphens) |
| `requirements` | `dict` | Yes | -- | Dictionary with deployment requirements (see fields below) |

**Requirements Dictionary Fields:**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `region` | `str` | `"us-east-1"` | AWS region for deployment |

**Methods:**

| Method | Returns | Description |
|--------|---------|-------------|
| `generate_cloudformation_template()` | `str` | YAML CloudFormation/SAM template with DynamoDB, Lambda, API Gateway, Cognito, IAM, and CloudWatch |
| `generate_cdk_stack()` | `str` | TypeScript CDK stack with equivalent resources |
| `generate_terraform_configuration()` | `str` | Terraform HCL configuration with equivalent resources |

**Example:**

```python
from scripts.serverless_stack import ServerlessStackGenerator

generator = ServerlessStackGenerator("my-saas-app", {"region": "us-west-2"})

# Generate CloudFormation template
cfn = generator.generate_cloudformation_template()
with open("template.yaml", "w") as f:
    f.write(cfn)

# Generate CDK stack
cdk = generator.generate_cdk_stack()
with open("lib/stack.ts", "w") as f:
    f.write(cdk)

# Generate Terraform config
tf = generator.generate_terraform_configuration()
with open("main.tf", "w") as f:
    f.write(tf)
```

**Output Format:** Each method returns a string containing the full IaC template. Templates include: DynamoDB table (single-table design with PK/SK), Lambda function (Node.js 18.x, 512 MB, 10s timeout), API Gateway (REST, Cognito auth, CORS, throttling), Cognito User Pool (email sign-in, optional MFA), IAM roles (least privilege), and CloudWatch log group (7-day retention). All templates output: API URL, User Pool ID, User Pool Client ID, and Table Name.

---

### cost_optimizer.py

**Purpose:** Analyzes current AWS resource inventory and spending to generate prioritized cost optimization recommendations. Evaluates compute (EC2, Lambda), storage (S3), databases (RDS, DynamoDB), networking (NAT Gateway, VPC endpoints), and general optimizations (CloudWatch Logs, Elastic IPs, budget alerts).

**Usage:**

```python
from scripts.cost_optimizer import CostOptimizer

optimizer = CostOptimizer(current_resources, monthly_spend)
analysis = optimizer.analyze_and_optimize()
checklist = optimizer.generate_optimization_checklist()
```

**Constructor Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `current_resources` | `dict` | Yes | -- | Dictionary describing current AWS resources (see fields below) |
| `monthly_spend` | `float` | Yes | -- | Current monthly AWS spend in USD |

**Resources Dictionary Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `ec2_instances` | `list[dict]` | EC2 instances with `cpu_utilization` (%), `pricing` (`"on-demand"` or `"reserved"`) |
| `lambda_functions` | `list[dict]` | Lambda functions with `memory_mb`, `avg_memory_used_mb` |
| `s3_buckets` | `list[dict]` | S3 buckets with `name`, `size_gb`, `storage_class`, `has_lifecycle_policy` (bool) |
| `rds_instances` | `list[dict]` | RDS instances with `name`, `connections_per_day`, `monthly_cost`, `engine`, `utilization` (%) |
| `dynamodb_tables` | `list[dict]` | DynamoDB tables with `name`, `billing_mode`, `read_capacity_units`, `write_capacity_units`, `utilization_percentage` |
| `nat_gateways` | `list[dict]` | NAT Gateway resources |
| `multi_az_required` | `bool` | Whether multi-AZ NAT is required |
| `vpc_endpoints` | `list` | Existing VPC endpoints |
| `s3_data_transfer_gb` | `float` | Monthly S3 data transfer volume in GB |
| `cloudwatch_log_groups` | `list[dict]` | Log groups with `name`, `retention_days` (`-1` for never expire), `size_gb` |
| `elastic_ips` | `list[dict]` | Elastic IPs with `attached` (bool) |
| `has_budget_alerts` | `bool` | Whether AWS Budgets are configured |
| `has_cost_explorer` | `bool` | Whether Cost Explorer is enabled |

**Methods:**

| Method | Returns | Description |
|--------|---------|-------------|
| `analyze_and_optimize()` | `dict` | Full cost analysis with current spend, potential savings, optimized spend, savings percentage, recommendations list, and top 5 priority actions |
| `generate_optimization_checklist()` | `list[dict]` | Phased action checklist: Immediate (today), This Week, This Month, Ongoing |

**Example:**

```python
from scripts.cost_optimizer import CostOptimizer

resources = {
    "ec2_instances": [
        {"cpu_utilization": 5, "pricing": "on-demand"},
        {"cpu_utilization": 65, "pricing": "on-demand"}
    ],
    "s3_buckets": [
        {"name": "app-assets", "size_gb": 200, "storage_class": "STANDARD", "has_lifecycle_policy": False}
    ],
    "nat_gateways": [{"id": "nat-1"}, {"id": "nat-2"}],
    "multi_az_required": False,
    "has_budget_alerts": False,
    "has_cost_explorer": False
}

optimizer = CostOptimizer(resources, monthly_spend=3000)
result = optimizer.analyze_and_optimize()

print(f"Current spend: ${result['current_monthly_spend']}")
print(f"Potential savings: ${result['potential_monthly_savings']}")
print(f"Savings: {result['savings_percentage']}%")
for rec in result['priority_actions']:
    print(f"  [{rec['priority']}] {rec['service']}: {rec['recommendation']}")
```

**Output Format:** `analyze_and_optimize()` returns a dictionary with keys: `current_monthly_spend` (float), `potential_monthly_savings` (float), `optimized_monthly_spend` (float), `savings_percentage` (float), `recommendations` (list of dicts with `service`, `type`, `issue`, `recommendation`, `potential_savings`, `priority`), and `priority_actions` (top 5 high-priority recommendations sorted by savings).
