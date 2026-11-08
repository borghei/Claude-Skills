#!/usr/bin/env python3
"""Compare shipped styles against the visual system in interface-context.md.

Reads the context file's palette roles, type roles and radius scale, then
reports literal values in markup and styles that sit outside them:
off-system-font (a first face no type role names), off-system-color,
off-system-radius and off-system-font-size. Also returns the context file's
refusals, which the detector escalates so a refused pattern always fails.

Values behind var(), calc(), clamp(), em, % and named utility classes are
not read; only literals can drift. Pill and circle radii (9999px, 50%) and
zero are always allowed.

Usage:
  python3 system_checks.py --context interface-context.md --input src/styles/app.css --format text

Exit codes: 0 no drift, 1 drift found, 2 bad input (missing file, no visual system).
"""

from __future__ import annotations

import argparse
import importlib.util
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set


def _load(name: str):
    """Load a sibling module from this scripts/ folder (keeps the package self-contained)."""
    if name not in sys.modules:
        spec = importlib.util.spec_from_file_location(name, Path(__file__).with_name(f"{name}.py"))
        sys.modules[name] = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(sys.modules[name])
    return sys.modules[name]


C = _load("css_checks")
R = _load("ui_rules")
L = _load("context_linter")

GENERIC = {"serif", "sans-serif", "monospace", "cursive", "fantasy", "system-ui", "ui-sans-serif", "ui-serif",
           "ui-monospace", "inherit", "initial", "unset"}
DECL = re.compile(r"(?<![\w-])(--[\w-]+|font-family|fontFamily|font-size|fontSize|border(?:-[a-z]+)*-radius|"
                  r"borderRadius|color|background(?:-color)?|backgroundColor|border(?:-[a-z]+)?(?:-color)?|"
                  r"borderColor|fill|stroke|outline-color)\s*:\s*([^;{}\n]+)")
SVG_PAINT = re.compile(r"""(?<![\w-])(fill|stroke)=["'](#[0-9a-fA-F]{3,8})["']""")
TW = re.compile(r"(?<![\w-])(?:\w+:)*(bg|text|border|fill|stroke|rounded(?:-[a-z]{1,2})?|font)-\[([^\]\s]+)\]")
FACE_BLOCK = re.compile(r"@font-face\s*\{[^}]*\}", re.S)
SKIP_VALUE = re.compile(r"\b(calc|clamp|max|min|var|env)\(|%|\d(em|vw|vh|ch)\b|^(inherit|initial|unset|auto)$")
TOLERANCE = 3.0


def load_context(path: str) -> dict:
    """Visual-system values and refusals from a context file; ValueError when unusable."""
    try:
        text = Path(path).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise ValueError(f"cannot read context file {path}: {exc}") from exc
    sections, subs = L.parse(text)
    if "visual system" not in sections or not subs.get("palette roles") or not subs.get("type roles"):
        raise ValueError(f"{path} has no '## Visual system' with palette and type roles; run the document command")
    colors = [c for _, v in L.pairs(subs["palette roles"]).values() if (c := R.parse_color(v.split()[0].rstrip(",")))]
    fonts: Set[str] = set()
    sizes: Set[float] = set()
    for _, value in L.pairs(subs["type roles"]).values():
        fonts.add(re.split(r",|\s+with\s+", value)[0].strip().strip("'\"").lower())
        sizes |= {float(x) for x in re.findall(r"(\d+(?:\.\d+)?)px\s*/", value)}
    radii = {float(x) for _, v in L.pairs(subs.get("radius", [])).values() for x in re.findall(r"(\d+(?:\.\d+)?)px", v)}
    refusals = {r.split()[0].strip("`") for _, r in L.bullets(subs.get("refusals", [])) if r.split()}
    return {"colors": colors, "fonts": fonts, "sizes": sizes, "radii": radii | {0.0}, "refusals": refusals}


def hexify(color) -> str:
    return "#" + "".join(f"{max(0, min(255, round(v))):02x}" for v in color[:3])


def near(value: float, allowed: Set[float]) -> bool:
    return any(abs(value - a) <= 0.5 for a in allowed)


def in_palette(color, palette) -> bool:
    return any(max(abs(color[i] - p[i]) for i in range(3)) <= TOLERANCE for p in palette)


