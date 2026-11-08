#!/usr/bin/env python3
"""
Contrast Pairs — check one colour pair against WCAG 2.x and find the closest passing colour.

Shared layer of color_contrast_checker.py (which adds batch input, grading and the report).
Run alone to get the nearest foreground and background that reach a target ratio, keeping
hue and stepping only toward black or white.

Usage:
    python contrast_pairs.py --fg "#777" --bg "#fff"
    python contrast_pairs.py --fg "#888" --bg "#000" --level AAA --size large --format json

Exit codes: 0 the pair passes, 1 it fails (suggestions printed), 2 a colour could not be parsed.
"""

import argparse
import importlib.util as _ilu
import json
import os
import sys


def _sibling(name):
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), name + ".py")
    spec = _ilu.spec_from_file_location(name, path)
    mod = _ilu.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


_cp = _sibling("color_parse")
parse_color = _cp.parse_color
rgb_to_hex = _cp.rgb_to_hex
contrast_ratio = _cp.contrast_ratio

# WCAG contrast minimums per level: normal_text, large_text, ui_components
WCAG_LEVELS = _cp._MODEL["levels"]


def _first_passing(color, other, target_ratio, toward_white):
    """Step `color` toward white or black; return the first step that reaches the target."""
    for step in range(256):
        if toward_white:
            factor = step / 255
            cand = tuple(max(0, min(255, round(c + (255 - c) * factor))) for c in color)
        else:
            factor = 1 - step / 255
            cand = tuple(max(0, min(255, round(c * factor))) for c in color)
        if contrast_ratio(cand, other) >= target_ratio:
            return cand
    return None


def suggest_compliant_color(
    fg: tuple[int, int, int],
    bg: tuple[int, int, int],
    target_ratio: float,
    adjust: str = "foreground",
) -> tuple[int, int, int]:
    """Closest compliant colour by lightness, adjusting the foreground or the background.

    Foreground tries darker first, background tries lighter first; the smaller RGB
    distance wins and the first direction wins a tie.
    """
    if adjust == "foreground":
        color, other, order, fallback = fg, bg, (False, True), (0, 0, 0)
    else:
        color, other, order, fallback = bg, fg, (True, False), (255, 255, 255)

    best, best_distance = None, float("inf")
    for toward_white in order:
        cand = _first_passing(color, other, target_ratio, toward_white)
        if cand is not None:
            dist = sum(abs(a - b) for a, b in zip(color, cand))
            if best is None or dist < best_distance:
                best, best_distance = cand, dist
    return best if best else fallback


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
        result["suggestions"] = {
            "adjust_foreground": {
                "hex": rgb_to_hex(*suggested_fg),
                "rgb": list(suggested_fg),
                "new_ratio": round(contrast_ratio(suggested_fg, bg), 2),
            },
            "adjust_background": {
                "hex": rgb_to_hex(*suggested_bg),
                "rgb": list(suggested_bg),
                "new_ratio": round(contrast_ratio(fg, suggested_bg), 2),
            },
        }

    return result


def check_pairs_from_json(data: dict | list, level: str, suggest_fixes: bool) -> list[dict]:
    """Process multiple color pairs from JSON input ({"pairs": [...]}, {"colors": [...]} or [...])."""
    if isinstance(data, dict):
        pairs = data.get("pairs", data.get("colors", []))
    elif isinstance(data, list):
        pairs = data
    else:
        raise ValueError("Input must be a JSON object with a 'pairs' list, or a list of pairs")
    if not isinstance(pairs, list) or not all(isinstance(p, dict) for p in pairs):
        raise ValueError("Each pair must be an object with foreground/background keys")

    results = []
    for i, pair in enumerate(pairs):
        fg = pair.get("foreground", pair.get("fg", pair.get("color", "")))
        bg = pair.get("background", pair.get("bg", "#ffffff"))
        text_size = pair.get("text_size", pair.get("size", "normal"))
        label = pair.get("label", pair.get("name", f"pair_{i+1}"))

        result = check_pair(fg, bg, level, text_size, suggest_fixes)
        result["label"] = label
        results.append(result)

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Contrast Pairs — one WCAG pair check with the closest passing colours",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --fg "#777" --bg "#fff"
  %(prog)s --fg "#888" --bg "#000" --level AAA --size large --format json
        """,
    )
    parser.add_argument("--foreground", "--fg", required=True, help="Foreground color (hex, rgb, hsl)")
    parser.add_argument("--background", "--bg", required=True, help="Background color (hex, rgb, hsl)")
    parser.add_argument("--level", "-l", choices=["AA", "AAA"], default="AA", help="WCAG level (default: AA)")
    parser.add_argument("--size", choices=["normal", "large", "ui"], default="normal",
                        help="Text size context (default: normal)")
    parser.add_argument("--format", "-f", choices=["json", "text"], default="text",
                        help="Output format (default: text)")
    args = parser.parse_args()

    result = check_pair(args.foreground, args.background, args.level, args.size, suggest_fixes=True)
    if "error" in result:
        print(f"Error: {result['error']}", file=sys.stderr)
        sys.exit(2)

    if args.format == "json":
        print(json.dumps(result, indent=2))
    else:
        status = "PASS" if result["passes"] else "FAIL"
        print(f"[{status}] {result['foreground']['hex']} on {result['background']['hex']}: "
              f"{result['contrast_ratio']}:1 (need {result['required_ratio']}:1, {args.level} {result['text_size']})")
        if "suggestions" in result:
            sug = result["suggestions"]
            print(f"  Closest passing FG: {sug['adjust_foreground']['hex']} ({sug['adjust_foreground']['new_ratio']}:1)")
            print(f"  Closest passing BG: {sug['adjust_background']['hex']} ({sug['adjust_background']['new_ratio']}:1)")
    sys.exit(0 if result["passes"] else 1)


if __name__ == "__main__":
    main()
