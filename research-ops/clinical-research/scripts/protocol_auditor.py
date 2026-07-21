#!/usr/bin/env python3
"""
protocol_auditor.py — Audit a clinical study protocol outline for the elements
ICH E6 expects, plus the endpoint and eligibility defects that most often send a
protocol back from ethics or regulatory review.

Reports missing required sections, endpoint definition problems,
inclusion/exclusion conflicts, and gaps in the statistical and safety sections.
Stdlib only. Deterministic. Text (default) or JSON output.

Checks structure and internal consistency only. Not a regulatory review; does
not replace sign-off by qualified regulatory affairs and clinical personnel.

Usage:
    python3 protocol_auditor.py --input protocol.json [--format json] [--strict]

Input schema (see assets/sample_protocol.json for a complete example):
{
  "title": str, "protocol_id": str, "phase": str,
  "sections_present": [str],          # keys from REQUIRED_SECTIONS, see
                                      # protocol_rules.py
  "endpoints": [{"name", "role", "measure", "timepoint", "analysis_population"}],
  "eligibility": {"inclusion": [str], "exclusion": [str]},
  "statistics": {"sample_size_justified", "analysis_populations",
                 "missing_data_strategy", "interim_analyses",
                 "alpha_spending_function", "multiple_primary_comparisons",
                 "multiplicity_adjustment"},
  "safety": {"ae_reporting_defined", "sae_reporting_window_hours", "dsmb",
             "stopping_rules_defined"},
  "governance": {"ethics_submission_planned", "registered",
                 "informed_consent_process_described"}
}
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

# What a protocol must contain lives in its own module so clinical and
# regulatory readers can revise the domain content without touching the
# traversal and reporting logic here. Same-skill sibling import.
from protocol_rules import (
    DISCLAIMER,
    MAX_SAE_WINDOW_HOURS,
    PHASES_REQUIRING_DSMB,
    REQUIRED_SECTIONS,
    SEVERITY_ORDER,
    VAGUE_MEASURE_TERMS,
    Finding,
    Findings,
)


def check_sections(present: list[str]) -> Findings:
    """Flag every ICH E6 protocol section absent from the outline."""
    seen = {str(s).strip().lower().replace(" ", "_") for s in present}
    f = Findings()
    for key, description in REQUIRED_SECTIONS.items():
        if key not in seen:
            f.add("fail", "sections", f"missing section '{key}' — {description}")
    return f


def check_endpoints(endpoints: list[dict[str, Any]]) -> Findings:
    """Check endpoint count, hierarchy, and definition completeness."""
    f = Findings()
    if not endpoints:
        f.add("fail", "endpoints", "no endpoints defined — nothing to power or analyse")
        return f

    primaries = [e for e in endpoints if str(e.get("role", "")).lower() == "primary"]
    if not primaries:
        f.add("fail", "endpoints", "no primary endpoint designated")
    elif len(primaries) > 1:
        f.add("fail", "endpoints", f"{len(primaries)} co-primary endpoints — needs an "
              "explicit multiplicity strategy and a larger sample; confirm it is intended")

    for e in endpoints:
        name = e.get("name", "unnamed")
        role = str(e.get("role", "unspecified")).lower()
        sev = "fail" if role == "primary" else "warn"
        if not e.get("timepoint"):
            f.add(sev, "endpoints", f"'{name}' has no timepoint — not analysable")
        if not e.get("measure"):
            f.add(sev, "endpoints", f"'{name}' has no measure — state the instrument, "
                  "scale, or event counted")
        elif str(e["measure"]).strip().lower() in VAGUE_MEASURE_TERMS:
            f.add("warn", "endpoints", f"'{name}' measure '{e['measure']}' is too vague — "
                  "name the instrument and the threshold defining the outcome")
        if role == "primary" and not e.get("analysis_population"):
            f.add("warn", "endpoints",
                  f"primary endpoint '{name}' names no analysis population (ITT, mITT, PP)")
    return f


def check_eligibility(eligibility: dict[str, Any]) -> Findings:
    """Check inclusion and exclusion criteria for conflicts and redundancy."""
    f = Findings()
    inclusion = [str(c) for c in (eligibility.get("inclusion") or [])]
    exclusion = [str(c) for c in (eligibility.get("exclusion") or [])]
    if not inclusion:
        f.add("fail", "eligibility", "no inclusion criteria defined")
    if not exclusion:
        f.add("fail", "eligibility",
              "no exclusion criteria — every protocol needs explicit safety exclusions")

    inc = {c.strip().lower() for c in inclusion}
    overlap = inc & {c.strip().lower() for c in exclusion}
    if overlap:
        f.add("fail", "eligibility",
              f"criteria appear in both inclusion and exclusion: {sorted(overlap)}")

    # A criterion that merely negates an inclusion adds screening burden without
    # changing who is eligible.
    for exc in exclusion:
        low = exc.strip().lower()
        for prefix in ("not ", "no ", "absence of ", "does not "):
            if low.startswith(prefix) and low[len(prefix):] in inc:
                f.add("warn", "eligibility", f"exclusion '{exc}' negates an inclusion "
                      "criterion — redundant, and it lengthens screening")

    total = len(inclusion) + len(exclusion)
    if total > 30:
        f.add("warn", "eligibility", f"{total} eligibility criteria — beyond roughly 25-30, "
              "screen failure climbs steeply and accrual stalls; justify each")
    if len(exclusion) > 2 * max(len(inclusion), 1):
        f.add("warn", "eligibility", "exclusions heavily outnumber inclusions — the studied "
              "population may not resemble the treated one")
    return f


def check_statistics(stats: dict[str, Any]) -> Findings:
    """Check the statistical section for the elements reviewers look for first."""
    f = Findings()
    if not stats:
        f.add("fail", "statistics", "no statistics section")
        return f
    if not stats.get("sample_size_justified"):
        f.add("fail", "statistics", "sample size not justified — state effect size, alpha, "
              "power, and the source of the assumed variance")
    if not (stats.get("analysis_populations") or []):
        f.add("fail", "statistics", "no analysis populations defined (ITT, mITT, PP, safety)")
    if not stats.get("missing_data_strategy"):
        f.add("fail", "statistics", "no missing-data strategy — must be pre-specified, not "
              "chosen after the data are seen")
    interim = int(stats.get("interim_analyses", 0) or 0)
    if interim > 0 and not stats.get("alpha_spending_function"):
        f.add("fail", "statistics", f"{interim} interim analysis/analyses with no alpha "
              "spending function — unadjusted looks inflate type I error")
    if stats.get("multiple_primary_comparisons") and not stats.get("multiplicity_adjustment"):
        f.add("fail", "statistics",
              "multiple primary comparisons with no multiplicity adjustment")
    return f


def check_safety(safety: dict[str, Any], phase: str) -> Findings:
    """Check safety reporting and oversight provisions."""
    f = Findings()
    if not safety:
        f.add("fail", "safety", "no safety section")
        return f
    if not safety.get("ae_reporting_defined"):
        f.add("fail", "safety", "AE definitions and reporting procedure not defined")
    window = safety.get("sae_reporting_window_hours")
    if window is None:
        f.add("fail", "safety", "no SAE reporting window stated")
    elif int(window) > MAX_SAE_WINDOW_HOURS:
        f.add("fail", "safety", f"SAE window of {window}h exceeds the "
              f"{MAX_SAE_WINDOW_HOURS}h expectation for immediate sponsor reporting")
    if str(phase) in PHASES_REQUIRING_DSMB and not safety.get("dsmb"):
        f.add("warn", "safety",
              f"phase {phase} study with no DSMB — justify the absence in the protocol")
    if not safety.get("stopping_rules_defined"):
        f.add("warn", "safety", "no stopping rules — state futility and harm criteria "
              "before the first participant is enrolled")
    return f


def check_governance(governance: dict[str, Any]) -> Findings:
    """Check ethics, registration, and consent provisions."""
    f = Findings()
    if not governance.get("informed_consent_process_described"):
        f.add("fail", "governance", "informed consent process not described")
    if not governance.get("ethics_submission_planned"):
        f.add("fail", "governance", "no ethics committee submission planned")
    if not governance.get("registered"):
        f.add("warn", "governance", "study not registered — most journals require "
              "prospective registration before first enrolment")
    return f


def audit(protocol: dict[str, Any]) -> dict[str, Any]:
    """Run every protocol check and aggregate the findings."""
    findings: list[Finding] = [
        *check_sections(protocol.get("sections_present") or []),
        *check_endpoints(protocol.get("endpoints") or []),
        *check_eligibility(protocol.get("eligibility") or {}),
        *check_statistics(protocol.get("statistics") or {}),
        *check_safety(protocol.get("safety") or {}, str(protocol.get("phase", ""))),
        *check_governance(protocol.get("governance") or {}),
    ]
    counts = {"fail": 0, "warn": 0}
    for f in findings:
        counts[f.severity] = counts.get(f.severity, 0) + 1
    present = len(REQUIRED_SECTIONS) - sum(1 for f in findings if f.area == "sections")

    return {
        "title": protocol.get("title", ""),
        "protocol_id": protocol.get("protocol_id", ""),
        "phase": protocol.get("phase", ""),
        "sections_present": present,
        "sections_required": len(REQUIRED_SECTIONS),
        "verdict": ("not ready for submission" if counts["fail"]
                    else "structurally complete"),
        "severity_counts": counts,
        "findings": [{"severity": f.severity, "area": f.area, "message": f.message}
                     for f in findings],
        "disclaimer": DISCLAIMER,
    }


def render_text(report: dict[str, Any]) -> str:
    """Render the audit as human-readable text."""
    lines = [f"Protocol audit — {report['title']}",
             f"ID: {report['protocol_id']} | Phase: {report['phase']}",
             f"Sections: {report['sections_present']}/{report['sections_required']}",
             f"Verdict: {report['verdict'].upper()}", ""]
    counts = report["severity_counts"]
    lines.append(f"Findings: {counts.get('fail', 0)} fail, {counts.get('warn', 0)} warn")
    if not report["findings"]:
        lines.append("  none")
    for f in sorted(report["findings"],
                    key=lambda x: (SEVERITY_ORDER.get(x["severity"], 9), x["area"])):
        lines.append(f"  [{f['severity'].upper():4}] {f['area']}: {f['message']}")
    lines.append("")
    lines.append(f"NOTE: {report['disclaimer']}")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Audit a clinical protocol outline for required elements.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--input", required=True,
                        help="Path to the JSON protocol outline")
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
        protocol = json.loads(Path(args.input).read_text(encoding="utf-8"))
        report = audit(protocol)
        out = (json.dumps(report, indent=2) if args.format == "json"
               else render_text(report))
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
    except (ValueError, KeyError, TypeError) as exc:
        print(f"error: invalid protocol outline: {exc}", file=sys.stderr)
        return 1

    if args.strict and report["severity_counts"].get("fail", 0) > 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
