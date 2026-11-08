#!/usr/bin/env python3
"""Declaration-level checks for the interface detector.

Reads CSS from stylesheets, <style> blocks, inline styles, JSX style objects and
css/styled templates; flags generic or low-quality declarations. The entry
point is ui_slop_detector.py; this CLI scans stylesheets alone.

Usage:
  python3 css_checks.py --input styles.css --format text

Exit codes: 0 no findings, 1 findings, 2 bad input.
"""

from __future__ import annotations

import argparse
import importlib.util
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple


def _load(name: str):
    """Load a sibling module from this scripts/ folder (keeps the package self-contained)."""
    if name not in sys.modules:
        spec = importlib.util.spec_from_file_location(name, Path(__file__).with_name(f"{name}.py"))
        sys.modules[name] = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(sys.modules[name])
    return sys.modules[name]


R = _load("ui_rules")
P = _load("css_parse")
Decl, NUM, TEMPLATE = P.Decl, P.NUM, P.TEMPLATE
strip_comments, split_top, kebab, parse_decls = P.strip_comments, P.split_top, P.kebab, P.parse_decls
extract_blocks, px, blank = P.extract_blocks, P.px, P.blank
OVERUSED = {"inter", "roboto", "poppins", "montserrat", "open sans", "lato", "space grotesk",
            "plus jakarta sans", "dm sans", "geist", "outfit", "manrope", "playfair display", "fraunces"}
SYSTEM = {"system-ui", "-apple-system", "blinkmacsystemfont", "segoe ui", "helvetica",
          "helvetica neue", "arial", "sans-serif", "ui-sans-serif"}
SERIF_HINTS = ("serif", "playfair", "fraunces", "recoleta", "newsreader", "cormorant", "garamond",
               "georgia", "lora", "merriweather", "baskerville", "instrument serif")
PAGE_SEL = re.compile(r"(^|[\s,])(html|body|:root|main)\b")
BODY_SEL = re.compile(r"(^|[\s,>+~])(p|body|li|article|blockquote|dd|td)\b|\.prose|\.body(?![\w-])|\.content(?![\w-])")
HEAD_SEL = re.compile(r"(^|[\s,>])h[12]\b|\.hero|\.display|\.headline")
STEP_SEL = re.compile(r"^\s*(from|to|\d+(\.\d+)?%)(\s*,\s*(from|to|\d+(\.\d+)?%))*\s*$")
BG_VAR = re.compile(r"^--(color-)?(bg|background|surface|canvas|paper|page|base)(-[\w-]+)?$")
LAYOUT_PROPS = re.compile(r"(?<![\w-])(width|height|max-height|min-height|top|left|right|bottom|margin[\w-]*|padding[\w-]*)(?![\w-])")
SPACING = re.compile(r"^(padding|margin|gap|row-gap|column-gap)(-[a-z-]+)?$")
EXTRA: list = []


def shadow_layers(value: str) -> List[Tuple[List[float], Optional[R.Color], bool]]:
    out = []
    for layer, _ in split_top(value, ","):
        colors = R.find_colors(layer)
        bare = re.sub(r"#[0-9a-fA-F]+|\w+\([^)]*\)", " ", layer)
        nums = [px(t) or 0.0 for t in re.findall(r"-?\d*\.?\d+(?:px|rem|em)?", bare)]
        out.append((nums, colors[0] if colors else None, "inset" in layer))
    return out


