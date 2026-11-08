#!/usr/bin/env python3
"""
lean_canvas_validator.py — Audit a Lean Canvas for completeness,
specificity, and early-adopter discipline.

Stdlib only. JSON or markdown output.

Usage:
    python3 lean_canvas_validator.py --input canvas.json
    python3 lean_canvas_validator.py --input canvas.json --format markdown

Input schema:
{
  "canvas_name": "Acme — v1",
  "as_of": "2026-05-27",
  "problem": {
      "top_problems": ["...", "...", "..."],
      "existing_alternatives": ["..."]
  },
  "customer_segments": {
      "target": "...",
      "early_adopters_named": ["P1 - workaround X", "P2 - workaround Y"]
  },
  "unique_value_proposition": {
      "statement": "...",
      "names_segment": true,
      "names_outcome": true,
      "names_differentiator": true
  },
  "solution": {
      "features": ["...", "...", "..."]
  },
  "channels": [
      {"name": "...", "test_plan": "...", "cac_estimate_usd": 0}
  ],
  "revenue_streams": {
      "pricing_model": "subscription",
      "price_point": "...",
      "ltv_estimate_usd": 0,
      "first_10k_mrr_plan": "..."
  },
  "cost_structure": {
      "monthly_burn_usd": 0,
      "cac_estimate_usd": 0,
      "fixed_pct": 0,
      "top_lines": ["..."]
  },
  "key_metrics": {
      "north_star": "...",
      "input_metrics": ["...", "..."]
  },
  "unfair_advantage": {
      "current": "...",
      "honest_classification": "real|aspirational|none-yet",
      "plan_to_build": "..."
  },
  "assumptions": [
      {"block": "...", "statement": "...", "risk": "high|medium|low",
       "evidence": "high|medium|low|none", "test_planned": true}
  ]
}
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


GENERIC_TERMS = {
    "everyone", "all businesses", "all companies", "tbd",
    "world-class", "cutting-edge", "best-in-class",
    "online marketing", "social media", "execution", "first mover",
    "first-mover", "we move faster", "passion", "great team", "hard work",
}

REQUIRED_BLOCKS = [
    "problem", "customer_segments", "unique_value_proposition", "solution",
    "channels", "revenue_streams", "cost_structure", "key_metrics",
    "unfair_advantage",
]


@dataclass
class Issue:
    severity: str
    block: str
    message: str


def has_generic(text: str) -> list[str]:
    if not text:
        return []
    t = text.lower()
    return [g for g in GENERIC_TERMS if g in t]


def check_problem(c: dict[str, Any]) -> list[Issue]:
    issues = []
    p = c.get("problem") or {}
    probs = p.get("top_problems") or []
    if not probs:
        issues.append(Issue("fail", "problem", "no problems listed"))
    elif len(probs) > 3:
        issues.append(Issue("warn", "problem",
            f"{len(probs)} problems listed — top 3 only; rest goes to backlog"))
    alt = p.get("existing_alternatives") or []
    if not alt:
        issues.append(Issue("fail", "problem",
            "no existing alternatives listed — customers always do something today"))
    return issues


def check_segments(c: dict[str, Any]) -> list[Issue]:
    issues = []
    s = c.get("customer_segments") or {}
    target = s.get("target", "")
    if not target:
        issues.append(Issue("fail", "customer_segments", "no target segment"))
    elif has_generic(target):
        issues.append(Issue("warn", "customer_segments",
            f"target uses generic term(s): {', '.join(has_generic(target))}"))
    ea = s.get("early_adopters_named") or []
    if len(ea) < 5:
        issues.append(Issue("warn", "customer_segments",
            f"only {len(ea)} early adopters named — target 5+ specific ones"))
    return issues


def check_uvp(c: dict[str, Any]) -> list[Issue]:
    issues = []
    u = c.get("unique_value_proposition") or {}
    stmt = u.get("statement", "")
    if not stmt:
        issues.append(Issue("fail", "unique_value_proposition", "no UVP statement"))
        return issues
    if has_generic(stmt):
        issues.append(Issue("warn", "unique_value_proposition",
            f"UVP uses generic terms: {', '.join(has_generic(stmt))}"))
    if len(stmt) > 200:
        issues.append(Issue("warn", "unique_value_proposition",
            "UVP > 200 chars — likely a paragraph; aim for 1 sentence"))
    if not u.get("names_segment"):
        issues.append(Issue("warn", "unique_value_proposition",
            "UVP doesn't name segment"))
    if not u.get("names_outcome"):
        issues.append(Issue("warn", "unique_value_proposition",
            "UVP doesn't name outcome (measurable change)"))
    if not u.get("names_differentiator"):
        issues.append(Issue("warn", "unique_value_proposition",
            "UVP doesn't name differentiator from existing alternatives"))
    return issues


def check_solution(c: dict[str, Any]) -> list[Issue]:
    issues = []
    s = c.get("solution") or {}
    feats = s.get("features") or []
    if not feats:
        issues.append(Issue("fail", "solution", "no solution features listed"))
    elif len(feats) > 3:
        issues.append(Issue("warn", "solution",
            f"{len(feats)} features — top 3 only; rest goes to backlog"))
    return issues


def check_channels(c: dict[str, Any]) -> list[Issue]:
    issues = []
    chans = c.get("channels") or []
    if not chans:
        issues.append(Issue("fail", "channels", "no channels defined"))
        return issues
    if len(chans) > 4:
        issues.append(Issue("info", "channels",
            f"{len(chans)} channels — testing all in parallel rarely works"))
    for ch in chans:
        name = ch.get("name", "")
        if has_generic(name):
            issues.append(Issue("warn", "channels",
                f"channel '{name}' is generic"))
        if not ch.get("test_plan"):
            issues.append(Issue("warn", "channels",
                f"channel '{name}' has no test plan"))
        if not ch.get("cac_estimate_usd"):
            issues.append(Issue("info", "channels",
                f"channel '{name}' has no CAC estimate"))
    return issues


def check_revenue(c: dict[str, Any]) -> list[Issue]:
    issues = []
    r = c.get("revenue_streams") or {}
    if not r.get("pricing_model"):
        issues.append(Issue("fail", "revenue_streams", "no pricing model"))
    if not r.get("price_point"):
        issues.append(Issue("warn", "revenue_streams", "no price point set"))
    if not r.get("ltv_estimate_usd"):
        issues.append(Issue("warn", "revenue_streams", "no LTV estimate"))
    if not r.get("first_10k_mrr_plan"):
        issues.append(Issue("info", "revenue_streams",
            "no concrete plan to first $10K MRR"))
    return issues


def check_costs(c: dict[str, Any]) -> list[Issue]:
    issues = []
    cs = c.get("cost_structure") or {}
    if not cs.get("monthly_burn_usd"):
        issues.append(Issue("warn", "cost_structure", "no monthly burn estimate"))
    if not cs.get("cac_estimate_usd"):
        issues.append(Issue("warn", "cost_structure",
            "no CAC estimate — usually the biggest cost line"))
    top = cs.get("top_lines") or []
    if len(top) < 3:
        issues.append(Issue("info", "cost_structure",
            "fewer than 3 cost lines listed"))
    return issues


def check_metrics(c: dict[str, Any]) -> list[Issue]:
    issues = []
    m = c.get("key_metrics") or {}
    if not m.get("north_star"):
        issues.append(Issue("fail", "key_metrics", "no North Star metric"))
    inputs = m.get("input_metrics") or []
    if len(inputs) > 5:
        issues.append(Issue("warn", "key_metrics",
            f"{len(inputs)} input metrics — typically 2-4 driving the NS"))
    return issues


def check_unfair_advantage(c: dict[str, Any]) -> list[Issue]:
    issues = []
    u = c.get("unfair_advantage") or {}
    current = u.get("current", "")
    classification = (u.get("honest_classification") or "").lower()
    if not current and not classification:
        issues.append(Issue("warn", "unfair_advantage",
            "block empty — most startups have none yet; explicitly mark + plan"))
        return issues
    if has_generic(current):
        issues.append(Issue("warn", "unfair_advantage",
            f"contains generic non-moat: {', '.join(has_generic(current))}"))
    if classification == "aspirational":
        issues.append(Issue("info", "unfair_advantage",
            "marked aspirational — distinguish from real advantage"))
    if classification == "none-yet" and not u.get("plan_to_build"):
        issues.append(Issue("warn", "unfair_advantage",
            "no advantage + no plan to build one"))
    return issues


def check_assumptions(c: dict[str, Any]) -> list[Issue]:
    issues = []
    asums = c.get("assumptions") or []
    if not asums:
        issues.append(Issue("warn", "assumptions",
            "no assumption register — Lean Canvas is hypotheses; surface the riskiest"))
        return issues
    high_risk_no_test = [
        a for a in asums
        if (a.get("risk") or "").lower() == "high"
        and not a.get("test_planned")
    ]
    if high_risk_no_test:
        issues.append(Issue("warn", "assumptions",
            f"{len(high_risk_no_test)} high-risk assumption(s) without planned test"))
    return issues


CHECKERS = [
    check_problem, check_segments, check_uvp, check_solution, check_channels,
    check_revenue, check_costs, check_metrics, check_unfair_advantage,
    check_assumptions,
]


def validate(canvas: dict[str, Any]) -> dict[str, Any]:
    all_issues: list[Issue] = []
    for chk in CHECKERS:
        all_issues.extend(chk(canvas))
    sev = {"fail": 0, "warn": 0, "info": 0}
    for i in all_issues:
        sev[i.severity] += 1
    completeness = {b: ("populated" if canvas.get(b) else "empty") for b in REQUIRED_BLOCKS}
    populated = sum(1 for v in completeness.values() if v == "populated")
    completeness_pct = round((populated / len(REQUIRED_BLOCKS)) * 100)
    penalty = sev["fail"] * 10 + sev["warn"] * 3 + sev["info"] * 1
    quality_pct = max(0, completeness_pct - penalty)
    return {
        "canvas_name": canvas.get("canvas_name", ""),
        "as_of": canvas.get("as_of", ""),
        "completeness_pct": completeness_pct,
        "quality_pct": quality_pct,
        "block_completeness": completeness,
        "severity_counts": sev,
        "issues": [
            {"severity": i.severity, "block": i.block, "message": i.message}
            for i in all_issues
        ],
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = []
    lines.append(f"# Lean Canvas Validation — {report.get('canvas_name','(unnamed)')}\n")
    lines.append(f"_as of {report['as_of']}_\n")
    lines.append(f"**Completeness:** {report['completeness_pct']}%")
    lines.append(f"**Quality:** {report['quality_pct']}/100\n")
    sc = report["severity_counts"]
    lines.append(f"**Severity:** fail {sc['fail']} | warn {sc['warn']} | info {sc['info']}\n")
    lines.append("## Block status")
    lines.append("| Block | Status |")
    lines.append("|-------|--------|")
    for b, s in report["block_completeness"].items():
        lines.append(f"| {b} | {s} |")
    lines.append("")
    sev_order = {"fail": 0, "warn": 1, "info": 2}
    sorted_issues = sorted(report["issues"], key=lambda i: sev_order.get(i["severity"], 9))
    lines.append("## Issues")
    if not sorted_issues:
        lines.append("_No issues detected._")
    else:
        lines.append("| Severity | Block | Message |")
        lines.append("|----------|-------|---------|")
        for i in sorted_issues:
            lines.append(f"| {i['severity']} | {i['block']} | {i['message']} |")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Validate a Lean Canvas",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument("--input", required=True, help="JSON canvas")
    p.add_argument("--format", choices=["json", "markdown"], default="json")
    p.add_argument("--output", help="Write to file instead of stdout")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    try:
        canvas = json.loads(Path(args.input).read_text(encoding="utf-8"))
    except OSError as e:
        print(f"error: cannot read input: {e}", file=sys.stderr)
        return 2
    except json.JSONDecodeError as e:
        print(f"error: invalid JSON: {e}", file=sys.stderr)
        return 2

    if not isinstance(canvas, dict):
        print("error: top level must be a JSON object (see the schema in --help)", file=sys.stderr)
        return 2
    try:
        report = validate(canvas)
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
