#!/usr/bin/env python3
"""Utility-class checks for the interface detector.

Translates utility classes (the Tailwind vocabulary) on one element into the
same rules css_checks.py applies to declarations, adds class-only rules (faint
gray text, gray on color, removed focus ring, pulsing dots) and exposes the
shape predicates markup_checks.py uses (card, chip, icon tile, kicker, bold).

Usage:
  python3 class_checks.py --tag h1 --classes "bg-clip-text text-transparent italic font-serif"

Exit codes: 0 no findings, 1 findings, 2 bad input.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from pathlib import Path
from typing import List, Optional, Tuple


def _load(name: str):
    """Load a sibling module from this scripts/ folder (keeps the package self-contained)."""
    if name not in sys.modules:
        spec = importlib.util.spec_from_file_location(name, Path(__file__).with_name(f"{name}.py"))
        sys.modules[name] = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(sys.modules[name])
    return sys.modules[name]


C = _load("css_checks")
R = _load("ui_rules")


SCALE_LEADING = {"leading-none": "1", "leading-tight": "1.25", "leading-snug": "1.375"}
SCALE_TRACKING = {"tracking-tighter": "-0.05em", "tracking-tight": "-0.025em", "tracking-wide": "0.025em",
                  "tracking-wider": "0.05em", "tracking-widest": "0.1em"}
ROUNDED = re.compile(r"^rounded(-(sm|md|lg|xl|2xl|3xl|full|\[[^\]]+\]))?$")
CREAM_TOKENS = {"bg-amber-50", "bg-orange-50", "bg-yellow-50"}
BOLD = {"font-semibold", "font-bold", "font-extrabold", "font-black"}
CHIP_WORDS = re.compile(r"(^|[-_])(badge|chip|pill|tag|status)($|[-_])")
CARD_WORDS = re.compile(r"(^|[-_])card($|[-_]?$)")
SMALL_DOT = re.compile(r"^(w|h|size)-(0\.5|1|1\.5|2|2\.5|3)$")


def base(classes: List[str]) -> List[str]:
    """Tokens with no variant prefix (hover:, md:, dark: ...)."""
    return [c for c in classes if ":" not in c.replace("::", "")]


def arbitrary(token: str, prefix: str) -> Optional[str]:
    m = re.fullmatch(re.escape(prefix) + r"\[(.+)\]", token)
    return m.group(1).replace("_", " ").strip("'\"") if m else None


def to_decls(classes: List[str], line: int) -> List[C.Decl]:
    """Translate the class tokens that map cleanly onto CSS declarations."""
    out: List[C.Decl] = []
    for t in base(classes):
        for prefix, prop in (("text-", "font-size"), ("tracking-", "letter-spacing"), ("leading-", "line-height"),
                             ("shadow-", "box-shadow"), ("bg-", "background-color"), ("font-", "font-family")):
            value = arbitrary(t, prefix)
            if value is None:
                continue
            if prefix == "text-" and not C.NUM.fullmatch(value):
                prop = "color"
            if prefix == "font-" and re.fullmatch(r"\d+", value):
                prop = "font-weight"
            out.append((prop, value, line))
        if t in SCALE_LEADING:
            out.append(("line-height", SCALE_LEADING[t], line))
        if t in SCALE_TRACKING:
            out.append(("letter-spacing", SCALE_TRACKING[t], line))
        if t == "transition-all":
            out.append(("transition-property", "all", line))
        if t == "italic":
            out.append(("font-style", "italic", line))
        if t == "font-serif":
            out.append(("font-family", "serif", line))
        if t == "uppercase":
            out.append(("text-transform", "uppercase", line))
    return out


def tw_hue(token: str, prefix: str) -> Optional[float]:
    value = arbitrary(token, prefix)
    if value:
        color = R.parse_color(value)
        return R.hsl(color)[0] if color and R.chroma(color) >= 0.2 else None
    parsed = R.tw_color(token[len(prefix):]) if token.startswith(prefix) else None
    return float(R.TW_HUES[parsed[0]]) if parsed and parsed[0] in R.TW_HUES else None


def ground(classes: List[str]) -> Optional[str]:
    """Classify an element's own background: light, dark, color, or None."""
    for t in base(classes):
        if t in ("bg-white", "bg-transparent"):
            return "light" if t == "bg-white" else None
        if t == "bg-black":
            return "dark"
        parsed = R.tw_color(t[3:]) if t.startswith("bg-") else None
        if parsed:
            family, shade = parsed
            if family in R.TW_NEUTRALS:
                return "dark" if shade >= 600 else "light"
            return "color" if shade >= 400 else "light"
        value = arbitrary(t, "bg-")
        color = R.parse_color(value) if value else None
        if color:
            if R.chroma(color) >= 0.3:
                return "color"
            return "dark" if R.luminance(color) < 0.2 else "light"
    return None


