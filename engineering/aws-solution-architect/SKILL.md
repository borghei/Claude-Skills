---
name: aws-solution-architect
description: >
  Design AWS serverless architectures for startups with IaC. Use when designing serverless
  architecture, writing CloudFormation, optimizing AWS costs, setting up CI/CD, or migrating
  to AWS across Lambda, API Gateway, and DynamoDB.
license: MIT + Commons Clause
metadata:
  version: 1.1.0
  author: borghei
  category: engineering
  domain: cloud-architecture
  updated: 2026-11-08
  tags: [aws, serverless, cloudformation, cost-optimization]
---
# AWS Solution Architect

Design scalable, cost-effective AWS architectures for startups with infrastructure-as-code templates — recommend the right pattern, generate CloudFormation/CDK/Terraform, and optimize spend.

## Core Capabilities

- **Architecture design** — recommend serverless, three-tier, microservices, data-pipeline, GraphQL, IoT, or multi-region patterns from app type, scale, budget, and compliance needs.
- **IaC generation** — produce production-ready CloudFormation (SAM), CDK (TypeScript), and Terraform (HCL) with API Gateway, Lambda, DynamoDB, Cognito, IAM least-privilege, and CloudWatch.
- **Cost optimization** — analyze inventory for idle resources, right-sizing, Savings Plans, storage tiering, and NAT Gateway alternatives with prioritized savings.
- **Service selection** — decision matrices for compute, database, storage, networking, and security.
- **Operational excellence** — monitoring, alarming, disaster recovery (RTO/RPO), and security hardening.

## When to Use

- Designing serverless / three-tier / microservices / data-pipeline / multi-region AWS architecture.
- Writing or generating CloudFormation, CDK, or Terraform infrastructure-as-code.
- Reducing AWS costs, right-sizing, or evaluating Savings Plans / Reserved capacity.
- Selecting AWS services (Lambda, API Gateway, DynamoDB, Aurora, ECS/Fargate, EventBridge, AppSync).
- Setting up CI/CD (CodePipeline, CodeBuild) or migrating workloads to AWS.
- Hardening IAM, VPC, encryption, Cognito, WAF, or planning monitoring (CloudWatch, X-Ray).

## Clarify First

Before designing the architecture, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **App type & scale:** workload type and expected traffic (selects the pattern: serverless, three-tier, microservices, data-pipeline, or multi-region).
- **IaC target:** CloudFormation/SAM, CDK, or Terraform (sets the template format `serverless_stack.py` generates).
- **Budget & compliance constraints:** cost ceiling and any regulatory needs (drive service selection and the cost-optimization recommendations).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Quick Start Workflow

Each script is a command-line tool and an importable class. Every CLI prints an input template
with `--example` and supports `--format json`. Full parameters:
[references/tool-reference.md](references/tool-reference.md).

```bash
# 1. Pattern, service stack and rough monthly cost from requirements
python scripts/architecture_designer.py --input assets/sample_input.json          # Modern Three-Tier
python scripts/architecture_designer.py --input assets/sample_input.json --format json   # = assets/expected_output.json

# 2. Serverless IaC skeleton (SAM, CDK TypeScript or Terraform)
python scripts/serverless_stack.py --app-name orders-api --region eu-west-1 --format terraform --output /tmp/main.tf

# 3. Savings from a resource inventory and current spend
python scripts/cost_optimizer.py --resources assets/sample_resources.json --monthly-spend 2000
```

## Tools Overview

| Tool | Purpose | Notes |
|------|---------|-------|
| `architecture_designer.py` | Recommend a pattern + service stack + cost estimate from requirements | `--example` prints the requirements fields |
| `serverless_stack.py` | Generate CloudFormation (SAM) / CDK / Terraform serverless templates | `--app-name` must be lowercase letters, digits and hyphens; `--region` must look like `us-east-1` |
| `cost_optimizer.py` | Analyze inventory + spend into prioritized savings recommendations | `--example` prints the inventory shape |

**Exit codes (all three):** `0` output written; `2` missing or invalid input file, invalid
`--app-name` or `--region`. They are advisory: a costly design still exits 0.

Cost figures are rough list-price ranges for comparing options, not a quote; price the final
design in the AWS Pricing Calculator.

**Done when:**
1. The chosen pattern is justified against the requirements (traffic, data, team skills, budget), not only the designer's pick.
2. The generated template deploys to a sandbox account (`sam deploy`, `cdk deploy` or `terraform apply`) and is torn down cleanly.
3. IAM is least-privilege, data stores are encrypted and private, and budgets with alerts exist.
4. The monthly cost was checked in the AWS Pricing Calculator.

