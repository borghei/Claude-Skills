#!/usr/bin/env python3
"""Referral Economics Calculator - Model referral program economics and ROI.

Calculates reward sizing, K-factor, referral CAC, ROI projections, and break-even
analysis. Compares double-sided vs single-sided reward structures.

Usage:
    python referral_economics_calculator.py program.json
    python referral_economics_calculator.py program.json --format json
"""

import argparse
import json
import sys
from typing import Any


def safe_divide(num: float, den: float, default: float = 0.0) -> float:
    """Safely divide."""
    return num / den if den != 0 else default


def calculate_k_factor(avg_invitations: float, invitation_conversion_rate: float) -> float:
    """Calculate viral coefficient (K-factor)."""
    return avg_invitations * invitation_conversion_rate


def rate_k_factor(k: float) -> str:
    """Rate K-factor against benchmarks."""
    if k >= 1.0:
        return "Viral (exponential growth)"
    elif k >= 0.7:
        return "Strong referral contribution"
    elif k >= 0.3:
        return "Moderate referral contribution"
    elif k >= 0.1:
        return "Weak -- program needs optimization"
    else:
        return "Negligible -- fundamental redesign needed"


def model_economics(data: dict) -> dict:
    """Model referral program economics."""
    program = data.get("program", {})
    business = data.get("business", {})

    # Business metrics
    avg_ltv = business.get("avg_customer_ltv", 0)
    avg_first_payment = business.get("avg_first_payment", 0)
    other_cac = business.get("other_channel_cac", 0)
    active_users = business.get("active_users", 0)
    avg_monthly_revenue = business.get("avg_monthly_revenue_per_customer", 0)

    # Program metrics
    referrer_reward = program.get("referrer_reward", 0)
    referred_reward = program.get("referred_reward", 0)
    is_double_sided = referred_reward > 0
    reward_type = program.get("reward_type", "credit")  # credit, cash, discount, feature

    avg_invitations = program.get("avg_invitations_per_user", 0)
    invitation_conversion = program.get("invitation_conversion_rate", 0)
    active_referrer_pct = program.get("active_referrer_pct", 5) / 100

    # K-factor
    k_factor = calculate_k_factor(avg_invitations, invitation_conversion)
    k_rating = rate_k_factor(k_factor)

    # Cost per referral
    total_reward_per_referral = referrer_reward + referred_reward
    referral_cac = total_reward_per_referral  # Assuming 1:1 reward to acquisition

    # CAC comparison
    cac_savings_pct = safe_divide(other_cac - referral_cac, other_cac) * 100

    # LTV:CAC for referrals
    ltv_cac_ratio = safe_divide(avg_ltv, referral_cac) if referral_cac > 0 else float('inf')

    # Maximum sustainable reward
    target_referral_cac_pct = 15  # 15% of LTV
    max_reward = avg_ltv * (target_referral_cac_pct / 100)
    if is_double_sided:
        max_per_side = max_reward / 2
    else:
        max_per_side = max_reward

    # Revenue projections
    active_referrers = int(active_users * active_referrer_pct)
    monthly_referrals_sent = active_referrers * avg_invitations
    monthly_new_customers = int(monthly_referrals_sent * invitation_conversion)
    monthly_referral_revenue = monthly_new_customers * avg_monthly_revenue
    annual_referral_revenue = monthly_referral_revenue * 12
    monthly_reward_cost = monthly_new_customers * total_reward_per_referral
    annual_reward_cost = monthly_reward_cost * 12

    # ROI
    annual_profit = annual_referral_revenue - annual_reward_cost
    roi_pct = safe_divide(annual_profit, annual_reward_cost) * 100

    # Referral revenue share
    total_monthly_revenue = active_users * avg_monthly_revenue if avg_monthly_revenue > 0 else 1
    referral_revenue_share = safe_divide(monthly_referral_revenue, total_monthly_revenue) * 100

    # Double-sided vs single-sided comparison
    comparison = None
    if is_double_sided:
        # Model what single-sided would look like (assume 40% lower conversion)
        single_conversion = invitation_conversion * 0.6
        single_new_customers = int(monthly_referrals_sent * single_conversion)
        single_cost = single_new_customers * referrer_reward
        single_revenue = single_new_customers * avg_monthly_revenue * 12

        comparison = {
            "double_sided": {
                "annual_customers": monthly_new_customers * 12,
                "annual_revenue": round(annual_referral_revenue, 2),
                "annual_cost": round(annual_reward_cost, 2),
                "annual_profit": round(annual_profit, 2),
            },
            "single_sided_estimate": {
                "annual_customers": single_new_customers * 12,
                "annual_revenue": round(single_revenue, 2),
                "annual_cost": round(single_cost * 12, 2),
                "annual_profit": round(single_revenue - single_cost * 12, 2),
                "note": "Estimated at 40% lower conversion rate without referred reward",
            },
        }

    return {
        "k_factor": {
            "value": round(k_factor, 3),
            "rating": k_rating,
            "avg_invitations": avg_invitations,
            "invitation_conversion_rate": invitation_conversion,
        },
        "unit_economics": {
            "referral_cac": round(referral_cac, 2),
            "other_channel_cac": other_cac,
            "cac_savings_pct": round(cac_savings_pct, 1),
            "ltv_cac_ratio": round(ltv_cac_ratio, 1) if ltv_cac_ratio != float('inf') else "Infinite",
            "max_sustainable_reward": round(max_reward, 2),
            "max_per_side": round(max_per_side, 2),
            "current_reward_sustainable": total_reward_per_referral <= max_reward,
        },
        "projections": {
            "active_referrers": active_referrers,
            "monthly_referrals_sent": int(monthly_referrals_sent),
            "monthly_new_customers": monthly_new_customers,
            "monthly_referral_revenue": round(monthly_referral_revenue, 2),
            "annual_referral_revenue": round(annual_referral_revenue, 2),
            "monthly_reward_cost": round(monthly_reward_cost, 2),
            "annual_reward_cost": round(annual_reward_cost, 2),
            "annual_profit": round(annual_profit, 2),
            "roi_pct": round(roi_pct, 1),
            "referral_revenue_share_pct": round(referral_revenue_share, 1),
        },
        "reward_structure": {
            "type": "double_sided" if is_double_sided else "single_sided",
            "referrer_reward": referrer_reward,
            "referred_reward": referred_reward,
            "total_per_referral": total_reward_per_referral,
            "reward_type": reward_type,
        },
        "comparison": comparison,
    }


