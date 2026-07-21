#!/usr/bin/env python3
"""
Contrast Validator — check every declared foreground/background token pairing
against WCAG 2.1 contrast minimums, in both the light and dark theme.

Relative luminance and contrast ratios are computed from the WCAG definitions
using the standard library only; no color libraries are required.

Usage:
    python3 contrast_validator.py --input tokens.json
    python3 contrast_validator.py --input tokens.json --level AAA --format json
    python3 contrast_validator.py --input tokens.json --all-pairs
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

# WCAG 2.1 minimum contrast ratios by content class.
THRESHOLDS: Dict[str, Dict[str, float]] = {
    "AA": {"body": 4.5, "large": 3.0, "ui": 3.0, "decor": 1.5},
    "AAA": {"body": 7.0, "large": 4.5, "ui": 3.0, "decor": 1.5},
}
USAGE_LABEL = {
    "body": "body text (<18.66px regular)",
    "large": "large text (>=18.66px regular / >=14px bold)",
    "ui": "UI boundary, icon, or graphical object",
    "decor": "decorative rule (no WCAG minimum; 1.5:1 keeps it visible)",
}


def load_tokens(path: Path) -> Dict[str, Any]:
    """Load a design-token JSON file."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise SystemExit(f"error: token file not found: {path}")
    except json.JSONDecodeError as exc:
        raise SystemExit(f"error: {path} is not valid JSON ({exc.msg}, line {exc.lineno})")
    if "palette" not in data or "roles" not in data:
        raise SystemExit("error: token file must define both 'palette' and 'roles'")
    return data


def resolve_color(value: str, palette: Dict[str, Dict[str, str]]) -> str:
    """Resolve a role value ('ramp.step' or literal hex) to a hex string."""
    value = str(value).strip()
    if value.startswith("#"):
        return value.lower()
    if "." not in value:
        raise SystemExit(f"error: role value '{value}' must be 'ramp.step' or a hex color")
    ramp, step = value.split(".", 1)
    try:
        return str(palette[ramp][step]).lower()
    except KeyError:
        raise SystemExit(f"error: role references unknown palette entry '{value}'")


def hex_to_rgb(value: str) -> Tuple[int, int, int]:
    """Convert #rgb or #rrggbb to an (r, g, b) tuple of 0-255 integers."""
    body = value.lstrip("#")
    if len(body) == 3:
        body = "".join(c * 2 for c in body)
    if len(body) != 6:
        raise SystemExit(f"error: '{value}' is not a 3- or 6-digit hex color")
    try:
        return int(body[0:2], 16), int(body[2:4], 16), int(body[4:6], 16)
    except ValueError:
        raise SystemExit(f"error: '{value}' contains non-hex characters")


def relative_luminance(rgb: Tuple[int, int, int]) -> float:
    """Compute WCAG relative luminance for an sRGB triple."""
    channels: List[float] = []
    for raw in rgb:
        c = raw / 255.0
        channels.append(c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4)
    r, g, b = channels
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(fg_hex: str, bg_hex: str) -> float:
    """Compute the WCAG contrast ratio between two hex colors (1.0 - 21.0)."""
    lum_a = relative_luminance(hex_to_rgb(fg_hex))
    lum_b = relative_luminance(hex_to_rgb(bg_hex))
    lighter, darker = max(lum_a, lum_b), min(lum_a, lum_b)
    return round((lighter + 0.05) / (darker + 0.05), 2)


def declared_pairings(tokens: Dict[str, Any]) -> List[Dict[str, str]]:
    """Return the explicit pairings block, or a sane default if absent."""
    pairings = tokens.get("pairings")
    if pairings:
        return [dict(p) for p in pairings]
    return [{"fg": "text", "bg": "surface", "usage": "body"}]


def all_pairings(tokens: Dict[str, Any]) -> List[Dict[str, str]]:
    """Cross every non-surface role against every surface-like role."""
    roles = list(tokens["roles"].get("light", {}))
    backgrounds = [r for r in roles if "surface" in r]
    foregrounds = [r for r in roles if r not in backgrounds]
    usage = {"border": "decor", "accent": "large"}
    return [
        {"fg": fg, "bg": bg, "usage": usage.get(fg, "body")}
        for bg in backgrounds
        for fg in foregrounds
    ]


