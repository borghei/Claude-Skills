#!/usr/bin/env python3
"""
On-Page SEO Content Scorer

Scores content for on-page SEO quality across keyword optimization,
heading structure, readability, internal linking, and meta content.
Produces a weighted 0-100 score with specific recommendations.

Usage:
    python content_scorer.py article.md --keyword "cloud cost optimization"
    python content_scorer.py article.md --keyword "SEO audit" --json
    python content_scorer.py article.md --verbose
"""

import argparse
import json
import math
import re
import sys
from pathlib import Path


def count_syllables(word):
    """Estimate syllable count."""
    word = word.lower().strip()
    if len(word) <= 3:
        return 1
    count = 0
    vowels = 'aeiouy'
    prev = False
    for c in word:
        v = c in vowels
        if v and not prev:
            count += 1
        prev = v
    if word.endswith('e'):
        count -= 1
    return max(count, 1)


def flesch_score(text):
    """Calculate Flesch Reading Ease."""
    words = text.split()
    wc = len(words)
    sc = len([s for s in re.split(r'[.!?]+', text) if s.strip()])
    if wc == 0 or sc == 0:
        return 0
    syl = sum(count_syllables(w) for w in words)
    score = 206.835 - 1.015 * (wc / sc) - 84.6 * (syl / wc)
    return round(max(0, min(100, score)), 1)


def check_keyword(text, keyword):
    """Check keyword optimization."""
    if not keyword:
        return {}
    checks = {}
    kw = keyword.lower()
    words = text.lower().split()
    wc = len(words)

    # Density
    occurrences = text.lower().count(kw)
    density = (occurrences * len(kw.split()) / max(wc, 1)) * 100
    checks["keyword_density"] = {
        "value": round(density, 2),
        "pass": 0.5 <= density <= 2.5,
        "detail": f"{round(density, 2)}% density ({occurrences} occurrences)",
    }

    # In first 100 words
    first_100 = " ".join(words[:100])
    checks["in_first_100"] = {
        "pass": kw in first_100,
        "detail": "Present" if kw in first_100 else "Missing from first 100 words",
    }

    # In H1
    h1s = re.findall(r'^#\s+(.+)', text, re.MULTILINE)
    checks["in_h1"] = {
        "pass": any(kw in h.lower() for h in h1s),
        "detail": "In H1" if any(kw in h.lower() for h in h1s) else "Not in H1",
    }

    # In H2s
    h2s = re.findall(r'^##\s+(.+)', text, re.MULTILINE)
    h2_count = sum(1 for h in h2s if kw in h.lower())
    checks["in_h2s"] = {
        "pass": h2_count >= 1,
        "count": h2_count,
        "detail": f"In {h2_count}/{len(h2s)} H2 headings",
    }

    # In last 100 words
    last_100 = " ".join(words[-100:]) if wc >= 100 else " ".join(words)
    checks["in_conclusion"] = {
        "pass": kw in last_100,
        "detail": "Present in conclusion" if kw in last_100 else "Missing from conclusion",
    }

    return checks


def check_structure(text):
    """Check content structure."""
    checks = {}
    wc = len(text.split())

    # Word count
    checks["word_count"] = {
        "value": wc,
        "pass": wc >= 800,
        "detail": f"{wc} words (800+ recommended)",
    }

    # H1
    h1s = re.findall(r'^#\s+', text, re.MULTILINE)
    checks["single_h1"] = {
        "pass": len(h1s) == 1,
        "detail": f"{len(h1s)} H1(s) found — should be 1",
    }

    # H2 count
    h2s = re.findall(r'^##\s+', text, re.MULTILINE)
    checks["h2_count"] = {
        "pass": len(h2s) >= 3,
        "count": len(h2s),
        "detail": f"{len(h2s)} H2 sections",
    }

    # Heading frequency
    if wc > 0 and len(h2s) > 0:
        words_per_h2 = wc / len(h2s)
        checks["heading_frequency"] = {
            "pass": words_per_h2 <= 350,
            "value": round(words_per_h2),
            "detail": f"~{round(words_per_h2)} words between headings (target: <350)",
        }

    # Lists
    list_items = len(re.findall(r'^\s*[-*\d+\.]\s+', text, re.MULTILINE))
    checks["has_lists"] = {
        "pass": list_items >= 3,
        "count": list_items,
        "detail": f"{list_items} list items",
    }

    # Internal links
    int_links = len(re.findall(r'\[.*?\]\(/[^)]+\)', text))
    md_links = len(re.findall(r'\[.*?\]\([^)]+\)', text))
    checks["internal_links"] = {
        "pass": md_links >= 2,
        "count": md_links,
        "detail": f"{md_links} links found (2+ internal recommended)",
    }

    # Images
    images = len(re.findall(r'!\[.*?\]\(', text))
    checks["has_images"] = {
        "pass": images >= 1,
        "count": images,
        "detail": f"{images} images (1+ recommended per 500 words)",
    }

    return checks


