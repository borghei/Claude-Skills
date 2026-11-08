#!/usr/bin/env python3
"""Static finish gate for a website page: structure, imagery, effects and weight.

From source, no browser: head tags, one h1, heading order, sections and words, hero
actions, every <img> (alt, dimensions, lazy, eager hero, weight), captions, fonts,
blocking scripts, effects (CSS or utility classes) by business kind, scroll reveals,
reduced motion, layout transitions, fixed elements and dead links.

Usage:
  python3 page_gate.py page.html --kind service
  python3 page_gate.py dist/index.html --kind tech --format json

Exit codes: 0 pass, 1 FAIL findings (or WARN with --strict), 2 bad input.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from typing import Dict, List, Optional

HERE = Path(__file__).resolve().parent
DEFAULT_BUDGET = HERE.parent / "assets" / "site_budget.json"
KINDS = ("tech", "product", "service", "place")
SKIP = {"script", "style", "template", "noscript", "svg"}
REVEAL_ATTR = ("data-aos", "data-scroll", "data-sal", "data-reveal", "data-parallax")
REVEAL_CLASS = re.compile(r"\b(reveal|fade-?in|fade-up|slide-?up|animate__\w+|wow|aos-\w+|parallax)\b")
HEAVY_LIB = re.compile(r"three(\.module)?(\.min)?\.js|gsap|scrolltrigger|lenis|locomotive|\baos\b|particles|lottie|vanta|barba", re.I)
EFFECT_CSS = {"gradient": r"(linear|radial|conic)-gradient\(", "backdrop-filter": r"backdrop-filter\s*:",
              "blur-filter": r"(?<!backdrop-)filter\s*:\s*[^;]*blur\(", "blend-mode": r"mix-blend-mode\s*:"}
UTILITY_EFFECT = {"gradient": r"bg-gradient-to-\w+|bg-(linear|radial|conic)-\S+", "backdrop-filter": r"backdrop-blur(-\w+)?",
                  "blur-filter": r"blur(-\w+)?", "blend-mode": r"mix-blend-\w+"}
MOTION_CSS = r"@keyframes|animation(-name)?\s*:\s*(?!none\b)|transition(-property)?\s*:\s*(?!none\b)"
LAYOUT_TRANSITION = re.compile(r"transition(-property)?\s*:[^;}]*?(?<![\w-])(width|height|max-height|top|left|right|bottom|margin|padding)(?![\w-])")
BODYISH = {"body", "header", "nav", "main", "section", "article", "div", "h1", "p", "footer"}


_spec = importlib.util.spec_from_file_location("consistency_check", HERE / "consistency_check.py")
CC = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(CC)  # shared helpers: read, local_file, line_at, validate_budget
InputError = CC.InputError  # unreadable or unusable input; mapped to exit code 2


class PageParser(HTMLParser):
    """Record the facts the gate needs in one pass over the page."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.lang = self.kind = self.title = self.desc = self.cur = self.text_tag = None
        self.viewport, self.head = False, True
        self.headings, self.sections, self.imgs, self.links, self.scripts, self.effects = [], [], [], [], [], []
        self.fonts, self.css, self.sheets, self.reveals, self.captions = [], [], [], [], []
        self.font_files = self.skip = self.in_main = self.sec_depth = self.util_motion = self.util_reduce = 0
        self.util: Dict[str, int] = {}  # utility-class effects (Tailwind and kin): kind -> first line

    def handle_starttag(self, tag: str, attrs: List) -> None:
        a = {k: (v if v is not None else "") for k, v in attrs}
        line = self.getpos()[0]
        if tag in SKIP:
            self.skip += 1
        if tag in BODYISH:
            self.head = False  # also covers pages with an implicit <body>
        if tag == "html":
            self.lang, self.kind = a.get("lang") or None, a.get("data-kind") or None
        elif tag == "title" and not self.skip and self.title is None:  # never an inline SVG's <title>
            self.text_tag, self.title = "title", ""
        elif tag == "meta":
            name = (a.get("name") or "").lower()
            self.desc = a.get("content", "") if name == "description" else self.desc
            self.viewport = self.viewport or name == "viewport"
            self.kind = self.kind or (a.get("content") if name == "site-kind" else None) or None
        elif tag == "link":
            rel, href = a.get("rel", "").lower(), a.get("href", "")
            if "fonts.googleapis.com" in href:
                self.fonts += [f.split(":")[0].replace("+", " ").lower() for f in re.findall(r"family=([^&]+)", href)]
            elif "stylesheet" in rel and href:  # remote sheets are dropped by CC.local_file
                self.sheets.append(href)
            self.font_files += "preload" in rel and a.get("as") == "font"
        elif tag == "script" and a.get("src"):
            self.scripts.append({"src": a["src"], "line": line, "head": self.head,
                                 "deferred": "defer" in a or "async" in a or a.get("type") == "module"})
        elif tag == "main":
            self.in_main += 1
        elif tag == "section" and self.in_main:
            if self.sec_depth == 0:
                self.cur = {"id": a.get("id", ""), "line": line, "words": 0, "heading": None, "actions": 0,
                            "hero": not self.sections or "hero" in a.get("class", "")}
                self.sections.append(self.cur)
            self.sec_depth += 1
        elif tag == "img":
            self.imgs.append({"line": line, "a": a, "hero": bool(self.cur and self.cur["hero"]) or not self.sections})
        elif tag in ("a", "button"):
            self.links.append({"line": line, "href": a.get("href"), "tag": tag})
            if self.cur and re.search(r"\b(btn|button|cta)\b", a.get("class", "")):
                self.cur["actions"] += 1
        elif tag == "canvas" or (tag == "video" and "autoplay" in a):
            self.effects.append({"kind": "canvas" if tag == "canvas" else "autoplay-video", "line": line})
        elif tag == "figcaption":
            self.captions.append(line)
        elif tag == "style":
            self.text_tag = "style"
        if re.match(r"h[1-6]$", tag):
            self.headings.append({"level": int(tag[1]), "line": line})
            if self.cur and self.cur["heading"] is None:
                self.cur["heading"] = int(tag[1])
        if a.get("style"):
            self.css.append(("x{" + a["style"] + "}", line, ""))
        if any(k in a for k in REVEAL_ATTR) or REVEAL_CLASS.search(a.get("class", "")):
            self.reveals.append(line)
        utils = [c.split(":")[-1] for c in a.get("class", "").split()]  # md:backdrop-blur-sm -> backdrop-blur-sm
        for name in [n for n, rx in UTILITY_EFFECT.items() if n not in self.util and any(re.fullmatch(rx, c) for c in utils)]:
            self.util[name] = line
        self.util_motion = self.util_motion or (line if any(re.fullmatch(r"animate-(?!none$)[\w-]+", c) for c in utils) else 0)
        self.util_reduce = self.util_reduce or bool(re.search(r"\bmotion-(reduce|safe):", a.get("class", "")))

    def handle_endtag(self, tag: str) -> None:
        if tag in SKIP:
            self.skip = max(0, self.skip - 1)
        if tag in ("title", "style"):
            self.text_tag = None
        if tag == "main":
            self.in_main = max(0, self.in_main - 1)
        if tag == "section" and self.sec_depth:
            self.sec_depth -= 1
            self.cur = self.cur if self.sec_depth else None

    def handle_data(self, data: str) -> None:
        if self.text_tag == "title":
            self.title += data
        elif self.text_tag == "style":
            self.css.append((data, self.getpos()[0], ""))
        elif not self.skip and self.cur is not None:
            self.cur["words"] += len(re.findall(r"[A-Za-zÀ-ɏ0-9][\w'’-]*", data))


