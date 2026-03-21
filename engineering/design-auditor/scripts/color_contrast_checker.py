#!/usr/bin/env python3
"""
Color Contrast Checker — WCAG 2.1 color contrast validation.

Checks color contrast ratios against WCAG AA and AAA standards.
Supports hex, rgb, and hsl color formats. Suggests closest compliant
color alternatives when a pair fails.

Usage:
    python color_contrast_checker.py --foreground "#333" --background "#fff"
    python color_contrast_checker.py --input color_pairs.json --level AAA
    python color_contrast_checker.py --input colors.json --level AA --suggest-fixes
    python color_contrast_checker.py --foreground "rgb(51,51,51)" --background "hsl(0,0%,100%)"
"""

import argparse
import json
import math
import re
import sys
from datetime import datetime
from typing import Any

# WCAG contrast ratio requirements
WCAG_LEVELS = {
    "AA": {
        "normal_text": 4.5,
        "large_text": 3.0,
        "ui_components": 3.0,
    },
    "AAA": {
        "normal_text": 7.0,
        "large_text": 4.5,
        "ui_components": 3.0,  # AAA has no higher requirement for UI components
    },
}

# Large text: >= 18pt (24px) or >= 14pt (18.66px) bold
LARGE_TEXT_MIN_PX = 24
LARGE_TEXT_BOLD_MIN_PX = 18.66


# ── Color Parsing ────────────────────────────────────────────────────────────

def parse_hex(color: str) -> tuple[int, int, int]:
    """Parse hex color (#RGB, #RRGGBB) to (R, G, B)."""
    color = color.strip().lstrip("#")
    if len(color) == 3:
        color = "".join(c * 2 for c in color)
    if len(color) != 6:
        raise ValueError(f"Invalid hex color: #{color}")
    try:
        r = int(color[0:2], 16)
        g = int(color[2:4], 16)
        b = int(color[4:6], 16)
    except ValueError:
        raise ValueError(f"Invalid hex color: #{color}")
    return (r, g, b)


def parse_rgb(color: str) -> tuple[int, int, int]:
    """Parse rgb(R, G, B) or rgb(R G B) to (R, G, B)."""
    match = re.match(
        r"rgba?\s*\(\s*(\d{1,3})\s*[,\s]\s*(\d{1,3})\s*[,\s]\s*(\d{1,3})",
        color.strip(),
        re.IGNORECASE,
    )
    if not match:
        raise ValueError(f"Invalid rgb color: {color}")
    r, g, b = int(match.group(1)), int(match.group(2)), int(match.group(3))
    for val, name in [(r, "R"), (g, "G"), (b, "B")]:
        if not 0 <= val <= 255:
            raise ValueError(f"{name} value {val} out of range (0-255)")
    return (r, g, b)


def hsl_to_rgb(h: float, s: float, l: float) -> tuple[int, int, int]:
    """Convert HSL values to RGB. h in [0,360], s and l in [0,1]."""
    h = h % 360
    c = (1 - abs(2 * l - 1)) * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = l - c / 2

    if h < 60:
        r1, g1, b1 = c, x, 0
    elif h < 120:
        r1, g1, b1 = x, c, 0
    elif h < 180:
        r1, g1, b1 = 0, c, x
    elif h < 240:
        r1, g1, b1 = 0, x, c
    elif h < 300:
        r1, g1, b1 = x, 0, c
    else:
        r1, g1, b1 = c, 0, x

    r = round((r1 + m) * 255)
    g = round((g1 + m) * 255)
    b = round((b1 + m) * 255)
    return (max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)))


def parse_hsl(color: str) -> tuple[int, int, int]:
    """Parse hsl(H, S%, L%) to (R, G, B)."""
    match = re.match(
        r"hsla?\s*\(\s*([\d.]+)\s*[,\s]\s*([\d.]+)%?\s*[,\s]\s*([\d.]+)%?",
        color.strip(),
        re.IGNORECASE,
    )
    if not match:
        raise ValueError(f"Invalid hsl color: {color}")
    h = float(match.group(1))
    s = float(match.group(2)) / 100
    l_val = float(match.group(3)) / 100
    return hsl_to_rgb(h, s, l_val)


