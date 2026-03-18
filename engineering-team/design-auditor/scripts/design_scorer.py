#!/usr/bin/env python3
"""
Design Scorer — 12-category weighted design audit scoring system.

Computes Design Grade (A-F), AI Slop Grade (A-F), and Accessibility Grade (A-F)
from audit findings JSON input. Supports trend tracking against baselines and
generates prioritized fix recommendations.

Usage:
    python design_scorer.py --input findings.json --output report.json
    python design_scorer.py --input findings.json --baseline previous.json --verbose
    python design_scorer.py --input findings.json --format text
"""

import argparse
import json
import sys
from datetime import datetime
from typing import Any

# 12 audit categories with weights (must sum to 95% — 5% is coherence bonus)
CATEGORIES = {
    "visual_hierarchy": {"name": "Visual Hierarchy & Composition", "weight": 0.10},
    "typography": {"name": "Typography System", "weight": 0.08},
    "color_contrast": {"name": "Color & Contrast", "weight": 0.08},
    "spacing_layout": {"name": "Spacing & Layout Grid", "weight": 0.08},
    "interaction_states": {"name": "Interaction States", "weight": 0.10},
    "navigation_ia": {"name": "Navigation & Information Architecture", "weight": 0.08},
    "responsive": {"name": "Responsive Design", "weight": 0.08},
    "accessibility": {"name": "Accessibility (WCAG)", "weight": 0.12},
    "motion_animation": {"name": "Motion & Animation", "weight": 0.05},
    "content_microcopy": {"name": "Content & Microcopy", "weight": 0.05},
    "ai_slop": {"name": "AI Slop Indicators", "weight": 0.08},
    "performance_design": {"name": "Performance as Design", "weight": 0.05},
}

COHERENCE_WEIGHT = 0.05

PRIORITY_ORDER = ["critical", "high", "medium", "low", "cosmetic"]

PRIORITY_LABELS = {
    "critical": "Critical — Breaks core UX",
    "high": "High — Degrades experience",
    "medium": "Medium — Inconsistency",
    "low": "Low — Polish",
    "cosmetic": "Cosmetic — Nice-to-have",
}


def score_to_design_grade(score: float) -> str:
    """Convert a 0-100 weighted score to a Design Grade."""
    if score >= 95:
        return "A+"
    elif score >= 90:
        return "A"
    elif score >= 85:
        return "B+"
    elif score >= 80:
        return "B"
    elif score >= 75:
        return "C+"
    elif score >= 70:
        return "C"
    elif score >= 60:
        return "D"
    else:
        return "F"


def score_to_slop_grade(score: float) -> str:
    """Convert AI slop category score (0-10) to inverted grade.

    Higher score means fewer slop patterns detected, which is better.
    """
    if score >= 9:
        return "A"
    elif score >= 7:
        return "B"
    elif score >= 5:
        return "C"
    elif score >= 3:
        return "D"
    else:
        return "F"


def score_to_accessibility_grade(score: float) -> str:
    """Convert accessibility category score (0-10) to grade."""
    if score >= 9.5:
        return "A+"
    elif score >= 8.5:
        return "A"
    elif score >= 7:
        return "B"
    elif score >= 5:
        return "C"
    elif score >= 3:
        return "D"
    else:
        return "F"


def validate_findings(data: dict) -> list[str]:
    """Validate the structure of audit findings JSON."""
    errors = []

    if "categories" not in data:
        errors.append("Missing required 'categories' key")
        return errors

    cats = data["categories"]

    for key in CATEGORIES:
        if key not in cats:
            errors.append(f"Missing category: {key}")
            continue
        cat = cats[key]
        if "score" not in cat:
            errors.append(f"Missing 'score' in category '{key}'")
        elif not isinstance(cat["score"], (int, float)):
            errors.append(f"Score in '{key}' must be a number")
        elif not (0 <= cat["score"] <= 10):
            errors.append(f"Score in '{key}' must be between 0 and 10")

    if "coherence" in data:
        coh = data["coherence"]
        if "score" not in coh:
            errors.append("Missing 'score' in coherence")
        elif not isinstance(coh["score"], (int, float)):
            errors.append("Coherence score must be a number")
        elif not (0 <= coh["score"] <= 10):
            errors.append("Coherence score must be between 0 and 10")

    return errors


