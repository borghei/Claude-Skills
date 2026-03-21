#!/usr/bin/env python3
"""
Schema Coverage Auditor

Audits multiple pages or a directory of HTML files for schema markup
coverage, identifying pages missing schema, incomplete implementations,
and opportunities for additional schema types.

Usage:
    python schema_auditor.py --directory ./pages/
    python schema_auditor.py --files page1.html page2.html page3.html --json
    python schema_auditor.py --directory ./site/ --report coverage
"""

import argparse
import json
import re
import sys
from pathlib import Path


def extract_schema_types(html):
    """Extract all schema types from HTML file."""
    types = []
    pattern = r'<script\s+type=["\']application/ld\+json["\']>(.*?)</script>'
    matches = re.findall(pattern, html, re.DOTALL | re.IGNORECASE)

    for match in matches:
        try:
            data = json.loads(match.strip())
            if isinstance(data, list):
                for item in data:
                    t = item.get("@type", "")
                    if t:
                        types.append(t)
            elif isinstance(data, dict):
                if "@graph" in data:
                    for item in data["@graph"]:
                        t = item.get("@type", "")
                        if t:
                            types.append(t)
                else:
                    t = data.get("@type", "")
                    if t:
                        types.append(t)
        except (json.JSONDecodeError, AttributeError):
            types.append("_invalid_json")

    return types


def classify_page_type(filepath, html):
    """Guess page type from filename and content."""
    name = filepath.stem.lower()
    content_lower = html.lower()

    if name in ('index', 'home', 'homepage') or '<main' in content_lower[:500]:
        if 'product' in name or 'shop' in name:
            return "product"
        return "homepage"
    if 'blog' in name or 'post' in name or 'article' in name:
        return "blog_post"
    if 'faq' in name:
        return "faq"
    if 'about' in name:
        return "about"
    if 'contact' in name:
        return "contact"
    if 'product' in name or 'pricing' in name:
        return "product"
    if 'how' in name or 'guide' in name or 'tutorial' in name:
        return "howto"
    if 'event' in name:
        return "event"
    if 'author' in name or 'team' in name:
        return "author"

    # Check content patterns
    if re.search(r'<h[23].*?FAQ|Frequently Asked', html, re.IGNORECASE):
        return "faq"
    if re.search(r'Step\s+\d|How\s+to', html, re.IGNORECASE):
        return "howto"

    return "content"


RECOMMENDED_SCHEMA = {
    "homepage": ["Organization", "WebSite"],
    "blog_post": ["Article", "BreadcrumbList"],
    "faq": ["FAQPage", "BreadcrumbList"],
    "howto": ["HowTo", "BreadcrumbList", "Article"],
    "product": ["Product", "BreadcrumbList"],
    "about": ["Organization", "BreadcrumbList"],
    "contact": ["LocalBusiness", "BreadcrumbList"],
    "event": ["Event", "BreadcrumbList"],
    "author": ["Person", "BreadcrumbList"],
    "content": ["Article", "BreadcrumbList"],
}


