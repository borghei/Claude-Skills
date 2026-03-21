#!/usr/bin/env python3
"""Dependency Mapper - Map and analyze cross-team/cross-service dependencies.

Reads dependency data and produces a dependency matrix, critical path analysis,
and risk assessment for delivery coordination.

Usage:
    python dependency_mapper.py --deps dependencies.json
    python dependency_mapper.py --deps dependencies.json --json
    python dependency_mapper.py --example
"""

import argparse
import json
import sys
from collections import defaultdict


def load_data(path: str) -> dict:
    """Load dependency data from JSON file."""
    with open(path, "r") as f:
        return json.load(f)


def build_graph(dependencies: list) -> tuple:
    """Build adjacency list and reverse adjacency list from dependencies."""
    graph = defaultdict(list)
    reverse_graph = defaultdict(list)
    all_nodes = set()

    for dep in dependencies:
        source = dep.get("from")
        target = dep.get("to")
        if source and target:
            graph[source].append({
                "target": target,
                "type": dep.get("type", "depends_on"),
                "risk": dep.get("risk", "Medium"),
                "description": dep.get("description", ""),
                "owner": dep.get("owner", "Unassigned"),
            })
            reverse_graph[target].append(source)
            all_nodes.add(source)
            all_nodes.add(target)

    return graph, reverse_graph, all_nodes


def find_cycles(graph: dict, all_nodes: set) -> list:
    """Detect circular dependencies using DFS."""
    cycles = []
    visited = set()
    rec_stack = set()
    path = []

    def dfs(node):
        visited.add(node)
        rec_stack.add(node)
        path.append(node)

        for edge in graph.get(node, []):
            neighbor = edge["target"]
            if neighbor not in visited:
                dfs(neighbor)
            elif neighbor in rec_stack:
                # Found a cycle
                cycle_start = path.index(neighbor)
                cycle = path[cycle_start:] + [neighbor]
                cycles.append(cycle)

        path.pop()
        rec_stack.discard(node)

    for node in all_nodes:
        if node not in visited:
            dfs(node)

    return cycles


def topological_sort(graph: dict, all_nodes: set) -> list:
    """Topological sort (Kahn's algorithm). Returns empty if cycle exists."""
    in_degree = defaultdict(int)
    for node in all_nodes:
        if node not in in_degree:
            in_degree[node] = 0
    for node in graph:
        for edge in graph[node]:
            in_degree[edge["target"]] += 1

    queue = [n for n in all_nodes if in_degree[n] == 0]
    result = []

    while queue:
        queue.sort()  # Deterministic ordering
        node = queue.pop(0)
        result.append(node)
        for edge in graph.get(node, []):
            target = edge["target"]
            in_degree[target] -= 1
            if in_degree[target] == 0:
                queue.append(target)

    return result if len(result) == len(all_nodes) else []


def analyze_dependencies(data: dict) -> dict:
    """Analyze dependencies and produce report."""
    project = data.get("project", "Unknown")
    dependencies = data.get("dependencies", [])

    if not dependencies:
        return {"project": project, "error": "No dependencies provided"}

    graph, reverse_graph, all_nodes = build_graph(dependencies)

    # Dependency matrix
    matrix = {}
    for source in sorted(all_nodes):
        row = {}
        for edge in graph.get(source, []):
            row[edge["target"]] = edge["type"]
        matrix[source] = row

    # Fan-in / fan-out analysis
    node_metrics = {}
    for node in sorted(all_nodes):
        fan_out = len(graph.get(node, []))
        fan_in = len(reverse_graph.get(node, []))
        node_metrics[node] = {
            "fan_out": fan_out,
            "fan_in": fan_in,
            "total_connections": fan_out + fan_in,
            "is_bottleneck": fan_in >= 3,
            "is_hub": fan_out >= 3,
        }

    # Cycle detection
    cycles = find_cycles(graph, all_nodes)

    # Execution order
    execution_order = topological_sort(graph, all_nodes)

    # Risk analysis
    risk_counts = {"High": 0, "Medium": 0, "Low": 0}
    high_risk_deps = []
    for dep in dependencies:
        risk = dep.get("risk", "Medium")
        risk_counts[risk] = risk_counts.get(risk, 0) + 1
        if risk == "High":
            high_risk_deps.append({
                "from": dep["from"],
                "to": dep["to"],
                "description": dep.get("description", ""),
                "owner": dep.get("owner", "Unassigned"),
            })

    # Bottlenecks
    bottlenecks = [
        {"node": node, "fan_in": metrics["fan_in"], "fan_out": metrics["fan_out"]}
        for node, metrics in node_metrics.items()
        if metrics["is_bottleneck"]
    ]

    # Recommendations
    recs = []
    if cycles:
        recs.append(f"Circular dependencies detected ({len(cycles)} cycle(s)). Break cycles by introducing interfaces or shared contracts.")
    if bottlenecks:
        for b in bottlenecks:
            recs.append(f"'{b['node']}' is a bottleneck ({b['fan_in']} inbound dependencies). Consider decoupling or adding redundancy.")
    if high_risk_deps:
        unowned = [d for d in high_risk_deps if d["owner"] == "Unassigned"]
        if unowned:
            recs.append(f"{len(unowned)} high-risk dependency(ies) without an owner. Assign owners immediately.")
    if not recs:
        recs.append("Dependency structure looks manageable. Continue monitoring during execution.")

    return {
        "project": project,
        "total_nodes": len(all_nodes),
        "total_dependencies": len(dependencies),
        "risk_distribution": risk_counts,
        "execution_order": execution_order,
        "has_cycles": len(cycles) > 0,
        "cycles": [" -> ".join(c) for c in cycles],
        "bottlenecks": bottlenecks,
        "high_risk_dependencies": high_risk_deps,
        "node_metrics": node_metrics,
        "recommendations": recs,
    }


