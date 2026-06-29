#!/usr/bin/env python3
"""Estimate and compare the cost of a lead-plus-subagents design vs a single strong agent.

This tool models the *topology* of a multi-agent system: one orchestrator (lead) that
delegates to N scoped subagents, each on a chosen price tier with its own call count,
token sizes, and reasoning effort. It reports the total cost, a per-role breakdown, and
a side-by-side comparison against a "single strong agent" baseline that does the same
volume of work entirely on one (typically the most expensive) tier.

Prices are NEUTRAL PLACEHOLDERS and are meant to be overridden with your own numbers.
No vendor pricing is hardcoded. Supply real per-million-token rates with --price or in
the JSON input's "price_tiers" block before trusting the dollar figures.

------------------------------------------------------------------------------------
Price tiers
------------------------------------------------------------------------------------
Roles reference a named price tier instead of a model name, so the tool stays
model-agnostic. Three neutral tiers ship as placeholders:

    economy   input 0.25  output 1.00   (cheap/narrow subagents)
    standard  input 2.00  output 8.00   (general work)
    frontier  input 12.00 output 40.00  (orchestrator / hard synthesis)

All figures are USD per 1,000,000 tokens and are illustrative only. Override any tier:
    --price economy=0.20/0.80 --price frontier=10/30

------------------------------------------------------------------------------------
Reasoning effort
------------------------------------------------------------------------------------
Each role may carry an "effort" multiplier (default 1.0) applied to its OUTPUT tokens,
a simple proxy for reasoning/thinking effort: a high-effort branch emits more output
tokens. Use it to model "cheap mechanical extraction (effort 0.5)" vs "deep synthesis
(effort 2.0)".

------------------------------------------------------------------------------------
JSON input format (--file / --stdin)
------------------------------------------------------------------------------------
{
  "orchestrator": {
    "role": "lead", "tier": "frontier",
    "calls": 4, "input_tokens": 6000, "output_tokens": 1500, "effort": 1.5
  },
  "subagents": [
    {"role": "researcher", "tier": "economy",  "calls": 3, "input_tokens": 4000,
     "output_tokens": 2000, "effort": 1.0},
    {"role": "extractor",  "tier": "economy",  "calls": 5, "input_tokens": 2500,
     "output_tokens": 600,  "effort": 0.5},
    {"role": "reviewer",   "tier": "standard", "calls": 1, "input_tokens": 8000,
     "output_tokens": 1200, "effort": 1.0}
  ],
  "price_tiers": {                 // optional: overrides the placeholder defaults
    "economy":  {"input": 0.20, "output": 0.80},
    "frontier": {"input": 10.0, "output": 30.0}
  },
  "baseline_tier": "frontier",     // optional: tier the single-agent baseline runs on
  "baseline_context_multiplier": 1.3  // optional: input bloat for a single un-isolated loop
}

------------------------------------------------------------------------------------
Repeatable-flag input (no JSON file needed)
------------------------------------------------------------------------------------
Each role flag takes a comma-separated spec:
    role,tier,calls,input_tokens,output_tokens[,effort]

    --orchestrator lead,frontier,4,6000,1500,1.5 \
    --subagent researcher,economy,3,4000,2000 \
    --subagent extractor,economy,5,2500,600,0.5 \
    --subagent reviewer,standard,1,8000,1200

------------------------------------------------------------------------------------
Baseline ("single strong agent")
------------------------------------------------------------------------------------
The baseline assumes one agent on --baseline-tier (default: the orchestrator's tier, or
"frontier") performs the SAME total call/token volume as all roles combined, with no
context isolation. Its input tokens are multiplied by --baseline-context-multiplier
(default 1.0) to optionally model the extra context a single un-isolated loop re-reads.
This isolates the savings from running narrow work on cheaper tiers.

Usage:
    python multi_agent_cost_estimator.py --file design.json
    python multi_agent_cost_estimator.py --file design.json --json
    python multi_agent_cost_estimator.py --stdin < design.json
    python multi_agent_cost_estimator.py --orchestrator lead,frontier,4,6000,1500 \
        --subagent researcher,economy,3,4000,2000 --runs 1000
"""

import argparse
import json
import sys
from typing import Any

# Neutral placeholder price tiers, USD per 1,000,000 tokens.
# These are NOT vendor prices. Override with --price or the JSON "price_tiers" block.
DEFAULT_PRICE_TIERS: dict[str, dict[str, float]] = {
    "economy":  {"input": 0.25, "output": 1.00},
    "standard": {"input": 2.00, "output": 8.00},
    "frontier": {"input": 12.00, "output": 40.00},
}

DEFAULT_EFFORT = 1.0


