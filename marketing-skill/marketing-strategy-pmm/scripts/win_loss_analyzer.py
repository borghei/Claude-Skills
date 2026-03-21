#!/usr/bin/env python3
"""Win/Loss Analyzer - Analyze win/loss data to improve competitive strategy.

Processes deal outcome data to identify patterns in wins and losses by
competitor, deal size, segment, and reason.

Usage:
    python win_loss_analyzer.py deals.json
    python win_loss_analyzer.py deals.json --json
    python win_loss_analyzer.py --demo
"""

import argparse
import json
import sys
from collections import Counter


def analyze_win_loss(deals):
    """Analyze win/loss patterns from deal data."""
    wins = [d for d in deals if d.get("outcome") == "won"]
    losses = [d for d in deals if d.get("outcome") == "lost"]
    total = len(deals)

    overall_win_rate = len(wins) / max(total, 1) * 100

    # Win rate by competitor
    by_competitor = {}
    for deal in deals:
        comp = deal.get("competitor", "unknown")
        if comp not in by_competitor:
            by_competitor[comp] = {"won": 0, "lost": 0, "total": 0}
        by_competitor[comp]["total"] += 1
        if deal.get("outcome") == "won":
            by_competitor[comp]["won"] += 1
        else:
            by_competitor[comp]["lost"] += 1

    competitor_rates = []
    for comp, data in by_competitor.items():
        rate = data["won"] / max(data["total"], 1) * 100
        competitor_rates.append({
            "competitor": comp,
            "win_rate": round(rate, 1),
            "won": data["won"],
            "lost": data["lost"],
            "total": data["total"],
        })
    competitor_rates.sort(key=lambda x: x["win_rate"], reverse=True)

    # Win/loss reasons
    win_reasons = Counter(d.get("win_reason", "unknown") for d in wins)
    loss_reasons = Counter(d.get("loss_reason", "unknown") for d in losses)

    # By deal size
    size_buckets = {"small": {"min": 0, "max": 10000}, "mid": {"min": 10000, "max": 50000}, "large": {"min": 50000, "max": float("inf")}}
    by_size = {}
    for bucket_name, bucket_range in size_buckets.items():
        bucket_deals = [d for d in deals if bucket_range["min"] <= d.get("deal_size", 0) < bucket_range["max"]]
        bucket_wins = [d for d in bucket_deals if d.get("outcome") == "won"]
        by_size[bucket_name] = {
            "total": len(bucket_deals),
            "won": len(bucket_wins),
            "win_rate": round(len(bucket_wins) / max(len(bucket_deals), 1) * 100, 1),
        }

    # By segment
    by_segment = {}
    for deal in deals:
        seg = deal.get("segment", "unknown")
        if seg not in by_segment:
            by_segment[seg] = {"won": 0, "lost": 0, "total": 0}
        by_segment[seg]["total"] += 1
        if deal.get("outcome") == "won":
            by_segment[seg]["won"] += 1
        else:
            by_segment[seg]["lost"] += 1

    segment_rates = []
    for seg, data in by_segment.items():
        rate = data["won"] / max(data["total"], 1) * 100
        segment_rates.append({"segment": seg, "win_rate": round(rate, 1), "total": data["total"]})
    segment_rates.sort(key=lambda x: x["win_rate"], reverse=True)

    # Average deal size
    avg_won_size = sum(d.get("deal_size", 0) for d in wins) / max(len(wins), 1)
    avg_lost_size = sum(d.get("deal_size", 0) for d in losses) / max(len(losses), 1)

    # Sales cycle length
    won_cycles = [d.get("sales_cycle_days", 0) for d in wins if d.get("sales_cycle_days")]
    lost_cycles = [d.get("sales_cycle_days", 0) for d in losses if d.get("sales_cycle_days")]
    avg_won_cycle = sum(won_cycles) / max(len(won_cycles), 1) if won_cycles else None
    avg_lost_cycle = sum(lost_cycles) / max(len(lost_cycles), 1) if lost_cycles else None

    # Insights
    insights = []
    if competitor_rates:
        worst = competitor_rates[-1]
        if worst["win_rate"] < 30 and worst["total"] >= 3:
            insights.append(f"Lowest win rate against {worst['competitor']} ({worst['win_rate']:.0f}%). Review battlecard and product gaps.")
    if avg_won_size > avg_lost_size * 1.5:
        insights.append(f"We win bigger deals (${avg_won_size:,.0f} avg) vs losses (${avg_lost_size:,.0f}). Consider moving upmarket.")
    if loss_reasons:
        top_loss = loss_reasons.most_common(1)[0]
        insights.append(f"Top loss reason: '{top_loss[0]}' ({top_loss[1]} deals). Address in product roadmap or sales training.")

    return {
        "summary": {
            "total_deals": total,
            "wins": len(wins),
            "losses": len(losses),
            "overall_win_rate": round(overall_win_rate, 1),
            "avg_won_deal_size": round(avg_won_size, 2),
            "avg_lost_deal_size": round(avg_lost_size, 2),
            "avg_won_cycle_days": round(avg_won_cycle, 1) if avg_won_cycle else None,
            "avg_lost_cycle_days": round(avg_lost_cycle, 1) if avg_lost_cycle else None,
        },
        "by_competitor": competitor_rates,
        "by_segment": segment_rates,
        "by_deal_size": by_size,
        "win_reasons": dict(win_reasons.most_common(10)),
        "loss_reasons": dict(loss_reasons.most_common(10)),
        "insights": insights,
    }


