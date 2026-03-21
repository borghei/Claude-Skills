#!/usr/bin/env python3
"""
Tool ROI Calculator

Calculate the ROI and break-even timeline for a free tool based on
traffic, conversion, and cost assumptions.

Usage:
    python tool_roi_calculator.py --build-cost 5000 --monthly-traffic 2000 --conversion-rate 8 --lead-value 50
    python tool_roi_calculator.py --build-cost 5000 --monthly-traffic 2000 --conversion-rate 8 --lead-value 50 --json
"""

import argparse
import json
import math
import sys


def calculate_roi(build_cost: float, monthly_traffic: int,
                  conversion_rate: float, lead_value: float,
                  monthly_hosting: float) -> dict:
    """Calculate free tool ROI."""
    monthly_leads = monthly_traffic * (conversion_rate / 100.0)
    monthly_value = monthly_leads * lead_value
    monthly_net = monthly_value - monthly_hosting

    # Break-even calculation
    if monthly_net > 0:
        breakeven_months = math.ceil(build_cost / monthly_net)
    else:
        breakeven_months = -1  # Never breaks even

    # 12-month projection
    monthly_projections = []
    cumulative_cost = build_cost
    cumulative_revenue = 0

    for month in range(1, 13):
        # Traffic ramp: 30% in month 1, 60% month 2, 100% month 3+
        if month == 1:
            traffic_factor = 0.30
        elif month == 2:
            traffic_factor = 0.60
        else:
            traffic_factor = 1.0

        month_traffic = int(monthly_traffic * traffic_factor)
        month_leads = month_traffic * (conversion_rate / 100.0)
        month_value = month_leads * lead_value
        cumulative_cost += monthly_hosting
        cumulative_revenue += month_value
        net_position = cumulative_revenue - cumulative_cost

        monthly_projections.append({
            "month": month,
            "traffic": month_traffic,
            "leads": round(month_leads, 1),
            "revenue": round(month_value, 2),
            "cumulative_cost": round(cumulative_cost, 2),
            "cumulative_revenue": round(cumulative_revenue, 2),
            "net_position": round(net_position, 2),
            "profitable": net_position > 0,
        })

    # Annual summary
    annual_revenue = sum(m["revenue"] for m in monthly_projections)
    annual_cost = build_cost + (monthly_hosting * 12)
    annual_roi = ((annual_revenue - annual_cost) / annual_cost * 100) if annual_cost > 0 else 0

    # Scenario analysis
    scenarios = []
    for traffic_mult, label in [(0.5, "Conservative (50% traffic)"),
                                 (1.0, "Base case"),
                                 (1.5, "Optimistic (150% traffic)"),
                                 (2.0, "Viral (200% traffic)")]:
        sc_monthly = monthly_traffic * traffic_mult * (conversion_rate / 100.0) * lead_value
        sc_annual = sc_monthly * 12  # Simplified (no ramp)
        sc_roi = ((sc_annual - annual_cost) / annual_cost * 100) if annual_cost > 0 else 0
        sc_breakeven = math.ceil(build_cost / max(0.01, sc_monthly - monthly_hosting))
        scenarios.append({
            "scenario": label,
            "monthly_revenue": round(sc_monthly, 2),
            "annual_revenue": round(sc_annual, 2),
            "annual_roi_pct": round(sc_roi, 1),
            "breakeven_months": sc_breakeven if sc_monthly > monthly_hosting else -1,
        })

    return {
        "inputs": {
            "build_cost": build_cost,
            "monthly_traffic": monthly_traffic,
            "conversion_rate_pct": conversion_rate,
            "lead_value": lead_value,
            "monthly_hosting": monthly_hosting,
        },
        "monthly_metrics": {
            "monthly_leads": round(monthly_leads, 1),
            "monthly_revenue": round(monthly_value, 2),
            "monthly_cost": monthly_hosting,
            "monthly_net": round(monthly_net, 2),
        },
        "annual_summary": {
            "annual_revenue": round(annual_revenue, 2),
            "annual_cost": round(annual_cost, 2),
            "annual_profit": round(annual_revenue - annual_cost, 2),
            "annual_roi_pct": round(annual_roi, 1),
            "breakeven_month": breakeven_months,
        },
        "monthly_projections": monthly_projections,
        "scenarios": scenarios,
        "recommendations": _generate_recommendations(breakeven_months, annual_roi, monthly_leads),
    }


