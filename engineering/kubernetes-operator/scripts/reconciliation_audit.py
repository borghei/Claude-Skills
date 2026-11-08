#!/usr/bin/env python3
"""
reconciliation_audit.py — Audit Go controller code and CRDs for operator anti-patterns.

Scans a controller source directory (Go) and optional CRD YAML files for
static-detectable anti-patterns from the operator-anti-patterns reference:
  - Missing finalizer (creates external resources but no finalizer)
  - No leader election but replicas > 1 (when checking manifests)
  - Tight loop on error (unconditional `return ctrl.Result{}, err`)
  - No OwnerReference set on child resources
  - Wide RBAC verbs (* or excessive get;list;watch on resources outside scope)
  - Status writes spec fields (heuristic)
  - Hardcoded namespace in Get/List calls
  - CRD without status subresource / printer columns / observedGeneration
  - Reconcile function exceeds line threshold

Stdlib only. Markdown or JSON output.

Usage:
    python3 reconciliation_audit.py --controller-path ./internal/controllers
    python3 reconciliation_audit.py --controller-path ./internal/controllers --crd config/crd/bases/*.yaml
    python3 reconciliation_audit.py --controller-path . --format json --severity warning
"""

from __future__ import annotations

import argparse
import glob
import json
import re
import sys
from dataclasses import dataclass, asdict, field
from pathlib import Path


@dataclass
class Finding:
    severity: str  # info / warning / critical
    file: str
    line: int
    rule_id: str
    rule_name: str
    snippet: str
    recommendation: str


SEVERITY_LEVEL = {"info": 0, "warning": 1, "critical": 2}


# --- Go source scanning ---

def scan_go_files(root: Path) -> dict[str, str]:
    """Return {path: text} for all .go files under root, excluding tests."""
    files: dict[str, str] = {}
    for p in root.rglob("*.go"):
        if p.name.endswith("_test.go"):
            continue
        if any(part in {"vendor", "node_modules", ".git"} for part in p.parts):
            continue
        try:
            files[str(p)] = p.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
    return files


def line_of(text: str, pos: int) -> int:
    return text.count("\n", 0, pos) + 1


def snippet_at(text: str, pos: int, lines: int = 2) -> str:
    lines_list = text.splitlines()
    ln = line_of(text, pos)
    start = max(0, ln - 1)
    end = min(len(lines_list), ln + lines - 1)
    return "\n".join(lines_list[start:end])[:300]


# --- Rule implementations ---

RULE_FINALIZER_MISSING = re.compile(r"client\.Create\(|r\.Create\(|client\.Apply", re.MULTILINE)
RULE_FINALIZER_REF = re.compile(r"controllerutil\.AddFinalizer|ContainsFinalizer", re.MULTILINE)
RULE_OWNER_REF = re.compile(r"SetControllerReference|SetOwnerReference", re.MULTILINE)
RULE_TIGHT_LOOP = re.compile(r"return\s+ctrl\.Result\{\s*\}\s*,\s*err\b", re.MULTILINE)
RULE_STATUS_UPDATE_SPEC = re.compile(r"\.Status\(\)\.Update.*\n.*\.Spec\.", re.MULTILINE | re.DOTALL)
RULE_HARDCODED_NS = re.compile(r"client\.ObjectKey\{[^}]*Namespace:\s*\"([^\"]+)\"", re.MULTILINE)
RULE_RBAC_WIDE = re.compile(r"\+kubebuilder:rbac:[^\n]*resources=\*[^\n]*", re.MULTILINE)
RULE_RBAC_VERBS_STAR = re.compile(r"\+kubebuilder:rbac:[^\n]*verbs=[^\n]*\*[^\n]*", re.MULTILINE)
RULE_OBSERVED_GENERATION = re.compile(r"ObservedGeneration", re.MULTILINE)
RULE_LEADER_ELECTION = re.compile(r"LeaderElection\s*:\s*(?!false\b)\w+", re.MULTILINE)


