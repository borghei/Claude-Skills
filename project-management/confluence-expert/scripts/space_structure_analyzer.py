#!/usr/bin/env python3
"""Space Structure Analyzer - Analyze Confluence space architecture against best practices.

Evaluates page hierarchy depth, naming consistency, and structural patterns
to recommend improvements for navigation and discoverability.

Usage:
    python space_structure_analyzer.py --space space.json
    python space_structure_analyzer.py --space space.json --json
    python space_structure_analyzer.py --example
"""

import argparse
import json
import sys
from collections import Counter


def load_data(path: str) -> dict:
    with open(path, "r") as f:
        return json.load(f)


def analyze_structure(data: dict) -> dict:
    space_name = data.get("space", "Unknown")
    pages = data.get("pages", [])

    # Build hierarchy
    page_map = {p.get("id"): p for p in pages}
    children = {}
    root_pages = []

    for p in pages:
        parent_id = p.get("parent_id")
        if parent_id:
            if parent_id not in children:
                children[parent_id] = []
            children[parent_id].append(p["id"])
        else:
            root_pages.append(p["id"])

    # Calculate depths
    def get_depth(page_id, depth=0):
        max_depth = depth
        for child_id in children.get(page_id, []):
            child_depth = get_depth(child_id, depth + 1)
            max_depth = max(max_depth, child_depth)
        return max_depth

    max_depth = 0
    depth_distribution = Counter()
    for page in pages:
        page_id = page.get("id")
        # Calculate this page's depth
        depth = 0
        current = page
        while current.get("parent_id") and current["parent_id"] in page_map:
            depth += 1
            current = page_map[current["parent_id"]]
        depth_distribution[depth] += 1
        max_depth = max(max_depth, depth)

    # Root page analysis
    recommended_roots = ["Overview", "Team Information", "Projects", "Processes", "Meeting Notes", "Resources"]

    # Naming analysis
    titles = [p.get("title", "") for p in pages]
    short_titles = [t for t in titles if len(t) < 5]
    long_titles = [t for t in titles if len(t) > 60]
    duplicate_titles = [t for t, count in Counter(titles).items() if count > 1]

    # Score
    score = 100
    issues = []
    recs = []

    if max_depth > 5:
        issues.append(f"Page hierarchy too deep ({max_depth} levels). Recommended max: 3-4 levels.")
        recs.append("Flatten deep hierarchies. Use labels and search instead of deep nesting.")
        score -= 20
    elif max_depth > 3:
        issues.append(f"Page hierarchy is {max_depth} levels deep. Consider flattening to 3.")
        score -= 10

    if len(root_pages) > 10:
        issues.append(f"Too many root pages ({len(root_pages)}). Creates cluttered navigation.")
        recs.append("Consolidate root pages into 5-7 top-level categories.")
        score -= 15
    elif len(root_pages) < 3:
        issues.append(f"Only {len(root_pages)} root page(s). Consider adding standard sections.")
        score -= 5

    if short_titles:
        issues.append(f"{len(short_titles)} page(s) with very short titles (<5 chars).")
        recs.append("Use descriptive page titles. Short titles are hard to find in search.")
        score -= 5

    if duplicate_titles:
        issues.append(f"{len(duplicate_titles)} duplicate title(s): {', '.join(duplicate_titles[:3])}")
        recs.append("Rename duplicate pages to be unique and descriptive.")
        score -= 10

    # Wide pages (too many children)
    wide_pages = []
    for page_id, child_list in children.items():
        if len(child_list) > 15:
            page = page_map.get(page_id, {})
            wide_pages.append({"title": page.get("title", "Unknown"), "children": len(child_list)})
    if wide_pages:
        issues.append(f"{len(wide_pages)} page(s) with >15 children. Creates scrolling navigation.")
        recs.append("Group child pages under subcategories. Target 5-10 children per page.")
        score -= 10

    score = max(0, score)
    if score >= 80:
        rating = "Well Structured"
    elif score >= 60:
        rating = "Needs Improvement"
    else:
        rating = "Poorly Structured"

    return {
        "space": space_name,
        "total_pages": len(pages),
        "score": score,
        "rating": rating,
        "max_depth": max_depth,
        "root_pages": len(root_pages),
        "depth_distribution": dict(depth_distribution),
        "naming": {
            "short_titles": len(short_titles),
            "long_titles": len(long_titles),
            "duplicates": duplicate_titles,
        },
        "wide_pages": wide_pages,
        "issues": issues,
        "recommendations": recs,
    }


def print_report(result: dict) -> None:
    print(f"\nSpace Structure Analysis: {result['space']}")
    print(f"Pages: {result['total_pages']}")
    print("=" * 55)
    print(f"Score: {result['score']}/100 ({result['rating']})")
    print(f"Max Depth: {result['max_depth']}  |  Root Pages: {result['root_pages']}")

    print(f"\nDepth Distribution:")
    for depth in sorted(result["depth_distribution"].keys()):
        count = result["depth_distribution"][depth]
        bar = "#" * min(count, 40)
        print(f"  Level {depth}: {count:>4} pages  {bar}")

    if result["naming"]["duplicates"]:
        print(f"\nDuplicate Titles: {', '.join(result['naming']['duplicates'])}")

    if result["wide_pages"]:
        print(f"\nWide Pages (>15 children):")
        for wp in result["wide_pages"]:
            print(f"  - {wp['title']}: {wp['children']} children")

    if result["issues"]:
        print(f"\nIssues:")
        for issue in result["issues"]:
            print(f"  ! {issue}")

    if result["recommendations"]:
        print(f"\nRecommendations:")
        for i, r in enumerate(result["recommendations"], 1):
            print(f"  {i}. {r}")
    print()


def print_example() -> None:
    example = {
        "space": "Engineering Team",
        "pages": [
            {"id": "1", "title": "Overview", "parent_id": None},
            {"id": "2", "title": "Team Members", "parent_id": "1"},
            {"id": "3", "title": "Projects", "parent_id": None},
            {"id": "4", "title": "Project Alpha", "parent_id": "3"},
            {"id": "5", "title": "Design Docs", "parent_id": "4"},
            {"id": "6", "title": "API Spec", "parent_id": "5"},
            {"id": "7", "title": "v2 Changes", "parent_id": "6"},
            {"id": "8", "title": "Meeting Notes", "parent_id": None},
            {"id": "9", "title": "test", "parent_id": None},
            {"id": "10", "title": "test", "parent_id": None},
        ],
    }
    print(json.dumps(example, indent=2))


def main():
    parser = argparse.ArgumentParser(description="Analyze Confluence space structure.")
    parser.add_argument("--space", type=str, help="Path to space structure JSON file")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--example", action="store_true", help="Print example and exit")
    args = parser.parse_args()

    if args.example:
        print_example()
        return
    if not args.space:
        parser.error("--space is required")

    data = load_data(args.space)
    result = analyze_structure(data)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print_report(result)


if __name__ == "__main__":
    main()
