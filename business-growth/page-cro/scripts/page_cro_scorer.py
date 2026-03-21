#!/usr/bin/env python3
"""
Page CRO Scorer

Score a marketing page across the 7 CRO dimensions: value proposition
clarity, headline effectiveness, CTA hierarchy, visual hierarchy,
social proof, objection handling, and friction points.

Usage:
    python page_cro_scorer.py page_audit.json
    python page_cro_scorer.py page_audit.json --json
"""

import argparse
import json
import sys


DIMENSIONS = {
    "value_proposition": {
        "label": "Value Proposition Clarity",
        "weight": 20,
        "checks": [
            ("benefit_stated_explicitly", "Primary benefit is stated explicitly (not jargon)"),
            ("customer_language", "Written in customer language, not product language"),
            ("differentiator_clear", "Differentiator is clear"),
            ("specific_numbers", "Includes specific numbers, timeframes, or outcomes"),
            ("passes_5_second_test", "Passes 5-second test (what, who, why in 5 seconds)"),
        ],
    },
    "headline": {
        "label": "Headline Effectiveness",
        "weight": 15,
        "checks": [
            ("communicates_core_value", "Communicates core value"),
            ("specific_not_generic", "Specific (numbers, outcomes), not generic"),
            ("addresses_target_audience", "Addresses target audience"),
            ("matches_traffic_source", "Matches traffic source messaging"),
        ],
    },
    "cta_hierarchy": {
        "label": "CTA Hierarchy & Placement",
        "weight": 18,
        "checks": [
            ("one_clear_primary_cta", "One clear primary CTA"),
            ("cta_above_fold", "CTA visible above the fold"),
            ("cta_communicates_value", "CTA copy communicates value (not 'Submit')"),
            ("cta_repeated", "CTA repeated at decision points"),
            ("secondary_cta_distinct", "Secondary CTA is visually distinct from primary"),
        ],
    },
    "visual_hierarchy": {
        "label": "Visual Hierarchy & Scannability",
        "weight": 12,
        "checks": [
            ("headline_most_prominent", "Headline is most prominent element"),
            ("scannable_in_10_seconds", "Key points visible in 10-second scan"),
            ("adequate_whitespace", "Adequate white space between sections"),
            ("images_support_message", "Images support the message (product screenshots, not stock)"),
        ],
    },
    "social_proof": {
        "label": "Social Proof & Trust",
        "weight": 15,
        "checks": [
            ("customer_logos", "Customer logos visible"),
            ("testimonials_specific", "Testimonials are specific (include metrics)"),
            ("testimonials_attributed", "Testimonials attributed (name, title, company, photo)"),
            ("trust_badges", "Trust badges present (security, compliance, awards)"),
            ("numbers_based_proof", "Numbers-based proof ('10,000+ teams')"),
        ],
    },
    "objection_handling": {
        "label": "Objection Handling",
        "weight": 12,
        "checks": [
            ("price_value_addressed", "Price/value objection addressed"),
            ("fit_addressed", "'Will this work for me?' answered"),
            ("risk_reduction", "Risk reduction offered (trial, guarantee, no CC)"),
            ("setup_complexity_addressed", "Implementation concern addressed"),
            ("faq_present", "FAQ section addresses top objections"),
        ],
    },
    "friction_points": {
        "label": "Friction Points",
        "weight": 8,
        "checks": [
            ("form_optimized", "Form is optimized (minimal fields)"),
            ("next_step_clear", "Next step is clear from every section"),
            ("mobile_responsive", "Mobile experience is fully responsive"),
            ("load_time_acceptable", "Load time < 3 seconds"),
        ],
    },
}


