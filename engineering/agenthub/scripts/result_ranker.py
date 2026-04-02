#!/usr/bin/env python3
"""Rank and merge outputs from multiple agents in a workflow.

Scores agent outputs on completeness, length, structure, and relevance.
Supports different merge strategies: synthesize (combine complementary),
rank-select (pick best), and chain (use final).

Usage:
    python result_ranker.py --session session.json --list-outputs
    python result_ranker.py --session session.json --rank
    python result_ranker.py --session session.json --merge synthesize
    python result_ranker.py --session session.json --merge rank-select --json
"""

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path


def load_session(path):
    """Load session with agent outputs."""
    try:
        with open(path, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"Error loading session: {e}", file=sys.stderr)
        sys.exit(1)


def extract_outputs(session):
    """Extract completed agent outputs from session."""
    agents = session.get("agents", {})
    outputs = []
    for agent_id, agent_data in agents.items():
        if agent_data.get("state") == "COMPLETED" and agent_data.get("outputs"):
            outputs.append({
                "agent_id": agent_id,
                "state": agent_data["state"],
                "outputs": agent_data["outputs"],
                "duration_s": agent_data.get("duration_s", 0),
                "eval_score": agent_data.get("eval_score"),
                "task": agent_data.get("task", ""),
            })
    return outputs


def score_output(output):
    """Score an individual agent output on quality dimensions."""
    scores = {}
    output_data = output.get("outputs", {})

    # Completeness: fraction of output fields that are non-empty
    total_fields = len(output_data)
    non_empty = sum(1 for v in output_data.values() if v)
    scores["completeness"] = non_empty / total_fields if total_fields > 0 else 0

    # Depth: total content length across all output fields
    total_length = 0
    for value in output_data.values():
        if isinstance(value, str):
            total_length += len(value)
        elif isinstance(value, (list, dict)):
            total_length += len(json.dumps(value))
    # Normalize: 500 chars is minimal, 5000 is good, cap at 1.0
    scores["depth"] = min(1.0, total_length / 5000) if total_length > 0 else 0

    # Structure: presence of structured data (lists, dicts, headers)
    has_structure = 0
    for value in output_data.values():
        if isinstance(value, (list, dict)):
            has_structure += 1
        elif isinstance(value, str):
            if re.search(r"^#+\s|\n-\s|\n\d+\.\s", value):
                has_structure += 1
    scores["structure"] = has_structure / total_fields if total_fields > 0 else 0

    # Use existing eval score if available
    if output.get("eval_score") is not None:
        scores["eval"] = output["eval_score"]
    else:
        scores["eval"] = None

    # Composite score
    weights = {"completeness": 0.3, "depth": 0.3, "structure": 0.2}
    weighted_sum = sum(scores[k] * w for k, w in weights.items())
    total_weight = sum(weights.values())

    if scores["eval"] is not None:
        weighted_sum += scores["eval"] * 0.2
        total_weight += 0.2

    scores["composite"] = round(weighted_sum / total_weight, 3) if total_weight > 0 else 0

    return scores


def rank_outputs(outputs):
    """Rank outputs by quality score."""
    ranked = []
    for output in outputs:
        scores = score_output(output)
        ranked.append({
            **output,
            "scores": scores,
        })
    ranked.sort(key=lambda x: -x["scores"]["composite"])
    return ranked


def merge_synthesize(ranked_outputs):
    """Synthesize complementary outputs into a unified result."""
    sections = {}
    for output in ranked_outputs:
        agent_id = output["agent_id"]
        task = output.get("task", agent_id)
        output_data = output.get("outputs", {})

        for key, value in output_data.items():
            section_key = key
            if section_key not in sections:
                sections[section_key] = {
                    "content": value,
                    "source": agent_id,
                    "score": output["scores"]["composite"],
                }
            else:
                # If existing has lower score, prefer new
                if output["scores"]["composite"] > sections[section_key]["score"]:
                    sections[section_key] = {
                        "content": value,
                        "source": agent_id,
                        "score": output["scores"]["composite"],
                    }

    merged = {}
    attribution = {}
    for key, section in sections.items():
        merged[key] = section["content"]
        attribution[key] = section["source"]

    return {
        "strategy": "synthesize",
        "merged_output": merged,
        "attribution": attribution,
        "sections_count": len(merged),
        "sources_count": len(set(attribution.values())),
    }


def merge_rank_select(ranked_outputs):
    """Select the best output from competing agents."""
    if not ranked_outputs:
        return {"strategy": "rank-select", "selected": None, "reason": "No outputs available"}

    best = ranked_outputs[0]
    return {
        "strategy": "rank-select",
        "selected_agent": best["agent_id"],
        "selected_output": best["outputs"],
        "score": best["scores"]["composite"],
        "runner_up": ranked_outputs[1]["agent_id"] if len(ranked_outputs) > 1 else None,
        "runner_up_score": ranked_outputs[1]["scores"]["composite"] if len(ranked_outputs) > 1 else None,
        "total_candidates": len(ranked_outputs),
    }


