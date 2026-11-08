#!/usr/bin/env python3
"""Structural checks for the interface detector over HTML, JSX, TSX, Vue and Svelte.

Walks the element tree with a tolerant parser and flags shapes no single
declaration reveals: cards inside cards, eyebrow labels and icon tiles stacked
over headings, chip soup, rows of identical cards, mostly-bold text, emoji
icons, vague control labels and headlines, skipped heading levels and section
numbering. Classes, inline styles and <style> blocks are handed to
class_checks.py and css_checks.py. ui_slop_detector.py is the entry point.

Usage:
  python3 markup_checks.py --input page.html --format text

Exit codes: 0 no findings, 1 findings, 2 bad input.
"""

from __future__ import annotations

import argparse
import importlib.util
import re
import sys
from pathlib import Path
from html.parser import HTMLParser
from typing import List, Optional


def _load(name: str):
    """Load a sibling module from this scripts/ folder (keeps the package self-contained)."""
    if name not in sys.modules:
        spec = importlib.util.spec_from_file_location(name, Path(__file__).with_name(f"{name}.py"))
        sys.modules[name] = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(sys.modules[name])
    return sys.modules[name]


K = _load("class_checks")
C = _load("css_checks")
R = _load("ui_rules")


CLOSES = {"p": set("p div section article aside header footer nav main form table ul ol dl pre blockquote figure "
                   "h1 h2 h3 h4 h5 h6 hr".split()), "li": {"li"}}  # start tags that close an open <p> / <li>
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}
HEADINGS = {"h1": 1, "h2": 2, "h3": 3, "h4": 4, "h5": 5, "h6": 6}
TEXT_TAGS = {"p", "li", "span", "a", "button", "td", "label", "dd", "small"}
ICON_CONTEXT = {"button", "a", "li", "nav", "label", "th", "dt", "h1", "h2", "h3", "h4"}
EMOJI = re.compile("[\U0001F300-\U0001FAFF\U0001F000-\U0001F2FF☀-➿⭐⭕]")
VAGUE_LABELS = {"submit", "ok", "okay", "yes", "no", "click here", "here", "go", "click", "this link", "button"}
VAGUE_HEADLINES = [re.compile(p, re.I) for p in (
    r"^welcome to\b", r"\ball[- ]in[- ]one\b", r"^the future of\b", r"^unlock (the|your)\b",
    r"^(supercharge|elevate|transform|revolutioni[sz]e|empower|level up) your\b",
    r"^(built|designed|made) for (the )?(modern|you|everyone|teams)\b", r"^everything you need\b",
    r"^(your|the) (ultimate|complete|only) .*\b(solution|platform|toolkit|hub)\b",
    r"^next[- ]gen(eration)?\b", r"^reimagin(e|ing)\b", r"^(work|build|ship) smarter\b")]
SECTION_NUMBER = re.compile(r"^\(?0\d\)?[.)/:—-]?$|^\d{2}\s*/\s*\d{2}$")
FONT_LINK = re.compile(r"fonts\.googleapis\.com/css2?\?(.*)", re.I)


LITERAL = re.compile(r"\"([^\"]*)\"|'([^']*)'|`([^`]*)`")


def class_exprs(text: str) -> str:
    """className={cn("a", cond && "b")} or class={...} -> class="a b": every string literal in the
    expression counts (conditional classes apply some of the time). Newlines are kept."""
    out, i = [], 0
    for m in re.finditer(r"(?<![\w:-])(?:className|class)=\{", text):
        if m.start() < i:
            continue
        depth, j = 1, m.end()
        while j < len(text) and depth:
            depth += {"{": 1, "}": -1}.get(text[j], 0)
            j += 1
        expr = text[m.end():j - 1]
        words = " ".join("".join(g) for g in LITERAL.findall(expr))
        out += [text[i:m.start()], 'class="' + re.sub(r"\$\{[^}]*\}|\"", " ", words) + '"' + "\n" * expr.count("\n")]
        i = j
    return "".join(out) + text[i:]


def prepare_jsx(text: str, generics: bool = True) -> str:
    """Make JSX/TSX (or Svelte markup, generics=False) parseable as markup without moving any line."""
    text = text.replace("=>", "=_")
    if generics:
        text = re.sub(r"(?<=[\w\]])<[A-Za-z_][\w.,\s\[\]|]*>", lambda m: " " * len(m.group(0)), text)
    return class_exprs(text)


