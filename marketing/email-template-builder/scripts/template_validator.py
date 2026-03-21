#!/usr/bin/env python3
"""
Email Template Validator

Validates email HTML templates for client compatibility, accessibility,
responsive design, and deliverability best practices.

Usage:
    python template_validator.py template.html
    python template_validator.py template.html --json
"""

import argparse
import json
import re
import sys
from pathlib import Path


def validate_template(html: str) -> dict:
    result = {
        "valid": True,
        "score": 100,
        "errors": [],
        "warnings": [],
        "info": [],
        "compatibility": {},
        "accessibility": {},
    }

    # --- Structure checks ---
    has_html_tag = bool(re.search(r"<html", html, re.IGNORECASE))
    has_head = bool(re.search(r"<head", html, re.IGNORECASE))
    has_body = bool(re.search(r"<body", html, re.IGNORECASE))
    has_doctype = bool(re.search(r"<!doctype", html, re.IGNORECASE))
    has_meta_viewport = bool(re.search(r'name\s*=\s*"viewport"', html, re.IGNORECASE))
    has_charset = bool(re.search(r'charset\s*=\s*"?utf-8', html, re.IGNORECASE))
    has_lang = bool(re.search(r'<html[^>]+lang\s*=', html, re.IGNORECASE))

    if not has_html_tag:
        result["errors"].append("Missing <html> tag")
        result["score"] -= 10
    if not has_head:
        result["warnings"].append("Missing <head> tag")
        result["score"] -= 5
    if not has_body:
        result["errors"].append("Missing <body> tag")
        result["score"] -= 10
    if has_meta_viewport:
        result["info"].append("Viewport meta tag present (good for mobile)")
    if has_charset:
        result["info"].append("UTF-8 charset declared")
    if has_lang:
        result["info"].append("Language attribute set on <html>")
    else:
        result["warnings"].append("Missing lang attribute on <html> tag (accessibility)")
        result["score"] -= 3

    # --- Outlook compatibility ---
    uses_flexbox = bool(re.search(r"display\s*:\s*flex", html, re.IGNORECASE))
    uses_grid = bool(re.search(r"display\s*:\s*grid", html, re.IGNORECASE))
    uses_tables = bool(re.search(r"<table", html, re.IGNORECASE))
    uses_css_vars = bool(re.search(r"var\(--", html))
    uses_calc = bool(re.search(r"calc\(", html, re.IGNORECASE))

    compat = {}
    compat["outlook_safe"] = not uses_flexbox and not uses_grid and uses_tables
    compat["uses_tables"] = uses_tables
    compat["uses_flexbox"] = uses_flexbox
    compat["uses_grid"] = uses_grid

    if uses_flexbox:
        result["warnings"].append("CSS flexbox detected -- breaks in Outlook (Windows). Use table layout.")
        result["score"] -= 8
    if uses_grid:
        result["warnings"].append("CSS grid detected -- breaks in Outlook (Windows). Use table layout.")
        result["score"] -= 8
    if uses_css_vars:
        result["warnings"].append("CSS custom properties (variables) not supported in many email clients.")
        result["score"] -= 5
    if uses_calc:
        result["warnings"].append("calc() not supported in Outlook. Use fixed values.")
        result["score"] -= 3
    if not uses_tables:
        result["warnings"].append("No <table> elements found. Table-based layout is most compatible for email.")
        result["score"] -= 5

    result["compatibility"] = compat

    # --- Inline styles check ---
    style_blocks = len(re.findall(r"<style", html, re.IGNORECASE))
    inline_styles = len(re.findall(r'style\s*=\s*"', html, re.IGNORECASE))

    if style_blocks > 0 and inline_styles == 0:
        result["warnings"].append("Styles in <style> blocks only -- Gmail strips <head> styles. Use inline styles.")
        result["score"] -= 10
    elif inline_styles > 0:
        result["info"].append(f"Inline styles detected ({inline_styles} elements) -- good for email client compatibility.")

    # --- Image checks ---
    images = re.findall(r"<img[^>]*>", html, re.IGNORECASE)
    images_no_alt = [img for img in images if not re.search(r'alt\s*=\s*"[^"]+', img, re.IGNORECASE)]
    images_no_dims = [img for img in images if not (re.search(r'width', img, re.IGNORECASE) and re.search(r'height', img, re.IGNORECASE))]

    acc = {}
    acc["total_images"] = len(images)
    acc["images_missing_alt"] = len(images_no_alt)
    acc["images_missing_dimensions"] = len(images_no_dims)

    if images_no_alt:
        result["warnings"].append(f"{len(images_no_alt)} image(s) missing alt text (accessibility + deliverability)")
        result["score"] -= len(images_no_alt) * 2
    if images_no_dims:
        result["warnings"].append(f"{len(images_no_dims)} image(s) missing width/height (causes CLS)")
        result["score"] -= len(images_no_dims)

    result["accessibility"] = acc

    # --- Responsive check ---
    has_media_queries = bool(re.search(r"@media", html, re.IGNORECASE))
    has_max_width = bool(re.search(r"max-width", html, re.IGNORECASE))

    if has_media_queries:
        result["info"].append("Media queries detected (responsive design)")
    else:
        result["warnings"].append("No media queries found. Template may not be responsive on mobile.")
        result["score"] -= 5

    # --- Container width ---
    containers = re.findall(r'(?:max-)?width\s*[:=]\s*"?(\d+)(?:px)?', html)
    wide = [int(w) for w in containers if int(w) > 600]
    if wide:
        result["warnings"].append(f"Container wider than 600px detected ({max(wide)}px). Breaks on Gmail mobile.")
        result["score"] -= 5

    # --- Dark mode ---
    has_dark = bool(re.search(r"prefers-color-scheme:\s*dark", html, re.IGNORECASE))
    if has_dark:
        result["info"].append("Dark mode support detected")
    else:
        result["warnings"].append("No dark mode support. 30%+ of users use dark mode.")
        result["score"] -= 3

    # --- Size check ---
    size_kb = len(html.encode()) / 1024
    if size_kb > 102:
        result["errors"].append(f"Template is {size_kb:.0f}KB. Gmail clips emails over 102KB.")
        result["score"] -= 15
    elif size_kb > 80:
        result["warnings"].append(f"Template is {size_kb:.0f}KB. Approaching Gmail's 102KB clip threshold.")
        result["score"] -= 5
    else:
        result["info"].append(f"Template size: {size_kb:.1f}KB (under 102KB Gmail limit)")

    result["score"] = max(0, min(100, result["score"]))
    result["valid"] = result["score"] >= 50 and not result["errors"]
    result["grade"] = "A" if result["score"] >= 90 else "B" if result["score"] >= 75 else "C" if result["score"] >= 60 else "D" if result["score"] >= 40 else "F"

    return result


