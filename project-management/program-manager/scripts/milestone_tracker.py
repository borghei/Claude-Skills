#!/usr/bin/env python3
"""Milestone Tracker - Track program milestones with status and trend analysis.

Reads milestone data and produces a timeline view with status indicators,
critical path highlighting, and schedule health assessment.

Usage:
    python milestone_tracker.py --milestones milestones.json
    python milestone_tracker.py --milestones milestones.json --json
    python milestone_tracker.py --example
"""

import argparse
import json
import sys
from datetime import datetime, timedelta


def load_data(path: str) -> dict:
    """Load milestone data from JSON file."""
    with open(path, "r") as f:
        return json.load(f)


def parse_date(s: str) -> datetime:
    """Parse date string."""
    for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    raise ValueError(f"Cannot parse date: {s}")


def analyze_milestones(data: dict) -> dict:
    """Analyze milestone status and trends."""
    program = data.get("program", "Unknown")
    milestones = data.get("milestones", [])
    today = datetime.now()

    results = []
    total = len(milestones)
    completed = 0
    on_track = 0
    at_risk = 0
    overdue = 0
    total_variance_days = 0

    for ms in milestones:
        name = ms.get("name", "Unknown")
        project = ms.get("project", "Unknown")
        planned_str = ms.get("planned_date", "")
        actual_str = ms.get("actual_date", "")
        status = ms.get("status", "Not Started")
        is_critical = ms.get("critical_path", False)
        dependencies = ms.get("dependencies", [])

        planned = parse_date(planned_str) if planned_str else None
        actual = parse_date(actual_str) if actual_str else None

        # Calculate variance
        variance_days = 0
        if status == "Complete" and planned and actual:
            variance_days = (actual - planned).days
            completed += 1
        elif status == "In Progress" and planned:
            days_until = (planned - today).days
            if days_until < 0:
                variance_days = days_until
                overdue += 1
            elif days_until <= 7:
                at_risk += 1
            else:
                on_track += 1
        elif status == "Not Started" and planned:
            days_until = (planned - today).days
            if days_until < 0:
                variance_days = days_until
                overdue += 1
            else:
                on_track += 1

        total_variance_days += abs(variance_days)

        # RAG for this milestone
        if status == "Complete":
            if variance_days <= 0:
                rag = "GREEN"
            elif variance_days <= 5:
                rag = "AMBER"
            else:
                rag = "RED"
        elif status == "In Progress":
            if planned and (planned - today).days < 0:
                rag = "RED"
            elif planned and (planned - today).days <= 7:
                rag = "AMBER"
            else:
                rag = "GREEN"
        else:
            if planned and (planned - today).days < 0:
                rag = "RED"
            else:
                rag = "GREEN"

        results.append({
            "name": name,
            "project": project,
            "planned_date": planned_str,
            "actual_date": actual_str if actual_str else None,
            "status": status,
            "rag": rag,
            "variance_days": variance_days,
            "critical_path": is_critical,
            "dependencies": dependencies,
        })

    # Sort by planned date
    results.sort(key=lambda x: x["planned_date"] if x["planned_date"] else "9999-99-99")

    # Schedule health
    not_completed = total - completed
    if overdue > 0:
        schedule_health = "AT RISK"
    elif at_risk > not_completed * 0.3:
        schedule_health = "CAUTION"
    else:
        schedule_health = "ON TRACK"

    # Critical path analysis
    critical_milestones = [m for m in results if m["critical_path"]]
    critical_overdue = [m for m in critical_milestones if m["rag"] == "RED"]

    # Recommendations
    recs = []
    if critical_overdue:
        recs.append(f"{len(critical_overdue)} critical-path milestone(s) are overdue. This directly impacts the program end date -- escalate immediately.")
    if overdue > 0:
        recs.append(f"{overdue} milestone(s) overdue. Review scope, add resources, or negotiate new dates with stakeholders.")
    if at_risk > 0:
        recs.append(f"{at_risk} milestone(s) due within 7 days. Confirm delivery readiness and clear any blockers.")

    upcoming_7d = [m for m in results if m["status"] != "Complete" and m["planned_date"] and 0 <= (parse_date(m["planned_date"]) - today).days <= 7]
    if upcoming_7d:
        recs.append(f"Upcoming this week: {', '.join(m['name'] for m in upcoming_7d)}")

    return {
        "program": program,
        "date": today.strftime("%Y-%m-%d"),
        "schedule_health": schedule_health,
        "total_milestones": total,
        "completed": completed,
        "on_track": on_track,
        "at_risk": at_risk,
        "overdue": overdue,
        "completion_pct": round(completed / total * 100, 1) if total > 0 else 0,
        "milestones": results,
        "critical_path_count": len(critical_milestones),
        "critical_overdue": len(critical_overdue),
        "recommendations": recs,
    }


