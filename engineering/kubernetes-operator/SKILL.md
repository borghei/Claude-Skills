---
name: kubernetes-operator
description: >
  Design, build, and operate Kubernetes operators. Use when extending Kubernetes with a custom
  controller, choosing a framework, designing CRDs, implementing reconciliation loops, or
  auditing an operator for anti-patterns.
license: MIT + Commons Clause
metadata:
  version: 1.1.0
  author: borghei
  category: engineering
  domain: engineering
  updated: 2026-06-17
  tags: [kubernetes, operator-pattern, crd, controller-runtime, kubebuilder, platform-engineering, sre]
---

# Kubernetes Operator

End-to-end Kubernetes operator design and construction. Covers the operator pattern (control loops for stateful workloads), CRD design (schema, validation, conversion, status), the reconciliation loop (idempotency, convergence, level- vs edge-triggered), framework selection (controller-runtime / Kubebuilder / operator-SDK / metacontroller), and operational concerns (finalizers, leader election, RBAC scoping, status subresource, observability). Targets Go-based operators (the dominant ecosystem) with notes on alternatives (KOPF, JOSDK, kube-rs).

## Core Capabilities

- **Decide whether to write an operator** — operator vs Helm vs GitOps vs admission webhook vs Crossplane, and when NOT to build one at all.
- **CRD design** — spec/status separation, OpenAPI v3 structural schemas, CEL cross-field validation, versioning, conversion webhooks, status subresource, printer columns, scale subresource.
- **Reconciliation loops** — idempotent, level-triggered, converging control loops; phase machines vs always-converge; owner references and garbage collection.
- **Controller-runtime patterns (Go)** — skeleton reconcilers, server-side apply, finalizers, leader election, watches/predicates/indexers, error classification, envtest.
- **Framework selection** — controller-runtime, Kubebuilder, operator-SDK, Metacontroller, KOPF, JOSDK, kube-rs.
- **Operational hardening** — finalizers, leader election, tightened RBAC, status conditions/observedGeneration, Prometheus metrics + structured logging.
- **Anti-pattern audit** — 24-entry catalog with severities, detection heuristics, and fixes for production-readiness review.

## When to Use

| Situation | Skill applies |
|-----------|---------------|
| Building a new operator for an internal platform primitive | Yes — start with the **operator pattern decision** |
| Auditing an existing operator for production-readiness | Yes — use **anti-patterns** + `scripts/reconciliation_audit.py` |
| Designing CRDs for a custom resource | Yes — use **CRD design** + `scripts/crd_validator.py` |
| Deciding "operator vs Helm chart vs plain manifests" | Yes — use the decision matrix |
| Scaffolding a new operator project | Yes — `scripts/operator_scaffold.py` |
| Debugging a controller that "isn't reconciling" | Yes — use **reconciliation troubleshooting** |
| Just running someone else's operator (Postgres, Kafka, etc.) | Partially — useful for understanding what it does and how to monitor it |

## Clarify First

Before scaffolding or auditing, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Task** — scaffold an operator, validate a CRD, or audit a controller (selects `operator_scaffold.py` vs `crd_validator.py` vs `reconciliation_audit.py`)
- [ ] **Resource identity** — for scaffolding: the operator name, API group, and kind (sets `--name`/`--group`/`--kind`); for validation/audit: the CRD YAML or controller path (the input the scripts read)
- [ ] **Framework** — controller-runtime/Kubebuilder/operator-SDK (Go), or KOPF/JOSDK/kube-rs (drives the scaffold patterns)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Tools

| Tool | Purpose | Command |
|------|---------|---------|
| `crd_validator.py` | Validate CRD YAML against design best practices (preserve-unknown, missing descriptions/enums/printer-columns, status subresource, cluster-scope) | `python3 scripts/crd_validator.py --schema my-crd.yaml --format markdown` |
| `operator_scaffold.py` | Generate a production-ready operator project skeleton with stricter RBAC, observability, and finalizer scaffolding | `python3 scripts/operator_scaffold.py --name db-operator --group example.com --kind Database` |
| `reconciliation_audit.py` | Audit Go controller source + CRDs for static-detectable anti-patterns (missing finalizers, no leader election, tight loops, no ownerRef, wide RBAC) | `python3 scripts/reconciliation_audit.py --controller-path ./internal/controllers --crd ./config/crd/bases/*.yaml` |

All scripts: stdlib only, argparse CLI, JSON or markdown output.

## References

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/operator-pattern-and-crds.md](references/operator-pattern-and-crds.md)** — pattern fundamentals, full CRD schema design (validation, CEL, status patterns), versioning, conversion webhooks, status/scale subresources, printer columns, RBAC, and a production-CRD checklist. Read when designing or reviewing a CRD.
- **[references/controller-runtime-patterns.md](references/controller-runtime-patterns.md)** — Go controller-runtime examples: skeleton reconciler, idempotent apply, owner refs, status updates, finalizers, leader election, watches/predicates/indexers, error handling, RBAC markers, envtest, plus the reconciliation-loop overview and operational concerns. Read when implementing or debugging a controller.
- **[references/operator-anti-patterns.md](references/operator-anti-patterns.md)** — the full 24-entry anti-pattern catalog with severity, symptoms, consequences, fixes, a static-detection summary, and symptom-based triage. Read during design review, code review, or pre-production audit.
- **[references/operator-decisions-and-workflows.md](references/operator-decisions-and-workflows.md)** — when NOT to write an operator, operator-vs-alternatives decision matrix, framework selection, the four end-to-end workflows (scaffold / audit / design CRD / upgrade versions), and tooling outputs. Read when deciding the approach or running a workflow.

## Scope & Limitations

**Covers:** operator pattern decisions; CRD design (schema/validation/versioning/conversion/subresources); idempotent reconciliation loops; Go controller-runtime / Kubebuilder / operator-SDK patterns; finalizers, leader election, RBAC scoping, observability; anti-pattern auditing. Primary target is Go operators, with notes on KOPF (Python), JOSDK (Java), kube-rs (Rust).

**Does NOT cover:** operating third-party community operators beyond understanding/monitoring them; cloud-provider-specific resource provisioning (see Crossplane); general Kubernetes cluster administration.

## Integration Points

| Skill | Integration |
|-------|------------|
| `engineering/chaos-engineering` | Chaos-test operators (kill the controller, partition from API server) |
| `engineering/observability-designer` | Wire metrics + logging for operators |
| `engineering/incident-commander` | Operators amplify blast radius; incident response matters more |
| `engineering/feature-flags-architect` | Operators with `spec.feature.<x>.enabled` fields effectively become flag systems; consider the trade-off |
