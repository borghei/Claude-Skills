#!/usr/bin/env python3
"""
Social Media Growth Tracker

Tracks follower growth, engagement trends, and content performance
over time. Generates growth reports with projections.

Usage:
    python growth_tracker.py data.json
    python growth_tracker.py data.json --json
    python growth_tracker.py --sample

Input JSON:
{
    "platform": "linkedin",
    "weekly_data": [
        {"week": "2026-03-01", "followers": 4800, "posts": 4, "impressions": 25000, "engagements": 850}
    ]
}
"""

import argparse
import json
import sys
from pathlib import Path

SAMPLE = {
    "platform": "linkedin",
    "weekly_data": [
        {"week": "2026-01-06", "followers": 4200, "posts": 3, "impressions": 18000, "engagements": 540},
        {"week": "2026-01-13", "followers": 4280, "posts": 4, "impressions": 22000, "engagements": 710},
        {"week": "2026-01-20", "followers": 4350, "posts": 4, "impressions": 24000, "engagements": 820},
        {"week": "2026-01-27", "followers": 4410, "posts": 3, "impressions": 19000, "engagements": 600},
        {"week": "2026-02-03", "followers": 4500, "posts": 5, "impressions": 28000, "engagements": 950},
        {"week": "2026-02-10", "followers": 4620, "posts": 5, "impressions": 31000, "engagements": 1100},
        {"week": "2026-02-17", "followers": 4750, "posts": 4, "impressions": 26000, "engagements": 870},
        {"week": "2026-02-24", "followers": 4850, "posts": 4, "impressions": 27000, "engagements": 920},
        {"week": "2026-03-03", "followers": 4980, "posts": 5, "impressions": 32000, "engagements": 1200},
        {"week": "2026-03-10", "followers": 5120, "posts": 5, "impressions": 35000, "engagements": 1350},
        {"week": "2026-03-17", "followers": 5280, "posts": 4, "impressions": 30000, "engagements": 1100},
    ],
}


def analyze_growth(data: dict) -> dict:
    platform = data.get("platform", "unknown")
    weekly = data.get("weekly_data", [])

    if len(weekly) < 2:
        return {"error": "Need at least 2 weeks of data"}

    # Calculate week-over-week metrics
    weekly_metrics = []
    for i, week in enumerate(weekly):
        entry = {
            "week": week["week"],
            "followers": week["followers"],
            "posts": week.get("posts", 0),
            "impressions": week.get("impressions", 0),
            "engagements": week.get("engagements", 0),
            "engagement_rate": round(week.get("engagements", 0) / max(week.get("impressions", 1), 1) * 100, 2),
        }

        if i > 0:
            prev = weekly[i - 1]
            follower_growth = week["followers"] - prev["followers"]
            growth_rate = round(follower_growth / max(prev["followers"], 1) * 100, 2)
            entry["follower_growth"] = follower_growth
            entry["growth_rate_pct"] = growth_rate
            entry["impressions_change"] = week.get("impressions", 0) - prev.get("impressions", 0)

        weekly_metrics.append(entry)

    # Overall stats
    first = weekly[0]
    last = weekly[-1]
    total_growth = last["followers"] - first["followers"]
    total_growth_pct = round(total_growth / max(first["followers"], 1) * 100, 2)
    weeks_count = len(weekly)
    avg_weekly_growth = round(total_growth / max(weeks_count - 1, 1))
    avg_weekly_growth_pct = round(total_growth_pct / max(weeks_count - 1, 1), 2)

    avg_engagement_rate = round(sum(w["engagement_rate"] for w in weekly_metrics) / len(weekly_metrics), 2)
    avg_impressions = round(sum(w["impressions"] for w in weekly_metrics) / len(weekly_metrics))
    avg_posts = round(sum(w["posts"] for w in weekly_metrics) / len(weekly_metrics), 1)

    # Trends
    growth_rates = [w.get("growth_rate_pct", 0) for w in weekly_metrics[1:]]
    engagement_rates = [w["engagement_rate"] for w in weekly_metrics]

    growth_trending = "up" if len(growth_rates) >= 3 and growth_rates[-1] > growth_rates[0] else "down" if len(growth_rates) >= 3 and growth_rates[-1] < growth_rates[0] else "stable"
    engagement_trending = "up" if len(engagement_rates) >= 3 and engagement_rates[-1] > engagement_rates[0] else "down" if len(engagement_rates) >= 3 and engagement_rates[-1] < engagement_rates[0] else "stable"

    # Projections
    projection_30d = last["followers"] + avg_weekly_growth * 4
    projection_90d = last["followers"] + avg_weekly_growth * 13

    # Recommendations
    recs = []
    if avg_weekly_growth_pct < 1:
        recs.append("Growth is slow. Increase posting frequency and engagement activity.")
    if avg_engagement_rate < 2:
        recs.append("Engagement rate is below average. Focus on hooks and conversation-driving CTAs.")
    if engagement_trending == "down":
        recs.append("Engagement is declining. Refresh content formats and try new angles.")
    if growth_trending == "up":
        recs.append("Growth is trending positively. Maintain consistency and double down on what works.")
    if avg_posts < 3:
        recs.append("Posting frequency is low. Aim for 4-5 posts per week minimum.")

    return {
        "platform": platform,
        "period": f"{first['week']} to {last['week']}",
        "weeks_tracked": weeks_count,
        "summary": {
            "starting_followers": first["followers"],
            "current_followers": last["followers"],
            "total_growth": total_growth,
            "total_growth_pct": total_growth_pct,
            "avg_weekly_growth": avg_weekly_growth,
            "avg_weekly_growth_pct": avg_weekly_growth_pct,
            "avg_engagement_rate": avg_engagement_rate,
            "avg_impressions_per_week": avg_impressions,
            "avg_posts_per_week": avg_posts,
        },
        "trends": {
            "follower_growth": growth_trending,
            "engagement": engagement_trending,
        },
        "projections": {
            "30_day": projection_30d,
            "90_day": projection_90d,
        },
        "weekly_metrics": weekly_metrics,
        "recommendations": recs,
    }


