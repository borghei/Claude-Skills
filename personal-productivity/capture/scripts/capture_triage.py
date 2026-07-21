#!/usr/bin/env python3
"""Triage a raw capture log into actions, projects, reference, someday, or drop.

Reads a capture log (JSON list or newline-delimited markdown bullets) and
assigns each item an outcome bucket plus a suggested next action phrased as a
concrete verb. Deterministic: no clock reads, no network, no randomness.

Usage:
    python3 capture_triage.py --input assets/sample_capture_log.json
    python3 capture_triage.py --input log.md --today 2026-07-21 --format json
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, asdict
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Verbs that already name a single physical next action.
ACTION_VERBS = {
    "call", "email", "text", "draft", "write", "send", "reply", "book",
    "buy", "order", "pay", "file", "print", "sign", "schedule", "cancel",
    "reschedule", "confirm", "ask", "read", "review", "renew", "upload",
    "delete", "install", "measure", "photograph", "return",
}

# Verbs that imply several steps and therefore a project, not an action.
PROJECT_VERBS = {
    "launch", "plan", "organise", "organize", "migrate", "redesign", "build",
    "hire", "onboard", "research", "figure", "sort", "improve", "fix",
    "overhaul", "rebuild", "prepare", "set", "move", "refinance",
}

SOMEDAY_MARKERS = ("someday", "maybe", "one day", "would be nice", "eventually")
REFERENCE_MARKERS = ("http://", "https://", "recipe", "quote", "article", "podcast", "isbn")
DROP_MARKERS = ("nvm", "never mind", "no longer", "cancelled", "obsolete", "duplicate")

# Vague nouns that signal the capture was never turned into an outcome.
VAGUE_HEADS = ("stuff", "things", "notes", "thoughts", "misc", "follow up", "followup")

STALE_DAYS = 14
ROTTEN_DAYS = 45


@dataclass
class TriagedItem:
    """One capture-log entry after classification."""

    id: str
    text: str
    bucket: str
    next_action: str
    two_minute: bool
    age_days: Optional[int]
    flags: List[str]
    confidence: str


def parse_log(path: Path) -> List[Dict[str, Any]]:
    """Load a capture log from JSON or from markdown bullet lines."""
    raw = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        data = json.loads(raw)
        if isinstance(data, dict):
            if "items" not in data:
                raise ValueError(
                    f"{path.name} is a JSON object with no 'items' key "
                    f"(found: {', '.join(sorted(data)) or 'nothing'}) — expected a capture log")
            items = data["items"]
        else:
            items = data
        if not isinstance(items, list):
            raise ValueError("JSON log must be a list, or an object with an 'items' list")
        return items
    items = []
    for n, line in enumerate(raw.splitlines(), start=1):
        stripped = line.strip().lstrip("-*").strip()
        if stripped:
            items.append({"id": f"L{n}", "text": stripped})
    return items


def age_in_days(captured_at: Optional[str], today: Optional[date]) -> Optional[int]:
    """Days between a capture timestamp and the reference date, if both exist."""
    if not captured_at or today is None:
        return None
    try:
        captured = datetime.strptime(captured_at[:10], "%Y-%m-%d").date()
    except ValueError:
        return None
    return (today - captured).days


def first_verb(text: str) -> Optional[str]:
    """Return the first recognised leading verb in the item text."""
    words = re.findall(r"[a-z']+", text.lower())
    for word in words[:3]:
        if word in ACTION_VERBS or word in PROJECT_VERBS:
            return word
    return None


def suggest_next_action(text: str, bucket: str, verb: Optional[str]) -> str:
    """Phrase a concrete next physical action for the item."""
    clean = text.strip().rstrip(".")
    if bucket == "action" and verb:
        return clean[0].upper() + clean[1:]
    if bucket == "action":
        return f"Do: {clean}"
    if bucket == "project":
        return f"Decide and schedule the first step toward: {clean}"
    if bucket == "reference":
        return f"File in reference under a retrievable topic: {clean}"
    if bucket == "someday":
        return f"Park on the someday list with a review date: {clean}"
    return f"Delete — no outcome attached: {clean}"


def classify(item: Dict[str, Any], today: Optional[date]) -> TriagedItem:
    """Assign a bucket, next action, and quality flags to one capture item."""
    text = str(item.get("text", "")).strip()
    if not text:
        raise ValueError(f"item {item.get('id', '?')} has no 'text' field")
    lower = text.lower()
    flags: List[str] = []
    verb = first_verb(lower)
    words = len(text.split())

    if any(m in lower for m in DROP_MARKERS):
        bucket, confidence = "drop", "high"
    elif any(m in lower for m in SOMEDAY_MARKERS):
        bucket, confidence = "someday", "high"
    elif any(m in lower for m in REFERENCE_MARKERS):
        bucket, confidence = "reference", "high"
    elif verb in PROJECT_VERBS or " and " in lower:
        bucket, confidence = "project", "high" if verb else "medium"
    elif verb in ACTION_VERBS:
        bucket, confidence = "action", "high"
    elif any(lower.startswith(h) or lower == h for h in VAGUE_HEADS):
        bucket, confidence = "project", "low"
        flags.append("unactionable-phrasing")
    else:
        bucket, confidence = "project", "low"
        flags.append("no-verb")

    if words <= 2 and bucket != "reference":
        flags.append("too-terse")
        confidence = "low"

    age = age_in_days(item.get("captured_at"), today)
    if age is not None:
        if age >= ROTTEN_DAYS:
            flags.append("rotten")
        elif age >= STALE_DAYS:
            flags.append("stale")

    two_minute = bucket == "action" and verb in {"reply", "email", "text", "confirm", "sign", "pay"} and words <= 8

    return TriagedItem(
        id=str(item.get("id", "?")),
        text=text,
        bucket=bucket,
        next_action=suggest_next_action(text, bucket, verb),
        two_minute=two_minute,
        age_days=age,
        flags=flags,
        confidence=confidence,
    )


def triage(items: List[Dict[str, Any]], today: Optional[date]) -> Dict[str, Any]:
    """Classify every item and summarise the resulting distribution."""
    results = [classify(i, today) for i in items]
    counts: Dict[str, int] = {}
    for r in results:
        counts[r.bucket] = counts.get(r.bucket, 0) + 1
    return {
        "total": len(results),
        "counts": counts,
        "two_minute_count": sum(1 for r in results if r.two_minute),
        "needs_rewrite": sum(1 for r in results if r.confidence == "low"),
        "items": [asdict(r) for r in results],
    }


def output(report: Dict[str, Any], fmt: str) -> None:
    """Print the triage report as text or JSON."""
    if fmt == "json":
        print(json.dumps(report, indent=2))
        return
    print(f"Capture triage — {report['total']} items")
    print("-" * 46)
    for bucket, n in sorted(report["counts"].items(), key=lambda kv: -kv[1]):
        print(f"  {bucket:<10} {n:>3}")
    print(f"\n  2-minute items: {report['two_minute_count']} (do these before filing anything)")
    print(f"  Needs rewrite:  {report['needs_rewrite']} (low-confidence phrasing)\n")
    for item in report["items"]:
        marks = " ".join(f"[{f}]" for f in item["flags"])
        quick = " (2-min)" if item["two_minute"] else ""
        print(f"[{item['bucket']}] {item['id']}: {item['text']}{quick} {marks}")
        print(f"    -> {item['next_action']}")


def main() -> None:
    """Parse arguments, triage the capture log, and emit the report."""
    parser = argparse.ArgumentParser(
        description="Triage a capture log into actions, projects, reference, someday, or drop.",
    )
    parser.add_argument("--input", required=True, help="Path to a .json capture log or a .md bullet list")
    parser.add_argument("--today", help="Reference date YYYY-MM-DD for age calculations (omit to skip ageing)")
    parser.add_argument("--bucket", help="Show only items landing in this bucket (action, project, reference, someday, drop)")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format (default: text)")
    args = parser.parse_args()

    try:
        path = Path(args.input)
        if not path.exists():
            raise FileNotFoundError(f"capture log not found: {path}")
        today = datetime.strptime(args.today, "%Y-%m-%d").date() if args.today else None
        report = triage(parse_log(path), today)
        if args.bucket:
            report["items"] = [i for i in report["items"] if i["bucket"] == args.bucket]
        output(report, args.format)
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
