#!/usr/bin/env python3
"""Analyze sales pipeline for forecast accuracy, stage velocity, and health.

Reads opportunity data from CSV or JSON and produces pipeline coverage,
stage conversion rates, deal aging, velocity metrics, and forecast projections.

Usage:
    python pipeline_analyzer.py --data opportunities.csv --quota 2500000
    python pipeline_analyzer.py --data opportunities.json --quota 5000000 --json
"""

import argparse
import csv
import json
import os
import sys
from collections import defaultdict
from datetime import datetime, timedelta

STAGE_ORDER = {
    "prospect": 0,
    "discovery": 1,
    "demo": 2,
    "evaluation": 3,
    "proposal": 4,
    "negotiation": 5,
    "closed_won": 6,
    "closed_lost": 7,
}

STAGE_PROBABILITIES = {
    "prospect": 0.10,
    "discovery": 0.20,
    "demo": 0.40,
    "evaluation": 0.40,
    "proposal": 0.60,
    "negotiation": 0.80,
    "closed_won": 1.00,
    "closed_lost": 0.00,
}

AGING_THRESHOLDS = {
    "prospect": 14,
    "discovery": 21,
    "demo": 14,
    "evaluation": 21,
    "proposal": 14,
    "negotiation": 21,
}


def load_data(filepath):
    """Load opportunity data from CSV or JSON file."""
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


def parse_date(value):
    """Parse date from common formats."""
    if not value:
        return None
    for fmt in ["%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%Y-%m-%dT%H:%M:%S"]:
        try:
            return datetime.strptime(str(value).strip(), fmt)
        except ValueError:
            continue
    return None


def normalize_stage(stage):
    """Normalize stage name to standard key."""
    if not stage:
        return "unknown"
    s = stage.lower().strip().replace(" ", "_").replace("/", "_")
    for key in STAGE_ORDER:
        if key in s:
            return key
    return s