def compute_weighted_score(data: dict) -> dict:
    """Compute weighted scores across all categories."""
    cats = data["categories"]
    category_results = {}
    total_weighted = 0.0

    for key, meta in CATEGORIES.items():
        cat = cats[key]
        raw_score = float(cat["score"])
        weighted = raw_score * meta["weight"] * 10  # Convert to 0-100 scale contribution
        category_results[key] = {
            "name": meta["name"],
            "weight": meta["weight"],
            "raw_score": raw_score,
            "weighted_contribution": round(weighted, 2),
            "findings": cat.get("findings", []),
        }
        total_weighted += weighted

    # Coherence bonus
    coherence_score = 5.0  # Default if not provided
    if "coherence" in data:
        coherence_score = float(data["coherence"]["score"])
    coherence_weighted = coherence_score * COHERENCE_WEIGHT * 10
    total_weighted += coherence_weighted

    return {
        "categories": category_results,
        "coherence": {
            "raw_score": coherence_score,
            "weighted_contribution": round(coherence_weighted, 2),
        },
        "total_score": round(total_weighted, 2),
    }


def extract_recommendations(data: dict) -> list[dict]:
    """Extract and prioritize all findings as recommendations."""
    recommendations = []
    cats = data.get("categories", {})

    for key, cat in cats.items():
        category_name = CATEGORIES.get(key, {}).get("name", key)
        for finding in cat.get("findings", []):
            rec = {
                "category": category_name,
                "category_key": key,
                "description": finding.get("description", ""),
                "priority": finding.get("priority", "medium"),
                "fix": finding.get("fix", ""),
                "impact_score": finding.get("impact", 5),
            }
            recommendations.append(rec)

    # Sort by priority order, then by impact score descending
    def sort_key(r):
        pri_idx = PRIORITY_ORDER.index(r["priority"]) if r["priority"] in PRIORITY_ORDER else 99
        return (pri_idx, -r["impact_score"])

    recommendations.sort(key=sort_key)
    return recommendations


def compute_trend(current: dict, baseline: dict) -> dict:
    """Compare current scores against a baseline for trend tracking."""
    trend = {}
    current_cats = current.get("categories", {})
    baseline_cats = baseline.get("categories", {})

    for key in CATEGORIES:
        current_score = current_cats.get(key, {}).get("raw_score", 0)
        baseline_score = baseline_cats.get(key, {}).get("raw_score", 0)
        delta = round(current_score - baseline_score, 2)
        direction = "improved" if delta > 0 else ("declined" if delta < 0 else "unchanged")
        trend[key] = {
            "name": CATEGORIES[key]["name"],
            "current": current_score,
            "baseline": baseline_score,
            "delta": delta,
            "direction": direction,
        }

    current_total = current.get("total_score", 0)
    baseline_total = baseline.get("total_score", 0)
    total_delta = round(current_total - baseline_total, 2)

    trend["_overall"] = {
        "current_total": current_total,
        "baseline_total": baseline_total,
        "delta": total_delta,
        "direction": "improved" if total_delta > 0 else ("declined" if total_delta < 0 else "unchanged"),
    }

    return trend


def count_by_priority(recommendations: list[dict]) -> dict:
    """Count findings by priority level."""
    counts = {p: 0 for p in PRIORITY_ORDER}
    for rec in recommendations:
        pri = rec.get("priority", "medium")
        if pri in counts:
            counts[pri] += 1
        else:
            counts[pri] = counts.get(pri, 0) + 1
    return counts


