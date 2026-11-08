#!/usr/bin/env python3
"""Static access, links, forms, head and shell check for a website page.

Checks from source, no browser: every control has a name, every field a visible
label and the right type, no positive tabindex, a skip link, a menu button that
states its state, share tags and an icon, forms that really send, in-page links
that land, one label per target, buttons that start with a verb, the main action
worded the same in the hero and further down, no carousel or chat widget, no
embedded map, and no code that detects a headless checker. Elements marked
data-assumed (prices or hours the brief did not give) are listed for the report.

Usage:
  python3 access_links_check.py page.html
  python3 access_links_check.py dist/index.html --format json --strict

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
from typing import Dict, List

VERBS = set("""book buy order pre-order preorder reserve try start get download compare see watch read find join
subscribe sign contact configure add send email request call visit view open plan check apply donate shop rent hire
claim register create build install upgrade choose pick schedule ask talk write message browse meet test begin
reach skip""".split())
NO_LABEL_TYPES = {"hidden", "submit", "button", "reset", "image"}
CAROUSEL = re.compile(r"\b(swiper|slick|splide|glide|flickity|owl-carousel|embla|carousel|slideshow|marquee)\b", re.I)
WIDGET = re.compile(r"intercom|crisp\.chat|drift\.com|tawk\.to|zendesk|livechat|tidio|hs-scripts|olark", re.I)
POPUP = re.compile(r"\b(modal|popup|pop-up|lightbox-newsletter|newsletter-modal|exit-intent)\b", re.I)
GAMING = re.compile(r"navigator\.webdriver|HeadlessChrome|__playwright|callPhantom|_phantom|__nightmare|/headless/i", re.I)


class InputError(Exception):
    """Raised for unreadable or unusable input; mapped to exit code 2."""


_spec = importlib.util.spec_from_file_location("consistency_check", Path(__file__).resolve().parent / "consistency_check.py")
CC = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(CC)  # shared helper: local_file (relative and root-relative paths)


class AccessParser(HTMLParser):
    """Collect controls, fields, labels, links, head tags and scripts in one pass."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids, self.label_for, self.meta, self.icons = set(), set(), {}, []
        self.controls: List[Dict] = []  # open and closed <a>/<button>
        self.open: List[Dict] = []
        self.fields: List[Dict] = []
        self.forms: List[Dict] = []
        self.scripts: List[Dict] = []
        self.other: List[Dict] = []  # carousel, widget, popup, map, assumed, tabindex
        self.stack: List[str] = []
        self.label_depth = self.main_seen = self.sections = 0
        self.in_script, self.lang, self.main_id = None, "", ""

    def handle_starttag(self, tag: str, attrs: List) -> None:
        a = {k: (v if v is not None else "") for k, v in attrs}
        line = self.getpos()[0]
        if a.get("id"):
            self.ids.add(a["id"])
        cls = a.get("class", "")
        if tag == "html":
            self.lang = a.get("lang", "").lower()
        if tag == "main":
            self.main_seen, self.main_id = 1, a.get("id", "")
        if tag == "section" and self.main_seen and "section" not in self.stack:
            self.sections += 1
        if tag == "label":
            self.label_depth += 1
            if a.get("for"):
                self.label_for.add(a["for"])
        elif tag == "meta":
            key = (a.get("property") or a.get("name") or "").lower()
            if key:
                self.meta[key] = a.get("content", "")
        elif tag == "link" and "icon" in a.get("rel", "").lower().split():
            self.icons.append(line)
        elif tag in ("a", "button"):
            c = {"tag": tag, "line": line, "a": a, "text": "", "img_alt": False, "section": self.sections,
                 "chrome": any(t in self.stack for t in ("nav", "header", "footer")), "pre_main": not self.main_seen}
            self.controls.append(c)
            self.open.append(c)
        elif tag == "img" and self.open and a.get("alt", "").strip():
            self.open[-1]["img_alt"] = True
        elif tag in ("input", "select", "textarea") and a.get("type", "").lower() not in NO_LABEL_TYPES:
            self.fields.append({"tag": tag, "line": line, "a": a, "wrapped": self.label_depth > 0})
        elif tag == "form":
            self.forms.append({"line": line, "a": a})
        elif tag == "script":
            self.in_script = {"line": line, "src": a.get("src", ""), "code": ""}
            self.scripts.append(self.in_script)
        elif tag == "iframe" and re.search(r"maps?\.|/maps", a.get("src", ""), re.I):
            self.other.append({"id": "map-embed", "line": line})
        elif tag in ("marquee", "dialog"):
            self.other.append({"id": "carousel" if tag == "marquee" else "popup", "line": line})
        if CAROUSEL.search(cls):
            self.other.append({"id": "carousel", "line": line})
        if POPUP.search(cls):
            self.other.append({"id": "popup", "line": line})
        if "data-assumed" in a:
            self.other.append({"id": "assumed", "line": line})
        if re.fullmatch(r"\d+", a.get("tabindex", "").strip()) and int(a["tabindex"]) > 0:
            self.other.append({"id": "tabindex", "line": line})
        if tag not in ("br", "img", "input", "meta", "link", "hr", "source", "wbr"):
            self.stack.append(tag)

    def handle_endtag(self, tag: str) -> None:
        if tag == "label":
            self.label_depth = max(0, self.label_depth - 1)
        if tag in ("a", "button"):
            for i in range(len(self.open) - 1, -1, -1):
                if self.open[i]["tag"] == tag:
                    self.open.pop(i)
                    break
        if tag == "script":
            self.in_script = None
        if tag in self.stack:
            while self.stack and self.stack.pop() != tag:
                pass

    def handle_data(self, data: str) -> None:
        if self.in_script is not None:
            self.in_script["code"] += data
            return
        for c in self.open:
            c["text"] += data


