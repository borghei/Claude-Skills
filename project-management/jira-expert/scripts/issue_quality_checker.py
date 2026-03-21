#!/usr/bin/env python3
"""Issue Quality Checker - Evaluate Jira issue quality against best practices.

Reads a set of Jira issues and scores them for completeness, clarity, and
adherence to team standards. Produces a quality report with actionable fixes.

Usage:
    python issue_quality_checker.py --issues issues.json
    python issue_quality_checker.py --issues issues.json --json
    python issue_quality_checker.py --example
"""

import argparse
import json
import re
import sys


QUALITY_CHECKS = {
    "has_summary": {"weight": 10, "description": "Issue has a non-empty summary"},
    "summary_length": {"weight": 5, "description": "Summary is 10-80 characters (concise but descriptive)"},
    "has_description": {"weight": 15, "description": "Issue has a non-empty description"},
    "description_length": {"weight": 5, "description": "Description is at least 50 characters"},
    "has_acceptance_criteria": {"weight": 15, "description": "Description contains acceptance criteria"},
    "has_assignee": {"weight": 10, "description": "Issue is assigned to someone"},
    "has_priority": {"weight": 5, "description": "Priority is set"},
    "has_story_points": {"weight": 10, "description": "Story points are estimated (for stories)"},
    "has_labels": {"weight": 5, "description": "At least one label is applied"},
    "has_epic_link": {"weight": 10, "description": "Issue is linked to an epic"},
    "has_sprint": {"weight": 5, "description": "Issue is assigned to a sprint"},
    "no_vague_summary": {"weight": 5, "description": "Summary does not use vague words like 'fix stuff', 'update things'"},
}


def load_data(path: str) -> dict:
    """Load issues from JSON file."""
    with open(path, "r") as f:
        return json.load(f)


VAGUE_PATTERNS = [
    r"\bfix stuff\b",
    r"\bupdate things\b",
    r"\bmisc\b",
    r"\bvarious\b",
    r"\btodo\b",
    r"\bwip\b",
    r"\btest$",
    r"^bug$",
    r"^task$",
    r"^story$",
]


def check_issue(issue: dict) -> dict:
    """Run quality checks on a single issue."""
    key = issue.get("key", "UNKNOWN")
    issue_type = issue.get("type", "Story").lower()
    summary = issue.get("summary", "").strip()
    description = issue.get("description", "").strip()
    assignee = issue.get("assignee", "")
    priority = issue.get("priority", "")
    story_points = issue.get("story_points")
    labels = issue.get("labels", [])
    epic_link = issue.get("epic_link", "")
    sprint = issue.get("sprint", "")

    results = {}
    total_possible = 0
    total_earned = 0

    # has_summary
    check = QUALITY_CHECKS["has_summary"]
    passed = len(summary) > 0
    results["has_summary"] = {"passed": passed, "weight": check["weight"]}
    total_possible += check["weight"]
    if passed:
        total_earned += check["weight"]

    # summary_length
    check = QUALITY_CHECKS["summary_length"]
    passed = 10 <= len(summary) <= 80
    results["summary_length"] = {"passed": passed, "weight": check["weight"], "value": len(summary)}
    total_possible += check["weight"]
    if passed:
        total_earned += check["weight"]

    # has_description
    check = QUALITY_CHECKS["has_description"]
    passed = len(description) > 0
    results["has_description"] = {"passed": passed, "weight": check["weight"]}
    total_possible += check["weight"]
    if passed:
        total_earned += check["weight"]

    # description_length
    check = QUALITY_CHECKS["description_length"]
    passed = len(description) >= 50
    results["description_length"] = {"passed": passed, "weight": check["weight"], "value": len(description)}
    total_possible += check["weight"]
    if passed:
        total_earned += check["weight"]

    # has_acceptance_criteria
    check = QUALITY_CHECKS["has_acceptance_criteria"]
    ac_patterns = [r"acceptance criteria", r"\bac\b.*:", r"given.*when.*then", r"\[ \]", r"\[x\]", r"- \[ \]"]
    passed = any(re.search(p, description, re.IGNORECASE) for p in ac_patterns)
    results["has_acceptance_criteria"] = {"passed": passed, "weight": check["weight"]}
    total_possible += check["weight"]
    if passed:
        total_earned += check["weight"]

    # has_assignee
    check = QUALITY_CHECKS["has_assignee"]
    passed = bool(assignee)
    results["has_assignee"] = {"passed": passed, "weight": check["weight"]}
    total_possible += check["weight"]
    if passed:
        total_earned += check["weight"]

    # has_priority
    check = QUALITY_CHECKS["has_priority"]
    passed = bool(priority) and priority.lower() not in ("none", "")
    results["has_priority"] = {"passed": passed, "weight": check["weight"]}
    total_possible += check["weight"]
    if passed:
        total_earned += check["weight"]

    # has_story_points (only for stories)
    check = QUALITY_CHECKS["has_story_points"]
    if issue_type in ("story", "task"):
        passed = story_points is not None and story_points > 0
        results["has_story_points"] = {"passed": passed, "weight": check["weight"]}
        total_possible += check["weight"]
        if passed:
            total_earned += check["weight"]

    # has_labels
    check = QUALITY_CHECKS["has_labels"]
    passed = len(labels) > 0
    results["has_labels"] = {"passed": passed, "weight": check["weight"]}
    total_possible += check["weight"]
    if passed:
        total_earned += check["weight"]

    # has_epic_link
    check = QUALITY_CHECKS["has_epic_link"]
    passed = bool(epic_link)
    results["has_epic_link"] = {"passed": passed, "weight": check["weight"]}
    total_possible += check["weight"]
    if passed:
        total_earned += check["weight"]

    # has_sprint
    check = QUALITY_CHECKS["has_sprint"]
    passed = bool(sprint)
    results["has_sprint"] = {"passed": passed, "weight": check["weight"]}
    total_possible += check["weight"]
    if passed:
        total_earned += check["weight"]

    # no_vague_summary
    check = QUALITY_CHECKS["no_vague_summary"]
    passed = not any(re.search(p, summary, re.IGNORECASE) for p in VAGUE_PATTERNS)
    results["no_vague_summary"] = {"passed": passed, "weight": check["weight"]}
    total_possible += check["weight"]
    if passed:
        total_earned += check["weight"]

    score = round(total_earned / total_possible * 100, 1) if total_possible > 0 else 0

    # Failures
    failures = [
        {"check": k, "description": QUALITY_CHECKS[k]["description"]}
        for k, v in results.items()
        if not v["passed"]
    ]

    return {
        "key": key,
        "type": issue.get("type", "Unknown"),
        "summary": summary[:60] + "..." if len(summary) > 60 else summary,
        "score": score,
        "checks_passed": sum(1 for v in results.values() if v["passed"]),
        "checks_total": len(results),
        "failures": failures,
    }