def generate_report(data: dict, baseline_data: dict | None = None) -> dict:
    """Generate a complete scored audit report."""
    scores = compute_weighted_score(data)
    recommendations = extract_recommendations(data)
    priority_counts = count_by_priority(recommendations)

    # Extract individual grades
    ai_slop_score = data["categories"].get("ai_slop", {}).get("score", 5)
    accessibility_score = data["categories"].get("accessibility", {}).get("score", 5)

    report = {
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "tool": "design_scorer.py",
            "version": "2.0.0",
        },
        "grades": {
            "design_grade": score_to_design_grade(scores["total_score"]),
            "design_score": scores["total_score"],
            "ai_slop_grade": score_to_slop_grade(ai_slop_score),
            "ai_slop_score": ai_slop_score,
            "accessibility_grade": score_to_accessibility_grade(accessibility_score),
            "accessibility_score": accessibility_score,
        },
        "category_breakdown": scores["categories"],
        "coherence": scores["coherence"],
        "recommendations": recommendations,
        "summary": {
            "total_findings": len(recommendations),
            "by_priority": priority_counts,
            "top_3_issues": recommendations[:3] if recommendations else [],
        },
    }

    # Add trend data if baseline provided
    if baseline_data is not None:
        baseline_scores = compute_weighted_score(baseline_data)
        report["trend"] = compute_trend(scores, baseline_scores)

    return report


def format_text_report(report: dict) -> str:
    """Format report as human-readable text."""
    lines = []
    lines.append("=" * 72)
    lines.append("DESIGN AUDIT REPORT")
    lines.append("=" * 72)
    lines.append(f"Generated: {report['metadata']['generated_at']}")
    lines.append("")

    # Grades
    grades = report["grades"]
    lines.append("GRADES")
    lines.append("-" * 40)
    lines.append(f"  Design Grade:        {grades['design_grade']} ({grades['design_score']}/100)")
    lines.append(f"  AI Slop Grade:       {grades['ai_slop_grade']} ({grades['ai_slop_score']}/10)")
    lines.append(f"  Accessibility Grade: {grades['accessibility_grade']} ({grades['accessibility_score']}/10)")
    lines.append("")

    # Category breakdown
    lines.append("CATEGORY BREAKDOWN")
    lines.append("-" * 72)
    lines.append(f"  {'Category':<42} {'Score':>6} {'Weight':>7} {'Contrib':>8}")
    lines.append(f"  {'-'*42} {'-'*6} {'-'*7} {'-'*8}")

    for key, cat in report["category_breakdown"].items():
        name = cat["name"]
        if len(name) > 40:
            name = name[:37] + "..."
        lines.append(
            f"  {name:<42} {cat['raw_score']:>5.1f} {cat['weight']*100:>6.0f}% {cat['weighted_contribution']:>7.2f}"
        )

    coh = report["coherence"]
    lines.append(
        f"  {'Overall Coherence Bonus':<42} {coh['raw_score']:>5.1f} {'5':>6}% {coh['weighted_contribution']:>7.2f}"
    )
    lines.append(f"  {'':<42} {'':>6} {'Total':>7} {grades['design_score']:>7.2f}")
    lines.append("")

    # Summary
    summary = report["summary"]
    lines.append("FINDINGS SUMMARY")
    lines.append("-" * 40)
    lines.append(f"  Total findings: {summary['total_findings']}")
    for pri, count in summary["by_priority"].items():
        if count > 0:
            lines.append(f"    {PRIORITY_LABELS.get(pri, pri)}: {count}")
    lines.append("")

    # Top issues
    if summary["top_3_issues"]:
        lines.append("TOP ISSUES")
        lines.append("-" * 40)
        for i, issue in enumerate(summary["top_3_issues"], 1):
            lines.append(f"  {i}. [{issue['priority'].upper()}] {issue['description']}")
            if issue.get("fix"):
                lines.append(f"     Fix: {issue['fix']}")
            lines.append(f"     Category: {issue['category']}")
            lines.append("")

    # Trend (if present)
    if "trend" in report:
        lines.append("TREND vs BASELINE")
        lines.append("-" * 72)
        trend = report["trend"]
        overall = trend.get("_overall", {})
        direction_symbol = {"improved": "+", "declined": "-", "unchanged": "="}

        for key, t in trend.items():
            if key == "_overall":
                continue
            sym = direction_symbol.get(t["direction"], "?")
            lines.append(
                f"  {t['name']:<42} {t['baseline']:.1f} -> {t['current']:.1f} ({sym}{abs(t['delta']):.1f})"
            )

        lines.append("")
        sym = direction_symbol.get(overall.get("direction", "unchanged"), "?")
        lines.append(
            f"  Overall: {overall.get('baseline_total', 0):.1f} -> "
            f"{overall.get('current_total', 0):.1f} ({sym}{abs(overall.get('delta', 0)):.1f})"
        )
        lines.append("")

    # All recommendations
    if report["recommendations"]:
        lines.append("ALL RECOMMENDATIONS (by priority)")
        lines.append("-" * 72)
        current_priority = None
        for rec in report["recommendations"]:
            if rec["priority"] != current_priority:
                current_priority = rec["priority"]
                lines.append(f"\n  [{current_priority.upper()}]")
            lines.append(f"    - {rec['description']}")
            if rec.get("fix"):
                lines.append(f"      Fix: {rec['fix']}")
    lines.append("")
    lines.append("=" * 72)
    return "\n".join(lines)


