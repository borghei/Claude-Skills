#!/usr/bin/env python3
"""Analyse a process definition for cycle time, value-added ratio and bottlenecks.

Computes touch time vs wait time, process cycle efficiency, first-pass yield,
expected rework cost per loop, and ranks steps by their contribution to lead
time. Works on any sequential process described as steps with owner, duration,
wait time and rework rate.

Usage:
    python3 process_analyzer.py --input sample_process.json
    python3 process_analyzer.py --input sample_process.json --format json
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Lean classification of work. Only value_added earns customer willingness to pay.
VALUE_TYPES = {"value_added", "business_value_added", "non_value_added"}

# Process cycle efficiency bands for transactional (office) processes.
PCE_BANDS = [
    (0.05, "POOR", "Typical for an un-improved transactional process. Wait time dominates."),
    (0.15, "BELOW AVERAGE", "Some flow, but queues still control lead time."),
    (0.25, "AVERAGE", "Reasonable for a multi-team process with approvals."),
    (0.50, "GOOD", "Strong flow. Remaining gains come from batch size and automation."),
    (1.01, "WORLD CLASS", "Rare outside single-owner automated processes. Verify the data."),
]

# A step consuming more than this share of lead time is the constraint.
BOTTLENECK_SHARE = 0.20
# Rework at or above this rate destroys predictability and is fixed before anything else.
REWORK_ALERT = 0.10
# Wait/touch ratio above this on a single step means it is a queue, not work.
QUEUE_RATIO_ALERT = 3.0
# Only the worst queues are worth naming; a long list of alerts is not a finding.
MAX_QUEUE_FINDINGS = 3


def classify_pce(pce: float) -> Dict[str, str]:
    """Return the benchmark band and interpretation for a process cycle efficiency."""
    for ceiling, label, note in PCE_BANDS:
        if pce < ceiling:
            return {"band": label, "interpretation": note}
    return {"band": "INVALID", "interpretation": "PCE above 100% means the input data is wrong."}


def validate(steps: List[Dict[str, Any]]) -> None:
    """Raise ValueError if the step list is malformed."""
    if not steps:
        raise ValueError("input JSON needs a non-empty 'steps' array")
    ids = [s.get("id") for s in steps]
    if len(set(ids)) != len(ids):
        raise ValueError("step ids must be unique")
    for s in steps:
        vt = s.get("value_type", "business_value_added")
        if vt not in VALUE_TYPES:
            raise ValueError(
                f"step '{s.get('id')}' has value_type '{vt}'; expected one of {sorted(VALUE_TYPES)}"
            )
        if float(s.get("process_time_min", 0)) < 0 or float(s.get("wait_time_min", 0)) < 0:
            raise ValueError(f"step '{s.get('id')}' has a negative duration")
        rate = float(s.get("rework_rate", 0))
        if not 0 <= rate < 1:
            raise ValueError(f"step '{s.get('id')}' has rework_rate {rate}; must be >= 0 and < 1")


def rework_cost(steps: List[Dict[str, Any]], index: int, id_to_index: Dict[str, int]) -> float:
    """Expected minutes added per unit by rework looping back from this step."""
    step = steps[index]
    rate = float(step.get("rework_rate", 0))
    if rate == 0:
        return 0.0
    target = step.get("rework_to", step.get("id"))
    start = id_to_index.get(target, index)
    if start > index:
        start = index
    loop = sum(
        float(s.get("process_time_min", 0)) + float(s.get("wait_time_min", 0))
        for s in steps[start : index + 1]
    )
    return rate * loop


def analyse(data: Dict[str, Any]) -> Dict[str, Any]:
    """Compute flow metrics, bottlenecks and rework exposure for a process."""
    steps = data.get("steps", [])
    validate(steps)
    id_to_index = {s.get("id"): i for i, s in enumerate(steps)}

    enriched: List[Dict[str, Any]] = []
    for i, s in enumerate(steps):
        touch = float(s.get("process_time_min", 0))
        wait = float(s.get("wait_time_min", 0))
        rw = rework_cost(steps, i, id_to_index)
        enriched.append(
            {
                "id": s.get("id"),
                "name": s.get("name", s.get("id")),
                "owner": s.get("owner", "unassigned"),
                "value_type": s.get("value_type", "business_value_added"),
                "process_time_min": touch,
                "wait_time_min": wait,
                "elapsed_min": touch + wait,
                "rework_rate": float(s.get("rework_rate", 0)),
                "expected_rework_min": round(rw, 1),
                "queue_ratio": round(wait / touch, 2) if touch else None,
                "automated": bool(s.get("automated", False)),
            }
        )

    total_touch = sum(e["process_time_min"] for e in enriched)
    total_wait = sum(e["wait_time_min"] for e in enriched)
    total_rework = sum(e["expected_rework_min"] for e in enriched)
    lead_time = total_touch + total_wait
    va_touch = sum(e["process_time_min"] for e in enriched if e["value_type"] == "value_added")

    pce = va_touch / lead_time if lead_time else 0.0
    va_ratio = va_touch / total_touch if total_touch else 0.0

    fpy = 1.0
    for e in enriched:
        fpy *= 1 - e["rework_rate"]

    for e in enriched:
        e["share_of_lead_time"] = round(e["elapsed_min"] / lead_time, 3) if lead_time else 0.0

    ranked = sorted(enriched, key=lambda e: e["elapsed_min"], reverse=True)
    bottlenecks = [e for e in ranked if e["share_of_lead_time"] >= BOTTLENECK_SHARE] or ranked[:1]

    by_value: Dict[str, float] = {}
    for e in enriched:
        by_value[e["value_type"]] = by_value.get(e["value_type"], 0.0) + e["process_time_min"]

    findings: List[str] = []
    for b in bottlenecks:
        findings.append(
            f"Constraint: '{b['name']}' ({b['owner']}) consumes {b['share_of_lead_time']:.0%} "
            f"of lead time — {b['wait_time_min']:.0f} min of it is wait."
        )
    for e in sorted(enriched, key=lambda x: -x["expected_rework_min"]):
        if e["rework_rate"] >= REWORK_ALERT:
            findings.append(
                f"Rework: '{e['name']}' fails {e['rework_rate']:.0%} of the time, "
                f"adding {e['expected_rework_min']:.0f} min expected per unit."
            )

    queued = [
        e
        for e in enriched
        if e["queue_ratio"] is not None and e["queue_ratio"] >= QUEUE_RATIO_ALERT
    ]
    if queued:
        worst = sorted(queued, key=lambda x: -x["wait_time_min"])[:MAX_QUEUE_FINDINGS]
        for e in worst:
            findings.append(
                f"Queue: '{e['name']}' waits {e['wait_time_min']:.0f} min against "
                f"{e['process_time_min']:.0f} min of work ({e['queue_ratio']:.0f}x) — "
                "a scheduling problem, not a capacity problem."
            )
        if len(queued) > MAX_QUEUE_FINDINGS:
            findings.append(
                f"{len(queued)} of {len(enriched)} steps wait more than {QUEUE_RATIO_ALERT:.0f}x "
                "their work time. Queueing is systemic here — fix the scheduling policy, "
                "not the individual steps."
            )
    nva = by_value.get("non_value_added", 0.0)
    if total_touch and nva / total_touch > 0.25:
        findings.append(
            f"{nva / total_touch:.0%} of touch time is non-value-added — eliminate before optimising."
        )
    if fpy < 0.75:
        findings.append(
            f"First-pass yield is {fpy:.0%}; roughly 1 in {max(round(1 / (1 - fpy)), 1)} units "
            "needs rework somewhere. Fix quality before speed."
        )

    demand = data.get("demand_per_month")
    monthly: Optional[Dict[str, float]] = None
    if demand:
        d = float(demand)
        monthly = {
            "units_per_month": d,
            "touch_hours_per_month": round(d * total_touch / 60, 1),
            "rework_hours_per_month": round(d * total_rework / 60, 1),
            "non_value_added_hours_per_month": round(d * nva / 60, 1),
        }

    return {
        "process_name": data.get("process_name", "unnamed process"),
        "step_count": len(enriched),
        "steps": enriched,
        "metrics": {
            "total_touch_time_min": round(total_touch, 1),
            "total_wait_time_min": round(total_wait, 1),
            "lead_time_min": round(lead_time, 1),
            "lead_time_days_at_8h": round(lead_time / 480, 2),
            "value_added_time_min": round(va_touch, 1),
            "process_cycle_efficiency": round(pce, 4),
            "value_added_ratio": round(va_ratio, 3),
            "first_pass_yield": round(fpy, 3),
            "expected_rework_min": round(total_rework, 1),
            "touch_time_by_value_type": {k: round(v, 1) for k, v in by_value.items()},
        },
        "pce_assessment": classify_pce(pce),
        "bottlenecks": bottlenecks,
        "monthly_load": monthly,
        "findings": findings,
    }


def output(result: Dict[str, Any], fmt: str) -> None:
    """Print the process analysis as JSON or a human-readable report."""
    if fmt == "json":
        print(json.dumps(result, indent=2))
        return

    m = result["metrics"]
    print(f"PROCESS ANALYSIS — {result['process_name']}")
    print("=" * 78)
    print(f"{result['step_count']} steps")
    print()
    print(f"{'Step':<32}{'Owner':<14}{'Touch':>8}{'Wait':>8}{'Share':>8}{'Rwk':>6}")
    print("-" * 78)
    for s in result["steps"]:
        tag = {"value_added": "V", "business_value_added": "B", "non_value_added": "N"}[s["value_type"]]
        print(
            f"{tag} {s['name'][:29]:<30}{s['owner'][:13]:<14}{s['process_time_min']:>8.0f}"
            f"{s['wait_time_min']:>8.0f}{s['share_of_lead_time']:>8.0%}{s['rework_rate']:>6.0%}"
        )
    print("-" * 78)
    print("V = value-added   B = business-value-added   N = non-value-added")
    print()
    print("FLOW METRICS")
    print(f"  Lead time              {m['lead_time_min']:>10.0f} min ({m['lead_time_days_at_8h']} working days)")
    print(f"  Touch time             {m['total_touch_time_min']:>10.0f} min")
    print(f"  Wait time              {m['total_wait_time_min']:>10.0f} min")
    print(f"  Value-added time       {m['value_added_time_min']:>10.0f} min")
    print(f"  Expected rework        {m['expected_rework_min']:>10.0f} min/unit")
    print(f"  Process cycle eff.     {m['process_cycle_efficiency']:>10.1%}  [{result['pce_assessment']['band']}]")
    print(f"  Value-added ratio      {m['value_added_ratio']:>10.1%}")
    print(f"  First-pass yield       {m['first_pass_yield']:>10.1%}")
    print(f"  -> {result['pce_assessment']['interpretation']}")
    if result["monthly_load"]:
        ml = result["monthly_load"]
        print()
        print(f"MONTHLY LOAD AT {ml['units_per_month']:.0f} UNITS")
        print(f"  Touch            {ml['touch_hours_per_month']:>8.0f} h")
        print(f"  Rework           {ml['rework_hours_per_month']:>8.0f} h")
        print(f"  Non-value-added  {ml['non_value_added_hours_per_month']:>8.0f} h")
    if result["findings"]:
        print()
        print("FINDINGS")
        for f in result["findings"]:
            print(f"  ! {f}")


def main() -> None:
    """Parse arguments, run the process analysis, and print the result."""
    parser = argparse.ArgumentParser(
        description="Analyse a process for cycle time, value-added ratio and bottlenecks.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to a process definition JSON file (see assets/sample_process.json)",
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
        print(f"Error: could not analyse process — {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
