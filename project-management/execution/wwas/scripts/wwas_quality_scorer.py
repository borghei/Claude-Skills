#!/usr/bin/env python3
"""WWAS Quality Scorer - Score WWAS backlog items for completeness and quality.

Reads WWAS items and evaluates the quality of Why, What, and Acceptance
Criteria sections against best practices.

Usage:
    python wwas_quality_scorer.py --items items.json
    python wwas_quality_scorer.py --items items.json --json
    python wwas_quality_scorer.py --example
"""

import argparse
import json
import re
import sys


WEAK_WHY_PATTERNS = [
    r"customer asked",
    r"best practice",
    r"need this for",
    r"we need",
    r"requirement",
    r"it\'s important",
    r"because we should",
]

IMPL_DETAIL_PATTERNS = [
    r"\bAPI\b", r"\b200\b", r"\bJSON\b", r"\brender\b",
    r"\bunit test\b", r"\bdatabase\b", r"\bSQL\b", r"\bCSS\b",
    r"\bcomponent\b", r"\bReact\b", r"\bendpoint\b",
]


def load_data(path: str) -> dict:
    with open(path, "r") as f:
        return json.load(f)


def score_item(item: dict) -> dict:
    title = item.get("title", "Untitled")
    why = item.get("why", "").strip()
    what = item.get("what", "").strip()
    acceptance_criteria = item.get("acceptance_criteria", [])
    design_link = item.get("design_link", "")

    score = 0
    max_score = 100
    checks = {}

    # WHY quality (35 points)
    why_score = 0
    why_issues = []
    if not why:
        why_issues.append("Why is missing entirely")
    elif len(why) < 30:
        why_score = 5
        why_issues.append("Why is too brief -- add strategic context")
    else:
        why_score = 10
        # Check for metric reference
        if re.search(r'\d+%|\$\d|#\d|\d+[xX]', why):
            why_score += 10  # Has quantitative reference
        else:
            why_issues.append("Why lacks quantitative metrics (e.g., '40% increase', '$500K pipeline')")
            why_score += 5

        # Check for weak patterns
        if any(re.search(p, why, re.IGNORECASE) for p in WEAK_WHY_PATTERNS):
            why_issues.append("Why uses generic rationale -- connect to a specific business objective")
            why_score = max(5, why_score - 5)
        else:
            why_score += 5

        # Check for OKR/objective reference
        if re.search(r'Q[1-4]|OKR|objective|target|goal|north star', why, re.IGNORECASE):
            why_score += 10
        else:
            why_issues.append("Why does not reference a specific OKR or business objective")
            why_score += 5

    checks["why"] = {"score": min(35, why_score), "max": 35, "issues": why_issues}
    score += min(35, why_score)

    # WHAT quality (30 points)
    what_score = 0
    what_issues = []
    if not what:
        what_issues.append("What is missing entirely")
    elif len(what) < 50:
        what_score = 5
        what_issues.append("What is too brief -- should be a reminder of the discussion (1-2 paragraphs)")
    elif len(what) > 1000:
        what_score = 15
        what_issues.append("What is too detailed -- this should be a reminder, not a specification. Move details to a design doc.")
    else:
        what_score = 20

    if design_link:
        what_score += 10
    elif what and len(what) > 50:
        what_issues.append("No design link provided (add if design exists)")
        what_score += 5

    checks["what"] = {"score": min(30, what_score), "max": 30, "issues": what_issues}
    score += min(30, what_score)

    # ACCEPTANCE CRITERIA quality (35 points)
    ac_score = 0
    ac_issues = []
    ac_count = len(acceptance_criteria)

    if ac_count == 0:
        ac_issues.append("No acceptance criteria defined")
    elif ac_count < 4:
        ac_score = 10
        ac_issues.append(f"Only {ac_count} criteria (minimum: 4)")
    else:
        ac_score = 15

    # Check for implementation details in AC
    impl_count = 0
    for ac in acceptance_criteria:
        if any(re.search(p, ac, re.IGNORECASE) for p in IMPL_DETAIL_PATTERNS):
            impl_count += 1
    if impl_count > 0:
        ac_issues.append(f"{impl_count} criteria contain implementation details -- rewrite as observable user outcomes")
        ac_score = max(5, ac_score - 5)
    elif ac_count > 0:
        ac_score += 10

    # Check for edge cases
    edge_words = [r"error", r"empty", r"no data", r"invalid", r"fails", r"timeout", r"edge"]
    has_edge_case = any(any(re.search(w, ac, re.IGNORECASE) for w in edge_words) for ac in acceptance_criteria)
    if has_edge_case:
        ac_score += 10
    elif ac_count >= 4:
        ac_issues.append("No edge case or error state criteria -- add at least 1")
        ac_score += 5

    checks["acceptance_criteria"] = {"score": min(35, ac_score), "max": 35, "count": ac_count, "issues": ac_issues}
    score += min(35, ac_score)

    score = max(0, min(100, score))
    if score >= 80:
        rating = "Sprint Ready"
    elif score >= 55:
        rating = "Needs Refinement"
    else:
        rating = "Not Ready"

    all_issues = checks["why"]["issues"] + checks["what"]["issues"] + checks["acceptance_criteria"]["issues"]

    return {
        "title": title,
        "score": score,
        "rating": rating,
        "why_score": checks["why"]["score"],
        "what_score": checks["what"]["score"],
        "ac_score": checks["acceptance_criteria"]["score"],
        "ac_count": ac_count,
        "issues": all_issues,
        "checks": checks,
    }


