#!/usr/bin/env python3
"""Lint a project's interface context file (product brief + design brief).

The context file is the durable record every refinement command reads first:
platform, users and jobs, surfaces and their modes, voice and terms, evidence
on hand, constraints, and the visual system (palette roles, type roles,
spacing, radius, motion, named rules, refusals). This linter checks that it
is complete, specific, honest about evidence, and internally consistent
(declared text/surface pairs pass WCAG AA, body type is readable, the
spacing scale climbs).

Usage:
  python3 context_linter.py --input interface-context.md --format text
  python3 context_linter.py --input interface-context.md --strict --format json

Exit codes: 0 no errors (warnings allowed unless --strict), 1 errors (or
warnings under --strict), 2 bad input (missing, empty, or not a context file).
"""

from __future__ import annotations

import argparse
import importlib.util
import json
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


REQUIRED = ["platform", "users and jobs", "surfaces", "voice and terms", "evidence on hand",
            "constraints", "visual system"]
PLATFORMS = {"web", "ios", "android", "cross-platform"}
MODES = {"persuade", "operate", "read", "showcase"}
PRODUCT_SECTIONS = {"users and jobs", "surfaces", "voice and terms", "evidence on hand", "constraints",
                    "purpose and positioning", "principles", "brand commitments"}
RECOMMENDED = {"purpose and positioning": "what the product is for and what a neighbour could not truthfully copy",
               "principles": "two to five durable decisions the team can cite"}
RECOMMENDED_SUBS = {"elevation": "shadow or border vocabulary", "layout": "content width, measure and grid",
                    "components": "how buttons, fields, tables or cards are built"}
PLACEHOLDER = re.compile(r"\bTBD\b|\bTODO\b|\bXXX\b|lorem ipsum|\?\?\?|\[\.\.\.\]|<(product|name|user|tbd)[^>]*>", re.I)
VAGUE = re.compile(r"\b(modern|clean|sleek|intuitive|user-friendly|beautiful|seamless|cutting-edge|world-class|"
                   r"innovative|elegant|stunning|delightful)\b", re.I)
CLAIMS = re.compile(r"\b(testimonials?|customer quotes?|case stud(y|ies)|benchmarks?|awards?|press|logo walls?|"
                    r"ratings?|reviews?|\d+x faster)\b", re.I)
ABSENT = re.compile(r"\b(none|absent|not available|do not invent|no \w+ yet|missing)\b", re.I)
SOURCE = re.compile(r"(https?://|[\w-]+/[\w./-]+|\b[\w-]+\.(md|json|csv|pdf|png|jpg|svg|txt|xlsx|html)\b)")
HEX_OR_PX = re.compile(r"#[0-9a-fA-F]{3,8}\b|\b\d+px\b")


def unfenced(text: str) -> List[str]:
    """Lines with fenced code blocks blanked (examples inside fences are not the file's content)."""
    out, fence = [], False
    for line in text.splitlines():
        if line.lstrip().startswith(("```", "~~~")):
            fence, line = not fence, ""
        out.append("" if fence else line)
    return out


def parse(text: str) -> Tuple[Dict[str, List[Tuple[int, str]]], Dict[str, List[Tuple[int, str]]]]:
    """Return {h2 section: [(line, text)]} and {h3 subsection under Visual system: [(line, text)]}."""
    sections: Dict[str, List[Tuple[int, str]]] = {}
    subs: Dict[str, List[Tuple[int, str]]] = {}
    h2 = h3 = None
    for number, raw in enumerate(unfenced(text), 1):
        line = raw.rstrip()
        if line.startswith("## "):
            h2, h3 = line[3:].strip().lower(), None
            sections.setdefault(h2, [])
        elif line.startswith("### ") and h2:
            h3 = line[4:].strip().lower()
            subs.setdefault(h3, [])
        elif h2 and line.strip():
            sections[h2].append((number, line.strip()))
            if h3 and h2 == "visual system":
                subs[h3].append((number, line.strip()))
    return sections, subs


def pairs(lines: List[Tuple[int, str]]) -> Dict[str, Tuple[int, str]]:
    """'- key: value' bullets as {key: (line, value)}."""
    out = {}
    for number, text in lines:
        m = re.match(r"^[-*]\s+\**([\w .-]+?)\**\s*:\s*(.+)$", text)
        if m:
            out[m.group(1).strip().lower()] = (number, m.group(2).strip())
    return out


