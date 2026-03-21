#!/usr/bin/env python3
"""Action Item Tracker - Track meeting action items across multiple meetings.

Aggregates action items from meeting summaries and tracks completion status,
overdue items, and per-person accountability.

Usage:
    python action_item_tracker.py --meetings meetings.json
    python action_item_tracker.py --meetings meetings.json --json
    python action_item_tracker.py --example
"""

import argparse
import json
import sys
from datetime import datetime
from collections import defaultdict


def load_data(path: str) -> dict:
    with open(path, "r") as f:
        return json.load(f)


def parse_date(s: str) -> datetime:
    for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    return None


def analyze_actions(data: dict) -> dict:
    meetings = data.get("meetings", [])
    today = datetime.now()

    all_actions = []
    for meeting in meetings:
        meeting_date = meeting.get("date", "Unknown")
        meeting_topic = meeting.get("topic", "Unknown")
        for action in meeting.get("action_items", []):
            action["meeting_date"] = meeting_date
            action["meeting_topic"] = meeting_topic
            all_actions.append(action)

    # Classify actions
    completed = []
    overdue = []
    upcoming = []
    no_date = []

    person_stats = defaultdict(lambda: {"total": 0, "completed": 0, "overdue": 0})

    for action in all_actions:
        owner = action.get("owner", "Unassigned")
        status = action.get("status", "open").lower()
        due_str = action.get("due_date", "")
        due_dt = parse_date(due_str) if due_str else None

        person_stats[owner]["total"] += 1

        if status in ("done", "complete", "completed"):
            completed.append(action)
            person_stats[owner]["completed"] += 1
        elif due_dt and due_dt < today:
            overdue.append(action)
            person_stats[owner]["overdue"] += 1
        elif due_dt:
            upcoming.append(action)
        else:
            no_date.append(action)

    # Sort overdue by most overdue first
    for a in overdue:
        due_dt = parse_date(a.get("due_date", ""))
        a["days_overdue"] = (today - due_dt).days if due_dt else 0
    overdue.sort(key=lambda x: x.get("days_overdue", 0), reverse=True)

    # Person accountability
    person_results = []
    for person, stats in sorted(person_stats.items()):
        completion_rate = round(stats["completed"] / stats["total"] * 100) if stats["total"] > 0 else 0
        person_results.append({
            "person": person,
            "total": stats["total"],
            "completed": stats["completed"],
            "overdue": stats["overdue"],
            "completion_rate_pct": completion_rate,
        })
    person_results.sort(key=lambda x: x["completion_rate_pct"])

    total = len(all_actions)
    completion_rate = round(len(completed) / total * 100, 1) if total > 0 else 0

    recs = []
    if overdue:
        top_overdue_owners = list(set(a.get("owner", "Unknown") for a in overdue[:5]))
        recs.append(f"{len(overdue)} overdue action item(s). Top owners: {', '.join(top_overdue_owners)}")
    if no_date:
        recs.append(f"{len(no_date)} action item(s) without due dates. Add specific dates for accountability.")
    if completion_rate < 70:
        recs.append(f"Completion rate is {completion_rate:.0f}% (target: 80%+). Review blockers in next meeting.")

    return {
        "analysis_date": today.strftime("%Y-%m-%d"),
        "total_meetings": len(meetings),
        "total_actions": total,
        "completed": len(completed),
        "overdue": len(overdue),
        "upcoming": len(upcoming),
        "no_due_date": len(no_date),
        "completion_rate_pct": completion_rate,
        "overdue_items": [
            {"action": a.get("action"), "owner": a.get("owner"), "due_date": a.get("due_date"), "days_overdue": a.get("days_overdue", 0), "meeting": a.get("meeting_topic")}
            for a in overdue[:10]
        ],
        "person_accountability": person_results,
        "recommendations": recs,
    }


def print_report(result: dict) -> None:
    print(f"\nAction Item Tracker")
    print(f"Date: {result['analysis_date']}  |  Meetings: {result['total_meetings']}")
    print("=" * 65)
    print(f"Total: {result['total_actions']}  |  Done: {result['completed']}  |  Overdue: {result['overdue']}  |  Upcoming: {result['upcoming']}")
    print(f"Completion Rate: {result['completion_rate_pct']:.0f}%")

    if result["overdue_items"]:
        print(f"\nOverdue Items:")
        for item in result["overdue_items"]:
            print(f"  [{item['days_overdue']}d overdue] {item['owner']}: {item['action'][:50]} (due: {item['due_date']})")

    print(f"\nPerson Accountability:")
    print(f"  {'Person':<20} {'Total':>6} {'Done':>6} {'Overdue':>8} {'Rate':>6}")
    print(f"  {'-'*20} {'-'*6} {'-'*6} {'-'*8} {'-'*6}")
    for p in result["person_accountability"]:
        print(f"  {p['person']:<20} {p['total']:>6} {p['completed']:>6} {p['overdue']:>8} {p['completion_rate_pct']:>5}%")

    if result["recommendations"]:
        print(f"\nRecommendations:")
        for i, r in enumerate(result["recommendations"], 1):
            print(f"  {i}. {r}")
    print()


def print_example() -> None:
    example = {
        "meetings": [
            {
                "date": "2026-03-14",
                "topic": "Sprint Planning",
                "action_items": [
                    {"action": "Draft API spec for new endpoint", "owner": "Alice", "due_date": "2026-03-18", "status": "complete"},
                    {"action": "Set up staging environment", "owner": "Bob", "due_date": "2026-03-16", "status": "open"},
                ],
            },
            {
                "date": "2026-03-07",
                "topic": "Stakeholder Review",
                "action_items": [
                    {"action": "Prepare Q1 metrics report", "owner": "Carol", "due_date": "2026-03-10", "status": "open"},
                    {"action": "Schedule design review", "owner": "Alice", "due_date": "2026-03-12", "status": "complete"},
                ],
            },
        ],
    }
    print(json.dumps(example, indent=2))


def main():
    parser = argparse.ArgumentParser(description="Track meeting action items.")
    parser.add_argument("--meetings", type=str, help="Path to meetings JSON file")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--example", action="store_true", help="Print example and exit")
    args = parser.parse_args()

    if args.example:
        print_example()
        return
    if not args.meetings:
        parser.error("--meetings is required")

    data = load_data(args.meetings)
    result = analyze_actions(data)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print_report(result)


if __name__ == "__main__":
    main()
