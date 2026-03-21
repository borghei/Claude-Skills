#!/usr/bin/env python3
"""Estimate infrastructure sizing based on workload requirements.

Calculates compute, storage, and network requirements from user counts,
data volumes, and performance targets. Produces sizing recommendations
with cost tier estimates.

Usage:
    python sizing_calculator.py --data workload.json
    python sizing_calculator.py --data workload.csv --json
    python sizing_calculator.py --data workload.json --growth-factor 2.0
"""

import argparse
import csv
import json
import math
import os
import sys
from datetime import datetime


# Sizing reference tables (cloud-agnostic tiers)
COMPUTE_TIERS = [
    {"name": "Small", "vcpus": 2, "ram_gb": 4, "max_concurrent": 500, "monthly_cost": 70},
    {"name": "Medium", "vcpus": 4, "ram_gb": 16, "max_concurrent": 2000, "monthly_cost": 200},
    {"name": "Large", "vcpus": 8, "ram_gb": 32, "max_concurrent": 5000, "monthly_cost": 400},
    {"name": "XLarge", "vcpus": 16, "ram_gb": 64, "max_concurrent": 10000, "monthly_cost": 800},
    {"name": "2XLarge", "vcpus": 32, "ram_gb": 128, "max_concurrent": 25000, "monthly_cost": 1600},
    {"name": "4XLarge", "vcpus": 64, "ram_gb": 256, "max_concurrent": 50000, "monthly_cost": 3200},
]

STORAGE_TIERS = [
    {"name": "Standard SSD", "iops": 3000, "throughput_mbps": 125, "cost_per_gb": 0.10},
    {"name": "Performance SSD", "iops": 16000, "throughput_mbps": 250, "cost_per_gb": 0.17},
    {"name": "Premium SSD", "iops": 64000, "throughput_mbps": 900, "cost_per_gb": 0.30},
]

DB_TIERS = [
    {"name": "Small DB", "vcpus": 2, "ram_gb": 8, "max_connections": 100, "storage_gb": 100, "monthly_cost": 150},
    {"name": "Medium DB", "vcpus": 4, "ram_gb": 16, "max_connections": 500, "storage_gb": 500, "monthly_cost": 400},
    {"name": "Large DB", "vcpus": 8, "ram_gb": 32, "max_connections": 1000, "storage_gb": 1000, "monthly_cost": 800},
    {"name": "XLarge DB", "vcpus": 16, "ram_gb": 64, "max_connections": 2000, "storage_gb": 2000, "monthly_cost": 1600},
    {"name": "2XLarge DB", "vcpus": 32, "ram_gb": 128, "max_connections": 5000, "storage_gb": 5000, "monthly_cost": 3200},
]


def load_data(filepath):
    """Load workload data from CSV or JSON file."""
    ext = os.path.splitext(filepath)[1].lower()
    if ext == ".json":
        with open(filepath, "r") as f:
            data = json.load(f)
            return data if isinstance(data, list) else [data]
    elif ext == ".csv":
        with open(filepath, "r") as f:
            return list(csv.DictReader(f))
    else:
        print(f"Error: Unsupported file format '{ext}'. Use .csv or .json.", file=sys.stderr)
        sys.exit(1)


def safe_float(value, default=0.0):
    """Parse float safely."""
    try:
        return float(str(value).replace(",", "").strip())
    except (ValueError, TypeError):
        return default


def safe_int(value, default=0):
    """Parse int safely."""
    try:
        return int(float(str(value).strip()))
    except (ValueError, TypeError):
        return default


def select_compute_tier(concurrent_users, growth_factor):
    """Select appropriate compute tier based on concurrent users."""
    target = concurrent_users * growth_factor
    for tier in COMPUTE_TIERS:
        if target <= tier["max_concurrent"]:
            return tier
    return COMPUTE_TIERS[-1]  # Largest tier


def calculate_compute_instances(concurrent_users, growth_factor, ha_enabled):
    """Calculate number of compute instances needed."""
    tier = select_compute_tier(concurrent_users, growth_factor)
    target_users = concurrent_users * growth_factor

    instances = max(1, math.ceil(target_users / tier["max_concurrent"]))
    if ha_enabled:
        instances = max(instances, 2)  # Minimum 2 for HA
        instances += 1  # Additional instance for failover

    return {
        "tier": tier["name"],
        "vcpus_per_instance": tier["vcpus"],
        "ram_gb_per_instance": tier["ram_gb"],
        "instances": instances,
        "total_vcpus": tier["vcpus"] * instances,
        "total_ram_gb": tier["ram_gb"] * instances,
        "monthly_cost": tier["monthly_cost"] * instances,
        "max_capacity": tier["max_concurrent"] * instances,
    }


