#!/usr/bin/env python3
"""Generate Mermaid diagrams from agent workflow DAG definitions.

Reads a workflow JSON and produces a Mermaid graph that visualizes steps, edges,
agent assignments, patterns (fan-out/fan-in, sequential, etc.), and optional
model/cost annotations.

Workflow JSON format:
{
  "name": "content-pipeline",
  "steps": [
    {"id": "research", "agent": "researcher", "depends_on": [], "model": "claude-sonnet-4-20250514"},
    {"id": "write", "agent": "writer", "depends_on": ["research"]},
    {"id": "review", "agent": "reviewer", "depends_on": ["write"], "terminal": true}
  ]
}

Optional step fields:
  - "model": str       - annotates the node with model name
  - "terminal": bool   - marks step as a terminal/end node
  - "parallel_branches": int - shows fan-out multiplier on node
  - "description": str - short label shown inside the node

Output formats:
  - Mermaid (default): paste into any Mermaid-compatible renderer
  - Also supports --direction (TD, LR, BT, RL) for graph orientation

Usage:
  python workflow_visualizer.py workflow.json
  python workflow_visualizer.py workflow.json --json
  python workflow_visualizer.py workflow.json --direction LR
  python workflow_visualizer.py workflow.json --annotate-models
  python workflow_visualizer.py workflow.json --annotate-cost
  python workflow_visualizer.py --stdin < workflow.json
"""

import argparse
import json
import sys
from typing import Any


# Agent-to-style mapping for visual differentiation
AGENT_STYLES: dict[str, str] = {
    "researcher":  "fill:#e1f5fe,stroke:#0288d1",
    "writer":      "fill:#f3e5f5,stroke:#7b1fa2",
    "editor":      "fill:#fce4ec,stroke:#c62828",
    "reviewer":    "fill:#fff3e0,stroke:#ef6c00",
    "coder":       "fill:#e8f5e9,stroke:#2e7d32",
    "analyst":     "fill:#fff9c4,stroke:#f9a825",
    "orchestrator":"fill:#f5f5f5,stroke:#616161,stroke-width:2px",
    "router":      "fill:#e0e0e0,stroke:#424242,stroke-dasharray:5 5",
    "validator":   "fill:#ffebee,stroke:#b71c1c",
}

MODEL_SHORT_NAMES: dict[str, str] = {
    "claude-opus-4-20250514":   "Opus",
    "claude-sonnet-4-20250514": "Sonnet",
    "claude-haiku-4-20250514":  "Haiku",
    "claude-opus":   "Opus",
    "claude-sonnet": "Sonnet",
    "claude-haiku":  "Haiku",
    "gpt-4o":       "GPT-4o",
    "gpt-4o-mini":  "GPT-4o-mini",
    "gpt-4-turbo":  "GPT-4T",
}


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

    if not isinstance(data, dict) or "steps" not in data:
        raise ValueError("Workflow must be a JSON object with a 'steps' array")
    return data


def sanitize_id(step_id: str) -> str:
    """Make a step ID safe for Mermaid node identifiers."""
    return step_id.replace("-", "_").replace(" ", "_").replace(".", "_")


def build_node_label(step: dict[str, Any], annotate_models: bool, annotate_cost: bool) -> str:
    """Build the display label for a workflow node."""
    step_id = step.get("id", "?")
    agent = step.get("agent", "")
    desc = step.get("description", "")
    model = step.get("model", "")
    parallel = step.get("parallel_branches", 1)

    parts: list[str] = []

    # Primary label
    if desc:
        parts.append(f"<b>{step_id}</b><br/>{desc}")
    else:
        parts.append(f"<b>{step_id}</b>")

    # Agent
    if agent:
        parts.append(f"<i>{agent}</i>")

    # Model annotation
    if annotate_models and model:
        short = MODEL_SHORT_NAMES.get(model, model.split("/")[-1])
        parts.append(f"[{short}]")

    # Parallel branches
    if parallel > 1:
        parts.append(f"x{parallel} branches")

    # Cost annotation
    if annotate_cost:
        input_t = step.get("estimated_input_tokens", 0)
        output_t = step.get("estimated_output_tokens", 0)
        if input_t or output_t:
            parts.append(f"{input_t + output_t:,} tok")

    return "<br/>".join(parts)


