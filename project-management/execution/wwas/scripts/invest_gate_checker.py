#!/usr/bin/env python3
"""INVEST Gate Checker - Validate WWAS items against INVEST quality gates.

Reads WWAS backlog items and checks each against the 6 INVEST criteria
with actionable fix suggestions for failing items.

Usage:
    python invest_gate_checker.py --items items.json
    python invest_gate_checker.py --items items.json --json
    python invest_gate_checker.py --example
"""

import argparse
import json
import re
import sys


def load_data(path: str) -> dict:
    with open(path, "r") as f:
        return json.load(f)


def check_invest(item: dict) -> dict:
    title = item.get("title", "Untitled")
    why = item.get("why", "")
    what = item.get("what", "")
    acceptance_criteria = item.get("acceptance_criteria", [])
    dependencies = item.get("dependencies", [])
    story_points = item.get("story_points")

    gates = {}

    # Independent
    blocked = len(dependencies) > 0
    gates["independent"] = {
        "passed": not blocked,
        "detail": f"Blocked by: {', '.join(dependencies)}" if blocked else "No blocking dependencies",
        "action": "Reorder backlog or combine dependent items" if blocked else None,
    }

    # Negotiable
    prescriptive_patterns = [r"\bmust use\b", r"\bimplement with\b", r"\buse \w+ framework\b", r"\brequires?\s+\w+\s+library\b"]
    is_prescriptive = any(re.search(p, what, re.IGNORECASE) for p in prescriptive_patterns)
    gates["negotiable"] = {
        "passed": not is_prescriptive,
        "detail": "What prescribes implementation approach" if is_prescriptive else "Implementation approach is open",
        "action": "Remove technology/implementation specifics from What -- describe the outcome, not the solution" if is_prescriptive else None,
    }

    # Valuable
    has_value = len(why) >= 30 and not any(re.search(p, why, re.IGNORECASE) for p in [r"customer asked", r"best practice", r"we need this"])
    gates["valuable"] = {
        "passed": has_value,
        "detail": "Why connects to business objective" if has_value else "Why is missing or lacks strategic context",
        "action": "Rewrite Why to reference a specific OKR, metric, or customer evidence" if not has_value else None,
    }

    # Estimable
    enough_context = len(what) >= 50 and len(acceptance_criteria) >= 3
    gates["estimable"] = {
        "passed": enough_context,
        "detail": f"What: {len(what)} chars, {len(acceptance_criteria)} AC" if enough_context else "Insufficient detail for estimation",
        "action": "Add more context to What and provide at least 4 acceptance criteria" if not enough_context else None,
    }

    # Small
    if story_points is not None:
        is_small = story_points <= 8
        size_detail = f"Story points: {story_points}"
    else:
        # Heuristic: many AC = potentially large
        is_small = len(acceptance_criteria) <= 8 and len(what) < 500
        size_detail = f"{len(acceptance_criteria)} AC, {len(what)} chars description"
    gates["small"] = {
        "passed": is_small,
        "detail": size_detail if is_small else f"Likely too large: {size_detail}",
        "action": "Split by user segment, scenario, or outcome to fit one sprint" if not is_small else None,
    }

    # Testable
    observable_patterns = [r"\bshows\b", r"\bdisplays\b", r"\benables\b", r"\bprevents\b", r"\bnotifies\b", r"\bwithin\b", r"\bwhen\b", r"\bif\b", r"\bless than\b", r"\bmore than\b"]
    testable_count = sum(1 for ac in acceptance_criteria if any(re.search(p, ac, re.IGNORECASE) for p in observable_patterns))
    is_testable = testable_count >= 2 or len(acceptance_criteria) >= 4
    gates["testable"] = {
        "passed": is_testable,
        "detail": f"{testable_count}/{len(acceptance_criteria)} criteria clearly testable" if acceptance_criteria else "No acceptance criteria",
        "action": "Rewrite criteria as observable outcomes: '[Thing] [does] [expected behavior] [under condition]'" if not is_testable else None,
    }

    passed = sum(1 for g in gates.values() if g["passed"])
    total = len(gates)

    if passed == 6:
        verdict = "PASS - Sprint Ready"
    elif passed >= 4:
        verdict = "CONDITIONAL - Fix before sprint"
    else:
        verdict = "FAIL - Needs refinement"

    actions = [{"gate": k, "action": v["action"]} for k, v in gates.items() if v.get("action")]

    return {
        "title": title,
        "passed": passed,
        "total": total,
        "verdict": verdict,
        "gates": gates,
        "required_actions": actions,
    }


def analyze_items(data: dict) -> dict:
    items = data.get("items", [])
    results = [check_invest(item) for item in items]

    pass_count = sum(1 for r in results if "PASS" in r["verdict"])
    conditional = sum(1 for r in results if "CONDITIONAL" in r["verdict"])
    fail_count = sum(1 for r in results if "FAIL" in r["verdict"])

    # Most common failing gates
    gate_fails = {}
    for r in results:
        for gate, info in r["gates"].items():
            if not info["passed"]:
                gate_fails[gate] = gate_fails.get(gate, 0) + 1

    return {
        "total_items": len(results),
        "passed": pass_count,
        "conditional": conditional,
        "failed": fail_count,
        "common_failures": sorted(gate_fails.items(), key=lambda x: x[1], reverse=True),
        "items": results,
    }


def print_report(result: dict) -> None:
    print(f"\nINVEST Gate Check (WWAS)")
    print(f"Items: {result['total_items']}")
    print("=" * 60)
    print(f"Pass: {result['passed']}  |  Conditional: {result['conditional']}  |  Fail: {result['failed']}")

    if result["common_failures"]:
        print(f"\nMost Common Failures:")
        for gate, count in result["common_failures"]:
            print(f"  {gate.upper()}: {count} item(s)")

    for item in result["items"]:
        print(f"\n  [{item['verdict']}] {item['title']} ({item['passed']}/{item['total']})")
        for gate, info in item["gates"].items():
            status = "PASS" if info["passed"] else "FAIL"
            print(f"    [{status}] {gate.upper()}: {info['detail']}")
        if item["required_actions"]:
            for action in item["required_actions"]:
                print(f"    -> {action['gate'].upper()}: {action['action']}")
    print()


def print_example() -> None:
    example = {
        "items": [
            {
                "title": "Guided Onboarding Wizard",
                "why": "Our Q2 North Star is reducing time-to-value from 14 days to 3 days. 60% of churned users never completed setup.",
                "what": "Add a step-by-step setup wizard for new users covering data source connection, teammate invite, and first dashboard creation.",
                "acceptance_criteria": [
                    "Wizard appears on first login",
                    "Users can skip and resume later",
                    "Milestones completable in any order",
                    "Completion shows next steps",
                    "If no data source available, shows sample data option",
                ],
                "dependencies": [],
                "story_points": 5,
            },
            {
                "title": "Rebuild Everything",
                "why": "We need this.",
                "what": "Rebuild. Must use React 19 and implement with GraphQL.",
                "acceptance_criteria": ["It works"],
                "dependencies": ["API v3", "DB migration"],
                "story_points": 40,
            },
        ],
    }
    print(json.dumps(example, indent=2))


def main():
    parser = argparse.ArgumentParser(description="Check WWAS items against INVEST gates.")
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
