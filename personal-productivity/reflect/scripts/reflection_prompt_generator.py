#!/usr/bin/env python3
"""Generate a cadence-appropriate reflection prompt set from recent commitments.

Builds a daily, weekly, or quarterly prompt set that forces decisions rather
than journaling: every commitment from the previous cycle is surfaced with its
status, overdue and repeatedly-missed items get accountability prompts, and the
set closes with a required behaviour change. Deterministic: no clock reads, no
network, no randomness.

Usage:
    python3 reflection_prompt_generator.py --input assets/sample_commitments.json --cadence weekly
    python3 reflection_prompt_generator.py --input c.json --cadence quarterly --as-of 2026-07-21 --format json
"""

import argparse
import json
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# A commitment carried this many cycles without progress is a decision, not a task.
REPEAT_MISS_THRESHOLD = 3

CADENCE_SPEC: Dict[str, Dict[str, Any]] = {
    "daily": {
        "minutes": 5,
        "purpose": "Catch today's evidence before it decays. Not a diary — one observation, one adjustment.",
        "core": [
            "What did I predict about today that turned out wrong?",
            "Where did my time actually go, versus where I said it would go?",
            "What is the one thing I would do differently if today repeated?",
        ],
        "closing": "Name one concrete change for tomorrow. If nothing changes, today's reflection was journaling.",
    },
    "weekly": {
        "minutes": 20,
        "purpose": "Test last week's commitments against outcomes and extract one pattern worth acting on.",
        "core": [
            "Which commitments did I keep, and which did I quietly drop? Why those specifically?",
            "What did I believe on Monday that I no longer believe?",
            "Which piece of work took materially longer than I estimated, and what did I fail to account for?",
            "What did I avoid this week, and what does the avoidance tell me?",
            "What surprised me — and had I predicted it, would I have acted differently?",
        ],
        "closing": "State one behaviour change for next week, phrased as a rule, not an intention.",
    },
    "quarterly": {
        "minutes": 90,
        "purpose": "Score judgement across the quarter and change something structural — role, commitments, or method.",
        "core": [
            "Which of my quarter-start predictions were wrong, and were they wrong in a consistent direction?",
            "What did I commit to that I never started? What does the pattern across those say about what I actually value?",
            "Which recurring commitment has produced no return and should be killed?",
            "Where was I overconfident, and what was the cost in decisions made on that confidence?",
            "What did I learn that changed how I work, versus what I merely read about?",
            "If I were advising someone else with this quarter's record, what would I tell them to stop doing?",
        ],
        "closing": "Kill one commitment, change one method, and write next quarter's predictions with explicit confidence levels.",
    },
}


def load_commitments(path: Path) -> List[Dict[str, Any]]:
    """Load commitment records from a JSON list or an object with a 'commitments' key."""
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        if "commitments" not in data:
            raise ValueError(
                f"{path.name} is a JSON object with no 'commitments' key "
                f"(found: {', '.join(sorted(data)) or 'nothing'}) — expected a commitment log")
        items = data["commitments"]
    else:
        items = data
    if not isinstance(items, list):
        raise ValueError("input must be a JSON list or an object with a 'commitments' list")
    return items


def parse_date(value: Any) -> Optional[date]:
    """Parse a YYYY-MM-DD value, returning None when absent or malformed."""
    if not value:
        return None
    try:
        return datetime.strptime(str(value)[:10], "%Y-%m-%d").date()
    except ValueError:
        return None


def classify_commitment(item: Dict[str, Any], as_of: Optional[date]) -> Dict[str, Any]:
    """Attach status, overdue days, and carry count to one commitment."""
    status = str(item.get("status", "open")).lower()
    if status not in {"kept", "missed", "partial", "open"}:
        raise ValueError(f"unknown status {status!r} — use kept, missed, partial, or open")
    due = parse_date(item.get("due"))
    overdue = (as_of - due).days if due and as_of and as_of > due and status != "kept" else 0
    carried = int(item.get("carried_cycles", 0))
    return {
        "id": str(item.get("id", "?")),
        "text": str(item.get("text", "")).strip(),
        "status": status,
        "due": str(item["due"])[:10] if item.get("due") else None,
        "overdue_days": overdue,
        "carried_cycles": carried,
        "chronic": carried >= REPEAT_MISS_THRESHOLD,
    }


def ordinal(n: int) -> str:
    """Render a small integer as an English ordinal word or numeral."""
    words = {2: "second", 3: "third", 4: "fourth", 5: "fifth", 6: "sixth", 7: "seventh"}
    if n in words:
        return words[n]
    suffix = "th" if 11 <= n % 100 <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


