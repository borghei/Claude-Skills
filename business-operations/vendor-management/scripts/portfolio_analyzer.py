#!/usr/bin/env python3
"""Analyse a vendor portfolio for renewal risk, spend concentration and risk tier.

Computes days to each renewal and notice deadline, flags contracts about to
auto-renew unchallenged, derives risk tiers from data sensitivity and business
criticality, measures concentration with a Herfindahl index, and identifies
consolidation candidates.

Usage:
    python3 portfolio_analyzer.py --input sample_portfolio.json --format json
"""

import argparse
import json
import sys
from datetime import date
from pathlib import Path
from typing import Any, Dict, List

# Risk contributions. Data sensitivity and business criticality dominate because
# they determine blast radius, not spend.
DATA_RISK = {"pii": 3, "phi": 4, "financial": 3, "confidential": 2, "internal": 1, "public": 0}
CRITICALITY_RISK = {"critical": 4, "high": 3, "medium": 2, "low": 1}

# Renewal windows in days.
NOTICE_URGENT_DAYS = 30
RENEWAL_HORIZON_DAYS = 120

# Herfindahl-Hirschman index thresholds on category spend share.
HHI_CONCENTRATED = 2500
HHI_MODERATE = 1500

# A category with this many vendors is a consolidation candidate.
CONSOLIDATION_VENDOR_COUNT = 3


def risk_tier(vendor: Dict[str, Any]) -> Dict[str, Any]:
    """Derive a risk tier from data sensitivity, criticality and substitutability."""
    data_class = str(vendor.get("data_classification", "internal")).lower()
    criticality = str(vendor.get("business_criticality", "medium")).lower()
    if data_class not in DATA_RISK:
        raise ValueError(
            f"vendor '{vendor.get('name')}' has data_classification '{data_class}'; "
            f"expected one of {sorted(DATA_RISK)}"
        )
    if criticality not in CRITICALITY_RISK:
        raise ValueError(
            f"vendor '{vendor.get('name')}' has business_criticality '{criticality}'; "
            f"expected one of {sorted(CRITICALITY_RISK)}"
        )

    score = DATA_RISK[data_class] + CRITICALITY_RISK[criticality]
    drivers = [f"data: {data_class}", f"criticality: {criticality}"]
    if not vendor.get("has_alternative", True):
        score += 2
        drivers.append("no ready alternative")
    if vendor.get("subprocessors", False):
        score += 1
        drivers.append("uses subprocessors")

    tier = (
        "TIER 1 (critical)" if score >= 8
        else "TIER 2 (high)" if score >= 6
        else "TIER 3 (moderate)" if score >= 4
        else "TIER 4 (low)"
    )
    return {"tier": tier, "risk_score": score, "risk_drivers": drivers}


def renewal_status(vendor: Dict[str, Any], as_of: date) -> Dict[str, Any]:
    """Compute days to renewal and to the notice deadline, with an action flag."""
    raw = vendor.get("renewal_date")
    if not raw:
        raise ValueError(f"vendor '{vendor.get('name')}' is missing 'renewal_date'")
    try:
        renewal = date.fromisoformat(str(raw))
    except ValueError as exc:
        raise ValueError(
            f"vendor '{vendor.get('name')}' has renewal_date '{raw}'; expected YYYY-MM-DD"
        ) from exc

    notice_days = int(vendor.get("notice_days", 0))
    days_to_renewal = (renewal - as_of).days
    days_to_notice = days_to_renewal - notice_days
    auto_renew = bool(vendor.get("auto_renew", False))

    action = (
        "LOCKED — notice window missed, auto-renews" if days_to_notice < 0 and auto_renew
        else "EXPIRED NOTICE — renegotiate or expect lapse" if days_to_notice < 0
        else f"ACT NOW — {days_to_notice}d to notice deadline"
        if days_to_notice <= NOTICE_URGENT_DAYS
        else "PREPARE — inside renewal horizon" if days_to_renewal <= RENEWAL_HORIZON_DAYS
        else "monitor"
    )

    return {
        "renewal_date": str(renewal),
        "days_to_renewal": days_to_renewal,
        "notice_days": notice_days,
        "days_to_notice_deadline": days_to_notice,
        "auto_renew": auto_renew,
        "action": action,
    }


