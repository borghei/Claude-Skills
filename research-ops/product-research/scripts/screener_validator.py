#!/usr/bin/env python3
"""
screener_validator.py — Validate a recruiting screener for transparency,
disqualification logic, quota coverage, and professional-respondent exposure.

Reads a JSON screener (criteria, items, quotas, incentive) and reports every
criterion no item tests, every item whose qualifying answer is obvious to a
motivated respondent, and every gap in the quota plan.

Stdlib only. Deterministic. Text (default) or JSON output.

Usage:
    python3 screener_validator.py --input screener.json
    python3 screener_validator.py --input screener.json --format json
    python3 screener_validator.py --input screener.json --strict

Input schema:
{
  "study": "Ticket triage discovery",
  "target_sessions": 8,
  "incentive_value": 120,
  "recruiting_source": "existing_customers",
  "criteria": [
      {"id": "C1", "description": "Handles inbound tickets daily",
       "kind": "qualify", "tested_by": ["Q2"]},
      {"id": "C2", "description": "Works at a competitor",
       "kind": "disqualify", "tested_by": ["Q4"]}
  ],
  "items": [
      {"id": "Q2", "text": "In a typical week, which of these tasks do you
                            personally perform?",
       "options": ["Triaging inbound tickets", "Writing documentation",
                   "Managing billing", "None of these"],
       "qualifying_options": ["Triaging inbound tickets"]}
  ],
  "quotas": [{"segment": "high_volume", "target": 4},
             {"segment": "low_volume", "target": 4}]
}
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# Above this, an incentive starts attracting people who answer for the money.
HIGH_INCENTIVE = 200
MIN_DISTRACTOR_OPTIONS = 2
TRAP_HINT_WORDS = ("trap", "decoy", "fictional", "does not exist", "invented")


@dataclass
class Finding:
    """A defect in the screener design."""

    severity: str
    ref: str
    message: str


def check_criteria_coverage(criteria: list[dict[str, Any]],
                            item_ids: set[str]) -> list[Finding]:
    """Flag criteria with no testing item, and items referenced but not defined."""
    findings: list[Finding] = []
    if not criteria:
        findings.append(Finding("fail", "screener",
                                "no criteria defined — a screener without explicit "
                                "qualifying criteria cannot be validated or audited"))
        return findings

    has_disqualifier = any(c.get("kind") == "disqualify" for c in criteria)
    if not has_disqualifier:
        findings.append(Finding("fail", "screener",
                                "no disqualifying criteria — every screener needs explicit "
                                "exclusions (competitors, employees, prior participants), "
                                "not just inclusions"))

    for crit in criteria:
        cid = str(crit.get("id", "?"))
        tested_by = crit.get("tested_by") or []
        if not tested_by:
            findings.append(Finding("fail", cid,
                                    f"criterion '{crit.get('description', '')}' is not tested "
                                    "by any item — it will not be enforced"))
            continue
        for ref in tested_by:
            if ref not in item_ids:
                findings.append(Finding("fail", cid,
                                        f"references item '{ref}', which is not defined"))
    return findings


def check_item(item: dict[str, Any]) -> list[Finding]:
    """Check one screener item for transparency and option-set quality."""
    item_id = str(item.get("id", "?"))
    findings: list[Finding] = []
    options = [str(o) for o in (item.get("options") or [])]
    qualifying = [str(o) for o in (item.get("qualifying_options") or [])]

    if not str(item.get("text", "")).strip():
        findings.append(Finding("fail", item_id, "item has no text"))

    if not options:
        # Open-numeric items are fine, but they cannot be scored automatically.
        if item.get("type") not in ("numeric", "open"):
            findings.append(Finding("warn", item_id,
                                    "no options and not marked type 'numeric' or 'open' — "
                                    "qualification cannot be applied consistently"))
        return findings

    if qualifying:
        unknown = [q for q in qualifying if q not in options]
        if unknown:
            findings.append(Finding("fail", item_id,
                                    f"qualifying option(s) {unknown} are not in the option list"))
        if len(qualifying) == len(options):
            findings.append(Finding("fail", item_id,
                                    "every option qualifies — this item screens nobody out"))
        distractors = len(options) - len(qualifying)
        # Trap items are meant to have a single disqualifying option.
        if 0 < distractors < MIN_DISTRACTOR_OPTIONS and not item.get("is_trap"):
            findings.append(Finding("warn", item_id,
                                    f"only {distractors} non-qualifying option(s) — with so few "
                                    "distractors the qualifying answer is guessable; add more"))
        if len(qualifying) == 1 and options and options[0] == qualifying[0]:
            findings.append(Finding("warn", item_id,
                                    "the qualifying option is listed first — move it into the "
                                    "middle of the list so it does not read as the intended answer"))
    else:
        findings.append(Finding("warn", item_id,
                                "no qualifying_options declared — reviewers cannot tell what "
                                "this item screens on"))

    lowered_text = str(item.get("text", "")).lower()
    if any(word in lowered_text for word in TRAP_HINT_WORDS):
        findings.append(Finding("fail", item_id,
                                "item text reveals that it is a trap item — remove the hint"))

    seen = {o.strip().lower() for o in options}
    if len(seen) != len(options):
        findings.append(Finding("fail", item_id, "duplicate response options"))

    return findings


def check_recruiting(screener: dict[str, Any], items: list[dict[str, Any]]) -> list[Finding]:
    """Check incentive level, trap coverage, and quota arithmetic."""
    findings: list[Finding] = []
    incentive = float(screener.get("incentive_value", 0) or 0)
    source = str(screener.get("recruiting_source", "")).lower()
    target = int(screener.get("target_sessions", 0) or 0)

    has_trap = any(item.get("is_trap") for item in items)
    if source in ("panel", "public_list") and not has_trap:
        findings.append(Finding("fail", "recruiting",
                                "panel recruiting without a trap item — professional "
                                "respondents will qualify themselves in; add an item with "
                                "an invented option that disqualifies on selection"))
    elif not has_trap:
        findings.append(Finding("warn", "recruiting",
                                "no trap item — add one if the incentive is meaningful "
                                "relative to the participant's time"))

    if incentive >= HIGH_INCENTIVE and not has_trap:
        findings.append(Finding("fail", "recruiting",
                                f"incentive of {incentive:g} is high enough to attract "
                                "answer-for-money respondents and there is no trap item"))

    quotas = screener.get("quotas") or []
    if not quotas:
        findings.append(Finding("warn", "recruiting",
                                "no quotas — recruiting without quotas produces a sample of "
                                "convenience skewed toward your most engaged users"))
    else:
        quota_total = sum(int(q.get("target", 0)) for q in quotas)
        if target and quota_total != target:
            findings.append(Finding("warn", "recruiting",
                                    f"quota targets sum to {quota_total} but target_sessions "
                                    f"is {target}"))
        thin = [q["segment"] for q in quotas if int(q.get("target", 0)) < 3]
        if thin:
            findings.append(Finding("warn", "recruiting",
                                    f"segment(s) {thin} have fewer than 3 sessions — that is "
                                    "anecdote, not a segment finding"))
    if target and target < 5:
        findings.append(Finding("warn", "recruiting",
                                f"{target} sessions is below the 5-6 needed to see a pattern "
                                "in a single segment"))
    return findings


def validate(screener: dict[str, Any]) -> dict[str, Any]:
    """Run every screener check and aggregate the findings."""
    items = screener.get("items") or []
    if not items:
        raise ValueError("screener must contain a non-empty 'items' list")
    item_ids = {str(i.get("id", "")) for i in items}

    findings: list[Finding] = []
    findings.extend(check_criteria_coverage(screener.get("criteria") or [], item_ids))
    for item in items:
        findings.extend(check_item(item))
    findings.extend(check_recruiting(screener, items))

    counts = {"fail": 0, "warn": 0}
    for f in findings:
        counts[f.severity] = counts.get(f.severity, 0) + 1

    return {
        "study": screener.get("study", ""),
        "item_count": len(items),
        "criteria_count": len(screener.get("criteria") or []),
        "target_sessions": screener.get("target_sessions", 0),
        "verdict": "not ready to field" if counts["fail"] else "ready to field",
        "severity_counts": counts,
        "findings": [{"severity": f.severity, "ref": f.ref, "message": f.message}
                     for f in findings],
    }


def render_text(report: dict[str, Any]) -> str:
    """Render the validation as human-readable text."""
    lines = [f"Screener validation — {report['study']}",
             f"Criteria: {report['criteria_count']} | Items: {report['item_count']} | "
             f"Target sessions: {report['target_sessions']}",
             f"Verdict: {report['verdict'].upper()}", ""]
    counts = report["severity_counts"]
    lines.append(f"Findings: {counts.get('fail', 0)} fail, {counts.get('warn', 0)} warn")
    if not report["findings"]:
        lines.append("  none — screener is clean")
    order = {"fail": 0, "warn": 1}
    for f in sorted(report["findings"], key=lambda x: order.get(x["severity"], 9)):
        lines.append(f"  [{f['severity'].upper():4}] {f['ref']}: {f['message']}")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Validate a recruiting screener before recruiting opens.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--input", required=True, help="Path to the JSON screener")
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
        screener = json.loads(Path(args.input).read_text(encoding="utf-8"))
        report = validate(screener)
        out = json.dumps(report, indent=2) if args.format == "json" else render_text(report)
        if args.output:
            Path(args.output).write_text(out, encoding="utf-8")
            print(f"wrote {args.output}", file=sys.stderr)
        else:
            print(out)
    except OSError as exc:
        print(f"error: cannot read or write file: {exc}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as exc:
        print(f"error: --input is not valid JSON: {exc}", file=sys.stderr)
        return 1
    except (ValueError, KeyError, TypeError, ZeroDivisionError) as exc:
        print(f"error: invalid screener: {exc}", file=sys.stderr)
        return 1

    if args.strict and report["severity_counts"].get("fail", 0) > 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
