#!/usr/bin/env python3
"""
Design System Validator — Validates CSS against design token definitions.

Detects off-system colors, spacing values, font sizes, border radii,
shadows, and other hardcoded values that should use design tokens.
Reports design system compliance percentage.

Usage:
    python design_system_validator.py --tokens tokens.json --input styles.css
    python design_system_validator.py --tokens tokens.json --input src/ --glob "*.css"
    python design_system_validator.py --tokens tokens.json --input styles.css --output report.json
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from typing import Any

# CSS properties grouped by token category
TOKEN_CATEGORIES = {
    "colors": {
        "properties": [
            "color", "background-color", "background", "border-color",
            "border-top-color", "border-right-color", "border-bottom-color",
            "border-left-color", "outline-color", "box-shadow", "text-shadow",
            "fill", "stroke", "text-decoration-color", "caret-color",
            "column-rule-color", "accent-color",
        ],
        "extract_pattern": r"(#[0-9a-fA-F]{3,8}|rgba?\s*\([^)]+\)|hsla?\s*\([^)]+\))",
    },
    "spacing": {
        "properties": [
            "margin", "margin-top", "margin-right", "margin-bottom", "margin-left",
            "padding", "padding-top", "padding-right", "padding-bottom", "padding-left",
            "gap", "row-gap", "column-gap", "top", "right", "bottom", "left",
            "inset",
        ],
        "extract_pattern": r"(\d+(?:\.\d+)?(?:px|rem|em))",
    },
    "font_sizes": {
        "properties": ["font-size"],
        "extract_pattern": r"(\d+(?:\.\d+)?(?:px|rem|em))",
    },
    "font_families": {
        "properties": ["font-family"],
        "extract_pattern": r"font-family\s*:\s*([^;]+)",
    },
    "font_weights": {
        "properties": ["font-weight"],
        "extract_pattern": r"(\d{3}|bold|normal|lighter|bolder)",
    },
    "line_heights": {
        "properties": ["line-height"],
        "extract_pattern": r"(\d+(?:\.\d+)?(?:px|rem|em|%)?)",
    },
    "border_radii": {
        "properties": ["border-radius", "border-top-left-radius",
                       "border-top-right-radius", "border-bottom-right-radius",
                       "border-bottom-left-radius"],
        "extract_pattern": r"(\d+(?:\.\d+)?(?:px|rem|em|%))",
    },
    "shadows": {
        "properties": ["box-shadow", "text-shadow"],
        "extract_pattern": r"((?:\d+(?:\.\d+)?(?:px|rem|em)\s+){2,}(?:\d+(?:\.\d+)?(?:px|rem|em)\s+)?(?:\d+(?:\.\d+)?(?:px|rem|em)\s+)?(?:#[0-9a-fA-F]{3,8}|rgba?\s*\([^)]+\)|hsla?\s*\([^)]+\)))",
    },
    "breakpoints": {
        "properties": [],  # Extracted from media queries
        "extract_pattern": r"@media[^{]*(?:min|max)-width\s*:\s*(\d+(?:\.\d+)?(?:px|rem|em))",
    },
    "z_indices": {
        "properties": ["z-index"],
        "extract_pattern": r"(-?\d+)",
    },
    "transitions": {
        "properties": ["transition", "transition-duration", "animation-duration"],
        "extract_pattern": r"(\d+(?:\.\d+)?(?:ms|s))",
    },
}

# Values to skip during validation (CSS keywords, special values)
SKIP_VALUES = {
    "0", "0px", "auto", "inherit", "initial", "unset", "revert",
    "none", "transparent", "currentColor", "currentcolor",
    "100%", "50%", "0%",
}


def load_tokens(path: str) -> dict:
    """Load design tokens from JSON file.

    Expected format:
    {
        "colors": {"primary": "#1a73e8", "secondary": "#5f6368", ...},
        "spacing": {"xs": "4px", "sm": "8px", "md": "16px", ...},
        "font_sizes": {"sm": "14px", "base": "16px", "lg": "18px", ...},
        "font_families": {"sans": "Inter, sans-serif", ...},
        "font_weights": {"normal": "400", "medium": "500", "bold": "700"},
        "line_heights": {"tight": "1.25", "normal": "1.5", "relaxed": "1.75"},
        "border_radii": {"sm": "4px", "md": "8px", "lg": "12px", "full": "9999px"},
        "shadows": {"sm": "0 1px 2px rgba(0,0,0,0.05)", ...},
        "breakpoints": {"sm": "640px", "md": "768px", "lg": "1024px", "xl": "1280px"},
        "z_indices": {"dropdown": "1000", "modal": "2000", "tooltip": "3000"},
        "transitions": {"fast": "150ms", "normal": "300ms", "slow": "500ms"}
    }
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Token file not found: {path}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in token file: {e}", file=sys.stderr)
        sys.exit(1)

    # Normalize: extract just the values into flat sets
    normalized = {}
    for category, tokens in data.items():
        if isinstance(tokens, dict):
            normalized[category] = set(str(v).strip().lower() for v in tokens.values())
        elif isinstance(tokens, list):
            normalized[category] = set(str(v).strip().lower() for v in tokens)
        else:
            normalized[category] = set()

    return normalized


