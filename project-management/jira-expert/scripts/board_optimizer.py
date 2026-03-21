#!/usr/bin/env python3
"""Board Optimizer - Analyze Jira board configuration and recommend optimizations.

Evaluates board settings (columns, WIP limits, swimlanes, filters) against
best practices and produces actionable recommendations.

Usage:
    python board_optimizer.py --board board.json
    python board_optimizer.py --board board.json --json
    python board_optimizer.py --example
"""

import argparse
import json
import sys


BEST_PRACTICES = {
    "columns": {
        "min": 3,
        "max": 8,
        "recommended": ["To Do", "In Progress", "In Review", "Done"],
    },
    "wip_limits": {
        "enabled": True,
        "rule": "WIP limit per column should be ~1.5x team size for that column",
    },
    "swimlanes": {
        "recommended_types": ["Expedite", "Standard", "Fixed Date"],
    },
}


def load_data(path: str) -> dict:
    """Load board configuration from JSON file."""
    with open(path, "r") as f:
        return json.load(f)


def analyze_board(data: dict) -> dict:
    """Analyze board configuration against best practices."""
    board_name = data.get("name", "Unknown Board")
    board_type = data.get("type", "scrum")
    team_size = data.get("team_size", 5)
    columns = data.get("columns", [])
    swimlanes = data.get("swimlanes", [])
    filter_jql = data.get("filter_jql", "")

    issues = []
    recommendations = []
    score = 100  # Start at 100, deduct for problems

    # Column analysis
    col_count = len(columns)
    if col_count < BEST_PRACTICES["columns"]["min"]:
        issues.append(f"Too few columns ({col_count}). Minimum recommended: {BEST_PRACTICES['columns']['min']}")
        recommendations.append("Add distinct columns for key workflow states (e.g., 'In Review' or 'QA') to improve visibility.")
        score -= 15
    elif col_count > BEST_PRACTICES["columns"]["max"]:
        issues.append(f"Too many columns ({col_count}). Maximum recommended: {BEST_PRACTICES['columns']['max']}")
        recommendations.append("Consolidate columns with low usage. Too many columns create visual noise and slow scanning.")
        score -= 10

    # WIP limit analysis
    columns_without_wip = []
    columns_with_high_wip = []
    for col in columns:
        name = col.get("name", "Unknown")
        wip = col.get("wip_limit")
        if name.lower() in ("to do", "backlog", "done"):
            continue  # WIP limits not typically needed for start/end columns
        if wip is None or wip == 0:
            columns_without_wip.append(name)
        elif wip > team_size * 2:
            columns_with_high_wip.append({"name": name, "wip": wip, "recommended": int(team_size * 1.5)})

    if columns_without_wip:
        issues.append(f"No WIP limits on active columns: {', '.join(columns_without_wip)}")
        recommendations.append(f"Set WIP limits on active columns. Start with ~{int(team_size * 1.5)} (1.5x team size) and adjust based on flow.")
        score -= 20

    if columns_with_high_wip:
        for c in columns_with_high_wip:
            issues.append(f"'{c['name']}' WIP limit ({c['wip']}) is too high. Recommended: ~{c['recommended']}")
        recommendations.append("Lower WIP limits to expose bottlenecks. High limits mask flow problems.")
        score -= 10

    # Swimlane analysis
    if not swimlanes:
        if board_type == "kanban":
            recommendations.append("Consider adding swimlanes (e.g., 'Expedite' and 'Standard') to distinguish priority classes of service.")
            score -= 5
    else:
        has_expedite = any(s.get("name", "").lower() in ("expedite", "urgent", "blocker") for s in swimlanes)
        if not has_expedite:
            recommendations.append("Add an 'Expedite' swimlane for urgent items with a strict WIP limit of 1.")

    # Filter analysis
    if not filter_jql:
        issues.append("No board filter JQL defined")
        recommendations.append("Define a specific board filter to prevent irrelevant issues from appearing. Example: project = PROJ AND type in (Story, Bug, Task)")
        score -= 10
    else:
        if "project" not in filter_jql.lower():
            recommendations.append("Board filter should include a project clause to prevent cross-project noise.")
            score -= 5

    # Done column analysis
    done_columns = [c for c in columns if c.get("name", "").lower() == "done"]
    if done_columns:
        done_col = done_columns[0]
        if not done_col.get("auto_close", False):
            recommendations.append("Enable automatic resolution when issues move to 'Done' column to keep data clean.")

    # Board type specific
    if board_type == "scrum":
        if not data.get("estimation_enabled", True):
            recommendations.append("Enable story point estimation for velocity tracking and sprint planning accuracy.")
            score -= 5
    elif board_type == "kanban":
        if not any(c.get("wip_limit") for c in columns):
            issues.append("Kanban board has no WIP limits -- this defeats the purpose of Kanban")
            score -= 25

    # Card layout
    card_fields = data.get("card_fields", [])
    essential_fields = ["assignee", "priority", "story_points"]
    missing_fields = [f for f in essential_fields if f not in card_fields]
    if missing_fields and card_fields:
        recommendations.append(f"Add these fields to card layout for better visibility: {', '.join(missing_fields)}")

    # Score classification
    if score >= 90:
        rating = "Excellent"
    elif score >= 70:
        rating = "Good"
    elif score >= 50:
        rating = "Needs Improvement"
    else:
        rating = "Poor"

    return {
        "board_name": board_name,
        "board_type": board_type,
        "team_size": team_size,
        "score": max(0, score),
        "rating": rating,
        "column_count": col_count,
        "columns": [{"name": c.get("name"), "wip_limit": c.get("wip_limit"), "statuses": c.get("statuses", [])} for c in columns],
        "swimlane_count": len(swimlanes),
        "issues": issues,
        "recommendations": recommendations,
    }


