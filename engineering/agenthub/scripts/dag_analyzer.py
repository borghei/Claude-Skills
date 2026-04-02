#!/usr/bin/env python3
"""Analyze multi-agent DAG workflow definitions for structural issues.

Validates workflow definitions by checking for cycles, unreachable nodes,
missing input/output references, and bottlenecks. Also computes critical
path length and parallelization potential.

Usage:
    python dag_analyzer.py --workflow workflow.json --validate
    python dag_analyzer.py --workflow workflow.json --critical-path
    python dag_analyzer.py --workflow workflow.json --visualize
    python dag_analyzer.py --workflow workflow.json --json
"""

import argparse
import json
import sys
from collections import defaultdict, deque
from pathlib import Path


def load_workflow(path):
    """Load workflow definition from JSON file."""
    try:
        with open(path, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"Error loading workflow: {e}", file=sys.stderr)
        sys.exit(1)


def build_graph(workflow):
    """Build adjacency list and reverse graph from workflow agents."""
    agents = workflow.get("agents", {})
    graph = defaultdict(list)      # agent -> list of dependents
    reverse = defaultdict(list)    # agent -> list of dependencies
    all_nodes = set(agents.keys())

    for agent_id, agent_def in agents.items():
        deps = agent_def.get("dependencies", [])
        for dep in deps:
            graph[dep].append(agent_id)
            reverse[agent_id].append(dep)

    return graph, reverse, all_nodes


def detect_cycles(graph, all_nodes):
    """Detect cycles using DFS coloring (white/gray/black)."""
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {n: WHITE for n in all_nodes}
    cycles = []

    def dfs(node, path):
        color[node] = GRAY
        path.append(node)
        for neighbor in graph.get(node, []):
            if color[neighbor] == GRAY:
                # Found a cycle
                cycle_start = path.index(neighbor)
                cycles.append(path[cycle_start:] + [neighbor])
            elif color[neighbor] == WHITE:
                dfs(neighbor, path)
        path.pop()
        color[node] = BLACK

    for node in all_nodes:
        if color[node] == WHITE:
            dfs(node, [])

    return cycles


def topological_sort(graph, reverse, all_nodes):
    """Kahn's algorithm for topological sort."""
    in_degree = {n: 0 for n in all_nodes}
    for node in all_nodes:
        for dep in reverse.get(node, []):
            in_degree[node] = in_degree.get(node, 0)
        in_degree[node] = len(reverse.get(node, []))

    queue = deque([n for n in all_nodes if in_degree[n] == 0])
    order = []

    while queue:
        node = queue.popleft()
        order.append(node)
        for dependent in graph.get(node, []):
            in_degree[dependent] -= 1
            if in_degree[dependent] == 0:
                queue.append(dependent)

    if len(order) != len(all_nodes):
        return None  # Cycle exists
    return order


def find_roots_and_terminals(graph, reverse, all_nodes):
    """Identify root nodes (no deps) and terminal nodes (no dependents)."""
    roots = [n for n in all_nodes if not reverse.get(n)]
    terminals = [n for n in all_nodes if not graph.get(n)]
    return sorted(roots), sorted(terminals)


def compute_critical_path(workflow, graph, reverse, all_nodes):
    """Compute the critical path (longest path through the DAG)."""
    agents = workflow.get("agents", {})
    config = workflow.get("config", {})
    default_timeout = config.get("timeout_per_agent", 300)

    # Estimate duration per agent (use timeout as upper bound)
    durations = {}
    for agent_id in all_nodes:
        agent_config = agents.get(agent_id, {}).get("config", {})
        durations[agent_id] = agent_config.get("timeout", default_timeout)

    # Compute longest path from each node
    longest_to = {n: 0 for n in all_nodes}
    predecessor = {n: None for n in all_nodes}

    topo = topological_sort(graph, reverse, all_nodes)
    if topo is None:
        return None, 0  # Cycle

    for node in topo:
        for dependent in graph.get(node, []):
            new_dist = longest_to[node] + durations[node]
            if new_dist > longest_to[dependent]:
                longest_to[dependent] = new_dist
                predecessor[dependent] = node

    # Find the terminal with the longest path
    terminals = [n for n in all_nodes if not graph.get(n)]
    if not terminals:
        return [], 0

    end_node = max(terminals, key=lambda n: longest_to[n] + durations[n])
    total_time = longest_to[end_node] + durations[end_node]

    # Reconstruct path
    path = [end_node]
    current = end_node
    while predecessor[current] is not None:
        current = predecessor[current]
        path.append(current)
    path.reverse()

    return path, total_time


