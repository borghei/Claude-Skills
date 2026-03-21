#!/usr/bin/env python3
"""Popup ROI Estimator - Estimate revenue impact of popup lead capture.

Models lead volume, conversion pipeline, and customer lifetime value to estimate
popup program ROI. Compares popup-sourced leads against other acquisition channels.

Usage:
    python popup_roi_estimator.py roi_data.json
    python popup_roi_estimator.py roi_data.json --format json
"""

import argparse
import json
import sys
from typing import Any


def safe_divide(num: float, den: float, default: float = 0.0) -> float:
    """Safely divide two numbers."""
    return num / den if den != 0 else default


def estimate_popup_roi(data: dict) -> dict:
    """Estimate ROI from popup lead capture program."""
    popup = data.get("popup_performance", {})
    business = data.get("business_metrics", {})
    channels = data.get("other_channels", [])

    # Core popup metrics
    monthly_visitors = popup.get("monthly_visitors", 0)
    popup_view_rate = popup.get("popup_view_rate_pct", 50) / 100
    popup_conversion_rate = popup.get("popup_conversion_rate_pct", 3) / 100
    lead_to_customer_rate = popup.get("lead_to_customer_rate_pct", 5) / 100

    # Business metrics
    avg_ltv = business.get("avg_customer_ltv", 0)
    avg_order_value = business.get("avg_order_value", 0)
    monthly_popup_cost = business.get("monthly_popup_tool_cost", 0)

    # Calculate pipeline
    monthly_impressions = int(monthly_visitors * popup_view_rate)
    monthly_leads = int(monthly_impressions * popup_conversion_rate)
    monthly_customers = int(monthly_leads * lead_to_customer_rate)

    # Revenue calculation
    if avg_ltv > 0:
        monthly_revenue = monthly_customers * avg_ltv
        revenue_metric = "LTV-based"
    elif avg_order_value > 0:
        monthly_revenue = monthly_customers * avg_order_value
        revenue_metric = "AOV-based"
    else:
        monthly_revenue = 0
        revenue_metric = "No revenue metric provided"

    annual_revenue = monthly_revenue * 12
    annual_cost = monthly_popup_cost * 12

    # Cost per lead and CAC
    cost_per_lead = safe_divide(monthly_popup_cost, monthly_leads)
    popup_cac = safe_divide(monthly_popup_cost, monthly_customers)

    # ROI
    monthly_profit = monthly_revenue - monthly_popup_cost
    annual_profit = annual_revenue - annual_cost
    roi_pct = safe_divide(annual_profit, annual_cost) * 100

    popup_analysis = {
        "pipeline": {
            "monthly_visitors": monthly_visitors,
            "monthly_impressions": monthly_impressions,
            "monthly_leads": monthly_leads,
            "monthly_customers": monthly_customers,
            "popup_view_rate_pct": round(popup_view_rate * 100, 2),
            "popup_conversion_rate_pct": round(popup_conversion_rate * 100, 2),
            "lead_to_customer_rate_pct": round(lead_to_customer_rate * 100, 2),
        },
        "revenue": {
            "revenue_metric": revenue_metric,
            "monthly_revenue": round(monthly_revenue, 2),
            "annual_revenue": round(annual_revenue, 2),
            "monthly_cost": round(monthly_popup_cost, 2),
            "annual_cost": round(annual_cost, 2),
            "monthly_profit": round(monthly_profit, 2),
            "annual_profit": round(annual_profit, 2),
            "roi_pct": round(roi_pct, 1),
        },
        "unit_economics": {
            "cost_per_lead": round(cost_per_lead, 2),
            "popup_cac": round(popup_cac, 2),
            "ltv_to_cac_ratio": round(safe_divide(avg_ltv, popup_cac), 2) if popup_cac > 0 else "N/A",
        },
    }

    # Channel comparison
    channel_comparison = []
    for ch in channels:
        ch_leads = ch.get("monthly_leads", 0)
        ch_cost = ch.get("monthly_cost", 0)
        ch_customers = ch.get("monthly_customers", 0)
        ch_cpl = safe_divide(ch_cost, ch_leads)
        ch_cac = safe_divide(ch_cost, ch_customers)
        ch_ltv_cac = safe_divide(avg_ltv, ch_cac) if ch_cac > 0 else 0

        channel_comparison.append({
            "channel": ch.get("name", "Unknown"),
            "monthly_leads": ch_leads,
            "monthly_customers": ch_customers,
            "cost_per_lead": round(ch_cpl, 2),
            "cac": round(ch_cac, 2),
            "ltv_to_cac": round(ch_ltv_cac, 2),
        })

    # Add popup as a channel for comparison
    channel_comparison.insert(0, {
        "channel": "Popup Lead Capture",
        "monthly_leads": monthly_leads,
        "monthly_customers": monthly_customers,
        "cost_per_lead": round(cost_per_lead, 2),
        "cac": round(popup_cac, 2),
        "ltv_to_cac": round(safe_divide(avg_ltv, popup_cac), 2) if popup_cac > 0 else 0,
    })

    # Improvement scenarios
    scenarios = []
    for improvement_name, new_rate in [
        ("Optimized copy (+50% conversion)", popup_conversion_rate * 1.5),
        ("Added countdown timer (+46% per benchmarks)", popup_conversion_rate * 1.46),
        ("Gamified popup (+3x per benchmarks)", popup_conversion_rate * 3),
    ]:
        new_leads = int(monthly_impressions * new_rate)
        new_customers = int(new_leads * lead_to_customer_rate)
        new_revenue = new_customers * (avg_ltv if avg_ltv > 0 else avg_order_value)
        scenarios.append({
            "scenario": improvement_name,
            "new_conversion_rate_pct": round(new_rate * 100, 2),
            "monthly_leads": new_leads,
            "monthly_customers": new_customers,
            "monthly_revenue": round(new_revenue, 2),
            "incremental_monthly_revenue": round(new_revenue - monthly_revenue, 2),
        })

    return {
        "popup_analysis": popup_analysis,
        "channel_comparison": channel_comparison,
        "improvement_scenarios": scenarios,
    }


