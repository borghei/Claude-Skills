#!/usr/bin/env python3
"""Diagnose a recurring meeting series: decision density, churn, and attendance decay.

Usage:
    python3 meeting_series_diagnostic.py --input sample_series.json
    python3 meeting_series_diagnostic.py --input sample_series.json --format json
    python3 meeting_series_diagnostic.py --input sample_series.json --churn-threshold 2
"""

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Tuple

# Decisions per person-hour. Below the floor a series is not deciding anything.
DENSITY_FLOOR = 0.15
DENSITY_HEALTHY = 0.35


def load_series(path: Path) -> Dict[str, Any]:
    """Read and validate the meeting-series export."""
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise SystemExit(f"error: file not found: {path}")
    except json.JSONDecodeError as exc:
        raise SystemExit(f"error: {path} is not valid JSON ({exc.msg}, line {exc.lineno})")
    if not isinstance(doc, dict) or not doc.get("occurrences"):
        raise SystemExit("error: series JSON needs a non-empty 'occurrences' list")
    return doc


def occurrence_rows(doc: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Compute per-occurrence person-hours, decision density and hygiene flags."""
    invited = int(doc.get("invited", 0)) or None
    rows = []
    for occ in doc["occurrences"]:
        attended = int(occ.get("attended", 0))
        hours = float(occ.get("duration_min", 30)) / 60.0
        person_hours = hours * attended
        decisions = int(occ.get("decisions", 0))
        rows.append({
            "date": occ.get("date", "?"),
            "duration_min": occ.get("duration_min", 30),
            "attended": attended,
            "attendance_rate": round(attended / invited * 100, 1) if invited else None,
            "person_hours": round(person_hours, 2),
            "decisions": decisions,
            "actions": int(occ.get("actions", 0)),
            "density": round(decisions / person_hours, 3) if person_hours else 0.0,
            "agenda": bool(occ.get("agenda_posted", False)),
            "notes": bool(occ.get("notes_published", False)),
            "topics": [t.lower().strip() for t in occ.get("topics", [])],
        })
    return rows


def find_churn(rows: List[Dict[str, Any]], threshold: int) -> List[Dict[str, Any]]:
    """Find topics that recur without the series resolving them.

    Notes rarely attribute a decision to a specific topic, so this uses decisions
    recorded in the same occurrence as a proxy: a topic is churning when it has
    recurred at least `threshold` times and fewer than a third of those
    appearances coincided with any decision at all.
    """
    appearances: Counter = Counter()
    decided_alongside: Counter = Counter()
    for row in rows:
        for topic in row["topics"]:
            appearances[topic] += 1
            decided_alongside[topic] += row["decisions"]
    churning = []
    for topic, count in appearances.items():
        ratio = decided_alongside[topic] / count
        if count >= threshold and ratio < 0.34:
            churning.append({"topic": topic, "appearances": count,
                             "decisions_while_discussed": decided_alongside[topic],
                             "decisions_per_appearance": round(ratio, 2)})
    return sorted(churning, key=lambda c: -c["appearances"])


def attendance_trend(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Compare attendance in the first and second half of the series."""
    if len(rows) < 4:
        return {"comparable": False}
    mid = len(rows) // 2
    early = sum(r["attended"] for r in rows[:mid]) / mid
    late = sum(r["attended"] for r in rows[mid:]) / (len(rows) - mid)
    delta = round((late - early) / early * 100, 1) if early else 0.0
    return {"comparable": True, "early_avg": round(early, 1), "late_avg": round(late, 1),
            "change_pct": delta, "decaying": delta <= -15.0}


def diagnose(doc: Dict[str, Any], rows: List[Dict[str, Any]], churn_threshold: int) -> Dict[str, Any]:
    """Assemble the series diagnosis, verdict and prescription."""
    n = len(rows)
    total_hours = sum(r["person_hours"] for r in rows)
    total_decisions = sum(r["decisions"] for r in rows)
    total_actions = sum(r["actions"] for r in rows)
    density = round(total_decisions / total_hours, 3) if total_hours else 0.0
    agenda_rate = round(sum(1 for r in rows if r["agenda"]) / n * 100, 1)
    notes_rate = round(sum(1 for r in rows if r["notes"]) / n * 100, 1)
    empty = [r for r in rows if r["decisions"] == 0 and r["actions"] == 0]
    churn = find_churn(rows, churn_threshold)
    trend = attendance_trend(rows)

    verdict, prescription = _verdict(density, empty, n, churn, agenda_rate, notes_rate, trend)
    return {
        "series": doc.get("title", "untitled series"),
        "occurrences": n,
        "totals": {
            "person_hours": round(total_hours, 2),
            "decisions": total_decisions,
            "actions": total_actions,
            "decision_density": density,
            "empty_occurrences": len(empty),
            "agenda_compliance_pct": agenda_rate,
            "notes_compliance_pct": notes_rate,
        },
        "verdict": verdict,
        "prescription": prescription,
        "churning_topics": churn,
        "attendance": trend,
        "detail": rows,
    }


def _verdict(density: float, empty: List[Dict[str, Any]], n: int, churn: List[Dict[str, Any]],
             agenda_rate: float, notes_rate: float, trend: Dict[str, Any]) -> Tuple[str, List[str]]:
    """Pick the headline verdict and the ordered list of fixes."""
    fixes: List[str] = []
    if agenda_rate < 80:
        fixes.append(f"Agenda posted for only {agenda_rate}% of occurrences — make "
                     "no-agenda-by-start-time an automatic cancellation.")
    if notes_rate < 80:
        fixes.append(f"Notes published for only {notes_rate}% of occurrences — absentees "
                     "cannot catch up, so attendance becomes compulsory by default.")
    for c in churn:
        tail = ("with no decision" if not c["decisions_while_discussed"]
                else f"alongside only {c['decisions_while_discussed']} decision(s)")
        fixes.append(f"'{c['topic']}' has come up {c['appearances']} times {tail} — "
                     "name a decision owner and a deadline, or drop it from the agenda.")
    if trend.get("decaying"):
        fixes.append(f"Attendance fell {abs(trend['change_pct'])}% across the series — "
                     "people are voting with their calendars.")
    if len(empty) / n >= 0.4:
        fixes.append(f"{len(empty)} of {n} occurrences produced neither a decision nor an "
                     "action — those slots were a written update.")

    if density < DENSITY_FLOOR and len(empty) / n >= 0.4:
        return ("KILL — the series does not decide anything and frequently produces no output at all.",
                fixes + ["Cancel it. Replace with a written update and a comment window."])
    if density < DENSITY_FLOOR:
        return ("CONVERT TO ASYNC — decisions per person-hour are below the floor.",
                fixes + ["Move the standing content to a written update; book time only "
                         "when a specific decision stalls."])
    if density < DENSITY_HEALTHY:
        return ("RESTRUCTURE — the series decides things, but inefficiently.",
                fixes + ["Cut duration 25% and trim the invite list to the people who "
                         "actually hold the decision."])
    return ("KEEP — decision density is healthy.",
            fixes or ["No structural changes needed."])


def output(report: Dict[str, Any], fmt: str) -> None:
    """Print the diagnosis as JSON or as a human-readable report."""
    if fmt == "json":
        print(json.dumps(report, indent=2))
        return
    t = report["totals"]
    print(f"MEETING SERIES DIAGNOSTIC — {report['series']}")
    print("=" * 66)
    print(f"{report['occurrences']} occurrences | {t['person_hours']} person-hours | "
          f"{t['decisions']} decisions | {t['actions']} actions")
    print(f"Decision density: {t['decision_density']} per person-hour "
          f"(floor {DENSITY_FLOOR}, healthy {DENSITY_HEALTHY})")
    print(f"Agenda compliance {t['agenda_compliance_pct']}% | "
          f"Notes compliance {t['notes_compliance_pct']}% | "
          f"Empty occurrences {t['empty_occurrences']}")
    print(f"\n{report['verdict']}\n")
    print("PRESCRIPTION")
    for i, fix in enumerate(report["prescription"], 1):
        print(f"  {i}. {fix}")
    if report["churning_topics"]:
        print("\nCHURNING TOPICS (recur often, rarely resolved)")
        for c in report["churning_topics"]:
            print(f"  {c['appearances']}x  {c['topic']:<32}"
                  f"{c['decisions_per_appearance']} decisions/appearance")
    a = report["attendance"]
    if a.get("comparable"):
        print(f"\nATTENDANCE  first half {a['early_avg']} -> second half {a['late_avg']} "
              f"({a['change_pct']:+}%)")
    print("\nPER OCCURRENCE")
    print(f"  {'date':<13}{'att':>4}{'min':>5}{'dec':>5}{'act':>5}{'density':>9}  hygiene")
    for r in report["detail"]:
        hygiene = ("agenda" if r["agenda"] else "NO-AGENDA") + "/" + ("notes" if r["notes"] else "NO-NOTES")
        print(f"  {r['date']:<13}{r['attended']:>4}{r['duration_min']:>5}{r['decisions']:>5}"
              f"{r['actions']:>5}{r['density']:>9.3f}  {hygiene}")


def main() -> None:
    """Parse arguments, diagnose the meeting series and print the report."""
    parser = argparse.ArgumentParser(
        description="Diagnose a recurring meeting series for decision density, topic churn "
                    "and attendance decay.")
    parser.add_argument("--input", required=True, help="path to a meeting-series JSON export")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                        help="output format (default: text)")
    parser.add_argument("--churn-threshold", type=int, default=3,
                        help="times a topic may recur undecided before it is flagged (default: 3)")
    args = parser.parse_args()
    try:
        doc = load_series(Path(args.input))
        rows = occurrence_rows(doc)
        output(diagnose(doc, rows, args.churn_threshold), args.format)
    except SystemExit:
        raise
    except (KeyError, TypeError, ValueError, ZeroDivisionError) as exc:
        print(f"error: malformed series data — {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
