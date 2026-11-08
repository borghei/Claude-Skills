#!/usr/bin/env python3
"""Lint an async decision questionnaire before it is sent.

Checks that the questionnaire names its purpose, the decision riding on it, a
deadline and the default that applies if nobody answers, and that every
question is neutral, asks one thing, and carries an answer format. Pick-one
questions need at least two options plus an escape option, and decision
options need stated trade-offs. Deterministic: dates are compared against
--today, never the system clock.

Usage:
    python3 questionnaire_linter.py --input assets/sample_questionnaire_flawed.json
    python3 questionnaire_linter.py --input q.json --today 2026-11-08 --format json
    python3 questionnaire_linter.py --input q.json --max-questions 8 --max-minutes 10
"""

import argparse
import json
import re
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List

FORMATS = {"pick-one", "ranked", "number", "yes-no", "free-text"}
LEADING = [
    r"\bdon'?t you (think|agree|feel)\b", r"\bwouldn'?t (it|you|that)\b", r"\bsurely\b",
    r"\bobviously\b", r"\bclearly\b", r"\bagree that\b", r"\bisn'?t it (true|better|obvious)\b",
    r"\bshouldn'?t we\b", r"\bright\?\s*$",
]
VAGUE = [r"\bthoughts\??\s*$", r"\bany feedback\b", r"\bany (comments|input)\b",
         r"\bwhat do you think\b", r"\bhow do you feel about\b", r"\bgeneral impressions?\b"]
ESCAPE_WORDS = ("none", "other", "neither", "something else", "don't know", "not sure")
DEFAULT_MAX_QUESTIONS = 10
DEFAULT_MAX_MINUTES = 15
MINUTES_PER_FORMAT = {"pick-one": 1.0, "yes-no": 0.75, "number": 1.5, "ranked": 2.0, "free-text": 3.0}


def finding(severity: str, where: str, code: str, message: str) -> Dict[str, str]:
    """Build one finding record."""
    return {"severity": severity, "where": where, "code": code, "message": message}


def parse_day(value: str, label: str) -> date:
    """Parse a YYYY-MM-DD string or raise a readable ValueError."""
    try:
        return datetime.strptime(str(value)[:10], "%Y-%m-%d").date()
    except ValueError:
        raise ValueError(f"{label} {value!r} is not a YYYY-MM-DD date")


def check_header(q: Dict[str, Any], today: date) -> List[Dict[str, str]]:
    """Check the send-level fields: purpose, decision, people, deadline, default."""
    out: List[Dict[str, str]] = []
    required = {
        "purpose": "no purpose — the recipient cannot tell why this matters",
        "decision": "no decision named — answers will not converge on anything",
        "deadline": "no deadline — async questionnaires without one are answered never",
        "default_if_no_answer": "no default decision if unanswered — silence then blocks the work",
        "context": "no context paragraph — the recipient is not inside your head",
    }
    for key, msg in required.items():
        if not str(q.get(key, "")).strip():
            out.append(finding("error", "header", f"missing-{key.replace('_', '-')}", msg))
    if not q.get("to"):
        out.append(finding("error", "header", "missing-recipient", "no recipient named"))
    if not str(q.get("use_of_answers", "")).strip():
        out.append(finding("warn", "header", "missing-use", "say how answers will be used and who sees them"))
    if q.get("deadline"):
        due = parse_day(q["deadline"], "deadline")
        if due < today:
            out.append(finding("error", "header", "deadline-past", f"deadline {due} is before {today}"))
        elif (due - today).days < 2:
            out.append(finding("warn", "header", "deadline-tight",
                               f"deadline gives under 2 days — async answers need slack"))
    context = str(q.get("context", ""))
    if len(context.split()) > 180:
        out.append(finding("warn", "header", "context-long",
                           f"context is {len(context.split())} words — keep it to one short paragraph"))
    if not str(q.get("closing_question", "")).strip():
        out.append(finding("warn", "header", "missing-catch-all", "add a closing 'anything we did not ask?'"))
    return out


def check_options(q: Dict[str, Any]) -> List[Dict[str, str]]:
    """Check decision options for trade-offs, a single recommendation, and an escape."""
    out: List[Dict[str, str]] = []
    options = q.get("options") or []
    if not options:
        out.append(finding("warn", "options", "no-options",
                           "no decision options listed — fine for pure discovery, weak for a decision"))
        return out
    if len(options) < 2:
        out.append(finding("error", "options", "single-option", "one option is a notification, not a choice"))
    recommended = [o for o in options if o.get("recommended")]
    if len(recommended) > 1:
        out.append(finding("error", "options", "multiple-recommended", "more than one option is marked recommended"))
    for opt in options:
        label = opt.get("id") or opt.get("label") or "?"
        if not str(opt.get("tradeoffs", "")).strip():
            out.append(finding("error", f"option {label}", "missing-tradeoffs",
                               "option has no stated trade-off — the recipient cannot weigh it"))
    labels = " ".join(str(o.get("label", "")).lower() for o in options)
    if not any(word in labels for word in ESCAPE_WORDS):
        out.append(finding("warn", "options", "no-escape-option", "add 'none of these / something else'"))
    return out


