#!/usr/bin/env python3
"""Estimate token usage and dollar cost for agent workflow execution.

Takes a workflow definition with step-level token and model annotations, then
calculates per-step and total costs using published pricing.  Supports model
tiering analysis (what-if you swapped Sonnet for Haiku on routing steps?).

Workflow JSON format:
{
  "name": "content-pipeline",
  "steps": [
    {
      "id": "research",
      "agent": "researcher",
      "depends_on": [],
      "model": "claude-sonnet-4-20250514",
      "estimated_input_tokens": 2000,
      "estimated_output_tokens": 4000
    },
    {
      "id": "write",
      "agent": "writer",
      "depends_on": ["research"],
      "model": "claude-sonnet-4-20250514",
      "estimated_input_tokens": 5000,
      "estimated_output_tokens": 8000
    }
  ]
}

Optional fields per step:
  - "parallel_branches": int (for fan-out steps, multiplies cost)
  - "retry_probability": float 0-1 (expected retry rate, adds proportional cost)
  - "cached_input_tokens": int (tokens served from prompt cache at reduced rate)

Usage:
  python cost_estimator.py workflow.json
  python cost_estimator.py workflow.json --json
  python cost_estimator.py workflow.json --runs 1000
  python cost_estimator.py workflow.json --override-model claude-haiku-4-20250514
"""

import argparse
import json
import sys
from typing import Any

# Pricing per 1M tokens (USD) as of early 2026
# Source: anthropic.com/pricing, openai.com/pricing
MODEL_PRICING: dict[str, dict[str, float]] = {
    # Anthropic models
    "claude-opus-4-20250514":   {"input": 15.00, "output": 75.00, "cached_input": 1.50},
    "claude-sonnet-4-20250514": {"input": 3.00,  "output": 15.00, "cached_input": 0.30},
    "claude-haiku-4-20250514":  {"input": 0.80,  "output": 4.00,  "cached_input": 0.08},
    # Aliases
    "claude-opus":   {"input": 15.00, "output": 75.00, "cached_input": 1.50},
    "claude-sonnet": {"input": 3.00,  "output": 15.00, "cached_input": 0.30},
    "claude-haiku":  {"input": 0.80,  "output": 4.00,  "cached_input": 0.08},
    # OpenAI models (approximate)
    "gpt-4o":       {"input": 2.50, "output": 10.00, "cached_input": 1.25},
    "gpt-4o-mini":  {"input": 0.15, "output": 0.60,  "cached_input": 0.075},
    "gpt-4-turbo":  {"input": 10.00, "output": 30.00, "cached_input": 5.00},
    # Default fallback
    "default":      {"input": 3.00,  "output": 15.00, "cached_input": 0.30},
}

DEFAULT_MODEL = "claude-sonnet-4-20250514"
DEFAULT_INPUT_TOKENS = 1000
DEFAULT_OUTPUT_TOKENS = 500


def get_pricing(model: str) -> dict[str, float]:
    """Look up pricing for a model, falling back to default."""
    return MODEL_PRICING.get(model, MODEL_PRICING["default"])


def cost_for_tokens(token_count: int, rate_per_million: float) -> float:
    """Calculate dollar cost for a given token count and rate per 1M tokens."""
    return (token_count / 1_000_000) * rate_per_million


