#!/usr/bin/env python3
"""
Investment Screener

Screens and ranks investment opportunities by criteria including ROI, risk level,
payback period, growth rate, and efficiency metrics. Produces a composite score
for comparison.

Expected JSON input: {"opportunities": [{"name", "type", "sector", "amount",
  "expected_roi_pct", "risk_level", "payback_months", ...}]}

Usage:
    python investment_screener.py opportunities.json
    python investment_screener.py opportunities.json --min-roi 15
    python investment_screener.py opportunities.json --max-payback 36 --max-risk medium
    python investment_screener.py opportunities.json --sector technology --format json
"""

import argparse
import json
import sys
from typing import Any, Dict, List, Optional, Tuple


RISK_LEVELS = {"low": 1, "medium": 2, "high": 3, "very_high": 4}
RISK_LABELS = {1: "Low", 2: "Medium", 3: "High", 4: "Very High"}


def parse_risk(risk_str: str) -> int:
    """Convert risk string to numeric level."""
    return RISK_LEVELS.get(risk_str.lower().replace(" ", "_").replace("-", "_"), 2)


def score_return(roi_pct: float, risk_level: int) -> float:
    """Score expected return (0-100), risk-adjusted."""
    if roi_pct >= 30:
        base = 90 + min((roi_pct - 30) / 7, 10)
    elif roi_pct >= 20:
        base = 70 + (roi_pct - 20) * 2
    elif roi_pct >= 10:
        base = 50 + (roi_pct - 10) * 2
    elif roi_pct >= 5:
        base = 30 + (roi_pct - 5) * 4
    else:
        base = max(0, roi_pct * 6)

    # Risk adjustment: penalize high risk relative to return
    risk_penalty = (risk_level - 2) * 8  # medium is baseline (0 penalty)
    return max(0, min(100, base - risk_penalty))


def score_risk(risk_level: int, runway_months: Optional[float] = None) -> float:
    """Score risk (0-100, higher is better/lower risk)."""
    risk_base = {1: 90, 2: 70, 3: 45, 4: 20}
    base = risk_base.get(risk_level, 50)

    if runway_months is not None:
        if runway_months >= 18:
            base += 10
        elif runway_months >= 12:
            base += 5
        elif runway_months < 6:
            base -= 15
        else:
            base -= 5

    return max(0, min(100, base))


def score_growth(growth_pct: Optional[float]) -> float:
    """Score revenue growth (0-100)."""
    if growth_pct is None:
        return 50  # neutral if unknown
    if growth_pct >= 100:
        return 90 + min((growth_pct - 100) / 10, 10)
    elif growth_pct >= 50:
        return 70 + (growth_pct - 50) * 0.4
    elif growth_pct >= 20:
        return 50 + (growth_pct - 20) * 0.67
    elif growth_pct >= 0:
        return 30 + growth_pct * 1.0
    else:
        return max(0, 30 + growth_pct)


def score_efficiency(gross_margin_pct: Optional[float], burn_rate: Optional[float],
                     revenue: Optional[float]) -> float:
    """Score operational efficiency (0-100)."""
    scores = []

    if gross_margin_pct is not None:
        if gross_margin_pct >= 75:
            scores.append(90)
        elif gross_margin_pct >= 50:
            scores.append(70)
        elif gross_margin_pct >= 30:
            scores.append(50)
        else:
            scores.append(30)

    if burn_rate is not None and revenue is not None and burn_rate > 0:
        burn_multiple = (burn_rate * 12) / max(revenue, 1)
        if burn_multiple < 1:
            scores.append(90)
        elif burn_multiple < 2:
            scores.append(65)
        else:
            scores.append(35)

    return sum(scores) / len(scores) if scores else 50


def score_payback(payback_months: Optional[float]) -> float:
    """Score payback period (0-100, shorter is better)."""
    if payback_months is None:
        return 50
    if payback_months <= 12:
        return 90 + min((12 - payback_months), 10)
    elif payback_months <= 24:
        return 70 + (24 - payback_months) * 1.67
    elif payback_months <= 36:
        return 50 + (36 - payback_months) * 1.67
    elif payback_months <= 60:
        return 20 + (60 - payback_months) * 1.25
    else:
        return max(0, 20 - (payback_months - 60) * 0.5)


