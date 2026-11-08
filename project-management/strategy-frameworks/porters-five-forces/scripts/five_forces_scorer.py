#!/usr/bin/env python3
"""
five_forces_scorer.py — Score Porter's Five Forces for an industry,
identify the dominant force, and surface strategy implications.

Stdlib only. JSON or markdown output.

Usage:
    python3 five_forces_scorer.py --input forces.json
    python3 five_forces_scorer.py --input forces.json --format markdown

Input schema:
{
  "industry": "Mid-market HR analytics B2B SaaS",
  "as_of": "2026-05-27",
  "horizon_years": 3,
  "forces": {
      "new_entrants": {
          "intensity": "high|medium|low",
          "factors": ["low capital", "no proprietary IP", ...],
          "evidence": "..."
      },
      "supplier_power": {...},
      "buyer_power": {...},
      "substitute_threat": {...},
      "competitive_rivalry": {...},
      "complementors": {...}    # optional 6th force
  },
  "strategy_implications": [
      {"force": "buyer_power", "move": "diversify segment", "priority": "high"}
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


FORCE_NAMES = [
    "new_entrants", "supplier_power", "buyer_power",
    "substitute_threat", "competitive_rivalry",
]

INTENSITY_SCORE = {"low": 1, "medium": 2, "high": 3}


@dataclass
class Issue:
    severity: str
    force: str
    message: str


def check_force(name: str, f: dict[str, Any]) -> tuple[list[Issue], int]:
    issues = []
    if not f:
        issues.append(Issue("fail", name, "force not scored"))
        return issues, 0
    intensity = (f.get("intensity") or "").lower()
    if intensity not in INTENSITY_SCORE:
        issues.append(Issue("fail", name, f"intensity must be low/medium/high (got '{intensity}')"))
        return issues, 0
    factors = f.get("factors") or []
    if len(factors) < 2:
        issues.append(Issue("warn", name,
            f"fewer than 2 supporting factors; reasoning thin"))
    if not f.get("evidence"):
        issues.append(Issue("warn", name, "no evidence cited"))
    return issues, INTENSITY_SCORE[intensity]


def check_industry_definition(industry: str) -> list[Issue]:
    if not industry:
        return [Issue("fail", "industry",
            "no industry defined — Five Forces requires specific industry")]
    if len(industry) < 20:
        return [Issue("warn", "industry",
            f"industry definition short ({len(industry)} chars); add specifics (segment / geography)")]
    return []


def check_strategy_implications(implications: list[dict[str, Any]]) -> list[Issue]:
    issues = []
    if not implications:
        return [Issue("warn", "strategy_implications",
            "no strategy implications drawn — Five Forces without action is decorative")]
    high_count = sum(1 for i in implications if (i.get("priority") or "").lower() == "high")
    if high_count == 0:
        issues.append(Issue("warn", "strategy_implications",
            "no high-priority strategic moves identified"))
    elif high_count > 5:
        issues.append(Issue("warn", "strategy_implications",
            f"{high_count} high-priority moves — too many; pick 2-3"))
    return issues


def analyze(state: dict[str, Any]) -> dict[str, Any]:
    industry = state.get("industry", "")
    forces = state.get("forces") or {}
    implications = state.get("strategy_implications") or []

    all_issues: list[Issue] = []
    all_issues.extend(check_industry_definition(industry))

    force_scores: dict[str, int] = {}
    force_intensities: dict[str, str] = {}
    for fname in FORCE_NAMES:
        issues, score = check_force(fname, forces.get(fname))
        all_issues.extend(issues)
        force_scores[fname] = score
        f = forces.get(fname) or {}
        force_intensities[fname] = (f.get("intensity") or "").lower() or "—"

    # Optional 6th force
    if forces.get("complementors"):
        issues, score = check_force("complementors", forces["complementors"])
        all_issues.extend(issues)
        force_scores["complementors"] = score
        force_intensities["complementors"] = (forces["complementors"].get("intensity") or "").lower() or "—"

    all_issues.extend(check_strategy_implications(implications))
    if all(force_intensities.get(f) == "medium" for f in FORCE_NAMES):
        all_issues.append(Issue("warn", "forces",
            "every force rated medium; usually a sign the factors were not weighed"))

    # Industry attractiveness: sum of all NEGATIVE forces (high=unfavorable for incumbents)
    total = sum(force_scores.get(f, 0) for f in FORCE_NAMES)
    # Max would be 5×3 = 15. Lower = more attractive.
    unscored = [f for f in FORCE_NAMES if not force_scores.get(f)]
    if unscored:
        attractiveness = f"Not rated ({len(unscored)} of 5 forces unscored)"
    elif total <= 7:
        attractiveness = "Attractive (low overall force intensity)"
    elif total <= 10:
        attractiveness = "Moderate"
    else:
        attractiveness = "Unattractive (high overall force intensity)"

    # Dominant force(s)
    high_forces = [f for f in FORCE_NAMES if force_intensities.get(f) == "high"]
    medium_forces = [f for f in FORCE_NAMES if force_intensities.get(f) == "medium"]

    sev_counts = {"fail": 0, "warn": 0, "info": 0}
    for i in all_issues:
        sev_counts[i.severity] += 1

    return {
        "industry": industry,
        "as_of": state.get("as_of", ""),
        "horizon_years": state.get("horizon_years", 3),
        "force_intensities": force_intensities,
        "total_intensity_score": total,
        "max_score": 15,
        "attractiveness_verdict": attractiveness,
        "dominant_high_forces": high_forces,
        "medium_forces": medium_forces,
        "implication_count": len(implications),
        "severity_counts": sev_counts,
        "issues": [
            {"severity": i.severity, "force": i.force, "message": i.message}
            for i in all_issues
        ],
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = []
    lines.append(f"# Porter's Five Forces — {report.get('industry','')}\n")
    lines.append(f"_as of {report['as_of']} | horizon: {report['horizon_years']} years_\n")
    lines.append(f"## Attractiveness: **{report['attractiveness_verdict']}**")
    lines.append(f"_Total intensity: {report['total_intensity_score']}/{report['max_score']}_\n")
    lines.append("## Force intensities")
    lines.append("| Force | Intensity |")
    lines.append("|-------|-----------|")
    for f, i in report["force_intensities"].items():
        lines.append(f"| {f} | {i} |")
    lines.append("")
    if report["dominant_high_forces"]:
        lines.append("**Dominant (high) forces:** " + ", ".join(report["dominant_high_forces"]))
    sc = report["severity_counts"]
    lines.append(f"\n**Severity:** fail {sc['fail']} | warn {sc['warn']} | info {sc['info']}\n")
    sev_order = {"fail": 0, "warn": 1, "info": 2}
    sorted_issues = sorted(report["issues"], key=lambda i: sev_order.get(i["severity"], 9))
    lines.append("## Issues")
    if not sorted_issues:
        lines.append("_No issues detected._")
    else:
        lines.append("| Severity | Force | Message |")
        lines.append("|----------|-------|---------|")
        for i in sorted_issues:
            lines.append(f"| {i['severity']} | {i['force']} | {i['message']} |")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Score Porter's Five Forces",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument("--input", required=True, help="JSON of forces")
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
