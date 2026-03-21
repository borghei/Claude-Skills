#!/usr/bin/env python3
"""Content Health Auditor - Audit Confluence content for quality and freshness.

Reads page metadata and produces a health report identifying stale content,
orphaned pages, missing owners, and content quality gaps.

Usage:
    python content_health_auditor.py --pages pages.json
    python content_health_auditor.py --pages pages.json --json
    python content_health_auditor.py --example
"""

import argparse
import json
import sys
from datetime import datetime


def load_data(path: str) -> dict:
    with open(path, "r") as f:
        return json.load(f)


def analyze_content(data: dict) -> dict:
    space = data.get("space", "Unknown")
    pages = data.get("pages", [])
    today = datetime.now()

    stale = []
    orphaned = []
    no_owner = []
    no_labels = []
    low_quality = []
    healthy = []

    for page in pages:
        title = page.get("title", "Untitled")
        owner = page.get("owner", "")
        last_updated = page.get("last_updated", "")
        labels = page.get("labels", [])
        has_parent = page.get("has_parent", True)
        views_30d = page.get("views_30d", 0)
        word_count = page.get("word_count", 0)
        has_links = page.get("has_links", False)

        issues = []
        score = 100

        # Freshness
        if last_updated:
            try:
                updated_dt = datetime.strptime(last_updated, "%Y-%m-%d")
                days = (today - updated_dt).days
                if days > 365:
                    issues.append("Stale (>12 months)")
                    stale.append(title)
                    score -= 30
                elif days > 180:
                    issues.append("Aging (>6 months)")
                    score -= 15
            except ValueError:
                pass
        else:
            issues.append("No update date")
            score -= 10

        # Orphaned
        if not has_parent:
            issues.append("Orphaned (no parent page)")
            orphaned.append(title)
            score -= 20

        # Owner
        if not owner:
            issues.append("No owner assigned")
            no_owner.append(title)
            score -= 15

        # Labels
        if not labels:
            issues.append("No labels")
            no_labels.append(title)
            score -= 10

        # Content quality
        if word_count < 50:
            issues.append("Very short content (<50 words)")
            score -= 15
        if not has_links and word_count > 100:
            issues.append("No links to related content")
            score -= 5

        # Low engagement
        if views_30d == 0 and word_count > 0:
            issues.append("Zero views in 30 days")
            score -= 10

        score = max(0, score)
        if score >= 80:
            rating = "Healthy"
            healthy.append(title)
        elif score >= 50:
            rating = "Needs Attention"
        else:
            rating = "Poor"
            low_quality.append(title)

        page["health_score"] = score
        page["health_rating"] = rating
        page["issues"] = issues

    # Aggregate metrics
    total = len(pages)
    avg_score = round(sum(p["health_score"] for p in pages) / total, 1) if total > 0 else 0

    if avg_score >= 75:
        overall = "Healthy"
    elif avg_score >= 50:
        overall = "Needs Improvement"
    else:
        overall = "Poor"

    recs = []
    if stale:
        recs.append(f"{len(stale)} stale page(s) (>12 months old). Review for archiving or updating.")
    if orphaned:
        recs.append(f"{len(orphaned)} orphaned page(s). Move under appropriate parent pages or archive.")
    if no_owner:
        recs.append(f"{len(no_owner)} page(s) without owners. Assign owners for maintenance accountability.")
    if no_labels:
        recs.append(f"{len(no_labels)} page(s) without labels. Add labels to improve discoverability.")

    page_results = sorted(pages, key=lambda x: x["health_score"])

    return {
        "space": space,
        "audit_date": today.strftime("%Y-%m-%d"),
        "total_pages": total,
        "overall_health": overall,
        "avg_health_score": avg_score,
        "summary": {
            "healthy": len(healthy),
            "stale": len(stale),
            "orphaned": len(orphaned),
            "no_owner": len(no_owner),
            "no_labels": len(no_labels),
            "low_quality": len(low_quality),
        },
        "pages": [
            {
                "title": p.get("title"),
                "owner": p.get("owner", "None"),
                "health_score": p["health_score"],
                "health_rating": p["health_rating"],
                "issues": p["issues"],
                "last_updated": p.get("last_updated", "Unknown"),
                "views_30d": p.get("views_30d", 0),
            }
            for p in page_results
        ],
        "recommendations": recs,
    }


def print_report(result: dict) -> None:
    print(f"\nContent Health Audit: {result['space']}")
    print(f"Date: {result['audit_date']}  |  Pages: {result['total_pages']}")
    print("=" * 65)
    print(f"Overall Health: {result['overall_health']} (avg score: {result['avg_health_score']:.0f}/100)")

    s = result["summary"]
    print(f"  Healthy: {s['healthy']}  |  Stale: {s['stale']}  |  Orphaned: {s['orphaned']}  |  No Owner: {s['no_owner']}")

    print(f"\nPage Details (sorted by score):")
    print(f"  {'Title':<30} {'Score':>6} {'Rating':<16} {'Issues'}")
    print(f"  {'-'*30} {'-'*6} {'-'*16} {'-'*30}")
    for p in result["pages"]:
        title = p["title"][:28] + ".." if len(p["title"]) > 30 else p["title"]
        issues = "; ".join(p["issues"][:2]) if p["issues"] else "None"
        print(f"  {title:<30} {p['health_score']:>5}% {p['health_rating']:<16} {issues}")

    if result["recommendations"]:
        print(f"\nRecommendations:")
        for i, r in enumerate(result["recommendations"], 1):
            print(f"  {i}. {r}")
    print()


def print_example() -> None:
    example = {
        "space": "Engineering Team",
        "pages": [
            {"title": "Onboarding Guide", "owner": "Alice", "last_updated": "2026-03-01", "labels": ["onboarding", "guide"], "has_parent": True, "views_30d": 45, "word_count": 500, "has_links": True},
            {"title": "Old Architecture Doc", "owner": "", "last_updated": "2024-06-15", "labels": [], "has_parent": True, "views_30d": 2, "word_count": 1200, "has_links": True},
            {"title": "Untitled Draft", "owner": "Bob", "last_updated": "2026-01-10", "labels": [], "has_parent": False, "views_30d": 0, "word_count": 30, "has_links": False},
            {"title": "API Reference", "owner": "Carol", "last_updated": "2026-02-20", "labels": ["api", "reference"], "has_parent": True, "views_30d": 120, "word_count": 2000, "has_links": True},
        ],
    }
    print(json.dumps(example, indent=2))


def main():
    parser = argparse.ArgumentParser(description="Audit Confluence content health.")
    parser.add_argument("--pages", type=str, help="Path to pages JSON file")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--example", action="store_true", help="Print example and exit")
    args = parser.parse_args()

    if args.example:
        print_example()
        return
    if not args.pages:
        parser.error("--pages is required")

    data = load_data(args.pages)
    result = analyze_content(data)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print_report(result)


if __name__ == "__main__":
    main()
