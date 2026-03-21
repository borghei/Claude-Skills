#!/usr/bin/env python3
"""
Content Calendar Generator

Generates a structured content calendar with pillar assignments,
format recommendations, and posting schedule.

Usage:
    python content_calendar_generator.py --platform linkedin --weeks 4
    python content_calendar_generator.py --platform linkedin --weeks 4 --json
"""

import argparse
import json
import sys
from datetime import datetime, timedelta

TEMPLATES = {
    "linkedin": {
        "posts_per_week": 4,
        "schedule": [
            {"day": "monday", "pillar": "educational", "format": "long post or carousel", "focus": "How-to or framework"},
            {"day": "tuesday", "pillar": "engagement", "format": "question or poll", "focus": "Discussion starter"},
            {"day": "wednesday", "pillar": "behind_the_scenes", "format": "story or photo", "focus": "Team or process"},
            {"day": "thursday", "pillar": "educational", "format": "thread or carousel", "focus": "Industry insight"},
        ],
        "time": "08:00",
    },
    "twitter": {
        "posts_per_week": 7,
        "schedule": [
            {"day": "monday", "pillar": "educational", "format": "thread", "focus": "Weekly framework"},
            {"day": "tuesday", "pillar": "engagement", "format": "question", "focus": "Community question"},
            {"day": "wednesday", "pillar": "industry_insights", "format": "commentary", "focus": "News reaction"},
            {"day": "thursday", "pillar": "educational", "format": "thread", "focus": "Tips and tactics"},
            {"day": "friday", "pillar": "personal", "format": "story", "focus": "Lesson or reflection"},
            {"day": "monday", "pillar": "social_proof", "format": "result share", "focus": "Case study"},
            {"day": "wednesday", "pillar": "promotional", "format": "announcement", "focus": "Product or content"},
        ],
        "time": "09:00",
    },
    "instagram": {
        "posts_per_week": 5,
        "schedule": [
            {"day": "monday", "pillar": "educational", "format": "carousel", "focus": "Tutorial or tips"},
            {"day": "tuesday", "pillar": "behind_the_scenes", "format": "reel", "focus": "Process or culture"},
            {"day": "wednesday", "pillar": "engagement", "format": "story + poll", "focus": "Community interaction"},
            {"day": "thursday", "pillar": "educational", "format": "reel", "focus": "Quick tip or hack"},
            {"day": "friday", "pillar": "social_proof", "format": "carousel", "focus": "Results or testimonial"},
        ],
        "time": "11:00",
    },
}

DAY_MAP = {"monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3, "friday": 4, "saturday": 5, "sunday": 6}


def generate_calendar(platform: str, weeks: int = 4) -> dict:
    template = TEMPLATES.get(platform, TEMPLATES["linkedin"])

    today = datetime.now()
    next_monday = today + timedelta(days=(7 - today.weekday()) % 7)

    calendar = []
    for week_num in range(weeks):
        week_start = next_monday + timedelta(weeks=week_num)
        week_posts = []

        for slot in template["schedule"]:
            day_offset = DAY_MAP.get(slot["day"], 0)
            post_date = week_start + timedelta(days=day_offset)

            week_posts.append({
                "date": post_date.strftime("%Y-%m-%d"),
                "day": slot["day"].title(),
                "time": template["time"],
                "pillar": slot["pillar"].replace("_", " ").title(),
                "format": slot["format"],
                "focus": slot["focus"],
                "topic_idea": "",
                "status": "planned",
            })

        calendar.append({
            "week": week_num + 1,
            "start_date": week_start.strftime("%Y-%m-%d"),
            "posts": sorted(week_posts, key=lambda x: x["date"]),
        })

    return {
        "platform": platform,
        "posts_per_week": template["posts_per_week"],
        "total_posts": template["posts_per_week"] * weeks,
        "weeks": weeks,
        "calendar": calendar,
        "batch_creation_plan": {
            "planning_time": "30 min (Friday before)",
            "creation_time": "2 hours (Monday morning)",
            "scheduling_time": "15 min (after creation)",
            "daily_engagement": "15 min/day",
            "weekly_review": "30 min (Friday)",
        },
        "content_idea_sources": [
            "Customer FAQ and support tickets",
            "Industry news and trend reactions",
            "Internal team discussions and debates",
            "Competitor content (improve or counter)",
            "Analytics data and interesting findings",
            "Personal experience and lessons learned",
        ],
    }


def format_human(result: dict) -> str:
    lines = ["\n" + "=" * 75, "  CONTENT CALENDAR GENERATOR", "=" * 75]
    lines.append(f"\n  Platform: {result['platform'].title()} | {result['posts_per_week']}/week | {result['total_posts']} total posts")

    for week in result["calendar"]:
        lines.append(f"\n  Week {week['week']} ({week['start_date']}):")
        lines.append(f"  {'Date':<12} {'Day':<10} {'Pillar':<18} {'Format':<20} Focus")
        lines.append(f"  {'-'*75}")
        for post in week["posts"]:
            lines.append(f"  {post['date']:<12} {post['day']:<10} {post['pillar']:<18} {post['format']:<20} {post['focus']}")

    b = result["batch_creation_plan"]
    lines.append(f"\n  Batch Creation Plan:")
    for key, val in b.items():
        lines.append(f"    {key.replace('_', ' ').title()}: {val}")

    lines.append(f"\n  Content Idea Sources:")
    for s in result["content_idea_sources"]:
        lines.append(f"    - {s}")

    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Generate social media content calendar.")
    parser.add_argument("--platform", "-p", default="linkedin", choices=list(TEMPLATES.keys()))
    parser.add_argument("--weeks", "-w", type=int, default=4)
    parser.add_argument("--json", action="store_true", dest="json_output")
    args = parser.parse_args()

    result = generate_calendar(args.platform, args.weeks)
    if args.json_output:
        print(json.dumps(result, indent=2))
    else:
        print(format_human(result))


if __name__ == "__main__":
    main()
