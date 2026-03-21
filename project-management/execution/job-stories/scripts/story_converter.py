#!/usr/bin/env python3
"""Story Converter - Convert between user stories and job stories.

Takes user stories in "As a / I want / So that" format and converts them
to JTBD "When / I want / So I can" format with quality guidance.

Usage:
    python story_converter.py --stories stories.json
    python story_converter.py --stories stories.json --json
    python story_converter.py --example
"""

import argparse
import json
import re
import sys


def load_data(path: str) -> dict:
    with open(path, "r") as f:
        return json.load(f)


def convert_story(story: dict) -> dict:
    role = story.get("role", "").strip()
    want = story.get("want", "").strip()
    so_that = story.get("so_that", "").strip()
    title = story.get("title", "Untitled")

    # Original user story
    original = f"As a {role}, I want to {want}, so that {so_that}."

    # Conversion guidance
    situation_hints = []
    if role:
        situation_hints.append(f"Think about when a {role} would need this capability. What is the specific context or trigger?")

    # Generate a template conversion
    situation_suggestion = f"[When a {role} is {_infer_context(want)}]"
    motivation_suggestion = want
    outcome_suggestion = so_that

    # Quality warnings
    warnings = []
    if not so_that or len(so_that) < 10:
        warnings.append("The 'so that' is vague or missing. Strengthen the outcome with measurable criteria.")
    if role and role.lower() in ("user", "admin", "manager"):
        warnings.append(f"Role '{role}' is generic. The job story should describe the specific situation instead.")
    if any(word in want.lower() for word in ["button", "dropdown", "modal", "api"]):
        warnings.append("The 'I want' contains solution details. Rewrite to describe the capability, not the UI element.")

    converted = {
        "title": title,
        "original_user_story": original,
        "converted_job_story": {
            "situation": situation_suggestion,
            "motivation": motivation_suggestion,
            "outcome": outcome_suggestion,
        },
        "template": f"When {situation_suggestion}, I want to {motivation_suggestion}, so I can {outcome_suggestion}.",
        "conversion_notes": situation_hints,
        "warnings": warnings,
        "needs_refinement": len(warnings) > 0,
    }
    return converted


def _infer_context(want: str) -> str:
    """Infer a situational context from the want statement."""
    action_patterns = {
        r"see|view|check|monitor": "reviewing information",
        r"create|add|make": "creating something new",
        r"edit|update|change|modify": "updating existing data",
        r"delete|remove": "cleaning up or removing items",
        r"export|download|share": "sharing or extracting data",
        r"search|find|filter": "looking for specific information",
        r"configure|set up|customize": "setting up or customizing the system",
    }
    for pattern, context in action_patterns.items():
        if re.search(pattern, want.lower()):
            return context
    return "performing a specific task"


def batch_convert(data: dict) -> dict:
    stories = data.get("stories", [])
    results = [convert_story(s) for s in stories]

    needs_refinement = sum(1 for r in results if r["needs_refinement"])

    return {
        "total_stories": len(results),
        "converted": len(results),
        "needs_refinement": needs_refinement,
        "stories": results,
    }


def print_report(result: dict) -> None:
    print(f"\nStory Conversion: User Stories -> Job Stories")
    print(f"Converted: {result['converted']}  |  Needs Refinement: {result['needs_refinement']}")
    print("=" * 65)

    for s in result["stories"]:
        print(f"\n  {s['title']}")
        print(f"  BEFORE: {s['original_user_story']}")
        print(f"  AFTER:  {s['template']}")
        if s["warnings"]:
            for w in s["warnings"]:
                print(f"    ! {w}")
        if s["conversion_notes"]:
            for n in s["conversion_notes"]:
                print(f"    > {n}")
    print()


def print_example() -> None:
    example = {
        "stories": [
            {
                "title": "Export User Data",
                "role": "admin",
                "want": "export user data as a CSV file",
                "so_that": "I can comply with data subject access requests",
            },
            {
                "title": "View Dashboard",
                "role": "user",
                "want": "see a dashboard with my key metrics",
                "so_that": "I can track my progress",
            },
            {
                "title": "Click Button",
                "role": "manager",
                "want": "click the approve button on the modal",
                "so_that": "the request is processed",
            },
        ],
    }
    print(json.dumps(example, indent=2))


def main():
    parser = argparse.ArgumentParser(description="Convert user stories to job stories.")
    parser.add_argument("--stories", type=str, help="Path to user stories JSON file")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--example", action="store_true", help="Print example and exit")
    args = parser.parse_args()

    if args.example:
        print_example()
        return
    if not args.stories:
        parser.error("--stories is required")

    data = load_data(args.stories)
    result = batch_convert(data)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print_report(result)


if __name__ == "__main__":
    main()
