#!/usr/bin/env python3
"""Analyze win/loss patterns from closed deal data.

Reads closed deal data from CSV or JSON and identifies patterns in wins vs.
losses across dimensions: deal size, sales cycle, competitor, industry,
lead source, and qualification score.

Usage:
    python win_loss_analyzer.py --data closed_deals.csv
    python win_loss_analyzer.py --data deals.json --json
    python win_loss_analyzer.py --data deals.csv --min-deals 5
"""

import argparse
import csv
import json
import math
import os
import sys
from collections import defaultdict
from datetime import datetime


def load_data(filepath):
    """Load closed deal data from CSV or JSON file."""
    ext = os.path.splitext(filepath)[1].lower()
    if ext == ".json":
        with open(filepath, "r") as f:
            data = json.load(f)
            return data if isinstance(data, list) else [data]
    elif ext == ".csv":
        with open(filepath, "r") as f:
            return list(csv.DictReader(f))
    else:
        print(f"Error: Unsupported file format '{ext}'. Use .csv or .json.", file=sys.stderr)
        sys.exit(1)


def parse_amount(value):
    """Parse monetary amount from string."""
    if not value:
        return 0.0
    cleaned = str(value).replace("$", "").replace(",", "").strip()
    try:
        return float(cleaned)
    except ValueError:
        return 0.0


def parse_days(value):
    """Parse numeric days value."""
    try:
        return int(float(str(value).strip()))
    except (ValueError, TypeError):
        return 0


def is_won(deal):
    """Determine if a deal was won."""
    outcome = str(deal.get("outcome", deal.get("stage", deal.get("status", "")))).lower().strip()
    return outcome in ("won", "closed_won", "closed won", "win", "1", "true")


def bucket_amount(amount):
    """Categorize deal amount into size buckets."""
    if amount < 25000:
        return "SMB (<$25K)"
    elif amount < 100000:
        return "Mid-Market ($25K-$100K)"
    elif amount < 500000:
        return "Enterprise ($100K-$500K)"
    else:
        return "Strategic ($500K+)"


def bucket_cycle(days):
    """Categorize sales cycle length into buckets."""
    if days <= 0:
        return "Unknown"
    elif days <= 30:
        return "Fast (0-30d)"
    elif days <= 60:
        return "Normal (31-60d)"
    elif days <= 90:
        return "Extended (61-90d)"
    else:
        return "Long (90d+)"


def analyze_dimension(deals, get_key, min_deals=3):
    """Analyze win/loss rates by a given dimension."""
    groups = defaultdict(lambda: {"won": 0, "lost": 0, "won_value": 0, "lost_value": 0})
    for deal in deals:
        key = get_key(deal)
        if not key or key == "Unknown" or key == "":
            key = "Unspecified"
        amount = parse_amount(deal.get("amount", deal.get("acv", deal.get("value", 0))))
        if is_won(deal):
            groups[key]["won"] += 1
            groups[key]["won_value"] += amount
        else:
            groups[key]["lost"] += 1
            groups[key]["lost_value"] += amount

    results = {}
    for key, data in groups.items():
        total = data["won"] + data["lost"]
        if total >= min_deals:
            results[key] = {
                "won": data["won"],
                "lost": data["lost"],
                "total": total,
                "win_rate": round(data["won"] / total * 100, 1),
                "won_value": round(data["won_value"], 2),
                "lost_value": round(data["lost_value"], 2),
                "avg_won_value": round(data["won_value"] / data["won"], 2) if data["won"] > 0 else 0,
            }
    return dict(sorted(results.items(), key=lambda x: x[1]["win_rate"], reverse=True))


def find_patterns(analysis_results):
    """Identify key patterns and actionable insights."""
    patterns = []

    for dimension, data in analysis_results.items():
        if not data:
            continue

        rates = [(k, v["win_rate"], v["total"]) for k, v in data.items()]
        if len(rates) < 2:
            continue

        best = max(rates, key=lambda x: x[1])
        worst = min(rates, key=lambda x: x[1])

        if best[1] - worst[1] > 15:
            patterns.append({
                "dimension": dimension,
                "finding": f"Win rate varies significantly: {best[0]} ({best[1]}%) vs {worst[0]} ({worst[1]}%)",
                "spread": round(best[1] - worst[1], 1),
                "recommendation": f"Investigate what drives success in '{best[0]}' and apply lessons to '{worst[0]}'",
                "priority": "high" if best[1] - worst[1] > 30 else "medium",
            })

    return sorted(patterns, key=lambda p: p["spread"], reverse=True)


def analyze_loss_reasons(deals):
    """Analyze primary loss reasons if provided."""
    reasons = defaultdict(lambda: {"count": 0, "total_value": 0})
    for deal in deals:
        if is_won(deal):
            continue
        reason = deal.get("loss_reason", deal.get("close_reason", deal.get("reason", "")))
        if reason:
            reason = str(reason).strip()
            amount = parse_amount(deal.get("amount", deal.get("acv", 0)))
            reasons[reason]["count"] += 1
            reasons[reason]["total_value"] += amount

    return dict(sorted(reasons.items(), key=lambda x: x[1]["count"], reverse=True))


