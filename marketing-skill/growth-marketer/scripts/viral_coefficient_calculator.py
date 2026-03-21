#!/usr/bin/env python3
"""Viral Coefficient Calculator - Calculate and forecast viral growth metrics.

Computes K-factor, viral cycle time, effective viral rate, and forecasts
user growth from referral data.

Usage:
    python viral_coefficient_calculator.py referral_data.json
    python viral_coefficient_calculator.py referral_data.json --json
    python viral_coefficient_calculator.py --invites 5000 --conversions 800 --users 2000 --cycle-days 7
"""

import argparse
import json
import sys
import math


def calculate_viral_metrics(total_users, invites_sent, invite_conversions,
                            cycle_time_days, time_period_days=30):
    """Calculate comprehensive viral growth metrics."""
    # K-factor = invites per user * conversion rate of invites
    invites_per_user = invites_sent / max(total_users, 1)
    invite_conversion_rate = invite_conversions / max(invites_sent, 1)
    k_factor = invites_per_user * invite_conversion_rate

    # Effective viral rate (accounts for cycle time)
    cycles_per_period = time_period_days / max(cycle_time_days, 1)

    # Branching factor (how many users each cohort eventually creates)
    # For K < 1: total = 1 / (1 - K) [geometric series]
    if k_factor < 1:
        branching_factor = 1 / (1 - k_factor)
    else:
        branching_factor = float("inf")  # True viral growth

    # Forecast: users after N cycles
    forecast = []
    users = total_users
    for cycle in range(1, int(cycles_per_period * 12) + 1):
        new_users = int(users * k_factor)
        users += new_users
        month = cycle * cycle_time_days / 30
        if cycle % max(1, int(cycles_per_period)) == 0:
            forecast.append({
                "month": round(month),
                "total_users": users,
                "new_from_viral": new_users,
            })

    # Time to reach milestones
    milestones = {}
    if k_factor > 0:
        for target_multiple in [2, 5, 10]:
            target = total_users * target_multiple
            if k_factor >= 1:
                # Exponential growth
                cycles_needed = math.log(target / total_users) / math.log(1 + k_factor)
                days_needed = cycles_needed * cycle_time_days
                milestones[f"{target_multiple}x_users"] = {
                    "target": target,
                    "estimated_days": round(days_needed),
                    "estimated_months": round(days_needed / 30, 1),
                }
            elif k_factor > 0:
                # Will the geometric series reach the target?
                max_reachable = total_users * branching_factor
                if max_reachable >= target:
                    # Approximate time
                    cycles_needed = math.log(1 - (target / max_reachable)) / math.log(k_factor)
                    days_needed = abs(cycles_needed) * cycle_time_days
                    milestones[f"{target_multiple}x_users"] = {
                        "target": target,
                        "estimated_days": round(days_needed),
                        "estimated_months": round(days_needed / 30, 1),
                    }
                else:
                    milestones[f"{target_multiple}x_users"] = {
                        "target": target,
                        "estimated_days": None,
                        "note": f"K-factor too low. Max reachable: {int(max_reachable):,}",
                    }

    # Assessment
    if k_factor >= 1.0:
        assessment = "TRUE VIRAL GROWTH: Each user brings more than one new user. Growth is exponential."
    elif k_factor >= 0.7:
        assessment = "STRONG VIRAL BOOST: Significant viral amplification of paid/organic acquisition."
    elif k_factor >= 0.4:
        assessment = "MODERATE VIRAL EFFECT: Viral referrals supplement other channels meaningfully."
    elif k_factor >= 0.1:
        assessment = "WEAK VIRAL EFFECT: Minimal viral contribution. Focus on improving invite UX and conversion."
    else:
        assessment = "NO MEANINGFUL VIRALITY: Consider implementing referral incentives or in-product sharing."

    # Improvement scenarios
    scenarios = []
    for improve_invites in [1.0, 1.25, 1.5]:
        for improve_conv in [1.0, 1.25, 1.5]:
            if improve_invites == 1.0 and improve_conv == 1.0:
                continue
            new_ipu = invites_per_user * improve_invites
            new_conv = min(1.0, invite_conversion_rate * improve_conv)
            new_k = new_ipu * new_conv
            scenarios.append({
                "invites_per_user_change": f"+{int((improve_invites - 1) * 100)}%",
                "conversion_change": f"+{int((improve_conv - 1) * 100)}%",
                "new_k_factor": round(new_k, 3),
                "improvement": f"+{round((new_k - k_factor) / max(k_factor, 0.001) * 100)}%",
            })

    return {
        "metrics": {
            "k_factor": round(k_factor, 3),
            "invites_per_user": round(invites_per_user, 2),
            "invite_conversion_rate": round(invite_conversion_rate, 4),
            "cycle_time_days": cycle_time_days,
            "branching_factor": round(branching_factor, 2) if branching_factor != float("inf") else "infinite",
            "cycles_per_month": round(30 / max(cycle_time_days, 1), 1),
        },
        "assessment": assessment,
        "is_truly_viral": k_factor >= 1.0,
        "forecast": forecast[:12],
        "milestones": milestones,
        "improvement_scenarios": scenarios,
    }


