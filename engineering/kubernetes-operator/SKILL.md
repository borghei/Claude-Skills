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
  updated: 2026-11-08
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

Before scaffolding or auditing, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Task:** scaffold an operator, validate a CRD, or audit a controller (selects `operator_scaffold.py` vs `crd_validator.py` vs `reconciliation_audit.py`).
- **Resource identity:** for scaffolding: the operator name, API group, and kind (sets `--name`/`--group`/`--kind`); for validation/audit: the CRD YAML or controller path (the input the scripts read).
- **Framework:** controller-runtime/Kubebuilder/operator-SDK (Go), or KOPF/JOSDK/kube-rs (drives the scaffold patterns).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Workflow

1. **Decide whether to build one.** Use the decision matrix in [references/operator-decisions-and-workflows.md](references/operator-decisions-and-workflows.md); a Helm chart, GitOps or an admission policy is often enough.
2. **Design the CRD** (spec/status split, structural schema, CEL rules, status subresource, printer columns) and check it with `crd_validator.py`.
3. **Scaffold** with `operator_scaffold.py`, then `go mod tidy` (resolves current controller-runtime and k8s.io versions) and `make generate manifests build` (controller-gen writes DeepCopy methods, CRDs and RBAC). Kubebuilder (`kubebuilder init` / `create api`) is the fuller alternative when you want its project layout, webhooks and test harness.
4. **Implement** the reconciler: idempotent, level-triggered, owner references on children, finalizers for external resources, `observedGeneration` and conditions in status.
5. **Audit** with `reconciliation_audit.py` against the controller source and CRDs; fix every critical finding.
6. **Verify** with envtest or a kind cluster: create, update and delete the resource; kill the controller mid-reconcile and confirm it converges; run two replicas with leader election on.

## Quick Start

```bash
python3 scripts/crd_validator.py --schema assets/sample_crd_weak.yaml                            # no status subresource, untyped spec (exit 1)
python3 scripts/reconciliation_audit.py --controller-path assets --crd assets/sample_crd_weak.yaml  # missing finalizer/ownerRef, wildcard RBAC ... (exit 1)
python3 scripts/operator_scaffold.py --name db-operator --group example.com --kind Database --out "$(mktemp -d)/db-operator"
```

Then, in the scaffolded project:

```bash
go mod tidy && make generate manifests build
python3 <skill>/scripts/reconciliation_audit.py --controller-path . --crd config/crd/bases/*.yaml   # 0 findings (exit 0)
```

## Tools Overview

| Tool | What it does | Key flags | Exit codes |
|------|--------------|-----------|------------|
| `crd_validator.py` | CRD design checks: status subresource, structural schema (root or spec preserve-unknown-fields), descriptions, enums, printer columns, observedGeneration/conditions, storage versions and conversion, cluster scope, categories, shortNames | `--schema <files/globs>`, `--severity`, `--format markdown|json` | 0 no critical, 1 critical finding, 2 unreadable file or no CRD |
| `operator_scaffold.py` | controller-runtime skeleton: go.mod (versions resolved by `go mod tidy`), Makefile with controller-gen targets, main.go with leader election flag, health and metrics, typed API, reconciler with finalizer and status handling, Dockerfile, Deployment, README | `--name`, `--group`, `--kind`, `--scope`, `--out`, `--go-module`, `--namespace`, `--categories` | 0, 2 output directory not empty |
| `reconciliation_audit.py` | Static checks on Go controllers and CRDs: creates without finalizer, no owner reference, tight error requeue, status/spec mixing, hard-coded namespace, wildcard RBAC, no observedGeneration, manager without leader election | `--controller-path`, `--crd`, `--severity`, `--format` | 0 no critical, 1 critical finding, 2 bad path |

The scaffold targets Go 1.27 (go.mod and the Dockerfile's `GO_VERSION` agree; keep them in step). To confirm it builds in your environment, run `go mod tidy && make generate manifests build` in the generated project: it must finish without errors and write `bin/manager` and `config/crd/bases/*.yaml`. It is a starting skeleton, not a finished operator. The audit is pattern-based: it cannot see dynamic dispatch or code generated elsewhere, so pair it with envtest.

## Anti-Patterns

**Mistake:** Writing an operator for something a Helm chart already handles.
**Why it happens:** Operators feel like the "proper" Kubernetes way.
**Instead:** Build one only when you need a control loop over live state (failover, backups, upgrades). Every operator is a service you have to run.

**Mistake:** Edge-triggered logic ("on create, do X").
**Why it happens:** Events look like the natural trigger.
**Instead:** Reconcile from current state every time; events are dropped and replayed, so the loop must converge from any starting point.

**Mistake:** Returning every error to the work queue.
**Why it happens:** It is the default pattern in tutorials.
**Instead:** Separate permanent errors (bad spec: record a condition, return nil) from transient ones (requeue with backoff), or a bad object spins forever.

## Files

- `scripts/crd_validator.py`, `scripts/operator_scaffold.py`, `scripts/reconciliation_audit.py` — the tools above.
- `assets/sample_crd_weak.yaml` (flawed CRD), `assets/sample_controller_flawed.go` (flawed reconciler).

## Reference Documentation

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
