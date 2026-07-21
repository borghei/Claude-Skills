#!/usr/bin/env python3
"""Track action-item ageing and follow-through across a series of meetings.

Deterministic: the reference date comes from --as-of or from the newest date in
the data, never from the system clock.

Usage:
    python3 commitment_tracker.py --input sample_commitments.json
    python3 commitment_tracker.py --input sample_commitments.json --format json
    python3 commitment_tracker.py --input sample_commitments.json --as-of 2026-07-21
"""

import argparse
import json
import sys
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

OPEN_STATES = {"open", "in_progress", "blocked"}
AGE_BANDS = [(7, "0-7 days"), (14, "8-14 days"), (30, "15-30 days"), (10**6, "31+ days")]
# Follow-through below this fraction marks an owner as over-committed.
FOLLOW_THROUGH_FLOOR = 0.6


def parse_date(value: Optional[str], field: str) -> Optional[date]:
    """Parse an ISO YYYY-MM-DD string, raising an actionable error on bad input."""
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        raise SystemExit(f"error: '{value}' in field '{field}' is not an ISO date (YYYY-MM-DD)")


def load_actions(path: Path) -> List[Dict[str, Any]]:
    """Read and validate the action-item register."""
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise SystemExit(f"error: file not found: {path}")
    except json.JSONDecodeError as exc:
        raise SystemExit(f"error: {path} is not valid JSON ({exc.msg}, line {exc.lineno})")
    actions = doc.get("actions") if isinstance(doc, dict) else doc
    if not isinstance(actions, list) or not actions:
        raise SystemExit("error: expected a non-empty 'actions' list")
    for a in actions:
        if "id" not in a or "created" not in a:
            raise SystemExit("error: every action needs at least 'id' and 'created' (YYYY-MM-DD)")
    return actions


def reference_date(actions: List[Dict[str, Any]], as_of: Optional[str]) -> date:
    """Resolve the reference date: --as-of when given, otherwise the newest date present."""
    if as_of:
        parsed = parse_date(as_of, "--as-of")
        if parsed:
            return parsed
    seen = []
    for a in actions:
        for field in ("created", "due", "closed"):
            parsed = parse_date(a.get(field), field)
            if parsed:
                seen.append(parsed)
    if not seen:
        raise SystemExit("error: no parsable dates in the register; pass --as-of explicitly")
    return max(seen)


def band(days: int) -> str:
    """Return the ageing band label for a number of days open."""
    for limit, label in AGE_BANDS:
        if days <= limit:
            return label
    return AGE_BANDS[-1][1]


def enrich(actions: List[Dict[str, Any]], today: date) -> List[Dict[str, Any]]:
    """Annotate each action with age, overdue days and its accountability gaps."""
    rows = []
    for a in actions:
        created = parse_date(a["created"], "created")
        due = parse_date(a.get("due"), "due")
        closed = parse_date(a.get("closed"), "closed")
        status = str(a.get("status", "open")).lower()
        end = closed or today
        age = (end - created).days if created else 0
        overdue = (today - due).days if due and not closed and due < today else 0
        slipped = bool(due and closed and closed > due)
        gaps = []
        if not a.get("owner"):
            gaps.append("no owner")
        if not due:
            gaps.append("no due date")
        rows.append({
            "id": a["id"],
            "text": a.get("text", ""),
            "owner": a.get("owner"),
            "meeting": a.get("meeting", "unknown"),
            "created": a["created"],
            "due": a.get("due"),
            "closed": a.get("closed"),
            "status": status,
            "age_days": age,
            "age_band": band(age),
            "overdue_days": overdue,
            "slipped": slipped,
            "carried_over": int(a.get("carried_over", 0)),
            "gaps": gaps,
        })
    return rows