def gate(path: Path, kind: Optional[str], b: Dict) -> Dict:
    """Parse the page and return the findings and summary counts."""
    raw = CC.read(path)
    if "<" not in raw or not re.search(r"<(html|body|main|section|div|h1|p)\b", raw, re.I):
        raise InputError(f"{path} does not look like an HTML page")
    p = PageParser()
    p.feed(raw)
    p.close()
    sheets = [CC.local_file(path, h) for h in p.sheets]
    p.css += [(f.read_text(encoding="utf-8", errors="replace"), 1, f.name) for f in sheets if f]
    strip = (re.sub(r"/\*.*?\*/", lambda m: "\n" * m.group(0).count("\n"), t, flags=re.S) for t, _, _ in p.css)
    chunks = [(t, ln, lb, [m.start() for m in re.finditer("\n", t)]) for t, (_, ln, lb) in zip(strip, p.css)]
    css = "\n".join(c[0] for c in chunks)
    declared, kind = kind or p.kind, (kind or p.kind or "product").lower()
    if kind not in KINDS:
        raise InputError(f"unknown kind '{kind}'; use one of {', '.join(KINDS)}")
    out: List[Dict] = []

    def add(sev: str, cid: str, line: int, msg: str) -> None:
        out.append({"severity": sev, "id": cid, "line": line, "message": msg})

    def css_hits(rx: str) -> List[tuple]:
        """(match, line, suffix): page lines for <style>/style="", 0 plus ' [sheet.css:N]' for linked sheets."""
        hits = []
        for text, base, label, nls in chunks:
            for m in re.finditer(rx, text, re.I):
                n = base + CC.line_at(nls, m.start())
                hits.append((m, 0, f" [{label}:{n}]") if label else (m, n, ""))
        return hits

    def css_at(rx: str) -> tuple:
        return (css_hits(rx) or [(None, 0, "")])[0][1:]

    def tiered(cid: str, lines: List[int], msg: str, fail_at: int = 4) -> None:
        for ln in lines:
            add("FAIL" if len(lines) >= fail_at else "WARN", cid, ln, f"{msg} ({len(lines)} on the page)")

    if not declared:
        add("WARN", "kind-missing", 1, "no <html data-kind> and no --kind: checked as a product page")
    for ok, cid, msg in ((p.lang, "lang", "<html> has no lang attribute"), (p.viewport, "viewport", "no meta viewport"),
                         ((p.title or "").strip(), "title", "no <title>")):
        if not ok:
            add("FAIL", cid, 1, msg)
    if not p.desc or (p.title or "").strip().lower() == p.desc.strip().lower():
        add("WARN", "description", 1, "meta description missing or repeats the title")
    h1 = [h for h in p.headings if h["level"] == 1]
    if len(h1) != 1:
        add("FAIL", "one-h1", h1[1]["line"] if len(h1) > 1 else 1, f"{len(h1)} h1 elements; a page has exactly one")
    for prev, cur in zip(p.headings, p.headings[1:]):
        if cur["level"] > prev["level"] + 1:
            add("WARN", "heading-order", cur["line"], f"h{prev['level']} jumps to h{cur['level']}")
    if len(p.sections) > b.get("max_sections", 10):
        add("WARN", "section-count", p.sections[-1]["line"], f"{len(p.sections)} sections; a long page loses its order past {b.get('max_sections', 10)}")
    for s in p.sections[1:]:
        if s["heading"] is None:
            add("WARN", "section-heading", s["line"], f"section {s['id'] or '(no id)'} has no heading naming what it holds")
        if s["words"] > b.get("max_words_per_section", 160):
            add("WARN", "section-words", s["line"], f"section {s['id'] or '(no id)'} has {s['words']} words; cut or split it")
    words = sum(s["words"] for s in p.sections)
    if words > b.get("max_total_words", 1100):
        add("WARN", "page-words", 1, f"{words} words in sections; move long copy to sub-pages")
    if p.sections and p.sections[0]["actions"] > b.get("max_hero_actions", 2):
        add("WARN", "hero-actions", p.sections[0]["line"], f"{p.sections[0]['actions']} buttons in the hero; budget {b.get('max_hero_actions', 2)}")

    tiered("img-alt", [i["line"] for i in p.imgs if "alt" not in i["a"]], "<img> without alt", 1)
    tiered("img-dims", [i["line"] for i in p.imgs if not ("width" in i["a"] and "height" in i["a"])
                        and "aspect-ratio" not in i["a"].get("style", "")], "<img> without width and height")
    tiered("img-lazy", [i["line"] for i in p.imgs if not i["hero"] and i["a"].get("loading") != "lazy"], "image below the hero not loading=lazy")
    eager = [i["line"] for i in p.imgs if i["hero"] and i["a"].get("loading") != "lazy"]
    if len(eager) > b.get("eager_images", 2):
        add("WARN", "eager-images", eager[-1], f"{len(eager)} eager images in the hero; the first screen should load one or two")
    total_kib = 0.0
    for i in p.imgs:
        if i["hero"] and i["a"].get("loading") == "lazy":
            add("WARN", "hero-lazy", i["line"], "hero image is lazy; load it eagerly with fetchpriority=high")
        src = i["a"].get("src", "")
        if src.startswith("data:") and len(src) * 3 / 4 / 1024 > b.get("inline_data_uri_kib", 40):
            add("WARN", "data-uri", i["line"], "large inline data: image; ship it as a file")
        if (local := CC.local_file(path, src)):
            kib = local.stat().st_size / 1024
            total_kib += kib
            if kib > b.get("image_warn_kib", 350):
                add("FAIL" if kib > b.get("image_fail_kib", 700) else "WARN", "img-weight", i["line"], f"{src} is {kib:.0f} KiB")
    if total_kib > b.get("images_total_warn_kib", 1200):
        add("FAIL" if total_kib > b.get("images_total_fail_kib", 2400) else "WARN", "img-total", 1, f"local images total {total_kib:.0f} KiB")
    for ln in p.captions:
        add("WARN", "caption", ln, "caption under a picture; a heading names the set, the picture shows the thing")

    families = set(p.fonts) | {f.strip("'\" ").lower() for f in re.findall(r"@font-face\s*\{[^}]*font-family\s*:\s*([^;}]+)", css)}
    if len(families) > b.get("max_font_families", 2):
        add("FAIL" if len(families) > b.get("max_font_families", 2) + 1 else "WARN", "font-families", 1, f"{len(families)} font families: {', '.join(sorted(families))}")
    files = p.font_files + len(re.findall(r"@font-face", css))
    if files > b.get("max_font_files", 4):
        add("WARN", "font-files", 1, f"{files} font files; request only the weights the page uses")
    for s in p.scripts:
        if s["head"] and not s["deferred"]:
            add("WARN", "blocking-script", s["line"], f"{s['src']} blocks rendering; add defer or type=module")
        if HEAVY_LIB.search(s["src"]):
            p.effects.append({"kind": "library " + Path(s["src"]).name, "line": s["line"]})
    for name, rx in EFFECT_CSS.items():  # static CSS effects count against the budget but do not move
        if re.search(rx, css, re.I):
            p.effects.append({"kind": name + css_at(rx)[1], "line": css_at(rx)[0], "static": True})
        elif name in p.util:
            p.effects.append({"kind": name + " (utility class)", "line": p.util[name], "static": True})
    allowed = b.get("effects_allowed", {}).get(kind, 0)
    if len(p.effects) > allowed:
        for e in p.effects:
            add("WARN" if kind == "tech" else "FAIL", "effects", e["line"], f"{e['kind']}: a {kind} page gets {allowed} effect(s), this one has {len(p.effects)}")
    tiered("scroll-reveal", p.reveals, "element revealed on scroll; content should stand at rest", 3)
    for _, ln, sfx in css_hits(r"scroll-snap-type")[:1]:
        add("WARN", "scroll-snap", ln, "scroll-snap steers the reader's scroll" + sfx)
    moving = [e for e in p.effects if not e.get("static")]
    if (re.search(MOTION_CSS, css, re.I) or p.util_motion or moving) and "prefers-reduced-motion" not in css and not p.util_reduce:
        ln, sfx = css_at(MOTION_CSS) if re.search(MOTION_CSS, css, re.I) else (p.util_motion or moving[0]["line"], "")
        add("FAIL", "reduced-motion", ln, "the page moves but has no prefers-reduced-motion rule" + sfx)
    for m, ln, sfx in css_hits(LAYOUT_TRANSITION.pattern):
        add("WARN", "layout-transition", ln, f"transition on {m.group(2)}; animate transform and opacity only{sfx}")
    for _, ln, sfx in css_hits(r"transition\s*:\s*all\b"):
        add("WARN", "transition-all", ln, "transition: all animates layout by accident; name the properties" + sfx)
    fixed = len(re.findall(r"position\s*:\s*(fixed|sticky)", css))
    if fixed > b.get("max_fixed_elements", 1):
        ln, sfx = css_at(r"position\s*:\s*(fixed|sticky)")
        add("WARN", "fixed-elements", ln, f"{fixed} fixed or sticky rules; only the header should stay put{sfx}")
    for ln in p.links:
        href = ln["href"]
        if ln["tag"] == "a" and (href is None or href.strip() in ("", "#") or href.lower().startswith("javascript:")):
            add("FAIL", "dead-link", ln["line"], f"link with href={href!r} goes nowhere")
    out.sort(key=lambda f: (f["line"], f["id"]))
    return {"file": str(path), "kind": kind, "sections": len(p.sections), "words": words, "images": len(p.imgs),
            "effects": len(p.effects), "font_families": sorted(families), "findings": out}


