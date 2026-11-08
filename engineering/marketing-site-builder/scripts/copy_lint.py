#!/usr/bin/env python3
"""Lint website copy for the tells that make a page read as generic or generated.

Reads an HTML page (or a Markdown/plain-text copy draft) and reports, with line
numbers: hype words, stock lines, template or chat residue, vague button labels,
device tics over their budget (virtue words, contrast frames, -ing riders,
fragment headings), em-dash, exclamation and emoji overuse, unsourced proof
figures, default-cast names, footer sign-offs, question headings and a stale
copyright year. The word lists live in assets/copy_tells.json.

Usage:
  python3 copy_lint.py page.html
  python3 copy_lint.py draft.md --allow harness --format json --strict

Exit codes: 0 clean, 1 FAIL findings (or WARN with --strict), 2 bad input.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from typing import Dict, List, Optional

DEFAULT_LEXICON = Path(__file__).resolve().parent.parent / "assets" / "copy_tells.json"
BLOCK = set("address article aside blockquote body dd details div dl dt figcaption figure footer form "
            "h1 h2 h3 h4 h5 h6 header li main nav ol p section summary table td th tr ul title".split())
SKIP = {"script", "style", "template", "noscript", "svg"}
EMOJI = re.compile("[\U0001F300-\U0001FAFF☀-➿⭐✅]")
TWO_FRAGMENT = re.compile(r"^(?:[^.?!]{2,48}[.!] ){1,3}[^.?!]{2,55}[.!]?$")
YEAR = re.compile(r"(?:©|\(c\)|copyright)\s*(?:\d{4}\s*[-–]\s*)?((?:19|20)\d\d)", re.I)


class InputError(Exception):
    """Raised for unreadable or unusable input; mapped to exit code 2."""


class CopyParser(HTMLParser):
    """Collect visible text as block segments and link/button labels as action segments."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.segments: List[Dict] = []
        self.stack: List[str] = []
        self.skip = 0
        self.buf: List[tuple] = []  # (data, source line where the chunk starts)
        self.actions: List[List] = []  # [text parts, line]

    def _kind(self) -> str:
        heads = [t for t in self.stack if t in ("h1", "h2", "h3", "h4", "h5", "h6", "title")]
        if heads:
            return "h1" if heads[-1] == "h1" else "heading"
        return "footer" if "footer" in self.stack else "body"

    def flush(self) -> None:
        raw = "".join(d for d, _ in self.buf)
        text = raw.lstrip()
        if text:
            anchors, pos = [], 0
            for d, ln in self.buf:  # each chunk keeps its own source line, so tags spanning lines don't shift hits
                anchors.append((pos, ln))
                pos += len(d)
            self.segments.append({"text": text, "raw": raw, "shift": len(raw) - len(text),
                                  "anchors": anchors, "line": 0, "kind": self._kind()})
            self.segments[-1]["line"] = line_of(self.segments[-1], 0)
        self.buf = []

    def handle_starttag(self, tag: str, attrs: List) -> None:
        if tag in SKIP:
            self.skip += 1
            return
        a = dict(attrs)
        if tag == "meta" and (a.get("name") or "").lower() == "description" and a.get("content"):
            self.segments.append({"text": a["content"], "line": self.getpos()[0], "kind": "body"})
        if tag in BLOCK:
            self.flush()
        if tag in ("a", "button"):
            self.actions.append([[], self.getpos()[0]])
        if tag == "br":
            self.handle_data("\n")
        if tag not in ("br", "img", "input", "meta", "link", "hr"):
            self.stack.append(tag)

    def handle_endtag(self, tag: str) -> None:
        if tag in SKIP:
            self.skip = max(0, self.skip - 1)
            return
        if tag in BLOCK:
            self.flush()
        if tag in ("a", "button") and self.actions:
            parts, line = self.actions.pop()
            label = " ".join("".join(parts).split())
            if label:
                self.segments.append({"text": label, "line": line, "kind": "action"})
        if tag in self.stack:
            while self.stack and self.stack.pop() != tag:
                pass

    def handle_data(self, data: str) -> None:
        if self.skip:
            return
        self.buf.append((data, self.getpos()[0]))
        for act in self.actions:
            act[0].append(data)


def line_of(seg: Dict, offset: int) -> int:
    """Map a character offset in a segment's text to its line in the source file."""
    if "anchors" not in seg:
        return seg["line"] + seg["text"][:offset].count("\n")
    raw_off = offset + seg["shift"]
    start, line = max((a for a in seg["anchors"] if a[0] <= raw_off), default=seg["anchors"][0])
    return line + seg["raw"][start:raw_off].count("\n")


