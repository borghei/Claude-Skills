#!/usr/bin/env python3
"""Template Usage Analyzer - Analyze template adoption and effectiveness.

Reads template usage data and produces adoption metrics, quality scores,
and recommendations for template optimization.

Usage:
    python template_usage_analyzer.py --usage usage.json
    python template_usage_analyzer.py --usage usage.json --json
    python template_usage_analyzer.py --example
"""

import argparse
import json
import sys
from datetime import datetime


def load_data(path: str) -> dict:
    with open(path, "r") as f:
        return json.load(f)


def analyze_usage(data: dict) -> dict:
    org = data.get("organization", "Unknown")
    templates = data.get("templates", [])
    total_pages = data.get("total_pages_created", 0)

    results = []
    total_from_template = 0

    for t in templates:
        name = t.get("name", "Unknown")
        uses = t.get("uses_30d", 0)
        total_from_template += uses
        created_date = t.get("created_date", "Unknown")
        last_updated = t.get("last_updated", "Unknown")
        quality_score = 0

        # Quality checks
        has_instructions = t.get("has_instructions", False)
        has_example = t.get("has_example", False)
        has_owner = t.get("has_owner", False)
        section_count = t.get("section_count", 0)
        has_dynamic_content = t.get("has_dynamic_content", False)

        if has_instructions:
            quality_score += 20
        if has_example:
            quality_score += 20
        if has_owner:
            quality_score += 15
        if section_count >= 3:
            quality_score += 15
        elif section_count >= 1:
            quality_score += 10
        if has_dynamic_content:
            quality_score += 15
        # Version freshness
        if last_updated != "Unknown":
            try:
                updated_dt = datetime.strptime(last_updated, "%Y-%m-%d")
                days_since = (datetime.now() - updated_dt).days
                if days_since <= 90:
                    quality_score += 15
                elif days_since <= 180:
                    quality_score += 10
                elif days_since <= 365:
                    quality_score += 5
            except ValueError:
                pass

        if quality_score >= 80:
            quality_rating = "Excellent"
        elif quality_score >= 60:
            quality_rating = "Good"
        elif quality_score >= 40:
            quality_rating = "Fair"
        else:
            quality_rating = "Poor"

        results.append({
            "name": name,
            "uses_30d": uses,
            "created_date": created_date,
            "last_updated": last_updated,
            "quality_score": quality_score,
            "quality_rating": quality_rating,
            "has_instructions": has_instructions,
            "has_example": has_example,
            "has_owner": has_owner,
            "section_count": section_count,
            "has_dynamic_content": has_dynamic_content,
        })

    results.sort(key=lambda x: x["uses_30d"], reverse=True)

    adoption_rate = round(total_from_template / total_pages * 100, 1) if total_pages > 0 else 0
    avg_quality = round(sum(r["quality_score"] for r in results) / len(results), 1) if results else 0

    # Recommendations
    recs = []
    unused = [r for r in results if r["uses_30d"] == 0]
    if unused:
        recs.append(f"{len(unused)} template(s) with zero usage in 30 days. Review for deprecation or promotion.")
    low_quality = [r for r in results if r["quality_rating"] == "Poor"]
    if low_quality:
        names = ", ".join(r["name"] for r in low_quality[:3])
        recs.append(f"Low quality templates: {names}. Add instructions, examples, and assign owners.")
    if adoption_rate < 50:
        recs.append(f"Template adoption is {adoption_rate:.0f}% (target: 70%+). Promote templates in team channels and pin to space sidebars.")
    no_owner = [r for r in results if not r["has_owner"]]
    if no_owner:
        recs.append(f"{len(no_owner)} template(s) without an owner. Assign owners for maintenance accountability.")

    return {
        "organization": org,
        "analysis_date": datetime.now().strftime("%Y-%m-%d"),
        "total_templates": len(results),
        "total_pages_created": total_pages,
        "pages_from_templates": total_from_template,
        "adoption_rate_pct": adoption_rate,
        "avg_quality_score": avg_quality,
        "templates": results,
        "recommendations": recs,
    }


def print_report(result: dict) -> None:
    print(f"\nTemplate Usage Analysis: {result['organization']}")
    print(f"Date: {result['analysis_date']}")
    print("=" * 65)
    print(f"Templates: {result['total_templates']}  |  Adoption: {result['adoption_rate_pct']:.0f}%  |  Avg Quality: {result['avg_quality_score']:.0f}/100")

    print(f"\nTemplate Details:")
    print(f"  {'Template':<30} {'Uses':>6} {'Quality':>8} {'Rating':<12} {'Updated'}")
    print(f"  {'-'*30} {'-'*6} {'-'*8} {'-'*12} {'-'*12}")
    for t in result["templates"]:
        name = t["name"][:28] + ".." if len(t["name"]) > 30 else t["name"]
        print(f"  {name:<30} {t['uses_30d']:>6} {t['quality_score']:>7}% {t['quality_rating']:<12} {t['last_updated']}")

    if result["recommendations"]:
        print(f"\nRecommendations:")
        for i, r in enumerate(result["recommendations"], 1):
            print(f"  {i}. {r}")
    print()


def print_example() -> None:
    example = {
        "organization": "Acme Corp",
        "total_pages_created": 150,
        "templates": [
            {"name": "Meeting Notes", "uses_30d": 45, "created_date": "2025-06-01", "last_updated": "2026-02-15", "has_instructions": True, "has_example": True, "has_owner": True, "section_count": 5, "has_dynamic_content": True},
            {"name": "Sprint Retrospective", "uses_30d": 12, "created_date": "2025-08-01", "last_updated": "2026-01-10", "has_instructions": True, "has_example": False, "has_owner": True, "section_count": 4, "has_dynamic_content": False},
            {"name": "Old Project Template", "uses_30d": 0, "created_date": "2024-03-01", "last_updated": "2024-06-01", "has_instructions": False, "has_example": False, "has_owner": False, "section_count": 2, "has_dynamic_content": False},
        ],
    }
    print(json.dumps(example, indent=2))


def main():
    parser = argparse.ArgumentParser(description="Analyze template adoption and effectiveness.")
    parser.add_argument("--usage", type=str, help="Path to usage data JSON file")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    parser.add_argument("--example", action="store_true", help="Print example data and exit")
    args = parser.parse_args()

    if args.example:
        print_example()
        return
    if not args.usage:
        parser.error("--usage is required (use --example to see the expected format)")

    data = load_data(args.usage)
    result = analyze_usage(data)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print_report(result)


if __name__ == "__main__":
    main()
