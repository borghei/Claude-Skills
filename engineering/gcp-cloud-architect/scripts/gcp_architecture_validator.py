#!/usr/bin/env python3
"""
gcp_architecture_validator.py — Validate GCP workload configs / Terraform for anti-patterns.

Reads a workload YAML spec OR scans Terraform files for common GCP anti-patterns:
  - Public IPs on managed services (Cloud SQL, Memorystore)
  - Service Account keys created (instead of Workload Identity)
  - Single-zone deployment for tier-1
  - Wide IAM bindings (basic roles at project level)
  - GCS bucket allUsers / allAuthenticatedUsers grants
  - Default VPC in use
  - Org Policy missing
  - No HA on Cloud SQL
  - BigQuery on-demand for high-volume

Stdlib only. Markdown or JSON output.

Usage:
    python3 gcp_architecture_validator.py --workload-config workload.yaml
    python3 gcp_architecture_validator.py --terraform ./infra/*.tf
    python3 gcp_architecture_validator.py --workload-config workload.yaml --terraform ./infra/main.tf --format json
"""

from __future__ import annotations

import argparse
import glob
import json
import re
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any


@dataclass
class Finding:
    severity: str  # info / warning / critical
    rule_id: str
    rule_name: str
    location: str
    detail: str
    recommendation: str


SEVERITY_LEVEL = {"info": 0, "warning": 1, "critical": 2}


# Minimal YAML parser (same minimal subset)
def parse_yaml(text: str) -> dict[str, Any]:
    lines: list[tuple[int, str]] = []
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip(" "))
        lines.append((indent, line[indent:]))
    result, _ = _parse_block(lines, 0, 0)
    return result if isinstance(result, dict) else {}


def _parse_block(lines, idx, indent):
    if idx >= len(lines):
        return None, idx
    first_indent = lines[idx][0]
    if first_indent < indent:
        return None, idx
    first_line = lines[idx][1]
    if first_line.startswith("- "):
        return _parse_seq(lines, idx, first_indent)
    return _parse_map(lines, idx, first_indent)


def _parse_map(lines, idx, indent):
    out: dict[str, Any] = {}
    while idx < len(lines):
        cur_indent, content = lines[idx]
        if cur_indent < indent:
            break
        if cur_indent > indent:
            idx += 1
            continue
        if ":" not in content:
            idx += 1
            continue
        key, _, rest = content.partition(":")
        key = key.strip().strip('"').strip("'")
        rest = rest.strip()
        if rest:
            out[key] = _scalar(rest)
            idx += 1
        else:
            idx += 1
            if idx < len(lines) and lines[idx][0] > indent:
                value, idx = _parse_block(lines, idx, lines[idx][0])
                out[key] = value if value is not None else {}
            else:
                out[key] = {}
    return out, idx


def _parse_seq(lines, idx, indent):
    out: list[Any] = []
    while idx < len(lines):
        cur_indent, content = lines[idx]
        if cur_indent < indent:
            break
        if not content.startswith("- "):
            break
        rest = content[2:].strip()
        if not rest:
            idx += 1
            if idx < len(lines) and lines[idx][0] > indent:
                value, idx = _parse_block(lines, idx, lines[idx][0])
                out.append(value if value is not None else {})
            else:
                out.append(None)
        elif ":" in rest:
            synth = [(indent + 2, rest)]
            j = idx + 1
            while j < len(lines) and lines[j][0] > indent:
                synth.append(lines[j])
                j += 1
            value, _ = _parse_map(synth, 0, indent + 2)
            out.append(value)
            idx = j
        else:
            out.append(_scalar(rest))
            idx += 1
    return out, idx


