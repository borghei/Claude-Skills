#!/usr/bin/env python3
"""
Markdown to HTML — convert an authored markdown document into a single
self-contained HTML file: semantic structure, automatic table of contents,
numbered figures and tables with resolvable cross-references, footnotes, and
an inlined stylesheet.

Parsing lives in md_render.py alongside this file. All user content is
HTML-escaped before any markup is emitted, and link/image URLs are restricted
to safe schemes, so untrusted markdown cannot inject script into the output.

Usage:
    python3 md_to_html.py --input report.md --out report.html
    python3 md_to_html.py --input report.md --out report.html --css theme.css
    python3 md_to_html.py --input report.md --toc-depth 3 --format json
"""

import argparse
import html
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from md_render import Renderer, collect_labels


def strip_frontmatter(lines: List[str]) -> List[str]:
    """Drop a leading YAML frontmatter block if present."""
    if not lines or lines[0].strip() != "---":
        return lines
    end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), 0)
    return lines[end + 1:]


def convert(md_text: str, toc_depth: int) -> Tuple[str, Dict[str, Any]]:
    """Convert markdown source into body HTML plus a conversion report."""
    lines = strip_frontmatter(md_text.replace("\r\n", "\n").split("\n"))
    labels = collect_labels(lines)
    renderer = Renderer(labels, toc_depth)
    renderer.render(lines)
    footnotes, missing = renderer.footnotes_html()
    body = "\n".join(renderer.out).replace("\x01TOC\x01", renderer.toc_html())
    if footnotes:
        body = f"{body}\n{footnotes}"
    title = next((l.strip("# ").strip() for l in lines if l.startswith("# ")), "Document")
    report = {
        "title": title,
        "headings": len(renderer.toc),
        "figures": renderer.counters["fig"],
        "tables": renderer.counters["tbl"],
        "footnotes": len(renderer.notes),
        "undefined_footnotes": missing,
        "unresolved_xrefs": sorted(set(renderer.unresolved)),
        "labels": sorted(labels),
    }
    return body, report


def build_document(title: str, body: str, css: str, lang: str) -> str:
    """Wrap rendered body content in a complete self-contained HTML file."""
    return (f'<!DOCTYPE html>\n<html lang="{html.escape(lang, quote=True)}">\n<head>\n'
            '<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            f"<title>{html.escape(title)}</title>\n<style>\n{css}\n</style>\n"
            f"</head>\n<body>\n<main>\n{body}\n</main>\n</body>\n</html>\n")


def load_css(css_path: Optional[str], skill_root: Path) -> str:
    """Load the stylesheet to inline, defaulting to the bundled document theme."""
    path = Path(css_path) if css_path else skill_root / "assets" / "document_theme.css"
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise SystemExit(
            f"error: stylesheet not found: {path}\n"
            "       pass --css PATH, or restore assets/document_theme.css")


def output(report: Dict[str, Any], out_path: Optional[Path], fmt: str) -> int:
    """Print the conversion report; returns the number of blocking problems."""
    problems = len(report["unresolved_xrefs"]) + len(report["undefined_footnotes"])
    if fmt == "json":
        print(json.dumps({**report, "problems": problems,
                          "gate": "fail" if problems else "pass"}, indent=2))
        return problems
    print(f"Converted: {report['title']}")
    print(f"  headings in TOC : {report['headings']}")
    print(f"  figures         : {report['figures']}")
    print(f"  tables          : {report['tables']}")
    print(f"  footnotes       : {report['footnotes']}")
    if report["unresolved_xrefs"]:
        print(f"  UNRESOLVED refs : {', '.join(report['unresolved_xrefs'])}")
    if report["undefined_footnotes"]:
        print(f"  UNDEFINED notes : {', '.join(report['undefined_footnotes'])}")
    print(f"  written to      : {out_path}" if out_path
          else "  (no --out given; nothing written)")
    print(f"\nGATE: {'FAIL' if problems else 'PASS'}")
    return problems


def main() -> None:
    """Parse arguments, convert the document, and exit non-zero on broken refs."""
    parser = argparse.ArgumentParser(
        description="Convert authored markdown into a self-contained HTML document.")
    parser.add_argument("--input", required=True, help="path to the markdown source file")
    parser.add_argument("--out", help="path to write the generated HTML file")
    parser.add_argument("--css", help="stylesheet to inline (default: bundled document theme)")
    parser.add_argument("--title", help="override the document title (default: first H1)")
    parser.add_argument("--lang", default="en", help="html lang attribute (default: en)")
    parser.add_argument("--toc-depth", type=int, default=2,
                        help="heading levels below H1 to list in the TOC (default: 2)")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                        help="report format (default: text)")
    parser.add_argument("--no-gate", action="store_true",
                        help="always exit 0, even with unresolved references")
    args = parser.parse_args()

    try:
        md_text = Path(args.input).read_text(encoding="utf-8")
        body, report = convert(md_text, args.toc_depth)
        css = load_css(args.css, Path(__file__).resolve().parent.parent)
        document = build_document(args.title or report["title"], body, css, args.lang)
        out_path = Path(args.out) if args.out else None
        if out_path:
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(document, encoding="utf-8")
        problems = output(report, out_path, args.format)
    except FileNotFoundError:
        print(f"error: input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)
    except SystemExit:
        raise
    except Exception as exc:  # noqa: BLE001 - surface an actionable message
        print(f"error: conversion failed ({type(exc).__name__}: {exc})", file=sys.stderr)
        sys.exit(1)
    if problems and not args.no_gate:
        sys.exit(2)  # 2 = gate failed (1 is reserved for tool errors)


if __name__ == "__main__":
    main()
