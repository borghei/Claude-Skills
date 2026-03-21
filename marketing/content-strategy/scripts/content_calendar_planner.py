#!/usr/bin/env python3
"""
Content Calendar Planner

Generates a structured content calendar from a topic list, distributing
content across weeks by pillar, funnel stage, content type, and priority.
Supports weekly and bi-weekly cadences.

Usage:
    python content_calendar_planner.py --topics topics.csv --cadence weekly
    python content_calendar_planner.py --topics topics.csv --weeks 8 --json
    python content_calendar_planner.py --topics topics.csv --cadence biweekly --start 2026-04-01
"""

import argparse
import csv
import json
import re
import sys
from datetime import date, timedelta
from pathlib import Path


def load_topics(filepath):
    """Load topics from CSV."""
    topics = []
    with open(filepath, 'r', encoding='utf-8') as f:
        sample = f.read(1024)
        f.seek(0)
        if ',' in sample or '\t' in sample:
            try:
                dialect = csv.Sniffer().sniff(sample, delimiters=',\t')
            except csv.Error:
                dialect = csv.excel
            reader = csv.DictReader(f, dialect=dialect)
            for row in reader:
                topic = {}
                for key in ['topic', 'Topic', 'title', 'Title', 'keyword', 'Keyword']:
                    if key in row and row[key]:
                        topic["topic"] = row[key].strip()
                        break
                if "topic" not in topic and row:
                    topic["topic"] = list(row.values())[0].strip()

                for key in ['pillar', 'Pillar', 'category', 'Category']:
                    if key in row and row[key]:
                        topic["pillar"] = row[key].strip()

                for key in ['funnel', 'Funnel', 'stage', 'Stage']:
                    if key in row and row[key]:
                        topic["funnel"] = row[key].strip().lower()

                for key in ['type', 'Type', 'format', 'Format']:
                    if key in row and row[key]:
                        topic["content_type"] = row[key].strip()

                for key in ['priority', 'Priority', 'score', 'Score']:
                    if key in row and row[key]:
                        try:
                            topic["priority"] = int(str(row[key]).strip())
                        except ValueError:
                            topic["priority"] = {"high": 3, "medium": 2, "low": 1}.get(
                                row[key].strip().lower(), 2
                            )

                for key in ['volume', 'Volume']:
                    if key in row and row[key]:
                        try:
                            topic["volume"] = int(str(row[key]).replace(',', '').strip())
                        except ValueError:
                            pass

                if topic.get("topic"):
                    topics.append(topic)
        else:
            for line in f:
                t = line.strip()
                if t:
                    topics.append({"topic": t})

    return topics


def classify_topic(topic):
    """Auto-classify topic if metadata is missing."""
    t = topic.get("topic", "").lower()

    # Funnel stage
    if "funnel" not in topic:
        if any(w in t for w in ['what is', 'guide', 'introduction', 'basics', 'overview', 'how to']):
            topic["funnel"] = "awareness"
        elif any(w in t for w in ['vs', 'compare', 'best', 'review', 'alternative', 'case study']):
            topic["funnel"] = "consideration"
        elif any(w in t for w in ['pricing', 'demo', 'tutorial', 'setup', 'getting started']):
            topic["funnel"] = "decision"
        else:
            topic["funnel"] = "awareness"

    # Content type
    if "content_type" not in topic:
        if 'how to' in t or 'guide' in t or 'tutorial' in t:
            topic["content_type"] = "guide"
        elif 'vs' in t or 'compare' in t or 'best' in t:
            topic["content_type"] = "comparison"
        elif 'what is' in t:
            topic["content_type"] = "explainer"
        elif 'case study' in t or 'example' in t:
            topic["content_type"] = "case_study"
        else:
            topic["content_type"] = "article"

    # Priority
    if "priority" not in topic:
        topic["priority"] = 2

    return topic