def check_io_references(workflow):
    """Verify all input references resolve to upstream outputs."""
    agents = workflow.get("agents", {})
    issues = []

    # Map each agent to its outputs
    output_map = {}
    for agent_id, agent_def in agents.items():
        for output in agent_def.get("outputs", []):
            output_map[output] = agent_id

    # Check inputs
    for agent_id, agent_def in agents.items():
        deps = set(agent_def.get("dependencies", []))
        for inp in agent_def.get("inputs", []):
            if inp in output_map:
                producer = output_map[inp]
                # Check that the producer is an upstream dependency
                if producer not in deps and producer != agent_id:
                    issues.append({
                        "type": "missing_dependency",
                        "agent": agent_id,
                        "input": inp,
                        "producer": producer,
                        "message": f"Agent '{agent_id}' uses input '{inp}' from '{producer}' but doesn't list it as a dependency",
                    })
            # Inputs might be workflow-level inputs (not produced by agents)

    # Check for unused outputs
    all_inputs = set()
    for agent_def in agents.values():
        all_inputs.update(agent_def.get("inputs", []))

    for output_name, producer in output_map.items():
        if output_name not in all_inputs:
            # Terminal output -- expected
            if not any(
                producer in agents[a].get("dependencies", [])
                for a in agents
            ):
                pass  # Terminal agent output, this is fine

    return issues


def compute_parallel_groups(graph, reverse, all_nodes):
    """Compute which agents can run in parallel at each level."""
    topo = topological_sort(graph, reverse, all_nodes)
    if topo is None:
        return []

    # Compute level (longest path from any root to this node)
    level = {n: 0 for n in all_nodes}
    for node in topo:
        for dependent in graph.get(node, []):
            level[dependent] = max(level[dependent], level[node] + 1)

    # Group by level
    groups = defaultdict(list)
    for node in all_nodes:
        groups[level[node]].append(node)

    return [{"level": lvl, "agents": sorted(agents)} for lvl, agents in sorted(groups.items())]


def validate_workflow(workflow):
    """Run all validation checks on a workflow definition."""
    agents = workflow.get("agents", {})
    if not agents:
        return {"valid": False, "errors": ["No agents defined in workflow"]}

    graph, reverse, all_nodes = build_graph(workflow)
    errors = []
    warnings = []

    # Check for unknown dependencies
    for agent_id, agent_def in agents.items():
        for dep in agent_def.get("dependencies", []):
            if dep not in all_nodes:
                errors.append(f"Agent '{agent_id}' depends on unknown agent '{dep}'")

    # Cycle detection
    cycles = detect_cycles(graph, all_nodes)
    for cycle in cycles:
        errors.append(f"Cycle detected: {' -> '.join(cycle)}")

    # IO reference check
    io_issues = check_io_references(workflow)
    for issue in io_issues:
        warnings.append(issue["message"])

    # Root/terminal check
    roots, terminals = find_roots_and_terminals(graph, reverse, all_nodes)
    if not roots:
        errors.append("No root agents found (all agents have dependencies)")
    if not terminals:
        warnings.append("No terminal agents found (all agents have dependents)")

    # Unreachable check
    if roots and not cycles:
        reachable = set()
        queue = deque(roots)
        while queue:
            node = queue.popleft()
            if node in reachable:
                continue
            reachable.add(node)
            queue.extend(graph.get(node, []))
        unreachable = all_nodes - reachable
        for node in unreachable:
            warnings.append(f"Agent '{node}' is unreachable from root agents")

    # Critical path
    crit_path, crit_time = compute_critical_path(workflow, graph, reverse, all_nodes)
    parallel_groups = compute_parallel_groups(graph, reverse, all_nodes)

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "stats": {
            "total_agents": len(all_nodes),
            "root_agents": roots,
            "terminal_agents": terminals,
            "max_parallel": max(len(g["agents"]) for g in parallel_groups) if parallel_groups else 0,
            "depth": len(parallel_groups),
            "critical_path": crit_path if crit_path else [],
            "critical_path_time_s": crit_time,
        },
        "parallel_groups": parallel_groups,
    }