NOT_CARD = {"button", "input", "select", "textarea", "summary", "label", "img", "span", "code", "kbd", "dialog"}


def is_card(tag: str, classes: List[str]) -> bool:
    toks = base(classes)
    if tag in NOT_CARD:
        return False
    if tag == "card" or any(CARD_WORDS.search(t) and not re.search(r"card-(body|header|footer|title|text|content|img)", t)
                            for t in toks):
        return True
    rounded = any(ROUNDED.match(t) and t != "rounded-full" for t in toks)
    framed = any(t.startswith("shadow") and t != "shadow-none" for t in toks) or "border" in toks
    # all-round padding of 3+, or vertical padding of 4+: a px-6 py-3 call to action is a button, not a card
    padded = any(re.match(r"^p-(\d+|\[)", t) and not re.match(r"^p-[0-2](\.5)?$", t) for t in toks) or any(
        re.match(r"^py-([4-9]|\d{2,}|\[)", t) for t in toks)
    return rounded and framed and padded


def is_chip(tag: str, classes: List[str]) -> bool:
    toks = base(classes)
    if tag not in ("span", "div", "a", "li", "button", "small", "badge", "chip", "tag"):
        return False
    return tag in ("badge", "chip") or any(CHIP_WORDS.search(t) for t in toks) or (
        "rounded-full" in toks and any(t.startswith("px-") for t in toks) and any(t in ("text-xs", "text-sm") for t in toks))


def is_icon_tile(classes: List[str]) -> bool:
    toks = base(classes)
    size = {m.group(2) for t in toks for m in [re.match(r"^(w|h|size)-(\d+)$", t)] if m and 8 <= int(m.group(2)) <= 16}
    square = any(t.startswith("size-") for t in toks) or (any(t.startswith("w-") for t in toks) and len(size) == 1)
    tinted = any(t.startswith("bg-") for t in toks) and any(ROUNDED.match(t) for t in toks)
    named = any(re.search(r"icon[-_]?(wrap|wrapper|tile|box|circle|container|bg)", t) for t in toks)
    return named or (square and bool(size) and tinted)


def is_kicker(classes: List[str], style: str = "") -> bool:
    toks = base(classes)
    if any(re.search(r"eyebrow|kicker|overline|pretitle|supertitle", t) for t in toks):
        return True
    tracked = any(t.startswith("tracking-") and t not in ("tracking-normal", "tracking-tight", "tracking-tighter")
                  for t in toks) or "letter-spacing" in style
    return ("uppercase" in toks or "uppercase" in style) and tracked


def is_bold(classes: List[str]) -> bool:
    return any(t in BOLD or t in ("font-[600]", "font-[700]", "font-[800]") for t in base(classes))