def cost_for_tokens(token_count: float, rate_per_million: float) -> float:
    """Dollar cost for a token count at a rate per 1,000,000 tokens."""
    return (token_count / 1_000_000) * rate_per_million


def normalize_role(raw: dict[str, Any], kind: str) -> dict[str, Any]:
    """Validate and fill defaults for a single role spec."""
    role = str(raw.get("role", kind))
    tier = str(raw.get("tier", "standard"))
    try:
        calls = int(raw.get("calls", 1))
        input_tokens = int(raw.get("input_tokens", 0))
        output_tokens = int(raw.get("output_tokens", 0))
        effort = float(raw.get("effort", DEFAULT_EFFORT))
    except (TypeError, ValueError) as e:
        raise ValueError(f"Role '{role}': numeric field is not a number ({e})")
    if calls < 0 or input_tokens < 0 or output_tokens < 0 or effort < 0:
        raise ValueError(f"Role '{role}': calls/tokens/effort must be non-negative")
    return {
        "role": role,
        "kind": kind,
        "tier": tier,
        "calls": calls,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "effort": effort,
    }


def parse_role_flag(spec: str, kind: str) -> dict[str, Any]:
    """Parse a 'role,tier,calls,input,output[,effort]' flag value."""
    parts = [p.strip() for p in spec.split(",")]
    if len(parts) < 5:
        raise ValueError(
            f"--{kind} expects 'role,tier,calls,input_tokens,output_tokens[,effort]', "
            f"got: {spec!r}"
        )
    raw: dict[str, Any] = {
        "role": parts[0],
        "tier": parts[1],
        "calls": parts[2],
        "input_tokens": parts[3],
        "output_tokens": parts[4],
    }
    if len(parts) >= 6 and parts[5] != "":
        raw["effort"] = parts[5]
    return normalize_role(raw, kind)


def parse_price_flag(spec: str) -> tuple[str, dict[str, float]]:
    """Parse a 'tier=input/output' price override flag."""
    if "=" not in spec:
        raise ValueError(f"--price expects 'tier=input/output', got: {spec!r}")
    tier, rates = spec.split("=", 1)
    if "/" not in rates:
        raise ValueError(f"--price rates must be 'input/output', got: {rates!r}")
    in_s, out_s = rates.split("/", 1)
    try:
        return tier.strip(), {"input": float(in_s), "output": float(out_s)}
    except ValueError:
        raise ValueError(f"--price rates must be numbers, got: {rates!r}")


def resolve_tier(tier: str, price_tiers: dict[str, dict[str, float]]) -> dict[str, float]:
    """Look up a tier's rates, falling back to 'standard' then to any defined tier."""
    if tier in price_tiers:
        return price_tiers[tier]
    if "standard" in price_tiers:
        return price_tiers["standard"]
    # last resort: first defined tier
    return next(iter(price_tiers.values()))


def estimate_role(role: dict[str, Any], price_tiers: dict[str, dict[str, float]]) -> dict[str, Any]:
    """Cost a single role across all its calls."""
    rates = resolve_tier(role["tier"], price_tiers)
    effective_output = role["output_tokens"] * role["effort"]

    in_tokens = role["input_tokens"] * role["calls"]
    out_tokens = effective_output * role["calls"]

    input_cost = cost_for_tokens(in_tokens, rates["input"])
    output_cost = cost_for_tokens(out_tokens, rates["output"])
    total_cost = input_cost + output_cost

    return {
        "role": role["role"],
        "kind": role["kind"],
        "tier": role["tier"],
        "calls": role["calls"],
        "effort": role["effort"],
        "input_tokens": int(in_tokens),
        "output_tokens": int(out_tokens),
        "total_tokens": int(in_tokens + out_tokens),
        "input_cost_usd": round(input_cost, 6),
        "output_cost_usd": round(output_cost, 6),
        "cost_usd": round(total_cost, 6),
    }


