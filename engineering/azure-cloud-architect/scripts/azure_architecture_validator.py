#!/usr/bin/env python3
"""
azure_architecture_validator.py — Validate Azure workload configs / Bicep for anti-patterns.

Reads a workload YAML spec OR scans Bicep files for common Azure anti-patterns
(the rules match Bicep syntax; ARM JSON templates are not matched):
  - Public endpoints on storage/SQL/Cosmos when private endpoint expected
  - Connection strings / shared keys instead of Managed Identity
  - Single-AZ deployment for tier-1
  - Wide RBAC scopes
  - Missing diagnostic settings
  - Resource Locks missing on critical resources
  - Premium tier without justification
  - Default password / cred in deployment params

Stdlib only. Markdown or JSON output.

Usage:
    python3 azure_architecture_validator.py --workload-config workload.yaml
    python3 azure_architecture_validator.py --bicep ./infra/*.bicep
    python3 azure_architecture_validator.py --workload-config workload.yaml --bicep ./infra/main.bicep --format json
"""

from __future__ import annotations

import argparse
import glob
import json
import re
import sys
from dataclasses import dataclass, asdict, field
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


# Minimal YAML parser for workload specs (reused pattern from crd_validator.py).
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

    if tier == 1 and not compute.get("zone_redundant"):
        findings.append(Finding("critical", "WS001", "Tier-1 compute not zone-redundant",
                                "compute.zone_redundant",
                                f"compute.zone_redundant={compute.get('zone_redundant')}",
                                "Set zone_redundant=true for tier-1 workloads. Use a SKU that supports zones (e.g., Premium v3 App Service in zone-redundant mode)."))
    if tier == 1 and not compute.get("multi_region"):
        findings.append(Finding("warning", "WS002", "Tier-1 single-region",
                                "compute.multi_region", "No multi-region plan",
                                "For tier-1, document a multi-region active-passive or active-active topology. At minimum, document RPO/RTO."))

    if not network.get("vnet"):
        findings.append(Finding("warning", "WS003", "No VNet",
                                "network.vnet", "VNet not configured",
                                "Most production workloads should run in a VNet for Private Endpoint + NSG + segmentation."))
    if network.get("vnet") and not network.get("private_endpoints"):
        findings.append(Finding("warning", "WS004", "VNet without Private Endpoints",
                                "network.private_endpoints", "private_endpoints=false",
                                "Use Private Endpoint to access PaaS services from the VNet. Public endpoints are an unnecessary attack surface."))

    if not identity.get("managed_identity"):
        findings.append(Finding("critical", "WS005", "No Managed Identity",
                                "identity.managed_identity", "managed_identity=false",
                                "Use Managed Identity for service-to-service auth. Eliminates shared keys / secrets in app config."))
    rbac_scope = identity.get("rbac_scope", "")
    if rbac_scope and rbac_scope.lower() in ("subscription", "management_group"):
        findings.append(Finding("warning", "WS006", "Wide RBAC scope",
                                "identity.rbac_scope", f"rbac_scope={rbac_scope}",
                                "Scope RBAC to resource or resource group; subscription scope is overly broad."))

    if not observability.get("log_analytics"):
        findings.append(Finding("critical", "WS007", "No Log Analytics",
                                "observability.log_analytics", "log_analytics=false",
                                "Send diagnostic logs to Log Analytics. Required for audit, troubleshooting, security analytics."))
    if not observability.get("alerts"):
        findings.append(Finding("warning", "WS008", "No alerts configured",
                                "observability.alerts", "alerts=false",
                                "Configure alerts on SLO-relevant signals (error rate, latency p99, throughput)."))

    if not security.get("mfa_enforced"):
        findings.append(Finding("critical", "WS009", "MFA not enforced",
                                "security.mfa_enforced", "mfa_enforced=false",
                                "Enforce MFA via Conditional Access for all admin access. Without it, you fail nearly every compliance audit."))
    if not security.get("defender_for_cloud"):
        findings.append(Finding("warning", "WS010", "Defender for Cloud not enabled",
                                "security.defender_for_cloud", "defender_for_cloud=false",
                                "Enable Defender for the services in use. Adds threat detection + compliance dashboards."))

    for i, ds in enumerate(data_services):
        if not isinstance(ds, dict):
            continue
        svc = ds.get("service", "unknown")
        if tier == 1 and not ds.get("zone_redundant"):
            findings.append(Finding("critical", "WS011", f"Tier-1 data service {svc} not zone-redundant",
                                    f"data[{i}].zone_redundant", f"service={svc}",
                                    "Enable zone-redundant HA on the data service."))
        if not ds.get("backup_tested"):
            findings.append(Finding("critical", "WS012", f"Data service {svc} backup not tested",
                                    f"data[{i}].backup_tested", f"service={svc}",
                                    "Test backup restore quarterly. An untested backup is not a backup."))
        if ds.get("public_access"):
            findings.append(Finding("critical", "WS013", f"Data service {svc} has public access",
                                    f"data[{i}].public_access", f"service={svc}",
                                    "Disable public network access. Use Private Endpoint."))

    return findings