def estimate_step(step: dict[str, Any], override_model: str | None = None) -> dict[str, Any]:
    """Estimate cost for a single workflow step."""
    step_id = step.get("id", "<unknown>")
    model = override_model or step.get("model", DEFAULT_MODEL)
    pricing = get_pricing(model)

    input_tokens = step.get("estimated_input_tokens", DEFAULT_INPUT_TOKENS)
    output_tokens = step.get("estimated_output_tokens", DEFAULT_OUTPUT_TOKENS)
    cached_tokens = step.get("cached_input_tokens", 0)
    parallel = step.get("parallel_branches", 1)
    retry_prob = step.get("retry_probability", 0.0)

    # Separate cached from non-cached input
    non_cached_input = max(0, input_tokens - cached_tokens)

    # Base cost for one execution
    base_input_cost = cost_for_tokens(non_cached_input, pricing["input"])
    base_cached_cost = cost_for_tokens(cached_tokens, pricing["cached_input"])
    base_output_cost = cost_for_tokens(output_tokens, pricing["output"])
    base_cost = base_input_cost + base_cached_cost + base_output_cost

    # Multiply by parallel branches
    branch_cost = base_cost * parallel

    # Add expected retry cost
    retry_cost = branch_cost * retry_prob
    total_cost = branch_cost + retry_cost

    total_tokens = (input_tokens + output_tokens) * parallel
    total_tokens_with_retry = total_tokens + int(total_tokens * retry_prob)

    return {
        "step_id": step_id,
        "model": model,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "cached_input_tokens": cached_tokens,
        "parallel_branches": parallel,
        "retry_probability": retry_prob,
        "base_cost_usd": round(base_cost, 6),
        "total_cost_usd": round(total_cost, 6),
        "total_tokens": total_tokens_with_retry,
    }


def estimate_workflow(
    workflow: dict[str, Any],
    num_runs: int = 1,
    override_model: str | None = None,
) -> dict[str, Any]:
    """Estimate cost for the entire workflow."""
    name = workflow.get("name", "<unnamed>")
    steps = workflow.get("steps", [])

    step_estimates = []
    for step in steps:
        est = estimate_step(step, override_model)
        step_estimates.append(est)

    per_run_cost = sum(e["total_cost_usd"] for e in step_estimates)
    per_run_tokens = sum(e["total_tokens"] for e in step_estimates)

    # Model breakdown
    model_costs: dict[str, float] = {}
    model_tokens: dict[str, int] = {}
    for e in step_estimates:
        m = e["model"]
        model_costs[m] = model_costs.get(m, 0.0) + e["total_cost_usd"]
        model_tokens[m] = model_tokens.get(m, 0) + e["total_tokens"]

    model_breakdown = [
        {"model": m, "cost_usd": round(model_costs[m], 6), "tokens": model_tokens[m]}
        for m in sorted(model_costs.keys())
    ]

    # Optimization suggestions
    suggestions = _generate_suggestions(step_estimates)

    return {
        "workflow": name,
        "step_count": len(steps),
        "per_run": {
            "cost_usd": round(per_run_cost, 6),
            "total_tokens": per_run_tokens,
        },
        "projected": {
            "runs": num_runs,
            "total_cost_usd": round(per_run_cost * num_runs, 4),
            "total_tokens": per_run_tokens * num_runs,
        },
        "steps": step_estimates,
        "model_breakdown": model_breakdown,
        "optimization_suggestions": suggestions,
    }


def _generate_suggestions(step_estimates: list[dict]) -> list[str]:
    """Generate cost optimization suggestions based on step analysis."""
    suggestions: list[str] = []

    # Find expensive steps using Opus
    opus_steps = [e for e in step_estimates if "opus" in e["model"].lower()]
    if opus_steps:
        names = ", ".join(e["step_id"] for e in opus_steps)
        suggestions.append(
            f"Steps using Opus ({names}): consider Sonnet for 5x cost reduction "
            f"unless output quality requires Opus."
        )

    # Find routing/classification steps not using Haiku
    for e in step_estimates:
        sid = e["step_id"].lower()
        if any(k in sid for k in ("route", "classify", "dispatch", "triage", "intent")):
            if "haiku" not in e["model"].lower():
                suggestions.append(
                    f"Step '{e['step_id']}' appears to be routing/classification — "
                    f"consider Haiku for ~85% cost reduction."
                )

    # Find steps with no caching on large inputs
    for e in step_estimates:
        if e["input_tokens"] > 3000 and e["cached_input_tokens"] == 0:
            suggestions.append(
                f"Step '{e['step_id']}' uses {e['input_tokens']} input tokens with no caching — "
                f"prompt caching could reduce input cost by ~90%."
            )

    # High parallel branch counts
    for e in step_estimates:
        if e["parallel_branches"] > 5:
            suggestions.append(
                f"Step '{e['step_id']}' fans out to {e['parallel_branches']} branches — "
                f"consider early termination or reducing branch count."
            )

    if not suggestions:
        suggestions.append("No obvious optimizations detected. Workflow appears cost-efficient.")

    return suggestions


