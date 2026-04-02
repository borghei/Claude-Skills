#!/usr/bin/env python3
"""
Video Content Planner

Plans video content calendar from topics, audience data, and content pillars.
Distributes topics across weeks, assigns production slots, and balances
content mix by pillar and funnel stage.

Expected JSON input with: channel, audience, content_pillars, topics

Usage:
    python video_content_planner.py topics.json
    python video_content_planner.py topics.json --weeks 8 --frequency 3
    python video_content_planner.py topics.json --platforms youtube,tiktok
    python video_content_planner.py topics.json --format json
"""

import argparse
import json
import sys
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple


PLATFORM_DEFAULTS = {
    "youtube": {"optimal_length_min": 12, "max_length_min": 25, "best_days": ["Tuesday", "Thursday", "Saturday"]},
    "tiktok": {"optimal_length_min": 1, "max_length_min": 3, "best_days": ["Tuesday", "Wednesday", "Thursday", "Friday"]},
    "linkedin": {"optimal_length_min": 2, "max_length_min": 10, "best_days": ["Tuesday", "Wednesday", "Thursday"]},
    "instagram": {"optimal_length_min": 1, "max_length_min": 1.5, "best_days": ["Monday", "Wednesday", "Friday"]},
    "shorts": {"optimal_length_min": 0.75, "max_length_min": 1, "best_days": ["Monday", "Wednesday", "Friday", "Saturday"]},
}

FUNNEL_STAGES = {
    "tofu": {"label": "Top of Funnel", "target_ratio": 0.50},
    "mofu": {"label": "Middle of Funnel", "target_ratio": 0.30},
    "bofu": {"label": "Bottom of Funnel", "target_ratio": 0.20},
}

DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def load_topics(filepath: str) -> Dict[str, Any]:
    """Load topics and channel data from JSON."""
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def assign_funnel_stage(topic: Dict) -> str:
    """Assign funnel stage based on topic properties."""
    stage = topic.get("funnel_stage", "").lower()
    if stage in FUNNEL_STAGES:
        return stage

    # Infer from format/pillar
    fmt = topic.get("format", "").lower()
    pillar = topic.get("pillar", "").lower()

    if any(kw in pillar for kw in ["how", "tutorial", "guide", "education"]):
        return "tofu"
    if any(kw in pillar for kw in ["case study", "demo", "review", "comparison"]):
        return "mofu"
    if any(kw in pillar for kw in ["testimonial", "conversion", "pricing"]):
        return "bofu"
    if fmt in ("tutorial", "commentary"):
        return "tofu"
    if fmt in ("interview", "vlog"):
        return "mofu"
    return "tofu"


def prioritize_topics(topics: List[Dict]) -> List[Dict]:
    """Sort topics by priority score."""
    priority_values = {"high": 3, "medium": 2, "low": 1}
    return sorted(topics, key=lambda t: priority_values.get(t.get("priority", "medium"), 2), reverse=True)


