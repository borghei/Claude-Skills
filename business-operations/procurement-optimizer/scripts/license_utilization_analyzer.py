#!/usr/bin/env python3
"""Analyse SaaS license utilisation and quantify wasted seat spend.

Usage:
    python3 license_utilization_analyzer.py --input spend.json
                                            [--min-utilization 0.70]
                                            [--format text|json]

Input JSON shape:
    {"currency": "USD", "tools": [
        {"name": "...", "category": "crm", "annual_cost": 288000,
         "seats_purchased": 240, "seats_assigned": 231, "seats_active_30d": 198,
         "criticality": "critical"}]}
"""

import argparse
import json
import sys
from collections import defaultdict
from typing import Any, Dict, List

# Benchmark active-seat utilisation below which a tool is over-licensed.
# Tools with low natural cadence get a lower bar: an LMS is not used weekly.
CATEGORY_BENCHMARK: Dict[str, float] = {
    "crm": 0.85,
    "chat": 0.85,
    "collaboration": 0.85,
    "developer-tools": 0.80,
    "security": 0.90,
    "support": 0.85,
    "product-analytics": 0.60,
    "design": 0.70,
    "finance": 0.80,
    "knowledge-base": 0.50,
    "legal": 0.55,
    "whiteboard": 0.40,
    "hr": 0.40,
}
DEFAULT_BENCHMARK = 0.70

# Buffer kept above active usage when recommending a new seat count, so a
# reduction does not immediately trigger emergency seat purchases.
SAFETY_BUFFER = 1.12


def utilisation(tool: Dict[str, Any]) -> Dict[str, float]:
    """Compute assigned and active utilisation ratios for one tool."""
    purchased = int(tool.get("seats_purchased", 0) or 0)
    if purchased <= 0:
        raise ValueError(f"{tool.get('name', '?')}: seats_purchased must be > 0")
    assigned = int(tool.get("seats_assigned", 0) or 0)
    active = int(tool.get("seats_active_30d", 0) or 0)
    return {
        "assigned_ratio": round(assigned / purchased, 3),
        "active_ratio": round(active / purchased, 3),
        "adoption_ratio": round(active / assigned, 3) if assigned else 0.0,
    }


def analyse_tool(tool: Dict[str, Any], override: float) -> Dict[str, Any]:
    """Evaluate one tool against its category benchmark and size the waste."""
    name = str(tool.get("name", "(unnamed)"))
    category = str(tool.get("category", "other")).lower()
    cost = float(tool.get("annual_cost", 0) or 0)
    purchased = int(tool.get("seats_purchased", 0) or 0)
    active = int(tool.get("seats_active_30d", 0) or 0)
    ratios = utilisation(tool)

    benchmark = override if override > 0 else CATEGORY_BENCHMARK.get(
        category, DEFAULT_BENCHMARK)
    cost_per_seat = cost / purchased if purchased else 0.0

    recommended = max(int(active * SAFETY_BUFFER + 0.999), 1)
    recommended = min(recommended, purchased)
    reclaimable = purchased - recommended
    waste = round(reclaimable * cost_per_seat, 2)

    if ratios["active_ratio"] >= benchmark:
        verdict, action = "healthy", "No seat action. Renegotiate on price, not volume."
    elif ratios["adoption_ratio"] < 0.5 and ratios["assigned_ratio"] > 0.7:
        verdict = "adoption failure"
        action = ("Seats are assigned but unused. Fix adoption or cut deep - "
                  "reducing seats alone leaves the same people not using it.")
    elif ratios["active_ratio"] < benchmark * 0.5:
        verdict = "severely over-licensed"
        action = (f"Cut to ~{recommended} seats at renewal. Consider whether the tool "
                  "should survive at all.")
    else:
        verdict = "over-licensed"
        action = f"Cut to ~{recommended} seats at renewal."

    return {
        "name": name, "category": category, "criticality": tool.get("criticality", "core"),
        "annual_cost": round(cost, 2), "cost_per_seat": round(cost_per_seat, 2),
        "seats_purchased": purchased,
        "seats_assigned": int(tool.get("seats_assigned", 0) or 0),
        "seats_active_30d": active,
        "assigned_utilization": ratios["assigned_ratio"],
        "active_utilization": ratios["active_ratio"],
        "adoption_of_assigned": ratios["adoption_ratio"],
        "benchmark": benchmark,
        "verdict": verdict,
        "recommended_seats": recommended,
        "reclaimable_seats": reclaimable,
        "annual_waste": waste,
        "action": action,
    }