def detect_patterns(steps: list[dict[str, Any]]) -> list[dict[str, str]]:
    """Detect orchestration patterns in the workflow."""
    patterns: list[dict[str, str]] = []
    all_ids = {s["id"] for s in steps}

    # Build dependency map
    dependents: dict[str, list[str]] = {s["id"]: [] for s in steps}
    for s in steps:
        for dep in s.get("depends_on", []):
            if dep in dependents:
                dependents[dep].append(s["id"])

    # Fan-out: one node with multiple dependents
    for sid, deps in dependents.items():
        if len(deps) >= 3:
            patterns.append({
                "pattern": "fan-out",
                "source": sid,
                "targets": ", ".join(deps),
            })

    # Fan-in: one node with multiple dependencies
    for s in steps:
        deps = s.get("depends_on", [])
        if len(deps) >= 3:
            patterns.append({
                "pattern": "fan-in",
                "target": s["id"],
                "sources": ", ".join(deps),
            })

    # Sequential chain detection
    chain: list[str] = []
    for s in steps:
        deps = s.get("depends_on", [])
        if not deps:
            # Potential chain start
            current = s["id"]
            seq = [current]
            while True:
                next_nodes = dependents.get(current, [])
                if len(next_nodes) == 1:
                    next_node = next_nodes[0]
                    # Check the next node only depends on current
                    next_step = next((st for st in steps if st["id"] == next_node), None)
                    if next_step and len(next_step.get("depends_on", [])) == 1:
                        seq.append(next_node)
                        current = next_node
                    else:
                        break
                else:
                    break
            if len(seq) >= 3:
                chain = seq
                patterns.append({
                    "pattern": "sequential-pipeline",
                    "chain": " -> ".join(seq),
                })

    return patterns


def generate_mermaid(
    workflow: dict[str, Any],
    direction: str = "TD",
    annotate_models: bool = False,
    annotate_cost: bool = False,
) -> str:
    """Generate a Mermaid diagram string from the workflow."""
    steps = workflow.get("steps", [])
    name = workflow.get("name", "workflow")

    lines: list[str] = []
    lines.append(f"---")
    lines.append(f"title: {name}")
    lines.append(f"---")
    lines.append(f"graph {direction}")

    # Nodes
    entry_ids: set[str] = set()
    terminal_ids: set[str] = set()
    agents_used: set[str] = set()

    for step in steps:
        sid = sanitize_id(step["id"])
        label = build_node_label(step, annotate_models, annotate_cost)
        deps = step.get("depends_on", [])
        agent = step.get("agent", "")
        is_terminal = step.get("terminal", False)

        if not deps:
            entry_ids.add(sid)
        if is_terminal:
            terminal_ids.add(sid)
        if agent:
            agents_used.add(agent)

        # Node shape: entry = stadium, terminal = double circle, default = rounded rect
        if not deps:
            lines.append(f"    {sid}([{label}])")
        elif is_terminal:
            lines.append(f"    {sid}(({label}))")
        else:
            lines.append(f"    {sid}[{label}]")

    lines.append("")

    # Edges
    for step in steps:
        sid = sanitize_id(step["id"])
        for dep in step.get("depends_on", []):
            dep_safe = sanitize_id(dep)
            lines.append(f"    {dep_safe} --> {sid}")

    lines.append("")

    # Style classes based on agent
    styled_agents: set[str] = set()
    for step in steps:
        agent = step.get("agent", "")
        sid = sanitize_id(step["id"])
        if agent in AGENT_STYLES:
            class_name = f"cls_{agent}"
            if agent not in styled_agents:
                style = AGENT_STYLES[agent]
                lines.append(f"    classDef {class_name} {style}")
                styled_agents.add(agent)
            lines.append(f"    class {sid} {class_name}")

    return "\n".join(lines)


