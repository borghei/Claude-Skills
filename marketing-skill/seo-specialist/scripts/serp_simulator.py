#!/usr/bin/env python3
"""
SERP Appearance Simulator

Simulates how a page would appear in Google search results. Validates title
tag length, meta description, URL structure, and rich snippet eligibility.
Previews desktop and mobile SERP snippets with character truncation warnings.

Usage:
    python serp_simulator.py --title "Cloud Cost Guide" --description "Learn strategies..." --url "/guides/cloud"
    python serp_simulator.py --file page.md --json
    python serp_simulator.py --title "Title" --description "Desc" --url "/path" --keyword "cloud cost"
"""

import argparse
import json
import re
import sys
from pathlib import Path


# SERP display limits (2026 standards)
TITLE_MAX_PIXELS = 600  # ~60 characters
TITLE_MAX_CHARS = 60
DESC_MAX_CHARS_DESKTOP = 160
DESC_MAX_CHARS_MOBILE = 120
URL_MAX_DISPLAY_CHARS = 75


def estimate_pixel_width(text):
    """Rough pixel width estimation for SERP titles."""
    # Approximate: uppercase ~9px, lowercase ~7px, space ~4px, numbers ~7px
    width = 0
    for char in text:
        if char.isupper():
            width += 9
        elif char.islower():
            width += 7
        elif char.isdigit():
            width += 7
        elif char == ' ':
            width += 4
        else:
            width += 7
    return width


def analyze_title(title, keyword=None):
    """Analyze title tag for SERP optimization."""
    issues = []
    char_count = len(title)
    pixel_width = estimate_pixel_width(title)

    # Length check
    if char_count > TITLE_MAX_CHARS:
        truncated = title[:TITLE_MAX_CHARS - 3] + "..."
        issues.append({
            "type": "title_too_long",
            "severity": "High",
            "detail": f"Title is {char_count} chars — will truncate at ~{TITLE_MAX_CHARS} chars",
            "truncated_preview": truncated,
        })
    elif char_count < 30:
        issues.append({
            "type": "title_too_short",
            "severity": "Medium",
            "detail": f"Title is only {char_count} chars — aim for 50-60 chars to maximize SERP real estate",
        })

    # Keyword placement
    if keyword:
        kw_lower = keyword.lower()
        title_lower = title.lower()
        if kw_lower not in title_lower:
            issues.append({
                "type": "keyword_missing",
                "severity": "High",
                "detail": f"Primary keyword '{keyword}' not found in title",
            })
        elif not title_lower.startswith(kw_lower) and title_lower.find(kw_lower) > 30:
            issues.append({
                "type": "keyword_not_frontloaded",
                "severity": "Medium",
                "detail": f"Keyword appears late in title (position {title_lower.find(kw_lower)}) — front-load for CTR",
            })

    # Power words for CTR
    power_words = ['guide', 'how to', 'best', 'top', 'free', 'new', 'proven',
                   'step', 'easy', 'ultimate', 'complete', 'simple', 'fast']
    has_power = any(w in title.lower() for w in power_words)

    # Numbers in title
    has_number = bool(re.search(r'\d+', title))

    return {
        "title": title,
        "char_count": char_count,
        "pixel_width_estimate": pixel_width,
        "will_truncate": char_count > TITLE_MAX_CHARS,
        "has_power_word": has_power,
        "has_number": has_number,
        "issues": issues,
    }


def analyze_description(description, keyword=None):
    """Analyze meta description for SERP optimization."""
    issues = []
    char_count = len(description)

    # Length check
    if char_count > DESC_MAX_CHARS_DESKTOP:
        issues.append({
            "type": "desc_too_long",
            "severity": "Medium",
            "detail": f"Description is {char_count} chars — may truncate on desktop (>{DESC_MAX_CHARS_DESKTOP}) and will truncate on mobile (>{DESC_MAX_CHARS_MOBILE})",
        })
    elif char_count < 80:
        issues.append({
            "type": "desc_too_short",
            "severity": "Medium",
            "detail": f"Description is only {char_count} chars — aim for 140-160 chars",
        })

    # Keyword in description
    if keyword and keyword.lower() not in description.lower():
        issues.append({
            "type": "keyword_missing_desc",
            "severity": "Medium",
            "detail": f"Keyword '{keyword}' not in meta description — Google bolds matching terms",
        })

    # CTA presence
    cta_patterns = r'\b(learn|discover|find out|get|try|start|read|see|check|download)\b'
    has_cta = bool(re.search(cta_patterns, description, re.IGNORECASE))

    # Mobile truncation preview
    mobile_preview = description[:DESC_MAX_CHARS_MOBILE]
    if len(description) > DESC_MAX_CHARS_MOBILE:
        mobile_preview = mobile_preview[:DESC_MAX_CHARS_MOBILE - 3] + "..."

    return {
        "description": description,
        "char_count": char_count,
        "desktop_truncates": char_count > DESC_MAX_CHARS_DESKTOP,
        "mobile_truncates": char_count > DESC_MAX_CHARS_MOBILE,
        "mobile_preview": mobile_preview,
        "has_cta": has_cta,
        "issues": issues,
    }