def check_block(selector: str, decls: List[Decl], path: str, cat: dict, ctx: dict) -> List[dict]:
    """Run every declaration rule over one block; update ctx stats in place."""
    f: List[dict] = []
    d: Dict[str, Tuple[str, int]] = {p: (v, ln) for p, v, ln in decls}

    def hit(rule: str, line: int, ev: str, sev: Optional[str] = None) -> None:
        f.append(R.make_finding(cat, rule, path, line, ev, sev))

    radius = px(d.get("border-radius", ("0", 0))[0]) or 0.0
    size = px(d.get("font-size", ("", 0))[0]) or 16.0
    for prop, value, line in decls:
        low = value.lower()
        ctx["spacing"].extend(t for t in low.split() if SPACING.match(prop) and t not in ("0", "auto", "0px"))
        if re.match(r"border-(left|right|inline-start|inline-end)(-width)?$", prop):
            width = px(low) or 0.0
            side_color = R.find_colors(low) or R.find_colors(d.get(prop.replace("-width", "") + "-color", ("", 0))[0])
            if width >= 2 and side_color and not R.is_neutral(side_color[0]):
                hit("side-stripe-border", line, f"{prop}: {value}", None if radius >= 4 else "advisory")
        if prop in ("background-clip", "-webkit-background-clip") and low == "text":
            hit("gradient-text", line, f"{prop}: {value}")
        if "gradient(" in low and prop.startswith("background"):
            hues = [R.hsl(c)[0] for c in R.find_colors(low) if R.chroma(c) >= 0.2]
            violet = [h for h in hues if 235 <= h <= 320]
            if violet and any(abs(h - violet[0]) >= 20 for h in hues):
                hit("ai-hue-gradient", line, f"{prop}: {value}")
            if low.startswith("repeating-") or "repeating-" in low:
                hit("repeating-stripes", line, f"{prop}: {value}")
            elif low.count("linear-gradient(") >= 2 and "1px" in low and "px" in d.get("background-size", ("", 0))[0]:
                hit("grid-line-background", line, f"{prop}: {value}")
        if prop in ("box-shadow", "text-shadow"):
            for nums, color, inset in shadow_layers(low):
                x, y, blur = (nums + [0.0, 0.0, 0.0])[:3]
                if color and x == 0 and y == 0 and blur > 0 and R.chroma(color) >= 0.25 and color[3] > 0.15:
                    hit("glow-shadow", line, f"{prop}: {value}")
                    break
                if prop == "box-shadow" and not inset and (abs(x) >= 3 or abs(y) >= 3) and blur == 0 \
                        and color and color[3] >= 0.5:
                    hit("hard-offset-shadow", line, f"{prop}: {value}")
                    break
        if prop == "font-family":
            face = low.split(",")[0].strip().strip("'\"")
            if face in OVERUSED:
                hit("overused-face", line, f"font-family: {value}")
            elif face in SYSTEM and (PAGE_SEL.search(selector) or HEAD_SEL.search(selector)):
                hit("default-font-stack", line, f"{selector} font-family: {value}")
        if prop == "font-style" and low == "italic" and HEAD_SEL.search(selector) \
                and any(s in d.get("font-family", ("", 0))[0].lower().replace("sans-serif", "") for s in SERIF_HINTS):
            hit("italic-serif-display", line, f"{selector} {{font-style: italic}}")
        if prop == "font-size" and not re.search(r"sr-only|visually-hidden", selector):
            n = px(low)
            floor = 12 if BODY_SEL.search(selector) else 11  # running text 12px, labels and controls 11px
            if n is not None and 0 < n < floor and not re.search(r"\b(calc|max)\(", low):
                hit("tiny-text", line, f"{selector} font-size: {value}".strip())
        if prop == "line-height" and BODY_SEL.search(selector):
            n = NUM.match(low)
            ratio = float(n.group(1)) / size if n and n.group(2) == "px" else float(n.group(1)) if n and not n.group(2) else None
            if ratio is not None and 0 < ratio < 1.3:
                hit("tight-body-leading", line, f"{selector} line-height: {value}")
        if prop == "letter-spacing":
            n = NUM.match(low)
            em = float(n.group(1)) / (size if n.group(2) == "px" else 1) if n and n.group(2) in ("em", "px") else None
            if em is not None and em < -0.04:
                hit("crushed-tracking", line, f"letter-spacing: {value}")
            elif em is not None and em >= 0.05 and BODY_SEL.search(selector) \
                    and "uppercase" not in d.get("text-transform", ("", 0))[0]:
                hit("wide-body-tracking", line, f"{selector} letter-spacing: {value}")
        if prop == "text-align" and low == "justify" and d.get("hyphens", ("", 0))[0] != "auto":
            hit("justified-text", line, f"{selector} text-align: justify")
        if prop in ("transition", "transition-property"):
            first = low.split(",")[0].split()
            if "all" in re.split(r"[\s,]+", low) or (prop == "transition" and first and re.match(r"^[\d.]+m?s$", first[0])):
                hit("transition-all", line, f"{prop}: {value}")
            elif LAYOUT_PROPS.search(low):
                hit("layout-property-motion", line, f"{prop}: {value}")
        if STEP_SEL.match(selector) and LAYOUT_PROPS.fullmatch(prop):
            hit("layout-property-motion", line, f"@keyframes {selector} {{{prop}}}")
        if prop in ("transition-timing-function", "animation-timing-function", "transition", "animation"):
            ys = R.bezier_ys(low)
            if any(y < -0.05 or y > 1.05 for y in ys) or re.search(r"\b(bounce|elastic|wobble|jello|rubber)", low):
                hit("bounce-easing", line, f"{prop}: {value}")
        if prop in ("animation", "animation-name") and low not in ("none", ""):
            ctx["animated"] = ctx["animated"] or (path, line)
            infinite = "infinite" in low or "infinite" in d.get("animation-iteration-count", ("", 0))[0]
            if infinite and re.search(r"marquee|ticker|scroll-x|scroll-left|loop-x|logo-scroll", low):
                hit("marquee-scroll", line, f"{prop}: {value}")
            elif infinite and re.search(r"pulse|ping|blink|breath|glow", low) \
                    and re.search(r"dot|status|live|indicator|online|beacon|ping", selector):
                hit("decorative-pulse", line, f"{selector} {{{prop}: {value}}}")
        if prop == "outline" and low in ("none", "0", "0px") and ":not(:focus-visible)" not in selector.replace(" ", "") \
                and (not ctx["focus_visible"] or (
                "focus-visible" in selector and "box-shadow" not in d and "border" not in d)):
            hit("focus-ring-removed", line, f"{selector} outline: {value}".strip())
        if prop in ("background", "background-color") or BG_VAR.match(prop):
            colors = R.find_colors(low) if "gradient(" not in low and "url(" not in low else []
            if len(colors) == 1 and R.is_cream(colors[0]) and (PAGE_SEL.search(selector) or BG_VAR.match(prop)):
                hit("cream-ground", line, f"{selector or ':root'} {prop}: {value}")
    fg = R.find_colors(d.get("color", ("", 0))[0])
    bg_val = d.get("background-color", d.get("background", ("", 0)))
    bg = R.find_colors(bg_val[0]) if "gradient(" not in bg_val[0] and "url(" not in bg_val[0] else []
    if fg and bg and fg[0][3] >= 0.99 and bg[0][3] >= 0.99:
        bold = (d.get("font-weight", ("400", 0))[0] in ("bold", "bolder", "700", "800", "900"))
        need = 3.0 if size >= 24 or (size >= 18.66 and bold) else 4.5
        ratio = R.contrast(fg[0], bg[0])
        line = d["color"][1]
        if ratio < need:
            hit("low-contrast-pair", line, f"{selector}: {d['color'][0]} on {bg_val[0]} = {ratio:.2f}:1 (needs {need})")
        elif R.is_neutral(fg[0]) and 0.3 < R.hsl(fg[0])[2] < 0.8 and R.chroma(bg[0]) >= 0.3:
            hit("gray-on-color", line, f"{selector}: {d['color'][0]} on {bg_val[0]}")
    for extra in EXTRA:  # further layers register here (extra_checks.check_block)
        f += extra(selector, decls, path, cat, ctx)
    return f


