#!/usr/bin/env python3
"""Affiliate Commission Modeler - Model affiliate commission structures and economics.

Calculates per-tier commission economics, lifetime partner value, and compares
flat fee vs recurring percentage commission models.

Usage:
    python affiliate_commission_modeler.py affiliate.json
    python affiliate_commission_modeler.py affiliate.json --format json
"""

import argparse
import json
import sys
from typing import Any


def safe_divide(num: float, den: float, default: float = 0.0) -> float:
    """Safely divide."""
    return num / den if den != 0 else default


DEFAULT_TIERS = [
    {"name": "Standard", "min_conversions": 0, "commission_pct": 20},
    {"name": "Silver", "min_conversions": 10, "commission_pct": 25},
    {"name": "Gold", "min_conversions": 25, "commission_pct": 30},
]


def model_commissions(data: dict) -> dict:
    """Model affiliate commission economics."""
    business = data.get("business", {})
    program = data.get("program", {})
    partners = data.get("partners", [])

    avg_monthly_revenue = business.get("avg_monthly_revenue_per_customer", 0)
    avg_customer_lifetime_months = business.get("avg_customer_lifetime_months", 24)
    avg_ltv = avg_monthly_revenue * avg_customer_lifetime_months
    gross_margin_pct = business.get("gross_margin_pct", 80) / 100

    tiers = program.get("tiers", DEFAULT_TIERS)
    cookie_window_days = program.get("cookie_window_days", 30)
    payment_threshold = program.get("payment_threshold", 50)
    commission_type = program.get("commission_type", "recurring")  # recurring or flat

    flat_fee = program.get("flat_fee_per_conversion", 0)

    # Tier analysis
    tier_analysis = []
    for tier in tiers:
        commission_pct = tier.get("commission_pct", 20) / 100

        if commission_type == "recurring":
            monthly_commission_per_customer = avg_monthly_revenue * commission_pct
            lifetime_commission_per_customer = monthly_commission_per_customer * avg_customer_lifetime_months
            effective_cac = lifetime_commission_per_customer
        else:
            monthly_commission_per_customer = 0
            lifetime_commission_per_customer = flat_fee
            effective_cac = flat_fee

        # Margin after commission
        if commission_type == "recurring":
            margin_after_commission = (avg_monthly_revenue * gross_margin_pct) - monthly_commission_per_customer
            margin_after_commission_pct = safe_divide(margin_after_commission, avg_monthly_revenue) * 100
        else:
            # Flat fee only impacts first month
            margin_after_commission = (avg_monthly_revenue * gross_margin_pct) - safe_divide(flat_fee, avg_customer_lifetime_months)
            margin_after_commission_pct = safe_divide(margin_after_commission, avg_monthly_revenue) * 100

        ltv_after_commission = avg_ltv * gross_margin_pct - lifetime_commission_per_customer
        ltv_cac = safe_divide(avg_ltv * gross_margin_pct, effective_cac) if effective_cac > 0 else float('inf')

        tier_analysis.append({
            "tier_name": tier.get("name", "Unknown"),
            "min_conversions": tier.get("min_conversions", 0),
            "commission_pct": tier.get("commission_pct", 20),
            "monthly_commission_per_customer": round(monthly_commission_per_customer, 2),
            "lifetime_commission_per_customer": round(lifetime_commission_per_customer, 2),
            "effective_cac": round(effective_cac, 2),
            "margin_after_commission_pct": round(margin_after_commission_pct, 1),
            "ltv_after_commission": round(ltv_after_commission, 2),
            "ltv_cac_ratio": round(ltv_cac, 1) if ltv_cac != float('inf') else "Infinite",
            "sustainable": ltv_after_commission > 0,
        })

    # Partner analysis
    partner_analysis = []
    total_partner_revenue = 0
    total_partner_cost = 0

    for partner in partners:
        name = partner.get("name", "Unknown")
        conversions = partner.get("monthly_conversions", 0)
        total_conversions = partner.get("total_conversions", conversions)

        # Find applicable tier
        applicable_tier = tiers[0]
        for tier in tiers:
            if total_conversions >= tier.get("min_conversions", 0):
                applicable_tier = tier

        commission_pct = applicable_tier.get("commission_pct", 20) / 100

        if commission_type == "recurring":
            monthly_payout = conversions * avg_monthly_revenue * commission_pct
            # Also paying on retained customers from previous months
            retained_customers = partner.get("active_customers", conversions)
            total_monthly_payout = retained_customers * avg_monthly_revenue * commission_pct
        else:
            monthly_payout = conversions * flat_fee
            total_monthly_payout = monthly_payout

        monthly_revenue_generated = conversions * avg_monthly_revenue
        annual_payout = total_monthly_payout * 12
        annual_revenue = monthly_revenue_generated * 12

        total_partner_revenue += annual_revenue
        total_partner_cost += annual_payout

        partner_analysis.append({
            "name": name,
            "tier": applicable_tier.get("name", "Standard"),
            "monthly_conversions": conversions,
            "total_conversions": total_conversions,
            "monthly_revenue_generated": round(monthly_revenue_generated, 2),
            "monthly_payout": round(total_monthly_payout, 2),
            "annual_payout": round(annual_payout, 2),
            "roi": round(safe_divide(annual_revenue, annual_payout), 1) if annual_payout > 0 else "Infinite",
        })

    # Model comparison (recurring vs flat)
    model_comparison = None
    if commission_type == "recurring":
        # Compare against flat fee equivalent
        # What flat fee gives same total payout as recurring over lifetime?
        recurring_lifetime = avg_monthly_revenue * (tiers[0]["commission_pct"] / 100) * avg_customer_lifetime_months
        model_comparison = {
            "current_model": "Recurring",
            "current_lifetime_cost": round(recurring_lifetime, 2),
            "equivalent_flat_fee": round(recurring_lifetime, 2),
            "note": f"A ${recurring_lifetime:.0f} flat fee equals your standard-tier recurring commission over {avg_customer_lifetime_months} months",
            "recurring_advantage": "Aligns partner incentives with retention (they benefit from your retention)",
            "flat_advantage": "Lower total cost if customers retain longer than expected; simpler accounting",
        }

    return {
        "summary": {
            "commission_type": commission_type,
            "tier_count": len(tiers),
            "partner_count": len(partners),
            "avg_ltv": round(avg_ltv, 2),
            "cookie_window_days": cookie_window_days,
            "total_annual_partner_revenue": round(total_partner_revenue, 2),
            "total_annual_partner_cost": round(total_partner_cost, 2),
            "program_roi": round(safe_divide(total_partner_revenue, total_partner_cost), 1) if total_partner_cost > 0 else "N/A",
        },
        "tier_analysis": tier_analysis,
        "partner_analysis": partner_analysis,
        "model_comparison": model_comparison,
    }


