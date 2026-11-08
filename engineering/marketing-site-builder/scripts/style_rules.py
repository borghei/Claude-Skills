#!/usr/bin/env python3
"""Rule-level CSS checks that a count of distinct values cannot see.

consistency_check.py counts how many spacings, radii and colours a page uses.
This script reads the same CSS rule by rule (selector plus declarations, with
var() resolved) and flags the choices that make a page read as a template:
a violet or lavender accent, an over-used default typeface, bold-and-big
weights, text under 13px, reading text under 16px or tightly leaded, labels set
in tracked capitals, text and ground in one rule that fail contrast, a
photograph set as a CSS background, and web fonts loaded without font-display.

Usage:
  python3 style_rules.py page.html
  python3 style_rules.py page.html --css dist/assets/app.css --format json

Exit codes: 0 pass, 1 FAIL findings (or WARN with --strict), 2 bad input.
"""
from __future__ import annotations

import argparse
import colorsys
import importlib.util
import json
import math
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

HERE = Path(__file__).resolve().parent
DEFAULT_FACES = {"inter", "roboto", "open sans", "lato", "montserrat", "poppins", "space grotesk",
                 "plus jakarta sans", "nunito", "raleway", "dm sans", "manrope"}
READING = re.compile(r"(^|[\s>+~,(])(p|li|dd|td|body|blockquote|article)(?=$|[\s.:#\[>+~,)])")
PHOTO_URL = re.compile(r"url\(\s*['\"]?[^)'\"]+\.(jpe?g|png|webp|avif)(\?[^)'\"]*)?['\"]?\s*\)", re.I)


