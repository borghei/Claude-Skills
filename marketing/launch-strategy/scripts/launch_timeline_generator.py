#!/usr/bin/env python3
"""Launch Timeline Generator - Generate phased launch timelines with milestones.

Creates a week-by-week launch plan based on tier, launch date, and channel strategy.

Usage:
    python launch_timeline_generator.py --date 2026-04-15 --tier 1
    python launch_timeline_generator.py config.json --json
"""

import argparse
import json
import sys
from datetime import datetime, timedelta


TIER_1_TIMELINE = [
    {"week_offset": -8, "phase": "Foundation", "tasks": [
        {"task": "Define positioning and messaging", "owner": "PMM", "priority": "critical"},
        {"task": "Identify primary audience segment", "owner": "PMM", "priority": "critical"},
        {"task": "Draft competitive positioning", "owner": "PMM", "priority": "high"},
        {"task": "Begin asset creation brief", "owner": "Marketing", "priority": "high"},
    ]},
    {"week_offset": -6, "phase": "Asset Creation", "tasks": [
        {"task": "Write landing page copy", "owner": "Copywriter", "priority": "critical"},
        {"task": "Create product screenshots/demo video", "owner": "Design", "priority": "critical"},
        {"task": "Draft blog announcement post", "owner": "Content", "priority": "high"},
        {"task": "Draft email announcement", "owner": "Email", "priority": "high"},
        {"task": "Create social media content calendar", "owner": "Social", "priority": "medium"},
    ]},
    {"week_offset": -4, "phase": "Channel Preparation", "tasks": [
        {"task": "Build and test landing page", "owner": "Web", "priority": "critical"},
        {"task": "Set up tracking and UTMs", "owner": "Analytics", "priority": "critical"},
        {"task": "Prepare Product Hunt listing", "owner": "Marketing", "priority": "medium"},
        {"task": "Draft press release / media pitch", "owner": "PR", "priority": "medium"},
        {"task": "Begin audience warming on social", "owner": "Social", "priority": "medium"},
        {"task": "Set up waitlist if applicable", "owner": "Web", "priority": "medium"},
    ]},
    {"week_offset": -2, "phase": "Final Preparation", "tasks": [
        {"task": "Review all assets (final approval)", "owner": "Marketing Lead", "priority": "critical"},
        {"task": "Load email sequences and test", "owner": "Email", "priority": "critical"},
        {"task": "Schedule social posts", "owner": "Social", "priority": "high"},
        {"task": "Brief team on launch plan", "owner": "Marketing Lead", "priority": "critical"},
        {"task": "Brief support team", "owner": "Support Lead", "priority": "high"},
        {"task": "Configure paid ad campaigns", "owner": "Paid", "priority": "high"},
        {"task": "Document rollback plan", "owner": "Engineering", "priority": "medium"},
    ]},
    {"week_offset": -1, "phase": "Pre-Launch Week", "tasks": [
        {"task": "Final landing page QA", "owner": "QA", "priority": "critical"},
        {"task": "Test all tracking fires correctly", "owner": "Analytics", "priority": "critical"},
        {"task": "Confirm partner co-promotions", "owner": "Partnerships", "priority": "medium"},
        {"task": "Send pre-launch teaser to VIP list", "owner": "Email", "priority": "medium"},
        {"task": "Prepare launch day war room", "owner": "Marketing Lead", "priority": "high"},
    ]},
    {"week_offset": 0, "phase": "LAUNCH WEEK", "tasks": [
        {"task": "Launch Day: Flip page live, send emails, publish posts", "owner": "All", "priority": "critical"},
        {"task": "Monitor analytics every 2 hours", "owner": "Analytics", "priority": "critical"},
        {"task": "Respond to all comments/questions", "owner": "Social + Support", "priority": "critical"},
        {"task": "Product Hunt engagement (if applicable)", "owner": "Founders", "priority": "high"},
        {"task": "Send Day 2 follow-up content", "owner": "Content", "priority": "high"},
        {"task": "Share early results with team", "owner": "Marketing Lead", "priority": "medium"},
    ]},
    {"week_offset": 1, "phase": "Post-Launch Week 1", "tasks": [
        {"task": "Publish 'what we learned' content", "owner": "Content", "priority": "high"},
        {"task": "Collect early user testimonials", "owner": "CS", "priority": "high"},
        {"task": "Create comparison pages", "owner": "Content", "priority": "medium"},
        {"task": "Fix any reported issues", "owner": "Engineering", "priority": "critical"},
        {"task": "Share public metrics if impressive", "owner": "Social", "priority": "medium"},
    ]},
    {"week_offset": 3, "phase": "Post-Launch Month", "tasks": [
        {"task": "Publish case study or user story", "owner": "Content", "priority": "high"},
        {"task": "Submit to directories (G2, Capterra)", "owner": "Marketing", "priority": "medium"},
        {"task": "Run retargeting on non-converters", "owner": "Paid", "priority": "medium"},
        {"task": "Full launch retrospective", "owner": "Marketing Lead", "priority": "high"},
        {"task": "Document playbook for next launch", "owner": "Marketing Lead", "priority": "medium"},
    ]},
]

