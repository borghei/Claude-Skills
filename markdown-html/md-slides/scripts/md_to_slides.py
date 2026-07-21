#!/usr/bin/env python3
"""
Markdown to Slides — convert a markdown source into a self-contained HTML slide
deck: slide splitting, per-slide layouts, speaker notes, keyboard navigation,
and an inlined stylesheet and script.

Slide parsing and rendering live in slide_render.py alongside this file. User
content is HTML-escaped before markup is emitted and URLs are restricted to a
safe-scheme allowlist, so untrusted markdown cannot inject script into a deck.

Usage:
    python3 md_to_slides.py --input deck.md --out deck.html
    python3 md_to_slides.py --input deck.md --out deck.html --split-on h2
    python3 md_to_slides.py --input deck.md --format json
"""

import argparse
import html
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from slide_render import HEADING_RE, LAYOUTS, render_slide, split_slides, strip_frontmatter


def build_deck(slides: List[Dict[str, Any]], title: str, css: str, js: str,
               lang: str) -> str:
    """Assemble the complete self-contained deck document."""
    sections = "\n".join(render_slide(s, i + 1) for i, s in enumerate(slides))
    return (f'<!DOCTYPE html>\n<html lang="{html.escape(lang, quote=True)}">\n<head>\n'
            '<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            f"<title>{html.escape(title)}</title>\n<style>\n{css}\n</style>\n</head>\n"
            '<body>\n<div id="progress"></div>\n<main>\n'
            f"{sections}\n</main>\n"
            '<div id="counter" aria-live="polite"></div>\n'
            '<div id="help">arrows navigate &middot; N notes &middot; T theme &middot; F full screen</div>\n'
            '<aside id="notes-pane" aria-label="Speaker notes"></aside>\n'
            f"<script>\n{js}\n</script>\n</body>\n</html>\n")


def load_asset(path: Optional[str], default: Path, kind: str) -> str:
    """Load an inlinable asset, falling back to the bundled deck default."""
    target = Path(path) if path else default
    try:
        return target.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise SystemExit(f"error: {kind} not found: {target}\n"
                         f"       pass an explicit path, or restore assets/{default.name}")


def summarize(slides: List[Dict[str, Any]], title: str) -> Dict[str, Any]:
    """Build a machine-readable summary of the generated deck."""
    layouts: Dict[str, int] = {}
    for slide in slides:
        name = slide["layout"] if slide["layout"] in LAYOUTS else "default"
        layouts[name] = layouts.get(name, 0) + 1
    with_notes = sum(1 for s in slides if s["notes"])
    return {"title": title, "slides": len(slides), "layouts": layouts,
            "unknown_layouts": sorted({s["layout"] for s in slides} - LAYOUTS),
            "with_notes": with_notes, "without_notes": len(slides) - with_notes}


def output(summary: Dict[str, Any], out_path: Optional[Path], fmt: str) -> None:
    """Print the build report in the requested format."""
    if fmt == "json":
        print(json.dumps({**summary, "output": str(out_path) if out_path else None}, indent=2))
        return
    layouts = ", ".join(f"{k}={v}" for k, v in sorted(summary["layouts"].items()))
    print(f"Deck: {summary['title']}")
    print(f"  slides      : {summary['slides']}")
    print(f"  layouts     : {layouts}")
    print(f"  with notes  : {summary['with_notes']} ({summary['without_notes']} without)")
    if summary["unknown_layouts"]:
        print("  UNKNOWN layouts (rendered as default): "
              f"{', '.join(summary['unknown_layouts'])}")
    print(f"  written to  : {out_path}" if out_path else "  (no --out given; nothing written)")


def main() -> None:
    """Parse arguments, build the deck, and report."""
    parser = argparse.ArgumentParser(
        description="Convert markdown into a self-contained HTML slide deck.")
    parser.add_argument("--input", required=True, help="path to the markdown deck source")
    parser.add_argument("--out", help="path to write the generated HTML deck")
    parser.add_argument("--css", help="stylesheet to inline (default: bundled deck theme)")
    parser.add_argument("--js", help="navigation script to inline (default: bundled deck_nav.js)")
    parser.add_argument("--title", help="deck title (default: first heading)")
    parser.add_argument("--lang", default="en", help="html lang attribute (default: en)")
    parser.add_argument("--split-on", choices=["rule", "h2"], default="rule",
                        help="split slides on '---' only (default) or also on every h2")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                        help="report format (default: text)")
    args = parser.parse_args()

    try:
        lines = strip_frontmatter(
            Path(args.input).read_text(encoding="utf-8").replace("\r\n", "\n").split("\n"))
        slides = split_slides(lines, args.split_on)
        if not slides:
            raise SystemExit("error: no slides found - separate slides with a '---' line")
        assets = Path(__file__).resolve().parent.parent / "assets"
        css = load_asset(args.css, assets / "deck_theme.css", "stylesheet")
        js = load_asset(args.js, assets / "deck_nav.js", "navigation script")
        first = next((HEADING_RE.match(l.strip()).group("text")
                      for s in slides for l in s["lines"] if HEADING_RE.match(l.strip())), "Deck")
        title = args.title or first
        out_path = Path(args.out) if args.out else None
        if out_path:
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(build_deck(slides, title, css, js, args.lang), encoding="utf-8")
        output(summarize(slides, title), out_path, args.format)
    except FileNotFoundError:
        print(f"error: input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)
    except SystemExit:
        raise
    except Exception as exc:  # noqa: BLE001 - surface an actionable message
        print(f"error: deck build failed ({type(exc).__name__}: {exc})", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
