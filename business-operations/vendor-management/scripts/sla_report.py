#!/usr/bin/env python3
"""Report SLA compliance for a vendor period and compute service credits owed.

Evaluates each committed metric against its target in the correct direction,
selects the applicable credit tier, totals credits against period contract
value, and reads the trend from prior periods so a one-off is not confused with
a decline.

Usage:
    python3 sla_report.py --input sample_sla.json
    python3 sla_report.py --input sample_sla.json --format json
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

VALID_DIRECTIONS = {"higher_is_better", "lower_is_better"}

# Credits are capped as a share of period fees in most contracts.
DEFAULT_CREDIT_CAP_PCT = 100.0

# Breach magnitude relative to target, for severity banding.
SEVERITY_MINOR = 0.02
SEVERITY_MAJOR = 0.10


def is_breach(actual: float, target: float, direction: str) -> bool:
    """Return True if the actual value misses the target in the stated direction."""
    if direction == "higher_is_better":
        return actual < target
    return actual > target


def breach_magnitude(actual: float, target: float, direction: str, unit: str) -> float:
    """Return the relative size of a breach against target, or 0.0 if compliant.

    High-target percentage metrics (availability, success rate) are measured on
    the complement: missing 99.9% uptime by 0.48 points is not a 0.5% miss, it is
    nearly six times the permitted downtime.
    """
    if not is_breach(actual, target, direction) or target == 0:
        return 0.0
    if direction == "higher_is_better" and unit.strip() == "%" and target >= 90:
        allowed_miss = 100.0 - target
        actual_miss = 100.0 - actual
        if allowed_miss <= 0:
            return float(actual_miss)
        return actual_miss / allowed_miss - 1.0
    return abs(actual - target) / abs(target)


def applicable_credit(sla: Dict[str, Any], actual: float, direction: str) -> float:
    """Return the highest credit percentage triggered by this result."""
    credit = 0.0
    for tier in sla.get("credit_tiers", []):
        threshold = float(tier.get("threshold", 0))
        pct = float(tier.get("credit_pct", 0))
        if is_breach(actual, threshold, direction):
            credit = max(credit, pct)
    return credit


def trend(history: List[Dict[str, Any]], actual: float, direction: str) -> Optional[str]:
    """Describe the direction of travel across prior periods, if history exists."""
    values = [float(h.get("actual")) for h in history if h.get("actual") is not None]
    if len(values) < 2:
        return None
    series = values + [actual]
    first_half = sum(series[: len(series) // 2]) / (len(series) // 2)
    second_half = sum(series[len(series) // 2 :]) / (len(series) - len(series) // 2)
    delta = second_half - first_half
    if abs(delta) < abs(first_half) * 0.005:
        return "flat"
    improving = delta > 0 if direction == "higher_is_better" else delta < 0
    return "improving" if improving else "DEGRADING"


def analyse(data: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate every SLA for the period and total the credits owed."""
    slas = data.get("slas", [])
    if not slas:
        raise ValueError("input JSON needs a non-empty 'slas' array")
    acv = float(data.get("annual_contract_value", 0))
    periods_per_year = int(data.get("periods_per_year", 4))
    if periods_per_year <= 0:
        raise ValueError("'periods_per_year' must be greater than zero")
    period_fees = acv / periods_per_year
    cap_pct = float(data.get("credit_cap_pct", DEFAULT_CREDIT_CAP_PCT))

    results: List[Dict[str, Any]] = []
    for sla in slas:
        name = sla.get("metric", "unnamed metric")
        direction = str(sla.get("direction", "higher_is_better")).lower()
        if direction not in VALID_DIRECTIONS:
            raise ValueError(
                f"SLA '{name}' has direction '{direction}'; expected one of {sorted(VALID_DIRECTIONS)}"
            )
        if "target" not in sla or "actual" not in sla:
            raise ValueError(f"SLA '{name}' needs both 'target' and 'actual'")
        target = float(sla["target"])
        actual = float(sla["actual"])

        unit = str(sla.get("unit", ""))
        breached = is_breach(actual, target, direction)
        magnitude = breach_magnitude(actual, target, direction, unit)
        if not breached:
            severity = "compliant"
        elif magnitude < SEVERITY_MINOR:
            severity = "MINOR"
        elif magnitude < SEVERITY_MAJOR:
            severity = "MAJOR"
        else:
            severity = "SEVERE"

        credit_pct = applicable_credit(sla, actual, direction) if breached else 0.0
        uses_error_budget = (
            direction == "higher_is_better" and unit.strip() == "%" and target >= 90
        )
        results.append(
            {
                "error_budget_multiple": round(magnitude + 1.0, 2) if uses_error_budget and breached else None,
                "metric": name,
                "unit": unit,
                "has_credit_tiers": bool(sla.get("credit_tiers")),
                "direction": direction,
                "target": target,
                "actual": actual,
                "breached": breached,
                "breach_magnitude": round(magnitude, 4),
                "severity": severity,
                "credit_pct": credit_pct,
                "credit_amount": round(period_fees * credit_pct / 100.0, 2),
                "trend": trend(sla.get("history", []), actual, direction),
                "business_impact": sla.get("business_impact", ""),
            }
        )

    raw_credit_pct = sum(r["credit_pct"] for r in results)
    capped_pct = min(raw_credit_pct, cap_pct)
    credit_amount = round(period_fees * capped_pct / 100.0, 2)

    breaches = [r for r in results if r["breached"]]
    severe = [r for r in results if r["severity"] == "SEVERE"]
    degrading = [r for r in results if r["trend"] == "DEGRADING"]

    findings: List[str] = []
    for r in severe:
        if r["error_budget_multiple"] is not None:
            size = f"{r['error_budget_multiple']:.1f}x the permitted error budget"
        else:
            size = f"{r['breach_magnitude']:.1%} past target"
        findings.append(
            f"SEVERE breach on {r['metric']}: {r['actual']}{r['unit']} against a "
            f"{r['target']}{r['unit']} target — {size}. "
            "Escalate to the contract owner, not the account manager."
        )
    for r in degrading:
        findings.append(
            f"{r['metric']} is DEGRADING across periods — this is a trend, not an incident. "
            "Raise it at the next business review with the full series."
        )
    if raw_credit_pct > cap_pct:
        findings.append(
            f"Credits earned ({raw_credit_pct:.0f}% of period fees) exceed the contractual cap "
            f"({cap_pct:.0f}%). The cap is now doing the work the SLA should — a signal the "
            "remedy structure is too weak to change behaviour."
        )
    toothless = [r for r in breaches if not r["has_credit_tiers"]]
    if toothless:
        findings.append(
            "Breached with no credit tier defined: "
            + ", ".join(r["metric"] for r in toothless)
            + ". An SLA with no remedy is a statement of intent; add credit tiers at renewal."
        )
    if not breaches:
        findings.append(
            "All committed metrics met. Confirm the targets still reflect what the business "
            "needs — a permanently green SLA is usually measuring the wrong thing."
        )

    return {
        "vendor": data.get("vendor", "unnamed vendor"),
        "period": data.get("period", "unspecified"),
        "annual_contract_value": acv,
        "period_fees": round(period_fees, 2),
        "slas": results,
        "summary": {
            "metrics_tracked": len(results),
            "breaches": len(breaches),
            "severe_breaches": len(severe),
            "compliance_rate": round((len(results) - len(breaches)) / len(results), 3),
            "credit_pct_earned": round(raw_credit_pct, 2),
            "credit_pct_applied": round(capped_pct, 2),
            "credit_amount": credit_amount,
            "credit_cap_pct": cap_pct,
        },
        "findings": findings,
    }


