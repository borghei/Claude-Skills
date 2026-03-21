#!/usr/bin/env python3
"""
Social Media Audit Scorer

Scores social media profiles and content strategy against
best practices. Generates actionable audit report.

Usage:
    python social_audit_scorer.py audit_data.json
    python social_audit_scorer.py audit_data.json --json
    python social_audit_scorer.py --sample

Input JSON:
{
    "platform": "linkedin",
    "profile": {
        "has_professional_photo": true,
        "has_banner": true,
        "has_bio_cta": true,
        "has_link": true,
        "has_pinned_post": false
    },
    "content": {
        "posts_last_30_days": 12,
        "avg_engagement_rate": 2.5,
        "content_types": {"text": 6, "carousel": 3, "video": 2, "poll": 1},
        "pillar_mix": {"educational": 40, "promotional": 30, "behind_scenes": 15, "engagement": 10, "social_proof": 5}
    },
    "engagement": {
        "avg_response_time_hours": 4,
        "outbound_comments_per_week": 15,
        "dm_response_rate": 80
    }
}
"""

import argparse
import json
import sys
from pathlib import Path

PLATFORM_STANDARDS = {
    "linkedin": {
        "min_posts_month": 12,
        "good_posts_month": 16,
        "excellent_posts_month": 20,
        "engagement_avg": 2.0,
        "engagement_good": 3.5,
        "promo_cap": 15,
    },
    "twitter": {
        "min_posts_month": 20,
        "good_posts_month": 40,
        "excellent_posts_month": 60,
        "engagement_avg": 0.7,
        "engagement_good": 1.5,
        "promo_cap": 15,
    },
    "instagram": {
        "min_posts_month": 12,
        "good_posts_month": 20,
        "excellent_posts_month": 28,
        "engagement_avg": 1.5,
        "engagement_good": 3.0,
        "promo_cap": 15,
    },
}

SAMPLE = {
    "platform": "linkedin",
    "profile": {
        "has_professional_photo": True,
        "has_banner": True,
        "has_bio_cta": False,
        "has_link": True,
        "has_pinned_post": False,
        "bio_includes_value_prop": True,
    },
    "content": {
        "posts_last_30_days": 12,
        "avg_engagement_rate": 2.5,
        "content_types": {"text": 6, "carousel": 3, "video": 2, "poll": 1},
        "pillar_mix": {"educational": 40, "promotional": 30, "behind_scenes": 15, "engagement": 10, "social_proof": 5},
    },
    "engagement": {
        "avg_response_time_hours": 4,
        "outbound_comments_per_week": 15,
        "dm_response_rate": 80,
    },
}


