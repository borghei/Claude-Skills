#!/usr/bin/env python3
"""
ost_validator.py — Audit an Opportunity Solution Tree for outcome
quality, opportunity-vs-solution discipline, solution diversity, and
assumption-test coverage.

Stdlib only. JSON or markdown output.

Usage:
    python3 ost_validator.py --input ost.json
    python3 ost_validator.py --input ost.json --format markdown

Exit codes: 0 no fail findings, 1 at least one fail finding, 2 bad input.

Input schema:
{
  "tree_name": "Activation Q3",
  "as_of": "2026-05-27",
  "last_updated": "2026-05-20",
  "outcome": {
      "statement": "Lift W1 activation from 28% to 40% by end of Q3",
      "is_measurable": true,
      "is_behavioral_or_business": true,
      "is_bounded": true,
      "team_can_influence": true
  },
  "opportunities": [
      {
          "id": "O1",
          "statement": "...",
          "is_customer_phrased": true,
          "has_evidence": true,
          "evidence_sources": ["interview-007","funnel data"],
          "solutions": [
              {
                  "id": "O1-S1",
                  "statement": "...",
                  "is_solution_not_opportunity": true,
                  "assumption_tests": [
                      {"description": "...", "time_bounded": true,
                       "success_criterion_defined": true}
                  ]
              }
          ]
      }
  ]
}
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any


@dataclass
class Issue:
    severity: str
    location: str
    message: str


def parse_date(s: str | None) -> date | None:
    if not s:
        return None
    try:
        return datetime.strptime(s, "%Y-%m-%d").date()
    except ValueError:
        return None


def check_outcome(o: dict[str, Any]) -> list[Issue]:
    issues = []
    if not o:
        return [Issue("fail", "outcome", "no outcome defined")]
    stmt = o.get("statement", "")
    if not stmt:
        issues.append(Issue("fail", "outcome", "no outcome statement"))
        return issues
    if not o.get("is_measurable"):
        issues.append(Issue("fail", "outcome", "outcome not marked measurable"))
    if not o.get("is_behavioral_or_business"):
        issues.append(Issue("fail", "outcome",
            "outcome not behavioral or business — likely an output"))
    if not o.get("is_bounded"):
        issues.append(Issue("warn", "outcome", "outcome not time-bounded"))
    if not o.get("team_can_influence"):
        issues.append(Issue("warn", "outcome",
            "outcome may not be within team's direct influence"))
    # Check for output-language in statement
    output_words = ["ship", "build", "launch", "release", "deliver"]
    if any(w in stmt.lower() for w in output_words):
        issues.append(Issue("warn", "outcome",
            f"statement contains output-language: rephrase as behavior/metric change"))
    return issues


BUILD_VERBS = {"add", "build", "create", "implement", "launch", "integrate", "redesign",
               "replace", "ship", "introduce", "enable", "develop", "migrate", "automate"}


def check_opportunities(opps: list[dict[str, Any]]) -> list[Issue]:
    issues = []
    if not opps:
        return [Issue("fail", "opportunities", "no opportunities defined")]
    if len(opps) > 8:
        issues.append(Issue("warn", "opportunities",
            f"{len(opps)} opportunities — usually 3-7; cluster + prioritize"))
    elif len(opps) < 2:
        issues.append(Issue("info", "opportunities",
            f"only {len(opps)} opportunity — usually 3+ for healthy divergence"))

    for opp in opps:
        oid = opp.get("id", "")
        if not opp.get("is_customer_phrased"):
            issues.append(Issue("warn", f"opp:{oid}",
                "not marked as customer-phrased — may be a solution disguised as opportunity"))
        # Cross-check the self-reported flag against the text: a build verb up front is a solution.
        first = str(opp.get("statement", "")).strip().lower().split(" ")[0]
        if first in BUILD_VERBS:
            issues.append(Issue("warn", f"opp:{oid}",
                f"statement starts with '{first}' — reads as a solution; rephrase as the customer need"))
        if not opp.get("has_evidence"):
            issues.append(Issue("warn", f"opp:{oid}",
                "no evidence flag set — opportunities need customer evidence"))
        sources = opp.get("evidence_sources") or []
        if not sources:
            issues.append(Issue("warn", f"opp:{oid}",
                "no evidence sources listed"))
    return issues


def check_solutions(opps: list[dict[str, Any]]) -> list[Issue]:
    issues = []
    for opp in opps:
        oid = opp.get("id", "")
        sols = opp.get("solutions") or []
        if not sols:
            issues.append(Issue("warn", f"opp:{oid}",
                "no solutions defined"))
            continue
        if len(sols) == 1:
            issues.append(Issue("warn", f"opp:{oid}",
                "only 1 solution — force 3+ alternatives for divergence"))
        elif len(sols) > 6:
            issues.append(Issue("info", f"opp:{oid}",
                f"{len(sols)} solutions — usually 3-5; pick the top after divergent brainstorm"))
        for sol in sols:
            sid = sol.get("id", "")
            if not sol.get("is_solution_not_opportunity"):
                issues.append(Issue("info", f"opp:{oid}/sol:{sid}",
                    "not confirmed solution-not-opportunity — verify it's a thing to build"))
    return issues


def check_assumption_tests(opps: list[dict[str, Any]]) -> list[Issue]:
    issues = []
    for opp in opps:
        oid = opp.get("id", "")
        sols = opp.get("solutions") or []
        for sol in sols:
            sid = sol.get("id", "")
            tests = sol.get("assumption_tests") or []
            if not tests:
                issues.append(Issue("warn", f"opp:{oid}/sol:{sid}",
                    "no assumption tests defined — solution can't be validated"))
                continue
            for t in tests:
                desc = t.get("description", "")
                if not t.get("time_bounded"):
                    issues.append(Issue("warn", f"opp:{oid}/sol:{sid}",
                        f"test '{desc[:40]}...' not time-bounded"))
                if not t.get("success_criterion_defined"):
                    issues.append(Issue("warn", f"opp:{oid}/sol:{sid}",
                        f"test '{desc[:40]}...' has no success criterion"))
    return issues


def check_freshness(tree: dict[str, Any]) -> list[Issue]:
    issues = []
    today = parse_date(tree.get("as_of")) or date.today()
    last = parse_date(tree.get("last_updated"))
    if not last:
        issues.append(Issue("info", "freshness", "no last_updated date"))
        return issues
    days = (today - last).days
    if days > 30:  # checked first: the 30-day fail was unreachable behind the 14-day warn
        issues.append(Issue("fail", "freshness",
            f"OST not updated in {days} days — stale tree; refresh required"))
    elif days > 14:
        issues.append(Issue("warn", "freshness",
            f"OST not updated in {days} days — weekly rhythm recommended"))
    return issues


def validate(tree: dict[str, Any]) -> dict[str, Any]:
    all_issues: list[Issue] = []
    all_issues.extend(check_outcome(tree.get("outcome", {})))
    opps = tree.get("opportunities") or []
    all_issues.extend(check_opportunities(opps))
    all_issues.extend(check_solutions(opps))
    all_issues.extend(check_assumption_tests(opps))
    all_issues.extend(check_freshness(tree))

    sev = {"fail": 0, "warn": 0, "info": 0}
    for i in all_issues:
        sev[i.severity] += 1

    total_sols = sum(len(o.get("solutions") or []) for o in opps)
    total_tests = sum(
        len(sol.get("assumption_tests") or [])
        for o in opps for sol in (o.get("solutions") or [])
    )

    return {
        "tree_name": tree.get("tree_name", ""),
        "as_of": tree.get("as_of", ""),
        "last_updated": tree.get("last_updated", ""),
        "counts": {
            "opportunities": len(opps),
            "solutions": total_sols,
            "tests": total_tests,
        },
        "severity_counts": sev,
        "issues": [
            {"severity": i.severity, "location": i.location, "message": i.message}
            for i in all_issues
        ],
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = []
    lines.append(f"# OST Audit — {report.get('tree_name','(unnamed)')}\n")
    lines.append(f"_as of {report['as_of']} | last updated {report['last_updated']}_\n")
    c = report["counts"]
    lines.append(f"**Counts:** opportunities={c['opportunities']} | "
                f"solutions={c['solutions']} | tests={c['tests']}\n")
    sc = report["severity_counts"]
    lines.append(f"**Severity:** fail {sc['fail']} | warn {sc['warn']} | info {sc['info']}\n")
    sev_order = {"fail": 0, "warn": 1, "info": 2}
    sorted_issues = sorted(report["issues"], key=lambda i: sev_order.get(i["severity"], 9))
    lines.append("## Issues")
    if not sorted_issues:
        lines.append("_No issues detected._")
    else:
        lines.append("| Severity | Location | Message |")
        lines.append("|----------|----------|---------|")
        for i in sorted_issues:
            lines.append(f"| {i['severity']} | {i['location']} | {i['message']} |")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Validate an Opportunity Solution Tree",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument("--input", required=True, help="JSON OST")
    p.add_argument("--format", choices=["json", "markdown"], default="json")
    p.add_argument("--output", help="Write to file instead of stdout")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    try:
        tree = json.loads(Path(args.input).read_text(encoding="utf-8"))
    except OSError as e:
        print(f"error: cannot read input: {e}", file=sys.stderr)
        return 2
    except json.JSONDecodeError as e:
        print(f"error: invalid JSON: {e}", file=sys.stderr)
        return 2

    report = validate(tree)
    out = render_markdown(report) if args.format == "markdown" else json.dumps(report, indent=2)

    if args.output:
        Path(args.output).write_text(out, encoding="utf-8")
        print(f"wrote {args.output}", file=sys.stderr)
    else:
        print(out)
    return 1 if report["severity_counts"]["fail"] else 0  # 1 = at least one fail finding


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, KeyError, TypeError, AttributeError, IndexError) as exc:
        print(f"error: bad input ({type(exc).__name__}): {exc}", file=sys.stderr)
        sys.exit(2)
