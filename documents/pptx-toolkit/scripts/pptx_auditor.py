#!/usr/bin/env python3
"""
Pptx Auditor — audit a Microsoft PowerPoint .pptx file using the Python
standard library only. Reads OOXML directly via zipfile + xml.etree.

Usage:
    python pptx_auditor.py deck.pptx
    python pptx_auditor.py deck.pptx --json
"""

import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path


P_NS = "{http://schemas.openxmlformats.org/presentationml/2006/main}"
A_NS = "{http://schemas.openxmlformats.org/drawingml/2006/main}"


def parse_xml(blob):
    try:
        return ET.fromstring(blob)
    except ET.ParseError:
        return None


def text_of(element):
    return "".join(element.itertext())


def slide_words(slide_xml):
    """Word count for a slide, summing all <a:t> text runs."""
    doc = parse_xml(slide_xml)
    if doc is None:
        return 0, ""
    runs = doc.findall(f".//{A_NS}t")
    text = " ".join(r.text or "" for r in runs)
    word_count = len([w for w in re.split(r"\s+", text) if w.strip()])
    return word_count, text


def slide_is_hidden(slide_xml):
    doc = parse_xml(slide_xml)
    if doc is None:
        return False
    return doc.attrib.get("show") == "0"


def slide_animation_count(slide_xml):
    doc = parse_xml(slide_xml)
    if doc is None:
        return 0
    # Animation timing nodes — sub-elements of <p:timing>
    return len(doc.findall(f".//{P_NS}timing//{P_NS}cTn"))


def slide_image_count(files, slide_name):
    """Count how many images this slide references via its rels."""
    rel_path = slide_name.replace("slides/", "slides/_rels/") + ".rels"
    if rel_path not in files:
        return 0
    rels_xml = parse_xml(files[rel_path])
    if rels_xml is None:
        return 0
    count = 0
    for rel in rels_xml:
        target = rel.attrib.get("Target", "")
        if "/media/" in target:
            count += 1
    return count


def has_speaker_notes(files, slide_full_name):
    """A slide has speaker notes if it links to a notesSlide with text.

    slide_full_name is the full archive path, e.g. 'ppt/slides/slide1.xml'.
    """
    rel_path = slide_full_name.replace("slides/", "slides/_rels/") + ".rels"
    if rel_path not in files:
        return False
    rels_xml = parse_xml(files[rel_path])
    if rels_xml is None:
        return False
    notes_target = None
    for rel in rels_xml:
        if "notesSlide" in rel.attrib.get("Type", ""):
            notes_target = rel.attrib.get("Target", "")
            break
    if not notes_target:
        return False
    # Resolve relative path: target like "../notesSlides/notesSlide1.xml"
    # relative to "ppt/slides/_rels/slide1.xml.rels" → "ppt/notesSlides/notesSlide1.xml"
    notes_target_norm = notes_target.replace("../", "")
    notes_blob = files.get(f"ppt/{notes_target_norm}")
    if not notes_blob:
        return False
    doc = parse_xml(notes_blob)
    if doc is None:
        return False
    notes_text = " ".join((r.text or "") for r in doc.findall(f".//{A_NS}t"))
    cleaned = re.sub(r"\d+", "", notes_text).strip()
    return len(cleaned) > 5


def theme_name(files):
    for name, blob in files.items():
        if name.startswith("ppt/theme/theme") and name.endswith(".xml"):
            doc = parse_xml(blob)
            if doc is not None:
                return doc.attrib.get("name", "(unnamed)")
    return "(unknown)"


def audit(path):
    if not zipfile.is_zipfile(path):
        raise ValueError(f"Not a valid .pptx file: {path}")
    with zipfile.ZipFile(path) as zf:
        files = {name: zf.read(name) for name in zf.namelist()}

    slide_names = sorted(
        n for n in files if n.startswith("ppt/slides/slide") and n.endswith(".xml")
    )

    slides = []
    for name in slide_names:
        xml = files[name]
        words, _ = slide_words(xml)
        slides.append({
            "name": name.split("/")[-1],
            "words": words,
            "hidden": slide_is_hidden(xml),
            "animation_count": slide_animation_count(xml),
            "image_count": slide_image_count(files, name),
            "has_notes": has_speaker_notes(files, name),
        })

    slide_count = len(slides)
    hidden_count = sum(1 for s in slides if s["hidden"])
    notes_count = sum(1 for s in slides if s["has_notes"])
    total_words = sum(s["words"] for s in slides)
    total_animations = sum(s["animation_count"] for s in slides)
    total_images = sum(s["image_count"] for s in slides)
    embedded_media = sum(1 for n in files if n.startswith("ppt/media/"))

    densest = sorted(slides, key=lambda s: -s["words"])[:5]

    return {
        "file": str(path),
        "theme": theme_name(files),
        "slide_count": slide_count,
        "hidden_slide_count": hidden_count,
        "slides_with_notes": notes_count,
        "notes_coverage_pct": round(100 * notes_count / slide_count, 1) if slide_count else 0,
        "words_total": total_words,
        "words_per_slide_mean": round(total_words / slide_count, 1) if slide_count else 0,
        "words_per_slide_max": max((s["words"] for s in slides), default=0),
        "animations_total": total_animations,
        "images_total": total_images,
        "embedded_media_total": embedded_media,
        "top5_densest_slides": densest,
        "slides": slides,
    }


def render_human(result):
    lines = [f"Audit: {result['file']}"]
    lines.append("")
    lines.append(f"  Theme:                {result['theme']}")
    lines.append(f"  Slide count:          {result['slide_count']} ({result['hidden_slide_count']} hidden)")
    lines.append(f"  Speaker notes:        {result['slides_with_notes']}/{result['slide_count']} ({result['notes_coverage_pct']}%)")
    lines.append(f"  Total words:          {result['words_total']}")
    lines.append(f"  Words/slide (mean):   {result['words_per_slide_mean']}")
    lines.append(f"  Words/slide (max):    {result['words_per_slide_max']}")
    lines.append(f"  Total animations:     {result['animations_total']}")
    lines.append(f"  Total images:         {result['images_total']}")
    lines.append(f"  Embedded media files: {result['embedded_media_total']}")
    lines.append("")
    if result["top5_densest_slides"]:
        lines.append("Top 5 densest slides:")
        for s in result["top5_densest_slides"]:
            lines.append(f"  {s['name']:<14} {s['words']} words"
                         + (" (hidden)" if s["hidden"] else "")
                         + (" [no notes]" if not s["has_notes"] else ""))
    lines.append("")
    issues = []
    if result["words_per_slide_max"] > 60:
        issues.append(f"slide(s) over 60 words — see top 5")
    if result["hidden_slide_count"] > 0:
        issues.append(f"{result['hidden_slide_count']} hidden slide(s) present")
    if result["notes_coverage_pct"] < 70 and result["slide_count"] > 5:
        issues.append(f"speaker-notes coverage low: {result['notes_coverage_pct']}%")
    if result["animations_total"] > 100:
        issues.append(f"high animation count: {result['animations_total']}")
    if issues:
        lines.append("Pre-handoff issues:")
        for i in issues:
            lines.append(f"  • {i}")
    else:
        lines.append("Pre-handoff issues: none — deck is in good shape.")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Audit a .pptx file (stdlib only).")
    parser.add_argument("pptx", help="Path to .pptx file")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    path = Path(args.pptx)
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
