#!/usr/bin/env python3
"""Story Quality Checker - Validate job stories against JTBD and INVEST criteria.

Reads job stories and checks each for format compliance, specificity,
and quality against best practices.

Usage:
    python story_quality_checker.py --stories stories.json
    python story_quality_checker.py --stories stories.json --json
    python story_quality_checker.py --example
"""

import argparse
import json
import re
import sys


VAGUE_SITUATIONS = [
    r"^when i use",
    r"^when i need",
    r"^when i am a",
    r"^when i want",
    r"^when using the",
]

SOLUTION_WORDS = [
    r"\bdropdown\b", r"\bbutton\b", r"\bmodal\b", r"\bpopup\b",
    r"\bcheckbox\b", r"\btextbox\b", r"\bAPI\b", r"\bendpoint\b",
    r"\bdatabase\b", r"\bCSS\b", r"\bReact\b", r"\bcomponent\b",
]

VAGUE_OUTCOMES = [
    r"so i can use it",
    r"so i can be productive",
    r"so i can do my job",
    r"so i can be happy",
    r"so i can feel",
    r"so it works",
]


def load_data(path: str) -> dict:
    with open(path, "r") as f:
        return json.load(f)


def check_story(story: dict) -> dict:
    title = story.get("title", "Untitled")
    situation = story.get("situation", "").strip()
    motivation = story.get("motivation", "").strip()
    outcome = story.get("outcome", "").strip()
    acceptance_criteria = story.get("acceptance_criteria", [])

    checks = []
    score = 100

    # Format: has all three parts
    if not situation:
        checks.append({"check": "has_situation", "passed": False, "detail": "Missing 'When [situation]'"})
        score -= 20
    else:
        checks.append({"check": "has_situation", "passed": True})

    if not motivation:
        checks.append({"check": "has_motivation", "passed": False, "detail": "Missing 'I want to [motivation]'"})
        score -= 20
    else:
        checks.append({"check": "has_motivation", "passed": True})

    if not outcome:
        checks.append({"check": "has_outcome", "passed": False, "detail": "Missing 'So I can [outcome]'"})
        score -= 20
    else:
        checks.append({"check": "has_outcome", "passed": True})

    # Situation quality
    if situation:
        is_vague = any(re.search(p, situation.lower()) for p in VAGUE_SITUATIONS)
        checks.append({
            "check": "specific_situation",
            "passed": not is_vague,
            "detail": "Situation is too vague -- add specific context or trigger" if is_vague else "Situation is specific",
        })
        if is_vague:
            score -= 10

    # Motivation: not solution-prescriptive
    if motivation:
        has_solution = any(re.search(p, motivation, re.IGNORECASE) for p in SOLUTION_WORDS)
        checks.append({
            "check": "solution_agnostic",
            "passed": not has_solution,
            "detail": "Motivation prescribes a solution -- describe the capability instead" if has_solution else "Motivation is solution-agnostic",
        })
        if has_solution:
            score -= 10

    # Outcome quality
    if outcome:
        is_vague = any(re.search(p, outcome.lower()) for p in VAGUE_OUTCOMES)
        checks.append({
            "check": "measurable_outcome",
            "passed": not is_vague,
            "detail": "Outcome is too vague -- add observable/measurable criteria" if is_vague else "Outcome is measurable",
        })
        if is_vague:
            score -= 10

    # Acceptance criteria
    ac_count = len(acceptance_criteria)
    has_enough_ac = ac_count >= 4
    checks.append({
        "check": "acceptance_criteria_count",
        "passed": has_enough_ac,
        "detail": f"{ac_count} criteria (minimum: 4)" if not has_enough_ac else f"{ac_count} criteria",
    })
    if not has_enough_ac:
        score -= 10

    # AC quality: check for implementation details
    impl_detail_count = 0
    for ac in acceptance_criteria:
        if any(re.search(p, ac, re.IGNORECASE) for p in [r"\bAPI\b", r"\b200\b", r"\brender\b", r"\bunit test\b", r"\bdatabase\b"]):
            impl_detail_count += 1
    if impl_detail_count > 0:
        checks.append({
            "check": "ac_outcome_focused",
            "passed": False,
            "detail": f"{impl_detail_count} criteria reference implementation details -- rewrite as user-observable outcomes",
        })
        score -= 5 * impl_detail_count
    else:
        checks.append({"check": "ac_outcome_focused", "passed": True, "detail": "Criteria are outcome-focused"})

    score = max(0, score)
    if score >= 85:
        rating = "Ready"
    elif score >= 65:
        rating = "Needs Refinement"
    else:
        rating = "Not Ready"

    return {
        "title": title,
        "score": score,
        "rating": rating,
        "checks_passed": sum(1 for c in checks if c["passed"]),
        "checks_total": len(checks),
        "checks": checks,
        "full_story": f"When {situation}, I want to {motivation}, so I can {outcome}." if all([situation, motivation, outcome]) else "Incomplete",
    }