def print_report(result: dict) -> None:
    """Print human-readable dependency report."""
    if "error" in result:
        print(f"Error: {result['error']}")
        return

    print(f"\nDependency Map: {result['project']}")
    print(f"Components: {result['total_nodes']}  |  Dependencies: {result['total_dependencies']}")
    print("=" * 60)

    rd = result["risk_distribution"]
    print(f"Risk: High={rd.get('High',0)}, Medium={rd.get('Medium',0)}, Low={rd.get('Low',0)}")

    if result["has_cycles"]:
        print(f"\n!! CIRCULAR DEPENDENCIES DETECTED:")
        for c in result["cycles"]:
            print(f"  {c}")

    if result["execution_order"]:
        print(f"\nRecommended Execution Order:")
        for i, node in enumerate(result["execution_order"], 1):
            metrics = result["node_metrics"].get(node, {})
            flags = []
            if metrics.get("is_bottleneck"):
                flags.append("BOTTLENECK")
            if metrics.get("is_hub"):
                flags.append("HUB")
            flag_str = f"  [{', '.join(flags)}]" if flags else ""
            print(f"  {i}. {node}  (in:{metrics.get('fan_in',0)} out:{metrics.get('fan_out',0)}){flag_str}")

    if result["high_risk_dependencies"]:
        print(f"\nHigh-Risk Dependencies:")
        for d in result["high_risk_dependencies"]:
            print(f"  {d['from']} -> {d['to']}: {d['description']} (Owner: {d['owner']})")

    if result["recommendations"]:
        print(f"\nRecommendations:")
        for i, r in enumerate(result["recommendations"], 1):
            print(f"  {i}. {r}")
    print()


def print_example() -> None:
    """Print example dependency data JSON."""
    example = {
        "project": "Platform Migration",
        "dependencies": [
            {"from": "Auth Service", "to": "User Database", "type": "depends_on", "risk": "High", "owner": "Alice", "description": "Auth requires user DB schema migration first"},
            {"from": "API Gateway", "to": "Auth Service", "type": "depends_on", "risk": "Medium", "owner": "Bob", "description": "Gateway needs auth endpoints available"},
            {"from": "Web App", "to": "API Gateway", "type": "depends_on", "risk": "Low", "owner": "Carol", "description": "Frontend depends on gateway routes"},
            {"from": "Mobile App", "to": "API Gateway", "type": "depends_on", "risk": "Low", "owner": "Dave", "description": "Mobile depends on gateway routes"},
            {"from": "Analytics", "to": "User Database", "type": "depends_on", "risk": "Medium", "owner": "Unassigned", "description": "Analytics reads from user DB"},
            {"from": "Analytics", "to": "API Gateway", "type": "depends_on", "risk": "High", "owner": "Unassigned", "description": "Analytics collects API usage data"},
        ],
    }
    print(json.dumps(example, indent=2))


def main():
    parser = argparse.ArgumentParser(
        description="Map and analyze cross-team/cross-service dependencies."
    )
    parser.add_argument("--deps", type=str, help="Path to dependencies JSON file")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    parser.add_argument("--example", action="store_true", help="Print example dependencies JSON and exit")
    args = parser.parse_args()

    if args.example:
        print_example()
        return

    if not args.deps:
        parser.error("--deps is required (use --example to see the expected format)")

    data = load_data(args.deps)
    result = analyze_dependencies(data)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print_report(result)


if __name__ == "__main__":
    main()
