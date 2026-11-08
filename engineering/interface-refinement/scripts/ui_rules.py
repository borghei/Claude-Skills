#!/usr/bin/env python3
"""Rule catalog, colour maths and finding builder for the interface detector.

Shared by css_checks.py, class_checks.py, markup_checks.py and
ui_slop_detector.py. Run on its own it lists the rule catalog or computes the
WCAG contrast of one colour pair.

Usage:
  python3 ui_rules.py --list --format text
  python3 ui_rules.py --list --scope motion --format json
  python3 ui_rules.py --contrast "#9ca3af" "#ffffff"

Exit codes: 0 ok (contrast >= 4.5 when --contrast is used), 1 contrast below
4.5:1, 2 bad input (unreadable catalog, unparseable colour).
"""

from __future__ import annotations

import argparse
import colorsys
import json
import math
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Dict, List, Optional, Tuple

CATALOG_PATH = Path(__file__).resolve().parent.parent / "references" / "detector-rules.json"
REQUIRED_FIELDS = ("id", "name", "family", "severity", "scope", "command", "why", "fix")
SEVERITY_RANK = {"high": 3, "medium": 2, "advisory": 1}

Color = Tuple[float, float, float, float]

NAMED = {
    "white": "#ffffff", "black": "#000000", "gray": "#808080", "grey": "#808080",
    "silver": "#c0c0c0", "purple": "#800080", "violet": "#ee82ee", "indigo": "#4b0082",
    "blue": "#0000ff", "cyan": "#00ffff", "aqua": "#00ffff", "teal": "#008080",
    "fuchsia": "#ff00ff", "magenta": "#ff00ff", "pink": "#ffc0cb", "red": "#ff0000",
    "orange": "#ffa500", "yellow": "#ffff00", "green": "#008000", "beige": "#f5f5dc",
    "ivory": "#fffff0", "linen": "#faf0e6", "oldlace": "#fdf5e6", "cornsilk": "#fff8dc",
    "navy": "#000080", "lavender": "#e6e6fa", "whitesmoke": "#f5f5f5", "gainsboro": "#dcdcdc",
}

# Approximate hue of each utility-class colour family (degrees).
TW_HUES = {
    "red": 0, "orange": 25, "amber": 38, "yellow": 48, "lime": 84, "green": 142,
    "emerald": 160, "teal": 173, "cyan": 189, "sky": 199, "blue": 217, "indigo": 239,
    "violet": 258, "purple": 271, "fuchsia": 292, "pink": 330, "rose": 350,
}
TW_NEUTRALS = ("slate", "gray", "zinc", "neutral", "stone")
# Light-to-mid neutral steps that fail 4.5:1 on white (values are the published defaults).
TW_FAINT = {
    "slate": {200: "#e2e8f0", 300: "#cbd5e1", 400: "#94a3b8"},
    "gray": {200: "#e5e7eb", 300: "#d1d5db", 400: "#9ca3af"},
    "zinc": {200: "#e4e4e7", 300: "#d4d4d8", 400: "#a1a1aa"},
    "neutral": {200: "#e5e5e5", 300: "#d4d4d4", 400: "#a3a3a3"},
    "stone": {200: "#e7e5e4", 300: "#d6d3d1", 400: "#a8a29e"},
}

HEX_RE = re.compile(r"#(?:[0-9a-fA-F]{3,4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})\b")
FUNC_RE = re.compile(r"\b(rgba?|hsla?|oklch)\(([^)]*)\)", re.I)
WORD_RE = re.compile(r"(?<![\w-])(" + "|".join(sorted(NAMED, key=len, reverse=True)) + r")(?![\w-])", re.I)
OPAQUE_RE = re.compile(r"\b(var|url|env)\((?:[^()]|\([^()]*\))*\)", re.I)


def _num(token: str, scale: float = 1.0) -> float:
    token = token.strip()
    if token.endswith("%"):
        return float(token[:-1]) / 100.0 * scale
    return float(token)


def _hex(value: str) -> Color:
    h = value.lstrip("#")
    if len(h) in (3, 4):
        h = "".join(ch * 2 for ch in h)
    alpha = int(h[6:8], 16) / 255.0 if len(h) == 8 else 1.0
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), alpha)


