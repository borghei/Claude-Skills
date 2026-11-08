#!/usr/bin/env python3
"""
stakeholder_analyzer.py — Audit a stakeholder map for completeness,
blocker plans, HP/LI engagement, and quadrant balance.

Stdlib only. JSON or markdown output.

Usage:
    python3 stakeholder_analyzer.py --input stakeholders.json
    python3 stakeholder_analyzer.py --input stakeholders.json --format markdown

Input schema:
{
  "initiative": "Enterprise deal with Customer-X",
  "as_of": "2026-05-27",
  "stakeholders": [
      {
          "name": "Mary",
          "title": "VP IT",
          "role": "Economic buyer",       # buyer|user|approver|champion|veto|...
          "power": 5,                      # 1-5
          "interest": 5,                   # 1-5
          "support": "champion",           # champion|supporter|neutral|skeptic|blocker
          "engagement_cadence": "weekly",
          "engagement_owner": "AE",
          "blocker_conversion_plan_present": true   # for blockers/skeptics
      }
  ]
}
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any


SUPPORT_VALUES = {"champion", "supporter", "neutral", "skeptic", "blocker"}


@dataclass
class Issue:
    severity: str
    stakeholder: str
    message: str


def quadrant_of(power: int, interest: int) -> str:
    """Return MC (Manage Closely), KS (Keep Satisfied), KI (Keep Informed), M (Monitor)."""
    p_high = power >= 4
    i_high = interest >= 4
    if p_high and i_high:
        return "manage_closely"
    if p_high and not i_high:
        return "keep_satisfied"
    if not p_high and i_high:
        return "keep_informed"
    return "monitor"


def check_stakeholder(s: dict[str, Any]) -> list[Issue]:
    issues = []
    name = s.get("name", "(unnamed)")
    power = int(s.get("power", 0) or 0)
    interest = int(s.get("interest", 0) or 0)
    support = (s.get("support") or "").lower()

    if not name or name == "(unnamed)":
        issues.append(Issue("fail", name, "stakeholder has no name"))
    if power < 1 or power > 5:
        issues.append(Issue("warn", name, f"power={power} not in 1-5"))
    if interest < 1 or interest > 5:
        issues.append(Issue("warn", name, f"interest={interest} not in 1-5"))
    if support not in SUPPORT_VALUES:
        issues.append(Issue("warn", name, f"support='{support}' invalid"))

    quad = quadrant_of(power, interest)

    # Engagement check by quadrant
    cadence = (s.get("engagement_cadence") or "").lower()
    owner = s.get("engagement_owner", "")

    if quad == "manage_closely":
        if cadence not in ("daily", "weekly", "bi-weekly", "biweekly"):
            issues.append(Issue("warn", name,
                f"Manage-Closely stakeholder needs weekly-or-tighter cadence (current: {cadence or 'none'})"))
        if not owner:
            issues.append(Issue("warn", name,
                "Manage-Closely stakeholder has no engagement owner"))
    elif quad == "keep_satisfied":
        if cadence not in ("monthly", "bi-weekly", "biweekly", "weekly"):
            issues.append(Issue("warn", name,
                f"Keep-Satisfied (HP/LI) needs monthly-or-tighter cadence — risk of sleeping-authority surprise (current: {cadence or 'none'})"))

    # Blocker/skeptic must have conversion plan
    if support in ("blocker", "skeptic"):
        if not s.get("blocker_conversion_plan_present"):
            # A powerful blocker with no plan is the classic way initiatives die late: gate on it.
            sev = "fail" if support == "blocker" and power >= 4 else "warn"
            issues.append(Issue(sev, name,
                f"{support} has no conversion plan — convert, neutralize, or out-vote"))

    return issues


def analyze(state: dict[str, Any]) -> dict[str, Any]:
    stakeholders = state.get("stakeholders") or []
    all_issues: list[Issue] = []
    if not stakeholders:
        all_issues.append(Issue("fail", "(initiative)", "no stakeholders listed"))
    for s in stakeholders:
        all_issues.extend(check_stakeholder(s))

    # Quadrant distribution
    by_quadrant: dict[str, list[dict[str, Any]]] = {
        "manage_closely": [], "keep_satisfied": [],
        "keep_informed": [], "monitor": [],
    }
    by_support = Counter()
    for s in stakeholders:
        q = quadrant_of(int(s.get("power", 0)), int(s.get("interest", 0)))
        by_quadrant[q].append(s)
        by_support[(s.get("support") or "").lower()] += 1

    # Initiative-level checks
    blockers = [s for s in stakeholders if (s.get("support") or "").lower() == "blocker"]
    skeptics = [s for s in stakeholders if (s.get("support") or "").lower() == "skeptic"]
    high_power_blockers = [
        s for s in blockers if int(s.get("power", 0)) >= 4
    ]
    if high_power_blockers:
        all_issues.append(Issue("warn", "(initiative)",
            f"{len(high_power_blockers)} high-power blocker(s) — explicit conversion required"))

    keep_satisfied = by_quadrant["keep_satisfied"]
    if keep_satisfied:
        without_plan = [s for s in keep_satisfied if not s.get("engagement_owner")]
        if without_plan:
            all_issues.append(Issue("warn", "(initiative)",
                f"{len(without_plan)} HP/LI stakeholder(s) without engagement plan — sleeping-authority risk"))

    if not by_quadrant["manage_closely"]:
        all_issues.append(Issue("warn", "(initiative)",
            "no Manage-Closely stakeholders identified — verify the initiative has clear decision-makers"))

    if len(stakeholders) < 5 and "major" in (state.get("initiative") or "").lower():
        all_issues.append(Issue("info", "(initiative)",
            f"only {len(stakeholders)} stakeholders for what looks like a major initiative — likely incomplete"))

    sev = {"fail": 0, "warn": 0, "info": 0}
    for i in all_issues:
        sev[i.severity] += 1

    return {
        "initiative": state.get("initiative", ""),
        "as_of": state.get("as_of", ""),
        "stakeholder_count": len(stakeholders),
        "by_quadrant": {q: [s.get("name") for s in v] for q, v in by_quadrant.items()},
        "by_support_count": dict(by_support),
        "high_power_blockers_count": len(high_power_blockers),
        "severity_counts": sev,
        "issues": [
            {"severity": i.severity, "stakeholder": i.stakeholder, "message": i.message}
            for i in all_issues
        ],
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = []
    lines.append(f"# Stakeholder Map Audit — {report.get('initiative','')}\n")
    lines.append(f"_as of {report['as_of']} | {report['stakeholder_count']} stakeholders_\n")
    lines.append("## By quadrant")
    for q, names in report["by_quadrant"].items():
        lines.append(f"- **{q}**: {', '.join(names) if names else '(none)'}")
    lines.append("")
    lines.append("## By support")
    for s, c in report["by_support_count"].items():
        lines.append(f"- {s}: {c}")
    lines.append(f"\n**High-power blockers:** {report['high_power_blockers_count']}\n")
    sc = report["severity_counts"]
    lines.append(f"**Severity:** fail {sc['fail']} | warn {sc['warn']} | info {sc['info']}\n")
    sev_order = {"fail": 0, "warn": 1, "info": 2}
    sorted_issues = sorted(report["issues"], key=lambda i: sev_order.get(i["severity"], 9))
    lines.append("## Issues")
    if not sorted_issues:
        lines.append("_No issues detected._")
    else:
        lines.append("| Severity | Stakeholder | Message |")
        lines.append("|----------|-------------|---------|")
        for i in sorted_issues:
            lines.append(f"| {i['severity']} | {i['stakeholder']} | {i['message']} |")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Audit a stakeholder map",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument("--input", required=True, help="JSON of stakeholders")
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
