#!/usr/bin/env python3
"""Tolerant CSS reader for the interface detector.

Turns stylesheets, SCSS/LESS nesting, JSX style objects and css/styled
template literals into (selector, [(property, value, line)]) blocks in one
linear pass, so large and minified files stay fast. css_checks.py runs the
rules over these blocks; this CLI prints the blocks, for debugging a parse.

Usage:
  python3 css_parse.py --input styles.css --format text

Exit codes: 0 parsed, 2 bad input (missing or unreadable file).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from typing import List, Optional, Tuple

Decl = Tuple[str, str, int]  # property, value, line
TEMPLATE = re.compile(r"(?<![\w.])(?:css|styled(?:\.\w+|\([^)]*\))(?:\.attrs\([^)]*\))?)\s*`")
PX_PROPS = ("font-size", "letter-spacing", "border-radius", "border-left-width", "border-right-width",
            "padding", "margin", "gap")
NUM = re.compile(r"(-?\d*\.?\d+)(px|rem|em)?")


def strip_comments(text: str) -> str:
    return re.sub(r"/\*.*?\*/", lambda m: re.sub(r"[^\n]", " ", m.group(0)), text, flags=re.S)


def split_top(text: str, seps: str) -> List[Tuple[str, int]]:
    """Split on separators outside quotes and parentheses; keep each part's offset."""
    parts, depth, quote, start = [], 0, "", 0
    for i, ch in enumerate(text):
        if quote:
            quote = "" if ch == quote else quote
        elif ch in "'\"`":
            quote = ch
        elif ch == "(":
            depth += 1
        elif ch == ")":
            depth = max(0, depth - 1)
        elif ch in seps and depth == 0:
            parts.append((text[start:i], start))
            start = i + 1
    parts.append((text[start:], start))
    return parts


def kebab(prop: str) -> str:
    prop = prop.strip().strip("'\"")
    if prop.startswith("--") or "-" in prop:
        return prop.lower()
    out = re.sub(r"([A-Z])", lambda m: "-" + m.group(1).lower(), prop)
    return "-" + out[1:] if out.startswith("webkit") or out.startswith("moz") else out


def parse_decls(body: str, first_line: int, js: bool) -> List[Decl]:
    decls = []
    for part, off in split_top(body, ",;\n" if js else ";"):
        if ":" not in part:
            continue
        prop, value = part.split(":", 1)
        prop = kebab(prop)
        if not re.fullmatch(r"-?-?[a-z][a-z0-9-]*", prop):
            continue
        value = value.strip()
        if len(value) > 1 and value[0] == value[-1] and value[0] in "'\"`":
            value = value[1:-1].strip()
        if js and re.fullmatch(r"-?\d*\.?\d+", value) and prop in PX_PROPS:
            value += "px"
        line = first_line + body[:off + len(part) - len(part.lstrip())].count("\n")
        decls.append((prop, value, line))
    return decls


def expr_end(text: str, i: int) -> int:
    """Index just past the '}' closing the ${ at text[i]; nested templates are skipped whole."""
    depth, i = 1, i + 2
    while i < len(text) and depth:
        if text[i] == "`":
            i = template_end(text, i)
        elif text[i] in "{}":
            depth += 1 if text[i] == "{" else -1
        i += 1
    return i


def template_end(text: str, i: int) -> int:
    """Index of the backtick closing the template opened at text[i]."""
    i += 1
    while i < len(text) and text[i] != "`":
        i = i + 2 if text[i] == "\\" else expr_end(text, i) if text.startswith("${", i) else i + 1
    return i


def blank(s: str) -> str:
    return re.sub(r"[^\n]", " ", s)


def blanked(text: str, start: int, end: int, spans: List[Tuple[int, int]]) -> str:
    """text[start:end] with each (a, b) span blanked, newlines kept; linear in the length."""
    out, at = [], start
    for a, b in spans:
        out += [text[at:a], blank(text[a:b])]
        at = b
    return "".join(out) + text[at:end]


