#!/usr/bin/env python3
"""
Markdown rendering core for the md-document skill: the markdown subset parser,
the escaping-first inline renderer, figure/table numbering, and cross-reference
resolution.

Imported by the CLI tools in this same scripts/ directory. Self-contained —
standard library only, no imports from any other skill. Subset: ATX headings
with optional {#sec:label}, fenced code, flat lists, pipe tables with an
optional "Table:" caption, blockquotes, rules, standalone images as numbered
figures, emphasis, code spans, links, footnotes, [@fig:x] cross-references.
"""

import html
import re
from typing import Any, Dict, List, Tuple

LABEL_RE = re.compile(r"\s*\{#(fig|tbl|sec):([A-Za-z0-9_-]+)\}\s*$")
IMAGE_LINE_RE = re.compile(r"^!\[(?P<alt>[^\]]*)\]\((?P<src>[^)\s]+)\)(?P<tail>.*)$")
TABLE_CAPTION_RE = re.compile(r"^Table:\s*(?P<caption>.+)$")
FOOTNOTE_DEF_RE = re.compile(r"^\[\^(?P<id>[^\]]+)\]:\s*(?P<text>.+)$")
HEADING_RE = re.compile(r"^(?P<hashes>#{1,6})\s+(?P<text>.+?)\s*$")
SAFE_URL_RE = re.compile(r"^(https?:|mailto:|#|[./]|[A-Za-z0-9_-]+[./])")
CODE_SPAN_RE = re.compile(r"`([^`]+)`")
IMG_RE = re.compile(r"!\[([^\]]*)\]\(([^)\s]+)\)")
LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")
XREF_RE = re.compile(r"\[@(fig|tbl|sec):([A-Za-z0-9_-]+)\]")
FNREF_RE = re.compile(r"\[\^([^\]]+)\]")
BOLD_RE = re.compile(r"\*\*([^*]+)\*\*")
ITALIC_RE = re.compile(r"(?<![*\w])\*([^*]+)\*(?!\*)")
ULI_RE = re.compile(r"^\s*[-*]\s+(.*)$")
OLI_RE = re.compile(r"^\s*\d+\.\s+(.*)$")
KIND_LABEL = {"fig": "Figure", "tbl": "Table", "sec": "Section"}
MISSING_NOTE = '<em class="xref-broken">undefined footnote</em>'


def slugify(text: str) -> str:
    """Turn heading text into a stable, URL-safe anchor id."""
    clean = re.sub(r"[^\w\s-]", "", re.sub(r"[*`_]", "", text)).strip().lower()
    return re.sub(r"[\s_]+", "-", clean) or "section"


def safe_url(url: str) -> str:
    """Return an escaped url if its scheme is safe, else a neutral placeholder.

    Blocks javascript:, data:, vbscript: and anything else that could execute
    when the generated document is opened.
    """
    url = url.strip()
    return html.escape(url, quote=True) if SAFE_URL_RE.match(url) else "#blocked-url"


def collect_labels(lines: List[str]) -> Dict[str, Dict[str, Any]]:
    """First pass: assign a number to every figure, table, and section label.

    Numbering must be known before rendering so that a [@fig:x] reference
    appearing earlier than its figure still resolves to the right number.
    """
    labels: Dict[str, Dict[str, Any]] = {}
    counters = {"fig": 0, "tbl": 0}
    section: List[int] = []
    in_code = False
    for line in lines:
        if line.startswith("```"):
            in_code = not in_code
        if in_code or line.startswith("```"):
            continue
        stripped = line.rstrip()
        match = LABEL_RE.search(stripped)
        bare = LABEL_RE.sub("", stripped)
        heading = HEADING_RE.match(bare)
        if heading:
            depth = len(heading.group("hashes")) - 1
            if depth > 0:
                section = (section[:depth] + [0] * (depth - len(section)))
                section[depth - 1] += 1
            if match and match.group(1) == "sec":
                labels[f"sec:{match.group(2)}"] = {
                    "kind": "sec", "number": ".".join(str(n) for n in section),
                    "anchor": slugify(heading.group("text"))}
            continue
        kind = "fig" if IMAGE_LINE_RE.match(stripped) else (
            "tbl" if TABLE_CAPTION_RE.match(bare) else "")
        if kind:
            counters[kind] += 1
            name = (match.group(2) if match and match.group(1) == kind
                    else f"_{counters[kind]}")
            labels[f"{kind}:{name}"] = {"kind": kind, "number": str(counters[kind]),
                                        "anchor": f"{kind}-{name}"}
    return labels


