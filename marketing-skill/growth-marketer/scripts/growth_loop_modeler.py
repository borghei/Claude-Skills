#!/usr/bin/env python3
"""Growth Loop Modeler - Model and forecast compound growth loops.

Simulates growth loops (viral, content, paid, product-led) over time,
calculating user acquisition, retention, and compounding effects.

Usage:
    python growth_loop_modeler.py config.json
    python growth_loop_modeler.py config.json --json
    python growth_loop_modeler.py --type viral --users 1000 --k-factor 0.6 --months 12
    python growth_loop_modeler.py --type plg --users 500 --free-to-paid 0.05 --expansion 0.15 --months 12
"""

import argparse
import json
import sys
import math


def model_viral_loop(initial_users, k_factor, cycle_time_days, churn_rate, months):
    """Model viral growth loop over time.

    K-factor = invites_per_user * invite_conversion_rate
    Each cycle: new_users = existing_users * k_factor
    """
    cycles_per_month = 30 / max(cycle_time_days, 1)
    timeline = []
    total_users = initial_users
    organic_acquired = 0

    for month in range(1, months + 1):
        month_start = total_users
        new_viral = 0

        for _ in range(int(cycles_per_month)):
            cycle_new = int(total_users * k_factor)
            new_viral += cycle_new
            total_users += cycle_new

        churned = int(total_users * churn_rate)
        total_users = max(0, total_users - churned)
        organic_acquired += new_viral

        timeline.append({
            "month": month,
            "total_users": total_users,
            "new_viral": new_viral,
            "churned": churned,
            "net_growth": total_users - month_start,
            "growth_rate": round((total_users - month_start) / max(month_start, 1) * 100, 1),
        })

    return {
        "loop_type": "viral",
        "parameters": {
            "initial_users": initial_users,
            "k_factor": k_factor,
            "cycle_time_days": cycle_time_days,
            "monthly_churn_rate": churn_rate,
        },
        "timeline": timeline,
        "summary": {
            "final_users": total_users,
            "total_viral_acquired": organic_acquired,
            "growth_multiple": round(total_users / max(initial_users, 1), 2),
            "sustainable": k_factor > churn_rate,
        },
    }


def model_plg_loop(initial_users, free_to_paid_rate, expansion_rate, churn_rate,
                    arpu, months, viral_coefficient=0.2):
    """Model product-led growth loop.

    Free users -> Paid users -> Expansion -> Referrals -> More free users
    """
    timeline = []
    free_users = initial_users
    paid_users = 0
    total_revenue = 0

    for month in range(1, months + 1):
        # Conversions from free to paid
        new_paid = int(free_users * free_to_paid_rate)
        paid_users += new_paid

        # Expansion revenue
        expansion_users = int(paid_users * expansion_rate)

        # Churn
        churned_paid = int(paid_users * churn_rate)
        paid_users = max(0, paid_users - churned_paid)

        # Viral referrals from paid users
        new_free_from_referrals = int(paid_users * viral_coefficient)
        free_users += new_free_from_referrals

        # Monthly revenue
        monthly_revenue = paid_users * arpu
        total_revenue += monthly_revenue

        # MRR and growth
        timeline.append({
            "month": month,
            "free_users": free_users,
            "paid_users": paid_users,
            "new_conversions": new_paid,
            "new_referrals": new_free_from_referrals,
            "churned": churned_paid,
            "mrr": round(monthly_revenue, 2),
            "total_revenue": round(total_revenue, 2),
        })

    ltv = arpu / max(churn_rate, 0.01)

    return {
        "loop_type": "product_led_growth",
        "parameters": {
            "initial_free_users": initial_users,
            "free_to_paid_rate": free_to_paid_rate,
            "expansion_rate": expansion_rate,
            "monthly_churn_rate": churn_rate,
            "arpu": arpu,
            "viral_coefficient": viral_coefficient,
        },
        "timeline": timeline,
        "summary": {
            "final_free_users": free_users,
            "final_paid_users": paid_users,
            "final_mrr": round(paid_users * arpu, 2),
            "total_revenue": round(total_revenue, 2),
            "estimated_ltv": round(ltv, 2),
        },
    }