def analyze_issues(data: dict) -> dict:
    """Analyze all issues and produce aggregate report."""
    project = data.get("project", "Unknown")
    issues = data.get("issues", [])

    results = [check_issue(issue) for issue in issues]
    scores = [r["score"] for r in results]
    avg_score = round(sum(scores) / len(scores), 1) if scores else 0

    # Aggregate failure counts
    failure_counts = {}
    for r in results:
        for f in r["failures"]:
            check = f["check"]
            failure_counts[check] = failure_counts.get(check, 0) + 1

    top_failures = sorted(failure_counts.items(), key=lambda x: x[1], reverse=True)

    # Quality distribution
    excellent = sum(1 for s in scores if s >= 90)
    good = sum(1 for s in scores if 70 <= s < 90)
    fair = sum(1 for s in scores if 50 <= s < 70)
    poor = sum(1 for s in scores if s < 50)

    if avg_score >= 85:
        rating = "Excellent"
    elif avg_score >= 70:
        rating = "Good"
    elif avg_score >= 50:
        rating = "Needs Improvement"
    else:
        rating = "Poor"

    return {
        "project": project,
        "total_issues": len(issues),
        "average_score": avg_score,
        "rating": rating,
        "distribution": {"excellent": excellent, "good": good, "fair": fair, "poor": poor},
        "top_failures": [
            {"check": t[0], "count": t[1], "description": QUALITY_CHECKS.get(t[0], {}).get("description", "")}
            for t in top_failures[:5]
        ],
        "issues": results,
    }


def print_report(result: dict) -> None:
    """Print human-readable quality report."""
    print(f"\nIssue Quality Report: {result['project']}")
    print(f"Issues Analyzed: {result['total_issues']}")
    print("=" * 60)
    print(f"Average Quality Score: {result['average_score']:.1f}% ({result['rating']})")

    d = result["distribution"]
    print(f"\nDistribution:")
    print(f"  Excellent (90+): {d['excellent']}")
    print(f"  Good (70-89):    {d['good']}")
    print(f"  Fair (50-69):    {d['fair']}")
    print(f"  Poor (<50):      {d['poor']}")

    if result["top_failures"]:
        print(f"\nTop Quality Gaps:")
        for f in result["top_failures"]:
            print(f"  [{f['count']} issues] {f['description']}")

    print(f"\nPer-Issue Scores:")
    print(f"  {'Key':<15} {'Type':<10} {'Score':>6}  {'Issues'}")
    print(f"  {'-'*15} {'-'*10} {'-'*6}  {'-'*30}")
    for issue in sorted(result["issues"], key=lambda x: x["score"]):
        failures_str = ", ".join(f["check"] for f in issue["failures"][:3])
        if len(issue["failures"]) > 3:
            failures_str += f" +{len(issue['failures'])-3} more"
        print(f"  {issue['key']:<15} {issue['type']:<10} {issue['score']:>5.0f}%  {failures_str}")

    print()


def print_example() -> None:
    """Print example issues JSON."""
    example = {
        "project": "PROJ",
        "issues": [
            {
                "key": "PROJ-101",
                "type": "Story",
                "summary": "Add user onboarding wizard for new signups",
                "description": "## Acceptance Criteria\n- [ ] Wizard appears on first login\n- [ ] User can skip at any step\n- [ ] Progress is saved if user leaves",
                "assignee": "alice",
                "priority": "High",
                "story_points": 5,
                "labels": ["onboarding"],
                "epic_link": "PROJ-50",
                "sprint": "Sprint 24",
            },
            {
                "key": "PROJ-102",
                "type": "Bug",
                "summary": "fix stuff",
                "description": "",
                "assignee": "",
                "priority": "",
                "story_points": None,
                "labels": [],
                "epic_link": "",
                "sprint": "",
            },
        ],
    }
    print(json.dumps(example, indent=2))


def main():
    parser = argparse.ArgumentParser(
        description="Evaluate Jira issue quality against best practices."
    )
    parser.add_argument("--issues", type=str, help="Path to issues JSON file")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    parser.add_argument("--example", action="store_true", help="Print example input JSON and exit")
    args = parser.parse_args()

    if args.example:
        print_example()
        return

    if not args.issues:
        parser.error("--issues is required (use --example to see the expected format)")

    data = load_data(args.issues)
    result = analyze_issues(data)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print_report(result)


if __name__ == "__main__":
    main()
