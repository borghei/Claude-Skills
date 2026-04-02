#!/usr/bin/env python3
"""Generate Playwright test code from user story descriptions.

Parses structured user story input (JSON or plain text) and generates
Playwright spec files with Page Object references, proper assertions,
and test isolation following the 10 golden rules.

Usage:
    python test_generator.py --story "User can log in with email and password" --page LoginPage --route /login
    python test_generator.py --stories stories.json --output ./tests/e2e/generated/
    python test_generator.py --story "User can add item to cart" --page CartPage --route /cart --json
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path


# Maps common actions to Playwright assertion patterns
ACTION_PATTERNS = {
    "log in": {"action": "fill + click", "assertions": ["toHaveURL", "toBeVisible"]},
    "sign up": {"action": "fill + click", "assertions": ["toHaveURL", "toBeVisible"]},
    "register": {"action": "fill + click", "assertions": ["toHaveURL", "toBeVisible"]},
    "submit": {"action": "click", "assertions": ["toBeVisible", "toHaveText"]},
    "navigate": {"action": "goto + click", "assertions": ["toHaveURL"]},
    "search": {"action": "fill + click", "assertions": ["toBeVisible", "toHaveCount"]},
    "delete": {"action": "click + confirm", "assertions": ["not.toBeVisible", "toHaveCount"]},
    "edit": {"action": "fill + click", "assertions": ["toHaveText", "toBeVisible"]},
    "add": {"action": "click + fill", "assertions": ["toBeVisible", "toHaveCount"]},
    "remove": {"action": "click", "assertions": ["not.toBeVisible"]},
    "upload": {"action": "setInputFiles", "assertions": ["toBeVisible"]},
    "download": {"action": "click + waitForDownload", "assertions": ["toBeTruthy"]},
    "filter": {"action": "click + select", "assertions": ["toHaveCount"]},
    "sort": {"action": "click", "assertions": ["toHaveText"]},
}

VALIDATION_SCENARIOS = [
    {"name": "empty required field", "approach": "leave field empty, submit", "assertion": "error message visible"},
    {"name": "invalid format", "approach": "enter malformed data", "assertion": "validation error shown"},
    {"name": "boundary value", "approach": "enter min/max boundary", "assertion": "accepted or rejected correctly"},
    {"name": "duplicate entry", "approach": "submit same data twice", "assertion": "duplicate error or idempotent success"},
]


def to_kebab_case(text):
    """Convert text to kebab-case for file names."""
    text = re.sub(r"[^a-zA-Z0-9\s]", "", text)
    return re.sub(r"\s+", "-", text.strip().lower())


def to_camel_case(text):
    """Convert text to camelCase."""
    words = re.sub(r"[^a-zA-Z0-9\s]", " ", text).strip().split()
    if not words:
        return "element"
    return words[0].lower() + "".join(w.capitalize() for w in words[1:])


def detect_action(story):
    """Detect the primary action from a user story."""
    story_lower = story.lower()
    for action_key, pattern in ACTION_PATTERNS.items():
        if action_key in story_lower:
            return action_key, pattern
    return "interact", {"action": "click", "assertions": ["toBeVisible"]}


def extract_nouns(story):
    """Extract likely UI element nouns from a story."""
    # Remove common stop words and extract meaningful nouns
    stop_words = {
        "user", "can", "should", "be", "able", "to", "the", "a", "an", "with",
        "and", "or", "on", "in", "for", "from", "by", "as", "is", "are", "was",
        "when", "then", "given", "that", "their", "my", "i", "they",
    }
    words = re.findall(r"[a-zA-Z]+", story.lower())
    nouns = [w for w in words if w not in stop_words and len(w) > 2]
    return nouns


def generate_test_scenarios(story, action_key, pattern):
    """Generate test scenarios from a user story."""
    scenarios = []

    # Happy path
    scenarios.append({
        "name": f"successfully {action_key}s",
        "type": "happy_path",
        "description": f"Verify that the user can {action_key} under normal conditions",
        "assertions": pattern["assertions"],
    })

    # Validation scenarios
    if pattern["action"] in ("fill + click", "click + fill"):
        for vs in VALIDATION_SCENARIOS[:3]:  # Top 3 validation scenarios
            scenarios.append({
                "name": f"shows error for {vs['name']}",
                "type": "validation",
                "description": vs["approach"],
                "assertions": ["toBeVisible"],  # Error message visible
            })

    # Negative path
    scenarios.append({
        "name": f"handles {action_key} failure gracefully",
        "type": "negative",
        "description": f"Verify error handling when {action_key} fails",
        "assertions": ["toBeVisible"],  # Error state visible
    })

    return scenarios


def generate_spec_code(story, page_name, route, scenarios):
    """Generate TypeScript spec file content."""
    describe_name = story.rstrip(".")
    page_var = to_camel_case(page_name)
    page_file = re.sub(r"(?<!^)(?=[A-Z])", "-", page_name).lower()
    if not page_file.endswith("-page"):
        page_file += ".page"

    lines = []
    lines.append(f"import {{ test, expect }} from '@playwright/test';")
    lines.append(f"import {{ {page_name} }} from '../../pages/{page_file}';")
    lines.append("")
    lines.append(f"test.describe('{describe_name}', () => {{")
    lines.append(f"  let {page_var}: {page_name};")
    lines.append("")
    lines.append(f"  test.beforeEach(async ({{ page }}) => {{")
    lines.append(f"    {page_var} = new {page_name}(page);")
    lines.append(f"    await {page_var}.goto();")
    lines.append(f"  }});")

    for scenario in scenarios:
        lines.append("")
        lines.append(f"  test('{scenario['name']}', async ({{ page }}) => {{")
        lines.append(f"    // TODO: Implement - {scenario['description']}")

        if scenario["type"] == "happy_path":
            lines.append(f"    // Arrange: Set up test data")
            lines.append(f"    // Act: Perform the {story.lower().split('can')[-1].strip() if 'can' in story.lower() else 'action'}")
            lines.append(f"    // Assert: Verify expected outcome")
            for assertion in scenario["assertions"]:
                if assertion == "toHaveURL":
                    lines.append(f"    await expect(page).toHaveURL(/\\/{route.strip('/')}/);")
                else:
                    lines.append(f"    // await expect(locator).{assertion}();")
        elif scenario["type"] == "validation":
            lines.append(f"    // Act: {scenario['description']}")
            lines.append(f"    // Assert: Error message is displayed")
            lines.append(f"    // await expect({page_var}.errorMessage).toBeVisible();")
        else:
            lines.append(f"    // Arrange: Set up failure condition")
            lines.append(f"    // Act: Attempt the action")
            lines.append(f"    // Assert: Error state is shown to user")
            lines.append(f"    // await expect({page_var}.errorMessage).toBeVisible();")

        lines.append(f"  }});")

    lines.append(f"}});")
    lines.append("")

    return "\n".join(lines)


def process_story(story, page_name, route):
    """Process a single user story into test scenarios and code."""
    action_key, pattern = detect_action(story)
    scenarios = generate_test_scenarios(story, action_key, pattern)
    code = generate_spec_code(story, page_name, route, scenarios)
    nouns = extract_nouns(story)

    return {
        "story": story,
        "detected_action": action_key,
        "page_name": page_name,
        "route": route,
        "scenario_count": len(scenarios),
        "scenarios": scenarios,
        "suggested_elements": nouns,
        "code": code,
    }


def load_stories_file(path):
    """Load stories from a JSON file.

    Expected format:
    [
        {"story": "User can log in", "page": "LoginPage", "route": "/login"},
        ...
    ]
    """
    with open(path, "r") as f:
        return json.load(f)


def format_human(results):
    """Format results for human-readable output."""
    output = []
    output.append("=" * 70)
    output.append("PLAYWRIGHT TEST GENERATOR")
    output.append("=" * 70)

    for result in results:
        output.append("")
        output.append(f"Story: {result['story']}")
        output.append(f"Action: {result['detected_action']}")
        output.append(f"Page: {result['page_name']} ({result['route']})")
        output.append(f"Scenarios: {result['scenario_count']}")
        output.append("")

        for s in result["scenarios"]:
            marker = {"happy_path": "+", "validation": "~", "negative": "x"}
            output.append(f"  [{marker.get(s['type'], '?')}] {s['name']}")

        output.append("")
        output.append("-" * 70)
        output.append("GENERATED CODE")
        output.append("-" * 70)
        output.append(result["code"])

        if result["suggested_elements"]:
            output.append("Suggested Page Object elements: " + ", ".join(result["suggested_elements"][:8]))
        output.append("")

    return "\n".join(output)


def main():
    parser = argparse.ArgumentParser(
        description="Generate Playwright test code from user story descriptions.",
        epilog="Example: python test_generator.py --story 'User can log in' --page LoginPage --route /login",
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--story", help="Single user story text")
    source.add_argument("--stories", help="Path to JSON file with multiple stories")
    parser.add_argument("--page", help="Page Object class name (required with --story)")
    parser.add_argument("--route", default="/", help="Page route (default: /)")
    parser.add_argument("--output", help="Output directory for generated spec files")
    parser.add_argument("--json", action="store_true", dest="json_output", help="Output as JSON")

    args = parser.parse_args()

    results = []

    if args.story:
        if not args.page:
            print("Error: --page is required when using --story", file=sys.stderr)
            sys.exit(1)
        results.append(process_story(args.story, args.page, args.route))
    else:
        stories_path = Path(args.stories)
        if not stories_path.exists():
            print(f"Error: Stories file '{args.stories}' not found.", file=sys.stderr)
            sys.exit(1)
        stories = load_stories_file(stories_path)
        for s in stories:
            results.append(process_story(s["story"], s["page"], s.get("route", "/")))

    # Write output files if --output specified
    if args.output:
        out_dir = Path(args.output)
        out_dir.mkdir(parents=True, exist_ok=True)
        for result in results:
            filename = to_kebab_case(result["story"])[:50] + ".spec.ts"
            filepath = out_dir / filename
            filepath.write_text(result["code"], encoding="utf-8")
            print(f"Written: {filepath}", file=sys.stderr)

    if args.json_output:
        print(json.dumps(results, indent=2))
    else:
        print(format_human(results))


if __name__ == "__main__":
    main()
