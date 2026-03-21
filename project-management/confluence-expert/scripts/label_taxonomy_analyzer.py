#!/usr/bin/env python3
"""Label Taxonomy Analyzer - Analyze Confluence label usage and recommend taxonomy.

Reads label data across pages and identifies inconsistencies, unused labels,
and suggests a standardized taxonomy.

Usage:
    python label_taxonomy_analyzer.py --labels labels.json
    python label_taxonomy_analyzer.py --labels labels.json --json
    python label_taxonomy_analyzer.py --example
"""

import argparse
import json
import re
import sys
from collections import Counter


def load_data(path: str) -> dict:
    with open(path, "r") as f:
        return json.load(f)


def analyze_labels(data: dict) -> dict:
    space = data.get("space", "Unknown")
    pages = data.get("pages", [])

    all_labels = []
    pages_with_labels = 0
    pages_without_labels = 0
    label_page_map = {}

    for page in pages:
        labels = page.get("labels", [])
        if labels:
            pages_with_labels += 1
        else:
            pages_without_labels += 1
        for label in labels:
            all_labels.append(label)
            if label not in label_page_map:
                label_page_map[label] = []
            label_page_map[label].append(page.get("title", "Unknown"))

    label_counts = Counter(all_labels)
    total_unique = len(label_counts)
    total_uses = len(all_labels)
    coverage_pct = round(pages_with_labels / len(pages) * 100, 1) if pages else 0

    # Identify issues
    issues = []

    # Inconsistent casing
    lower_map = {}
    for label in label_counts:
        key = label.lower()
        if key not in lower_map:
            lower_map[key] = []
        lower_map[key].append(label)
    case_conflicts = {k: v for k, v in lower_map.items() if len(v) > 1}
    if case_conflicts:
        for key, variants in case_conflicts.items():
            issues.append({
                "type": "case_conflict",
                "description": f"Case variants: {', '.join(variants)}",
                "suggestion": f"Standardize to: {key}",
            })

    # Inconsistent separators
    separator_issues = []
    for label in label_counts:
        if " " in label:
            separator_issues.append(label)
        elif "_" in label and "-" in str(label_counts):
            separator_issues.append(label)
    if separator_issues:
        issues.append({
            "type": "separator_inconsistency",
            "description": f"Labels with spaces (use hyphens instead): {', '.join(separator_issues[:5])}",
            "suggestion": "Use lowercase-hyphen-separated labels consistently.",
        })

    # Rarely used labels (only 1 page)
    rare_labels = [l for l, c in label_counts.items() if c == 1]

    # Very popular labels (might be too broad)
    popular_labels = [(l, c) for l, c in label_counts.most_common(5)]

    # Label categories (heuristic grouping)
    categories = {
        "status": [], "type": [], "team": [], "project": [], "other": [],
    }
    status_words = {"draft", "review", "approved", "archived", "deprecated", "active", "done", "wip"}
    type_words = {"guide", "how-to", "faq", "reference", "process", "template", "meeting", "retro", "sprint"}
    team_words = {"engineering", "product", "design", "marketing", "sales", "support", "hr", "finance"}

    for label in label_counts:
        lower = label.lower().replace("-", " ").replace("_", " ")
        words = set(lower.split())
        if words & status_words:
            categories["status"].append(label)
        elif words & type_words:
            categories["type"].append(label)
        elif words & team_words:
            categories["team"].append(label)
        else:
            categories["other"].append(label)

    # Recommendations
    recs = []
    if coverage_pct < 70:
        recs.append(f"Label coverage is {coverage_pct:.0f}% (target: 90%+). Add labels to {pages_without_labels} unlabeled pages.")
    if case_conflicts:
        recs.append(f"Fix {len(case_conflicts)} label case conflict(s). Standardize to lowercase-hyphen format.")
    if len(rare_labels) > total_unique * 0.5:
        recs.append(f"{len(rare_labels)} labels used only once. Consolidate into a curated taxonomy of 20-30 standard labels.")
    if separator_issues:
        recs.append("Replace spaces and underscores in labels with hyphens for consistency.")

    return {
        "space": space,
        "total_pages": len(pages),
        "pages_with_labels": pages_with_labels,
        "pages_without_labels": pages_without_labels,
        "coverage_pct": coverage_pct,
        "total_unique_labels": total_unique,
        "total_label_uses": total_uses,
        "top_labels": [{"label": l, "count": c} for l, c in label_counts.most_common(10)],
        "rare_labels": rare_labels[:20],
        "case_conflicts": {k: v for k, v in list(case_conflicts.items())[:5]},
        "categories": {k: v for k, v in categories.items() if v},
        "issues": issues,
        "recommendations": recs,
    }


def print_report(result: dict) -> None:
    print(f"\nLabel Taxonomy Analysis: {result['space']}")
    print(f"Pages: {result['total_pages']}  |  Unique Labels: {result['total_unique_labels']}")
    print("=" * 55)
    print(f"Coverage: {result['coverage_pct']:.0f}% ({result['pages_with_labels']} labeled / {result['pages_without_labels']} unlabeled)")

    print(f"\nTop Labels:")
    for tl in result["top_labels"]:
        bar = "#" * min(tl["count"], 30)
        print(f"  {tl['label']:<25} {tl['count']:>4}  {bar}")

    if result["case_conflicts"]:
        print(f"\nCase Conflicts:")
        for key, variants in result["case_conflicts"].items():
            print(f"  '{key}': {', '.join(variants)}")

    if result["categories"]:
        print(f"\nLabel Categories:")
        for cat, labels in result["categories"].items():
            print(f"  {cat.title()}: {', '.join(labels[:5])}")

    if result["rare_labels"]:
        print(f"\nRarely Used Labels (1 page): {', '.join(result['rare_labels'][:10])}")

    if result["recommendations"]:
        print(f"\nRecommendations:")
        for i, r in enumerate(result["recommendations"], 1):
            print(f"  {i}. {r}")
    print()


def print_example() -> None:
    example = {
        "space": "Engineering Team",
        "pages": [
            {"title": "Onboarding Guide", "labels": ["onboarding", "guide", "engineering"]},
            {"title": "API Reference", "labels": ["api", "reference", "Engineering"]},
            {"title": "Sprint 23 Retro", "labels": ["sprint", "retro"]},
            {"title": "Old Design Doc", "labels": ["design doc"]},
            {"title": "Quick Notes", "labels": []},
            {"title": "Architecture Overview", "labels": ["architecture", "reference"]},
        ],
    }
    print(json.dumps(example, indent=2))


def main():
    parser = argparse.ArgumentParser(description="Analyze Confluence label taxonomy.")
    parser.add_argument("--labels", type=str, help="Path to label data JSON file")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--example", action="store_true", help="Print example and exit")
    args = parser.parse_args()

    if args.example:
        print_example()
        return
    if not args.labels:
        parser.error("--labels is required")

    data = load_data(args.labels)
    result = analyze_labels(data)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print_report(result)


if __name__ == "__main__":
    main()
