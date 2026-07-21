#!/usr/bin/env python3
"""
Print Profile — generate a print/PDF stylesheet from a JSON profile, covering
page geometry, running heads, page numbering, break control, orphan/widow
limits, and expansion of external link URLs onto paper.

The generated block is meant to be appended to an already-inlined document
stylesheet, so the exported HTML file stays self-contained.

Usage:
    python3 print_profile.py --input print_profile.json
    python3 print_profile.py --input print_profile.json --out print.css
    python3 print_profile.py --input print_profile.json --format json
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

PAGE_SIZES = {"A4": "210mm x 297mm", "A5": "148mm x 210mm",
              "Letter": "8.5in x 11in", "Legal": "8.5in x 14in"}
NUMBER_POSITIONS = {"bottom-center": "@bottom-center", "bottom-outer": "@bottom-right",
                    "bottom-inner": "@bottom-left", "top-outer": "@top-right"}
# Light values forced on paper so a dark theme never reaches a printer.
PRINT_LIGHT_ROLES = {
    "surface": "#ffffff", "surface-raised": "#f1f5f9", "text": "#0f172a",
    "text-muted": "#475569", "border": "#94a3b8", "link": "#0369a1",
    "accent": "#0369a1", "code-surface": "#f1f5f9", "code-text": "#1e293b",
}


def load_profile(path: Path) -> Dict[str, Any]:
    """Load and validate a print-profile JSON file."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise SystemExit(f"error: profile not found: {path}")
    except json.JSONDecodeError as exc:
        raise SystemExit(f"error: {path} is not valid JSON ({exc.msg}, line {exc.lineno})")
    size = data.get("page", {}).get("size", "A4")
    if size not in PAGE_SIZES:
        raise SystemExit(f"error: unknown page size '{size}' "
                         f"(supported: {', '.join(PAGE_SIZES)})")
    position = data.get("page_numbers", {}).get("position", "bottom-center")
    if position not in NUMBER_POSITIONS:
        raise SystemExit(f"error: unknown page-number position '{position}' "
                         f"(supported: {', '.join(NUMBER_POSITIONS)})")
    return data


def page_rules(profile: Dict[str, Any]) -> List[str]:
    """Build the @page blocks: geometry, margin boxes, and mirrored margins."""
    page = profile.get("page", {})
    numbers = profile.get("page_numbers", {})
    head = profile.get("running_head", {})
    size = page.get("size", "A4")
    orientation = page.get("orientation", "portrait")
    top, bottom = page.get("margin_top", "20mm"), page.get("margin_bottom", "20mm")
    inner, outer = page.get("margin_inner", "20mm"), page.get("margin_outer", "18mm")
    box = NUMBER_POSITIONS[numbers.get("position", "bottom-center")]
    counter = ('counter(page) " / " counter(pages)'
               if numbers.get("format") == "counter-of-total" else "counter(page)")

    lines = [f"@page {{ size: {size} {orientation}; "
             f"margin: {top} {outer} {bottom} {inner}; "
             f"{box} {{ content: {counter}; font-size: 9pt; color: #475569; }} }}"]
    if page.get("double_sided"):
        lines.append(f"@page :left {{ margin: {top} {inner} {bottom} {outer}; }}")
        lines.append(f"@page :right {{ margin: {top} {outer} {bottom} {inner}; }}")
    if head.get("left") or head.get("right"):
        left = json.dumps(head.get("left", ""))
        right = json.dumps(head.get("right", ""))
        head_style = "font-size: 9pt; color: #475569;"
        lines.append(f"@page {{ @top-left {{ content: {left}; {head_style} }} "
                     f"@top-right {{ content: {right}; {head_style} }} }}")
    if not head.get("show_on_first_page", False):
        lines.append("@page :first { @top-left { content: none; } "
                     "@top-right { content: none; } }")
    if numbers.get("start_at", 1) != 1:
        lines.append(f"body {{ counter-reset: page {int(numbers['start_at']) - 1}; }}")
    return lines