def label_of(c: Dict) -> str:
    """Visible label of a control, whitespace and emoji collapsed."""
    return " ".join(re.sub(r"[^\w'&,.\- ]+", " ", c["text"]).split())


def check(path: Path) -> Dict:
    """Parse the page and return findings plus the assumed-fact list."""
    if not path.is_file():
        raise InputError(f"file not found: {path}")
    try:
        raw = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise InputError(f"cannot read {path}: {exc}") from exc
    if "<" not in raw or not re.search(r"<(html|body|main|section|div|h1|p)\b", raw, re.I):
        raise InputError(f"{path} does not look like an HTML page")
    p = AccessParser()
    p.feed(raw)
    p.close()
    out: List[Dict] = []

    def add(sev: str, cid: str, line: int, msg: str) -> None:
        out.append({"severity": sev, "id": cid, "line": line, "message": msg})

    for c in p.controls:
        a = c["a"]
        named = label_of(c) or c["img_alt"] or any(a.get(k, "").strip() for k in ("aria-label", "aria-labelledby", "title"))
        if not named:
            add("FAIL", "a11y-name", c["line"], f"<{c['tag']}> has no name: add visible text or aria-label in the page's language")
        if c["tag"] == "button" and re.search(r"toggle|menu|burger|hamburger", a.get("class", ""), re.I) and "aria-expanded" not in a:
            add("WARN", "menu-toggle", c["line"], "menu button without aria-expanded: it must say whether the menu is open")
        href = a.get("href", "")
        if c["tag"] == "a" and href.startswith("#") and href not in ("#", "#top") and href[1:] not in p.ids:
            add("FAIL", "anchor-target", c["line"], f"link to {href} lands nowhere: no element has that id")
    for f in p.fields:
        a = f["a"]
        visible = f["wrapped"] or (a.get("id") and a["id"] in p.label_for)
        if not visible:
            hint = " (a placeholder is not a label)" if a.get("placeholder") else ""
            sev = "WARN" if a.get("aria-label") or a.get("aria-labelledby") else "FAIL"
            add(sev, "field-label", f["line"], f"<{f['tag']}> has no visible <label>{hint}")
        name = (a.get("name", "") + " " + a.get("id", "")).lower()
        if f["tag"] == "input" and "email" in name and a.get("type", "text").lower() != "email":
            add("WARN", "field-type", f["line"], "email field is not type=email: phones show the wrong keyboard")
        if a.get("type", "").lower() == "email" and not a.get("autocomplete"):
            add("WARN", "field-type", f["line"], "email field without autocomplete=email")
    for f in p.forms:
        action = f["a"].get("action")
        if not f["a"].get("data-endpoint") and (action is None or action.strip() in ("", "#") or action.lower().startswith("javascript:")):
            add("FAIL", "form-action", f["line"], "form sends nowhere: give it the client's form address or a mailto stand-in, and list it in the report")
    for o in p.other:
        msgs = {"map-embed": ("WARN", "embedded map loads a third party with the page: link to a map search instead"),
                "carousel": ("FAIL", "carousel, slider or marquee: show whole items in a grid; nothing advances by itself"),
                "popup": ("WARN", "modal or popup in the shell: the page renders header, main and footer only"),
                "tabindex": ("FAIL", "tabindex above 0 breaks the reading order")}
        if o["id"] in msgs:
            add(msgs[o["id"]][0], o["id"], o["line"], msgs[o["id"]][1])
    for s in p.scripts:
        code = s["code"]
        local = CC.local_file(path, s["src"])
        if local:
            code += local.read_text(encoding="utf-8", errors="replace")
        if GAMING.search(code):
            add("FAIL", "checker-gaming", s["line"], "script tests for a headless or automated browser: the page must behave the same for a checker")
        if WIDGET.search(s["src"]) or WIDGET.search(code[:2000]):
            add("WARN", "shell-widget", s["line"], "chat or marketing widget floats over the page; leave it out unless the client requires it")
        if CAROUSEL.search(Path(s["src"]).name):
            add("FAIL", "carousel", s["line"], f"carousel library {Path(s['src']).name}: show whole items in a grid")

    skip = [c for c in p.controls if c["pre_main"] and c["a"].get("href", "").startswith("#") and len(c["a"]["href"]) > 1]
    if not any("skip" in label_of(c).lower() or (p.main_id and c["a"]["href"] == "#" + p.main_id) for c in skip):
        add("WARN", "skip-link", 1, "no skip link: the first Tab should reach 'Skip to content'")
    missing = [k for k in ("og:title", "og:description", "og:image", "twitter:card") if k not in p.meta]
    if missing:
        add("WARN", "share-meta", 1, f"share tags missing: {', '.join(missing)}")
    if not p.icons or "theme-color" not in p.meta:
        add("WARN", "head-icon", 1, "no " + " and no ".join(x for x, ok in (("link rel=icon", p.icons), ("theme-color", "theme-color" in p.meta)) if not ok))

    actions = [c for c in p.controls if label_of(c) and (c["tag"] == "button" or re.search(r"\b(btn|button|cta)\b", c["a"].get("class", "")))]
    for c in actions if p.lang[:2] in ("", "en") else []:  # the verb list is English
        first_word = label_of(c).split()[0].lower()
        if first_word not in VERBS and not re.search(r"toggle|menu", c["a"].get("class", ""), re.I):
            add("WARN", "button-verb", c["line"], f"button '{label_of(c)}' does not start with a verb: name what happens (Book a table)")
    by_target: Dict[str, set] = {}
    for c in p.controls:
        href = c["a"].get("href", "")
        if c["tag"] == "a" and href not in ("", "#") and not c["chrome"] and label_of(c):
            by_target.setdefault(href, set()).add(label_of(c).lower())
    for href, labels in by_target.items():
        if len(labels) > 1:
            add("WARN", "label-target", 1, f"{href} is reached by {len(labels)} labels ({'; '.join(sorted(labels))}): one target, one wording")
    distinct = {label_of(c).lower() for c in p.controls if label_of(c) and not c["chrome"]}
    if len(distinct) > 10:
        add("WARN", "label-count", 1, f"{len(distinct)} different link and button labels outside the nav and footer; ten at most")
    hero = [c for c in actions if c["section"] == 1]
    if hero:
        main = label_of(hero[0]).lower()
        if not any(label_of(c).lower() == main for c in p.controls if c["section"] > 1 or (c["chrome"] and c is not hero[0])):
            add("WARN", "main-action", hero[0]["line"], f"the hero's main action '{label_of(hero[0])}' never appears again word for word (nav, close or booking)")
    assumed = [o["line"] for o in p.other if o["id"] == "assumed"]
    out.sort(key=lambda f: (f["line"], f["id"]))
    return {"file": str(path), "controls": len(p.controls), "fields": len(p.fields), "forms": len(p.forms),
            "assumed_lines": assumed, "findings": out}


def main() -> None:
    """CLI entry point."""
    ap = argparse.ArgumentParser(description="Static access, links, forms, head and shell check for a website page.")
    ap.add_argument("path", help="HTML page")
    ap.add_argument("--strict", action="store_true", help="treat WARN as failing")
    ap.add_argument("--format", choices=["text", "json"], default="text", help="output format")
    args = ap.parse_args()
    try:
        res = check(Path(args.path))
    except InputError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(2)
    fails = sum(f["severity"] == "FAIL" for f in res["findings"])
    if args.format == "json":
        print(json.dumps(res, indent=2))
    else:
        print(f"access_links_check: {res['file']}  controls={res['controls']} fields={res['fields']} forms={res['forms']}")
        for f in res["findings"]:
            print(f"  {f['severity']:4} L{f['line']:<4} {f['id']:<15} {f['message']}")
        if res["assumed_lines"]:
            print(f"  INFO assumed facts marked data-assumed on lines {', '.join(map(str, res['assumed_lines']))}: list each in the report")
        print(f"  {fails} FAIL, {len(res['findings']) - fails} WARN")
    sys.exit(1 if fails or (args.strict and res["findings"]) else 0)


if __name__ == "__main__":
    main()