def format_text(result: dict) -> str:
    """Format as human-readable text."""
    lines = []
    s = result["summary"]

    lines.append("=" * 60)
    lines.append("AFFILIATE COMMISSION MODEL")
    lines.append("=" * 60)
    lines.append("")
    lines.append(f"Commission Type: {s['commission_type'].title()}")
    lines.append(f"Tiers: {s['tier_count']}  |  Partners: {s['partner_count']}")
    lines.append(f"Avg Customer LTV: ${s['avg_ltv']:,.2f}")
    lines.append(f"Cookie Window: {s['cookie_window_days']} days")
    lines.append(f"Program ROI: {s['program_roi']}x" if isinstance(s['program_roi'], (int, float)) else f"Program ROI: {s['program_roi']}")
    lines.append("")

    lines.append("-" * 60)
    lines.append("TIER ECONOMICS")
    lines.append("-" * 60)
    for tier in result["tier_analysis"]:
        sustainable = "OK" if tier["sustainable"] else "UNSUSTAINABLE"
        lines.append(f"\n  {tier['tier_name']} ({tier['commission_pct']}% | {tier['min_conversions']}+ conversions)")
        lines.append(f"    Commission/customer/mo: ${tier['monthly_commission_per_customer']:,.2f}")
        lines.append(f"    Lifetime commission:    ${tier['lifetime_commission_per_customer']:,.2f}")
        lines.append(f"    Margin after commission: {tier['margin_after_commission_pct']:.1f}%")
        ltv_cac = tier['ltv_cac_ratio']
        lines.append(f"    LTV:CAC:                {ltv_cac}:1" if isinstance(ltv_cac, (int, float)) else f"    LTV:CAC:                {ltv_cac}")
        lines.append(f"    Status:                 {sustainable}")

    if result["partner_analysis"]:
        lines.append("")
        lines.append("-" * 60)
        lines.append("PARTNER PERFORMANCE")
        lines.append("-" * 60)
        for p in result["partner_analysis"]:
            roi_str = f"{p['roi']}x" if isinstance(p['roi'], (int, float)) else p['roi']
            lines.append(f"  {p['name']} [{p['tier']}]: {p['monthly_conversions']} conv/mo | ${p['monthly_payout']:,.0f}/mo payout | ROI: {roi_str}")

    if result.get("model_comparison"):
        mc = result["model_comparison"]
        lines.append("")
        lines.append("-" * 40)
        lines.append("MODEL COMPARISON")
        lines.append("-" * 40)
        lines.append(f"  Current: {mc['current_model']}")
        lines.append(f"  Lifetime cost/customer: ${mc['current_lifetime_cost']:,.2f}")
        lines.append(f"  Equivalent flat fee: ${mc['equivalent_flat_fee']:,.2f}")
        lines.append(f"  Recurring advantage: {mc['recurring_advantage']}")
        lines.append(f"  Flat advantage: {mc['flat_advantage']}")

    lines.append("")
    return "\n".join(lines)


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Model affiliate commission structures and economics."
    )
    parser.add_argument(
        "input_file",
        help="Path to JSON file with affiliate program data",
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

    result = model_commissions(data)

    if args.format == "json":
        print(json.dumps(result, indent=2))
    else:
        print(format_text(result))


if __name__ == "__main__":
    main()
