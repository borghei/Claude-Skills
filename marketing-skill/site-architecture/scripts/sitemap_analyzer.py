#!/usr/bin/env python3
"""
Site Architecture Sitemap Analyzer

Analyzes XML sitemaps for architectural issues including URL depth
distribution, directory structure patterns, orphan detection signals,
and crawl equity concentration.

Usage:
    python sitemap_analyzer.py --file sitemap.xml
    python sitemap_analyzer.py --file sitemap.xml --json
    python sitemap_analyzer.py --file sitemap.xml --depth-report
"""

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import urlparse

try:
    import xml.etree.ElementTree as ET
except ImportError:
    print("Error: xml.etree.ElementTree not available", file=sys.stderr)
    sys.exit(1)


SITEMAP_NS = {'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9'}


def parse_sitemap(content):
    """Parse sitemap XML and extract URLs."""
    try:
        root = ET.fromstring(content)
    except ET.ParseError as e:
        return [], f"XML parse error: {e}"

    urls = []
    # Try with namespace
    for url_elem in root.findall('.//sm:url/sm:loc', SITEMAP_NS):
        if url_elem.text:
            urls.append(url_elem.text.strip())
    # Try without namespace
    if not urls:
        for url_elem in root.findall('.//url/loc'):
            if url_elem.text:
                urls.append(url_elem.text.strip())
    # Check for sitemap index
    if not urls:
        for loc in root.findall('.//sm:sitemap/sm:loc', SITEMAP_NS):
            if loc.text:
                urls.append(loc.text.strip())
        if not urls:
            for loc in root.findall('.//sitemap/loc'):
                if loc.text:
                    urls.append(loc.text.strip())

    return urls, None


def analyze_depth(urls):
    """Analyze URL depth distribution."""
    depth_counts = Counter()
    depth_urls = defaultdict(list)

    for url in urls:
        parsed = urlparse(url)
        segments = [s for s in parsed.path.split('/') if s]
        depth = len(segments)
        depth_counts[depth] += 1
        if len(depth_urls[depth]) < 5:  # Keep max 5 examples per depth
            depth_urls[depth].append(url)

    return dict(depth_counts), {k: v for k, v in depth_urls.items()}


def analyze_directories(urls):
    """Analyze directory/section structure."""
    directories = Counter()
    for url in urls:
        parsed = urlparse(url)
        segments = [s for s in parsed.path.split('/') if s]
        if segments:
            directories[segments[0]] += 1

    return dict(directories.most_common(20))


def analyze_patterns(urls):
    """Detect URL patterns and anomalies."""
    issues = []
    stats = {
        "total_urls": len(urls),
        "unique_domains": len(set(urlparse(u).netloc for u in urls)),
        "with_params": 0,
        "with_uppercase": 0,
        "with_underscores": 0,
        "inconsistent_trailing_slash": False,
    }

    trailing_slash = {"with": 0, "without": 0}

    for url in urls:
        parsed = urlparse(url)

        if parsed.query:
            stats["with_params"] += 1

        if parsed.path != parsed.path.lower():
            stats["with_uppercase"] += 1

        if '_' in parsed.path:
            stats["with_underscores"] += 1

        if parsed.path.endswith('/') and parsed.path != '/':
            trailing_slash["with"] += 1
        elif parsed.path and parsed.path != '/':
            trailing_slash["without"] += 1

    # Check trailing slash consistency
    if trailing_slash["with"] > 0 and trailing_slash["without"] > 0:
        stats["inconsistent_trailing_slash"] = True
        issues.append({
            "type": "inconsistent_trailing_slash",
            "severity": "Medium",
            "detail": f"{trailing_slash['with']} URLs with trailing slash, {trailing_slash['without']} without — pick one convention",
        })

    if stats["with_params"] > 0:
        issues.append({
            "type": "parameterized_urls",
            "severity": "Medium",
            "detail": f"{stats['with_params']} URLs contain query parameters — verify canonical handling",
        })

    if stats["with_uppercase"] > 0:
        issues.append({
            "type": "uppercase_urls",
            "severity": "Medium",
            "detail": f"{stats['with_uppercase']} URLs contain uppercase characters",
        })

    if stats["with_underscores"] > 0:
        issues.append({
            "type": "underscore_urls",
            "severity": "Low",
            "detail": f"{stats['with_underscores']} URLs use underscores instead of hyphens",
        })

    if stats["unique_domains"] > 1:
        issues.append({
            "type": "multiple_domains",
            "severity": "High",
            "detail": f"Sitemap contains URLs from {stats['unique_domains']} domains",
        })

    return stats, issues


