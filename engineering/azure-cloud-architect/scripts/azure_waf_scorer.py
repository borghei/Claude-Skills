#!/usr/bin/env python3
"""
azure_waf_scorer.py — Score an Azure workload against the Well-Architected Framework.

Takes a workload YAML spec and scores it against the 5 WAF pillars
(Reliability, Security, Cost Optimization, Operational Excellence,
Performance Efficiency), 10 checks per pillar.

Outputs per-pillar score 0-100, overall average, and findings sorted by severity.

Stdlib only. Markdown or JSON output.

Usage:
    python3 azure_waf_scorer.py --workload-config workload.yaml
    python3 azure_waf_scorer.py --workload-config workload.yaml --format json
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Any


# Reuse the same minimal YAML parser
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
    severity: str  # info=1, warning=2, critical=3
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


def check_reliability(spec: dict[str, Any]) -> list[Check]:
    tier = spec.get("tier", 2)
    cb = []
    cb.append(Check("R1", "Reliability", "Deployed across at least 2 AZs?",
                    "critical", bool(get(spec, "compute.zone_redundant")),
                    f"compute.zone_redundant={get(spec, 'compute.zone_redundant')}",
                    "Enable zone-redundant tier on PaaS or deploy VMSS across zones."))
    cb.append(Check("R2", "Reliability", "RPO/RTO documented?",
                    "critical", bool(get(spec, "reliability.rpo_minutes")) and bool(get(spec, "reliability.rto_minutes")),
                    f"rpo={get(spec, 'reliability.rpo_minutes')}, rto={get(spec, 'reliability.rto_minutes')}",
                    "Define RPO/RTO with business stakeholders and document."))
    cb.append(Check("R3", "Reliability", "Backups tested with restore drill?",
                    "critical", all(d.get("backup_tested") for d in spec.get("data", []) if isinstance(d, dict)),
                    "data services backup_tested status",
                    "Schedule quarterly restore tests; untested backup is no backup."))
    cb.append(Check("R4", "Reliability", "Multi-region DR plan for tier-1?",
                    "critical" if tier == 1 else "warning",
                    bool(get(spec, "compute.multi_region")),
                    f"multi_region={get(spec, 'compute.multi_region')}",
                    "Document failover/failback runbook with regular DR tests."))
    cb.append(Check("R5", "Reliability", "Health probes configured?",
                    "warning", bool(get(spec, "operations.health_probes")),
                    "operations.health_probes",
                    "Configure liveness + readiness probes; LBs need these to route safely."))
    cb.append(Check("R6", "Reliability", "Autoscaling enabled?",
                    "warning", bool(get(spec, "compute.autoscale")),
                    f"compute.autoscale={get(spec, 'compute.autoscale')}",
                    "Configure autoscale based on actual load metrics."))
    cb.append(Check("R7", "Reliability", "Retry/circuit-breaker patterns in app code?",
                    "warning", bool(get(spec, "operations.retry_policies")),
                    "operations.retry_policies",
                    "Use Polly / tenacity / similar — exponential backoff + max retries + circuit breaker."))
    cb.append(Check("R8", "Reliability", "Data services configured for HA?",
                    "critical", all(d.get("zone_redundant") or d.get("ha") for d in spec.get("data", []) if isinstance(d, dict)),
                    "data zone_redundant or ha",
                    "Enable HA (zone-redundant tier or geo-replication) on each data service."))
    cb.append(Check("R9", "Reliability", "PaaS using zone-redundant tiers?",
                    "warning", bool(get(spec, "compute.zone_redundant")),
                    f"compute.zone_redundant={get(spec, 'compute.zone_redundant')}",
                    "Pick zone-redundant SKUs for PaaS services where available."))
    cb.append(Check("R10", "Reliability", "Chaos exercise in last 6 months?",
                    "info", bool(get(spec, "operations.chaos_last_run")),
                    f"operations.chaos_last_run={get(spec, 'operations.chaos_last_run')}",
                    "Run a chaos gameday (see engineering/chaos-engineering skill) quarterly."))
    return cb


def check_security(spec: dict[str, Any]) -> list[Check]:
    cb = []
    cb.append(Check("S1", "Security", "Private endpoints for PaaS?",
                    "critical", bool(get(spec, "network.private_endpoints")),
                    f"private_endpoints={get(spec, 'network.private_endpoints')}",
                    "Use Private Endpoint for all production PaaS access."))
    cb.append(Check("S2", "Security", "Secrets in Key Vault?",
                    "critical", bool(get(spec, "security.key_vault")),
                    f"security.key_vault={get(spec, 'security.key_vault')}",
                    "Store all secrets in Key Vault; reference via @Microsoft.KeyVault(SecretUri=...) syntax."))
    cb.append(Check("S3", "Security", "Managed Identity for service-to-service auth?",
                    "critical", bool(get(spec, "identity.managed_identity")),
                    f"identity.managed_identity={get(spec, 'identity.managed_identity')}",
                    "Use Managed Identity; avoid connection strings / shared keys."))
    cb.append(Check("S4", "Security", "MFA enforced for admin access?",
                    "critical", bool(get(spec, "security.mfa_enforced")),
                    f"security.mfa_enforced={get(spec, 'security.mfa_enforced')}",
                    "Conditional Access policy: enforce MFA for all admin roles."))
    cb.append(Check("S5", "Security", "Defender for Cloud enabled?",
                    "warning", bool(get(spec, "security.defender_for_cloud")),
                    f"security.defender_for_cloud={get(spec, 'security.defender_for_cloud')}",
                    "Enable Defender plans for services in use."))
    cb.append(Check("S6", "Security", "Diagnostic logs sent to Log Analytics?",
                    "critical", bool(get(spec, "observability.log_analytics")),
                    f"observability.log_analytics={get(spec, 'observability.log_analytics')}",
                    "Enable diagnostic settings on every resource sending to Log Analytics."))
    cb.append(Check("S7", "Security", "RBAC at least-privileged scope?",
                    "warning", get(spec, "identity.rbac_scope", "") in ("resource", "resource_group"),
                    f"identity.rbac_scope={get(spec, 'identity.rbac_scope')}",
                    "Scope RBAC to resource/resource-group, not subscription."))
    cb.append(Check("S8", "Security", "NSGs configured with least-privilege rules?",
                    "warning", bool(get(spec, "network.nsg_least_privilege")),
                    f"network.nsg_least_privilege={get(spec, 'network.nsg_least_privilege')}",
                    "Audit NSGs for 0.0.0.0/0 inbound on management ports; restrict to known sources."))
    cb.append(Check("S9", "Security", "Encryption at rest enabled?",
                    "critical", bool(get(spec, "security.encryption_at_rest", True)),
                    f"security.encryption_at_rest={get(spec, 'security.encryption_at_rest', True)}",
                    "Confirm encryption at rest (default for most PaaS; explicit for VMs)."))
    cb.append(Check("S10", "Security", "TLS 1.2+ enforced?",
                    "warning", bool(get(spec, "security.min_tls_1_2", True)),
                    f"security.min_tls_1_2={get(spec, 'security.min_tls_1_2', True)}",
                    "Set minimumTlsVersion: '1.2' on all services that expose it."))
    return cb


def check_cost(spec: dict[str, Any]) -> list[Check]:
    cb = []
    cb.append(Check("C1", "Cost", "Resources right-sized?",
                    "warning", bool(get(spec, "cost.right_sized")),
                    f"cost.right_sized={get(spec, 'cost.right_sized')}",
                    "Audit by Azure Advisor; downsize SKUs running consistently under 25% utilization."))
    cb.append(Check("C2", "Cost", "Reserved Instances / Savings Plans for predictable workloads?",
                    "warning", bool(get(spec, "cost.reservations_purchased")),
                    f"cost.reservations_purchased={get(spec, 'cost.reservations_purchased')}",
                    "Buy 1-yr or 3-yr commitments for steady baseline; up to 72% savings."))
    cb.append(Check("C3", "Cost", "Autoscaling enabled?",
                    "warning", bool(get(spec, "compute.autoscale")),
                    f"compute.autoscale={get(spec, 'compute.autoscale')}",
                    "Same as R6; autoscale prevents over-provisioning."))
    cb.append(Check("C4", "Cost", "Spot / Low-Priority used for fault-tolerant workloads?",
                    "info", bool(get(spec, "cost.spot_used")),
                    f"cost.spot_used={get(spec, 'cost.spot_used')}",
                    "Use spot for batch jobs, CI, dev fleets — up to 90% savings."))
    cb.append(Check("C5", "Cost", "Storage tiered (Hot/Cool/Cold/Archive) per access pattern?",
                    "warning", bool(get(spec, "cost.storage_tiered")),
                    f"cost.storage_tiered={get(spec, 'cost.storage_tiered')}",
                    "Use lifecycle management to auto-tier blobs."))
    cb.append(Check("C6", "Cost", "Dev/test shut down outside business hours?",
                    "info", bool(get(spec, "cost.devtest_schedule")),
                    f"cost.devtest_schedule={get(spec, 'cost.devtest_schedule')}",
                    "DevTest Labs or Automation runbook for 7pm-7am + weekend shutdown."))
    cb.append(Check("C7", "Cost", "Orphaned resources cleaned up (disks, IPs, snapshots)?",
                    "warning", bool(get(spec, "cost.orphans_cleaned")),
                    f"cost.orphans_cleaned={get(spec, 'cost.orphans_cleaned')}",
                    "Periodically run Resource Graph queries for orphaned resources."))
    cb.append(Check("C8", "Cost", "Cosmos/SQL throughput right-sized?",
                    "warning", bool(get(spec, "cost.db_throughput_right_sized")),
                    f"cost.db_throughput_right_sized={get(spec, 'cost.db_throughput_right_sized')}",
                    "Cosmos autoscale; SQL serverless for spiky; tune partition keys."))
    cb.append(Check("C9", "Cost", "Log Analytics retention tuned per table?",
                    "warning", bool(get(spec, "cost.log_retention_tuned")),
                    f"cost.log_retention_tuned={get(spec, 'cost.log_retention_tuned')}",
                    "Tier retention per table (e.g., 30 days for app logs, 1yr for audit)."))
    cb.append(Check("C10", "Cost", "Cost alerts/budgets configured?",
                    "critical", bool(get(spec, "cost.budgets_configured")),
                    f"cost.budgets_configured={get(spec, 'cost.budgets_configured')}",
                    "Set monthly budgets per subscription/RG with alert thresholds."))
    return cb


def check_operations(spec: dict[str, Any]) -> list[Check]:
    cb = []
    cb.append(Check("O1", "Operations", "Infrastructure as code (Bicep/ARM/Terraform)?",
                    "warning", bool(get(spec, "operations.iac")),
                    f"operations.iac={get(spec, 'operations.iac')}",
                    "Define all infra as code; review changes via PR."))
    cb.append(Check("O2", "Operations", "Deployments via CI/CD (no portal changes in prod)?",
                    "critical", bool(get(spec, "operations.ci_cd")),
                    f"operations.ci_cd={get(spec, 'operations.ci_cd')}",
                    "Lock prod portal write access; deploy via pipelines only."))
    cb.append(Check("O3", "Operations", "Staging environment with prod-like config?",
                    "warning", bool(get(spec, "operations.staging_env")),
                    f"operations.staging_env={get(spec, 'operations.staging_env')}",
                    "Stand up a staging environment for pre-prod validation."))
    cb.append(Check("O4", "Operations", "SLO-based alerting?",
                    "warning", bool(get(spec, "observability.slo_alerts")),
                    f"observability.slo_alerts={get(spec, 'observability.slo_alerts')}",
                    "Define SLOs; alert on burn rate, not raw infra metrics."))
    cb.append(Check("O5", "Operations", "Runbooks documented?",
                    "warning", bool(get(spec, "operations.runbooks")),
                    f"operations.runbooks={get(spec, 'operations.runbooks')}",
                    "Write runbooks for common operational tasks."))
    cb.append(Check("O6", "Operations", "Gradual rollout (canary/slots/blue-green)?",
                    "warning", bool(get(spec, "operations.gradual_rollout")),
                    f"operations.gradual_rollout={get(spec, 'operations.gradual_rollout')}",
                    "Use deployment slots (App Service) or progressive delivery; see feature-flags-architect."))
    cb.append(Check("O7", "Operations", "On-call defined with escalation paths?",
                    "warning", bool(get(spec, "operations.on_call_defined")),
                    f"operations.on_call_defined={get(spec, 'operations.on_call_defined')}",
                    "Set up on-call rotation with documented escalation."))
    cb.append(Check("O8", "Operations", "Blameless post-incident reviews?",
                    "info", bool(get(spec, "operations.blameless_pir")),
                    f"operations.blameless_pir={get(spec, 'operations.blameless_pir')}",
                    "Conduct PIRs within 5 business days of every Sev1/2 incident."))
    cb.append(Check("O9", "Operations", "Azure Policy governance (tagging, allowed SKUs)?",
                    "warning", bool(get(spec, "operations.azure_policy")),
                    f"operations.azure_policy={get(spec, 'operations.azure_policy')}",
                    "Use Azure Policy initiatives for governance + compliance."))
    cb.append(Check("O10", "Operations", "Deployment slots / zero-downtime swap?",
                    "info", bool(get(spec, "operations.deployment_slots")),
                    f"operations.deployment_slots={get(spec, 'operations.deployment_slots')}",
                    "Use App Service deployment slots for safe deploys."))
    return cb


def check_performance(spec: dict[str, Any]) -> list[Check]:
    cb = []
    cb.append(Check("P1", "Performance", "Load tested under realistic load?",
                    "warning", bool(get(spec, "performance.load_tested")),
                    f"performance.load_tested={get(spec, 'performance.load_tested')}",
                    "Use Azure Load Testing or k6/Locust; test at peak + 50% headroom."))
    cb.append(Check("P2", "Performance", "Caches (Redis/CDN/Front Door) in use?",
                    "warning", bool(get(spec, "performance.caching")),
                    f"performance.caching={get(spec, 'performance.caching')}",
                    "Add Redis for app cache, Front Door/CDN for assets."))
    cb.append(Check("P3", "Performance", "Database queries optimized (indexes, query plans)?",
                    "warning", bool(get(spec, "performance.db_optimized")),
                    f"performance.db_optimized={get(spec, 'performance.db_optimized')}",
                    "Review slow query logs; add indexes; check query plans."))
    cb.append(Check("P4", "Performance", "Data partitioned for scale-out?",
                    "warning", bool(get(spec, "performance.data_partitioned")),
                    f"performance.data_partitioned={get(spec, 'performance.data_partitioned')}",
                    "Pick Cosmos partition key thoughtfully; SQL sharding if needed."))
    cb.append(Check("P5", "Performance", "Async patterns for I/O-bound work?",
                    "info", bool(get(spec, "performance.async_io")),
                    f"performance.async_io={get(spec, 'performance.async_io')}",
                    "Use async/await; avoid thread starvation on I/O."))
    cb.append(Check("P6", "Performance", "Autoscaling responsive to load?",
                    "warning", bool(get(spec, "compute.autoscale")),
                    f"compute.autoscale={get(spec, 'compute.autoscale')}",
                    "Tune autoscale rules; pre-scale for known peaks."))
    cb.append(Check("P7", "Performance", "Static assets served via CDN?",
                    "warning", bool(get(spec, "performance.cdn_assets")),
                    f"performance.cdn_assets={get(spec, 'performance.cdn_assets')}",
                    "Use Front Door / Azure CDN for static assets."))
    cb.append(Check("P8", "Performance", "Workload profiled to find bottlenecks?",
                    "info", bool(get(spec, "performance.profiled")),
                    f"performance.profiled={get(spec, 'performance.profiled')}",
                    "Use Application Insights Profiler; identify hot paths."))
    cb.append(Check("P9", "Performance", "Request/response sizes reasonable?",
                    "info", bool(get(spec, "performance.payload_reviewed")),
                    f"performance.payload_reviewed={get(spec, 'performance.payload_reviewed')}",
                    "Audit for overfetching; use field-level GraphQL or projection queries."))
    cb.append(Check("P10", "Performance", "SLOs defined and tracked?",
                    "warning", bool(get(spec, "performance.slos_defined")),
                    f"performance.slos_defined={get(spec, 'performance.slos_defined')}",
                    "Define SLI/SLO for latency p95/p99, error rate, throughput."))
    return cb


def score(checks: list[Check]) -> int:
    total_weight = sum(SEVERITY_WEIGHT[c.severity] for c in checks)
    if total_weight == 0:
        return 0
    passed_weight = sum(SEVERITY_WEIGHT[c.severity] for c in checks if c.pass_)
    return int(100 * passed_weight / total_weight)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Score Azure workload against Well-Architected Framework",
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
    except (OSError, ValueError, IndexError) as e:
        print(f"error: cannot read {args.workload_config}: {e}", file=sys.stderr)
        return 2
    if not isinstance(spec, dict) or not spec:
        print(f"error: {args.workload_config} is not a workload spec (expected a YAML mapping)", file=sys.stderr)
        return 2

    pillars = {
        "Reliability": check_reliability(spec),
        "Security": check_security(spec),
        "Cost": check_cost(spec),
        "Operations": check_operations(spec),
        "Performance": check_performance(spec),
    }
    scores = {name: score(checks) for name, checks in pillars.items()}
    overall = sum(scores.values()) // len(scores)
    failed = [c for checks in pillars.values() for c in checks if not c.pass_]
    failed.sort(key=lambda c: -SEVERITY_WEIGHT[c.severity])

    if args.format == "json":
        out = json.dumps(
            {
                "workload_name": spec.get("name", "unnamed"),
                "tier": spec.get("tier", 2),
                "scores": scores,
                "overall_score": overall,
                "failed_checks": [asdict(c) for c in failed],
            },
            indent=2,
        )
    else:
        lines = ["# Azure WAF Assessment", ""]
        lines.append(f"**Workload:** {spec.get('name', 'unnamed')}  ")
        lines.append(f"**Tier:** {spec.get('tier', 2)}")
        lines.append("")
        lines.append(f"## Overall Score: {overall}/100")
        lines.append("")
        lines.append("| Pillar | Score |")
        lines.append("|--------|-------|")
        for name, sc in scores.items():
            lines.append(f"| {name} | {sc}/100 |")
        lines.append("")
        if failed:
            lines.append(f"## Failed Checks ({len(failed)})")
            lines.append("")
            lines.append("| ID | Pillar | Severity | Question | Recommendation |")
            lines.append("|----|--------|----------|----------|----------------|")
            for c in failed:
                lines.append(f"| {c.id} | {c.pillar} | {c.severity} | {c.question} | {c.recommendation[:80]} |")
        out = "\n".join(lines)

    if args.output:
        Path(args.output).write_text(out)
        print(f"wrote {args.output}", file=sys.stderr)
    else:
        print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