def render_inline(text: str, labels: Dict[str, Dict[str, Any]],
                  used_notes: List[str], unresolved: List[str]) -> str:
    """Escape a span of text, then apply inline markdown to the escaped result.

    Escaping first is what makes the output injection-safe: no user byte can
    become markup. Code spans are lifted out before escaping so emphasis inside
    them is not interpreted, then reinserted escaped.
    """
    spans: List[str] = []

    def stash(match: re.Match) -> str:
        spans.append(match.group(1))
        return f"\x00{len(spans) - 1}\x00"

    text = html.escape(CODE_SPAN_RE.sub(stash, text), quote=True)

    def xref(match: re.Match) -> str:
        key = f"{match.group(1)}:{match.group(2)}"
        entry = labels.get(key)
        if not entry:
            unresolved.append(key)
            return f'<span class="xref-broken">[?{key}]</span>'
        return (f'<a class="xref" href="#{entry["anchor"]}">'
                f'{KIND_LABEL[entry["kind"]]} {entry["number"]}</a>')

    def footnote(match: re.Match) -> str:
        note_id = match.group(1)
        if note_id not in used_notes:
            used_notes.append(note_id)
        return (f'<sup class="fn"><a id="fnref-{note_id}" href="#fn-{note_id}">'
                f'{used_notes.index(note_id) + 1}</a></sup>')

    text = IMG_RE.sub(
        lambda m: f'<img src="{safe_url(html.unescape(m.group(2)))}" alt="{m.group(1)}">', text)
    text = XREF_RE.sub(xref, text)
    text = FNREF_RE.sub(footnote, text)
    text = LINK_RE.sub(
        lambda m: f'<a href="{safe_url(html.unescape(m.group(2)))}">{m.group(1)}</a>', text)
    text = ITALIC_RE.sub(r"<em>\1</em>", BOLD_RE.sub(r"<strong>\1</strong>", text))
    for i, span in enumerate(spans):
        text = text.replace(f"\x00{i}\x00", f"<code>{html.escape(span)}</code>")
    return text


