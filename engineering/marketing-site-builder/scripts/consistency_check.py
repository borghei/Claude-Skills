#!/usr/bin/env python3
"""Count how many distinct design values a page really uses, against a budget.

Reads an HTML page (<style>, style="", local and root-relative linked sheets) or CSS
files, resolves var(--token), and reports per category (spacing, radius, colour, accent
hue, font family and size, shadow, duration, button variant) the distinct values against
the budget and where each first appears. Warns on off-grid spacing, pure black, slow UI.

Usage:
  python3 consistency_check.py page.html --css extra.css --budget my_budget.json
  python3 consistency_check.py styles.css --format json

Exit codes: 0 within budget, 1 a category over budget (or WARN with --strict), 2 bad input.
"""
from __future__ import annotations

import argparse
import bisect
import colorsys
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import unquote

DEFAULT_BUDGET = Path(__file__).resolve().parent.parent / "assets" / "site_budget.json"
LENGTH = re.compile(r"(-?\d*\.?\d+)(px|rem|em)\b")
DURATION = re.compile(r"(?<![\w.-])(\d*\.?\d+)(ms|s)\b")
COLOUR = re.compile(r"#[0-9a-fA-F]{3,8}\b|\b(?:rgba?|hsla?|oklch|oklab|lab|lch)\([^)]*\)|"
                    r"\b(?:white|black|red|blue|green|yellow|orange|purple|violet|pink|gray|grey|navy|teal)\b", re.I)
VAR = re.compile(r"var\(\s*(--[\w-]+)\s*(?:,\s*([^()]*(?:\([^()]*\))?[^()]*))?\)")
GENERIC = {"sans-serif", "serif", "monospace", "system-ui", "cursive", "inherit", "initial", "ui-sans-serif",
           "ui-serif", "ui-monospace", "-apple-system", "blinkmacsystemfont", "unset", "emoji"}
SPACING = re.compile(r"^(margin|padding)(-[a-z-]+)?$|^(row-|column-)?gap$")
COLOUR_PROPS = re.compile(r"^(color|background(-color)?|border(-[a-z]+)*(-color)?|outline(-color)?|fill|stroke|"
                          r"box-shadow|text-decoration(-color)?|caret-color|accent-color|text-shadow)$")


class InputError(Exception):
    """Raised for unreadable or unusable input; mapped to exit code 2."""