def plan_calendar(topics, cadence="weekly", weeks=8, start_date=None):
    """Plan content calendar distributing topics across weeks."""
    if start_date is None:
        start_date = date.today()
    elif isinstance(start_date, str):
        start_date = date.fromisoformat(start_date)

    # Sort by priority (highest first)
    topics.sort(key=lambda t: t.get("priority", 2), reverse=True)

    # Determine posts per week
    posts_per_week = 2 if cadence == "weekly" else 1

    calendar = []
    topic_index = 0

    for week in range(weeks):
        week_start = start_date + timedelta(weeks=week)
        week_end = week_start + timedelta(days=6)

        week_plan = {
            "week": week + 1,
            "start_date": week_start.isoformat(),
            "end_date": week_end.isoformat(),
            "content": [],
        }

        for slot in range(posts_per_week):
            if topic_index < len(topics):
                topic = topics[topic_index]
                day_offset = 0 if slot == 0 else 3  # Mon and Thu
                publish_date = week_start + timedelta(days=day_offset)

                week_plan["content"].append({
                    "topic": topic["topic"],
                    "publish_date": publish_date.isoformat(),
                    "brief_due": (publish_date - timedelta(days=14)).isoformat(),
                    "draft_due": (publish_date - timedelta(days=9)).isoformat(),
                    "review_due": (publish_date - timedelta(days=5)).isoformat(),
                    "pillar": topic.get("pillar", "Unassigned"),
                    "funnel": topic.get("funnel", "awareness"),
                    "content_type": topic.get("content_type", "article"),
                    "priority": topic.get("priority", 2),
                    "volume": topic.get("volume"),
                })
                topic_index += 1

        # Add refresh slot every 4th week
        if (week + 1) % 4 == 0:
            week_plan["content"].append({
                "topic": "[REFRESH: Update highest-performing existing post]",
                "publish_date": (week_start + timedelta(days=4)).isoformat(),
                "content_type": "refresh",
                "pillar": "Cross-pillar",
                "funnel": "mixed",
                "priority": 3,
            })

        calendar.append(week_plan)

    return {
        "cadence": cadence,
        "total_weeks": weeks,
        "total_pieces": topic_index,
        "remaining_topics": len(topics) - topic_index,
        "calendar": calendar,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Plan a content calendar from topic list"
    )
    parser.add_argument("--topics", required=True, help="CSV file with topics")
    parser.add_argument("--cadence", choices=["weekly", "biweekly"], default="weekly")
    parser.add_argument("--weeks", type=int, default=8, help="Number of weeks to plan (default: 8)")
    parser.add_argument("--start", help="Start date (YYYY-MM-DD, default: today)")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    fp = Path(args.topics)
    if not fp.exists():
        print(f"Error: {fp} not found", file=sys.stderr)
        sys.exit(1)

    topics = load_topics(fp)
    if not topics:
        print("No topics found.", file=sys.stderr)
        sys.exit(1)

    topics = [classify_topic(t) for t in topics]
    calendar = plan_calendar(topics, args.cadence, args.weeks, args.start)

    if args.json:
        print(json.dumps(calendar, indent=2))
    else:
        print(f"\n{'='*70}")
        print(f"  CONTENT CALENDAR — {calendar['total_weeks']} weeks, {calendar['total_pieces']} pieces")
        print(f"{'='*70}")
        print(f"  Cadence: {args.cadence} | Remaining topics: {calendar['remaining_topics']}")

        for week in calendar["calendar"]:
            print(f"\n  Week {week['week']} ({week['start_date']} to {week['end_date']}):")
            for item in week["content"]:
                funnel = item.get("funnel", "")[:5].upper()
                ctype = item.get("content_type", "")[:10]
                print(f"    [{funnel}] {item['publish_date']} | {ctype:<10} | {item['topic'][:50]}")

        # Summary by funnel
        funnel_counts = {"awareness": 0, "consideration": 0, "decision": 0, "mixed": 0}
        for week in calendar["calendar"]:
            for item in week["content"]:
                f = item.get("funnel", "awareness")
                funnel_counts[f] = funnel_counts.get(f, 0) + 1

        print(f"\n  Funnel Distribution:")
        for f, c in funnel_counts.items():
            if c > 0:
                print(f"    {f.capitalize()}: {c} pieces")

        print()


if __name__ == "__main__":
    main()