def format_report(result):
    """Format human-readable report."""
    lines = []
    lines.append("=" * 60)
    lines.append("VIRAL COEFFICIENT ANALYSIS")
    lines.append("=" * 60)

    m = result["metrics"]
    lines.append(f"K-Factor:                {m['k_factor']}")
    lines.append(f"Invites per user:        {m['invites_per_user']}")
    lines.append(f"Invite conversion rate:  {m['invite_conversion_rate']:.1%}")
    lines.append(f"Cycle time:              {m['cycle_time_days']} days")
    lines.append(f"Branching factor:        {m['branching_factor']}")
    lines.append(f"Cycles per month:        {m['cycles_per_month']}")
    lines.append("")
    lines.append(f"Assessment: {result['assessment']}")
    lines.append("")

    # Forecast
    if result["forecast"]:
        lines.append("--- GROWTH FORECAST ---")
        lines.append(f"{'Month':>6} {'Users':>12} {'New Viral':>12}")
        lines.append("-" * 35)
        for f in result["forecast"]:
            lines.append(f"{f['month']:>6} {f['total_users']:>12,} {f['new_from_viral']:>12,}")
        lines.append("")

    # Milestones
    if result["milestones"]:
        lines.append("--- GROWTH MILESTONES ---")
        for label, data in result["milestones"].items():
            if data.get("estimated_days"):
                lines.append(f"  {label}: ~{data['estimated_months']} months ({data['estimated_days']} days)")
            elif data.get("note"):
                lines.append(f"  {label}: {data['note']}")
        lines.append("")

    # Improvement scenarios
    if result["improvement_scenarios"]:
        lines.append("--- IMPROVEMENT SCENARIOS ---")
        lines.append(f"{'Invites':>10} {'Conv':>10} {'New K':>8} {'Change':>10}")
        for s in result["improvement_scenarios"]:
            lines.append(f"{s['invites_per_user_change']:>10} {s['conversion_change']:>10} {s['new_k_factor']:>8} {s['improvement']:>10}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Calculate viral growth metrics")
    parser.add_argument("input", nargs="?", help="JSON file with referral data")
    parser.add_argument("--invites", type=int, help="Total invites sent")
    parser.add_argument("--conversions", type=int, help="Invites that converted")
    parser.add_argument("--users", type=int, help="Total users who could invite")
    parser.add_argument("--cycle-days", type=int, default=7, help="Viral cycle time in days")
    parser.add_argument("--json", action="store_true", dest="json_output", help="Output JSON")
    args = parser.parse_args()

    if args.input:
        try:
            with open(args.input, "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            print(f"Error: File not found: {args.input}", file=sys.stderr)
            sys.exit(1)

        result = calculate_viral_metrics(
            data.get("total_users", 1000),
            data.get("invites_sent", 0),
            data.get("invite_conversions", 0),
            data.get("cycle_time_days", 7),
        )
    elif args.invites and args.conversions and args.users:
        result = calculate_viral_metrics(args.users, args.invites, args.conversions, args.cycle_days)
    else:
        parser.print_help()
        sys.exit(1)

    if args.json_output:
        print(json.dumps(result, indent=2))
    else:
        print(format_report(result))


if __name__ == "__main__":
    main()
