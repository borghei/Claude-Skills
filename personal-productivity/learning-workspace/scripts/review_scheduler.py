#!/usr/bin/env python3
"""Schedule spaced reviews from a learning record and gate its honesty.

Reads learning-record.json (modules, sessions, items with review history,
misconceptions). For every item it computes the retrieval streak, the next
review date on an expanding interval ladder, and whether it is due. It also
produces a resume brief (last session, active module, what is due, open
misconceptions) and gates the record: an item marked secure without spaced
evidence, an open misconception with no recheck, reviews dated after today.

Usage:
    python3 review_scheduler.py --input assets/sample_learning_record.json --today 2026-11-08
    python3 review_scheduler.py --input learning-record.json --format json

Exit codes: 0 record clean, 1 gate failed (error findings), 2 unreadable input.
"""

import argparse
import json
import sys
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Days until the next review after N consecutive successful spaced recalls.
LADDER = [1, 3, 7, 14, 30, 60, 120]
SECURE_STREAK = 3
SECURE_MIN_GAP_DAYS = 5
RESULTS = {"recalled", "partial", "failed"}
TOLERANCE = 0.75


class InputError(Exception):
    """Raised when the record cannot be read or is malformed."""


def parse_date(value: Any, where: str) -> date:
    """Parse a YYYY-MM-DD string or raise InputError naming the field."""
    try:
        return date.fromisoformat(str(value)[:10])
    except ValueError:
        raise InputError(f"bad date {value!r} in {where} — expected YYYY-MM-DD")


