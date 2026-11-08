#!/usr/bin/env python3
"""
viability_verdict.py — Compute a go / not-yet verdict for a business that has
not launched, from its economics report and the demand evidence collected.

The verdict is computed, never written by hand. It reads the JSON report that
launch_economics.py produces (--format json) and an evidence file listing the
cash the founder can put in and every demand test run so far. Simulated buyer
panels count, but only as unconfirmed demand: a plan can reach VIABLE only when
real people were shown a real price and enough of them committed.

Verdicts:
    VIABLE       every check passes and demand is confirmed by a real test
    UNCONFIRMED  the numbers pass; demand rests on simulated or unpriced evidence
    NOT YET      at least one check fails (the failing numbers are listed)
    INCOMPLETE   an input needed for a check is missing

Stdlib only. Deterministic. Text (default) or JSON output.

Usage:
    python3 viability_verdict.py --economics report.json --evidence evidence.json
    python3 viability_verdict.py --economics report.json --evidence evidence.json --format json

Exit codes: 0 VIABLE or UNCONFIRMED, 1 NOT YET or INCOMPLETE, 2 bad input.

Evidence schema (see assets/sample_evidence.json):
{
  "funding_available": float,
  "demand_evidence": [{"kind": "presale"|"waitlist"|"pilot"|"landing_page"|
                       "interviews"|"simulated_panel",
                       "reached": int, "converted": int, "price_shown": bool,
                       "note": str}],
  "thresholds": {"min_real_conversion": 0.05, "min_panel_buy_rate": 0.25,
                 "min_real_sample": 30, "funding_buffer": 1.2}
}
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

KINDS = ("presale", "waitlist", "pilot", "landing_page", "interviews", "simulated_panel")
DEFAULTS = {"min_real_conversion": 0.05, "min_panel_buy_rate": 0.25,
            "min_real_sample": 30, "funding_buffer": 1.2}
REQUIRED_ECON = ("business", "contribution_per_unit", "year1_operating_profit",
                 "break_even_per_day", "capacity_per_day", "cash_needed", "what_ifs")


class InputError(ValueError):
    """Raised when an input file cannot be used at all."""


def _read(path: str) -> Any:
    """Read and parse a JSON file, mapping failures to InputError."""
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except OSError as exc:
        raise InputError(f"cannot read {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise InputError(f"{path} is not valid JSON: {exc}") from exc


def check_economics(econ: dict[str, Any]) -> list[dict[str, Any]]:
    """Return the economics checks (margin, year one, break-even, capacity, stress) as rows."""
    rows = []
    c = econ["contribution_per_unit"]
    rows.append({"check": "each unit earns money before fixed costs",
                 "status": "pass" if c > 0 else "fail", "value": c})
    y1 = econ["year1_operating_profit"]
    rows.append({"check": "year one makes an operating profit",
                 "status": "pass" if y1 >= 0 else "fail", "value": y1})
    bep, cap = econ["break_even_per_day"], econ["capacity_per_day"]
    if cap is None:
        status = "pass" if bep is not None else "fail"
    else:
        status = "pass" if bep is not None and bep <= cap else "fail"
    rows.append({"check": "break-even fits inside capacity", "status": status,
                 "value": f"{bep} vs {cap if cap is not None else 'no limit'}"})
    over = [f["message"] if isinstance(f, dict) else str(f) for f in econ.get("findings") or []
            if (f.get("severity") if isinstance(f, dict) else "") == "fail" and "capacity" in str(f)]
    plan = econ.get("plan_per_day")
    if not over and cap is not None and isinstance(plan, (int, float)) and plan > cap:
        over.append(f"plan {plan:g}/day exceeds capacity {cap:g}/day")
    rows.append({"check": "plan and ramp fit inside capacity", "status": "fail" if over else "pass",
                 "value": "; ".join(dict.fromkeys(over)) or "fits"})
    worst = min(econ["what_ifs"], key=lambda w: w["year1_operating_profit"]) if econ["what_ifs"] else None
    if worst is not None:
        ok = worst["year1_operating_profit"] >= 0
        rows.append({"check": "year one survives the worst what-if",
                     "status": "pass" if ok else "warn",
                     "value": f"{worst['case']}: {worst['year1_operating_profit']:,.0f}"})
    return rows


def check_funding(econ: dict[str, Any], evidence: dict[str, Any],
                  t: dict[str, float]) -> dict[str, Any]:
    """Compare the cash the founder has against the cash the model needs."""
    have = evidence.get("funding_available")
    need = econ["cash_needed"]
    if have is None:
        return {"check": "funding covers the cash needed", "status": "missing",
                "value": f"need {need:,.0f}; funding_available not given"}
    if not isinstance(have, (int, float)) or isinstance(have, bool) or have < 0:
        raise InputError("funding_available must be a non-negative number")
    if have < need:
        status = "fail"
    elif have < need * t["funding_buffer"]:
        status = "warn"
    else:
        status = "pass"
    return {"check": "funding covers the cash needed", "status": status,
            "value": f"have {have:,.0f}, need {need:,.0f} (+{t['funding_buffer'] - 1:.0%} buffer)"}


def check_demand(evidence: dict[str, Any], t: dict[str, float]) -> dict[str, Any]:
    """Classify the demand evidence: confirmed, unconfirmed, failed or missing."""
    items = evidence.get("demand_evidence") or []
    if not isinstance(items, list):
        raise InputError("demand_evidence must be a list")
    real_pass, real_fail, panel_pass, notes = [], [], [], []
    for i, item in enumerate(items):
        kind = item.get("kind") if isinstance(item, dict) else None
        if kind not in KINDS:
            raise InputError(f"demand_evidence[{i}].kind must be one of {KINDS}")
        reached, converted = item.get("reached"), item.get("converted")
        if not all(isinstance(v, int) and not isinstance(v, bool) and v >= 0
                   for v in (reached, converted)) or converted > reached:
            raise InputError(f"demand_evidence[{i}] needs integers reached >= converted >= 0")
        rate = converted / reached if reached else 0.0
        label = f"{kind}: {converted}/{reached} ({rate:.0%})"
        if kind == "simulated_panel":
            (panel_pass if rate >= t["min_panel_buy_rate"] else real_fail).append(label)
            notes.append(f"{label} - simulated, an upper bound at best")
        elif not item.get("price_shown") or kind == "interviews":
            notes.append(f"{label} - no price at the moment of commitment, does not confirm demand")
        elif reached < t["min_real_sample"]:
            notes.append(f"{label} - fewer than {t['min_real_sample']:.0f} reached, too small to read")
        elif rate >= t["min_real_conversion"]:
            real_pass.append(label)
        else:
            real_fail.append(label)
    if real_pass:
        status = "pass"
    elif real_fail:
        status = "fail"
    elif panel_pass or notes:
        status = "unconfirmed"
    else:
        status = "missing"
    return {"check": "demand confirmed by people shown a real price", "status": status,
            "value": "; ".join(real_pass or real_fail or panel_pass) or "no usable test",
            "notes": notes}


def verdict(econ: dict[str, Any], evidence: dict[str, Any]) -> dict[str, Any]:
    """Assemble every check and compute the verdict."""
    missing = [k for k in REQUIRED_ECON if k not in econ]
    if missing:
        raise InputError(f"economics report is missing {missing}; run launch_economics.py --format json")
    t = dict(DEFAULTS)
    for k, v in (evidence.get("thresholds") or {}).items():
        if k in DEFAULTS:
            try:
                t[k] = float(v)
            except (TypeError, ValueError):
                raise InputError(f"threshold {k!r} must be a number, got {v!r}") from None
    rows = check_economics(econ) + [check_funding(econ, evidence, t), check_demand(evidence, t)]
    statuses = [r["status"] for r in rows]
    if "fail" in statuses:
        result = "NOT YET"
    elif "missing" in statuses:
        result = "INCOMPLETE"
    elif "unconfirmed" in statuses:
        result = "UNCONFIRMED"
    else:
        result = "VIABLE"
    actions = []
    for r in rows:
        if r["status"] in ("fail", "missing"):
            actions.append(f"fix: {r['check']} ({r['value']})")
        elif r["status"] == "unconfirmed":
            actions.append("run a priced real-world test (pre-sale, deposit or pilot) before committing money")
        elif r["status"] == "warn":
            actions.append(f"watch: {r['check']} ({r['value']})")
    return {"business": econ["business"], "verdict": result, "checks": rows,
            "thresholds": t, "next_actions": actions,
            "key_numbers": {k: econ.get(k) for k in (
                "price", "contribution_per_unit", "margin_at_plan", "break_even_per_day",
                "year1_operating_profit", "cash_needed", "payback_month")}}


def render_text(r: dict[str, Any]) -> str:
    """Render the verdict for a person."""
    lines = [f"Viability verdict — {r['business']}", f"VERDICT: {r['verdict']}", "", "Checks:"]
    for row in r["checks"]:
        lines.append(f"  [{row['status'].upper():11}] {row['check']}: {row['value']}")
        lines += [f"                {n}" for n in row.get("notes", [])]
    lines += ["", "Key numbers:"]
    lines += [f"  {k}: {v}" for k, v in r["key_numbers"].items()]
    if r["next_actions"]:
        lines += ["", "Next actions:"] + [f"  - {a}" for a in r["next_actions"]]
    return "\n".join(lines)


def main() -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Compute a viability verdict from an economics report and demand evidence.",
        formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    parser.add_argument("--economics", required=True,
                        help="JSON report written by launch_economics.py --format json")
    parser.add_argument("--evidence", required=True, help="Evidence JSON (funding and demand tests)")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                        help="Output format (default: text)")
    args = parser.parse_args()
    try:
        econ, evidence = _read(args.economics), _read(args.evidence)
        if not isinstance(econ, dict) or not isinstance(evidence, dict):
            raise InputError("both files must contain a JSON object")
        report = verdict(econ, evidence)
    except (InputError, TypeError, KeyError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(report, indent=2) if args.format == "json" else render_text(report))
    return 0 if report["verdict"] in ("VIABLE", "UNCONFIRMED") else 1


if __name__ == "__main__":
    sys.exit(main())
