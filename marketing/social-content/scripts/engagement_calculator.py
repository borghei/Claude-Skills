#!/usr/bin/env python3
"""
Social Media Engagement Calculator

Calculates engagement rates, benchmarks performance against
industry standards, and identifies top-performing content patterns.

Usage:
    python engagement_calculator.py posts.json
    python engagement_calculator.py posts.json --json
    python engagement_calculator.py --sample

Input JSON:
{
    "platform": "linkedin",
    "posts": [
        {
            "id": "post_1",
            "type": "text",
            "impressions": 5000,
            "likes": 120,
            "comments": 25,
            "shares": 15,
            "saves": 8,
            "clicks": 45,
            "date": "2026-03-01"
        }
    ]
}
"""

import argparse
import json
import sys
from pathlib import Path

BENCHMARKS = {
    "linkedin": {
        "engagement_rate": {"poor": 1.0, "average": 2.0, "good": 3.5, "excellent": 5.0},
        "by_format": {
            "carousel": {"avg_engagement": 4.5},
            "text": {"avg_engagement": 2.8},
            "image": {"avg_engagement": 2.2},
            "video": {"avg_engagement": 3.0},
            "poll": {"avg_engagement": 5.0},
            "document": {"avg_engagement": 4.2},
        },
    },
    "twitter": {
        "engagement_rate": {"poor": 0.3, "average": 0.7, "good": 1.5, "excellent": 3.0},
        "by_format": {
            "thread": {"avg_engagement": 2.0},
            "text": {"avg_engagement": 0.8},
            "image": {"avg_engagement": 1.2},
            "video": {"avg_engagement": 1.5},
            "poll": {"avg_engagement": 2.5},
        },
    },
    "instagram": {
        "engagement_rate": {"poor": 0.5, "average": 1.5, "good": 3.0, "excellent": 5.0},
        "by_format": {
            "reel": {"avg_engagement": 4.0},
            "carousel": {"avg_engagement": 3.5},
            "image": {"avg_engagement": 1.8},
            "story": {"avg_engagement": 2.0},
        },
    },
    "tiktok": {
        "engagement_rate": {"poor": 1.0, "average": 3.0, "good": 6.0, "excellent": 10.0},
        "by_format": {
            "video": {"avg_engagement": 5.0},
        },
    },
}

SAMPLE = {
    "platform": "linkedin",
    "follower_count": 5000,
    "posts": [
        {"id": "1", "type": "carousel", "impressions": 8500, "likes": 280, "comments": 45, "shares": 32, "saves": 18, "clicks": 95, "date": "2026-03-01"},
        {"id": "2", "type": "text", "impressions": 3200, "likes": 85, "comments": 22, "shares": 8, "saves": 5, "clicks": 30, "date": "2026-03-03"},
        {"id": "3", "type": "text", "impressions": 4100, "likes": 110, "comments": 35, "shares": 12, "saves": 10, "clicks": 55, "date": "2026-03-05"},
        {"id": "4", "type": "image", "impressions": 2800, "likes": 65, "comments": 8, "shares": 3, "saves": 2, "clicks": 20, "date": "2026-03-07"},
        {"id": "5", "type": "poll", "impressions": 6200, "likes": 150, "comments": 88, "shares": 25, "saves": 12, "clicks": 40, "date": "2026-03-10"},
        {"id": "6", "type": "video", "impressions": 5500, "likes": 195, "comments": 42, "shares": 28, "saves": 15, "clicks": 65, "date": "2026-03-12"},
        {"id": "7", "type": "carousel", "impressions": 9200, "likes": 320, "comments": 55, "shares": 40, "saves": 25, "clicks": 110, "date": "2026-03-15"},
    ],
}


def calc_engagement(post: dict) -> dict:
    impressions = post.get("impressions", 0)
    likes = post.get("likes", 0)
    comments = post.get("comments", 0)
    shares = post.get("shares", 0)
    saves = post.get("saves", 0)
    clicks = post.get("clicks", 0)

    total_engagements = likes + comments + shares + saves + clicks
    engagement_rate = (total_engagements / impressions * 100) if impressions > 0 else 0

    # Weighted engagement (comments and shares more valuable)
    weighted = likes * 1 + comments * 3 + shares * 4 + saves * 2 + clicks * 1.5
    weighted_rate = (weighted / impressions * 100) if impressions > 0 else 0

    return {
        "id": post.get("id", ""),
        "type": post.get("type", "unknown"),
        "date": post.get("date", ""),
        "impressions": impressions,
        "total_engagements": total_engagements,
        "engagement_rate": round(engagement_rate, 2),
        "weighted_engagement_rate": round(weighted_rate, 2),
        "breakdown": {
            "likes": likes,
            "comments": comments,
            "shares": shares,
            "saves": saves,
            "clicks": clicks,
        },
    }