def _scalar(s: str):
    s = s.strip()
    if s.startswith('"') and s.endswith('"'):
        return s[1:-1]
    if s.startswith("'") and s.endswith("'"):
        return s[1:-1]
    if s.lower() in ("true", "yes"):
        return True
    if s.lower() in ("false", "no"):
        return False
    if s.lower() in ("null", "~", ""):
        return None
    try:
        return int(s)
    except ValueError:
        pass
    try:
        return float(s)
    except ValueError:
        pass
    return s


# -- Workload spec rules --

def validate_workload(spec: dict[str, Any]) -> list[Finding]:
    findings: list[Finding] = []
    tier = spec.get("tier", 2)
    compute = spec.get("compute", {}) or {}
    data_services = spec.get("data", []) or []
    identity = spec.get("identity", {}) or {}
    network = spec.get("network", {}) or {}
    observability = spec.get("observability", {}) or {}
    security = spec.get("security", {}) or {}

    if tier == 1 and not compute.get("multi_zone") and not compute.get("regional"):
        findings.append(Finding("critical", "WS001", "Tier-1 compute not multi-zone/regional",
                                "compute.multi_zone", f"multi_zone={compute.get('multi_zone')} regional={compute.get('regional')}",
                                "Use regional MIG / Cloud Run (regional) / GKE regional cluster for tier-1."))
    if tier == 1 and not compute.get("multi_region"):
        findings.append(Finding("warning", "WS002", "Tier-1 single-region",
                                "compute.multi_region", "No multi-region plan",
                                "Document multi-region DR posture for tier-1 workloads."))

    if not network.get("vpc"):
        findings.append(Finding("warning", "WS003", "No VPC",
                                "network.vpc", "VPC not configured",
                                "Create a custom VPC; delete the default. Plan subnets explicitly."))
    if network.get("vpc") and not network.get("private_service_connect"):
        findings.append(Finding("warning", "WS004", "VPC without Private Service Connect",
                                "network.private_service_connect", "PSC not enabled",
                                "Use PSC for private access to managed services."))
    if network.get("default_vpc_in_use"):
        findings.append(Finding("critical", "WS005", "Default VPC in use",
                                "network.default_vpc_in_use", "default_vpc_in_use=true",
                                "Delete the default VPC. Build a custom VPC with explicit subnets."))

    if identity.get("service_account_keys"):
        findings.append(Finding("critical", "WS006", "Service Account keys in use",
                                "identity.service_account_keys", "service_account_keys=true",
                                "Switch to Workload Identity / Workload Identity Federation. Avoid SA keys."))
    if not identity.get("workload_identity"):
        findings.append(Finding("warning", "WS007", "Workload Identity not enabled",
                                "identity.workload_identity", "workload_identity=false",
                                "Enable Workload Identity for GKE / use ambient identity for Cloud Run."))

    iam_basic = identity.get("uses_basic_roles", False)
    if iam_basic:
        findings.append(Finding("warning", "WS008", "Basic IAM roles in use",
                                "identity.uses_basic_roles", "uses_basic_roles=true",
                                "Replace basic (owner/editor/viewer) with predefined or custom roles at smallest scope."))

    if not observability.get("cloud_logging"):
        findings.append(Finding("critical", "WS009", "Cloud Logging not enabled",
                                "observability.cloud_logging", "cloud_logging=false",
                                "Enable Cloud Logging; required for audit + ops."))
    if not observability.get("alerts"):
        findings.append(Finding("warning", "WS010", "No alerts configured",
                                "observability.alerts", "alerts=false",
                                "Configure alerts on SLO-relevant signals."))

    if not security.get("mfa_enforced"):
        findings.append(Finding("critical", "WS011", "MFA not enforced for admin",
                                "security.mfa_enforced", "mfa_enforced=false",
                                "Enforce MFA on admin Google Accounts via org policy / Google Workspace."))
    if not security.get("scc_enabled"):
        findings.append(Finding("warning", "WS012", "Security Command Center not enabled",
                                "security.scc_enabled", "scc_enabled=false",
                                "Enable SCC (Premium for production orgs) for threat detection."))

    for i, ds in enumerate(data_services):
        if not isinstance(ds, dict):
            continue
        svc = ds.get("service", "unknown")
        if tier == 1 and svc == "cloud-sql" and not ds.get("ha"):
            findings.append(Finding("critical", "WS013", f"Cloud SQL not HA",
                                    f"data[{i}].ha", f"service={svc}",
                                    "Enable HA on Cloud SQL (regional with sync replica)."))
        if ds.get("public_ip"):
            findings.append(Finding("critical", "WS014", f"Public IP on {svc}",
                                    f"data[{i}].public_ip", f"service={svc}",
                                    "Disable public IP. Use private IP via Service Networking + PSC."))
        if not ds.get("backup_tested"):
            findings.append(Finding("critical", "WS015", f"Backup not tested on {svc}",
                                    f"data[{i}].backup_tested", f"service={svc}",
                                    "Test backup restore quarterly."))
        if svc == "bigquery" and ds.get("pricing_model") == "on-demand" and ds.get("monthly_scan_tb", 0) > 100:
            findings.append(Finding("warning", "WS016", "BigQuery on-demand at high volume",
                                    f"data[{i}].pricing_model", f"scan_tb={ds.get('monthly_scan_tb')}",
                                    "Switch to Editions slots for high-volume scans."))
        if svc == "gcs" and (ds.get("public_access") or ds.get("all_users_access")):
            findings.append(Finding("critical", "WS017", "GCS bucket public access",
                                    f"data[{i}]", f"service={svc}",
                                    "Remove allUsers / allAuthenticatedUsers. Use signed URLs for temporary public access."))

    if not spec.get("operations", {}).get("org_policies"):
        findings.append(Finding("warning", "WS018", "No Org Policies",
                                "operations.org_policies", "org_policies=false",
                                "Enable Org Policy constraints (allowed regions, disallowed services, no public IPs)."))

    return findings


