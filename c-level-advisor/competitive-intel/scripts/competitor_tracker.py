#!/usr/bin/env python3
"""
Competitor Tracker - Track competitor movements across 8 dimensions over time.

Detects significant changes, generates alerts, calculates movement velocity,
and produces tracking summaries by competitor and dimension.

Usage:
    python competitor_tracker.py --input tracking_data.json
    python competitor_tracker.py --input tracking_data.json --json
"""

import argparse
import json
import sys
from datetime import datetime


DIMENSIONS = [
    "product", "pricing", "funding", "hiring",
    "partnerships", "customers", "messaging", "market_share"
]

SIGNIFICANCE_THRESHOLDS = {
    "product": 2,
    "pricing": 1,
    "funding": 1,
    "hiring": 2,
    "partnerships": 1,
    "customers": 2,
    "messaging": 2,
    "market_share": 1,
}


def load_data(path):
    with open(path, "r") as f:
        return json.load(f)


def calculate_change(current, previous):
    """Calculate absolute and percentage change."""
    if previous == 0:
        return current, 0 if current == 0 else 100.0
    abs_change = current - previous
    pct_change = round((abs_change / abs(previous)) * 100, 1)
    return abs_change, pct_change


def detect_alerts(competitor_name, dimension, abs_change, pct_change, current_value):
    """Detect significant changes that warrant alerts."""
    threshold = SIGNIFICANCE_THRESHOLDS.get(dimension, 2)
    alerts = []

    if abs(abs_change) >= threshold:
        direction = "increased" if abs_change > 0 else "decreased"
        severity = "HIGH" if abs(pct_change) >= 30 else "MEDIUM"
        alerts.append({
            "competitor": competitor_name,
            "dimension": dimension,
            "severity": severity,
            "message": f"{dimension} {direction} by {abs(abs_change)} ({abs(pct_change)}%)",
            "current_value": current_value,
            "change": abs_change,
        })

    return alerts


def analyze_tracking(data):
    """Analyze competitor tracking data over time."""
    competitors = data.get("competitors", [])
    analysis_date = data.get("analysis_date", datetime.now().strftime("%Y-%m-%d"))

    results = {
        "timestamp": datetime.now().isoformat(),
        "analysis_date": analysis_date,
        "competitors_tracked": len(competitors),
        "alerts": [],
        "competitor_summaries": [],
        "dimension_trends": {},
        "recommended_actions": [],
    }

    all_alerts = []

    for comp in competitors:
        name = comp.get("name", "Unknown")
        entries = comp.get("tracking_entries", [])

        if len(entries) < 2:
            results["competitor_summaries"].append({
                "name": name,
                "status": "Insufficient data (need 2+ entries)",
                "changes": [],
            })
            continue

        # Sort entries by date
        entries.sort(key=lambda x: x.get("date", ""))
        latest = entries[-1]
        previous = entries[-2]

        changes = []
        movement_score = 0

        for dim in DIMENSIONS:
            current_val = latest.get("scores", {}).get(dim, 0)
            prev_val = previous.get("scores", {}).get(dim, 0)

            abs_change, pct_change = calculate_change(current_val, prev_val)

            if abs_change != 0:
                changes.append({
                    "dimension": dim,
                    "previous": prev_val,
                    "current": current_val,
                    "change": abs_change,
                    "pct_change": pct_change,
                })
                movement_score += abs(abs_change)

                alerts = detect_alerts(name, dim, abs_change, pct_change, current_val)
                all_alerts.extend(alerts)

        # Calculate overall trajectory
        total_current = sum(latest.get("scores", {}).get(d, 0) for d in DIMENSIONS)
        total_previous = sum(previous.get("scores", {}).get(d, 0) for d in DIMENSIONS)
        trajectory = "strengthening" if total_current > total_previous else (
            "weakening" if total_current < total_previous else "stable"
        )

        results["competitor_summaries"].append({
            "name": name,
            "tier": comp.get("tier", 0),
            "trajectory": trajectory,
            "movement_score": movement_score,
            "total_score_current": total_current,
            "total_score_previous": total_previous,
            "period": f"{previous.get('date', '?')} to {latest.get('date', '?')}",
            "changes": sorted(changes, key=lambda x: abs(x["change"]), reverse=True),
            "entries_count": len(entries),
        })

    # Sort summaries by movement score
    results["competitor_summaries"].sort(key=lambda x: x.get("movement_score", 0), reverse=True)

    # Sort alerts by severity
    severity_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    all_alerts.sort(key=lambda x: severity_order.get(x["severity"], 2))
    results["alerts"] = all_alerts

    # Dimension trends across all competitors
    for dim in DIMENSIONS:
        improving = 0
        declining = 0
        stable = 0
        for summary in results["competitor_summaries"]:
            for change in summary.get("changes", []):
                if change["dimension"] == dim:
                    if change["change"] > 0:
                        improving += 1
                    elif change["change"] < 0:
                        declining += 1
                    else:
                        stable += 1
        results["dimension_trends"][dim] = {
            "competitors_improving": improving,
            "competitors_declining": declining,
            "competitors_stable": stable,
        }

    # Generate recommended actions
    high_alerts = [a for a in all_alerts if a["severity"] == "HIGH"]
    if high_alerts:
        results["recommended_actions"].append(
            f"URGENT: {len(high_alerts)} high-severity changes detected -- review within 48 hours"
        )
    strengthening = [s for s in results["competitor_summaries"] if s.get("trajectory") == "strengthening"]
    if strengthening:
        names = ", ".join(s["name"] for s in strengthening[:3])
        results["recommended_actions"].append(
            f"Monitor: {names} showing strengthening trajectory"
        )
    for dim, trend in results["dimension_trends"].items():
        if trend["competitors_improving"] >= 3:
            results["recommended_actions"].append(
                f"Industry trend: {trend['competitors_improving']} competitors improving on {dim}"
            )

    return results


