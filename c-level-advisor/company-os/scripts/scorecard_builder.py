#!/usr/bin/env python3
"""
Company Scorecard Builder - Build and track weekly company scorecards.

Manages 5-15 weekly metrics with owners, targets, and RAG status.
Identifies trends, flags issues for L10 discussion, and generates
IDS-ready issue lists.
"""

import argparse
import json
import sys
from datetime import datetime


def build_scorecard(data: dict) -> dict:
    """Build company scorecard with status and trends."""
    metrics = data.get("metrics", [])
    weeks_of_data = data.get("weeks", 1)

    results = {
        "timestamp": datetime.now().isoformat(),
        "metrics_count": len(metrics),
        "summary": {"green": 0, "yellow": 0, "red": 0},
        "scorecard": [],
        "issues_for_ids": [],
        "rocks_status": [],
        "recommendations": [],
    }

    if len(metrics) > 15:
        results["recommendations"].append(f"Too many metrics ({len(metrics)}). Maximum 15. Cut to focus attention.")
    elif len(metrics) < 5:
        results["recommendations"].append(f"Only {len(metrics)} metrics. Consider adding to cover blind spots.")

    for m in metrics:
        name = m.get("name", "")
        owner = m.get("owner", "Unassigned")
        target = m.get("target", 0)
        current = m.get("current", 0)
        previous = m.get("previous", None)
        direction = m.get("direction", "higher_is_better")
        fmt = m.get("format", "number")
        weeks_red = m.get("consecutive_weeks_red", 0)

        # RAG calculation
        if target == 0:
            status = "N/A"
        elif direction == "higher_is_better":
            ratio = current / target
            status = "G" if ratio >= 0.95 else "Y" if ratio >= 0.85 else "R"
        elif direction == "lower_is_better":
            ratio = current / target
            status = "G" if ratio <= 1.05 else "Y" if ratio <= 1.15 else "R"
        else:
            status = "G" if abs(current - target) / target < 0.05 else "Y" if abs(current - target) / target < 0.10 else "R"

        # Trend
        if previous is not None:
            if direction == "higher_is_better":
                trend = "Improving" if current > previous else "Declining" if current < previous else "Flat"
            else:
                trend = "Improving" if current < previous else "Declining" if current > previous else "Flat"
        else:
            trend = "N/A"

        metric_result = {
            "name": name,
            "owner": owner,
            "target": target,
            "current": current,
            "previous": previous,
            "status": status,
            "trend": trend,
            "consecutive_weeks_red": weeks_red + (1 if status == "R" else 0),
            "needs_discussion": status == "R",
        }
        results["scorecard"].append(metric_result)

        if status == "G":
            results["summary"]["green"] += 1
        elif status == "Y":
            results["summary"]["yellow"] += 1
        elif status == "R":
            results["summary"]["red"] += 1
            results["issues_for_ids"].append({
                "metric": name,
                "owner": owner,
                "current_value": current,
                "target": target,
                "weeks_red": metric_result["consecutive_weeks_red"],
                "suggested_ids_format": f"IDENTIFY: {name} is below target ({current} vs {target}). Root cause?",
            })

    # Rocks status
    rocks = data.get("rocks", [])
    for rock in rocks:
        results["rocks_status"].append({
            "rock": rock.get("description", ""),
            "owner": rock.get("owner", ""),
            "status": rock.get("status", "on_track"),
            "due": rock.get("due_date", ""),
        })

    # Recommendations
    red_count = results["summary"]["red"]
    if red_count >= 3:
        results["recommendations"].append(f"{red_count} metrics in RED. Prioritize in L10 IDS discussion.")
    chronic_red = [m for m in results["scorecard"] if m["consecutive_weeks_red"] >= 3]
    if chronic_red:
        results["recommendations"].append(
            f"{len(chronic_red)} metric(s) red for 3+ weeks: {', '.join(m['name'] for m in chronic_red)}. "
            "Either the target is wrong or the plan isn't working. Force resolution."
        )

    off_track_rocks = [r for r in results["rocks_status"] if r["status"] == "off_track"]
    if off_track_rocks:
        results["recommendations"].append(f"{len(off_track_rocks)} rock(s) off track. Address in L10.")

    return results