def estimate(
    orchestrator: dict[str, Any] | None,
    subagents: list[dict[str, Any]],
    price_tiers: dict[str, dict[str, float]],
    baseline_tier: str | None,
    baseline_context_multiplier: float,
    runs: int,
) -> dict[str, Any]:
    """Estimate multi-agent cost and the single-strong-agent baseline."""
    roles: list[dict[str, Any]] = []
    if orchestrator is not None:
        roles.append(orchestrator)
    roles.extend(subagents)

    role_estimates = [estimate_role(r, price_tiers) for r in roles]

    multi_cost = sum(e["cost_usd"] for e in role_estimates)
    multi_input_tokens = sum(e["input_tokens"] for e in role_estimates)
    multi_output_tokens = sum(e["output_tokens"] for e in role_estimates)
    multi_calls = sum(e["calls"] for e in role_estimates)

    # Baseline: same total volume on one strong tier, no context isolation.
    if baseline_tier is None:
        baseline_tier = orchestrator["tier"] if orchestrator else "frontier"
    base_rates = resolve_tier(baseline_tier, price_tiers)
    base_input = multi_input_tokens * baseline_context_multiplier
    base_output = multi_output_tokens  # same work produced, just on one agent
    baseline_cost = (
        cost_for_tokens(base_input, base_rates["input"])
        + cost_for_tokens(base_output, base_rates["output"])
    )

    savings = baseline_cost - multi_cost
    savings_pct = (savings / baseline_cost * 100) if baseline_cost > 0 else 0.0

    return {
        "price_tiers": price_tiers,
        "multi_agent": {
            "roles": role_estimates,
            "total_calls": multi_calls,
            "input_tokens": multi_input_tokens,
            "output_tokens": multi_output_tokens,
            "total_tokens": multi_input_tokens + multi_output_tokens,
            "per_run_cost_usd": round(multi_cost, 6),
        },
        "single_strong_agent_baseline": {
            "tier": baseline_tier,
            "context_multiplier": baseline_context_multiplier,
            "input_tokens": int(base_input),
            "output_tokens": int(base_output),
            "total_tokens": int(base_input + base_output),
            "per_run_cost_usd": round(baseline_cost, 6),
        },
        "comparison": {
            "per_run_savings_usd": round(savings, 6),
            "savings_pct": round(savings_pct, 2),
            "cheaper": "multi_agent" if savings >= 0 else "single_strong_agent",
        },
        "projected": {
            "runs": runs,
            "multi_agent_total_usd": round(multi_cost * runs, 4),
            "baseline_total_usd": round(baseline_cost * runs, 4),
            "savings_total_usd": round(savings * runs, 4),
        },
    }


def _short(tier: str) -> str:
    return tier[:10]


def format_human(result: dict[str, Any]) -> str:
    lines: list[str] = []
    ma = result["multi_agent"]
    base = result["single_strong_agent_baseline"]
    cmp = result["comparison"]
    proj = result["projected"]

    lines.append("Multi-Agent Cost Estimate")
    lines.append("=" * 64)
    lines.append("Prices are user-supplied placeholders unless overridden. Verify before use.")
    lines.append("")

    lines.append("Per-Role Breakdown:")
    lines.append(f"  {'Role':<16}{'Kind':<8}{'Tier':<10}{'Calls':>6}{'Effort':>8}"
                 f"{'Tokens':>12}{'Cost':>11}")
    lines.append(f"  {'-'*15:<16}{'-'*7:<8}{'-'*9:<10}{'-'*5:>6}{'-'*7:>8}"
                 f"{'-'*11:>12}{'-'*10:>11}")
    for e in ma["roles"]:
        lines.append(
            f"  {e['role'][:15]:<16}{e['kind'][:7]:<8}{_short(e['tier']):<10}"
            f"{e['calls']:>6}{e['effort']:>8.2f}{e['total_tokens']:>12,}"
            f"{('$' + format(e['cost_usd'], '.4f')):>11}"
        )
    lines.append("")

    lines.append("Multi-Agent (per run):")
    lines.append(f"  Calls:  {ma['total_calls']:,}")
    lines.append(f"  Tokens: {ma['total_tokens']:,} "
                 f"(in {ma['input_tokens']:,} / out {ma['output_tokens']:,})")
    lines.append(f"  Cost:   ${ma['per_run_cost_usd']:.4f}")
    lines.append("")

    lines.append(f"Single Strong Agent Baseline (tier '{base['tier']}', "
                 f"context x{base['context_multiplier']}):")
    lines.append(f"  Tokens: {base['total_tokens']:,} "
                 f"(in {base['input_tokens']:,} / out {base['output_tokens']:,})")
    lines.append(f"  Cost:   ${base['per_run_cost_usd']:.4f}")
    lines.append("")

    cheaper = cmp["cheaper"].replace("_", " ")
    lines.append("Comparison (per run):")
    lines.append(f"  Cheaper design: {cheaper}")
    lines.append(f"  Savings:        ${cmp['per_run_savings_usd']:.4f} "
                 f"({cmp['savings_pct']:+.1f}% vs baseline)")
    lines.append("")

    if proj["runs"] > 1:
        lines.append(f"Projected over {proj['runs']:,} runs:")
        lines.append(f"  Multi-agent: ${proj['multi_agent_total_usd']:,.2f}")
        lines.append(f"  Baseline:    ${proj['baseline_total_usd']:,.2f}")
        lines.append(f"  Savings:     ${proj['savings_total_usd']:,.2f}")

    return "\n".join(lines)


