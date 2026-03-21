#!/usr/bin/env python3
"""
Launch Checklist Generator

Generate a phased launch checklist (pre-launch, launch week, post-launch)
customized to the tool type and distribution channels.

Usage:
    python launch_checklist_generator.py --tool-type calculator --channels seo,producthunt,social
    python launch_checklist_generator.py --tool-type checker --channels seo,email --json
"""

import argparse
import json
import sys


TOOL_TYPES = ["calculator", "generator", "checker", "grader", "converter", "template", "visualization"]

CHANNELS = ["seo", "producthunt", "social", "email", "reddit", "hackernews", "outreach", "newsletters"]

BASE_CHECKLIST = {
    "pre_launch": [
        {"task": "Finalize tool functionality and test all inputs/outputs", "priority": "HIGH", "days_before": 14},
        {"task": "Create SEO landing page with target keyword in H1, title tag, and meta description", "priority": "HIGH", "days_before": 10},
        {"task": "Add SoftwareApplication schema markup to landing page", "priority": "MEDIUM", "days_before": 10},
        {"task": "Add FAQ section with FAQPage schema (5-7 questions)", "priority": "MEDIUM", "days_before": 10},
        {"task": "Set up analytics tracking (form views, interactions, completions, submissions)", "priority": "HIGH", "days_before": 7},
        {"task": "Configure lead capture form (email-only, positioned after results)", "priority": "HIGH", "days_before": 7},
        {"task": "Test on mobile devices (touch targets, keyboard types, responsive layout)", "priority": "HIGH", "days_before": 5},
        {"task": "Create social media preview images (OG tags, Twitter cards)", "priority": "MEDIUM", "days_before": 5},
        {"task": "Write launch announcement copy (email, social, blog)", "priority": "MEDIUM", "days_before": 3},
    ],
    "launch_week": [
        {"task": "Publish and verify landing page is indexed", "priority": "HIGH", "day": 1},
        {"task": "Send announcement to existing email subscribers", "priority": "HIGH", "day": 1},
        {"task": "Monitor for critical bugs and fix within 24 hours", "priority": "HIGH", "day": "1-7"},
        {"task": "Respond to all user feedback and questions within 12 hours", "priority": "MEDIUM", "day": "1-7"},
    ],
    "post_launch": [
        {"task": "Review analytics: usage, completion rate, lead capture rate", "priority": "HIGH", "week": 2},
        {"task": "Fix top UX issues based on analytics and feedback", "priority": "HIGH", "week": 2},
        {"task": "Submit to relevant tool directories (Free Tools, AlternativeTo)", "priority": "MEDIUM", "week": 3},
        {"task": "Reach out to 'best [category] tools' listicle authors for inclusion", "priority": "MEDIUM", "week": 3},
        {"task": "Monitor search rankings for target keywords", "priority": "MEDIUM", "week": 4},
        {"task": "Publish blog post with use cases and tips", "priority": "MEDIUM", "week": 4},
        {"task": "Iterate on lead capture based on conversion data", "priority": "MEDIUM", "week": 6},
        {"task": "Track backlinks with GSC or Ahrefs", "priority": "LOW", "week": 8},
    ],
}

CHANNEL_TASKS = {
    "producthunt": {
        "pre_launch": [
            {"task": "Prepare Product Hunt listing (tagline, description, images, first comment)", "priority": "HIGH", "days_before": 3},
            {"task": "Line up 5+ early supporters for launch day upvotes", "priority": "MEDIUM", "days_before": 3},
        ],
        "launch_week": [
            {"task": "Submit to Product Hunt (aim for Tuesday-Thursday)", "priority": "HIGH", "day": 1},
            {"task": "Engage with every Product Hunt comment within 2 hours", "priority": "HIGH", "day": 1},
        ],
    },
    "social": {
        "launch_week": [
            {"task": "Post launch thread on Twitter/X with tool demo GIF", "priority": "HIGH", "day": 1},
            {"task": "Post professional use case on LinkedIn", "priority": "MEDIUM", "day": 1},
            {"task": "Share user success stories and results on social", "priority": "LOW", "day": 7},
        ],
    },
    "reddit": {
        "launch_week": [
            {"task": "Share in relevant subreddits (genuinely helpful, not promotional)", "priority": "MEDIUM", "day": 2},
        ],
    },
    "hackernews": {
        "launch_week": [
            {"task": "Submit 'Show HN' post (only if technically interesting)", "priority": "MEDIUM", "day": 2},
        ],
    },
    "outreach": {
        "post_launch": [
            {"task": "Email bloggers and resource page owners who link to similar tools", "priority": "MEDIUM", "week": 2},
            {"task": "Pitch to industry newsletter editors for featured mention", "priority": "MEDIUM", "week": 3},
        ],
    },
    "newsletters": {
        "post_launch": [
            {"task": "Submit to relevant newsletter directories for mention", "priority": "LOW", "week": 4},
        ],
    },
    "email": {
        "launch_week": [
            {"task": "Send dedicated launch email to subscriber list", "priority": "HIGH", "day": 1},
        ],
        "post_launch": [
            {"task": "Add tool mention to email signature and newsletter footer", "priority": "LOW", "week": 2},
        ],
    },
}