def bullets(lines: List[Tuple[int, str]]) -> List[Tuple[int, str]]:
    return [(n, re.sub(r"^[-*]\s+", "", t)) for n, t in lines if re.match(r"^[-*]\s+", t)]


def lint(text: str, catalog: Dict[str, dict]) -> Tuple[List[dict], List[dict]]:
    errors: List[dict] = []
    warns: List[dict] = []
    err = lambda sec, line, msg: errors.append({"section": sec, "line": line, "message": msg})  # noqa: E731
    warn = lambda sec, line, msg: warns.append({"section": sec, "line": line, "message": msg})  # noqa: E731
    sections, subs = parse(text)
    for name in REQUIRED:
        if name not in sections:
            err(name, 0, f"missing required section '## {name.title()}'")
    for number, line in enumerate(unfenced(text), 1):
        if PLACEHOLDER.search(line):
            err("*", number, f"placeholder left in: {line.strip()[:70]}")
    for name, what in RECOMMENDED.items():
        if name not in sections:
            warn(name, 0, f"no '## {name.capitalize()}' section ({what})")
    purpose = pairs(sections.get("purpose and positioning", []))
    if "purpose and positioning" in sections and "positioning" not in purpose:
        warn("purpose and positioning", 0, "no '- Positioning:' line; critique cannot judge specificity without it")
    principles = bullets(sections.get("principles", []))
    if "principles" in sections and not 2 <= len(principles) <= 5:
        warn("principles", 0, f"{len(principles)} principle(s); keep two to five")
    platform = " ".join(t for _, t in sections.get("platform", [])).strip().lower()
    if "platform" in sections and platform not in PLATFORMS:
        err("platform", 0, f"platform '{platform or '(empty)'}' is not one of {', '.join(sorted(PLATFORMS))}")
    surfaces = bullets(sections.get("surfaces", []))
    if "surfaces" in sections and not surfaces:
        err("surfaces", 0, "no surfaces listed; use '- <surface>: <mode> - <job>'")
    for number, item in surfaces:
        m = re.match(r"^(.+?):\s*(\w+)\s*[-–—:]+\s*(.+)$", item)
        if not m or m.group(2).lower() not in MODES:
            err("surfaces", number, f"surface needs a mode ({', '.join(sorted(MODES))}) and a job: '{item[:60]}'")
        elif len(m.group(3).split()) < 3:
            err("surfaces", number, f"job for '{m.group(1)}' is too thin to steer design: '{m.group(3)}'")
    for sec in PRODUCT_SECTIONS:
        for number, line in sections.get(sec, []):
            for word in VAGUE.findall(line):
                warn(sec, number, f"vague adjective '{word}': say what it means for this product")
            if HEX_OR_PX.search(line) and sec != "constraints":
                warn(sec, number, "visual detail in a product section; move it under '## Visual system'")
    for number, item in bullets(sections.get("evidence on hand", [])):
        if SOURCE.search(item) or ABSENT.search(item):
            continue
        if CLAIMS.search(item):
            err("evidence on hand", number, f"claimed evidence with no source path or stated absence: '{item[:60]}'")
        else:
            warn("evidence on hand", number, f"evidence without a source path: '{item[:60]}'")
    if "visual system" in sections:
        for name, what in RECOMMENDED_SUBS.items():
            if name not in subs:
                warn(name, 0, f"no '### {name.capitalize()}' under Visual system ({what})")
        lint_visual(subs, catalog, err, warn, platform)
    return errors, warns


