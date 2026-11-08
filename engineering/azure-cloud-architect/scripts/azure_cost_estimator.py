#!/usr/bin/env python3
"""
azure_cost_estimator.py — Rough Azure monthly cost estimate from a workload spec YAML.

Stdlib only; uses a built-in pricing table (approximate, list prices as of early 2026,
no commitment discounts). For accurate quotes, always cross-check with Azure Pricing
Calculator. This tool is designed for relative comparison + spotting big-ticket items
and optimization opportunities — not as a substitute for a current price quote.

Output: per-service monthly cost, total, and prioritized optimization suggestions.

Usage:
    python3 azure_cost_estimator.py --workload-config workload.yaml
    python3 azure_cost_estimator.py --workload-config workload.yaml --format json
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Any


# Approximate monthly USD prices (list, no discounts). Updated rarely.
# Always verify with Azure Pricing Calculator for production budgeting.
PRICING = {
    # Compute - App Service Linux (per instance per month, ~730h)
    "app_service": {
        "B1": 13, "B2": 26, "B3": 52,
        "S1": 73, "S2": 146, "S3": 292,
        "P1v3": 130, "P2v3": 260, "P3v3": 520,
        "I1v2": 295, "I2v2": 590, "I3v2": 1180,
    },
    # Container Apps - approx per vCPU-hour + GiB-hour
    "container_apps_active_vcpu_hour": 0.000024,
    "container_apps_active_gib_hour": 0.000003,
    # Functions Premium plan per instance per month
    "functions_premium": {"EP1": 150, "EP2": 300, "EP3": 600},
    # AKS control plane
    "aks_control_plane_free": 0,
    "aks_control_plane_standard": 73,  # ~$0.10/h
    "aks_control_plane_premium": 439,
    # VMSS / VM - General Purpose Linux per instance/month (approximate)
    "vm": {
        "D2s_v5": 95, "D4s_v5": 190, "D8s_v5": 380, "D16s_v5": 760,
        "E2s_v5": 122, "E4s_v5": 244, "E8s_v5": 488,
        "F2s_v2": 75, "F4s_v2": 150, "F8s_v2": 300,
    },
    # Storage - per GB-month Hot block blob LRS
    "storage_hot_gb": 0.0184,
    "storage_cool_gb": 0.0084,
    "storage_cold_gb": 0.0036,
    "storage_archive_gb": 0.00099,
    # Storage egress per GB (after first 100 GB free)
    "storage_egress_gb": 0.087,
    # SQL DB per vCore (GP Gen5 General Purpose)
    "sqldb_gp_vcore_per_month": 220,
    "sqldb_bc_vcore_per_month": 550,
    "sqldb_hyperscale_vcore_per_month": 250,
    # Cosmos DB - per 100 RU/s (manual) or autoscale (10%-100%)
    "cosmos_ru_per_month_per_100": 5.84,  # $0.008/h × 730h
    # Cosmos storage per GB-month
    "cosmos_storage_gb": 0.25,
    # Log Analytics per GB ingested (PAYG)
    "log_analytics_gb": 2.30,
    # Application Insights ingestion same model
    "app_insights_gb": 2.30,
    # Front Door Premium base + WAF
    "front_door_premium_base": 330,
    "front_door_premium_request_per_million": 1.0,
    # Application Gateway WAF v2 fixed + capacity unit
    "app_gateway_waf_v2_fixed_per_month": 320,
    "app_gateway_waf_v2_capacity_unit_per_month": 26,
    # Azure Cache for Redis
    "redis": {
        "C0": 16, "C1": 80, "C2": 120, "C3": 250, "C4": 500, "C5": 770, "C6": 1500,
        "P1": 600, "P2": 1100, "P3": 2200, "P4": 4400, "P5": 8800,
    },
    # PG Flexible Server
    "pg_burstable_b1ms": 25, "pg_burstable_b2s": 50,
    "pg_general_d2ds_v4": 175, "pg_general_d4ds_v4": 350, "pg_general_d8ds_v4": 700,
    # Public IP standard
    "public_ip_standard_per_month": 3.65,
    # NAT Gateway
    "nat_gateway_per_month": 32,
    "nat_gateway_data_processed_gb": 0.045,
    # Key Vault
    "key_vault_operations_per_10k": 0.03,
}


# Minimal YAML parser (same as validator)
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


def cost_app_service(c: dict[str, Any]) -> CostLine:
    sku = c.get("sku", "P1v3")
    instances = c.get("instances", 1)
    rate = PRICING["app_service"].get(sku, 130)
    opt = ""
    if sku.startswith("P") and "v3" not in sku:
        opt = "Consider P*v3 — newer, often cheaper for equivalent specs"
    return CostLine("App Service", sku, instances, rate * instances, opt)


def cost_aks(c: dict[str, Any]) -> list[CostLine]:
    lines: list[CostLine] = []
    tier = c.get("sku_tier", "standard").lower()
    if tier == "free":
        cp_cost = 0
    elif tier == "premium":
        cp_cost = PRICING["aks_control_plane_premium"]
    else:
        cp_cost = PRICING["aks_control_plane_standard"]
    lines.append(CostLine("AKS Control Plane", tier, 1, cp_cost))
    node_pool = c.get("node_pool", {})
    node_sku = node_pool.get("sku", "D4s_v5")
    node_count = node_pool.get("count", 3)
    rate = PRICING["vm"].get(node_sku, 190)
    monthly = rate * node_count
    opt = ""
    if not node_pool.get("reserved"):
        opt = "Consider 1-yr or 3-yr Reserved Instances for steady node pools — up to 40-60% off"
    lines.append(CostLine("AKS Worker Nodes", f"{node_sku} × {node_count}", node_count, monthly, opt))
    return lines


def cost_sql_db(c: dict[str, Any]) -> CostLine:
    tier = c.get("tier", "general-purpose").lower()
    vcores = c.get("vcores", 2)
    if tier in ("business-critical", "bc"):
        rate = PRICING["sqldb_bc_vcore_per_month"]
    elif tier == "hyperscale":
        rate = PRICING["sqldb_hyperscale_vcore_per_month"]
    else:
        rate = PRICING["sqldb_gp_vcore_per_month"]
    monthly = rate * vcores
    opt = ""
    if tier in ("business-critical", "bc") and vcores >= 8:
        opt = "Verify Business Critical features (in-mem OLTP, local SSD) are needed — GP is much cheaper"
    if c.get("dtu_model"):
        opt = "Migrate from DTU to vCore model for flexibility + Hybrid Benefit"
    return CostLine("Azure SQL DB", f"{tier} {vcores}vCore", vcores, monthly, opt)


def cost_cosmos(c: dict[str, Any]) -> list[CostLine]:
    lines: list[CostLine] = []
    mode = c.get("mode", "autoscale")
    if mode == "serverless":
        # Approximation: $0.30 per million RUs consumed
        rus = c.get("monthly_ru_millions", 10)
        monthly = rus * 0.30
        lines.append(CostLine("Cosmos DB", "serverless", rus, monthly, ""))
    else:
        max_ru = c.get("max_ru_per_sec", 1000)
        # Autoscale pays for max(consumed, 10% of ceiling); manual pays for full
        if mode == "autoscale":
            billed_ru = max_ru * c.get("avg_utilization", 0.5)
            billed_ru = max(billed_ru, max_ru * 0.1)
        else:
            billed_ru = max_ru
        monthly = (billed_ru / 100) * PRICING["cosmos_ru_per_month_per_100"]
        opt = ""
        if mode == "manual" and c.get("avg_utilization", 0.5) < 0.5:
            opt = "Switch to autoscale — pays for max(used, 10% ceiling), often cheaper"
        lines.append(CostLine("Cosmos DB", f"{mode} {max_ru}RU/s", max_ru, monthly, opt))
    storage_gb = c.get("storage_gb", 50)
    lines.append(CostLine("Cosmos DB Storage", "GB", storage_gb, storage_gb * PRICING["cosmos_storage_gb"]))
    return lines


def cost_storage(c: dict[str, Any]) -> CostLine:
    tier = c.get("tier", "hot")
    gb = c.get("size_gb", 100)
    rate = PRICING.get(f"storage_{tier}_gb", PRICING["storage_hot_gb"])
    monthly = gb * rate
    opt = ""
    if tier == "hot" and c.get("avg_access_days", 0) > 30:
        opt = "Move to Cool tier if avg access > 30 days; large savings"
    return CostLine("Storage Account", f"{tier} {gb}GB", gb, monthly, opt)


def cost_log_analytics(c: dict[str, Any]) -> CostLine:
    gb_per_day = c.get("ingest_gb_per_day", 1)
    monthly_gb = gb_per_day * 30
    rate = PRICING["log_analytics_gb"]
    monthly = monthly_gb * rate
    opt = ""
    if gb_per_day >= 100:
        opt = "Switch to commitment tier — at 100GB/day saves ~15%, at 500GB/day saves ~30%"
    return CostLine("Log Analytics", "ingestion", monthly_gb, monthly, opt)


def cost_redis(c: dict[str, Any]) -> CostLine:
    sku = c.get("sku", "C1")
    rate = PRICING["redis"].get(sku, 80)
    return CostLine("Cache for Redis", sku, 1, rate)


def cost_front_door(c: dict[str, Any]) -> CostLine:
    base = PRICING["front_door_premium_base"]
    request_millions = c.get("request_millions_per_month", 50)
    req_cost = request_millions * PRICING["front_door_premium_request_per_million"]
    return CostLine("Front Door Premium", "incl WAF", request_millions, base + req_cost)


def cost_app_gateway(c: dict[str, Any]) -> CostLine:
    cu = c.get("capacity_units", 4)
    monthly = PRICING["app_gateway_waf_v2_fixed_per_month"] + cu * PRICING["app_gateway_waf_v2_capacity_unit_per_month"]
    return CostLine("Application Gateway WAF v2", f"{cu}CU", cu, monthly)


def cost_pg_flex(c: dict[str, Any]) -> CostLine:
    tier = c.get("tier", "general_d4ds_v4")
    rate = PRICING.get(f"pg_{tier}", 350)
    return CostLine("PG Flexible Server", tier, 1, rate)


def cost_egress(c: dict[str, Any]) -> CostLine:
    gb = c.get("egress_gb_per_month", 100)
    free = 100
    billable = max(0, gb - free)
    monthly = billable * PRICING["storage_egress_gb"]
    opt = ""
    if gb > 5000:
        opt = "Egress > 5TB/mo — use Front Door/CDN, private peering, or compression"
    return CostLine("Bandwidth Egress", f"{gb}GB", gb, monthly, opt)


def estimate(spec: dict[str, Any]) -> tuple[list[CostLine], list[str]]:
    lines: list[CostLine] = []

    compute = spec.get("compute", {}) or {}
    compute_type = compute.get("type", "").lower()
    if compute_type == "app-service":
        lines.append(cost_app_service(compute))
    elif compute_type == "aks":
        lines.extend(cost_aks(compute))
    elif compute_type == "vmss":
        sku = compute.get("sku", "D4s_v5")
        count = compute.get("count", 3)
        rate = PRICING["vm"].get(sku, 190)
        lines.append(CostLine("VMSS", f"{sku} × {count}", count, rate * count,
                              "Consider Reserved Instances or Savings Plans for steady workloads"))

    for ds in spec.get("data", []) or []:
        if not isinstance(ds, dict):
            continue
        svc = ds.get("service", "").lower()
        if svc == "sql-db":
            lines.append(cost_sql_db(ds))
        elif svc == "cosmos":
            lines.extend(cost_cosmos(ds))
        elif svc == "storage":
            lines.append(cost_storage(ds))
        elif svc == "pg-flex":
            lines.append(cost_pg_flex(ds))
        elif svc == "redis":
            lines.append(cost_redis(ds))

    obs = spec.get("observability", {}) or {}
    if obs.get("log_analytics"):
        lines.append(cost_log_analytics(obs))

    network = spec.get("network", {}) or {}
    if network.get("front_door"):
        lines.append(cost_front_door(network.get("front_door", {})))
    if network.get("app_gateway"):
        lines.append(cost_app_gateway(network.get("app_gateway", {})))
    if network.get("egress_gb_per_month"):
        lines.append(cost_egress(network))

    suggestions: list[str] = []
    total = sum(l.monthly_usd for l in lines)
    if total > 10000:
        suggestions.append("[HIGH] Workload > $10k/mo — investigate Reserved Instances and Savings Plans across services")
    for l in lines:
        if l.optimization:
            suggestions.append(f"[{l.service}] {l.optimization} (current: ${l.monthly_usd:,.0f}/mo)")

    return lines, suggestions


def render_human(lines: list[CostLine], suggestions: list[str]) -> str:
    out = ["=" * 72, "AZURE MONTHLY COST ESTIMATE (approximate, list prices)", "=" * 72]
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
    out.append("NOTE: Price table = approximate list prices as of early 2026, no discounts. For procurement,")
    out.append("always validate with Azure Pricing Calculator and apply reservations/discounts.")
    return "\n".join(out)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Estimate Azure monthly cost from workload spec",
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
    except (OSError, ValueError, IndexError) as e:
        print(f"error: cannot read {args.workload_config}: {e}", file=sys.stderr)
        return 2
    if not isinstance(spec, dict) or not spec:
        print(f"error: {args.workload_config} is not a workload spec (expected a YAML mapping)", file=sys.stderr)
        return 2
    lines, suggestions = estimate(spec)
    if not lines:
        print("error: no priced services found; set compute.type (app-service|aks|vmss) or data[].service "
              "(sql-db|cosmos|storage|pg-flex|redis) as in assets/sample_workload.yaml", file=sys.stderr)
        return 2
    if args.format == "json":
        out = json.dumps(
            {
                "lines": [asdict(l) for l in lines],
                "total_monthly_usd": sum(l.monthly_usd for l in lines),
                "price_table": "approximate Azure list prices, early 2026, no discounts",
                "suggestions": suggestions,
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