def build_result(
    workflow: dict[str, Any],
    mermaid: str,
    direction: str,
    annotate_models: bool,
    annotate_cost: bool,
) -> dict[str, Any]:
    """Build the full result dict."""
    steps = workflow.get("steps", [])
    patterns = detect_patterns(steps)

    entry_points = [s["id"] for s in steps if not s.get("depends_on")]
    terminal_nodes = [s["id"] for s in steps if s.get("terminal", False)]
    agents = sorted({s.get("agent", "") for s in steps if s.get("agent")})
    edge_count = sum(len(s.get("depends_on", [])) for s in steps)

    return {
        "workflow": workflow.get("name", "<unnamed>"),
        "step_count": len(steps),
        "edge_count": edge_count,
        "entry_points": entry_points,
        "terminal_nodes": terminal_nodes,
        "agents": agents,
        "patterns_detected": patterns,
        "options": {
            "direction": direction,
            "annotate_models": annotate_models,
            "annotate_cost": annotate_cost,
        },
        "mermaid": mermaid,
    }


def format_human(result: dict[str, Any]) -> str:
    """Format results for human reading."""
    lines: list[str] = []
    lines.append(f"Workflow: {result['workflow']}")
    lines.append(f"Steps:    {result['step_count']}, Edges: {result['edge_count']}")
    lines.append(f"Agents:   {', '.join(result['agents']) if result['agents'] else 'none specified'}")

    if result["entry_points"]:
        lines.append(f"Entry:    {', '.join(result['entry_points'])}")
    if result["terminal_nodes"]:
        lines.append(f"Terminal: {', '.join(result['terminal_nodes'])}")

    if result["patterns_detected"]:
        lines.append("")
        lines.append("Detected Patterns:")
        for p in result["patterns_detected"]:
            pattern = p.get("pattern", "unknown")
            if pattern == "fan-out":
                lines.append(f"  Fan-out: {p['source']} -> [{p['targets']}]")
            elif pattern == "fan-in":
                lines.append(f"  Fan-in:  [{p['sources']}] -> {p['target']}")
            elif pattern == "sequential-pipeline":
                lines.append(f"  Sequential: {p['chain']}")

    lines.append("")
    lines.append("Mermaid Diagram:")
    lines.append("```mermaid")
    lines.append(result["mermaid"])
    lines.append("```")
    lines.append("")
    lines.append("Copy the mermaid block into any compatible renderer")
    lines.append("(GitHub, Notion, mermaid.live, VS Code preview, etc.)")

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate Mermaid diagrams from agent workflow definitions",
        epilog="Paste output into mermaid.live or any Mermaid-compatible renderer.",
    )
    parser.add_argument("file", nargs="?", help="Path to workflow JSON file")
    parser.add_argument("--stdin", action="store_true", help="Read workflow from stdin")
    parser.add_argument("--json", action="store_true", dest="json_output",
                        help="Output full results as JSON (includes mermaid field)")
    parser.add_argument("--direction", choices=["TD", "LR", "BT", "RL"], default="TD",
                        help="Graph direction: TD (top-down), LR (left-right), etc. (default: TD)")
    parser.add_argument("--annotate-models", action="store_true",
                        help="Show model names on each node")
    parser.add_argument("--annotate-cost", action="store_true",
                        help="Show estimated token counts on each node")
    parser.add_argument("--raw", action="store_true",
                        help="Output only the raw Mermaid text (no wrapper)")
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

    mermaid = generate_mermaid(
        workflow,
        direction=args.direction,
        annotate_models=args.annotate_models,
        annotate_cost=args.annotate_cost,
    )

    if args.raw:
        print(mermaid)
        return 0

    result = build_result(workflow, mermaid, args.direction,
                          args.annotate_models, args.annotate_cost)

    if args.json_output:
        print(json.dumps(result, indent=2))
    else:
        print(format_human(result))

    return 0


if __name__ == "__main__":
    sys.exit(main())
