#!/usr/bin/env python3
"""
Assumption Tracker CLI Tool

Tracks, scores, and prioritizes product assumptions using an Impact x Risk
matrix. Classifies assumptions into quadrants: Test Now, Proceed, Investigate,
or Defer.

Usage:
    python3 assumption_tracker.py input.json [--format json|text]
    python3 assumption_tracker.py --demo [--format json|text]

Input JSON format:
    {
        "assumptions": [
            {
                "description": "Users will prefer AI summaries over manual notes",
                "category": "value",
                "confidence": "low",
                "impact": 9
            }
        ]
    }

Categories: value, usability, viability, feasibility, ethics, gtm, strategy, team
Confidence: high, medium, low
Impact: 1-10

Requires: Python 3.7+ (standard library only)
"""

import argparse
import json
import sys
from typing import Any

VALID_CATEGORIES = {
    "value", "usability", "viability", "feasibility",
    "ethics", "gtm", "strategy", "team",
}

VALID_CONFIDENCE = {"high", "medium", "low"}

CONFIDENCE_NUMERIC = {
    "high": 0.8,
    "medium": 0.5,
    "low": 0.2,
}

CATEGORY_LABELS = {
    "value": "Value",
    "usability": "Usability",
    "viability": "Viability",
    "feasibility": "Feasibility",
    "ethics": "Ethics",
    "gtm": "Go-to-Market",
    "strategy": "Strategy & Objectives",
    "team": "Team",
}

SUGGESTED_TESTS = {
    "value": "Customer interviews, fake door test, landing page test, pre-order experiment",
    "usability": "Usability test (5 users), prototype walkthrough, first-click test",
    "viability": "Financial modeling, pricing experiment, unit economics analysis",
    "feasibility": "Technical spike, proof of concept, architecture review",
    "ethics": "Ethics review board, user consent study, regulatory consultation",
    "gtm": "Channel experiment, SEO keyword test, paid ad test",
    "strategy": "Strategy review with leadership, competitive analysis",
    "team": "Skills assessment, hiring timeline analysis, training feasibility study",
}


def calculate_risk_score(impact: int, confidence: str) -> float:
    """Calculate risk score = impact * (1 - confidence_numeric)."""
    conf_value = CONFIDENCE_NUMERIC.get(confidence.lower(), 0.5)
    return round(impact * (1.0 - conf_value), 2)


def classify_quadrant(impact: int, confidence: str) -> str:
    """Classify assumption into a prioritization quadrant."""
    high_impact = impact >= 7
    low_confidence = confidence.lower() in ("low", "medium")

    if high_impact and low_confidence:
        return "Test Now"
    elif high_impact and not low_confidence:
        return "Proceed"
    elif not high_impact and confidence.lower() == "low":
        return "Investigate"
    else:
        return "Defer"


def validate_assumption(assumption: dict[str, Any], index: int) -> list[str]:
    """Validate a single assumption entry. Returns list of error messages."""
    errors = []
    if not assumption.get("description"):
        errors.append(f"Assumption {index}: missing 'description'")

    category = assumption.get("category", "").lower()
    if category not in VALID_CATEGORIES:
        errors.append(
            f"Assumption {index}: invalid category '{category}'. "
            f"Valid: {', '.join(sorted(VALID_CATEGORIES))}"
        )

    confidence = assumption.get("confidence", "").lower()
    if confidence not in VALID_CONFIDENCE:
        errors.append(
            f"Assumption {index}: invalid confidence '{confidence}'. "
            f"Valid: {', '.join(sorted(VALID_CONFIDENCE))}"
        )

    impact = assumption.get("impact")
    if not isinstance(impact, (int, float)) or impact < 1 or impact > 10:
        errors.append(f"Assumption {index}: 'impact' must be a number 1-10")

    return errors


def process_assumptions(assumptions: list[dict[str, Any]]) -> dict[str, Any]:
    """Process all assumptions and return analysis results."""
    processed = []
    for assumption in assumptions:
        category = assumption["category"].lower()
        confidence = assumption["confidence"].lower()
        impact = int(assumption["impact"])
        risk_score = calculate_risk_score(impact, confidence)
        quadrant = classify_quadrant(impact, confidence)

        processed.append({
            "description": assumption["description"],
            "category": category,
            "category_label": CATEGORY_LABELS.get(category, category),
            "confidence": confidence,
            "impact": impact,
            "risk_score": risk_score,
            "quadrant": quadrant,
            "suggested_test": SUGGESTED_TESTS.get(category, "Further investigation needed"),
        })

    # Sort by risk score descending
    processed.sort(key=lambda x: -x["risk_score"])

    # Summary
    quadrant_counts = {"Test Now": 0, "Proceed": 0, "Investigate": 0, "Defer": 0}
    category_counts: dict[str, int] = {}
    for item in processed:
        quadrant_counts[item["quadrant"]] += 1
        cat = item["category_label"]
        category_counts[cat] = category_counts.get(cat, 0) + 1

    return {
        "total": len(processed),
        "summary": {
            "by_quadrant": quadrant_counts,
            "by_category": category_counts,
        },
        "assumptions": processed,
    }