def evaluate(tokens: Dict[str, Any], pairings: List[Dict[str, str]],
             level: str) -> List[Dict[str, Any]]:
    """Score every pairing in every theme mode against the target level."""
    palette = tokens["palette"]
    results: List[Dict[str, Any]] = []
    for mode, role_map in tokens["roles"].items():
        for pair in pairings:
            fg_role, bg_role = pair.get("fg", ""), pair.get("bg", "")
            if fg_role not in role_map or bg_role not in role_map:
                results.append({
                    "mode": mode, "fg": fg_role, "bg": bg_role,
                    "usage": pair.get("usage", "body"), "ratio": None,
                    "required": None, "status": "missing",
                    "detail": f"role not defined in '{mode}' mode",
                })
                continue
            usage = pair.get("usage", "body")
            if usage not in THRESHOLDS[level]:
                raise SystemExit(f"error: unknown usage '{usage}' (use body, large, or ui)")
            fg_hex = resolve_color(role_map[fg_role], palette)
            bg_hex = resolve_color(role_map[bg_role], palette)
            ratio = contrast_ratio(fg_hex, bg_hex)
            required = THRESHOLDS[level][usage]
            results.append({
                "mode": mode, "fg": fg_role, "bg": bg_role, "usage": usage,
                "fg_hex": fg_hex, "bg_hex": bg_hex, "ratio": ratio,
                "required": required,
                "status": "pass" if ratio >= required else "fail",
                "detail": USAGE_LABEL[usage],
            })
    return results


def output(results: List[Dict[str, Any]], level: str, fmt: str) -> int:
    """Print results and return the number of failures."""
    failures = [r for r in results if r["status"] != "pass"]
    if fmt == "json":
        print(json.dumps({
            "level": level,
            "checked": len(results),
            "failed": len(failures),
            "gate": "fail" if failures else "pass",
            "results": results,
        }, indent=2))
        return len(failures)

    print(f"WCAG {level} contrast check - {len(results)} pairings\n")
    for mode in sorted({r["mode"] for r in results}):
        print(f"[{mode} mode]")
        for r in [x for x in results if x["mode"] == mode]:
            pair = f"{r['fg']} on {r['bg']}"
            if r["status"] == "missing":
                print(f"  MISS  {pair:<34} {r['detail']}")
                continue
            mark = "PASS" if r["status"] == "pass" else "FAIL"
            print(f"  {mark}  {pair:<34} {r['ratio']:>5}:1  "
                  f"(needs {r['required']}:1, {r['usage']})")
        print()
    if failures:
        print(f"GATE: FAIL - {len(failures)} pairing(s) below WCAG {level}")
        print("Fix by darkening the foreground ramp step or lightening the surface,")
        print("then re-run. A ramp step of 100 is usually worth ~1.3x of ratio.")
    else:
        print(f"GATE: PASS - all pairings meet WCAG {level}")
    return len(failures)


def main() -> None:
    """Parse arguments, validate contrast, and exit non-zero on failure."""
    parser = argparse.ArgumentParser(
        description="Validate design-token color pairings against WCAG contrast minimums.")
    parser.add_argument("--input", required=True,
                        help="path to the design-token JSON file")
    parser.add_argument("--level", choices=["AA", "AAA"], default="AA",
                        help="WCAG conformance level to enforce (default: AA)")
    parser.add_argument("--all-pairs", action="store_true",
                        help="ignore the 'pairings' block and cross-check every role")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                        help="output format (default: text)")
    parser.add_argument("--no-gate", action="store_true",
                        help="always exit 0, even when pairings fail (report-only mode)")
    args = parser.parse_args()

    try:
        tokens = load_tokens(Path(args.input))
        pairings = all_pairings(tokens) if args.all_pairs else declared_pairings(tokens)
        results = evaluate(tokens, pairings, args.level)
        failures = output(results, args.level, args.format)
    except SystemExit:
        raise
    except Exception as exc:  # noqa: BLE001 - surface an actionable message
        print(f"error: contrast validation failed ({type(exc).__name__}: {exc})",
              file=sys.stderr)
        sys.exit(1)
    if failures and not args.no_gate:
        sys.exit(2)  # 2 = gate failed (1 is reserved for tool errors)


if __name__ == "__main__":
    main()
