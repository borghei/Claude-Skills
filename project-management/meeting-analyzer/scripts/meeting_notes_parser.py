#!/usr/bin/env python3
"""Extract decisions, action items and open questions from raw meeting notes.

Pattern-rule extraction only — no model calls, no network, fully deterministic.

Usage:
    python3 meeting_notes_parser.py --input sample_notes.md
    python3 meeting_notes_parser.py --input sample_notes.md --format json
    python3 meeting_notes_parser.py --input sample_notes.md --strict
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Strong cues fire anywhere, including in prose paragraphs. Weak cues only fire
# on list items or under a matching section heading, where the surrounding
# structure already signals intent — this is what keeps discussion prose out of
# the action list.
DECISION_CUES = [
    r"^\s*decision\s*[:\-]", r"\bwe (?:have )?decided\b", r"\bdecided (?:to|that|on)\b",
    r"\bagreed (?:to|that|on)\b", r"\bwe(?:'| a)re going with\b",
    r"\bwe will (?:use|adopt|ship|keep|build|hold|move|go)\b",
    r"\bapproved\b", r"\bsigned?-off\b", r"\bresolved (?:to|that)\b", r"\bDECISION\b",
]
ACTION_CUES_STRONG = [
    r"^\s*(?:action|todo|next step)s?\s*[:\-]", r"\baction item\b", r"\bACTION\b", r"\[ \]",
    r"@[\w.\-]+\s+(?:to|will)\b", r"\btakes? (?:the )?action\b",
    r"^[A-Z][a-z]+(?:\s+[A-Z]\.)?\s+(?:will|to)\s+[a-z]+",
]
ACTION_CUES_WEAK = [
    r"\bwill\s+[a-z]+", r"\bto\s+(?:draft|write|send|update|investigate|schedule|confirm|review|scope|open|produce|chase|tell)\b",
    r"\bowns? (?:this|it)\b", r"\bfollows? up\b", r"\bshould (?:tell|send|update|check|confirm)\b",
    r"\bneeds? to\b",
]
QUESTION_CUES_STRONG = [
    r"^\s*(?:open question|question|unresolved|parked)s?\s*[:\-]", r"^\s*TBD\b",
    r"\bstill (?:unclear|unknown|open|undecided)\b", r"\bopen question\b",
    r"\bwe don'?t know\b", r"\bno resolution\b",
]
QUESTION_CUES_WEAK = [
    r"\bneeds? (?:more )?(?:investigation|research|input)\b", r"\bTBD\b", r"\?\s*$",
]
# "@name", "Owner: Name", "Name will ...", "(Name)"
OWNER_PATTERNS = [
    r"@([A-Za-z][\w.\-]{1,24})",
    r"\bowner\s*[:=]\s*([A-Z][\w.\-]*(?:\s+[A-Z]\.?)?)",
    r"^\s*(?:[-*]\s*)?(?:\[[ x]\]\s*)?([A-Z][a-z]+(?:\s+[A-Z]\.?)?)\s+(?:will|to|owns|takes)\b",
]
DATE_PATTERNS = [
    r"\b(\d{4}-\d{2}-\d{2})\b",
    r"\b(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*(?:\s+\d{4})?)\b",
    r"\b((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2}(?:,?\s+\d{4})?)\b",
    r"\b(?:by|due|before|eod|eow)\s+(next\s+\w+|this\s+\w+|\w+day)\b",
]
VAGUE_DATES = [r"\bsoon\b", r"\bnext sprint\b", r"\basap\b", r"\bwhen (?:we|i) (?:can|get)\b",
               r"\bin the next few (?:days|weeks)\b", r"\beventually\b", r"\bat some point\b"]


def read_notes(path: Path) -> List[str]:
    """Read a markdown or plain-text notes file into a list of non-empty lines."""
    try:
        raw = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise SystemExit(f"error: notes file not found: {path}")
    except UnicodeDecodeError:
        raise SystemExit(f"error: {path} is not UTF-8 text. Export notes as .md or .txt.")
    return [ln.rstrip() for ln in raw.splitlines()]


def clean(line: str) -> str:
    """Strip markdown list markers, checkboxes and leading labels from a line."""
    text = re.sub(r"^\s*(?:[-*+]|\d+[.)])\s*", "", line)
    text = re.sub(r"^\s*\[[ xX]\]\s*", "", text)
    text = re.sub(r"^\s*(?:decision|action|todo|ai|open question|question|next step)s?\s*[:\-]\s*",
                  "", text, flags=re.IGNORECASE)
    return text.strip()


def matches(text: str, cues: List[str]) -> bool:
    """Return True when any cue pattern fires on the line."""
    return any(re.search(cue, text, flags=re.IGNORECASE | re.MULTILINE) for cue in cues)


def find_owner(text: str) -> Optional[str]:
    """Extract the first plausible owner name from an action line, if present."""
    for pattern in OWNER_PATTERNS:
        found = re.search(pattern, text)
        if found:
            name = found.group(1).strip()
            if name.lower() not in {"we", "the", "team", "someone", "everyone", "tbd"}:
                return name
    return None


def find_due(text: str) -> Optional[str]:
    """Extract the first explicit due date from an action line, if present."""
    for pattern in DATE_PATTERNS:
        found = re.search(pattern, text, flags=re.IGNORECASE)
        if found:
            return found.group(1).strip()
    return None


def reflow(lines: List[str]) -> List[Tuple[int, str]]:
    """Join hard-wrapped continuation lines so a wrapped item is one unit.

    A line continues the previous one when it is not a heading, not a list item,
    and the previous line did not end on sentence-terminating punctuation.
    """
    units: List[Tuple[int, str]] = []
    for number, raw in enumerate(lines, 1):
        stripped = raw.strip()
        if not stripped:
            units.append((number, ""))
            continue
        starts_new = (stripped.startswith("#")
                      or bool(re.match(r"^\s*(?:[-*+]|\d+[.)]|\[[ xX]\]|>)", raw))
                      or not units or not units[-1][1]
                      or units[-1][1].endswith((".", "!", "?")))
        if starts_new:
            units.append((number, stripped))
        else:
            prev_no, prev_text = units[-1]
            units[-1] = (prev_no, f"{prev_text} {stripped}")
    return [(n, t) for n, t in units if t]


def classify(lines: List[str]) -> Dict[str, List[Dict[str, Any]]]:
    """Walk the notes and bucket each item into decisions, actions or open questions.

    Section headings ("## Decisions") set a sticky context so bare bullets under
    them inherit the right type even when the line itself carries no cue word.
    Weak cues only fire on list items or inside a matching section, which keeps
    discussion prose out of the action list.
    """
    out: Dict[str, List[Dict[str, Any]]] = {"decisions": [], "actions": [], "questions": []}
    section: Optional[str] = None
    for number, raw in reflow(lines):
        if raw.lstrip().startswith("#"):
            head = raw.lower()
            section = ("decisions" if "decision" in head else
                       "actions" if any(w in head for w in ("action", "todo", "next step")) else
                       "questions" if any(w in head for w in ("question", "parked", "unresolved")) else
                       None)
            continue
        text = clean(raw)
        if len(text) < 8:
            continue
        bullet = bool(re.match(r"^\s*(?:[-*+]|\d+[.)]|\[[ xX]\])", raw))
        structured = bullet or section is not None
        if matches(raw, DECISION_CUES):
            kind: Optional[str] = "decisions"
        elif matches(raw, ACTION_CUES_STRONG):
            kind = "actions"
        elif matches(raw, QUESTION_CUES_STRONG):
            kind = "questions"
        elif structured and matches(raw, ACTION_CUES_WEAK):
            kind = "actions"
        elif structured and matches(raw, QUESTION_CUES_WEAK):
            kind = "questions"
        else:
            kind = section if bullet else None
        if kind is None:
            continue
        item: Dict[str, Any] = {"line": number, "text": text}
        if kind == "actions":
            # Owner and date detection runs on the cleaned text so that leading
            # labels ("ACTION:") and list markers do not block the ^Name anchor.
            item["owner"] = find_owner(text)
            item["due"] = find_due(text)
            item["vague_due"] = matches(text, VAGUE_DATES) and item["due"] is None
            gaps = []
            if not item["owner"]:
                gaps.append("no owner — an action owned by 'the team' is owned by nobody")
            if not item["due"]:
                gaps.append("no due date — reads as 'someday'" if not item["vague_due"]
                            else "due date is vague ('soon', 'next sprint') — pin a calendar date")
            item["gaps"] = gaps
            item["complete"] = not gaps
        out[kind].append(item)
    return out


def build_report(path: Path, items: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
    """Assemble extraction counts, completeness rate and a meeting verdict."""
    actions = items["actions"]
    complete = [a for a in actions if a["complete"]]
    rate = round(len(complete) / len(actions) * 100, 1) if actions else 0.0
    decisions = len(items["decisions"])
    if decisions == 0 and not actions:
        verdict = "NO OUTPUT — this meeting produced neither a decision nor an action. Cancel or restructure it."
    elif decisions == 0:
        verdict = "NO DECISIONS — actions without decisions means the group is coordinating, not deciding. Consider async."
    elif rate < 60 and actions:
        verdict = f"WEAK ACCOUNTABILITY — only {rate}% of actions have both an owner and a date."
    else:
        verdict = "HEALTHY — decisions recorded and actions are attributable."
    return {
        "source": str(path),
        "counts": {"decisions": decisions, "actions": len(actions), "questions": len(items["questions"])},
        "action_completeness_pct": rate,
        "incomplete_actions": len(actions) - len(complete),
        "verdict": verdict,
        **items,
    }


def output(report: Dict[str, Any], fmt: str) -> None:
    """Print the extraction as JSON or as a human-readable report."""
    if fmt == "json":
        print(json.dumps(report, indent=2))
        return
    c = report["counts"]
    print(f"MEETING NOTES EXTRACTION — {report['source']}")
    print("=" * 66)
    print(f"Decisions {c['decisions']} | Actions {c['actions']} "
          f"({report['action_completeness_pct']}% fully specified) | Open questions {c['questions']}")
    print(f"\n{report['verdict']}\n")
    print("DECISIONS")
    for d in report["decisions"] or []:
        print(f"  L{d['line']:<4} {d['text']}")
    if not report["decisions"]:
        print("  (none found)")
    print("\nACTION ITEMS")
    for a in report["actions"] or []:
        mark = "OK " if a["complete"] else "!! "
        print(f"  {mark}L{a['line']:<4} {a['text']}")
        print(f"        owner: {a['owner'] or '(none)':<14} due: {a['due'] or '(none)'}")
        for gap in a["gaps"]:
            print(f"        gap: {gap}")
    if not report["actions"]:
        print("  (none found)")
    print("\nOPEN QUESTIONS")
    for q in report["questions"] or []:
        print(f"  L{q['line']:<4} {q['text']}")
    if not report["questions"]:
        print("  (none found)")


def main() -> None:
    """Parse arguments, extract meeting artefacts and print the report."""
    parser = argparse.ArgumentParser(
        description="Extract decisions, actions and open questions from meeting notes "
                    "using deterministic pattern rules.")
    parser.add_argument("--input", required=True, help="path to a markdown or plain-text notes file")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                        help="output format (default: text)")
    parser.add_argument("--strict", action="store_true",
                        help="exit 1 if any action item is missing an owner or a due date")
    args = parser.parse_args()
    try:
        path = Path(args.input)
        report = build_report(path, classify(read_notes(path)))
        output(report, args.format)
        if args.strict and report["incomplete_actions"]:
            print(f"\nstrict: {report['incomplete_actions']} action(s) missing an owner or a date",
                  file=sys.stderr)
            sys.exit(1)
    except SystemExit:
        raise
    except (re.error, TypeError, ValueError) as exc:
        print(f"error: could not parse the notes — {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