def visualize_dag(workflow):
    """Generate a text-based DAG visualization."""
    graph, reverse, all_nodes = build_graph(workflow)
    groups = compute_parallel_groups(graph, reverse, all_nodes)
    lines = []

    for group in groups:
        level_agents = group["agents"]
        level_line = "  |  ".join(f"[{a}]" for a in level_agents)
        lines.append(f"Level {group['level']}: {level_line}")

        # Show edges
        for agent in level_agents:
            dependents = graph.get(agent, [])
            for dep in dependents:
                lines.append(f"  {agent} --> {dep}")

    return "\n".join(lines)


def format_human(result, visualization=None):
    """Format validation result for human output."""
    output = []
    output.append("=" * 60)
    output.append("DAG WORKFLOW ANALYZER")
    output.append("=" * 60)

    if not result["valid"]:
        output.append("")
        output.append("VALIDATION: FAILED")
        output.append("-" * 60)
        for err in result["errors"]:
            output.append(f"  [ERROR] {err}")
    else:
        output.append("")
        output.append("VALIDATION: PASSED")

    if result["warnings"]:
        output.append("")
        output.append("WARNINGS")
        output.append("-" * 60)
        for warn in result["warnings"]:
            output.append(f"  [WARN] {warn}")

    stats = result["stats"]
    output.append("")
    output.append("STATISTICS")
    output.append("-" * 60)
    output.append(f"  Total agents:     {stats['total_agents']}")
    output.append(f"  Root agents:      {', '.join(stats['root_agents'])}")
    output.append(f"  Terminal agents:  {', '.join(stats['terminal_agents'])}")
    output.append(f"  Max parallelism:  {stats['max_parallel']}")
    output.append(f"  DAG depth:        {stats['depth']} levels")
    if stats["critical_path"]:
        output.append(f"  Critical path:    {' -> '.join(stats['critical_path'])}")
        output.append(f"  Est. time:        {stats['critical_path_time_s']}s")

    if result["parallel_groups"]:
        output.append("")
        output.append("EXECUTION GROUPS")
        output.append("-" * 60)
        for group in result["parallel_groups"]:
            agents_str = ", ".join(group["agents"])
            output.append(f"  Level {group['level']}: [{agents_str}]  ({len(group['agents'])} parallel)")

    if visualization:
        output.append("")
        output.append("DAG VISUALIZATION")
        output.append("-" * 60)
        output.append(visualization)

    return "\n".join(output)


def main():
    parser = argparse.ArgumentParser(
        description="Analyze multi-agent DAG workflow definitions.",
        epilog="Example: python dag_analyzer.py --workflow workflow.json --validate",
    )
    parser.add_argument("--workflow", required=True, help="Path to workflow JSON file")
    parser.add_argument("--validate", action="store_true", help="Run full validation")
    parser.add_argument("--critical-path", action="store_true", help="Show critical path only")
    parser.add_argument("--visualize", action="store_true", help="Show DAG visualization")
    parser.add_argument("--json", action="store_true", dest="json_output", help="Output as JSON")

    args = parser.parse_args()

    wf_path = Path(args.workflow)
    if not wf_path.exists():
        print(f"Error: Workflow file '{args.workflow}' not found.", file=sys.stderr)
        sys.exit(1)

    workflow = load_workflow(wf_path)
    result = validate_workflow(workflow)
    visualization = visualize_dag(workflow) if args.visualize else None

    if args.json_output:
        output = result
        if visualization:
            output["visualization"] = visualization
        print(json.dumps(output, indent=2))
    else:
        print(format_human(result, visualization))

    # Exit with error code if invalid
    if not result["valid"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
