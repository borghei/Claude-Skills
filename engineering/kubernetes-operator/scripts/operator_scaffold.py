#!/usr/bin/env python3
"""
operator_scaffold.py — Generate an operator project skeleton (builds after `make generate`).

Outputs a directory tree with:
  - Sensible Go module + Kubebuilder-style layout
  - CRD with full schema + status subresource + printer columns
  - Reconciler skeleton with finalizers, leader election, structured logging
  - Tight RBAC markers (not the default permissive ones)
  - Manager startup with metrics + health endpoints
  - Dockerfile + deployment manifests
  - README documenting design decisions

This produces source code; you still run `go mod tidy` + `make` to build.

Stdlib only.

Usage:
    python3 operator_scaffold.py --name db-operator --group example.com --kind Database
    python3 operator_scaffold.py --name billing-op --group billing.example.com --kind Invoice --scope Namespaced --out ./billing-op
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path


# No pinned requires: `go mod tidy` resolves the current controller-runtime and the
# matching k8s.io libraries, so the skeleton does not start out of date. Raise the go
# directive if the resolved controller-runtime asks for a newer Go.
GO_MOD_TEMPLATE = """module {go_module}

go 1.27
"""

# controller-gen writes zz_generated.deepcopy.go (DeepCopyObject) and the CRD/RBAC
# manifests from the kubebuilder markers; without it the types do not compile.
MAKEFILE_TEMPLATE = """CONTROLLER_GEN ?= $(shell go env GOPATH)/bin/controller-gen

.PHONY: all generate manifests build test run docker-build

all: generate manifests build

$(CONTROLLER_GEN):
\tgo install sigs.k8s.io/controller-tools/cmd/controller-gen@latest

generate: $(CONTROLLER_GEN)  ## DeepCopy methods for the API types
\t$(CONTROLLER_GEN) object paths="./api/..."

manifests: $(CONTROLLER_GEN)  ## CRDs and RBAC from kubebuilder markers
\t$(CONTROLLER_GEN) crd rbac:roleName={name}-manager-role paths="./..." output:crd:artifacts:config=config/crd/bases

build: generate
\tgo build -o bin/manager ./cmd/manager

test: generate manifests
\tgo test ./...

run: generate manifests
\tgo run ./cmd/manager

docker-build: generate
\tdocker build -t {name}:dev .
"""

MAIN_GO_TEMPLATE = """package main

import (
    "flag"
    "os"

    "k8s.io/apimachinery/pkg/runtime"
    utilruntime "k8s.io/apimachinery/pkg/util/runtime"
    clientgoscheme "k8s.io/client-go/kubernetes/scheme"
    ctrl "sigs.k8s.io/controller-runtime"
    "sigs.k8s.io/controller-runtime/pkg/healthz"
    "sigs.k8s.io/controller-runtime/pkg/log/zap"
    metricsserver "sigs.k8s.io/controller-runtime/pkg/metrics/server"

    {api_pkg_alias} "{go_module}/api/v1alpha1"
    "{go_module}/internal/controllers"
)

var (
    scheme   = runtime.NewScheme()
    setupLog = ctrl.Log.WithName("setup")
)

func init() {{
    utilruntime.Must(clientgoscheme.AddToScheme(scheme))
    utilruntime.Must({api_pkg_alias}.AddToScheme(scheme))
}}