def lint_visual(subs, catalog, err, warn, platform: str) -> None:
    palette = pairs(subs.get("palette roles", []))
    colors = {}
    for role in ("surface", "text", "action"):
        if role not in palette:
            err("palette roles", 0, f"palette role '{role}' is required")
    for role, (number, value) in palette.items():
        color = R.parse_color(value.split()[0].rstrip(","))
        if color is None:
            err("palette roles", number, f"role '{role}' value '{value}' is not a colour")
        else:
            colors[role] = color
    checks = [("text", "surface", 4.5), ("text-muted", "surface", 4.5), ("muted", "surface", 4.5),
              ("action-text", "action", 4.5), ("action", "surface", 3.0)]
    for fg, bg, need in checks:
        if fg in colors and bg in colors:
            ratio = R.contrast(colors[fg], colors[bg])
            if ratio < need:
                err("palette roles", palette[fg][0], f"{fg} on {bg} is {ratio:.2f}:1, needs {need}:1")
    if "surface" in colors and R.is_cream(colors["surface"]):
        warn("palette roles", palette["surface"][0], "cream surface: record which brief requirement chose it")
    types = pairs(subs.get("type roles", []))
    if "body" not in types:
        err("type roles", 0, "type role 'body' is required ('- body: <family>, <size>px/<line-height>, <weight>')")
    if "heading" not in types and "display" not in types:
        warn("type roles", 0, "no 'heading' or 'display' role; hierarchy is undefined")
    for role, (number, value) in types.items():
        family = value.split(",")[0].strip().lower()
        if family in C.OVERUSED:
            warn("type roles", number, f"'{family}' is an overused default; record why this face was chosen")
        m = re.search(r"(\d+(?:\.\d+)?)px\s*/\s*(\d+(?:\.\d+)?)", value)
        if role == "body":
            if not m:
                err("type roles", number, "body role needs size/line-height, e.g. '16px/1.55'")
                continue
            size, leading = float(m.group(1)), float(m.group(2))
            if size < 14:
                err("type roles", number, f"body size {size:g}px is below 14px")
            elif size < 16 and platform == "web":
                warn("type roles", number, f"body size {size:g}px; 16px is the web body floor unless the surface is dense")
            if not 1.3 <= leading <= 1.9:
                warn("type roles", number, f"body line-height {leading:g} is outside 1.3-1.9")
    steps = [float(x) for _, v in pairs(subs.get("spacing scale", [])).values() for x in re.findall(r"\d+(?:\.\d+)?", v)]
    if not steps:
        err("spacing scale", 0, "no spacing scale ('- steps: 4, 8, 12, 16, 24, 40')")
    elif any(b <= a for a, b in zip(steps, steps[1:])):
        err("spacing scale", 0, f"spacing steps must climb: {steps}")
    elif len(steps) < 4:
        warn("spacing scale", 0, "fewer than 4 spacing steps; groups and sections will blur together")
    for number, value in pairs(subs.get("motion", [])).values():
        for ms in re.findall(r"(\d+)\s*ms", value):
            if int(ms) > 800:
                warn("motion", number, f"{ms}ms is longer than any interface transition should be")
        ys = R.bezier_ys(value)
        if any(y < 0 or y > 1 for y in ys) or re.search(r"\b(bounce|elastic|back)\b", value, re.I):
            warn("motion", number, "overshoot or bounce easing in the motion tokens")
    if not bullets(subs.get("named rules", [])):
        warn("named rules", 0, "no named rules; add one or two the team can cite in review")
    refusals = bullets(subs.get("refusals", []))
    if len(refusals) < 3:
        err("refusals", 0, f"{len(refusals)} refusal(s); list at least 3 patterns this product refuses")
    known = sum(1 for _, r in refusals if r.split()[0].strip("`") in catalog)
    if refusals and not known:
        warn("refusals", 0, "no refusal names a detector rule id; the detector cannot enforce them")


def main(argv: Optional[List[str]] = None) -> int:
    p = argparse.ArgumentParser(description="Lint an interface context file (product + design brief).")
    p.add_argument("--input", required=True, help="Path to the context markdown file")
    p.add_argument("--strict", action="store_true", help="Treat warnings as failures")
    p.add_argument("--format", choices=("text", "json"), default="text", help="Output format")
    args = p.parse_args(argv)
    path = Path(args.input)
    try:
        text = path.read_text(encoding="utf-8")
        catalog = R.load_catalog()
    except (OSError, UnicodeDecodeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if not text.strip() or "## " not in text:
        print(f"error: {path} is empty or has no '## ' sections; not a context file", file=sys.stderr)
        return 2
    try:
        errors, warns = lint(text, catalog)
    except (ValueError, TypeError, IndexError) as exc:
        print(f"error: could not parse {path}: {exc}", file=sys.stderr)
        return 2
    failed = bool(errors) or (args.strict and bool(warns))
    verdict = "FAIL" if failed else "PASS"
    if args.format == "json":
        print(json.dumps({"file": str(path), "verdict": verdict, "errors": errors, "warnings": warns}, indent=2))
    else:
        for kind, items in (("ERROR", errors), ("WARN", warns)):
            for i in items:
                where = f"line {i['line']}" if i["line"] else i["section"]
                print(f"{kind:<5} [{i['section']}] {where}: {i['message']}")
        print(f"{verdict}  {len(errors)} error(s), {len(warns)} warning(s) in {path}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