def concentration(vendors: List[Dict[str, Any]], total: float) -> Dict[str, Any]:
    """Compute spend shares and a Herfindahl-Hirschman index by category."""
    by_category: Dict[str, Dict[str, Any]] = {}
    for v in vendors:
        cat = v.get("category", "uncategorised")
        bucket = by_category.setdefault(cat, {"spend": 0.0, "vendors": []})
        bucket["spend"] += v["annual_spend"]
        bucket["vendors"].append(v["name"])

    hhi = 0.0
    for bucket in by_category.values():
        share = bucket["spend"] / total if total else 0.0
        bucket["share"] = round(share, 3)
        bucket["spend"] = round(bucket["spend"], 0)
        bucket["vendor_count"] = len(bucket["vendors"])
        hhi += (share * 100) ** 2

    band = (
        "CONCENTRATED" if hhi >= HHI_CONCENTRATED
        else "MODERATE" if hhi >= HHI_MODERATE
        else "DIVERSE"
    )
    return {"by_category": by_category, "hhi": round(hhi, 0), "band": band}


def analyse(data: Dict[str, Any]) -> Dict[str, Any]:
    """Produce the full portfolio analysis as of the supplied date."""
    raw_vendors = data.get("vendors", [])
    if not raw_vendors:
        raise ValueError("input JSON needs a non-empty 'vendors' array")
    as_of_raw = data.get("as_of")
    if not as_of_raw:
        raise ValueError("input JSON needs an 'as_of' date (YYYY-MM-DD) so results are reproducible")
    try:
        as_of = date.fromisoformat(str(as_of_raw))
    except ValueError as exc:
        raise ValueError(f"'as_of' is '{as_of_raw}'; expected YYYY-MM-DD") from exc

    vendors: List[Dict[str, Any]] = []
    for v in raw_vendors:
        spend = float(v.get("annual_spend", 0))
        if spend < 0:
            raise ValueError(f"vendor '{v.get('name')}' has negative annual_spend")
        record = {"name": v.get("name", "unnamed"), "annual_spend": spend,
                  "category": v.get("category", "uncategorised"),
                  "owner": v.get("owner", "unassigned")}
        record.update(risk_tier(v))
        record.update(renewal_status(v, as_of))
        vendors.append(record)

    total = sum(v["annual_spend"] for v in vendors)
    for v in vendors:
        v["spend_share"] = round(v["annual_spend"] / total, 3) if total else 0.0

    conc = concentration(vendors, total)

    consolidation = [
        {
            "category": cat,
            "vendor_count": b["vendor_count"],
            "combined_spend": b["spend"],
            "vendors": b["vendors"],
        }
        for cat, b in conc["by_category"].items()
        if b["vendor_count"] >= CONSOLIDATION_VENDOR_COUNT
    ]
    consolidation.sort(key=lambda c: -c["combined_spend"])

    urgent = [v for v in vendors if v["action"].startswith(("ACT NOW", "LOCKED", "EXPIRED"))]
    upcoming = sorted(
        [v for v in vendors if 0 <= v["days_to_renewal"] <= RENEWAL_HORIZON_DAYS],
        key=lambda v: v["days_to_renewal"],
    )

    findings: List[str] = [
        f"{v['name']}: {v['action']} ({v['annual_spend']:,.0f}/year)." for v in urgent
    ]
    top = max(vendors, key=lambda v: v["annual_spend"])
    if top["spend_share"] > 0.25:
        findings.append(
            f"{top['name']} is {top['spend_share']:.0%} of total vendor spend. Single-vendor "
            "concentration at this level is a negotiating weakness and a continuity risk."
        )
    if conc["band"] == "CONCENTRATED":
        findings.append(
            f"Category spend is concentrated (HHI {conc['hhi']:.0f}). "
            "Leverage is high within categories but so is switching cost."
        )
    findings.extend(
        f"Consolidation candidate: {c['vendor_count']} vendors in '{c['category']}' "
        f"totalling {c['combined_spend']:,.0f}/year — {', '.join(c['vendors'])}."
        for c in consolidation
    )
    tier1 = [v["name"] for v in vendors if v["tier"].startswith("TIER 1")]
    if tier1:
        findings.append(
            f"{len(tier1)} Tier 1 vendor(s) requiring annual security review and a tested "
            f"exit plan: {', '.join(tier1)}."
        )
    unowned = [v["name"] for v in vendors if v["owner"] == "unassigned"]
    if unowned:
        findings.append(
            f"No internal owner assigned: {', '.join(unowned)}. "
            "Unowned contracts are the ones that auto-renew."
        )

    tier_counts: Dict[str, int] = {}
    for v in vendors:
        tier_counts[v["tier"]] = tier_counts.get(v["tier"], 0) + 1

    return {
        "as_of": str(as_of),
        "vendor_count": len(vendors),
        "total_annual_spend": round(total, 0),
        "vendors": sorted(vendors, key=lambda v: -v["annual_spend"]),
        "tier_counts": tier_counts,
        "concentration": conc,
        "consolidation_candidates": consolidation,
        "renewals_in_horizon": [
            {"name": v["name"], "days_to_renewal": v["days_to_renewal"], "action": v["action"]}
            for v in upcoming
        ],
        "findings": findings,
    }