func main() {{
    var metricsAddr string
    var probeAddr string
    var enableLeaderElection bool

    flag.StringVar(&metricsAddr, "metrics-bind-address", ":8080", "Bind addr for metrics")
    flag.StringVar(&probeAddr, "health-probe-bind-address", ":8081", "Bind addr for health probes")
    flag.BoolVar(&enableLeaderElection, "leader-elect", false, "Enable leader election")
    opts := zap.Options{{Development: false}}
    opts.BindFlags(flag.CommandLine)
    flag.Parse()

    ctrl.SetLogger(zap.New(zap.UseFlagOptions(&opts)))

    mgr, err := ctrl.NewManager(ctrl.GetConfigOrDie(), ctrl.Options{{
        Scheme:                  scheme,
        Metrics:                 metricsserver.Options{{BindAddress: metricsAddr}},
        HealthProbeBindAddress:  probeAddr,
        LeaderElection:          enableLeaderElection,
        LeaderElectionID:        "{leader_id}",
        LeaderElectionNamespace: "{operator_namespace}",
    }})
    if err != nil {{
        setupLog.Error(err, "unable to start manager")
        os.Exit(1)
    }}

    if err = (&controllers.{kind}Reconciler{{
        Client: mgr.GetClient(),
        Scheme: mgr.GetScheme(),
    }}).SetupWithManager(mgr); err != nil {{
        setupLog.Error(err, "unable to create controller", "controller", "{kind}")
        os.Exit(1)
    }}

    if err := mgr.AddHealthzCheck("healthz", healthz.Ping); err != nil {{
        setupLog.Error(err, "unable to set up health check")
        os.Exit(1)
    }}
    if err := mgr.AddReadyzCheck("readyz", healthz.Ping); err != nil {{
        setupLog.Error(err, "unable to set up ready check")
        os.Exit(1)
    }}

    setupLog.Info("starting manager")
    if err := mgr.Start(ctrl.SetupSignalHandler()); err != nil {{
        setupLog.Error(err, "problem running manager")
        os.Exit(1)
    }}
}}
"""

TYPES_GO_TEMPLATE = """// Package v1alpha1 contains the {kind} API.
// +kubebuilder:object:generate=true
// +groupName={group}
package v1alpha1

import (
    metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
    "k8s.io/apimachinery/pkg/runtime/schema"
    "sigs.k8s.io/controller-runtime/pkg/scheme"
)

// GroupVersion describes the GVR of this API.
var GroupVersion = schema.GroupVersion{{Group: "{group}", Version: "v1alpha1"}}
var SchemeBuilder = &scheme.Builder{{GroupVersion: GroupVersion}}
var AddToScheme = SchemeBuilder.AddToScheme

// +kubebuilder:object:root=true
// +kubebuilder:subresource:status
// +kubebuilder:printcolumn:name="Phase",type="string",JSONPath=".status.phase"
// +kubebuilder:printcolumn:name="Age",type="date",JSONPath=".metadata.creationTimestamp"
// +kubebuilder:resource:scope={scope}{categories_marker}

// {kind} is the Schema for the {plural} API
type {kind} struct {{
    metav1.TypeMeta   `json:",inline"`
    metav1.ObjectMeta `json:"metadata,omitempty"`

    Spec   {kind}Spec   `json:"spec,omitempty"`
    Status {kind}Status `json:"status,omitempty"`
}}

// {kind}Spec describes the desired state of a {kind}.
type {kind}Spec struct {{
    // Example: a stable identifier from the user.
    // +kubebuilder:validation:Required
    // +kubebuilder:validation:Pattern=`^[a-z][a-z0-9-]*$`
    Name string `json:"name"`

    // Replicas — adjust to your domain. Default 1.
    // +kubebuilder:validation:Minimum=1
    // +kubebuilder:validation:Maximum=10
    // +kubebuilder:default=1
    Replicas int32 `json:"replicas,omitempty"`
}}

// {kind}Status describes the observed state. Operator-owned.
type {kind}Status struct {{
    // Phase is a human-readable summary.
    // +kubebuilder:validation:Enum=Pending;Provisioning;Running;Updating;Failed;Terminating
    Phase string `json:"phase,omitempty"`

    // ObservedGeneration is the spec.generation last reconciled.
    ObservedGeneration int64 `json:"observedGeneration,omitempty"`

    // Conditions follow K8s API conventions.
    // +patchMergeKey=type
    // +patchStrategy=merge
    Conditions []metav1.Condition `json:"conditions,omitempty" patchStrategy:"merge" patchMergeKey:"type"`
}}

// +kubebuilder:object:root=true
type {kind}List struct {{
    metav1.TypeMeta `json:",inline"`
    metav1.ListMeta `json:"metadata,omitempty"`
    Items           []{kind} `json:"items"`
}}

