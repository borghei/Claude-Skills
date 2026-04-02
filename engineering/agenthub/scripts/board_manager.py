#!/usr/bin/env python3
"""Manage agent task boards with status tracking for multi-agent workflows.

Provides a visual dashboard of agent states within an orchestration session.
Supports multiple view modes: board (kanban), timeline, summary.

Usage:
    python board_manager.py --session session.json --view board
    python board_manager.py --session session.json --view timeline
    python board_manager.py --session session.json --agent researcher --detail
    python board_manager.py --session session.json --json

Expected session.json format:
{
    "session_id": "abc123",
    "workflow_name": "market-analysis",
    "started_at": "2026-04-02T10:30:00",
    "agents": {
        "researcher": {"state": "COMPLETED", "started_at": "...", "completed_at": "...", "duration_s": 90, "outputs": {...}},
        "data_collector": {"state": "RUNNING", "started_at": "...", "duration_s": null},
        "analyst": {"state": "PENDING", "dependencies": ["data_collector", "researcher"]},
        "writer": {"state": "PENDING", "dependencies": ["analyst"]}
    }
}
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path


STATE_SYMBOLS = {
    "COMPLETED": "[x]",
    "RUNNING": "[>]",
    "PENDING": "[ ]",
    "FAILED": "[!]",
    "SKIPPED": "[-]",
    "READY": "[~]",
    "EVALUATING": "[?]",
}

STATE_ORDER = {
    "RUNNING": 0,
    "READY": 1,
    "EVALUATING": 2,
    "PENDING": 3,
    "COMPLETED": 4,
    "FAILED": 5,
    "SKIPPED": 6,
}


def load_session(path):
    """Load session state from JSON file."""
    try:
        with open(path, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"Error loading session: {e}", file=sys.stderr)
        sys.exit(1)


def compute_elapsed(session):
    """Compute elapsed time since session start."""
    started = session.get("started_at", "")
    if not started:
        return 0
    try:
        start_dt = datetime.fromisoformat(started)
        return (datetime.now() - start_dt).total_seconds()
    except ValueError:
        return 0


def format_duration(seconds):
    """Format seconds as Xm Ys."""
    if seconds is None or seconds == 0:
        return "---"
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    if minutes > 0:
        return f"{minutes}m {secs:02d}s"
    return f"{secs}s"


def group_by_state(agents):
    """Group agents by their current state."""
    groups = {}
    for agent_id, agent_data in agents.items():
        state = agent_data.get("state", "PENDING")
        if state not in groups:
            groups[state] = []
        groups[state].append({"id": agent_id, **agent_data})
    return groups


def render_board_view(session):
    """Render kanban-style board view."""
    agents = session.get("agents", {})
    groups = group_by_state(agents)
    elapsed = compute_elapsed(session)

    lines = []
    lines.append(f"AgentHub Board - Session: {session.get('session_id', '?')}")
    lines.append(f"Workflow: {session.get('workflow_name', '?')}")
    lines.append(f"Started: {session.get('started_at', '?')[:19]} | Elapsed: {format_duration(elapsed)}")
    lines.append("")

    # Column layout
    column_order = ["RUNNING", "READY", "EVALUATING", "PENDING", "COMPLETED", "FAILED", "SKIPPED"]
    active_columns = [s for s in column_order if s in groups]

    if not active_columns:
        lines.append("  No agents in session.")
        return "\n".join(lines)

    # Header
    col_width = 22
    header = ""
    for state in active_columns:
        count = len(groups[state])
        header += f"{state} ({count})".ljust(col_width)
    lines.append(header)
    lines.append("─" * (col_width * len(active_columns)))

    # Find max rows
    max_rows = max(len(groups[s]) for s in active_columns)

    for row in range(max_rows):
        row_line = ""
        for state in active_columns:
            if row < len(groups[state]):
                agent = groups[state][row]
                symbol = STATE_SYMBOLS.get(state, "[?]")
                duration = format_duration(agent.get("duration_s"))
                entry = f"{symbol} {agent['id'][:14]}"
                if state in ("COMPLETED", "RUNNING"):
                    entry += f" {duration}"
                row_line += entry.ljust(col_width)
            else:
                row_line += " " * col_width
        lines.append(row_line)

    # Show pending dependencies
    pending = groups.get("PENDING", [])
    if pending:
        lines.append("")
        lines.append("WAITING ON:")
        for agent in pending:
            deps = agent.get("dependencies", [])
            if deps:
                lines.append(f"  {agent['id']} <- {', '.join(deps)}")

    return "\n".join(lines)


def render_timeline_view(session):
    """Render timeline/gantt-style view."""
    agents = session.get("agents", {})
    elapsed = compute_elapsed(session)

    lines = []
    lines.append(f"AgentHub Timeline - Session: {session.get('session_id', '?')}")
    lines.append(f"Elapsed: {format_duration(elapsed)}")
    lines.append("")

    # Sort by start time, then by state
    sorted_agents = sorted(
        agents.items(),
        key=lambda x: (
            STATE_ORDER.get(x[1].get("state", "PENDING"), 9),
            x[1].get("started_at", "z"),
        ),
    )

    max_name_len = max(len(aid) for aid, _ in sorted_agents) if sorted_agents else 10
    bar_width = 40

    for agent_id, agent_data in sorted_agents:
        state = agent_data.get("state", "PENDING")
        duration = agent_data.get("duration_s", 0) or 0
        symbol = STATE_SYMBOLS.get(state, "[?]")

        # Proportional bar
        if elapsed > 0 and duration > 0:
            bar_len = max(1, int(duration / max(elapsed, 1) * bar_width))
        elif state == "RUNNING":
            bar_len = max(1, int(bar_width * 0.3))
        else:
            bar_len = 0

        bar_char = {"COMPLETED": "=", "RUNNING": ">", "FAILED": "x", "PENDING": ".", "READY": "~"}
        char = bar_char.get(state, " ")
        bar = char * bar_len

        name = agent_id.ljust(max_name_len)
        dur_str = format_duration(duration if duration else None)
        lines.append(f"  {symbol} {name}  [{bar:<{bar_width}}]  {dur_str}")

    return "\n".join(lines)


def render_summary_view(session):
    """Render compact one-line-per-agent summary."""
    agents = session.get("agents", {})
    elapsed = compute_elapsed(session)

    total = len(agents)
    completed = sum(1 for a in agents.values() if a.get("state") == "COMPLETED")
    failed = sum(1 for a in agents.values() if a.get("state") == "FAILED")
    running = sum(1 for a in agents.values() if a.get("state") == "RUNNING")

    progress_pct = int(completed / total * 100) if total else 0
    bar_len = int(progress_pct / 5)
    progress_bar = "█" * bar_len + "░" * (20 - bar_len)

    lines = []
    lines.append(f"Session: {session.get('session_id', '?')} | {session.get('workflow_name', '?')}")
    lines.append(f"Progress: [{progress_bar}] {progress_pct}% ({completed}/{total})")
    lines.append(f"Running: {running} | Failed: {failed} | Elapsed: {format_duration(elapsed)}")
    lines.append("")
    lines.append(f"{'Agent':<20} {'State':<12} {'Duration':<10}")
    lines.append("─" * 42)

    for agent_id, agent_data in sorted(agents.items(), key=lambda x: STATE_ORDER.get(x[1].get("state", "PENDING"), 9)):
        state = agent_data.get("state", "PENDING")
        duration = format_duration(agent_data.get("duration_s"))
        lines.append(f"{agent_id:<20} {state:<12} {duration:<10}")

    return "\n".join(lines)


def render_agent_detail(session, agent_id):
    """Render detailed view for a specific agent."""
    agents = session.get("agents", {})
    if agent_id not in agents:
        return f"Agent '{agent_id}' not found in session."

    agent = agents[agent_id]
    lines = []
    lines.append(f"Agent Detail: {agent_id}")
    lines.append("=" * 50)
    lines.append(f"  State:        {agent.get('state', 'PENDING')}")
    lines.append(f"  Started:      {agent.get('started_at', '---')}")
    lines.append(f"  Completed:    {agent.get('completed_at', '---')}")
    lines.append(f"  Duration:     {format_duration(agent.get('duration_s'))}")
    lines.append(f"  Dependencies: {', '.join(agent.get('dependencies', [])) or 'none'}")
    lines.append(f"  Retries:      {agent.get('retries', 0)}")

    if agent.get("task"):
        lines.append(f"  Task:         {agent['task'][:60]}")
    if agent.get("error"):
        lines.append(f"  Error:        {agent['error'][:80]}")
    if agent.get("outputs"):
        lines.append(f"  Outputs:      {json.dumps(agent['outputs'], indent=2)[:200]}")
    if agent.get("eval_score") is not None:
        lines.append(f"  Eval score:   {agent['eval_score']}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Manage agent task boards with status tracking.",
        epilog="Example: python board_manager.py --session session.json --view board",
    )
    parser.add_argument("--session", required=True, help="Path to session state JSON file")
    parser.add_argument("--view", choices=["board", "timeline", "summary"], default="board", help="View mode")
    parser.add_argument("--agent", help="Show detail for a specific agent")
    parser.add_argument("--json", action="store_true", dest="json_output", help="Output as JSON")

    args = parser.parse_args()

    session_path = Path(args.session)
    if not session_path.exists():
        print(f"Error: Session file '{args.session}' not found.", file=sys.stderr)
        sys.exit(1)

    session = load_session(session_path)

    if args.json_output:
        agents = session.get("agents", {})
        result = {
            "session_id": session.get("session_id"),
            "workflow_name": session.get("workflow_name"),
            "elapsed_s": compute_elapsed(session),
            "total_agents": len(agents),
            "by_state": {},
            "agents": agents,
        }
        for state in set(a.get("state", "PENDING") for a in agents.values()):
            result["by_state"][state] = sum(1 for a in agents.values() if a.get("state") == state)
        print(json.dumps(result, indent=2))
    elif args.agent:
        print(render_agent_detail(session, args.agent))
    elif args.view == "board":
        print(render_board_view(session))
    elif args.view == "timeline":
        print(render_timeline_view(session))
    elif args.view == "summary":
        print(render_summary_view(session))


if __name__ == "__main__":
    main()