def normalize_color(color: str) -> str:
    """Normalize color to lowercase hex for comparison."""
    color = color.strip().lower()
    if color.startswith("#"):
        # Expand 3-char hex to 6-char
        hex_val = color.lstrip("#")
        if len(hex_val) == 3:
            hex_val = "".join(c * 2 for c in hex_val)
        return f"#{hex_val[:6]}"
    return color


def normalize_value(value: str) -> str:
    """Normalize a CSS value for comparison."""
    value = value.strip().lower()
    # Remove extra whitespace
    value = re.sub(r"\s+", " ", value)
    return value


def parse_css_declarations(css_content: str) -> list[dict]:
    """Parse CSS into declarations with file position info."""
    declarations = []
    # Remove comments
    css_clean = re.sub(r"/\*.*?\*/", "", css_content, flags=re.DOTALL)

    # Track line numbers
    lines = css_clean.split("\n")
    current_selector = ""

    for line_num, line in enumerate(lines, 1):
        stripped = line.strip()

        # Track selector context
        if "{" in stripped and ":" not in stripped.split("{")[0]:
            current_selector = stripped.split("{")[0].strip()

        # Match property: value declarations
        prop_match = re.match(r"\s*([\w-]+)\s*:\s*(.+?)(?:;|$)", stripped)
        if prop_match:
            prop = prop_match.group(1).strip().lower()
            value = prop_match.group(2).strip()
            declarations.append({
                "property": prop,
                "value": value,
                "line": line_num,
                "selector": current_selector,
                "raw": stripped,
            })

    # Also extract media query breakpoints
    for match in re.finditer(r"@media[^{]*\{", css_clean):
        bp_match = re.search(r"(?:min|max)-width\s*:\s*(\d+(?:\.\d+)?(?:px|rem|em))", match.group())
        if bp_match:
            line = css_clean[:match.start()].count("\n") + 1
            declarations.append({
                "property": "__media_query__",
                "value": bp_match.group(1),
                "line": line,
                "selector": "@media",
                "raw": match.group().strip(),
            })

    return declarations


def extract_values_from_declaration(decl: dict, category: str) -> list[dict]:
    """Extract token-checkable values from a CSS declaration."""
    prop = decl["property"]
    value = decl["value"]
    cat_config = TOKEN_CATEGORIES.get(category, {})
    properties = cat_config.get("properties", [])
    pattern = cat_config.get("extract_pattern", "")

    # Special case for media queries
    if category == "breakpoints" and prop == "__media_query__":
        return [{"value": normalize_value(value), "original": value, "context": decl}]

    # Check if property matches category
    if prop not in properties:
        return []

    # Extract values using pattern
    results = []
    if pattern:
        matches = re.findall(pattern, value, re.IGNORECASE)
        for m in matches:
            normalized = normalize_value(m)
            if normalized not in SKIP_VALUES:
                results.append({
                    "value": normalized,
                    "original": m,
                    "context": decl,
                })

    return results


