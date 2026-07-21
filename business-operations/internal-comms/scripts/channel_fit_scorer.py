#!/usr/bin/env python3
"""Rank internal communication channels against a message profile.

Usage:
    python3 channel_fit_scorer.py --input profile.json [--top 4] [--format text|json]

Input JSON shape (each value 1-5 unless noted):
    {"message": {"name": "...", "urgency": 4, "complexity": 3,
                 "audience_size": 800, "sensitivity": 5,
                 "needs_discussion": true, "needs_record": true}}
"""

import argparse
import json
import sys
from typing import Any, Dict, List

# Channel capability profile. Each trait scored 1-5.
#   speed        - how fast it reaches people
#   depth        - how much complexity it carries
#   reach        - practical audience ceiling before it degrades
#   intimacy     - suitability for sensitive or personal news
#   two_way      - support for genuine discussion
#   durability   - whether it survives as a reference record
CHANNELS: Dict[str, Dict[str, Any]] = {
    "1:1 conversation": {"speed": 3, "depth": 5, "reach": 1, "intimacy": 5,
                         "two_way": 5, "durability": 1, "ceiling": 5},
    "team meeting": {"speed": 3, "depth": 4, "reach": 2, "intimacy": 4,
                     "two_way": 5, "durability": 1, "ceiling": 30},
    "all-hands": {"speed": 2, "depth": 3, "reach": 5, "intimacy": 3,
                  "two_way": 2, "durability": 2, "ceiling": 5000},
    "email": {"speed": 4, "depth": 4, "reach": 5, "intimacy": 2,
              "two_way": 1, "durability": 4, "ceiling": 100000},
    "chat announcement": {"speed": 5, "depth": 2, "reach": 4, "intimacy": 1,
                          "two_way": 3, "durability": 2, "ceiling": 5000},
    "intranet / wiki post": {"speed": 1, "depth": 5, "reach": 3, "intimacy": 1,
                             "two_way": 2, "durability": 5, "ceiling": 100000},
    "recorded video": {"speed": 2, "depth": 4, "reach": 5, "intimacy": 3,
                       "two_way": 1, "durability": 4, "ceiling": 100000},
    "manager cascade": {"speed": 2, "depth": 5, "reach": 4, "intimacy": 4,
                        "two_way": 5, "durability": 1, "ceiling": 5000},
    "office hours / AMA": {"speed": 2, "depth": 5, "reach": 3, "intimacy": 4,
                           "two_way": 5, "durability": 2, "ceiling": 500},
}


def clamp(value: Any, low: int = 1, high: int = 5) -> int:
    """Coerce a value to an integer within the given inclusive range."""
    try:
        num = int(value)
    except (TypeError, ValueError):
        num = low
    return max(low, min(high, num))


def score_channel(name: str, traits: Dict[str, Any],
                  msg: Dict[str, Any]) -> Dict[str, Any]:
    """Score one channel against the message profile, with disqualification reasons."""
    urgency = clamp(msg.get("urgency", 3))
    complexity = clamp(msg.get("complexity", 3))
    sensitivity = clamp(msg.get("sensitivity", 3))
    size = int(msg.get("audience_size", 50) or 0)
    needs_discussion = bool(msg.get("needs_discussion", False))
    needs_record = bool(msg.get("needs_record", False))

    raw = 0.0
    raw += traits["speed"] * (urgency / 5.0) * 4
    raw += traits["depth"] * (complexity / 5.0) * 4
    raw += traits["intimacy"] * (sensitivity / 5.0) * 4
    raw += traits["two_way"] * (4 if needs_discussion else 1)
    raw += traits["durability"] * (4 if needs_record else 1)
    raw += traits["reach"] * 2

    disqualifiers: List[str] = []
    if size > traits["ceiling"]:
        disqualifiers.append(
            f"audience of {size} exceeds practical ceiling of {traits['ceiling']}")
    if sensitivity >= 4 and traits["intimacy"] <= 2:
        disqualifiers.append("too impersonal for a high-sensitivity message")
    if needs_record and traits["durability"] <= 2:
        disqualifiers.append("leaves no durable record")
    if needs_discussion and traits["two_way"] <= 2:
        disqualifiers.append("no path for real discussion")

    # Normalise against the theoretical maximum for this profile.
    max_raw = (5 * (urgency / 5.0) * 4 + 5 * (complexity / 5.0) * 4
               + 5 * (sensitivity / 5.0) * 4
               + 5 * (4 if needs_discussion else 1)
               + 5 * (4 if needs_record else 1) + 10)
    fit = round(100.0 * raw / max_raw, 1) if max_raw else 0.0
    if disqualifiers:
        fit = round(fit * 0.4, 1)

    return {
        "channel": name,
        "fit": fit,
        "durable": traits["durability"] >= 4,
        "disqualifiers": disqualifiers,
    }