def analyze_pipeline(opportunities, quota):
    """Run full pipeline analysis."""
    today = datetime.now()
    results = {
        "total_opportunities": 0,
        "total_pipeline_value": 0,
        "weighted_pipeline_value": 0,
        "quota": quota,
        "coverage_ratio": 0,
        "weighted_coverage": 0,
        "stage_summary": {},
        "aging_alerts": [],
        "velocity_metrics": {},
        "forecast": {},
    }

    stage_deals = defaultdict(list)
    stage_values = defaultdict(float)
    stage_counts = defaultdict(int)
    cycle_times = []
    won_values = []
    lost_values = []

    for opp in opportunities:
        stage = normalize_stage(opp.get("stage", ""))
        amount = parse_amount(opp.get("amount", opp.get("acv", opp.get("value", 0))))
        created_date = parse_date(opp.get("created_date", opp.get("create_date", "")))
        close_date = parse_date(opp.get("close_date", opp.get("expected_close", "")))
        stage_date = parse_date(opp.get("stage_date", opp.get("last_stage_change", "")))

        if stage in ("closed_won", "closed_lost"):
            if stage == "closed_won":
                won_values.append(amount)
                if created_date and close_date:
                    days = (close_date - created_date).days
                    if days > 0:
                        cycle_times.append(days)
            else:
                lost_values.append(amount)
            continue

        results["total_opportunities"] += 1
        prob = STAGE_PROBABILITIES.get(stage, 0.20)
        weighted = amount * prob

        results["total_pipeline_value"] += amount
        results["weighted_pipeline_value"] += weighted

        stage_deals[stage].append({
            "name": opp.get("name", opp.get("deal_name", opp.get("opportunity", "Unknown"))),
            "amount": amount,
            "weighted": round(weighted, 2),
            "close_date": close_date.strftime("%Y-%m-%d") if close_date else "Not set",
        })
        stage_values[stage] += amount
        stage_counts[stage] += 1

        # Check aging
        if stage_date:
            days_in_stage = (today - stage_date).days
            threshold = AGING_THRESHOLDS.get(stage, 21)
            if days_in_stage > threshold:
                results["aging_alerts"].append({
                    "deal": opp.get("name", opp.get("deal_name", "Unknown")),
                    "stage": stage,
                    "days_in_stage": days_in_stage,
                    "threshold": threshold,
                    "amount": amount,
                })

    # Coverage ratios
    if quota > 0:
        results["coverage_ratio"] = round(results["total_pipeline_value"] / quota, 2)
        results["weighted_coverage"] = round(results["weighted_pipeline_value"] / quota, 2)

    # Stage summary
    for stage in sorted(stage_counts.keys(), key=lambda s: STAGE_ORDER.get(s, 99)):
        results["stage_summary"][stage] = {
            "count": stage_counts[stage],
            "total_value": round(stage_values[stage], 2),
            "avg_deal_size": round(stage_values[stage] / stage_counts[stage], 2) if stage_counts[stage] > 0 else 0,
            "probability": STAGE_PROBABILITIES.get(stage, 0.20),
            "weighted_value": round(stage_values[stage] * STAGE_PROBABILITIES.get(stage, 0.20), 2),
        }

    # Velocity metrics
    total_won = len(won_values)
    total_lost = len(lost_values)
    total_decided = total_won + total_lost
    results["velocity_metrics"] = {
        "avg_cycle_time_days": round(sum(cycle_times) / len(cycle_times), 1) if cycle_times else 0,
        "median_cycle_time_days": sorted(cycle_times)[len(cycle_times) // 2] if cycle_times else 0,
        "win_rate": round(total_won / total_decided * 100, 1) if total_decided > 0 else 0,
        "avg_won_deal_size": round(sum(won_values) / total_won, 2) if won_values else 0,
        "avg_lost_deal_size": round(sum(lost_values) / total_lost, 2) if lost_values else 0,
        "total_won": total_won,
        "total_lost": total_lost,
    }

    # Forecast
    gap = quota - results["weighted_pipeline_value"]
    open_pipeline = results["total_pipeline_value"]
    win_rate = results["velocity_metrics"]["win_rate"]
    required_win_rate = (gap / open_pipeline * 100) if open_pipeline > 0 and gap > 0 else 0

    results["forecast"] = {
        "weighted_forecast": round(results["weighted_pipeline_value"], 2),
        "gap_to_quota": round(max(gap, 0), 2),
        "gap_percentage": round(max(gap, 0) / quota * 100, 1) if quota > 0 else 0,
        "required_win_rate": round(required_win_rate, 1),
        "current_win_rate": win_rate,
        "on_track": gap <= 0,
    }

    results["total_pipeline_value"] = round(results["total_pipeline_value"], 2)
    results["weighted_pipeline_value"] = round(results["weighted_pipeline_value"], 2)

    return results


def format_human(results):
    """Format results for human-readable output."""
    lines = []
    lines.append("=" * 70)
    lines.append("PIPELINE ANALYSIS REPORT")
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("=" * 70)

    lines.append(f"\n  Open Opportunities:    {results['total_opportunities']}")
    lines.append(f"  Total Pipeline Value:  ${results['total_pipeline_value']:,.2f}")
    lines.append(f"  Weighted Pipeline:     ${results['weighted_pipeline_value']:,.2f}")
    lines.append(f"  Quota:                 ${results['quota']:,.2f}")
    lines.append(f"  Coverage Ratio:        {results['coverage_ratio']}x")
    lines.append(f"  Weighted Coverage:     {results['weighted_coverage']}x")

    cov = results["coverage_ratio"]
    if cov >= 4:
        lines.append("  Coverage Status:       HEALTHY (4x+)")
    elif cov >= 3:
        lines.append("  Coverage Status:       ADEQUATE (3x)")
    elif cov >= 2:
        lines.append("  Coverage Status:       WARNING (below 3x)")
    else:
        lines.append("  Coverage Status:       CRITICAL (below 2x)")

    lines.append(f"\n{'STAGE BREAKDOWN':^70}")
    lines.append("-" * 70)
    lines.append(f"  {'Stage':<16} {'Count':>6} {'Value':>14} {'Prob':>6} {'Weighted':>14}")
    lines.append("  " + "-" * 58)
    for stage, data in results["stage_summary"].items():
        lines.append(
            f"  {stage:<16} {data['count']:>6} "
            f"${data['total_value']:>12,.2f} "
            f"{data['probability']:>5.0%} "
            f"${data['weighted_value']:>12,.2f}"
        )

    vm = results["velocity_metrics"]
    lines.append(f"\n{'VELOCITY METRICS':^70}")
    lines.append("-" * 70)
    lines.append(f"  Avg Sales Cycle:     {vm['avg_cycle_time_days']} days")
    lines.append(f"  Median Sales Cycle:  {vm['median_cycle_time_days']} days")
    lines.append(f"  Win Rate:            {vm['win_rate']}%")
    lines.append(f"  Avg Won Deal Size:   ${vm['avg_won_deal_size']:,.2f}")
    lines.append(f"  Won Deals:           {vm['total_won']}")
    lines.append(f"  Lost Deals:          {vm['total_lost']}")

    fc = results["forecast"]
    lines.append(f"\n{'FORECAST':^70}")
    lines.append("-" * 70)
    lines.append(f"  Weighted Forecast:     ${fc['weighted_forecast']:,.2f}")
    lines.append(f"  Gap to Quota:          ${fc['gap_to_quota']:,.2f} ({fc['gap_percentage']}%)")
    lines.append(f"  Required Win Rate:     {fc['required_win_rate']}%")
    lines.append(f"  Current Win Rate:      {fc['current_win_rate']}%")
    status = "ON TRACK" if fc["on_track"] else "AT RISK"
    lines.append(f"  Status:                {status}")

    if results["aging_alerts"]:
        lines.append(f"\n{'AGING ALERTS':^70}")
        lines.append("-" * 70)
        for alert in sorted(results["aging_alerts"], key=lambda a: a["days_in_stage"], reverse=True):
            lines.append(
                f"  {alert['deal']:<30} {alert['stage']:<14} "
                f"{alert['days_in_stage']}d (threshold: {alert['threshold']}d)  "
                f"${alert['amount']:,.2f}"
            )

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Analyze sales pipeline for coverage, velocity, and forecast accuracy."
    )
    parser.add_argument("--data", required=True, help="Path to opportunities CSV or JSON file")
    parser.add_argument(
        "--quota", type=float, default=2500000, help="Quarterly quota target (default: 2500000)"
    )
    parser.add_argument("--json", action="store_true", help="Output results as JSON")

    args = parser.parse_args()

    if not os.path.exists(args.data):
        print(f"Error: File not found: {args.data}", file=sys.stderr)
        sys.exit(1)

    opportunities = load_data(args.data)
    if not opportunities:
        print("Error: No opportunities found in input file.", file=sys.stderr)
        sys.exit(1)

    results = analyze_pipeline(opportunities, args.quota)

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(format_human(results))

    sys.exit(0 if results["forecast"]["on_track"] else 1)


if __name__ == "__main__":
    main()