TIER_2_TIMELINE = [
    {"week_offset": -4, "phase": "Foundation & Assets", "tasks": [
        {"task": "Define messaging for feature", "owner": "PMM", "priority": "critical"},
        {"task": "Write feature page or update", "owner": "Copywriter", "priority": "critical"},
        {"task": "Draft blog post", "owner": "Content", "priority": "high"},
        {"task": "Create email announcement", "owner": "Email", "priority": "high"},
    ]},
    {"week_offset": -2, "phase": "Preparation", "tasks": [
        {"task": "Set up tracking", "owner": "Analytics", "priority": "critical"},
        {"task": "Schedule social posts", "owner": "Social", "priority": "high"},
        {"task": "Brief team", "owner": "Marketing Lead", "priority": "high"},
        {"task": "Load email sequences", "owner": "Email", "priority": "high"},
    ]},
    {"week_offset": 0, "phase": "LAUNCH", "tasks": [
        {"task": "Publish page, send email, post social", "owner": "All", "priority": "critical"},
        {"task": "Monitor analytics", "owner": "Analytics", "priority": "high"},
        {"task": "In-app notification active", "owner": "Product", "priority": "high"},
    ]},
    {"week_offset": 1, "phase": "Follow-Up", "tasks": [
        {"task": "Collect feedback and testimonials", "owner": "CS", "priority": "medium"},
        {"task": "Share results internally", "owner": "Marketing Lead", "priority": "medium"},
    ]},
]


def generate_timeline(launch_date, tier=1, custom_tasks=None):
    """Generate a dated timeline from launch date and tier."""
    template = TIER_1_TIMELINE if tier == 1 else TIER_2_TIMELINE

    if isinstance(launch_date, str):
        launch_date = datetime.strptime(launch_date, "%Y-%m-%d")

    phases = []
    all_tasks = []

    for phase_template in template:
        offset_days = phase_template["week_offset"] * 7
        phase_start = launch_date + timedelta(days=offset_days)

        phase = {
            "phase": phase_template["phase"],
            "start_date": phase_start.strftime("%Y-%m-%d"),
            "week_offset": phase_template["week_offset"],
            "tasks": [],
        }

        for task in phase_template["tasks"]:
            task_entry = {
                "task": task["task"],
                "owner": task["owner"],
                "priority": task["priority"],
                "due_date": phase_start.strftime("%Y-%m-%d"),
                "status": "pending",
            }
            phase["tasks"].append(task_entry)
            all_tasks.append(task_entry)

        phases.append(phase)

    # Add custom tasks
    if custom_tasks:
        for ct in custom_tasks:
            offset = ct.get("week_offset", 0)
            task_date = launch_date + timedelta(days=offset * 7)
            task_entry = {
                "task": ct.get("task", "Custom task"),
                "owner": ct.get("owner", "TBD"),
                "priority": ct.get("priority", "medium"),
                "due_date": task_date.strftime("%Y-%m-%d"),
                "status": "pending",
            }
            all_tasks.append(task_entry)

    total_duration = (phases[-1]["start_date"] if phases else launch_date.strftime("%Y-%m-%d"))
    prep_start = phases[0]["start_date"] if phases else launch_date.strftime("%Y-%m-%d")

    return {
        "tier": tier,
        "launch_date": launch_date.strftime("%Y-%m-%d"),
        "preparation_start": prep_start,
        "total_tasks": len(all_tasks),
        "critical_tasks": len([t for t in all_tasks if t["priority"] == "critical"]),
        "phases": phases,
    }


def format_report(timeline):
    """Format human-readable timeline."""
    lines = []
    lines.append("=" * 70)
    lines.append(f"LAUNCH TIMELINE (Tier {timeline['tier']})")
    lines.append("=" * 70)
    lines.append(f"Launch Date:       {timeline['launch_date']}")
    lines.append(f"Prep Starts:       {timeline['preparation_start']}")
    lines.append(f"Total Tasks:       {timeline['total_tasks']}")
    lines.append(f"Critical Tasks:    {timeline['critical_tasks']}")
    lines.append("")

    for phase in timeline["phases"]:
        is_launch = "LAUNCH" in phase["phase"].upper()
        marker = ">>>" if is_launch else "---"
        lines.append(f"{marker} {phase['phase']} (Week {phase['week_offset']:+d}, {phase['start_date']}) {marker}")

        for task in phase["tasks"]:
            priority_marker = {"critical": "!!!", "high": "!!", "medium": "!", "low": ""}[task["priority"]]
            lines.append(f"    [{task['priority'][:1].upper()}] {priority_marker} {task['task']} ({task['owner']})")
        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Generate phased launch timelines")
    parser.add_argument("input", nargs="?", help="JSON config file")
    parser.add_argument("--date", help="Launch date (YYYY-MM-DD)")
    parser.add_argument("--tier", type=int, choices=[1, 2], default=1, help="Launch tier")
    parser.add_argument("--json", action="store_true", dest="json_output", help="Output JSON")
    args = parser.parse_args()

    if args.input:
        try:
            with open(args.input, "r", encoding="utf-8") as f:
                config = json.load(f)
            launch_date = config.get("launch_date", config.get("date"))
            tier = config.get("tier", args.tier)
            custom_tasks = config.get("custom_tasks", [])
        except FileNotFoundError:
            print(f"Error: File not found: {args.input}", file=sys.stderr)
            sys.exit(1)
    elif args.date:
        launch_date = args.date
        tier = args.tier
        custom_tasks = []
    else:
        parser.print_help()
        sys.exit(1)

    timeline = generate_timeline(launch_date, tier, custom_tasks)

    if args.json_output:
        print(json.dumps(timeline, indent=2))
    else:
        print(format_report(timeline))


if __name__ == "__main__":
    main()