def check_question(item: Dict[str, Any], idx: int) -> List[Dict[str, str]]:
    """Check one question for neutrality, single focus, and an answer format."""
    out: List[Dict[str, str]] = []
    where = item.get("id") or f"Q{idx + 1}"
    text = str(item.get("text", "")).strip()
    if not text:
        return [finding("error", where, "empty-question", "question has no text")]
    lowered = text.lower()
    for pattern in LEADING:
        if re.search(pattern, lowered):
            out.append(finding("error", where, "leading", f"leading phrasing ('{re.search(pattern, lowered).group(0)}')"))
            break
    for pattern in VAGUE:
        if re.search(pattern, lowered):
            out.append(finding("error", where, "vague", "open-ended fishing question — ask for something specific"))
            break
    if text.count("?") > 1:
        out.append(finding("error", where, "compound", "more than one question mark — split it"))
    elif re.search(r"\?\s*\w", text) or re.search(r"\b(and|or) (also |should|would|could|do|does|is|are|can|will|what|how|why|when)\b", lowered):
        out.append(finding("error", where, "compound", "two asks joined in one question — split it"))
    fmt = item.get("format")
    if fmt not in FORMATS:
        out.append(finding("error", where, "missing-format",
                           f"answer format {fmt!r} not one of {', '.join(sorted(FORMATS))}"))
        return out
    choices = item.get("options") or []
    if fmt in ("pick-one", "ranked"):
        if len(choices) < 2:
            out.append(finding("error", where, "too-few-choices", f"{fmt} question needs at least 2 choices"))
        elif fmt == "pick-one" and not any(w in " ".join(map(str, choices)).lower() for w in ESCAPE_WORDS):
            out.append(finding("warn", where, "no-escape-choice", "add 'none / don't know' so nobody is forced"))
    if fmt == "number" and not str(item.get("unit", "")).strip():
        out.append(finding("error", where, "missing-unit", "number answer has no unit — you will get mixed units back"))
    if fmt == "free-text" and not item.get("max_words"):
        out.append(finding("warn", where, "uncapped-free-text", "cap free text (e.g. 50 words) to keep answers comparable"))
    if fmt == "yes-no" and not item.get("condition_prompt"):
        out.append(finding("warn", where, "yes-no-no-condition", "ask 'yes, if…' — bare yes/no hides the condition"))
    if not str(item.get("theme", "")).strip():
        out.append(finding("warn", where, "missing-theme", "group questions under a theme"))
    return out


def lint(q: Dict[str, Any], today: date, max_q: int, max_min: int) -> Dict[str, Any]:
    """Run every check and return the report."""
    if not isinstance(q, dict):
        raise ValueError("questionnaire must be a JSON object")
    questions = q.get("questions")
    if not isinstance(questions, list) or not questions:
        raise ValueError("questionnaire needs a non-empty 'questions' list")
    findings = check_header(q, today) + check_options(q)
    for idx, item in enumerate(questions):
        findings += check_question(item if isinstance(item, dict) else {}, idx)
    if len(questions) > max_q:
        findings.append(finding("error", "size", "too-many-questions",
                                f"{len(questions)} questions (budget {max_q}) — cut or send a second round"))
    estimate = sum(MINUTES_PER_FORMAT.get(i.get("format"), 2.0) for i in questions if isinstance(i, dict))
    stated = q.get("effort_minutes")
    if stated is None:
        findings.append(finding("warn", "size", "missing-effort", f"state the effort (estimated ~{estimate:.0f} min)"))
    elif float(stated) > max_min:
        findings.append(finding("error", "size", "effort-over-budget", f"stated effort {stated} min exceeds {max_min}"))
    if estimate > max_min:
        findings.append(finding("warn", "size", "estimate-over-budget",
                                f"answer formats imply ~{estimate:.0f} min, over the {max_min} min budget"))
    errors = sum(1 for f in findings if f["severity"] == "error")
    return {"title": q.get("title", "(untitled)"), "questions": len(questions),
            "estimated_minutes": round(estimate, 1), "errors": errors,
            "warnings": len(findings) - errors, "ready_to_send": errors == 0, "findings": findings}


def output(report: Dict[str, Any], fmt: str) -> None:
    """Print the report as text or JSON."""
    if fmt == "json":
        print(json.dumps(report, indent=2))
        return
    status = "READY TO SEND" if report["ready_to_send"] else "NOT READY"
    print(f"{status}  {report['title']}")
    print(f"  {report['questions']} questions, ~{report['estimated_minutes']} min to answer, "
          f"{report['errors']} errors, {report['warnings']} warnings")
    for f in sorted(report["findings"], key=lambda x: x["severity"] != "error"):
        print(f"  [{f['severity']:5}] {f['where']:<10} {f['code']:<22} {f['message']}")


def main() -> None:
    """Parse arguments, lint the questionnaire, and exit 1 if any error finding."""
    parser = argparse.ArgumentParser(description="Lint an async decision questionnaire before sending it.")
    parser.add_argument("--input", required=True, help="questionnaire JSON file")
    parser.add_argument("--today", default="2026-11-08", help="reference date YYYY-MM-DD (default 2026-11-08)")
    parser.add_argument("--max-questions", type=int, default=DEFAULT_MAX_QUESTIONS, help="question budget (default 10)")
    parser.add_argument("--max-minutes", type=int, default=DEFAULT_MAX_MINUTES, help="effort budget in minutes (default 15)")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="output format (default: text)")
    args = parser.parse_args()
    try:
        data = json.loads(Path(args.input).read_text(encoding="utf-8"))
        report = lint(data, parse_day(args.today, "--today"), args.max_questions, args.max_minutes)
    except FileNotFoundError:
        print(f"error: file not found: {args.input}", file=sys.stderr)
        sys.exit(2)
    except json.JSONDecodeError as exc:
        print(f"error: {args.input} is not valid JSON: {exc}", file=sys.stderr)
        sys.exit(2)
    except (ValueError, TypeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(2)
    output(report, args.format)
    sys.exit(0 if report["ready_to_send"] else 1)


if __name__ == "__main__":
    main()
