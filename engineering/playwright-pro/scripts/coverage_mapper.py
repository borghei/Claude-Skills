#!/usr/bin/env python3
"""Map Playwright tests to user stories and identify coverage gaps.

Reads a user flows definition file and scans Playwright test files to
determine which flows are covered by tests and which have gaps. Produces
a coverage matrix with gap analysis and recommendations.

Usage:
    python coverage_mapper.py --tests ./tests/e2e/ --flows flows.json
    python coverage_mapper.py --tests ./tests/e2e/ --flows flows.json --json
    python coverage_mapper.py --tests ./tests/e2e/ --flows flows.json --gaps-only

Expected flows.json format:
[
    {
        "id": "AUTH-001",
        "name": "User login with email",
        "priority": "critical",
        "keywords": ["login", "sign in", "email", "password", "authenticate"],
        "pages": ["/login", "/dashboard"],
        "steps": ["Navigate to login", "Enter email", "Enter password", "Click sign in", "See dashboard"]
    }
]
"""

import argparse
import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path


def load_flows(path):
    """Load user flow definitions from JSON file."""
    with open(path, "r") as f:
        flows = json.load(f)
    for flow in flows:
        flow.setdefault("priority", "medium")
        flow.setdefault("keywords", [])
        flow.setdefault("pages", [])
        flow.setdefault("steps", [])
    return flows


def scan_test_files(test_dir):
    """Scan Playwright test files and extract test metadata."""
    test_dir = Path(test_dir)
    test_files = []

    patterns = ["**/*.spec.ts", "**/*.test.ts", "**/*.spec.js", "**/*.test.js"]
    found_files = set()
    for pattern in patterns:
        found_files.update(test_dir.glob(pattern))

    for tf in sorted(found_files):
        try:
            content = tf.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue

        # Extract test names
        test_names = re.findall(r"test\s*\(\s*['\"](.+?)['\"]", content)

        # Extract describe block names
        describe_names = re.findall(r"test\.describe\s*\(\s*['\"](.+?)['\"]", content)

        # Extract URLs navigated to
        urls = re.findall(r"\.goto\s*\(\s*['\"](.+?)['\"]", content)
        urls += re.findall(r"toHaveURL\s*\(\s*['\"/](.+?)['\"/]", content)

        # Extract Page Object imports
        page_objects = re.findall(r"import\s*\{.*?(\w+Page)\w*.*?\}\s*from", content)

        # Extract all significant words for keyword matching
        words = set(re.findall(r"[a-zA-Z]{3,}", content.lower()))

        test_files.append({
            "path": str(tf.relative_to(test_dir) if tf.is_relative_to(test_dir) else tf),
            "test_names": test_names,
            "describe_names": describe_names,
            "urls": urls,
            "page_objects": page_objects,
            "word_set": words,
            "test_count": len(test_names),
        })

    return test_files


def compute_match_score(flow, test_file):
    """Compute a match score between a flow and a test file.

    Returns a score from 0.0 to 1.0 indicating how likely the test
    covers the flow.
    """
    score = 0.0
    max_score = 0.0

    # Keyword matching (weight: 0.4)
    max_score += 0.4
    if flow["keywords"]:
        keyword_matches = sum(
            1 for kw in flow["keywords"]
            if kw.lower() in test_file["word_set"]
        )
        keyword_ratio = keyword_matches / len(flow["keywords"])
        score += 0.4 * keyword_ratio

    # URL matching (weight: 0.3)
    max_score += 0.3
    if flow["pages"]:
        url_matches = 0
        for flow_url in flow["pages"]:
            flow_url_clean = flow_url.strip("/").lower()
            for test_url in test_file["urls"]:
                test_url_clean = test_url.strip("/").lower()
                if flow_url_clean in test_url_clean or test_url_clean in flow_url_clean:
                    url_matches += 1
                    break
        url_ratio = url_matches / len(flow["pages"])
        score += 0.3 * url_ratio

    # Test name matching (weight: 0.2)
    max_score += 0.2
    flow_name_words = set(re.findall(r"[a-zA-Z]{3,}", flow["name"].lower()))
    all_test_text = " ".join(test_file["test_names"] + test_file["describe_names"]).lower()
    test_text_words = set(re.findall(r"[a-zA-Z]{3,}", all_test_text))
    if flow_name_words:
        name_overlap = len(flow_name_words & test_text_words) / len(flow_name_words)
        score += 0.2 * name_overlap

    # Flow ID in test name (weight: 0.1)
    max_score += 0.1
    flow_id = flow["id"].lower()
    if flow_id in all_test_text.lower():
        score += 0.1

    return round(score / max_score if max_score > 0 else 0, 3)


def map_coverage(flows, test_files, threshold=0.3):
    """Map flows to tests and identify gaps."""
    coverage = []

    for flow in flows:
        matches = []
        for tf in test_files:
            score = compute_match_score(flow, tf)
            if score >= threshold:
                matches.append({
                    "file": tf["path"],
                    "score": score,
                    "test_count": tf["test_count"],
                    "test_names": tf["test_names"][:5],  # Limit for readability
                })

        matches.sort(key=lambda m: -m["score"])

        status = "covered" if matches else "gap"
        best_score = matches[0]["score"] if matches else 0.0

        coverage.append({
            "flow_id": flow["id"],
            "flow_name": flow["name"],
            "priority": flow["priority"],
            "status": status,
            "best_match_score": best_score,
            "matching_tests": matches[:3],  # Top 3 matches
            "total_matching_files": len(matches),
        })

    return coverage


