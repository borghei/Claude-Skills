#!/usr/bin/env python3
"""Count the copy devices that read as generated when they repeat, and the page's
honesty tells, as a companion to copy_lint.py.

copy_lint.py catches words and phrases. This script catches shapes: number-pair
and colon headings, negation runs, a strip of figures, step numbers on cards,
eyebrow labels over every section, a wall of quotes, a response-time promise in
two wordings, "since <year>" said twice, a heading whose grey half runs on,
all-caps labels, sentences of one length, apology notes ("names are examples"),
and a default-cast name used as the page's own brand. Given several pages, it
also prints their first headings side by side and the heading phrases they share.

Usage:
  python3 copy_devices.py page.html
  python3 copy_devices.py home.html pricing.html --format json
  python3 copy_devices.py draft.md --strict

Exit codes: 0 clean, 1 FAIL findings (or WARN with --strict), 2 bad input.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import statistics
import sys
from html.parser import HTMLParser
from pathlib import Path
from typing import Dict, List

HERE = Path(__file__).resolve().parent
NUM = r"(?:\d[\d.,]*|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|a dozen|dozens|hundreds)"
NUMBER_PAIR = re.compile(rf"^{NUM}\b[^.]*?[,.]\s+{NUM}\b", re.I)
NEGATION = re.compile(r"\bno [^.,;\n]{1,30}(?:, no |\. no |; no )", re.I)
FIGURE = re.compile(r"(?<![\w:])[~<>]?\d[\d.,]*\s?(?:\+|%|x|×|k|m|bn)?(?![\w:])", re.I)
MONEY_OR_TIME = re.compile(r"[€$£¥]|\b\d{1,2}:\d\d\b|\b(?:euros?|dollars?|pounds?|usd|eur|gbp)\b", re.I)
RESPONSE = re.compile(r"\b(?:within|in under|in less than) (?:an?|one|two|three|four|\d+) (?:working |business )?(?:minutes?|hours?|days?)\b", re.I)
SINCE = re.compile(r"\bsince (?:19|20)\d\d\b", re.I)
EYEBROW = re.compile(r"^(?:eyebrow|kicker|overline|pretitle|section-label|section-kicker|tagline|label-top)(?:__|--|$)")
APOLOGY = [r"\b(?:names|figures|numbers|prices|quotes)(?: and \w+)?(?: on this page| shown)? are (?:examples|illustrative|fictional|placeholders)\b",
           r"\brepresentative (?:image|photo|photograph|picture)s?\b", r"\bfor illustration(?: purposes)?(?: only)?\b",
           r"\billustrative (?:only|purposes)\b", r"\bimage(?:s)? for reference\b", r"\bsample (?:data|figures|names|prices)\b"]
SENT = re.compile(r"[^.!?]+[.!?]")


def _sibling(name: str):
    """Load a sibling script as a module without a package import."""
    spec = importlib.util.spec_from_file_location(name, HERE / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


CL = _sibling("copy_lint")


class StructParser(HTMLParser):
    """Record headings (with the text before a .muted span), the title, eyebrows and quotes."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.headings: List[Dict] = []
        self.title, self.in_title, self.skip = "", False, 0
        self.eyebrows: List[int] = []
        self.blockquotes: List[int] = []
        self.cur = None

    def handle_starttag(self, tag: str, attrs: List) -> None:
        a = {k: (v or "") for k, v in attrs}
        if tag in CL.SKIP:
            self.skip += 1
        if tag == "title" and not self.skip and not self.title:
            self.in_title = True
        if re.fullmatch(r"h[1-6]", tag):
            self.cur = {"level": int(tag[1]), "line": self.getpos()[0], "text": "", "before": None}
            self.headings.append(self.cur)
        if self.cur is not None and tag == "span" and "muted" in a.get("class", "").split() and self.cur["before"] is None:
            self.cur["before"] = self.cur["text"]
        if any(EYEBROW.match(c) for c in a.get("class", "").split()):
            self.eyebrows.append(self.getpos()[0])
        if tag == "blockquote":
            self.blockquotes.append(self.getpos()[0])

    def handle_endtag(self, tag: str) -> None:
        if tag in CL.SKIP:
            self.skip = max(0, self.skip - 1)
        if tag == "title":
            self.in_title = False
        if re.fullmatch(r"h[1-6]", tag):
            self.cur = None

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.title += data
        elif self.cur is not None and not self.skip:
            self.cur["text"] += data


def squash(text: str) -> str:
    """Collapse whitespace and curly quotes."""
    return " ".join(text.replace("’", "'").replace("“", '"').replace("”", '"').split())