def score_page(data: dict) -> dict:
    """Score page across 7 CRO dimensions."""
    page = data.get("page", {})
    page_type = page.get("type", "landing-page")
    page_url = page.get("url", "unknown")
    checks = page.get("checks", {})

    dimension_results = []
    total_score = 0
    total_max = 0

    for dim_key, dim_config in DIMENSIONS.items():
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
        total_score += dim_score
        total_max += weight

        # Severity
        dim_pct = (dim_score / weight * 100) if weight > 0 else 0
        if dim_pct >= 80:
            severity = "OK"
        elif dim_pct >= 50:
            severity = "WARNING"
        else:
            severity = "CRITICAL"

        dimension_results.append({
            "dimension": dim_key,
            "label": dim_config["label"],
            "score": round(dim_score, 1),
            "max_score": weight,
            "percentage": round(dim_pct, 1),
            "severity": severity,
            "checks_passed": passed,
            "checks_total": len(dim_checks),
            "checks": check_results,
        })

    overall_pct = (total_score / total_max * 100) if total_max > 0 else 0

    if overall_pct >= 80:
        grade = "A"
    elif overall_pct >= 65:
        grade = "B"
    elif overall_pct >= 50:
        grade = "C"
    elif overall_pct >= 35:
        grade = "D"
    else:
        grade = "F"

    # Quick wins (failed checks in high-weight dimensions)
    quick_wins = []
    for dim in dimension_results:
        if dim["severity"] in ("CRITICAL", "WARNING"):
            for check in dim["checks"]:
                if not check["passed"]:
                    quick_wins.append({
                        "dimension": dim["label"],
                        "fix": check["check"],
                        "impact_weight": dim["max_score"],
                    })

    quick_wins.sort(key=lambda x: x["impact_weight"], reverse=True)

    return {
        "page_url": page_url,
        "page_type": page_type,
        "overall_score": round(total_score, 1),
        "max_score": total_max,
        "overall_percentage": round(overall_pct, 1),
        "grade": grade,
        "dimensions": dimension_results,
        "quick_wins": quick_wins[:7],
        "recommendations": _generate_recommendations(dimension_results, overall_pct),
    }


def _generate_recommendations(dimensions: list, overall: float) -> list:
    """Generate recommendations."""
    recs = []
    critical = [d for d in dimensions if d["severity"] == "CRITICAL"]
    for d in critical:
        recs.append({
            "priority": "HIGH",
            "recommendation": f"{d['label']} scores {d['percentage']:.0f}%. Address failed checks in this dimension first.",
        })

    if overall < 50:
        recs.append({
            "priority": "HIGH",
            "recommendation": "Overall score below 50%. Focus on value proposition clarity and CTA hierarchy before testing other elements.",
        })

    return recs


def format_text(result: dict) -> str:
    """Format results as human-readable text."""
    lines = []
    lines.append("=" * 60)
    lines.append(f"PAGE CRO AUDIT: {result['grade']} ({result['overall_score']}/{result['max_score']})")
    lines.append("=" * 60)

    lines.append(f"\nPage: {result['page_url']}")
    lines.append(f"Type: {result['page_type']}")
    lines.append(f"Score: {result['overall_percentage']}%")

    lines.append(f"\n--- Dimension Scores ---")
    for dim in result["dimensions"]:
        bar = "#" * int(dim["percentage"] / 5)
        status = f"[{dim['severity']}]"
        lines.append(f"  {dim['label']:<30} {dim['score']:>5.1f}/{dim['max_score']}  ({dim['percentage']:>5.1f}%) {status}")

    lines.append(f"\n--- Detailed Checks ---")
    for dim in result["dimensions"]:
        lines.append(f"\n  {dim['label']}:")
        for check in dim["checks"]:
            status = "[PASS]" if check["passed"] else "[FAIL]"
            lines.append(f"    {status} {check['check']}")

    if result["quick_wins"]:
        lines.append(f"\n--- Quick Wins (Fix First) ---")
        for i, qw in enumerate(result["quick_wins"], 1):
            lines.append(f"  {i}. {qw['fix']} ({qw['dimension']})")

    if result["recommendations"]:
        lines.append(f"\n--- Recommendations ---")
        for r in result["recommendations"]:
            lines.append(f"[{r['priority']}] {r['recommendation']}")

    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Score a marketing page across 7 CRO dimensions."
    )
    parser.add_argument("input_file", help="JSON file with page audit data")
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

    result = score_page(data)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(format_text(result))


if __name__ == "__main__":
    main()
