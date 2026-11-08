#!/usr/bin/env python3
"""
Design System Validator — Validates CSS against design token definitions.

Detects off-system colors, spacing values, font sizes, border radii,
shadows, and other hardcoded values that should use design tokens.
Reports design system compliance percentage. Parsing and token lookup live in
css_declarations.py; the categories in references/token-categories.json.

Usage:
    python design_system_validator.py --tokens tokens.json --input styles.css
    python design_system_validator.py --tokens tokens.json --input src/ --glob "*.css"
    python design_system_validator.py --tokens tokens.json --input styles.css --output report.json

Exit codes: 0 checked, 1 compliance below --min-compliance, 2 bad input (missing or
invalid token file, no CSS files found).
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


_css = _sibling("css_declarations")
TOKEN_CATEGORIES = _css.TOKEN_CATEGORIES
load_tokens = _css.load_tokens
normalize_color = _css.normalize_color
parse_css_declarations = _css.parse_css_declarations
extract_values_from_declaration = _css.extract_values_from_declaration
find_closest_token = _css.find_closest_token
collect_css_files = _css.collect_css_files


def validate_css(sources: list[tuple[str, str]], tokens: dict) -> dict:
    """Validate CSS against design tokens; each (file, css) source is parsed on its own."""
    declarations = []
    for css_file, css_content in sources:
        for decl in parse_css_declarations(css_content):
            decl["file"] = css_file
            declarations.append(decl)
    violations = []
    compliant_count = 0
    total_checked = 0
    category_stats = {}

    for category in TOKEN_CATEGORIES:
        token_values = tokens.get(category, set())
        if not token_values:
            continue

        cat_violations = []
        cat_compliant = 0
        cat_total = 0

        for decl in declarations:
            extracted = extract_values_from_declaration(decl, category)
            for item in extracted:
                cat_total += 1
                total_checked += 1
                val = item["value"]

                # Special normalization for colors
                if category == "colors":
                    val = normalize_color(val)
                    token_normalized = {normalize_color(t) for t in token_values}
                    is_compliant = val in token_normalized
                else:
                    is_compliant = val in token_values

                if is_compliant:
                    cat_compliant += 1
                    compliant_count += 1
                else:
                    violation = {
                        "category": category,
                        "property": item["context"]["property"],
                        "value": item["original"],
                        "normalized_value": val,
                        "file": item["context"]["file"],
                        "line": item["context"]["line"],
                        "selector": item["context"]["selector"],
                        "raw": item["context"]["raw"],
                    }

                    # Find closest token value
                    closest = find_closest_token(val, token_values, category)
                    if closest:
                        violation["suggested_token"] = closest

                    cat_violations.append(violation)
                    violations.append(violation)

        if cat_total > 0:
            category_stats[category] = {
                "total": cat_total,
                "compliant": cat_compliant,
                "violations": len(cat_violations),
                "compliance_rate": round(cat_compliant / cat_total * 100, 1),
            }

    compliance_rate = round(compliant_count / max(total_checked, 1) * 100, 1)

    return {
        "total_checked": total_checked,
        "compliant": compliant_count,
        "violations_count": len(violations),
        "compliance_rate": compliance_rate,
        "violations": violations,
        "category_stats": category_stats,
    }


def generate_report(results: dict, tokens_path: str, input_path: str) -> dict:
    """Generate a complete validation report."""
    # Determine compliance grade
    rate = results["compliance_rate"]
    if rate >= 95:
        grade = "A"
    elif rate >= 85:
        grade = "B"
    elif rate >= 70:
        grade = "C"
    elif rate >= 50:
        grade = "D"
    else:
        grade = "F"

    # Group violations by category for easier remediation
    by_category = {}
    for v in results["violations"]:
        cat = v["category"]
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(v)

    return {
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "tool": "design_system_validator.py",
            "version": "2.0.0",
            "tokens_file": tokens_path,
            "input_path": input_path,
        },
        "compliance_grade": grade,
        "compliance_rate": results["compliance_rate"],
        "summary": {
            "total_values_checked": results["total_checked"],
            "compliant_values": results["compliant"],
            "violations": results["violations_count"],
        },
        "category_breakdown": results["category_stats"],
        "violations_by_category": {
            cat: [
                {
                    "property": v["property"],
                    "value": v["value"],
                    "file": v["file"],
                    "line": v["line"],
                    "selector": v["selector"],
                    "suggested_token": v.get("suggested_token", "N/A"),
                }
                for v in violations
            ]
            for cat, violations in by_category.items()
        },
        "all_violations": results["violations"],
    }


def format_text_report(report: dict) -> str:
    """Format report as human-readable text."""
    lines = []
    lines.append("=" * 60)
    lines.append("DESIGN SYSTEM VALIDATION REPORT")
    lines.append("=" * 60)
    lines.append(f"Generated: {report['metadata']['generated_at']}")
    lines.append(f"Tokens: {report['metadata']['tokens_file']}")
    lines.append(f"Input: {report['metadata']['input_path']}")
    lines.append("")

    lines.append(f"Compliance Grade: {report['compliance_grade']}")
    lines.append(f"Compliance Rate: {report['compliance_rate']}%")
    lines.append("")

    s = report["summary"]
    lines.append(f"Values checked: {s['total_values_checked']}")
    lines.append(f"Compliant: {s['compliant_values']}")
    lines.append(f"Violations: {s['violations']}")
    lines.append("")

    # Category breakdown
    if report["category_breakdown"]:
        lines.append("CATEGORY BREAKDOWN")
        lines.append("-" * 60)
        lines.append(f"  {'Category':<20} {'Total':>6} {'Pass':>6} {'Fail':>6} {'Rate':>7}")
        lines.append(f"  {'-'*20} {'-'*6} {'-'*6} {'-'*6} {'-'*7}")
        for cat, stats in report["category_breakdown"].items():
            lines.append(
                f"  {cat:<20} {stats['total']:>6} {stats['compliant']:>6} "
                f"{stats['violations']:>6} {stats['compliance_rate']:>6.1f}%"
            )
        lines.append("")

    # Violations by category
    if report["violations_by_category"]:
        lines.append("VIOLATIONS BY CATEGORY")
        lines.append("-" * 60)
        for cat, violations in report["violations_by_category"].items():
            lines.append(f"\n  [{cat.upper()}] ({len(violations)} violations)")
            for v in violations[:20]:  # Limit display
                suggestion = f" -> {v['suggested_token']}" if v.get('suggested_token') != 'N/A' else ""
                lines.append(f"    {v['file']}:{v['line']}: {v['property']}: {v['value']}{suggestion}")
                if v.get("selector"):
                    lines.append(f"      Selector: {v['selector']}")
            if len(violations) > 20:
                lines.append(f"    ... and {len(violations) - 20} more")

    lines.append("")
    lines.append("=" * 60)
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Design System Validator — Validate CSS against design tokens",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --tokens tokens.json --input styles.css
  %(prog)s --tokens tokens.json --input src/ --glob "*.css"
  %(prog)s --tokens tokens.json --input styles.css --output report.json --format text
        """,
    )
    parser.add_argument("--tokens", "-t", required=True, help="Path to design tokens JSON file")
    parser.add_argument("--input", "-i", required=True, help="Path to CSS file or directory")
    parser.add_argument("--glob", "-g", default="*.css", help="Glob pattern for CSS files (default: *.css)")
    parser.add_argument("--min-compliance", type=float, default=None,
                        help="Exit 1 when the compliance rate (percent) is below this value")
    parser.add_argument("--output", "-o", help="Path to write report (default: stdout)")
    parser.add_argument("--format", "-f", choices=["json", "text"], default="json",
                       help="Output format (default: json)")

    args = parser.parse_args()

    # Load tokens
    tokens = load_tokens(args.tokens)

    # Collect CSS files
    css_files = collect_css_files(args.input, args.glob)
    if not css_files:
        print(f"No CSS files found at: {args.input}", file=sys.stderr)
        sys.exit(2)

    # Read each file; lines are reported per file
    sources = []
    for css_file in css_files:
        try:
            with open(css_file, "r", encoding="utf-8") as f:
                sources.append((css_file, f.read()))
        except (IOError, UnicodeDecodeError) as e:
            print(f"Warning: Could not read {css_file}: {e}", file=sys.stderr)

    results = validate_css(sources, tokens)

    # Generate report
    report = generate_report(results, args.tokens, args.input)

    output = format_text_report(report) if args.format == "text" else json.dumps(report, indent=2)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"Report written to {args.output}")
    else:
        print(output)
    if args.min_compliance is not None and results["compliance_rate"] < args.min_compliance:
        sys.exit(1)


if __name__ == "__main__":
    main()
