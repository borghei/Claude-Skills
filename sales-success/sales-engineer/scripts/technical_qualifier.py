#!/usr/bin/env python3
"""Score technical fit between prospect requirements and solution capabilities.

Evaluates each requirement against solution capabilities and produces a
technical qualification score with gap analysis and risk assessment.

Usage:
    python technical_qualifier.py --requirements reqs.csv --capabilities caps.json
    python technical_qualifier.py --requirements reqs.json --json
    python technical_qualifier.py --requirements reqs.csv --threshold 70
"""

import argparse
import csv
import json
import os
import sys
from datetime import datetime


COVERAGE_CATEGORIES = {
    "full": {"score": 100, "label": "Fully Met", "description": "Requirement fully supported today"},
    "partial": {"score": 60, "label": "Partially Met", "description": "Partially supported; gap exists"},
    "roadmap": {"score": 30, "label": "On Roadmap", "description": "Planned for future release"},
    "partner": {"score": 50, "label": "Via Partner", "description": "Available through partner integration"},
    "na": {"score": 100, "label": "Not Applicable", "description": "Not relevant to this evaluation"},
    "gap": {"score": 0, "label": "Not Supported", "description": "Not available and not planned"},
}

PRIORITY_WEIGHTS = {
    "must": 3.0,
    "must_have": 3.0,
    "must-have": 3.0,
    "critical": 3.0,
    "should": 2.0,
    "should_have": 2.0,
    "should-have": 2.0,
    "important": 2.0,
    "nice": 1.0,
    "nice_to_have": 1.0,
    "nice-to-have": 1.0,
    "optional": 0.5,
}

FIT_LABELS = {
    (0, 40): ("Poor Fit", "Significant gaps in critical areas. Likely disqualify unless gaps can be addressed."),
    (40, 60): ("Moderate Fit", "Notable gaps exist. Requires roadmap commitments or workarounds."),
    (60, 75): ("Good Fit", "Meets most requirements. Address partial coverage areas in demo."),
    (75, 90): ("Strong Fit", "Well-aligned. Minor gaps manageable through configuration or roadmap."),
    (90, 101): ("Excellent Fit", "Near-complete coverage. Strong technical candidate for selection."),
}


def load_data(filepath):
    """Load data from CSV or JSON file."""
    ext = os.path.splitext(filepath)[1].lower()
    if ext == ".json":
        with open(filepath, "r") as f:
            data = json.load(f)
            return data if isinstance(data, list) else [data]
    elif ext == ".csv":
        with open(filepath, "r") as f:
            return list(csv.DictReader(f))
    else:
        print(f"Error: Unsupported file format '{ext}'. Use .csv or .json.", file=sys.stderr)
        sys.exit(1)


def normalize_coverage(value):
    """Normalize coverage status to standard category."""
    if not value:
        return "gap"
    val = str(value).lower().strip().replace(" ", "_").replace("-", "_")
    for key in COVERAGE_CATEGORIES:
        if key in val:
            return key
    if val in ("yes", "true", "1", "supported", "available"):
        return "full"
    if val in ("no", "false", "0", "unsupported"):
        return "gap"
    return "gap"


def normalize_priority(value):
    """Normalize priority to standard weight."""
    if not value:
        return "should", 2.0
    val = str(value).lower().strip().replace(" ", "_").replace("-", "_")
    for key, weight in PRIORITY_WEIGHTS.items():
        if key in val:
            return key.replace("_", " ").title(), weight
    return "Should", 2.0


