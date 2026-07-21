#!/usr/bin/env python3
"""
Marketplace Health Scorer — score a two-sided marketplace on liquidity, balance,
take-rate sustainability, repeat rate, and supply density.

Usage:
    python marketplace_health_scorer.py metrics.json
    python marketplace_health_scorer.py metrics.json --json

Input schema (all values per a defined market unit — e.g., a single city / category):
{
  "market_unit": "Bay Area food delivery",
  "active_supply_units": 1200,
  "active_demand_units": 18000,
  "transactions_per_period": 45000,
  "period_days": 30,
  "fill_rate_pct": 88.0,
  "search_to_purchase_pct": 12.0,
  "buyer_repeat_rate_90d_pct": 55.0,
  "supplier_retention_90d_pct": 78.0,
  "take_rate_pct": 22.0,
  "blended_supplier_margin_pct": 12.0,
  "gmv_per_period": 6800000.00
}
"""

import argparse
import json
import sys
from pathlib import Path


def score_dimension(name, value, thresholds, higher_is_better=True):
    """Score 0-100 against tiered thresholds.

    thresholds: list of (threshold_value, score) sorted by threshold ascending.
    """
    sorted_thresholds = sorted(thresholds, key=lambda t: t[0])
    if higher_is_better:
        score = 0
        for thr, sc in sorted_thresholds:
            if value >= thr:
                score = sc
        return score
    else:
        score = 100
        for thr, sc in sorted_thresholds:
            if value > thr:
                score = sc
        return score


def grade(score):
    if score >= 80:
        return "A"
    if score >= 60:
        return "B"
    if score >= 40:
        return "C"
    if score >= 20:
        return "D"
    return "F"


def assess(model):
    market = model.get("market_unit", "(unspecified)")
    supply = float(model.get("active_supply_units", 0))
    demand = float(model.get("active_demand_units", 0))
    txns = float(model.get("transactions_per_period", 0))
    period = float(model.get("period_days", 30))
    fill_rate = float(model.get("fill_rate_pct", 0))
    search_to_buy = float(model.get("search_to_purchase_pct", 0))
    repeat = float(model.get("buyer_repeat_rate_90d_pct", 0))
    supplier_ret = float(model.get("supplier_retention_90d_pct", 0))
    take = float(model.get("take_rate_pct", 0))
    supplier_margin = float(model.get("blended_supplier_margin_pct", 0))
    gmv = float(model.get("gmv_per_period", 0))

    # Liquidity — proxied by transaction density, fill rate, and search-to-purchase
    liquidity_score = (
        score_dimension("fill_rate", fill_rate, [(60, 30), (75, 50), (85, 75), (92, 90)])
        * 0.4
        + score_dimension("search_to_buy", search_to_buy, [(2, 20), (5, 40), (10, 65), (20, 85), (30, 95)])
        * 0.6
    )

    # Demand-supply balance — txns / supply gives utilization signal
    txn_per_supply = txns / supply if supply > 0 else 0
    demand_per_supply = demand / supply if supply > 0 else 0
    balance_score = score_dimension("demand_per_supply", demand_per_supply,
                                    [(2, 30), (5, 55), (10, 75), (20, 90)])
    # Penalty if demand-per-supply is so low (over-supply) or so high (under-supply) it suggests imbalance
    if demand_per_supply > 100:
        balance_score = min(balance_score, 50)  # severe under-supply
    if demand_per_supply < 1:
        balance_score = min(balance_score, 30)

    # Repeat — buyer + supplier retention
    repeat_score = (repeat + supplier_ret) / 2

    # Supply density — txns per supplier per period
    txns_per_supplier_per_period = txns / supply if supply > 0 else 0
    txns_per_supplier_monthly = txns_per_supplier_per_period * (30.0 / period if period > 0 else 1)
    density_score = score_dimension("txns_per_supplier_monthly", txns_per_supplier_monthly,
                                    [(2, 25), (10, 50), (30, 75), (75, 90)])

    # Take rate sustainability — depends on supplier margin
    if supplier_margin <= 0:
        take_score = 20  # supplier loses money — unsustainable
    elif take > supplier_margin * 4:
        take_score = 30  # take rate eats most of supplier margin
    elif take > supplier_margin * 2:
        take_score = 55
    elif take > supplier_margin:
        take_score = 75
    else:
        take_score = 90

    overall = (liquidity_score + balance_score + repeat_score + density_score + take_score) / 5

    return {
        "market_unit": market,
        "scores": {
            "liquidity": round(liquidity_score, 1),
            "supply_demand_balance": round(balance_score, 1),
            "repeat_strength": round(repeat_score, 1),
            "supply_density": round(density_score, 1),
            "take_rate_sustainability": round(take_score, 1),
            "overall": round(overall, 1),
        },
        "grade": grade(overall),
        "metrics_used": {
            "fill_rate_pct": fill_rate,
            "search_to_purchase_pct": search_to_buy,
            "demand_per_supply_ratio": round(demand_per_supply, 2),
            "txns_per_supplier_per_period": round(txns_per_supplier_per_period, 2),
            "buyer_repeat_rate_90d_pct": repeat,
            "supplier_retention_90d_pct": supplier_ret,
            "take_rate_pct": take,
            "blended_supplier_margin_pct": supplier_margin,
        },
    }


def render_human(r):
    s = r["scores"]
    lines = [f"Marketplace Health — {r['market_unit']}"]
    lines.append("=" * 60)
    lines.append("")
    lines.append(f"Overall: {s['overall']} (grade: {r['grade']})")
    lines.append("")
    lines.append("Per-dimension:")
    lines.append(f"  Liquidity:                 {s['liquidity']}")
    lines.append(f"  Supply / demand balance:   {s['supply_demand_balance']}")
    lines.append(f"  Repeat strength:           {s['repeat_strength']}")
    lines.append(f"  Supply density:            {s['supply_density']}")
    lines.append(f"  Take-rate sustainability:  {s['take_rate_sustainability']}")
    lines.append("")
    lines.append("Headline diagnoses:")
    weakest = min(s, key=lambda k: s[k] if k != "overall" else 999)
    lines.append(f"  Weakest dimension: {weakest} ({s[weakest]})")
    if s["take_rate_sustainability"] < 50:
        lines.append("  Take rate likely too high relative to supplier margin — squeezing supplier exit risk.")
    if s["liquidity"] < 50:
        lines.append("  Liquidity weak — buyers searching but not converting; supply may be fragmented.")
    if s["repeat_strength"] < 40:
        lines.append("  Low repeat — risk of off-platform leakage or unmet need.")
    if s["supply_density"] < 30:
        lines.append("  Suppliers transacting too rarely to stay engaged — risk of supplier churn.")
    if s["supply_demand_balance"] < 30:
        lines.append("  Supply / demand seriously imbalanced — focus on the constrained side.")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Score marketplace health.")
    parser.add_argument("metrics", help="Path to metrics.json")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    path = Path(args.metrics)
    if not path.exists():
        print(f"Error: file not found: {path}", file=sys.stderr)
        return 1

    try:
        model = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"Invalid JSON: {exc}", file=sys.stderr)
        return 1

    result = assess(model)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(render_human(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
