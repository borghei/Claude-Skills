#!/usr/bin/env python3
"""
AI Slop Detector — grades HTML/CSS for patterns typical of generated landing pages.

Detects stock gradients, template hero/grid/pricing/testimonial structure, template
section order, shadow/blur/radius overuse, mixed icon sets and stock copy. Each finding
has a confidence (0.0-1.0); findings at or above --threshold set the A-F grade. The
checks live in slop_visual_checks.py and slop_content_checks.py, the patterns in
references/slop-patterns.json. This tool grades; to fix what it finds, use
engineering/interface-refinement (its ui_slop_detector.py routes findings to commands).

Usage:
    python ai_slop_detector.py --input page.html
    python ai_slop_detector.py --input page.html --css styles.css
    python ai_slop_detector.py --input page.html --css styles.css --threshold 0.6
    python ai_slop_detector.py --input page.html --format text

Exit codes: 0 nothing at/above threshold, 1 patterns found, 2 bad input.
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


_vis = _sibling("slop_visual_checks")
_con = _sibling("slop_content_checks")
SlopFinding = _vis.SlopFinding
load_page = _vis.load_page


def compute_slop_grade(findings: list[SlopFinding], threshold: float) -> str:
    """Compute overall AI Slop Grade based on findings."""
    if not findings:
        return "A"

    high_confidence = [f for f in findings if f.confidence >= threshold]
    count = len(high_confidence)

    if count == 0:
        return "A"
    elif count <= 2:
        return "B"
    elif count <= 5:
        return "C"
    elif count <= 8:
        return "D"
    else:
        return "F"


def analyze(html_content: str, css_content: str, threshold: float) -> dict:
    """Run all detection passes and produce a report."""
    all_findings: list[SlopFinding] = []

    # Visual patterns (CSS-focused)
    all_findings.extend(_vis.detect_stock_gradients(css_content))
    all_findings.extend(_vis.detect_shadow_overuse(css_content))
    all_findings.extend(_vis.detect_large_border_radius(css_content))

    # Structural patterns (HTML-focused)
    all_findings.extend(_con.detect_generic_hero(html_content))
    all_findings.extend(_con.detect_three_column_grids(html_content, css_content))
    all_findings.extend(_con.detect_pricing_tables(html_content))
    all_findings.extend(_con.detect_testimonial_layouts(html_content))
    all_findings.extend(_con.detect_template_ordering(html_content))

    # Copy patterns
    all_findings.extend(_con.detect_generic_copy(html_content))
    all_findings.extend(_con.detect_lorem_ipsum(html_content))

    # Consistency patterns
    all_findings.extend(_vis.detect_icon_inconsistency(html_content, css_content))


    # Filter by threshold
    above_threshold = [f for f in all_findings if f.confidence >= threshold]
    below_threshold = [f for f in all_findings if f.confidence < threshold]

    grade = compute_slop_grade(all_findings, threshold)

    # Group by type
    by_type = {}
    for f in all_findings:
        cat = f.pattern_type.split("_")[0]
        if cat not in by_type:
            by_type[cat] = []
        by_type[cat].append(f.to_dict())

    return {
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "tool": "ai_slop_detector.py",
            "version": "2.0.0",
            "threshold": threshold,
        },
        "grade": grade,
        "summary": {
            "total_patterns": len(all_findings),
            "above_threshold": len(above_threshold),
            "below_threshold": len(below_threshold),
            "by_category": {cat: len(items) for cat, items in by_type.items()},
        },
        "findings": [f.to_dict() for f in sorted(all_findings, key=lambda x: -x.confidence)],
        "findings_by_category": by_type,
    }


def format_text_report(report: dict) -> str:
    """Format report as human-readable text."""
    lines = []
    lines.append("=" * 60)
    lines.append("AI SLOP DETECTION REPORT")
    lines.append("=" * 60)
    lines.append(f"Generated: {report['metadata']['generated_at']}")
    lines.append(f"Threshold: {report['metadata']['threshold']}")
    lines.append("")

    lines.append(f"AI Slop Grade: {report['grade']}")
    lines.append("")

    s = report["summary"]
    lines.append(f"Total patterns detected: {s['total_patterns']}")
    lines.append(f"  Above threshold: {s['above_threshold']}")
    lines.append(f"  Below threshold: {s['below_threshold']}")
    lines.append("")

    if s["by_category"]:
        lines.append("By Category:")
        category_labels = {
            "visual": "Visual Patterns",
            "structural": "Structural Patterns",
            "copy": "Copy Patterns",
        }
        for cat, count in s["by_category"].items():
            label = category_labels.get(cat, cat.title())
            lines.append(f"  {label}: {count}")
        lines.append("")

    if report["findings"]:
        lines.append("FINDINGS (sorted by confidence)")
        lines.append("-" * 60)
        for f in report["findings"]:
            conf_bar = "#" * int(f["confidence"] * 10)
            lines.append(f"\n  [{f['confidence']:.2f}] {conf_bar}")
            lines.append(f"  Type: {f['pattern_type']}")
            lines.append(f"  {f['description']}")
            if f.get("evidence"):
                lines.append(f"  Evidence: {f['evidence']}")
            if f.get("line"):
                lines.append(f"  Line: {f['line']}")
            if f.get("remediation"):
                lines.append(f"  Fix: {f['remediation']}")

    lines.append("")
    lines.append("=" * 60)
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="AI Slop Detector — Analyze HTML/CSS for AI-generated UI patterns",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --input page.html
  %(prog)s --input page.html --css styles.css --threshold 0.6
  %(prog)s --input page.html --format text
        """,
    )
    parser.add_argument("--input", "-i", required=True, help="Path to HTML file to analyze")
    parser.add_argument("--css", "-c", help="Path to CSS file (optional, will also extract inline styles from HTML)")
    parser.add_argument("--threshold", "-t", type=float, default=0.5, help="Confidence threshold (0.0-1.0, default: 0.5)")
    parser.add_argument("--output", "-o", help="Path to write report JSON (default: stdout)")
    parser.add_argument("--format", "-f", choices=["json", "text"], default="json", help="Output format (default: json)")

    args = parser.parse_args()

    # Validate threshold
    if not 0.0 <= args.threshold <= 1.0:
        print("Error: Threshold must be between 0.0 and 1.0", file=sys.stderr)
        sys.exit(2)

    # Read files; inline and embedded styles from the HTML are added to the CSS
    html_content, css_content = load_page(args.input, args.css)

    # Analyze
    report = analyze(html_content, css_content, args.threshold)

    # Output
    if args.format == "text":
        output = format_text_report(report)
    else:
        output = json.dumps(report, indent=2)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"Report written to {args.output}")
    else:
        print(output)
    # Exit 1 when any pattern is at or above the confidence threshold.
    sys.exit(1 if report["summary"]["above_threshold"] else 0)


if __name__ == "__main__":
    main()
