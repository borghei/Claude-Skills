#!/usr/bin/env python3
"""Goal Tracker - Track executive development goals with progress and accountability.

Manage development goals with status tracking, deadline monitoring, and progress
reporting. Goals are stored in a local JSON file for persistence.

Usage:
    python goal_tracker.py add --goal "Delegate all operational decisions" --deadline 2026-06-01 --category delegation
    python goal_tracker.py list
    python goal_tracker.py update --id 1 --status in-progress --progress 50
    python goal_tracker.py report --json
"""

import argparse
import json
import os
import sys
from datetime import datetime

DEFAULT_STORE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "goals_data.json")

CATEGORIES = [
    "strategic", "communication", "delegation", "decision",
    "people", "eq", "execution", "self_awareness", "other"
]

STATUSES = ["not-started", "in-progress", "completed", "blocked", "cancelled"]


def load_goals(store_path):
    if os.path.exists(store_path):
        with open(store_path, "r") as f:
            return json.load(f)
    return {"goals": [], "next_id": 1}


def save_goals(data, store_path):
    with open(store_path, "w") as f:
        json.dump(data, f, indent=2)


def add_goal(data, goal_text, deadline, category, owner):
    goal = {
        "id": data["next_id"],
        "goal": goal_text,
        "category": category,
        "owner": owner,
        "status": "not-started",
        "progress": 0,
        "deadline": deadline,
        "created": datetime.now().strftime("%Y-%m-%d"),
        "updated": datetime.now().strftime("%Y-%m-%d"),
        "notes": []
    }
    data["goals"].append(goal)
    data["next_id"] += 1
    return goal


def update_goal(data, goal_id, status=None, progress=None, note=None):
    for goal in data["goals"]:
        if goal["id"] == goal_id:
            if status:
                goal["status"] = status
            if progress is not None:
                goal["progress"] = min(100, max(0, progress))
            if note:
                goal["notes"].append({
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "text": note
                })
            goal["updated"] = datetime.now().strftime("%Y-%m-%d")
            return goal
    return None