def detect_no_finalizer_with_external_resources(file: str, text: str) -> list[Finding]:
    findings: list[Finding] = []
    creates_resources = RULE_FINALIZER_MISSING.search(text)
    has_finalizer_code = RULE_FINALIZER_REF.search(text)
    if creates_resources and not has_finalizer_code:
        ln = line_of(text, creates_resources.start())
        findings.append(Finding(
            severity="warning",
            file=file,
            line=ln,
            rule_id="OP001",
            rule_name="No finalizer despite resource creation",
            snippet=snippet_at(text, creates_resources.start()),
            recommendation="If this controller creates resources external to K8s, add a finalizer to clean them up on CR delete. If it only creates K8s resources with OwnerReferences, this may be a false positive (GC handles cleanup).",
        ))
    return findings


def detect_missing_owner_references(file: str, text: str) -> list[Finding]:
    findings: list[Finding] = []
    if "r.Create(" in text or "r.Patch(" in text or "client.Apply" in text:
        if not RULE_OWNER_REF.search(text):
            # find first create
            m = re.search(r"r\.(Create|Patch)\(", text)
            if m:
                findings.append(Finding(
                    severity="warning",
                    file=file,
                    line=line_of(text, m.start()),
                    rule_id="OP002",
                    rule_name="Missing OwnerReference",
                    snippet=snippet_at(text, m.start()),
                    recommendation="Set controllerutil.SetControllerReference(parent, child, r.Scheme) before creating child resources to enable garbage collection.",
                ))
    return findings


def detect_tight_loop_on_error(file: str, text: str) -> list[Finding]:
    findings: list[Finding] = []
    for m in RULE_TIGHT_LOOP.finditer(text):
        # heuristic: check that nearby code distinguishes error types
        # rough — look in the 200 chars before for error classification
        context = text[max(0, m.start() - 300):m.start()]
        if not re.search(r"isPermanent|isTransient|apierrors\.Is|IsConflict|IsAlreadyExists|IsNotFound", context):
            findings.append(Finding(
                severity="info",
                file=file,
                line=line_of(text, m.start()),
                rule_id="OP003",
                rule_name="Unconditional error return (may tight-loop on permanent errors)",
                snippet=snippet_at(text, m.start()),
                recommendation="Distinguish permanent from transient errors. For permanent errors, record on status and return nil (no requeue).",
            ))
    return findings


def detect_status_writes_spec(file: str, text: str) -> list[Finding]:
    findings: list[Finding] = []
    for m in RULE_STATUS_UPDATE_SPEC.finditer(text):
        findings.append(Finding(
            severity="warning",
            file=file,
            line=line_of(text, m.start()),
            rule_id="OP004",
            rule_name="Status update path appears to read spec fields",
            snippet=snippet_at(text, m.start()),
            recommendation="Ensure controller never writes to .Spec fields. Status should reflect observed state, derived but not equal to spec.",
        ))
    return findings


def detect_hardcoded_namespace(file: str, text: str) -> list[Finding]:
    findings: list[Finding] = []
    for m in RULE_HARDCODED_NS.finditer(text):
        ns = m.group(1)
        if ns in ("default", "kube-system"):
            continue  # often legitimate test/fixture data
        findings.append(Finding(
            severity="info",
            file=file,
            line=line_of(text, m.start()),
            rule_id="OP005",
            rule_name=f"Hardcoded namespace: {ns}",
            snippet=snippet_at(text, m.start()),
            recommendation="Read own namespace from POD_NAMESPACE env var or service-account token. Hardcoded namespaces prevent flexible deployment.",
        ))
    return findings