def format_human(result: dict) -> str:
    lines = ["\n" + "=" * 65, "  SOCIAL MEDIA GROWTH TRACKER", "=" * 65]
    s = result["summary"]
    lines.append(f"\n  Platform: {result['platform'].title()} | {result['period']}")
    lines.append(f"  Followers: {s['starting_followers']} -> {s['current_followers']} (+{s['total_growth']}, {s['total_growth_pct']}%)")
    lines.append(f"  Avg Weekly Growth: +{s['avg_weekly_growth']} ({s['avg_weekly_growth_pct']}%/week)")
    lines.append(f"  Avg Engagement: {s['avg_engagement_rate']}% | Avg Impressions: {s['avg_impressions_per_week']:,}/week")

    t = result["trends"]
    lines.append(f"\n  Trends: Growth {t['follower_growth']} | Engagement {t['engagement']}")

    p = result["projections"]
    lines.append(f"  Projections: 30d -> {p['30_day']:,} | 90d -> {p['90_day']:,} followers")

    lines.append(f"\n  Weekly Breakdown:")
    lines.append(f"  {'Week':<12} {'Followers':<10} {'Growth':<8} {'Posts':<6} {'Impr.':<10} {'Eng%'}")
    lines.append(f"  {'-'*60}")
    for w in result["weekly_metrics"]:
        g = f"+{w.get('follower_growth', '-')}" if "follower_growth" in w else "-"
        lines.append(f"  {w['week']:<12} {w['followers']:<10} {g:<8} {w['posts']:<6} {w['impressions']:<10} {w['engagement_rate']}%")

    if result["recommendations"]:
        lines.append(f"\n  Recommendations:")
        for i, r in enumerate(result["recommendations"], 1):
            lines.append(f"    {i}. {r}")

    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Track social media growth and engagement trends.")
    parser.add_argument("file", nargs="?")
    parser.add_argument("--json", action="store_true", dest="json_output")
    parser.add_argument("--sample", action="store_true")
    args = parser.parse_args()

    if args.sample:
        data = SAMPLE
    elif args.file:
        try:
            data = json.loads(Path(args.file).read_text())
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)

    result = analyze_growth(data)
    if args.json_output:
        print(json.dumps(result, indent=2))
    else:
        print(format_human(result))


if __name__ == "__main__":
    main()
