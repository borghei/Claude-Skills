#!/usr/bin/env python3
"""
gcp_cost_estimator.py — Rough GCP monthly cost estimate from a workload spec YAML.

Stdlib only; uses a built-in pricing table (approximate, list prices, no commitment
discounts, US regions). For accurate quotes, always cross-check Google Cloud Pricing
Calculator. Designed for relative comparison + spotting big-ticket items.

Output: per-service monthly cost, total, prioritized optimization suggestions.

Usage:
    python3 gcp_cost_estimator.py --workload-config workload.yaml
    python3 gcp_cost_estimator.py --workload-config workload.yaml --format json
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any


# Approximate monthly USD prices (list, no SUDs/CUDs, US regions, early 2026).
PRICING = {
    # Compute Engine — per instance per month (730h), General-purpose, US
    "gce": {
        "e2-medium": 25, "e2-standard-2": 50, "e2-standard-4": 100, "e2-standard-8": 200,
        "n2-standard-2": 70, "n2-standard-4": 140, "n2-standard-8": 280, "n2-standard-16": 560,
        "n2d-standard-2": 60, "n2d-standard-4": 120, "n2d-standard-8": 240,
        "c3-standard-4": 200, "c3-standard-8": 400,
    },
    # GKE control plane
    "gke_management_per_hour": 0.10,  # $73/mo per cluster after first free
    # GKE Autopilot — per pod-CPU-hour and pod-memory-hour
    "autopilot_vcpu_hour": 0.0445,
    "autopilot_memory_gib_hour": 0.0049,
    # Cloud Run — per CPU-second + per memory-GiB-second + per request
    "cloud_run_vcpu_sec": 0.000024,
    "cloud_run_memory_gib_sec": 0.0000025,
    "cloud_run_per_million_requests": 0.40,
    # Cloud SQL — per vCPU-hour (PostgreSQL Enterprise example)
    "cloud_sql_pg_vcpu_per_month": 50,   # base; varies by tier
    "cloud_sql_pg_memory_gb_per_month": 9,
    "cloud_sql_pg_storage_gb_per_month": 0.17,
    "cloud_sql_ha_multiplier": 2.0,
    # Spanner — per node per month (regional)
    "spanner_regional_node_per_month": 720,
    "spanner_multi_region_node_per_month": 2160,
    "spanner_storage_gb_per_month": 0.30,
    # BigQuery
    "bigquery_on_demand_per_tb_scan": 5.0,
    "bigquery_storage_active_gb_per_month": 0.02,
    "bigquery_storage_long_term_gb_per_month": 0.01,
    # Cloud Storage
    "gcs_standard_gb_per_month": 0.020,
    "gcs_nearline_gb_per_month": 0.010,
    "gcs_coldline_gb_per_month": 0.004,
    "gcs_archive_gb_per_month": 0.0012,
    # Memorystore Redis (Standard tier)
    "memorystore_redis_gb_per_hour": 0.054,
    # Cloud Logging
    "logging_per_gb_ingested": 0.50,
    # Egress
    "egress_internet_per_gb": 0.12,
    # Public IP (static)
    "public_ip_per_month": 7.30,
    # Cloud NAT
    "cloud_nat_per_month": 32,
    "cloud_nat_data_processed_gb": 0.045,
    # Pub/Sub
    "pubsub_per_tib_per_month": 40,
    # Cloud Functions / Run — included in cloud_run_*
}


# Reuse minimal YAML parser
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
class CostLine:
    service: str
    sku: str
    quantity: float
    monthly_usd: float
    optimization: str = ""


def cost_gce(c: dict[str, Any]) -> CostLine:
    sku = c.get("sku", "n2-standard-4")
    count = c.get("count", 1)
    rate = PRICING["gce"].get(sku, 140)
    monthly = rate * count
    opt = ""
    if not c.get("cud_purchased"):
        opt = "Consider 1-yr or 3-yr CUDs for steady GCE workloads (up to 70% off)"
    if not c.get("preemptible_used") and c.get("workload_type") == "batch":
        opt = "Use Preemptible / Spot VMs for batch — up to 91% savings"
    return CostLine("Compute Engine", f"{sku} × {count}", count, monthly, opt)


def cost_gke(c: dict[str, Any]) -> list[CostLine]:
    lines: list[CostLine] = []
    mode = c.get("mode", "autopilot").lower()
    if mode == "autopilot":
        pods = c.get("pods", 100)
        pod_cpu = c.get("avg_pod_cpu", 0.25)
        pod_mem = c.get("avg_pod_memory_gib", 0.5)
        monthly = pods * pod_cpu * PRICING["autopilot_vcpu_hour"] * 730 + pods * pod_mem * PRICING["autopilot_memory_gib_hour"] * 730
        lines.append(CostLine("GKE Autopilot", f"{pods} pods", pods, monthly,
                              "Profile pod utilization. If consistently > 70%, Standard nodes may be cheaper."))
    else:
        node_sku = c.get("node_sku", "n2-standard-4")
        node_count = c.get("node_count", 3)
        rate = PRICING["gce"].get(node_sku, 140)
        monthly = rate * node_count
        management = PRICING["gke_management_per_hour"] * 730  # always charged after first free cluster
        lines.append(CostLine("GKE Control Plane", "Standard", 1, management))
        opt = "Consider 1-yr or 3-yr CUDs for nodes (up to 70% off)" if not c.get("cud_purchased") else ""
        lines.append(CostLine("GKE Worker Nodes", f"{node_sku} × {node_count}", node_count, monthly, opt))
    return lines


def cost_cloud_run(c: dict[str, Any]) -> CostLine:
    avg_instances = c.get("avg_instances", 1)
    vcpu_per_instance = c.get("vcpu_per_instance", 1)
    memory_gib_per_instance = c.get("memory_gib_per_instance", 0.5)
    requests_millions = c.get("requests_millions_per_month", 1)
    request_cost = requests_millions * PRICING["cloud_run_per_million_requests"]
    # Approximation: avg_instances * vcpu * 730h * 3600s
    vcpu_seconds = avg_instances * vcpu_per_instance * 730 * 3600
    memory_seconds = avg_instances * memory_gib_per_instance * 730 * 3600
    compute_cost = vcpu_seconds * PRICING["cloud_run_vcpu_sec"] + memory_seconds * PRICING["cloud_run_memory_gib_sec"]
    return CostLine("Cloud Run", f"avg {avg_instances} instances", avg_instances, request_cost + compute_cost)


def cost_cloud_sql(c: dict[str, Any]) -> CostLine:
    vcpus = c.get("vcpus", 2)
    memory_gb = c.get("memory_gb", 8)
    storage_gb = c.get("storage_gb", 100)
    monthly = (vcpus * PRICING["cloud_sql_pg_vcpu_per_month"]
               + memory_gb * PRICING["cloud_sql_pg_memory_gb_per_month"]
               + storage_gb * PRICING["cloud_sql_pg_storage_gb_per_month"])
    if c.get("ha"):
        monthly *= PRICING["cloud_sql_ha_multiplier"]
    opt = ""
    if not c.get("cud_purchased"):
        opt = "Consider 1-yr CUDs for steady DB workloads"
    return CostLine("Cloud SQL", f"{vcpus}vCPU/{memory_gb}GB/{storage_gb}GB", 1, monthly, opt)


def cost_spanner(c: dict[str, Any]) -> CostLine:
    nodes = c.get("nodes", 1)
    multi_region = c.get("multi_region", False)
    rate = PRICING["spanner_multi_region_node_per_month"] if multi_region else PRICING["spanner_regional_node_per_month"]
    storage_gb = c.get("storage_gb", 50)
    monthly = nodes * rate + storage_gb * PRICING["spanner_storage_gb_per_month"]
    opt = ""
    if multi_region and c.get("tier") != "enterprise-plus":
        opt = "Multi-region Spanner is expensive — confirm you need it; regional may suffice"
    return CostLine("Spanner", f"{'multi-region' if multi_region else 'regional'} × {nodes} nodes", nodes, monthly, opt)


def cost_bigquery(c: dict[str, Any]) -> list[CostLine]:
    lines: list[CostLine] = []
    model = c.get("pricing_model", "on-demand")
    storage_gb = c.get("storage_gb", 1000)
    storage_cost = storage_gb * PRICING["bigquery_storage_active_gb_per_month"]
    lines.append(CostLine("BigQuery Storage", "active", storage_gb, storage_cost))
    if model == "on-demand":
        scan_tb = c.get("monthly_scan_tb", 10)
        compute_cost = scan_tb * 1000 * PRICING["bigquery_on_demand_per_tb_scan"] / 1000  # already in TB
        # simplification: $5/TB
        compute_cost = scan_tb * PRICING["bigquery_on_demand_per_tb_scan"]
        opt = ""
        if scan_tb > 1000:  # > 1PB/mo
            opt = "Switch to Editions slots — typically 30-50% cheaper at this scale"
        lines.append(CostLine("BigQuery On-Demand", f"{scan_tb}TB scanned", scan_tb, compute_cost, opt))
    else:
        # Editions: rough estimate
        slots = c.get("slots", 100)
        # Standard Edition: ~$0.04/slot-hour
        monthly = slots * 0.04 * 730
        lines.append(CostLine("BigQuery Editions", f"{slots} slots", slots, monthly))
    return lines


def cost_gcs(c: dict[str, Any]) -> CostLine:
    storage_class = c.get("storage_class", "standard")
    gb = c.get("size_gb", 100)
    rate = PRICING.get(f"gcs_{storage_class}_gb_per_month", PRICING["gcs_standard_gb_per_month"])
    monthly = gb * rate
    opt = ""
    if storage_class == "standard" and c.get("avg_access_days", 0) > 30:
        opt = "Move to Nearline (30d) or Coldline (90d) tier via lifecycle policy"
    return CostLine("Cloud Storage", f"{storage_class} {gb}GB", gb, monthly, opt)


def cost_memorystore(c: dict[str, Any]) -> CostLine:
    size_gb = c.get("size_gb", 4)
    monthly = size_gb * PRICING["memorystore_redis_gb_per_hour"] * 730
    return CostLine("Memorystore Redis", f"{size_gb}GB", size_gb, monthly)


def cost_logging(c: dict[str, Any]) -> CostLine:
    gb_per_day = c.get("ingest_gb_per_day", 1)
    monthly_gb = gb_per_day * 30
    free_tier = 50
    billable = max(0, monthly_gb - free_tier)
    monthly = billable * PRICING["logging_per_gb_ingested"]
    opt = ""
    if gb_per_day >= 100:
        opt = "Filter at source; sink long-term to BigQuery for cheaper storage"
    return CostLine("Cloud Logging", "ingestion", monthly_gb, monthly, opt)


def cost_egress(c: dict[str, Any]) -> CostLine:
    gb = c.get("egress_gb_per_month", 100)
    monthly = gb * PRICING["egress_internet_per_gb"]
    opt = ""
    if gb > 5000:
        opt = "Egress > 5TB/mo — use Cloud CDN, Standard network tier, or peering"
    return CostLine("Internet Egress", f"{gb}GB", gb, monthly, opt)


# Keys this estimator (and the sibling validator/CAF scorer, which share the spec) read.
# Anything else in these sections is probably a typo that silently falls back to a default.
KNOWN_KEYS = {
    "compute": {"type", "sku", "count", "cud_purchased", "preemptible_used", "workload_type", "mode",
                "pods", "avg_pod_cpu", "avg_pod_memory_gib", "node_sku", "node_count", "avg_instances",
                "vcpu_per_instance", "memory_gib_per_instance", "requests_millions_per_month",
                "multi_region", "multi_zone", "regional", "autoscale", "public_ip"},
    "data": {"service", "name", "vcpus", "memory_gb", "storage_gb", "ha", "cud_purchased", "nodes",
             "multi_region", "tier", "pricing_model", "monthly_scan_tb", "slots", "storage_class",
             "size_gb", "avg_access_days", "backup_tested", "public_ip", "public_access", "all_users_access"},
    "observability": {"cloud_logging", "ingest_gb_per_day", "alerts", "slo_alerts", "audit_log_export"},
    "network": {"egress_gb_per_month", "vpc", "private_service_connect", "default_vpc_in_use",
                "firewall_least_privilege"},
}
COMPUTE_TYPES = {"gce", "compute-engine", "gke", "cloud-run"}
DATA_SERVICES = {"cloud-sql", "spanner", "bigquery", "gcs", "memorystore"}


def spec_warnings(spec: dict[str, Any]) -> list[str]:
    """Unknown keys and unsupported types, which would otherwise be ignored silently."""
    warns: list[str] = []
    for section, known in KNOWN_KEYS.items():
        blocks = spec.get(section) or []
        for i, block in enumerate(blocks if isinstance(blocks, list) else [blocks]):
            if not isinstance(block, dict):
                continue
            where = f"{section}[{i}]" if isinstance(blocks, list) else section
            for key in sorted(set(block) - known):
                warns.append(f"{where}.{key}: unknown key, ignored (default used instead)")
    ctype = str((spec.get("compute") or {}).get("type", "")).lower()
    if ctype and ctype not in COMPUTE_TYPES:
        warns.append(f"compute.type '{ctype}' is not priced (supported: {', '.join(sorted(COMPUTE_TYPES))})")
    for ds in spec.get("data", []) or []:
        if isinstance(ds, dict) and str(ds.get("service", "")).lower() not in DATA_SERVICES:
            warns.append(f"data service '{ds.get('service')}' is not priced (supported: {', '.join(sorted(DATA_SERVICES))})")
    return warns


def estimate(spec: dict[str, Any]) -> tuple[list[CostLine], list[str]]:
    lines: list[CostLine] = []
    compute = spec.get("compute", {}) or {}
    ctype = compute.get("type", "").lower()
    if ctype == "gce" or ctype == "compute-engine":
        lines.append(cost_gce(compute))
    elif ctype == "gke":
        lines.extend(cost_gke(compute))
    elif ctype == "cloud-run":
        lines.append(cost_cloud_run(compute))

    for ds in spec.get("data", []) or []:
        if not isinstance(ds, dict):
            continue
        svc = ds.get("service", "").lower()
        if svc == "cloud-sql":
            lines.append(cost_cloud_sql(ds))
        elif svc == "spanner":
            lines.append(cost_spanner(ds))
        elif svc == "bigquery":
            lines.extend(cost_bigquery(ds))
        elif svc == "gcs":
            lines.append(cost_gcs(ds))
        elif svc == "memorystore":
            lines.append(cost_memorystore(ds))

    obs = spec.get("observability", {}) or {}
    if obs.get("cloud_logging"):
        lines.append(cost_logging(obs))

    network = spec.get("network", {}) or {}
    if network.get("egress_gb_per_month"):
        lines.append(cost_egress(network))

    suggestions: list[str] = []
    total = sum(l.monthly_usd for l in lines)
    if total > 10000:
        suggestions.append("[HIGH] Workload > $10k/mo — investigate CUDs across services")
    for l in lines:
        if l.optimization:
            suggestions.append(f"[{l.service}] {l.optimization} (current: ${l.monthly_usd:,.0f}/mo)")
    return lines, suggestions


def render_human(lines: list[CostLine], suggestions: list[str]) -> str:
    out = ["=" * 72, "GCP MONTHLY COST ESTIMATE (approximate, list prices)", "=" * 72]
    out.append("")
    out.append(f"{'SERVICE':<28} {'SKU':<28} {'MONTHLY USD':>12}")
    out.append("-" * 72)
    for l in lines:
        out.append(f"{l.service:<28} {l.sku[:28]:<28} {'$' + format(l.monthly_usd, ',.0f'):>12}")
    out.append("-" * 72)
    total = sum(l.monthly_usd for l in lines)
    out.append(f"{'TOTAL':<28} {'':<28} {'$' + format(total, ',.0f'):>12}")
    out.append("")
    if suggestions:
        out.append("Optimization opportunities:")
        for s in suggestions:
            out.append(f"  {s}")
    out.append("")
    out.append("NOTE: Estimates are approximations using list prices (no SUDs/CUDs).")
    out.append("Always validate with Google Cloud Pricing Calculator for procurement.")
    return "\n".join(out)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Estimate GCP monthly cost from workload spec",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument("--workload-config", required=True, help="Path to workload YAML spec")
    p.add_argument("--format", choices=["human", "json"], default="human")
    p.add_argument("--output", help="Output file path")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    try:
        spec = parse_yaml(Path(args.workload_config).read_text())
    except OSError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    if not isinstance(spec, dict) or not spec:
        print("error: workload spec is empty or not a mapping (see assets/sample_workload.yaml)", file=sys.stderr)
        return 2
    warnings = spec_warnings(spec)
    for w in warnings:
        print(f"warning: {w}", file=sys.stderr)
    lines, suggestions = estimate(spec)
    if not lines:
        print("error: nothing to price - no supported compute, data, logging or egress entries", file=sys.stderr)
        return 2
    if args.format == "json":
        out = json.dumps(
            {
                "lines": [asdict(l) for l in lines],
                "total_monthly_usd": sum(l.monthly_usd for l in lines),
                "suggestions": suggestions,
                "warnings": warnings,
            },
            indent=2,
        )
    else:
        out = render_human(lines, suggestions)
    if args.output:
        Path(args.output).write_text(out)
        print(f"wrote {args.output}", file=sys.stderr)
    else:
        print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