# -- Terraform scanning rules --

TF_DEFAULT_NET_RE = re.compile(r"resource\s+\"google_compute_network\"\s+\"default\"", re.MULTILINE)
TF_BASIC_ROLE_RE = re.compile(r"role\s*=\s*\"roles/(?:owner|editor)\"", re.MULTILINE)
TF_ALL_USERS_RE = re.compile(r"member\s*=\s*\"allUsers\"|members\s*=\s*\[\s*\"allUsers\"", re.MULTILINE)
TF_PUBLIC_IP_RE = re.compile(r"public_ip_address_configuration|ipv4_enabled\s*=\s*true", re.MULTILINE)
TF_SA_KEY_RE = re.compile(r"resource\s+\"google_service_account_key\"", re.MULTILINE)
# An access_config block inside network_interface gives a VM an external IP.
TF_VM_EXTERNAL_IP_RE = re.compile(r"network_interface\s*\{[^}]*?access_config\s*\{", re.DOTALL)
TF_RULES = ["TF001 default network", "TF002 basic roles (owner/editor)", "TF003 allUsers grants",
            "TF004 public IP on Cloud SQL", "TF005 service account keys", "TF006 VM external IP"]


def scan_tf_file(path: str, text: str) -> list[Finding]:
    findings: list[Finding] = []
    for m in TF_DEFAULT_NET_RE.finditer(text):
        ln = text.count("\n", 0, m.start()) + 1
        findings.append(Finding("warning", "TF001", "Default network referenced",
                                f"{path}:{ln}", m.group(0)[:80],
                                "Create a custom VPC; don't use the default."))
    for m in TF_BASIC_ROLE_RE.finditer(text):
        ln = text.count("\n", 0, m.start()) + 1
        findings.append(Finding("warning", "TF002", "Basic role assigned",
                                f"{path}:{ln}", m.group(0),
                                "Use predefined or custom roles; basic roles are too broad."))
    for m in TF_ALL_USERS_RE.finditer(text):
        ln = text.count("\n", 0, m.start()) + 1
        findings.append(Finding("critical", "TF003", "Resource granted to allUsers",
                                f"{path}:{ln}", m.group(0)[:80],
                                "Use signed URLs or specific principals. allUsers makes the resource public."))
    for m in TF_PUBLIC_IP_RE.finditer(text):
        ln = text.count("\n", 0, m.start()) + 1
        findings.append(Finding("warning", "TF004", "Public IP enabled",
                                f"{path}:{ln}", m.group(0),
                                "Use private IP via Service Networking + PSC."))
    for m in TF_SA_KEY_RE.finditer(text):
        ln = text.count("\n", 0, m.start()) + 1
        findings.append(Finding("critical", "TF005", "Service Account key resource created",
                                f"{path}:{ln}", m.group(0),
                                "Use Workload Identity Federation instead of SA keys."))
    for m in TF_VM_EXTERNAL_IP_RE.finditer(text):
        ln = text.count("\n", 0, m.start()) + 1
        findings.append(Finding("warning", "TF006", "VM with external IP",
                                f"{path}:{ln}", "network_interface { access_config { ... } }",
                                "Drop access_config; reach the VM through IAP TCP forwarding or a load balancer."))
    return findings


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Validate GCP workload spec / Terraform for anti-patterns",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument("--workload-config", help="Path to workload YAML spec")
    p.add_argument("--terraform", nargs="*", default=[], help="Terraform file paths or globs")
    p.add_argument("--severity", choices=["info", "warning", "critical"], default="info")
    p.add_argument("--format", choices=["markdown", "json"], default="markdown")
    p.add_argument("--output", help="Output file path")
    return p.parse_args()