def per_owner(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Summarise follow-through, overdue load and slippage for each named owner."""
    buckets: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for r in rows:
        buckets[r["owner"] or "(unowned)"].append(r)
    out = []
    for owner, items in buckets.items():
        done = [i for i in items if i["status"] == "done"]
        on_time = [i for i in done if not i["slipped"]]
        rate = len(done) / len(items)
        out.append({
            "owner": owner,
            "total": len(items),
            "done": len(done),
            "open": len([i for i in items if i["status"] in OPEN_STATES]),
            "overdue": len([i for i in items if i["overdue_days"] > 0]),
            "follow_through_pct": round(rate * 100, 1),
            "on_time_pct": round(len(on_time) / len(done) * 100, 1) if done else 0.0,
            "over_committed": rate < FOLLOW_THROUGH_FLOOR and len(items) >= 3,
        })
    return sorted(out, key=lambda o: (-o["overdue"], o["follow_through_pct"]))


def per_meeting(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Summarise how well each meeting's commitments actually get closed."""
    buckets: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for r in rows:
        buckets[r["meeting"]].append(r)
    out = []
    for meeting, items in buckets.items():
        done = [i for i in items if i["status"] == "done"]
        out.append({
            "meeting": meeting,
            "actions": len(items),
            "completion_pct": round(len(done) / len(items) * 100, 1),
            "unowned": len([i for i in items if not i["owner"]]),
            "undated": len([i for i in items if not i["due"]]),
            "avg_carry_over": round(sum(i["carried_over"] for i in items) / len(items), 2),
        })
    return sorted(out, key=lambda m: m["completion_pct"])


def build_report(rows: List[Dict[str, Any]], today: date) -> Dict[str, Any]:
    """Assemble register-wide totals, ageing distribution and the headline verdict."""
    done = [r for r in rows if r["status"] == "done"]
    open_items = [r for r in rows if r["status"] in OPEN_STATES]
    overdue = [r for r in open_items if r["overdue_days"] > 0]
    ageing: Dict[str, int] = defaultdict(int)
    for r in open_items:
        ageing[r["age_band"]] += 1
    completion = round(len(done) / len(rows) * 100, 1)
    stale = [r for r in open_items if r["age_days"] > 30]
    if completion < 50:
        verdict = (f"BROKEN FOLLOW-THROUGH — {completion}% of commitments closed. "
                   "The meetings are producing intentions, not commitments.")
    elif overdue and len(overdue) / max(len(open_items), 1) > 0.4:
        verdict = (f"OVERDUE BACKLOG — {len(overdue)} of {len(open_items)} open actions are past due. "
                   "Re-negotiate dates publicly rather than letting them lapse silently.")
    elif stale:
        verdict = (f"STALE TAIL — {len(stale)} action(s) open beyond 30 days. "
                   "Close, reassign, or explicitly drop them.")
    else:
        verdict = f"HEALTHY — {completion}% closed with no stale tail."
    return {
        "as_of": today.isoformat(),
        "totals": {
            "actions": len(rows),
            "done": len(done),
            "open": len(open_items),
            "overdue": len(overdue),
            "unowned": len([r for r in rows if not r["owner"]]),
            "undated": len([r for r in rows if not r["due"]]),
            "completion_pct": completion,
        },
        "ageing_open": dict(ageing),
        "verdict": verdict,
        "by_owner": per_owner(rows),
        "by_meeting": per_meeting(rows),
        "oldest_open": sorted(open_items, key=lambda r: -r["age_days"])[:5],
    }


def output(report: Dict[str, Any], fmt: str) -> None:
    """Print the commitment report as JSON or as a human-readable report."""
    if fmt == "json":
        print(json.dumps(report, indent=2))
        return
    t = report["totals"]
    print(f"COMMITMENT FOLLOW-THROUGH — as of {report['as_of']}")
    print("=" * 66)
    print(f"{t['actions']} actions | {t['done']} done ({t['completion_pct']}%) | "
          f"{t['open']} open | {t['overdue']} overdue")
    print(f"Accountability gaps: {t['unowned']} unowned, {t['undated']} undated")
    print(f"\n{report['verdict']}\n")
    print("AGEING OF OPEN ACTIONS")
    for _, label in AGE_BANDS:
        print(f"  {label:<12}{report['ageing_open'].get(label, 0)}")
    print("\nBY OWNER")
    print(f"  {'owner':<14}{'total':>6}{'done':>6}{'overdue':>9}{'follow-thru':>13}{'on-time':>9}")
    for o in report["by_owner"]:
        flag = "  << over-committed" if o["over_committed"] else ""
        print(f"  {o['owner']:<14}{o['total']:>6}{o['done']:>6}{o['overdue']:>9}"
              f"{o['follow_through_pct']:>12.1f}%{o['on_time_pct']:>8.1f}%{flag}")
    print("\nBY MEETING")
    for m in report["by_meeting"]:
        print(f"  {m['meeting']:<26}{m['actions']:>3} actions  {m['completion_pct']:>5.1f}% closed  "
              f"{m['unowned']} unowned  {m['undated']} undated")
    print("\nOLDEST OPEN")
    for r in report["oldest_open"]:
        due = f"due {r['due']}" if r["due"] else "no due date"
        print(f"  {r['age_days']:>4}d  [{r['owner'] or 'unowned'}] {r['text'][:52]} ({due})")


def main() -> None:
    """Parse arguments, analyse the commitment register and print the report."""
    parser = argparse.ArgumentParser(
        description="Track action-item ageing and follow-through across a meeting series.")
    parser.add_argument("--input", required=True, help="path to an action-item register JSON")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                        help="output format (default: text)")
    parser.add_argument("--as-of", help="reference date YYYY-MM-DD (default: newest date in the data)")
    args = parser.parse_args()
    try:
        actions = load_actions(Path(args.input))
        today = reference_date(actions, args.as_of)
        output(build_report(enrich(actions, today), today), args.format)
    except SystemExit:
        raise
    except (KeyError, TypeError, ValueError, ZeroDivisionError) as exc:
        print(f"error: malformed commitment data — {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