def _generate_recommendations(breakeven: int, roi: float, leads: float) -> list:
    """Generate recommendations."""
    recs = []
    if breakeven <= 0:
        recs.append({
            "priority": "CRITICAL",
            "recommendation": "Tool does not break even. Increase traffic, conversion rate, or lead value -- or reduce build cost.",
        })
    elif breakeven > 6:
        recs.append({
            "priority": "HIGH",
            "recommendation": f"Break-even at month {breakeven} exceeds 6-month target. Consider reducing scope to lower build cost.",
        })
    else:
        recs.append({
            "priority": "INFO",
            "recommendation": f"Break-even at month {breakeven} -- within target. Proceed with build.",
        })

    if leads < 10:
        recs.append({
            "priority": "MEDIUM",
            "recommendation": "Monthly lead volume is low. Consider higher-traffic tool types (calculators, checkers) or broader keyword targeting.",
        })

    recs.append({
        "priority": "MEDIUM",
        "recommendation": "Factor in backlink value (not modeled here). Quality backlinks from tool pages can significantly boost domain authority.",
    })

    return recs


def format_text(result: dict) -> str:
    """Format results as human-readable text."""
    lines = []
    lines.append("=" * 60)
    lines.append("FREE TOOL ROI CALCULATOR")
    lines.append("=" * 60)

    inp = result["inputs"]
    lines.append(f"\n--- Inputs ---")
    lines.append(f"Build Cost:        ${inp['build_cost']:>10,.2f}")
    lines.append(f"Monthly Traffic:   {inp['monthly_traffic']:>10,d}")
    lines.append(f"Conversion Rate:   {inp['conversion_rate_pct']:>10.1f}%")
    lines.append(f"Lead Value:        ${inp['lead_value']:>10,.2f}")
    lines.append(f"Monthly Hosting:   ${inp['monthly_hosting']:>10,.2f}")

    mm = result["monthly_metrics"]
    lines.append(f"\n--- Monthly Metrics (at full traffic) ---")
    lines.append(f"Monthly Leads:     {mm['monthly_leads']:>10.1f}")
    lines.append(f"Monthly Revenue:   ${mm['monthly_revenue']:>10,.2f}")
    lines.append(f"Monthly Net:       ${mm['monthly_net']:>10,.2f}")

    an = result["annual_summary"]
    lines.append(f"\n--- Annual Summary ---")
    lines.append(f"Annual Revenue:    ${an['annual_revenue']:>10,.2f}")
    lines.append(f"Annual Cost:       ${an['annual_cost']:>10,.2f}")
    lines.append(f"Annual Profit:     ${an['annual_profit']:>10,.2f}")
    lines.append(f"Annual ROI:        {an['annual_roi_pct']:>10.1f}%")
    be = an['breakeven_month']
    lines.append(f"Break-Even Month:  {'Never' if be <= 0 else str(be):>10}")

    lines.append(f"\n--- 12-Month Projection ---")
    lines.append(f"{'Month':>6} {'Traffic':>8} {'Leads':>7} {'Revenue':>10} {'Net Pos':>10}")
    for m in result["monthly_projections"]:
        lines.append(
            f"{m['month']:>6d} {m['traffic']:>8,d} {m['leads']:>7.0f} "
            f"${m['revenue']:>8,.0f} ${m['net_position']:>8,.0f}"
        )

    lines.append(f"\n--- Scenarios ---")
    lines.append(f"{'Scenario':<30} {'Monthly':>10} {'Annual':>10} {'ROI':>8} {'B/E':>6}")
    for s in result["scenarios"]:
        be_str = str(s["breakeven_months"]) if s["breakeven_months"] > 0 else "Never"
        lines.append(
            f"{s['scenario']:<30} ${s['monthly_revenue']:>8,.0f} "
            f"${s['annual_revenue']:>8,.0f} {s['annual_roi_pct']:>7.0f}% {be_str:>6}"
        )

    lines.append(f"\n--- Recommendations ---")
    for r in result["recommendations"]:
        lines.append(f"[{r['priority']}] {r['recommendation']}")

    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Calculate ROI and break-even for a free marketing tool."
    )
    parser.add_argument("--build-cost", type=float, required=True,
                        help="Total build cost in dollars")
    parser.add_argument("--monthly-traffic", type=int, required=True,
                        help="Expected monthly sessions after 90 days")
    parser.add_argument("--conversion-rate", type=float, required=True,
                        help="Expected lead conversion rate as percentage")
    parser.add_argument("--lead-value", type=float, required=True,
                        help="Dollar value per captured lead")
    parser.add_argument("--monthly-hosting", type=float, default=50,
                        help="Monthly hosting/maintenance cost (default: 50)")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")

    args = parser.parse_args()

    result = calculate_roi(args.build_cost, args.monthly_traffic,
                           args.conversion_rate, args.lead_value,
                           args.monthly_hosting)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(format_text(result))


if __name__ == "__main__":
    main()
