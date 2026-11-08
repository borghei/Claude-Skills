#!/usr/bin/env python3
"""Consolidate questionnaire answers into a decision-record summary.

Reads the questionnaire that was sent and the responses that came back, then
reports, per question, who answered, what they said, how many said "don't
know", and where respondents disagree. Questions marked "critical" decide the
outcome: a critical question with no usable answer after the deadline falls
back to the questionnaire's default decision; before the deadline it needs a
follow-up. Deterministic: the deadline is compared against --today.

Usage:
    python3 answer_consolidator.py --input assets/sample_questionnaire_clean.json \
        --answers assets/sample_answers.json
    python3 answer_consolidator.py --input q.json --answers a.json --today 2026-11-21 --format json
"""

import argparse
import json
import statistics
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List

DONT_KNOW = {"dont-know", "don't know", "not sure", "unknown", "n/a", "?"}
# Numbers whose spread exceeds this share of the median count as a disagreement.
NUMBER_SPREAD_LIMIT = 0.5


def parse_day(value: str, label: str) -> date:
    """Parse a YYYY-MM-DD string or raise a readable ValueError."""
    try:
        return datetime.strptime(str(value)[:10], "%Y-%m-%d").date()
    except ValueError:
        raise ValueError(f"{label} {value!r} is not a YYYY-MM-DD date")


def load_json(path: str) -> Any:
    """Load a JSON file, letting the caller map errors to exit codes."""
    return json.loads(Path(path).read_text(encoding="utf-8"))


def is_dont_know(value: Any) -> bool:
    """True when an answer is an explicit 'I don't know'."""
    return isinstance(value, str) and value.strip().lower() in DONT_KNOW


def detect_conflict(fmt: str, values: List[Any]) -> str:
    """Return a short conflict description, or '' when respondents agree."""
    if len(values) < 2:
        return ""
    if fmt in ("pick-one", "yes-no"):
        # A yes-no answer may carry its condition ("no - if encrypted"); compare the verdict only.
        keys = [str(v).strip().lower() for v in values]
        if fmt == "yes-no":
            keys = [k.split()[0].strip(",.;:-") if k.split() else k for k in keys]
        distinct = sorted(set(keys))
        return f"split answers: {', '.join(distinct)}" if len(distinct) > 1 else ""
    if fmt == "ranked":
        firsts = sorted({str(v[0]).strip().lower() for v in values if isinstance(v, list) and v})
        return f"different first choices: {', '.join(firsts)}" if len(firsts) > 1 else ""
    if fmt == "number":
        nums = []
        for v in values:
            try:
                nums.append(float(v))
            except (TypeError, ValueError):
                return "non-numeric answer to a number question"
        mid = statistics.median(nums)
        spread = max(nums) - min(nums)
        if mid and spread / abs(mid) > NUMBER_SPREAD_LIMIT:
            return f"numbers range {min(nums):g}-{max(nums):g} (median {mid:g})"
    return ""