def distribute_to_calendar(
    topics: List[Dict],
    pillars: List[Dict],
    weeks: int,
    frequency: int,
    platforms: List[str],
    start_date: datetime,
) -> List[Dict]:
    """Distribute topics across weekly calendar slots."""
    sorted_topics = prioritize_topics(list(topics))

    # Build pillar lookup
    pillar_map = {}
    for p in pillars:
        pillar_map[p["name"].lower()] = p

    # Calculate slots
    total_slots = weeks * frequency
    calendar = []
    topic_idx = 0
    used_pillars = defaultdict(int)

    for week in range(weeks):
        week_start = start_date + timedelta(weeks=week)
        week_entries = []

        # Determine which days to publish this week
        primary_platform = platforms[0] if platforms else "youtube"
        best_days = PLATFORM_DEFAULTS.get(primary_platform, {}).get("best_days", ["Tuesday", "Thursday"])

        publish_days = []
        for day_name in best_days[:frequency]:
            day_idx = DAY_NAMES.index(day_name)
            publish_date = week_start + timedelta(days=(day_idx - week_start.weekday()) % 7)
            if publish_date < week_start:
                publish_date += timedelta(weeks=1)
            publish_days.append(publish_date)

        # Fill remaining slots if frequency > best_days
        while len(publish_days) < frequency:
            for day_idx in range(7):
                candidate = week_start + timedelta(days=day_idx)
                if candidate not in publish_days:
                    publish_days.append(candidate)
                    if len(publish_days) >= frequency:
                        break

        publish_days.sort()

        for slot_idx, pub_date in enumerate(publish_days):
            if topic_idx < len(sorted_topics):
                topic = sorted_topics[topic_idx]
                topic_idx += 1
            else:
                # Generate placeholder for remaining slots
                topic = {
                    "title": f"[TBD] Week {week + 1} Slot {slot_idx + 1}",
                    "pillar": pillars[slot_idx % len(pillars)]["name"] if pillars else "General",
                    "priority": "low",
                    "placeholder": True,
                }

            pillar_name = topic.get("pillar", "General")
            pillar_info = pillar_map.get(pillar_name.lower(), {})
            funnel = assign_funnel_stage(topic)
            used_pillars[pillar_name] += 1

            # Calculate production dates
            script_due = pub_date - timedelta(days=7)
            film_date = pub_date - timedelta(days=4)
            edit_due = pub_date - timedelta(days=2)

            entry = {
                "week": week + 1,
                "publish_date": pub_date.strftime("%Y-%m-%d"),
                "publish_day": DAY_NAMES[pub_date.weekday()],
                "title": topic.get("title", "Untitled"),
                "pillar": pillar_name,
                "format": topic.get("format", pillar_info.get("format", "standard")),
                "funnel_stage": funnel,
                "priority": topic.get("priority", "medium"),
                "est_length_min": pillar_info.get("avg_length_min", 10),
                "platforms": platforms,
                "production_schedule": {
                    "script_due": script_due.strftime("%Y-%m-%d"),
                    "film_date": film_date.strftime("%Y-%m-%d"),
                    "edit_due": edit_due.strftime("%Y-%m-%d"),
                },
                "placeholder": topic.get("placeholder", False),
            }
            calendar.append(entry)

    return calendar


def analyze_calendar_balance(calendar: List[Dict], pillars: List[Dict]) -> Dict[str, Any]:
    """Analyze content mix balance in the calendar."""
    pillar_counts = defaultdict(int)
    funnel_counts = defaultdict(int)
    format_counts = defaultdict(int)
    total = len(calendar)

    for entry in calendar:
        if not entry.get("placeholder"):
            pillar_counts[entry["pillar"]] += 1
            funnel_counts[entry["funnel_stage"]] += 1
            format_counts[entry["format"]] += 1

    actual_total = sum(pillar_counts.values())

    # Compare pillar distribution to targets
    pillar_analysis = {}
    for p in pillars:
        name = p["name"]
        target = p.get("ratio", 1 / len(pillars))
        actual = pillar_counts.get(name, 0) / actual_total if actual_total > 0 else 0
        deviation = abs(actual - target)
        pillar_analysis[name] = {
            "target_pct": round(target * 100, 1),
            "actual_pct": round(actual * 100, 1),
            "count": pillar_counts.get(name, 0),
            "balanced": deviation < 0.10,
        }

    # Funnel analysis
    funnel_analysis = {}
    for stage, info in FUNNEL_STAGES.items():
        actual = funnel_counts.get(stage, 0) / actual_total if actual_total > 0 else 0
        funnel_analysis[stage] = {
            "label": info["label"],
            "target_pct": round(info["target_ratio"] * 100, 1),
            "actual_pct": round(actual * 100, 1),
            "count": funnel_counts.get(stage, 0),
        }

    issues = []
    for name, data in pillar_analysis.items():
        if not data["balanced"]:
            if data["actual_pct"] < data["target_pct"] - 10:
                issues.append(f"Under-represented pillar: {name} ({data['actual_pct']}% vs {data['target_pct']}% target)")
            elif data["actual_pct"] > data["target_pct"] + 10:
                issues.append(f"Over-represented pillar: {name} ({data['actual_pct']}% vs {data['target_pct']}% target)")

    return {
        "total_videos": total,
        "planned_videos": actual_total,
        "placeholder_videos": total - actual_total,
        "pillar_balance": pillar_analysis,
        "funnel_balance": funnel_analysis,
        "format_mix": dict(format_counts),
        "issues": issues,
    }