def parse_color(color: str) -> tuple[int, int, int]:
    """Parse any supported color format to (R, G, B)."""
    color = color.strip()

    # Named colors (common ones)
    named_colors = {
        "black": (0, 0, 0),
        "white": (255, 255, 255),
        "red": (255, 0, 0),
        "green": (0, 128, 0),
        "blue": (0, 0, 255),
        "yellow": (255, 255, 0),
        "cyan": (0, 255, 255),
        "magenta": (255, 0, 255),
        "gray": (128, 128, 128),
        "grey": (128, 128, 128),
        "orange": (255, 165, 0),
        "purple": (128, 0, 128),
        "transparent": (0, 0, 0),
    }

    lower = color.lower()
    if lower in named_colors:
        return named_colors[lower]

    if color.startswith("#") or re.match(r"^(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})$", color):
        return parse_hex(color)
    elif lower.startswith("rgb"):
        return parse_rgb(color)
    elif lower.startswith("hsl"):
        return parse_hsl(color)
    else:
        # Try as hex without #
        try:
            return parse_hex(color)
        except ValueError:
            raise ValueError(
                f"Unsupported color format: '{color}'. "
                "Use hex (#RGB/#RRGGBB), rgb(R,G,B), or hsl(H,S%,L%)"
            )


def rgb_to_hex(r: int, g: int, b: int) -> str:
    """Convert RGB to hex string."""
    return f"#{r:02x}{g:02x}{b:02x}"


# ── Luminance & Contrast ────────────────────────────────────────────────────

def relative_luminance(r: int, g: int, b: int) -> float:
    """Calculate relative luminance per WCAG 2.1 definition.

    Uses the sRGB to linear conversion and ITU-R BT.709 coefficients.
    """
    def linearize(channel: int) -> float:
        srgb = channel / 255
        if srgb <= 0.04045:
            return srgb / 12.92
        else:
            return ((srgb + 0.055) / 1.055) ** 2.4

    r_lin = linearize(r)
    g_lin = linearize(g)
    b_lin = linearize(b)

    return 0.2126 * r_lin + 0.7152 * g_lin + 0.0722 * b_lin


def contrast_ratio(fg: tuple[int, int, int], bg: tuple[int, int, int]) -> float:
    """Calculate contrast ratio between two colors."""
    l1 = relative_luminance(*fg)
    l2 = relative_luminance(*bg)
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


# ── Fix Suggestion ───────────────────────────────────────────────────────────

def suggest_compliant_color(
    fg: tuple[int, int, int],
    bg: tuple[int, int, int],
    target_ratio: float,
    adjust: str = "foreground",
) -> tuple[int, int, int]:
    """Find the closest compliant color by adjusting lightness.

    Adjusts the specified color (foreground or background) to meet the
    target contrast ratio while preserving hue and saturation as much
    as possible.
    """
    bg_lum = relative_luminance(*bg)
    fg_lum = relative_luminance(*fg)

    if adjust == "foreground":
        # Determine if we need to go lighter or darker
        # Try darkening first (more common for text)
        best = None
        best_distance = float("inf")

        for step in range(256):
            # Try darker
            factor = 1 - step / 255
            r = max(0, min(255, round(fg[0] * factor)))
            g = max(0, min(255, round(fg[1] * factor)))
            b = max(0, min(255, round(fg[2] * factor)))
            ratio = contrast_ratio((r, g, b), bg)
            if ratio >= target_ratio:
                dist = abs(fg[0] - r) + abs(fg[1] - g) + abs(fg[2] - b)
                if dist < best_distance:
                    best = (r, g, b)
                    best_distance = dist
                break

        # Try lighter
        for step in range(256):
            factor = step / 255
            r = max(0, min(255, round(fg[0] + (255 - fg[0]) * factor)))
            g = max(0, min(255, round(fg[1] + (255 - fg[1]) * factor)))
            b = max(0, min(255, round(fg[2] + (255 - fg[2]) * factor)))
            ratio = contrast_ratio((r, g, b), bg)
            if ratio >= target_ratio:
                dist = abs(fg[0] - r) + abs(fg[1] - g) + abs(fg[2] - b)
                if best is None or dist < best_distance:
                    best = (r, g, b)
                    best_distance = dist
                break

        return best if best else (0, 0, 0)
    else:
        # Adjust background
        best = None
        best_distance = float("inf")

        for step in range(256):
            factor = step / 255
            r = max(0, min(255, round(bg[0] + (255 - bg[0]) * factor)))
            g = max(0, min(255, round(bg[1] + (255 - bg[1]) * factor)))
            b = max(0, min(255, round(bg[2] + (255 - bg[2]) * factor)))
            ratio = contrast_ratio(fg, (r, g, b))
            if ratio >= target_ratio:
                dist = abs(bg[0] - r) + abs(bg[1] - g) + abs(bg[2] - b)
                if dist < best_distance:
                    best = (r, g, b)
                    best_distance = dist
                break

        for step in range(256):
            factor = 1 - step / 255
            r = max(0, min(255, round(bg[0] * factor)))
            g = max(0, min(255, round(bg[1] * factor)))
            b = max(0, min(255, round(bg[2] * factor)))
            ratio = contrast_ratio(fg, (r, g, b))
            if ratio >= target_ratio:
                dist = abs(bg[0] - r) + abs(bg[1] - g) + abs(bg[2] - b)
                if best is None or dist < best_distance:
                    best = (r, g, b)
                    best_distance = dist
                break

        return best if best else (255, 255, 255)