def calculate_storage(data_volume_gb, growth_factor, retention_months):
    """Calculate storage requirements."""
    base_storage = data_volume_gb * growth_factor
    projected_growth = base_storage * (1 + (retention_months * 0.05))  # 5% monthly growth assumption
    total_storage = math.ceil(projected_growth)

    # Select storage tier
    tier = STORAGE_TIERS[0]  # Default to standard
    if total_storage > 1000:
        tier = STORAGE_TIERS[1]  # Performance for larger volumes
    if total_storage > 5000:
        tier = STORAGE_TIERS[2]  # Premium for very large volumes

    # Backup storage (1.5x primary)
    backup_storage = math.ceil(total_storage * 1.5)

    return {
        "primary_storage_gb": total_storage,
        "backup_storage_gb": backup_storage,
        "total_storage_gb": total_storage + backup_storage,
        "storage_tier": tier["name"],
        "iops": tier["iops"],
        "throughput_mbps": tier["throughput_mbps"],
        "monthly_cost": round(total_storage * tier["cost_per_gb"], 2),
        "backup_monthly_cost": round(backup_storage * tier["cost_per_gb"] * 0.5, 2),  # Backup at 50% rate
    }


def calculate_database(total_users, concurrent_users, data_volume_gb, growth_factor, ha_enabled):
    """Calculate database sizing."""
    target_connections = max(concurrent_users * growth_factor * 0.1, 50)  # ~10% of concurrent need DB connections
    target_storage = data_volume_gb * growth_factor * 1.5  # 1.5x for indexes and overhead

    selected_tier = DB_TIERS[0]
    for tier in DB_TIERS:
        if target_connections <= tier["max_connections"] and target_storage <= tier["storage_gb"]:
            selected_tier = tier
            break
    else:
        selected_tier = DB_TIERS[-1]

    replicas = 0
    if ha_enabled:
        replicas = 1  # Read replica for HA
    if concurrent_users > 5000:
        replicas += 1  # Additional read replica for scale

    return {
        "tier": selected_tier["name"],
        "vcpus": selected_tier["vcpus"],
        "ram_gb": selected_tier["ram_gb"],
        "max_connections": selected_tier["max_connections"],
        "allocated_storage_gb": selected_tier["storage_gb"],
        "read_replicas": replicas,
        "monthly_cost": selected_tier["monthly_cost"] * (1 + replicas),
    }


def calculate_network(concurrent_users, data_volume_gb):
    """Calculate network requirements."""
    estimated_bandwidth_mbps = max(concurrent_users * 0.1, 10)  # ~100kbps per concurrent user
    cdn_recommended = concurrent_users > 1000

    return {
        "estimated_bandwidth_mbps": round(estimated_bandwidth_mbps, 1),
        "cdn_recommended": cdn_recommended,
        "load_balancer": concurrent_users > 500,
        "waf_recommended": True,
        "monthly_cost": round(estimated_bandwidth_mbps * 5, 2),  # Rough estimate
    }


def size_infrastructure(workload, growth_factor):
    """Calculate full infrastructure sizing for a workload."""
    name = workload.get("name", workload.get("project", workload.get("customer", "Unknown")))
    total_users = safe_int(workload.get("total_users", workload.get("users", 0)))
    concurrent_users = safe_int(workload.get("concurrent_users", workload.get("peak_users", 0)))
    if concurrent_users == 0 and total_users > 0:
        concurrent_users = max(int(total_users * 0.1), 10)  # Default 10% concurrency

    data_volume_gb = safe_float(workload.get("data_volume_gb", workload.get("data_gb", 0)))
    retention_months = safe_int(workload.get("retention_months", 12))
    ha_required = str(workload.get("ha_required", workload.get("high_availability", "true"))).lower() in ("true", "1", "yes")

    response_time_target = workload.get("response_time_ms", workload.get("latency_target", "500ms"))
    uptime_target = workload.get("uptime_target", workload.get("sla", "99.9%"))
    region = workload.get("region", workload.get("deployment_region", "Single Region"))
    environments = safe_int(workload.get("environments", 3))  # dev, staging, prod

    compute = calculate_compute_instances(concurrent_users, growth_factor, ha_required)
    storage = calculate_storage(data_volume_gb, growth_factor, retention_months)
    database = calculate_database(total_users, concurrent_users, data_volume_gb, growth_factor, ha_required)
    network = calculate_network(concurrent_users, data_volume_gb)

    # Total cost estimate
    prod_monthly = compute["monthly_cost"] + storage["monthly_cost"] + storage["backup_monthly_cost"] + database["monthly_cost"] + network["monthly_cost"]
    # Non-prod environments at 50% of prod cost
    non_prod_monthly = prod_monthly * 0.5 * max(environments - 1, 0)
    total_monthly = round(prod_monthly + non_prod_monthly, 2)
    total_annual = round(total_monthly * 12, 2)

    # Sizing confidence
    if total_users > 0 and concurrent_users > 0 and data_volume_gb > 0:
        confidence = "High"
        confidence_note = "All key inputs provided. Estimates are reliable."
    elif total_users > 0 or concurrent_users > 0:
        confidence = "Medium"
        confidence_note = "Partial inputs. Some values estimated from defaults."
    else:
        confidence = "Low"
        confidence_note = "Minimal inputs. Treat as rough order-of-magnitude estimate."

    return {
        "name": name,
        "inputs": {
            "total_users": total_users,
            "concurrent_users": concurrent_users,
            "data_volume_gb": data_volume_gb,
            "retention_months": retention_months,
            "ha_required": ha_required,
            "growth_factor": growth_factor,
            "response_time_target": str(response_time_target),
            "uptime_target": str(uptime_target),
            "region": region,
            "environments": environments,
        },
        "compute": compute,
        "storage": storage,
        "database": database,
        "network": network,
        "cost_estimate": {
            "production_monthly": round(prod_monthly, 2),
            "non_production_monthly": round(non_prod_monthly, 2),
            "total_monthly": total_monthly,
            "total_annual": total_annual,
        },
        "confidence": confidence,
        "confidence_note": confidence_note,
    }