def analyse(payload: Dict[str, Any], override: float) -> Dict[str, Any]:
    """Analyse every tool in the dataset and summarise portfolio-level waste."""
    tools = payload.get("tools")
    if not isinstance(tools, list) or not tools:
        raise ValueError("input JSON must contain a non-empty 'tools' array")

    results = [analyse_tool(t, override) for t in tools]
    results.sort(key=lambda r: -r["annual_waste"])

    total_spend = sum(r["annual_cost"] for r in results)
    total_waste = sum(r["annual_waste"] for r in results)
    by_category: Dict[str, Dict[str, float]] = defaultdict(
        lambda: {"spend": 0.0, "waste": 0.0, "tools": 0})
    for r in results:
        bucket = by_category[r["category"]]
        bucket["spend"] += r["annual_cost"]
        bucket["waste"] += r["annual_waste"]
        bucket["tools"] += 1

    headcount = int(payload.get("headcount", 0) or 0)
    return {
        "currency": payload.get("currency", "USD"),
        "tool_count": len(results),
        "total_annual_spend": round(total_spend, 2),
        "total_annual_waste": round(total_waste, 2),
        "waste_pct_of_spend": round(100.0 * total_waste / total_spend, 1) if total_spend else 0.0,
        "spend_per_head": round(total_spend / headcount, 2) if headcount else None,
        "by_category": {
            k: {"spend": round(v["spend"], 2), "waste": round(v["waste"], 2),
                "tools": int(v["tools"]),
                "waste_pct": round(100.0 * v["waste"] / v["spend"], 1) if v["spend"] else 0.0}
            for k, v in sorted(by_category.items(), key=lambda kv: -kv[1]["spend"])},
        "tools": results,
    }


def output(result: Dict[str, Any], fmt: str) -> None:
    """Print the utilisation analysis as JSON or human-readable text."""
    if fmt == "json":
        print(json.dumps(result, indent=2))
        return

    cur = result["currency"]
    print(f"License utilisation across {result['tool_count']} tools")
    print(f"  total spend  {cur} {result['total_annual_spend']:,.0f}")
    print(f"  reclaimable  {cur} {result['total_annual_waste']:,.0f} "
          f"({result['waste_pct_of_spend']}% of spend)")
    if result["spend_per_head"] is not None:
        print(f"  spend/head   {cur} {result['spend_per_head']:,.0f}")

    print("\nBy category:")
    for cat, vals in result["by_category"].items():
        print(f"  {cat:<20} {cur} {vals['spend']:>10,.0f}  waste "
              f"{cur} {vals['waste']:>9,.0f} ({vals['waste_pct']}%)  "
              f"{vals['tools']} tool(s)")

    print("\nPer tool (sorted by reclaimable spend):")
    for t in result["tools"]:
        print(f"  {t['name']} [{t['category']}, {t['criticality']}]")
        print(f"    seats {t['seats_purchased']} purchased / {t['seats_assigned']} assigned "
              f"/ {t['seats_active_30d']} active")
        print(f"    active utilisation {t['active_utilization']:.0%} vs benchmark "
              f"{t['benchmark']:.0%}  -> {t['verdict'].upper()}")
        print(f"    {cur} {t['annual_cost']:,.0f}/yr at {cur} {t['cost_per_seat']:,.0f}/seat; "
              f"reclaimable {cur} {t['annual_waste']:,.0f} "
              f"({t['reclaimable_seats']} seats)")
        print(f"    {t['action']}")


def main() -> None:
    """Parse arguments, run the analysis, and emit the report."""
    parser = argparse.ArgumentParser(
        description="Analyse SaaS license utilisation and quantify wasted seat spend.")
    parser.add_argument("--input", required=True,
                        help="Path to a JSON file with a 'tools' array")
    parser.add_argument("--min-utilization", type=float, default=0.0,
                        help="Override the per-category utilisation benchmark, e.g. 0.70. "
                             "Default 0 uses the built-in category benchmarks.")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                        help="Output format (default: text)")
    args = parser.parse_args()

    if args.min_utilization and not 0.0 < args.min_utilization <= 1.0:
        print("Error: --min-utilization must be between 0 and 1", file=sys.stderr)
        sys.exit(1)

    try:
        with open(args.input, "r", encoding="utf-8") as fh:
            payload = json.load(fh)
    except FileNotFoundError:
        print(f"Error: input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as exc:
        print(f"Error: {args.input} is not valid JSON ({exc})", file=sys.stderr)
        sys.exit(1)

    try:
        result = analyse(payload, args.min_utilization)
    except (ValueError, TypeError, ZeroDivisionError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    output(result, args.format)


if __name__ == "__main__":
    main()