def analyze_architecture_health(depth_counts, total_urls):
    """Score architectural health based on depth distribution."""
    issues = []

    # Calculate percentage at each depth
    depth_pcts = {}
    for depth, count in depth_counts.items():
        depth_pcts[depth] = round(count / max(total_urls, 1) * 100, 1)

    # Deep pages check
    deep_pages = sum(count for depth, count in depth_counts.items() if depth >= 4)
    deep_pct = round(deep_pages / max(total_urls, 1) * 100, 1)

    if deep_pct > 5:
        issues.append({
            "type": "excessive_depth",
            "severity": "High",
            "detail": f"{deep_pct}% of pages are 4+ levels deep — target <5%",
        })

    # Shallow concentration check
    shallow = sum(count for depth, count in depth_counts.items() if depth <= 2)
    shallow_pct = round(shallow / max(total_urls, 1) * 100, 1)

    if shallow_pct < 50:
        issues.append({
            "type": "deep_heavy",
            "severity": "Medium",
            "detail": f"Only {shallow_pct}% of pages at depth 1-2 — architecture may be too deep",
        })

    # Score
    score = 100
    for issue in issues:
        if issue["severity"] == "High":
            score -= 20
        elif issue["severity"] == "Medium":
            score -= 10
    score = max(0, score)

    return {
        "depth_distribution": depth_pcts,
        "deep_page_percentage": deep_pct,
        "shallow_page_percentage": shallow_pct,
        "score": score,
        "issues": issues,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Analyze sitemap for site architecture issues"
    )
    parser.add_argument("--file", required=True, help="XML sitemap file path")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--depth-report", action="store_true", help="Show detailed depth analysis")
    args = parser.parse_args()

    fp = Path(args.file)
    if not fp.exists():
        print(f"Error: {fp} not found", file=sys.stderr)
        sys.exit(1)

    content = fp.read_text(encoding="utf-8", errors="replace")
    urls, error = parse_sitemap(content)

    if error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)

    if not urls:
        print("No URLs found in sitemap.", file=sys.stderr)
        sys.exit(1)

    depth_counts, depth_examples = analyze_depth(urls)
    directories = analyze_directories(urls)
    url_stats, url_issues = analyze_patterns(urls)
    health = analyze_architecture_health(depth_counts, len(urls))

    all_issues = url_issues + health["issues"]

    result = {
        "source": str(fp),
        "total_urls": len(urls),
        "depth_distribution": depth_counts,
        "directories": directories,
        "url_stats": url_stats,
        "architecture_health": health,
        "issues": all_issues,
    }

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"\n{'='*60}")
        print(f"  SITE ARCHITECTURE ANALYSIS — {len(urls)} URLs")
        print(f"{'='*60}")
        print(f"  Architecture Score: {health['score']}/100")

        print(f"\n  Depth Distribution:")
        for depth in sorted(depth_counts.keys()):
            count = depth_counts[depth]
            pct = health["depth_distribution"].get(depth, 0)
            bar = "#" * int(pct / 2)
            print(f"    Depth {depth}: {count:>6} pages ({pct:>5.1f}%) {bar}")

        if args.depth_report:
            print(f"\n  Examples by Depth:")
            for depth in sorted(depth_examples.keys()):
                print(f"    Depth {depth}:")
                for url in depth_examples[depth][:3]:
                    print(f"      {url}")

        print(f"\n  Top Directories:")
        for dir_name, count in list(directories.items())[:10]:
            print(f"    /{dir_name}/: {count} pages")

        if all_issues:
            print(f"\n  Issues ({len(all_issues)}):")
            for issue in all_issues:
                print(f"    [{issue['severity']}] {issue['detail']}")
        else:
            print(f"\n  No issues found.")

        print()


if __name__ == "__main__":
    main()
