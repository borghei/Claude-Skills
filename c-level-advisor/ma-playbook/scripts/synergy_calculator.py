#!/usr/bin/env python3
"""Synergy Calculator - Calculate and track revenue and cost synergies for M&A.

Provides confidence-weighted projections for revenue synergies (cross-sell, upsell,
market expansion) and cost synergies (headcount, tools, infrastructure). Outputs
phased realization timeline.

Usage:
    python synergy_calculator.py --revenue-synergies 500000 --cost-synergies 200000 --confidence 0.7 --timeline-months 24
    python synergy_calculator.py --revenue-synergies 1000000 --cost-synergies 500000 --confidence 0.6 --timeline-months 18 --deal-value 5000000 --json
"""

import argparse
import json
import sys
from datetime import datetime

SYNERGY_TYPES = {
    "revenue": {
        "categories": [
            {"name": "Cross-sell to acquired customer base", "typical_pct": 0.30, "realization_months": "6-18"},
            {"name": "Upsell combined product to existing customers", "typical_pct": 0.25, "realization_months": "9-24"},
            {"name": "New market access / geographic expansion", "typical_pct": 0.25, "realization_months": "12-24"},
            {"name": "Pricing power from combined offering", "typical_pct": 0.10, "realization_months": "6-12"},
            {"name": "Combined brand / reputation leverage", "typical_pct": 0.10, "realization_months": "12-36"}
        ],
        "typical_confidence_discount": 0.50,
        "warning": "Revenue synergies are historically overestimated by 30-50%"
    },
    "cost": {
        "categories": [
            {"name": "Headcount optimization (overlapping roles)", "typical_pct": 0.35, "realization_months": "1-6"},
            {"name": "Tool and vendor consolidation", "typical_pct": 0.20, "realization_months": "3-12"},
            {"name": "Infrastructure consolidation", "typical_pct": 0.20, "realization_months": "6-18"},
            {"name": "G&A overhead reduction", "typical_pct": 0.15, "realization_months": "3-9"},
            {"name": "Procurement leverage", "typical_pct": 0.10, "realization_months": "6-12"}
        ],
        "typical_confidence_discount": 0.75,
        "warning": "Cost synergies are more reliable but require execution discipline"
    }
}

REALIZATION_PHASES = [
    {"phase": 1, "name": "Quick Wins", "months": "0-3", "typical_pct": 0.15, "focus": "Tool consolidation, obvious overlaps, procurement wins"},
    {"phase": 2, "name": "Integration", "months": "3-6", "typical_pct": 0.25, "focus": "Headcount optimization, process merge, initial cross-sell"},
    {"phase": 3, "name": "Optimization", "months": "6-12", "typical_pct": 0.35, "focus": "Revenue synergies begin, infrastructure consolidation, combined product"},
    {"phase": 4, "name": "Full Realization", "months": "12-24", "typical_pct": 0.25, "focus": "Market expansion, full revenue synergies, pricing optimization"}
]


def calculate_synergies(revenue_synergies, cost_synergies, confidence, timeline_months, deal_value=None):
    # Confidence-weighted projections
    revenue_weighted = round(revenue_synergies * confidence * SYNERGY_TYPES["revenue"]["typical_confidence_discount"])
    cost_weighted = round(cost_synergies * confidence * SYNERGY_TYPES["cost"]["typical_confidence_discount"])
    total_raw = revenue_synergies + cost_synergies
    total_weighted = revenue_weighted + cost_weighted

    # Scenario modeling
    scenarios = {
        "optimistic": {
            "revenue": round(revenue_synergies * 1.0),
            "cost": round(cost_synergies * 1.0),
            "total": round(revenue_synergies + cost_synergies),
            "probability": f"{int(confidence * 30)}%"
        },
        "base": {
            "revenue": revenue_weighted,
            "cost": cost_weighted,
            "total": total_weighted,
            "probability": f"{int(confidence * 100)}%"
        },
        "conservative": {
            "revenue": round(revenue_synergies * confidence * 0.3),
            "cost": round(cost_synergies * confidence * 0.6),
            "total": round(revenue_synergies * confidence * 0.3 + cost_synergies * confidence * 0.6),
            "probability": f"{int(min(95, confidence * 100 + 20))}%"
        }
    }

    # Phased realization timeline
    phases = []
    cumulative = 0
    for phase in REALIZATION_PHASES:
        phase_amount = round(total_weighted * phase["typical_pct"])
        cumulative += phase_amount
        phases.append({
            "phase": phase["phase"],
            "name": phase["name"],
            "months": phase["months"],
            "amount": phase_amount,
            "cumulative": cumulative,
            "focus": phase["focus"],
            "pct_of_total": f"{int(phase['typical_pct'] * 100)}%"
        })

    # Revenue synergy breakdown
    revenue_breakdown = []
    for cat in SYNERGY_TYPES["revenue"]["categories"]:
        revenue_breakdown.append({
            "category": cat["name"],
            "estimated_amount": round(revenue_synergies * cat["typical_pct"]),
            "weighted_amount": round(revenue_weighted * cat["typical_pct"]),
            "realization_timeline": cat["realization_months"]
        })

    # Cost synergy breakdown
    cost_breakdown = []
    for cat in SYNERGY_TYPES["cost"]["categories"]:
        cost_breakdown.append({
            "category": cat["name"],
            "estimated_amount": round(cost_synergies * cat["typical_pct"]),
            "weighted_amount": round(cost_weighted * cat["typical_pct"]),
            "realization_timeline": cat["realization_months"]
        })

    # ROI if deal value provided
    roi_analysis = None
    if deal_value and deal_value > 0:
        annual_synergy = total_weighted * (12 / timeline_months) if timeline_months > 0 else 0
        payback_months = round(deal_value / (total_weighted / timeline_months)) if total_weighted > 0 else 999
        roi_pct = round((total_weighted / deal_value) * 100, 1) if deal_value > 0 else 0
        roi_analysis = {
            "deal_value": deal_value,
            "total_synergies_over_period": total_weighted,
            "annualized_synergies": round(annual_synergy),
            "payback_months": payback_months,
            "roi_percentage": roi_pct,
            "synergy_as_pct_of_deal": round(total_weighted / deal_value * 100, 1)
        }

    return {
        "calculation_date": datetime.now().strftime("%Y-%m-%d"),
        "inputs": {
            "revenue_synergies_raw": revenue_synergies,
            "cost_synergies_raw": cost_synergies,
            "confidence_level": confidence,
            "timeline_months": timeline_months,
            "deal_value": deal_value
        },
        "summary": {
            "total_raw": total_raw,
            "total_confidence_weighted": total_weighted,
            "revenue_weighted": revenue_weighted,
            "cost_weighted": cost_weighted,
            "confidence_discount_applied": f"Revenue: {int(confidence * SYNERGY_TYPES['revenue']['typical_confidence_discount'] * 100)}%, Cost: {int(confidence * SYNERGY_TYPES['cost']['typical_confidence_discount'] * 100)}%"
        },
        "scenarios": scenarios,
        "revenue_breakdown": revenue_breakdown,
        "cost_breakdown": cost_breakdown,
        "realization_phases": phases,
        "roi_analysis": roi_analysis,
        "warnings": [
            SYNERGY_TYPES["revenue"]["warning"],
            SYNERGY_TYPES["cost"]["warning"],
            f"Timeline assumes {timeline_months} months; delays common in first 6 months",
            "Track synergies quarterly with specific metrics and owners"
        ]
    }