def model_content_loop(initial_monthly_traffic, content_pieces_per_month,
                       avg_traffic_per_piece, traffic_decay_rate,
                       conversion_rate, months):
    """Model content/SEO growth loop.

    Content -> Organic traffic -> Leads -> Customers -> Revenue -> More content budget
    """
    timeline = []
    total_content = 0
    cumulative_traffic = 0

    for month in range(1, months + 1):
        total_content += content_pieces_per_month

        # Each piece generates traffic but decays over time
        monthly_traffic = initial_monthly_traffic
        for piece_month in range(total_content):
            months_old = month - (piece_month // content_pieces_per_month)
            if months_old > 0:
                piece_traffic = avg_traffic_per_piece * ((1 - traffic_decay_rate) ** months_old)
                monthly_traffic += max(0, piece_traffic)

        conversions = int(monthly_traffic * conversion_rate)
        cumulative_traffic += monthly_traffic

        timeline.append({
            "month": month,
            "total_content_pieces": total_content,
            "monthly_traffic": int(monthly_traffic),
            "conversions": conversions,
            "cumulative_traffic": int(cumulative_traffic),
        })

    return {
        "loop_type": "content",
        "parameters": {
            "initial_monthly_traffic": initial_monthly_traffic,
            "content_pieces_per_month": content_pieces_per_month,
            "avg_traffic_per_piece": avg_traffic_per_piece,
            "traffic_decay_rate": traffic_decay_rate,
            "conversion_rate": conversion_rate,
        },
        "timeline": timeline,
        "summary": {
            "total_content": total_content,
            "final_monthly_traffic": timeline[-1]["monthly_traffic"] if timeline else 0,
            "traffic_growth_multiple": round(
                timeline[-1]["monthly_traffic"] / max(initial_monthly_traffic, 1), 2
            ) if timeline else 0,
            "total_conversions": sum(t["conversions"] for t in timeline),
        },
    }


def format_report(result):
    """Format human-readable growth model report."""
    lines = []
    lines.append("=" * 65)
    lines.append(f"GROWTH LOOP MODEL: {result['loop_type'].upper().replace('_', ' ')}")
    lines.append("=" * 65)

    lines.append("\nParameters:")
    for k, v in result["parameters"].items():
        lines.append(f"  {k.replace('_', ' ').title()}: {v}")
    lines.append("")

    lines.append("--- TIMELINE ---")
    if result["loop_type"] == "viral":
        lines.append(f"{'Month':>6} {'Total':>10} {'New Viral':>10} {'Churned':>10} {'Growth':>8}")
        lines.append("-" * 50)
        for t in result["timeline"]:
            lines.append(f"{t['month']:>6} {t['total_users']:>10,} {t['new_viral']:>10,} {t['churned']:>10,} {t['growth_rate']:>7.1f}%")
    elif result["loop_type"] == "product_led_growth":
        lines.append(f"{'Month':>6} {'Free':>8} {'Paid':>8} {'MRR':>12} {'Total Rev':>12}")
        lines.append("-" * 50)
        for t in result["timeline"]:
            lines.append(f"{t['month']:>6} {t['free_users']:>8,} {t['paid_users']:>8,} ${t['mrr']:>10,.0f} ${t['total_revenue']:>10,.0f}")
    elif result["loop_type"] == "content":
        lines.append(f"{'Month':>6} {'Content':>8} {'Traffic':>10} {'Conversions':>12}")
        lines.append("-" * 40)
        for t in result["timeline"]:
            lines.append(f"{t['month']:>6} {t['total_content_pieces']:>8} {t['monthly_traffic']:>10,} {t['conversions']:>12,}")

    lines.append("")
    lines.append("--- SUMMARY ---")
    for k, v in result["summary"].items():
        label = k.replace("_", " ").title()
        if isinstance(v, float):
            lines.append(f"  {label}: {v:,.2f}")
        elif isinstance(v, int):
            lines.append(f"  {label}: {v:,}")
        else:
            lines.append(f"  {label}: {v}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Model and forecast compound growth loops")
    parser.add_argument("input", nargs="?", help="JSON config file")
    parser.add_argument("--type", choices=["viral", "plg", "content"], help="Growth loop type")
    parser.add_argument("--users", type=int, default=1000, help="Initial users")
    parser.add_argument("--k-factor", type=float, default=0.5, help="Viral K-factor")
    parser.add_argument("--free-to-paid", type=float, default=0.05, help="PLG conversion rate")
    parser.add_argument("--expansion", type=float, default=0.1, help="PLG expansion rate")
    parser.add_argument("--churn", type=float, default=0.05, help="Monthly churn rate")
    parser.add_argument("--arpu", type=float, default=50, help="Average revenue per user")
    parser.add_argument("--months", type=int, default=12, help="Forecast months")
    parser.add_argument("--json", action="store_true", dest="json_output", help="Output JSON")
    args = parser.parse_args()

    if args.input:
        try:
            with open(args.input, "r", encoding="utf-8") as f:
                config = json.load(f)
        except FileNotFoundError:
            print(f"Error: File not found: {args.input}", file=sys.stderr)
            sys.exit(1)

        loop_type = config.get("type", "viral")
    elif args.type:
        loop_type = args.type
        config = {}
    else:
        parser.print_help()
        sys.exit(1)

    if loop_type == "viral":
        result = model_viral_loop(
            config.get("initial_users", args.users),
            config.get("k_factor", args.k_factor),
            config.get("cycle_time_days", 14),
            config.get("churn_rate", args.churn),
            config.get("months", args.months),
        )
    elif loop_type == "plg":
        result = model_plg_loop(
            config.get("initial_users", args.users),
            config.get("free_to_paid_rate", args.free_to_paid),
            config.get("expansion_rate", args.expansion),
            config.get("churn_rate", args.churn),
            config.get("arpu", args.arpu),
            config.get("months", args.months),
        )
    elif loop_type == "content":
        result = model_content_loop(
            config.get("initial_monthly_traffic", args.users),
            config.get("content_pieces_per_month", 4),
            config.get("avg_traffic_per_piece", 200),
            config.get("traffic_decay_rate", 0.1),
            config.get("conversion_rate", 0.02),
            config.get("months", args.months),
        )
    else:
        print(f"Unknown loop type: {loop_type}", file=sys.stderr)
        sys.exit(1)

    if args.json_output:
        print(json.dumps(result, indent=2))
    else:
        print(format_report(result))


if __name__ == "__main__":
    main()
