#!/usr/bin/env python3
"""Audit a team's recurring-meeting calendar for load, cost, overlap and low-value recurrences.

Usage:
    python3 meeting_load_auditor.py --input sample_calendar.json
    python3 meeting_load_auditor.py --input sample_calendar.json --format json
    python3 meeting_load_auditor.py --input sample_calendar.json --maker-hours-target 24
"""

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Tuple

WORK_WEEK_HOURS = 40.0
# Verdict thresholds, in decisions recorded per month for the whole meeting series.
DECISION_FLOOR = 1.0
BIG_ROOM = 8  # attendees above which a meeting is a broadcast, not a working session


def _minutes(clock: str) -> int:
    """Convert an "HH:MM" 24-hour clock string into minutes past midnight."""
    hh, mm = clock.split(":")
    return int(hh) * 60 + int(mm)


def load_calendar(path: Path) -> Dict[str, Any]:
    """Read and validate the calendar export, returning the parsed document."""
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise SystemExit(f"error: calendar file not found: {path}")
    except json.JSONDecodeError as exc:
        raise SystemExit(f"error: {path} is not valid JSON ({exc.msg}, line {exc.lineno})")
    if not isinstance(doc, dict) or "meetings" not in doc or "people" not in doc:
        raise SystemExit("error: calendar JSON needs top-level 'people' and 'meetings' keys")
    return doc


def cost_table(doc: Dict[str, Any]) -> Dict[str, float]:
    """Build a person-id -> fully-loaded hourly cost lookup, falling back to the default."""
    default = float(doc.get("default_hourly_cost", 0))
    return {p["id"]: float(p.get("hourly_cost", default)) for p in doc["people"]}


def score_meeting(meeting: Dict[str, Any], weekly_hours: float) -> Tuple[str, List[str]]:
    """Classify a recurring meeting as KEEP, TRIM, ASYNC or KILL with the reasons why."""
    reasons: List[str] = []
    decisions = float(meeting.get("decisions_last_month", 0))
    attendees = len(meeting.get("attendees", []))

    if not meeting.get("has_agenda", False):
        reasons.append("no standing agenda")
    if not meeting.get("has_notes", False):
        reasons.append("no written record — absentees cannot catch up")
    if decisions < DECISION_FLOOR:
        reasons.append(f"{decisions:g} decisions in the last month")
    if attendees >= BIG_ROOM and meeting.get("type") != "broadcast":
        reasons.append(f"{attendees} attendees — a broadcast wearing a working-session badge")
    if meeting.get("duration_min", 0) >= 60 and decisions < 2:
        reasons.append("60+ minutes for fewer than 2 decisions per month")

    if decisions < DECISION_FLOOR and not meeting.get("has_agenda", False):
        verdict = "KILL"
    elif decisions < DECISION_FLOOR or (attendees >= BIG_ROOM and meeting.get("type") != "broadcast"):
        verdict = "ASYNC"
    elif reasons and weekly_hours >= 2.0:
        verdict = "TRIM"
    elif reasons:
        verdict = "TRIM"
    else:
        verdict = "KEEP"
    return verdict, reasons