def print_human(result):
    print(f"\n{'='*70}")
    print(f"SYNERGY CALCULATION")
    print(f"Date: {result['calculation_date']}")
    print(f"{'='*70}\n")

    s = result["summary"]
    print(f"SUMMARY:")
    print(f"  Total Raw Estimate:        ${s['total_raw']:>12,}")
    print(f"  Confidence-Weighted Total:  ${s['total_confidence_weighted']:>12,}")
    print(f"  Revenue Synergies (weighted): ${s['revenue_weighted']:>10,}")
    print(f"  Cost Synergies (weighted):    ${s['cost_weighted']:>10,}")
    print(f"  Discount Applied: {s['confidence_discount_applied']}\n")

    print("SCENARIOS:")
    print("-" * 50)
    for name, sc in result["scenarios"].items():
        print(f"  {name.upper():<15s} ${sc['total']:>10,}  (probability: {sc['probability']})")

    print(f"\nREVENUE SYNERGY BREAKDOWN:")
    print("-" * 60)
    for r in result["revenue_breakdown"]:
        print(f"  ${r['weighted_amount']:>8,}  {r['category']:<45s}  ({r['realization_timeline']})")

    print(f"\nCOST SYNERGY BREAKDOWN:")
    print("-" * 60)
    for c in result["cost_breakdown"]:
        print(f"  ${c['weighted_amount']:>8,}  {c['category']:<45s}  ({c['realization_timeline']})")

    print(f"\nREALIZATION TIMELINE:")
    print("-" * 60)
    for p in result["realization_phases"]:
        print(f"  Phase {p['phase']}: {p['name']:<20s} Months {p['months']:<8s} ${p['amount']:>8,}  (cumulative: ${p['cumulative']:>10,})")

    if result["roi_analysis"]:
        roi = result["roi_analysis"]
        print(f"\nROI ANALYSIS:")
        print(f"  Deal Value:         ${roi['deal_value']:>12,}")
        print(f"  Total Synergies:    ${roi['total_synergies_over_period']:>12,} ({roi['synergy_as_pct_of_deal']}% of deal)")
        print(f"  Annualized:         ${roi['annualized_synergies']:>12,}")
        print(f"  Payback:            {roi['payback_months']} months")

    print(f"\nWARNINGS:")
    for w in result["warnings"]:
        print(f"  [!] {w}")
    print()


def main():
    parser = argparse.ArgumentParser(description="Calculate M&A synergies with confidence weighting")
    parser.add_argument("--revenue-synergies", type=float, required=True, help="Estimated revenue synergies ($)")
    parser.add_argument("--cost-synergies", type=float, required=True, help="Estimated cost synergies ($)")
    parser.add_argument("--confidence", type=float, required=True, help="Confidence level (0.0-1.0)")
    parser.add_argument("--timeline-months", type=int, required=True, help="Realization timeline in months")
    parser.add_argument("--deal-value", type=float, default=None, help="Deal value for ROI calculation ($)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    if not 0 < args.confidence <= 1.0:
        print("Error: Confidence must be between 0 and 1.0", file=sys.stderr)
        sys.exit(1)

    result = calculate_synergies(args.revenue_synergies, args.cost_synergies, args.confidence, args.timeline_months, args.deal_value)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print_human(result)


if __name__ == "__main__":
    main()
