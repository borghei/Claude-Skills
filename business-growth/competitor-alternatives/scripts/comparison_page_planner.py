#!/usr/bin/env python3
"""
Comparison Page Planner

Generate a prioritized comparison page plan from competitor data with
keyword targets, page format recommendations, and URL slugs.

Usage:
    python comparison_page_planner.py competitors.json
    python comparison_page_planner.py competitors.json --json
    python comparison_page_planner.py competitors.json --brand "acme"
"""

import argparse
import json
import re
import sys


PAGE_FORMATS = [
    {"format": "singular_alternative", "url_pattern": "/alternatives/{competitor}",
     "keyword_pattern": "{competitor} alternative", "intent": "switch"},
    {"format": "plural_alternatives", "url_pattern": "/alternatives/{competitor}-alternatives",
     "keyword_pattern": "{competitor} alternatives", "intent": "research"},
    {"format": "vs_page", "url_pattern": "/vs/{competitor}",
     "keyword_pattern": "{brand} vs {competitor}", "intent": "compare"},
]


def slugify(text: str) -> str:
    """Convert text to URL-safe slug."""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text


def plan_pages(data: dict, brand: str) -> dict:
    """Generate comparison page plan."""
    competitors = data.get("competitors", [])
    if not competitors:
        return {"error": "No competitor data provided."}

    brand_slug = slugify(brand)
    pages = []

    for comp in competitors:
        name = comp.get("name", "Unknown")
        slug = slugify(name)
        search_volume = comp.get("estimated_search_volume", {})
        deal_frequency = comp.get("deal_frequency", 0)
        threat_level = comp.get("threat_level", "medium").lower()

        # Score for prioritization
        priority_score = 0
        priority_score += deal_frequency * 3
        if threat_level == "critical":
            priority_score += 20
        elif threat_level == "high":
            priority_score += 15
        elif threat_level == "medium":
            priority_score += 8

        comp_pages = []
        for fmt in PAGE_FORMATS:
            url = fmt["url_pattern"].replace("{competitor}", slug).replace("{brand}", brand_slug)
            keyword = fmt["keyword_pattern"].replace("{competitor}", name).replace("{brand}", brand)
            sv = search_volume.get(fmt["format"], 0)
            priority_score += sv / 100

            comp_pages.append({
                "format": fmt["format"],
                "url": url,
                "primary_keyword": keyword,
                "estimated_search_volume": sv,
                "intent": fmt["intent"],
            })

        pages.append({
            "competitor": name,
            "priority_score": round(priority_score, 1),
            "threat_level": threat_level,
            "deal_frequency": deal_frequency,
            "pages": comp_pages,
        })

    pages.sort(key=lambda x: x["priority_score"], reverse=True)

    # Build execution plan
    total_pages = sum(len(p["pages"]) for p in pages)
    execution_plan = []
    phase = 1
    for i, comp in enumerate(pages):
        if i < 3:
            phase_label = f"Phase 1 (Weeks 1-4): Top priority"
        elif i < 6:
            phase_label = f"Phase 2 (Weeks 5-8): Medium priority"
        else:
            phase_label = f"Phase 3 (Weeks 9+): Lower priority"

        for page in comp["pages"]:
            execution_plan.append({
                "phase": phase_label,
                "competitor": comp["competitor"],
                "format": page["format"],
                "url": page["url"],
                "keyword": page["primary_keyword"],
                "search_volume": page["estimated_search_volume"],
            })

    return {
        "brand": brand,
        "total_competitors": len(competitors),
        "total_pages_planned": total_pages,
        "prioritized_competitors": pages,
        "execution_plan": execution_plan,
        "recommendations": _generate_recommendations(pages),
    }


def _generate_recommendations(pages: list) -> list:
    """Generate recommendations for page creation."""
    recs = []
    if pages:
        top = pages[0]
        recs.append({
            "priority": "HIGH",
            "recommendation": f"Start with {top['competitor']} -- highest priority based on deal frequency and threat level.",
        })

    high_sv = []
    for p in pages:
        for page in p["pages"]:
            if page["estimated_search_volume"] > 1000:
                high_sv.append(f"{p['competitor']} ({page['format']})")
    if high_sv:
        recs.append({
            "priority": "HIGH",
            "recommendation": f"High search volume opportunities: {', '.join(high_sv[:3])}",
        })

    recs.append({
        "priority": "MEDIUM",
        "recommendation": "Create a hub page at /alternatives/ or /compare/ linking to all comparison content for internal linking.",
    })
    recs.append({
        "priority": "MEDIUM",
        "recommendation": "Include 'Last updated: [Month Year]' on every page and refresh quarterly.",
    })

    return recs


def format_text(result: dict) -> str:
    """Format results as human-readable text."""
    lines = []
    lines.append("=" * 70)
    lines.append(f"COMPARISON PAGE PLAN -- {result['brand']}")
    lines.append("=" * 70)

    lines.append(f"\nTotal Competitors: {result['total_competitors']}")
    lines.append(f"Total Pages Planned: {result['total_pages_planned']}")

    lines.append(f"\n--- Prioritized Competitors ---")
    for i, comp in enumerate(result["prioritized_competitors"]):
        lines.append(f"\n  {i+1}. {comp['competitor']} (score: {comp['priority_score']}, threat: {comp['threat_level']})")
        for page in comp["pages"]:
            sv = f"SV: {page['estimated_search_volume']}" if page["estimated_search_volume"] else "SV: unknown"
            lines.append(f"     {page['format']:<25} {page['url']:<40} {sv}")

    lines.append(f"\n--- Execution Plan ---")
    current_phase = ""
    for item in result["execution_plan"]:
        if item["phase"] != current_phase:
            current_phase = item["phase"]
            lines.append(f"\n  {current_phase}")
        lines.append(f"    {item['competitor']:<20} {item['format']:<25} {item['url']}")

    lines.append(f"\n--- Recommendations ---")
    for r in result["recommendations"]:
        lines.append(f"[{r['priority']}] {r['recommendation']}")

    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Generate a prioritized comparison page plan from competitor data."
    )
    parser.add_argument("input_file", help="JSON file with competitor names and search volume estimates")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    parser.add_argument("--brand", default="your-product", help="Your brand name for URL slugs")

    args = parser.parse_args()

    try:
        with open(args.input_file, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found: {args.input_file}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {args.input_file}: {e}", file=sys.stderr)
        sys.exit(1)

    result = plan_pages(data, args.brand)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(format_text(result))


if __name__ == "__main__":
    main()