def format_human(result: dict[str, Any]) -> str:
    """Format estimation results for human reading."""
    lines: list[str] = []
    lines.append(f"Workflow: {result['workflow']}")
    lines.append(f"Steps:    {result['step_count']}")
    lines.append("")

    # Per-run summary
    pr = result["per_run"]
    lines.append(f"Per-Run Cost:   ${pr['cost_usd']:.4f}")
    lines.append(f"Per-Run Tokens: {pr['total_tokens']:,}")

    proj = result["projected"]
    if proj["runs"] > 1:
        lines.append("")
        lines.append(f"Projected ({proj['runs']:,} runs):")
        lines.append(f"  Total Cost:   ${proj['total_cost_usd']:,.2f}")
        lines.append(f"  Total Tokens: {proj['total_tokens']:,}")

    # Step breakdown
    lines.append("")
    lines.append("Step Breakdown:")
    lines.append(f"  {'Step':<20} {'Model':<30} {'Tokens':>10} {'Cost':>10}")
    lines.append(f"  {'-'*20} {'-'*30} {'-'*10} {'-'*10}")
    for s in result["steps"]:
        model_short = s["model"].replace("claude-", "").replace("-20250514", "")
        branch_note = f" x{s['parallel_branches']}" if s["parallel_branches"] > 1 else ""
        lines.append(
            f"  {s['step_id']:<20} {model_short + branch_note:<30} "
            f"{s['total_tokens']:>10,} ${s['total_cost_usd']:>9.4f}"
        )

    # Model breakdown
    lines.append("")
    lines.append("By Model:")
    for mb in result["model_breakdown"]:
        model_short = mb["model"].replace("claude-", "").replace("-20250514", "")
        lines.append(f"  {model_short:<30} {mb['tokens']:>10,} tokens  ${mb['cost_usd']:.4f}")

    # Suggestions
    if result["optimization_suggestions"]:
        lines.append("")
        lines.append("Optimization Suggestions:")
        for s in result["optimization_suggestions"]:
            lines.append(f"  - {s}")

    return "\n".join(lines)


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


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Estimate token usage and cost for agent workflow execution",
        epilog="Pricing based on published rates as of early 2026.",
    )
    parser.add_argument("file", nargs="?", help="Path to workflow JSON file")
    parser.add_argument("--stdin", action="store_true", help="Read workflow from stdin")
    parser.add_argument("--json", action="store_true", dest="json_output",
                        help="Output results as JSON")
    parser.add_argument("--runs", type=int, default=1,
                        help="Number of projected runs for total cost (default: 1)")
    parser.add_argument("--override-model", type=str, default=None,
                        help="Override model for all steps (what-if analysis)")
    args = parser.parse_args()

    if not args.file and not args.stdin:
        parser.error("Provide a workflow file path or use --stdin")

    if args.runs < 1:
        parser.error("--runs must be >= 1")

    try:
        workflow = load_workflow(args.file, args.stdin)
    except (ValueError, FileNotFoundError, PermissionError) as e:
        if args.json_output:
            print(json.dumps({"error": str(e)}, indent=2))
        else:
            print(f"Error: {e}", file=sys.stderr)
        return 2

    result = estimate_workflow(workflow, num_runs=args.runs, override_model=args.override_model)

    if args.json_output:
        print(json.dumps(result, indent=2))
    else:
        print(format_human(result))

    return 0


if __name__ == "__main__":
    sys.exit(main())