def output(result: Dict[str, Any], fmt: str) -> None:
    """Print the SLA report as JSON or a human-readable report."""
    if fmt == "json":
        print(json.dumps(result, indent=2))
        return

    s = result["summary"]
    print(f"SLA REPORT — {result['vendor']} — {result['period']}")
    print("=" * 80)
    print(
        f"Period fees {result['period_fees']:,.0f} | {s['metrics_tracked']} metrics | "
        f"compliance {s['compliance_rate']:.0%}"
    )
    print()
    print(f"{'Metric':<26}{'Target':>10}{'Actual':>10}{'Severity':>11}{'Credit':>9}  Trend")
    print("-" * 80)
    for r in result["slas"]:
        trend_str = r["trend"] or "-"
        print(
            f"{r['metric'][:25]:<26}{r['target']:>10}{r['actual']:>10}"
            f"{r['severity']:>11}{r['credit_pct']:>8.0f}%  {trend_str}"
        )
    print("-" * 80)
    print()
    print("CREDITS")
    print(f"  Earned          {s['credit_pct_earned']:>8.1f}% of period fees")
    print(f"  Cap             {s['credit_cap_pct']:>8.1f}%")
    print(f"  Applied         {s['credit_pct_applied']:>8.1f}%  =  {s['credit_amount']:,.2f}")
    if result["findings"]:
        print()
        print("FINDINGS")
        for f in result["findings"]:
            print(f"  ! {f}")


def main() -> None:
    """Parse arguments, evaluate the SLAs, and print the result."""
    parser = argparse.ArgumentParser(
        description="Report SLA compliance and compute service credits owed for a period.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to an SLA JSON file (see assets/sample_sla.json)",
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
        print(f"Error: could not build SLA report — {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