def format_text(result: dict) -> str:
    """Format ROI estimate as human-readable text."""
    lines = []
    pa = result["popup_analysis"]

    lines.append("=" * 60)
    lines.append("POPUP ROI ESTIMATE")
    lines.append("=" * 60)
    lines.append("")

    p = pa["pipeline"]
    lines.append("-" * 40)
    lines.append("LEAD PIPELINE")
    lines.append("-" * 40)
    lines.append(f"  Monthly Visitors:    {p['monthly_visitors']:>10,}")
    lines.append(f"  Popup Impressions:   {p['monthly_impressions']:>10,}  ({p['popup_view_rate_pct']}% view rate)")
    lines.append(f"  Leads Captured:      {p['monthly_leads']:>10,}  ({p['popup_conversion_rate_pct']}% conversion)")
    lines.append(f"  New Customers:       {p['monthly_customers']:>10,}  ({p['lead_to_customer_rate_pct']}% lead-to-customer)")
    lines.append("")

    r = pa["revenue"]
    lines.append("-" * 40)
    lines.append(f"REVENUE ({r['revenue_metric']})")
    lines.append("-" * 40)
    lines.append(f"  Monthly Revenue:     ${r['monthly_revenue']:>12,.2f}")
    lines.append(f"  Annual Revenue:      ${r['annual_revenue']:>12,.2f}")
    lines.append(f"  Monthly Cost:        ${r['monthly_cost']:>12,.2f}")
    lines.append(f"  Annual Profit:       ${r['annual_profit']:>12,.2f}")
    lines.append(f"  ROI:                 {r['roi_pct']:>12.1f}%")
    lines.append("")

    u = pa["unit_economics"]
    lines.append("-" * 40)
    lines.append("UNIT ECONOMICS")
    lines.append("-" * 40)
    lines.append(f"  Cost per Lead:       ${u['cost_per_lead']:>12,.2f}")
    lines.append(f"  Popup CAC:           ${u['popup_cac']:>12,.2f}")
    lines.append(f"  LTV:CAC Ratio:       {u['ltv_to_cac_ratio']}:1" if isinstance(u['ltv_to_cac_ratio'], (int, float)) else f"  LTV:CAC Ratio:       {u['ltv_to_cac_ratio']}")
    lines.append("")

    if result["channel_comparison"]:
        lines.append("-" * 40)
        lines.append("CHANNEL COMPARISON")
        lines.append("-" * 40)
        for ch in result["channel_comparison"]:
            lines.append(f"  {ch['channel']:<25} Leads: {ch['monthly_leads']:>5,}  CAC: ${ch['cac']:>8,.2f}  LTV:CAC: {ch['ltv_to_cac']:.1f}x")
        lines.append("")

    if result["improvement_scenarios"]:
        lines.append("-" * 40)
        lines.append("IMPROVEMENT SCENARIOS")
        lines.append("-" * 40)
        for sc in result["improvement_scenarios"]:
            lines.append(f"\n  {sc['scenario']}")
            lines.append(f"    Conv Rate: {sc['new_conversion_rate_pct']}%  |  Leads: {sc['monthly_leads']:,}  |  Revenue: ${sc['monthly_revenue']:,.2f}  |  Uplift: ${sc['incremental_monthly_revenue']:+,.2f}/mo")

    lines.append("")
    return "\n".join(lines)


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Estimate revenue impact of popup lead capture program."
    )
    parser.add_argument(
        "input_file",
        help="Path to JSON file with popup performance and revenue data",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    args = parser.parse_args()

    try:
        with open(args.input_file, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found: {args.input_file}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)

    result = estimate_popup_roi(data)

    if args.format == "json":
        print(json.dumps(result, indent=2))
    else:
        print(format_text(result))


if __name__ == "__main__":
    main()