def print_report(result: dict) -> None:
    """Print human-readable board analysis."""
    print(f"\nBoard Analysis: {result['board_name']}")
    print(f"Type: {result['board_type'].title()}  |  Team Size: {result['team_size']}")
    print("=" * 55)
    print(f"Score: {result['score']}/100 ({result['rating']})")
    print()

    print("Column Configuration:")
    for col in result["columns"]:
        wip = f"WIP: {col['wip_limit']}" if col.get("wip_limit") else "No WIP limit"
        print(f"  [{col['name']:<20}] {wip}")

    if result["issues"]:
        print(f"\nIssues Found ({len(result['issues'])}):")
        for issue in result["issues"]:
            print(f"  ! {issue}")

    if result["recommendations"]:
        print(f"\nRecommendations ({len(result['recommendations'])}):")
        for i, rec in enumerate(result["recommendations"], 1):
            print(f"  {i}. {rec}")

    print()


def print_example() -> None:
    """Print example board configuration JSON."""
    example = {
        "name": "Team Alpha Board",
        "type": "kanban",
        "team_size": 6,
        "filter_jql": "project = ALPHA AND type in (Story, Bug, Task)",
        "estimation_enabled": True,
        "columns": [
            {"name": "Backlog", "wip_limit": None, "statuses": ["Backlog"]},
            {"name": "To Do", "wip_limit": None, "statuses": ["To Do"]},
            {"name": "In Progress", "wip_limit": 4, "statuses": ["In Progress"]},
            {"name": "In Review", "wip_limit": None, "statuses": ["In Review"]},
            {"name": "Done", "wip_limit": None, "auto_close": True, "statuses": ["Done"]},
        ],
        "swimlanes": [
            {"name": "Expedite", "jql": "priority = Blocker"},
            {"name": "Standard", "jql": ""},
        ],
        "card_fields": ["assignee", "priority"],
    }
    print(json.dumps(example, indent=2))


def main():
    parser = argparse.ArgumentParser(
        description="Analyze Jira board configuration and recommend optimizations."
    )
    parser.add_argument("--board", type=str, help="Path to board config JSON file")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    parser.add_argument("--example", action="store_true", help="Print example board config and exit")
    args = parser.parse_args()

    if args.example:
        print_example()
        return

    if not args.board:
        parser.error("--board is required (use --example to see the expected format)")

    data = load_data(args.board)
    result = analyze_board(data)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print_report(result)


if __name__ == "__main__":
    main()
