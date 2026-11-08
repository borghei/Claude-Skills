#!/usr/bin/env python3
"""Second layer of detector rules: surface effects, images, type scale and fonts.

Declaration rules (run on every CSS block through the css_checks hook):
radial-glow, organic-clip-path, buried-raster, hairline-wide-shadow,
blinking-cursor, all-caps-body, font-display-missing. Markup rules (regex
over the raw file, so line numbers are exact): broken-image,
image-missing-dimensions, shape-assembled-illustration, oversized-headline,
all-caps-body. Project rule: flat-type-hierarchy, from the h1/h2/h3/body
sizes gathered across the whole scan.

Usage (runs this layer alone, for debugging a rule):
  python3 extra_checks.py --input page.html styles.css --format text

Exit codes: 0 nothing fired, 1 findings, 2 bad input.
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


C = _load("css_checks")
R = _load("ui_rules")

ROLE_TAGS = ("h1", "h2", "h3", "body", "p")
CARDISH = re.compile(r"card|tile|feature|plan|pricing|item", re.I)
CAPS_EXEMPT = re.compile(r"label|eyebrow|kicker|overline|badge|chip|tag|btn|button|nav|caption|\bth\b|legend|abbr", re.I)
CARET = re.compile(r"\b(blink|caret|cursor|typing|typewriter)[\w-]*", re.I)
PLACEHOLDER_SRC = re.compile(r"^(#|about:blank|https?://(via\.)?placehold|https?://[\w.]*placeholder|"
                             r"https?://dummyimage|https?://picsum\.photos|https?://fakeimg|https?://lorempixel)", re.I)
IMG = re.compile(r"<img\b([^>]*?)/?>", re.I | re.S)
SVG = re.compile(r"<svg\b([^>]*)>(.*?)(?:</svg\s*>|(?=<svg\b)|\Z)", re.I | re.S)
H1 = re.compile(r"<h1\b([^>]*)>(.*?)(?:</h1\s*>|(?=<h1\b)|\Z)", re.I | re.S)
PARA = re.compile(r"<p\b([^>]*)>(.*?)(?:</p\s*>|(?=<p\b|</(?:div|section|article|li|td|main|body)\b)|\Z)", re.I | re.S)
ATTR = re.compile(r"""([\w:@\[\].-]+)\s*=\s*(?:"([^"]*)"|'([^']*)'|\{([^}]*)\})""")
DISPLAY_CLASS = re.compile(r"(?<![\w-])(?:\w+:)?text-(?:[6-9]xl|\[(\d+(?:\.\d+)?)(px|rem)\])")
SHAPES = re.compile(r"<(circle|ellipse|rect|polygon|polyline|line)\b([^>]*)>", re.I)


def attrs(raw: str) -> Dict[str, str]:
    out = {}
    for m in ATTR.finditer(raw):
        key = re.sub(r"^(v-bind:|:|\[)|\]$", "", m.group(1).lower())  # Vue :src, Angular [src]
        out[key] = next((g for g in m.groups()[1:] if g is not None), "")
    for bare in re.findall(r"(?<![\w:=-])(fill|hidden)(?=[\s/>]|$)", raw):
        out.setdefault(bare.lower(), "true")
    return out