def check_meta(text):
    """Check meta content signals."""
    checks = {}

    # Meta description in frontmatter
    desc_match = re.search(r'^description:\s*(.+)', text, re.MULTILINE)
    if desc_match:
        desc = desc_match.group(1).strip().strip('"').strip("'")
        checks["meta_description"] = {
            "pass": 120 <= len(desc) <= 160,
            "length": len(desc),
            "detail": f"Meta description: {len(desc)} chars (target: 140-160)",
        }
    else:
        checks["meta_description"] = {
            "pass": False,
            "detail": "No meta description found in frontmatter",
        }

    # Schema markup
    has_schema = bool(re.search(r'schema\.org|application/ld\+json|@type', text, re.IGNORECASE))
    checks["schema_markup"] = {
        "pass": has_schema,
        "detail": "Schema markup detected" if has_schema else "No schema markup found",
    }

    return checks


def calculate_score(keyword_checks, structure_checks, meta_checks, readability):
    """Calculate weighted overall score."""
    def pass_rate(checks):
        if not checks:
            return 0
        return sum(1 for v in checks.values() if v.get("pass", False)) / len(checks)

    read_score = 100 if 50 <= readability <= 80 else max(0, 100 - abs(readability - 65) * 2)

    score = (
        pass_rate(keyword_checks) * 30 +
        pass_rate(structure_checks) * 30 +
        pass_rate(meta_checks) * 15 +
        (read_score / 100) * 25
    ) * 100 / 100

    return round(score, 1)


def main():
    parser = argparse.ArgumentParser(description="Score content for on-page SEO")
    parser.add_argument("file", help="Content file path")
    parser.add_argument("--keyword", help="Target keyword")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    fp = Path(args.file)
    if not fp.exists():
        print(f"Error: {fp} not found", file=sys.stderr)
        sys.exit(1)

    text = fp.read_text(encoding="utf-8", errors="replace")
    readability = flesch_score(text)
    kw_checks = check_keyword(text, args.keyword)
    struct_checks = check_structure(text)
    meta_checks = check_meta(text)
    score = calculate_score(kw_checks, struct_checks, meta_checks, readability)
    grade = "A" if score >= 85 else "B" if score >= 70 else "C" if score >= 55 else "D" if score >= 40 else "F"

    result = {
        "file": str(fp),
        "word_count": len(text.split()),
        "readability": readability,
        "score": score,
        "grade": grade,
        "keyword_checks": kw_checks,
        "structure_checks": struct_checks,
        "meta_checks": meta_checks,
    }

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"\n{'='*55}")
        print(f"  ON-PAGE SEO SCORE: {score}/100 (Grade: {grade})")
        print(f"{'='*55}")
        print(f"  File: {fp} | Words: {len(text.split())} | Readability: {readability}")
        if args.keyword:
            print(f"  Keyword: {args.keyword}")

        if args.verbose:
            for label, checks in [("Keyword", kw_checks), ("Structure", struct_checks), ("Meta", meta_checks)]:
                if checks:
                    print(f"\n  --- {label} ---")
                    for k, v in checks.items():
                        s = "PASS" if v.get("pass") else "FAIL"
                        print(f"  [{s}] {k}: {v['detail']}")
        else:
            # Summary
            all_checks = {**kw_checks, **struct_checks, **meta_checks}
            fails = [k for k, v in all_checks.items() if not v.get("pass")]
            if fails:
                print(f"\n  Failing checks: {', '.join(fails)}")

        print()


if __name__ == "__main__":
    main()