def print_human(calendar: List[Dict], analysis: Dict, channel: str) -> None:
    """Print calendar in human-readable format."""
    print("=" * 76)
    print(f"  Video Content Calendar - {channel}")
    print("=" * 76)
    print(f"\n  Total Videos: {analysis['total_videos']} ({analysis['planned_videos']} planned, "
          f"{analysis['placeholder_videos']} TBD)")

    current_week = 0
    for entry in calendar:
        if entry["week"] != current_week:
            current_week = entry["week"]
            print(f"\n  --- Week {current_week} ---")

        placeholder = " [TBD]" if entry.get("placeholder") else ""
        print(f"  {entry['publish_date']} ({entry['publish_day']:<9}): {entry['title']}{placeholder}")
        print(f"    Pillar: {entry['pillar']} | Format: {entry['format']} | "
              f"Funnel: {entry['funnel_stage']} | ~{entry['est_length_min']} min")
        sched = entry["production_schedule"]
        print(f"    Script: {sched['script_due']} | Film: {sched['film_date']} | Edit: {sched['edit_due']}")

    # Balance analysis
    print(f"\n  {'=' * 72}")
    print(f"  CONTENT MIX ANALYSIS")
    print(f"  {'=' * 72}")

    print(f"\n  Pillar Distribution:")
    for name, data in analysis["pillar_balance"].items():
        status = "OK" if data["balanced"] else "!!"
        bar = "#" * max(1, int(data["actual_pct"] / 3))
        print(f"    [{status}] {name:<25} {data['actual_pct']:>5.1f}% (target: {data['target_pct']:.1f}%)  {bar}")

    print(f"\n  Funnel Distribution:")
    for stage, data in analysis["funnel_balance"].items():
        bar = "#" * max(1, int(data["actual_pct"] / 3))
        print(f"    {data['label']:<20} {data['actual_pct']:>5.1f}% (target: {data['target_pct']:.1f}%)  {bar}")

    if analysis["issues"]:
        print(f"\n  Issues:")
        for issue in analysis["issues"]:
            print(f"    [!] {issue}")

    print()


def main():
    parser = argparse.ArgumentParser(
        description="Plan video content calendar from topics and audience data"
    )
    parser.add_argument("file", help="JSON file with topics and channel data")
    parser.add_argument("--format", choices=["human", "json"], default="human", help="Output format")
    parser.add_argument("--weeks", type=int, default=4, help="Number of weeks to plan (default: 4)")
    parser.add_argument("--frequency", type=int, default=2,
                        help="Videos per week (default: 2)")
    parser.add_argument("--platforms", default="youtube",
                        help="Comma-separated target platforms (default: youtube)")
    parser.add_argument("--start-date", help="Start date YYYY-MM-DD (default: next Monday)")
    args = parser.parse_args()

    data = load_topics(args.file)

    channel = data.get("channel", "My Channel")
    pillars = data.get("content_pillars", [])
    topics = data.get("topics", [])
    platforms = [p.strip() for p in args.platforms.split(",")]

    if args.start_date:
        start = datetime.strptime(args.start_date, "%Y-%m-%d")
    else:
        today = datetime.now()
        days_until_monday = (7 - today.weekday()) % 7
        if days_until_monday == 0:
            days_until_monday = 7
        start = today + timedelta(days=days_until_monday)

    calendar = distribute_to_calendar(topics, pillars, args.weeks, args.frequency, platforms, start)
    analysis = analyze_calendar_balance(calendar, pillars)

    if args.format == "json":
        print(json.dumps({"channel": channel, "calendar": calendar, "analysis": analysis}, indent=2))
    else:
        print_human(calendar, analysis, channel)


if __name__ == "__main__":
    main()