def get_demo_data():
    return [
        {"outcome": "won", "competitor": "CompA", "deal_size": 24000, "segment": "mid_market", "win_reason": "product_fit", "sales_cycle_days": 45},
        {"outcome": "lost", "competitor": "CompA", "deal_size": 36000, "segment": "enterprise", "loss_reason": "missing_feature", "sales_cycle_days": 90},
        {"outcome": "won", "competitor": "CompB", "deal_size": 12000, "segment": "smb", "win_reason": "ease_of_use", "sales_cycle_days": 21},
        {"outcome": "won", "competitor": "CompB", "deal_size": 18000, "segment": "mid_market", "win_reason": "ease_of_use", "sales_cycle_days": 30},
        {"outcome": "lost", "competitor": "CompA", "deal_size": 48000, "segment": "enterprise", "loss_reason": "price", "sales_cycle_days": 120},
        {"outcome": "won", "competitor": "status_quo", "deal_size": 8000, "segment": "smb", "win_reason": "time_savings", "sales_cycle_days": 14},
        {"outcome": "lost", "competitor": "CompC", "deal_size": 30000, "segment": "mid_market", "loss_reason": "relationship", "sales_cycle_days": 60},
        {"outcome": "won", "competitor": "CompC", "deal_size": 24000, "segment": "mid_market", "win_reason": "product_fit", "sales_cycle_days": 35},
        {"outcome": "lost", "competitor": "status_quo", "deal_size": 6000, "segment": "smb", "loss_reason": "no_budget", "sales_cycle_days": 45},
        {"outcome": "won", "competitor": "CompA", "deal_size": 42000, "segment": "enterprise", "win_reason": "product_fit", "sales_cycle_days": 75},
    ]


def format_report(analysis):
    """Format human-readable report."""
    lines = []
    lines.append("=" * 65)
    lines.append("WIN/LOSS ANALYSIS")
    lines.append("=" * 65)

    s = analysis["summary"]
    lines.append(f"Total Deals:      {s['total_deals']}")
    lines.append(f"Win Rate:         {s['overall_win_rate']:.0f}% ({s['wins']}W / {s['losses']}L)")
    lines.append(f"Avg Won Size:     ${s['avg_won_deal_size']:,.0f}")
    lines.append(f"Avg Lost Size:    ${s['avg_lost_deal_size']:,.0f}")
    if s["avg_won_cycle_days"]:
        lines.append(f"Avg Won Cycle:    {s['avg_won_cycle_days']:.0f} days")
    lines.append("")

    lines.append("--- BY COMPETITOR ---")
    lines.append(f"{'Competitor':<20} {'Win Rate':>10} {'Won':>5} {'Lost':>5} {'Total':>5}")
    lines.append("-" * 48)
    for c in analysis["by_competitor"]:
        lines.append(f"{c['competitor']:<20} {c['win_rate']:>9.0f}% {c['won']:>5} {c['lost']:>5} {c['total']:>5}")
    lines.append("")

    lines.append("--- TOP WIN REASONS ---")
    for reason, count in sorted(analysis["win_reasons"].items(), key=lambda x: x[1], reverse=True):
        lines.append(f"  {reason}: {count}")

    lines.append("--- TOP LOSS REASONS ---")
    for reason, count in sorted(analysis["loss_reasons"].items(), key=lambda x: x[1], reverse=True):
        lines.append(f"  {reason}: {count}")
    lines.append("")

    if analysis["insights"]:
        lines.append("--- INSIGHTS ---")
        for insight in analysis["insights"]:
            lines.append(f"  * {insight}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Analyze win/loss data for competitive strategy")
    parser.add_argument("input", nargs="?", help="JSON file with deal data")
    parser.add_argument("--json", action="store_true", dest="json_output", help="Output JSON")
    parser.add_argument("--demo", action="store_true", help="Run with demo data")
    args = parser.parse_args()

    if args.demo:
        deals = get_demo_data()
    elif args.input:
        try:
            with open(args.input, "r", encoding="utf-8") as f:
                data = json.load(f)
            deals = data if isinstance(data, list) else data.get("deals", [])
        except FileNotFoundError:
            print(f"Error: File not found: {args.input}", file=sys.stderr)
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)

    analysis = analyze_win_loss(deals)

    if args.json_output:
        print(json.dumps(analysis, indent=2))
    else:
        print(format_report(analysis))


if __name__ == "__main__":
    main()
