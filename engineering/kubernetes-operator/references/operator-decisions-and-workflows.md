# Operator Decisions and Workflows

Read this when deciding whether to write an operator at all, choosing a framework, picking operator vs. alternatives, or running an end-to-end operator workflow (scaffold, audit, design a CRD, upgrade CRD versions). Also documents the script tooling outputs.

---

## When NOT to write an operator

Operators are extensions of Kubernetes. They cost ongoing maintenance, RBAC review, security audit, version-skew handling, and (often) a dedicated SRE rotation. Avoid if:

- Your resource is **stateless** and fits CronJob + Deployment + ConfigMap (no extra control loop needed)
- You can model the workload as a Helm chart with values overrides
- An existing community operator (CNCF / vendor) covers your needs — adopt it instead
- The lifecycle has < 5 transitions (then a Job + readiness probe is simpler)
- You'd be the only consumer (consider a less heavyweight extension point — admission webhook, Lua/JSONNet, GitOps controller config)

A useful rule: write an operator only when the resource has at least 2-3 non-trivial state transitions AND existing primitives can't model them cleanly.

---

## The operator pattern in one paragraph

An operator is a **controller** (Kubernetes control-loop program) that watches **CustomResources** (CRs) representing application-specific state, and drives the cluster toward the **desired state** declared in the CR's spec, recording **observed state** in the CR's status. The pattern: a domain expert encodes operational knowledge as software — "when CR X is created, do A; when X.spec.replicas changes, do B; when underlying Pod fails, do C" — so users get a declarative API instead of a wiki of runbooks.

Three building blocks:

1. **CRD** (CustomResourceDefinition) — schema for the new resource type
2. **Controller** — control loop that reconciles spec → state
3. **Custom Resource** (CR) — instances users create to ask for things

---

## Operator vs alternatives — decision matrix

| Need | Use |
|------|-----|
| Run a stateless app | Deployment + Service |
| Run a stateful app with simple lifecycle | StatefulSet + headless Service |
| Manage configuration drift | Argo CD / Flux (GitOps controllers) |
| Add validation/mutation to existing K8s API | Admission webhook (no operator) |
| Manage external resources from inside cluster | Operator (if non-trivial), OR Crossplane (if matches its model) |
| Automate complex stateful workloads with domain expertise | **Operator** |
| Multi-cluster federation | Operator + push to other clusters (e.g., Karmada, KubeFed) |
| Simple "do X on YAML change" | Metacontroller (declarative composition, no Go) |

---

## Framework selection

The three dominant Go frameworks (and others):

| Framework | Use when | Skip when |
|-----------|----------|-----------|
| **controller-runtime** | You want full control; building a complex multi-controller operator; library, not framework | You want batteries-included scaffolding |
| **Kubebuilder** | Greenfield operator; want scaffolding, conventions, makefile, CI templates | You don't want code generation in your repo |
| **operator-SDK** | Came from Operator Lifecycle Manager world; want OLM packaging | OLM isn't your target |
| **Metacontroller** | Operator logic fits a simple "given parent + children YAML → output YAML" model, written in any language | You need fine-grained control or complex state |
| **KOPF (Python)** | Team is Python-first; operator is mostly orchestration, not perf-critical | Need maximum K8s API surface |
| **JOSDK (Java)** | Team is Java-first; integrating with Java ecosystem libs | Same as above |
| **kube-rs (Rust)** | Team is Rust-first; perf or reliability concerns where Go isn't enough | No Rust expertise on the team |

**Default recommendation:** Kubebuilder for greenfield operators. It uses controller-runtime under the hood, gives you scaffolding without lock-in, and you can drop into raw controller-runtime any time.

---

## End-to-end workflows

### Workflow: Scaffold a new operator

1. **Decide.** Confirm operator is the right pattern (see anti-section above).
2. **Bootstrap.**
   ```
   kubebuilder init --domain example.com --repo example.com/db-operator
   kubebuilder create api --group example.com --version v1alpha1 --kind Database
   ```
   Or use `scripts/operator_scaffold.py --name db-operator --group example.com --kind Database` for a pre-templated skeleton (stricter RBAC, observability, finalizer handling); follow it with `go mod tidy && make generate manifests build`.
3. **Design CRD.** Write the spec/status schema; validate with `scripts/crd_validator.py`.
4. **Implement controller.** Start with: fetch → handle delete (finalizer) → reconcile children → update status.
5. **Add tests.** Use envtest (sets up a real K8s API server for tests).
6. **Wire observability.** Prometheus metrics, structured logging.
7. **Document.** README with example CR, available fields, status meanings, common errors.

### Workflow: Audit an existing operator

1. **Run** `scripts/reconciliation_audit.py --controller-path ./internal/controllers --crd ./config/crd/bases/*.yaml`.
2. **Review** flagged anti-patterns:
   - Missing finalizer + creates external resources
   - No leader election + replicas > 1
   - Status writes spec fields
   - Reconcile is not idempotent (creates duplicates on retry)
   - No requeue backoff (tight loop on error)
   - Wide RBAC verbs / wide scopes
   - Missing observed generation tracking
3. **File issues** for each finding.
4. **Re-audit** after fixes.

### Workflow: Design a CRD

1. **Sketch** the spec: minimum fields the user must provide to make sense of the resource.
2. **Sketch** the status: what the operator will report back.
3. **Validate** with `scripts/crd_validator.py --schema my-crd.yaml`. Output: warnings on missing descriptions, dangerous fields (preserve-unknown), missing printer columns, etc.
4. **Add OpenAPI validation:** required, enum, pattern, min/max.
5. **Add `x-kubernetes-validations`** for cross-field rules.
6. **Add printer columns:** at minimum, `Phase` and `Age`.
7. **Add `kubectl explain` descriptions** for every field.
8. **Iterate** with users — read the YAML they write, identify confusion.

### Workflow: Upgrade CRD versions

The v1alpha1 → v1 upgrade is one of the most error-prone parts of operator development.

1. **Add the new version** (v1beta1) alongside v1alpha1. Both `served: true`. Pick the **storage version** carefully (whichever you'd rather have in etcd).
2. **Write a conversion webhook** if fields differ. Or use "round-tripping" conversion — write to the storage version, read from the served version.
3. **Test conversion both directions** with test cases.
4. **Deploy** the new operator with both versions served.
5. **Migrate** users to v1beta1 (update tooling, docs, examples).
6. **Remove** v1alpha1 (`served: false`, then later remove from CRD).

Don't delete an old version while users are still writing it.

---

## Tooling outputs

| Script | Input | Output |
|--------|-------|--------|
| `scripts/crd_validator.py` | Path to one or more CRD YAML files | Markdown report of schema issues, missing descriptions, dangerous fields, printer column suggestions |
| `scripts/operator_scaffold.py` | Operator name, group, kind, namespace-scope | Bootstrapped project structure with stricter RBAC, observability, finalizer skeleton |
| `scripts/reconciliation_audit.py` | Controller source directory (Go) + CRD YAMLs | Findings: missing finalizers, no leader election, tight loops, wide RBAC, status anti-patterns |

All scripts: stdlib only, argparse CLI, JSON or markdown output.
