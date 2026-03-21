#!/usr/bin/env python3
"""Channel Mix Optimizer - Optimize marketing budget allocation across channels.

Analyzes channel performance data (spend, leads, revenue) and recommends
optimal budget reallocation to maximize ROI.

Usage:
    python channel_mix_optimizer.py channels.json
    python channel_mix_optimizer.py channels.json --budget 100000 --json
    python channel_mix_optimizer.py --demo
"""

import argparse
import json
import sys


def analyze_channels(channels, total_budget=None):
    """Analyze channel performance and recommend budget allocation."""
    results = []
    total_spend = sum(ch.get("spend", 0) for ch in channels)
    total_leads = sum(ch.get("leads", 0) for ch in channels)
    total_revenue = sum(ch.get("revenue", 0) for ch in channels)

    if total_budget is None:
        total_budget = total_spend

    for ch in channels:
        name = ch.get("name", ch.get("channel", "Unknown"))
        spend = ch.get("spend", 0)
        leads = ch.get("leads", 0)
        revenue = ch.get("revenue", 0)
        customers = ch.get("customers", 0)
        impressions = ch.get("impressions", 0)
        clicks = ch.get("clicks", 0)

        # Calculate metrics
        cpl = spend / max(leads, 1)
        cac = spend / max(customers, 1) if customers else None
        roas = revenue / max(spend, 1)
        roi = ((revenue - spend) / max(spend, 1)) * 100
        ctr = (clicks / max(impressions, 1)) * 100 if impressions else None
        conversion_rate = (leads / max(clicks, 1)) * 100 if clicks else None
        spend_share = (spend / max(total_spend, 1)) * 100
        revenue_share = (revenue / max(total_revenue, 1)) * 100
        efficiency_index = revenue_share / max(spend_share, 0.1)

        results.append({
            "channel": name,
            "spend": spend,
            "leads": leads,
            "revenue": revenue,
            "customers": customers,
            "cpl": round(cpl, 2),
            "cac": round(cac, 2) if cac else None,
            "roas": round(roas, 2),
            "roi": round(roi, 1),
            "ctr": round(ctr, 2) if ctr else None,
            "conversion_rate": round(conversion_rate, 2) if conversion_rate else None,
            "spend_share": round(spend_share, 1),
            "revenue_share": round(revenue_share, 1),
            "efficiency_index": round(efficiency_index, 2),
        })

    # Rank by efficiency
    results.sort(key=lambda x: x["efficiency_index"], reverse=True)

    # Calculate optimal allocation
    # Weighted by efficiency index
    total_efficiency = sum(r["efficiency_index"] for r in results)
    recommendations = []

    for r in results:
        weight = r["efficiency_index"] / max(total_efficiency, 0.01)
        # Blend current allocation with efficiency-based allocation (70/30)
        current_share = r["spend_share"] / 100
        optimal_share = weight
        recommended_share = (current_share * 0.3 + optimal_share * 0.7)

        recommended_budget = int(total_budget * recommended_share)
        budget_change = recommended_budget - r["spend"]
        change_pct = ((recommended_budget - r["spend"]) / max(r["spend"], 1)) * 100

        # Project ROI at new budget (linear assumption with diminishing returns)
        diminishing_factor = 0.85 if budget_change > 0 else 1.1
        projected_revenue = r["revenue"] * (recommended_budget / max(r["spend"], 1)) * diminishing_factor
        projected_roas = projected_revenue / max(recommended_budget, 1)

        recommendations.append({
            "channel": r["channel"],
            "current_budget": r["spend"],
            "recommended_budget": recommended_budget,
            "budget_change": budget_change,
            "change_pct": round(change_pct, 1),
            "current_roas": r["roas"],
            "projected_roas": round(projected_roas, 2),
            "efficiency_rank": results.index(r) + 1,
            "action": "increase" if budget_change > 0 else ("decrease" if budget_change < 0 else "maintain"),
        })

    # Normalize recommendations to total budget
    total_recommended = sum(r["recommended_budget"] for r in recommendations)
    if total_recommended > 0:
        scale_factor = total_budget / total_recommended
        for r in recommendations:
            r["recommended_budget"] = int(r["recommended_budget"] * scale_factor)
            r["budget_change"] = r["recommended_budget"] - [ch for ch in results if ch["channel"] == r["channel"]][0]["spend"]

    # Summary
    current_total_roas = total_revenue / max(total_spend, 1)
    projected_total_revenue = sum(
        r["projected_roas"] * r["recommended_budget"] for r in recommendations
    )
    projected_total_roas = projected_total_revenue / max(total_budget, 1)

    return {
        "summary": {
            "total_budget": total_budget,
            "current_spend": total_spend,
            "total_leads": total_leads,
            "total_revenue": total_revenue,
            "current_roas": round(current_total_roas, 2),
            "projected_roas": round(projected_total_roas, 2),
            "projected_revenue": round(projected_total_revenue, 2),
            "revenue_improvement": round(
                ((projected_total_revenue - total_revenue) / max(total_revenue, 1)) * 100, 1
            ),
        },
        "channels": results,
        "recommendations": sorted(recommendations, key=lambda x: x["budget_change"], reverse=True),
    }


