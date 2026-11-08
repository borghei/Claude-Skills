#!/usr/bin/env python3
"""
Landing Page Conversion Checklist

Runs a comprehensive conversion optimization audit on
landing page HTML against 2025-2026 best practices.

Proof checks (logos, testimonials, counts) report what is missing; they never ask
for proof the client cannot source, so they do not affect the exit code.

Usage:
    python conversion_checklist.py page.html
    python conversion_checklist.py page.html --format json

Exit codes: 0 every gating check passes, 1 a gating check fails (H1 present,
single H1, CTA present, viewport meta, title tag), 2 missing, unreadable or
non-HTML input.
"""

import argparse
import json
import re
import sys
from pathlib import Path

HTML_TAG = re.compile(r"<[^>]+>")
NON_VISIBLE = re.compile(r"<(script|style|template|noscript)\b.*?</\1\s*>|<!--.*?-->", re.IGNORECASE | re.DOTALL)
GATING = {"H1 Tag Present", "Single H1", "CTA Button Present", "Viewport Meta", "Title Tag"}


def meta(lower: str, key: str) -> bool:
    """True when a <meta> names key (name= or property=), with any quoting and attribute order."""
    return any(re.search(r"""(?:name|property)\s*=\s*["']?""" + re.escape(key) + r"""\b""", m)
               for m in re.findall(r"<meta\b[^>]*>", lower))


def audit_page(html: str) -> dict:
    lower = html.lower()
    plain = HTML_TAG.sub(" ", NON_VISIBLE.sub(" ", html))
    plain = re.sub(r"\s+", " ", plain).strip()

    checks = []
    score = 0
    max_score = 0

    def check(name, condition, points, fail_msg):
        nonlocal score, max_score
        max_score += points
        if condition:
            score += points
            checks.append({"name": name, "status": "PASS", "points": points})
        else:
            checks.append({"name": name, "status": "FAIL", "points": 0, "max_points": points, "fix": fail_msg})

    # Above the Fold
    check("H1 Tag Present", bool(re.search(r"<h1", lower)), 10, "Add a clear H1 headline")
    check("Single H1", len(re.findall(r"<h1", lower)) <= 1, 5, "Use only one H1 per page")
    cta_tags = re.findall(r"<button\b|<a\b[^>]*class\s*=\s*[\"']?[^\"'>]*\b(?:btn|button|cta)", lower)
    check("CTA Button Present", bool(cta_tags), 10, "Add a prominent CTA button")
    check("Subheadline Present", bool(re.search(r"<(h2|p class[^>]*sub)", lower)), 5, "Add a subheadline under H1")

    # Navigation
    has_nav = bool(re.search(r"<nav|<header[^>]*>.*<a", lower, re.DOTALL))
    nav_link_count = len(re.findall(r"<nav.*?</nav>", lower, re.DOTALL))
    check("Minimal Navigation", not has_nav or nav_link_count <= 1, 8, "Remove navigation -- landing pages should have no exit paths")

    # Social Proof
    check("Customer Logos", bool(re.search(r"<img\b[^>]*alt\s*=\s*[\"'][^\"']*logo|class\s*=\s*[\"']?[^\"'>]*\blogos?\b", lower)), 8,
          "Real customer logos only with permission; without them leave the row out")
    check("Testimonials", bool(re.search(r"<blockquote\b|class\s*=\s*[\"']?[^\"'>]*\b(testimonial|review)", lower)), 8,
          "Named testimonials the client can source, quoted exactly; never invented")
    check("Numbers/Metrics", bool(re.search(r"\d+\s*(team|compan|customer|user|client)", plain, re.IGNORECASE)), 5,
          "A customer count or metric only if the client can source it")

    # Trust & Credibility
    check("Security Badges", bool(re.search(r"\b(soc ?2|gdpr|iso ?27001|hipaa|encrypted|ssl)\b", plain, re.IGNORECASE)), 5, "Add security badges if relevant")
    check("Privacy Policy Link", bool(re.search(r"<a\b[^>]*href\s*=\s*[\"']?[^\"'>]*privacy|<a\b[^>]*>[^<]*privacy", lower)), 3, "Link to privacy policy near forms")

    # CTA Optimization
    cta_count = len(cta_tags)
    check("Multiple CTAs", cta_count >= 2, 8, "Place CTAs at hero, mid-page, and bottom")
    check("Risk Reversal Near CTA", bool(re.search(r"(no credit card|cancel anytime|free trial|money.back|risk.free|guarantee)", lower)), 8, "Add risk reversal text near CTAs")

    # Objection Handling
    check("FAQ Section", bool(re.search(r"(faq|frequently|common question|questions)", plain, re.IGNORECASE)), 5, "Add FAQ section to handle buying objections")
    check("How It Works", bool(re.search(r"(how it works|how [\w ]{1,30} works|step \d|\d steps|<ol\b)", lower)), 5, "Add 'How It Works' section (3-4 steps)")

    # Mobile & Performance
    check("Viewport Meta", meta(lower, "viewport"), 5, "Add viewport meta tag for mobile")
    check("Mobile-Friendly", bool(re.search(r"@media|<link\b[^>]*stylesheet", lower)), 3, "Add responsive CSS/media queries (an external stylesheet is assumed to carry them)")

    images = re.findall(r"<img[^>]*>", html, re.IGNORECASE)
    images_with_alt = len(re.findall(r"<img\b[^>]*\balt\s*=", html, re.IGNORECASE))  # alt="" is right for decoration
    check("Image Alt Text", not images or images_with_alt >= len(images) * 0.8, 3, "Add alt text to all images")

    # SEO
    check("Title Tag", bool(re.search(r"<title[^>]*>\s*\S[^<]*</title>", lower)), 3, "Add a title tag with primary keyword")
    check("Meta Description", meta(lower, "description"), 3, "Add meta description with benefit + CTA")
    check("OG Image", meta(lower, "og:image"), 2, "Add Open Graph image for social sharing")

    # Content Quality
    word_count = len(plain.split())
    check("Adequate Content", word_count >= 120, 3, "Under 120 words: the page may not answer what, for whom, how and what it costs")
    check("Not Too Long", word_count <= 3000, 2, "Page is extremely long. Consider trimming.")

    # Form optimization (if form exists)
    has_form = bool(re.search(r"<form", lower))
    if has_form:
        inputs = [i for i in re.findall(r"<input\b[^>]*>|<select\b|<textarea\b", lower)
                  if not re.search(r"type\s*=\s*[\"']?(hidden|submit|button|reset|image)\b", i)]
        check("Form Fields < 5", len(inputs) <= 5, 5, f"Form has {len(inputs)} fields. Reduce to minimum required.")

    pct = round(score / max(max_score, 1) * 100)

    return {
        "score": pct,
        "points": f"{score}/{max_score}",
        "grade": "A" if pct >= 85 else "B" if pct >= 70 else "C" if pct >= 55 else "D" if pct >= 40 else "F",
        "checks": checks,
        "passed": sum(1 for c in checks if c["status"] == "PASS"),
        "failed": sum(1 for c in checks if c["status"] == "FAIL"),
        "total_checks": len(checks),
        "quick_wins": [c["fix"] for c in checks if c["status"] == "FAIL" and c.get("max_points", 0) >= 5][:5],
        "gating_failed": [c["name"] for c in checks if c["status"] == "FAIL" and c["name"] in GATING],
        "benchmarks": {
            "median_conversion_rate": "6.6% (all industries, 2025 data)",
            "top_10_pct": ">10% conversion rate",
            "page_load_target": "<3 seconds on mobile",
            "note": "Every second of load time reduces conversion by ~7%",
        },
    }