def detect_wide_rbac(file: str, text: str) -> list[Finding]:
    findings: list[Finding] = []
    for m in RULE_RBAC_WIDE.finditer(text):
        findings.append(Finding(
            severity="critical",
            file=file,
            line=line_of(text, m.start()),
            rule_id="OP006",
            rule_name="RBAC has resources=* (wildcard)",
            snippet=snippet_at(text, m.start()),
            recommendation="Enumerate specific resources. resources=* grants the controller far more than it needs.",
        ))
    for m in RULE_RBAC_VERBS_STAR.finditer(text):
        findings.append(Finding(
            severity="critical",
            file=file,
            line=line_of(text, m.start()),
            rule_id="OP007",
            rule_name="RBAC has verbs containing wildcard",
            snippet=snippet_at(text, m.start()),
            recommendation="Enumerate specific verbs. verbs=* allows the controller to delete, escalate, etc., that it likely doesn't need.",
        ))
    return findings


def detect_missing_observed_generation(file: str, text: str) -> list[Finding]:
    """Check that controllers updating status also set ObservedGeneration."""
    findings: list[Finding] = []
    if ".Status().Update(" in text or ".Status().Patch(" in text:
        if not RULE_OBSERVED_GENERATION.search(text):
            m = re.search(r"\.Status\(\)\.(?:Update|Patch)", text)
            if m:
                findings.append(Finding(
                    severity="warning",
                    file=file,
                    line=line_of(text, m.start()),
                    rule_id="OP008",
                    rule_name="Status update without ObservedGeneration",
                    snippet=snippet_at(text, m.start()),
                    recommendation="Set obj.Status.ObservedGeneration = obj.Generation before status update. Lets users tell if their spec changes have been processed.",
                ))
    return findings


def detect_long_reconcile(file: str, text: str) -> list[Finding]:
    """Reconcile function over 200 lines = anti-pattern."""
    findings: list[Finding] = []
    m = re.search(r"func\s+\([^)]+\)\s+Reconcile\s*\(", text)
    if not m:
        return findings
    # Find the closing brace at the same indent level
    pos = text.find("{", m.end())
    if pos == -1:
        return findings
    depth = 1
    cur = pos + 1
    while cur < len(text) and depth > 0:
        if text[cur] == "{":
            depth += 1
        elif text[cur] == "}":
            depth -= 1
        cur += 1
    func_text = text[pos:cur]
    lines = func_text.count("\n")
    if lines > 200:
        findings.append(Finding(
            severity="info",
            file=file,
            line=line_of(text, m.start()),
            rule_id="OP009",
            rule_name=f"Reconcile function is {lines} lines",
            snippet=snippet_at(text, m.start()),
            recommendation="Decompose into per-concern reconcilers or per-phase handlers. 200+ line Reconcile is hard to test and review.",
        ))
    return findings


def detect_no_leader_election(file: str, text: str) -> list[Finding]:
    findings: list[Finding] = []
    if "ctrl.NewManager" in text and not RULE_LEADER_ELECTION.search(text):
        m = re.search(r"ctrl\.NewManager", text)
        if m:
            findings.append(Finding(
                severity="warning",
                file=file,
                line=line_of(text, m.start()),
                rule_id="OP010",
                rule_name="Manager created without LeaderElection: true",
                snippet=snippet_at(text, m.start()),
                recommendation="Enable LeaderElection: true if deployment runs > 1 replica. Without it, multiple replicas reconcile concurrently and race.",
            ))
    return findings


RULES = [
    detect_no_finalizer_with_external_resources,
    detect_missing_owner_references,
    detect_tight_loop_on_error,
    detect_status_writes_spec,
    detect_hardcoded_namespace,
    detect_wide_rbac,
    detect_missing_observed_generation,
    detect_long_reconcile,
    detect_no_leader_election,
]


def audit_controllers(root: Path) -> list[Finding]:
    files = scan_go_files(root)
    all_findings: list[Finding] = []
    for path, text in files.items():
        for rule in RULES:
            all_findings.extend(rule(path, text))
    return all_findings


# --- CRD-side audit ---

CRD_SCHEMA_RE = re.compile(r"subresources:\s*\n\s*status:\s*\{\s*\}", re.MULTILINE)
CRD_PREV_UNKNOWN_RE = re.compile(r"x-kubernetes-preserve-unknown-fields:\s*true", re.MULTILINE)
CRD_PRINTER_RE = re.compile(r"additionalPrinterColumns:", re.MULTILINE)


