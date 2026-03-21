#!/usr/bin/env python3
"""
Social Media Post Scheduler

Generates optimal posting schedules based on platform best practices,
content pillar allocation, and audience timezone.

Usage:
    python post_scheduler.py --platform linkedin --posts-per-week 5
    python post_scheduler.py --platform linkedin --posts-per-week 5 --timezone "US/Eastern" --json
    python post_scheduler.py --config schedule_config.json
"""

import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

PLATFORM_OPTIMAL = {
    "linkedin": {
        "best_days": ["tuesday", "wednesday", "thursday"],
        "good_days": ["monday", "friday"],
        "avoid_days": ["saturday", "sunday"],
        "best_times": ["07:00", "08:00", "09:00"],
        "good_times": ["10:00", "11:00", "12:00"],
        "max_per_day": 1,
        "min_per_week": 3,
        "max_per_week": 5,
        "best_formats": ["carousel", "text", "poll", "document", "video"],
    },
    "twitter": {
        "best_days": ["monday", "tuesday", "wednesday", "thursday", "friday"],
        "good_days": [],
        "avoid_days": ["saturday", "sunday"],
        "best_times": ["08:00", "09:00", "10:00", "12:00", "13:00"],
        "good_times": ["14:00", "15:00", "17:00"],
        "max_per_day": 5,
        "min_per_week": 5,
        "max_per_week": 15,
        "best_formats": ["thread", "text", "image", "poll", "quote_tweet"],
    },
    "instagram": {
        "best_days": ["tuesday", "wednesday", "thursday"],
        "good_days": ["monday", "friday"],
        "avoid_days": ["sunday"],
        "best_times": ["09:00", "11:00", "14:00"],
        "good_times": ["07:00", "12:00", "17:00"],
        "max_per_day": 2,
        "min_per_week": 4,
        "max_per_week": 7,
        "best_formats": ["reel", "carousel", "story", "image"],
    },
    "tiktok": {
        "best_days": ["tuesday", "wednesday", "thursday", "friday"],
        "good_days": ["monday", "saturday"],
        "avoid_days": ["sunday"],
        "best_times": ["07:00", "10:00", "14:00", "19:00"],
        "good_times": ["08:00", "12:00", "17:00"],
        "max_per_day": 3,
        "min_per_week": 5,
        "max_per_week": 14,
        "best_formats": ["video"],
    },
}

CONTENT_PILLARS = {
    "educational": 0.30,
    "industry_insights": 0.25,
    "behind_the_scenes": 0.20,
    "personal_opinion": 0.15,
    "promotional": 0.10,
}

DAY_MAP = {
    0: "monday", 1: "tuesday", 2: "wednesday",
    3: "thursday", 4: "friday", 5: "saturday", 6: "sunday",
}


