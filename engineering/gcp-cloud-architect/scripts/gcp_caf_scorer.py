#!/usr/bin/env python3
"""
gcp_caf_scorer.py — Score a GCP workload against the Cloud Architecture Framework.

Takes a workload YAML spec and scores it against the 5 CAF pillars
(Operational Excellence, Security, Reliability, Cost Optimization, Performance
Optimization), 10 checks per pillar.

Stdlib only. Markdown or JSON output.

Usage:
    python3 gcp_caf_scorer.py --workload-config workload.yaml
    python3 gcp_caf_scorer.py --workload-config workload.yaml --format json
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any


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


@dataclass
class Check:
    id: str
    pillar: str
    question: str
    severity: str
    pass_: bool
    detail: str
    recommendation: str


SEVERITY_WEIGHT = {"info": 1, "warning": 2, "critical": 3}


def get(spec: dict[str, Any], path: str, default=None):
    keys = path.split(".")
    cur = spec
    for k in keys:
        if not isinstance(cur, dict):
            return default
        cur = cur.get(k, default if k == keys[-1] else {})
    return cur


def check_operations(spec: dict[str, Any]) -> list[Check]:
    cb = []
    cb.append(Check("O1", "Operations", "Infrastructure as code?",
                    "warning", bool(get(spec, "operations.iac")),
                    f"operations.iac={get(spec, 'operations.iac')}",
                    "Use Terraform / Config Connector / Deployment Manager."))
    cb.append(Check("O2", "Operations", "CI/CD for prod deploys?",
                    "critical", bool(get(spec, "operations.ci_cd")),
                    f"operations.ci_cd={get(spec, 'operations.ci_cd')}",
                    "Lock prod console write; deploy via pipelines only."))
    cb.append(Check("O3", "Operations", "Staging environment?",
                    "warning", bool(get(spec, "operations.staging_env")),
                    f"operations.staging_env={get(spec, 'operations.staging_env')}",
                    "Stand up staging for pre-prod validation."))
    cb.append(Check("O4", "Operations", "SLO-based alerting?",
                    "warning", bool(get(spec, "observability.slo_alerts")),
                    f"observability.slo_alerts={get(spec, 'observability.slo_alerts')}",
                    "Define SLOs; alert on burn rate, not raw infra metrics."))
    cb.append(Check("O5", "Operations", "Runbooks documented?",
                    "warning", bool(get(spec, "operations.runbooks")),
                    f"operations.runbooks={get(spec, 'operations.runbooks')}",
                    "Write runbooks for common operational tasks."))
    cb.append(Check("O6", "Operations", "Gradual rollout (canary/traffic-split)?",
                    "warning", bool(get(spec, "operations.gradual_rollout")),
                    f"operations.gradual_rollout={get(spec, 'operations.gradual_rollout')}",
                    "Cloud Run revisions with traffic split; GKE rolling updates with canary."))
    cb.append(Check("O7", "Operations", "On-call rotations defined?",
                    "warning", bool(get(spec, "operations.on_call_defined")),
                    f"operations.on_call_defined={get(spec, 'operations.on_call_defined')}",
                    "Set up on-call with documented escalation paths."))
    cb.append(Check("O8", "Operations", "Blameless post-incident reviews?",
                    "info", bool(get(spec, "operations.blameless_pir")),
                    f"operations.blameless_pir={get(spec, 'operations.blameless_pir')}",
                    "Conduct PIRs within 5 business days of every Sev1/2."))
    cb.append(Check("O9", "Operations", "Org Policy enforced?",
                    "warning", bool(get(spec, "operations.org_policies")),
                    f"operations.org_policies={get(spec, 'operations.org_policies')}",
                    "Set Org Policy constraints (allowed regions, services, no public IPs)."))
    cb.append(Check("O10", "Operations", "Traffic splitting / zero-downtime swaps?",
                    "info", bool(get(spec, "operations.traffic_split")),
                    f"operations.traffic_split={get(spec, 'operations.traffic_split')}",
                    "Cloud Run revisions, GKE rolling updates, traffic-managed deploys."))
    return cb


def check_security(spec: dict[str, Any]) -> list[Check]:
    cb = []
    cb.append(Check("S1", "Security", "Private Service Connect / private IPs for managed services?",
                    "critical", bool(get(spec, "network.private_service_connect")),
                    f"network.private_service_connect={get(spec, 'network.private_service_connect')}",
                    "Use PSC; disable public IPs on Cloud SQL, Memorystore, etc."))
    cb.append(Check("S2", "Security", "Secrets in Secret Manager?",
                    "critical", bool(get(spec, "security.secret_manager")),
                    f"security.secret_manager={get(spec, 'security.secret_manager')}",
                    "Store secrets in Secret Manager; reference at runtime."))
    cb.append(Check("S3", "Security", "Workload Identity (not SA keys)?",
                    "critical", bool(get(spec, "identity.workload_identity")) and not bool(get(spec, "identity.service_account_keys")),
                    f"workload_identity={get(spec, 'identity.workload_identity')} sa_keys={get(spec, 'identity.service_account_keys')}",
                    "Use Workload Identity (GKE) or Workload Identity Federation. No SA keys."))
    cb.append(Check("S4", "Security", "MFA enforced for admin?",
                    "critical", bool(get(spec, "security.mfa_enforced")),
                    f"security.mfa_enforced={get(spec, 'security.mfa_enforced')}",
                    "Enforce MFA on admin Google Accounts."))
    cb.append(Check("S5", "Security", "Security Command Center enabled?",
                    "warning", bool(get(spec, "security.scc_enabled")) or bool(get(spec, "security.scc_premium")),
                    f"scc_enabled={get(spec, 'security.scc_enabled')} scc_premium={get(spec, 'security.scc_premium')}",
                    "Enable SCC; Premium for production orgs."))
    cb.append(Check("S6", "Security", "Audit logs enabled and exported?",
                    "critical", bool(get(spec, "observability.audit_log_export")),
                    f"observability.audit_log_export={get(spec, 'observability.audit_log_export')}",
                    "Enable Cloud Audit Logs; export to BigQuery or SIEM via Pub/Sub."))
    cb.append(Check("S7", "Security", "IAM least-privileged (predefined > custom > basic)?",
                    "warning", not bool(get(spec, "identity.uses_basic_roles")),
                    f"identity.uses_basic_roles={get(spec, 'identity.uses_basic_roles')}",
                    "Avoid basic roles (owner/editor/viewer) in production."))
    cb.append(Check("S8", "Security", "Firewall rules least-privilege?",
                    "warning", bool(get(spec, "network.firewall_least_privilege")),
                    f"network.firewall_least_privilege={get(spec, 'network.firewall_least_privilege')}",
                    "Audit firewall rules; restrict 0.0.0.0/0 to specific ports/sources."))
    cb.append(Check("S9", "Security", "Encryption at rest (default + CMEK if compliance)?",
                    "critical", bool(get(spec, "security.encryption_at_rest", True)),
                    f"security.encryption_at_rest={get(spec, 'security.encryption_at_rest', True)}",
                    "Default encryption on; CMEK for compliance."))
    cb.append(Check("S10", "Security", "TLS 1.2+ on public endpoints?",
                    "warning", bool(get(spec, "security.min_tls_1_2", True)),
                    f"security.min_tls_1_2={get(spec, 'security.min_tls_1_2', True)}",
                    "Enforce TLS 1.2+ on all public endpoints (LB SSL policies)."))
    return cb


def check_reliability(spec: dict[str, Any]) -> list[Check]:
    tier = spec.get("tier", 2)
    cb = []
    cb.append(Check("R1", "Reliability", "Multi-zone / regional resources?",
                    "critical",
                    bool(get(spec, "compute.multi_zone")) or bool(get(spec, "compute.regional")),
                    f"multi_zone={get(spec, 'compute.multi_zone')} regional={get(spec, 'compute.regional')}",
                    "Use regional MIG / regional GKE / multi-zone managed services."))
    cb.append(Check("R2", "Reliability", "RPO/RTO documented?",
                    "critical", bool(get(spec, "reliability.rpo_minutes")) and bool(get(spec, "reliability.rto_minutes")),
                    f"rpo={get(spec, 'reliability.rpo_minutes')} rto={get(spec, 'reliability.rto_minutes')}",
                    "Define RPO/RTO with stakeholders."))
    cb.append(Check("R3", "Reliability", "Backups tested?",
                    "critical", all(d.get("backup_tested") for d in spec.get("data", []) if isinstance(d, dict)),
                    "data backup_tested status",
                    "Quarterly restore drills."))
    cb.append(Check("R4", "Reliability", "Multi-region DR plan for tier-1?",
                    "critical" if tier == 1 else "warning",
                    bool(get(spec, "compute.multi_region")),
                    f"multi_region={get(spec, 'compute.multi_region')}",
                    "Document multi-region failover/failback."))
    cb.append(Check("R5", "Reliability", "Health probes configured?",
                    "warning", bool(get(spec, "operations.health_probes")),
                    f"operations.health_probes={get(spec, 'operations.health_probes')}",
                    "Liveness + readiness probes for stateless services."))
    cb.append(Check("R6", "Reliability", "Autoscaling enabled?",
                    "warning", bool(get(spec, "compute.autoscale")),
                    f"compute.autoscale={get(spec, 'compute.autoscale')}",
                    "Configure HPA/MIG autoscaler / Cloud Run scaling."))
    cb.append(Check("R7", "Reliability", "Retry / circuit-breaker patterns?",
                    "warning", bool(get(spec, "operations.retry_policies")),
                    f"operations.retry_policies={get(spec, 'operations.retry_policies')}",
                    "Use retry library with exponential backoff + circuit breakers."))
    cb.append(Check("R8", "Reliability", "Data services HA?",
                    "critical", all(d.get("ha") or d.get("multi_region") for d in spec.get("data", []) if isinstance(d, dict)),
                    "data ha or multi_region",
                    "Enable HA on every data service."))
    cb.append(Check("R9", "Reliability", "Regional / multi-zone managed services?",
                    "warning", bool(get(spec, "compute.regional")),
                    f"compute.regional={get(spec, 'compute.regional')}",
                    "Pick regional tiers; zonal resources are single-zone risk."))
    cb.append(Check("R10", "Reliability", "Chaos exercise in past 6 months?",
                    "info", bool(get(spec, "operations.chaos_last_run")),
                    f"operations.chaos_last_run={get(spec, 'operations.chaos_last_run')}",
                    "Quarterly chaos gameday (see engineering/chaos-engineering)."))
    return cb


def check_cost(spec: dict[str, Any]) -> list[Check]:
    cb = []
    cb.append(Check("C1", "Cost", "Right-sized resources?",
                    "warning", bool(get(spec, "cost.right_sized")),
                    f"cost.right_sized={get(spec, 'cost.right_sized')}",
                    "Use Cloud Recommender right-sizing suggestions."))
    cb.append(Check("C2", "Cost", "CUDs purchased for predictable workloads?",
                    "warning", bool(get(spec, "cost.cuds_purchased")),
                    f"cost.cuds_purchased={get(spec, 'cost.cuds_purchased')}",
                    "Buy 1-yr or 3-yr CUDs for stable baseline."))
    cb.append(Check("C3", "Cost", "Autoscaling enabled?",
                    "warning", bool(get(spec, "compute.autoscale")),
                    f"compute.autoscale={get(spec, 'compute.autoscale')}",
                    "Same as R6."))
    cb.append(Check("C4", "Cost", "Preemptible / Spot VMs for fault-tolerant work?",
                    "info", bool(get(spec, "cost.spot_used")),
                    f"cost.spot_used={get(spec, 'cost.spot_used')}",
                    "Up to 91% off for batch, CI, dev fleets."))
    cb.append(Check("C5", "Cost", "Storage class tiering?",
                    "warning", bool(get(spec, "cost.storage_tiered")),
                    f"cost.storage_tiered={get(spec, 'cost.storage_tiered')}",
                    "Lifecycle rules to move old data to Nearline/Coldline/Archive."))
    cb.append(Check("C6", "Cost", "Dev/test shut down outside business hours?",
                    "info", bool(get(spec, "cost.devtest_schedule")),
                    f"cost.devtest_schedule={get(spec, 'cost.devtest_schedule')}",
                    "Cloud Scheduler + Functions to stop/start outside hours."))
    cb.append(Check("C7", "Cost", "Orphaned resources cleaned?",
                    "warning", bool(get(spec, "cost.orphans_cleaned")),
                    f"cost.orphans_cleaned={get(spec, 'cost.orphans_cleaned')}",
                    "Use Asset Inventory + Recommender for orphan detection."))
    cb.append(Check("C8", "Cost", "BigQuery slot reservation for high-volume?",
                    "warning",
                    not (any(d.get("service") == "bigquery" and d.get("pricing_model") == "on-demand" and d.get("monthly_scan_tb", 0) > 1000 for d in spec.get("data", []) if isinstance(d, dict))),
                    "BigQuery on-demand at scale",
                    "Switch to Editions slots for sustained > 1PB/mo."))
    cb.append(Check("C9", "Cost", "Cloud Logging retention tuned?",
                    "warning", bool(get(spec, "cost.log_retention_tuned")),
                    f"cost.log_retention_tuned={get(spec, 'cost.log_retention_tuned')}",
                    "Tier retention per log type; sink long-term to BigQuery."))
    cb.append(Check("C10", "Cost", "Budgets / alerts configured?",
                    "critical", bool(get(spec, "cost.budgets_configured")),
                    f"cost.budgets_configured={get(spec, 'cost.budgets_configured')}",
                    "Set per-project monthly budgets with email/Pub-Sub alerts."))
    return cb


def check_performance(spec: dict[str, Any]) -> list[Check]:
    cb = []
    cb.append(Check("P1", "Performance", "Load tested?",
                    "warning", bool(get(spec, "performance.load_tested")),
                    f"performance.load_tested={get(spec, 'performance.load_tested')}",
                    "Use Cloud Build + k6 / Locust; test at peak + 50%."))
    cb.append(Check("P2", "Performance", "Caches (Memorystore / Cloud CDN) in use?",
                    "warning", bool(get(spec, "performance.caching")),
                    f"performance.caching={get(spec, 'performance.caching')}",
                    "Memorystore for app cache; Cloud CDN for HTTP."))
    cb.append(Check("P3", "Performance", "DB queries optimized?",
                    "warning", bool(get(spec, "performance.db_optimized")),
                    f"performance.db_optimized={get(spec, 'performance.db_optimized')}",
                    "Indexes, query plans, partitioning."))
    cb.append(Check("P4", "Performance", "Data partitioned for scale-out?",
                    "warning", bool(get(spec, "performance.data_partitioned")),
                    f"performance.data_partitioned={get(spec, 'performance.data_partitioned')}",
                    "Spanner primary key design; Bigtable row keys; BigQuery partitions."))
    cb.append(Check("P5", "Performance", "Async patterns for I/O-bound work?",
                    "info", bool(get(spec, "performance.async_io")),
                    f"performance.async_io={get(spec, 'performance.async_io')}",
                    "async/await; thread pools; non-blocking I/O."))
    cb.append(Check("P6", "Performance", "Autoscaling responsive?",
                    "warning", bool(get(spec, "compute.autoscale")),
                    f"compute.autoscale={get(spec, 'compute.autoscale')}",
                    "Tune autoscaler reaction time; pre-scale for peaks."))
    cb.append(Check("P7", "Performance", "Static assets via Cloud CDN?",
                    "warning", bool(get(spec, "performance.cdn_assets")),
                    f"performance.cdn_assets={get(spec, 'performance.cdn_assets')}",
                    "Cloud CDN attached to HTTP(S) LB."))
    cb.append(Check("P8", "Performance", "Cloud Profiler enabled?",
                    "info", bool(get(spec, "performance.profiler")),
                    f"performance.profiler={get(spec, 'performance.profiler')}",
                    "Cloud Profiler for continuous CPU/memory profiling."))
    cb.append(Check("P9", "Performance", "Request/response sizes reviewed?",
                    "info", bool(get(spec, "performance.payload_reviewed")),
                    f"performance.payload_reviewed={get(spec, 'performance.payload_reviewed')}",
                    "Audit for overfetching; projection queries; compression."))
    cb.append(Check("P10", "Performance", "SLOs defined?",
                    "warning", bool(get(spec, "performance.slos_defined")),
                    f"performance.slos_defined={get(spec, 'performance.slos_defined')}",
                    "Define SLI/SLO for latency p95/p99, error rate."))
    return cb


def is_unknown(c: Check) -> bool:
    """A check whose spec field is absent is unknown, not failed (detail reads "path=None")."""
    return c.detail.endswith("=None")


def score(checks: list[Check]) -> int | None:
    checks = [c for c in checks if not is_unknown(c)]
    total_weight = sum(SEVERITY_WEIGHT[c.severity] for c in checks)
    if total_weight == 0:
        return None
    passed_weight = sum(SEVERITY_WEIGHT[c.severity] for c in checks if c.pass_)
    return int(100 * passed_weight / total_weight)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Score GCP workload against Cloud Architecture Framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument("--workload-config", required=True, help="Path to workload YAML spec")
    p.add_argument("--format", choices=["markdown", "json"], default="markdown")
    p.add_argument("--output", help="Output file path")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    try:
        spec = parse_yaml(Path(args.workload_config).read_text())
    except OSError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    pillars = {
        "Operations": check_operations(spec),
        "Security": check_security(spec),
        "Reliability": check_reliability(spec),
        "Cost": check_cost(spec),
        "Performance": check_performance(spec),
    }
    if not spec:
        print("error: workload spec is empty or not a mapping", file=sys.stderr)
        return 2
    scores = {name: score(checks) for name, checks in pillars.items()}
    known = [s for s in scores.values() if s is not None]
    overall = sum(known) // len(known) if known else None
    unknown = [c for checks in pillars.values() for c in checks if is_unknown(c)]
    failed = [c for checks in pillars.values() for c in checks if not c.pass_ and not is_unknown(c)]
    failed.sort(key=lambda c: -SEVERITY_WEIGHT[c.severity])
    if args.format == "json":
        out = json.dumps(
            {
                "workload_name": spec.get("name", "unnamed"),
                "tier": spec.get("tier", 2),
                "scores": scores,
                "overall_score": overall,
                "failed_checks": [asdict(c) for c in failed],
                "unknown_checks": [c.id for c in unknown],
            },
            indent=2,
        )
    else:
        lines = ["# GCP CAF Assessment", ""]
        lines.append(f"**Workload:** {spec.get('name', 'unnamed')}  ")
        lines.append(f"**Tier:** {spec.get('tier', 2)}")
        lines.append("")
        lines.append(f"## Overall Score: {overall if overall is not None else 'n/a'}/100")
        lines.append("")
        lines.append(f"Scored on the {50 - len(unknown)} of 50 checks the spec answers; "
                     f"{len(unknown)} not provided (listed below, not counted as failures).")
        lines.append("")
        lines.append("| Pillar | Score |")
        lines.append("|--------|-------|")
        for name, sc in scores.items():
            lines.append(f"| {name} | {str(sc) + '/100' if sc is not None else 'n/a (no data)'} |")
        lines.append("")
        if failed:
            lines.append(f"## Failed Checks ({len(failed)})")
            lines.append("")
            lines.append("| ID | Pillar | Severity | Question | Recommendation |")
            lines.append("|----|--------|----------|----------|----------------|")
            for c in failed:
                lines.append(f"| {c.id} | {c.pillar} | {c.severity} | {c.question} | {c.recommendation[:80]} |")
        if unknown:
            lines.append("")
            lines.append(f"## Not Provided ({len(unknown)})")
            lines.append("")
            lines.append(", ".join(f"{c.id} ({c.detail.split('=')[0]})" for c in unknown))
        out = "\n".join(lines)
    if args.output:
        Path(args.output).write_text(out)
        print(f"wrote {args.output}", file=sys.stderr)
    else:
        print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