def analyze_items(data: dict) -> dict:
    items = data.get("items", [])
    results = [score_item(item) for item in items]
    scores = [r["score"] for r in results]
    avg = round(sum(scores) / len(scores), 1) if scores else 0

    ready = sum(1 for r in results if r["rating"] == "Sprint Ready")
    needs_work = sum(1 for r in results if r["rating"] == "Needs Refinement")
    not_ready = sum(1 for r in results if r["rating"] == "Not Ready")

    return {
        "total_items": len(results),
        "average_score": avg,
        "sprint_ready": ready,
        "needs_refinement": needs_work,
        "not_ready": not_ready,
        "items": results,
    }


def print_report(result: dict) -> None:
    print(f"\nWWAS Quality Report")
    print(f"Items: {result['total_items']}  |  Avg Score: {result['average_score']:.0f}/100")
    print("=" * 65)
    print(f"Sprint Ready: {result['sprint_ready']}  |  Needs Refinement: {result['needs_refinement']}  |  Not Ready: {result['not_ready']}")

    print(f"\n  {'Title':<30} {'Score':>6} {'Why':>5} {'What':>5} {'AC':>5} {'Rating'}")
    print(f"  {'-'*30} {'-'*6} {'-'*5} {'-'*5} {'-'*5} {'-'*16}")
    for item in sorted(result["items"], key=lambda x: x["score"]):
        title = item["title"][:28] + ".." if len(item["title"]) > 30 else item["title"]
        print(f"  {title:<30} {item['score']:>5}% {item['why_score']:>4} {item['what_score']:>4} {item['ac_score']:>4} {item['rating']}")
        for issue in item["issues"][:2]:
            print(f"    ! {issue}")
    print()


def print_example() -> None:
    example = {
        "items": [
            {
                "title": "Guided Onboarding Wizard",
                "why": "Our Q2 North Star is reducing time-to-value from 14 days to 3 days. 60% of churned users never completed setup.",
                "what": "Add a step-by-step setup wizard that guides new users through connecting a data source, inviting a teammate, and creating their first dashboard. Skippable and resumable.",
                "design_link": "https://figma.com/file/abc123",
                "acceptance_criteria": [
                    "Wizard appears automatically on first login for new users",
                    "Users can skip at any step and return from help menu",
                    "Each milestone completable independently in any order",
                    "Completion confirmation with suggested next steps",
                    "Does not appear for existing users who completed setup",
                    "Functional on desktop and mobile browsers",
                ],
            },
            {
                "title": "Fix UI Bug",
                "why": "Customer asked for it.",
                "what": "Fix the button.",
                "acceptance_criteria": ["API returns 200"],
            },
        ],
    }
    print(json.dumps(example, indent=2))


def main():
    parser = argparse.ArgumentParser(description="Score WWAS backlog item quality.")
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
