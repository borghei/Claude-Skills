#!/usr/bin/env python3
"""Story Converter - Convert between user stories and job stories.

Takes user stories in "As a / I want / So that" format and converts them
to JTBD "When / I want / So I can" format with quality guidance.

Usage:
    python story_converter.py --stories stories.json
    python story_converter.py --stories stories.json --format json
    python story_converter.py --example
"""

import argparse
import json
import re
import sys


def fail(msg: str) -> None:
    """Print a one-line input error and exit 2."""
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(2)


def load_data(path: str, key: str = "stories") -> dict:
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
    return data


def _article(word: str) -> str:
    # Vowel letters except 'u' ("a user", "an admin") — good enough for role names.
    return "an" if word[:1].lower() in "aeio" else "a"


def _clean_outcome(text: str) -> tuple:
    """Return (outcome clause, is_first_person) with 'so that' / 'I can' prefixes removed."""
    text = re.sub(r"^(so that|so)\s+", "", text.strip().rstrip("."), flags=re.IGNORECASE)
    match = re.match(r"^i\s+(can|could|will)\s+", text, re.IGNORECASE)
    if match:
        return text[match.end():], True
    if re.match(r"^i\s+", text, re.IGNORECASE):
        return text[2:], True
    return text, False


def convert_story(story: dict) -> dict:
    role = str(story.get("role", "")).strip()
    want = re.sub(r"^(to\s+)", "", str(story.get("want", "")).strip().rstrip("."), flags=re.IGNORECASE)
    so_that = str(story.get("so_that", "")).strip()
    title = story.get("title", "Untitled")

    original = f"As {_article(role)} {role}, I want to {want}, so that {so_that.rstrip('.')}."
    outcome, first_person = _clean_outcome(so_that)

    # The situation is the part a converter cannot know: it must come from research.
    # Emit a marked placeholder with a hint instead of inventing one.
    who = role or "user"
    situation = f"[SITUATION: the moment {_article(who)} {who} needs this; hint: {_infer_context(want)}]"
    outcome_clause = f"so I can {outcome}" if first_person else f"so that {outcome}"

    warnings = []
    if not outcome or len(outcome) < 10:
        warnings.append("The outcome is vague or missing. Name the progress the user is trying to make.")
    elif not first_person:
        warnings.append("The outcome describes a system state, not the user's progress. Rewrite it as 'so I can ...'.")
    if role and role.lower() in ("user", "admin", "manager", "customer"):
        warnings.append(f"Role '{role}' is generic. Replace it with the specific situation from research.")
    if re.search(r"\b(button|dropdown|modal|api|click|tap|screen)\b", want, re.IGNORECASE):
        warnings.append("The 'I want' names a UI element or action. Describe the capability, not the control.")

    return {
        "title": title,
        "original_user_story": original,
        "converted_job_story": {"situation": situation, "motivation": want, "outcome": outcome},
        "template": f"When {situation}, I want to {want}, {outcome_clause}.",
        "conversion_notes": ["Replace the [SITUATION] placeholder with an observed trigger before the story enters the backlog."],
        "warnings": warnings,
        "needs_refinement": bool(warnings),
    }


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
    parser = argparse.ArgumentParser(
        description="Convert user stories to job-story drafts. The situation is left as a marked placeholder "
                    "for you to fill from research. Exit 0 converted, 2 bad input.")
    parser.add_argument("--stories", type=str, help="Path to user stories JSON ({'stories': [{title, role, want, so_that}]})")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format (default: text)")
    parser.add_argument("--json", action="store_true", help="Shorthand for --format json")
    parser.add_argument("--example", action="store_true", help="Print an example input file and exit")
    args = parser.parse_args()

    if args.example:
        print_example()
        return
    if not args.stories:
        parser.error("--stories is required (or --example)")

    result = batch_convert(load_data(args.stories, "stories"))
    if args.json or args.format == "json":
        print(json.dumps(result, indent=2))
    else:
        print_report(result)


if __name__ == "__main__":
    main()
