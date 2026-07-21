#!/usr/bin/env python3
"""Audit a capture log for staleness, unactionable phrasing, and inbox drift.

Complements triage: instead of sorting items, this scores the health of the
capture habit itself — how fast items leave the inbox, how many are phrased in
a way that can never be executed, and where the backlog is rotting.

Usage:
    python3 capture_audit.py --input assets/sample_capture_log.json --today 2026-07-21
    python3 capture_audit.py --input log.json --today 2026-07-21 --format json
"""

import argparse
import json
import re
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# An item older than this without processing means the weekly pass is not happening.
STALE_DAYS = 14
ROTTEN_DAYS = 45

# Health thresholds, expressed as a share of the log.
MAX_STALE_SHARE = 0.20
MAX_UNACTIONABLE_SHARE = 0.25

CONCRETE_VERBS = {
    "call", "email", "text", "draft", "write", "send", "reply", "book", "buy",
    "order", "pay", "file", "print", "sign", "schedule", "cancel", "confirm",
    "ask", "read", "review", "renew", "upload", "delete", "install", "return",
}

VAGUE_PHRASES = (
    "think about", "look into", "follow up", "followup", "deal with", "sort out",
    "circle back", "touch base", "revisit", "handle", "sometime", "asap", "stuff",
)

SOURCE_FIELD = "source"

# Items that never claimed to be actions are exempt from the phrasing audit.
NON_ACTION_MARKERS = (
    "http://", "https://", "someday", "maybe", "one day", "nvm", "never mind",
    "no longer", "cancelled", "obsolete",
)


def is_action_intent(text: str) -> bool:
    """True when the item is meant to become an action and so must be executable."""
    lower = text.lower()
    return not any(marker in lower for marker in NON_ACTION_MARKERS)


def load_items(path: Path) -> List[Dict[str, Any]]:
    """Load capture items from a JSON list or an object with an 'items' key."""
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        if "items" not in data:
            raise ValueError(
                f"{path.name} is a JSON object with no 'items' key "
                f"(found: {', '.join(sorted(data)) or 'nothing'}) — expected a capture log")
        items = data["items"]
    else:
        items = data
    if not isinstance(items, list):
        raise ValueError("capture log must be a JSON list or an object with an 'items' list")
    return items


def item_age(item: Dict[str, Any], today: date) -> Optional[int]:
    """Age of a capture item in days, or None when it carries no timestamp."""
    stamp = item.get("captured_at")
    if not stamp:
        return None
    try:
        return (today - datetime.strptime(str(stamp)[:10], "%Y-%m-%d").date()).days
    except ValueError:
        return None


def phrasing_problems(text: str) -> List[str]:
    """Return the phrasing defects that stop an item from being executable."""
    problems: List[str] = []
    lower = text.lower().strip()
    words = re.findall(r"[a-z']+", lower)
    if not words:
        return ["empty"]
    if len(words) <= 2:
        problems.append("too-terse")
    if not any(w in CONCRETE_VERBS for w in words):
        problems.append("no-concrete-verb")
    for phrase in VAGUE_PHRASES:
        if phrase in lower:
            problems.append(f"vague:{phrase}")
            break
    if lower.endswith("?") and not any(w in CONCRETE_VERBS for w in words):
        problems.append("open-question")
    return problems


def source_breakdown(items: List[Dict[str, Any]]) -> Dict[str, int]:
    """Count captures per source so the leakiest inbox is visible."""
    counts: Dict[str, int] = {}
    for item in items:
        key = str(item.get(SOURCE_FIELD, "unspecified"))
        counts[key] = counts.get(key, 0) + 1
    return counts


def grade(stale_share: float, unactionable_share: float) -> Tuple[str, str]:
    """Grade capture-habit health and name the dominant failure."""
    if stale_share <= MAX_STALE_SHARE and unactionable_share <= MAX_UNACTIONABLE_SHARE:
        return "healthy", "The log is being processed and phrased for execution."
    if stale_share > MAX_STALE_SHARE and unactionable_share > MAX_UNACTIONABLE_SHARE:
        return "failing", "Items are neither processed on time nor phrased as actions."
    if stale_share > MAX_STALE_SHARE:
        return "at-risk", "Capture works; the weekly processing pass does not."
    return "at-risk", "Processing happens; items are captured too vaguely to execute."