def analyse(path: Path, lexicon: Path) -> Dict:
    """Return findings and the page's headings for one HTML page or Markdown draft."""
    try:
        segs, lex, is_html = CL.load(path, lexicon)
    except CL.InputError as exc:
        raise ValueError(str(exc)) from exc
    out: List[Dict] = []

    def add(sev: str, cid: str, line: int, match: str, msg: str) -> None:
        out.append({"severity": sev, "id": cid, "line": line, "match": squash(match)[:60], "message": msg})

    def budget(cid: str, hits: List[tuple], limit: int, msg: str) -> None:
        if len(hits) > limit:
            sev = "FAIL" if len(hits) >= limit * 2 + 1 else "WARN"
            for line, text in hits:
                add(sev, cid, line, text, f"{msg}: {len(hits)} on the page, budget {limit}")

    if is_html:
        sp = StructParser()
        sp.feed(path.read_text(encoding="utf-8"))
        heads = [{"level": h["level"], "line": h["line"], "text": squash(h["text"]), "before": h["before"]} for h in sp.headings]
        title, eyebrows, bq = squash(sp.title), sp.eyebrows, sp.blockquotes
    else:
        heads = [{"level": 1 if s["kind"] == "h1" else 2, "line": s["line"], "text": squash(s["text"]), "before": None}
                 for s in segs if s["kind"] in ("h1", "heading")]
        title, eyebrows, bq = "", [], []
    body = [s for s in segs if s["kind"] in ("body", "footer")]

    budget("number-pair", [(h["line"], h["text"]) for h in heads if NUMBER_PAIR.search(h["text"])], 1,
           "number-pair heading ('Four X, four Y'): say what the section holds")
    neg = [(CL.line_of(s, m.start()), m.group(0)) for s in body + [s for s in segs if s["kind"] in ("h1", "heading")]
           for m in NEGATION.finditer(s["text"])]
    budget("negation-run", neg, 1, "negation run ('No X, no Y'): keep one, and only refusals a buyer can check")
    for h in heads:
        if h["level"] <= 3 and ":" in h["text"] and not re.search(r"\d:\d", h["text"]):
            add("WARN", "colon-heading", h["line"], h["text"], "colon heading: name the thing, put the claim in the line under it")
        if h["before"] is not None and h["before"].strip() and not re.search(r"[.!?]\s*$", h["before"]):
            add("WARN", "run-on", h["line"], h["text"], "the grey half runs on from the first: end the first sentence with a full stop")
    caps = [s for s in segs if s["kind"] != "action" and len(s["text"].split()) <= 6
            and len(re.findall(r"\b[A-Z]{4,}\b", s["text"])) >= 1 and s["text"].strip().upper() == s["text"].strip()]
    budget("caps-label", [(s["line"], s["text"]) for s in caps], 1, "label set in capitals: sentence case reads calmer")

    run: List[Dict] = []
    strips: List[tuple] = []
    for s in body + [{"text": "", "line": 0, "kind": "end"}]:
        t = squash(s["text"])
        short_fig = 0 < len(t.split()) <= 4 and FIGURE.match(t) and not MONEY_OR_TIME.search(t)
        if short_fig:
            run.append(s)
            continue
        if len(run) >= 3:
            strips.append((run[0]["line"], " / ".join(squash(r["text"]) for r in run[:4])))
        run = []
        figs = FIGURE.findall(t)
        if len(figs) >= 3 and len(t) < 140 and not MONEY_OR_TIME.search(t) and len(t.split()) <= 4 * len(figs) \
                and not re.search(r"[a-z]{3,}[.!?](\s|$)", t):
            strips.append((s["line"], t))
    for line, text in strips:
        add("WARN", "stat-strip", line, text, "strip of figures over one-word labels: each number goes in the sentence it proves, from the brief")
    steps = [s for s in segs if re.fullmatch(r"0\d\.?", squash(s["text"]))]
    if len(steps) >= 3:
        add("WARN", "step-numbers", steps[0]["line"], f"{len(steps)} step numbers", "number only steps that really happen in order")
    if len(eyebrows) > 2:
        add("WARN", "eyebrows", eyebrows[0], f"{len(eyebrows)} eyebrow labels", "one or two a page; a heading that names the thing needs no label over it")
    quoted = [s["line"] for s in body if re.fullmatch(r'"[^"]{20,}"(?:\s*[-—–,]\s*.{0,60})?', squash(s["text"]))]
    if len(set(bq) | set(quoted)) >= 3:
        add("WARN", "testimonials", min(set(bq) | set(quoted)), f"{len(set(bq) | set(quoted))} quotes",
            "only quotes the brief gives, word for word with name and role; none is a normal page")
    resp = [(CL.line_of(s, m.start()), m.group(0).lower()) for s in body for m in RESPONSE.finditer(s["text"])]
    if len({w for _, w in resp}) >= 2:
        for line, w in resp:
            add("WARN", "response-time", line, w, "a response-time promise in more than one wording: one promise, from the brief, said the same way")
    since = [(CL.line_of(s, m.start()), m.group(0)) for s in segs if s["kind"] != "action" for m in SINCE.finditer(s["text"])]
    budget("since-year", since, 1, "'since <year>' repeated: say it once, where it matters")
    for s in segs:
        for rx in APOLOGY:
            for m in re.finditer(rx, s["text"], re.I):
                add("FAIL", "apology-note", CL.line_of(s, m.start()), m.group(0),
                    "a note apologising for the content: replace it with real material or leave the element out")
        for m in re.finditer(r"\bcoming soon\b", s["text"], re.I):
            add("WARN", "coming-soon", CL.line_of(s, m.start()), m.group(0), "'coming soon' only for what the brief says is coming")
    names = [n.lower() for n in lex.get("default_cast", {}).get("names", [])]
    own = [(1, title)] + [(h["line"], h["text"]) for h in heads if h["level"] == 1]
    for line, text in own:
        for n in names:
            if re.search(r"\b" + re.escape(n) + r"(?![\w-])", text, re.I):
                add("FAIL", "cast-brand", line, text, f"'{n}' is a name generated pages keep coining; the brand comes from the brief or a searched coinage")

    sents = [len(m.group(0).split()) for s in body for m in SENT.finditer(s["text"]) if len(m.group(0).split()) > 1]
    if len(sents) >= 20:
        sd = statistics.pstdev(sents)
        frag = sum(n <= 4 for n in sents) / len(sents)
        if sd < 4:
            add("WARN", "even-rhythm", 1, f"{len(sents)} sentences", f"every sentence about {statistics.mean(sents):.0f} words (spread {sd:.1f}): let length follow meaning")
        if frag > 0.3:
            add("WARN", "fragment-drumbeat", 1, f"{frag:.0%} fragments", "over 30% of sentences are four words or fewer: join the ones that carry one thought")
    out.sort(key=lambda f: (f["line"], f["id"]))
    return {"file": str(path), "headings": [h["text"] for h in heads], "findings": out}