def output(result: Dict[str, Any], fmt: str) -> None:
    """Print the portfolio analysis as JSON or a human-readable report."""
    if fmt == "json":
        print(json.dumps(result, indent=2))
        return

    print(f"VENDOR PORTFOLIO — as of {result['as_of']}")
    print("=" * 84)
    print(
        f"{result['vendor_count']} vendors | {result['total_annual_spend']:,.0f} annual spend | "
        f"concentration {result['concentration']['band']} (HHI {result['concentration']['hhi']:.0f})"
    )
    print()
    print(f"{'Vendor':<24}{'Category':<14}{'Annual':>12}{'Share':>7}  {'Tier':<18}Renewal")
    print("-" * 84)
    for v in result["vendors"]:
        print(
            f"{v['name'][:23]:<24}{v['category'][:13]:<14}{v['annual_spend']:>12,.0f}"
            f"{v['spend_share']:>7.0%}  {v['tier']:<18}{v['days_to_renewal']:>4}d"
        )
    print("-" * 84)
    print()
    print("RISK TIERS: " + " | ".join(f"{t} {c}" for t, c in sorted(result["tier_counts"].items())))
    print()
    print("RENEWALS IN HORIZON")
    for r in result["renewals_in_horizon"] or []:
        print(f"  {r['name'][:26]:<28}{r['days_to_renewal']:>4}d   {r['action']}")
    if not result["renewals_in_horizon"]:
        print("  none within the horizon")
    if result["findings"]:
        print()
        print("FINDINGS")
        for f in result["findings"]:
            print(f"  ! {f}")


def main() -> None:
    """Parse arguments, run the portfolio analysis, and print the result."""
    parser = argparse.ArgumentParser(
        description="Analyse a vendor portfolio for renewal risk, concentration and risk tier.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to a portfolio JSON file (see assets/sample_portfolio.json)",
    )
    parser.add_argument(
        "--format", choices=["text", "json"], default="text", help="Output format"
    )
    args = parser.parse_args()

    try:
        data = json.loads(Path(args.input).read_text(encoding="utf-8"))
        output(analyse(data), args.format)
    except FileNotFoundError:
        print(f"Error: input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as exc:
        print(f"Error: {args.input} is not valid JSON ({exc})", file=sys.stderr)
        sys.exit(1)
    except (ValueError, KeyError, TypeError) as exc:
        print(f"Error: could not analyse portfolio — {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
