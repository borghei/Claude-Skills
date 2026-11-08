#!/usr/bin/env python3
"""
Color Parse — parse CSS colours and compute WCAG 2.x relative luminance and contrast.

Shared layer of color_contrast_checker.py. Run alone to see how a colour string is read
(hex #RGB/#RRGGBB, rgb()/rgba(), hsl()/hsla(), a few named colours) and, with --against,
the contrast ratio between two colours. Alpha is ignored: pass the opaque colour you see.

Usage:
    python color_parse.py --color "#777"
    python color_parse.py --color "hsl(200, 50%, 40%)" --against "#fff" --format json

Exit codes: 0 parsed, 2 a colour could not be parsed.
"""

import argparse
import json
import os
import re
import sys

_DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "references", "wcag-contrast.json")
with open(_DATA, "r", encoding="utf-8") as _f:
    _MODEL = json.load(_f)

NAMED_COLORS = {k: tuple(v) for k, v in _MODEL["named_colors"].items()}


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
    lower = color.lower()
    if lower in NAMED_COLORS:
        return NAMED_COLORS[lower]

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


def relative_luminance(r: int, g: int, b: int) -> float:
    """Relative luminance per WCAG 2.x (sRGB linearisation, BT.709 coefficients)."""
    def linearize(channel: int) -> float:
        srgb = channel / 255
        if srgb <= 0.04045:
            return srgb / 12.92
        else:
            return ((srgb + 0.055) / 1.055) ** 2.4

    return 0.2126 * linearize(r) + 0.7152 * linearize(g) + 0.0722 * linearize(b)


def contrast_ratio(fg: tuple[int, int, int], bg: tuple[int, int, int]) -> float:
    """Calculate contrast ratio between two colors."""
    l1 = relative_luminance(*fg)
    l2 = relative_luminance(*bg)
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


def describe(color: str) -> dict:
    """Parsed view of one colour string."""
    rgb = parse_color(color)
    return {"input": color, "rgb": list(rgb), "hex": rgb_to_hex(*rgb),
            "relative_luminance": round(relative_luminance(*rgb), 4)}


def main():
    parser = argparse.ArgumentParser(
        description="Color Parse — read a CSS colour and its WCAG luminance; optional contrast ratio",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --color "#777"
  %(prog)s --color "rgb(51,51,51)" --against "hsl(0,0%%,100%%)" --format json
        """,
    )
    parser.add_argument("--color", "-c", required=True, help="Colour to parse (hex, rgb, hsl, named)")
    parser.add_argument("--against", "-a", help="Second colour; adds the contrast ratio between the two")
    parser.add_argument("--format", "-f", choices=["json", "text"], default="text",
                        help="Output format (default: text)")
    args = parser.parse_args()

    try:
        result = {"color": describe(args.color)}
        if args.against:
            result["against"] = describe(args.against)
            ratio = contrast_ratio(tuple(result["color"]["rgb"]), tuple(result["against"]["rgb"]))
            result["contrast_ratio"] = round(ratio, 2)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(2)

    if args.format == "json":
        print(json.dumps(result, indent=2))
    else:
        for key in ("color", "against"):
            if key in result:
                c = result[key]
                print(f"{c['input']}: {c['hex']} rgb{tuple(c['rgb'])} luminance {c['relative_luminance']}")
        if "contrast_ratio" in result:
            print(f"Contrast ratio: {result['contrast_ratio']}:1")


if __name__ == "__main__":
    main()