def sameness(results: List[Dict]) -> List[Dict]:
    """Heading phrases of three words or more that two or more pages share."""
    seen: Dict[str, set] = {}
    for r in results:
        for h in r["headings"]:
            w = re.findall(r"[a-z0-9']+", h.lower())
            for i in range(len(w) - 2):
                seen.setdefault(" ".join(w[i:i + 3]), set()).add(r["file"])
    return [{"severity": "WARN", "id": "shared-phrase", "line": 0, "match": p, "message": f"heading phrase on {len(f)} pages: {', '.join(sorted(f))}"}
            for p, f in sorted(seen.items()) if len(f) >= 2]


def main() -> None:
    """CLI entry point."""
    ap = argparse.ArgumentParser(description="Count repeated copy devices and honesty tells on one or more pages.")
    ap.add_argument("paths", nargs="+", help="HTML pages or .md/.txt copy drafts")
    ap.add_argument("--lexicon", default=str(CL.DEFAULT_LEXICON), help="word lists JSON (default: assets/copy_tells.json)")
    ap.add_argument("--strict", action="store_true", help="treat WARN as failing")
    ap.add_argument("--format", choices=["text", "json"], default="text", help="output format")
    args = ap.parse_args()
    try:
        results = [analyse(Path(p), Path(args.lexicon)) for p in args.paths]
    except (ValueError, OSError, re.error) as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(2)
    shared = sameness(results) if len(results) > 1 else []
    findings = [f for r in results for f in r["findings"]] + shared
    fails = sum(f["severity"] == "FAIL" for f in findings)
    if args.format == "json":
        print(json.dumps({"pages": results, "shared": shared, "fail": fails, "warn": len(findings) - fails}, indent=2))
    else:
        for r in results:
            print(f"copy_devices: {r['file']}")
            for f in r["findings"]:
                print(f"  {f['severity']:4} L{f['line']:<4} {f['id']:<17} \"{f['match']}\"  {f['message']}")
        if len(results) > 1:
            print("  first headings side by side:")
            for r in results:
                print(f"    {Path(r['file']).name:<24} {' | '.join(r['headings'][:4])}")
            for f in shared:
                print(f"  WARN {f['id']:<17} \"{f['match']}\"  {f['message']}")
        print(f"  {fails} FAIL, {len(findings) - fails} WARN")
    sys.exit(1 if fails or (args.strict and findings) else 0)


if __name__ == "__main__":
    main()