func init() {{
    SchemeBuilder.Register(&{kind}{{}}, &{kind}List{{}})
}}

// DeepCopy methods live in zz_generated.deepcopy.go, written by `make generate`.
"""

CONTROLLER_GO_TEMPLATE = """package controllers

import (
    "context"
    "fmt"
    "time"

    apierrors "k8s.io/apimachinery/pkg/api/errors"
    "k8s.io/apimachinery/pkg/api/meta"
    metav1 "k8s.io/apimachinery/pkg/apis/meta/v1"
    "k8s.io/apimachinery/pkg/runtime"
    ctrl "sigs.k8s.io/controller-runtime"
    "sigs.k8s.io/controller-runtime/pkg/builder"
    "sigs.k8s.io/controller-runtime/pkg/client"
    "sigs.k8s.io/controller-runtime/pkg/controller/controllerutil"
    "sigs.k8s.io/controller-runtime/pkg/log"
    "sigs.k8s.io/controller-runtime/pkg/predicate"

    {api_pkg_alias} "{go_module}/api/v1alpha1"
)

const {kind_var}Finalizer = "{group}/finalizer"

type {kind}Reconciler struct {{
    client.Client
    Scheme *runtime.Scheme
}}

// +kubebuilder:rbac:groups={group},resources={plural},verbs=get;list;watch;create;update;patch;delete
// +kubebuilder:rbac:groups={group},resources={plural}/status,verbs=get;update;patch
// +kubebuilder:rbac:groups={group},resources={plural}/finalizers,verbs=update