class Tree(HTMLParser):
    """Single-pass walker; findings accumulate in self.findings."""

    def __init__(self, path: str, cat: dict, ctx: dict):
        super().__init__(convert_charrefs=True)
        self.path, self.cat, self.ctx = path, cat, ctx
        self.stack: List[dict] = []
        self.root = {"tag": "#root", "children": [], "card": False, "ground": None, "page": False,
                     "chips": 0, "text": [], "line": 1, "heading": False, "icon": False,
                     "attrs": {}, "classes": [], "kicker": False, "tile": False, "bold": False, "photo": False}
        self.root["ground"] = ctx.get("page_ground")
        self.findings: List[dict] = []
        self.last_level = 0
        self.text_elems = self.bold_elems = 0
        self.first_bold = 0
        self.chips: List[int] = []
        self.numbers: List[int] = []
        self.in_raw = ""

    def hit(self, rule: str, line: int, evidence: str, severity: Optional[str] = None) -> None:
        self.findings.append(R.make_finding(self.cat, rule, self.path, line, evidence, severity))

    def parent(self) -> dict:
        return self.stack[-1] if self.stack else self.root

    def handle_starttag(self, tag, attrs):
        for open_tag, closers in CLOSES.items():
            if tag in closers and self.stack and self.stack[-1]["tag"] == open_tag:
                self.handle_endtag(open_tag)
        line = self.getpos()[0]
        a = {k: (v or "") for k, v in attrs}
        bound = " ".join("".join(g) for g in LITERAL.findall(a.get(":class", "") + a.get("v-bind:class", "")))
        classes = (a.get("class", "") + " " + a.get("classname", "") + " " + bound).split()
        style = a.get("style", "")
        parent = self.parent()
        ancestors = self.stack
        src = a.get("src", "") or a.get(":src", "")
        photo = None if tag != "img" else bool(src) and not re.search(r"\.svg(\?|$)|icon", src, re.I)
        node = {"tag": tag, "classes": classes, "line": line, "children": [], "text": [], "chips": 0,
                "card": K.is_card(tag, classes) and a.get("role") not in ("dialog", "alertdialog"), "kicker": K.is_kicker(classes, style.lower()),
                "tile": K.is_icon_tile(classes), "bold": K.is_bold(classes) or bool(
                    re.search(r"font-weight\s*:\s*(bold|[6-9]00)", style)),
                "ground": K.ground(classes) or parent["ground"], "heading": tag in HEADINGS,
                "icon": tag in ("svg", "i") or tag.endswith("icon") or (tag == "img" and photo is False),
                "photo": bool(photo),
                "page": tag in ("body", "html", "main") or "min-h-screen" in classes, "attrs": a}
        if tag in HEADINGS:
            self.on_heading(tag, line, parent)
        if node["card"] and any(n["card"] for n in ancestors):
            outer = next(n for n in reversed(ancestors) if n["card"])
            self.hit("nested-cards", line, f"<{tag}> card inside the card opened at line {outer['line']}")
        if K.is_chip(tag, classes) and not any(n["tag"] in ("td", "th") for n in ancestors):  # status columns
            self.chips.append(line)
            holder = next((n for n in reversed(ancestors) if n["card"]), None)
            if holder:
                holder["chips"] += 1
        if classes:
            env = {"ctx": self.ctx, "ground": parent["ground"], "page": node["page"]}
            self.findings += K.check_classes(tag, classes, line, self.path, self.cat, env)
        if style:
            self.findings += C.check_block(tag, C.parse_decls(style, line, False), self.path, self.cat, self.ctx)
        if tag == "marquee":
            self.hit("marquee-scroll", line, "<marquee> element")
        if tag == "link" and FONT_LINK.search(a.get("href", "")):
            for fam in re.findall(r"family=([^:&;]+)", FONT_LINK.search(a["href"]).group(1)):
                if fam.replace("+", " ").lower() in C.OVERUSED:
                    self.hit("overused-face", line, f"font link loads {fam.replace('+', ' ')}")
        if tag in ("style", "script"):
            self.in_raw = tag
        if tag in VOID:
            self.close(node, parent)
        else:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID and self.stack and self.stack[-1]["tag"] == tag:
            self.handle_endtag(tag)

    def on_heading(self, tag: str, line: int, parent: dict) -> None:
        level = HEADINGS[tag]
        if self.last_level and level > self.last_level + 1:
            self.hit("skipped-heading", line, f"h{self.last_level} followed by {tag}")
        self.last_level = level
        prev = parent["children"][-1] if parent["children"] else None
        if prev and level <= 3 and prev["tag"] in ("p", "span", "div", "small", "strong"):
            words = " ".join(prev["text"]).strip()
            if prev["kicker"] and 0 < len(words) <= 48:
                self.hit("kicker-above-heading", prev["line"], f'"{words}" above <{tag}>')
            elif prev["tile"] and prev["icon"]:
                self.hit("icon-tile-stack", prev["line"], f"icon tile above <{tag}>")

    def handle_endtag(self, tag):
        if self.in_raw == tag:
            self.in_raw = ""
        if not any(n["tag"] == tag for n in self.stack):
            return
        while self.stack:
            node = self.stack.pop()
            self.close(node, self.parent())
            if node["tag"] == tag:
                break

    def close(self, node: dict, parent: dict) -> None:
        text = " ".join(" ".join(node["text"]).split())
        tag, line = node["tag"], node["line"]
        parent["children"].append(node)
        parent["text"].append(text)
        parent["heading"] = parent["heading"] or node["heading"]
        parent["icon"] = parent["icon"] or node["icon"]
        parent["photo"] = parent.get("photo") or node["photo"]
        if node["card"] and node["chips"] >= 4:
            self.hit("chip-soup", line, f"{node['chips']} chips inside one card")
        is_button = tag == "button" or node["attrs"].get("role") == "button" or any(
            c in ("btn", "button") or c.startswith("btn-") for c in node["classes"])
        label = text.lower().strip(" .!:→>")
        if tag == "input" and node["attrs"].get("type") in ("submit", "button"):
            label, is_button = node["attrs"].get("value", "").lower().strip(), True
        if (is_button or tag == "a") and label in VAGUE_LABELS:
            self.hit("vague-control-label", line, f'<{tag}> "{label}"')
        if tag in ("h1", "h2") and any(p.search(text) for p in VAGUE_HEADLINES):
            self.hit("vague-headline", line, f'<{tag}> "{text[:80]}"')
        if SECTION_NUMBER.match(text) and not node["children"]:
            self.numbers.append(line)
        if tag in TEXT_TAGS and text:
            self.text_elems += 1
            if node["bold"]:
                self.bold_elems += 1
                self.first_bold = self.first_bold or line
        kids = node["children"]
        run = 1
        for i in range(1, len(kids) + 1):
            same = i < len(kids) and kids[i]["classes"] and kids[i]["classes"] == kids[i - 1]["classes"] \
                and kids[i]["tag"] == kids[i - 1]["tag"]
            if same:
                run += 1
                continue
            first = kids[i - run]
            row = kids[i - run:i]  # product and media grids (a photo in every card) are content, not a template
            if run >= 3 and all(k["heading"] for k in row) and (first["card"] or first["icon"]) \
                    and not all(k["photo"] for k in row):
                self.hit("identical-card-row", first["line"], f"{run} <{first['tag']}> siblings share one class list")
            run = 1

    def handle_data(self, data):
        if self.in_raw == "style":
            found, _ = C.scan_text(data, self.path, self.cat, line0=self.getpos()[0], ctx=self.ctx)
            self.findings += found
            return
        if self.in_raw or not data.strip():
            return
        node = self.parent()
        node["text"].append(data)
        stripped = data.strip()
        alone = len(stripped) <= 3 and EMOJI.match(stripped)
        if EMOJI.search(stripped) and (alone or node["tag"] in ICON_CONTEXT or "icon" in " ".join(node["classes"])
                                       or (node["tag"] == "p" and EMOJI.match(stripped))):
            node["icon"] = True
            self.hit("emoji-icon", self.getpos()[0], f"<{node['tag']}> {stripped[:40]}")

    def finish(self) -> List[dict]:
        while self.stack:
            node = self.stack.pop()
            self.close(node, self.parent())
        self.close(self.root, {"children": [], "text": [], "heading": False, "icon": False, "photo": False})
        if self.text_elems >= 8 and self.bold_elems / self.text_elems >= 0.5:
            self.hit("everything-bold", self.first_bold, f"{self.bold_elems} of {self.text_elems} text elements are bold")
        if len(self.chips) >= 12 and not any(f["rule"] == "chip-soup" for f in self.findings):
            self.hit("chip-soup", self.chips[0], f"{len(self.chips)} chips in one file")
        if len(self.numbers) >= 3:
            self.hit("numbered-section-labels", self.numbers[0], f"{len(self.numbers)} bare section numbers")
        seen, out = set(), []
        for f in self.findings:
            key = (f["line"], f["rule"])
            if key not in seen:
                seen.add(key)
                out.append(f)
        return out


