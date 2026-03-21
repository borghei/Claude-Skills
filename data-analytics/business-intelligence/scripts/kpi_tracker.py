#!/usr/bin/env python3
"""Calculate and track KPIs from data files against targets and thresholds.

Reads a KPI definition file (JSON) and a data file (CSV/JSON), computes
each metric, evaluates RAG status, and reports trends.

Usage:
    python kpi_tracker.py --definitions kpis.json --data sales.csv
    python kpi_tracker.py --definitions kpis.json --data sales.csv --json
    python kpi_tracker.py --definitions kpis.json --data sales.csv --period monthly

KPI definition format (kpis.json):
[
    {
        "name": "Monthly Revenue",
        "column": "revenue",
        "aggregation": "sum",
        "target": 100000,
        "warning_pct": 0.9,
        "critical_pct": 0.8,
        "higher_is_better": true
    }
]
"""

import argparse
import csv
import json
import math
import os
import sys
from collections import defaultdict


# ---------------------------------------------------------------------------
# Aggregation functions
# ---------------------------------------------------------------------------

def _agg_sum(values: list) -> float:
    return sum(values)

def _agg_mean(values: list) -> float:
    return sum(values) / len(values) if values else 0

def _agg_count(values: list) -> float:
    return float(len(values))

def _agg_count_distinct(values: list) -> float:
    return float(len(set(values)))

def _agg_min(values: list) -> float:
    return min(values) if values else 0

def _agg_max(values: list) -> float:
    return max(values) if values else 0

def _agg_median(values: list) -> float:
    s = sorted(values)
    n = len(s)
    if n == 0:
        return 0.0
    mid = n // 2
    return (s[mid - 1] + s[mid]) / 2.0 if n % 2 == 0 else s[mid]


AGG_MAP = {
    "sum": _agg_sum,
    "mean": _agg_mean,
    "average": _agg_mean,
    "count": _agg_count,
    "count_distinct": _agg_count_distinct,
    "min": _agg_min,
    "max": _agg_max,
    "median": _agg_median,
}


# ---------------------------------------------------------------------------
# Core
# ---------------------------------------------------------------------------

def load_data(file_path: str) -> list:
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".csv":
        with open(file_path, "r", newline="") as f:
            return list(csv.DictReader(f))
    elif ext == ".json":
        with open(file_path, "r") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    else:
        print(f"Error: Unsupported file type '{ext}'.", file=sys.stderr)
        sys.exit(1)


def _extract_numeric(data: list, column: str) -> list:
    values = []
    for row in data:
        v = row.get(column)
        if v is not None:
            try:
                values.append(float(str(v)))
            except ValueError:
                pass
    return values


def _extract_raw(data: list, column: str) -> list:
    return [str(row.get(column, "")) for row in data if row.get(column) is not None]


def _rag_status(actual: float, target: float, warning_pct: float, critical_pct: float, higher_is_better: bool) -> str:
    if higher_is_better:
        if actual >= target:
            return "GREEN"
        elif actual >= target * warning_pct:
            return "YELLOW"
        elif actual >= target * critical_pct:
            return "YELLOW"
        else:
            return "RED"
    else:
        if actual <= target:
            return "GREEN"
        elif actual <= target / warning_pct:
            return "YELLOW"
        else:
            return "RED"


def compute_kpi(kpi_def: dict, data: list) -> dict:
    name = kpi_def["name"]
    column = kpi_def["column"]
    agg_name = kpi_def.get("aggregation", "sum")
    target = kpi_def.get("target")
    warning_pct = kpi_def.get("warning_pct", 0.9)
    critical_pct = kpi_def.get("critical_pct", 0.8)
    higher_is_better = kpi_def.get("higher_is_better", True)

    agg_fn = AGG_MAP.get(agg_name)
    if not agg_fn:
        return {"name": name, "error": f"Unknown aggregation: {agg_name}"}

    if agg_name == "count_distinct":
        raw = _extract_raw(data, column)
        actual = agg_fn(raw)
    else:
        values = _extract_numeric(data, column)
        if not values:
            return {"name": name, "error": f"No numeric values found in column '{column}'."}
        actual = agg_fn(values)

    result = {
        "name": name,
        "column": column,
        "aggregation": agg_name,
        "actual": round(actual, 2),
    }

    if target is not None:
        result["target"] = target
        result["variance"] = round(actual - target, 2)
        result["variance_pct"] = round((actual - target) / target * 100, 2) if target != 0 else 0
        result["status"] = _rag_status(actual, target, warning_pct, critical_pct, higher_is_better)
    else:
        result["status"] = "NO_TARGET"

    return result


def compute_all_kpis(kpi_defs: list, data: list) -> dict:
    results = []
    for kpi_def in kpi_defs:
        results.append(compute_kpi(kpi_def, data))

    green = sum(1 for r in results if r.get("status") == "GREEN")
    yellow = sum(1 for r in results if r.get("status") == "YELLOW")
    red = sum(1 for r in results if r.get("status") == "RED")

    return {
        "total_kpis": len(results),
        "green": green,
        "yellow": yellow,
        "red": red,
        "health_score": round(green / len(results) * 100, 1) if results else 0,
        "kpis": results,
    }


def main():
    parser = argparse.ArgumentParser(description="Calculate and track KPIs against targets.")
    parser.add_argument("--definitions", required=True, help="Path to KPI definitions JSON file")
    parser.add_argument("--data", required=True, help="Path to data file (CSV or JSON)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    for path, label in [(args.definitions, "Definitions"), (args.data, "Data")]:
        if not os.path.exists(path):
            print(f"Error: {label} file not found: {path}", file=sys.stderr)
            sys.exit(1)

    with open(args.definitions, "r") as f:
        kpi_defs = json.load(f)

    if not isinstance(kpi_defs, list):
        print("Error: KPI definitions must be a JSON array.", file=sys.stderr)
        sys.exit(1)

    data = load_data(args.data)
    if not data:
        print("Error: No data rows found.", file=sys.stderr)
        sys.exit(1)

    report = compute_all_kpis(kpi_defs, data)

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print("KPI Tracker Report")
        print("=" * 65)
        print(f"KPIs: {report['total_kpis']}  |  GREEN: {report['green']}  YELLOW: {report['yellow']}  RED: {report['red']}  |  Health: {report['health_score']}%")
        print()
        print(f"{'KPI':<30} {'Actual':>12} {'Target':>12} {'Var %':>8} {'Status':<8}")
        print("-" * 65)
        for kpi in report["kpis"]:
            if "error" in kpi:
                print(f"  {kpi['name']:<28} ERROR: {kpi['error']}")
                continue
            target_str = str(kpi.get("target", "-"))
            var_str = f"{kpi.get('variance_pct', 0):+.1f}%" if "variance_pct" in kpi else "-"
            status = kpi.get("status", "?")
            marker = {"GREEN": "[OK]", "YELLOW": "[!!]", "RED": "[XX]"}.get(status, "[ ]")
            print(f"  {kpi['name']:<28} {kpi['actual']:>12,.2f} {target_str:>12} {var_str:>8} {marker}")

    sys.exit(0)


if __name__ == "__main__":
    main()