def format_human(result: dict) -> str:
    lines = ["\n" + "=" * 55, "  EMAIL TEMPLATE VALIDATOR", "=" * 55]
    lines.append(f"\n  Score: {result['score']}/100 (Grade: {result['grade']})")
    lines.append(f"  Valid: {'Yes' if result['valid'] else 'No'}")

    c = result["compatibility"]
    lines.append(f"\n  Compatibility:")
    lines.append(f"    Outlook Safe: {'Yes' if c.get('outlook_safe') else 'No'}")
    lines.append(f"    Uses Tables: {'Yes' if c.get('uses_tables') else 'No'}")

    if result["errors"]:
        lines.append(f"\n  Errors:")
        for e in result["errors"]:
            lines.append(f"    X {e}")

    if result["warnings"]:
        lines.append(f"\n  Warnings:")
        for w in result["warnings"]:
            lines.append(f"    ! {w}")

    if result["info"]:
        lines.append(f"\n  Info:")
        for i in result["info"]:
            lines.append(f"    + {i}")

    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Validate email HTML template for compatibility and deliverability.")
    parser.add_argument("file", help="HTML template file")
    parser.add_argument("--json", action="store_true", dest="json_output")
    args = parser.parse_args()

    try:
        html = Path(args.file).read_text()
    except FileNotFoundError:
        print(f"Error: {args.file} not found", file=sys.stderr)
        sys.exit(1)

    result = validate_template(html)
    if args.json_output:
        print(json.dumps(result, indent=2))
    else:
        print(format_human(result))


if __name__ == "__main__":
    main()
