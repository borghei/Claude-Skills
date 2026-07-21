#!/usr/bin/env python3
"""
study_budget_builder.py — Build a study budget from unit costs and report the
cost-per-participant and cost-per-insight the funder will actually ask about.

Reads a JSON budget spec containing participant-driven unit costs, site-driven
costs, fixed programme costs, and a duration. Expands them into line items,
grosses participant costs up for screen failure, applies contingency and
overhead, and flags the structural problems that make research budgets
under-fund themselves.

Stdlib only. Deterministic. Text (default) or JSON output.

Usage:
    python3 study_budget_builder.py --input budget.json
    python3 study_budget_builder.py --input budget.json --format json
    python3 study_budget_builder.py --input budget.json --strict

Input schema:
{
  "study": "...", "currency": "EUR",
  "participants_enrolled": 408, "screen_failure_rate": 0.25,
  "sites": 6, "duration_months": 30,
  "expected_insights": 12,
  "per_participant": {"screening": 320, "visits": 1150, "incentive": 150,
                      "lab": 480},
  "per_participant_screened_only": {"screening": true},
  "per_site": {"startup": 12000, "closeout": 4000},
  "per_site_month": {"coordination": 900},
  "fixed": {"protocol_development": 45000, "biostatistics": 38000,
            "data_management": 52000, "monitoring": 90000},
  "contingency_rate": 0.10, "overhead_rate": 0.20
}

Entries in per_participant listed as true in per_participant_screened_only are
charged on screened participants; everything else is charged on enrolled only.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

# Below this, a research budget has no absorption capacity for the scope changes
# that occur in essentially every study.
MIN_CONTINGENCY = 0.08
# Above this share, the budget is paying for structure rather than for evidence.
MAX_FIXED_SHARE = 0.55


def _expand(costs: dict[str, Any], multiplier: float, category: str,
            basis: str) -> list[dict[str, Any]]:
    """Expand a unit-cost block into line items at the given multiplier."""
    lines: list[dict[str, Any]] = []
    for name, unit_cost in costs.items():
        value = float(unit_cost)
        if value < 0:
            raise ValueError(f"{category} cost '{name}' is negative")
        lines.append({
            "category": category,
            "name": name,
            "unit_cost": round(value, 2),
            "units": round(multiplier, 2),
            "basis": basis,
            "total": round(value * multiplier, 2),
        })
    return lines


def build(spec: dict[str, Any]) -> dict[str, Any]:
    """Expand every cost block into line items and total the budget."""
    enrolled = float(spec.get("participants_enrolled", 0) or 0)
    if enrolled <= 0:
        raise ValueError("participants_enrolled must be a positive number")
    screen_fail = float(spec.get("screen_failure_rate", 0) or 0)
    if not 0 <= screen_fail < 1:
        raise ValueError("screen_failure_rate must be in [0, 1)")
    sites = float(spec.get("sites", 0) or 0)
    months = float(spec.get("duration_months", 0) or 0)
    if sites <= 0 or months <= 0:
        raise ValueError("sites and duration_months must both be positive")

    screened = enrolled / (1 - screen_fail)
    screened_only = spec.get("per_participant_screened_only") or {}

    lines: list[dict[str, Any]] = []
    per_participant = spec.get("per_participant") or {}
    for name, unit_cost in per_participant.items():
        on_screened = bool(screened_only.get(name))
        multiplier = screened if on_screened else enrolled
        basis = "per screened participant" if on_screened else "per enrolled participant"
        lines.extend(_expand({name: unit_cost}, multiplier, "participant", basis))

    lines.extend(_expand(spec.get("per_site") or {}, sites, "site", "per site"))
    lines.extend(_expand(spec.get("per_site_month") or {}, sites * months,
                         "site", "per site-month"))
    lines.extend(_expand(spec.get("fixed") or {}, 1.0, "fixed", "fixed"))

    if not lines:
        raise ValueError("budget spec contains no cost blocks")

    direct = sum(line["total"] for line in lines)
    contingency_rate = float(spec.get("contingency_rate", 0) or 0)
    overhead_rate = float(spec.get("overhead_rate", 0) or 0)
    for name, rate in (("contingency_rate", contingency_rate),
                       ("overhead_rate", overhead_rate)):
        if not 0 <= rate < 1:
            raise ValueError(f"{name} must be in [0, 1)")

    contingency = direct * contingency_rate
    overhead = (direct + contingency) * overhead_rate
    total = direct + contingency + overhead

    by_category: dict[str, float] = {}
    for line in lines:
        by_category[line["category"]] = by_category.get(line["category"], 0.0) + line["total"]

    insights = float(spec.get("expected_insights", 0) or 0)

    return {
        "study": spec.get("study", ""),
        "currency": spec.get("currency", ""),
        "participants_enrolled": enrolled,
        "participants_screened": math.ceil(screened),
        "screen_failure_rate": screen_fail,
        "sites": sites,
        "duration_months": months,
        "line_items": sorted(lines, key=lambda x: -x["total"]),
        "by_category": {k: round(v, 2) for k, v in by_category.items()},
        "direct_costs": round(direct, 2),
        "contingency": round(contingency, 2),
        "overhead": round(overhead, 2),
        "total": round(total, 2),
        "cost_per_enrolled": round(total / enrolled, 2),
        "cost_per_screened": round(total / screened, 2),
        "cost_per_site_month": round(total / (sites * months), 2),
        "cost_per_insight": round(total / insights, 2) if insights else None,
        "monthly_burn_average": round(total / months, 2),
    }


def review(budget: dict[str, Any], spec: dict[str, Any]) -> list[dict[str, str]]:
    """Flag structural problems that make a research budget under-fund itself."""
    findings: list[dict[str, str]] = []
    total = budget["total"]

    if budget["screen_failure_rate"] == 0:
        findings.append({"severity": "fail", "message":
                         "screen_failure_rate is 0 — no study screens only the "
                         "participants it enrols; screening costs will be unfunded"})
    elif budget["screen_failure_rate"] < 0.10:
        findings.append({"severity": "warn", "message":
                         f"screen failure of {budget['screen_failure_rate']:.0%} is "
                         "optimistic for most protocols; check it against comparable "
                         "studies"})

    contingency_rate = float(spec.get("contingency_rate", 0) or 0)
    if contingency_rate < MIN_CONTINGENCY:
        findings.append({"severity": "fail", "message":
                         f"contingency of {contingency_rate:.0%} is below the "
                         f"{MIN_CONTINGENCY:.0%} floor — a research budget with no "
                         "absorption capacity requires a change request for every "
                         "protocol amendment"})

    fixed_share = budget["by_category"].get("fixed", 0) / total if total else 0
    if fixed_share > MAX_FIXED_SHARE:
        findings.append({"severity": "warn", "message":
                         f"fixed costs are {fixed_share:.0%} of the budget — above "
                         f"{MAX_FIXED_SHARE:.0%} the study is paying mostly for "
                         "structure; consider whether the scope justifies it"})

    if not spec.get("per_site_month"):
        findings.append({"severity": "warn", "message":
                         "no per-site-month costs — site coordination is an ongoing "
                         "cost for the full duration and is routinely omitted"})

    covered = set((spec.get("fixed") or {}).keys())
    for expected, label in (("biostatistics", "biostatistics"),
                            ("data_management", "data management"),
                            ("monitoring", "monitoring")):
        if not any(expected in key for key in covered):
            findings.append({"severity": "warn", "message":
                             f"no {label} line in fixed costs — commonly forgotten and "
                             "rarely absorbable later"})

    if budget["cost_per_insight"] is None:
        findings.append({"severity": "warn", "message":
                         "expected_insights not stated — without it the budget cannot "
                         "be compared against alternative uses of the same money"})

    return findings


def render_text(b: dict[str, Any], findings: list[dict[str, str]]) -> str:
    """Render the budget as human-readable text."""
    cur = b["currency"]
    lines = [f"Study budget — {b['study']}",
             f"{b['participants_enrolled']:.0f} enrolled "
             f"({b['participants_screened']:,} screened at "
             f"{b['screen_failure_rate']:.0%} failure) | "
             f"{b['sites']:.0f} sites | {b['duration_months']:.0f} months", "",
             f"  {'CATEGORY':12} {'LINE':26} {'UNIT':>10} {'UNITS':>9} {'TOTAL':>14}"]
    for line in b["line_items"]:
        lines.append(f"  {line['category']:12} {line['name'][:26]:26} "
                     f"{line['unit_cost']:10,.0f} {line['units']:9,.1f} "
                     f"{line['total']:14,.0f}")
    lines.append("")
    lines.append(f"  {'direct costs':40} {b['direct_costs']:>21,.0f} {cur}")
    lines.append(f"  {'contingency':40} {b['contingency']:>21,.0f} {cur}")
    lines.append(f"  {'overhead':40} {b['overhead']:>21,.0f} {cur}")
    lines.append(f"  {'TOTAL':40} {b['total']:>21,.0f} {cur}")
    lines.append("")
    lines.append("Unit economics:")
    lines.append(f"  per enrolled participant   {b['cost_per_enrolled']:>12,.0f} {cur}")
    lines.append(f"  per screened participant   {b['cost_per_screened']:>12,.0f} {cur}")
    lines.append(f"  per site-month             {b['cost_per_site_month']:>12,.0f} {cur}")
    if b["cost_per_insight"] is not None:
        lines.append(f"  per expected insight       {b['cost_per_insight']:>12,.0f} {cur}")
    lines.append(f"  average monthly burn       {b['monthly_burn_average']:>12,.0f} {cur}")
    lines.append("")
    fails = sum(1 for f in findings if f["severity"] == "fail")
    lines.append(f"Findings: {fails} fail, {len(findings) - fails} warn")
    for f in sorted(findings, key=lambda x: 0 if x["severity"] == "fail" else 1):
        lines.append(f"  [{f['severity'].upper():4}] {f['message']}")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Build a study budget from unit costs and review its structure.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--input", required=True, help="Path to the JSON budget spec")
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
        spec = json.loads(Path(args.input).read_text(encoding="utf-8"))
    except OSError as exc:
        print(f"error: cannot read --input '{args.input}': {exc}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as exc:
        print(f"error: --input is not valid JSON: {exc}", file=sys.stderr)
        return 1

    try:
        budget = build(spec)
        findings = review(budget, spec)
    except (ValueError, KeyError, TypeError, ZeroDivisionError) as exc:
        print(f"error: invalid budget spec: {exc}", file=sys.stderr)
        return 1

    if args.format == "json":
        out = json.dumps({**budget, "findings": findings}, indent=2)
    else:
        out = render_text(budget, findings)
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