def analyse_meetings(doc: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Compute weekly person-hours, cost and a verdict for every recurring meeting."""
    costs = cost_table(doc)
    rows: List[Dict[str, Any]] = []
    for m in doc["meetings"]:
        occ = float(m.get("occurrences_per_week", 1))
        hours_each = float(m.get("duration_min", 30)) / 60.0
        attendees = m.get("attendees", [])
        person_hours = hours_each * occ * len(attendees)
        weekly_cost = hours_each * occ * sum(costs.get(a, 0.0) for a in attendees)
        verdict, reasons = score_meeting(m, person_hours)
        rows.append({
            "id": m.get("id", m.get("title", "?")),
            "title": m.get("title", "untitled"),
            "attendees": len(attendees),
            "weekly_person_hours": round(person_hours, 2),
            "weekly_cost": round(weekly_cost, 2),
            "annual_cost": round(weekly_cost * 46, 2),
            "verdict": verdict,
            "reasons": reasons,
        })
    return sorted(rows, key=lambda r: r["weekly_cost"], reverse=True)


def analyse_people(doc: Dict[str, Any], maker_target: float) -> List[Dict[str, Any]]:
    """Compute each person's weekly meeting hours and remaining uninterrupted maker time."""
    load: Dict[str, float] = defaultdict(float)
    for m in doc["meetings"]:
        hours = float(m.get("duration_min", 30)) / 60.0 * float(m.get("occurrences_per_week", 1))
        for a in m.get("attendees", []):
            load[a] += hours
    rows = []
    for person in doc["people"]:
        hours = round(load.get(person["id"], 0.0), 2)
        maker = round(WORK_WEEK_HOURS - hours, 2)
        rows.append({
            "id": person["id"],
            "name": person.get("name", person["id"]),
            "role": person.get("role", ""),
            "meeting_hours": hours,
            "share_of_week_pct": round(hours / WORK_WEEK_HOURS * 100, 1),
            "maker_hours": maker,
            "below_maker_target": maker < maker_target,
        })
    return sorted(rows, key=lambda r: r["meeting_hours"], reverse=True)


def find_overlaps(doc: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Find meetings on the same day whose times collide for at least one shared attendee."""
    clashes = []
    meetings = [m for m in doc["meetings"] if m.get("day") and m.get("start_utc")]
    for i, a in enumerate(meetings):
        for b in meetings[i + 1:]:
            if a.get("day") != b.get("day"):
                continue
            a_start, b_start = _minutes(a["start_utc"]), _minutes(b["start_utc"])
            a_end = a_start + int(a.get("duration_min", 30))
            b_end = b_start + int(b.get("duration_min", 30))
            if a_start < b_end and b_start < a_end:
                shared = sorted(set(a.get("attendees", [])) & set(b.get("attendees", [])))
                if shared:
                    clashes.append({
                        "day": a["day"],
                        "meetings": [a.get("title"), b.get("title")],
                        "double_booked": shared,
                    })
    return clashes


def propose_consolidation(doc: Dict[str, Any], rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Propose merges for meeting pairs whose attendee sets overlap by 60% or more."""
    by_id = {r["id"]: r for r in rows}
    proposals = []
    meetings = doc["meetings"]
    for i, a in enumerate(meetings):
        for b in meetings[i + 1:]:
            sa, sb = set(a.get("attendees", [])), set(b.get("attendees", []))
            if not sa or not sb:
                continue
            jaccard = len(sa & sb) / len(sa | sb)
            if jaccard >= 0.6 and a.get("type") == b.get("type"):
                smaller = min(by_id[a.get("id", "?")]["weekly_person_hours"],
                              by_id[b.get("id", "?")]["weekly_person_hours"])
                proposals.append({
                    "merge": [a.get("title"), b.get("title")],
                    "audience_overlap_pct": round(jaccard * 100, 1),
                    "weekly_person_hours_reclaimed": round(smaller, 2),
                })
    return sorted(proposals, key=lambda p: p["weekly_person_hours_reclaimed"], reverse=True)


def output(report: Dict[str, Any], fmt: str) -> None:
    """Print the audit as JSON or as a human-readable report."""
    if fmt == "json":
        print(json.dumps(report, indent=2))
        return
    t = report["totals"]
    print(f"MEETING LOAD AUDIT — {report['team']}")
    print("=" * 62)
    print(f"Recurring meetings : {t['meetings']}")
    print(f"Weekly person-hours: {t['weekly_person_hours']}")
    print(f"Weekly cost        : {t['currency']} {t['weekly_cost']:,.0f}"
          f"   (annualised {t['currency']} {t['annual_cost']:,.0f})")
    print(f"Reclaimable        : {t['reclaimable_person_hours']} person-hours/week\n")

    print("PER-MEETING VERDICTS")
    print(f"{'verdict':<8}{'h/wk':>6}{'cost/wk':>10}  title")
    for r in report["meetings"]:
        print(f"{r['verdict']:<8}{r['weekly_person_hours']:>6.1f}{r['weekly_cost']:>10,.0f}  {r['title']}")
        for reason in r["reasons"]:
            print(f"{'':<24}- {reason}")

    print("\nPER-PERSON LOAD")
    for p in report["people"]:
        flag = "  << below maker-time target" if p["below_maker_target"] else ""
        print(f"  {p['name']:<18}{p['meeting_hours']:>5.1f}h "
              f"({p['share_of_week_pct']:>4.1f}% of week), maker {p['maker_hours']:>5.1f}h{flag}")

    if report["overlaps"]:
        print("\nDOUBLE BOOKINGS")
        for c in report["overlaps"]:
            print(f"  {c['day']}: {c['meetings'][0]} vs {c['meetings'][1]} "
                  f"-> {', '.join(c['double_booked'])}")

    if report["consolidation"]:
        print("\nCONSOLIDATION PROPOSAL")
        for p in report["consolidation"]:
            print(f"  Merge '{p['merge'][0]}' + '{p['merge'][1]}' "
                  f"({p['audience_overlap_pct']}% same audience) "
                  f"-> reclaims {p['weekly_person_hours_reclaimed']}h/week")


def build_report(doc: Dict[str, Any], maker_target: float) -> Dict[str, Any]:
    """Assemble the full audit report from the parsed calendar document."""
    rows = analyse_meetings(doc)
    reclaimable = sum(r["weekly_person_hours"] for r in rows if r["verdict"] in ("KILL", "ASYNC"))
    return {
        "team": doc.get("team", "unnamed team"),
        "totals": {
            "meetings": len(rows),
            "weekly_person_hours": round(sum(r["weekly_person_hours"] for r in rows), 2),
            "weekly_cost": round(sum(r["weekly_cost"] for r in rows), 2),
            "annual_cost": round(sum(r["annual_cost"] for r in rows), 2),
            "reclaimable_person_hours": round(reclaimable, 2),
            "currency": doc.get("currency", "USD"),
        },
        "meetings": rows,
        "people": analyse_people(doc, maker_target),
        "overlaps": find_overlaps(doc),
        "consolidation": propose_consolidation(doc, rows),
    }


def main() -> None:
    """Parse arguments, run the audit and print the report."""
    parser = argparse.ArgumentParser(
        description="Audit recurring meetings for load, cost, overlap and low-value recurrences.")
    parser.add_argument("--input", required=True,
                        help="path to a calendar export JSON (people + meetings keys)")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                        help="output format (default: text)")
    parser.add_argument("--maker-hours-target", type=float, default=24.0,
                        help="uninterrupted hours per week each person needs (default: 24)")
    args = parser.parse_args()
    try:
        doc = load_calendar(Path(args.input))
        output(build_report(doc, args.maker_hours_target), args.format)
    except SystemExit:
        raise
    except (KeyError, TypeError, ValueError) as exc:
        print(f"error: malformed calendar data — {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