def new_context(text: str) -> dict:
    return {"spacing": [], "animated": None, "focus_visible": ":focus-visible" in text,
            "reduced_motion": "prefers-reduced-motion" in text or "motion-reduce" in text or "motion-safe" in text}


def scan_text(text: str, path: str, cat: dict, js: bool = False, line0: int = 1,
              ctx: Optional[dict] = None) -> Tuple[List[dict], dict]:
    """Scan CSS-bearing text; returns findings and the context stats it gathered."""
    ctx = ctx or new_context(text)
    findings: List[dict] = []
    for selector, decls in extract_blocks(text, line0, js):
        findings += check_block(selector, decls, path, cat, ctx)
    if "@keyframes" in text and not ctx["animated"]:
        ctx["animated"] = (path, line0 + text[:text.index("@keyframes")].count("\n"))
    return findings, ctx


def main(argv: Optional[List[str]] = None) -> int:
    p = argparse.ArgumentParser(description="Run the declaration-level interface rules over stylesheets.")
    p.add_argument("--input", nargs="+", required=True, help="CSS/SCSS files")
    p.add_argument("--format", choices=("text", "json"), default="text", help="Output format")
    args = p.parse_args(argv)
    try:
        cat = R.load_catalog()
        findings: List[dict] = []
        for path in args.input:
            with open(path, encoding="utf-8") as fh:
                text = fh.read()
            found, ctx = scan_text(text, path, cat)
            findings += found + R.file_level(ctx, path, cat)
    except (OSError, UnicodeDecodeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return R.print_findings(findings, args.format)


if __name__ == "__main__":
    sys.exit(main())