def compute_summary(coverage):
    """Compute summary statistics from coverage results."""
    total = len(coverage)
    covered = sum(1 for c in coverage if c["status"] == "covered")
    gaps = total - covered

    by_priority = defaultdict(lambda: {"total": 0, "covered": 0, "gaps": 0})
    for c in coverage:
        p = c["priority"]
        by_priority[p]["total"] += 1
        if c["status"] == "covered":
            by_priority[p]["covered"] += 1
        else:
            by_priority[p]["gaps"] += 1

    return {
        "total_flows": total,
        "covered": covered,
        "gaps": gaps,
        "coverage_pct": round(covered / total * 100, 1) if total else 0,
        "by_priority": dict(by_priority),
    }


def format_human(coverage, summary, test_file_count):
    """Format results for human-readable output."""
    output = []
    output.append("=" * 70)
    output.append("TEST COVERAGE MAPPER")
    output.append("=" * 70)
    output.append("")
    output.append(f"  User flows:     {summary['total_flows']}")
    output.append(f"  Test files:     {test_file_count}")
    output.append(f"  Covered:        {summary['covered']} ({summary['coverage_pct']}%)")
    output.append(f"  Gaps:           {summary['gaps']}")
    output.append("")

    # By priority
    priority_order = ["critical", "high", "medium", "low"]
    output.append("COVERAGE BY PRIORITY")
    output.append("-" * 70)
    for p in priority_order:
        stats = summary["by_priority"].get(p)
        if stats:
            pct = round(stats["covered"] / stats["total"] * 100) if stats["total"] else 0
            bar_filled = int(pct / 5)
            bar = "#" * bar_filled + "." * (20 - bar_filled)
            output.append(f"  {p.upper():<10} [{bar}] {pct:>3}%  ({stats['covered']}/{stats['total']})")
    output.append("")

    # Coverage matrix
    output.append("COVERAGE MATRIX")
    output.append("-" * 70)
    output.append(f"  {'ID':<12} {'Priority':<10} {'Status':<10} {'Score':>6}  Flow Name")
    output.append(f"  {'─' * 12} {'─' * 10} {'─' * 10} {'─' * 6}  {'─' * 25}")

    for c in coverage:
        status_mark = "COVERED" if c["status"] == "covered" else "GAP"
        output.append(
            f"  {c['flow_id']:<12} {c['priority']:<10} {status_mark:<10} "
            f"{c['best_match_score']:>5.0%}  {c['flow_name'][:35]}"
        )
        if c["matching_tests"]:
            for mt in c["matching_tests"][:2]:
                output.append(f"  {'':>42} -> {mt['file']} ({mt['test_count']} tests)")
    output.append("")

    # Gaps detail
    gaps = [c for c in coverage if c["status"] == "gap"]
    if gaps:
        output.append("COVERAGE GAPS (need tests)")
        output.append("-" * 70)
        for g in sorted(gaps, key=lambda x: {"critical": 0, "high": 1, "medium": 2, "low": 3}.get(x["priority"], 9)):
            output.append(f"  [{g['priority'].upper()}] {g['flow_id']}: {g['flow_name']}")
        output.append("")

    # Verdict
    output.append("=" * 70)
    critical_gaps = [g for g in gaps if g["priority"] == "critical"]
    if critical_gaps:
        output.append(f"VERDICT: CRITICAL GAPS - {len(critical_gaps)} critical flows have no test coverage")
    elif gaps:
        output.append(f"VERDICT: GAPS EXIST - {len(gaps)} flows need tests ({summary['coverage_pct']}% covered)")
    else:
        output.append("VERDICT: FULL COVERAGE - All defined user flows have test coverage")
    output.append("=" * 70)

    return "\n".join(output)


def main():
    parser = argparse.ArgumentParser(
        description="Map Playwright tests to user stories and identify coverage gaps.",
        epilog="Example: python coverage_mapper.py --tests ./tests/e2e/ --flows flows.json",
    )
    parser.add_argument("--tests", required=True, help="Path to Playwright test directory")
    parser.add_argument("--flows", required=True, help="Path to user flows JSON definition file")
    parser.add_argument("--threshold", type=float, default=0.3, help="Match score threshold (default: 0.3)")
    parser.add_argument("--gaps-only", action="store_true", help="Only show flows with coverage gaps")
    parser.add_argument("--json", action="store_true", dest="json_output", help="Output as JSON")

    args = parser.parse_args()

    if not os.path.isdir(args.tests):
        print(f"Error: Test directory '{args.tests}' not found.", file=sys.stderr)
        sys.exit(1)
    if not os.path.isfile(args.flows):
        print(f"Error: Flows file '{args.flows}' not found.", file=sys.stderr)
        sys.exit(1)

    flows = load_flows(args.flows)
    test_files = scan_test_files(args.tests)
    coverage = map_coverage(flows, test_files, args.threshold)

    if args.gaps_only:
        coverage = [c for c in coverage if c["status"] == "gap"]

    summary = compute_summary(coverage)

    if args.json_output:
        print(json.dumps({"summary": summary, "coverage": coverage}, indent=2))
    else:
        print(format_human(coverage, summary, len(test_files)))


if __name__ == "__main__":
    main()