def accountability_prompts(commitments: List[Dict[str, Any]]) -> List[str]:
    """Build prompts that force a decision on each unresolved commitment."""
    prompts: List[str] = []
    for item in commitments:
        if item["chronic"]:
            prompts.append(
                f"[{item['id']}] \"{item['text']}\" has carried {item['carried_cycles']} cycles with no "
                f"progress. Carrying it a {ordinal(item['carried_cycles'] + 1)} time is a decision to never "
                "do it — so make the decision explicitly: commit to a date, delegate it, or kill it now.")
        elif item["status"] == "missed":
            prompts.append(
                f"[{item['id']}] \"{item['text']}\" was missed. Was the estimate wrong, the priority wrong, "
                "or the commitment never real? Name which — the fix differs for each.")
        elif item["status"] == "partial":
            prompts.append(
                f"[{item['id']}] \"{item['text']}\" was partially done. What specifically stopped it, and is "
                "the remainder still worth finishing?")
        elif item["overdue_days"] > 0:
            days = "day" if item["overdue_days"] == 1 else "days"
            prompts.append(
                f"[{item['id']}] \"{item['text']}\" is {item['overdue_days']} {days} overdue. Re-commit with a "
                "new date you believe, or drop it — a silently slipping date erodes every other date you set.")
    return prompts


def summarise(commitments: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Count commitment outcomes and compute the keep rate."""
    counts: Dict[str, int] = {"kept": 0, "missed": 0, "partial": 0, "open": 0}
    for item in commitments:
        counts[item["status"]] += 1
    closed = counts["kept"] + counts["missed"] + counts["partial"]
    return {
        "total": len(commitments),
        "counts": counts,
        "keep_rate": round(counts["kept"] / closed, 2) if closed else None,
        "chronic": [c["id"] for c in commitments if c["chronic"]],
        "overdue": [c["id"] for c in commitments if c["overdue_days"] > 0],
    }


def keep_rate_note(keep_rate: Optional[float]) -> str:
    """Interpret the commitment keep rate."""
    if keep_rate is None:
        return "No closed commitments this cycle — nothing to score yet."
    if keep_rate >= 0.85:
        return (f"Keep rate {keep_rate:.0%} — high. Check you are not under-committing; a rate this high "
                "often means the commitments are safe rather than that execution is strong.")
    if keep_rate >= 0.6:
        return f"Keep rate {keep_rate:.0%} — healthy. Commitments are ambitious enough to sometimes fail, and mostly hold."
    return (f"Keep rate {keep_rate:.0%} — you are committing to more than you deliver. Cut the number of "
            "commitments per cycle before trying to improve execution.")


def build(commitments: List[Dict[str, Any]], cadence: str, as_of: Optional[date]) -> Dict[str, Any]:
    """Assemble the full prompt set for the requested cadence."""
    spec = CADENCE_SPEC[cadence]
    classified = [classify_commitment(c, as_of) for c in commitments]
    summary = summarise(classified)
    return {
        "cadence": cadence,
        "as_of": as_of.isoformat() if as_of else None,
        "time_budget_min": spec["minutes"],
        "purpose": spec["purpose"],
        "summary": summary,
        "keep_rate_note": keep_rate_note(summary["keep_rate"]),
        "core_prompts": spec["core"],
        "accountability_prompts": accountability_prompts(classified),
        "closing_requirement": spec["closing"],
        "commitments": classified,
    }


def output(report: Dict[str, Any], fmt: str) -> None:
    """Print the prompt set as text or JSON."""
    if fmt == "json":
        print(json.dumps(report, indent=2))
        return
    print(f"{report['cadence'].upper()} REFLECTION — {report['time_budget_min']} minutes")
    print(report["purpose"])
    counts = report["summary"]["counts"]
    print(f"\nCommitments: {counts['kept']} kept, {counts['missed']} missed, "
          f"{counts['partial']} partial, {counts['open']} open")
    print(report["keep_rate_note"])
    print("-" * 66)
    print("\nCore prompts:")
    for n, prompt in enumerate(report["core_prompts"], start=1):
        print(f"  {n}. {prompt}")
    if report["accountability_prompts"]:
        print("\nCommitment accountability — each needs a decision, not a note:")
        for prompt in report["accountability_prompts"]:
            print(f"  - {prompt}")
    print(f"\nClosing requirement:\n  {report['closing_requirement']}")


def main() -> None:
    """Parse arguments, build the prompt set, and emit it."""
    parser = argparse.ArgumentParser(
        description="Generate a cadence-appropriate reflection prompt set from recent commitments.",
    )
    parser.add_argument("--input", required=True, help="Path to the JSON commitment log")
    parser.add_argument("--cadence", required=True, choices=sorted(CADENCE_SPEC), help="Reflection cadence to generate")
    parser.add_argument("--as-of", help="Reference date YYYY-MM-DD for overdue calculations (omit to skip)")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format (default: text)")
    args = parser.parse_args()

    try:
        path = Path(args.input)
        if not path.exists():
            raise FileNotFoundError(f"commitment log not found: {path}")
        as_of = datetime.strptime(args.as_of, "%Y-%m-%d").date() if args.as_of else None
        output(build(load_commitments(path), args.cadence, as_of), args.format)
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