def audit(items: List[Dict[str, Any]], today: date) -> Dict[str, Any]:
    """Score staleness, phrasing quality, and source distribution for the log."""
    if not items:
        raise ValueError("capture log is empty — nothing to audit")
    findings: List[Dict[str, Any]] = []
    stale = rotten = unactionable = undated = exempt = 0
    ages: List[int] = []

    for item in items:
        text = str(item.get("text", "")).strip()
        age = item_age(item, today)
        if is_action_intent(text):
            problems = phrasing_problems(text)
        else:
            problems = []
            exempt += 1
        if age is None:
            undated += 1
        else:
            ages.append(age)
            if age >= ROTTEN_DAYS:
                rotten += 1
            elif age >= STALE_DAYS:
                stale += 1
        if problems:
            unactionable += 1
        if problems or (age is not None and age >= STALE_DAYS):
            findings.append({
                "id": str(item.get("id", "?")),
                "text": text,
                "age_days": age,
                "problems": problems,
            })

    total = len(items)
    action_intent = total - exempt
    stale_share = (stale + rotten) / total
    unactionable_share = unactionable / action_intent if action_intent else 0.0
    status, verdict = grade(stale_share, unactionable_share)

    return {
        "total": total,
        "status": status,
        "verdict": verdict,
        "oldest_days": max(ages) if ages else None,
        "median_age_days": sorted(ages)[len(ages) // 2] if ages else None,
        "stale": stale,
        "rotten": rotten,
        "undated": undated,
        "action_intent": action_intent,
        "unactionable": unactionable,
        "stale_share": round(stale_share, 3),
        "unactionable_share": round(unactionable_share, 3),
        "sources": source_breakdown(items),
        "findings": findings,
    }


def output(report: Dict[str, Any], fmt: str) -> None:
    """Print the audit as text or JSON."""
    if fmt == "json":
        print(json.dumps(report, indent=2))
        return
    print(f"Capture-log audit — {report['total']} items — {report['status'].upper()}")
    print(report["verdict"])
    print("-" * 52)
    print(f"  oldest item      {report['oldest_days']} days")
    print(f"  median age       {report['median_age_days']} days")
    print(f"  stale (>={STALE_DAYS}d)   {report['stale']}")
    print(f"  rotten (>={ROTTEN_DAYS}d)  {report['rotten']}")
    print(f"  undated          {report['undated']}")
    print(f"  unactionable     {report['unactionable']} of {report['action_intent']} action-intent ({report['unactionable_share']:.0%})")
    print("\n  Captures by source:")
    for src, n in sorted(report["sources"].items(), key=lambda kv: -kv[1]):
        print(f"    {src:<18} {n}")
    if report["findings"]:
        print("\n  Items needing attention:")
        for f in report["findings"]:
            age = f"{f['age_days']}d" if f["age_days"] is not None else "undated"
            problems = ", ".join(f["problems"]) or "stale only"
            print(f"    {f['id']} ({age}): {f['text']}")
            print(f"        {problems}")


def main() -> None:
    """Parse arguments, audit the capture log, and emit the report."""
    parser = argparse.ArgumentParser(
        description="Audit a capture log for staleness and unactionable phrasing.",
    )
    parser.add_argument("--input", required=True, help="Path to the JSON capture log")
    parser.add_argument("--today", required=True, help="Reference date YYYY-MM-DD for all age calculations")
    parser.add_argument("--stale-days", type=int, default=STALE_DAYS, help=f"Days before an item counts as stale (default: {STALE_DAYS})")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format (default: text)")
    args = parser.parse_args()

    try:
        path = Path(args.input)
        if not path.exists():
            raise FileNotFoundError(f"capture log not found: {path}")
        today = datetime.strptime(args.today, "%Y-%m-%d").date()
        globals()["STALE_DAYS"] = args.stale_days
        output(audit(load_items(path), today), args.format)
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