def consolidate(q: Dict[str, Any], answers: Dict[str, Any], today: date) -> Dict[str, Any]:
    """Merge responses into per-question results and an overall decision state."""
    questions = q.get("questions")
    if not isinstance(questions, list) or not questions:
        raise ValueError("questionnaire needs a non-empty 'questions' list")
    responses = answers.get("responses") if isinstance(answers, dict) else None
    if not isinstance(responses, list):
        raise ValueError("answers file needs a 'responses' list")
    deadline = parse_day(q["deadline"], "deadline") if q.get("deadline") else None
    past_deadline = bool(deadline and today > deadline)
    recipients = [str(r) for r in (q.get("to") or [])]
    responded = [str(r.get("respondent", "?")) for r in responses]
    known_ids = {str(item.get("id")) for item in questions}

    results: List[Dict[str, Any]] = []
    for item in questions:
        qid = str(item.get("id"))
        fmt = str(item.get("format", ""))
        given, dont_know = [], []
        for resp in responses:
            val = (resp.get("answers") or {}).get(qid)
            if val is None or (isinstance(val, str) and not val.strip()):
                continue
            (dont_know if is_dont_know(val) else given).append({"respondent": resp.get("respondent", "?"), "value": val})
        conflict = detect_conflict(fmt, [g["value"] for g in given])
        critical = bool(item.get("critical"))
        if given and not conflict:
            state = "resolved"
        elif conflict:
            state = "conflict"
        elif past_deadline and critical:
            state = "default-applied"
        else:
            state = "unanswered"
        results.append({"id": qid, "text": item.get("text", ""), "format": fmt, "critical": critical,
                        "state": state, "answers": given, "dont_know": [d["respondent"] for d in dont_know],
                        "conflict": conflict})

    stray = sorted({k for r in responses for k in (r.get("answers") or {}) if k not in known_ids})
    blocking = [r for r in results if r["critical"] and r["state"] in ("conflict", "unanswered")]
    if any(r["state"] == "default-applied" for r in results) and not blocking:
        outcome = "default-applied"
    elif blocking:
        outcome = "needs-follow-up"
    else:
        outcome = "ready-to-record"
    return {
        "title": q.get("title", "(untitled)"), "decision": q.get("decision", ""),
        "deadline": str(deadline) if deadline else None, "today": str(today), "past_deadline": past_deadline,
        "default_if_no_answer": q.get("default_if_no_answer", ""),
        "recipients": recipients, "responded": responded,
        "missing_respondents": [r for r in recipients if r not in responded],
        "stray_answer_ids": stray, "outcome": outcome,
        "blocking_questions": [r["id"] for r in blocking], "questions": results,
    }


def render_value(value: Any) -> str:
    """Format one answer value for text output."""
    return " > ".join(map(str, value)) if isinstance(value, list) else str(value)


def output(report: Dict[str, Any], fmt: str) -> None:
    """Print the consolidation as text or JSON."""
    if fmt == "json":
        print(json.dumps(report, indent=2))
        return
    print(f"DECISION RECORD DRAFT  {report['title']}")
    print(f"  Decision: {report['decision']}")
    print(f"  Outcome: {report['outcome'].upper()}  (deadline {report['deadline']}, today {report['today']})")
    print(f"  Responded: {', '.join(report['responded']) or 'nobody'}")
    if report["missing_respondents"]:
        print(f"  No response yet: {', '.join(report['missing_respondents'])}")
    if report["outcome"] == "default-applied":
        print(f"  Default applied: {report['default_if_no_answer']}")
    for r in report["questions"]:
        flag = "*" if r["critical"] else " "
        print(f"\n {flag}{r['id']} [{r['state']}] {r['text']}")
        for a in r["answers"]:
            print(f"      {a['respondent']}: {render_value(a['value'])}")
        if r["dont_know"]:
            print(f"      don't know: {', '.join(r['dont_know'])}")
        if r["conflict"]:
            print(f"      CONFLICT: {r['conflict']}")
    if report["stray_answer_ids"]:
        print(f"\n  Answers to unknown question ids ignored: {', '.join(report['stray_answer_ids'])}")
    if report["blocking_questions"]:
        print(f"\n  Follow up before recording: {', '.join(report['blocking_questions'])} (* = critical)")


def main() -> None:
    """Parse arguments, consolidate answers, exit 1 when a critical question still blocks."""
    parser = argparse.ArgumentParser(description="Consolidate questionnaire answers into a decision-record draft.")
    parser.add_argument("--input", required=True, help="questionnaire JSON that was sent")
    parser.add_argument("--answers", required=True, help="responses JSON ({'responses': [...]})")
    parser.add_argument("--today", default="2026-11-08", help="reference date YYYY-MM-DD (default 2026-11-08)")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="output format (default: text)")
    args = parser.parse_args()
    try:
        report = consolidate(load_json(args.input), load_json(args.answers), parse_day(args.today, "--today"))
    except FileNotFoundError as exc:
        print(f"error: file not found: {exc.filename}", file=sys.stderr)
        sys.exit(2)
    except json.JSONDecodeError as exc:
        print(f"error: invalid JSON: {exc}", file=sys.stderr)
        sys.exit(2)
    except (ValueError, TypeError, AttributeError, KeyError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(2)
    output(report, args.format)
    sys.exit(1 if report["outcome"] == "needs-follow-up" else 0)


if __name__ == "__main__":
    main()