def score_requirements(requirements):
    """Score technical fit from requirements data."""
    scored = []
    total_weighted = 0
    total_max = 0
    category_summary = {cat: 0 for cat in COVERAGE_CATEGORIES}
    priority_gaps = {"must": [], "should": [], "nice": []}

    for req in requirements:
        req_id = req.get("id", req.get("req_id", f"R{len(scored)+1}"))
        requirement = req.get("requirement", req.get("description", req.get("name", "Unknown")))
        category_name = req.get("category", req.get("area", "General"))
        coverage_raw = req.get("coverage", req.get("status", req.get("response", "")))
        priority_raw = req.get("priority", "should")
        notes = req.get("notes", req.get("detail", ""))

        coverage = normalize_coverage(coverage_raw)
        priority_label, priority_weight = normalize_priority(priority_raw)
        coverage_data = COVERAGE_CATEGORIES[coverage]
        coverage_score = coverage_data["score"]

        weighted_score = coverage_score * priority_weight
        max_score = 100 * priority_weight
        total_weighted += weighted_score
        total_max += max_score

        category_summary[coverage] += 1

        if coverage in ("gap", "partial", "roadmap") and priority_weight >= 2.0:
            bucket = "must" if priority_weight >= 3.0 else "should"
            priority_gaps[bucket].append({
                "id": req_id,
                "requirement": requirement,
                "coverage": coverage_data["label"],
                "priority": priority_label,
            })

        scored.append({
            "id": req_id,
            "requirement": requirement,
            "category": category_name,
            "priority": priority_label,
            "priority_weight": priority_weight,
            "coverage": coverage_data["label"],
            "coverage_key": coverage,
            "score": coverage_score,
            "weighted_score": round(weighted_score, 1),
            "notes": notes,
        })

    overall_score = round((total_weighted / total_max) * 100, 1) if total_max > 0 else 0

    fit_label = "Unknown"
    fit_advice = ""
    for (lo, hi), (label, advice) in FIT_LABELS.items():
        if lo <= overall_score < hi:
            fit_label = label
            fit_advice = advice
            break

    # Must-have coverage
    must_haves = [s for s in scored if s["priority_weight"] >= 3.0]
    must_met = sum(1 for s in must_haves if s["coverage_key"] in ("full", "na"))
    must_total = len(must_haves)

    return {
        "overall_score": overall_score,
        "fit_label": fit_label,
        "fit_advice": fit_advice,
        "total_requirements": len(scored),
        "must_have_coverage": f"{must_met}/{must_total}" if must_total > 0 else "N/A",
        "must_have_rate": round(must_met / must_total * 100, 1) if must_total > 0 else 100,
        "category_summary": {
            COVERAGE_CATEGORIES[k]["label"]: v for k, v in category_summary.items() if v > 0
        },
        "critical_gaps": priority_gaps["must"],
        "important_gaps": priority_gaps["should"],
        "scored_requirements": scored,
    }


def format_human(results, threshold):
    """Format results for human-readable output."""
    lines = []
    lines.append("=" * 70)
    lines.append("TECHNICAL QUALIFICATION SCORECARD")
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"Qualification Threshold: {threshold}%")
    lines.append("=" * 70)

    lines.append(f"\n  Overall Technical Fit:    {results['overall_score']}% ({results['fit_label']})")
    lines.append(f"  Assessment:              {results['fit_advice']}")
    lines.append(f"  Total Requirements:      {results['total_requirements']}")
    lines.append(f"  Must-Have Coverage:      {results['must_have_coverage']} ({results['must_have_rate']}%)")
    status = "QUALIFIED" if results["overall_score"] >= threshold else "BELOW THRESHOLD"
    lines.append(f"  Qualification Status:    {status}")

    lines.append(f"\n  Coverage Distribution:")
    for label, count in results["category_summary"].items():
        pct = round(count / results["total_requirements"] * 100, 1) if results["total_requirements"] > 0 else 0
        lines.append(f"    {label:<20} {count:>4} ({pct}%)")

    if results["critical_gaps"]:
        lines.append(f"\n  CRITICAL GAPS (Must-Have):")
        for gap in results["critical_gaps"]:
            lines.append(f"    [{gap['id']}] {gap['requirement']}")
            lines.append(f"           Coverage: {gap['coverage']} | Priority: {gap['priority']}")

    if results["important_gaps"]:
        lines.append(f"\n  IMPORTANT GAPS (Should-Have):")
        for gap in results["important_gaps"]:
            lines.append(f"    [{gap['id']}] {gap['requirement']}")
            lines.append(f"           Coverage: {gap['coverage']} | Priority: {gap['priority']}")

    lines.append(f"\n{'DETAILED REQUIREMENTS':^70}")
    lines.append("-" * 70)
    lines.append(f"  {'ID':<6} {'Requirement':<30} {'Priority':<10} {'Coverage':<15} {'Score':>5}")
    lines.append("  " + "-" * 68)
    for req in results["scored_requirements"]:
        flag = " *" if req["coverage_key"] in ("gap", "partial") and req["priority_weight"] >= 2.0 else ""
        lines.append(
            f"  {req['id']:<6} {req['requirement'][:30]:<30} "
            f"{req['priority']:<10} {req['coverage']:<15} {req['score']:>5}{flag}"
        )

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Score technical fit between prospect requirements and solution capabilities."
    )
    parser.add_argument("--requirements", "--data", required=True, dest="data",
                        help="Path to requirements CSV or JSON file")
    parser.add_argument(
        "--threshold",
        type=float,
        default=70,
        help="Minimum qualification score (default: 70)",
    )
    parser.add_argument("--json", action="store_true", help="Output results as JSON")

    args = parser.parse_args()

    if not os.path.exists(args.data):
        print(f"Error: File not found: {args.data}", file=sys.stderr)
        sys.exit(1)

    requirements = load_data(args.data)
    if not requirements:
        print("Error: No requirements found in input file.", file=sys.stderr)
        sys.exit(1)

    results = score_requirements(requirements)

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(format_human(results, args.threshold))

    sys.exit(0 if results["overall_score"] >= args.threshold else 1)


if __name__ == "__main__":
    main()
