#!/usr/bin/env python3
"""
burn_vs_milestone_tracker.py — Track research spend against milestone
completion and forecast the cost at completion.

Applies earned-value mechanics to a research programme: milestone completion
weights give earned value, actual spend gives cost performance, and the planned
spend curve gives schedule performance. Forecasts the estimate at completion and
the overrun, and flags the specific pattern where spend is tracking to plan but
delivery is not.

Stdlib only. Deterministic. Text (default) or JSON output.

Usage:
    python3 burn_vs_milestone_tracker.py --input burn.json
    python3 burn_vs_milestone_tracker.py --input burn.json --format json
    python3 burn_vs_milestone_tracker.py --input burn.json --strict

Input schema:
{
  "programme": "...", "currency": "EUR", "budget_at_completion": 1250000,
  "as_of_period": 8,
  "milestones": [
      {"name": "Protocol approved", "weight": 0.10, "complete": 1.0,
       "planned_period": 2},
      {"name": "First site activated", "weight": 0.15, "complete": 1.0,
       "planned_period": 4}
  ],
  "periods": [
      {"period": 1, "planned_spend": 60000, "actual_spend": 72000},
      {"period": 2, "planned_spend": 80000, "actual_spend": 91000}
  ]
}

Milestone weights should sum to 1.0. `complete` is the fraction delivered, 0-1.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

# Performance indices below this are treated as materially off-plan.
INDEX_WARN = 0.90
INDEX_FAIL = 0.80
# A programme past this much of its budget with far less delivered is in trouble.
LATE_STAGE_BURN = 0.60


def _index(numerator: float, denominator: float) -> float | None:
    """Return a performance index, or None when the denominator is zero."""
    if denominator <= 0:
        return None
    return numerator / denominator


def compute(payload: dict[str, Any]) -> dict[str, Any]:
    """Compute earned value, performance indices, and the completion forecast."""
    bac = float(payload.get("budget_at_completion", 0) or 0)
    if bac <= 0:
        raise ValueError("budget_at_completion must be a positive number")

    milestones = payload.get("milestones") or []
    if not milestones:
        raise ValueError("payload must contain a non-empty 'milestones' list")
    periods = payload.get("periods") or []
    if not periods:
        raise ValueError("payload must contain a non-empty 'periods' list")

    weight_total = sum(float(m.get("weight", 0)) for m in milestones)
    if weight_total <= 0:
        raise ValueError("milestone weights must sum to a positive number")

    as_of = int(payload.get("as_of_period", 0) or max(
        int(p.get("period", 0)) for p in periods))

    completed_fraction = 0.0
    milestone_rows: list[dict[str, Any]] = []
    for m in milestones:
        weight = float(m.get("weight", 0)) / weight_total
        complete = float(m.get("complete", 0) or 0)
        if not 0 <= complete <= 1:
            raise ValueError(f"milestone '{m.get('name', '?')}' complete must be in [0, 1]")
        completed_fraction += weight * complete
        planned_period = m.get("planned_period")
        # A milestone due this period and not delivered is already overdue.
        overdue = (planned_period is not None and int(planned_period) <= as_of
                   and complete < 1.0)
        milestone_rows.append({
            "name": m.get("name", ""),
            "weight": round(weight, 4),
            "complete": complete,
            "planned_period": planned_period,
            "overdue": overdue,
        })

    elapsed = [p for p in periods if int(p.get("period", 0)) <= as_of]
    actual_cost = sum(float(p.get("actual_spend", 0) or 0) for p in elapsed)
    planned_value = sum(float(p.get("planned_spend", 0) or 0) for p in elapsed)
    earned_value = completed_fraction * bac

    cpi = _index(earned_value, actual_cost)
    spi = _index(earned_value, planned_value)

    # Cost-performance-based forecast: the cheapest honest projection.
    eac = bac / cpi if cpi else None
    overrun = (eac - bac) if eac is not None else None
    remaining_budget = bac - actual_cost
    remaining_work = bac - earned_value
    tcpi = _index(remaining_work, remaining_budget) if remaining_budget > 0 else None

    return {
        "programme": payload.get("programme", ""),
        "currency": payload.get("currency", ""),
        "as_of_period": as_of,
        "budget_at_completion": round(bac, 2),
        "actual_cost": round(actual_cost, 2),
        "planned_value": round(planned_value, 2),
        "earned_value": round(earned_value, 2),
        "percent_spent": round(actual_cost / bac, 4),
        "percent_delivered": round(completed_fraction, 4),
        "cost_performance_index": round(cpi, 3) if cpi else None,
        "schedule_performance_index": round(spi, 3) if spi else None,
        "estimate_at_completion": round(eac, 2) if eac else None,
        "forecast_overrun": round(overrun, 2) if overrun is not None else None,
        "to_complete_performance_index": round(tcpi, 3) if tcpi else None,
        "milestones": milestone_rows,
    }


def review(r: dict[str, Any]) -> list[dict[str, str]]:
    """Flag the spend/delivery patterns that predict a programme in trouble."""
    findings: list[dict[str, str]] = []
    cpi = r["cost_performance_index"]
    spi = r["schedule_performance_index"]
    spent, delivered = r["percent_spent"], r["percent_delivered"]

    if cpi is None:
        findings.append({"severity": "warn", "message":
                         "no spend recorded — cost performance cannot be assessed"})
    elif cpi < INDEX_FAIL:
        findings.append({"severity": "fail", "message":
                         f"cost performance index {cpi:.2f} — every unit of delivery is "
                         f"costing {1 / cpi:.2f}x its budget; forecast overrun "
                         f"{r['forecast_overrun']:,.0f}"})
    elif cpi < INDEX_WARN:
        findings.append({"severity": "warn", "message":
                         f"cost performance index {cpi:.2f} — drifting over budget"})

    if spi is not None and spi < INDEX_FAIL:
        findings.append({"severity": "fail", "message":
                         f"schedule performance index {spi:.2f} — delivery is well "
                         "behind the planned curve"})
    elif spi is not None and spi < INDEX_WARN:
        findings.append({"severity": "warn", "message":
                         f"schedule performance index {spi:.2f} — slipping"})

    gap = spent - delivered
    if gap > 0.20:
        findings.append({"severity": "fail", "message":
                         f"{spent:.0%} of budget spent against {delivered:.0%} delivered "
                         f"— a {gap:.0%} gap; this is the pattern that precedes a "
                         "request for supplementary funding"})
    elif gap > 0.10:
        findings.append({"severity": "warn", "message":
                         f"{spent:.0%} spent against {delivered:.0%} delivered — "
                         "watch the gap"})

    if spent > LATE_STAGE_BURN and delivered < spent - 0.15:
        findings.append({"severity": "fail", "message":
                         "past 60% of budget with delivery materially behind — "
                         "descope now; the remaining budget cannot absorb the gap"})

    tcpi = r["to_complete_performance_index"]
    if tcpi is not None and tcpi > 1.2:
        findings.append({"severity": "fail", "message":
                         f"finishing inside budget now requires efficiency of "
                         f"{tcpi:.2f} against {cpi if cpi else 0:.2f} achieved so far — "
                         "not recoverable without a scope change"})

    overdue = [m["name"] for m in r["milestones"] if m["overdue"]]
    if overdue:
        findings.append({"severity": "warn", "message":
                         f"overdue milestones: {overdue}"})

    if not findings:
        findings.append({"severity": "info", "message":
                         "spend and delivery are tracking together within tolerance"})
    return findings


def render_text(r: dict[str, Any], findings: list[dict[str, str]]) -> str:
    """Render the burn analysis as human-readable text."""
    cur = r["currency"]
    lines = [f"Burn vs milestones — {r['programme']} (period {r['as_of_period']})", "",
             f"  budget at completion   {r['budget_at_completion']:>14,.0f} {cur}",
             f"  actual cost            {r['actual_cost']:>14,.0f} {cur}",
             f"  planned value          {r['planned_value']:>14,.0f} {cur}",
             f"  earned value           {r['earned_value']:>14,.0f} {cur}", "",
             f"  spent                  {r['percent_spent']:>14.1%}",
             f"  delivered              {r['percent_delivered']:>14.1%}"]
    if r["cost_performance_index"]:
        lines.append(f"  cost performance (CPI) {r['cost_performance_index']:>14.2f}")
    if r["schedule_performance_index"]:
        lines.append(f"  sched performance (SPI){r['schedule_performance_index']:>14.2f}")
    if r["estimate_at_completion"]:
        lines.append(f"  estimate at completion {r['estimate_at_completion']:>14,.0f} {cur}")
        lines.append(f"  forecast overrun       {r['forecast_overrun']:>14,.0f} {cur}")
    if r["to_complete_performance_index"]:
        lines.append(f"  required TCPI          {r['to_complete_performance_index']:>14.2f}")
    lines.append("")
    lines.append("Milestones:")
    for m in r["milestones"]:
        flag = " OVERDUE" if m["overdue"] else ""
        lines.append(f"  {m['complete']:5.0%} (w {m['weight']:.2f})  {m['name']}{flag}")
    lines.append("")
    fails = sum(1 for f in findings if f["severity"] == "fail")
    warns = sum(1 for f in findings if f["severity"] == "warn")
    lines.append(f"Findings: {fails} fail, {warns} warn")
    order = {"fail": 0, "warn": 1, "info": 2}
    for f in sorted(findings, key=lambda x: order.get(x["severity"], 9)):
        lines.append(f"  [{f['severity'].upper():4}] {f['message']}")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Track research burn against milestone delivery and forecast overrun.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--input", required=True, help="Path to the JSON burn payload")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                        help="Output format; text is the default")
    parser.add_argument("--output", help="Write output to this file instead of stdout")
    parser.add_argument("--strict", action="store_true",
                        help="Exit non-zero if any finding has severity 'fail'")
    return parser.parse_args()


def main() -> int:
    """CLI entry point."""
    args = parse_args()
    try:
        payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
    except OSError as exc:
        print(f"error: cannot read --input '{args.input}': {exc}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as exc:
        print(f"error: --input is not valid JSON: {exc}", file=sys.stderr)
        return 1

    try:
        report = compute(payload)
        findings = review(report)
    except (ValueError, KeyError, TypeError, ZeroDivisionError) as exc:
        print(f"error: invalid burn payload: {exc}", file=sys.stderr)
        return 1

    if args.format == "json":
        out = json.dumps({**report, "findings": findings}, indent=2)
    else:
        out = render_text(report, findings)
    try:
        if args.output:
            Path(args.output).write_text(out, encoding="utf-8")
            print(f"wrote {args.output}", file=sys.stderr)
        else:
            print(out)
    except OSError as exc:
        print(f"error: cannot write --output '{args.output}': {exc}", file=sys.stderr)
        return 1

    if args.strict and any(f["severity"] == "fail" for f in findings):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