def load_record(path: Path) -> Dict[str, Any]:
    """Read and shape-check the learning record."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise InputError(f"record not found: {path}")
    except json.JSONDecodeError as exc:
        raise InputError(f"record is not valid JSON ({path}): {exc}")
    if not isinstance(data, dict):
        raise InputError("record must be a JSON object")
    for key in ("modules", "sessions", "items", "misconceptions"):
        data.setdefault(key, [])
        if not isinstance(data[key], list):
            raise InputError(f"'{key}' must be a list")
    return data


def latest_date(record: Dict[str, Any]) -> date:
    """Return the latest date mentioned in the record, used when --today is omitted."""
    found: List[date] = [parse_date(s["date"], "sessions") for s in record["sessions"] if s.get("date")]
    for item in record["items"]:
        found += [parse_date(r["date"], f"items.{item.get('id')}") for r in item.get("reviews") or []]
    if not found:
        raise InputError("record has no dates; pass --today")
    return max(found)


def schedule_item(item: Dict[str, Any]) -> Tuple[int, Optional[date], int]:
    """Return (streak, next_due, widest_gap_days) for one item's review history.

    A recall only extends the streak when it came at least one ladder step after
    the previous review; same-day re-reads build fluency, not storage. A failure
    resets the streak, a partial recall repeats the current step.
    """
    reviews = sorted(item.get("reviews") or [], key=lambda r: str(r.get("date")))
    intro = item.get("introduced")
    if not reviews:
        if not intro:
            return 0, None, 0
        return 0, parse_date(intro, f"items.{item.get('id')}") + timedelta(days=LADDER[0]), 0
    streak, widest = 0, 0
    prev = parse_date(intro, f"items.{item.get('id')}.introduced") if intro else None
    for rev in reviews:
        when = parse_date(rev.get("date"), f"items.{item.get('id')}.reviews")
        result = rev.get("result")
        if result not in RESULTS:
            raise InputError(f"items.{item.get('id')}: review result {result!r} not in {sorted(RESULTS)}")
        step = LADDER[min(streak, len(LADDER) - 1)]
        gap = (when - prev).days if prev else step
        # Allow a review up to a quarter of the step early; earlier than that is re-reading.
        needed = max(1, round(step * TOLERANCE))
        if result == "recalled":
            if gap >= needed:
                streak += 1
                widest = max(widest, gap)
        elif result == "failed":
            streak = 0
        prev = when
    return streak, prev + timedelta(days=LADDER[min(streak, len(LADDER) - 1)]), widest


def analyse(record: Dict[str, Any], today: date) -> Dict[str, Any]:
    """Compute the schedule, resume brief and gate findings."""
    findings: List[Dict[str, str]] = []

    def add(sev: str, where: str, msg: str) -> None:
        findings.append({"severity": sev, "where": where, "message": msg})

    module_ids = {m.get("id") for m in record["modules"]}
    status = {m.get("id"): m.get("status", "todo") for m in record["modules"]}
    for m in record["modules"]:
        for dep in m.get("depends_on") or []:
            if dep not in module_ids:
                add("error", f"modules.{m.get('id')}", f"depends on unknown module '{dep}'")
            elif m.get("status") in ("active", "done") and status.get(dep) == "todo":
                add("warn", f"modules.{m.get('id')}", f"started before prerequisite '{dep}'")
    schedule: List[Dict[str, Any]] = []
    for item in record["items"]:
        iid = str(item.get("id"))
        streak, due, widest = schedule_item(item)
        future = [r for r in item.get("reviews") or [] if parse_date(r.get("date"), iid) > today]
        if future:
            add("error", f"items.{iid}", f"{len(future)} review(s) dated after {today} — the record is not trustworthy")
        state = item.get("state", "new")
        if state == "secure" and (streak < SECURE_STREAK or widest < SECURE_MIN_GAP_DAYS):
            add("error", f"items.{iid}", f"marked secure with streak {streak} and widest gap {widest}d; needs "
                f"{SECURE_STREAK} spaced recalls incl. one {SECURE_MIN_GAP_DAYS}+ days apart (fluency is not storage)")
        if state in ("learning", "secure") and not str(item.get("evidence", "")).strip():
            add("error", f"items.{iid}", "no evidence recorded — coverage is not learning")
        if item.get("module") and item["module"] not in module_ids:
            add("warn", f"items.{iid}", f"belongs to unknown module '{item['module']}'")
        overdue = (today - due).days if due and due < today else 0
        if overdue > 14:
            add("warn", f"items.{iid}", f"{overdue} days overdue; review it before new material")
        schedule.append({"id": iid, "concept": item.get("concept", ""), "state": state, "streak": streak,
                         "next_due": due.isoformat() if due else None, "overdue_days": overdue,
                         "due_now": bool(due and due <= today)})
    open_mis = []
    for mis in record["misconceptions"]:
        mid = str(mis.get("id"))
        if mis.get("status", "open") != "open":
            continue
        recheck = mis.get("recheck")
        if not recheck:
            add("error", f"misconceptions.{mid}", "open with no recheck date — it will resurface in a later lesson")
        elif parse_date(recheck, mid) < today:
            add("warn", f"misconceptions.{mid}", f"recheck {recheck} has passed; probe it at the next warm-up")
        open_mis.append({"id": mid, "belief": mis.get("belief", ""), "recheck": recheck})
    sessions = sorted(record["sessions"], key=lambda s: str(s.get("date")))
    last = sessions[-1] if sessions else {}
    gap = (today - parse_date(last["date"], "sessions")).days if last.get("date") else None
    active = [m.get("id") for m in record["modules"] if m.get("status") == "active"]
    nxt = next((m.get("id") for m in record["modules"] if m.get("status") == "todo"
                and all(status.get(d) == "done" for d in m.get("depends_on") or [])), None)
    if len(active) > 1:
        add("warn", "modules", f"{len(active)} modules active at once ({', '.join(map(str, active))})")
    due_now = sorted([s for s in schedule if s["due_now"]], key=lambda s: (-s["overdue_days"], s["id"]))
    week_end = today + timedelta(days=7)
    upcoming = [s for s in schedule if s["next_due"] and not s["due_now"]
                and date.fromisoformat(s["next_due"]) <= week_end]
    resume = {"last_session": last.get("date"), "last_lesson": last.get("lesson"), "days_since": gap,
              "active_module": active[0] if active else None, "next_module": nxt,
              "warm_up": [s["id"] for s in due_now[:5]],
              "restart_mode": "rebuild" if gap is not None and gap > 21 else "continue"}
    return {"topic": record.get("topic", ""), "today": today.isoformat(),
            "passed": not any(f["severity"] == "error" for f in findings),
            "resume": resume, "due_now": due_now, "due_this_week": upcoming,
            "open_misconceptions": open_mis, "schedule": schedule, "findings": findings}


def output(report: Dict[str, Any], fmt: str) -> None:
    """Print the report as text or JSON."""
    if fmt == "json":
        print(json.dumps(report, indent=2))
        return
    r = report["resume"]
    print(f"Learning record: {report['topic']}  (today {report['today']})  "
          f"[{'PASS' if report['passed'] else 'FAIL'}]")
    last = f"last session {r['last_session']} ({r['days_since']} days ago)" if r["last_session"] else "no sessions yet"
    print(f"Resume: {last}, mode {r['restart_mode']}; "
          f"active {r['active_module'] or '-'}, next {r['next_module'] or '-'}")
    print(f"Due now ({len(report['due_now'])}):")
    for s in report["due_now"]:
        print(f"  {s['id']:<5} {s['concept'][:48]:<48} streak {s['streak']}  overdue {s['overdue_days']}d")
    print(f"Due in the next 7 days: {', '.join(s['id'] for s in report['due_this_week']) or 'none'}")
    if report["open_misconceptions"]:
        print("Open misconceptions:")
        for m in report["open_misconceptions"]:
            print(f"  {m['id']}: {m['belief'][:60]} (recheck {m['recheck']})")
    print(f"Findings ({len(report['findings'])}):")
    for f in report["findings"]:
        print(f"  [{f['severity']:5}] {f['where']}: {f['message']}")


def main() -> None:
    """Parse arguments, analyse the record, print, and exit by the gate."""
    parser = argparse.ArgumentParser(description="Spaced-review schedule, resume brief and honesty gate.")
    parser.add_argument("--input", required=True, help="learning-record.json")
    parser.add_argument("--today", help="YYYY-MM-DD (default: latest date in the record)")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="output format")
    args = parser.parse_args()
    try:
        record = load_record(Path(args.input))
        today = parse_date(args.today, "--today") if args.today else latest_date(record)
        report = analyse(record, today)
    except InputError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(2)
    except (KeyError, TypeError, AttributeError) as exc:
        print(f"error: malformed learning record: {exc!r}", file=sys.stderr)
        sys.exit(2)
    output(report, args.format)
    sys.exit(0 if report["passed"] else 1)


if __name__ == "__main__":
    main()
