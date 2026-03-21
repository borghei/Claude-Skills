#!/usr/bin/env python3
"""
Internal Link Structure Mapper

Maps internal linking structure from a sitemap, analyzes hub-spoke
relationships, identifies potential orphan pages, and scores link
equity distribution across the site architecture.

Usage:
    python link_mapper.py --sitemap sitemap.xml
    python link_mapper.py --sitemap sitemap.xml --json
    python link_mapper.py --urls urls.txt --hub-analysis
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
    ET = None


SITEMAP_NS = {'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9'}


def parse_sitemap(filepath):
    """Extract URLs from XML sitemap."""
    if not ET:
        return [], "XML parser not available"
    content = filepath.read_text(encoding="utf-8", errors="replace")
    try:
        root = ET.fromstring(content)
    except ET.ParseError as e:
        return [], f"Parse error: {e}"

    urls = []
    for loc in root.findall('.//sm:url/sm:loc', SITEMAP_NS):
        if loc.text:
            urls.append(loc.text.strip())
    if not urls:
        for loc in root.findall('.//url/loc'):
            if loc.text:
                urls.append(loc.text.strip())
    return urls, None


def load_urls(filepath):
    """Load URLs from a text file."""
    return [l.strip() for l in filepath.read_text().splitlines()
            if l.strip() and not l.startswith('#')]


def build_hierarchy(urls):
    """Build a hierarchical structure from URLs."""
    hierarchy = defaultdict(list)
    url_info = {}

    for url in urls:
        parsed = urlparse(url)
        segments = [s for s in parsed.path.split('/') if s]
        depth = len(segments)

        # Determine parent
        if depth == 0:
            parent = None
        elif depth == 1:
            parent = "/"
        else:
            parent_path = "/" + "/".join(segments[:-1]) + "/"
            parent = parent_path

        # Determine section (first segment)
        section = segments[0] if segments else "root"

        url_info[url] = {
            "url": url,
            "path": parsed.path,
            "depth": depth,
            "section": section,
            "parent_path": parent,
            "segments": segments,
        }

        hierarchy[section].append(url)

    return hierarchy, url_info


def identify_hubs(hierarchy, url_info):
    """Identify potential hub pages in each section."""
    hubs = []

    for section, urls in hierarchy.items():
        if section == "root":
            continue

        # The shallowest page in a section is likely the hub
        section_urls = sorted(urls, key=lambda u: url_info[u]["depth"])
        if section_urls:
            hub_url = section_urls[0]
            spoke_count = len(section_urls) - 1

            hubs.append({
                "section": section,
                "hub_url": hub_url,
                "hub_depth": url_info[hub_url]["depth"],
                "spoke_count": spoke_count,
                "spoke_urls": section_urls[1:],
            })

    return hubs


def analyze_link_equity(url_info, hubs):
    """Estimate link equity distribution."""
    total = len(url_info)
    depth_distribution = Counter()
    section_distribution = Counter()

    for info in url_info.values():
        depth_distribution[info["depth"]] += 1
        section_distribution[info["section"]] += 1

    # Estimate equity concentration
    # Pages at depth 1-2 get more equity than deep pages
    equity_estimates = {}
    for url, info in url_info.items():
        depth = info["depth"]
        if depth == 0:
            equity = 100  # Homepage
        elif depth == 1:
            equity = 50
        elif depth == 2:
            equity = 25
        elif depth == 3:
            equity = 12
        else:
            equity = 5
        equity_estimates[url] = equity

    # Section balance
    sections = list(section_distribution.keys())
    if sections:
        avg_pages = total / len(sections)
        imbalanced = {s: c for s, c in section_distribution.items()
                      if c > avg_pages * 3 or (c < avg_pages * 0.2 and c < 3)}
    else:
        imbalanced = {}

    return {
        "depth_distribution": dict(depth_distribution),
        "section_distribution": dict(section_distribution.most_common(20)),
        "equity_estimates": equity_estimates,
        "imbalanced_sections": imbalanced,
    }


def detect_potential_orphans(url_info, hubs):
    """Identify pages that might be orphans based on structure."""
    potential_orphans = []

    hub_sections = {h["section"] for h in hubs}

    for url, info in url_info.items():
        # Deep pages not in any hub section
        if info["depth"] >= 3 and info["section"] not in hub_sections:
            potential_orphans.append({
                "url": url,
                "reason": "Deep page in section with no hub",
                "depth": info["depth"],
            })

        # Pages at unusual depth for their section
        section_urls = [u for u, i in url_info.items() if i["section"] == info["section"]]
        section_depths = [url_info[u]["depth"] for u in section_urls]
        if section_depths:
            avg_depth = sum(section_depths) / len(section_depths)
            if info["depth"] > avg_depth + 2:
                potential_orphans.append({
                    "url": url,
                    "reason": "Unusually deep for its section",
                    "depth": info["depth"],
                })

    return potential_orphans


def main():
    parser = argparse.ArgumentParser(
        description="Map internal link structure from sitemap"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--sitemap", help="XML sitemap file")
    group.add_argument("--urls", help="Text file with URLs")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--hub-analysis", action="store_true", help="Show hub-spoke analysis")
    args = parser.parse_args()

    urls = []
    if args.sitemap:
        fp = Path(args.sitemap)
        if not fp.exists():
            print(f"Error: {fp} not found", file=sys.stderr)
            sys.exit(1)
        urls, err = parse_sitemap(fp)
        if err:
            print(f"Error: {err}", file=sys.stderr)
            sys.exit(1)
    else:
        fp = Path(args.urls)
        if not fp.exists():
            print(f"Error: {fp} not found", file=sys.stderr)
            sys.exit(1)
        urls = load_urls(fp)

    if not urls:
        print("No URLs found.", file=sys.stderr)
        sys.exit(1)

    hierarchy, url_info = build_hierarchy(urls)
    hubs = identify_hubs(hierarchy, url_info)
    equity = analyze_link_equity(url_info, hubs)
    orphans = detect_potential_orphans(url_info, hubs)

    result = {
        "total_urls": len(urls),
        "sections": len(hierarchy),
        "hubs": hubs,
        "equity_analysis": {
            "depth_distribution": equity["depth_distribution"],
            "section_distribution": equity["section_distribution"],
            "imbalanced_sections": equity["imbalanced_sections"],
        },
        "potential_orphans": orphans,
    }

    if args.json:
        print(json.dumps(result, indent=2, default=str))
    else:
        print(f"\n{'='*60}")
        print(f"  LINK STRUCTURE MAP — {len(urls)} URLs, {len(hierarchy)} sections")
        print(f"{'='*60}")

        print(f"\n  Depth Distribution:")
        for depth in sorted(equity["depth_distribution"].keys()):
            count = equity["depth_distribution"][depth]
            pct = round(count / len(urls) * 100, 1)
            print(f"    Depth {depth}: {count} pages ({pct}%)")

        print(f"\n  Top Sections:")
        for section, count in list(equity["section_distribution"].items())[:10]:
            print(f"    /{section}/: {count} pages")

        if args.hub_analysis and hubs:
            print(f"\n  Hub-Spoke Analysis:")
            for hub in sorted(hubs, key=lambda h: h["spoke_count"], reverse=True):
                print(f"\n    Hub: /{hub['section']}/ ({hub['spoke_count']} spokes)")
                print(f"    Hub URL: {hub['hub_url']}")
                for spoke in hub["spoke_urls"][:5]:
                    print(f"      -> {spoke}")
                if hub["spoke_count"] > 5:
                    print(f"      ... and {hub['spoke_count'] - 5} more")

        if equity["imbalanced_sections"]:
            print(f"\n  Imbalanced Sections:")
            for section, count in equity["imbalanced_sections"].items():
                print(f"    /{section}/: {count} pages (check balance)")

        if orphans:
            print(f"\n  Potential Orphan Pages ({len(orphans)}):")
            for o in orphans[:10]:
                print(f"    {o['url']} — {o['reason']} (depth: {o['depth']})")
            if len(orphans) > 10:
                print(f"    ... and {len(orphans) - 10} more")

        print()


if __name__ == "__main__":
    main()
