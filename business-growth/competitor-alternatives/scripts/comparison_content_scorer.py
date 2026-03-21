#!/usr/bin/env python3
"""
Comparison Content Scorer

Score existing comparison page content against quality and SEO best
practices. Evaluates honesty, depth, SEO signals, trust elements,
and conversion optimization.

Usage:
    python comparison_content_scorer.py page_content.json
    python comparison_content_scorer.py page_content.json --json
"""

import argparse
import json
import sys


SCORING_DIMENSIONS = {
    "honesty_and_balance": {
        "weight": 20,
        "checks": [
            ("acknowledges_competitor_strengths", "Acknowledges competitor strengths explicitly"),
            ("includes_who_competitor_is_best_for", "Includes 'Who [Competitor] is best for' section"),
            ("honest_about_own_limitations", "Honest about own limitations"),
            ("uses_verifiable_claims", "Claims are verifiable from public sources"),
            ("no_aggressive_language", "No aggressive or disparaging language"),
        ],
    },
    "content_depth": {
        "weight": 25,
        "checks": [
            ("has_tldr_summary", "TL;DR summary at the top"),
            ("paragraph_comparisons", "Paragraph comparisons (not just tables)"),
            ("pricing_comparison", "Detailed pricing comparison with hidden costs"),
            ("use_case_scenarios", "Real use case scenarios"),
            ("migration_section", "Migration section with steps and timeline"),
        ],
    },
    "seo_optimization": {
        "weight": 20,
        "checks": [
            ("keyword_in_h1", "Target keyword in H1"),
            ("keyword_in_title_tag", "Target keyword in title tag"),
            ("keyword_in_meta_description", "Target keyword in meta description"),
            ("faq_section", "FAQ section present"),
            ("schema_markup", "Schema markup (FAQPage or SoftwareApplication)"),
            ("last_updated_date", "Last updated date visible"),
        ],
    },
    "trust_elements": {
        "weight": 15,
        "checks": [
            ("customer_testimonials", "Customer testimonials from switchers"),
            ("specific_metrics", "Specific metrics in testimonials (not generic praise)"),
            ("attributed_quotes", "Quotes attributed with name, title, company"),
            ("data_sources_cited", "Data sources cited for claims"),
        ],
    },
    "conversion_optimization": {
        "weight": 20,
        "checks": [
            ("primary_cta_visible", "Primary CTA visible above fold"),
            ("cta_repeated", "CTA repeated after major sections"),
            ("risk_reversal", "Risk reversal (free trial, no CC, guarantee)"),
            ("clear_next_step", "Clear next step for interested readers"),
        ],
    },
}


def score_content(data: dict) -> dict:
    """Score comparison page content."""
    page = data.get("page", {})
    page_url = page.get("url", "unknown")
    competitor = page.get("competitor", "Unknown")
    checks = page.get("checks", {})

    dimension_results = []
    total_score = 0
    total_max = 0

    for dim_key, dim_config in SCORING_DIMENSIONS.items():
        weight = dim_config["weight"]
        dim_checks = dim_config["checks"]
        passed = 0
        check_results = []

        for check_key, check_label in dim_checks:
            is_present = checks.get(check_key, False)
            if is_present:
                passed += 1
            check_results.append({
                "check": check_label,
                "key": check_key,
                "passed": is_present,
            })

        dim_score = (passed / len(dim_checks) * weight) if dim_checks else 0
        dim_max = weight
        total_score += dim_score
        total_max += dim_max

        dimension_results.append({
            "dimension": dim_key,
            "score": round(dim_score, 1),
            "max_score": dim_max,
            "percentage": round((dim_score / dim_max * 100) if dim_max > 0 else 0, 1),
            "checks_passed": passed,
            "checks_total": len(dim_checks),
            "checks": check_results,
        })

    overall_pct = (total_score / total_max * 100) if total_max > 0 else 0

    # Grade
    if overall_pct >= 85:
        grade = "A"
    elif overall_pct >= 70:
        grade = "B"
    elif overall_pct >= 55:
        grade = "C"
    elif overall_pct >= 40:
        grade = "D"
    else:
        grade = "F"

    # Priority fixes
    fixes = []
    for dim in dimension_results:
        if dim["percentage"] < 60:
            for check in dim["checks"]:
                if not check["passed"]:
                    fixes.append({
                        "dimension": dim["dimension"],
                        "fix": check["check"],
                        "impact": "high" if dim["max_score"] >= 20 else "medium",
                    })

    fixes.sort(key=lambda x: 0 if x["impact"] == "high" else 1)

    return {
        "page_url": page_url,
        "competitor": competitor,
        "overall_score": round(total_score, 1),
        "max_score": total_max,
        "overall_percentage": round(overall_pct, 1),
        "grade": grade,
        "dimensions": dimension_results,
        "priority_fixes": fixes[:10],
    }


def format_text(result: dict) -> str:
    """Format results as human-readable text."""
    lines = []
    lines.append("=" * 60)
    lines.append(f"COMPARISON CONTENT SCORE: {result['competitor']}")
    lines.append("=" * 60)

    lines.append(f"\nPage: {result['page_url']}")
    lines.append(f"Overall Score: {result['overall_score']}/{result['max_score']} ({result['overall_percentage']}%)")
    lines.append(f"Grade: {result['grade']}")

    lines.append(f"\n--- Dimension Scores ---")
    for dim in result["dimensions"]:
        bar = "#" * int(dim["percentage"] / 5)
        lines.append(f"  {dim['dimension']:<25} {dim['score']:>5.1f}/{dim['max_score']}  ({dim['percentage']:>5.1f}%)  {bar}")

        for check in dim["checks"]:
            status = "[PASS]" if check["passed"] else "[FAIL]"
            lines.append(f"    {status} {check['check']}")

    if result["priority_fixes"]:
        lines.append(f"\n--- Priority Fixes ---")
        for i, fix in enumerate(result["priority_fixes"], 1):
            lines.append(f"  {i}. [{fix['impact'].upper()}] {fix['fix']} ({fix['dimension']})")

    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Score comparison page content against quality and SEO best practices."
    )
    parser.add_argument("input_file", help="JSON file with comparison page content and metadata")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")

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

    result = score_content(data)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(format_text(result))


if __name__ == "__main__":
    main()
