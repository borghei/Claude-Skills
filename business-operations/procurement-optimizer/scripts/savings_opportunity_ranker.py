#!/usr/bin/env python3
"""Rank SaaS savings opportunities by value, effort, and renewal-timing leverage.

Usage:
    python3 savings_opportunity_ranker.py --input spend.json --as-of 2026-07-21
                                          [--top 10] [--format text|json]

Input JSON shape: the same dataset consumed by license_utilization_analyzer.py,
with 'renewal_date', 'notice_period_days', 'auto_renew', and 'term_months'.
"""

import argparse
import json
import sys
from datetime import date, datetime
from typing import Any, Dict, List

CATEGORY_BENCHMARK: Dict[str, float] = {
    "crm": 0.85, "chat": 0.85, "collaboration": 0.85, "developer-tools": 0.80,
    "security": 0.90, "support": 0.85, "product-analytics": 0.60, "design": 0.70,
    "finance": 0.80, "knowledge-base": 0.50, "legal": 0.55, "whiteboard": 0.40,
    "hr": 0.40,
}
DEFAULT_BENCHMARK = 0.70
SAFETY_BUFFER = 1.12

# Days before renewal at which each negotiation phase opens.
NEGOTIATION_OPEN = 120
NEGOTIATION_IDEAL = 90


def parse_date(value: str, field: str) -> date:
    """Parse an ISO-8601 date string, raising a clear error on bad input."""
    try:
        return datetime.strptime(str(value).strip(), "%Y-%m-%d").date()
    except (ValueError, TypeError):
        raise ValueError(f"{field} must be an ISO date (YYYY-MM-DD), got: {value!r}")


def renewal_window(tool: Dict[str, Any], as_of: date) -> Dict[str, Any]:
    """Classify where a contract sits relative to its notice and negotiation windows."""
    raw = str(tool.get("renewal_date", "")).strip()
    if not raw:
        return {"days_to_renewal": None, "phase": "unknown",
                "leverage": 0.3, "note": "No renewal date recorded - find it first."}

    days = (parse_date(raw, f"{tool.get('name', '?')} renewal_date") - as_of).days
    notice = int(tool.get("notice_period_days", 30) or 30)
    auto = bool(tool.get("auto_renew", True))

    if days < 0:
        return {"days_to_renewal": days, "phase": "lapsed",
                "leverage": 0.2,
                "note": "Renewal date has passed. Confirm what you are now committed to."}
    if auto and days <= notice:
        return {"days_to_renewal": days, "phase": "locked",
                "leverage": 0.1,
                "note": (f"Inside the {notice}-day notice window on an auto-renewing "
                         "contract. This term is committed - plan for the next one.")}
    if days <= notice + 15:
        return {"days_to_renewal": days, "phase": "urgent",
                "leverage": 0.5,
                "note": (f"Notice deadline in {days - notice} day(s). Serve notice now "
                         "to preserve optionality, even if you intend to renew.")}
    if days <= NEGOTIATION_IDEAL:
        return {"days_to_renewal": days, "phase": "late",
                "leverage": 0.7,
                "note": "Negotiating late. Expect to trade term length for price."}
    if days <= NEGOTIATION_OPEN:
        return {"days_to_renewal": days, "phase": "ideal",
                "leverage": 1.0,
                "note": "Ideal negotiation window. Open the conversation this week."}
    return {"days_to_renewal": days, "phase": "early",
            "leverage": 0.6,
            "note": f"Too early to negotiate. Calendar the opening at T-{NEGOTIATION_OPEN} days."}


def seat_opportunity(tool: Dict[str, Any]) -> Dict[str, Any]:
    """Size the seat-reduction opportunity for one tool."""
    purchased = int(tool.get("seats_purchased", 0) or 0)
    if purchased <= 0:
        raise ValueError(f"{tool.get('name', '?')}: seats_purchased must be > 0")
    active = int(tool.get("seats_active_30d", 0) or 0)
    cost = float(tool.get("annual_cost", 0) or 0)
    category = str(tool.get("category", "other")).lower()
    benchmark = CATEGORY_BENCHMARK.get(category, DEFAULT_BENCHMARK)
    util = active / purchased

    if util >= benchmark:
        return {"kind": "price-only", "value": round(cost * 0.08, 2), "effort_days": 3.0,
                "detail": ("Utilisation is healthy. Pursue an 8% price concession, "
                           "not a volume cut.")}

    recommended = min(max(int(active * SAFETY_BUFFER + 0.999), 1), purchased)
    reclaimable = purchased - recommended
    value = round(reclaimable * (cost / purchased), 2)
    effort = 2.0 if reclaimable < 30 else 5.0
    return {"kind": "seat-reduction", "value": value, "effort_days": effort,
            "detail": (f"Cut {reclaimable} of {purchased} seats to ~{recommended} "
                       f"(active {active}, utilisation {util:.0%} vs {benchmark:.0%} "
                       "benchmark).")}


