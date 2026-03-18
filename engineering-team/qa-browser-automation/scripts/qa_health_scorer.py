#!/usr/bin/env python3
"""QA Health Scorer — Computes a weighted health score (0-100) from QA findings.

Uses a 10-category weighted system with severity-based deductions to produce
an overall quality grade (A-F). Supports trend tracking against previous
baselines and machine-readable JSON output for CI integration.

Usage:
    python qa_health_scorer.py findings.json
    python qa_health_scorer.py findings.json --json
    python qa_health_scorer.py findings.json --baseline previous.json
    python qa_health_scorer.py findings.json --threshold 80
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

CATEGORY_WEIGHTS: dict[str, float] = {
    "console_errors": 0.12,
    "broken_links": 0.08,
    "visual_consistency": 0.10,
    "functional": 0.18,
    "ux_flow": 0.12,
    "performance": 0.12,
    "content_quality": 0.05,
    "accessibility": 0.13,
    "security_headers": 0.05,
    "mobile_responsive": 0.05,
}

SEVERITY_DEDUCTIONS: dict[str, int] = {
    "P0": 30,
    "P1": 18,
    "P2": 10,
    "P3": 4,
    "P4": 1,
}

GRADE_THRESHOLDS: list[tuple[int, str]] = [
    (90, "A"),
    (80, "B"),
    (70, "C"),
    (60, "D"),
    (0, "F"),
]

CATEGORY_DISPLAY_NAMES: dict[str, str] = {
    "console_errors": "Console Errors",
    "broken_links": "Broken Links",
    "visual_consistency": "Visual Consistency",
    "functional": "Functional",
    "ux_flow": "UX Flow",
    "performance": "Performance",
    "content_quality": "Content Quality",
    "accessibility": "Accessibility",
    "security_headers": "Security Headers",
    "mobile_responsive": "Mobile Responsive",
}


# ---------------------------------------------------------------------------
# Scoring Logic
# ---------------------------------------------------------------------------

def compute_category_scores(findings: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """Compute per-category scores from a list of findings.

    Each finding must have at minimum:
        - severity: P0-P4
        - category: one of the 10 category keys

    Returns a dict keyed by category with score, deductions, and finding counts.
    """
    category_deductions: dict[str, float] = {cat: 0.0 for cat in CATEGORY_WEIGHTS}
    category_counts: dict[str, dict[str, int]] = {
        cat: {sev: 0 for sev in SEVERITY_DEDUCTIONS} for cat in CATEGORY_WEIGHTS
    }

    for finding in findings:
        severity = finding.get("severity", "P3")
        category = finding.get("category", "functional")

        if severity not in SEVERITY_DEDUCTIONS:
            severity = "P3"
        if category not in CATEGORY_WEIGHTS:
            category = "functional"

        deduction = SEVERITY_DEDUCTIONS[severity]
        weight = CATEGORY_WEIGHTS[category]
        # Scale deduction by category weight so a P0 in a low-weight category
        # doesn't disproportionately crush the overall score.
        weighted_deduction = deduction * weight
        category_deductions[category] += weighted_deduction
        category_counts[category][severity] += 1

    results: dict[str, dict[str, Any]] = {}
    for cat, weight in CATEGORY_WEIGHTS.items():
        max_points = weight * 100
        raw_score = max(0.0, max_points - category_deductions[cat])
        pct = (raw_score / max_points * 100) if max_points > 0 else 100.0
        results[cat] = {
            "weight": weight,
            "max_points": round(max_points, 2),
            "deductions": round(category_deductions[cat], 2),
            "score_points": round(raw_score, 2),
            "score_pct": round(pct, 1),
            "finding_counts": category_counts[cat],
            "total_findings": sum(category_counts[cat].values()),
        }
    return results


def compute_overall_score(category_scores: dict[str, dict[str, Any]]) -> float:
    """Sum weighted category scores into an overall 0-100 score."""
    total = sum(cs["score_points"] for cs in category_scores.values())
    return round(max(0.0, min(100.0, total)), 1)


def score_to_grade(score: float) -> str:
    """Convert a numeric score to a letter grade."""
    for threshold, grade in GRADE_THRESHOLDS:
        if score >= threshold:
            return grade
    return "F"


def summarize_findings(findings: list[dict[str, Any]]) -> dict[str, int]:
    """Count findings by severity."""
    counts: dict[str, int] = {sev: 0 for sev in SEVERITY_DEDUCTIONS}
    for f in findings:
        sev = f.get("severity", "P3")
        if sev in counts:
            counts[sev] += 1
        else:
            counts["P3"] += 1
    return counts


# ---------------------------------------------------------------------------
# Trend Tracking
# ---------------------------------------------------------------------------

def compute_trend(current_score: float, baseline_path: str | None) -> dict[str, Any] | None:
    """Compare current score against a previous baseline if provided."""
    if baseline_path is None:
        return None

    path = Path(baseline_path)
    if not path.exists():
        return {"error": f"Baseline file not found: {baseline_path}"}

    try:
        with open(path, "r", encoding="utf-8") as f:
            baseline = json.load(f)
    except (json.JSONDecodeError, OSError) as exc:
        return {"error": f"Failed to read baseline: {exc}"}

    prev_score = baseline.get("overall_score", baseline.get("score", 0))
    delta = round(current_score - prev_score, 1)
    direction = "improved" if delta > 0 else "declined" if delta < 0 else "unchanged"

    return {
        "previous_score": prev_score,
        "current_score": current_score,
        "delta": delta,
        "direction": direction,
        "baseline_file": str(path),
    }


# ---------------------------------------------------------------------------
# Output Formatting
# ---------------------------------------------------------------------------

def format_human_readable(
    overall_score: float,
    grade: str,
    category_scores: dict[str, dict[str, Any]],
    severity_summary: dict[str, int],
    trend: dict[str, Any] | None,
    threshold: int,
) -> str:
    """Format results as a human-readable text report."""
    lines: list[str] = []
    lines.append("=" * 60)
    lines.append("  QA HEALTH SCORE REPORT")
    lines.append("=" * 60)
    lines.append("")

    # Overall score
    pass_fail = "PASS" if overall_score >= threshold else "FAIL"
    lines.append(f"  Overall Score:  {overall_score}/100  (Grade: {grade})  [{pass_fail}]")
    lines.append(f"  Threshold:      {threshold}")
    lines.append(f"  Timestamp:      {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    lines.append("")

    # Trend
    if trend and "error" not in trend:
        arrow = "^" if trend["delta"] > 0 else "v" if trend["delta"] < 0 else "="
        lines.append(f"  Trend:          {trend['direction']} ({arrow} {abs(trend['delta'])} pts from {trend['previous_score']})")
        lines.append("")

    # Severity summary
    lines.append("-" * 60)
    lines.append("  FINDINGS BY SEVERITY")
    lines.append("-" * 60)
    total_findings = sum(severity_summary.values())
    lines.append(f"  Total findings: {total_findings}")
    for sev in ["P0", "P1", "P2", "P3", "P4"]:
        count = severity_summary.get(sev, 0)
        deduction = SEVERITY_DEDUCTIONS[sev]
        marker = " !!!" if sev == "P0" and count > 0 else ""
        lines.append(f"    {sev} ({'-' + str(deduction)} pts each):  {count}{marker}")
    lines.append("")

    # Category breakdown
    lines.append("-" * 60)
    lines.append("  CATEGORY BREAKDOWN")
    lines.append("-" * 60)
    header = f"  {'Category':<22} {'Weight':>6} {'Score':>7} {'Findings':>8}"
    lines.append(header)
    lines.append("  " + "-" * 46)

    for cat, data in category_scores.items():
        name = CATEGORY_DISPLAY_NAMES.get(cat, cat)
        weight_str = f"{int(data['weight'] * 100)}%"
        score_str = f"{data['score_pct']:.0f}%"
        findings_str = str(data["total_findings"])
        lines.append(f"  {name:<22} {weight_str:>6} {score_str:>7} {findings_str:>8}")

    lines.append("")
    lines.append("=" * 60)

    # Recommendations
    critical_categories = [
        (cat, data) for cat, data in category_scores.items()
        if data["score_pct"] < 70
    ]
    if critical_categories:
        lines.append("  PRIORITY AREAS")
        lines.append("-" * 60)
        for cat, data in sorted(critical_categories, key=lambda x: x[1]["score_pct"]):
            name = CATEGORY_DISPLAY_NAMES.get(cat, cat)
            lines.append(f"  - {name}: {data['score_pct']:.0f}% ({data['total_findings']} findings)")
        lines.append("")

    return "\n".join(lines)


def format_json_output(
    overall_score: float,
    grade: str,
    category_scores: dict[str, dict[str, Any]],
    severity_summary: dict[str, int],
    trend: dict[str, Any] | None,
    threshold: int,
) -> str:
    """Format results as JSON for machine consumption."""
    result: dict[str, Any] = {
        "overall_score": overall_score,
        "grade": grade,
        "passed": overall_score >= threshold,
        "threshold": threshold,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "severity_summary": severity_summary,
        "total_findings": sum(severity_summary.values()),
        "categories": {},
    }

    for cat, data in category_scores.items():
        result["categories"][cat] = {
            "display_name": CATEGORY_DISPLAY_NAMES.get(cat, cat),
            "weight": data["weight"],
            "score_pct": data["score_pct"],
            "deductions": data["deductions"],
            "total_findings": data["total_findings"],
            "finding_counts": data["finding_counts"],
        }

    if trend is not None:
        result["trend"] = trend

    return json.dumps(result, indent=2)


# ---------------------------------------------------------------------------
# Input Handling
# ---------------------------------------------------------------------------

def load_findings(filepath: str) -> list[dict[str, Any]]:
    """Load findings from a JSON file.

    Accepts either a JSON array of findings directly, or an object with a
    'findings' key containing the array.
    """
    path = Path(filepath)
    if not path.exists():
        print(f"Error: File not found: {filepath}", file=sys.stderr)
        sys.exit(1)

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as exc:
        print(f"Error: Invalid JSON in {filepath}: {exc}", file=sys.stderr)
        sys.exit(1)

    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        if "findings" in data:
            return data["findings"]
        # Single finding object
        return [data]

    print(f"Error: Unexpected JSON structure in {filepath}", file=sys.stderr)
    sys.exit(1)


def validate_findings(findings: list[dict[str, Any]]) -> list[str]:
    """Validate findings and return a list of warnings."""
    warnings: list[str] = []
    valid_severities = set(SEVERITY_DEDUCTIONS.keys())
    valid_categories = set(CATEGORY_WEIGHTS.keys())

    for i, finding in enumerate(findings):
        if not isinstance(finding, dict):
            warnings.append(f"Finding #{i}: not a dict, skipping")
            continue
        sev = finding.get("severity")
        if sev and sev not in valid_severities:
            warnings.append(f"Finding #{i}: unknown severity '{sev}', defaulting to P3")
        cat = finding.get("category")
        if cat and cat not in valid_categories:
            warnings.append(f"Finding #{i}: unknown category '{cat}', defaulting to 'functional'")

    return warnings


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser."""
    parser = argparse.ArgumentParser(
        prog="qa_health_scorer",
        description="Compute a weighted QA health score (0-100) from findings.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python qa_health_scorer.py findings.json\n"
            "  python qa_health_scorer.py findings.json --json\n"
            "  python qa_health_scorer.py findings.json --baseline prev.json --threshold 85\n"
        ),
    )
    parser.add_argument(
        "findings_file",
        help="Path to JSON file containing QA findings",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output results as JSON",
    )
    parser.add_argument(
        "--baseline",
        default=None,
        help="Path to previous score JSON for trend comparison",
    )
    parser.add_argument(
        "--threshold",
        type=int,
        default=70,
        help="Minimum passing score (default: 70)",
    )
    parser.add_argument(
        "--save-baseline",
        action="store_true",
        dest="save_baseline",
        help="Save current score to .qa-baselines/{date}.json for future trend comparison",
    )
    return parser