def format_text(results):
    """Format results as human-readable text."""
    lines = [
        "=" * 60,
        "COMPETITOR TRACKING REPORT",
        "=" * 60,
        f"Analysis Date: {results['analysis_date']}",
        f"Competitors Tracked: {results['competitors_tracked']}",
        "",
    ]

    if results["alerts"]:
        lines.append("ALERTS")
        for a in results["alerts"]:
            lines.append(f"  [{a['severity']}] {a['competitor']}: {a['message']}")
        lines.append("")

    lines.append("COMPETITOR SUMMARIES")
    for s in results["competitor_summaries"]:
        if s.get("status"):
            lines.append(f"\n  {s['name']}: {s['status']}")
            continue
        lines.append(f"\n  {s['name']} (Tier {s.get('tier', '?')})")
        lines.append(f"    Trajectory: {s['trajectory'].upper()}")
        lines.append(f"    Movement Score: {s['movement_score']}")
        lines.append(f"    Period: {s['period']}")
        if s["changes"]:
            lines.append("    Changes:")
            for c in s["changes"][:5]:
                direction = "+" if c["change"] > 0 else ""
                lines.append(
                    f"      {c['dimension']}: {c['previous']} -> {c['current']} "
                    f"({direction}{c['change']}, {c['pct_change']}%)"
                )

    if results["dimension_trends"]:
        lines.append("")
        lines.append("DIMENSION TRENDS")
        for dim, trend in results["dimension_trends"].items():
            lines.append(
                f"  {dim}: {trend['competitors_improving']} improving, "
                f"{trend['competitors_declining']} declining, "
                f"{trend['competitors_stable']} stable"
            )

    if results["recommended_actions"]:
        lines.append("")
        lines.append("RECOMMENDED ACTIONS")
        for action in results["recommended_actions"]:
            lines.append(f"  * {action}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Track competitor movements across 8 dimensions over time"
    )
    parser.add_argument("--input", required=True, help="Path to JSON tracking data file")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    args = parser.parse_args()

    try:
        data = load_data(args.input)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading input file: {e}", file=sys.stderr)
        sys.exit(1)

    results = analyze_tracking(data)

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(format_text(results))


if __name__ == "__main__":
    main()
