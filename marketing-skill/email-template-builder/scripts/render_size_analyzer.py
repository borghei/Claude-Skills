#!/usr/bin/env python3
"""
Email Render Size Analyzer

Analyzes email template file size, estimates render weight,
and checks against Gmail's 102KB clip threshold.

Usage:
    python render_size_analyzer.py template.html
    python render_size_analyzer.py template.html --json
    python render_size_analyzer.py --dir templates/
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

GMAIL_CLIP_THRESHOLD_KB = 102
WARNING_THRESHOLD_KB = 80
OPTIMAL_SIZE_KB = 50


def analyze_file(filepath: str) -> dict:
    path = Path(filepath)
    html = path.read_text()
    raw_bytes = len(html.encode("utf-8"))
    raw_kb = raw_bytes / 1024

    # Count elements
    tags = re.findall(r"<(\w+)", html)
    tag_counts = {}
    for t in tags:
        t_lower = t.lower()
        tag_counts[t_lower] = tag_counts.get(t_lower, 0) + 1

    # Inline style weight
    inline_styles = re.findall(r'style\s*=\s*"([^"]*)"', html)
    style_bytes = sum(len(s.encode()) for s in inline_styles)
    style_kb = style_bytes / 1024

    # Style block weight
    style_blocks = re.findall(r"<style[^>]*>(.*?)</style>", html, re.DOTALL | re.IGNORECASE)
    block_bytes = sum(len(s.encode()) for s in style_blocks)
    block_kb = block_bytes / 1024

    # Image references
    img_srcs = re.findall(r'<img[^>]+src\s*=\s*"([^"]*)"', html, re.IGNORECASE)
    base64_images = [s for s in img_srcs if s.startswith("data:")]
    base64_bytes = sum(len(s.encode()) for s in base64_images)

    # Comments
    comments = re.findall(r"<!--.*?-->", html, re.DOTALL)
    comment_bytes = sum(len(c.encode()) for c in comments)

    # Whitespace
    stripped = re.sub(r"\s+", " ", html)
    minified_bytes = len(stripped.encode())
    whitespace_bytes = raw_bytes - minified_bytes

    result = {
        "file": str(path.name),
        "raw_size_kb": round(raw_kb, 2),
        "gmail_status": "CLIPPED" if raw_kb > GMAIL_CLIP_THRESHOLD_KB else "WARNING" if raw_kb > WARNING_THRESHOLD_KB else "OK",
        "headroom_kb": round(GMAIL_CLIP_THRESHOLD_KB - raw_kb, 2),
        "breakdown": {
            "inline_styles_kb": round(style_kb, 2),
            "style_blocks_kb": round(block_kb, 2),
            "base64_images_kb": round(base64_bytes / 1024, 2),
            "comments_kb": round(comment_bytes / 1024, 2),
            "whitespace_kb": round(whitespace_bytes / 1024, 2),
            "content_kb": round(minified_bytes / 1024, 2),
        },
        "element_counts": dict(sorted(tag_counts.items(), key=lambda x: -x[1])[:10]),
        "total_elements": len(tags),
        "image_count": len(img_srcs),
        "base64_image_count": len(base64_images),
        "recommendations": [],
    }

    # Recommendations
    if raw_kb > GMAIL_CLIP_THRESHOLD_KB:
        result["recommendations"].append(f"CRITICAL: Email is {raw_kb:.0f}KB -- Gmail will clip at 102KB. Reduce by {raw_kb - GMAIL_CLIP_THRESHOLD_KB:.0f}KB.")

    if base64_bytes > 0:
        result["recommendations"].append(f"Replace base64 images ({base64_bytes/1024:.1f}KB) with hosted URLs to reduce size.")

    if comment_bytes > 500:
        result["recommendations"].append(f"Remove HTML comments to save {comment_bytes/1024:.1f}KB.")

    if whitespace_bytes > raw_bytes * 0.15:
        result["recommendations"].append(f"Minify HTML to save ~{whitespace_bytes/1024:.1f}KB of whitespace.")

    if style_kb > 10:
        result["recommendations"].append("Large inline style payload. Consider consolidating repeated styles.")

    if len(tags) > 500:
        result["recommendations"].append(f"High element count ({len(tags)}). Simplify template structure.")

    if raw_kb <= OPTIMAL_SIZE_KB:
        result["recommendations"].append("Template size is optimal for fast rendering across all clients.")

    return result


def format_human(results: list) -> str:
    lines = ["\n" + "=" * 55, "  EMAIL RENDER SIZE ANALYZER", "=" * 55]

    for r in results:
        status_icon = {"OK": "+", "WARNING": "!", "CLIPPED": "X"}
        lines.append(f"\n  File: {r['file']}")
        lines.append(f"  Size: {r['raw_size_kb']}KB [{status_icon.get(r['gmail_status'], '?')}] {r['gmail_status']}")
        lines.append(f"  Gmail Headroom: {r['headroom_kb']}KB remaining")
        lines.append(f"  Elements: {r['total_elements']} | Images: {r['image_count']}")

        b = r["breakdown"]
        lines.append(f"\n  Size Breakdown:")
        lines.append(f"    Content:       {b['content_kb']}KB")
        lines.append(f"    Inline Styles: {b['inline_styles_kb']}KB")
        lines.append(f"    Style Blocks:  {b['style_blocks_kb']}KB")
        lines.append(f"    Whitespace:    {b['whitespace_kb']}KB")
        lines.append(f"    Base64 Images: {b['base64_images_kb']}KB")
        lines.append(f"    Comments:      {b['comments_kb']}KB")

        if r["recommendations"]:
            lines.append(f"\n  Recommendations:")
            for rec in r["recommendations"]:
                lines.append(f"    > {rec}")

        lines.append("-" * 55)

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Analyze email template render size and Gmail clip risk.")
    parser.add_argument("file", nargs="?", help="HTML template file")
    parser.add_argument("--dir", help="Directory of HTML templates")
    parser.add_argument("--json", action="store_true", dest="json_output")
    args = parser.parse_args()

    files = []
    if args.dir:
        dirpath = Path(args.dir)
        files = sorted(dirpath.glob("*.html"))
        if not files:
            print(f"No .html files found in {args.dir}", file=sys.stderr)
            sys.exit(1)
    elif args.file:
        files = [Path(args.file)]
    else:
        parser.print_help()
        sys.exit(1)

    results = []
    for f in files:
        try:
            results.append(analyze_file(str(f)))
        except FileNotFoundError:
            print(f"Warning: {f} not found, skipping", file=sys.stderr)

    if args.json_output:
        print(json.dumps(results if len(results) > 1 else results[0], indent=2))
    else:
        print(format_human(results))


if __name__ == "__main__":
    main()
