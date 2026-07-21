#!/usr/bin/env python3
"""Build a sequenced internal communication plan from a change description.

Usage:
    python3 comms_sequencer.py --input change.json [--format text|json]

Input JSON shape:
    {"change": {"name": "...", "type": "reorg", "reversible": false,
                "embargoed": false, "effective_date": "2026-09-01"},
     "audiences": [{"name": "Platform team", "impact": "high",
                    "headcount": 24, "role": "ic"}]}
"""

import argparse
import json
import sys
from typing import Any, Dict, List

IMPACT_WEIGHT = {"high": 1.0, "medium": 0.4, "low": 0.05}

# Lower rank number = briefed earlier.
ROLE_RANK = {
    "exec": 0,
    "manager": 1,
    "customer-facing": 2,
    "ic": 3,
    "external": 4,
}

# Change types that must never carry an open feedback window.
IRREVERSIBLE_TYPES = {"reorg", "layoff", "shutdown", "acquisition", "leadership-change"}


def blast_radius(audiences: List[Dict[str, Any]]) -> int:
    """Return the count of people whose work or employment materially changes."""
    total = 0.0
    for aud in audiences:
        weight = IMPACT_WEIGHT.get(str(aud.get("impact", "low")).lower(), 0.05)
        total += weight * float(aud.get("headcount", 0))
    return int(round(total))


def radius_band(radius: int) -> Dict[str, Any]:
    """Map a blast radius to its sequencing pattern, lead time, and enablement need."""
    if radius <= 10:
        return {"band": "1-10", "lead_days": 0, "manager_enablement": False,
                "pattern": "Direct 1:1 conversations, then a quiet team note"}
    if radius <= 50:
        return {"band": "11-50", "lead_days": 2, "manager_enablement": True,
                "pattern": "Manager brief -> team meetings -> written follow-up"}
    if radius <= 250:
        return {"band": "51-250", "lead_days": 4, "manager_enablement": True,
                "pattern": "Exec brief -> manager brief + FAQ -> all-hands -> written"}
    return {"band": "250+", "lead_days": 7, "manager_enablement": True,
            "pattern": "Influencer pre-brief -> exec -> manager -> all-hands -> 2-week reinforcement"}


