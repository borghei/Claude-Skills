#!/usr/bin/env python3
"""Backlog Alignment Checker - Check WWAS backlog items for strategic alignment.

Reads WWAS items and validates each Why statement against defined OKRs,
identifying orphaned items and strategic gaps.

Usage:
    python backlog_alignment_checker.py --backlog backlog.json
    python backlog_alignment_checker.py --backlog backlog.json --json
    python backlog_alignment_checker.py --example
"""

import argparse
import json
import re
import sys


def load_data(path: str) -> dict:
    with open(path, "r") as f:
        return json.load(f)


def check_alignment(data: dict) -> dict:
    okrs = data.get("okrs", [])
    items = data.get("items", [])

    okr_keywords = {}
    for okr in okrs:
        okr_id = okr.get("id", "")
        okr_name = okr.get("name", "")
        keywords = okr.get("keywords", [])
        # Also extract words from the OKR name
        name_words = [w.lower() for w in re.findall(r'\w+', okr_name) if len(w) > 3]
        okr_keywords[okr_id] = {
            "name": okr_name,
            "keywords": [k.lower() for k in keywords] + name_words,
        }

    results = []
    aligned = 0
    unaligned = 0
    okr_coverage = {okr_id: 0 for okr_id in okr_keywords}

    for item in items:
        title = item.get("title", "Untitled")
        why = item.get("why", "").lower()
        what = item.get("what", "")
        acceptance_criteria = item.get("acceptance_criteria", [])
        explicit_okr = item.get("okr_ref", "")

        # Check explicit OKR reference
        matched_okrs = []
        if explicit_okr and explicit_okr in okr_keywords:
            matched_okrs.append(explicit_okr)

        # Check keyword matching
        for okr_id, okr_info in okr_keywords.items():
            if okr_id in matched_okrs:
                continue
            for kw in okr_info["keywords"]:
                if kw in why:
                    matched_okrs.append(okr_id)
                    break

        is_aligned = len(matched_okrs) > 0

        # Quality checks on Why
        why_quality = "Good"
        why_issues = []
        if not why or len(why) < 20:
            why_quality = "Missing"
            why_issues.append("Why statement is missing or too short")
        elif any(phrase in why for phrase in ["customer asked", "best practice", "need this", "just because"]):
            why_quality = "Weak"
            why_issues.append("Why uses generic rationale -- connect to a specific metric or OKR")

        # WWAS completeness
        has_why = len(why) >= 20
        has_what = len(what) >= 30
        has_ac = len(acceptance_criteria) >= 4
        completeness = sum([has_why, has_what, has_ac])

        if is_aligned:
            aligned += 1
            for okr_id in matched_okrs:
                okr_coverage[okr_id] = okr_coverage.get(okr_id, 0) + 1
        else:
            unaligned += 1

        results.append({
            "title": title,
            "is_aligned": is_aligned,
            "matched_okrs": [okr_keywords[oid]["name"] for oid in matched_okrs if oid in okr_keywords],
            "why_quality": why_quality,
            "why_issues": why_issues,
            "completeness": {
                "has_why": has_why,
                "has_what": has_what,
                "has_acceptance_criteria": has_ac,
                "score": f"{completeness}/3",
            },
        })

    # OKR coverage analysis
    uncovered_okrs = [okr_keywords[oid]["name"] for oid, count in okr_coverage.items() if count == 0]
    heavily_loaded = [(okr_keywords[oid]["name"], count) for oid, count in okr_coverage.items() if count > 5]

    alignment_rate = round(aligned / len(items) * 100, 1) if items else 0

    recs = []
    if unaligned > 0:
        recs.append(f"{unaligned} backlog item(s) not aligned to any OKR. Review and either connect to objectives or deprioritize.")
    if uncovered_okrs:
        recs.append(f"OKRs with no backlog items: {', '.join(uncovered_okrs[:3])}. Create WWAS items to support these objectives.")
    if heavily_loaded:
        for name, count in heavily_loaded:
            recs.append(f"OKR '{name}' has {count} items. Check if scope is too broad or items need re-scoping.")
    weak_whys = [r for r in results if r["why_quality"] == "Weak"]
    if weak_whys:
        recs.append(f"{len(weak_whys)} item(s) with weak Why statements. Strengthen with specific metrics, OKR references, or customer evidence.")

    return {
        "total_items": len(items),
        "aligned": aligned,
        "unaligned": unaligned,
        "alignment_rate_pct": alignment_rate,
        "okr_coverage": {okr_keywords[oid]["name"]: count for oid, count in okr_coverage.items()},
        "uncovered_okrs": uncovered_okrs,
        "items": results,
        "recommendations": recs,
    }