def get_demo_data():
    return [
        {"name": "Paid Search", "spend": 45000, "leads": 520, "revenue": 180000, "customers": 52, "impressions": 250000, "clicks": 12500},
        {"name": "LinkedIn Ads", "spend": 30000, "leads": 310, "revenue": 145000, "customers": 35, "impressions": 180000, "clicks": 5400},
        {"name": "Email Marketing", "spend": 5000, "leads": 380, "revenue": 120000, "customers": 40, "impressions": 0, "clicks": 0},
        {"name": "Content/SEO", "spend": 12000, "leads": 250, "revenue": 95000, "customers": 28, "impressions": 0, "clicks": 0},
        {"name": "Display Ads", "spend": 15000, "leads": 90, "revenue": 22000, "customers": 8, "impressions": 500000, "clicks": 3500},
        {"name": "Social Organic", "spend": 3000, "leads": 120, "revenue": 38000, "customers": 15, "impressions": 100000, "clicks": 8000},
    ]


def format_report(analysis):
    """Format human-readable report."""
    lines = []
    lines.append("=" * 75)
    lines.append("CHANNEL MIX OPTIMIZATION REPORT")
    lines.append("=" * 75)

    s = analysis["summary"]
    lines.append(f"Total Budget:        ${s['total_budget']:,.0f}")
    lines.append(f"Current ROAS:        {s['current_roas']:.1f}x")
    lines.append(f"Projected ROAS:      {s['projected_roas']:.1f}x")
    lines.append(f"Revenue Improvement: {s['revenue_improvement']:+.1f}%")
    lines.append("")

    # Channel performance
    lines.append("--- CHANNEL PERFORMANCE (ranked by efficiency) ---")
    lines.append(f"{'Channel':<20} {'Spend':>10} {'Revenue':>10} {'ROAS':>6} {'CPL':>8} {'Efficiency':>10}")
    lines.append("-" * 70)
    for ch in analysis["channels"]:
        lines.append(
            f"{ch['channel']:<20} ${ch['spend']:>9,} ${ch['revenue']:>9,} "
            f"{ch['roas']:>5.1f}x ${ch['cpl']:>7,.0f} {ch['efficiency_index']:>10.2f}"
        )
    lines.append("")

    # Recommendations
    lines.append("--- BUDGET RECOMMENDATIONS ---")
    lines.append(f"{'Channel':<20} {'Current':>10} {'Recommended':>12} {'Change':>10} {'Action':>10}")
    lines.append("-" * 65)
    for r in analysis["recommendations"]:
        lines.append(
            f"{r['channel']:<20} ${r['current_budget']:>9,} ${r['recommended_budget']:>11,} "
            f"{r['change_pct']:>+9.0f}% {r['action']:>10}"
        )

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Optimize marketing budget allocation across channels")
    parser.add_argument("input", nargs="?", help="JSON file with channel performance data")
    parser.add_argument("--budget", type=float, help="Total budget to allocate")
    parser.add_argument("--json", action="store_true", dest="json_output", help="Output JSON")
    parser.add_argument("--demo", action="store_true", help="Run with demo data")
    args = parser.parse_args()

    if args.demo:
        channels = get_demo_data()
    elif args.input:
        try:
            with open(args.input, "r", encoding="utf-8") as f:
                data = json.load(f)
            channels = data if isinstance(data, list) else data.get("channels", [])
        except FileNotFoundError:
            print(f"Error: File not found: {args.input}", file=sys.stderr)
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)

    analysis = analyze_channels(channels, args.budget)

    if args.json_output:
        print(json.dumps(analysis, indent=2))
    else:
        print(format_report(analysis))


if __name__ == "__main__":
    main()