def analyze_posts(data: dict) -> dict:
    platform = data.get("platform", "linkedin").lower()
    follower_count = data.get("follower_count", 0)
    posts = data.get("posts", [])
    bench = BENCHMARKS.get(platform, BENCHMARKS["linkedin"])

    post_results = [calc_engagement(p) for p in posts]

    # Sort by engagement rate
    post_results.sort(key=lambda x: x["engagement_rate"], reverse=True)

    # Aggregates
    total_impressions = sum(p["impressions"] for p in post_results)
    total_engagements = sum(p["total_engagements"] for p in post_results)
    avg_engagement = (total_engagements / total_impressions * 100) if total_impressions > 0 else 0

    # By format
    format_stats = {}
    for p in post_results:
        fmt = p["type"]
        if fmt not in format_stats:
            format_stats[fmt] = {"count": 0, "total_impressions": 0, "total_engagements": 0}
        format_stats[fmt]["count"] += 1
        format_stats[fmt]["total_impressions"] += p["impressions"]
        format_stats[fmt]["total_engagements"] += p["total_engagements"]

    for fmt in format_stats:
        f = format_stats[fmt]
        f["avg_engagement_rate"] = round(f["total_engagements"] / f["total_impressions"] * 100, 2) if f["total_impressions"] > 0 else 0
        fmt_bench = bench.get("by_format", {}).get(fmt, {})
        f["benchmark"] = fmt_bench.get("avg_engagement", "N/A")

    # Classify overall performance
    eng_bench = bench["engagement_rate"]
    if avg_engagement >= eng_bench["excellent"]:
        performance = "excellent"
    elif avg_engagement >= eng_bench["good"]:
        performance = "good"
    elif avg_engagement >= eng_bench["average"]:
        performance = "average"
    else:
        performance = "below_average"

    # Top and bottom performers
    top_3 = post_results[:3] if len(post_results) >= 3 else post_results
    bottom_3 = post_results[-3:] if len(post_results) >= 3 else post_results

    # Recommendations
    recs = []
    if performance in ("below_average", "average"):
        recs.append("Try more engaging formats: carousels and polls typically outperform text posts.")
        recs.append("Strengthen hooks -- the first 2 lines determine engagement on most platforms.")

    best_format = max(format_stats.items(), key=lambda x: x[1]["avg_engagement_rate"])[0] if format_stats else "unknown"
    recs.append(f"Best performing format: {best_format}. Consider increasing its share in your content mix.")

    # Engagement quality
    total_comments = sum(p["breakdown"]["comments"] for p in post_results)
    total_likes = sum(p["breakdown"]["likes"] for p in post_results)
    if total_likes > 0:
        comment_ratio = total_comments / total_likes
        if comment_ratio < 0.1:
            recs.append("Low comment-to-like ratio. Add questions or prompts to drive conversations.")
        elif comment_ratio > 0.3:
            recs.append("Strong comment-to-like ratio. Your content is sparking conversations.")

    return {
        "platform": platform,
        "follower_count": follower_count,
        "post_count": len(post_results),
        "aggregate": {
            "total_impressions": total_impressions,
            "total_engagements": total_engagements,
            "avg_engagement_rate": round(avg_engagement, 2),
            "performance_vs_benchmark": performance,
            "benchmark_range": f"{eng_bench['average']}-{eng_bench['good']}%",
        },
        "by_format": format_stats,
        "top_performers": top_3,
        "bottom_performers": bottom_3,
        "all_posts": post_results,
        "recommendations": recs,
    }


def format_human(result: dict) -> str:
    lines = ["\n" + "=" * 65, "  SOCIAL MEDIA ENGAGEMENT CALCULATOR", "=" * 65]
    agg = result["aggregate"]
    lines.append(f"\n  Platform: {result['platform'].title()} | Posts: {result['post_count']} | Followers: {result['follower_count']}")
    lines.append(f"  Avg Engagement: {agg['avg_engagement_rate']}% ({agg['performance_vs_benchmark']})")
    lines.append(f"  Benchmark: {agg['benchmark_range']}")

    lines.append(f"\n  By Format:")
    for fmt, stats in sorted(result["by_format"].items(), key=lambda x: -x[1]["avg_engagement_rate"]):
        lines.append(f"    {fmt:<12} {stats['avg_engagement_rate']}% avg ({stats['count']} posts) | benchmark: {stats['benchmark']}%")

    lines.append(f"\n  Top Performers:")
    for p in result["top_performers"]:
        lines.append(f"    [{p['type']}] {p['engagement_rate']}% -- {p['impressions']} impressions -- {p['date']}")

    if result["recommendations"]:
        lines.append(f"\n  Recommendations:")
        for r in result["recommendations"]:
            lines.append(f"    > {r}")

    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Calculate social media engagement metrics.")
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

    result = analyze_posts(data)
    if args.json_output:
        print(json.dumps(result, indent=2))
    else:
        print(format_human(result))


if __name__ == "__main__":
    main()
