#!/usr/bin/env python3
"""
Color Contrast Checker — WCAG 2.x color contrast validation.

Checks color contrast ratios against WCAG AA and AAA standards (1.4.3 text, 1.4.11
non-text UI). Supports hex, rgb, and hsl color formats. Suggests closest compliant
color alternatives when a pair fails. Parsing lives in color_parse.py and the pair
check in contrast_pairs.py; this script adds batch input, grading and the report.

Usage:
    python color_contrast_checker.py --foreground "#333" --background "#fff"
    python color_contrast_checker.py --input color_pairs.json --level AAA
    python color_contrast_checker.py --input colors.json --level AA --suggest-fixes
    python color_contrast_checker.py --foreground "rgb(51,51,51)" --background "hsl(0,0%,100%)"

Exit codes: 0 all pairs pass, 1 a pair fails, 2 bad input (missing file, invalid JSON,
malformed pair list, or an unparseable colour in single-pair mode).
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


_pairs = _sibling("contrast_pairs")
check_pair = _pairs.check_pair
check_pairs_from_json = _pairs.check_pairs_from_json


def generate_report(results: list[dict], level: str) -> dict:
    """Generate a summary report from multiple pair checks."""
    total = len(results)
    passing = sum(1 for r in results if r.get("passes", False))
    failing = total - passing
    errors = [r for r in results if "error" in r]

    report = {
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "tool": "color_contrast_checker.py",
            "version": "2.0.0",
            "wcag_level": level,
        },
        "summary": {
            "total_pairs": total,
            "passing": passing,
            "failing": failing,
            "errors": len(errors),
            "compliance_rate": round(passing / max(total, 1) * 100, 1),
        },
        "results": results,
        "failing_pairs": [r for r in results if not r.get("passes", True) and "error" not in r],
    }

    # Determine accessibility grade
    rate = report["summary"]["compliance_rate"]
    if rate == 100 and level == "AAA":
        report["accessibility_grade"] = "A+"
    elif rate == 100:
        report["accessibility_grade"] = "A"
    elif rate >= 90:
        report["accessibility_grade"] = "B"
    elif rate >= 70:
        report["accessibility_grade"] = "C"
    elif rate >= 50:
        report["accessibility_grade"] = "D"
    else:
        report["accessibility_grade"] = "F"

    return report


def format_text_output(report: dict) -> str:
    """Format report as human-readable text."""
    lines = []
    lines.append("=" * 60)
    lines.append("COLOR CONTRAST CHECK REPORT")
    lines.append("=" * 60)
    lines.append(f"Generated: {report['metadata']['generated_at']}")
    lines.append(f"WCAG Level: {report['metadata']['wcag_level']}")
    lines.append("")

    s = report["summary"]
    lines.append(f"Accessibility Grade: {report.get('accessibility_grade', 'N/A')}")
    lines.append(f"Compliance Rate: {s['compliance_rate']}%")
    lines.append(f"Total pairs: {s['total_pairs']} | Pass: {s['passing']} | Fail: {s['failing']}")
    lines.append("")

    for r in report["results"]:
        if "error" in r:
            lines.append(f"  ERROR: {r['error']}")
            continue

        label = r.get("label", "")
        status = "PASS" if r["passes"] else "FAIL"
        fg_hex = r["foreground"]["hex"]
        bg_hex = r["background"]["hex"]
        ratio = r["contrast_ratio"]
        required = r["required_ratio"]

        lines.append(f"  [{status}] {label}")
        lines.append(f"    FG: {fg_hex}  BG: {bg_hex}")
        lines.append(f"    Ratio: {ratio}:1 (required: {required}:1)")
        lines.append(f"    AA normal: {'Y' if r.get('wcag_aa_normal') else 'N'} | "
                     f"AA large: {'Y' if r.get('wcag_aa_large') else 'N'} | "
                     f"AAA normal: {'Y' if r.get('wcag_aaa_normal') else 'N'} | "
                     f"AAA large: {'Y' if r.get('wcag_aaa_large') else 'N'}")

        if "suggestions" in r:
            sug = r["suggestions"]
            lines.append(f"    Suggested FG: {sug['adjust_foreground']['hex']} (ratio: {sug['adjust_foreground']['new_ratio']}:1)")
            lines.append(f"    Suggested BG: {sug['adjust_background']['hex']} (ratio: {sug['adjust_background']['new_ratio']}:1)")
        lines.append("")

    if report["failing_pairs"]:
        lines.append("FAILING PAIRS SUMMARY")
        lines.append("-" * 40)
        for r in report["failing_pairs"]:
            lines.append(f"  {r.get('label', '?')}: {r['foreground']['hex']} on {r['background']['hex']} "
                        f"= {r['contrast_ratio']}:1 (need {r['required_ratio']}:1)")

    lines.append("")
    lines.append("=" * 60)
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Color Contrast Checker — WCAG 2.1 color contrast validation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --foreground "#333" --background "#fff"
  %(prog)s --foreground "rgb(51,51,51)" --background "hsl(0,0%%,100%%)"
  %(prog)s --input colors.json --level AAA --suggest-fixes
  %(prog)s --foreground "#666" --background "#eee" --size large
        """,
    )

    # Single pair mode
    parser.add_argument("--foreground", "--fg", help="Foreground color (hex, rgb, hsl)")
    parser.add_argument("--background", "--bg", help="Background color (hex, rgb, hsl)")
    parser.add_argument("--size", choices=["normal", "large", "ui"], default="normal",
                       help="Text size context (default: normal)")

    # Batch mode
    parser.add_argument("--input", "-i", help="Path to JSON file with color pairs")

    # Options
    parser.add_argument("--level", "-l", choices=["AA", "AAA"], default="AA",
                       help="WCAG level to check against (default: AA)")
    parser.add_argument("--suggest-fixes", "-s", action="store_true",
                       help="Suggest compliant color alternatives for failing pairs")
    parser.add_argument("--output", "-o", help="Path to write report (default: stdout)")
    parser.add_argument("--format", "-f", choices=["json", "text"], default="json",
                       help="Output format (default: json)")

    args = parser.parse_args()

    # Determine mode
    if args.input:
        # Batch mode
        try:
            with open(args.input, "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            print(f"Error: File not found: {args.input}", file=sys.stderr)
            sys.exit(2)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON: {e}", file=sys.stderr)
            sys.exit(2)

        try:
            results = check_pairs_from_json(data, args.level, args.suggest_fixes)
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(2)

    elif args.foreground and args.background:
        # Single pair mode: an unparseable colour is bad input, not a failing pair
        result = check_pair(args.foreground, args.background, args.level, args.size, args.suggest_fixes)
        if "error" in result:
            print(f"Error: {result['error']}", file=sys.stderr)
            sys.exit(2)
        result["label"] = "input_pair"
        results = [result]

    else:
        parser.error("Provide either --foreground and --background, or --input")
        return

    # Generate report
    report = generate_report(results, args.level)

    # Output
    if args.format == "text":
        output = format_text_output(report)
    else:
        output = json.dumps(report, indent=2)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"Report written to {args.output}")
    else:
        print(output)
    # Exit 1 when any pair fails the requested WCAG level.
    sys.exit(1 if report["summary"]["failing"] else 0)


if __name__ == "__main__":
    main()
