#!/usr/bin/env python3
"""
Slide rendering core for the md-slides skill: slide splitting, speaker-note
extraction, per-slide layouts, and the escaping-first markdown renderer.

Imported by the CLI tools in this same scripts/ directory. Self-contained —
standard library only, no imports from any other skill. Subset: headings,
emphasis, code spans and fences, flat lists, pipe tables, blockquotes, links,
and images.
"""

import html
import re
from typing import Any, Dict, List

LAYOUT_RE = re.compile(r"^\[layout:\s*(?P<name>[a-z-]+)\]\s*$")
HEADING_RE = re.compile(r"^(?P<hashes>#{1,6})\s+(?P<text>.+?)\s*$")
SAFE_URL_RE = re.compile(r"^(https?:|mailto:|#|[./]|[A-Za-z0-9_-]+[./])")
CODE_SPAN_RE = re.compile(r"`([^`]+)`")
IMG_RE = re.compile(r"!\[([^\]]*)\]\(([^)\s]+)\)")
LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")
BOLD_RE = re.compile(r"\*\*([^*]+)\*\*")
ITALIC_RE = re.compile(r"(?<![*\w])\*([^*]+)\*(?!\*)")
ULI_RE = re.compile(r"^\s*[-*]\s+(.*)$")
OLI_RE = re.compile(r"^\s*\d+\.\s+(.*)$")
LAYOUTS = {"default", "title", "section", "two-column", "quote", "image"}
NOTES_MARKER = "???"
COLUMN_MARKER = ":::"


def safe_url(url: str) -> str:
    """Return an escaped url if its scheme is safe, else a neutral placeholder."""
    url = url.strip()
    return html.escape(url, quote=True) if SAFE_URL_RE.match(url) else "#blocked-url"


def render_inline(text: str) -> str:
    """Escape a span of text, then apply inline markdown to the escaped result.

    Escaping first is the injection-safety property: no byte of source content
    can become a tag. Code spans are lifted out so emphasis inside them is
    not interpreted.
    """
    spans: List[str] = []

    def stash(match: re.Match) -> str:
        spans.append(match.group(1))
        return f"\x00{len(spans) - 1}\x00"

    text = html.escape(CODE_SPAN_RE.sub(stash, text), quote=True)
    text = IMG_RE.sub(
        lambda m: f'<img src="{safe_url(html.unescape(m.group(2)))}" alt="{m.group(1)}">', text)
    text = LINK_RE.sub(
        lambda m: f'<a href="{safe_url(html.unescape(m.group(2)))}">{m.group(1)}</a>', text)
    text = ITALIC_RE.sub(r"<em>\1</em>", BOLD_RE.sub(r"<strong>\1</strong>", text))
    for i, span in enumerate(spans):
        text = text.replace(f"\x00{i}\x00", f"<code>{html.escape(span)}</code>")
    return text


def strip_frontmatter(lines: List[str]) -> List[str]:
    """Drop a leading YAML frontmatter block if present."""
    if not lines or lines[0].strip() != "---":
        return lines
    end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), 0)
    return lines[end + 1:]


def split_slides(lines: List[str], split_on: str) -> List[Dict[str, Any]]:
    """Split source lines into slide records of content, notes, and layout.

    A line of exactly '---' always starts a slide; with split_on='h2' every
    '## ' heading additionally starts one.
    """
    slides: List[Dict[str, Any]] = []
    body: List[str] = []
    notes: List[str] = []
    layout = "default"
    in_notes = False
    in_code = False

    def flush() -> bool:
        """Emit the buffered slide; returns True if one was actually produced."""
        emitted = bool(any(line.strip() for line in body) or notes)
        if emitted:
            slides.append({"lines": list(body), "notes": "\n".join(notes).strip(),
                           "layout": layout})
        body.clear()
        notes.clear()
        return emitted

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code = not in_code
        # A layout directive declared before a split must survive it, so the
        # layout only resets when a slide was genuinely emitted.
        if not in_code and stripped == "---":
            if flush():
                layout = "default"
            in_notes = False
            continue
        if not in_code and split_on == "h2" and stripped.startswith("## ") and body:
            if flush():
                layout = "default"
            in_notes = False
        if not in_code and stripped == NOTES_MARKER:
            in_notes = True
            continue
        if in_notes:
            notes.append(line.rstrip())
            continue
        match = LAYOUT_RE.match(stripped)
        if match and not in_code:
            layout = match.group("name")
            continue
        body.append(line)
    flush()
    return slides


