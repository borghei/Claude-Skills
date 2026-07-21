#!/usr/bin/env python3
"""Route each pending communication to sync, async or a written decision record.

Usage:
    python3 channel_router.py --input sample_messages.json
    python3 channel_router.py --input sample_messages.json --format json
    python3 channel_router.py --input sample_messages.json --core-overlap-hours 3
"""

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Tuple

CHANNELS = {
    "written_decision": "Written decision record (doc + named approver + comment deadline)",
    "async_thread": "Async thread (Slack/Teams channel or issue comment)",
    "sync_meeting": "Live meeting (agenda + pre-read + notes)",
    "sync_1on1": "Live 1:1 or small private call",
    "broadcast": "One-way broadcast (email, all-hands, changelog)",
}
# An async round-trip across N timezones costs roughly this many hours of wall-clock latency.
ASYNC_ROUND_TRIP_HOURS = 18


def load_messages(path: Path) -> List[Dict[str, Any]]:
    """Read and validate the pending-message list."""
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise SystemExit(f"error: file not found: {path}")
    except json.JSONDecodeError as exc:
        raise SystemExit(f"error: {path} is not valid JSON ({exc.msg}, line {exc.lineno})")
    messages = doc.get("messages") if isinstance(doc, dict) else doc
    if not isinstance(messages, list) or not messages:
        raise SystemExit("error: expected a non-empty 'messages' list")
    return messages


def route(msg: Dict[str, Any], core_overlap: float) -> Tuple[str, List[str], str]:
    """Pick a channel for one message and return (channel, reasons, urgency band)."""
    reasons: List[str] = []
    reversibility = msg.get("reversibility", "two_way")
    stakeholders = int(msg.get("stakeholders", 1))
    needs_decision = bool(msg.get("needs_decision", False))
    urgency = float(msg.get("urgency_hours", 72))
    context = msg.get("context_shared", "medium")
    emotional = msg.get("emotional_load", "low")
    timezones = int(msg.get("timezones_spanned", 1))

    band = "same-day" if urgency <= 8 else "this-week" if urgency <= 72 else "scheduled"

    if emotional == "high" or msg.get("personal", False):
        reasons.append("high emotional load — tone does not survive text")
        return "sync_1on1", reasons, band

    if needs_decision and reversibility == "one_way":
        reasons.append("irreversible decision — needs a durable record and a named approver")
        if stakeholders >= 4 and context == "low":
            reasons.append(f"{stakeholders} stakeholders with little shared context")
            return "sync_meeting", reasons, band
        return "written_decision", reasons, band

    if not needs_decision and stakeholders >= 8:
        reasons.append(f"informational to {stakeholders} people — no decision to make")
        return "broadcast", reasons, band

    if context == "low" and needs_decision:
        reasons.append("low shared context — async will burn several round trips")
        return "sync_meeting", reasons, band

    if needs_decision and urgency <= 8:
        reasons.append(f"decision needed within {urgency:g}h — faster than one async round trip")
        return "sync_meeting", reasons, band

    if urgency <= ASYNC_ROUND_TRIP_HOURS and timezones >= 3 and core_overlap < 2:
        reasons.append(f"needed in {urgency:g}h across {timezones} timezones with "
                       f"{core_overlap:g}h overlap — async cannot land in time")
        return "sync_meeting", reasons, band

    if needs_decision and reversibility == "two_way":
        reasons.append("reversible decision — default to async and let disagreement pull it to sync")
    else:
        reasons.append("no decision required and context is shared")
    return "async_thread", reasons, band


def sla_for(band: str, channel: str) -> str:
    """Return the response SLA that applies to this urgency band and channel."""
    if channel == "broadcast":
        return "no response expected"
    table = {
        "same-day": "acknowledge within 2 working hours; resolve same day",
        "this-week": "first substantive reply within 1 working day",
        "scheduled": "reply within 3 working days; escalate on day 4",
    }
    return table[band]


def analyse(messages: List[Dict[str, Any]], core_overlap: float) -> Dict[str, Any]:
    """Route every message and summarise the resulting channel mix."""
    rows = []
    for msg in messages:
        channel, reasons, band = route(msg, core_overlap)
        rows.append({
            "id": msg.get("id", "?"),
            "summary": msg.get("summary", ""),
            "channel": channel,
            "channel_label": CHANNELS[channel],
            "urgency_band": band,
            "sla": sla_for(band, channel),
            "reasons": reasons,
        })
    mix = Counter(r["channel"] for r in rows)
    # 1:1s are excluded: they are unavoidable by design, not calendar bloat.
    sync = mix["sync_meeting"]
    return {
        "core_overlap_hours": core_overlap,
        "messages": rows,
        "mix": dict(mix),
        "sync_share_pct": round(sync / len(rows) * 100, 1),
        "verdict": (
            "Sync-heavy. More than a third of traffic is booking calendar time — "
            "tighten written context so reversible calls resolve async."
            if sync / len(rows) > 0.34 else
            "Healthy mix. Sync time is reserved for irreversible, low-context or personal calls."
        ),
    }


def output(report: Dict[str, Any], fmt: str) -> None:
    """Print the routing report as JSON or as a human-readable report."""
    if fmt == "json":
        print(json.dumps(report, indent=2))
        return
    print("COMMUNICATION CHANNEL ROUTING")
    print("=" * 62)
    print(f"Core-hours overlap: {report['core_overlap_hours']:g}h   "
          f"Sync share: {report['sync_share_pct']}%\n")
    for r in report["messages"]:
        print(f"[{r['id']}] {r['summary']}")
        print(f"     -> {r['channel_label']}")
        print(f"        urgency: {r['urgency_band']}   SLA: {r['sla']}")
        for reason in r["reasons"]:
            print(f"        why: {reason}")
        print()
    print("CHANNEL MIX")
    for channel, count in sorted(report["mix"].items(), key=lambda kv: -kv[1]):
        print(f"  {channel:<18}{count}")
    print(f"\n{report['verdict']}")


def main() -> None:
    """Parse arguments, route the pending messages and print the report."""
    parser = argparse.ArgumentParser(
        description="Route pending communications to sync, async, or a written decision record.")
    parser.add_argument("--input", required=True,
                        help="path to a JSON file with a 'messages' list")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                        help="output format (default: text)")
    parser.add_argument("--core-overlap-hours", type=float, default=3.0,
                        help="hours of shared working time across the team (default: 3)")
    args = parser.parse_args()
    try:
        messages = load_messages(Path(args.input))
        output(analyse(messages, args.core_overlap_hours), args.format)
    except SystemExit:
        raise
    except (KeyError, TypeError, ValueError) as exc:
        print(f"error: malformed message data — {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