def main() -> None:
    """CLI entry point."""
    ap = argparse.ArgumentParser(description="Static structure, imagery, effects and weight gate for a website page.")
    ap.add_argument("path", help="HTML page")
    ap.add_argument("--kind", choices=KINDS, help="business kind (default: <html data-kind> or meta site-kind, else product)")
    ap.add_argument("--budget", default=str(DEFAULT_BUDGET), help="budget JSON (default: assets/site_budget.json)")
    ap.add_argument("--strict", action="store_true", help="treat WARN as failing")
    ap.add_argument("--format", choices=["text", "json"], default="text", help="output format")
    args = ap.parse_args()
    try:
        budget = CC.validate_budget(json.loads(CC.read(Path(args.budget))), ("page",))["page"]
        res = gate(Path(args.path), args.kind, budget)
    except (InputError, OSError, ValueError) as exc:  # ValueError: the budget is not valid JSON
        print(f"error: {'budget is not valid JSON: ' if isinstance(exc, ValueError) else ''}{exc}", file=sys.stderr)
        sys.exit(2)
    fails = sum(f["severity"] == "FAIL" for f in res["findings"])
    if args.format == "json":
        print(json.dumps(res, indent=2))
    else:
        print(f"page_gate: {res['file']}  kind={res['kind']} sections={res['sections']} words={res['words']} "
              f"images={res['images']} effects={res['effects']} fonts={len(res['font_families'])}")
        for f in res["findings"]:
            print(f"  {f['severity']:4} L{f['line'] or '-':<4} {f['id']:<17} {f['message']}")
        print(f"  {fails} FAIL, {len(res['findings']) - fails} WARN")
    sys.exit(1 if fails or (args.strict and res["findings"]) else 0)


if __name__ == "__main__":
    main()