def print_report(result: dict) -> None:
    """Print human-readable milestone report."""
    print(f"\nMilestone Tracker: {result['program']}")
    print(f"Date: {result['date']}")
    print("=" * 75)
    print(f"Schedule Health: {result['schedule_health']}")
    print(f"Milestones: {result['completed']}/{result['total_milestones']} complete ({result['completion_pct']:.0f}%)")
    print(f"  On Track: {result['on_track']}  |  At Risk: {result['at_risk']}  |  Overdue: {result['overdue']}")
    print(f"  Critical Path: {result['critical_path_count']} milestones ({result['critical_overdue']} overdue)")

    print(f"\nTimeline:")
    print(f"  {'Status':<6} {'Milestone':<30} {'Project':<15} {'Planned':<12} {'Actual':<12} {'Var':>5} {'CP'}")
    print(f"  {'-'*6} {'-'*30} {'-'*15} {'-'*12} {'-'*12} {'-'*5} {'-'*3}")
    for m in result["milestones"]:
        name = m["name"][:28] + ".." if len(m["name"]) > 30 else m["name"]
        project = m["project"][:13] + ".." if len(m["project"]) > 15 else m["project"]
        actual = m["actual_date"] if m["actual_date"] else "---"
        var = f"{m['variance_days']:+d}d" if m["variance_days"] != 0 else "0d"
        cp = "*" if m["critical_path"] else ""
        rag_icon = {"GREEN": "[G]", "AMBER": "[A]", "RED": "[R]"}.get(m["rag"], "[?]")
        print(f"  {rag_icon:<6} {name:<30} {project:<15} {m['planned_date']:<12} {actual:<12} {var:>5} {cp}")

    if result["recommendations"]:
        print(f"\nRecommendations:")
        for i, r in enumerate(result["recommendations"], 1):
            print(f"  {i}. {r}")
    print()


def print_example() -> None:
    """Print example milestone data JSON."""
    example = {
        "program": "Digital Transformation",
        "milestones": [
            {"name": "Requirements Complete", "project": "API Migration", "planned_date": "2026-02-01", "actual_date": "2026-02-03", "status": "Complete", "critical_path": True, "dependencies": []},
            {"name": "API v2 Released", "project": "API Migration", "planned_date": "2026-03-15", "actual_date": "2026-03-14", "status": "Complete", "critical_path": True, "dependencies": ["Requirements Complete"]},
            {"name": "Beta Launch", "project": "Frontend Rebuild", "planned_date": "2026-04-01", "status": "In Progress", "critical_path": True, "dependencies": ["API v2 Released"]},
            {"name": "Data Schema Finalized", "project": "Analytics Platform", "planned_date": "2026-03-20", "status": "In Progress", "critical_path": False, "dependencies": []},
            {"name": "UAT Complete", "project": "Frontend Rebuild", "planned_date": "2026-04-15", "status": "Not Started", "critical_path": True, "dependencies": ["Beta Launch"]},
            {"name": "Go Live", "project": "Frontend Rebuild", "planned_date": "2026-05-01", "status": "Not Started", "critical_path": True, "dependencies": ["UAT Complete"]},
        ],
    }
    print(json.dumps(example, indent=2))


def main():
    parser = argparse.ArgumentParser(
        description="Track program milestones with status and trend analysis."
    )
    parser.add_argument("--milestones", type=str, help="Path to milestones JSON file")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    parser.add_argument("--example", action="store_true", help="Print example milestones JSON and exit")
    args = parser.parse_args()

    if args.example:
        print_example()
        return

    if not args.milestones:
        parser.error("--milestones is required (use --example to see the expected format)")

    data = load_data(args.milestones)
    result = analyze_milestones(data)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print_report(result)


if __name__ == "__main__":
    main()