def analyze_stories(data: dict) -> dict:
    stories = data.get("stories", [])
    results = [check_story(s) for s in stories]
    scores = [r["score"] for r in results]
    avg = round(sum(scores) / len(scores), 1) if scores else 0

    ready = sum(1 for r in results if r["rating"] == "Ready")
    needs_work = sum(1 for r in results if r["rating"] == "Needs Refinement")
    not_ready = sum(1 for r in results if r["rating"] == "Not Ready")

    return {
        "total_stories": len(results),
        "average_score": avg,
        "ready": ready,
        "needs_refinement": needs_work,
        "not_ready": not_ready,
        "stories": results,
    }


def print_report(result: dict) -> None:
    print(f"\nJob Story Quality Check")
    print(f"Stories: {result['total_stories']}  |  Avg Score: {result['average_score']:.0f}/100")
    print("=" * 65)
    print(f"Ready: {result['ready']}  |  Needs Refinement: {result['needs_refinement']}  |  Not Ready: {result['not_ready']}")

    for s in sorted(result["stories"], key=lambda x: x["score"]):
        print(f"\n  [{s['rating']}] {s['title']} (Score: {s['score']})")
        if s["full_story"] != "Incomplete":
            print(f"    {s['full_story'][:100]}")
        for c in s["checks"]:
            if not c["passed"]:
                print(f"    ! {c.get('detail', c['check'])}")
    print()


def print_example() -> None:
    example = {
        "stories": [
            {
                "title": "Weekly Budget Check",
                "situation": "I am preparing my weekly budget on Sunday evening",
                "motivation": "see how much I have spent so far this month by category",
                "outcome": "decide where to cut back before the month ends",
                "acceptance_criteria": [
                    "Spending view shows current month transactions grouped by category",
                    "Each category displays total spent and remaining budget",
                    "Categories exceeding budget are visually distinguished",
                    "Tapping a category shows individual transactions",
                    "View loads within 2 seconds on mobile",
                    "Date range is fixed to current calendar month",
                ],
            },
            {
                "title": "Bad Example Story",
                "situation": "I use the app",
                "motivation": "click the dropdown to select a report",
                "outcome": "be productive",
                "acceptance_criteria": ["API returns 200", "Component renders"],
            },
        ],
    }
    print(json.dumps(example, indent=2))


def main():
    parser = argparse.ArgumentParser(description="Validate job stories against JTBD and INVEST criteria.")
    parser.add_argument("--stories", type=str, help="Path to stories JSON file")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--example", action="store_true", help="Print example and exit")
    args = parser.parse_args()

    if args.example:
        print_example()
        return
    if not args.stories:
        parser.error("--stories is required")

    data = load_data(args.stories)
    result = analyze_stories(data)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print_report(result)


if __name__ == "__main__":
    main()
