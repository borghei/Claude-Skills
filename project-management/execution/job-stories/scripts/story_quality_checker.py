#!/usr/bin/env python3
"""Story Quality Checker - Validate job stories against JTBD and INVEST criteria.

Reads job stories and checks each for format compliance, specificity,
and quality against best practices.

Usage:
    python story_quality_checker.py --stories stories.json
    python story_quality_checker.py --stories stories.json --format json
    python story_quality_checker.py --example
"""

import argparse
import json
import re
import sys


# Patterns match the clause body; the "When" / "so I can" prefix is stripped first,
# because the input fields hold only the body ("I use the app", "be productive").
VAGUE_SITUATIONS = [
    r"^i use\b",
    r"^i need\b",
    r"^i am an? \w+$",
    r"^i want\b",
    r"^using the\b",
    r"^i open the (app|tool|product)\b",
]

SOLUTION_WORDS = [
    r"\bdropdown\b", r"\bbutton\b", r"\bmodal\b", r"\bpopup\b",
    r"\bcheckbox\b", r"\btextbox\b", r"\bAPI\b", r"\bendpoint\b",
    r"\bdatabase\b", r"\bCSS\b", r"\bReact\b", r"\bcomponent\b",
]

VAGUE_OUTCOMES = [
    r"^use it$",
    r"^be (more )?productive$",
    r"^do my job$",
    r"^be happy$",
    r"^feel\b",
    r"^it works$",
    r"^save time$",
]


def _body(text: str, prefix: str) -> str:
    """Lowercase clause with a leading prefix (e.g. 'when', 'so i can') and final period removed."""
    text = text.strip().rstrip(".").lower()
    return re.sub(rf"^{prefix}\s+", "", text)


def fail(msg: str) -> None:
    """Print a one-line input error and exit 2."""
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(2)


def load_data(path: str, key: str) -> dict:
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except OSError as exc:
        fail(f"cannot read {path}: {exc.strerror or exc}")
    except ValueError as exc:
        fail(f"{path} is not valid JSON: {exc}")
    items = data.get(key) if isinstance(data, dict) else None
    if not isinstance(items, list) or not items or not all(isinstance(i, dict) for i in items):
        fail(f"{path} must be a JSON object with a non-empty '{key}' list of objects")
    for item in items:
        for field in ("acceptance_criteria", "dependencies"):
            if not isinstance(item.get(field, []), list):
                fail(f"{path}: '{field}' in '{item.get('title', 'Untitled')}' must be a list")
    return data


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
        is_vague = any(re.search(p, _body(situation, "when")) for p in VAGUE_SITUATIONS)
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
        is_vague = any(re.search(p, _body(outcome, r"so (that )?(i can )?")) for p in VAGUE_OUTCOMES)
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
        if any(re.search(p, ac, re.IGNORECASE) for p in [r"\bAPI\b", r"\b200\b", r"\brenders?\b", r"\bcomponent\b", r"\bendpoint\b", r"\bunit test\b", r"\bdatabase\b"]):
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
    parser = argparse.ArgumentParser(
        description="Check job stories for format, specificity and outcome-focused acceptance criteria. Exit 0 all ready, 1 at least one is not, 2 bad input.")
    parser.add_argument("--stories", type=str, help="Path to JSON file: {'stories': [...]} (see --example)")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format (default: text)")
    parser.add_argument("--json", action="store_true", help="Shorthand for --format json")
    parser.add_argument("--example", action="store_true", help="Print an example input file and exit")
    args = parser.parse_args()

    if args.example:
        print_example()
        return 0
    if not args.stories:
        parser.error("--stories is required (or --example)")

    result = analyze_stories(load_data(args.stories, "stories"))
    if args.json or args.format == "json":
        print(json.dumps(result, indent=2))
    else:
        print_report(result)
    return 0 if result["ready"] == result["total_stories"] else 1


if __name__ == "__main__":
    sys.exit(main())