def load_json_input(path: str | None, use_stdin: bool) -> dict[str, Any]:
    if use_stdin:
        raw = sys.stdin.read()
    elif path:
        with open(path, "r", encoding="utf-8") as f:
            raw = f.read()
    else:
        return {}
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {e}")
    if not isinstance(data, dict):
        raise ValueError("Input JSON must be an object")
    return data


def build_inputs(args: argparse.Namespace) -> dict[str, Any]:
    """Merge JSON input and CLI flags into a single normalized spec."""
    data = load_json_input(args.file, args.stdin)

    # Price tiers: start from defaults, layer JSON, then CLI --price overrides.
    price_tiers = {t: dict(r) for t, r in DEFAULT_PRICE_TIERS.items()}
    for tier, rates in (data.get("price_tiers") or {}).items():
        price_tiers[tier] = {"input": float(rates["input"]), "output": float(rates["output"])}
    for spec in args.price or []:
        tier, rates = parse_price_flag(spec)
        price_tiers[tier] = rates

    # Orchestrator: CLI flag wins over JSON.
    orchestrator = None
    if args.orchestrator:
        orchestrator = parse_role_flag(args.orchestrator, "orchestrator")
    elif data.get("orchestrator"):
        orchestrator = normalize_role(data["orchestrator"], "orchestrator")

    # Subagents: CLI flags REPLACE JSON subagents if any are given.
    subagents: list[dict[str, Any]] = []
    if args.subagent:
        for spec in args.subagent:
            subagents.append(parse_role_flag(spec, "subagent"))
    else:
        for raw in data.get("subagents") or []:
            subagents.append(normalize_role(raw, "subagent"))

    if orchestrator is None and not subagents:
        raise ValueError(
            "No roles provided. Supply --orchestrator/--subagent flags or a JSON "
            "file/stdin with 'orchestrator'/'subagents'."
        )

    baseline_tier = args.baseline_tier or data.get("baseline_tier")
    baseline_mult = (
        args.baseline_context_multiplier
        if args.baseline_context_multiplier is not None
        else float(data.get("baseline_context_multiplier", 1.0))
    )
    if baseline_mult < 0:
        raise ValueError("baseline_context_multiplier must be non-negative")

    return {
        "orchestrator": orchestrator,
        "subagents": subagents,
        "price_tiers": price_tiers,
        "baseline_tier": baseline_tier,
        "baseline_context_multiplier": baseline_mult,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Estimate and compare lead+subagents cost vs a single strong agent. "
                    "Prices are user-supplied placeholders; override before trusting figures.",
    )
    parser.add_argument("--file", help="Path to a JSON design spec")
    parser.add_argument("--stdin", action="store_true", help="Read JSON design spec from stdin")
    parser.add_argument("--orchestrator", metavar="role,tier,calls,in,out[,effort]",
                        help="Lead/orchestrator role spec (overrides JSON)")
    parser.add_argument("--subagent", action="append", metavar="role,tier,calls,in,out[,effort]",
                        help="A scoped subagent spec; repeatable (replaces JSON subagents)")
    parser.add_argument("--price", action="append", metavar="tier=input/output",
                        help="Override a price tier (USD per 1M tokens); repeatable")
    parser.add_argument("--baseline-tier", help="Tier the single-strong-agent baseline runs on "
                        "(default: orchestrator's tier, else 'frontier')")
    parser.add_argument("--baseline-context-multiplier", type=float, default=None,
                        help="Input-token multiplier for the un-isolated single agent (default 1.0)")
    parser.add_argument("--runs", type=int, default=1,
                        help="Projected number of runs for total cost (default 1)")
    parser.add_argument("--json", action="store_true", dest="json_output",
                        help="Output results as JSON")
    args = parser.parse_args()

    if args.runs < 1:
        parser.error("--runs must be >= 1")

    try:
        spec = build_inputs(args)
        result = estimate(
            orchestrator=spec["orchestrator"],
            subagents=spec["subagents"],
            price_tiers=spec["price_tiers"],
            baseline_tier=spec["baseline_tier"],
            baseline_context_multiplier=spec["baseline_context_multiplier"],
            runs=args.runs,
        )
    except (ValueError, FileNotFoundError, PermissionError, KeyError) as e:
        if args.json_output:
            print(json.dumps({"error": str(e)}, indent=2))
        else:
            print(f"Error: {e}", file=sys.stderr)
        return 2

    if args.json_output:
        print(json.dumps(result, indent=2))
    else:
        print(format_human(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
