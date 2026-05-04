#!/usr/bin/env python3
"""
Transcript Analyzer — extract decisions, action items, open questions,
risks, and quotes from a meeting transcript.

Usage:
    python transcript_analyzer.py transcript.txt
    python transcript_analyzer.py transcript.txt --json

Expected transcript format (one turn per line):
    Speaker: utterance
"""

import argparse
import json
import re
import sys
from pathlib import Path


DECISION_MARKERS = [
    r"\bwe (?:decided|agreed|will go with|are going with|chose|are choosing)\b",
    r"\b(?:decision|decided|agreed) (?:is|to)\b",
    r"\b(?:let's|we'll) (?:go with|move forward with|ship)\b",
    r"\bfinal call (?:is|on)\b",
    r"\bsign[- ]?off\b",
]

ACTION_MARKERS = [
    r"\b(?:i|we|i'll|we'll|i will|we will) (?:will |'ll )?(?:send|share|draft|review|prepare|set up|schedule|build|ship|own|take|follow up|circle back|sync|email|message|update|investigate|test|deploy|publish|hand off)\b",
    r"\bfollow up\b",
    r"\baction item\b",
    r"\bnext step(?:s)?\b",
    r"\b(?:i'll|we'll) get (?:that|this) (?:done|to you|over)\b",
    r"\b(?:i|we) (?:can|need to|should|have to|will) (?:send|share|draft|review|prepare|set up|schedule|build|ship|own|take|follow up|circle back|sync|email|message|update|investigate|test|deploy|publish|hand off)\b",
]

RISK_MARKERS = [
    r"\brisk\b",
    r"\bconcern\b",
    r"\bblocker\b",
    r"\bblocked on\b",
    r"\bif (?:.*)(?:slip|miss|fail|break)\b",
    r"\bworried (?:about|that)\b",
]

PAIN_MARKERS = [
    r"\b(?:painful|frustrat\w+|struggle|struggling|hard to|difficult to|takes (?:way )?too long|wastes? (?:my |our )?time)\b",
    r"\bhate (?:that|when|how)\b",
    r"\bwish (?:we|i|it) (?:could|had|would)\b",
    r"\b(?:problem|issue) (?:is|with)\b",
]

DUE_DATE_PATTERNS = [
    r"\bby (?:end of )?(?:today|tomorrow)\b",
    r"\b(?:today|tomorrow)\b",
    r"\bby (?:end of )?(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b",
    r"\b(?:by |on )(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b",
    r"\bby (?:next |this )?(?:week|month|quarter)\b",
    r"\bby \w+ \d{1,2}\b",
    r"\b(?:eod|eow|cob)\b",
    r"\b\d{1,2}/\d{1,2}\b",
]


def parse_transcript(text):
    """Yield (speaker, utterance) pairs."""
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        m = re.match(r"^([A-Z][\w .'-]{0,40}?):\s*(.+)$", line)
        if m:
            yield m.group(1).strip(), m.group(2).strip()
        else:
            # Continuation or non-speaker line — attach to previous speaker as anonymous
            yield "", line


def split_sentences(text):
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p.strip() for p in parts if p.strip()]


def matches_any(sentence, patterns):
    s = sentence.lower()
    for p in patterns:
        if re.search(p, s):
            return True
    return False


def extract_due_date(sentence):
    s = sentence.lower()
    for pattern in DUE_DATE_PATTERNS:
        m = re.search(pattern, s)
        if m:
            return m.group(0).strip()
    return None


def guess_owner(sentence, current_speaker):
    """Heuristic: if speaker says 'I will', they own it.
    If they say 'X will' or 'X is going to', X owns it."""
    s = sentence.strip()
    if re.search(r"\b(i|i'll|i will|i'm going to|i can|i need to|i should)\b", s, re.IGNORECASE):
        return current_speaker or "self"
    m = re.search(r"\b([A-Z][a-zA-Z]{1,30}) (?:will|'ll|is going to|can|needs to|should|to)\b", s)
    if m and m.group(1).lower() not in {"we", "they", "you", "i"}:
        return m.group(1)
    if re.search(r"\bwe (?:will|'ll|are going to|can|need to|should)\b", s, re.IGNORECASE):
        return "team"
    return current_speaker or "unassigned"


def analyze(text):
    decisions = []
    actions = []
    questions = []
    risks = []
    pains = []
    quotes = []

    for speaker, utterance in parse_transcript(text):
        for sentence in split_sentences(utterance):
            if matches_any(sentence, DECISION_MARKERS):
                decisions.append({"speaker": speaker, "text": sentence})
            if matches_any(sentence, ACTION_MARKERS):
                actions.append({
                    "owner": guess_owner(sentence, speaker),
                    "due": extract_due_date(sentence),
                    "text": sentence,
                })
            if sentence.endswith("?"):
                questions.append({"speaker": speaker, "text": sentence})
            if matches_any(sentence, RISK_MARKERS):
                risks.append({"speaker": speaker, "text": sentence})
            if matches_any(sentence, PAIN_MARKERS):
                pains.append({"speaker": speaker, "text": sentence})
            if speaker and len(sentence.split()) > 12:
                quotes.append({"speaker": speaker, "text": sentence})

    # Dedupe items (same-text duplicates)
    def dedupe(items, key="text"):
        seen = set()
        out = []
        for item in items:
            t = item.get(key, "").lower().strip()
            if t and t not in seen:
                seen.add(t)
                out.append(item)
        return out

    return {
        "decisions": dedupe(decisions),
        "action_items": dedupe(actions),
        "open_questions": dedupe(questions),
        "risks": dedupe(risks),
        "pains": dedupe(pains),
        "quotes": dedupe(quotes)[:20],
    }


def render_human(result):
    lines = []
    sections = [
        ("Decisions", result["decisions"], None),
        ("Action items", result["action_items"], "action"),
        ("Open questions", result["open_questions"], None),
        ("Risks", result["risks"], None),
        ("Pains", result["pains"], None),
        ("Notable quotes", result["quotes"], None),
    ]
    for title, items, kind in sections:
        lines.append(f"\n## {title} ({len(items)})")
        if not items:
            lines.append("  (none)")
            continue
        for item in items:
            if kind == "action":
                owner = item.get("owner", "unassigned")
                due = item.get("due") or "no due date"
                lines.append(f"  - [{owner} · {due}] {item['text']}")
            else:
                speaker = item.get("speaker") or "—"
                lines.append(f"  - ({speaker}) {item['text']}")
    return "\n".join(lines).lstrip()


def main():
    parser = argparse.ArgumentParser(description="Extract decisions, actions, questions, risks from a transcript.")
    parser.add_argument("transcript", help="Path to transcript text file")
    parser.add_argument("--json", action="store_true", help="Output JSON instead of human-readable")
    args = parser.parse_args()

    try:
        text = Path(args.transcript).read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    result = analyze(text)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(render_human(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