def generate_schedule(platform: str, posts_per_week: int, weeks: int = 2, timezone: str = "UTC", pillars: dict = None) -> dict:
    config = PLATFORM_OPTIMAL.get(platform, PLATFORM_OPTIMAL["linkedin"])
    pillars = pillars or CONTENT_PILLARS

    # Validate
    if posts_per_week < config["min_per_week"]:
        posts_per_week = config["min_per_week"]
    if posts_per_week > config["max_per_week"]:
        posts_per_week = config["max_per_week"]

    # Build available days ranked by priority
    all_days = config["best_days"] + config["good_days"]

    # Distribute posts across days
    schedule_days = []
    while len(schedule_days) < posts_per_week:
        for day in all_days:
            if len(schedule_days) >= posts_per_week:
                break
            # Check max per day
            day_count = sum(1 for d in schedule_days if d == day)
            if day_count < config["max_per_day"]:
                schedule_days.append(day)

    # Assign pillars based on allocation
    pillar_slots = []
    remaining = posts_per_week
    for pillar, pct in sorted(pillars.items(), key=lambda x: -x[1]):
        count = max(1, round(posts_per_week * pct))
        count = min(count, remaining)
        pillar_slots.extend([pillar] * count)
        remaining -= count
    # Fill any remaining
    while len(pillar_slots) < posts_per_week:
        pillar_slots.append("educational")
    pillar_slots = pillar_slots[:posts_per_week]

    # Assign times
    all_times = config["best_times"] + config["good_times"]

    # Generate weekly schedule
    weekly_schedules = []
    today = datetime.now()
    next_monday = today + timedelta(days=(7 - today.weekday()) % 7)

    for week in range(weeks):
        week_start = next_monday + timedelta(weeks=week)
        week_schedule = []

        for i, (day_name, pillar) in enumerate(zip(schedule_days, pillar_slots)):
            day_num = list(DAY_MAP.values()).index(day_name)
            post_date = week_start + timedelta(days=day_num)
            time = all_times[i % len(all_times)]
            fmt = config["best_formats"][i % len(config["best_formats"])]

            week_schedule.append({
                "date": post_date.strftime("%Y-%m-%d"),
                "day": day_name.title(),
                "time": time,
                "timezone": timezone,
                "pillar": pillar.replace("_", " ").title(),
                "suggested_format": fmt,
                "status": "planned",
            })

        weekly_schedules.append({
            "week": week + 1,
            "start_date": week_start.strftime("%Y-%m-%d"),
            "posts": sorted(week_schedule, key=lambda x: x["date"]),
        })

    result = {
        "platform": platform,
        "posts_per_week": posts_per_week,
        "timezone": timezone,
        "schedule": weekly_schedules,
        "pillar_allocation": {p.replace("_", " ").title(): f"{v*100:.0f}%" for p, v in pillars.items()},
        "platform_guidelines": {
            "best_days": config["best_days"],
            "best_times": config["best_times"],
            "avoid_days": config["avoid_days"],
            "max_per_day": config["max_per_day"],
        },
        "tips": [
            "Leave 2-3 open slots per week for reactive/trending content.",
            "Batch create content in 2-3 hour sessions for consistency.",
            "Respond to all comments within 1 hour of posting for algorithm boost.",
            f"Engage on 5-10 others' posts daily for {platform} growth.",
        ],
    }

    return result


def format_human(result: dict) -> str:
    lines = ["\n" + "=" * 65, "  SOCIAL MEDIA POST SCHEDULER", "=" * 65]
    lines.append(f"\n  Platform: {result['platform'].title()} | {result['posts_per_week']} posts/week | TZ: {result['timezone']}")

    lines.append(f"\n  Content Pillar Allocation:")
    for p, v in result["pillar_allocation"].items():
        lines.append(f"    {p}: {v}")

    for week in result["schedule"]:
        lines.append(f"\n  Week {week['week']} (starting {week['start_date']}):")
        lines.append(f"    {'Date':<12} {'Day':<10} {'Time':<7} {'Pillar':<22} {'Format'}")
        lines.append(f"    {'-'*65}")
        for post in week["posts"]:
            lines.append(f"    {post['date']:<12} {post['day']:<10} {post['time']:<7} {post['pillar']:<22} {post['suggested_format']}")

    lines.append(f"\n  Tips:")
    for t in result["tips"]:
        lines.append(f"    > {t}")

    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Generate optimal social media posting schedule.")
    parser.add_argument("--platform", "-p", default="linkedin", choices=list(PLATFORM_OPTIMAL.keys()))
    parser.add_argument("--posts-per-week", "-n", type=int, default=5)
    parser.add_argument("--weeks", "-w", type=int, default=2)
    parser.add_argument("--timezone", "-tz", default="UTC")
    parser.add_argument("--config", help="JSON config file")
    parser.add_argument("--json", action="store_true", dest="json_output")
    args = parser.parse_args()

    if args.config:
        try:
            config = json.loads(Path(args.config).read_text())
            platform = config.get("platform", args.platform)
            ppw = config.get("posts_per_week", args.posts_per_week)
            weeks = config.get("weeks", args.weeks)
            tz = config.get("timezone", args.timezone)
            pillars = config.get("pillars", CONTENT_PILLARS)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        platform = args.platform
        ppw = args.posts_per_week
        weeks = args.weeks
        tz = args.timezone
        pillars = CONTENT_PILLARS

    result = generate_schedule(platform, ppw, weeks, tz, pillars)

    if args.json_output:
        print(json.dumps(result, indent=2))
    else:
        print(format_human(result))


if __name__ == "__main__":
    main()