def audit_page(filepath):
    """Audit a single page for schema coverage."""
    html = filepath.read_text(encoding="utf-8", errors="replace")
    found_types = extract_schema_types(html)
    page_type = classify_page_type(filepath, html)
    recommended = RECOMMENDED_SCHEMA.get(page_type, ["BreadcrumbList"])

    missing = [r for r in recommended if r not in found_types]
    extra = [f for f in found_types if f not in recommended and f != "_invalid_json"]
    has_invalid = "_invalid_json" in found_types

    issues = []
    if has_invalid:
        issues.append({
            "type": "invalid_json",
            "severity": "Critical",
            "detail": "Contains invalid JSON-LD that cannot be parsed",
        })
    for m in missing:
        issues.append({
            "type": "missing_schema",
            "severity": "High" if m in ("Article", "Product", "FAQPage") else "Medium",
            "detail": f"Missing recommended {m} schema for {page_type} page",
        })
    if not found_types:
        issues.append({
            "type": "no_schema",
            "severity": "High",
            "detail": "No structured data found on page",
        })

    score = 100
    for issue in issues:
        if issue["severity"] == "Critical":
            score -= 25
        elif issue["severity"] == "High":
            score -= 15
        elif issue["severity"] == "Medium":
            score -= 5
    score = max(0, score)

    return {
        "file": str(filepath),
        "page_type": page_type,
        "found_schema": found_types,
        "recommended_schema": recommended,
        "missing_schema": missing,
        "extra_schema": extra,
        "score": score,
        "issues": issues,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Audit schema markup coverage across pages"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--directory", help="Directory of HTML files to audit")
    group.add_argument("--files", nargs="+", help="Specific HTML files to audit")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument(
        "--report", choices=["coverage", "issues", "summary"],
        default="summary", help="Report type (default: summary)"
    )
    args = parser.parse_args()

    files = []
    if args.directory:
        dirpath = Path(args.directory)
        if not dirpath.is_dir():
            print(f"Error: {dirpath} is not a directory", file=sys.stderr)
            sys.exit(1)
        files = sorted(dirpath.glob("**/*.html")) + sorted(dirpath.glob("**/*.htm"))
    else:
        files = [Path(f) for f in args.files]

    if not files:
        print("No HTML files found.", file=sys.stderr)
        sys.exit(1)

    results = [audit_page(f) for f in files if f.exists()]

    # Summary stats
    total = len(results)
    with_schema = sum(1 for r in results if r["found_schema"])
    no_schema = sum(1 for r in results if not r["found_schema"])
    avg_score = round(sum(r["score"] for r in results) / max(total, 1), 1)

    # Type coverage
    all_types = {}
    for r in results:
        for t in r["found_schema"]:
            all_types[t] = all_types.get(t, 0) + 1

    # Missing analysis
    all_missing = {}
    for r in results:
        for m in r["missing_schema"]:
            all_missing[m] = all_missing.get(m, 0) + 1

    summary = {
        "total_pages": total,
        "with_schema": with_schema,
        "without_schema": no_schema,
        "coverage_rate": round(with_schema / max(total, 1) * 100, 1),
        "average_score": avg_score,
        "schema_types_found": all_types,
        "most_missing": dict(sorted(all_missing.items(), key=lambda x: x[1], reverse=True)[:5]),
    }

    output = {
        "summary": summary,
        "pages": results,
    }

    if args.json:
        print(json.dumps(output, indent=2))
    else:
        print(f"\n{'='*60}")
        print(f"  SCHEMA COVERAGE AUDIT — {total} pages")
        print(f"{'='*60}")
        print(f"  Coverage: {with_schema}/{total} pages ({summary['coverage_rate']}%)")
        print(f"  Average score: {avg_score}/100")
        print(f"  Pages without any schema: {no_schema}")

        if all_types:
            print(f"\n  Schema Types Found:")
            for t, count in sorted(all_types.items(), key=lambda x: x[1], reverse=True):
                print(f"    {t}: {count} pages")

        if all_missing:
            print(f"\n  Most Commonly Missing:")
            for t, count in sorted(all_missing.items(), key=lambda x: x[1], reverse=True)[:5]:
                print(f"    {t}: missing on {count} pages")

        if args.report in ("issues", "coverage"):
            print(f"\n  Per-Page Details:")
            for r in results:
                status = "OK" if r["score"] >= 80 else "NEEDS WORK" if r["score"] >= 50 else "POOR"
                found = ", ".join(r["found_schema"]) if r["found_schema"] else "none"
                print(f"\n  {r['file']} [{status}] Score: {r['score']}/100")
                print(f"    Type: {r['page_type']} | Schema: {found}")
                if r["missing_schema"]:
                    print(f"    Missing: {', '.join(r['missing_schema'])}")
                if args.report == "issues" and r["issues"]:
                    for issue in r["issues"]:
                        print(f"    [{issue['severity']}] {issue['detail']}")

        print()


if __name__ == "__main__":
    main()