def check_classes(tag: str, classes: List[str], line: int, path: str, cat: dict, env: dict) -> List[dict]:
    """Findings for one element's classes. env: inherited 'ground', 'page' flag, ctx stats."""
    f: List[dict] = []
    toks = base(classes)
    hit = lambda rule, ev, sev=None: f.append(R.make_finding(cat, rule, path, line, ev, sev))  # noqa: E731
    selector = tag + (" .page" if env.get("page") else "")
    f += C.check_block(selector if tag in ("p", "li", "h1", "h2", "td", "blockquote") else tag,
                       to_decls(classes, line), path, cat, env["ctx"])
    if "bg-clip-text" in toks and "text-transparent" in toks:
        hit("gradient-text", "bg-clip-text text-transparent")
    widths = [int(m.group(2)) for t in toks for m in [re.match(r"^border-(l|r|s|e)-(\d+)$", t)] if m]
    colors = [t for t in toks if re.match(r"^border-[a-z]+-\d{2,3}", t) and (R.tw_color(t[7:]) or ("",))[0] in R.TW_HUES]
    if widths and max(widths) >= 2 and colors:
        rounded = any(ROUNDED.match(t) for t in toks)
        hit("side-stripe-border", f"border-{max(widths)} {colors[0]}", None if rounded else "advisory")
    hues = [h for t in toks for p in ("from-", "via-", "to-") for h in [tw_hue(t, p)] if h is not None]
    violet = [h for h in hues if 235 <= h <= 320]
    if violet and any(abs(h - violet[0]) >= 20 for h in hues):
        hit("ai-hue-gradient", " ".join(t for t in toks if t.startswith(("from-", "via-", "to-"))))
    glow = [t for t in toks if t.startswith("shadow-") and (R.tw_color(t[7:]) or ("",))[0] in R.TW_HUES]
    if glow:
        hit("glow-shadow", glow[0])
    if (tag in ("body", "html", "main") or "min-h-screen" in toks) and \
            any(t in CREAM_TOKENS or (arbitrary(t, "bg-") and R.parse_color(arbitrary(t, "bg-") or "")
                                      and R.is_cream(R.parse_color(arbitrary(t, "bg-")))) for t in toks):
        hit("cream-ground", " ".join(t for t in toks if t.startswith("bg-")))
    grays = [R.tw_color(t[5:]) for t in toks if t.startswith("text-") and R.tw_color(t[5:])]
    grays = [g for g in grays if g[0] in R.TW_NEUTRALS]
    here = ground(classes) or env.get("ground")
    for family, shade in grays:
        if shade in R.TW_FAINT[family] and here in (None, "light"):
            ratio = R.contrast(R.parse_color(R.TW_FAINT[family][shade]), (255, 255, 255, 1))
            hit("faint-gray-text", f"text-{family}-{shade} on a light ground ({ratio:.2f}:1 on white)")
        elif here == "color" and 300 <= shade <= 600:
            hit("gray-on-color", f"text-{family}-{shade} on a colored ground")
    if ("outline-none" in classes or "focus:outline-none" in classes) and not any(
            c.startswith(("focus-visible:", "focus:ring", "focus:outline-")) and c != "focus:outline-none" for c in classes):
        hit("focus-ring-removed", "outline-none with no focus-visible style")
    if "animate-bounce" in toks:
        hit("bounce-easing", "animate-bounce")
    if any(t in ("animate-ping", "animate-pulse") for t in toks) and "rounded-full" in toks \
            and any(SMALL_DOT.match(t) for t in toks):
        hit("decorative-pulse", " ".join(t for t in toks if t.startswith(("animate-", "w-", "h-", "size-"))))
    if any("marquee" in t for t in toks) and any(t.startswith("animate-") for t in toks):
        hit("marquee-scroll", " ".join(t for t in toks if "marquee" in t or t.startswith("animate-")))
    if any(t.startswith("animate-") and t != "animate-none" for t in toks) and not env["ctx"]["animated"]:
        env["ctx"]["animated"] = (path, line)
    if any(c.startswith(("motion-safe:", "motion-reduce:")) for c in classes):
        env["ctx"]["reduced_motion"] = True
    return f


def main(argv: Optional[List[str]] = None) -> int:
    p = argparse.ArgumentParser(description="Check one element's utility classes against the interface rules.")
    p.add_argument("--classes", required=True, help="Space-separated class list")
    p.add_argument("--tag", default="div", help="Element tag name (default div)")
    p.add_argument("--format", choices=("text", "json"), default="text", help="Output format")
    args = p.parse_args(argv)
    try:
        cat = R.load_catalog()
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if not args.classes.strip():
        print("error: --classes is empty", file=sys.stderr)
        return 2
    env = {"ctx": C.new_context(""), "ground": None, "page": False}
    findings = check_classes(args.tag.lower(), args.classes.split(), 1, "<classes>", cat, env)
    flags: List[Tuple[str, bool]] = [("card", is_card(args.tag, args.classes.split())),
                                     ("chip", is_chip(args.tag, args.classes.split())),
                                     ("icon_tile", is_icon_tile(args.classes.split())),
                                     ("kicker", is_kicker(args.classes.split())), ("bold", is_bold(args.classes.split()))]
    if args.format == "json":
        print(json.dumps({"shapes": dict(flags), "findings": findings}, indent=2))
    else:
        names = ", ".join(name for name, on in flags if on)
        print(f"shapes: {names or 'none'}")
        for x in findings:
            print(f"  {x['rule']} [{x['severity']}]  {x['evidence']}")
        print(f"{len(findings)} finding(s).")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