def audit(data: dict) -> dict:
    platform = data.get("platform", "linkedin")
    standards = PLATFORM_STANDARDS.get(platform, PLATFORM_STANDARDS["linkedin"])
    profile = data.get("profile", {})
    content = data.get("content", {})
    engagement = data.get("engagement", {})

    scores = {}
    issues = []
    recommendations = []

    # --- Profile audit ---
    profile_score = 0
    profile_max = 0
    profile_checks = [
        ("has_professional_photo", 20, "Professional photo missing -- first impression matters."),
        ("has_banner", 15, "Banner image missing -- wasted branding opportunity."),
        ("has_bio_cta", 15, "Bio has no CTA -- tell visitors what to do next."),
        ("has_link", 10, "No link in profile -- missed traffic opportunity."),
        ("has_pinned_post", 10, "No pinned post -- pin your best performing content."),
        ("bio_includes_value_prop", 15, "Bio doesn't include a clear value proposition."),
    ]
    for key, points, issue_text in profile_checks:
        profile_max += points
        if profile.get(key, False):
            profile_score += points
        else:
            issues.append(issue_text)

    scores["profile"] = round(profile_score / profile_max * 100) if profile_max > 0 else 0

    # --- Content audit ---
    posts = content.get("posts_last_30_days", 0)
    eng_rate = content.get("avg_engagement_rate", 0)
    pillar_mix = content.get("pillar_mix", {})
    content_types = content.get("content_types", {})

    content_score = 50

    if posts >= standards["excellent_posts_month"]:
        content_score += 25
    elif posts >= standards["good_posts_month"]:
        content_score += 15
    elif posts >= standards["min_posts_month"]:
        content_score += 5
    else:
        content_score -= 15
        issues.append(f"Only {posts} posts in 30 days. Minimum {standards['min_posts_month']} recommended for {platform}.")
        recommendations.append(f"Increase posting frequency to {standards['good_posts_month']}/month.")

    if eng_rate >= standards["engagement_good"]:
        content_score += 25
    elif eng_rate >= standards["engagement_avg"]:
        content_score += 10
    else:
        content_score -= 10
        issues.append(f"Engagement rate {eng_rate}% is below {platform} average ({standards['engagement_avg']}%).")
        recommendations.append("Strengthen hooks and add conversation-starting CTAs to posts.")

    # Promotional cap
    promo_pct = pillar_mix.get("promotional", 0)
    if promo_pct > standards["promo_cap"]:
        content_score -= 10
        issues.append(f"Promotional content at {promo_pct}% exceeds {standards['promo_cap']}% cap.")
        recommendations.append("Reduce promotional content. Aim for 90/10 value/promo split.")

    # Format diversity
    if len(content_types) < 3:
        content_score -= 5
        recommendations.append("Mix more formats (text, carousel, video, poll) to avoid algorithm fatigue.")

    scores["content"] = max(0, min(100, content_score))

    # --- Engagement audit ---
    eng_score = 50
    response_time = engagement.get("avg_response_time_hours", 24)
    outbound = engagement.get("outbound_comments_per_week", 0)
    dm_rate = engagement.get("dm_response_rate", 0)

    if response_time <= 1:
        eng_score += 25
    elif response_time <= 2:
        eng_score += 15
    elif response_time <= 4:
        eng_score += 5
    else:
        eng_score -= 10
        issues.append(f"Average response time is {response_time} hours. Target under 2 hours.")

    if outbound >= 20:
        eng_score += 20
    elif outbound >= 10:
        eng_score += 10
    else:
        eng_score -= 10
        issues.append(f"Only {outbound} outbound comments/week. Social media is bilateral.")
        recommendations.append("Comment on 5-10 relevant posts daily. Engage more than you post.")

    if dm_rate >= 90:
        eng_score += 5
    elif dm_rate < 50:
        eng_score -= 5
        recommendations.append("Improve DM response rate for relationship building.")

    scores["engagement"] = max(0, min(100, eng_score))

    # --- Overall ---
    overall = round(scores["profile"] * 0.25 + scores["content"] * 0.45 + scores["engagement"] * 0.30)

    return {
        "platform": platform,
        "overall_score": overall,
        "grade": "A" if overall >= 85 else "B" if overall >= 70 else "C" if overall >= 55 else "D" if overall >= 40 else "F",
        "section_scores": scores,
        "issues": issues,
        "recommendations": recommendations,
        "stats": {
            "posts_30d": posts,
            "engagement_rate": eng_rate,
            "response_time_hrs": response_time,
            "outbound_comments_week": outbound,
        },
    }


def format_human(result: dict) -> str:
    lines = ["\n" + "=" * 55, "  SOCIAL MEDIA AUDIT SCORER", "=" * 55]
    lines.append(f"\n  Platform: {result['platform'].title()}")
    lines.append(f"  Overall Score: {result['overall_score']}/100 ({result['grade']})")

    lines.append(f"\n  Section Scores:")
    for section, score in result["section_scores"].items():
        bar = "#" * (score // 5) + "-" * (20 - score // 5)
        lines.append(f"    {section.title():<12} [{bar}] {score}/100")

    s = result["stats"]
    lines.append(f"\n  Stats: {s['posts_30d']} posts/30d | {s['engagement_rate']}% engagement | {s['response_time_hrs']}h response")

    if result["issues"]:
        lines.append(f"\n  Issues ({len(result['issues'])}):")
        for i in result["issues"]:
            lines.append(f"    ! {i}")

    if result["recommendations"]:
        lines.append(f"\n  Recommendations:")
        for i, r in enumerate(result["recommendations"], 1):
            lines.append(f"    {i}. {r}")

    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Audit and score social media presence.")
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

    result = audit(data)
    if args.json_output:
        print(json.dumps(result, indent=2))
    else:
        print(format_human(result))


if __name__ == "__main__":
    main()
