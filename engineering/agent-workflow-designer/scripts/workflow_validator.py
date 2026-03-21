#!/usr/bin/env python3
"""Validate agent workflow DAGs for cycles, dead ends, unreachable nodes, and structural issues.

Accepts a JSON workflow definition and checks for:
  - Cycles (circular dependencies between steps)
  - Unreachable nodes (steps not reachable from any entry point)
  - Dead ends (steps with no outgoing edges that aren't marked as terminal)
  - Missing dependency references (edges pointing to non-existent steps)
  - Duplicate step IDs
  - Empty workflows

Workflow JSON format:
{
  "name": "my-workflow",
  "steps": [
    {"id": "research", "agent": "researcher", "depends_on": []},
    {"id": "write", "agent": "writer", "depends_on": ["research"]},
    {"id": "review", "agent": "reviewer", "depends_on": ["write"], "terminal": true}
  ]
}

Usage:
  python workflow_validator.py workflow.json
  python workflow_validator.py workflow.json --json
  python workflow_validator.py --stdin < workflow.json
  echo '{"steps":[...]}' | python workflow_validator.py --stdin --json
"""

import argparse
import json
import sys
from collections import deque
from typing import Any


def load_workflow(path: str | None, use_stdin: bool) -> dict[str, Any]:
    """Load workflow definition from file or stdin."""
    if use_stdin:
        raw = sys.stdin.read()
    elif path:
        with open(path, "r", encoding="utf-8") as f:
            raw = f.read()
    else:
        raise ValueError("Provide a file path or use --stdin")

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {e}")

    if not isinstance(data, dict):
        raise ValueError("Workflow must be a JSON object")
    if "steps" not in data:
        raise ValueError("Workflow must contain a 'steps' array")
    if not isinstance(data["steps"], list):
        raise ValueError("'steps' must be a JSON array")

    return data


def validate_workflow(workflow: dict[str, Any]) -> dict[str, Any]:
    """Run all validation checks on the workflow. Returns a results dict."""
    steps = workflow.get("steps", [])
    name = workflow.get("name", "<unnamed>")

    errors: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []

    # --- Check: empty workflow ---
    if not steps:
        errors.append({"check": "empty_workflow", "message": "Workflow has no steps"})
        return _build_result(name, steps, errors, warnings)

    # --- Check: duplicate IDs ---
    seen_ids: dict[str, int] = {}
    for i, step in enumerate(steps):
        step_id = step.get("id")
        if step_id is None:
            errors.append({
                "check": "missing_id",
                "message": f"Step at index {i} has no 'id' field",
            })
            continue
        if step_id in seen_ids:
            errors.append({
                "check": "duplicate_id",
                "message": f"Duplicate step ID '{step_id}' (first at index {seen_ids[step_id]}, again at {i})",
            })
        seen_ids[step_id] = i

    all_ids = set(seen_ids.keys())

    # --- Build adjacency structures ---
    forward: dict[str, list[str]] = {sid: [] for sid in all_ids}
    reverse: dict[str, list[str]] = {sid: [] for sid in all_ids}
    terminal_ids: set[str] = set()
    entry_ids: set[str] = set()

    for step in steps:
        step_id = step.get("id")
        if step_id is None:
            continue
        deps = step.get("depends_on", [])
        if not isinstance(deps, list):
            errors.append({
                "check": "invalid_depends_on",
                "message": f"Step '{step_id}' has non-list 'depends_on': {deps}",
            })
            deps = []

        if step.get("terminal", False):
            terminal_ids.add(step_id)

        if not deps:
            entry_ids.add(step_id)

        for dep in deps:
            if dep not in all_ids:
                errors.append({
                    "check": "missing_dependency",
                    "message": f"Step '{step_id}' depends on '{dep}' which does not exist",
                })
            else:
                forward[dep].append(step_id)
                reverse[step_id].append(dep)

    # --- Check: cycle detection (Kahn's algorithm) ---
    in_degree = {sid: len(reverse.get(sid, [])) for sid in all_ids}
    queue = deque(sid for sid, deg in in_degree.items() if deg == 0)
    topo_order: list[str] = []

    while queue:
        node = queue.popleft()
        topo_order.append(node)
        for neighbor in forward.get(node, []):
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    if len(topo_order) != len(all_ids):
        cycle_nodes = sorted(all_ids - set(topo_order))
        errors.append({
            "check": "cycle_detected",
            "message": f"Circular dependency among steps: {cycle_nodes}",
            "nodes": cycle_nodes,
        })

    # --- Check: unreachable nodes ---
    reachable: set[str] = set()
    bfs_queue = deque(entry_ids)
    while bfs_queue:
        node = bfs_queue.popleft()
        if node in reachable:
            continue
        reachable.add(node)
        for neighbor in forward.get(node, []):
            if neighbor not in reachable:
                bfs_queue.append(neighbor)

    unreachable = sorted(all_ids - reachable)
    if unreachable:
        errors.append({
            "check": "unreachable_nodes",
            "message": f"Steps not reachable from any entry point: {unreachable}",
            "nodes": unreachable,
        })

    # --- Check: dead ends ---
    for sid in all_ids:
        if not forward.get(sid) and sid not in terminal_ids:
            warnings.append({
                "check": "dead_end",
                "message": f"Step '{sid}' has no outgoing edges and is not marked terminal",
            })

    # --- Check: no entry points ---
    if not entry_ids:
        errors.append({
            "check": "no_entry_point",
            "message": "No entry points found (all steps have dependencies)",
        })

    # --- Check: missing agent field ---
    for step in steps:
        step_id = step.get("id", "<unknown>")
        if "agent" not in step:
            warnings.append({
                "check": "missing_agent",
                "message": f"Step '{step_id}' has no 'agent' field specified",
            })

    return _build_result(name, steps, errors, warnings,
                         topo_order=topo_order,
                         entry_points=sorted(entry_ids),
                         terminal_nodes=sorted(terminal_ids))