def order_audiences(audiences: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Order audiences by role rank first, then by impact weight descending."""
    def key(aud: Dict[str, Any]) -> Any:
        role = str(aud.get("role", "ic")).lower()
        impact = str(aud.get("impact", "low")).lower()
        return (ROLE_RANK.get(role, 3), -IMPACT_WEIGHT.get(impact, 0.05),
                str(aud.get("name", "")))
    return sorted(audiences, key=key)


def build_sequence(change: Dict[str, Any],
                   audiences: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Produce the ordered communication steps with T-offsets in days."""
    radius = blast_radius(audiences)
    band = radius_band(radius)
    embargoed = bool(change.get("embargoed", False))
    lead = 0 if embargoed else band["lead_days"]
    steps: List[Dict[str, Any]] = []

    if embargoed:
        steps.append({
            "offset_days": 0,
            "step": "Simultaneous broadcast (embargo)",
            "audience": "all affected groups at once",
            "channel": "email + all-hands same hour",
            "note": "Embargo forbids cascade. State in the message that managers "
                    "could not be briefed first, and why.",
        })
    else:
        offset = -lead
        for aud in order_audiences(audiences):
            role = str(aud.get("role", "ic")).lower()
            impact = str(aud.get("impact", "low")).lower()
            if role == "exec":
                step_offset, channel = offset, "small-group briefing"
            elif role == "manager":
                step_offset = offset + max(lead - 2, 0)
                channel = "manager brief + talk track + FAQ"
            elif role == "customer-facing":
                step_offset = offset + max(lead - 1, 0)
                channel = "team session + holding statement"
            elif role == "external":
                step_offset, channel = 1, "partner note / customer email"
            else:
                step_offset, channel = 0, "all-hands then written broadcast"
            steps.append({
                "offset_days": step_offset,
                "step": f"Brief {aud.get('name', 'audience')}",
                "audience": f"{aud.get('name', 'audience')} "
                            f"({aud.get('headcount', 0)} people, {impact} impact)",
                "channel": channel,
                "note": "High-impact group: deliver live, not in writing first."
                        if impact == "high" else "Written delivery is sufficient.",
            })

    if band["manager_enablement"] and not embargoed:
        steps.append({
            "offset_days": -max(lead - 2, 1),
            "step": "Manager enablement session",
            "audience": "all people managers in scope",
            "channel": "60-min live session + written FAQ",
            "note": "Cover the talk track, what may and may not be repeated, "
                    "and the three questions they will be asked first.",
        })

    steps.extend([
        {"offset_days": 3, "step": "FAQ update", "audience": "all recipients",
         "channel": "shared doc + link in original thread",
         "note": "Publish the real questions asked, not the anticipated ones."},
        {"offset_days": 7, "step": "Manager check-in", "audience": "people managers",
         "channel": "existing manager forum",
         "note": "Surface where the message did not land."},
        {"offset_days": 14, "step": "Progress note", "audience": "all recipients",
         "channel": "written, short", "note": "Under 150 words. What has happened since."},
        {"offset_days": 28, "step": "Close-out", "audience": "all recipients",
         "channel": "written", "note": "Confirm the change is done and retire the FAQ."},
    ])
    return sorted(steps, key=lambda s: s["offset_days"])


def plan(data: Dict[str, Any]) -> Dict[str, Any]:
    """Assemble the full communication plan from the input payload."""
    change = data.get("change")
    audiences = data.get("audiences")
    if not isinstance(change, dict):
        raise ValueError("input JSON must contain a 'change' object")
    if not isinstance(audiences, list) or not audiences:
        raise ValueError("input JSON must contain a non-empty 'audiences' array")

    radius = blast_radius(audiences)
    band = radius_band(radius)
    ctype = str(change.get("type", "")).lower()
    reversible = bool(change.get("reversible", False))
    feedback = "none - do not solicit input on a settled decision"
    if reversible and ctype not in IRREVERSIBLE_TYPES:
        feedback = "5-10 business days, scoped to what is genuinely still open"

    warnings: List[str] = []
    if reversible and ctype in IRREVERSIBLE_TYPES:
        warnings.append(
            f"change.type '{ctype}' is marked reversible; treat as irreversible for comms "
            "purposes and remove any feedback invitation")
    if bool(change.get("embargoed")) and band["manager_enablement"]:
        warnings.append(
            "embargo removes the manager-first cascade this blast radius would normally require")
    if not change.get("effective_date"):
        warnings.append("no effective_date supplied; the message cannot satisfy 'what changed'")

    return {
        "change": change.get("name", "(unnamed change)"),
        "type": ctype or "unspecified",
        "effective_date": change.get("effective_date", "unspecified"),
        "total_recipients": sum(int(a.get("headcount", 0)) for a in audiences),
        "blast_radius": radius,
        "radius_band": band["band"],
        "pattern": band["pattern"],
        "lead_days": 0 if change.get("embargoed") else band["lead_days"],
        "manager_enablement_required": band["manager_enablement"],
        "feedback_window": feedback,
        "warnings": warnings,
        "sequence": build_sequence(change, audiences),
    }


def output(result: Dict[str, Any], fmt: str) -> None:
    """Print the plan as JSON or human-readable text."""
    if fmt == "json":
        print(json.dumps(result, indent=2))
        return

    print(f"Communication plan: {result['change']}  [{result['type']}]")
    print(f"  effective {result['effective_date']}")
    print(f"  recipients={result['total_recipients']}  blast radius={result['blast_radius']} "
          f"(band {result['radius_band']})")
    print(f"  pattern: {result['pattern']}")
    print(f"  lead time before broadcast: {result['lead_days']} day(s)")
    print(f"  manager enablement: "
          f"{'REQUIRED' if result['manager_enablement_required'] else 'not needed'}")
    print(f"  feedback window: {result['feedback_window']}")
    if result["warnings"]:
        print("\nWarnings:")
        for w in result["warnings"]:
            print(f"  ! {w}")
    print("\nSequence (T = broadcast day):")
    for step in result["sequence"]:
        off = step["offset_days"]
        label = f"T{off:+d}" if off else "T+0"
        print(f"  {label:>5}  {step['step']}")
        print(f"         audience: {step['audience']}")
        print(f"         channel:  {step['channel']}")
        print(f"         note:     {step['note']}")


def main() -> None:
    """Parse arguments, build the plan, and emit it."""
    parser = argparse.ArgumentParser(
        description="Sequence an internal change communication by audience and blast radius.")
    parser.add_argument("--input", required=True,
                        help="Path to a JSON file with 'change' and 'audiences'")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                        help="Output format (default: text)")
    args = parser.parse_args()

    try:
        with open(args.input, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except FileNotFoundError:
        print(f"Error: input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as exc:
        print(f"Error: {args.input} is not valid JSON ({exc})", file=sys.stderr)
        sys.exit(1)

    try:
        result = plan(data)
    except (ValueError, TypeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    output(result, args.format)


if __name__ == "__main__":
    main()