def format_human(result: dict) -> str:
    lines = ["\n" + "=" * 60, "  LANDING PAGE CONVERSION CHECKLIST", "=" * 60]
    lines.append(f"\n  Score: {result['score']}% ({result['grade']}) | {result['passed']}/{result['total_checks']} checks passed")

    lines.append(f"\n  Checklist:")
    for c in result["checks"]:
        icon = "+" if c["status"] == "PASS" else "X"
        fix = f" -- {c.get('fix', '')}" if c["status"] == "FAIL" else ""
        lines.append(f"    [{icon}] {c['name']}{fix}")

    if result["quick_wins"]:
        lines.append(f"\n  Top Quick Wins:")
        for i, qw in enumerate(result["quick_wins"], 1):
            lines.append(f"    {i}. {qw}")

    b = result["benchmarks"]
    lines.append(f"\n  Benchmarks (2025-2026):")
    lines.append(f"    Median conversion: {b['median_conversion_rate']}")
    lines.append(f"    Top performers: {b['top_10_pct']}")
    lines.append(f"    Load target: {b['page_load_target']}")
    lines.append(f"    Note: {b['note']}")

    lines.append("")
    return "\n".join(lines)


def load(path: str) -> str:
    """Read an HTML page; exit 2 on a missing, unreadable or non-HTML file."""
    try:
        html = Path(path).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        print(f"Error: cannot read {path}: {exc}", file=sys.stderr)
        sys.exit(2)
    if not re.search(r"<(html|body|main|section|div|h1|p)\b", html, re.IGNORECASE):
        print(f"Error: {path} does not look like an HTML page", file=sys.stderr)
        sys.exit(2)
    return html


def main():
    parser = argparse.ArgumentParser(description="Run conversion optimization checklist on landing page.")
    parser.add_argument("file", help="HTML file to audit")
    parser.add_argument("--json", action="store_true", dest="json_output", help="same as --format json")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="output format")
    args = parser.parse_args()
    if args.format == "json":
        args.json_output = True

    html = load(args.file)

    result = audit_page(html)
    if args.json_output:
        print(json.dumps(result, indent=2))
    else:
        print(format_human(result))
    sys.exit(1 if result["gating_failed"] else 0)


if __name__ == "__main__":
    main()
