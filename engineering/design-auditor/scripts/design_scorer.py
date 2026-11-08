#!/usr/bin/env python3
"""
Design Scorer — 12-category weighted design audit scoring system.

Computes Design Grade (A-F), AI Slop Grade (A-F), and Accessibility Grade (A-F)
from audit findings JSON input. Supports trend tracking against baselines and
generates prioritized fix recommendations. Validation and weighting live in
score_model.py; weights and grade bands in references/scoring-model.json.

Usage:
    python design_scorer.py --input findings.json --output report.json
    python design_scorer.py --input findings.json --baseline previous.json --verbose
    python design_scorer.py --input findings.json --format text

Exit codes: 0 scored, 2 missing file, invalid JSON or invalid findings.
"""

import argparse
import importlib.util as _ilu
import json
import os
import sys
from datetime import datetime


def _sibling(name):
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), name + ".py")
    spec = _ilu.spec_from_file_location(name, path)
    mod = _ilu.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


_sm = _sibling("score_model")
PRIORITY_LABELS = _sm.PRIORITY_LABELS
validate_findings = _sm.validate_findings
compute_weighted_score = _sm.compute_weighted_score
extract_recommendations = _sm.extract_recommendations
compute_trend = _sm.compute_trend
count_by_priority = _sm.count_by_priority
load_json_file = _sm.load_json_file


def score_to_design_grade(score: float) -> str:
    """Convert a 0-100 weighted score to a Design Grade."""
    return _sm.grade_for(score, "design")


def score_to_slop_grade(score: float) -> str:
    """Convert AI slop category score (0-10) to a grade; higher means fewer slop patterns."""
    return _sm.grade_for(score, "ai_slop")


def score_to_accessibility_grade(score: float) -> str:
    """Convert accessibility category score (0-10) to grade."""
    return _sm.grade_for(score, "accessibility")


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
        sys.exit(2)

    # Load baseline if provided
    baseline_data = None
    if args.baseline:
        baseline_data = load_json_file(args.baseline)
        baseline_errors = validate_findings(baseline_data)
        if baseline_errors:
            print("Baseline validation errors:", file=sys.stderr)
            for err in baseline_errors:
                print(f"  - {err}", file=sys.stderr)
            sys.exit(2)

    # Generate report
    report = generate_report(data, baseline_data)

    # Output
    if args.format == "text":
        output = format_verbose(report) if args.verbose else format_text_report(report)
    else:
        output = json.dumps(report, indent=2)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"Report written to {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
