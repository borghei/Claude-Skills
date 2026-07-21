#!/usr/bin/env python3
"""
portfolio_prioritizer.py — Rank a research portfolio by expected decision value
per unit of spend.

Applies value-of-information logic: a study is worth funding to the extent that
it changes a decision, and a decision is worth informing to the extent that
getting it wrong is expensive. Studies that inform decisions already made, or
that cost more than the decision is worth, are surfaced explicitly rather than
being ranked low and quietly funded anyway.

Stdlib only. Deterministic. Text (default) or JSON output.

Usage:
    python3 portfolio_prioritizer.py --input portfolio.json
    python3 portfolio_prioritizer.py --input portfolio.json --format json
    python3 portfolio_prioritizer.py --input portfolio.json --budget 400000

Input schema (see assets/sample_portfolio.json for a complete example):
{
  "portfolio": str, "currency": str, "available_budget": float,
  "studies": [{"id", "name", "cost",
               "decision_value",                 # cost of deciding wrong
               "probability_changes_decision",   # 0.0-1.0
               "decision_reversibility": "sprint"|"quarter"|"costly"
                                         |"one_way_door",
               "months_to_answer", "decision_deadline_months",
               "decision_already_made": bool}]
}
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

# A reversible decision can be corrected cheaply, so information about it is
# worth less regardless of the headline decision value.
REVERSIBILITY_MULTIPLIER = {
    "sprint": 0.15,
    "quarter": 0.45,
    "costly": 0.85,
    "one_way_door": 1.0,
}

# Concentration above this share of the portfolio in one study is a risk.
CONCENTRATION_WARN = 0.40


def score_study(study: dict[str, Any]) -> dict[str, Any]:
    """Compute expected decision value and value per unit cost for one study."""
    study_id = str(study.get("id", "?"))
    cost = float(study.get("cost", 0) or 0)
    if cost <= 0:
        raise ValueError(f"study {study_id}: cost must be a positive number")

    decision_value = float(study.get("decision_value", 0) or 0)
    if decision_value < 0:
        raise ValueError(f"study {study_id}: decision_value cannot be negative")

    p_change = float(study.get("probability_changes_decision", 0) or 0)
    if not 0 <= p_change <= 1:
        raise ValueError(
            f"study {study_id}: probability_changes_decision must be in [0, 1]")

    reversibility = str(study.get("decision_reversibility", "costly")).lower()
    if reversibility not in REVERSIBILITY_MULTIPLIER:
        raise ValueError(
            f"study {study_id}: decision_reversibility '{reversibility}'; expected "
            f"one of {sorted(REVERSIBILITY_MULTIPLIER)}")

    # Expected value of the information: the decision value at stake, weighted
    # by the chance the study actually changes the choice, discounted by how
    # cheaply a wrong choice could be undone anyway.
    expected_value = (decision_value * p_change
                      * REVERSIBILITY_MULTIPLIER[reversibility])

    # A study that lands after the decision has to be made buys nothing.
    months = float(study.get("months_to_answer", 0) or 0)
    deadline = study.get("decision_deadline_months")
    too_late = deadline is not None and months > float(deadline)
    if too_late:
        expected_value = 0.0

    already_made = bool(study.get("decision_already_made"))
    if already_made:
        expected_value = 0.0

    return {
        "id": study_id,
        "name": study.get("name", ""),
        "cost": round(cost, 2),
        "decision_value": round(decision_value, 2),
        "probability_changes_decision": p_change,
        "reversibility": reversibility,
        "months_to_answer": months,
        "expected_decision_value": round(expected_value, 2),
        "value_per_unit_cost": round(expected_value / cost, 2),
        "net_value": round(expected_value - cost, 2),
        "arrives_too_late": too_late,
        "decision_already_made": already_made,
        "fundable": expected_value > cost and not too_late and not already_made,
    }


def allocate(scored: list[dict[str, Any]], budget: float) -> dict[str, Any]:
    """Greedily fund studies by value per unit cost within the available budget."""
    ranked = sorted(scored, key=lambda s: -s["value_per_unit_cost"])
    funded: list[str] = []
    deferred: list[str] = []
    spent = 0.0
    captured = 0.0
    for study in ranked:
        if not study["fundable"]:
            deferred.append(study["id"])
            continue
        if spent + study["cost"] <= budget:
            funded.append(study["id"])
            spent += study["cost"]
            captured += study["expected_decision_value"]
        else:
            deferred.append(study["id"])
    return {
        "funded": funded,
        "deferred": deferred,
        "budget_used": round(spent, 2),
        "budget_remaining": round(budget - spent, 2),
        "expected_value_captured": round(captured, 2),
    }


def review(scored: list[dict[str, Any]], allocation: dict[str, Any],
           budget: float) -> list[dict[str, str]]:
    """Flag portfolio-level problems that ranking alone does not surface."""
    findings: list[dict[str, str]] = []

    already = [s["id"] for s in scored if s["decision_already_made"]]
    if already:
        findings.append({"severity": "fail", "message":
                         f"studies informing decisions already made: {already} — "
                         "these are documentation, not research; cut them"})

    late = [s["id"] for s in scored if s["arrives_too_late"]]
    if late:
        findings.append({"severity": "fail", "message":
                         f"studies answering after the decision deadline: {late} — "
                         "compress the method or accept the decision goes unevidenced"})

    upside_down = [s["id"] for s in scored
                   if s["expected_decision_value"] < s["cost"]
                   and not s["decision_already_made"] and not s["arrives_too_late"]]
    if upside_down:
        findings.append({"severity": "fail", "message":
                         f"studies costing more than their expected decision value: "
                         f"{upside_down} — the evidence is not worth what it costs"})

    reversible = [s["id"] for s in scored if s["reversibility"] == "sprint"]
    if reversible:
        findings.append({"severity": "warn", "message":
                         f"studies on sprint-reversible decisions: {reversible} — ship "
                         "an experiment instead; it is faster and yields better evidence"})

    total_cost = sum(s["cost"] for s in scored)
    if total_cost > budget:
        findings.append({"severity": "warn", "message":
                         f"portfolio asks {total_cost:,.0f} against a budget of "
                         f"{budget:,.0f} — {allocation['budget_used'] / budget:.0%} "
                         "of budget allocated to the highest-value subset"})

    funded_studies = [s for s in scored if s["id"] in allocation["funded"]]
    if funded_studies and allocation["budget_used"] > 0:
        top = max(funded_studies, key=lambda s: s["cost"])
        share = top["cost"] / allocation["budget_used"]
        if share > CONCENTRATION_WARN:
            findings.append({"severity": "warn", "message":
                             f"{top['id']} consumes {share:.0%} of allocated spend — "
                             "a single study carrying the portfolio means one delay "
                             "stalls all evidence delivery"})

    unfunded_valuable = [s["id"] for s in scored
                         if s["fundable"] and s["id"] in allocation["deferred"]]
    if unfunded_valuable:
        findings.append({"severity": "warn", "message":
                         f"value-positive studies left unfunded: {unfunded_valuable} — "
                         "these are the case for a budget increase"})

    return findings


def analyse(payload: dict[str, Any], budget_override: float | None = None) -> dict[str, Any]:
    """Score every study, allocate the budget, and review the portfolio."""
    studies = payload.get("studies") or []
    if not studies:
        raise ValueError("payload must contain a non-empty 'studies' list")
    budget = float(budget_override
                   if budget_override is not None
                   else payload.get("available_budget", 0) or 0)
    if budget <= 0:
        raise ValueError("available_budget must be positive (or pass --budget)")

    scored = [score_study(s) for s in studies]
    allocation = allocate(scored, budget)
    findings = review(scored, allocation, budget)

    return {
        "portfolio": payload.get("portfolio", ""),
        "currency": payload.get("currency", ""),
        "available_budget": round(budget, 2),
        "study_count": len(scored),
        "studies": sorted(scored, key=lambda s: -s["value_per_unit_cost"]),
        "allocation": allocation,
        "findings": findings,
    }


def render_text(r: dict[str, Any]) -> str:
    """Render the portfolio ranking as human-readable text."""
    cur = r["currency"]
    a = r["allocation"]
    lines = [f"Research portfolio — {r['portfolio']}",
             f"Budget: {r['available_budget']:,.0f} {cur} | "
             f"Studies: {r['study_count']}", "",
             f"  {'ID':5} {'COST':>10} {'EDV':>12} {'EDV/COST':>9} "
             f"{'NET':>12} {'FUND':>5}  NAME"]
    for s in r["studies"]:
        fund = "yes" if s["id"] in a["funded"] else "no"
        lines.append(f"  {s['id']:5} {s['cost']:10,.0f} "
                     f"{s['expected_decision_value']:12,.0f} "
                     f"{s['value_per_unit_cost']:9.2f} {s['net_value']:12,.0f} "
                     f"{fund:>5}  {s['name']}")
    lines.append("")
    lines.append(f"Funded: {', '.join(a['funded']) or 'none'}")
    lines.append(f"Deferred: {', '.join(a['deferred']) or 'none'}")
    lines.append(f"Budget used {a['budget_used']:,.0f} of {r['available_budget']:,.0f} "
                 f"{cur} | expected value captured {a['expected_value_captured']:,.0f} {cur}")
    lines.append("")
    fails = sum(1 for f in r["findings"] if f["severity"] == "fail")
    lines.append(f"Findings: {fails} fail, {len(r['findings']) - fails} warn")
    for f in sorted(r["findings"], key=lambda x: 0 if x["severity"] == "fail" else 1):
        lines.append(f"  [{f['severity'].upper():4}] {f['message']}")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Rank a research portfolio by expected decision value per unit cost.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--input", required=True, help="Path to the JSON portfolio")
    parser.add_argument("--budget", type=float,
                        help="Override the available_budget in the payload")
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
        report = analyse(payload, args.budget)
        out = (json.dumps(report, indent=2) if args.format == "json"
               else render_text(report))
        if args.output:
            Path(args.output).write_text(out, encoding="utf-8")
            print(f"wrote {args.output}", file=sys.stderr)
        else:
            print(out)
    except OSError as exc:
        print(f"error: cannot read or write file: {exc}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as exc:
        print(f"error: --input is not valid JSON: {exc}", file=sys.stderr)
        return 1
    except (ValueError, KeyError, TypeError, ZeroDivisionError) as exc:
        print(f"error: invalid portfolio: {exc}", file=sys.stderr)
        return 1

    if args.strict and any(f["severity"] == "fail" for f in report["findings"]):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
