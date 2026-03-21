#!/usr/bin/env python3
"""
pSEO Template Quality Scorer

Scores programmatic SEO page templates for content quality, uniqueness
potential, SEO compliance, and thin content risk. Evaluates template
structure and sample rendered pages.

Usage:
    python template_scorer.py --template template.html
    python template_scorer.py --pages page1.html page2.html page3.html --json
    python template_scorer.py --directory ./generated_pages/ --similarity-check
"""

import argparse
import json
import re
import sys
from pathlib import Path
from collections import Counter


def extract_text(html):
    """Extract visible text from HTML."""
    text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def count_unique_words(text):
    """Count unique words in text."""
    words = re.findall(r'\b[a-z]+\b', text.lower())
    return len(set(words))


def jaccard_similarity(text1, text2):
    """Calculate Jaccard similarity between two texts."""
    words1 = set(re.findall(r'\b[a-z]+\b', text1.lower()))
    words2 = set(re.findall(r'\b[a-z]+\b', text2.lower()))
    if not words1 or not words2:
        return 0.0
    intersection = words1 & words2
    union = words1 | words2
    return round(len(intersection) / len(union), 3)


def score_template(content):
    """Score a single template or page."""
    text = extract_text(content) if '<' in content else content
    word_count = len(text.split())
    unique_words = count_unique_words(text)

    checks = {}

    # Word count
    checks["word_count"] = {
        "value": word_count,
        "pass": word_count >= 500,
        "detail": f"{word_count} words (500+ required for pSEO pages in 2026)",
    }

    # Unique word ratio
    if word_count > 0:
        unique_ratio = unique_words / word_count
        checks["unique_word_ratio"] = {
            "value": round(unique_ratio, 3),
            "pass": unique_ratio >= 0.3,
            "detail": f"{round(unique_ratio * 100, 1)}% unique words (30%+ target)",
        }

    # H1 presence
    h1_count = len(re.findall(r'<h1[^>]*>|^#\s+', content, re.IGNORECASE | re.MULTILINE))
    checks["h1_present"] = {
        "pass": h1_count == 1,
        "count": h1_count,
        "detail": f"{h1_count} H1 tag(s) — should be exactly 1",
    }

    # Meta title
    title_match = re.search(r'<title[^>]*>(.*?)</title>', content, re.IGNORECASE | re.DOTALL)
    if title_match:
        title = title_match.group(1).strip()
        checks["meta_title"] = {
            "pass": 30 <= len(title) <= 60,
            "length": len(title),
            "detail": f"Title: {len(title)} chars (target 50-60)",
        }
    else:
        checks["meta_title"] = {
            "pass": False,
            "detail": "No <title> tag found",
        }

    # Meta description
    desc_match = re.search(r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']', content, re.IGNORECASE)
    if desc_match:
        desc = desc_match.group(1).strip()
        checks["meta_description"] = {
            "pass": 120 <= len(desc) <= 160,
            "length": len(desc),
            "detail": f"Description: {len(desc)} chars (target 140-160)",
        }
    else:
        checks["meta_description"] = {
            "pass": False,
            "detail": "No meta description found",
        }

    # Schema markup
    has_schema = bool(re.search(r'application/ld\+json|schema\.org', content, re.IGNORECASE))
    checks["schema_markup"] = {
        "pass": has_schema,
        "detail": "Schema markup present" if has_schema else "No schema markup",
    }

    # Internal links
    links = re.findall(r'<a[^>]+href=["\']([^"\']+)["\']', content, re.IGNORECASE)
    internal = [l for l in links if l.startswith('/') or l.startswith('#')]
    checks["internal_links"] = {
        "pass": len(internal) >= 3,
        "count": len(internal),
        "detail": f"{len(internal)} internal links (3+ required)",
    }

    # Conditional content markers (template variables)
    template_vars = len(re.findall(r'\{\{.*?\}\}|\{%.*?%\}|\$\{.*?\}|<%.*?%>', content))
    checks["template_variables"] = {
        "value": template_vars,
        "pass": template_vars >= 5,
        "detail": f"{template_vars} template variables (5+ indicates good uniqueness potential)",
    }

    # Breadcrumbs
    has_breadcrumb = bool(re.search(r'breadcrumb|BreadcrumbList|aria-label=["\']breadcrumb', content, re.IGNORECASE))
    checks["breadcrumbs"] = {
        "pass": has_breadcrumb,
        "detail": "Breadcrumbs detected" if has_breadcrumb else "No breadcrumbs found",
    }

    # Calculate score
    passed = sum(1 for c in checks.values() if c.get("pass", False))
    score = round((passed / len(checks)) * 100, 1)

    return {
        "word_count": word_count,
        "unique_words": unique_words,
        "score": score,
        "checks": checks,
    }