class Renderer:
    """Second pass: turn markdown lines into semantic HTML body content."""

    def __init__(self, labels: Dict[str, Dict[str, Any]], toc_depth: int) -> None:
        self.labels = labels
        self.toc_depth = toc_depth
        self.toc: List[Tuple[int, str, str]] = []
        self.notes: List[str] = []
        self.definitions: Dict[str, str] = {}
        self.unresolved: List[str] = []
        self.counters = {"fig": 0, "tbl": 0}
        self.out: List[str] = []

    def inline(self, text: str) -> str:
        """Render inline markdown within a block."""
        return render_inline(text, self.labels, self.notes, self.unresolved)

    def anchor_for(self, kind: str, line: str) -> str:
        """Advance the counter for a figure or table and return its anchor id."""
        self.counters[kind] += 1
        match = LABEL_RE.search(line)
        name = (match.group(2) if match and match.group(1) == kind
                else f"_{self.counters[kind]}")
        return f"{kind}-{name}"

    def heading(self, line: str) -> None:
        """Emit a heading, register its anchor, and record a TOC entry."""
        match = HEADING_RE.match(LABEL_RE.sub("", line))
        level, text = len(match.group("hashes")), match.group("text")
        anchor = slugify(text)
        if 2 <= level <= self.toc_depth + 1:
            self.toc.append((level, anchor, self.inline(text)))
        self.out.append(f'<h{level} id="{anchor}">{self.inline(text)}</h{level}>')

    def code_block(self, lines: List[str], start: int) -> int:
        """Emit a fenced code block; returns the index after the closing fence."""
        lang = lines[start].strip()[3:].strip()
        body: List[str] = []
        i = start + 1
        while i < len(lines) and not lines[i].startswith("```"):
            body.append(lines[i])
            i += 1
        cls = f' class="language-{html.escape(lang, quote=True)}"' if lang else ""
        self.out.append(f"<pre><code{cls}>{html.escape(chr(10).join(body))}</code></pre>")
        return i + 1

    def table(self, lines: List[str], start: int) -> int:
        """Emit a table with a header row, plus a numbered caption if present."""
        rows: List[List[str]] = []
        i = start
        while i < len(lines) and lines[i].lstrip().startswith("|"):
            cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
            if not all(re.fullmatch(r":?-{2,}:?", c) for c in cells):
                rows.append(cells)
            i += 1
        caption, look = "", i
        while look < len(lines) and not lines[look].strip():
            look += 1
        cap = (TABLE_CAPTION_RE.match(LABEL_RE.sub("", lines[look].strip()))
               if look < len(lines) else None)
        if cap:
            anchor = self.anchor_for("tbl", lines[look])
            caption = (f'<caption id="{anchor}">Table {self.counters["tbl"]}. '
                       f'{self.inline(cap.group("caption"))}</caption>')
            i = look + 1
        head = "".join(f'<th scope="col">{self.inline(c)}</th>' for c in rows[0])
        body = "".join("<tr>" + "".join(f"<td>{self.inline(c)}</td>" for c in row)
                       + "</tr>" for row in rows[1:])
        self.out.append(f'<div class="table-wrap"><table>{caption}<thead><tr>{head}'
                        f"</tr></thead><tbody>{body}</tbody></table></div>")
        return i

    def figure(self, line: str) -> None:
        """Emit a standalone image as a numbered figure with a caption."""
        match = IMAGE_LINE_RE.match(LABEL_RE.sub("", line.strip()))
        anchor = self.anchor_for("fig", line)
        alt = html.escape(match.group("alt"), quote=True)
        caption = match.group("tail").strip() or match.group("alt")
        self.out.append(
            f'<figure id="{anchor}"><img src="{safe_url(match.group("src"))}" alt="{alt}">'
            f'<figcaption>Figure {self.counters["fig"]}. {self.inline(caption)}</figcaption>'
            f"</figure>")

    def simple_list(self, lines: List[str], start: int, ordered: bool) -> int:
        """Emit a flat unordered or ordered list."""
        pattern = OLI_RE if ordered else ULI_RE
        items: List[str] = []
        i = start
        while i < len(lines):
            match = pattern.match(lines[i])
            if not match:
                break
            items.append(f"<li>{self.inline(match.group(1))}</li>")
            i += 1
        tag = "ol" if ordered else "ul"
        self.out.append(f"<{tag}>{''.join(items)}</{tag}>")
        return i

    def flush(self, paragraph: List[str]) -> None:
        """Emit any buffered paragraph lines as a single <p>."""
        if paragraph:
            self.out.append(f"<p>{self.inline(' '.join(paragraph))}</p>")
            paragraph.clear()

    def render(self, lines: List[str]) -> None:
        """Walk the document and dispatch each block to its handler."""
        i, paragraph = 0, []
        breaks = ("#", "```", ">", "|", "- ", "* ")
        while i < len(lines):
            stripped = lines[i].strip()
            if not stripped or stripped.startswith(breaks) or OLI_RE.match(stripped):
                self.flush(paragraph)
            fn_def = FOOTNOTE_DEF_RE.match(stripped)
            if fn_def:
                self.definitions[fn_def.group("id")] = fn_def.group("text")
            elif not stripped:
                pass
            elif stripped.startswith("```"):
                i = self.code_block(lines, i)
                continue
            elif stripped in ("[TOC]", "[toc]"):
                self.out.append("\x01TOC\x01")
            elif HEADING_RE.match(LABEL_RE.sub("", stripped)):
                self.heading(stripped)
            elif re.fullmatch(r"(-{3,}|\*{3,}|_{3,})", stripped):
                self.out.append("<hr>")
            elif IMAGE_LINE_RE.match(LABEL_RE.sub("", stripped)):
                self.figure(stripped)
            elif stripped.startswith("|"):
                i = self.table(lines, i)
                continue
            elif stripped.startswith("> "):
                self.out.append(f"<blockquote><p>{self.inline(stripped[2:])}</p></blockquote>")
            elif ULI_RE.match(stripped):
                i = self.simple_list(lines, i, ordered=False)
                continue
            elif OLI_RE.match(stripped):
                i = self.simple_list(lines, i, ordered=True)
                continue
            else:
                paragraph.append(stripped)
            i += 1
        self.flush(paragraph)

    def toc_html(self) -> str:
        """Render the collected headings as an indent-classed table of contents."""
        if not self.toc:
            return ""
        items = "".join(f'<li class="toc-l{level}"><a href="#{anchor}">{text}</a></li>'
                        for level, anchor, text in self.toc)
        return ('<nav class="toc" aria-label="Table of contents">'
                f"<h2>Contents</h2><ol>{items}</ol></nav>")

    def footnotes_html(self) -> Tuple[str, List[str]]:
        """Render the footnote list; returns the HTML and any undefined ids."""
        if not self.notes:
            return "", []
        missing = [n for n in self.notes if n not in self.definitions]
        items = "".join(
            f'<li id="fn-{n}">'
            f'{self.inline(self.definitions[n]) if n in self.definitions else MISSING_NOTE} '
            f'<a class="fn-back" href="#fnref-{n}" aria-label="Back to reference">&#8617;</a>'
            f"</li>" for n in self.notes)
        return f'<section class="footnotes"><h2>Notes</h2><ol>{items}</ol></section>', missing
