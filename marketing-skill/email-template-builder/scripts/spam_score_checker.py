#!/usr/bin/env python3
"""
Email Template Spam Score Checker

Analyzes email HTML templates for spam risk factors including
content-to-image ratio, link density, HTML complexity, and
deliverability best practices per 2025-2026 standards.

Usage:
    python spam_score_checker.py template.html
    python spam_score_checker.py template.html --json
"""

import argparse
import json
import re
import sys
from pathlib import Path

SPAM_WORDS = [
    "free", "guarantee", "act now", "limited time", "urgent", "winner",
    "click here", "buy now", "order now", "risk-free", "no obligation",
    "100% free", "amazing deal", "cash", "earn money", "double your",
    "congratulations", "you won", "apply now", "subscribe now",
]

REQUIRED_ELEMENTS = [
    ("unsubscribe_link", re.compile(r"unsubscribe|opt.out|manage.*preferences", re.IGNORECASE)),
    ("physical_address", re.compile(r"\d+\s+\w+\s+(st|street|ave|avenue|rd|road|blvd|dr|drive|suite|ste)", re.IGNORECASE)),
    ("plain_text_fallback", re.compile(r"content-type:\s*text/plain", re.IGNORECASE)),
    ("alt_text_on_images", re.compile(r'<img[^>]+alt\s*=\s*"[^"]+', re.IGNORECASE)),
]


def analyze_template(html: str) -> dict:
    result = {
        "overall_score": 10.0,
        "checks": [],
        "deductions": [],
        "recommendations": [],
    }

    plain_text = re.sub(r"<[^>]+>", " ", html)
    plain_text = re.sub(r"\s+", " ", plain_text).strip()
    text_length = len(plain_text)

    # Image analysis
    images = re.findall(r"<img[^>]*>", html, re.IGNORECASE)
    images_with_alt = len(re.findall(r'<img[^>]+alt\s*=\s*"[^"]+', html, re.IGNORECASE))
    images_without_alt = len(images) - images_with_alt
    image_area_hints = len(re.findall(r'<img[^>]*(?:width|height)', html, re.IGNORECASE))

    # Text-to-image ratio (approximate)
    html_length = len(html)
    img_chars = sum(len(img) for img in images)
    text_ratio = text_length / max(html_length, 1) * 100

    if text_ratio >= 60:
        result["checks"].append({"name": "Text-to-Image Ratio", "status": "PASS", "detail": f"{text_ratio:.0f}% text (target: 60%+)"})
    elif text_ratio >= 40:
        result["checks"].append({"name": "Text-to-Image Ratio", "status": "WARN", "detail": f"{text_ratio:.0f}% text"})
        result["overall_score"] -= 1
        result["deductions"].append("Low text-to-image ratio (-1)")
    else:
        result["checks"].append({"name": "Text-to-Image Ratio", "status": "FAIL", "detail": f"{text_ratio:.0f}% text (too image-heavy)"})
        result["overall_score"] -= 2
        result["deductions"].append("Very low text ratio (-2)")

    # Image alt text
    if images and images_without_alt > 0:
        result["checks"].append({"name": "Image Alt Text", "status": "WARN", "detail": f"{images_without_alt} image(s) missing alt text"})
        result["overall_score"] -= 0.5
    elif images:
        result["checks"].append({"name": "Image Alt Text", "status": "PASS", "detail": "All images have alt text"})

    # Link analysis
    links = re.findall(r'href\s*=\s*"([^"]*)"', html, re.IGNORECASE)
    external_links = [l for l in links if l.startswith("http")]
    shortener_links = [l for l in external_links if any(s in l for s in ["bit.ly", "tinyurl", "t.co", "goo.gl", "ow.ly"])]

    if shortener_links:
        result["checks"].append({"name": "URL Shorteners", "status": "FAIL", "detail": f"{len(shortener_links)} shortened URLs detected"})
        result["overall_score"] -= 2
        result["deductions"].append("URL shorteners trigger spam filters (-2)")
    else:
        result["checks"].append({"name": "URL Shorteners", "status": "PASS", "detail": "No URL shorteners"})

    if len(external_links) > 10:
        result["checks"].append({"name": "Link Count", "status": "WARN", "detail": f"{len(external_links)} links (high)"})
        result["overall_score"] -= 1
    else:
        result["checks"].append({"name": "Link Count", "status": "PASS", "detail": f"{len(external_links)} links"})

    # Spam words
    lower = plain_text.lower()
    found_spam = [w for w in SPAM_WORDS if w in lower]
    if not found_spam:
        result["checks"].append({"name": "Spam Trigger Words", "status": "PASS", "detail": "None detected"})
    elif len(found_spam) <= 2:
        result["checks"].append({"name": "Spam Trigger Words", "status": "WARN", "detail": f"Found: {', '.join(found_spam)}"})
        result["overall_score"] -= 0.5
    else:
        result["checks"].append({"name": "Spam Trigger Words", "status": "FAIL", "detail": f"Found {len(found_spam)}: {', '.join(found_spam)}"})
        result["overall_score"] -= 1.5

    # Required elements
    has_unsubscribe = bool(re.search(r"unsubscribe|opt.out|manage.*preferences", html, re.IGNORECASE))
    has_address = bool(re.search(r"\d+\s+\w+\s+(st|street|ave|avenue|rd|road)", html, re.IGNORECASE))

    if has_unsubscribe:
        # Check for one-click unsubscribe (RFC 8058)
        has_one_click = bool(re.search(r"list-unsubscribe|one-click", html, re.IGNORECASE))
        detail = "One-click unsubscribe detected" if has_one_click else "Unsubscribe link found (add RFC 8058 one-click header)"
        result["checks"].append({"name": "Unsubscribe", "status": "PASS", "detail": detail})
        if not has_one_click:
            result["recommendations"].append("Add RFC 8058 List-Unsubscribe and List-Unsubscribe-Post headers for Gmail/Yahoo compliance.")
    else:
        result["checks"].append({"name": "Unsubscribe", "status": "FAIL", "detail": "Missing unsubscribe mechanism"})
        result["overall_score"] -= 2
        result["deductions"].append("Missing unsubscribe (-2) -- required by CAN-SPAM, GDPR, and Gmail/Yahoo")

    if has_address:
        result["checks"].append({"name": "Physical Address", "status": "PASS", "detail": "Physical address detected"})
    else:
        result["checks"].append({"name": "Physical Address", "status": "WARN", "detail": "No physical address (CAN-SPAM requirement)"})
        result["overall_score"] -= 0.5

    # HTML validation
    unclosed_tags = 0
    for tag in ["div", "table", "tr", "td", "span", "p", "a"]:
        opens = len(re.findall(f"<{tag}[\\s>]", html, re.IGNORECASE))
        closes = len(re.findall(f"</{tag}>", html, re.IGNORECASE))
        unclosed_tags += abs(opens - closes)

    if unclosed_tags == 0:
        result["checks"].append({"name": "HTML Structure", "status": "PASS", "detail": "Tags appear balanced"})
    elif unclosed_tags <= 3:
        result["checks"].append({"name": "HTML Structure", "status": "WARN", "detail": f"~{unclosed_tags} potentially unclosed tags"})
        result["overall_score"] -= 0.5
    else:
        result["checks"].append({"name": "HTML Structure", "status": "FAIL", "detail": f"~{unclosed_tags} unclosed tags"})
        result["overall_score"] -= 1

    # Width check
    wide_elements = re.findall(r'width\s*[:=]\s*"?(\d+)', html)
    over_600 = [w for w in wide_elements if int(w) > 600]
    if over_600:
        result["checks"].append({"name": "Max Width", "status": "WARN", "detail": f"Elements wider than 600px detected"})
        result["overall_score"] -= 0.5
        result["recommendations"].append("Keep max container width at 600px for email client compatibility.")

    # Dark mode support
    has_dark_mode = bool(re.search(r"prefers-color-scheme:\s*dark", html, re.IGNORECASE))
    if has_dark_mode:
        result["checks"].append({"name": "Dark Mode", "status": "PASS", "detail": "Dark mode CSS detected"})
    else:
        result["checks"].append({"name": "Dark Mode", "status": "INFO", "detail": "No dark mode support (affects 30%+ of users)"})
        result["recommendations"].append("Add prefers-color-scheme: dark media queries for dark mode support.")

    # Subject line in meta
    has_preview = bool(re.search(r"preview|preheader", html, re.IGNORECASE))
    if has_preview:
        result["checks"].append({"name": "Preview Text", "status": "PASS", "detail": "Preview/preheader text detected"})
    else:
        result["recommendations"].append("Add preview text (80-120 chars) that complements the subject line.")

    result["overall_score"] = round(max(0, min(10, result["overall_score"])), 1)
    result["grade"] = "A" if result["overall_score"] >= 9 else "B" if result["overall_score"] >= 7 else "C" if result["overall_score"] >= 5 else "F"

    result["stats"] = {
        "html_size_bytes": len(html.encode()),
        "text_length": text_length,
        "image_count": len(images),
        "link_count": len(external_links),
        "text_ratio_percent": round(text_ratio, 1),
    }

    return result


