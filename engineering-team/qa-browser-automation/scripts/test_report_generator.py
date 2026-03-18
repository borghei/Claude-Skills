#!/usr/bin/env python3
"""Test Report Generator — Generates comprehensive QA reports from session data.

Takes QA session data (findings, scores, screenshots, accessibility results,
performance metrics) as JSON input and produces detailed reports in markdown
or JSON format. Includes executive summary, health score dashboard, findings
by severity, and actionable recommendations.

Usage:
    python test_report_generator.py session_data.json
    python test_report_generator.py session_data.json --format json
    python test_report_generator.py session_data.json --format markdown -o report.md
    python test_report_generator.py session_data.json --history scores_history.json
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

SEVERITY_ORDER = ["P0", "P1", "P2", "P3", "P4"]
SEVERITY_LABELS = {
    "P0": "Critical",
    "P1": "High",
    "P2": "Medium",
    "P3": "Low",
    "P4": "Cosmetic",
}
SEVERITY_EMOJI_TEXT = {
    "P0": "[CRITICAL]",
    "P1": "[HIGH]",
    "P2": "[MEDIUM]",
    "P3": "[LOW]",
    "P4": "[COSMETIC]",
}

GRADE_THRESHOLDS = [
    (90, "A"),
    (80, "B"),
    (70, "C"),
    (60, "D"),
    (0, "F"),
]

CATEGORY_DISPLAY_NAMES = {
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
# Data Loading
# ---------------------------------------------------------------------------

def load_session_data(filepath: str) -> dict[str, Any]:
    """Load QA session data from a JSON file.

    Expected structure:
    {
        "project": "My App",
        "url": "https://example.com",
        "tester": "QA Engineer",
        "tier": "standard",
        "timestamp": "2026-03-18T...",
        "health_score": { ... },       // optional, from qa_health_scorer
        "findings": [ ... ],            // list of finding objects
        "accessibility": { ... },       // optional, from accessibility_auditor
        "performance": { ... },         // optional, performance metrics
        "visual_regression": { ... },   // optional, from visual_regression_tracker
        "screenshots": [ ... ],         // optional, list of screenshot paths
        "notes": "..."                  // optional, free text
    }
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

    return data


def load_history(filepath: str | None) -> list[dict[str, Any]]:
    """Load score history for trend analysis."""
    if not filepath:
        return []
    path = Path(filepath)
    if not path.exists():
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            return data
        if isinstance(data, dict) and "history" in data:
            return data["history"]
        return []
    except (json.JSONDecodeError, OSError):
        return []


# ---------------------------------------------------------------------------
# Analysis Helpers
# ---------------------------------------------------------------------------

def score_to_grade(score: float) -> str:
    """Convert a numeric score to a letter grade."""
    for threshold, grade in GRADE_THRESHOLDS:
        if score >= threshold:
            return grade
    return "F"


def count_findings_by_severity(findings: list[dict[str, Any]]) -> dict[str, int]:
    """Count findings grouped by severity."""
    counts: dict[str, int] = {sev: 0 for sev in SEVERITY_ORDER}
    for f in findings:
        sev = f.get("severity", "P3")
        if sev in counts:
            counts[sev] += 1
        else:
            counts["P3"] += 1
    return counts


def count_findings_by_category(findings: list[dict[str, Any]]) -> dict[str, int]:
    """Count findings grouped by category."""
    counts: dict[str, int] = {}
    for f in findings:
        cat = f.get("category", "functional")
        counts[cat] = counts.get(cat, 0) + 1
    return counts