def _sibling(name: str):
    """Load a sibling script as a module without a package import."""
    spec = importlib.util.spec_from_file_location(name, HERE / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


CC = _sibling("consistency_check")


def rules(sources: List[Tuple[str, str, int]]) -> List[Tuple[str, Dict[str, str], str]]:
    """Return (selector, {property: value}, location) for every rule, at-rule wrappers walked through."""
    out = []
    for css, label, base in sources:
        css = re.sub(r"/\*.*?\*/", lambda m: "\n" * m.group(0).count("\n"), css, flags=re.S)
        stack: List[Tuple[str, Dict[str, str], int]] = []
        nls, start = [m.start() for m in re.finditer("\n", css)], 0
        for i, ch in enumerate(css):
            if ch not in "{};":
                continue
            piece = css[start:i]
            if ch == "{":
                lead = len(piece) - len(piece.lstrip())
                stack.append((" ".join(piece.split()), {}, base + CC.line_at(nls, start + lead)))
            elif stack:
                m = re.match(r"\s*(--[\w-]+|[a-zA-Z-]+)\s*:\s*(.+?)\s*$", piece, re.S)
                if m:
                    prop = m.group(1) if m.group(1).startswith("--") else m.group(1).lower()
                    stack[-1][1][prop] = m.group(2)
                if ch == "}":
                    sel, decls, line = stack.pop()
                    if decls:
                        out.append((sel, decls, f"{label}:{line}"))
            start = i + 1
    return out


def rgb_of(colour: str) -> Optional[Tuple[float, float, float]]:
    """Parse an opaque hex, rgb() or hsl() colour to 0..1 sRGB; None for anything else."""
    c = colour.strip().lower()
    if c in ("white", "#fff"):
        return (1.0, 1.0, 1.0)
    m = re.fullmatch(r"#([0-9a-f]{3}|[0-9a-f]{6})", c)
    if m:
        h = m.group(1) if len(m.group(1)) == 6 else "".join(x * 2 for x in m.group(1))
        return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    nums = re.findall(r"-?\d*\.?\d+%?", c)
    if c.startswith("rgb") and len(nums) >= 3 and (len(nums) == 3 or float(nums[3].rstrip("%")) >= (100 if "%" in nums[3] else 1)):
        return tuple(float(n.rstrip("%")) / (100 if n.endswith("%") else 255) for n in nums[:3])
    if c.startswith("hsl") and len(nums) >= 3:
        return colorsys.hls_to_rgb(float(nums[0]) % 360 / 360, float(nums[2].rstrip("%")) / 100, float(nums[1].rstrip("%")) / 100)
    return None


def oklch_hue(rgb: Tuple[float, float, float]) -> Tuple[float, float]:
    """Return (chroma, hue in degrees) of an sRGB colour in OKLCH."""
    lin = [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in rgb]
    l_ = (0.4122214708 * lin[0] + 0.5363325363 * lin[1] + 0.0514459929 * lin[2]) ** (1 / 3)
    m_ = (0.2119034982 * lin[0] + 0.6806995451 * lin[1] + 0.1073969566 * lin[2]) ** (1 / 3)
    s_ = (0.0883024619 * lin[0] + 0.2817188376 * lin[1] + 0.6299787005 * lin[2]) ** (1 / 3)
    a = 1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_
    b = 0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_
    return math.hypot(a, b), math.degrees(math.atan2(b, a)) % 360


def contrast(a: Tuple[float, ...], b: Tuple[float, ...]) -> float:
    """WCAG 2 contrast ratio of two sRGB colours."""
    def lum(c: Tuple[float, ...]) -> float:
        r, g, bl = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
        return 0.2126 * r + 0.7152 * g + 0.0722 * bl
    hi, lo = sorted((lum(a), lum(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def px(value: str) -> Optional[float]:
    """A single px/rem/em length in px, else None (clamp and calc are skipped)."""
    m = re.fullmatch(r"\s*(\d*\.?\d+)(px|rem|em)\s*", value)
    return float(m.group(1)) * (1 if m.group(2) == "px" else 16) if m else None


def check(path: Path, extra: List[str]) -> Dict:
    """Run every rule-level check and return findings."""
    try:
        sources, _ = CC.gather(path, extra)
        raw = CC.read(path)
    except CC.InputError as exc:
        raise ValueError(str(exc)) from exc
    rs = rules(sources)
    tokens = {p: v for _, d, _ in rs for p, v in d.items() if p.startswith("--")}
    out: List[Dict] = []

    def add(sev: str, cid: str, where: str, msg: str) -> None:
        out.append({"severity": sev, "id": cid, "line": int(where.rsplit(":", 1)[1]) if where.startswith(("style block", "inline style")) else 0,
                    "where": where, "message": msg})

    violet: Dict[str, str] = {}
    faces: Dict[str, str] = {}
    caps: List[str] = []
    for sel, decls, where in rs:
        val = {p: CC.resolve(v, tokens).strip() for p, v in decls.items()}
        for p, v in val.items():
            for col in CC.COLOUR.findall(v):
                rgb = rgb_of(col)
                if rgb:
                    chroma, hue = oklch_hue(rgb)
                    if chroma > 0.06 and 270 <= hue <= 330:
                        violet.setdefault(col.lower(), where)
        fam = val.get("font-family", "")
        if fam:
            first = fam.split(",")[0].strip().strip("'\"").lower()
            if first in DEFAULT_FACES:
                faces.setdefault(first, where)
        weight = val.get("font-weight", "")
        inline_bold = all(re.fullmatch(r"(strong|b|th|dt)(:[\w-]+)?", p.strip()) for p in sel.split(","))
        if sel != "@font-face" and not inline_bold and (weight in ("bold", "bolder") or (weight.isdigit() and int(weight) >= 700)):
            add("WARN", "heavy-weight", where, f"{sel} at weight {weight}: size and tight tracking carry a headline, not bold-and-big")
        size = px(val.get("font-size", ""))
        if size is not None and size < 13:
            add("WARN", "tiny-text", where, f"{sel} at {size:g}px: nothing on the page under 13px")
        elif size is not None and size < 16 and READING.search(sel):
            add("WARN", "small-body", where, f"{sel} at {size:g}px: text people read is 16px or more")
        lh = val.get("line-height", "")
        if READING.search(sel) and re.fullmatch(r"\d*\.?\d+", lh) and float(lh) < 1.4:
            add("WARN", "tight-leading", where, f"{sel} line-height {lh}: reading text wants 1.5 to 1.7")
        if val.get("text-transform", "").lower() == "uppercase":
            caps.append(where)
        fg = rgb_of(val.get("color", ""))
        bg_raw = val.get("background-color") or val.get("background", "")
        bg = rgb_of(bg_raw) if bg_raw and "gradient" not in bg_raw and "url(" not in bg_raw else None
        if fg and bg:
            ratio = contrast(fg, bg)
            if ratio < 4.5:
                add("FAIL" if ratio < 3 else "WARN", "contrast-pair", where,
                    f"{sel}: text {val['color']} on {bg_raw} is {ratio:.1f}:1; body text needs 4.5:1, large text 3:1")
        for p in ("background", "background-image"):
            if PHOTO_URL.search(val.get(p, "")):
                add("WARN", "css-bg-photo", where, f"{sel}: a photograph as CSS background cannot lazy-load or carry alt; use <img>")
        if sel == "@font-face" and "font-display" not in val:
            add("WARN", "font-display", where, "@font-face without font-display: swap shows text while the font loads")
    for col, where in violet.items():
        add("WARN", "violet", where, f"{col} is violet or lavender, the default hue of generated pages; take the accent from the client's material")
    for face, where in faces.items():
        add("WARN", "default-face", where, f"'{face}' is the face every template ships; pick a pairing with a reason")
    for href in re.findall(r"href=[\"']([^\"']*fonts\.googleapis\.com[^\"']*)", raw):
        fams = [f.split(":")[0].replace("+", " ").lower() for f in re.findall(r"family=([^&]+)", href)]
        for face in fams:
            if face in DEFAULT_FACES and face not in faces:
                faces[face] = "font link"
                add("WARN", "default-face", "font link:0", f"'{face}' is the face every template ships; pick a pairing with a reason")
        if "display=" not in href:
            add("WARN", "font-display", "font link:0", "web font link without display=swap")
    if len(caps) > 1:
        add("WARN", "tracked-caps", caps[0], f"{len(caps)} rules set text in capitals: labels read in sentence case")
    out.sort(key=lambda f: (f["severity"] != "FAIL", f["where"]))
    return {"file": str(path), "rules": len(rs), "findings": out}


def main() -> None:
    """CLI entry point."""
    ap = argparse.ArgumentParser(description="Rule-level CSS style checks: violet, default faces, small text, caps, contrast pairs.")
    ap.add_argument("path", help="HTML page or CSS file")
    ap.add_argument("--css", action="append", default=[], help="extra stylesheet to include (repeatable)")
    ap.add_argument("--strict", action="store_true", help="treat WARN as failing")
    ap.add_argument("--format", choices=["text", "json"], default="text", help="output format")
    args = ap.parse_args()
    try:
        res = check(Path(args.path), args.css)
    except (ValueError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(2)
    fails = sum(f["severity"] == "FAIL" for f in res["findings"])
    if args.format == "json":
        print(json.dumps(res, indent=2))
    else:
        print(f"style_rules: {res['file']}  ({res['rules']} rules)")
        for f in res["findings"]:
            print(f"  {f['severity']:4} {f['id']:<14} {f['where']:<18} {f['message']}")
        print(f"  {fails} FAIL, {len(res['findings']) - fails} WARN")
    sys.exit(1 if fails or (args.strict and res["findings"]) else 0)


if __name__ == "__main__":
    main()