def render_markdown(findings: list[Finding], min_sev: str) -> str:
    rel = [f for f in findings if SEVERITY_LEVEL[f.severity] >= SEVERITY_LEVEL[min_sev]]
    out = ["# GCP Architecture Validation Report", ""]
    out.append(f"_Total findings (>= {min_sev}): {len(rel)}_")
    out.append("")
    out.append("_Terraform rules checked (text patterns, not a plan evaluation): " + "; ".join(TF_RULES)
               + ". A clean result covers only these rules._")
    out.append("")
    by_sev: dict[str, list[Finding]] = {}
    for f in rel:
        by_sev.setdefault(f.severity, []).append(f)
    for sev in ["critical", "warning", "info"]:
        items = by_sev.get(sev, [])
        if not items:
            continue
        out.append(f"## {sev.upper()} ({len(items)})")
        out.append("")
        out.append("| Rule | Name | Location | Detail | Recommendation |")
        out.append("|------|------|----------|--------|----------------|")
        for f in items:
            out.append(f"| {f.rule_id} | {f.rule_name} | `{f.location}` | {f.detail[:60]} | {f.recommendation[:80]} |")
        out.append("")
    return "\n".join(out)


def main() -> int:
    args = parse_args()
    findings: list[Finding] = []
    if args.workload_config:
        try:
            spec = parse_yaml(Path(args.workload_config).read_text())
            findings.extend(validate_workload(spec))
        except OSError as e:
            print(f"error: {e}", file=sys.stderr)
            return 2
    tf_files: list[str] = []
    for s in args.terraform:
        if "*" in s:
            tf_files.extend(sorted(glob.glob(s)))
        else:
            tf_files.append(s)
    for f in tf_files:
        try:
            findings.extend(scan_tf_file(f, Path(f).read_text()))
        except OSError as e:
            print(f"error: cannot read {f}: {e}", file=sys.stderr)
            return 2
    if not args.workload_config and not tf_files:
        print("error: provide --workload-config or --terraform", file=sys.stderr)
        return 2
    if args.format == "json":
        out = json.dumps({"findings": [asdict(f) for f in findings], "terraform_rules_checked": TF_RULES}, indent=2)
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