def analyze_url(url):
    """Analyze URL for SERP appearance."""
    issues = []

    # Clean display URL
    display_url = url.lstrip('/')
    if len(display_url) > URL_MAX_DISPLAY_CHARS:
        issues.append({
            "type": "url_too_long",
            "severity": "Low",
            "detail": f"URL is {len(display_url)} chars — may truncate in SERP",
        })

    # Check for parameters
    if '?' in url:
        issues.append({
            "type": "url_has_params",
            "severity": "Medium",
            "detail": "URL contains query parameters — clean URLs perform better",
        })

    # Check for underscores
    if '_' in url:
        issues.append({
            "type": "url_underscores",
            "severity": "Low",
            "detail": "URL uses underscores — hyphens are preferred by Google",
        })

    # Depth
    depth = len([s for s in url.split('/') if s and s != 'https:' and s != 'http:'])
    if depth > 4:
        issues.append({
            "type": "url_too_deep",
            "severity": "Medium",
            "detail": f"URL has {depth} path segments — shallower URLs are preferred",
        })

    breadcrumbs = " › ".join(s for s in url.split('/') if s and not s.startswith(('http', 'https')))

    return {
        "url": url,
        "display_url": display_url,
        "breadcrumb_preview": breadcrumbs,
        "depth": depth,
        "issues": issues,
    }


def extract_from_file(filepath):
    """Extract title, description, and content from a markdown file."""
    text = filepath.read_text(encoding="utf-8", errors="replace")

    # Extract title from H1 or frontmatter
    title = ""
    h1_match = re.search(r'^#\s+(.+)', text, re.MULTILINE)
    if h1_match:
        title = h1_match.group(1).strip()

    # Extract description from frontmatter or first paragraph
    desc = ""
    desc_match = re.search(r'^description:\s*(.+)', text, re.MULTILINE)
    if desc_match:
        desc = desc_match.group(1).strip().strip('"').strip("'")
    else:
        paragraphs = [p.strip() for p in re.split(r'\n\s*\n', text)
                      if p.strip() and not p.strip().startswith('#') and not p.strip().startswith('---')]
        if paragraphs:
            desc = paragraphs[0][:160]

    return title, desc


def generate_serp_preview(title_analysis, desc_analysis, url_analysis):
    """Generate text-based SERP preview."""
    lines = []
    lines.append("")
    lines.append("  ┌─────────────────────────────────────────────────────┐")

    # URL breadcrumb
    breadcrumb = url_analysis["breadcrumb_preview"][:50]
    lines.append(f"  │ {breadcrumb:<51} │")

    # Title (blue, truncated if needed)
    title = title_analysis["title"]
    if title_analysis["will_truncate"]:
        title = title[:57] + "..."
    lines.append(f"  │ {title:<51} │")

    # Description
    desc = desc_analysis.get("mobile_preview", desc_analysis["description"][:120])
    # Wrap at 51 chars
    while desc:
        chunk = desc[:51]
        lines.append(f"  │ {chunk:<51} │")
        desc = desc[51:]

    lines.append("  └─────────────────────────────────────────────────────┘")
    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Simulate SERP appearance and optimize"
    )
    parser.add_argument("--title", help="Page title tag")
    parser.add_argument("--description", help="Meta description")
    parser.add_argument("--url", help="Page URL path")
    parser.add_argument("--file", help="Markdown file to extract from")
    parser.add_argument("--keyword", help="Target keyword for optimization check")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    title = args.title or ""
    description = args.description or ""
    url = args.url or "/"

    if args.file:
        filepath = Path(args.file)
        if not filepath.exists():
            print(f"Error: File not found: {filepath}", file=sys.stderr)
            sys.exit(1)
        file_title, file_desc = extract_from_file(filepath)
        title = title or file_title
        description = description or file_desc
        url = url or f"/{filepath.stem}"

    if not title:
        print("Error: No title provided. Use --title or --file", file=sys.stderr)
        sys.exit(1)

    title_analysis = analyze_title(title, args.keyword)
    desc_analysis = analyze_description(description, args.keyword)
    url_analysis = analyze_url(url)

    all_issues = title_analysis["issues"] + desc_analysis["issues"] + url_analysis["issues"]

    result = {
        "title": title_analysis,
        "description": desc_analysis,
        "url": url_analysis,
        "total_issues": len(all_issues),
        "passed": all(i["severity"] not in ("High", "Critical") for i in all_issues),
    }

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"\n{'='*60}")
        print(f"  SERP PREVIEW")
        print(f"{'='*60}")
        print(generate_serp_preview(title_analysis, desc_analysis, url_analysis))

        print(f"  Title: {title_analysis['char_count']} chars {'(will truncate)' if title_analysis['will_truncate'] else '(OK)'}")
        print(f"  Description: {desc_analysis['char_count']} chars {'(will truncate mobile)' if desc_analysis['mobile_truncates'] else '(OK)'}")
        print(f"  URL depth: {url_analysis['depth']} levels")
        print(f"  Power word: {'Yes' if title_analysis['has_power_word'] else 'No'}")
        print(f"  Number in title: {'Yes' if title_analysis['has_number'] else 'No'}")
        print(f"  CTA in description: {'Yes' if desc_analysis['has_cta'] else 'No'}")

        if all_issues:
            print(f"\n  Issues ({len(all_issues)}):")
            for issue in all_issues:
                print(f"    [{issue['severity']}] {issue['detail']}")
        else:
            print(f"\n  All checks passed.")

        print()


if __name__ == "__main__":
    main()