class StyleParser(HTMLParser):
    """Collect CSS sources (style blocks, inline styles, linked sheets) and button class sets."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.sources: List[Tuple[str, str, int]] = []  # (css, label, first line)
        self.links, self.buttons = [], []  # hrefs; (sorted class set, line)
        self.in_style, self.style_line = False, 0

    def handle_starttag(self, tag: str, attrs: List) -> None:
        a = {k: (v or "") for k, v in attrs}
        line = self.getpos()[0]
        if tag == "style":
            self.in_style, self.style_line = True, line
        if tag == "link" and "stylesheet" in a.get("rel", "").lower() and a.get("href"):
            self.links.append(a["href"])
        if a.get("style"):
            self.sources.append(("x{" + a["style"] + "}", "inline style", line))
        cls = a.get("class", "")
        if tag in ("a", "button", "input") and re.search(r"\b(btn|button|cta)\b", cls):
            self.buttons.append((" ".join(sorted(cls.split())), line))

    def handle_endtag(self, tag: str) -> None:
        self.in_style = self.in_style and tag != "style"

    def handle_data(self, data: str) -> None:
        if self.in_style:
            self.sources.append((data, "style block", self.style_line))


def read(path: Path) -> str:
    """Read a UTF-8 file or raise InputError."""
    try:
        if not path.is_file():
            raise InputError(f"file not found: {path}")
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise InputError(f"cannot read {path}: {exc}") from exc


def local_file(page: Path, href: str) -> Optional[Path]:
    """Resolve a local href against the page; a root-relative one (/_next/a.css) is tried up to four folders up."""
    if not href or re.match(r"^([a-z][a-z0-9+.-]*:|//|#)", href, re.I):
        return None
    rel = unquote(re.split(r"[?#]", href)[0])
    bases = [page.parent, *page.parent.parents][:5] if rel.startswith("/") else [page.parent]
    return next((b / rel.lstrip("/") for b in bases if (b / rel.lstrip("/")).is_file()), None)


def validate_budget(data: object, sections: Tuple[str, ...] = ("system", "page")) -> Dict:
    """Return the budget when each named section is an object of numbers; raise InputError otherwise."""
    num = lambda v: isinstance(v, (int, float)) and not isinstance(v, bool) and v >= 0  # noqa: E731
    for sec in sections:
        part = data.get(sec) if isinstance(data, dict) else None
        ea = part.get("effects_allowed", {}) if isinstance(part, dict) else None
        if not isinstance(ea, dict) or not all(num(v) for k, v in part.items() if k != "effects_allowed") \
                or not all(num(v) and isinstance(v, int) for v in ea.values()):
            raise InputError(f"budget needs a '{sec}' object whose values are all numbers of 0 or more")
    return data


def line_at(newlines: List[int], pos: int) -> int:
    """Lines before offset pos, given the sorted offsets of every newline (linear, not quadratic)."""
    return bisect.bisect_left(newlines, pos)


def gather(path: Path, extra: List[str]) -> Tuple[List[Tuple[str, str, int]], List[Tuple[str, int]]]:
    """Return CSS sources and button class sets for an HTML page or CSS file."""
    text = read(path)
    if not text.strip():
        raise InputError(f"file is empty: {path}")
    sources, buttons = [(text, path.name, 1)], []
    if path.suffix.lower() in (".html", ".htm"):
        if "<" not in text:
            raise InputError(f"{path} has an .html name but contains no markup")
        p = StyleParser()
        p.feed(text)
        p.close()
        sources, buttons = list(p.sources), p.buttons
        for local in filter(None, (local_file(path, href) for href in p.links)):
            sources.append((read(local), local.name, 1))
    for extra_path in extra:
        sources.append((read(Path(extra_path)), Path(extra_path).name, 1))
    if not any(src.strip() for src, _, _ in sources):
        raise InputError(f"no CSS found in {path} (no <style>, style=\"\" or local stylesheet; pass the built CSS with --css)")
    return sources, buttons


def declarations(sources: List[Tuple[str, str, int]]) -> List[Tuple[str, str, str]]:
    """Yield (property, value, location) for every declaration, comments stripped."""
    out = []
    for css, label, base in sources:
        css = re.sub(r"/\*.*?\*/", lambda m: "\n" * m.group(0).count("\n"), css, flags=re.S)
        nls = [m.start() for m in re.finditer("\n", css)]
        depth, start = 0, 0
        for i, ch in enumerate(css):  # a brace-depth scan, so declarations beside nested rules are kept
            if ch not in "{};":
                continue
            piece = css[start:i]
            if ch != "{" and depth > 0:  # a ';' or '}' inside a block ends a declaration; a '{' ends a selector
                m = re.match(r"\s*(--[\w-]+|[a-zA-Z-]+)\s*:\s*(.+?)\s*$", piece, re.S)
                if m:
                    lead = len(piece) - len(piece.lstrip())
                    line = base + line_at(nls, start + lead)
                    prop = m.group(1)
                    out.append((prop if prop.startswith("--") else prop.lower(), m.group(2), f"{label}:{line}"))
            depth += 1 if ch == "{" else -1 if ch == "}" else 0
            depth, start = max(depth, 0), i + 1
    return out


def resolve(value: str, tokens: Dict[str, str], depth: int = 0) -> str:
    """Expand var(--x, fallback) references using the collected custom properties."""
    if depth > 8 or "var(" not in value:
        return value
    return resolve(VAR.sub(lambda m: tokens.get(m.group(1), m.group(2) or ""), value), tokens, depth + 1)


def hue_bucket(colour: str) -> Optional[int]:
    """Return a 30-degree hue bucket for a clearly chromatic colour, else None."""
    c = colour.lower()
    rgb = None
    if c.startswith("#") and len(c) in (4, 5, 7, 9):
        h = "".join(ch * 2 for ch in c[1:4]) if len(c) < 7 else c[1:7]
        rgb = tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    elif c.startswith("rgb"):
        nums = re.findall(r"(\d*\.?\d+)(%?)", c)[:3]
        if len(nums) == 3:
            rgb = tuple(float(n) / (100 if pct else 255) for n, pct in nums)
    elif c.startswith(("oklch", "hsl")):
        nums = [float(n) for n in re.findall(r"\d*\.?\d+", c)]
        if c.startswith("hsl"):  # hue, saturation %, lightness %
            ok = len(nums) >= 3 and nums[1] > 30 and 15 < nums[2] < 90
            return int(nums[0] % 360 // 30) if ok else None
        return int(nums[2] % 360 // 30) if len(nums) >= 3 and nums[1] > 0.06 else None
    if rgb is None:
        return None
    h, light, sat = colorsys.rgb_to_hls(*rgb)
    return int(h * 360 // 30) if sat > 0.3 and 0.15 < light < 0.9 else None


def analyse(sources: List, buttons: List, budget: Dict) -> Dict:
    """Bucket every resolved value by category and compare with the budget."""
    decls = declarations(sources)
    tokens = {p: v for p, v, _ in decls if p.startswith("--")}
    cats: Dict[str, Dict[str, List[str]]] = {k: {} for k in ("spacing_values", "radius_values", "colour_values",
                                                             "font_families", "font_sizes", "shadow_styles", "durations")}
    warns: List[Dict] = []
    used_var = total = 0
    grid = max(1, int(budget.get("spacing_grid_px", 4)))

    put = lambda cat, val, loc: cats[cat].setdefault(val, []).append(loc)  # noqa: E731
    for prop, raw, loc in decls:
        if prop.startswith("--"):
            continue
        total += 1
        used_var += "var(" in raw
        val = resolve(raw, tokens).lower()
        if SPACING.match(prop):
            for px in [float(n) * (1 if u == "px" else 16) for n, u in LENGTH.findall(re.sub(r"calc\([^()]*(\([^()]*\)[^()]*)*\)", " ", val))]:
                if not px:
                    continue
                put("spacing_values", f"{px:g}px", loc)
                if px % grid:
                    warns.append({"id": "off-grid", "where": loc, "value": f"{px:g}px",
                                  "message": f"{prop} {px:g}px is off the {grid}px grid"})
        elif prop.startswith("border") and "radius" in prop:
            for part in (x for x in val.replace("/", " ").split() if x not in ("0", "0px")):
                m = LENGTH.match(part)
                put("radius_values", "pill" if m and float(m.group(1)) * (1 if m.group(2) == "px" else 16) >= 999 else part, loc)
        elif prop in ("font-family", "font"):
            fam = (val if prop == "font-family" else re.split(r"\d(?:px|rem|em|%)?(?:/\S+)?\s+", val)[-1]).split(",")[0].strip().strip("'\"")
            if fam and fam not in GENERIC:
                put("font_families", fam, loc)
        if prop == "font-size":
            put("font_sizes", " ".join(val.split()), loc)
        if prop in ("box-shadow", "text-shadow") and val.strip() not in ("none", "0", "inherit"):
            put("shadow_styles", " ".join(val.split()), loc)
        if prop.startswith("transition") or prop.startswith("animation"):
            for ms in [float(n) * (1000 if u == "s" else 1) for n, u in DURATION.findall(val)]:
                if not ms:
                    continue
                put("durations", f"{ms:g}ms", loc)
                if prop.startswith("transition") and ms > budget.get("max_ui_duration_ms", 700):
                    warns.append({"id": "slow-ui", "where": loc, "value": f"{ms:g}ms",
                                  "message": "UI transition slower than the budget; hover and press should feel immediate"})
        if COLOUR_PROPS.match(prop):
            for col in COLOUR.findall(val):
                col = " ".join(col.lower().split())
                col = "#" + "".join(ch * 2 for ch in col[1:]) if re.fullmatch(r"#[0-9a-f]{3}", col) else col
                put("colour_values", col, loc)
                if col in ("#000000", "black", "rgb(0,0,0)", "rgb(0, 0, 0)") and prop == "color":
                    warns.append({"id": "pure-black", "where": loc, "value": col,
                                  "message": "pure black ink reads harsh; use a near-black from the palette"})
    def summary(vals: Dict[str, List[str]], limit: int) -> Dict:
        return {"distinct": len(vals), "budget": limit, "over": len(vals) > limit, "values":
                {v: {"count": len(locs), "first": locs[0]} for v, locs in sorted(vals.items(), key=lambda kv: -len(kv[1]))}}

    report = {cat: summary(vals, int(budget.get(cat, 99))) for cat, vals in cats.items()}
    hues: Dict[str, List[str]] = {}
    variants: Dict[str, List[str]] = {}
    for col, locs in cats["colour_values"].items():
        b = hue_bucket(col)
        if b is not None:
            hues.setdefault(f"{b * 30}-{b * 30 + 29}deg", []).extend(locs)
    for cls, line in buttons:
        variants.setdefault(cls, []).append(f"html:{line}")
    report["accent_hues"] = summary(hues, int(budget.get("accent_hues", 2)))
    report["button_variants"] = summary(variants, int(budget.get("button_variants", 2)))
    return {"categories": report, "warnings": warns,
            "token_use": round(100 * used_var / total) if total else 0, "declarations": total}


def render(path: str, res: Dict, fmt: str) -> str:
    """Format the report as text or JSON."""
    if fmt == "json":
        return json.dumps({"file": path, **res}, indent=2)
    lines = [f"consistency_check: {path}  ({res['declarations']} declarations, {res['token_use']}% through var())"]
    for cat, r in res["categories"].items():
        lines.append(f"  {'FAIL' if r['over'] else 'ok  '} {cat:<16} {r['distinct']:>3} distinct / budget {r['budget']}")
        if r["over"]:
            for v, info in list(r["values"].items())[:14]:
                lines.append(f"         {v:<34} x{info['count']:<3} {info['first']}")
    for w in res["warnings"][:25]:
        lines.append(f"  WARN {w['id']:<11} {w['where']:<22} {w['value']:<10} {w['message']}")
    over = sum(r["over"] for r in res["categories"].values())
    lines.append(f"  {over} categories over budget, {len(res['warnings'])} warnings")
    return "\n".join(lines)


def main() -> None:
    """CLI entry point."""
    ap = argparse.ArgumentParser(description="Count distinct spacing, radius, colour, font, shadow and motion values against a budget.")
    ap.add_argument("path", help="HTML page or CSS file")
    ap.add_argument("--css", action="append", default=[], help="extra stylesheet to include (repeatable)")
    ap.add_argument("--budget", default=str(DEFAULT_BUDGET), help="budget JSON (default: assets/site_budget.json)")
    ap.add_argument("--strict", action="store_true", help="treat warnings as failing")
    ap.add_argument("--format", choices=["text", "json"], default="text", help="output format")
    args = ap.parse_args()
    try:
        try:
            budget = validate_budget(json.loads(read(Path(args.budget))), ("system",))["system"]
        except ValueError as exc:
            raise InputError(f"budget {args.budget} is not valid JSON: {exc}") from exc
        sources, buttons = gather(Path(args.path), args.css)
        res = analyse(sources, buttons, budget)
    except InputError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(2)
    print(render(args.path, res, args.format))
    over = any(r["over"] for r in res["categories"].values())
    sys.exit(1 if over or (args.strict and res["warnings"]) else 0)


if __name__ == "__main__":
    main()