def _build_result(
    name: str,
    steps: list,
    errors: list[dict],
    warnings: list[dict],
    topo_order: list[str] | None = None,
    entry_points: list[str] | None = None,
    terminal_nodes: list[str] | None = None,
) -> dict[str, Any]:
    valid = len(errors) == 0
    result: dict[str, Any] = {
        "workflow": name,
        "valid": valid,
        "step_count": len(steps),
        "errors": errors,
        "warnings": warnings,
    }
    if topo_order is not None:
        result["topological_order"] = topo_order
    if entry_points is not None:
        result["entry_points"] = entry_points
    if terminal_nodes is not None:
        result["terminal_nodes"] = terminal_nodes
    return result


def format_human(result: dict[str, Any]) -> str:
    """Format validation results for human reading."""
    lines: list[str] = []
    status = "VALID" if result["valid"] else "INVALID"
    lines.append(f"Workflow: {result['workflow']}")
    lines.append(f"Status:   {status}")
    lines.append(f"Steps:    {result['step_count']}")

    if result.get("entry_points"):
        lines.append(f"Entry:    {', '.join(result['entry_points'])}")
    if result.get("terminal_nodes"):
        lines.append(f"Terminal: {', '.join(result['terminal_nodes'])}")
    if result.get("topological_order"):
        lines.append(f"Order:    {' -> '.join(result['topological_order'])}")

    if result["errors"]:
        lines.append("")
        lines.append(f"ERRORS ({len(result['errors'])}):")
        for err in result["errors"]:
            lines.append(f"  [{err['check']}] {err['message']}")

    if result["warnings"]:
        lines.append("")
        lines.append(f"WARNINGS ({len(result['warnings'])}):")
        for warn in result["warnings"]:
            lines.append(f"  [{warn['check']}] {warn['message']}")

    if result["valid"] and not result["warnings"]:
        lines.append("")
        lines.append("No issues found. Workflow DAG is well-formed.")

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate agent workflow DAGs for structural issues",
        epilog="Exit codes: 0 = valid, 1 = invalid, 2 = input error",
    )
    parser.add_argument("file", nargs="?", help="Path to workflow JSON file")
    parser.add_argument("--stdin", action="store_true", help="Read workflow from stdin")
    parser.add_argument("--json", action="store_true", dest="json_output",
                        help="Output results as JSON")
    args = parser.parse_args()

    if not args.file and not args.stdin:
        parser.error("Provide a workflow file path or use --stdin")

    try:
        workflow = load_workflow(args.file, args.stdin)
    except (ValueError, FileNotFoundError, PermissionError) as e:
        if args.json_output:
            print(json.dumps({"error": str(e)}, indent=2))
        else:
            print(f"Error: {e}", file=sys.stderr)
        return 2

    result = validate_workflow(workflow)

    if args.json_output:
        print(json.dumps(result, indent=2))
    else:
        print(format_human(result))

    return 0 if result["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