def _oklch(l_: float, c: float, h: float) -> Tuple[float, float, float]:
    a, b = c * math.cos(math.radians(h)), c * math.sin(math.radians(h))
    lp = (l_ + 0.3963377774 * a + 0.2158037573 * b) ** 3
    mp = (l_ - 0.1055613458 * a - 0.0638541728 * b) ** 3
    sp = (l_ - 0.0894841775 * a - 1.2914855480 * b) ** 3
    lin = (4.0767416621 * lp - 3.3077115913 * mp + 0.2309699292 * sp,
           -1.2684380046 * lp + 2.6097574011 * mp - 0.3413193965 * sp,
           -0.0041960863 * lp - 0.7034186147 * mp + 1.7076147010 * sp)
    out = []
    for v in lin:
        v = min(1.0, max(0.0, v))
        v = 12.92 * v if v <= 0.0031308 else 1.055 * v ** (1 / 2.4) - 0.055
        out.append(v * 255)
    return out[0], out[1], out[2]


def parse_color(text: str) -> Optional[Color]:
    """Parse one CSS colour (hex, rgb/rgba, hsl/hsla, oklch, common names)."""
    text = (text or "").strip().lower()
    if not text or text in ("transparent", "currentcolor", "inherit", "initial", "none"):
        return None
    try:
        if HEX_RE.fullmatch(text):
            return _hex(text)
        if text in NAMED:
            return _hex(NAMED[text])
        m = FUNC_RE.fullmatch(text)
        if not m:
            return None
        parts = [("0" if p == "none" else p) for p in re.split(r"[\s,/]+", m.group(2).strip()) if p]
        kind = m.group(1).lower()
        alpha = _num(parts[3]) if len(parts) > 3 else 1.0
        if kind.startswith("rgb"):
            r, g, b = (_num(p, 255) for p in parts[:3])
        elif kind.startswith("hsl"):
            hue = float(parts[0].replace("deg", ""))
            sat = _num(parts[1]) if "%" in parts[1] else float(parts[1]) / 100
            light = _num(parts[2]) if "%" in parts[2] else float(parts[2]) / 100
            r, g, b = (v * 255 for v in colorsys.hls_to_rgb(hue / 360.0, light, sat))
        else:
            r, g, b = _oklch(_num(parts[0]), _num(parts[1], 0.4), float(parts[2].replace("deg", "")))
        clamp = lambda v, hi: min(hi, max(0.0, v))  # noqa: E731
        return (clamp(r, 255), clamp(g, 255), clamp(b, 255), clamp(alpha, 1.0))
    except (ValueError, IndexError):
        return None


def find_colors(text: str) -> List[Color]:
    """Every colour literal in a declaration value, in source order."""
    text = OPAQUE_RE.sub(" ", text or "")
    spans = []
    for regex in (HEX_RE, FUNC_RE, WORD_RE):
        spans += [(m.start(), m.group(0)) for m in regex.finditer(text or "")]
    out = [parse_color(token) for _, token in sorted(spans)]
    return [c for c in out if c is not None]


def hsl(color: Color) -> Tuple[float, float, float]:
    """Hue in degrees, saturation 0-1, lightness 0-1."""
    h, l_, s = colorsys.rgb_to_hls(color[0] / 255, color[1] / 255, color[2] / 255)
    return h * 360.0, s, l_


def bezier_ys(value: str) -> List[float]:
    """The two y control points of the first cubic-bezier(), skipping non-numeric (var(), calc()) ones."""
    m = re.search(r"cubic-bezier\(([^()]*(?:\([^()]*\)[^()]*)*)\)", value or "", re.I)
    out = []
    for token in (m.group(1).split(",")[1::2] if m else []):
        try:
            out.append(float(token))
        except ValueError:
            continue
    return out


def chroma(color: Color) -> float:
    return (max(color[:3]) - min(color[:3])) / 255.0


def is_neutral(color: Color) -> bool:
    return chroma(color) < 0.08


def luminance(color: Color) -> float:
    def channel(v: float) -> float:
        v /= 255.0
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = (channel(v) for v in color[:3])
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def over(top: Color, under: Color) -> Color:
    """Composite a translucent colour over an opaque one (what the browser paints)."""
    a = top[3]
    return (top[0] * a + under[0] * (1 - a), top[1] * a + under[1] * (1 - a), top[2] * a + under[2] * (1 - a), 1.0)