def format_text(results: dict[str, Any]) -> str:
    """Format results as human-readable text."""
    lines = []
    lines.append("=" * 70)
    lines.append("ASSUMPTION TRACKER - PRIORITIZED ANALYSIS")
    lines.append("=" * 70)

    # Summary
    lines.append("")
    lines.append(f"Total assumptions: {results['total']}")
    lines.append("")
    lines.append("By Quadrant:")
    for quadrant, count in results["summary"]["by_quadrant"].items():
        marker = " <<<" if quadrant == "Test Now" and count > 0 else ""
        lines.append(f"  {quadrant:15s} {count}{marker}")

    lines.append("")
    lines.append("By Category:")
    for category, count in sorted(results["summary"]["by_category"].items()):
        lines.append(f"  {category:25s} {count}")

    # Detailed list sorted by risk score
    lines.append("")
    lines.append("-" * 70)
    lines.append("ASSUMPTIONS (sorted by risk score, highest first)")
    lines.append("-" * 70)

    for i, a in enumerate(results["assumptions"], 1):
        lines.append("")
        lines.append(f"  #{i}  [{a['quadrant'].upper()}]")
        lines.append(f"  Description:    {a['description']}")
        lines.append(f"  Category:       {a['category_label']}")
        lines.append(f"  Confidence:     {a['confidence'].capitalize()}")
        lines.append(f"  Impact:         {a['impact']}/10")
        lines.append(f"  Risk Score:     {a['risk_score']}")
        lines.append(f"  Suggested Test: {a['suggested_test']}")

    # Action plan for Test Now
    test_now = [a for a in results["assumptions"] if a["quadrant"] == "Test Now"]
    if test_now:
        lines.append("")
        lines.append("=" * 70)
        lines.append("ACTION PLAN: TEST NOW (highest priority)")
        lines.append("=" * 70)
        for i, a in enumerate(test_now, 1):
            lines.append(f"")
            lines.append(f"  {i}. {a['description']}")
            lines.append(f"     Category:  {a['category_label']} | Risk Score: {a['risk_score']}")
            lines.append(f"     Test with: {a['suggested_test']}")

    lines.append("")
    lines.append("=" * 70)

    return "\n".join(lines)


def get_demo_data() -> dict[str, Any]:
    """Return sample input data for demonstration."""
    return {
        "assumptions": [
            {
                "description": "Users will prefer AI-generated summaries over manual note-taking",
                "category": "value",
                "confidence": "low",
                "impact": 9,
            },
            {
                "description": "Our infrastructure can handle real-time processing for 10K concurrent users",
                "category": "feasibility",
                "confidence": "medium",
                "impact": 8,
            },
            {
                "description": "Users will understand the drag-and-drop interface without a tutorial",
                "category": "usability",
                "confidence": "high",
                "impact": 7,
            },
            {
                "description": "The feature will generate enough upgrades to justify the 3-month engineering cost",
                "category": "viability",
                "confidence": "low",
                "impact": 8,
            },
            {
                "description": "Collecting usage data will not create GDPR compliance issues",
                "category": "ethics",
                "confidence": "medium",
                "impact": 9,
            },
            {
                "description": "Our target segment actively searches for solutions on Google",
                "category": "gtm",
                "confidence": "low",
                "impact": 6,
            },
            {
                "description": "This feature aligns with the company's Q3 objectives",
                "category": "strategy",
                "confidence": "high",
                "impact": 5,
            },
            {
                "description": "The team can learn the required ML skills within the project timeline",
                "category": "team",
                "confidence": "low",
                "impact": 7,
            },
        ]
    }


def main():
    parser = argparse.ArgumentParser(
        description="Assumption Tracker: score and prioritize product assumptions.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 assumption_tracker.py --demo
  python3 assumption_tracker.py --demo --format json
  python3 assumption_tracker.py assumptions.json
  python3 assumption_tracker.py assumptions.json --format json

Categories: value, usability, viability, feasibility, ethics, gtm, strategy, team
Confidence: high, medium, low
Impact: 1-10
        """,
    )
    parser.add_argument(
        "input_file",
        nargs="?",
        help="Path to JSON file with assumptions (omit if using --demo)",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run with built-in sample data",
    )
    parser.add_argument(
        "--format",
        choices=["json", "text"],
        default="text",
        help="Output format (default: text)",
    )

    args = parser.parse_args()

    if args.demo:
        data = get_demo_data()
    elif args.input_file:
        try:
            with open(args.input_file, "r") as f:
                data = json.load(f)
        except FileNotFoundError:
            print(f"Error: File not found: {args.input_file}", file=sys.stderr)
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in {args.input_file}: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)

    assumptions = data.get("assumptions", [])
    if not assumptions:
        print("Error: No assumptions found in input data.", file=sys.stderr)
        sys.exit(1)

    # Validate
    all_errors = []
    for i, assumption in enumerate(assumptions, 1):
        errors = validate_assumption(assumption, i)
        all_errors.extend(errors)

    if all_errors:
        print("Validation errors:", file=sys.stderr)
        for error in all_errors:
            print(f"  - {error}", file=sys.stderr)
        sys.exit(1)

    results = process_assumptions(assumptions)

    if args.format == "json":
        print(json.dumps(results, indent=2))
    else:
        print(format_text(results))


if __name__ == "__main__":
    main()
