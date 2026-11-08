#!/usr/bin/env python3
"""
ansoff_growth_scorer.py — Classify growth initiatives into Ansoff
quadrants, surface investment mix, flag misclassification + concentration.

Stdlib only. JSON or markdown output.

Usage:
    python3 ansoff_growth_scorer.py --input initiatives.json
    python3 ansoff_growth_scorer.py --input initiatives.json --format markdown

Input schema:
{
  "company_stage": "growth",   # early|growth|mature|declining
  "target_mix": {"market_penetration": 50, ...},  # optional; overrides the stage default
  "as_of": "2026-05-27",
  "initiatives": [
      {
          "name": "EU expansion",
          "quadrant": "market_development",  # market_penetration|market_development|product_development|diversification
          "investment_usd": 5000000,
          "expected_return_usd": 18000000,
          "risk_score": 4,           # 1-5
          "time_to_revenue_months": 12,
          "owner": "VP International",
          "rationale": "Proven SMB product to EU SMB market; localization + entity"
      }
  ]
}
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any


VALID_QUADRANTS = {
    "market_penetration", "market_development",
    "product_development", "diversification",
}

QUADRANT_LABELS = {
    "market_penetration": "Q1: Market Penetration",
    "market_development": "Q2: Market Development",
    "product_development": "Q3: Product Development",
    "diversification": "Q4: Diversification",
}

QUADRANT_RISK = {
    "market_penetration": "lowest",
    "market_development": "medium",
    "product_development": "medium",
    "diversification": "highest",
}

# Default target mix by stage: a heuristic starting point, not a published standard.
# Each row sums to 100. Override per company with "target_mix" in the input.
TARGET_MIX = {
    "early": {"market_penetration": 75, "market_development": 10,
              "product_development": 15, "diversification": 0},
    "growth": {"market_penetration": 50, "market_development": 25,
               "product_development": 20, "diversification": 5},
    "mature": {"market_penetration": 35, "market_development": 27,
               "product_development": 28, "diversification": 10},
    "declining": {"market_penetration": 25, "market_development": 25,
                  "product_development": 35, "diversification": 15},
}


@dataclass
class Issue:
    severity: str
    initiative: str
    message: str


def check_initiative(init: dict[str, Any]) -> list[Issue]:
    issues = []
    name = init.get("name", "(unnamed)")
    q = (init.get("quadrant") or "").lower()
    if q not in VALID_QUADRANTS:
        issues.append(Issue("fail", name, f"invalid quadrant: '{q}'"))
        return issues

    inv = float(init.get("investment_usd", 0) or 0)
    exp = float(init.get("expected_return_usd", 0) or 0)
    risk = int(init.get("risk_score", 0) or 0)

    if inv <= 0:
        issues.append(Issue("warn", name, "investment_usd not set"))
    if exp <= 0:
        issues.append(Issue("warn", name, "expected_return_usd not set"))

    # Risk should align with quadrant
    if q == "market_penetration" and risk >= 4:
        issues.append(Issue("info", name,
            "Q1 with high risk-score — may be misclassified (likely Q2 or Q3)"))
    if q == "diversification" and risk <= 2:
        issues.append(Issue("warn", name,
            "Q4 with low risk-score — usually misclassified or under-assessed"))
    if q == "product_development" and risk >= 5:
        issues.append(Issue("info", name,
            "Q3 with maximum risk — likely actually Q4 (verify shared capability + audience)"))

    if exp > 0 and inv > 0:
        rar = (exp - inv) / inv
        if rar < 0:
            issues.append(Issue("warn", name,
                f"expected return < investment (RAR {rar:.1%}) — verify"))

    if not init.get("rationale"):
        issues.append(Issue("warn", name, "no rationale provided"))

    if not init.get("owner"):
        issues.append(Issue("info", name, "no owner assigned"))

    return issues


def analyze(state: dict[str, Any]) -> dict[str, Any]:
    initiatives = state.get("initiatives") or []
    stage = (state.get("company_stage") or "growth").lower()
    all_issues: list[Issue] = []
    if stage not in TARGET_MIX:
        all_issues.append(Issue("warn", "(stage)", f"unknown company_stage '{stage}'; using growth"))
        stage = "growth"
    if not initiatives:
        all_issues.append(Issue("fail", "(initiatives)", "no initiatives listed"))
    by_quadrant: dict[str, list[dict[str, Any]]] = defaultdict(list)
    total_investment = 0.0
    investment_by_quadrant: dict[str, float] = defaultdict(float)
    return_by_quadrant: dict[str, float] = defaultdict(float)

    for init in initiatives:
        all_issues.extend(check_initiative(init))
        q = (init.get("quadrant") or "").lower()
        if q not in VALID_QUADRANTS:
            continue
        by_quadrant[q].append(init)
        inv = float(init.get("investment_usd", 0) or 0)
        exp = float(init.get("expected_return_usd", 0) or 0)
        total_investment += inv
        investment_by_quadrant[q] += inv
        return_by_quadrant[q] += exp

    actual_mix = {
        q: round((investment_by_quadrant[q] / total_investment) * 100, 1) if total_investment > 0 else 0
        for q in VALID_QUADRANTS
    }
    target = {q: float((state.get("target_mix") or TARGET_MIX[stage]).get(q, 0)) for q in VALID_QUADRANTS}
    if abs(sum(target.values()) - 100) > 0.5:
        all_issues.append(Issue("fail", "(target_mix)", f"target_mix sums to {sum(target.values()):g}, not 100"))
    delta = {q: round(actual_mix[q] - target[q], 1) for q in VALID_QUADRANTS}

    # Concentration warnings
    for q in VALID_QUADRANTS:
        if abs(delta[q]) > 20:
            all_issues.append(Issue("warn", "(mix)",
                f"{QUADRANT_LABELS[q]} at {actual_mix[q]}% vs target {target[q]}% — drift > 20pts"))

    if actual_mix.get("diversification", 0) > 25:
        all_issues.append(Issue("warn", "(mix)",
            f"Diversification >25% — bet-the-company risk; verify intentional"))

    if actual_mix.get("market_penetration", 0) > 85 and stage != "early":
        all_issues.append(Issue("info", "(mix)",
            "Market Penetration >85% — may be under-investing in future growth"))

    sev = {"fail": 0, "warn": 0, "info": 0}
    for i in all_issues:
        sev[i.severity] += 1

    return {
        "company_stage": stage,
        "as_of": state.get("as_of", ""),
        "initiative_count": len(initiatives),
        "total_investment_usd": total_investment,
        "actual_mix_pct": actual_mix,
        "target_mix_pct": target,
        "delta_vs_target_pp": delta,
        "investment_by_quadrant_usd": dict(investment_by_quadrant),
        "expected_return_by_quadrant_usd": dict(return_by_quadrant),
        "initiatives_by_quadrant_count": {q: len(v) for q, v in by_quadrant.items()},
        "severity_counts": sev,
        "issues": [
            {"severity": i.severity, "initiative": i.initiative, "message": i.message}
            for i in all_issues
        ],
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = []
    lines.append(f"# Ansoff Growth Mix — stage: {report['company_stage']}\n")
    lines.append(f"_as of {report['as_of']}_\n")
    lines.append(f"Initiatives: {report['initiative_count']} | "
                f"Total investment: ${report['total_investment_usd']:,.0f}\n")
    lines.append("## Mix vs target")
    lines.append("| Quadrant | Actual % | Target % | Delta (pp) |")
    lines.append("|----------|----------|----------|-----------|")
    for q in ["market_penetration", "market_development", "product_development", "diversification"]:
        a = report["actual_mix_pct"].get(q, 0)
        t = report["target_mix_pct"].get(q, 0)
        d = report["delta_vs_target_pp"].get(q, 0)
        lines.append(f"| {QUADRANT_LABELS[q]} | {a}% | {t}% | {d:+.1f} |")
    lines.append("")
    lines.append("## Initiative count by quadrant")
    for q, c in report["initiatives_by_quadrant_count"].items():
        lines.append(f"- {QUADRANT_LABELS.get(q, q)}: {c}")
    lines.append("")
    sc = report["severity_counts"]
    lines.append(f"## Severity: fail {sc['fail']} | warn {sc['warn']} | info {sc['info']}\n")
    sev_order = {"fail": 0, "warn": 1, "info": 2}
    sorted_issues = sorted(report["issues"], key=lambda i: sev_order.get(i["severity"], 9))
    lines.append("## Issues")
    if not sorted_issues:
        lines.append("_No issues detected._")
    else:
        lines.append("| Severity | Initiative | Message |")
        lines.append("|----------|------------|---------|")
        for i in sorted_issues:
            lines.append(f"| {i['severity']} | {i['initiative']} | {i['message']} |")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Classify Ansoff quadrants + surface investment mix",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument("--input", required=True, help="JSON of initiatives")
    p.add_argument("--format", choices=["json", "markdown"], default="json")
    p.add_argument("--output", help="Write to file instead of stdout")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    try:
        state = json.loads(Path(args.input).read_text(encoding="utf-8"))
    except OSError as e:
        print(f"error: cannot read input: {e}", file=sys.stderr)
        return 2
    except json.JSONDecodeError as e:
        print(f"error: invalid JSON: {e}", file=sys.stderr)
        return 2

    if not isinstance(state, dict):
        print("error: top level must be a JSON object (see the schema in --help)", file=sys.stderr)
        return 2
    try:
        report = analyze(state)
    except (AttributeError, TypeError, KeyError, ValueError) as e:
        print(f"error: unexpected input shape ({type(e).__name__}: {e})", file=sys.stderr)
        return 2
    out = render_markdown(report) if args.format == "markdown" else json.dumps(report, indent=2)

    if args.output:
        Path(args.output).write_text(out, encoding="utf-8")
        print(f"wrote {args.output}", file=sys.stderr)
    else:
        print(out)
    # Gate: 1 when any finding has severity "fail", else 0.
    return 1 if report.get("severity_counts", {}).get("fail") else 0


if __name__ == "__main__":
    sys.exit(main())