def format_human(results):
    """Format results for human-readable output."""
    lines = []
    lines.append("=" * 70)
    lines.append("INFRASTRUCTURE SIZING REPORT")
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("=" * 70)

    for r in results:
        lines.append(f"\n  Project: {r['name']}")
        lines.append(f"  Confidence: {r['confidence']} - {r['confidence_note']}")

        inp = r["inputs"]
        lines.append(f"\n  INPUTS")
        lines.append(f"    Users: {inp['total_users']:,} total / {inp['concurrent_users']:,} concurrent")
        lines.append(f"    Data: {inp['data_volume_gb']:,.1f} GB  |  Retention: {inp['retention_months']} months")
        lines.append(f"    HA: {'Yes' if inp['ha_required'] else 'No'}  |  Growth Factor: {inp['growth_factor']}x")
        lines.append(f"    Targets: {inp['response_time_target']} response, {inp['uptime_target']} uptime")
        lines.append(f"    Environments: {inp['environments']}  |  Region: {inp['region']}")

        c = r["compute"]
        lines.append(f"\n  COMPUTE")
        lines.append(f"    Tier: {c['tier']}  |  Instances: {c['instances']}")
        lines.append(f"    Total vCPUs: {c['total_vcpus']}  |  Total RAM: {c['total_ram_gb']} GB")
        lines.append(f"    Max Capacity: {c['max_capacity']:,} concurrent users")
        lines.append(f"    Monthly Cost: ${c['monthly_cost']:,.2f}")

        s = r["storage"]
        lines.append(f"\n  STORAGE")
        lines.append(f"    Primary: {s['primary_storage_gb']:,} GB ({s['storage_tier']})")
        lines.append(f"    Backup: {s['backup_storage_gb']:,} GB")
        lines.append(f"    IOPS: {s['iops']:,}  |  Throughput: {s['throughput_mbps']} MB/s")
        lines.append(f"    Monthly Cost: ${s['monthly_cost'] + s['backup_monthly_cost']:,.2f}")

        d = r["database"]
        lines.append(f"\n  DATABASE")
        lines.append(f"    Tier: {d['tier']}  |  vCPUs: {d['vcpus']}  |  RAM: {d['ram_gb']} GB")
        lines.append(f"    Max Connections: {d['max_connections']:,}  |  Storage: {d['allocated_storage_gb']:,} GB")
        lines.append(f"    Read Replicas: {d['read_replicas']}")
        lines.append(f"    Monthly Cost: ${d['monthly_cost']:,.2f}")

        n = r["network"]
        lines.append(f"\n  NETWORK")
        lines.append(f"    Bandwidth: {n['estimated_bandwidth_mbps']:.1f} Mbps")
        lines.append(f"    CDN: {'Recommended' if n['cdn_recommended'] else 'Optional'}")
        lines.append(f"    Load Balancer: {'Required' if n['load_balancer'] else 'Optional'}")
        lines.append(f"    WAF: {'Recommended' if n['waf_recommended'] else 'Optional'}")
        lines.append(f"    Monthly Cost: ${n['monthly_cost']:,.2f}")

        cost = r["cost_estimate"]
        lines.append(f"\n  COST SUMMARY")
        lines.append(f"    Production Monthly:      ${cost['production_monthly']:>10,.2f}")
        lines.append(f"    Non-Production Monthly:  ${cost['non_production_monthly']:>10,.2f}")
        lines.append(f"    Total Monthly:           ${cost['total_monthly']:>10,.2f}")
        lines.append(f"    Total Annual:            ${cost['total_annual']:>10,.2f}")

        lines.append("-" * 70)

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Estimate infrastructure sizing from workload requirements."
    )
    parser.add_argument("--data", required=True, help="Path to workload data CSV or JSON file")
    parser.add_argument(
        "--growth-factor",
        type=float,
        default=1.5,
        help="Growth multiplier for capacity planning (default: 1.5)",
    )
    parser.add_argument("--json", action="store_true", help="Output results as JSON")

    args = parser.parse_args()

    if not os.path.exists(args.data):
        print(f"Error: File not found: {args.data}", file=sys.stderr)
        sys.exit(1)

    workloads = load_data(args.data)
    if not workloads:
        print("Error: No workload data found in input file.", file=sys.stderr)
        sys.exit(1)

    results = [size_infrastructure(w, args.growth_factor) for w in workloads]

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(format_human(results))

    sys.exit(0)


if __name__ == "__main__":
    main()
