#!/usr/bin/env python3
"""
icp_scorer.py — Score a candidate account against an ICP, or audit an ICP
definition for specificity / disqualification discipline.

Stdlib only. Two modes:
  --mode validate: audit ICP definition completeness
  --mode score: score a list of accounts against the ICP

JSON or markdown output.

Usage:
    python3 icp_scorer.py --input icp_spec.json --mode validate
    python3 icp_scorer.py --input accounts.json --mode score --format markdown

Validate mode input:
{
  "icp_name": "Mid-market HR analytics",
  "dimensions": {
      "firmographics": {"defined": true, "specific": true, "exclusions": ["..."]},
      "tech_stack": {"defined": true, "signals": ["Workday","BambooHR"]},
      "buyer_persona": {"defined": true, "title": "VP People"},
      "jtbd": {"defined": true, "statement": "..."},
      "existing_alternatives": {"defined": true, "list": ["Excel + analyst"]},
      "trigger_events": {"defined": true, "list": ["new VP People","board ask"]},
      "budget_authority": {"defined": true, "level": "VP $25-100K"},
      "reachability": {"defined": true, "channels": ["LinkedIn","SHRM"], "list_size": 1200}
  },
  "disqualification_criteria_present": true
}

Score mode input:
{
  "icp_name": "Mid-market HR analytics",
  "scoring_weights": {
      "industry_fit": 15, "size_fit": 15, "geography": 10,
      "tech_stack_fit": 15, "buyer_role_match": 15,
      "trigger_event_present": 15, "budget_authority": 10, "timeline": 5
  },
  "accounts": [
      {
          "name": "Acme Corp",
          "industry_fit": 3, "size_fit": 3, "geography": 3,
          "tech_stack_fit": 2, "buyer_role_match": 3,
          "trigger_event_present": 3, "budget_authority": 2, "timeline": 2
      }
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


REQUIRED_DIMENSIONS = [
    "firmographics", "tech_stack", "buyer_persona", "jtbd",
    "existing_alternatives", "trigger_events", "budget_authority", "reachability",
]


@dataclass
class Issue:
    severity: str
    component: str
    message: str


def validate_icp(state: dict[str, Any]) -> dict[str, Any]:
    issues: list[Issue] = []
    dims = state.get("dimensions") or {}
    defined_count = 0
    for d in REQUIRED_DIMENSIONS:
        dd = dims.get(d, {})
        if dd.get("defined"):
            defined_count += 1
        else:
            issues.append(Issue("warn", d, f"dimension '{d}' not marked defined"))

    if defined_count < 6:
        issues.append(Issue("fail", "(icp)",
            f"only {defined_count}/8 dimensions defined — ICP too thin"))

    # Specificity checks
    firmo = dims.get("firmographics", {})
    if firmo.get("defined") and not firmo.get("specific"):
        issues.append(Issue("warn", "firmographics",
            "firmographics not marked specific — likely vague"))

    triggers = dims.get("trigger_events", {})
    if triggers.get("defined"):
        trig_list = triggers.get("list") or []
        if not trig_list:
            issues.append(Issue("warn", "trigger_events",
                "no specific triggers listed"))

    reach = dims.get("reachability", {})
    if reach.get("defined"):
        list_size = int(reach.get("list_size", 0) or 0)
        if list_size == 0:
            issues.append(Issue("warn", "reachability",
                "no addressable list size specified"))
        elif list_size < 200:
            issues.append(Issue("warn", "reachability",
                f"addressable list size {list_size} may be too small for outbound motion"))

    if not state.get("disqualification_criteria_present"):
        issues.append(Issue("warn", "(icp)",
            "no disqualification criteria — ICP that doesn't exclude isn't an ICP"))

    sev = {"fail": 0, "warn": 0, "info": 0}
    for i in issues:
        sev[i.severity] += 1

    return {
        "icp_name": state.get("icp_name", ""),
        "mode": "validate",
        "dimensions_defined": defined_count,
        "dimensions_required": len(REQUIRED_DIMENSIONS),
        "completeness_pct": round((defined_count / len(REQUIRED_DIMENSIONS)) * 100),
        "severity_counts": sev,
        "issues": [
            {"severity": i.severity, "component": i.component, "message": i.message}
            for i in issues
        ],
    }


DEFAULT_WEIGHTS = {
    "industry_fit": 15, "size_fit": 15, "geography": 10,
    "tech_stack_fit": 15, "buyer_role_match": 15,
    "trigger_event_present": 15, "budget_authority": 10, "timeline": 5,
}


def score_accounts(state: dict[str, Any]) -> dict[str, Any]:
    accounts = state.get("accounts") or []
    weights = state.get("scoring_weights") or DEFAULT_WEIGHTS
    # Normalize weights to sum to 100
    total_weight = sum(weights.values())
    if total_weight > 0:
        weights = {k: (v / total_weight) * 100 for k, v in weights.items()}

    scored = []
    for acc in accounts:
        name = acc.get("name", "(unnamed)")
        total = 0.0
        for dim, weight in weights.items():
            raw = int(acc.get(dim, 0) or 0)  # 0-3
            normalized = max(0.0, min(1.0, raw / 3.0))
            total += weight * normalized
        band = (
            "strong" if total >= 80 else
            "workable" if total >= 60 else
            "marginal" if total >= 40 else
            "disqualify"
        )
        scored.append({
            "name": name,
            "score": round(total, 1),
            "band": band,
        })

    scored.sort(key=lambda x: x["score"], reverse=True)
    band_counts = {"strong": 0, "workable": 0, "marginal": 0, "disqualify": 0}
    for s in scored:
        band_counts[s["band"]] += 1

    return {
        "icp_name": state.get("icp_name", ""),
        "mode": "score",
        # No accounts is a broken input, not an empty pipeline: gate on it.
        "severity_counts": {"fail": 0 if accounts else 1, "warn": 0, "info": 0},
        "account_count": len(accounts),
        "weights": weights,
        "band_counts": band_counts,
        "accounts": scored,
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = []
    if report["mode"] == "validate":
        lines.append(f"# ICP Validation — {report.get('icp_name','(unnamed)')}\n")
        lines.append(f"**Completeness:** {report['dimensions_defined']}/"
                    f"{report['dimensions_required']} dimensions ({report['completeness_pct']}%)\n")
        sc = report["severity_counts"]
        lines.append(f"**Severity:** fail {sc['fail']} | warn {sc['warn']} | info {sc['info']}\n")
        sev_order = {"fail": 0, "warn": 1, "info": 2}
        sorted_issues = sorted(report["issues"], key=lambda i: sev_order.get(i["severity"], 9))
        lines.append("## Issues")
        if not sorted_issues:
            lines.append("_No issues detected._")
        else:
            lines.append("| Severity | Component | Message |")
            lines.append("|----------|-----------|---------|")
            for i in sorted_issues:
                lines.append(f"| {i['severity']} | {i['component']} | {i['message']} |")
    else:
        lines.append(f"# ICP Scoring — {report.get('icp_name','(unnamed)')}\n")
        lines.append(f"_scored {report['account_count']} accounts_\n")
        bc = report["band_counts"]
        lines.append(f"**Distribution:** strong {bc['strong']} | workable {bc['workable']} | "
                    f"marginal {bc['marginal']} | disqualify {bc['disqualify']}\n")
        lines.append("## Accounts (ranked)")
        lines.append("| Account | Score | Band |")
        lines.append("|---------|-------|------|")
        for a in report["accounts"]:
            lines.append(f"| {a['name']} | {a['score']}/100 | {a['band']} |")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Validate ICP definition OR score accounts against ICP",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument("--input", required=True, help="JSON input")
    p.add_argument("--mode", choices=["validate", "score"], required=True)
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
        report = validate_icp(state) if args.mode == "validate" else score_accounts(state)
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
