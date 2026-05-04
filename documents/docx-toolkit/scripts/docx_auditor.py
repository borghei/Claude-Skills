#!/usr/bin/env python3
"""
Docx Auditor — audit a Microsoft Word .docx file using the Python standard
library only. Reads the underlying OOXML directly via zipfile + xml.etree.

Usage:
    python docx_auditor.py document.docx
    python docx_auditor.py document.docx --json
"""

import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path


W_NS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def load(path):
    if not zipfile.is_zipfile(path):
        raise ValueError(f"Not a valid .docx file: {path}")
    with zipfile.ZipFile(path) as zf:
        return {name: zf.read(name) for name in zf.namelist()}


def parse_xml(blob):
    try:
        return ET.fromstring(blob)
    except ET.ParseError:
        return None


def text_of(element):
    return "".join(element.itertext())


def audit(path):
    files = load(path)

    document_xml = files.get("word/document.xml")
    if not document_xml:
        raise ValueError("Missing word/document.xml — file may be corrupt")
    doc = parse_xml(document_xml)
    if doc is None:
        raise ValueError("Could not parse word/document.xml")

    paragraphs = doc.findall(f".//{W_NS}p")
    paragraph_count = len(paragraphs)

    full_text = " ".join(text_of(p) for p in paragraphs)
    word_count = len([w for w in re.split(r"\s+", full_text) if w.strip()])

    # Heading hierarchy
    headings = []
    style_usage = {}
    for p in paragraphs:
        pPr = p.find(f"{W_NS}pPr")
        if pPr is None:
            continue
        pStyle = pPr.find(f"{W_NS}pStyle")
        if pStyle is None:
            continue
        style = pStyle.get(f"{W_NS}val", "")
        style_usage[style] = style_usage.get(style, 0) + 1
        if style.lower().startswith("heading"):
            try:
                level = int(re.findall(r"\d+", style)[0])
                headings.append({"level": level, "text": text_of(p).strip()[:80]})
            except (IndexError, ValueError):
                pass

    # Detect heading gaps
    gaps = []
    prev_level = 0
    for h in headings:
        if prev_level and h["level"] > prev_level + 1:
            gaps.append({
                "from_level": prev_level,
                "to_level": h["level"],
                "at_heading": h["text"],
            })
        prev_level = h["level"]

    # Comments
    comments_xml = files.get("word/comments.xml")
    comment_count = 0
    if comments_xml:
        comments_doc = parse_xml(comments_xml)
        if comments_doc is not None:
            comment_count = len(comments_doc.findall(f"{W_NS}comment"))

    # Tracked changes
    tracked_change_tags = (
        f"{W_NS}ins",
        f"{W_NS}del",
        f"{W_NS}cellIns",
        f"{W_NS}cellDel",
        f"{W_NS}moveFrom",
        f"{W_NS}moveTo",
    )
    tracked_changes = sum(len(doc.findall(f".//{tag}")) for tag in tracked_change_tags)

    # Hyperlinks
    hyperlink_count = len(doc.findall(f".//{W_NS}hyperlink"))

    # Images
    image_count = sum(1 for name in files if name.startswith("word/media/"))

    # Tables
    table_count = len(doc.findall(f".//{W_NS}tbl"))

    # Paragraphs with no style (default body)
    default_paragraphs = sum(
        1 for p in paragraphs
        if (p.find(f"{W_NS}pPr") is None
            or p.find(f"{W_NS}pPr/{W_NS}pStyle") is None)
    )

    return {
        "file": str(path),
        "word_count": word_count,
        "paragraph_count": paragraph_count,
        "default_style_paragraphs": default_paragraphs,
        "headings": headings,
        "heading_gaps": gaps,
        "styles_used": dict(sorted(style_usage.items(), key=lambda kv: -kv[1])),
        "comment_count": comment_count,
        "tracked_changes_count": tracked_changes,
        "tracked_changes_present": tracked_changes > 0,
        "hyperlink_count": hyperlink_count,
        "image_count": image_count,
        "table_count": table_count,
    }


def render_human(result):
    lines = [f"Audit: {result['file']}"]
    lines.append("")
    lines.append(f"  Word count:           {result['word_count']}")
    lines.append(f"  Paragraphs:           {result['paragraph_count']}")
    lines.append(f"  Default-style paras:  {result['default_style_paragraphs']}")
    lines.append(f"  Tables:               {result['table_count']}")
    lines.append(f"  Hyperlinks:           {result['hyperlink_count']}")
    lines.append(f"  Images:               {result['image_count']}")
    lines.append(f"  Comments:             {result['comment_count']}")
    lines.append(f"  Tracked-change marks: {result['tracked_changes_count']} ({'PRESENT' if result['tracked_changes_present'] else 'none'})")
    lines.append("")
    lines.append(f"Heading hierarchy ({len(result['headings'])} headings):")
    for h in result["headings"][:30]:
        indent = "  " * h["level"]
        lines.append(f"  {indent}H{h['level']}: {h['text']}")
    if len(result["headings"]) > 30:
        lines.append(f"  … and {len(result['headings']) - 30} more")
    if result["heading_gaps"]:
        lines.append("")
        lines.append(f"Heading gaps detected ({len(result['heading_gaps'])}):")
        for g in result["heading_gaps"]:
            lines.append(f"  H{g['from_level']} → H{g['to_level']} at: {g['at_heading']}")
    lines.append("")
    lines.append(f"Styles used ({len(result['styles_used'])}):")
    for style, count in list(result["styles_used"].items())[:15]:
        lines.append(f"  {style:<30} {count}")
    lines.append("")
    issues = []
    if result["comment_count"] > 0:
        issues.append(f"{result['comment_count']} comment(s) present")
    if result["tracked_changes_present"]:
        issues.append("tracked changes present")
    if result["heading_gaps"]:
        issues.append(f"{len(result['heading_gaps'])} heading gap(s)")
    if len(result["styles_used"]) > 12:
        issues.append(f"style sprawl: {len(result['styles_used'])} styles used")
    if issues:
        lines.append(f"Pre-handoff issues: {', '.join(issues)}")
    else:
        lines.append("Pre-handoff issues: none — document is clean.")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Audit a .docx file (stdlib only).")
    parser.add_argument("docx", help="Path to .docx file")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    path = Path(args.docx)
    if not path.exists():
        print(f"Error: file not found: {path}", file=sys.stderr)
        return 1

    try:
        result = audit(path)
    except (ValueError, zipfile.BadZipFile) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(render_human(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
