#!/usr/bin/env python3
"""
survey_instrument_auditor.py — Audit a survey instrument for leading questions,
scale problems, and sample-size adequacy before fielding.

Reads a JSON instrument (population frame, target precision, and an ordered list
of items) and returns per-item findings plus a required-sample-size verdict
computed from the normal approximation with a finite population correction.

Stdlib only. Deterministic. Text (default) or JSON output.

Usage:
    python3 survey_instrument_auditor.py --input survey.json
    python3 survey_instrument_auditor.py --input survey.json --format json
    python3 survey_instrument_auditor.py --input survey.json --strict

Input schema (see assets/sample_survey.json for a complete example):
{
  "study": str, "population_size": int,
  "target_margin_of_error": 0.05, "confidence_level": 0.95,
  "planned_sample": int, "expected_response_rate": 0.12,
  "items": [{"id", "text",
             "type": "numeric"|"open"|"scale"|"single_choice"|"multi_choice",
             "scale_points": int, "options": [str]}]
}
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

Z_SCORES = {0.80: 1.282, 0.90: 1.645, 0.95: 1.960, 0.98: 2.326, 0.99: 2.576}

LEADING_PATTERNS = [
    (r"\bhow (valuable|useful|helpful|important|beneficial)\b",
     "presupposes value; ask about current behaviour and its cost instead"),
    (r"\bdon'?t you (agree|think)\b", "classic acquiescence prompt"),
    (r"\bwouldn'?t you\b", "invites agreement rather than measuring it"),
    (r"\bhow much do you (love|like|enjoy)\b", "presupposes a positive baseline"),
    (r"\b(obviously|clearly|surely|of course)\b", "asserts the answer inside the question"),
    (r"\b(innovative|cutting-edge|world-class|seamless|powerful|best-in-class)\b",
     "marketing adjective primes a favourable answer"),
    (r"\bimproved\b", "assumes the change was an improvement"),
]

# A conjunction alone is not a second question ("scheduling and billing admin" is
# one construct). Only flag a conjunction that introduces a second interrogative.
DOUBLE_BARREL_PATTERN = re.compile(
    r"\b(and|or)\s+(how|what|why|when|which|do you|are you|would you|did you)\b",
    re.IGNORECASE)

ABSOLUTE_PATTERN = re.compile(
    r"\b(always|never|all|none|every|everyone|nobody)\b", re.IGNORECASE)

ESCAPE_OPTIONS = ("don't know", "dont know", "not sure", "prefer not",
                  "not applicable", "n/a", "none of the above", "unsure")

MAX_ITEM_WORDS = 25
MAX_SCALE_POINTS = 7
MIN_SCALE_POINTS = 4


@dataclass
class Finding:
    """A single problem detected in one survey item or in the design."""

    severity: str
    item_id: str
    message: str


class Findings(list):
    """Accumulator so each rule reads as one call."""

    def add(self, severity: str, item_id: str, message: str) -> None:
        """Record one finding."""
        self.append(Finding(severity, item_id, message))


def audit_item(item: dict[str, Any]) -> Findings:
    """Check one survey item for wording, scale, and option-set problems."""
    item_id = str(item.get("id", "?"))
    text = str(item.get("text", "")).strip()
    f = Findings()
    if not text:
        f.add("fail", item_id, "item has no text")
        return f

    lowered = " ".join(text.lower().split())
    for pattern, reason in LEADING_PATTERNS:
        if re.search(pattern, lowered):
            f.add("fail", item_id, f"leading wording — {reason}")
    if DOUBLE_BARREL_PATTERN.search(lowered):
        f.add("warn", item_id, "double-barrelled item — a conjunction introduces a "
              "second question, so one answer serves both; split it")
    if ABSOLUTE_PATTERN.search(lowered):
        f.add("warn", item_id, "absolute term ('always', 'never') pushes respondents "
              "to the safe middle; use a frequency scale")
    words = len(text.split())
    if words > MAX_ITEM_WORDS:
        f.add("warn", item_id, f"{words} words — items over {MAX_ITEM_WORDS} words lose "
              "respondents; split or trim")

    item_type = str(item.get("type", "")).lower()
    options = [str(o) for o in (item.get("options") or [])]
    if item_type == "scale":
        points = int(item.get("scale_points", len(options) or 0))
        if points and points < MIN_SCALE_POINTS:
            f.add("warn", item_id, f"{points}-point scale is too coarse to detect "
                  f"movement; use {MIN_SCALE_POINTS}-{MAX_SCALE_POINTS} points")
        if points > MAX_SCALE_POINTS:
            f.add("warn", item_id, f"{points}-point scale exceeds reliable "
                  f"discrimination; cap at {MAX_SCALE_POINTS}")
        if options and points and len(options) != points:
            f.add("fail", item_id,
                  f"scale_points is {points} but {len(options)} labels supplied")
        if options and not any(_is_negative_anchor(o) for o in options):
            f.add("warn", item_id, "scale has no clearly negative anchor — an "
                  "unbalanced scale inflates positive response")

    if item_type in ("single_choice", "multi_choice", "scale") and options:
        if not any(any(e in o.lower() for e in ESCAPE_OPTIONS) for o in options):
            f.add("warn", item_id, "no 'don't know' / 'not applicable' escape option — "
                  "respondents will guess rather than skip")
        if len({o.strip().lower() for o in options}) != len(options):
            f.add("fail", item_id, "duplicate response options")
    return f


def _is_negative_anchor(option: str) -> bool:
    """Return True when a scale label reads as the low/negative end."""
    lowered = option.lower()
    negatives = ("not ", "never", "strongly disagree", "disagree", "poor",
                 "very dissatisfied", "dissatisfied", "none", "worse", "unlikely")
    return any(lowered.startswith(n) or n in lowered for n in negatives)


def required_sample(population: int, margin: float, confidence: float,
                    proportion: float = 0.5) -> int:
    """Return the sample size needed for a proportion at the given precision."""
    if margin <= 0 or margin >= 1:
        raise ValueError("target_margin_of_error must be between 0 and 1")
    z = Z_SCORES.get(round(confidence, 2))
    if z is None:
        raise ValueError(
            f"confidence_level {confidence} unsupported; use one of "
            f"{sorted(Z_SCORES)}"
        )
    n0 = (z ** 2) * proportion * (1 - proportion) / (margin ** 2)
    if population and population > 0:
        n0 = n0 / (1 + (n0 - 1) / population)
    return int(math.ceil(n0))


def audit_design(instrument: dict[str, Any]) -> tuple[list[Finding], dict[str, Any]]:
    """Check sampling adequacy and return the sample-size verdict."""
    findings: list[Finding] = []
    population = int(instrument.get("population_size", 0))
    margin = float(instrument.get("target_margin_of_error", 0.05))
    confidence = float(instrument.get("confidence_level", 0.95))
    planned = int(instrument.get("planned_sample", 0))
    response_rate = float(instrument.get("expected_response_rate", 0) or 0)

    needed = required_sample(population, margin, confidence)
    if planned and planned < needed:
        achieved = margin * math.sqrt(needed / planned)
        findings.append(Finding("fail", "design",
                                f"planned sample {planned} is below the {needed} required for "
                                f"+/-{margin:.0%} — actual precision would be about "
                                f"+/-{achieved:.1%}"))
    elif not planned:
        findings.append(Finding("warn", "design",
                                f"no planned_sample given; {needed} completes are required for "
                                f"+/-{margin:.0%} at {confidence:.0%} confidence"))

    invites = None
    if response_rate:
        if not 0 < response_rate <= 1:
            raise ValueError("expected_response_rate must be in (0, 1]")
        invites = int(math.ceil(needed / response_rate))
        if population and invites > population:
            findings.append(Finding("fail", "design",
                                    f"reaching {needed} completes at a {response_rate:.0%} "
                                    f"response rate needs {invites:,} invitations but the frame "
                                    f"holds only {population:,} — relax the margin or change mode"))

    return findings, {
        "population_size": population,
        "target_margin_of_error": margin,
        "confidence_level": confidence,
        "required_completes": needed,
        "planned_sample": planned,
        "invitations_needed": invites,
    }


def analyse(instrument: dict[str, Any]) -> dict[str, Any]:
    """Audit every item plus the sampling design."""
    items = instrument.get("items") or []
    if not items:
        raise ValueError("instrument must contain a non-empty 'items' list")

    findings: list[Finding] = []
    for item in items:
        findings.extend(audit_item(item))
    design_findings, sampling = audit_design(instrument)
    findings.extend(design_findings)

    counts = {"fail": 0, "warn": 0}
    for f in findings:
        counts[f.severity] = counts.get(f.severity, 0) + 1

    return {
        "study": instrument.get("study", ""),
        "item_count": len(items),
        "sampling": sampling,
        "severity_counts": counts,
        "findings": [{"severity": f.severity, "item_id": f.item_id, "message": f.message}
                     for f in findings],
    }


def render_text(report: dict[str, Any]) -> str:
    """Render the audit as human-readable text."""
    s = report["sampling"]
    lines = [f"Survey audit — {report['study']}",
             f"Items: {report['item_count']}", "",
             "Sampling:",
             f"  frame              {s['population_size']:,}",
             f"  target precision   +/-{s['target_margin_of_error']:.0%} at "
             f"{s['confidence_level']:.0%} confidence",
             f"  required completes {s['required_completes']:,}",
             f"  planned sample     {s['planned_sample'] or 'not stated'}"]
    if s["invitations_needed"]:
        lines.append(f"  invitations needed {s['invitations_needed']:,}")
    lines.append("")
    counts = report["severity_counts"]
    lines.append(f"Findings: {counts.get('fail', 0)} fail, {counts.get('warn', 0)} warn")
    if not report["findings"]:
        lines.append("  none — instrument is clean to field")
    order = {"fail": 0, "warn": 1}
    for f in sorted(report["findings"], key=lambda x: order.get(x["severity"], 9)):
        lines.append(f"  [{f['severity'].upper():4}] {f['item_id']}: {f['message']}")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Audit a survey instrument for bias, scale, and sample-size problems.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--input", required=True,
                        help="Path to the JSON survey instrument")
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
        instrument = json.loads(Path(args.input).read_text(encoding="utf-8"))
        report = analyse(instrument)
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
        print(f"error: invalid instrument: {exc}", file=sys.stderr)
        return 1

    if args.strict and report["severity_counts"].get("fail", 0) > 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
