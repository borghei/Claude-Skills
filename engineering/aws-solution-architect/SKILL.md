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
  updated: 2026-06-17
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

Before designing the architecture, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **App type & scale** — workload type and expected traffic (selects the pattern: serverless, three-tier, microservices, data-pipeline, or multi-region)
- [ ] **IaC target** — CloudFormation/SAM, CDK, or Terraform (sets the template format `serverless_stack.py` generates)
- [ ] **Budget & compliance constraints** — cost ceiling and any regulatory needs (drive service selection and the cost-optimization recommendations)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Tools

These are Python classes imported from `scripts/` (no CLI). See [references/tool-reference.md](references/tool-reference.md) for full parameters, methods, and examples.

| Tool | Purpose | Usage |
|------|---------|-------|
| `architecture_designer.py` | Recommend a pattern + service stack + cost estimate from requirements | `from scripts.architecture_designer import ArchitectureDesigner` |
| `serverless_stack.py` | Generate CloudFormation / CDK / Terraform serverless templates | `from scripts.serverless_stack import ServerlessStackGenerator` |
| `cost_optimizer.py` | Analyze inventory + spend → prioritized savings recommendations | `from scripts.cost_optimizer import CostOptimizer` |

## References

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
- Multi-cloud or hybrid-cloud architectures (Azure, GCP) -- see `engineering/cloud-migration-specialist/` for cross-cloud strategies
- Application-level code, business logic, or framework-specific implementation -- see `engineering/senior-fullstack/` for fullstack development
- Compliance audit execution or regulatory evidence collection -- see `ra-qm-team/` for SOC 2, HIPAA, GDPR, and ISO compliance skills
- AWS account management, organization policies, or billing disputes -- see AWS Support or `engineering/ms365-tenant-manager/` for tenant administration patterns

## Integration Points

| Skill | Integration | Data Flow |
|-------|-------------|-----------|
| `engineering/senior-devops` | CI/CD pipeline configuration for deploying generated IaC templates | Architecture templates flow into DevOps deployment pipelines and monitoring setup |
| `engineering/senior-secops` | Security hardening of generated architectures (IAM policies, WAF rules, GuardDuty) | Architecture design feeds into security review; SecOps findings feed back as architecture constraints |
| `ra-qm-team/soc2-compliance` | Compliance validation of AWS architectures against SOC 2 Trust Services Criteria | Architecture resource inventory feeds into compliance audit; audit findings drive architecture changes |
| `engineering/senior-backend` | Backend service implementation that runs on the designed AWS infrastructure | Architecture patterns define the runtime environment; backend requirements inform service selection |
| `engineering/tech-stack-evaluator` | Technology selection decisions that influence architecture pattern choice | Stack evaluation outputs (database, compute, messaging choices) feed into architecture requirements JSON |
| `c-level-advisor/cto-advisor` | Strategic infrastructure decisions, build-vs-buy, and cloud budget planning | Cost analysis from `cost_optimizer.py` informs CTO budget decisions; CTO constraints flow back as architecture requirements |