def contrast(fg: Color, bg: Color) -> float:
    hi, lo = sorted((luminance(fg), luminance(bg)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def is_cream(color: Color) -> bool:
    """Warm, very light, faintly tinted: the reflex 'tasteful' page ground."""
    hue, _, light = hsl(color)
    return 25 <= hue <= 60 and 0.88 <= light <= 0.975 and 0.02 <= chroma(color) <= 0.16


def tw_color(token: str) -> Optional[Tuple[str, int]]:
    """Split a utility colour token such as 'purple-500' into (family, shade)."""
    m = re.fullmatch(r"([a-z]+)-(\d{2,3})(?:/\d+)?", token)
    if not m or (m.group(1) not in TW_HUES and m.group(1) not in TW_NEUTRALS):
        return None
    return m.group(1), int(m.group(2))


def load_catalog(path: Path = CATALOG_PATH) -> Dict[str, dict]:
    """Load and validate the rule catalog; raise ValueError on any defect."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read rule catalog {path}: {exc}") from exc
    rules = data.get("rules") if isinstance(data, dict) else None
    if not isinstance(rules, list) or not rules:
        raise ValueError("rule catalog has no 'rules' list")
    out: Dict[str, dict] = {}
    for rule in rules:
        missing = [f for f in REQUIRED_FIELDS if not rule.get(f)]
        if missing:
            raise ValueError(f"rule {rule.get('id', '?')} missing {', '.join(missing)}")
        if rule["severity"] not in SEVERITY_RANK:
            raise ValueError(f"rule {rule['id']} has unknown severity {rule['severity']}")
        if rule["id"] in out:
            raise ValueError(f"duplicate rule id {rule['id']}")
        out[rule["id"]] = rule
    return out


def make_finding(catalog: Dict[str, dict], rule_id: str, path: str, line: int,
                 evidence: str, severity: Optional[str] = None) -> dict:
    """Build one finding dict from the catalog entry for rule_id."""
    rule = catalog[rule_id]
    return {"file": path, "line": line, "rule": rule_id, "severity": severity or rule["severity"],
            "scope": rule["scope"], "command": rule["command"], "name": rule["name"],
            "evidence": evidence.strip()[:160], "fix": rule["fix"]}


def file_level(ctx: dict, path: str, cat: dict) -> List[dict]:
    """Rules that need a whole file: one spacing value doing all the work."""
    values = ctx["spacing"]
    if len(values) >= 12:
        counts = Counter(values)
        top, count = counts.most_common(1)[0]
        if count / len(values) >= 0.6 and len(counts) < 3:  # a dense grid with 3+ steps still has rhythm
            return [make_finding(cat, "monotonous-spacing", path, 1,
                                   f"{top} is {count} of {len(values)} spacing values")]
    return []


def print_findings(findings: List[dict], fmt: str) -> int:
    """Shared output for the layer CLIs; returns the exit code (1 when anything fired)."""
    if fmt == "json":
        print(json.dumps({"findings": findings}, indent=2))
    else:
        for x in findings:
            print(f"{x['file']}:{x['line']}  {x['rule']} [{x['severity']}]  {x['evidence']}")
        print(f"{len(findings)} finding(s).")
    return 1 if findings else 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="List detector rules or compute a WCAG contrast pair.")
    p.add_argument("--list", action="store_true", help="List the rule catalog (default action)")
    p.add_argument("--scope", help="Only list rules in this scope (color, type, motion, ...)")
    p.add_argument("--contrast", nargs=2, metavar=("FG", "BG"), help="Contrast ratio of two colours")
    p.add_argument("--format", choices=("text", "json"), default="text", help="Output format")
    return p


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    if args.contrast:
        fg, bg = (parse_color(c) for c in args.contrast)
        if fg is None or bg is None:
            print("error: could not parse one of the colours", file=sys.stderr)
            return 2
        note = "translucent colour composited over a white canvas" if min(fg[3], bg[3]) < 1 else ""
        bg = over(bg, (255, 255, 255, 1.0))
        ratio = round(contrast(over(fg, bg), bg), 2)
        result = {"fg": args.contrast[0], "bg": args.contrast[1], "ratio": ratio, "note": note,
                  "aa_body": ratio >= 4.5, "aa_large": ratio >= 3.0, "aaa_body": ratio >= 7.0}
        if args.format == "json":
            print(json.dumps(result, indent=2))
        else:
            print(f"{args.contrast[0]} on {args.contrast[1]}: {ratio}:1  "
                  f"AA body {'pass' if result['aa_body'] else 'FAIL'}, "
                  f"AA large {'pass' if result['aa_large'] else 'FAIL'}" + (f"  ({note})" if note else ""))
        return 0 if result["aa_body"] else 1
    try:
        catalog = load_catalog()
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if args.scope and args.scope not in {r["scope"] for r in catalog.values()}:
        print(f"error: unknown scope '{args.scope}'", file=sys.stderr)
        return 2
    rules = [r for r in catalog.values() if not args.scope or r["scope"] == args.scope]
    if args.format == "json":
        print(json.dumps({"count": len(rules), "rules": rules}, indent=2))
    else:
        for r in rules:
            print(f"{r['id']:<26} {r['severity']:<9} {r['scope']:<12} -> {r['command']:<8} {r['name']}")
        print(f"\n{len(rules)} rules.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
