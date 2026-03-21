#!/usr/bin/env python3
"""Milestone Tracker - Track founder development milestones across key areas.

Track progress on delegation, leadership evolution, succession readiness, and
personal development milestones. Stored in local JSON for persistence.

Usage:
    python milestone_tracker.py add --category delegation --milestone "Hired first manager"
    python milestone_tracker.py list --category leadership
    python milestone_tracker.py progress
    python milestone_tracker.py report --json
"""

import argparse
import json
import os
import sys
from datetime import datetime

DEFAULT_STORE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "milestones_data.json")

CATEGORIES = {
    "delegation": {
        "name": "Delegation Progress",
        "milestones": [
            "Identified 5 tasks to delegate",
            "Hired first manager",
            "3 tasks at delegation Level 3",
            "Written decision parameters for direct reports",
            "5+ tasks at Level 4-5",
            "Calendar shows < 15% execution time",
            "Team makes decisions without waiting for founder"
        ]
    },
    "leadership": {
        "name": "Leadership Evolution",
        "milestones": [
            "Transitioned from IC to Manager (teaching not doing)",
            "Hired 2+ managers you trust",
            "Leadership team can run company for 2 weeks",
            "Built institutional leadership systems",
            "Potential successor identified",
            "Can articulate leadership style and blind spots",
            "360 feedback shows improving leadership scores"
        ]
    },
    "succession": {
        "name": "Succession Readiness",
        "milestones": [
            "Level 0: Key knowledge documented",
            "Level 1: Processes written down",
            "Level 2: Someone can cover each key function for 2 weeks",
            "Level 3: Leadership team runs company for a quarter",
            "Level 4: Potential successor identified and developing"
        ]
    },
    "wellbeing": {
        "name": "Founder Wellbeing",
        "milestones": [
            "Established exercise routine (3+ days/week)",
            "Sleep consistently 7+ hours",
            "Joined founder peer group",
            "Started therapy or coaching",
            "Protected recovery time on calendar",
            "Took 5+ consecutive days off",
            "Work hours consistently under 55/week"
        ]
    },
    "self_awareness": {
        "name": "Self-Awareness Development",
        "milestones": [
            "Completed founder archetype assessment",
            "Identified top 3 blind spots",
            "Ran first 360 feedback",
            "Created evidence file (wins, mistakes, patterns)",
            "Active mitigation strategy for each blind spot",
            "Re-ran 360 showing improvement",
            "Modeling vulnerability with team"
        ]
    }
}


def load_data(store_path):
    if os.path.exists(store_path):
        with open(store_path, "r") as f:
            return json.load(f)
    return {"milestones": [], "next_id": 1}


def save_data(data, store_path):
    with open(store_path, "w") as f:
        json.dump(data, f, indent=2)


def add_milestone(data, category, milestone_text, notes=""):
    milestone = {
        "id": data["next_id"],
        "category": category,
        "milestone": milestone_text,
        "achieved": True,
        "date_achieved": datetime.now().strftime("%Y-%m-%d"),
        "notes": notes
    }
    data["milestones"].append(milestone)
    data["next_id"] += 1
    return milestone


def list_milestones(data, category=None):
    milestones = data["milestones"]
    if category:
        milestones = [m for m in milestones if m["category"] == category]
    return milestones


def calculate_progress(data):
    progress = {}
    for cat_key, cat_info in CATEGORIES.items():
        total = len(cat_info["milestones"])
        achieved = len([m for m in data["milestones"] if m["category"] == cat_key])
        pct = round(achieved / total * 100) if total > 0 else 0
        progress[cat_key] = {
            "name": cat_info["name"],
            "total_milestones": total,
            "achieved": min(achieved, total),
            "percentage": min(pct, 100),
            "remaining": [
                ms for ms in cat_info["milestones"]
                if not any(m["milestone"] == ms for m in data["milestones"] if m["category"] == cat_key)
            ]
        }
    return progress


def generate_report(data):
    progress = calculate_progress(data)
    recent = sorted(data["milestones"], key=lambda m: m["date_achieved"], reverse=True)[:5]

    total_possible = sum(len(c["milestones"]) for c in CATEGORIES.values())
    total_achieved = len(data["milestones"])
    overall_pct = round(total_achieved / total_possible * 100) if total_possible > 0 else 0

    # Find weakest area
    weakest = min(progress.values(), key=lambda p: p["percentage"])
    strongest = max(progress.values(), key=lambda p: p["percentage"])

    return {
        "report_date": datetime.now().strftime("%Y-%m-%d"),
        "overall_progress": min(overall_pct, 100),
        "total_milestones_achieved": total_achieved,
        "total_milestones_possible": total_possible,
        "category_progress": progress,
        "recent_achievements": [
            {"milestone": m["milestone"], "category": m["category"], "date": m["date_achieved"]}
            for m in recent
        ],
        "weakest_area": {"name": weakest["name"], "percentage": weakest["percentage"]},
        "strongest_area": {"name": strongest["name"], "percentage": strongest["percentage"]},
        "next_recommended": weakest["remaining"][:2] if weakest["remaining"] else []
    }