def extract_blocks(text: str, line0: int = 1, js: bool = False,
                   top: Optional[str] = None) -> List[Tuple[str, List[Decl]]]:
    """{...} blocks innermost first, nested blocks blanked out of their parents (SCSS/LESS
    nesting keeps the parent's own declarations); top-level text becomes a block when `top` is set.
    One linear pass with a stack, so large and minified stylesheets stay fast."""
    text, blocks = strip_comments(text), []
    if js:
        spans = []
        for m in TEMPLATE.finditer(text):
            if spans and m.start() < spans[-1][1]:
                continue  # css`` nested in a styled template: handled with its parent below
            end = template_end(text, m.end() - 1)
            exprs, i = [], m.end()
            while (i := text.find("${", i, end)) >= 0:
                exprs.append((i, min(expr_end(text, i), end)))
                for inner in TEMPLATE.finditer(text, exprs[-1][0], exprs[-1][1]):
                    blocks += extract_blocks(text[inner.end():template_end(text, inner.end() - 1)],
                                             line0 + text.count("\n", 0, inner.end()), top="")
                i = exprs[-1][1]
            tag = re.search(r"styled\.(\w+)", m.group(0))
            blocks += extract_blocks(blanked(text, m.end(), end, exprs), line0 + text.count("\n", 0, m.end()),
                                     top=tag.group(1) if tag else "")
            spans.append((m.start(), min(end + 1, len(text))))
        text = blanked(text, 0, len(text), spans)
    stack: List[list] = []  # [selector, body start, line, child spans, selector start]
    kids: List[Tuple[int, int]] = []
    last, nl, line = -1, 0, line0
    for m in re.finditer(r"[{};]", text):
        at, ch = m.start(), m.group(0)
        line, nl = line + text.count("\n", nl, at), at
        if ch == "{":
            stack.append([text[last + 1:at], at + 1, line, [], last + 1])
        elif ch == "}" and stack:
            selector, start, first, spans, sel_at = stack.pop()
            body = blanked(text, start, at, spans)
            selector = " ".join(selector.split())
            if js:  # JS objects: only a quoted nested key ('& h1': {...}) is a selector
                key = re.search(r"['\"]([^'\"]+)['\"]\s*:\s*$", selector)
                selector = key.group(1) if key else ""
            blocks.append((selector, parse_decls(body, first, js and ";" not in body)))
            (stack[-1][3] if stack else kids).append((sel_at, at + 1))
        last = at
    if top is not None:
        blocks.append((top, parse_decls(blanked(text, 0, len(text), kids), line0, False)))
    return blocks


def px(value: str, base: float = 16.0) -> Optional[float]:
    m = NUM.search(value or "")
    if not m:
        return None
    n, unit = float(m.group(1)), m.group(2)
    return n * base if unit in ("rem", "em") else n if unit == "px" or n == 0 else None


def main(argv: Optional[List[str]] = None) -> int:
    p = argparse.ArgumentParser(description="Print the CSS blocks the detector reads from a file.")
    p.add_argument("--input", required=True, help="Stylesheet, markup or JSX/TSX file")
    p.add_argument("--format", choices=("text", "json"), default="text", help="Output format")
    args = p.parse_args(argv)
    try:
        with open(args.input, encoding="utf-8") as fh:
            text = fh.read()
    except (OSError, UnicodeDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    blocks = extract_blocks(text, js=args.input.lower().endswith((".jsx", ".tsx", ".js", ".ts")))
    if args.format == "json":
        print(json.dumps([{"selector": s, "declarations": d} for s, d in blocks], indent=2))
    else:
        for selector, decls in blocks:
            print(f"{selector or '(no selector)'}: " + "; ".join(f"L{ln} {p}: {v}" for p, v, ln in decls))
        print(f"{len(blocks)} block(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