TOOL_TYPE_TASKS = {
    "checker": {
        "pre_launch": [
            {"task": "Ensure detailed report output is gated behind email capture", "priority": "HIGH", "days_before": 7},
            {"task": "Add scoring rubric explanation to landing page", "priority": "MEDIUM", "days_before": 5},
        ],
    },
    "calculator": {
        "pre_launch": [
            {"task": "Add shareable results URL or social share button", "priority": "MEDIUM", "days_before": 5},
        ],
    },
    "generator": {
        "pre_launch": [
            {"task": "Add copy-to-clipboard and download buttons for generated content", "priority": "HIGH", "days_before": 5},
            {"task": "Add social share with pre-filled text for generated results", "priority": "MEDIUM", "days_before": 5},
        ],
    },
    "grader": {
        "pre_launch": [
            {"task": "Create visual scorecard output (suitable for social sharing)", "priority": "MEDIUM", "days_before": 5},
        ],
    },
    "visualization": {
        "pre_launch": [
            {"task": "Add embed code for users to embed visualization on their sites", "priority": "HIGH", "days_before": 5},
            {"task": "Ensure visualization renders correctly at common embed sizes", "priority": "MEDIUM", "days_before": 3},
        ],
    },
    "template": {
        "pre_launch": [
            {"task": "Gate downloads behind email capture (preview visible without email)", "priority": "HIGH", "days_before": 7},
        ],
    },
}


def generate_checklist(tool_type: str, channels: list) -> dict:
    """Generate customized launch checklist."""
    checklist = {
        "pre_launch": list(BASE_CHECKLIST["pre_launch"]),
        "launch_week": list(BASE_CHECKLIST["launch_week"]),
        "post_launch": list(BASE_CHECKLIST["post_launch"]),
    }

    # Add tool-type-specific tasks
    type_tasks = TOOL_TYPE_TASKS.get(tool_type, {})
    for phase, tasks in type_tasks.items():
        checklist[phase].extend(tasks)

    # Add channel-specific tasks
    for channel in channels:
        ch_tasks = CHANNEL_TASKS.get(channel, {})
        for phase, tasks in ch_tasks.items():
            checklist[phase].extend(tasks)

    # Count tasks
    total = sum(len(tasks) for tasks in checklist.values())
    high_priority = sum(1 for phase in checklist.values() for t in phase if t["priority"] == "HIGH")

    return {
        "tool_type": tool_type,
        "channels": channels,
        "summary": {
            "total_tasks": total,
            "pre_launch_tasks": len(checklist["pre_launch"]),
            "launch_week_tasks": len(checklist["launch_week"]),
            "post_launch_tasks": len(checklist["post_launch"]),
            "high_priority_tasks": high_priority,
        },
        "checklist": checklist,
    }


def format_text(result: dict) -> str:
    """Format results as human-readable text."""
    lines = []
    lines.append("=" * 60)
    lines.append(f"LAUNCH CHECKLIST: {result['tool_type'].upper()} TOOL")
    lines.append("=" * 60)

    lines.append(f"\nTool Type: {result['tool_type']}")
    lines.append(f"Channels: {', '.join(result['channels'])}")
    s = result["summary"]
    lines.append(f"Total Tasks: {s['total_tasks']} ({s['high_priority_tasks']} high priority)")

    for phase_name, phase_label in [("pre_launch", "PRE-LAUNCH (1-2 weeks before)"),
                                      ("launch_week", "LAUNCH WEEK"),
                                      ("post_launch", "POST-LAUNCH (weeks 2-8)")]:
        tasks = result["checklist"][phase_name]
        lines.append(f"\n--- {phase_label} ---")
        for t in tasks:
            priority_marker = "*" if t["priority"] == "HIGH" else " "
            timing = ""
            if "days_before" in t:
                timing = f" [D-{t['days_before']}]"
            elif "day" in t:
                timing = f" [Day {t['day']}]"
            elif "week" in t:
                timing = f" [Week {t['week']}]"
            lines.append(f"  {priority_marker} [ ] {t['task']}{timing}")

    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Generate a phased launch checklist for a free tool."
    )
    parser.add_argument("--tool-type", required=True, choices=TOOL_TYPES,
                        help="Type of free tool")
    parser.add_argument("--channels", default="seo,social,email",
                        help="Comma-separated launch channels (default: seo,social,email)")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")

    args = parser.parse_args()

    channels = [c.strip().lower() for c in args.channels.split(",") if c.strip()]
    invalid = [c for c in channels if c not in CHANNELS]
    if invalid:
        print(f"Warning: Unknown channels ignored: {', '.join(invalid)}", file=sys.stderr)
        channels = [c for c in channels if c in CHANNELS]

    result = generate_checklist(args.tool_type, channels)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(format_text(result))


if __name__ == "__main__":
    main()