def line_of(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1


def plain(html: str) -> str:
    return " ".join(re.sub(r"<[^>]+>|\{[^}]*\}", " ", html).split())


def alphas(segment: str) -> List[float]:
    found = [c[3] for c in R.find_colors(segment)]
    return found + [0.0] * len(re.findall(r"\btransparent\b", segment, re.I))


def gradient_segments(value: str) -> List[Tuple[str, int]]:
    """Each top-level gradient(...) call in a background value with its offset."""
    out = []
    for m in re.finditer(r"(?:repeating-)?(?:linear|radial|conic)-gradient\(", value):
        depth, i = 1, m.end()
        while i < len(value) and depth:
            depth += {"(": 1, ")": -1}.get(value[i], 0)
            i += 1
        out.append((value[m.start():i], m.start()))
    return out


def check_block(selector: str, decls: list, path: str, cat: dict, ctx: dict) -> List[dict]:
    """Declaration rules for one block; also records type-role sizes for the project rule."""
    f: List[dict] = []
    d = {p: (v, ln) for p, v, ln in decls}

    def hit(rule: str, line: int, ev: str) -> None:
        f.append(R.make_finding(cat, rule, path, line, ev))

    if selector.strip().lower().startswith("@font-face") and "font-display" not in d:
        hit("font-display-missing", decls[0][2] if decls else 1, "@font-face has no font-display")
    blend = any(p.endswith("blend-mode") and v.strip() not in ("normal", "") for p, v, _ in decls)
    for prop, value, line in decls:
        low = value.lower()
        if prop.startswith("background"):
            for seg, _ in gradient_segments(low):
                if seg.startswith("radial-gradient("):
                    cols = [c for c in R.find_colors(seg) if R.chroma(c) >= 0.25 and c[3] > 0.15]
                    if cols and any(a <= 0.05 for a in alphas(seg)):
                        hit("radial-glow", line, f"{selector} {prop}: {value}")
                        break
            url = low.find("url(")
            washes = [s for s, at in gradient_segments(low) if url > at]
            if url >= 0 and not blend and any(alphas(s) and min(alphas(s)) >= 0.9 for s in washes):
                hit("buried-raster", line, f"{selector} {prop}: {value}")
            elif url >= 0 and (C.px(d.get("opacity", ("1", 0))[0]) or 1.0) < 0.1:
                hit("buried-raster", line, f"{selector} background image at opacity {d['opacity'][0]}")
        if prop in ("clip-path", "-webkit-clip-path"):
            poly = re.search(r"polygon\(([^)]*)\)", low)
            if poly:
                pts = [p.split() for p in poly.group(1).split(",") if len(p.split()) == 2]
                xs, ys = {p[0] for p in pts}, {p[1] for p in pts}
                square = all(p[0] == q[0] or p[1] == q[1] for p, q in zip(pts, pts[1:] + pts[:1]))
                if len(pts) >= 10 and len(xs) >= 5 and len(ys) >= 5 and not square:
                    hit("organic-clip-path", line, f"clip-path: polygon() with {len(pts)} irregular points")
            elif re.search(r"path\(", low) and len(re.findall(r"[CcSsQqTtAa]\s*-?\d", low)) >= 3:
                hit("organic-clip-path", line, "clip-path: path() drawn with curves")
        if prop == "box-shadow" and CARDISH.search(selector):
            border = d.get("border", d.get("border-width", ("", 0)))[0].lower()
            blurs = [nums[2] for nums, color, inset in C.shadow_layers(low)
                     if len(nums) >= 3 and not inset and (color is None or color[3] > 0.04)]
            if re.match(r"^1px\b", border) and blurs and max(blurs) >= 24:
                hit("hairline-wide-shadow", line, f"{selector}: 1px border + {max(blurs):g}px shadow blur")
        if prop in ("animation", "animation-name") and (CARET.search(low) or CARET.search(selector)):
            timing = low + " " + d.get("animation-timing-function", ("", 0))[0]
            if "step" in timing:
                hit("blinking-cursor", line, f"{selector} {{{prop}: {value}}}")
        # a bare tag selector comes from utility classes or a styled tag; the markup rule
        # judges those by text length, so only real stylesheet selectors are read here
        if prop == "text-transform" and low == "uppercase" and C.BODY_SEL.search(selector) \
                and not re.fullmatch(r"[a-z][a-z0-9]*", selector.strip()) and not CAPS_EXEMPT.search(selector):
            hit("all-caps-body", line, f"{selector} text-transform: uppercase")
        if prop == "font-size" and "shared" in ctx:
            size = C.px(low) if not re.search(r"\b(calc|clamp|max|min|var)\(|%|\d(em|vw|vh)\b", low) else None
            for part in (s.strip().lower() for s in selector.split(",")):
                if part in ROLE_TAGS and size:
                    role = "body" if part in ("body", "p") else part
                    ctx["shared"].setdefault(role, (size, path, line))
    return f


def scan_markup(text: str, path: str, cat: dict) -> List[dict]:
    """Markup rules over raw HTML/JSX text (script bodies and comments blanked, lines kept)."""
    f: List[dict] = []
    text = re.sub(r"(<script\b[^>]*>)(.*?)(?=</script\s*>)|<!--.*?(?:-->|\Z)",
                  lambda m: (m.group(1) or "") + re.sub(r"[^\n]", " ", m.group(2) if m.group(1) else m.group(0)),
                  text, flags=re.I | re.S)

    def hit(rule: str, index: int, ev: str) -> None:
        f.append(R.make_finding(cat, rule, path, line_of(text, index), ev))

    for m in IMG.finditer(text):
        a = attrs(m.group(1))
        src = a.get("src")
        cls = a.get("class", "") + " " + a.get("classname", "")
        sized = bool(re.search(r"(?<![\w-])size-\S+|aspect-", cls + a.get("style", ""))) or (
            bool(re.search(r"(?<![\w-])w-\S+", cls)) and bool(re.search(r"(?<![\w-])h-(?!auto)\S+", cls)))
        if "{..." in m.group(1):
            continue  # spread props: the source and size come from the caller
        if src is None and not any(k in a for k in ("srcset", "data-src", "data-srcset")):
            hit("broken-image", m.start(), "<img> has no src")
        elif src is not None and (not src.strip() or PLACEHOLDER_SRC.match(src.strip())):
            hit("broken-image", m.start(), f'<img src="{src[:60]}">')
        elif not ({"width", "height"} <= set(a) or "fill" in a or sized):
            hit("image-missing-dimensions", m.start(), f"<img src=\"{(src or '')[:50]}\"> has no width/height")
    for m in SVG.finditer(text):
        a = attrs(m.group(1))
        box = [float(x) for x in re.findall(r"-?\d+(?:\.\d+)?", a.get("viewbox", ""))][2:4]
        size = [C.px(a.get("width", "")) or (box[0] if box else 0), C.px(a.get("height", "")) or (box[1] if box else 0)]
        shapes = SHAPES.findall(m.group(2))
        fills = {attrs(s[1]).get("fill", "").lower() for s in shapes} - {"", "none", "currentcolor", "transparent"}
        widths = {attrs(s[1]).get("width") for s in shapes if s[0].lower() == "rect"}
        bar_series = len(shapes) and all(s[0].lower() == "rect" for s in shapes) and len(widths) == 1
        if min(size) >= 200 and len(shapes) >= 12 and len(fills) >= 3 and not bar_series:
            hit("shape-assembled-illustration", m.start(),
                f"inline <svg> {size[0]:g}x{size[1]:g} built from {len(shapes)} shapes in {len(fills)} fills")
    for m in H1.finditer(text):
        a = attrs(m.group(1))
        words = len(plain(m.group(2)).split())
        cls = DISPLAY_CLASS.search(a.get("class", "") + " " + a.get("classname", ""))
        big = bool(cls) and (not cls.group(1) or float(cls.group(1)) * (16 if cls.group(2) == "rem" else 1) >= 64)
        inline = re.search(r"font-size\s*:\s*([\d.]+(?:px|rem))", a.get("style", ""))
        big = big or bool(inline and (C.px(inline.group(1)) or 0) >= 64)
        if big and words >= 8:
            hit("oversized-headline", m.start(), f"<h1> of {words} words at display size")
    for m in PARA.finditer(text):
        a = attrs(m.group(1))
        body = plain(m.group(2))
        if re.search(r"(?<![\w-])uppercase(?![\w-])", a.get("class", "") + " " + a.get("classname", "")) \
                and len(body) >= 80:
            hit("all-caps-body", m.start(), f'<p class="uppercase"> with {len(body)} characters')
    return f


def project_level(shared: Dict[str, tuple], cat: dict) -> List[dict]:
    """flat-type-hierarchy: every step between declared role sizes under 1.25x."""
    heads = [r for r in ("h1", "h2", "h3") if r in shared]
    if "body" not in shared or len(heads) < 2:
        return []
    sizes = sorted({shared[r][0] for r in heads + ["body"]}, reverse=True)
    steps = [a / b for a, b in zip(sizes, sizes[1:]) if b]
    if not steps or max(steps) >= 1.25:
        return []
    top = shared[heads[0]]
    roles = ", ".join(f"{r} {shared[r][0]:g}px" for r in heads + ["body"])
    return [R.make_finding(cat, "flat-type-hierarchy", top[1], top[2],
                           f"{roles}; largest step {max(steps):.2f}:1, target 1.25:1")]


def main(argv: Optional[List[str]] = None) -> int:
    p = argparse.ArgumentParser(description="Run the second detector layer (effects, images, type scale) alone.")
    p.add_argument("--input", nargs="+", required=True, help="Markup or stylesheet files")
    p.add_argument("--format", choices=("text", "json"), default="text", help="Output format")
    args = p.parse_args(argv)
    try:
        cat = R.load_catalog()
        findings: List[dict] = []
        shared: Dict[str, tuple] = {}
        for raw in args.input:
            text = Path(raw).read_text(encoding="utf-8")
            ctx = {"shared": shared}
            for selector, decls in C.extract_blocks(text):
                findings += check_block(selector, decls, raw, cat, ctx)
            if not raw.endswith((".css", ".scss", ".less")):
                findings += scan_markup(text, raw, cat)
        findings += project_level(shared, cat)
    except (OSError, UnicodeDecodeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return R.print_findings(findings, args.format)


if __name__ == "__main__":
    sys.exit(main())