def validate_css(css_content: str, tokens: dict) -> dict:
    """Validate CSS content against design tokens."""
    declarations = parse_css_declarations(css_content)
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


def find_closest_token(value: str, token_values: set, category: str) -> str | None:
    """Find the closest matching token value."""
    if category == "colors":
        return _find_closest_color(value, token_values)
    elif category in ("spacing", "font_sizes", "border_radii"):
        return _find_closest_numeric(value, token_values)
    return None


def _parse_numeric_value(val: str) -> float | None:
    """Extract numeric part from a CSS value like '16px' or '1.5rem'."""
    match = re.match(r"(-?\d+(?:\.\d+)?)", val)
    if match:
        return float(match.group(1))
    return None


def _find_closest_numeric(value: str, token_values: set) -> str | None:
    """Find closest numeric token value."""
    target = _parse_numeric_value(value)
    if target is None:
        return None

    closest = None
    min_diff = float("inf")

    for tv in token_values:
        tv_num = _parse_numeric_value(tv)
        if tv_num is not None:
            diff = abs(target - tv_num)
            if diff < min_diff:
                min_diff = diff
                closest = tv

    return closest


def _hex_to_rgb(hex_color: str) -> tuple[int, int, int] | None:
    """Convert hex to RGB tuple."""
    hex_val = hex_color.lstrip("#").lower()
    if len(hex_val) == 3:
        hex_val = "".join(c * 2 for c in hex_val)
    if len(hex_val) != 6:
        return None
    try:
        return (int(hex_val[0:2], 16), int(hex_val[2:4], 16), int(hex_val[4:6], 16))
    except ValueError:
        return None


def _find_closest_color(value: str, token_values: set) -> str | None:
    """Find closest color token by Euclidean distance in RGB space."""
    target_rgb = _hex_to_rgb(value)
    if target_rgb is None:
        return None

    closest = None
    min_dist = float("inf")

    for tv in token_values:
        tv_rgb = _hex_to_rgb(tv)
        if tv_rgb is not None:
            dist = sum((a - b) ** 2 for a, b in zip(target_rgb, tv_rgb)) ** 0.5
            if dist < min_dist:
                min_dist = dist
                closest = tv

    return closest


def collect_css_files(path: str, glob_pattern: str = "*.css") -> list[str]:
    """Collect CSS files from a path (file or directory)."""
    if os.path.isfile(path):
        return [path]

    if not os.path.isdir(path):
        print(f"Error: Path not found: {path}", file=sys.stderr)
        sys.exit(1)

    # Simple glob matching for *.css files
    files = []
    for root, dirs, filenames in os.walk(path):
        # Skip common non-source directories
        dirs[:] = [d for d in dirs if d not in ("node_modules", ".git", "dist", "build", "vendor")]
        for fname in filenames:
            if glob_pattern == "*.css" and fname.endswith(".css"):
                files.append(os.path.join(root, fname))
            elif glob_pattern == "*.scss" and fname.endswith(".scss"):
                files.append(os.path.join(root, fname))
            elif glob_pattern == "*" and (fname.endswith(".css") or fname.endswith(".scss")):
                files.append(os.path.join(root, fname))
    return sorted(files)


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
                lines.append(f"    Line {v['line']}: {v['property']}: {v['value']}{suggestion}")
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
        sys.exit(1)

    # Read and concatenate CSS
    all_css = ""
    for css_file in css_files:
        try:
            with open(css_file, "r", encoding="utf-8") as f:
                all_css += f"\n/* File: {css_file} */\n{f.read()}\n"
        except (IOError, UnicodeDecodeError) as e:
            print(f"Warning: Could not read {css_file}: {e}", file=sys.stderr)

    # Validate
    results = validate_css(all_css, tokens)

    # Generate report
    report = generate_report(results, args.tokens, args.input)

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


if __name__ == "__main__":
    main()