def format_text(results: dict) -> str:
    """Format as L10-ready scorecard."""
    s = results["summary"]
    lines = [
        "=" * 70,
        "WEEKLY SCORECARD",
        "=" * 70,
        f"Date: {results['timestamp'][:10]}  |  {s['green']}G / {s['yellow']}Y / {s['red']}R",
        "",
        f"{'Metric':<22} {'Owner':<10} {'Current':>10} {'Target':>10} {'RAG':>5} {'Trend':<12}",
        "-" * 70,
    ]

    for m in results["scorecard"]:
        rag = f"[{m['status']}]"
        discuss = " <<" if m["needs_discussion"] else ""
        lines.append(
            f"{m['name']:<22} {m['owner']:<10} {m['current']:>10} {m['target']:>10} "
            f"{rag:>5} {m['trend']:<12}{discuss}"
        )

    if results["issues_for_ids"]:
        lines.extend(["", "IDS ISSUES (discuss in L10):"])
        for issue in results["issues_for_ids"]:
            lines.append(f"  >> {issue['suggested_ids_format']} ({issue['owner']}, {issue['weeks_red']}w red)")

    if results["rocks_status"]:
        lines.extend(["", "ROCKS:"])
        for r in results["rocks_status"]:
            icon = "[x]" if r["status"] == "complete" else "[~]" if r["status"] == "on_track" else "[!]"
            lines.append(f"  {icon} {r['rock']} ({r['owner']}, due: {r['due']})")

    if results["recommendations"]:
        lines.extend(["", "RECOMMENDATIONS:"])
        for r in results["recommendations"]:
            lines.append(f"  -> {r}")

    lines.extend(["", "<< = needs L10 discussion", "=" * 70])
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Build and track weekly company scorecard")
    parser.add_argument("--input", "-i", help="JSON file with scorecard data")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    if args.input:
        with open(args.input) as f:
            data = json.load(f)
    else:
        data = {
            "metrics": [
                {"name": "New MRR", "owner": "CRO", "target": 50000, "current": 43000, "previous": 47000, "direction": "higher_is_better", "consecutive_weeks_red": 1},
                {"name": "Logo Churn", "owner": "CS Lead", "target": 1.0, "current": 0.8, "previous": 0.9, "direction": "lower_is_better", "consecutive_weeks_red": 0},
                {"name": "Active Users", "owner": "CPO", "target": 2000, "current": 2150, "previous": 2050, "direction": "higher_is_better", "consecutive_weeks_red": 0},
                {"name": "Deployments/wk", "owner": "CTO", "target": 3, "current": 3, "previous": 3, "direction": "higher_is_better", "consecutive_weeks_red": 0},
                {"name": "Critical Bugs", "owner": "CTO", "target": 0, "current": 2, "previous": 1, "direction": "lower_is_better", "consecutive_weeks_red": 2},
                {"name": "Runway (mo)", "owner": "CFO", "target": 18, "current": 16, "previous": 17, "direction": "higher_is_better", "consecutive_weeks_red": 3},
                {"name": "Offer Accept %", "owner": "CHRO", "target": 85, "current": 90, "previous": 80, "direction": "higher_is_better", "consecutive_weeks_red": 0},
            ],
            "rocks": [
                {"description": "Implement CRM with pipeline stages", "owner": "CRO", "status": "on_track", "due_date": "2026-03-31"},
                {"description": "Hire 3 senior engineers", "owner": "CTO", "status": "off_track", "due_date": "2026-04-15"},
                {"description": "Reduce churn from 3% to 1.5%", "owner": "CS Lead", "status": "on_track", "due_date": "2026-06-30"},
            ],
        }

    results = build_scorecard(data)
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(format_text(results))


if __name__ == "__main__":
    main()