def format_human(results, patterns, loss_reasons):
    """Format results for human-readable output."""
    lines = []
    lines.append("=" * 70)
    lines.append("WIN/LOSS ANALYSIS REPORT")
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("=" * 70)

    summary = results.get("summary", {})
    lines.append(f"\n  Total Deals Analyzed: {summary.get('total_deals', 0)}")
    lines.append(f"  Won: {summary.get('total_won', 0)}  |  Lost: {summary.get('total_lost', 0)}")
    lines.append(f"  Overall Win Rate: {summary.get('overall_win_rate', 0)}%")
    lines.append(f"  Total Won Revenue: ${summary.get('total_won_value', 0):,.2f}")
    lines.append(f"  Total Lost Revenue: ${summary.get('total_lost_value', 0):,.2f}")

    for dimension, data in results.items():
        if dimension == "summary":
            continue
        if not data:
            continue

        title = dimension.replace("_", " ").upper()
        lines.append(f"\n{'WIN RATE BY ' + title:^70}")
        lines.append("-" * 70)
        lines.append(f"  {'Category':<30} {'Won':>5} {'Lost':>5} {'Total':>6} {'Win Rate':>9}")
        lines.append("  " + "-" * 57)

        for category, stats in data.items():
            wr = stats["win_rate"]
            indicator = " ***" if wr >= 40 else " !" if wr < 15 else ""
            lines.append(
                f"  {category:<30} {stats['won']:>5} {stats['lost']:>5} "
                f"{stats['total']:>6} {wr:>8.1f}%{indicator}"
            )

    if loss_reasons:
        lines.append(f"\n{'LOSS REASONS':^70}")
        lines.append("-" * 70)
        lines.append(f"  {'Reason':<40} {'Count':>6} {'Lost Value':>14}")
        lines.append("  " + "-" * 62)
        for reason, data in loss_reasons.items():
            lines.append(f"  {reason:<40} {data['count']:>6} ${data['total_value']:>12,.2f}")

    if patterns:
        lines.append(f"\n{'KEY PATTERNS & RECOMMENDATIONS':^70}")
        lines.append("-" * 70)
        for i, p in enumerate(patterns, 1):
            lines.append(f"\n  {i}. [{p['priority'].upper()}] {p['dimension'].replace('_', ' ').title()}")
            lines.append(f"     Finding: {p['finding']}")
            lines.append(f"     Action:  {p['recommendation']}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Analyze win/loss patterns from closed deal data."
    )
    parser.add_argument("--data", required=True, help="Path to closed deals CSV or JSON file")
    parser.add_argument(
        "--min-deals",
        type=int,
        default=3,
        help="Minimum deals per category to include in analysis (default: 3)",
    )
    parser.add_argument("--json", action="store_true", help="Output results as JSON")

    args = parser.parse_args()

    if not os.path.exists(args.data):
        print(f"Error: File not found: {args.data}", file=sys.stderr)
        sys.exit(1)

    deals = load_data(args.data)
    if not deals:
        print("Error: No deals found in input file.", file=sys.stderr)
        sys.exit(1)

    total_won = sum(1 for d in deals if is_won(d))
    total_lost = len(deals) - total_won
    won_value = sum(parse_amount(d.get("amount", d.get("acv", 0))) for d in deals if is_won(d))
    lost_value = sum(parse_amount(d.get("amount", d.get("acv", 0))) for d in deals if not is_won(d))

    results = {
        "summary": {
            "total_deals": len(deals),
            "total_won": total_won,
            "total_lost": total_lost,
            "overall_win_rate": round(total_won / len(deals) * 100, 1) if deals else 0,
            "total_won_value": round(won_value, 2),
            "total_lost_value": round(lost_value, 2),
        },
        "deal_size": analyze_dimension(
            deals,
            lambda d: bucket_amount(parse_amount(d.get("amount", d.get("acv", 0)))),
            args.min_deals,
        ),
        "sales_cycle": analyze_dimension(
            deals,
            lambda d: bucket_cycle(parse_days(d.get("cycle_days", d.get("sales_cycle", 0)))),
            args.min_deals,
        ),
        "competitor": analyze_dimension(
            deals,
            lambda d: d.get("competitor", d.get("primary_competitor", "")),
            args.min_deals,
        ),
        "industry": analyze_dimension(
            deals, lambda d: d.get("industry", ""), args.min_deals
        ),
        "lead_source": analyze_dimension(
            deals, lambda d: d.get("lead_source", d.get("source", "")), args.min_deals
        ),
    }

    all_dimension_data = {k: v for k, v in results.items() if k != "summary"}
    patterns = find_patterns(all_dimension_data)
    loss_reasons = analyze_loss_reasons(deals)

    if args.json:
        output = {
            **results,
            "patterns": patterns,
            "loss_reasons": loss_reasons,
        }
        print(json.dumps(output, indent=2))
    else:
        print(format_human(results, patterns, loss_reasons))

    sys.exit(0)


if __name__ == "__main__":
    main()