def rank(data: Dict[str, Any], top: int) -> Dict[str, Any]:
    """Rank all channels for the message and pick a primary and a record channel."""
    msg = data.get("message")
    if not isinstance(msg, dict):
        raise ValueError("input JSON must contain a 'message' object")

    size = int(msg.get("audience_size", 50) or 0)
    scored = [score_channel(name, traits, msg) for name, traits in CHANNELS.items()]
    # Clean channels always outrank disqualified ones, regardless of raw fit.
    scored.sort(key=lambda c: (bool(c["disqualifiers"]), -c["fit"], c["channel"]))
    clean = [c for c in scored if not c["disqualifiers"]]

    def fits_audience(entry: Dict[str, Any]) -> bool:
        return size <= CHANNELS[entry["channel"]]["ceiling"]

    reachable = [c for c in scored if fits_audience(c)]
    notes: List[str] = []

    if clean:
        primary = clean[0]["channel"]
        durable_pool = [c for c in clean if c["durable"]]
    else:
        # No single channel satisfies every constraint, which is normal for
        # high-sensitivity messages at scale. Recommend a pairing instead.
        # Prefer genuine two-way delivery; break ties toward the wider-reaching
        # channel, since a 5-person format cannot carry a 200-person message.
        two_way = sorted(
            reachable,
            key=lambda c: (-CHANNELS[c["channel"]]["two_way"],
                           -CHANNELS[c["channel"]]["reach"], -c["fit"]))
        primary = two_way[0]["channel"] if two_way else scored[0]["channel"]
        durable_pool = [c for c in reachable if c["durable"]]
        notes.append(
            "No single channel satisfies this profile. Deliver live via the primary "
            "channel, then publish the same content to the record channel within the hour.")

    durable_pool = durable_pool or [c for c in scored if c["durable"]]
    if CHANNELS[primary]["durability"] >= 4:
        # The primary channel already leaves a record; no second channel needed.
        record = primary
    else:
        record = durable_pool[0]["channel"] if durable_pool else "intranet / wiki post"

    return {
        "message": msg.get("name", "(unnamed message)"),
        "profile": {
            "urgency": clamp(msg.get("urgency", 3)),
            "complexity": clamp(msg.get("complexity", 3)),
            "sensitivity": clamp(msg.get("sensitivity", 3)),
            "audience_size": size,
            "needs_discussion": bool(msg.get("needs_discussion", False)),
            "needs_record": bool(msg.get("needs_record", False)),
        },
        "single_channel_sufficient": bool(clean),
        "primary_channel": primary,
        "record_channel": record,
        "notes": notes,
        "ranked": scored[:max(top, 1)],
        "disqualified": [c for c in scored if c["disqualifiers"]],
    }


def output(result: Dict[str, Any], fmt: str) -> None:
    """Print the ranking as JSON or human-readable text."""
    if fmt == "json":
        print(json.dumps(result, indent=2))
        return

    prof = result["profile"]
    print(f"Channel fit: {result['message']}")
    print(f"  urgency={prof['urgency']} complexity={prof['complexity']} "
          f"sensitivity={prof['sensitivity']} audience={prof['audience_size']}")
    print(f"  needs_discussion={prof['needs_discussion']} needs_record={prof['needs_record']}")
    print(f"\nPrimary channel: {result['primary_channel']}")
    print(f"System of record: {result['record_channel']}")
    if not result["single_channel_sufficient"]:
        print("Single channel sufficient: NO - use the pairing above")
    for note in result["notes"]:
        print(f"  ! {note}")
    print("\nRanked:")
    for entry in result["ranked"]:
        flag = " [DISQUALIFIED]" if entry["disqualifiers"] else ""
        print(f"  {entry['fit']:>5}  {entry['channel']}{flag}")
        for reason in entry["disqualifiers"]:
            print(f"         - {reason}")
    if result["disqualified"]:
        print("\nDisqualified channels:")
        for entry in result["disqualified"]:
            print(f"  {entry['channel']}: {'; '.join(entry['disqualifiers'])}")


def main() -> None:
    """Parse arguments, rank the channels, and emit the report."""
    parser = argparse.ArgumentParser(
        description="Rank internal communication channels against a message profile.")
    parser.add_argument("--input", required=True,
                        help="Path to a JSON file containing a 'message' profile object")
    parser.add_argument("--top", type=int, default=5,
                        help="How many ranked channels to show (default: 5)")
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
        result = rank(data, args.top)
    except (ValueError, TypeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    output(result, args.format)


if __name__ == "__main__":
    main()