## Anti-Patterns

### Kubernetes for a three-person team
**Mistake:** Starting on EKS with service meshes for an MVP with a few thousand users.
**Why it happens:** It matches what large companies run.
**Instead:** Start serverless or with ECS Fargate and move only when a measured constraint demands it. Operating a cluster costs more than the compute.

### Templates straight to production
**Mistake:** Deploying the generated template into the production account unchanged.
**Why it happens:** It validates, so it looks finished.
**Instead:** Treat it as a skeleton: review IAM, add alarms and backups, deploy to a sandbox first.

### Cost estimate as budget
**Mistake:** Quoting the designer's monthly figure to finance.
**Why it happens:** A single number is easy to pass on.
**Instead:** Use it to compare patterns; budget from the Pricing Calculator with your real traffic, data transfer and Savings Plans.

## Files

- `scripts/architecture_designer.py`, `scripts/serverless_stack.py`, `scripts/cost_optimizer.py` — the three CLIs above.
- `assets/sample_input.json` and `assets/expected_output.json` (designer input and its JSON output), `assets/sample_resources.json` (optimizer input).
- `references/` — workflow, patterns, service selection, best practices, tool reference.

## Reference Documentation

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/workflow-and-usage.md](references/workflow-and-usage.md)** — the 6-step design→deploy→validate workflow, quick-start scenarios (MVP, scaling, cost optimization, IaC), input-requirements JSON, and output formats. Read when running an end-to-end design.
- **[references/architecture_patterns.md](references/architecture_patterns.md)** — the 6 detailed patterns (serverless, microservices, three-tier, data processing, GraphQL, multi-region) with full service specs. Read when selecting and designing a pattern.
- **[references/service_selection.md](references/service_selection.md)** — decision matrices for compute, database, storage, and messaging. Read when choosing between AWS services.
- **[references/best_practices.md](references/best_practices.md)** — serverless design, cost optimization, security hardening, scalability, plus service limitations, troubleshooting, and success criteria. Read before shipping an architecture.
- **[references/tool-reference.md](references/tool-reference.md)** — full Python API (constructors, methods, requirement/resource dictionaries, examples) for the three tools. Read when invoking the tools programmatically.

## Scope & Limitations

**This skill covers:**
- AWS architecture design for startups and growth-stage companies (serverless, three-tier, microservices, data pipelines, IoT, multi-region patterns)
- Infrastructure-as-code generation for CloudFormation (SAM), CDK (TypeScript), and Terraform (HCL)
- Cost analysis, right-sizing recommendations, and Savings Plans evaluation
- Service selection guidance for compute, database, storage, networking, and security

**This skill does NOT cover:**
- Multi-cloud or hybrid-cloud architectures -- see `engineering/senior-cloud-architect/`, `engineering/azure-cloud-architect/` and `engineering/gcp-cloud-architect/`
- Application-level code, business logic, or framework-specific implementation -- see `engineering/senior-fullstack/` for fullstack development
- Compliance audit execution or regulatory evidence collection -- see `ra-qm-team/` for SOC 2, HIPAA, GDPR, and ISO compliance skills
- AWS account management, organization policies, or billing disputes -- see AWS Support

## Integration Points

| Skill | Integration | Data Flow |
|-------|-------------|-----------|
| `engineering/senior-devops` | CI/CD pipeline configuration for deploying generated IaC templates | Architecture templates flow into DevOps deployment pipelines and monitoring setup |
| `engineering/senior-secops` | Security hardening of generated architectures (IAM policies, WAF rules, GuardDuty) | Architecture design feeds into security review; SecOps findings feed back as architecture constraints |
| `ra-qm-team/soc2-compliance-expert` | Compliance validation of AWS architectures against SOC 2 Trust Services Criteria | Architecture resource inventory feeds into compliance audit; audit findings drive architecture changes |
| `engineering/senior-backend` | Backend service implementation that runs on the designed AWS infrastructure | Architecture patterns define the runtime environment; backend requirements inform service selection |
| `engineering/tech-stack-evaluator` | Technology selection decisions that influence architecture pattern choice | Stack evaluation outputs (database, compute, messaging choices) feed into architecture requirements JSON |
| `c-level-advisor/cto-advisor` | Strategic infrastructure decisions, build-vs-buy, and cloud budget planning | Cost analysis from `cost_optimizer.py` informs CTO budget decisions; CTO constraints flow back as architecture requirements |
