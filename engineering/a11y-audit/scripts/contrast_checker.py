#!/usr/bin/env python3
"""
Contrast Checker - Check color contrast ratios against WCAG AA/AAA standards.

Calculates relative luminance contrast ratios between foreground and background
colors and validates against WCAG 2.1 thresholds for normal and large text.

Author: Claude Skills Engineering Team
License: MIT
"""

import argparse
import json
import math
import re
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Tuple, Optional, Dict


@dataclass
class ContrastResult:
    """Result of a contrast check."""
    foreground: str
    background: str
    ratio: float
    aa_normal: bool  # 4.5:1
    aa_large: bool   # 3:1
    aaa_normal: bool  # 7:1
    aaa_large: bool   # 4.5:1
    suggestion: Optional[str] = None


# Named CSS colors (common subset)
CSS_COLORS = {
    "black": "#000000", "white": "#ffffff", "red": "#ff0000",
    "green": "#008000", "blue": "#0000ff", "yellow": "#ffff00",
    "cyan": "#00ffff", "magenta": "#ff00ff", "gray": "#808080",
    "grey": "#808080", "silver": "#c0c0c0", "maroon": "#800000",
    "olive": "#808000", "navy": "#000080", "purple": "#800080",
    "teal": "#008080", "aqua": "#00ffff", "orange": "#ffa500",
    "pink": "#ffc0cb", "brown": "#a52a2a", "coral": "#ff7f50",
    "crimson": "#dc143c", "darkblue": "#00008b", "darkgreen": "#006400",
    "darkred": "#8b0000", "gold": "#ffd700", "indigo": "#4b0082",
    "ivory": "#fffff0", "khaki": "#f0e68c", "lavender": "#e6e6fa",
    "lime": "#00ff00", "linen": "#faf0e6", "mintcream": "#f5fffa",
    "salmon": "#fa8072", "tomato": "#ff6347", "turquoise": "#40e0d0",
    "violet": "#ee82ee", "wheat": "#f5deb3",
}


def parse_color(color_str: str) -> Optional[Tuple[int, int, int]]:
    """Parse a color string into RGB tuple."""
    color_str = color_str.strip().lower()

    # Named colors
    if color_str in CSS_COLORS:
        color_str = CSS_COLORS[color_str]

    # Hex: #rgb or #rrggbb
    if color_str.startswith("#"):
        hex_val = color_str[1:]
        if len(hex_val) == 3:
            hex_val = "".join(c * 2 for c in hex_val)
        if len(hex_val) == 6:
            try:
                r = int(hex_val[0:2], 16)
                g = int(hex_val[2:4], 16)
                b = int(hex_val[4:6], 16)
                return (r, g, b)
            except ValueError:
                return None

    # rgb(r, g, b) or rgba(r, g, b, a)
    rgb_match = re.match(r'rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)', color_str)
    if rgb_match:
        return (int(rgb_match.group(1)), int(rgb_match.group(2)), int(rgb_match.group(3)))

    return None


def relative_luminance(r: int, g: int, b: int) -> float:
    """Calculate relative luminance per WCAG 2.1 definition."""
    def linearize(val: int) -> float:
        srgb = val / 255.0
        if srgb <= 0.04045:
            return srgb / 12.92
        return ((srgb + 0.055) / 1.055) ** 2.4

    r_lin = linearize(r)
    g_lin = linearize(g)
    b_lin = linearize(b)
    return 0.2126 * r_lin + 0.7152 * g_lin + 0.0722 * b_lin


def contrast_ratio(fg: Tuple[int, int, int], bg: Tuple[int, int, int]) -> float:
    """Calculate contrast ratio between two colors."""
    l1 = relative_luminance(*fg)
    l2 = relative_luminance(*bg)
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


def suggest_compliant_color(fg: Tuple[int, int, int], bg: Tuple[int, int, int],
                            target_ratio: float = 4.5) -> Optional[str]:
    """Suggest a modified foreground color that meets the target ratio."""
    bg_lum = relative_luminance(*bg)
    current_ratio = contrast_ratio(fg, bg)

    if current_ratio >= target_ratio:
        return None

    # Try darkening or lightening the foreground
    best_color = None
    best_diff = float("inf")

    for step in range(256):
        # Try darker
        factor = 1.0 - (step / 255.0)
        dr = max(0, min(255, int(fg[0] * factor)))
        dg = max(0, min(255, int(fg[1] * factor)))
        db = max(0, min(255, int(fg[2] * factor)))
        dark_ratio = contrast_ratio((dr, dg, db), bg)
        if dark_ratio >= target_ratio:
            diff = sum(abs(a - b) for a, b in zip(fg, (dr, dg, db)))
            if diff < best_diff:
                best_diff = diff
                best_color = f"#{dr:02x}{dg:02x}{db:02x}"
            break

    for step in range(256):
        # Try lighter
        factor = step / 255.0
        lr = max(0, min(255, fg[0] + int((255 - fg[0]) * factor)))
        lg = max(0, min(255, fg[1] + int((255 - fg[1]) * factor)))
        lb = max(0, min(255, fg[2] + int((255 - fg[2]) * factor)))
        light_ratio = contrast_ratio((lr, lg, lb), bg)
        if light_ratio >= target_ratio:
            diff = sum(abs(a - b) for a, b in zip(fg, (lr, lg, lb)))
            if diff < best_diff:
                best_diff = diff
                best_color = f"#{lr:02x}{lg:02x}{lb:02x}"
            break

    return best_color


