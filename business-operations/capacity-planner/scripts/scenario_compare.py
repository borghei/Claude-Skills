#!/usr/bin/env python3
"""Compare hire / contract / defer scenarios against a multi-quarter demand curve.

Models added capacity quarter by quarter (including ramp), accumulates fully
loaded cost, and reports unmet demand, cost per incremental delivered hour, and
the quarter each scenario first clears demand.

Usage:
    python3 scenario_compare.py --input sample_scenarios.json
    python3 scenario_compare.py --input sample_scenarios.json --format json
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

# Monthly productivity multipliers for a new permanent hire, by seniority.
RAMP_CURVES: Dict[str, List[float]] = {
    "junior": [0.10, 0.25, 0.40, 0.55, 0.70, 0.85, 1.00],
    "mid": [0.15, 0.35, 0.55, 0.75, 0.90, 1.00],
    "senior": [0.25, 0.50, 0.75, 0.90, 1.00],
    "staff": [0.30, 0.55, 0.80, 1.00],
    "principal": [0.30, 0.55, 0.80, 1.00],
}

# Contractors ramp faster on scoped work but never reach an insider's context.
CONTRACT_RAMP = [0.50, 0.85, 0.95]
CONTRACT_CEILING = 0.95

# Fully loaded cost multiplier over base salary (benefits, tax, equipment, space).
DEFAULT_LOADING = 1.30

# A scenario clearing this share of cumulative demand is treated as sufficient.
DEMAND_CLEARED_RATIO = 0.95


def ramp_for_quarter(curve: List[float], months_since_start: int, ceiling: float = 1.0) -> float:
    """Average a monthly ramp curve across the three months of one quarter."""
    if months_since_start < 0:
        return 0.0
    total = 0.0
    for m in range(months_since_start, months_since_start + 3):
        total += min(curve[m], ceiling) if m < len(curve) else ceiling
    return total / 3.0


def scenario_capacity(scenario: Dict[str, Any], quarter: int, hours_per_fte: float) -> float:
    """Return incremental delivered hours a scenario adds in a given quarter."""
    kind = str(scenario.get("type", "hire")).lower()
    start = int(scenario.get("start_quarter", 0))
    if quarter < start:
        return 0.0
    count = float(scenario.get("count", 0))
    months = (quarter - start) * 3

    if kind == "hire":
        curve = RAMP_CURVES.get(str(scenario.get("seniority", "mid")).lower(), RAMP_CURVES["mid"])
        return count * hours_per_fte * ramp_for_quarter(curve, months)
    if kind == "contract":
        return count * hours_per_fte * ramp_for_quarter(CONTRACT_RAMP, months, CONTRACT_CEILING)
    if kind == "defer":
        return 0.0
    raise ValueError(f"unknown scenario type '{kind}' (expected hire, contract or defer)")


def scenario_cost(scenario: Dict[str, Any], quarter: int, hours_per_fte: float) -> float:
    """Return the cash cost a scenario incurs in a given quarter."""
    kind = str(scenario.get("type", "hire")).lower()
    start = int(scenario.get("start_quarter", 0))
    if quarter < start:
        return 0.0
    count = float(scenario.get("count", 0))

    if kind == "hire":
        loading = float(scenario.get("loading_multiplier", DEFAULT_LOADING))
        salary = float(scenario.get("annual_cost_per_head", 0)) * loading / 4.0
        cost = count * salary
        if quarter == start:
            cost += count * float(scenario.get("recruiting_cost_per_head", 0))
        return cost
    if kind == "contract":
        rate = float(scenario.get("hourly_rate", 0))
        return count * hours_per_fte * rate
    if kind == "defer":
        return 0.0
    raise ValueError(f"unknown scenario type '{kind}'")


def analyse(data: Dict[str, Any]) -> Dict[str, Any]:
    """Project every scenario across the planning horizon and rank them."""
    horizon = int(data.get("horizon_quarters", 4))
    demand = [float(x) for x in data.get("demand_hours_per_quarter", [])]
    if len(demand) < horizon:
        raise ValueError(
            f"'demand_hours_per_quarter' has {len(demand)} entries but horizon is {horizon}"
        )
    baseline = float(data.get("baseline_effective_hours_per_quarter", 0))
    hours_per_fte = float(data.get("hours_per_fte_quarter", 480))
    scenarios = data.get("scenarios", [])
    if not scenarios:
        raise ValueError("input JSON needs a non-empty 'scenarios' array")

    results: List[Dict[str, Any]] = []
    for scenario in scenarios:
        deferred = float(scenario.get("deferred_hours_per_quarter", 0))
        quarters: List[Dict[str, Any]] = []
        cum_added = cum_cost = cum_unmet = 0.0
        cleared_at = None
        for q in range(horizon):
            added = scenario_capacity(scenario, q, hours_per_fte)
            cost = scenario_cost(scenario, q, hours_per_fte)
            q_demand = max(demand[q] - deferred, 0.0)
            supply = baseline + added
            unmet = max(q_demand - supply, 0.0)
            cum_added += added
            cum_cost += cost
            cum_unmet += unmet
            if unmet == 0 and cleared_at is None:
                cleared_at = q
            quarters.append(
                {
                    "quarter_index": q,
                    "demand_hours": round(q_demand, 1),
                    "supply_hours": round(supply, 1),
                    "added_hours": round(added, 1),
                    "unmet_hours": round(unmet, 1),
                    "cost": round(cost, 0),
                }
            )
        total_demand = sum(max(d - deferred, 0.0) for d in demand[:horizon])
        met = total_demand - cum_unmet
        results.append(
            {
                "name": scenario.get("name", scenario.get("type", "unnamed")),
                "type": str(scenario.get("type", "hire")).lower(),
                "quarters": quarters,
                "total_added_hours": round(cum_added, 1),
                "total_cost": round(cum_cost, 0),
                "total_unmet_hours": round(cum_unmet, 1),
                "demand_met_ratio": round(met / total_demand, 3) if total_demand else 1.0,
                "cost_per_added_hour": round(cum_cost / cum_added, 2) if cum_added else None,
                "deferred_hours_per_quarter": deferred,
                "clears_demand_at_quarter": cleared_at,
            }
        )

    sufficient = [r for r in results if r["demand_met_ratio"] >= DEMAND_CLEARED_RATIO]
    pool = sufficient or results
    ranked = sorted(
        pool,
        key=lambda r: (
            -r["demand_met_ratio"] if not sufficient else 0,
            r["cost_per_added_hour"] if r["cost_per_added_hour"] is not None else float("inf"),
        ),
    )
    recommended = ranked[0]

    if sufficient:
        rationale = (
            f"'{recommended['name']}' clears {recommended['demand_met_ratio']:.0%} of demand at the "
            f"lowest cost per delivered hour among sufficient options."
        )
    else:
        rationale = (
            f"No scenario clears {DEMAND_CLEARED_RATIO:.0%} of demand. "
            f"'{recommended['name']}' gets closest ({recommended['demand_met_ratio']:.0%}); "
            "scope must be cut regardless of staffing choice."
        )

    return {
        "horizon_quarters": horizon,
        "baseline_effective_hours_per_quarter": baseline,
        "hours_per_fte_quarter": hours_per_fte,
        "scenarios": results,
        "recommendation": {"scenario": recommended["name"], "rationale": rationale},
    }


def output(result: Dict[str, Any], fmt: str) -> None:
    """Print the scenario comparison as JSON or a human-readable report."""
    if fmt == "json":
        print(json.dumps(result, indent=2))
        return

    print("SCENARIO COMPARISON")
    print("=" * 78)
    print(
        f"Horizon: {result['horizon_quarters']} quarters | "
        f"baseline {result['baseline_effective_hours_per_quarter']:.0f}h/qtr | "
        f"{result['hours_per_fte_quarter']:.0f}h per FTE-quarter"
    )
    for s in result["scenarios"]:
        print()
        print(f"{s['name'].upper()}  ({s['type']})")
        print(f"  {'Qtr':<6}{'Demand':>10}{'Supply':>10}{'Added':>10}{'Unmet':>10}{'Cost':>14}")
        for q in s["quarters"]:
            print(
                f"  Q{q['quarter_index']:<5}{q['demand_hours']:>10.0f}{q['supply_hours']:>10.0f}"
                f"{q['added_hours']:>10.0f}{q['unmet_hours']:>10.0f}{q['cost']:>14,.0f}"
            )
        cph = s["cost_per_added_hour"]
        cph_str = f"{cph:,.2f}/h" if cph is not None else "n/a (no capacity added)"
        cleared = (
            f"Q{s['clears_demand_at_quarter']}" if s["clears_demand_at_quarter"] is not None else "never"
        )
        print(
            f"  -> {s['total_added_hours']:.0f}h added, {s['total_cost']:,.0f} cost, "
            f"{cph_str}, demand met {s['demand_met_ratio']:.0%}, clears at {cleared}"
        )
    print()
    print("RECOMMENDATION")
    print(f"  {result['recommendation']['scenario']}: {result['recommendation']['rationale']}")


def main() -> None:
    """Parse arguments, run the scenario comparison, and print the result."""
    parser = argparse.ArgumentParser(
        description="Compare hire / contract / defer staffing scenarios over a planning horizon.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to a scenarios JSON file (see assets/sample_scenarios.json)",
    )
    parser.add_argument(
        "--format", choices=["text", "json"], default="text", help="Output format"
    )
    args = parser.parse_args()

    try:
        data = json.loads(Path(args.input).read_text(encoding="utf-8"))
        output(analyse(data), args.format)
    except FileNotFoundError:
        print(f"Error: input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as exc:
        print(f"Error: {args.input} is not valid JSON ({exc})", file=sys.stderr)
        sys.exit(1)
    except (ValueError, KeyError, TypeError) as exc:
        print(f"Error: could not compare scenarios — {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