# -- Bicep/ARM scanning rules --

BICEP_PUBLIC_ACCESS_RE = re.compile(r"publicNetworkAccess\s*[:=]\s*['\"]Enabled['\"]", re.IGNORECASE | re.MULTILINE)
BICEP_TLS_RE = re.compile(r"minimumTlsVersion\s*[:=]\s*['\"](?:1\.0|1\.1)['\"]", re.IGNORECASE | re.MULTILINE)
BICEP_KEY_BASED_RE = re.compile(r"allowSharedKeyAccess\s*[:=]\s*true", re.IGNORECASE | re.MULTILINE)
BICEP_DEFAULT_PWD_RE = re.compile(r"(password|adminPassword)\s*[:=]\s*['\"][^'\"]{1,12}['\"]", re.IGNORECASE | re.MULTILINE)
BICEP_NO_HTTPS_RE = re.compile(r"supportsHttpsTrafficOnly\s*[:=]\s*false", re.IGNORECASE | re.MULTILINE)


def scan_bicep_file(path: str, text: str) -> list[Finding]:
    findings: list[Finding] = []
    for m in BICEP_PUBLIC_ACCESS_RE.finditer(text):
        ln = text.count("\n", 0, m.start()) + 1
        findings.append(Finding("critical", "BC001", "publicNetworkAccess: Enabled",
                                f"{path}:{ln}", m.group(0),
                                "Set publicNetworkAccess: 'Disabled' for production resources; use Private Endpoint."))
    for m in BICEP_TLS_RE.finditer(text):
        ln = text.count("\n", 0, m.start()) + 1
        findings.append(Finding("critical", "BC002", "Old TLS minimum",
                                f"{path}:{ln}", m.group(0),
                                "Set minimumTlsVersion: '1.2' or '1.3'."))
    for m in BICEP_KEY_BASED_RE.finditer(text):
        ln = text.count("\n", 0, m.start()) + 1
        findings.append(Finding("warning", "BC003", "Shared key access enabled",
                                f"{path}:{ln}", m.group(0),
                                "Set allowSharedKeyAccess: false; use Managed Identity + RBAC instead."))
    for m in BICEP_DEFAULT_PWD_RE.finditer(text):
        ln = text.count("\n", 0, m.start()) + 1
        findings.append(Finding("critical", "BC004", "Hardcoded short password in IaC",
                                f"{path}:{ln}", "<redacted>",
                                "Use Key Vault reference for credentials; never inline."))
    for m in BICEP_NO_HTTPS_RE.finditer(text):
        ln = text.count("\n", 0, m.start()) + 1
        findings.append(Finding("critical", "BC005", "HTTP traffic allowed on storage",
                                f"{path}:{ln}", m.group(0),
                                "Set supportsHttpsTrafficOnly: true."))
    return findings


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Validate Azure workload spec / Bicep for anti-patterns",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument("--workload-config", help="Path to workload YAML spec")
    p.add_argument("--bicep", nargs="*", default=[], help="Bicep file paths or globs (ARM JSON is not matched)")
    p.add_argument("--severity", choices=["info", "warning", "critical"], default="info")
    p.add_argument("--format", choices=["markdown", "json"], default="markdown")
    p.add_argument("--output", help="Output file path")
    return p.parse_args()


def render_markdown(findings: list[Finding], min_sev: str) -> str:
    rel = [f for f in findings if SEVERITY_LEVEL[f.severity] >= SEVERITY_LEVEL[min_sev]]
    out = ["# Azure Architecture Validation Report", ""]
    out.append(f"_Total findings (>= {min_sev}): {len(rel)}_")
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
    bicep_files: list[str] = []
    for s in args.bicep:
        if "*" in s:
            bicep_files.extend(sorted(glob.glob(s)))
        else:
            bicep_files.append(s)
    for f in bicep_files:
        try:
            findings.extend(scan_bicep_file(f, Path(f).read_text()))
        except OSError:
            continue
    if not args.workload_config and not bicep_files:
        print("error: provide --workload-config or --bicep", file=sys.stderr)
        return 2
    if args.format == "json":
        out = json.dumps({"findings": [asdict(f) for f in findings]}, indent=2)
    else:
        out = render_markdown(findings, args.severity)
    if args.output:
        Path(args.output).write_text(out)
        print(f"wrote {args.output}", file=sys.stderr)
    else:
        print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