def rank(payload: Dict[str, Any], as_of: date, top: int) -> Dict[str, Any]:
    """Rank every savings opportunity by risk-adjusted value per unit of effort."""
    tools = payload.get("tools")
    if not isinstance(tools, list) or not tools:
        raise ValueError("input JSON must contain a non-empty 'tools' array")

    opportunities: List[Dict[str, Any]] = []
    for tool in tools:
        window = renewal_window(tool, as_of)
        opp = seat_opportunity(tool)
        # Leverage discounts value: a saving you cannot act on this cycle is
        # worth less than the same saving inside the negotiation window.
        realisable = round(opp["value"] * window["leverage"], 2)
        opportunities.append({
            "tool": tool.get("name", "(unnamed)"),
            "category": tool.get("category", "other"),
            "criticality": tool.get("criticality", "core"),
            "annual_cost": round(float(tool.get("annual_cost", 0) or 0), 2),
            "opportunity": opp["kind"],
            "gross_annual_value": opp["value"],
            "realisable_this_cycle": realisable,
            "effort_days": opp["effort_days"],
            "roi_per_day": round(realisable / opp["effort_days"], 2) if opp["effort_days"] else 0.0,
            "renewal_phase": window["phase"],
            "days_to_renewal": window["days_to_renewal"],
            "leverage": window["leverage"],
            "detail": opp["detail"],
            "timing_note": window["note"],
        })

    def sort_key(opp: Dict[str, Any]) -> Any:
        # Contracts inside their notice or ideal negotiation window are
        # time-boxed: missing the window costs a full contract year, so they
        # outrank a better ROI on a renewal that is nine months away.
        timeboxed = 0 if opp["renewal_phase"] in ("urgent", "ideal") else 1
        return (timeboxed, -opp["roi_per_day"], -opp["realisable_this_cycle"], opp["tool"])

    opportunities.sort(key=sort_key)
    shortlist = opportunities[:max(top, 1)]

    calendar = sorted(
        [o for o in opportunities if o["days_to_renewal"] is not None],
        key=lambda o: o["days_to_renewal"])
    act_now = [o for o in opportunities if o["renewal_phase"] in ("urgent", "ideal")]
    locked = [o for o in opportunities if o["renewal_phase"] == "locked"]

    return {
        "as_of": as_of.isoformat(),
        "currency": payload.get("currency", "USD"),
        "total_annual_spend": round(sum(o["annual_cost"] for o in opportunities), 2),
        "gross_annual_opportunity": round(sum(o["gross_annual_value"] for o in opportunities), 2),
        "realisable_this_cycle": round(sum(o["realisable_this_cycle"] for o in opportunities), 2),
        "locked_this_cycle": round(sum(o["gross_annual_value"] for o in locked), 2),
        "total_effort_days": round(sum(o["effort_days"] for o in opportunities), 1),
        "act_now_count": len(act_now),
        "shortlist": shortlist,
        "shortlist_value": round(sum(o["realisable_this_cycle"] for o in shortlist), 2),
        "shortlist_effort_days": round(sum(o["effort_days"] for o in shortlist), 1),
        "renewal_calendar": [
            {"tool": o["tool"], "days_to_renewal": o["days_to_renewal"],
             "phase": o["renewal_phase"], "note": o["timing_note"]}
            for o in calendar],
    }


def output(result: Dict[str, Any], fmt: str) -> None:
    """Print the ranked opportunities as JSON or human-readable text."""
    if fmt == "json":
        print(json.dumps(result, indent=2))
        return

    cur = result["currency"]
    print(f"Savings opportunities as of {result['as_of']}")
    print(f"  spend              {cur} {result['total_annual_spend']:>12,.0f}")
    print(f"  gross opportunity  {cur} {result['gross_annual_opportunity']:>12,.0f}")
    print(f"  realisable now     {cur} {result['realisable_this_cycle']:>12,.0f}")
    print(f"  locked this cycle  {cur} {result['locked_this_cycle']:>12,.0f} "
          "(inside notice window on auto-renew)")
    print(f"  {result['act_now_count']} contract(s) in an urgent or ideal negotiation window")

    print(f"\nShortlist ({len(result['shortlist'])} items, "
          f"{cur} {result['shortlist_value']:,.0f}, "
          f"{result['shortlist_effort_days']} days effort):")
    for i, opp in enumerate(result["shortlist"], 1):
        days = opp["days_to_renewal"]
        days_s = f"T-{days}d" if days is not None else "no date"
        print(f"  {i:>2}. {opp['tool']} [{opp['category']}] - {opp['opportunity']}")
        print(f"      {cur} {opp['realisable_this_cycle']:,.0f} realisable of "
              f"{cur} {opp['gross_annual_value']:,.0f} gross | "
              f"{opp['effort_days']}d effort | {opp['roi_per_day']:,.0f}/day")
        print(f"      renewal {days_s} ({opp['renewal_phase']}, leverage {opp['leverage']})")
        print(f"      {opp['detail']}")
        print(f"      {opp['timing_note']}")

    print("\nRenewal calendar:")
    for entry in result["renewal_calendar"]:
        print(f"  T-{entry['days_to_renewal']:<5}d  [{entry['phase']:>8}]  {entry['tool']}")


def main() -> None:
    """Parse arguments, rank the opportunities, and emit the report."""
    parser = argparse.ArgumentParser(
        description="Rank SaaS savings opportunities by value, effort, and renewal timing.")
    parser.add_argument("--input", required=True,
                        help="Path to a JSON file with a 'tools' array including renewal fields")
    parser.add_argument("--as-of", required=True,
                        help="Reference date as YYYY-MM-DD; required so runs are reproducible")
    parser.add_argument("--top", type=int, default=10,
                        help="How many opportunities to shortlist (default: 10)")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                        help="Output format (default: text)")
    args = parser.parse_args()

    try:
        with open(args.input, "r", encoding="utf-8") as fh:
            payload = json.load(fh)
    except FileNotFoundError:
        print(f"Error: input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as exc:
        print(f"Error: {args.input} is not valid JSON ({exc})", file=sys.stderr)
        sys.exit(1)

    try:
        result = rank(payload, parse_date(args.as_of, "--as-of"), args.top)
    except (ValueError, TypeError, ZeroDivisionError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    output(result, args.format)


if __name__ == "__main__":
    main()
