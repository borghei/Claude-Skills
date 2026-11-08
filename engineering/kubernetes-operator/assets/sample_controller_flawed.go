// Deliberately flawed controller for reconciliation_audit.py (exit 1).
// It creates child objects without a finalizer or owner reference, requeues
// errors in a tight loop, hard-codes a namespace, asks for wildcard RBAC, never
// records observedGeneration, and runs the manager without leader election.
package controllers

import (
	"context"

	appsv1 "k8s.io/api/apps/v1"
	ctrl "sigs.k8s.io/controller-runtime"
	"sigs.k8s.io/controller-runtime/pkg/client"
)

// +kubebuilder:rbac:groups=*,resources=*,verbs=*

type CacheReconciler struct {
	client.Client
}

func (r *CacheReconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {
	var cfg appsv1.Deployment
	if err := r.Get(ctx, client.ObjectKey{Namespace: "prod", Name: "cache-config"}, &cfg); err != nil {
		return ctrl.Result{}, err
	}
	dep := &appsv1.Deployment{}
	dep.Name = req.Name + "-cache"
	dep.Namespace = req.Namespace
	if err := r.Create(ctx, dep); err != nil {
		return ctrl.Result{}, err
	}
	return ctrl.Result{}, nil
}

func main() {
	mgr, _ := ctrl.NewManager(ctrl.GetConfigOrDie(), ctrl.Options{})
	_ = mgr.Start(ctrl.SetupSignalHandler())
}
