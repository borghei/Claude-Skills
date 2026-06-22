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
| Validating an ARM/Bicep/Terraform plan | Yes — `scripts/azure_architecture_validator.py` |
| Estimating Azure cost for a workload | Yes — `scripts/azure_cost_estimator.py` |
| Picking compute, data store, networking, or identity | Yes — see the decision-trees reference |
| Going to production without WAF review | Don't — run the WAF scorer first |

## Clarify First

Before designing or assessing, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Task** — design from scratch, review an existing architecture, validate IaC, or estimate cost (selects `azure_architecture_validator.py` vs `azure_cost_estimator.py` vs `azure_waf_scorer.py`)
- [ ] **Workload spec** — the YAML workload config, or the Bicep/ARM/Terraform files (the input the scripts parse)
- [ ] **Priority pillar** — reliability, security, cost, operational excellence, or performance (weights the WAF assessment and which recommendations lead)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Tools

| Tool | Purpose | Command |
|------|---------|---------|
| `azure_architecture_validator.py` | Validate a Bicep/ARM/YAML workload for anti-patterns and missing best-practice settings | `python scripts/azure_architecture_validator.py --bicep ./infra/*.bicep` |
| `azure_cost_estimator.py` | Estimate monthly Azure cost from a YAML workload spec | `python scripts/azure_cost_estimator.py --workload-config workload.yaml` |
| `azure_waf_scorer.py` | Score a workload against the five Well-Architected pillars | `python scripts/azure_waf_scorer.py --workload-config workload.yaml` |

All scripts: stdlib only, argparse CLI, JSON or markdown output (`--format`).

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
