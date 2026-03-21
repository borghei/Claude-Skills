#!/usr/bin/env python3
"""Color Accessibility Checker - Validate brand color palettes against WCAG contrast standards.

Checks all foreground/background color combinations for WCAG AA and AAA
compliance, identifies failing pairs, and suggests accessible alternatives.

Usage:
    python color_accessibility_checker.py palette.json
    python color_accessibility_checker.py palette.json --json
    python color_accessibility_checker.py --fg "#2563EB" --bg "#FFFFFF"
"""

import argparse
import json
import math
import sys


def hex_to_rgb(hex_color):
    """Convert hex color to RGB tuple."""
    hex_color = hex_color.strip().lstrip("#")
    if len(hex_color) == 3:
        hex_color = "".join(c * 2 for c in hex_color)
    if len(hex_color) != 6:
        raise ValueError(f"Invalid hex color: #{hex_color}")
    return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(r, g, b):
    """Convert RGB to hex string."""
    return f"#{r:02X}{g:02X}{b:02X}"


def relative_luminance(r, g, b):
    """Calculate relative luminance per WCAG 2.1 definition."""
    def linearize(val):
        v = val / 255.0
        return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4

    return 0.2126 * linearize(r) + 0.7152 * linearize(g) + 0.0722 * linearize(b)


def contrast_ratio(color1_rgb, color2_rgb):
    """Calculate WCAG contrast ratio between two colors."""
    l1 = relative_luminance(*color1_rgb)
    l2 = relative_luminance(*color2_rgb)
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


def wcag_compliance(ratio):
    """Determine WCAG compliance levels."""
    return {
        "aa_normal": ratio >= 4.5,
        "aa_large": ratio >= 3.0,
        "aaa_normal": ratio >= 7.0,
        "aaa_large": ratio >= 4.5,
    }


def suggest_darker(r, g, b, target_ratio, bg_rgb):
    """Suggest a darker version of the color to meet contrast target."""
    for factor in range(100, 0, -1):
        f = factor / 100.0
        new_r = int(r * f)
        new_g = int(g * f)
        new_b = int(b * f)
        ratio = contrast_ratio((new_r, new_g, new_b), bg_rgb)
        if ratio >= target_ratio:
            return rgb_to_hex(new_r, new_g, new_b), round(ratio, 2)
    return None, None


def suggest_lighter(r, g, b, target_ratio, bg_rgb):
    """Suggest a lighter version of the color to meet contrast target."""
    for factor in range(100, 256):
        f = factor / 100.0
        new_r = min(255, int(r * f))
        new_g = min(255, int(g * f))
        new_b = min(255, int(b * f))
        ratio = contrast_ratio((new_r, new_g, new_b), bg_rgb)
        if ratio >= target_ratio:
            return rgb_to_hex(new_r, new_g, new_b), round(ratio, 2)
    return None, None


def check_pair(fg_hex, bg_hex):
    """Check a single foreground/background pair."""
    fg_rgb = hex_to_rgb(fg_hex)
    bg_rgb = hex_to_rgb(bg_hex)
    ratio = contrast_ratio(fg_rgb, bg_rgb)
    compliance = wcag_compliance(ratio)

    result = {
        "foreground": fg_hex.upper() if not fg_hex.startswith("#") else f"#{fg_hex.lstrip('#').upper()}",
        "background": bg_hex.upper() if not bg_hex.startswith("#") else f"#{bg_hex.lstrip('#').upper()}",
        "contrast_ratio": round(ratio, 2),
        "compliance": compliance,
    }

    # Add suggestions if failing AA normal
    if not compliance["aa_normal"]:
        darker, darker_ratio = suggest_darker(*fg_rgb, 4.5, bg_rgb)
        if darker:
            result["suggestion_darker"] = {"color": darker, "ratio": darker_ratio}

        lighter, lighter_ratio = suggest_lighter(*fg_rgb, 4.5, bg_rgb)
        if lighter:
            result["suggestion_lighter"] = {"color": lighter, "ratio": lighter_ratio}

    return result