def format_text(result: dict) -> str:
    """Format as human-readable text."""
    lines = []

    lines.append("=" * 60)
    lines.append("REFERRAL PROGRAM ECONOMICS")
    lines.append("=" * 60)
    lines.append("")

    # K-factor
    kf = result["k_factor"]
    lines.append("-" * 40)
    lines.append("VIRAL COEFFICIENT (K-FACTOR)")
    lines.append("-" * 40)
    lines.append(f"  K-factor: {kf['value']}")
    lines.append(f"  Rating: {kf['rating']}")
    lines.append(f"  Avg invitations/user: {kf['avg_invitations']}")
    lines.append(f"  Invitation conversion: {kf['invitation_conversion_rate']*100:.1f}%")
    lines.append("")

    # Unit economics
    ue = result["unit_economics"]
    lines.append("-" * 40)
    lines.append("UNIT ECONOMICS")
    lines.append("-" * 40)
    lines.append(f"  Referral CAC:          ${ue['referral_cac']:>10,.2f}")
    lines.append(f"  Other Channel CAC:     ${ue['other_channel_cac']:>10,.2f}")
    lines.append(f"  CAC Savings:           {ue['cac_savings_pct']:>10.1f}%")
    ltv_cac = ue['ltv_cac_ratio']
    lines.append(f"  LTV:CAC Ratio:         {ltv_cac}:1" if isinstance(ltv_cac, (int, float)) else f"  LTV:CAC Ratio:         {ltv_cac}")
    lines.append(f"  Max Sustainable Reward: ${ue['max_sustainable_reward']:>9,.2f}")
    sustainable = "Yes" if ue["current_reward_sustainable"] else "NO -- reward exceeds 15% of LTV"
    lines.append(f"  Current Reward OK:     {sustainable}")
    lines.append("")

    # Projections
    pr = result["projections"]
    lines.append("-" * 40)
    lines.append("REVENUE PROJECTIONS")
    lines.append("-" * 40)
    lines.append(f"  Active Referrers:      {pr['active_referrers']:>10,}")
    lines.append(f"  Monthly Referrals:     {pr['monthly_referrals_sent']:>10,}")
    lines.append(f"  Monthly New Customers: {pr['monthly_new_customers']:>10,}")
    lines.append(f"  Monthly Revenue:       ${pr['monthly_referral_revenue']:>10,.2f}")
    lines.append(f"  Annual Revenue:        ${pr['annual_referral_revenue']:>10,.2f}")
    lines.append(f"  Annual Reward Cost:    ${pr['annual_reward_cost']:>10,.2f}")
    lines.append(f"  Annual Profit:         ${pr['annual_profit']:>10,.2f}")
    lines.append(f"  ROI:                   {pr['roi_pct']:>10.1f}%")
    lines.append(f"  Revenue Share:         {pr['referral_revenue_share_pct']:>10.1f}% of total")
    lines.append("")

    # Reward structure
    rs = result["reward_structure"]
    lines.append("-" * 40)
    lines.append("REWARD STRUCTURE")
    lines.append("-" * 40)
    lines.append(f"  Type: {rs['type'].replace('_', ' ').title()}")
    lines.append(f"  Referrer: ${rs['referrer_reward']:,.2f} ({rs['reward_type']})")
    if rs["referred_reward"] > 0:
        lines.append(f"  Referred: ${rs['referred_reward']:,.2f} ({rs['reward_type']})")
    lines.append(f"  Total/Referral: ${rs['total_per_referral']:,.2f}")
    lines.append("")

    # Comparison
    if result.get("comparison"):
        comp = result["comparison"]
        lines.append("-" * 40)
        lines.append("DOUBLE vs SINGLE-SIDED COMPARISON")
        lines.append("-" * 40)
        ds = comp["double_sided"]
        ss = comp["single_sided_estimate"]
        lines.append(f"  {'':20} {'Double':>12} {'Single (est)':>12}")
        lines.append(f"  {'Customers/yr':20} {ds['annual_customers']:>12,} {ss['annual_customers']:>12,}")
        lines.append(f"  {'Revenue/yr':20} ${ds['annual_revenue']:>10,.0f} ${ss['annual_revenue']:>10,.0f}")
        lines.append(f"  {'Cost/yr':20} ${ds['annual_cost']:>10,.0f} ${ss['annual_cost']:>10,.0f}")
        lines.append(f"  {'Profit/yr':20} ${ds['annual_profit']:>10,.0f} ${ss['annual_profit']:>10,.0f}")

    lines.append("")
    return "\n".join(lines)


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Calculate referral program economics and ROI."
    )
    parser.add_argument(
        "input_file",
        help="Path to JSON file with program economics data",
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

    result = model_economics(data)

    if args.format == "json":
        print(json.dumps(result, indent=2))
    else:
        print(format_text(result))


if __name__ == "__main__":
    main()