def print_progress_human(progress):
    print(f"\n{'='*60}")
    print(f"FOUNDER DEVELOPMENT PROGRESS")
    print(f"{'='*60}\n")

    for cat_key, data in progress.items():
        bar_filled = int(data["percentage"] / 5)
        bar = "#" * bar_filled + "." * (20 - bar_filled)
        print(f"  {data['name']:<30s} [{bar}] {data['percentage']:>3}% ({data['achieved']}/{data['total_milestones']})")

        if data["remaining"]:
            print(f"    Next: {data['remaining'][0]}")
    print()


def print_report_human(report):
    print(f"\n{'='*60}")
    print(f"MILESTONE TRACKER REPORT - {report['report_date']}")
    print(f"{'='*60}\n")

    print(f"Overall Progress: {report['overall_progress']}% ({report['total_milestones_achieved']}/{report['total_milestones_possible']})")
    print(f"Strongest: {report['strongest_area']['name']} ({report['strongest_area']['percentage']}%)")
    print(f"Weakest:   {report['weakest_area']['name']} ({report['weakest_area']['percentage']}%)\n")

    print("CATEGORY BREAKDOWN:")
    print("-" * 50)
    for cat_key, data in report["category_progress"].items():
        bar_filled = int(data["percentage"] / 5)
        bar = "#" * bar_filled + "." * (20 - bar_filled)
        print(f"  {data['name']:<30s} [{bar}] {data['percentage']:>3}%")

    if report["recent_achievements"]:
        print(f"\nRECENT ACHIEVEMENTS:")
        for a in report["recent_achievements"]:
            print(f"  [{a['date']}] {a['category']}: {a['milestone']}")

    if report["next_recommended"]:
        print(f"\nNEXT RECOMMENDED MILESTONES:")
        for m in report["next_recommended"]:
            print(f"  [ ] {m}")
    print()


def main():
    parser = argparse.ArgumentParser(description="Track founder development milestones")
    subparsers = parser.add_subparsers(dest="command")

    add_p = subparsers.add_parser("add", help="Record a milestone achievement")
    add_p.add_argument("--category", required=True, choices=list(CATEGORIES.keys()))
    add_p.add_argument("--milestone", required=True, help="Milestone description")
    add_p.add_argument("--notes", default="", help="Additional notes")
    add_p.add_argument("--json", action="store_true")
    add_p.add_argument("--store", default=DEFAULT_STORE)

    list_p = subparsers.add_parser("list", help="List milestones")
    list_p.add_argument("--category", choices=list(CATEGORIES.keys()))
    list_p.add_argument("--json", action="store_true")
    list_p.add_argument("--store", default=DEFAULT_STORE)

    prog_p = subparsers.add_parser("progress", help="Show progress across categories")
    prog_p.add_argument("--json", action="store_true")
    prog_p.add_argument("--store", default=DEFAULT_STORE)

    rep_p = subparsers.add_parser("report", help="Full progress report")
    rep_p.add_argument("--json", action="store_true")
    rep_p.add_argument("--store", default=DEFAULT_STORE)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    data = load_data(args.store)

    if args.command == "add":
        m = add_milestone(data, args.category, args.milestone, args.notes)
        save_data(data, args.store)
        if args.json:
            print(json.dumps(m, indent=2))
        else:
            print(f"Milestone #{m['id']} recorded: {m['milestone']}")

    elif args.command == "list":
        milestones = list_milestones(data, args.category)
        if args.json:
            print(json.dumps(milestones, indent=2))
        else:
            if not milestones:
                print("No milestones recorded.")
            else:
                for m in milestones:
                    print(f"  [{m['date_achieved']}] #{m['id']} {m['category']}: {m['milestone']}")

    elif args.command == "progress":
        progress = calculate_progress(data)
        if args.json:
            print(json.dumps(progress, indent=2))
        else:
            print_progress_human(progress)

    elif args.command == "report":
        report = generate_report(data)
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            print_report_human(report)


if __name__ == "__main__":
    main()