def generate_report(data):
    today = datetime.now().strftime("%Y-%m-%d")
    goals = data["goals"]

    total = len(goals)
    by_status = {}
    by_category = {}
    overdue = []
    at_risk = []

    for g in goals:
        status = g["status"]
        by_status[status] = by_status.get(status, 0) + 1
        cat = g["category"]
        by_category[cat] = by_category.get(cat, 0) + 1

        if g["deadline"] and g["status"] not in ("completed", "cancelled"):
            if g["deadline"] < today:
                overdue.append(g)
            else:
                days_left = (datetime.strptime(g["deadline"], "%Y-%m-%d") - datetime.now()).days
                expected_progress = max(0, min(100, 100 - (days_left * 100 // 90)))
                if g["progress"] < expected_progress - 20:
                    at_risk.append(g)

    avg_progress = sum(g["progress"] for g in goals) / total if total > 0 else 0

    return {
        "report_date": today,
        "total_goals": total,
        "average_progress": round(avg_progress, 1),
        "by_status": by_status,
        "by_category": by_category,
        "overdue": [{"id": g["id"], "goal": g["goal"], "deadline": g["deadline"]} for g in overdue],
        "at_risk": [{"id": g["id"], "goal": g["goal"], "progress": g["progress"]} for g in at_risk],
        "completion_rate": round(by_status.get("completed", 0) / total * 100, 1) if total > 0 else 0,
        "goals": goals
    }


def print_goals_human(goals):
    if not goals:
        print("No goals found.")
        return
    print(f"\n{'ID':>4}  {'Status':<14} {'Prog':>4}  {'Deadline':<12} {'Category':<16} {'Goal'}")
    print("-" * 90)
    for g in goals:
        status_marker = {"not-started": "[ ]", "in-progress": "[~]", "completed": "[x]", "blocked": "[!]", "cancelled": "[-]"}.get(g["status"], "[ ]")
        print(f"{g['id']:>4}  {status_marker} {g['status']:<10} {g['progress']:>3}%  {g['deadline']:<12} {g['category']:<16} {g['goal'][:40]}")


def print_report_human(report):
    print(f"\n{'='*70}")
    print(f"GOAL TRACKER REPORT - {report['report_date']}")
    print(f"{'='*70}\n")
    print(f"Total Goals: {report['total_goals']}")
    print(f"Average Progress: {report['average_progress']}%")
    print(f"Completion Rate: {report['completion_rate']}%\n")

    print("BY STATUS:")
    for status, count in report["by_status"].items():
        print(f"  {status:<14} {count}")

    print("\nBY CATEGORY:")
    for cat, count in report["by_category"].items():
        print(f"  {cat:<16} {count}")

    if report["overdue"]:
        print(f"\nOVERDUE ({len(report['overdue'])}):")
        for g in report["overdue"]:
            print(f"  [!] #{g['id']} - {g['goal']} (due: {g['deadline']})")

    if report["at_risk"]:
        print(f"\nAT RISK ({len(report['at_risk'])}):")
        for g in report["at_risk"]:
            print(f"  [~] #{g['id']} - {g['goal']} (progress: {g['progress']}%)")

    print()


def main():
    parser = argparse.ArgumentParser(description="Track executive development goals")
    subparsers = parser.add_subparsers(dest="command", help="Command")

    add_parser = subparsers.add_parser("add", help="Add a new goal")
    add_parser.add_argument("--goal", required=True, help="Goal description")
    add_parser.add_argument("--deadline", required=True, help="Deadline (YYYY-MM-DD)")
    add_parser.add_argument("--category", default="other", choices=CATEGORIES, help="Goal category")
    add_parser.add_argument("--owner", default="", help="Goal owner name")
    add_parser.add_argument("--json", action="store_true", help="Output as JSON")
    add_parser.add_argument("--store", default=DEFAULT_STORE, help="Data file path")

    list_parser = subparsers.add_parser("list", help="List all goals")
    list_parser.add_argument("--status", choices=STATUSES, help="Filter by status")
    list_parser.add_argument("--category", choices=CATEGORIES, help="Filter by category")
    list_parser.add_argument("--json", action="store_true", help="Output as JSON")
    list_parser.add_argument("--store", default=DEFAULT_STORE, help="Data file path")

    update_parser = subparsers.add_parser("update", help="Update a goal")
    update_parser.add_argument("--id", type=int, required=True, help="Goal ID")
    update_parser.add_argument("--status", choices=STATUSES, help="New status")
    update_parser.add_argument("--progress", type=int, help="Progress percentage (0-100)")
    update_parser.add_argument("--note", help="Add a note")
    update_parser.add_argument("--json", action="store_true", help="Output as JSON")
    update_parser.add_argument("--store", default=DEFAULT_STORE, help="Data file path")

    report_parser = subparsers.add_parser("report", help="Generate progress report")
    report_parser.add_argument("--json", action="store_true", help="Output as JSON")
    report_parser.add_argument("--store", default=DEFAULT_STORE, help="Data file path")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    data = load_goals(args.store)

    if args.command == "add":
        goal = add_goal(data, args.goal, args.deadline, args.category, args.owner)
        save_goals(data, args.store)
        if args.json:
            print(json.dumps(goal, indent=2))
        else:
            print(f"Goal #{goal['id']} added: {goal['goal']}")

    elif args.command == "list":
        goals = data["goals"]
        if args.status:
            goals = [g for g in goals if g["status"] == args.status]
        if args.category:
            goals = [g for g in goals if g["category"] == args.category]
        if args.json:
            print(json.dumps(goals, indent=2))
        else:
            print_goals_human(goals)

    elif args.command == "update":
        goal = update_goal(data, args.id, args.status, args.progress, args.note)
        if goal:
            save_goals(data, args.store)
            if args.json:
                print(json.dumps(goal, indent=2))
            else:
                print(f"Goal #{goal['id']} updated: {goal['status']} ({goal['progress']}%)")
        else:
            print(f"Error: Goal #{args.id} not found", file=sys.stderr)
            sys.exit(1)

    elif args.command == "report":
        report = generate_report(data)
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            print_report_human(report)


if __name__ == "__main__":
    main()