def print_report(result: dict) -> None:
    print(f"\nBacklog Alignment Check")
    print(f"Items: {result['total_items']}  |  Alignment: {result['alignment_rate_pct']:.0f}%")
    print("=" * 65)
    print(f"Aligned: {result['aligned']}  |  Unaligned: {result['unaligned']}")

    print(f"\nOKR Coverage:")
    for okr, count in result["okr_coverage"].items():
        bar = "#" * min(count, 20)
        indicator = " (NO ITEMS)" if count == 0 else ""
        print(f"  {okr[:35]:<35} {count:>3} items  {bar}{indicator}")

    print(f"\nItem Details:")
    for item in result["items"]:
        status = "OK" if item["is_aligned"] else "!!"
        okrs = ", ".join(item["matched_okrs"]) if item["matched_okrs"] else "NONE"
        print(f"  [{status}] {item['title'][:35]:<35} Why: {item['why_quality']:<8} OKRs: {okrs}")
        for issue in item["why_issues"]:
            print(f"       ! {issue}")

    if result["recommendations"]:
        print(f"\nRecommendations:")
        for i, r in enumerate(result["recommendations"], 1):
            print(f"  {i}. {r}")
    print()


def print_example() -> None:
    example = {
        "okrs": [
            {"id": "OKR-1", "name": "Reduce churn to <5% monthly", "keywords": ["churn", "retention", "activation"]},
            {"id": "OKR-2", "name": "Grow ARR to $10M", "keywords": ["revenue", "ARR", "enterprise", "upsell"]},
            {"id": "OKR-3", "name": "Improve developer experience", "keywords": ["developer", "DX", "API", "documentation"]},
        ],
        "items": [
            {
                "title": "Guided Onboarding Wizard",
                "why": "Our Q2 objective is to reduce churn. 60% of churned users never completed setup.",
                "what": "Add a step-by-step setup wizard for new users.",
                "acceptance_criteria": ["Wizard appears on first login", "Can be skipped", "Progress saved", "Completion confirmation shown"],
                "okr_ref": "OKR-1",
            },
            {
                "title": "Admin Dashboard Polish",
                "why": "Because the customer asked for it.",
                "what": "Clean up the admin dashboard UI.",
                "acceptance_criteria": ["Looks better"],
            },
            {
                "title": "API Rate Limit Docs",
                "why": "Developer support tickets about rate limits increased 40% last quarter, costing 10 hours/week.",
                "what": "Create comprehensive rate limit documentation with examples and troubleshooting guide.",
                "acceptance_criteria": ["Docs cover all endpoints", "Includes code examples", "FAQ section", "Linked from API portal"],
            },
        ],
    }
    print(json.dumps(example, indent=2))


def main():
    parser = argparse.ArgumentParser(description="Check WWAS backlog alignment with OKRs.")
    parser.add_argument("--backlog", type=str, help="Path to backlog JSON file")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--example", action="store_true", help="Print example and exit")
    args = parser.parse_args()

    if args.example:
        print_example()
        return
    if not args.backlog:
        parser.error("--backlog is required")

    data = load_data(args.backlog)
    result = check_alignment(data)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print_report(result)


if __name__ == "__main__":
    main()