def merge_chain(session):
    """Use the output of the last agent in the pipeline."""
    agents = session.get("agents", {})
    # Find terminal agent (no dependents)
    all_deps = set()
    for agent_data in agents.values():
        all_deps.update(agent_data.get("dependencies", []))

    terminal_agents = [
        aid for aid in agents
        if aid not in all_deps and agents[aid].get("state") == "COMPLETED"
    ]

    if not terminal_agents:
        return {"strategy": "chain", "error": "No completed terminal agent found"}

    # If multiple terminals, pick the one with highest eval score
    best_terminal = None
    best_score = -1
    for aid in terminal_agents:
        score = agents[aid].get("eval_score", 0) or 0
        if score > best_score:
            best_score = score
            best_terminal = aid

    return {
        "strategy": "chain",
        "terminal_agent": best_terminal,
        "output": agents[best_terminal].get("outputs", {}),
        "eval_score": best_score,
    }


def format_human(result, action):
    """Format result for human output."""
    output = []
    output.append("=" * 60)
    output.append("RESULT RANKER")
    output.append("=" * 60)

    if action == "list":
        output.append(f"\nAgent Outputs ({len(result['outputs'])} completed)")
        output.append("-" * 60)
        for o in result["outputs"]:
            output_keys = list(o.get("outputs", {}).keys())
            output.append(f"  {o['agent_id']}")
            output.append(f"    State: {o['state']} | Duration: {o.get('duration_s', 0)}s")
            output.append(f"    Outputs: {', '.join(output_keys[:5])}")
            if o.get("eval_score") is not None:
                output.append(f"    Eval: {o['eval_score']}")

    elif action == "rank":
        output.append(f"\nRanked Outputs ({len(result['ranked'])} agents)")
        output.append("-" * 60)
        output.append(f"  {'Rank':<6} {'Agent':<20} {'Score':>8} {'Comp':>6} {'Depth':>6} {'Struct':>6}")
        output.append(f"  {'─' * 6} {'─' * 20} {'─' * 8} {'─' * 6} {'─' * 6} {'─' * 6}")
        for i, r in enumerate(result["ranked"], 1):
            s = r["scores"]
            output.append(
                f"  {i:<6} {r['agent_id']:<20} {s['composite']:>8.3f} "
                f"{s['completeness']:>5.2f} {s['depth']:>5.2f} {s['structure']:>5.2f}"
            )

    elif action == "merge":
        merge_result = result["merge_result"]
        strategy = merge_result.get("strategy", "?")
        output.append(f"\nMerge Strategy: {strategy}")
        output.append("-" * 60)

        if strategy == "synthesize":
            output.append(f"  Sections: {merge_result['sections_count']}")
            output.append(f"  Sources:  {merge_result['sources_count']} agents")
            output.append("\n  Attribution:")
            for key, source in merge_result.get("attribution", {}).items():
                output.append(f"    {key} <- {source}")

        elif strategy == "rank-select":
            output.append(f"  Selected: {merge_result.get('selected_agent', '?')} (score: {merge_result.get('score', 0):.3f})")
            if merge_result.get("runner_up"):
                output.append(f"  Runner-up: {merge_result['runner_up']} (score: {merge_result['runner_up_score']:.3f})")

        elif strategy == "chain":
            output.append(f"  Terminal agent: {merge_result.get('terminal_agent', '?')}")

    return "\n".join(output)


def main():
    parser = argparse.ArgumentParser(
        description="Rank and merge outputs from multiple agents.",
        epilog="Example: python result_ranker.py --session session.json --rank",
    )
    parser.add_argument("--session", required=True, help="Path to session JSON file")
    parser.add_argument("--list-outputs", action="store_true", help="List all agent outputs")
    parser.add_argument("--rank", action="store_true", help="Rank outputs by quality")
    parser.add_argument("--merge", choices=["synthesize", "rank-select", "chain"], help="Merge strategy")
    parser.add_argument("--json", action="store_true", dest="json_output", help="Output as JSON")

    args = parser.parse_args()

    session_path = Path(args.session)
    if not session_path.exists():
        print(f"Error: Session file '{args.session}' not found.", file=sys.stderr)
        sys.exit(1)

    session = load_session(session_path)
    outputs = extract_outputs(session)

    if args.list_outputs:
        result = {"outputs": outputs}
        action = "list"
    elif args.rank:
        ranked = rank_outputs(outputs)
        result = {"ranked": ranked}
        action = "rank"
    elif args.merge:
        ranked = rank_outputs(outputs)
        if args.merge == "synthesize":
            merge_result = merge_synthesize(ranked)
        elif args.merge == "rank-select":
            merge_result = merge_rank_select(ranked)
        elif args.merge == "chain":
            merge_result = merge_chain(session)
        result = {"merge_result": merge_result}
        action = "merge"
    else:
        parser.print_help()
        sys.exit(1)

    if args.json_output:
        print(json.dumps(result, indent=2, default=str))
    else:
        print(format_human(result, action))


if __name__ == "__main__":
    main()