def calculate_composite(opp: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate composite score for an opportunity."""
    risk_level = parse_risk(opp.get("risk_level", "medium"))

    ret_score = score_return(opp.get("expected_roi_pct", 0), risk_level)
    risk_score = score_risk(risk_level, opp.get("runway_months"))
    growth_score = score_growth(opp.get("revenue_growth_pct"))
    eff_score = score_efficiency(
        opp.get("gross_margin_pct"),
        opp.get("burn_rate_monthly"),
        opp.get("revenue"),
    )
    payback_score = score_payback(opp.get("payback_months"))

    # Weighted composite
    composite = (
        ret_score * 0.30
        + risk_score * 0.25
        + growth_score * 0.20
        + eff_score * 0.15
        + payback_score * 0.10
    )

    return {
        "name": opp.get("name", "Unknown"),
        "sector": opp.get("sector", "unknown"),
        "type": opp.get("type", "unknown"),
        "stage": opp.get("stage", "unknown"),
        "amount": opp.get("amount", 0),
        "expected_roi_pct": opp.get("expected_roi_pct", 0),
        "risk_level": RISK_LABELS.get(risk_level, "Unknown"),
        "payback_months": opp.get("payback_months"),
        "scores": {
            "return": round(ret_score, 1),
            "risk": round(risk_score, 1),
            "growth": round(growth_score, 1),
            "efficiency": round(eff_score, 1),
            "payback": round(payback_score, 1),
        },
        "composite_score": round(composite, 1),
        "recommendation": get_recommendation(composite, risk_level),
    }


def get_recommendation(composite: float, risk_level: int) -> str:
    """Generate recommendation based on composite score."""
    if composite >= 80:
        return "STRONG BUY - Excellent opportunity across all dimensions"
    elif composite >= 65:
        return "BUY - Good opportunity, proceed with due diligence"
    elif composite >= 50:
        return "HOLD - Moderate opportunity, investigate further before committing"
    elif composite >= 35:
        return "CAUTION - Below-average opportunity, significant concerns"
    else:
        return "PASS - Poor risk-return profile, not recommended"


def apply_filters(opportunities: List[Dict], args: argparse.Namespace) -> List[Dict]:
    """Apply screening filters to opportunities."""
    filtered = []
    for opp in opportunities:
        if args.min_roi is not None and opp.get("expected_roi_pct", 0) < args.min_roi:
            continue
        if args.max_payback is not None and opp.get("payback_months"):
            if opp["payback_months"] > args.max_payback:
                continue
        if args.max_risk is not None:
            max_risk_val = parse_risk(args.max_risk)
            opp_risk_val = parse_risk(opp.get("risk_level", "medium"))
            if opp_risk_val > max_risk_val:
                continue
        if args.sector is not None:
            if opp.get("sector", "").lower() != args.sector.lower():
                continue
        if args.min_amount is not None and opp.get("amount", 0) < args.min_amount:
            continue
        if args.max_amount is not None and opp.get("amount", 0) > args.max_amount:
            continue
        filtered.append(opp)
    return filtered


def format_currency(amount: float) -> str:
    if amount >= 1_000_000:
        return f"${amount/1_000_000:.1f}M"
    elif amount >= 1_000:
        return f"${amount/1_000:.0f}K"
    return f"${amount:,.0f}"


def print_human(results: List[Dict[str, Any]], total_before_filter: int) -> None:
    """Print screening results in human-readable format."""
    print("=" * 72)
    print("  Investment Screening Results")
    print("=" * 72)
    print(f"\n  Screened: {len(results)} of {total_before_filter} opportunities passed filters\n")

    if not results:
        print("  No opportunities matched the specified criteria.")
        return

    # Sort by composite score descending
    results.sort(key=lambda x: x["composite_score"], reverse=True)

    print(f"  {'Rank':<5} {'Name':<22} {'Score':>6} {'ROI':>7} {'Risk':<10} {'Payback':>8} {'Amount':>10}")
    print(f"  {'-'*5} {'-'*22} {'-'*6} {'-'*7} {'-'*10} {'-'*8} {'-'*10}")

    for i, r in enumerate(results, 1):
        pb = f"{r['payback_months']}mo" if r['payback_months'] else "N/A"
        print(
            f"  {i:<5} {r['name']:<22} {r['composite_score']:>5.1f} "
            f"{r['expected_roi_pct']:>6.1f}% {r['risk_level']:<10} {pb:>8} "
            f"{format_currency(r['amount']):>10}"
        )

    # Detailed view for top 3
    print(f"\n  --- Top Opportunities Detail ---")
    for i, r in enumerate(results[:3], 1):
        print(f"\n  #{i} {r['name']} (Score: {r['composite_score']})")
        print(f"      Sector: {r['sector']} | Stage: {r['stage']} | Type: {r['type']}")
        s = r["scores"]
        print(f"      Return: {s['return']} | Risk: {s['risk']} | Growth: {s['growth']} | "
              f"Efficiency: {s['efficiency']} | Payback: {s['payback']}")
        print(f"      --> {r['recommendation']}")

    print()


def main():
    parser = argparse.ArgumentParser(
        description="Screen and rank investment opportunities by ROI, risk, payback, and more"
    )
    parser.add_argument("file", help="JSON file with investment opportunities")
    parser.add_argument("--format", choices=["human", "json"], default="human", help="Output format")
    parser.add_argument("--min-roi", type=float, help="Minimum expected ROI percentage")
    parser.add_argument("--max-payback", type=float, help="Maximum payback period in months")
    parser.add_argument("--max-risk", choices=["low", "medium", "high", "very_high"],
                        help="Maximum acceptable risk level")
    parser.add_argument("--sector", help="Filter by sector")
    parser.add_argument("--min-amount", type=float, help="Minimum investment amount")
    parser.add_argument("--max-amount", type=float, help="Maximum investment amount")
    parser.add_argument("--top", type=int, help="Show only top N results")
    args = parser.parse_args()

    with open(args.file, "r", encoding="utf-8") as f:
        data = json.load(f)

    opportunities = data.get("opportunities", [])
    if not opportunities:
        print("Error: No opportunities found in input", file=sys.stderr)
        sys.exit(1)

    total = len(opportunities)
    filtered = apply_filters(opportunities, args)
    results = [calculate_composite(opp) for opp in filtered]
    results.sort(key=lambda x: x["composite_score"], reverse=True)

    if args.top:
        results = results[:args.top]

    if args.format == "json":
        print(json.dumps({"total_screened": total, "passed_filters": len(results),
                          "results": results}, indent=2))
    else:
        print_human(results, total)


if __name__ == "__main__":
    main()
