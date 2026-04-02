#!/usr/bin/env python3
"""Manage orchestration sessions for multi-agent workflows.

Creates, updates, and queries session state. A session tracks the execution
lifecycle of a workflow including agent states, outputs, timing, and history.

Usage:
    python session_manager.py create --workflow workflow.json --output session.json
    python session_manager.py status --session session.json
    python session_manager.py update --session session.json --agent researcher --state COMPLETED --output-data '{"result": "..."}'
    python session_manager.py history --session session.json
    python session_manager.py list --dir ./sessions/
"""

import argparse
import json
import os
import sys
import uuid
from datetime import datetime
from pathlib import Path


def load_json(path):
    """Load JSON from file."""
    try:
        with open(path, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"Error loading {path}: {e}", file=sys.stderr)
        sys.exit(1)


def save_json(data, path):
    """Save JSON to file."""
    with open(path, "w") as f:
        json.dump(data, f, indent=2, default=str)


def cmd_create(args):
    """Create a new orchestration session from a workflow definition."""
    workflow = load_json(args.workflow)
    agents_def = workflow.get("agents", {})
    config = workflow.get("config", {})

    session_id = str(uuid.uuid4())[:8]
    now = datetime.now().isoformat()

    agents = {}
    for agent_id, agent_def in agents_def.items():
        deps = agent_def.get("dependencies", [])
        agents[agent_id] = {
            "state": "READY" if not deps else "PENDING",
            "task": agent_def.get("task", ""),
            "inputs": agent_def.get("inputs", []),
            "expected_outputs": agent_def.get("outputs", []),
            "dependencies": deps,
            "outputs": None,
            "started_at": None,
            "completed_at": None,
            "duration_s": None,
            "retries": 0,
            "max_retries": agent_def.get("config", {}).get("retries", config.get("retry_on_failure", 1)),
            "eval_score": None,
            "error": None,
        }

    session = {
        "session_id": session_id,
        "workflow_name": workflow.get("name", "unnamed"),
        "workflow_description": workflow.get("description", ""),
        "created_at": now,
        "started_at": now,
        "completed_at": None,
        "state": "RUNNING",
        "config": config,
        "agents": agents,
        "history": [
            {"timestamp": now, "event": "session_created", "detail": f"Workflow: {workflow.get('name', 'unnamed')}"}
        ],
    }

    output_path = args.output or f"session-{session_id}.json"
    save_json(session, output_path)

    return {
        "action": "create",
        "session_id": session_id,
        "workflow_name": workflow.get("name"),
        "agents_count": len(agents),
        "ready_agents": sum(1 for a in agents.values() if a["state"] == "READY"),
        "output_file": output_path,
    }


def cmd_status(args):
    """Show current session status."""
    session = load_json(args.session)
    agents = session.get("agents", {})

    by_state = {}
    for agent_data in agents.values():
        state = agent_data.get("state", "UNKNOWN")
        by_state[state] = by_state.get(state, 0) + 1

    total = len(agents)
    completed = by_state.get("COMPLETED", 0)
    failed = by_state.get("FAILED", 0)
    running = by_state.get("RUNNING", 0)

    # Determine overall health
    if session.get("state") == "COMPLETED":
        health = "COMPLETE"
    elif failed > 0 and running == 0 and by_state.get("PENDING", 0) > 0:
        health = "BLOCKED"
    elif failed > 0:
        health = "AT_RISK"
    elif running > 0:
        health = "RUNNING"
    else:
        health = "IDLE"

    # Elapsed time
    started = session.get("started_at", "")
    elapsed = 0
    if started:
        try:
            elapsed = (datetime.now() - datetime.fromisoformat(started)).total_seconds()
        except ValueError:
            pass

    return {
        "action": "status",
        "session_id": session.get("session_id"),
        "workflow_name": session.get("workflow_name"),
        "state": session.get("state"),
        "health": health,
        "total_agents": total,
        "by_state": by_state,
        "progress_pct": round(completed / total * 100, 1) if total else 0,
        "elapsed_s": round(elapsed),
        "agents": {
            aid: {
                "state": adata.get("state"),
                "duration_s": adata.get("duration_s"),
                "eval_score": adata.get("eval_score"),
            }
            for aid, adata in agents.items()
        },
    }


def cmd_update(args):
    """Update an agent's state in the session."""
    session = load_json(args.session)
    agents = session.get("agents", {})

    if args.agent not in agents:
        return {"action": "update", "error": f"Agent '{args.agent}' not found"}

    agent = agents[args.agent]
    old_state = agent["state"]
    now = datetime.now().isoformat()

    # Update state
    agent["state"] = args.state

    if args.state == "RUNNING" and not agent.get("started_at"):
        agent["started_at"] = now
    elif args.state == "COMPLETED":
        agent["completed_at"] = now
        if agent.get("started_at"):
            try:
                started = datetime.fromisoformat(agent["started_at"])
                agent["duration_s"] = round((datetime.now() - started).total_seconds(), 1)
            except ValueError:
                pass
    elif args.state == "FAILED":
        agent["completed_at"] = now
        agent["error"] = args.error_msg or "Unknown error"

    # Update outputs if provided
    if args.output_data:
        try:
            agent["outputs"] = json.loads(args.output_data)
        except json.JSONDecodeError:
            agent["outputs"] = {"raw": args.output_data}

    # Update eval score if provided
    if args.eval_score is not None:
        agent["eval_score"] = args.eval_score

    # Check if dependents can now be set to READY
    newly_ready = []
    if args.state == "COMPLETED":
        for other_id, other_agent in agents.items():
            if other_agent["state"] == "PENDING":
                deps = other_agent.get("dependencies", [])
                all_met = all(
                    agents.get(d, {}).get("state") == "COMPLETED"
                    for d in deps
                )
                if all_met:
                    other_agent["state"] = "READY"
                    newly_ready.append(other_id)

    # Check if all agents are done
    all_done = all(
        a["state"] in ("COMPLETED", "FAILED", "SKIPPED")
        for a in agents.values()
    )
    if all_done:
        session["state"] = "COMPLETED"
        session["completed_at"] = now

    # Log event
    event = {
        "timestamp": now,
        "event": "agent_state_change",
        "agent": args.agent,
        "old_state": old_state,
        "new_state": args.state,
    }
    if newly_ready:
        event["newly_ready"] = newly_ready
    session.setdefault("history", []).append(event)

    save_json(session, args.session)

    return {
        "action": "update",
        "agent": args.agent,
        "old_state": old_state,
        "new_state": args.state,
        "newly_ready": newly_ready,
        "session_complete": all_done,
    }