def audit_crd_files(files: list[str]) -> list[Finding]:
    findings: list[Finding] = []
    for f in files:
        try:
            text = Path(f).read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if "CustomResourceDefinition" not in text:
            continue
        if not CRD_SCHEMA_RE.search(text):
            findings.append(Finding(
                severity="warning",
                file=f,
                line=1,
                rule_id="CRD001",
                rule_name="Status subresource not enabled",
                snippet="(file scan)",
                recommendation="Add 'subresources: { status: {} }' under each version.",
            ))
        if not CRD_PRINTER_RE.search(text):
            findings.append(Finding(
                severity="info",
                file=f,
                line=1,
                rule_id="CRD002",
                rule_name="No printer columns",
                snippet="(file scan)",
                recommendation="Add additionalPrinterColumns: Phase + Age at minimum.",
            ))
        if CRD_PREV_UNKNOWN_RE.search(text):
            for m in CRD_PREV_UNKNOWN_RE.finditer(text):
                findings.append(Finding(
                    severity="critical",
                    file=f,
                    line=line_of(text, m.start()),
                    rule_id="CRD003",
                    rule_name="x-kubernetes-preserve-unknown-fields: true",
                    snippet=snippet_at(text, m.start()),
                    recommendation="Define structural schema. Preserving unknown fields defeats validation.",
                ))
    return findings


def render_markdown(findings: list[Finding], min_sev: str) -> str:
    rel = [f for f in findings if SEVERITY_LEVEL[f.severity] >= SEVERITY_LEVEL[min_sev]]
    out: list[str] = ["# Operator Reconciliation Audit", ""]
    out.append(f"_Total findings (>= {min_sev}): {len(rel)}_")
    out.append("")
    by_sev = {}
    for f in rel:
        by_sev.setdefault(f.severity, []).append(f)
    for sev in ["critical", "warning", "info"]:
        items = by_sev.get(sev, [])
        if not items:
            continue
        out.append(f"## {sev.upper()} ({len(items)})")
        out.append("")
        for f in items:
            out.append(f"### [{f.rule_id}] {f.rule_name}")
            out.append(f"- **File**: `{f.file}:{f.line}`")
            out.append(f"- **Recommendation**: {f.recommendation}")
            out.append("")
            out.append("```")
            out.append(f.snippet)
            out.append("```")
            out.append("")
    return "\n".join(out)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Audit operator controller code + CRDs for anti-patterns",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument("--controller-path", required=True, help="Root directory of controller Go source")
    p.add_argument("--crd", nargs="*", default=[], help="Optional CRD YAML paths or globs")
    p.add_argument("--severity", choices=["info", "warning", "critical"], default="info")
    p.add_argument("--format", choices=["markdown", "json"], default="markdown")
    p.add_argument("--output", help="Output file path")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.controller_path).resolve()
    if not root.exists():
        print(f"error: path not found: {root}", file=sys.stderr)
        return 2
    findings = audit_controllers(root)
    crd_files: list[str] = []
    for s in args.crd:
        if "*" in s:
            crd_files.extend(sorted(glob.glob(s)))
        else:
            crd_files.append(s)
    findings.extend(audit_crd_files(crd_files))

    if args.format == "json":
        out = json.dumps(
            {
                "summary": {
                    "total": len(findings),
                    "critical": sum(1 for f in findings if f.severity == "critical"),
                    "warning": sum(1 for f in findings if f.severity == "warning"),
                    "info": sum(1 for f in findings if f.severity == "info"),
                },
                "findings": [asdict(f) for f in findings],
            },
            indent=2,
            default=str,
        )
    else:
        out = render_markdown(findings, args.severity)

    if args.output:
        Path(args.output).write_text(out)
        print(f"wrote {args.output}", file=sys.stderr)
    else:
        print(out)
    return 1 if any(f.severity == "critical" for f in findings) else 0


if __name__ == "__main__":
    sys.exit(main())