func (r *{kind}Reconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {{
    logger := log.FromContext(ctx).WithValues("{kind_var}", req.NamespacedName)

    var obj {api_pkg_alias}.{kind}
    if err := r.Get(ctx, req.NamespacedName, &obj); err != nil {{
        if apierrors.IsNotFound(err) {{
            return ctrl.Result{{}}, nil
        }}
        return ctrl.Result{{}}, fmt.Errorf("fetch {kind_var}: %w", err)
    }}

    if !obj.DeletionTimestamp.IsZero() {{
        return r.handleDelete(ctx, &obj)
    }}

    if !controllerutil.ContainsFinalizer(&obj, {kind_var}Finalizer) {{
        controllerutil.AddFinalizer(&obj, {kind_var}Finalizer)
        if err := r.Update(ctx, &obj); err != nil {{
            return ctrl.Result{{}}, fmt.Errorf("add finalizer: %w", err)
        }}
        return ctrl.Result{{Requeue: true}}, nil
    }}

    logger.Info("reconciling", "spec", obj.Spec)

    // TODO: implement domain-specific reconciliation.
    // 1. Compute desired state from obj.Spec
    // 2. Compare to actual state in cluster
    // 3. Apply diffs (create / update child resources with OwnerReference)
    // 4. Update status

    obj.Status.Phase = "Running"
    obj.Status.ObservedGeneration = obj.Generation
    meta.SetStatusCondition(&obj.Status.Conditions, metav1.Condition{{
        Type:               "Available",
        Status:             metav1.ConditionTrue,
        Reason:             "Reconciled",
        Message:            "Operator reconciled successfully",
        ObservedGeneration: obj.Generation,
        LastTransitionTime: metav1.Now(),
    }})
    if err := r.Status().Update(ctx, &obj); err != nil {{
        return ctrl.Result{{}}, fmt.Errorf("update status: %w", err)
    }}

    return ctrl.Result{{RequeueAfter: 5 * time.Minute}}, nil
}}

func (r *{kind}Reconciler) handleDelete(ctx context.Context, obj *{api_pkg_alias}.{kind}) (ctrl.Result, error) {{
    logger := log.FromContext(ctx)
    if !controllerutil.ContainsFinalizer(obj, {kind_var}Finalizer) {{
        return ctrl.Result{{}}, nil
    }}
    logger.Info("cleanup before delete")

    // TODO: cleanup external resources here.
    // If cleanup fails, return RequeueAfter (don't remove finalizer).
    // Always have a max-age on cleanup attempts to prevent stuck finalizers.

    controllerutil.RemoveFinalizer(obj, {kind_var}Finalizer)
    if err := r.Update(ctx, obj); err != nil {{
        return ctrl.Result{{}}, fmt.Errorf("remove finalizer: %w", err)
    }}
    return ctrl.Result{{}}, nil
}}

func (r *{kind}Reconciler) SetupWithManager(mgr ctrl.Manager) error {{
    return ctrl.NewControllerManagedBy(mgr).
        For(&{api_pkg_alias}.{kind}{{}}, builder.WithPredicates(predicate.GenerationChangedPredicate{{}})).
        Complete(r)
}}
"""

DOCKERFILE_TEMPLATE = """# Keep GO_VERSION in step with the go directive in go.mod. Run `make generate` first.
ARG GO_VERSION=1.27
FROM golang:${GO_VERSION} AS builder
WORKDIR /workspace
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -o manager ./cmd/manager

FROM gcr.io/distroless/static:nonroot
WORKDIR /
COPY --from=builder /workspace/manager .
USER 65532:65532
ENTRYPOINT ["/manager"]
"""

DEPLOYMENT_TEMPLATE = """apiVersion: apps/v1
kind: Deployment
metadata:
  name: {name}-controller-manager
  namespace: {operator_namespace}
  labels:
    app.kubernetes.io/name: {name}
spec:
  replicas: 2
  selector:
    matchLabels:
      app.kubernetes.io/name: {name}
  template:
    metadata:
      labels:
        app.kubernetes.io/name: {name}
    spec:
      serviceAccountName: {name}-controller-manager
      containers:
        - name: manager
          image: ghcr.io/your-org/{name}:latest
          args:
            - --leader-elect=true
            - --metrics-bind-address=:8080
            - --health-probe-bind-address=:8081
          ports:
            - name: metrics
              containerPort: 8080
            - name: probes
              containerPort: 8081
          livenessProbe:
            httpGet:
              path: /healthz
              port: probes
            initialDelaySeconds: 15
            periodSeconds: 20
          readinessProbe:
            httpGet:
              path: /readyz
              port: probes
            initialDelaySeconds: 5
            periodSeconds: 10
          resources:
            requests:
              cpu: 100m
              memory: 128Mi
            limits:
              cpu: 500m
              memory: 512Mi
          securityContext:
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: true
            runAsNonRoot: true
            capabilities:
              drop: ["ALL"]
"""

README_TEMPLATE = """# {name}

A Kubernetes operator for `{kind}` resources in the `{group}` API group.

## Design decisions captured by scaffolding

- **Scope:** {scope}. Adjust if cluster-scope is necessary (justify in PR).
- **Storage version:** v1alpha1 to start. Plan to graduate to v1beta1/v1 within 2 quarters.
- **Status subresource:** enabled. Operator writes status via `Status().Update()`.
- **Leader election:** enabled by default in deployment manifest. Required when running > 1 replica.
- **Finalizer:** `{group}/finalizer` — used for external-resource cleanup on delete.
- **RBAC:** narrow by default (just CR, /status, /finalizers). Add more as the controller grows.
- **Observability:** Prometheus metrics on :8080, health probes on :8081.

## Layout

```
{name}/
├── cmd/manager/main.go            # Manager startup
├── api/v1alpha1/{kind_lower}_types.go    # CRD types
├── internal/controllers/{kind_lower}_controller.go  # Reconciler
├── config/crd/bases/              # Generated CRD YAML (run `make manifests`)
├── config/manager/deployment.yaml # Operator Deployment + ServiceAccount
├── config/rbac/role.yaml          # Generated RBAC (run `make manifests`)
├── Dockerfile
├── go.mod
└── README.md
```

## Next steps

1. `go mod tidy` to fetch dependencies.
2. Implement domain logic in `internal/controllers/{kind_lower}_controller.go`.
3. Add `Owns(...)` calls for child resources.
4. Add `Watches(...)` for cross-CR dependencies.
5. Add envtest-based integration tests.
6. Add Prometheus alerts on `controller_runtime_reconcile_errors_total`.

## CRD checklist (review before first apply)

- [ ] Spec fields have descriptions
- [ ] Validation rules (enum, pattern, min/max) added
- [ ] Status conditions follow K8s convention
- [ ] Printer columns added
- [ ] Categories / shortNames added if appropriate
- [ ] Conversion webhook planned (when adding v1beta1)

See `engineering/kubernetes-operator/references/operator-pattern-and-crds.md` for the full CRD design guide.
"""


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


def scaffold(args: argparse.Namespace) -> dict[str, str]:
    out_dir = Path(args.out or args.name).resolve()
    if out_dir.exists() and any(out_dir.iterdir()):
        raise FileExistsError(f"Output directory {out_dir} exists and is not empty")

    kind = args.kind
    kind_lower = kind.lower()
    kind_var = kind_lower[0]
    plural = kind_lower + "s"  # naive pluralization
    api_pkg_alias = args.group.split(".")[0].replace("-", "") + "v1alpha1"
    go_module = args.go_module or f"github.com/your-org/{args.name}"
    operator_namespace = args.namespace or f"{args.name}-system"
    leader_id = f"{args.name}.{args.group}"
    categories_marker = ""
    if args.categories:
        categories_marker = f',categories={{{",".join(args.categories.split(","))}}}'

    substitutions = {
        "name": args.name,
        "kind": kind,
        "kind_lower": kind_lower,
        "kind_var": kind_var,
        "plural": plural,
        "group": args.group,
        "scope": args.scope,
        "categories_marker": categories_marker,
        "go_module": go_module,
        "api_pkg_alias": api_pkg_alias,
        "operator_namespace": operator_namespace,
        "leader_id": leader_id,
    }

    files = {
        "go.mod": GO_MOD_TEMPLATE.format(**substitutions),
        "cmd/manager/main.go": MAIN_GO_TEMPLATE.format(**substitutions),
        f"api/v1alpha1/{kind_lower}_types.go": TYPES_GO_TEMPLATE.format(**substitutions),
        f"internal/controllers/{kind_lower}_controller.go": CONTROLLER_GO_TEMPLATE.format(**substitutions),
        "Dockerfile": DOCKERFILE_TEMPLATE,
        "Makefile": MAKEFILE_TEMPLATE.format(**substitutions),
        "config/manager/deployment.yaml": DEPLOYMENT_TEMPLATE.format(**substitutions),
        "README.md": README_TEMPLATE.format(**substitutions),
    }

    for rel, content in files.items():
        write_file(out_dir / rel, content)

    return {str(out_dir / rel): f"{len(content)} bytes" for rel, content in files.items()}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Scaffold a Kubernetes operator project skeleton (controller-runtime)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument("--name", required=True, help="Operator project name (e.g., db-operator)")
    p.add_argument("--group", required=True, help="API group (e.g., example.com)")
    p.add_argument("--kind", required=True, help="CRD kind (e.g., Database)")
    p.add_argument("--scope", choices=["Namespaced", "Cluster"], default="Namespaced")
    p.add_argument("--out", help="Output directory (default: <name>)")
    p.add_argument("--go-module", help="Go module path (default: github.com/your-org/<name>)")
    p.add_argument("--namespace", help="Operator deployment namespace (default: <name>-system)")
    p.add_argument("--categories", help="Comma-separated CRD categories (e.g., 'all,databases')")
    p.add_argument("--format", choices=["human", "json"], default="human", help="Report output format")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    try:
        files = scaffold(args)
    except FileExistsError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    if args.format == "json":
        print(json.dumps({"files_written": files}, indent=2))
    else:
        print(f"Scaffolded {len(files)} files:")
        for path in sorted(files):
            print(f"  {path}")
        print("\nNext steps:")
        print("  cd " + (args.out or args.name))
        print("  go mod tidy        # resolves current controller-runtime / k8s.io versions")
        print("  make generate manifests build   # controller-gen: DeepCopy, CRDs, RBAC")
        print("  # then add domain logic in internal/controllers/*.go and envtest tests")
    return 0


if __name__ == "__main__":
    sys.exit(main())