def compute_trend(current_score: float, history: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Compute trend data from score history."""
    if not history:
        return None

    scores = [h.get("score", h.get("overall_score", 0)) for h in history]
    if not scores:
        return None

    previous = scores[-1]
    delta = round(current_score - previous, 1)
    avg = round(sum(scores) / len(scores), 1)

    if len(scores) >= 2:
        recent_trend = scores[-1] - scores[-2]
        direction = "improving" if recent_trend > 0 else "declining" if recent_trend < 0 else "stable"
    else:
        direction = "improving" if delta > 0 else "declining" if delta < 0 else "stable"

    return {
        "previous_score": previous,
        "delta": delta,
        "direction": direction,
        "average": avg,
        "history_length": len(scores),
        "best": max(scores),
        "worst": min(scores),
    }


def generate_recommendations(
    findings: list[dict[str, Any]],
    health_score: dict[str, Any] | None,
    accessibility: dict[str, Any] | None,
) -> list[str]:
    """Generate prioritized recommendations based on findings."""
    recommendations: list[str] = []
    severity_counts = count_findings_by_severity(findings)

    if severity_counts.get("P0", 0) > 0:
        recommendations.append(
            f"URGENT: {severity_counts['P0']} critical issue(s) must be resolved before any release. "
            "These include application crashes, data loss risks, or security vulnerabilities."
        )

    if severity_counts.get("P1", 0) > 0:
        recommendations.append(
            f"HIGH PRIORITY: {severity_counts['P1']} high-severity issue(s) should be fixed within the current sprint."
        )

    if health_score:
        categories = health_score.get("categories", {})
        weak_categories = [
            (cat, data.get("score_pct", 100))
            for cat, data in categories.items()
            if data.get("score_pct", 100) < 70
        ]
        for cat, pct in sorted(weak_categories, key=lambda x: x[1]):
            display = CATEGORY_DISPLAY_NAMES.get(cat, cat)
            recommendations.append(
                f"Improve {display} (currently {pct:.0f}%): Focus on resolving {cat} findings to raise the overall health score."
            )

    if accessibility:
        must_fix = accessibility.get("by_severity", {}).get("must-fix", 0)
        if must_fix > 0:
            recommendations.append(
                f"Accessibility: {must_fix} must-fix WCAG violation(s) detected. "
                "Address these to meet minimum compliance requirements."
            )

    category_counts = count_findings_by_category(findings)
    top_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:3]
    if top_categories:
        cats = ", ".join(CATEGORY_DISPLAY_NAMES.get(c, c) for c, _ in top_categories)
        recommendations.append(
            f"Most affected areas: {cats}. Consider dedicated review sessions for these categories."
        )

    if not recommendations:
        recommendations.append("No critical issues found. Continue monitoring with regular QA sweeps.")

    return recommendations


# ---------------------------------------------------------------------------
# Markdown Report Generation
# ---------------------------------------------------------------------------

def generate_markdown_report(
    session: dict[str, Any],
    history: list[dict[str, Any]],
) -> str:
    """Generate a comprehensive markdown QA report."""
    lines: list[str] = []
    now = session.get("timestamp", datetime.now(timezone.utc).isoformat())
    project = session.get("project", "Unknown Project")
    url = session.get("url", "N/A")
    tester = session.get("tester", "QA Automation")
    tier = session.get("tier", "standard")
    findings = session.get("findings", [])
    health_data = session.get("health_score", {})
    accessibility = session.get("accessibility", {})
    performance = session.get("performance", {})
    visual_reg = session.get("visual_regression", {})
    notes = session.get("notes", "")

    overall_score = health_data.get("overall_score", health_data.get("score", 0))
    grade = score_to_grade(overall_score)
    severity_counts = count_findings_by_severity(findings)
    total_findings = sum(severity_counts.values())

    # --- Header ---
    lines.append(f"# QA Report: {project}")
    lines.append("")
    lines.append(f"**Date:** {now}")
    lines.append(f"**URL:** {url}")
    lines.append(f"**Tester:** {tester}")
    lines.append(f"**Tier:** {tier.capitalize()}")
    lines.append(f"**Total Findings:** {total_findings}")
    lines.append("")

    # --- Executive Summary ---
    lines.append("## Executive Summary")
    lines.append("")
    pass_fail = "PASS" if overall_score >= 70 else "FAIL"
    lines.append(f"The application scored **{overall_score}/100 (Grade: {grade})** — **{pass_fail}**.")
    lines.append("")

    if severity_counts.get("P0", 0) > 0:
        lines.append(f"**{severity_counts['P0']} critical issue(s) detected** requiring immediate attention before release.")
    elif severity_counts.get("P1", 0) > 0:
        lines.append(f"No critical issues, but **{severity_counts['P1']} high-severity issue(s)** should be addressed this sprint.")
    elif total_findings > 0:
        lines.append(f"No critical or high-severity issues. {total_findings} lower-priority finding(s) identified for improvement.")
    else:
        lines.append("No issues detected. The application is in excellent condition.")
    lines.append("")

    # --- Health Score Dashboard ---
    lines.append("## Health Score Dashboard")
    lines.append("")
    lines.append(f"| Metric | Value |")
    lines.append(f"|--------|-------|")
    lines.append(f"| Overall Score | {overall_score}/100 |")
    lines.append(f"| Grade | {grade} |")
    lines.append(f"| Status | {pass_fail} |")
    lines.append(f"| Total Findings | {total_findings} |")
    lines.append("")

    # Category breakdown
    categories = health_data.get("categories", {})
    if categories:
        lines.append("### Category Breakdown")
        lines.append("")
        lines.append("| Category | Weight | Score | Findings |")
        lines.append("|----------|--------|-------|----------|")
        for cat, data in categories.items():
            display = CATEGORY_DISPLAY_NAMES.get(cat, data.get("display_name", cat))
            weight = f"{int(data.get('weight', 0) * 100)}%"
            score_pct = f"{data.get('score_pct', 100):.0f}%"
            count = data.get("total_findings", 0)
            lines.append(f"| {display} | {weight} | {score_pct} | {count} |")
        lines.append("")

    # Trend
    trend = compute_trend(overall_score, history)
    if trend:
        lines.append("### Trend")
        lines.append("")
        arrow = "+" if trend["delta"] > 0 else "" if trend["delta"] < 0 else ""
        lines.append(f"- **Direction:** {trend['direction'].capitalize()}")
        lines.append(f"- **Previous:** {trend['previous_score']}")
        lines.append(f"- **Delta:** {arrow}{trend['delta']} pts")
        lines.append(f"- **Average:** {trend['average']} (over {trend['history_length']} runs)")
        lines.append(f"- **Best:** {trend['best']} / **Worst:** {trend['worst']}")
        lines.append("")

    # --- Findings by Severity ---
    lines.append("## Findings by Severity")
    lines.append("")

    for sev in SEVERITY_ORDER:
        sev_findings = [f for f in findings if f.get("severity", "P3") == sev]
        if not sev_findings:
            continue

        label = SEVERITY_LABELS.get(sev, sev)
        tag = SEVERITY_EMOJI_TEXT.get(sev, "")
        lines.append(f"### {sev} — {label} ({len(sev_findings)} finding{'s' if len(sev_findings) != 1 else ''})")
        lines.append("")

        for i, finding in enumerate(sev_findings, 1):
            title = finding.get("title", finding.get("message", "Untitled finding"))
            category = finding.get("category", "functional")
            display_cat = CATEGORY_DISPLAY_NAMES.get(category, category)
            description = finding.get("description", "")
            location = finding.get("location", finding.get("page", finding.get("url", "")))
            steps = finding.get("steps_to_reproduce", "")
            expected = finding.get("expected", "")
            actual = finding.get("actual", "")

            lines.append(f"**{i}. {title}** {tag}")
            lines.append(f"- **Category:** {display_cat}")
            if location:
                lines.append(f"- **Location:** {location}")
            if description:
                lines.append(f"- **Description:** {description}")
            if steps:
                lines.append(f"- **Steps:** {steps}")
            if expected:
                lines.append(f"- **Expected:** {expected}")
            if actual:
                lines.append(f"- **Actual:** {actual}")
            lines.append("")

    if total_findings == 0:
        lines.append("No findings recorded.")
        lines.append("")

    # --- Accessibility Results ---
    if accessibility:
        lines.append("## Accessibility Results")
        lines.append("")
        level = accessibility.get("level_checked", "AA")
        total_violations = accessibility.get("total_violations", 0)
        compliance = accessibility.get("compliance_percentage", 100)
        lines.append(f"- **Level Checked:** WCAG 2.1 {level}")
        lines.append(f"- **Violations:** {total_violations}")
        lines.append(f"- **Compliance:** {compliance}%")
        lines.append("")

        by_severity = accessibility.get("by_severity", {})
        if by_severity:
            lines.append("| Severity | Count |")
            lines.append("|----------|-------|")
            for sev in ("must-fix", "should-fix", "nice-to-have"):
                lines.append(f"| {sev} | {by_severity.get(sev, 0)} |")
            lines.append("")

        a11y_violations = accessibility.get("violations", [])
        if a11y_violations:
            lines.append("### Top Accessibility Violations")
            lines.append("")
            for v in a11y_violations[:10]:
                rule = v.get("rule_id", "unknown")
                msg = v.get("message", "")
                criterion = v.get("wcag_criterion", "")
                lines.append(f"- **{rule}** ({criterion}): {msg}")
            if len(a11y_violations) > 10:
                lines.append(f"- ... and {len(a11y_violations) - 10} more")
            lines.append("")

    # --- Performance Metrics ---
    if performance:
        lines.append("## Performance Metrics")
        lines.append("")

        metrics = performance.get("metrics", performance)
        if isinstance(metrics, dict):
            lines.append("| Metric | Value | Threshold | Status |")
            lines.append("|--------|-------|-----------|--------|")

            metric_defs = {
                "lcp": ("Largest Contentful Paint", "2.5s", 2500),
                "fid": ("First Input Delay", "100ms", 100),
                "cls": ("Cumulative Layout Shift", "0.1", 0.1),
                "inp": ("Interaction to Next Paint", "200ms", 200),
                "ttfb": ("Time to First Byte", "800ms", 800),
                "fcp": ("First Contentful Paint", "1.8s", 1800),
                "tti": ("Time to Interactive", "3.8s", 3800),
                "tbt": ("Total Blocking Time", "200ms", 200),
            }

            for key, (label, threshold_str, threshold_val) in metric_defs.items():
                value = metrics.get(key)
                if value is not None:
                    if key == "cls":
                        val_str = f"{value:.3f}"
                        status = "Pass" if value <= threshold_val else "Fail"
                    else:
                        val_str = f"{value}ms"
                        status = "Pass" if value <= threshold_val else "Fail"
                    lines.append(f"| {label} | {val_str} | {threshold_str} | {status} |")

            lines.append("")

        # Resource summary
        resources = performance.get("resources", {})
        if resources:
            lines.append("### Resource Summary")
            lines.append("")
            total_size = resources.get("total_size_kb", 0)
            request_count = resources.get("request_count", 0)
            lines.append(f"- **Total Transfer Size:** {total_size} KB")
            lines.append(f"- **Request Count:** {request_count}")
            for rtype, size in resources.get("by_type", {}).items():
                lines.append(f"- **{rtype}:** {size} KB")
            lines.append("")

    # --- Visual Regression ---
    if visual_reg:
        lines.append("## Visual Regression Results")
        lines.append("")
        summary = visual_reg.get("summary", {})
        lines.append(f"- **Pages Compared:** {summary.get('total_compared', 0)}")
        lines.append(f"- **Passed:** {summary.get('passed', 0)}")
        lines.append(f"- **Failed:** {summary.get('failed', 0)}")
        lines.append(f"- **New Pages:** {summary.get('new_pages', 0)}")
        lines.append("")

        pages = visual_reg.get("pages", {})
        failed_pages = {k: v for k, v in pages.items() if v.get("status") == "fail"}
        if failed_pages:
            lines.append("### Regressions Detected")
            lines.append("")
            lines.append("| Page | Change % |")
            lines.append("|------|----------|")
            for page, data in sorted(failed_pages.items(), key=lambda x: x[1].get("change_pct", 0), reverse=True):
                lines.append(f"| {page} | {data.get('change_pct', 0)}% |")
            lines.append("")

    # --- Recommendations ---
    recommendations = generate_recommendations(findings, health_data, accessibility)
    lines.append("## Recommendations")
    lines.append("")
    for i, rec in enumerate(recommendations, 1):
        lines.append(f"{i}. {rec}")
    lines.append("")

    # --- Notes ---
    if notes:
        lines.append("## Notes")
        lines.append("")
        lines.append(notes)
        lines.append("")

    # --- Footer ---
    lines.append("---")
    lines.append("")
    lines.append(f"*Generated by QA Browser Automation skill — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}*")
    lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# JSON Summary Generation
# ---------------------------------------------------------------------------

def generate_json_summary(
    session: dict[str, Any],
    history: list[dict[str, Any]],
) -> str:
    """Generate a JSON summary of the QA session."""
    findings = session.get("findings", [])
    health_data = session.get("health_score", {})
    accessibility = session.get("accessibility", {})
    performance = session.get("performance", {})
    visual_reg = session.get("visual_regression", {})

    overall_score = health_data.get("overall_score", health_data.get("score", 0))
    severity_counts = count_findings_by_severity(findings)
    category_counts = count_findings_by_category(findings)
    trend = compute_trend(overall_score, history)
    recommendations = generate_recommendations(findings, health_data, accessibility)

    summary: dict[str, Any] = {
        "report_type": "qa_session_summary",
        "generated": datetime.now(timezone.utc).isoformat(),
        "project": session.get("project", "Unknown"),
        "url": session.get("url", ""),
        "tier": session.get("tier", "standard"),
        "health_score": overall_score,
        "grade": score_to_grade(overall_score),
        "passed": overall_score >= 70,
        "total_findings": sum(severity_counts.values()),
        "findings_by_severity": severity_counts,
        "findings_by_category": category_counts,
        "accessibility_violations": accessibility.get("total_violations", 0),
        "accessibility_compliance_pct": accessibility.get("compliance_percentage"),
        "visual_regressions": visual_reg.get("summary", {}).get("failed", 0),
        "performance_metrics": performance.get("metrics", {}),
        "trend": trend,
        "recommendations": recommendations,
    }

    return json.dumps(summary, indent=2)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser."""
    parser = argparse.ArgumentParser(
        prog="test_report_generator",
        description="Generate comprehensive QA reports from session data.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python test_report_generator.py session_data.json\n"
            "  python test_report_generator.py session_data.json --format json\n"
            "  python test_report_generator.py session_data.json -o report.md\n"
            "  python test_report_generator.py session_data.json --history history.json\n"
        ),
    )
    parser.add_argument(
        "session_file",
        help="Path to QA session data JSON file",
    )
    parser.add_argument(
        "--format",
        choices=["markdown", "json"],
        default="markdown",
        dest="output_format",
        help="Output format (default: markdown)",
    )
    parser.add_argument(
        "-o", "--output",
        default=None,
        help="Write report to file instead of stdout",
    )
    parser.add_argument(
        "--history",
        default=None,
        help="Path to score history JSON for trend analysis",
    )
    return parser


def main() -> None:
    """Entry point."""
    parser = build_parser()
    args = parser.parse_args()

    session = load_session_data(args.session_file)
    history = load_history(args.history)

    if args.output_format == "json":
        output = generate_json_summary(session, history)
    else:
        output = generate_markdown_report(session, history)

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(output, encoding="utf-8")
        print(f"Report written to: {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
