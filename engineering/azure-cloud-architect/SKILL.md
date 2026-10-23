---
name: azure-cloud-architect
description: >
  Design, review, and validate Azure cloud architectures. Use when choosing Azure
  compute, storage, networking, or identity services, or applying the Azure
  Well-Architected Framework to a workload.
license: MIT + Commons Clause
metadata:
  version: 1.1.0
  author: borghei
  category: engineering
  domain: engineering
  updated: 2026-06-17
  tags: [azure, cloud-architecture, well-architected-framework, aks, app-service, entra-id, networking, cost-optimization]
---

# Azure Cloud Architect

End-to-end Azure-specific architecture: service selection, Well-Architected Framework assessment, identity and networking patterns, cost optimization, and operational defaults. Provider-specific complement to our generic `senior-cloud-architect` skill — that one covers cross-cloud patterns; this one knows AKS pricing tiers, when to pick Cosmos over SQL DB, and how Front Door differs from Application Gateway.

## Core Capabilities

- **Compute selection** — decision tree across AKS, App Service, Container Apps, Functions, VMs/VMSS, Batch, Static Web Apps, and API gateways.
- **Data store selection** — relational, NoSQL/document, cache, blob, time-series, search, vector, and warehouse decision trees.
- **Networking design** — VNets, Private/Service Endpoints, gateways (App Gateway, Front Door, Firewall, NAT, VPN/ER), hub-and-spoke and Private Link patterns.
- **Identity design** — Entra ID, Managed Identity (system/user-assigned), Workload Identity, Service Principals, and least-privilege RBAC scoping.
- **WAF assessment** — score workloads across Reliability, Security, Cost, Operational Excellence, and Performance Efficiency pillars.
- **Cost optimization** — right-sizing, reservations, autoscaling, spot, storage tiering, and egress-reduction levers with anti-pattern detection.

## When to Use

| Situation | Skill applies |
|-----------|---------------|
| Designing an Azure architecture from scratch | Yes — start with the **compute decision tree** |
| Reviewing an existing Azure architecture | Yes — run **WAF assessment** via `scripts/azure_waf_scorer.py` |
| Validating a Bicep template or a YAML workload spec | Yes — `scripts/azure_architecture_validator.py` (ARM JSON and Terraform are not checked) |
| Estimating Azure cost for a workload | Yes — `scripts/azure_cost_estimator.py` |
| Picking compute, data store, networking, or identity | Yes — see the decision-trees reference |
| Going to production without WAF review | Don't — run the WAF scorer first |

## Clarify First

Before designing or assessing, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Task:** design from scratch, review an existing architecture, validate IaC, or estimate cost (selects `azure_architecture_validator.py` vs `azure_cost_estimator.py` vs `azure_waf_scorer.py`).
- **Workload spec:** the YAML workload config, or the Bicep files (the input the scripts parse). ARM JSON templates and Terraform are not checked; for Terraform, describe the workload in the YAML spec instead.
- **Priority pillar:** reliability, security, cost, operational excellence, or performance (weights the WAF assessment and which recommendations lead).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Tools

| Tool | Purpose | Command |
|------|---------|---------|
| `azure_architecture_validator.py` | Validate a Bicep or YAML workload for anti-patterns and missing best-practice settings | `python scripts/azure_architecture_validator.py --bicep ./infra/*.bicep` |
| `azure_cost_estimator.py` | Estimate monthly Azure cost from a YAML workload spec | `python scripts/azure_cost_estimator.py --workload-config workload.yaml` |
| `azure_waf_scorer.py` | Score a workload against the five Well-Architected pillars | `python scripts/azure_waf_scorer.py --workload-config workload.yaml` |

All scripts: stdlib only, argparse CLI, JSON or markdown output (`--format`).

## Scope & Limitations

**In Scope:**
- Azure service selection through decision trees for compute, data stores, networking and identity
- Well-Architected Framework scoring with `azure_waf_scorer.py`: five pillars, ten checks each, read from a YAML workload spec
- Anti-pattern checks with `azure_architecture_validator.py` on a YAML workload spec or Bicep files: public endpoints, shared keys instead of Managed Identity, single-AZ tier-1, wide RBAC scopes, missing diagnostics and locks, and credentials in parameters
- Rough monthly cost estimates with `azure_cost_estimator.py` from a YAML workload spec, with prioritized optimization suggestions

**Out of Scope:**
- Cross-cloud patterns and the AWS and GCP equivalents (see `engineering/senior-cloud-architect/`, `engineering/aws-solution-architect/` and `engineering/gcp-cloud-architect/`)
- Writing or reviewing Terraform modules (see `engineering/terraform-patterns/`)
- Security posture audits of an exported cloud inventory and IAM (see `engineering/cloud-security/`)
- Kubernetes operator design for AKS workloads (see `engineering/kubernetes-operator/`)
- Compliance evidence and control mapping (see `ra-qm-team/soc2-compliance-expert/` and `ra-qm-team/information-security-manager-iso27001/`)

**Important Caveats:**
- The scripts never call Azure. They read files the user provides, and the WAF score reflects what the YAML spec declares, not what is deployed.
- The validator scans Bicep text with pattern rules; its rules do not match ARM JSON syntax, so ARM templates pass without findings. It does not compile templates or resolve modules and parameters, and it does not read Terraform.
- Cost figures come from a built-in table of approximate list prices from early 2026, with no reservation or savings-plan discounts. They are for relative comparison, not a quote; check the Azure Pricing Calculator before budgeting.
- Service tiers, SLAs, limits and prices in the references change often and should be confirmed against current Azure documentation.

## References

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/azure-decision-trees.md](references/azure-decision-trees.md)** — full compute, data store, networking, and identity decision trees with building-block, gateway, and RBAC tables. Read when selecting services or designing topology.
- **[references/azure-workflows-and-antipatterns.md](references/azure-workflows-and-antipatterns.md)** — the five WAF pillars, cost levers and anti-patterns, the design/review/migrate workflows, Azure-specific anti-patterns, and tooling outputs. Read when running a design or review.
- **[references/azure-services-reference.md](references/azure-services-reference.md)** — per-service depth: tiers, SLAs, limits, when to upgrade. Read when choosing a specific SKU or tier.
- **[references/azure-well-architected.md](references/azure-well-architected.md)** — 5-pillar WAF assessment with the 10-question checklist per pillar, common findings, and remediations. Read during a WAF review.
- **[references/azure-cost-optimization.md](references/azure-cost-optimization.md)** — full cost lever catalog, anti-patterns, and detection heuristics. Read when optimizing spend.

## Related skills

- `engineering/senior-cloud-architect` — generic multi-cloud architecture patterns
- `engineering/aws-solution-architect` — AWS counterpart
- `engineering/gcp-cloud-architect` — GCP counterpart
- `engineering/kubernetes-operator` — for AKS operator-pattern workloads
- `ra-qm-team/information-security-manager-iso27001` — for compliance-mapped controls (Azure has built-in Defender / Compliance Manager)
- `ra-qm-team/soc2-compliance-expert` — Azure-specific SOC 2 evidence collection