def segments_from_markdown(text: str) -> List[Dict]:
    """Treat each Markdown line as a segment; '#' lines are headings, link texts are actions."""
    segs: List[Dict] = []
    for n, line in enumerate(text.splitlines(), 1):
        if not line.strip():
            continue
        m = re.match(r"^(#{1,6})\s+(.*)", line)
        kind = ("h1" if len(m.group(1)) == 1 else "heading") if m else "body"
        segs.append({"text": m.group(2) if m else line, "line": n, "kind": kind})
        for lm in re.finditer(r"\[([^\]]+)\]\([^)]*\)", line):
            segs.append({"text": lm.group(1), "line": n, "kind": "action"})
    return segs


def load(path: Path, lexicon_path: Path) -> tuple:
    """Read the page and the lexicon; raise InputError on any problem."""
    if not path.is_file():
        raise InputError(f"file not found: {path}")
    try:
        raw = path.read_text(encoding="utf-8")
        lex = json.loads(lexicon_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError) as exc:
        raise InputError(f"cannot read input: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise InputError(f"lexicon is not valid JSON: {lexicon_path}: {exc}") from exc
    if not raw.strip():
        raise InputError(f"file is empty: {path}")
    is_html = path.suffix.lower() in (".html", ".htm")
    if is_html:
        if "<" not in raw:
            raise InputError(f"{path} has an .html name but contains no markup")
        parser = CopyParser()
        parser.feed(raw)
        parser.close()
        parser.flush()
    segs = parser.segments if is_html else segments_from_markdown(raw)
    if not any(s["text"].strip() for s in segs):
        raise InputError(f"no visible text found in {path}")
    if not isinstance(lex, dict) or not all(isinstance(lex.get(k), dict) for k in
                                            ("hype_words", "stock_phrases", "residue", "vague_ctas")):
        raise InputError("lexicon must be an object with hype_words, stock_phrases, residue and vague_ctas sections")
    return segs, lex, is_html


def lint(segs: List[Dict], lex: Dict, is_html: bool, allow: List[str], year: int) -> List[Dict]:
    """Run every check and return findings sorted by line."""
    out: List[Dict] = []
    allow_set = {a.lower() for a in allow}

    def add(sev: str, cid: str, seg: Dict, offset: int, match: str, msg: str) -> None:
        line = line_of(seg, offset)
        out.append({"severity": sev, "id": cid, "line": line, "match": match.strip()[:60], "message": msg})

    def scan(cid: str, regexes: List[str], sev: str, msg: str, kinds: Optional[tuple] = None) -> List[Dict]:
        hits = []
        for seg in segs:
            if kinds and seg["kind"] not in kinds:
                continue
            if seg["kind"] == "action" and kinds is None:
                continue  # labels are part of the block text already
            for rx in regexes:
                for m in re.finditer(rx, seg["text"], re.I):
                    if m.group(0).lower().strip() in allow_set:
                        continue
                    hits.append((seg, m.start(), m.group(0)))
        for seg, off, txt in hits:
            add(sev, cid, seg, off, txt, msg)
        return hits

    words = lambda ws: [r"\b" + re.escape(w) + r"(?![\w-])" for w in ws]  # noqa: E731
    scan("hype-word", words(lex["hype_words"]["words"]), "FAIL", "hype word: replace it with the fact it stands for")
    scan("stock-phrase", [re.escape(p) for p in lex["stock_phrases"]["phrases"]], "FAIL", "stock line that fits any business")
    res = [r"\b" + re.escape(p) + r"(?!\w)" if p[0].isalnum() else re.escape(p) for p in lex["residue"]["phrases"]]
    res += [p for p in lex["residue"].get("patterns", []) if is_html or "#" not in p]
    scan("residue", res, "FAIL", "template or chat residue left on the page")

    vague = {v.lower() for v in lex["vague_ctas"]["labels"]}
    soft = {v.lower() for v in lex["vague_ctas"].get("warn_labels", [])}
    for seg in (s for s in segs if s["kind"] == "action"):
        label = re.sub(r"[^\w' ]+", " ", EMOJI.sub("", seg["text"])).strip().lower()
        label = " ".join(label.split())
        if label in vague:
            add("FAIL", "vague-cta", seg, 0, seg["text"], "label names nothing: use a verb plus what the visitor gets")
        elif label in soft:
            add("WARN", "soft-cta", seg, 0, seg["text"], "label could name the transaction (Book a table, Start a free trial)")

    def budgeted(cid: str, hits: List, budget: int, msg: str) -> None:
        n = len(hits)
        if n <= budget:
            return
        sev = "FAIL" if n >= budget * 2 + 1 else "WARN"
        for seg, off, txt in hits:
            add(sev, cid, seg, off, txt, f"{msg}: {n} on the page, budget {budget}")

    def collect(regexes: List[str], kinds: Optional[tuple] = None) -> List:
        hits = []
        for seg in segs:
            if seg["kind"] == "action" or (kinds and seg["kind"] not in kinds):
                continue
            spans: List[tuple] = []  # one hit per stretch of text, however many patterns match it
            for rx in regexes:
                for m in re.finditer(rx, seg["text"], re.I):
                    if not any(m.start() < e and s < m.end() for s, e in spans):
                        spans.append((m.start(), m.end()))
                        hits.append((seg, m.start(), m.group(0)))
        return hits

    for key, cid, msg in (("virtue_words", "virtue-word", "virtue word about the business; show it with a fact"),
                          ("contrast_frames", "contrast-frame", "contrast frame ('X, not Y', 'rather than')"),
                          ("ing_riders", "ing-rider", "-ing rider tacked onto a claim")):
        sect = lex.get(key)
        if sect:
            pats = words(sect["words"]) if "words" in sect else sect["patterns"]
            budgeted(cid, collect(pats), int(sect.get("budget", 1)), msg)
    heads = [s for s in segs if s["kind"] in ("h1", "heading")]
    two = [(s, 0, s["text"]) for s in heads if TWO_FRAGMENT.match(" ".join(s["text"].split()))]
    budgeted("fragment-heading", two, 1, "fragment heading 'X. Y.'")
    budgeted("em-dash", collect(["—"]), 2, "em dashes")
    budgeted("exclamation", collect([r"\w!"], ("body", "footer")), 0, "exclamation mark in body copy")
    budgeted("emoji", collect([EMOJI.pattern]), 1, "emoji")

    for key, cid, msg in (("reveals", "reveal", "staged reveal or process talk"),
                          ("puffery", "puffery", "dead metaphor or inflated verb"),
                          ("proof_figures", "proof-figure", "round unsourced figure: use the brief's number with its source")):
        if key in lex:
            scan(cid, lex[key]["patterns"], "WARN", msg)
    if "default_cast" in lex:
        scan("default-cast", words(lex["default_cast"]["names"]), "WARN", "default-cast name: names come from the brief")
    if "footer_signoffs" in lex:  # sign-offs only count inside <footer>
        scan("footer-signoff", lex["footer_signoffs"]["patterns"], "WARN", "sign-off in the footer: keep it to the legal row", ("footer",))
    for s in heads:
        t = " ".join(s["text"].split())
        if t.endswith("?") and s["kind"] == "h1":
            add("WARN", "question-heading", s, 0, t, "h1 as a question: name the category instead")
        if s["kind"] == "h1" and len(t.split()) > 10:
            add("WARN", "h1-length", s, 0, t, f"h1 is {len(t.split())} words: name the category in 2 to 8")
    for s in segs:
        for m in YEAR.finditer(s["text"]):
            if int(m.group(1)) < year:
                add("WARN", "stale-year", s, m.start(), m.group(0), f"copyright year older than {year}")
    uniq = {(f["id"], f["line"], f["match"].lower()): f for f in reversed(out)}  # first hit wins
    return sorted(uniq.values(), key=lambda f: (f["line"], f["id"]))


def render(path: Path, findings: List[Dict], fmt: str) -> str:
    """Format findings as text or JSON."""
    fails = sum(f["severity"] == "FAIL" for f in findings)
    if fmt == "json":
        return json.dumps({"file": str(path), "fail": fails, "warn": len(findings) - fails, "findings": findings}, indent=2)
    lines = [f"copy_lint: {path}"]
    for f in findings:
        lines.append(f"  {f['severity']:4} L{f['line']:<4} {f['id']:<16} \"{f['match']}\"  {f['message']}")
    lines.append(f"  {fails} FAIL, {len(findings) - fails} WARN" + ("  (clean)" if not findings else ""))
    return "\n".join(lines)


def main() -> None:
    """CLI entry point."""
    ap = argparse.ArgumentParser(description="Lint website copy for generic and generated-sounding tells.")
    ap.add_argument("path", help="HTML page, or a .md/.txt copy draft")
    ap.add_argument("--lexicon", default=str(DEFAULT_LEXICON), help="word lists JSON (default: assets/copy_tells.json)")
    ap.add_argument("--allow", action="append", default=[], help="a word that is literal for this trade (repeatable)")
    ap.add_argument("--year", type=int, default=dt.date.today().year, help="current year for the copyright check")
    ap.add_argument("--strict", action="store_true", help="treat WARN as failing")
    ap.add_argument("--format", choices=["text", "json"], default="text", help="output format")
    args = ap.parse_args()
    try:
        segs, lex, is_html = load(Path(args.path), Path(args.lexicon))
        try:
            findings = lint(segs, lex, is_html, args.allow, args.year)
        except (KeyError, TypeError, AttributeError, ValueError, re.error) as exc:
            raise InputError(f"lexicon has the wrong shape or a bad pattern: {exc!r}") from exc
    except InputError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(2)
    print(render(Path(args.path), findings, args.format))
    fails = any(f["severity"] == "FAIL" for f in findings)
    sys.exit(1 if fails or (args.strict and findings) else 0)


if __name__ == "__main__":
    main()
