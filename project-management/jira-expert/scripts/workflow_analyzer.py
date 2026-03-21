#!/usr/bin/env python3
"""Workflow Analyzer - Analyze Jira workflow efficiency and identify bottlenecks.

Reads issue transition data and calculates time-in-status metrics, identifies
bottlenecks, and recommends workflow optimizations.

Usage:
    python workflow_analyzer.py --issues issues.json
    python workflow_analyzer.py --issues issues.json --json
    python workflow_analyzer.py --example
"""

import argparse
import json
import sys
from datetime import datetime, timedelta


def load_data(path: str) -> dict:
    """Load issue data from JSON file."""
    with open(path, "r") as f:
        return json.load(f)


def parse_date(date_str: str) -> datetime:
    """Parse ISO date string."""
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    raise ValueError(f"Cannot parse date: {date_str}")


def analyze_workflow(data: dict) -> dict:
    """Analyze workflow transitions and time-in-status."""
    project = data.get("project", "Unknown")
    issues = data.get("issues", [])

    if not issues:
        return {"project": project, "error": "No issues provided"}

    status_times = {}  # status -> list of durations in hours
    transition_counts = {}  # "from -> to" -> count
    back_transitions = 0
    total_transitions = 0

    for issue in issues:
        transitions = issue.get("transitions", [])
        for i, t in enumerate(transitions):
            from_status = t.get("from_status", "Unknown")
            to_status = t.get("to_status", "Unknown")
            entered = t.get("entered")
            exited = t.get("exited")

            # Track transition counts
            key = f"{from_status} -> {to_status}"
            transition_counts[key] = transition_counts.get(key, 0) + 1
            total_transitions += 1

            # Detect backward transitions (rework)
            standard_flow = ["To Do", "In Progress", "In Review", "QA", "Done"]
            from_idx = standard_flow.index(from_status) if from_status in standard_flow else -1
            to_idx = standard_flow.index(to_status) if to_status in standard_flow else -1
            if from_idx > to_idx >= 0:
                back_transitions += 1

            # Calculate time in status
            if entered and exited:
                try:
                    entered_dt = parse_date(entered)
                    exited_dt = parse_date(exited)
                    hours = (exited_dt - entered_dt).total_seconds() / 3600
                    if hours >= 0:
                        if from_status not in status_times:
                            status_times[from_status] = []
                        status_times[from_status].append(round(hours, 1))
                except ValueError:
                    pass

    # Calculate per-status metrics
    status_metrics = {}
    for status, times in status_times.items():
        avg = sum(times) / len(times)
        sorted_times = sorted(times)
        n = len(sorted_times)
        p50 = sorted_times[n // 2]
        p90 = sorted_times[int(n * 0.9)] if n >= 10 else sorted_times[-1]
        status_metrics[status] = {
            "count": n,
            "avg_hours": round(avg, 1),
            "median_hours": round(p50, 1),
            "p90_hours": round(p90, 1),
            "max_hours": round(max(times), 1),
        }

    # Identify bottleneck (longest average time)
    bottleneck = None
    if status_metrics:
        bottleneck_status = max(status_metrics.items(), key=lambda x: x[1]["avg_hours"])
        bottleneck = {
            "status": bottleneck_status[0],
            "avg_hours": bottleneck_status[1]["avg_hours"],
        }

    # Top transitions
    sorted_transitions = sorted(transition_counts.items(), key=lambda x: x[1], reverse=True)

    # Rework rate
    rework_rate = round(back_transitions / total_transitions * 100, 1) if total_transitions > 0 else 0

    # Recommendations
    recommendations = []
    if bottleneck and bottleneck["avg_hours"] > 24:
        recommendations.append(f"Bottleneck detected at '{bottleneck['status']}' (avg {bottleneck['avg_hours']:.0f}h). Investigate WIP limits, resource allocation, or definition clarity.")
    if rework_rate > 15:
        recommendations.append(f"High rework rate ({rework_rate:.0f}%). Improve Definition of Ready and add acceptance criteria reviews before development starts.")
    elif rework_rate > 5:
        recommendations.append(f"Moderate rework rate ({rework_rate:.0f}%). Consider adding code review checklists and automated quality gates.")

    for status, metrics in status_metrics.items():
        if metrics["p90_hours"] > metrics["avg_hours"] * 3:
            recommendations.append(f"'{status}' has high variance (avg {metrics['avg_hours']:.0f}h, P90 {metrics['p90_hours']:.0f}h). Some issues are stalling -- add aging WIP alerts.")

    if not recommendations:
        recommendations.append("Workflow appears healthy. Continue monitoring and consider reducing WIP limits for further optimization.")

    return {
        "project": project,
        "total_issues": len(issues),
        "total_transitions": total_transitions,
        "rework_rate_pct": rework_rate,
        "status_metrics": status_metrics,
        "bottleneck": bottleneck,
        "top_transitions": [{"transition": t[0], "count": t[1]} for t in sorted_transitions[:10]],
        "recommendations": recommendations,
    }


def print_report(result: dict) -> None:
    """Print human-readable workflow analysis."""
    if "error" in result:
        print(f"Error: {result['error']}")
        return

    print(f"\nWorkflow Analysis: {result['project']}")
    print(f"Issues: {result['total_issues']}  |  Transitions: {result['total_transitions']}")
    print("=" * 65)

    print(f"\nRework Rate: {result['rework_rate_pct']:.1f}%")

    if result["bottleneck"]:
        b = result["bottleneck"]
        print(f"Bottleneck: {b['status']} (avg {b['avg_hours']:.1f} hours)")

    print(f"\nTime-in-Status Metrics:")
    print(f"  {'Status':<20} {'Count':>6} {'Avg(h)':>8} {'Med(h)':>8} {'P90(h)':>8} {'Max(h)':>8}")
    print(f"  {'-'*20} {'-'*6} {'-'*8} {'-'*8} {'-'*8} {'-'*8}")
    for status, m in sorted(result["status_metrics"].items(), key=lambda x: x[1]["avg_hours"], reverse=True):
        print(f"  {status:<20} {m['count']:>6} {m['avg_hours']:>8.1f} {m['median_hours']:>8.1f} {m['p90_hours']:>8.1f} {m['max_hours']:>8.1f}")

    print(f"\nTop Transitions:")
    for t in result["top_transitions"][:5]:
        print(f"  {t['transition']:<35} {t['count']:>5}x")

    print(f"\nRecommendations:")
    for i, r in enumerate(result["recommendations"], 1):
        print(f"  {i}. {r}")
    print()


def print_example() -> None:
    """Print example issues JSON."""
    example = {
        "project": "PROJ",
        "issues": [
            {
                "key": "PROJ-101",
                "type": "Story",
                "transitions": [
                    {"from_status": "To Do", "to_status": "In Progress", "entered": "2026-03-01", "exited": "2026-03-03"},
                    {"from_status": "In Progress", "to_status": "In Review", "entered": "2026-03-03", "exited": "2026-03-05"},
                    {"from_status": "In Review", "to_status": "Done", "entered": "2026-03-05", "exited": "2026-03-06"},
                ],
            },
            {
                "key": "PROJ-102",
                "type": "Bug",
                "transitions": [
                    {"from_status": "To Do", "to_status": "In Progress", "entered": "2026-03-02", "exited": "2026-03-04"},
                    {"from_status": "In Progress", "to_status": "In Review", "entered": "2026-03-04", "exited": "2026-03-07"},
                    {"from_status": "In Review", "to_status": "In Progress", "entered": "2026-03-07", "exited": "2026-03-09"},
                    {"from_status": "In Progress", "to_status": "In Review", "entered": "2026-03-09", "exited": "2026-03-10"},
                    {"from_status": "In Review", "to_status": "Done", "entered": "2026-03-10", "exited": "2026-03-11"},
                ],
            },
        ],
    }
    print(json.dumps(example, indent=2))


def main():
    parser = argparse.ArgumentParser(
        description="Analyze Jira workflow efficiency and identify bottlenecks."
    )
    parser.add_argument("--issues", type=str, help="Path to issues JSON file with transition data")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    parser.add_argument("--example", action="store_true", help="Print example input JSON and exit")
    args = parser.parse_args()

    if args.example:
        print_example()
        return

    if not args.issues:
        parser.error("--issues is required (use --example to see the expected format)")

    data = load_data(args.issues)
    result = analyze_workflow(data)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print_report(result)


if __name__ == "__main__":
    main()