def body_rules(profile: Dict[str, Any]) -> List[str]:
    """Build the in-flow rules: type size, breaks, orphans, widows, link URLs."""
    typo = profile.get("typography", {})
    breaks = profile.get("breaks", {})
    links = profile.get("link_urls", {})
    lines: List[str] = []

    if profile.get("force_light_theme", True):
        forced = " ".join(f"--color-{k}: {v};" for k, v in PRINT_LIGHT_ROLES.items())
        lines.append(f":root {{ {forced} }}")
    lines.append(f"body {{ font-size: {typo.get('body_pt', 11)}pt; "
                 f"line-height: {typo.get('line_height', 1.45)}; "
                 f"background: #ffffff; padding: 0; }}")
    lines.append("main { max-width: none; margin: 0; }")
    if typo.get("hyphenate"):
        lines.append("p, li { hyphens: auto; }")
    lines.append(f"p, li, blockquote {{ orphans: {int(typo.get('orphans', 3))}; "
                 f"widows: {int(typo.get('widows', 3))}; }}")
    if breaks.get("page_break_before"):
        lines.append(", ".join(breaks["page_break_before"]) + " { break-before: page; }")
    if breaks.get("avoid_break_after"):
        lines.append(", ".join(breaks["avoid_break_after"]) + " { break-after: avoid-page; }")
    if breaks.get("avoid_break_inside"):
        lines.append(", ".join(breaks["avoid_break_inside"]) + " { break-inside: avoid; }")
    if breaks.get("toc_break_after"):
        lines.append(".toc { break-after: page; border: 0; background: none; padding: 0; }")
    if links.get("expand_external", True):
        lines.append('a[href^="http"]::after { content: " (" attr(href) ")"; '
                     "font-size: 9pt; word-break: break-all; }")
        for selector in links.get("skip_selectors", []):
            lines.append(f"{selector}::after {{ content: none; }}")
    return lines


def build_css(profile: Dict[str, Any]) -> str:
    """Render the complete @media print block for the profile."""
    body = "\n".join(f"  {rule}" for rule in body_rules(profile))
    pages = "\n".join(f"  {rule}" for rule in page_rules(profile))
    return (f"/* print profile: {profile.get('name', 'untitled')} */\n"
            f"@media print {{\n{pages}\n{body}\n}}\n")


def summarize(profile: Dict[str, Any], css: str) -> Dict[str, Any]:
    """Build a machine-readable summary of the generated print profile."""
    page = profile.get("page", {})
    size = page.get("size", "A4")
    return {
        "profile": profile.get("name", "untitled"),
        "page_size": size,
        "page_dimensions": PAGE_SIZES[size],
        "orientation": page.get("orientation", "portrait"),
        "double_sided": bool(page.get("double_sided")),
        "body_pt": profile.get("typography", {}).get("body_pt", 11),
        "running_head": bool(profile.get("running_head", {}).get("left")
                             or profile.get("running_head", {}).get("right")),
        "forces_light_theme": bool(profile.get("force_light_theme", True)),
        "rules": css.count(";"),
        "css_bytes": len(css.encode("utf-8")),
    }


def output(summary: Dict[str, Any], css: str, fmt: str, out_path: Any) -> None:
    """Emit the requested representation to stdout."""
    if fmt == "css":
        print(css)
        return
    if fmt == "json":
        print(json.dumps(summary, indent=2))
        return
    print(f"Print profile: {summary['profile']}")
    print(f"  page        : {summary['page_size']} {summary['orientation']} "
          f"({summary['page_dimensions']})")
    print(f"  double-sided: {'yes (mirrored margins)' if summary['double_sided'] else 'no'}")
    print(f"  body size   : {summary['body_pt']}pt")
    print(f"  running head: {'yes' if summary['running_head'] else 'no'}")
    print(f"  light forced: {'yes' if summary['forces_light_theme'] else 'NO - dark may print'}")
    print(f"  output      : {summary['css_bytes']} bytes")
    if out_path:
        print(f"  written to  : {out_path}")
    else:
        print("  (use --out PATH to write the CSS, or --format css to print it)")
    if not summary["forces_light_theme"]:
        print("\nWARNING: force_light_theme is false. Most browsers strip background\n"
              "colors when printing, which leaves light text on white paper.")


def main() -> None:
    """Parse arguments, generate the print stylesheet, and report."""
    parser = argparse.ArgumentParser(
        description="Generate a print/PDF stylesheet from a JSON print profile.")
    parser.add_argument("--input", required=True, help="path to the print-profile JSON file")
    parser.add_argument("--out", help="write the generated CSS to this path")
    parser.add_argument("--format", choices=["text", "json", "css"], default="text",
                        help="stdout format: text summary (default), json summary, or raw css")
    parser.add_argument("--append-to",
                        help="append the generated block to an existing stylesheet")
    args = parser.parse_args()

    try:
        profile = load_profile(Path(args.input))
        css = build_css(profile)
        out_path = Path(args.out) if args.out else None
        if out_path:
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(css, encoding="utf-8")
        if args.append_to:
            target = Path(args.append_to)
            if not target.exists():
                raise SystemExit(f"error: --append-to target does not exist: {target}")
            with target.open("a", encoding="utf-8") as handle:
                handle.write("\n" + css)
        output(summarize(profile, css), css, args.format, out_path)
    except SystemExit:
        raise
    except OSError as exc:
        print(f"error: could not write output ({exc})", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:  # noqa: BLE001 - surface an actionable message
        print(f"error: print profile generation failed ({type(exc).__name__}: {exc})",
              file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