def format_verbose(report: dict) -> str:
    """Format report with extra detail for verbose output."""
    text = format_text_report(report)
    lines = [text, ""]
    lines.append("DETAILED CATEGORY FINDINGS")
    lines.append("=" * 72)

    for key, cat in report["category_breakdown"].items():
        findings = cat.get("findings", [])
        if findings:
            lines.append(f"\n{cat['name']} (Score: {cat['raw_score']}/10)")
            lines.append("-" * 50)
            for f in findings:
                pri = f.get("priority", "medium")
                lines.append(f"  [{pri.upper()}] {f.get('description', '')}")
                if f.get("fix"):
                    lines.append(f"    Suggested fix: {f['fix']}")
                if f.get("impact"):
                    lines.append(f"    Impact score: {f['impact']}/10")

    lines.append("")
    return "\n".join(lines)


def load_json_file(path: str) -> dict:
    """Load and parse a JSON file."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found: {path}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {path}: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Design Scorer — 12-category weighted design audit scoring system",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --input findings.json --output report.json
  %(prog)s --input findings.json --baseline previous.json --verbose
  %(prog)s --input findings.json --format text
        """,
    )
    parser.add_argument("--input", "-i", required=True, help="Path to audit findings JSON file")
    parser.add_argument("--output", "-o", help="Path to write report JSON (default: stdout)")
    parser.add_argument("--baseline", "-b", help="Path to baseline findings JSON for trend comparison")
    parser.add_argument(
        "--format",
        "-f",
        choices=["json", "text"],
        default="json",
        help="Output format (default: json)",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Include detailed category findings")

    args = parser.parse_args()

    # Load input
    data = load_json_file(args.input)

    # Validate
    errors = validate_findings(data)
    if errors:
        print("Validation errors:", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        sys.exit(1)

    # Load baseline if provided
    baseline_data = None
    if args.baseline:
        baseline_data = load_json_file(args.baseline)
        baseline_errors = validate_findings(baseline_data)
        if baseline_errors:
            print("Baseline validation errors:", file=sys.stderr)
            for err in baseline_errors:
                print(f"  - {err}", file=sys.stderr)
            sys.exit(1)

    # Generate report
    report = generate_report(data, baseline_data)

    # Output
    if args.format == "text":
        if args.verbose:
            output = format_verbose(report)
        else:
            output = format_text_report(report)
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(output)
            print(f"Report written to {args.output}")
        else:
            print(output)
    else:
        output_json = json.dumps(report, indent=2)
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(output_json)
            print(f"Report written to {args.output}")
        else:
            print(output_json)


if __name__ == "__main__":
    main()