def main() -> None:
    """Entry point."""
    parser = build_parser()
    args = parser.parse_args()

    # Load and validate
    findings = load_findings(args.findings_file)
    warnings = validate_findings(findings)

    if warnings and not args.json_output:
        for w in warnings:
            print(f"Warning: {w}", file=sys.stderr)

    # Compute scores
    category_scores = compute_category_scores(findings)
    overall_score = compute_overall_score(category_scores)
    grade = score_to_grade(overall_score)
    severity_summary = summarize_findings(findings)
    trend = compute_trend(overall_score, args.baseline)

    # Output
    if args.json_output:
        print(format_json_output(
            overall_score, grade, category_scores,
            severity_summary, trend, args.threshold,
        ))
    else:
        print(format_human_readable(
            overall_score, grade, category_scores,
            severity_summary, trend, args.threshold,
        ))

    # Save baseline if requested
    if args.save_baseline:
        baseline_dir = Path(".qa-baselines")
        baseline_dir.mkdir(parents=True, exist_ok=True)
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        baseline_path = baseline_dir / f"{date_str}.json"
        baseline_data = {
            "score": overall_score,
            "grade": grade,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "findings_count": sum(severity_summary.values()),
            "category_scores": {
                cat: {"score_pct": data["score_pct"], "findings": data["total_findings"]}
                for cat, data in category_scores.items()
            },
        }
        with open(baseline_path, "w", encoding="utf-8") as f:
            json.dump(baseline_data, f, indent=2)
        # Also save as "latest" for easy reference
        latest_path = baseline_dir / "latest.json"
        with open(latest_path, "w", encoding="utf-8") as f:
            json.dump(baseline_data, f, indent=2)
        if not args.json_output:
            print(f"\nBaseline saved to {baseline_path} and {latest_path}")

    # Exit code: non-zero if below threshold
    if overall_score < args.threshold:
        sys.exit(1)


if __name__ == "__main__":
    main()