def check_similarity(pages):
    """Check content similarity across multiple pages."""
    texts = {}
    for fp in pages:
        content = fp.read_text(encoding="utf-8", errors="replace")
        texts[str(fp)] = extract_text(content) if '<' in content else content

    pairs = []
    files = list(texts.keys())
    for i in range(len(files)):
        for j in range(i + 1, len(files)):
            sim = jaccard_similarity(texts[files[i]], texts[files[j]])
            pairs.append({
                "page_a": files[i],
                "page_b": files[j],
                "similarity": sim,
                "risk": "High" if sim > 0.8 else "Medium" if sim > 0.6 else "Low",
            })

    pairs.sort(key=lambda p: p["similarity"], reverse=True)
    avg_similarity = round(sum(p["similarity"] for p in pairs) / max(len(pairs), 1), 3)
    high_risk = sum(1 for p in pairs if p["risk"] == "High")

    return {
        "total_pairs": len(pairs),
        "average_similarity": avg_similarity,
        "high_risk_pairs": high_risk,
        "pairs": pairs[:20],  # Top 20 most similar
    }


def main():
    parser = argparse.ArgumentParser(
        description="Score pSEO templates and page quality"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--template", help="Single template file to score")
    group.add_argument("--pages", nargs="+", help="Multiple rendered pages to score and compare")
    group.add_argument("--directory", help="Directory of generated pages")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--similarity-check", action="store_true", help="Check cross-page similarity")
    args = parser.parse_args()

    if args.template:
        fp = Path(args.template)
        if not fp.exists():
            print(f"Error: {fp} not found", file=sys.stderr)
            sys.exit(1)
        content = fp.read_text(encoding="utf-8", errors="replace")
        result = score_template(content)
        result["file"] = str(fp)

        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"\n{'='*55}")
            print(f"  TEMPLATE SCORE: {result['score']}/100")
            print(f"{'='*55}")
            print(f"  File: {fp}")
            print(f"  Words: {result['word_count']} | Unique: {result['unique_words']}")
            for key, check in result["checks"].items():
                status = "PASS" if check.get("pass") else "FAIL"
                print(f"  [{status}] {key}: {check['detail']}")
            print()
        return

    # Multi-page mode
    pages = []
    if args.pages:
        pages = [Path(p) for p in args.pages]
    elif args.directory:
        dirpath = Path(args.directory)
        pages = sorted(dirpath.glob("*.html")) + sorted(dirpath.glob("*.htm")) + sorted(dirpath.glob("*.md"))

    if not pages:
        print("No pages found.", file=sys.stderr)
        sys.exit(1)

    results = []
    for fp in pages:
        if fp.exists():
            content = fp.read_text(encoding="utf-8", errors="replace")
            result = score_template(content)
            result["file"] = str(fp)
            results.append(result)

    avg_score = round(sum(r["score"] for r in results) / max(len(results), 1), 1)
    avg_words = round(sum(r["word_count"] for r in results) / max(len(results), 1))
    thin_pages = sum(1 for r in results if r["word_count"] < 500)

    similarity = None
    if args.similarity_check and len(pages) >= 2:
        similarity = check_similarity([p for p in pages if p.exists()])

    output = {
        "total_pages": len(results),
        "average_score": avg_score,
        "average_word_count": avg_words,
        "thin_pages": thin_pages,
        "pages": results,
        "similarity": similarity,
    }

    if args.json:
        print(json.dumps(output, indent=2))
    else:
        print(f"\n{'='*60}")
        print(f"  pSEO PAGE SET ANALYSIS — {len(results)} pages")
        print(f"{'='*60}")
        print(f"  Average score: {avg_score}/100")
        print(f"  Average words: {avg_words}")
        print(f"  Thin pages (<500 words): {thin_pages}")

        for r in results:
            status = "OK" if r["score"] >= 70 else "WARN" if r["score"] >= 50 else "FAIL"
            print(f"  [{status}] {r['file']}: {r['score']}/100 ({r['word_count']} words)")

        if similarity:
            print(f"\n  Similarity Analysis:")
            print(f"  Average similarity: {similarity['average_similarity']}")
            print(f"  High-risk pairs (>80%): {similarity['high_risk_pairs']}")
            for pair in similarity["pairs"][:5]:
                print(f"    {pair['page_a']} <-> {pair['page_b']}: {pair['similarity']} [{pair['risk']}]")

        print()


if __name__ == "__main__":
    main()