def check_pair(
    fg_str: str,
    bg_str: str,
    level: str = "AA",
    text_size: str = "normal",
    suggest_fixes: bool = False,
) -> dict:
    """Check a single color pair against WCAG requirements."""
    try:
        fg = parse_color(fg_str)
    except ValueError as e:
        return {"error": f"Foreground: {e}"}

    try:
        bg = parse_color(bg_str)
    except ValueError as e:
        return {"error": f"Background: {e}"}

    ratio = contrast_ratio(fg, bg)
    requirements = WCAG_LEVELS.get(level, WCAG_LEVELS["AA"])

    if text_size == "large":
        required = requirements["large_text"]
        text_label = "large text"
    elif text_size == "ui":
        required = requirements["ui_components"]
        text_label = "UI components"
    else:
        required = requirements["normal_text"]
        text_label = "normal text"

    passes = ratio >= required

    result = {
        "foreground": {"input": fg_str, "rgb": list(fg), "hex": rgb_to_hex(*fg)},
        "background": {"input": bg_str, "rgb": list(bg), "hex": rgb_to_hex(*bg)},
        "contrast_ratio": round(ratio, 2),
        "required_ratio": required,
        "level": level,
        "text_size": text_label,
        "passes": passes,
    }

    # Check all levels for comprehensive reporting
    result["wcag_aa_normal"] = ratio >= 4.5
    result["wcag_aa_large"] = ratio >= 3.0
    result["wcag_aaa_normal"] = ratio >= 7.0
    result["wcag_aaa_large"] = ratio >= 4.5

    if suggest_fixes and not passes:
        suggested_fg = suggest_compliant_color(fg, bg, required, adjust="foreground")
        suggested_bg = suggest_compliant_color(fg, bg, required, adjust="background")
        new_fg_ratio = contrast_ratio(suggested_fg, bg)
        new_bg_ratio = contrast_ratio(fg, suggested_bg)

        result["suggestions"] = {
            "adjust_foreground": {
                "hex": rgb_to_hex(*suggested_fg),
                "rgb": list(suggested_fg),
                "new_ratio": round(new_fg_ratio, 2),
            },
            "adjust_background": {
                "hex": rgb_to_hex(*suggested_bg),
                "rgb": list(suggested_bg),
                "new_ratio": round(new_bg_ratio, 2),
            },
        }

    return result


def check_pairs_from_json(data: dict | list, level: str, suggest_fixes: bool) -> list[dict]:
    """Process multiple color pairs from JSON input."""
    results = []

    # Support both array and object with 'pairs' key
    if isinstance(data, dict):
        pairs = data.get("pairs", data.get("colors", []))
    elif isinstance(data, list):
        pairs = data
    else:
        return [{"error": "Invalid input format"}]

    for i, pair in enumerate(pairs):
        fg = pair.get("foreground", pair.get("fg", pair.get("color", "")))
        bg = pair.get("background", pair.get("bg", "#ffffff"))
        text_size = pair.get("text_size", pair.get("size", "normal"))
        label = pair.get("label", pair.get("name", f"pair_{i+1}"))

        result = check_pair(fg, bg, level, text_size, suggest_fixes)
        result["label"] = label
        results.append(result)

    return results


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
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON: {e}", file=sys.stderr)
            sys.exit(1)

        results = check_pairs_from_json(data, args.level, args.suggest_fixes)

    elif args.foreground and args.background:
        # Single pair mode
        result = check_pair(args.foreground, args.background, args.level, args.size, args.suggest_fixes)
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


if __name__ == "__main__":
    main()