def format_human(result: dict) -> str:
    lines = ["\n" + "=" * 55, "  EMAIL TEMPLATE SPAM SCORE CHECKER", "=" * 55]
    lines.append(f"\n  Score: {result['overall_score']}/10 (Grade: {result['grade']})")
    s = result["stats"]
    lines.append(f"  Size: {s['html_size_bytes']} bytes | Images: {s['image_count']} | Links: {s['link_count']} | Text: {s['text_ratio_percent']}%")

    lines.append(f"\n  Checks:")
    for c in result["checks"]:
        icon = {"PASS": "+", "WARN": "!", "FAIL": "X", "INFO": "i"}
        lines.append(f"    [{icon.get(c['status'], '?')}] {c['name']}: {c['detail']}")

    if result["deductions"]:
        lines.append(f"\n  Deductions:")
        for d in result["deductions"]:
            lines.append(f"    - {d}")

    if result["recommendations"]:
        lines.append(f"\n  Recommendations:")
        for r in result["recommendations"]:
            lines.append(f"    > {r}")

    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Check email template for spam risk factors.")
    parser.add_argument("file", help="HTML email template file")
    parser.add_argument("--json", action="store_true", dest="json_output")
    args = parser.parse_args()

    try:
        html = Path(args.file).read_text()
    except FileNotFoundError:
        print(f"Error: File not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    result = analyze_template(html)
    if args.json_output:
        print(json.dumps(result, indent=2))
    else:
        print(format_human(result))


if __name__ == "__main__":
    main()
