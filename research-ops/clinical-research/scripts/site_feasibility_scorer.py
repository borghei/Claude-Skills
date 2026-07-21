#!/usr/bin/env python3
"""
site_feasibility_scorer.py — Score candidate investigator sites on realistic
accrual capacity and operational readiness, then test whether the selected set
can deliver the enrolment target inside the accrual window.

Reads a JSON site set with each site's eligible population, historical accrual
performance, startup time, and operational readiness flags. Applies a discount
to self-reported accrual estimates, projects a realistic monthly rate, and
reports the enrolment shortfall or surplus for the study as a whole.

Stdlib only. Deterministic. Text (default) or JSON output.

Usage:
    python3 site_feasibility_scorer.py --input sites.json
    python3 site_feasibility_scorer.py --input sites.json --format json
    python3 site_feasibility_scorer.py --input sites.json --select 6

Input schema:
{
  "study": "...", "enrolment_target": 408, "accrual_window_months": 24,
  "sites": [
      {"id": "S01", "name": "Site name", "country": "DE",
       "annual_eligible_patients": 240,
       "self_reported_monthly_accrual": 4.0,
       "prior_studies_completed": 6,
       "prior_accrual_attainment": 0.75,
       "startup_months": 3,
       "has_dedicated_coordinator": true,
       "has_local_lab": true,
       "ethics_route": "national",
       "competing_studies": 1}
  ]
}

prior_accrual_attainment is the fraction of the site's committed enrolment it
actually delivered on previous studies. Omit it for sites with no track record.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

# Sites routinely overestimate their own accrual. This is the discount applied
# to a self-reported figure before it enters any projection.
OPTIMISM_DISCOUNT = 0.55
# Assumed attainment for a site with no completed prior studies.
NAIVE_SITE_ATTAINMENT = 0.5
# Each concurrently competing study removes roughly this share of capacity.
COMPETING_STUDY_PENALTY = 0.20
READINESS_MAX = 100


def _readiness(site: dict[str, Any]) -> tuple[int, list[str]]:
    """Score operational readiness out of 100 and list the gaps found."""
    score = READINESS_MAX
    gaps: list[str] = []
    if not site.get("has_dedicated_coordinator"):
        score -= 30
        gaps.append("no dedicated study coordinator — the single strongest "
                    "predictor of accrual shortfall")
    if not site.get("has_local_lab"):
        score -= 10
        gaps.append("no local lab — sample shipping adds protocol deviations")
    startup = float(site.get("startup_months", 0) or 0)
    if startup > 6:
        score -= 25
        gaps.append(f"{startup:g}-month startup consumes a quarter of a typical "
                    "accrual window before the first participant")
    elif startup > 3:
        score -= 10
        gaps.append(f"{startup:g}-month startup is slow")
    if int(site.get("prior_studies_completed", 0) or 0) == 0:
        score -= 15
        gaps.append("no completed prior studies — no track record to discount against")
    competing = int(site.get("competing_studies", 0) or 0)
    if competing >= 3:
        score -= 20
        gaps.append(f"{competing} competing studies contending for the same patients")
    elif competing == 2:
        score -= 10
        gaps.append("2 competing studies")
    return max(score, 0), gaps


def project_site(site: dict[str, Any], window_months: float) -> dict[str, Any]:
    """Project realistic enrolment for one site across the accrual window."""
    site_id = str(site.get("id", "?"))
    self_reported = float(site.get("self_reported_monthly_accrual", 0) or 0)
    if self_reported < 0:
        raise ValueError(f"site {site_id}: self_reported_monthly_accrual is negative")

    attainment = site.get("prior_accrual_attainment")
    if attainment is None:
        attainment = NAIVE_SITE_ATTAINMENT
        attainment_basis = "no track record — default applied"
    else:
        attainment = float(attainment)
        if not 0 <= attainment <= 2:
            raise ValueError(f"site {site_id}: prior_accrual_attainment must be in [0, 2]")
        attainment_basis = "prior attainment"

    # Blend the discounted self-report with the site's own historical attainment.
    discounted = self_reported * OPTIMISM_DISCOUNT
    projected_rate = discounted * (0.5 + 0.5 * min(attainment, 1.5))

    competing = int(site.get("competing_studies", 0) or 0)
    projected_rate *= max(1 - COMPETING_STUDY_PENALTY * competing, 0.2)

    # An eligible-population ceiling: a site cannot enrol faster than patients
    # present, and a screening-to-enrolment yield above 25%/year is optimistic.
    annual_eligible = float(site.get("annual_eligible_patients", 0) or 0)
    if annual_eligible > 0:
        ceiling = annual_eligible * 0.25 / 12
        capped = projected_rate > ceiling
        projected_rate = min(projected_rate, ceiling)
    else:
        capped = False

    startup = float(site.get("startup_months", 0) or 0)
    active_months = max(window_months - startup, 0)
    projected_total = projected_rate * active_months
    readiness, gaps = _readiness(site)

    return {
        "id": site_id,
        "name": site.get("name", ""),
        "country": site.get("country", ""),
        "self_reported_monthly": round(self_reported, 2),
        "projected_monthly": round(projected_rate, 2),
        "attainment_basis": attainment_basis,
        "startup_months": startup,
        "active_months": round(active_months, 1),
        "projected_enrolment": round(projected_total, 1),
        "readiness_score": readiness,
        "population_capped": capped,
        "gaps": gaps,
    }


def analyse(payload: dict[str, Any], select: int | None = None) -> dict[str, Any]:
    """Project every site, rank them, and test the enrolment plan."""
    sites = payload.get("sites") or []
    if not sites:
        raise ValueError("payload must contain a non-empty 'sites' list")
    window = float(payload.get("accrual_window_months", 0) or 0)
    if window <= 0:
        raise ValueError("accrual_window_months must be a positive number")
    target = float(payload.get("enrolment_target", 0) or 0)
    if target <= 0:
        raise ValueError("enrolment_target must be a positive number")

    projected = [project_site(s, window) for s in sites]
    # Rank by projected enrolment, then readiness as the tie-break.
    projected.sort(key=lambda s: (-s["projected_enrolment"], -s["readiness_score"]))

    chosen = projected[:select] if select else projected
    total = sum(s["projected_enrolment"] for s in chosen)
    shortfall = target - total

    findings: list[str] = []
    if shortfall > 0:
        findings.append(f"projected shortfall of {shortfall:.0f} participants "
                        f"({shortfall / target:.0%} of target) — add sites, extend "
                        "the window, or relax eligibility")
    else:
        findings.append(f"projected surplus of {-shortfall:.0f} participants "
                        f"({-shortfall / target:.0%} over target)")

    weak = [s["id"] for s in chosen if s["readiness_score"] < 60]
    if weak:
        findings.append(f"low-readiness sites in the selected set: {weak} — each "
                        "needs a remediation plan before activation")
    non_enrolling = [s["id"] for s in chosen if s["projected_enrolment"] < 3]
    if non_enrolling:
        findings.append(f"sites projected under 3 participants: {non_enrolling} — "
                        "activation cost typically exceeds their contribution")
    if chosen:
        top_share = chosen[0]["projected_enrolment"] / total if total else 0
        if top_share > 0.35:
            findings.append(f"{chosen[0]['id']} carries {top_share:.0%} of projected "
                            "enrolment — single-site concentration is the most common "
                            "cause of a missed accrual target")
    capped = [s["id"] for s in chosen if s["population_capped"]]
    if capped:
        findings.append(f"sites limited by eligible population rather than by their "
                        f"own estimate: {capped} — their self-reported rate is not "
                        "supported by the patient volume they reported")

    return {
        "study": payload.get("study", ""),
        "enrolment_target": target,
        "accrual_window_months": window,
        "sites_evaluated": len(projected),
        "sites_selected": len(chosen),
        "projected_enrolment": round(total, 1),
        "shortfall": round(shortfall, 1),
        "feasible": shortfall <= 0,
        "sites": chosen,
        "not_selected": [s["id"] for s in projected[len(chosen):]],
        "findings": findings,
        "disclaimer": ("Planning projection only. Discounts are heuristics from "
                       "general accrual experience, not therapeutic-area specific; "
                       "calibrate them against your own completed studies."),
    }


def render_text(report: dict[str, Any]) -> str:
    """Render the feasibility projection as human-readable text."""
    lines = [f"Site feasibility — {report['study']}",
             f"Target: {report['enrolment_target']:.0f} over "
             f"{report['accrual_window_months']:.0f} months | "
             f"Sites selected: {report['sites_selected']}/{report['sites_evaluated']}",
             f"Projected: {report['projected_enrolment']:.0f} — "
             f"{'FEASIBLE' if report['feasible'] else 'SHORTFALL'}", "",
             f"  {'ID':5} {'CTRY':5} {'SELF':>5} {'PROJ/M':>7} {'ACTIVE':>7} "
             f"{'TOTAL':>7} {'RDY':>4}  NAME"]
    for s in report["sites"]:
        lines.append(f"  {s['id']:5} {s['country']:5} {s['self_reported_monthly']:5.1f} "
                     f"{s['projected_monthly']:7.2f} {s['active_months']:7.1f} "
                     f"{s['projected_enrolment']:7.1f} {s['readiness_score']:4d}  {s['name']}")
    lines.append("")
    for s in report["sites"]:
        if s["gaps"]:
            lines.append(f"{s['id']} gaps:")
            for gap in s["gaps"]:
                lines.append(f"  - {gap}")
    if report["not_selected"]:
        lines.append("")
        lines.append("Not selected: " + ", ".join(report["not_selected"]))
    lines.append("")
    lines.append("Findings:")
    for f in report["findings"]:
        lines.append(f"  - {f}")
    lines.append("")
    lines.append(f"NOTE: {report['disclaimer']}")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Score site feasibility and test the enrolment plan.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--input", required=True, help="Path to the JSON site set")
    parser.add_argument("--select", type=int,
                        help="Evaluate only the top N sites by projected enrolment")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                        help="Output format; text is the default")
    parser.add_argument("--output", help="Write output to this file instead of stdout")
    parser.add_argument("--strict", action="store_true",
                        help="Exit non-zero if the plan is projected to fall short")
    return parser.parse_args()


def main() -> int:
    """CLI entry point."""
    args = parse_args()
    try:
        payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
        report = analyse(payload, args.select)
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
        print(f"error: invalid site set: {exc}", file=sys.stderr)
        return 1

    if args.strict and not report["feasible"]:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