def analyze_palette(palette_data):
    """Analyze all color combinations in a palette."""
    colors = []
    for item in palette_data:
        name = item.get("name", item.get("role", "unnamed"))
        hex_val = item.get("hex", item.get("color", ""))
        if hex_val:
            colors.append({"name": name, "hex": hex_val})

    results = []
    passing_pairs = 0
    failing_pairs = 0
    total_pairs = 0

    # Check every combination
    for i, fg in enumerate(colors):
        for j, bg in enumerate(colors):
            if i == j:
                continue
            total_pairs += 1
            pair_result = check_pair(fg["hex"], bg["hex"])
            pair_result["fg_name"] = fg["name"]
            pair_result["bg_name"] = bg["name"]

            if pair_result["compliance"]["aa_normal"]:
                passing_pairs += 1
            else:
                failing_pairs += 1

            results.append(pair_result)

    # Sort by contrast ratio (lowest first to highlight problems)
    results.sort(key=lambda x: x["contrast_ratio"])

    return {
        "summary": {
            "total_colors": len(colors),
            "total_pairs": total_pairs,
            "passing_aa_normal": passing_pairs,
            "failing_aa_normal": failing_pairs,
            "pass_rate": round(passing_pairs / max(total_pairs, 1) * 100, 1),
        },
        "pairs": results,
    }


def format_report(analysis):
    """Format human-readable report."""
    lines = []
    lines.append("=" * 70)
    lines.append("COLOR ACCESSIBILITY REPORT (WCAG 2.1)")
    lines.append("=" * 70)

    summary = analysis.get("summary")
    if summary:
        lines.append(f"Colors tested:    {summary['total_colors']}")
        lines.append(f"Pairs checked:    {summary['total_pairs']}")
        lines.append(f"Passing AA:       {summary['passing_aa_normal']} ({summary['pass_rate']:.0f}%)")
        lines.append(f"Failing AA:       {summary['failing_aa_normal']}")
        lines.append("")

    pairs = analysis.get("pairs", [analysis] if "contrast_ratio" in analysis else [])

    # Failing pairs
    failing = [p for p in pairs if not p["compliance"]["aa_normal"]]
    if failing:
        lines.append("--- FAILING PAIRS (below 4.5:1) ---")
        for p in failing:
            fg_label = p.get("fg_name", p["foreground"])
            bg_label = p.get("bg_name", p["background"])
            lines.append(f"  {fg_label} ({p['foreground']}) on {bg_label} ({p['background']})")
            lines.append(f"    Ratio: {p['contrast_ratio']}:1 | AA Normal: FAIL | AA Large: {'PASS' if p['compliance']['aa_large'] else 'FAIL'}")
            if "suggestion_darker" in p:
                s = p["suggestion_darker"]
                lines.append(f"    Suggestion (darker): {s['color']} (ratio: {s['ratio']}:1)")
            if "suggestion_lighter" in p:
                s = p["suggestion_lighter"]
                lines.append(f"    Suggestion (lighter): {s['color']} (ratio: {s['ratio']}:1)")
        lines.append("")

    # Passing pairs summary
    passing = [p for p in pairs if p["compliance"]["aa_normal"]]
    if passing:
        lines.append("--- PASSING PAIRS ---")
        for p in passing:
            fg_label = p.get("fg_name", p["foreground"])
            bg_label = p.get("bg_name", p["background"])
            aaa = "AAA" if p["compliance"]["aaa_normal"] else "AA"
            lines.append(f"  {fg_label} on {bg_label}: {p['contrast_ratio']}:1 [{aaa}]")
        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Validate brand color palettes against WCAG contrast standards"
    )
    parser.add_argument(
        "input",
        nargs="?",
        help="JSON file with color palette",
    )
    parser.add_argument(
        "--fg",
        help="Foreground color hex (e.g., #2563EB)",
    )
    parser.add_argument(
        "--bg",
        help="Background color hex (e.g., #FFFFFF)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output in JSON format",
    )
    args = parser.parse_args()

    if args.fg and args.bg:
        result = check_pair(args.fg, args.bg)
        if args.json_output:
            print(json.dumps(result, indent=2))
        else:
            print(format_report({"pairs": [result]}))
    elif args.input:
        try:
            with open(args.input, "r", encoding="utf-8") as f:
                data = json.load(f)
            palette = data if isinstance(data, list) else data.get("colors", data.get("palette", []))
        except FileNotFoundError:
            print(f"Error: File not found: {args.input}", file=sys.stderr)
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON: {e}", file=sys.stderr)
            sys.exit(1)

        analysis = analyze_palette(palette)
        if args.json_output:
            print(json.dumps(analysis, indent=2))
        else:
            print(format_report(analysis))
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