def cmd_history(args):
    """Show session event history."""
    session = load_json(args.session)
    history = session.get("history", [])
    return {
        "action": "history",
        "session_id": session.get("session_id"),
        "event_count": len(history),
        "events": history,
    }


def cmd_list(args):
    """List all sessions in a directory."""
    sessions_dir = Path(args.dir)
    if not sessions_dir.is_dir():
        return {"action": "list", "error": f"'{args.dir}' is not a directory"}

    sessions = []
    for jf in sorted(sessions_dir.glob("session-*.json")):
        try:
            data = json.loads(jf.read_text())
            sessions.append({
                "file": str(jf),
                "session_id": data.get("session_id"),
                "workflow_name": data.get("workflow_name"),
                "state": data.get("state"),
                "created_at": data.get("created_at"),
                "agents_count": len(data.get("agents", {})),
            })
        except (json.JSONDecodeError, OSError):
            continue

    return {"action": "list", "count": len(sessions), "sessions": sessions}


def format_human(result):
    """Format result for human output."""
    action = result.get("action", "unknown")
    lines = []

    if "error" in result:
        return f"Error: {result['error']}"

    if action == "create":
        lines.append(f"Session Created: {result['session_id']}")
        lines.append(f"  Workflow: {result['workflow_name']}")
        lines.append(f"  Agents:  {result['agents_count']} ({result['ready_agents']} ready)")
        lines.append(f"  File:    {result['output_file']}")

    elif action == "status":
        lines.append(f"Session: {result['session_id']} ({result['workflow_name']})")
        lines.append(f"  Health:   {result['health']}")
        lines.append(f"  Progress: {result['progress_pct']}% ({result['by_state']})")
        lines.append(f"  Elapsed:  {result['elapsed_s']}s")
        lines.append("")
        for aid, adata in result.get("agents", {}).items():
            dur = f"{adata['duration_s']}s" if adata.get("duration_s") else "---"
            lines.append(f"  {aid:<20} {adata['state']:<12} {dur}")

    elif action == "update":
        lines.append(f"Updated: {result['agent']} ({result['old_state']} -> {result['new_state']})")
        if result.get("newly_ready"):
            lines.append(f"  Newly ready: {', '.join(result['newly_ready'])}")
        if result.get("session_complete"):
            lines.append("  Session is now COMPLETE")

    elif action == "history":
        lines.append(f"Session History ({result['event_count']} events)")
        lines.append("-" * 50)
        for evt in result.get("events", []):
            ts = evt.get("timestamp", "")[:19]
            event_type = evt.get("event", "")
            detail = evt.get("detail", "")
            agent = evt.get("agent", "")
            if agent:
                lines.append(f"  {ts}  {event_type}: {agent} ({evt.get('old_state', '')} -> {evt.get('new_state', '')})")
            else:
                lines.append(f"  {ts}  {event_type}: {detail}")

    elif action == "list":
        lines.append(f"Sessions ({result['count']} found)")
        lines.append("-" * 60)
        for s in result.get("sessions", []):
            lines.append(f"  {s['session_id']}  {s['workflow_name']:<20}  {s['state']:<12}  {s['agents_count']} agents")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Manage orchestration sessions for multi-agent workflows.",
    )
    parser.add_argument("--json", action="store_true", dest="json_output", help="Output as JSON")

    sub = parser.add_subparsers(dest="command")

    p_create = sub.add_parser("create", help="Create a new session")
    p_create.add_argument("--workflow", required=True, help="Path to workflow JSON")
    p_create.add_argument("--output", help="Output session file path")

    p_status = sub.add_parser("status", help="Show session status")
    p_status.add_argument("--session", required=True, help="Path to session JSON")

    p_update = sub.add_parser("update", help="Update agent state")
    p_update.add_argument("--session", required=True, help="Path to session JSON")
    p_update.add_argument("--agent", required=True, help="Agent ID to update")
    p_update.add_argument("--state", required=True,
                          choices=["PENDING", "READY", "RUNNING", "COMPLETED", "FAILED", "SKIPPED", "EVALUATING"])
    p_update.add_argument("--output-data", help="Agent output data (JSON string)")
    p_update.add_argument("--eval-score", type=float, help="Evaluation score (0-1)")
    p_update.add_argument("--error-msg", help="Error message (for FAILED state)")

    p_history = sub.add_parser("history", help="Show session event history")
    p_history.add_argument("--session", required=True, help="Path to session JSON")

    p_list = sub.add_parser("list", help="List sessions in a directory")
    p_list.add_argument("--dir", required=True, help="Directory containing session files")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    commands = {
        "create": cmd_create,
        "status": cmd_status,
        "update": cmd_update,
        "history": cmd_history,
        "list": cmd_list,
    }

    result = commands[args.command](args)

    if args.json_output:
        print(json.dumps(result, indent=2, default=str))
    else:
        print(format_human(result))


if __name__ == "__main__":
    main()