def render_block(lines: List[str]) -> str:
    """Render one column or slide body of markdown into HTML."""
    out: List[str] = []
    paragraph: List[str] = []
    i = 0

    def flush_paragraph() -> None:
        if paragraph:
            out.append(f"<p>{render_inline(' '.join(paragraph))}</p>")
            paragraph.clear()

    while i < len(lines):
        stripped = lines[i].strip()
        if not stripped or stripped.startswith(("#", "```", ">", "|", "- ", "* ")) \
                or OLI_RE.match(stripped):
            flush_paragraph()
        if not stripped:
            i += 1
            continue
        if stripped.startswith("```"):
            lang = stripped[3:].strip()
            block: List[str] = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                block.append(lines[i])
                i += 1
            cls = f' class="language-{html.escape(lang, quote=True)}"' if lang else ""
            out.append(f"<pre><code{cls}>{html.escape(chr(10).join(block))}</code></pre>")
        elif HEADING_RE.match(stripped):
            match = HEADING_RE.match(stripped)
            level = len(match.group("hashes"))
            out.append(f"<h{level}>{render_inline(match.group('text'))}</h{level}>")
        elif stripped.startswith("> "):
            quote = []
            while i < len(lines) and lines[i].strip().startswith("> "):
                quote.append(lines[i].strip()[2:])
                i += 1
            out.append(f"<blockquote><p>{render_inline(' '.join(quote))}</p></blockquote>")
            continue
        elif stripped.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r":?-{2,}:?", c) for c in cells):
                    rows.append(cells)
                i += 1
            head = "".join(f'<th scope="col">{render_inline(c)}</th>' for c in rows[0])
            rest = "".join("<tr>" + "".join(f"<td>{render_inline(c)}</td>" for c in r)
                           + "</tr>" for r in rows[1:])
            out.append(f'<div class="table-wrap"><table><thead><tr>{head}</tr></thead>'
                       f"<tbody>{rest}</tbody></table></div>")
            continue
        elif ULI_RE.match(stripped) or OLI_RE.match(stripped):
            ordered = bool(OLI_RE.match(stripped))
            pattern, items = (OLI_RE if ordered else ULI_RE), []
            while i < len(lines) and pattern.match(lines[i]):
                items.append(f"<li>{render_inline(pattern.match(lines[i]).group(1))}</li>")
                i += 1
            out.append(f"<{'ol' if ordered else 'ul'}>{''.join(items)}"
                       f"</{'ol' if ordered else 'ul'}>")
            continue
        else:
            paragraph.append(stripped)
        i += 1
    flush_paragraph()
    return "\n".join(out)


def render_slide(slide: Dict[str, Any], index: int) -> str:
    """Render one slide record into a <section> element."""
    layout = slide["layout"] if slide["layout"] in LAYOUTS else "default"
    lines = slide["lines"]
    heads = [l for l in lines if HEADING_RE.match(l.strip())]
    split = next((i for i, l in enumerate(lines) if l.strip() == COLUMN_MARKER), None)
    if layout == "two-column" and split is not None:
        left = [l for l in lines[:split] if l not in heads]
        content = (render_block(heads) + '<div class="columns"><div>' + render_block(left)
                   + "</div><div>" + render_block(lines[split + 1:]) + "</div></div>")
    elif layout == "title":
        rest = [l.strip() for l in lines if l not in heads and l.strip()]
        subtitle = f'<p class="subtitle">{render_inline(" ".join(rest))}</p>' if rest else ""
        content = render_block(heads) + subtitle
    else:
        content = render_block(lines)
    notes = html.escape(slide["notes"], quote=True)
    return (f'<section class="slide layout-{layout}" id="slide-{index}" tabindex="-1" '
            f'aria-label="Slide {index}" data-notes="{notes}">\n{content}\n</section>')