def scan_markup(text: str, path: str, cat: dict, ctx: dict) -> List[dict]:
    """Findings for one markup file; JSX-family files are prepared first."""
    jsx = path.lower().endswith((".jsx", ".tsx", ".js", ".ts"))
    tree = Tree(path, cat, ctx)
    tree.feed(prepare_jsx(text) if jsx else prepare_jsx(text, False) if path.lower().endswith(".svelte") else text)
    findings = tree.finish()
    if jsx:
        found, _ = C.scan_text(text, path, cat, js=True, ctx=ctx)
        findings += [f for f in found if (f["line"], f["rule"]) not in {(x["line"], x["rule"]) for x in findings}]
    return findings


def main(argv: Optional[List[str]] = None) -> int:
    p = argparse.ArgumentParser(description="Run the structural interface rules over markup files.")
    p.add_argument("--input", nargs="+", required=True, help="HTML/JSX/TSX/Vue/Svelte files")
    p.add_argument("--format", choices=("text", "json"), default="text", help="Output format")
    args = p.parse_args(argv)
    findings: List[dict] = []
    try:
        cat = R.load_catalog()
        for path in args.input:
            with open(path, encoding="utf-8") as fh:
                text = fh.read()
            findings += scan_markup(text, path, cat, C.new_context(text))
    except (OSError, UnicodeDecodeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return R.print_findings(findings, args.format)


if __name__ == "__main__":
    sys.exit(main())