def gather(text: str) -> List[tuple]:
    """(kind, value text, parsed value, offset) for every literal font, colour, radius and size."""
    text = FACE_BLOCK.sub(lambda m: re.sub(r"[^\n]", " ", m.group(0)), C.strip_comments(text))
    out: List[tuple] = []
    for m in DECL.finditer(text):
        prop = C.kebab(m.group(1))
        value = m.group(2).strip().rstrip(",").strip().strip("'\"`").strip()
        low = value.lower()
        if prop == "font-family" or prop.startswith("--font") and "," in low:
            face = low.split(",")[0].strip().strip("'\"")
            if face and not face.startswith(("var(", "$", "{")):
                out.append(("font", face, face, m.start(2)))
        elif prop == "font-size" or (prop.startswith("--") and re.search(r"font-size|text-size", prop)):
            n = None if SKIP_VALUE.search(low) else C.px(low)
            if n:
                out.append(("size", value, n, m.start(2)))
        elif "radius" in prop:
            for token in low.split():
                n = None if SKIP_VALUE.search(token) else C.px(token)
                if n is not None and n < 999:
                    out.append(("radius", token, n, m.start(2)))
        elif "shadow" not in prop:
            for color in R.find_colors(low):
                out.append(("color", hexify(color), color, m.start(2)))
    for m in SVG_PAINT.finditer(text):
        color = R.parse_color(m.group(2))
        if color:
            out.append(("color", m.group(2), color, m.start(2)))
    for m in TW.finditer(text):
        kind, raw = m.group(1), m.group(2).strip("'\"")
        if kind == "font":
            out.append(("font", raw.replace("_", " ").lower(), raw.replace("_", " ").lower(), m.start(2)))
        elif kind.startswith("rounded") and C.px(raw) is not None and not SKIP_VALUE.search(raw):
            out.append(("radius", raw, C.px(raw), m.start(2)))
        elif kind == "text" and re.fullmatch(r"\d+(\.\d+)?(px|rem)", raw):
            out.append(("size", raw, C.px(raw), m.start(2)))
        elif R.parse_color(raw):
            out.append(("color", raw, R.parse_color(raw), m.start(2)))
    return out


def drift_file(text: str, path: str, system: dict, cat: dict) -> List[dict]:
    """One finding per file and distinct off-system value, at its first line."""
    seen: Dict[tuple, int] = {}
    first: Dict[tuple, tuple] = {}
    for kind, shown, value, offset in gather(text):
        if kind == "font":
            off = value not in system["fonts"] and value not in GENERIC and value not in C.SYSTEM
        elif kind == "size":
            off = bool(system["sizes"]) and not near(value, system["sizes"])
        elif kind == "radius":
            off = len(system["radii"]) > 1 and not near(value, system["radii"])
        else:
            off = value[3] > 0 and not in_palette(value, system["colors"])
        if not off:
            continue
        key = (kind, shown.lower() if kind != "color" else tuple(round(v) for v in value[:3]))
        seen[key] = seen.get(key, 0) + 1
        first.setdefault(key, (shown, text.count("\n", 0, offset) + 1))
    rule = {"font": "off-system-font", "size": "off-system-font-size", "radius": "off-system-radius",
            "color": "off-system-color"}
    out = []
    for key, (shown, line) in first.items():
        times = f" ({seen[key]} uses)" if seen[key] > 1 else ""
        what = {"font": "type roles", "size": "type roles", "radius": "radius scale", "color": "palette roles"}[key[0]]
        out.append(R.make_finding(cat, rule[key[0]], path, line, f"{shown[:80]} is not in the context file's {what}{times}"))
    return out


def honour(findings: List[dict], system: dict) -> List[dict]:
    """Drop face judgments the context file already decided: a recorded face is a choice, not a default."""
    def face(f: dict) -> str:
        m = re.search(r"(?:font-family:|loads)\s*([^,]+)", f["evidence"])
        return m.group(1).strip().strip("'\"").lower() if m else ""
    chose_system = bool(system["fonts"] & (C.SYSTEM | {"ui-sans-serif", "system-ui"}))
    return [f for f in findings if not (f["rule"] == "overused-face" and face(f) in system["fonts"])
            and not (f["rule"] == "default-font-stack" and chose_system)]


def escalate(findings: List[dict], refusals: Set[str]) -> int:
    """Refused rules fail the default gate: advisory becomes medium. Returns how many changed."""
    changed = 0
    for f in findings:
        if f["rule"] in refusals:
            f["evidence"] = (f["evidence"] + " [refused in context file]")[:200]
            if f["severity"] == "advisory":
                f["severity"] = "medium"
                changed += 1
    return changed


def main(argv: Optional[List[str]] = None) -> int:
    p = argparse.ArgumentParser(description="Report literal values outside the context file's visual system.")
    p.add_argument("--input", nargs="+", required=True, help="Markup or stylesheet files")
    p.add_argument("--context", required=True, help="Path to interface-context.md")
    p.add_argument("--format", choices=("text", "json"), default="text", help="Output format")
    args = p.parse_args(argv)
    try:
        cat = R.load_catalog()
        system = load_context(args.context)
        findings: List[dict] = []
        for raw in args.input:
            findings += drift_file(Path(raw).read_text(encoding="utf-8"), raw, system, cat)
    except (OSError, UnicodeDecodeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return R.print_findings(findings, args.format)


if __name__ == "__main__":
    sys.exit(main())
