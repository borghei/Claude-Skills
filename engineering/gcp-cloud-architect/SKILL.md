---
name: gcp-cloud-architect
description: >
  Design, review, and validate Google Cloud (GCP) architectures. Use when choosing GCP
  compute, storage, networking, or identity services, or applying the Google Cloud
  Architecture Framework (reliability, security, cost, performance).
license: MIT + Commons Clause
metadata:
  version: 1.1.0
  author: borghei
  category: engineering
  domain: engineering
  updated: 2026-06-17
  tags: [gcp, google-cloud, architecture, cloud-architecture-framework, gke, cloud-run, bigquery, iam, networking, cost-optimization]
---

# GCP Cloud Architect

End-to-end GCP-specific architecture: service selection, Google Cloud Architecture Framework assessment, identity and networking patterns, cost optimization, operational defaults. Provider-specific complement to our generic `senior-cloud-architect` skill — that one covers cross-cloud patterns; this one knows when to pick Spanner over Cloud SQL, how Workload Identity Federation differs from Service Account keys, and the right Cloud Run vs GKE call.

## Core Capabilities

- **Compute selection** — decision tree across GKE (Autopilot/Standard), Cloud Run, Cloud Functions, Cloud Run Jobs, Batch, Compute Engine, and Vertex AI.
- **Data store selection** — decision tree across Cloud SQL, Spanner, Firestore, Bigtable, Memorystore, Cloud Storage, and BigQuery.
- **Networking** — VPC, Private Service Connect, Interconnect/VPN, load-balancer choices, Shared VPC, peering, Cloud Armor, hub-and-spoke.
- **Identity** — IAM, Service Accounts, Workload Identity (GKE) and Workload Identity Federation, ADC, and least-privilege role/scope binding.
- **CAF assessment** — score workloads against the five Cloud Architecture Framework pillars.
- **Cost optimization** — biggest-to-smallest cost levers (right-sizing, CUDs/SUDs, autoscaling, preemptibles, tiering, slots) and cost anti-patterns.
- **Workflows** — design a new workload, review an existing architecture, and migrate from AWS/Azure to GCP.

## When to Use

| Situation | Skill applies |
|-----------|---------------|
| Designing a GCP architecture from scratch | Yes — start with **compute decision tree** |
| Reviewing an existing GCP architecture | Yes — run **CAF assessment** via `scripts/gcp_caf_scorer.py` |
| Validating a Terraform / Deployment Manager plan | Yes — `scripts/gcp_architecture_validator.py` |
| Estimating GCP cost for a workload | Yes — `scripts/gcp_cost_estimator.py` |
| Picking between GKE / Cloud Run / Functions / Cloud Run Jobs | Yes — see **compute decision tree** |
| Setting up IAM / Workload Identity correctly | Yes — see **identity reference** |
| Designing multi-region / multi-zone resilience | Yes — see **reliability reference** |
| Picking Cloud SQL vs Spanner vs Firestore vs BigQuery | Yes — see **data store decision tree** |
| Going to production without CAF review | Don't — run the CAF scorer first |

## Clarify First

Before designing or assessing, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Task** — design from scratch, review an existing architecture, validate IaC, or estimate cost (selects `gcp_architecture_validator.py` vs `gcp_cost_estimator.py` vs `gcp_caf_scorer.py`)
- [ ] **Workload spec** — the YAML workload config, or the Terraform/Deployment Manager files (the input the scripts parse)
- [ ] **Priority pillar** — reliability, security, cost, operational excellence, or performance (weights the CAF assessment and which recommendations lead)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Tools

| Tool | Purpose | Command |
|------|---------|---------|
| `gcp_architecture_validator.py` | Validate a Terraform plan or YAML workload spec for anti-patterns | `python scripts/gcp_architecture_validator.py --terraform ./infra/*.tf` |
| `gcp_cost_estimator.py` | Estimate monthly GCP cost from a workload spec, with optimization opportunities | `python scripts/gcp_cost_estimator.py --workload-config workload.yaml` |
| `gcp_caf_scorer.py` | Score a workload against the five Cloud Architecture Framework pillars | `python scripts/gcp_caf_scorer.py --workload-config workload.yaml` |

## References

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/decision-trees.md](references/decision-trees.md)** — the full compute decision tree and the data store decision tree. Read when selecting compute or storage.
- **[references/networking-and-identity.md](references/networking-and-identity.md)** — VPC/PSC/Interconnect building blocks, the load-balancer matrix, common networking patterns, and the IAM / Service Account / Workload Identity (Federation) patterns with least-privilege guidance. Read when designing networking or identity.
- **[references/caf-cost-and-workflows.md](references/caf-cost-and-workflows.md)** — the five CAF pillars, the cost-lever and cost-anti-pattern catalog, all three end-to-end workflows (design/review/migrate), the GCP-specific anti-patterns, and the script tooling-output table. Read when assessing, optimizing, or running a workflow.
- **[references/gcp-services-reference.md](references/gcp-services-reference.md)** — per-service depth: tiers, SLAs, limits, when to upgrade. Read when sizing a specific service.
- **[references/gcp-well-architected.md](references/gcp-well-architected.md)** — the 5-pillar CAF assessment with a 10-question checklist per pillar, common findings, and remediation patterns. Read during a CAF review.
- **[references/gcp-cost-optimization.md](references/gcp-cost-optimization.md)** — the full cost-lever catalog, anti-patterns, and detection heuristics. Read when driving down spend.

## Related skills

- `engineering/senior-cloud-architect` — generic multi-cloud architecture patterns
- `engineering/aws-solution-architect` — AWS counterpart
- `engineering/azure-cloud-architect` — Azure counterpart
- `engineering/kubernetes-operator` — for GKE operator-pattern workloads
- `ra-qm-team/information-security-manager-iso27001` — compliance-mapped controls (GCP has Security Command Center)
- `ra-qm-team/soc2-compliance-expert` — GCP-specific SOC 2 evidence collection
