#!/usr/bin/env python3
"""INVEST Validator - Validate backlog items against INVEST criteria.

Reads stories/items and evaluates each against the 6 INVEST criteria
(Independent, Negotiable, Valuable, Estimable, Small, Testable).

Usage:
    python invest_validator.py --items items.json
    python invest_validator.py --items items.json --json
    python invest_validator.py --example
"""

import argparse
import json
import re
import sys


def load_data(path: str) -> dict:
    with open(path, "r") as f:
        return json.load(f)


def validate_invest(item: dict) -> dict:
    title = item.get("title", "Untitled")
    description = item.get("description", "")
    acceptance_criteria = item.get("acceptance_criteria", [])
    dependencies = item.get("dependencies", [])
    story_points = item.get("story_points")
    sprint_fit = item.get("fits_in_sprint", None)

    checks = {}

    # Independent
    has_deps = len(dependencies) > 0
    checks["independent"] = {
        "passed": not has_deps,
        "detail": f"Has {len(dependencies)} dependency(ies): {', '.join(dependencies[:3])}" if has_deps else "No blocking dependencies",
        "fix": "Reorder backlog or combine dependent items" if has_deps else None,
    }

    # Negotiable
    impl_words = [r"\buse React\b", r"\buse API\b", r"\buse SQL\b", r"\bimplement with\b", r"\bmust use\b", r"\brequires \w+ library\b"]
    is_prescriptive = any(re.search(p, description, re.IGNORECASE) for p in impl_words)
    checks["negotiable"] = {
        "passed": not is_prescriptive,
        "detail": "Description prescribes implementation approach" if is_prescriptive else "Implementation approach is negotiable",
        "fix": "Remove implementation details from description -- describe the What, not the How" if is_prescriptive else None,
    }

    # Valuable
    has_outcome = bool(item.get("outcome") or item.get("so_that") or item.get("why"))
    value_words = [r"\breduce\b", r"\bincrease\b", r"\bimprove\b", r"\benable\b", r"\bsave\b", r"\beliminate\b"]
    has_value_language = any(re.search(p, description, re.IGNORECASE) for p in value_words)
    checks["valuable"] = {
        "passed": has_outcome or has_value_language,
        "detail": "Clear value proposition" if (has_outcome or has_value_language) else "No clear user or business value stated",
        "fix": "Add a Why or outcome statement connecting to user benefit or business objective" if not (has_outcome or has_value_language) else None,
    }

    # Estimable
    desc_length = len(description)
    has_ac = len(acceptance_criteria) >= 2
    checks["estimable"] = {
        "passed": desc_length >= 50 and has_ac,
        "detail": f"Description: {desc_length} chars, {len(acceptance_criteria)} AC" if desc_length >= 50 and has_ac else "Insufficient detail for estimation",
        "fix": "Add more context to description and at least 4 acceptance criteria" if not (desc_length >= 50 and has_ac) else None,
    }

    # Small
    if sprint_fit is not None:
        is_small = sprint_fit
    elif story_points is not None:
        is_small = story_points <= 8
    else:
        word_count = len(description.split())
        is_small = word_count < 200 and len(acceptance_criteria) <= 10
    checks["small"] = {
        "passed": is_small,
        "detail": f"Story points: {story_points}" if story_points else ("Fits in sprint" if is_small else "May be too large for one sprint"),
        "fix": "Split by user segment, scenario, or outcome to fit in one sprint" if not is_small else None,
    }

    # Testable
    testable_ac = sum(1 for ac in acceptance_criteria if any(re.search(p, ac.lower()) for p in [r"\bshows\b", r"\bdisplays\b", r"\benables\b", r"\bprevents\b", r"\bwithin\b", r"\bwhen\b", r"\bif\b"]))
    has_testable_ac = testable_ac >= 2 or len(acceptance_criteria) >= 4
    checks["testable"] = {
        "passed": has_testable_ac,
        "detail": f"{testable_ac}/{len(acceptance_criteria)} criteria are clearly testable" if acceptance_criteria else "No acceptance criteria",
        "fix": "Rewrite criteria as observable outcomes: '[Thing] [does] [expected behavior] [under condition]'" if not has_testable_ac else None,
    }

    passed = sum(1 for c in checks.values() if c["passed"])
    total = len(checks)
    score = round(passed / total * 100)

    if passed == 6:
        rating = "Sprint Ready"
    elif passed >= 4:
        rating = "Needs Refinement"
    else:
        rating = "Not Ready"

    fixes = [{"criterion": k, "action": v["fix"]} for k, v in checks.items() if v.get("fix")]

    return {
        "title": title,
        "score": score,
        "rating": rating,
        "passed": passed,
        "total": total,
        "checks": checks,
        "fixes": fixes,
    }


def analyze_items(data: dict) -> dict:
    items = data.get("items", [])
    results = [validate_invest(item) for item in items]

    ready = sum(1 for r in results if r["rating"] == "Sprint Ready")
    needs_work = sum(1 for r in results if r["rating"] == "Needs Refinement")
    not_ready = sum(1 for r in results if r["rating"] == "Not Ready")

    return {
        "total_items": len(results),
        "sprint_ready": ready,
        "needs_refinement": needs_work,
        "not_ready": not_ready,
        "items": results,
    }


def print_report(result: dict) -> None:
    print(f"\nINVEST Validation")
    print(f"Items: {result['total_items']}")
    print("=" * 60)
    print(f"Sprint Ready: {result['sprint_ready']}  |  Needs Refinement: {result['needs_refinement']}  |  Not Ready: {result['not_ready']}")

    for item in result["items"]:
        print(f"\n  [{item['rating']}] {item['title']} ({item['passed']}/{item['total']} INVEST)")
        for criterion, check in item["checks"].items():
            status = "PASS" if check["passed"] else "FAIL"
            print(f"    [{status}] {criterion.upper()}: {check['detail']}")
        if item["fixes"]:
            print(f"    Fixes needed:")
            for fix in item["fixes"]:
                print(f"      - {fix['criterion'].upper()}: {fix['action']}")
    print()


def print_example() -> None:
    example = {
        "items": [
            {
                "title": "Weekly Budget Summary",
                "description": "When preparing my weekly budget, I want to see spending by category so I can adjust before overspending. The view should group transactions and highlight over-budget categories.",
                "outcome": "Reduce time spent on budget review from 30 minutes to 5 minutes",
                "acceptance_criteria": [
                    "Shows current month transactions grouped by category",
                    "Displays total spent and remaining budget per category",
                    "Over-budget categories are visually highlighted",
                    "Tapping a category shows individual transactions",
                    "Loads within 2 seconds on mobile",
                ],
                "dependencies": [],
                "story_points": 5,
            },
            {
                "title": "Complete Platform Redesign",
                "description": "Redesign the entire platform. Use React and implement with a new API.",
                "acceptance_criteria": ["It works"],
                "dependencies": ["Database migration", "API v2 release"],
                "story_points": 40,
            },
        ],
    }
    print(json.dumps(example, indent=2))


def main():
    parser = argparse.ArgumentParser(description="Validate items against INVEST criteria.")
    parser.add_argument("--items", type=str, help="Path to items JSON file")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--example", action="store_true", help="Print example and exit")
    args = parser.parse_args()

    if args.example:
        print_example()
        return
    if not args.items:
        parser.error("--items is required")

    data = load_data(args.items)
    result = analyze_items(data)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print_report(result)


if __name__ == "__main__":
    main()
