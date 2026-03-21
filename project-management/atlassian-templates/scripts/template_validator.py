#!/usr/bin/env python3
"""Template Validator - Validate templates against quality standards.

Reads a template and checks it against quality criteria including
structure, instructions, completeness, and maintainability.

Usage:
    python template_validator.py --template template.json
    python template_validator.py --template template.json --json
    python template_validator.py --example
"""

import argparse
import json
import sys
from datetime import datetime


QUALITY_CHECKS = [
    {"id": "name", "weight": 10, "description": "Template has a descriptive name (>5 chars)"},
    {"id": "owner", "weight": 10, "description": "Template has a designated owner"},
    {"id": "description", "weight": 10, "description": "Template has a usage description"},
    {"id": "sections", "weight": 15, "description": "Template has 3+ structured sections"},
    {"id": "instructions", "weight": 15, "description": "Sections include inline instructions or placeholders"},
    {"id": "example", "weight": 10, "description": "A completed example is available"},
    {"id": "dynamic", "weight": 10, "description": "Uses dynamic content (macros, dates, Jira queries)"},
    {"id": "version", "weight": 5, "description": "Version number is tracked"},
    {"id": "freshness", "weight": 10, "description": "Updated within the last 12 months"},
    {"id": "labels", "weight": 5, "description": "Template has categorization labels"},
]


def load_data(path: str) -> dict:
    with open(path, "r") as f:
        return json.load(f)


def validate_template(data: dict) -> dict:
    name = data.get("name", "")
    results = []
    total_weight = 0
    earned_weight = 0

    # Name check
    check = {"id": "name", "weight": 10}
    passed = len(name.strip()) > 5
    results.append({"check": "name", "passed": passed, "weight": 10, "detail": f"Name: '{name}'"})
    total_weight += 10
    if passed:
        earned_weight += 10

    # Owner
    passed = bool(data.get("owner", "").strip())
    results.append({"check": "owner", "passed": passed, "weight": 10, "detail": f"Owner: {data.get('owner', 'Not set')}"})
    total_weight += 10
    if passed:
        earned_weight += 10

    # Description
    desc = data.get("description", "")
    passed = len(desc.strip()) > 20
    results.append({"check": "description", "passed": passed, "weight": 10, "detail": f"Description length: {len(desc)} chars"})
    total_weight += 10
    if passed:
        earned_weight += 10

    # Sections
    sections = data.get("sections", [])
    passed = len(sections) >= 3
    results.append({"check": "sections", "passed": passed, "weight": 15, "detail": f"Sections: {len(sections)}"})
    total_weight += 15
    if passed:
        earned_weight += 15

    # Instructions
    has_instructions = sum(1 for s in sections if s.get("has_instructions", False) or "[" in s.get("content", ""))
    passed = has_instructions >= len(sections) * 0.5 if sections else False
    results.append({"check": "instructions", "passed": passed, "weight": 15, "detail": f"Sections with instructions: {has_instructions}/{len(sections)}"})
    total_weight += 15
    if passed:
        earned_weight += 15

    # Example
    passed = data.get("has_example", False)
    results.append({"check": "example", "passed": passed, "weight": 10})
    total_weight += 10
    if passed:
        earned_weight += 10

    # Dynamic content
    passed = data.get("has_dynamic_content", False)
    results.append({"check": "dynamic", "passed": passed, "weight": 10})
    total_weight += 10
    if passed:
        earned_weight += 10

    # Version
    passed = bool(data.get("version", ""))
    results.append({"check": "version", "passed": passed, "weight": 5, "detail": f"Version: {data.get('version', 'Not set')}"})
    total_weight += 5
    if passed:
        earned_weight += 5

    # Freshness
    last_updated = data.get("last_updated", "")
    freshness_passed = False
    if last_updated:
        try:
            updated_dt = datetime.strptime(last_updated, "%Y-%m-%d")
            days = (datetime.now() - updated_dt).days
            freshness_passed = days <= 365
        except ValueError:
            pass
    results.append({"check": "freshness", "passed": freshness_passed, "weight": 10, "detail": f"Last updated: {last_updated or 'Unknown'}"})
    total_weight += 10
    if freshness_passed:
        earned_weight += 10

    # Labels
    labels = data.get("labels", [])
    passed = len(labels) >= 1
    results.append({"check": "labels", "passed": passed, "weight": 5, "detail": f"Labels: {', '.join(labels) if labels else 'None'}"})
    total_weight += 5
    if passed:
        earned_weight += 5

    score = round(earned_weight / total_weight * 100, 1) if total_weight > 0 else 0
    if score >= 85:
        rating = "Production Ready"
    elif score >= 65:
        rating = "Needs Minor Fixes"
    elif score >= 40:
        rating = "Needs Improvement"
    else:
        rating = "Not Ready"

    failures = [r for r in results if not r["passed"]]
    recs = []
    for f in failures:
        check_def = next((c for c in QUALITY_CHECKS if c["id"] == f["check"]), None)
        if check_def:
            recs.append(f"Fix: {check_def['description']}")

    return {
        "template_name": name,
        "score": score,
        "rating": rating,
        "checks_passed": sum(1 for r in results if r["passed"]),
        "checks_total": len(results),
        "results": results,
        "recommendations": recs,
    }


def print_report(result: dict) -> None:
    print(f"\nTemplate Validation: {result['template_name']}")
    print("=" * 55)
    print(f"Score: {result['score']:.0f}/100 ({result['rating']})")
    print(f"Checks: {result['checks_passed']}/{result['checks_total']} passed")

    print(f"\nChecks:")
    for r in result["results"]:
        status = "PASS" if r["passed"] else "FAIL"
        detail = f"  ({r.get('detail', '')})" if r.get("detail") else ""
        check_def = next((c for c in QUALITY_CHECKS if c["id"] == r["check"]), {})
        print(f"  [{status}] {check_def.get('description', r['check'])}{detail}")

    if result["recommendations"]:
        print(f"\nActions Needed:")
        for i, r in enumerate(result["recommendations"], 1):
            print(f"  {i}. {r}")
    print()


def print_example() -> None:
    example = {
        "name": "Sprint Retrospective Template",
        "owner": "Jane Smith",
        "description": "Standard template for sprint retrospective meetings. Covers what went well, challenges, and action items.",
        "version": "2.1",
        "last_updated": "2026-02-15",
        "labels": ["sprint", "retro", "agile"],
        "has_example": True,
        "has_dynamic_content": True,
        "sections": [
            {"title": "Sprint Overview", "content": "**Sprint**: [Number]\n**Velocity**: [X points]", "has_instructions": True},
            {"title": "What Went Well", "content": "- [Positive item]", "has_instructions": True},
            {"title": "Challenges", "content": "- [Challenge]", "has_instructions": True},
            {"title": "Action Items", "content": "- [ ] [Action] - @owner - [Date]", "has_instructions": True},
        ],
    }
    print(json.dumps(example, indent=2))


def main():
    parser = argparse.ArgumentParser(description="Validate templates against quality standards.")
    parser.add_argument("--template", type=str, help="Path to template JSON file")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--example", action="store_true", help="Print example and exit")
    args = parser.parse_args()

    if args.example:
        print_example()
        return
    if not args.template:
        parser.error("--template is required")

    data = load_data(args.template)
    result = validate_template(data)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print_report(result)


if __name__ == "__main__":
    main()
