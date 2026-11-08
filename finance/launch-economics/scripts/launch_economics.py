#!/usr/bin/env python3
"""
launch_economics.py — Unit economics and year-one cash model for a business
that has not opened yet.

Reads one JSON file describing the price of a unit, what each unit costs to
deliver, the monthly fixed costs, the one-off startup spend, the volume plan and
a 12-month ramp. Reports contribution per unit, break-even volume per day, the
operating margin at plan, a month-by-month year one, the cash the founder must
carry before the business funds itself, the payback month and four what-ifs.

All figures come from the input file. Absent fields stop the run rather than being guessed.

Stdlib only. Deterministic. Text (default) or JSON output.

Usage:
    python3 launch_economics.py --input numbers.json
    python3 launch_economics.py --input numbers.json --format json
    python3 launch_economics.py --input numbers.json --price 7.25 --volume-factor 0.8

Exit codes: 0 no fail findings, 1 at least one fail finding, 2 bad input.

Input schema (see assets/sample_launch_numbers.json):
{
  "business": str, "unit": str, "price": float,
  "variable_costs": [{"item": str, "cost": float, "source": "quote"|"public"|"estimate"}],
  "fixed_monthly":  [{"item": str, "cost": float, "source": ...}],
  "startup":        [{"item": str, "cost": float, "source": ...}],
  "operating_days_per_month": int, "plan_per_day": float,
  "capacity_per_day": float | null, "ramp_per_day": [12 floats]
}
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

SOURCES = ("quote", "public", "estimate")
ESTIMATE_SHARE_WARN = 0.5      # more than half the cost base is guesswork
FAST_RAMP_WARN = 0.8           # month 1 at 80%+ of plan is rarely true
PAYBACK_WARN_MONTHS = 12
WHAT_IFS = (
    ("price -10%", {"price": 0.90}),
    ("volume -20%", {"volume": 0.80}),
    ("unit costs +15%", {"variable": 1.15}),
    ("fixed costs +10%", {"fixed": 1.10}),
)


class InputError(ValueError):
    """Raised when the input file is structurally unusable."""


def _num(payload: dict[str, Any], key: str, allow_none: bool = False) -> float | None:
    """Read a required non-negative number from the payload."""
    if key not in payload:
        raise InputError(f"missing required field '{key}'")
    value = payload[key]
    if value is None and allow_none:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0:
        raise InputError(f"field '{key}' must be a non-negative number")
    return float(value)


def _lines(payload: dict[str, Any], key: str) -> list[dict[str, Any]]:
    """Validate a list of cost lines and return it."""
    lines = payload.get(key)
    if not isinstance(lines, list):
        raise InputError(f"field '{key}' must be a list of cost lines")
    for i, line in enumerate(lines):
        if not isinstance(line, dict) or "item" not in line or "cost" not in line:
            raise InputError(f"{key}[{i}] needs 'item' and 'cost'")
        if not isinstance(line["cost"], (int, float)) or line["cost"] < 0:
            raise InputError(f"{key}[{i}] cost must be a non-negative number")
        if line.get("source", "estimate") not in SOURCES:
            raise InputError(f"{key}[{i}] source must be one of {SOURCES}")
    return lines


def load(payload: dict[str, Any]) -> dict[str, Any]:
    """Validate the raw payload and normalise it into a model."""
    if not isinstance(payload, dict):
        raise InputError("top level must be a JSON object")
    ramp = payload.get("ramp_per_day")
    if not isinstance(ramp, list) or len(ramp) != 12 or not all(
            isinstance(v, (int, float)) and v >= 0 for v in ramp):
        raise InputError("ramp_per_day must be a list of 12 non-negative numbers")
    days = _num(payload, "operating_days_per_month")
    if not days or days > 31:
        raise InputError("operating_days_per_month must be between 1 and 31")
    return {
        "business": str(payload.get("business", "unnamed")),
        "unit": str(payload.get("unit", "unit")),
        "price": _num(payload, "price"),
        "variable": _lines(payload, "variable_costs"),
        "fixed": _lines(payload, "fixed_monthly"),
        "startup": _lines(payload, "startup"),
        "days": days,
        "plan": _num(payload, "plan_per_day"),
        "capacity": _num(payload, "capacity_per_day", allow_none=True),
        "ramp": [float(v) for v in ramp],
    }


def _total(lines: list[dict[str, Any]]) -> float:
    """Sum the cost of a list of lines."""
    return sum(float(line["cost"]) for line in lines)


def project(m: dict[str, Any], price: float, variable: float, fixed: float,
            volume: float) -> dict[str, Any]:
    """Project year one under one set of drivers; volume scales plan and ramp."""
    startup = _total(m["startup"])
    contribution = price - variable
    cap = m["capacity"]
    months, cumulative, trough, payback = [], -startup, -startup, None
    for i, per_day in enumerate(m["ramp"], start=1):
        sold = per_day * volume if cap is None else min(per_day * volume, cap)  # cannot sell past capacity
        units = sold * m["days"]
        revenue = units * price
        operating = units * contribution - fixed
        cumulative += operating
        trough = min(trough, cumulative)
        if cumulative >= 0 and payback is None:
            payback = i
        elif cumulative < 0:
            payback = None  # dipped back below zero: payback is not reached yet
        months.append({"month": i, "units": round(units), "revenue": round(revenue, 2),
                       "operating_profit": round(operating, 2),
                       "cumulative_cash": round(cumulative, 2)})
    plan_day = m["plan"] * volume if cap is None else min(m["plan"] * volume, cap)
    plan_units = plan_day * m["days"]
    plan_revenue = plan_units * price
    plan_profit = plan_units * contribution - fixed
    year1 = sum(row["operating_profit"] for row in months)
    return {
        "contribution_per_unit": round(contribution, 4),
        "contribution_margin": round(contribution / price, 4) if price else 0.0,
        "break_even_per_day": round(fixed / (contribution * m["days"]), 1) if contribution > 0 else None,
        "margin_at_plan": round(plan_profit / plan_revenue, 4) if plan_revenue else 0.0,
        "monthly_profit_at_plan": round(plan_profit, 2),
        "year1_operating_profit": round(year1, 2),
        "year1_after_startup": round(year1 - startup, 2),
        "cash_needed": round(-trough, 2) if trough < 0 else 0.0,
        "payback_month": payback,
        "months": months,
    }


def analyse(m: dict[str, Any], price: float | None = None,
            volume_factor: float = 1.0) -> dict[str, Any]:
    """Run the base case, the what-ifs and the findings."""
    price = m["price"] if price is None else price
    variable, fixed, startup = _total(m["variable"]), _total(m["fixed"]), _total(m["startup"])
    base = project(m, price, variable, fixed, volume_factor)
    what_ifs = []
    for label, mult in WHAT_IFS:
        case = project(m, price * mult.get("price", 1), variable * mult.get("variable", 1),
                       fixed * mult.get("fixed", 1), volume_factor * mult.get("volume", 1))
        what_ifs.append({"case": label, "margin_at_plan": case["margin_at_plan"],
                         "year1_operating_profit": case["year1_operating_profit"],
                         "cash_needed": case["cash_needed"], "payback_month": case["payback_month"]})
    findings: list[dict[str, str]] = []

    def add(sev: str, msg: str) -> None:
        findings.append({"severity": sev, "message": msg})

    if base["contribution_per_unit"] <= 0:
        add("fail", f"each {m['unit']} loses money before fixed costs: price {price:.2f} "
                    f"vs unit cost {variable:.2f}")
    if base["year1_operating_profit"] < 0:
        add("fail", f"year one runs at an operating loss of {-base['year1_operating_profit']:,.0f}")
    cap = m["capacity"]
    if cap is not None:
        bep = base["break_even_per_day"]
        if bep is not None and bep > cap:
            add("fail", f"break-even needs {bep:.0f}/day but capacity is {cap:.0f}/day")
        if m["plan"] * volume_factor > cap:
            add("fail", f"plan of {m['plan'] * volume_factor:.0f}/day exceeds capacity of {cap:.0f}/day")
        if max(m["ramp"]) * volume_factor > cap:
            add("fail", "the ramp exceeds capacity in at least one month")
    if base["payback_month"] is None:
        add("warn", "startup spend is not earned back inside year one")
    elif base["payback_month"] > PAYBACK_WARN_MONTHS:
        add("warn", f"payback in month {base['payback_month']}")
    if m["plan"] and m["ramp"][0] >= FAST_RAMP_WARN * m["plan"]:
        add("warn", f"month 1 volume is {m['ramp'][0] / m['plan']:.0%} of plan; ramps this fast need evidence")
    all_lines = m["variable"] + m["fixed"] + m["startup"]
    est = _total([ln for ln in all_lines if ln.get("source", "estimate") == "estimate"])
    share = est / _total(all_lines) if _total(all_lines) else 1.0
    if share > ESTIMATE_SHARE_WARN:
        add("warn", f"{share:.0%} of cost lines by value are estimates; get quotes")
    worst = min(what_ifs, key=lambda w: w["year1_operating_profit"])
    return {
        "business": m["business"], "unit": m["unit"], "price": price,
        "volume_factor": volume_factor, "unit_cost": round(variable, 4),
        "fixed_monthly": round(fixed, 2), "startup_total": round(startup, 2),
        "capacity_per_day": cap, "plan_per_day": m["plan"] * volume_factor,
        "estimate_share": round(share, 4), **base, "what_ifs": what_ifs,
        "most_sensitive_driver": worst["case"], "findings": findings,
        "fail_count": sum(1 for f in findings if f["severity"] == "fail"),
    }


def render_text(r: dict[str, Any]) -> str:
    """Render the report for a person."""
    u = r["unit"]
    bep = r["break_even_per_day"]
    lines = [
        f"Launch economics — {r['business']}",
        f"Price per {u}: {r['price']:.2f}   unit cost: {r['unit_cost']:.2f}   "
        f"contribution: {r['contribution_per_unit']:.2f} ({r['contribution_margin']:.0%})",
        f"Fixed per month: {r['fixed_monthly']:,.0f}   startup: {r['startup_total']:,.0f}",
        f"Break-even: {f'{bep:.1f} {u}/day' if bep is not None else 'never'}   "
        f"plan: {r['plan_per_day']:.0f}/day   capacity: {r['capacity_per_day'] or 'n/a'}",
        f"Operating margin at plan: {r['margin_at_plan']:.1%} "
        f"({r['monthly_profit_at_plan']:,.0f}/month)",
        f"Year one operating profit: {r['year1_operating_profit']:,.0f}   "
        f"after startup: {r['year1_after_startup']:,.0f}",
        f"Cash needed before self-funding: {r['cash_needed']:,.0f}   "
        f"payback month: {r['payback_month'] or 'beyond month 12'}",
        "", f"  {'MONTH':>5} {'UNITS':>8} {'REVENUE':>12} {'OP PROFIT':>11} {'CUM CASH':>11}",
    ]
    for row in r["months"]:
        lines.append(f"  {row['month']:>5} {row['units']:>8,} {row['revenue']:>12,.0f} "
                     f"{row['operating_profit']:>11,.0f} {row['cumulative_cash']:>11,.0f}")
    lines += ["", "What-ifs:"]
    for w in r["what_ifs"]:
        lines.append(f"  {w['case']:<17} margin {w['margin_at_plan']:>7.1%}  "
                     f"year one {w['year1_operating_profit']:>11,.0f}  cash {w['cash_needed']:>10,.0f}")
    lines += [f"Most sensitive driver: {r['most_sensitive_driver']}", "",
              f"Findings: {r['fail_count']} fail, {len(r['findings']) - r['fail_count']} warn"]
    lines += [f"  [{f['severity'].upper():4}] {f['message']}" for f in r["findings"]]
    return "\n".join(lines)


def main() -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Unit economics and year-one cash model for a pre-launch business.",
        formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    parser.add_argument("--input", required=True, help="Path to the numbers JSON")
    parser.add_argument("--price", type=float, help="Override the price for a what-if")
    parser.add_argument("--volume-factor", type=float, default=1.0,
                        help="Scale plan and ramp volume, e.g. 0.8 for 20%% fewer sales")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                        help="Output format (default: text)")
    args = parser.parse_args()
    try:
        if args.volume_factor <= 0 or (args.price is not None and args.price < 0):
            raise InputError("--volume-factor must be > 0 and --price >= 0")
        payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
        report = analyse(load(payload), args.price, args.volume_factor)
    except OSError as exc:
        print(f"error: cannot read input: {exc}", file=sys.stderr)
        return 2
    except json.JSONDecodeError as exc:
        print(f"error: input is not valid JSON: {exc}", file=sys.stderr)
        return 2
    except InputError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(report, indent=2) if args.format == "json" else render_text(report))
    return 1 if report["fail_count"] else 0


if __name__ == "__main__":
    sys.exit(main())