def check_contrast(fg_str: str, bg_str: str) -> Optional[ContrastResult]:
    """Check contrast between two colors."""
    fg = parse_color(fg_str)
    bg = parse_color(bg_str)

    if fg is None or bg is None:
        return None

    ratio = contrast_ratio(fg, bg)
    ratio_rounded = round(ratio, 2)

    suggestion = None
    if ratio < 4.5:
        suggestion = suggest_compliant_color(fg, bg, 4.5)

    return ContrastResult(
        foreground=fg_str,
        background=bg_str,
        ratio=ratio_rounded,
        aa_normal=ratio >= 4.5,
        aa_large=ratio >= 3.0,
        aaa_normal=ratio >= 7.0,
        aaa_large=ratio >= 4.5,
        suggestion=suggestion,
    )


def extract_css_colors(css_content: str) -> List[Tuple[str, str, str]]:
    """Extract color/background-color pairs from CSS."""
    pairs = []
    # Parse CSS rules (simplified)
    rule_pattern = re.compile(r'([^{]+)\{([^}]+)\}')

    for match in rule_pattern.finditer(css_content):
        selector = match.group(1).strip()
        body = match.group(2)

        color = None
        bg_color = None

        # Extract color property
        color_match = re.search(r'(?<![a-z-])color\s*:\s*([^;]+)', body)
        if color_match:
            color = color_match.group(1).strip()

        # Extract background-color
        bg_match = re.search(r'background-color\s*:\s*([^;]+)', body)
        if bg_match:
            bg_color = bg_match.group(1).strip()

        # Also check shorthand background
        if not bg_color:
            bg_short = re.search(r'background\s*:\s*([^;]+)', body)
            if bg_short:
                val = bg_short.group(1).strip()
                # Try to extract a color from shorthand
                if parse_color(val.split()[0]) is not None:
                    bg_color = val.split()[0]

        if color and bg_color:
            pairs.append((selector, color, bg_color))

    return pairs


def format_text_single(result: ContrastResult) -> str:
    """Format a single contrast result as text."""
    lines = []
    lines.append("=" * 50)
    lines.append("COLOR CONTRAST CHECK")
    lines.append("=" * 50)
    lines.append(f"Foreground: {result.foreground}")
    lines.append(f"Background: {result.background}")
    lines.append(f"Contrast Ratio: {result.ratio}:1")
    lines.append("")
    lines.append("WCAG Compliance:")
    lines.append(f"  AA Normal Text (4.5:1): {'PASS' if result.aa_normal else 'FAIL'}")
    lines.append(f"  AA Large Text  (3.0:1): {'PASS' if result.aa_large else 'FAIL'}")
    lines.append(f"  AAA Normal Text (7.0:1): {'PASS' if result.aaa_normal else 'FAIL'}")
    lines.append(f"  AAA Large Text  (4.5:1): {'PASS' if result.aaa_large else 'FAIL'}")

    if result.suggestion:
        lines.append(f"\nSuggested foreground for AA compliance: {result.suggestion}")

    lines.append("=" * 50)
    return "\n".join(lines)


def format_text_css(results: List[Tuple[str, ContrastResult]]) -> str:
    """Format CSS contrast results as text."""
    lines = []
    lines.append("=" * 60)
    lines.append("CSS COLOR CONTRAST REPORT")
    lines.append("=" * 60)

    failures = [(s, r) for s, r in results if not r.aa_normal]
    passes = [(s, r) for s, r in results if r.aa_normal]

    lines.append(f"\nColor pairs found: {len(results)}")
    lines.append(f"AA failures: {len(failures)}")
    lines.append(f"AA passes: {len(passes)}")

    if failures:
        lines.append("\n[FAILURES]")
        for selector, r in failures:
            lines.append(f"  {selector}")
            lines.append(f"    {r.foreground} on {r.background} = {r.ratio}:1")
            if r.suggestion:
                lines.append(f"    Suggested fix: {r.suggestion}")
            lines.append("")

    if passes:
        lines.append("\n[PASSES]")
        for selector, r in passes:
            lines.append(f"  {selector}: {r.ratio}:1")

    lines.append("=" * 60)
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Check color contrast ratios against WCAG AA/AAA standards."
    )
    parser.add_argument("--foreground", "--fg", help="Foreground color (hex, rgb, or name)")
    parser.add_argument("--background", "--bg", help="Background color (hex, rgb, or name)")
    parser.add_argument("--css", help="Path to CSS file to analyze")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format")
    args = parser.parse_args()

    if args.css:
        path = Path(args.css)
        if not path.exists():
            print(f"Error: File not found: {args.css}", file=sys.stderr)
            sys.exit(2)

        content = path.read_text()
        pairs = extract_css_colors(content)

        results = []
        for selector, fg, bg in pairs:
            result = check_contrast(fg, bg)
            if result:
                results.append((selector, result))

        if args.format == "json":
            data = []
            for selector, r in results:
                entry = asdict(r)
                entry["selector"] = selector
                data.append(entry)
            print(json.dumps({"pairs": data, "total": len(data),
                             "failures": sum(1 for _, r in results if not r.aa_normal)}, indent=2))
        else:
            print(format_text_css(results))

        if any(not r.aa_normal for _, r in results):
            sys.exit(1)

    elif args.foreground and args.background:
        result = check_contrast(args.foreground, args.background)
        if result is None:
            print("Error: Could not parse one or both colors.", file=sys.stderr)
            sys.exit(2)

        if args.format == "json":
            print(json.dumps(asdict(result), indent=2))
        else:
            print(format_text_single(result))

        if not result.aa_normal:
            sys.exit(1)
    else:
        parser.error("Provide either --foreground and --background, or --css")


if __name__ == "__main__":
    main()
