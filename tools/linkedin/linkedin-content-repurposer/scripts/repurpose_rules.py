#!/usr/bin/env python3
"""Rule data and text primitives shared by the two repurposing tools.

Holds the rule catalogue, the patterns for channel artefacts that do not
survive a move to LinkedIn (thread numbering, handles, timestamps, spoken
filler, slide references, document scaffolding), and the text helpers used by
repurpose_analyzer.py and draft_fidelity_check.py: file loading, sentence
splitting, figure extraction and the artefact scan.

Usage:
    python3 repurpose_rules.py --list-rules
    python3 repurpose_rules.py --list-rules --format json

Exit codes:
    0  rules printed
    2  bad arguments
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, NoReturn, Set

SEVERITY_RANK = {"blocker": 0, "rework": 1, "note": 2}

# House defaults, not platform facts. All are CLI-overridable.
TARGET_MIN_CHARS = 800
TARGET_MAX_CHARS = 1600
OPENING_CHARS = 200

RULES = {
    "RP-001": ("rework", "Thread numbering and thread markers",
               "Delete the markers and join the segments into continuous prose."),
    "RP-002": ("rework", "Handles from another network",
               "Replace each handle with the person's name, or drop the mention."),
    "RP-003": ("rework", "Hashtag cluster",
               "Remove the cluster; keep at most a couple of tags if you use any."),
    "RP-004": ("note", "Links in the body",
               "Decide deliberately where each link goes; do not carry them over by default."),
    "RP-005": ("rework", "Call to action that belongs to another channel",
               "Replace with one ask a LinkedIn reader can act on."),
    "RP-006": ("rework", "Timestamps or speaker labels",
               "Strip them; a post has one speaker and no clock."),
    "RP-007": ("rework", "Spoken filler",
               "Rewrite from the idea, not from the transcript sentence."),
    "RP-008": ("rework", "References to a stage, slide or room",
               "Describe the thing the slide showed, or cut the passage."),
    "RP-009": ("rework", "Document scaffolding",
               "Drop headings, cross-references and footnote markers; a post is one unit."),
    "RP-010": ("rework", "Markup that will not render",
               "Convert code, tables and images into a sentence or a separate attachment."),
    "RP-011": ("rework", "Mentions of the original channel",
               "Remove; the reader does not need the post's history."),
    "RP-020": ("rework", "Opening will not carry on its own",
               "Write a new opening from the strongest spine sentence."),
    "RP-021": ("note", "No first-person voice in the source",
               "Add where you stand: what you saw, did or decided."),
    "RP-022": ("blocker", "Nothing concrete to carry over",
               "Get one number, date or named case from the author before drafting."),
    "RP-023": ("note", "Source holds several separable points",
               "Plan one post per point; do not summarise them all into one."),
    "RP-024": ("note", "Sentences run long",
               "Break them where a speaker would have paused."),
    "RP-025": ("note", "Paragraphs run long",
               "Split into short paragraphs with one idea each."),
    "FD-001": ("blocker", "Draft contains a figure the source does not",
               "Restore the source's figure or remove the claim."),
    "FD-002": ("blocker", "Quoted words do not appear in the source",
               "Quote exactly, or turn the quotation into reported speech."),
    "FD-003": ("rework", "Draft is mostly copied sentences",
               "Rebuild from the spine; repurposing changes delivery, not just length."),
    "FD-005": ("note", "Length is outside the target band",
               "Trim or expand, unless the length is deliberate."),
    "FD-004": ("blocker", "Draft uses a name or subject the story bank forbids",
               "Remove it; the bank's never-name and no-go lists are final."),
    "FD-006": ("rework", "Opening leans on the source's history or a greeting",
               "Open on the point, not on where the material came from."),
    "FD-007": ("note", "Draft is a single block of text",
               "Add paragraph breaks."),
    "FD-008": ("note", "Names appear that the source does not contain",
               "Confirm each with the author."),
}

ARTEFACTS = [
    ("RP-001", re.compile(r"^\s*\(?\d{1,2}\s*[/)]\s*(\d{1,2})?(?=\s|$)|\d{1,2}/\d{1,2}\s*$"
                          r"|\bthread\s*[:👇]|🧵", re.I)),
    ("RP-002", re.compile(r"(?<![\w.])@[A-Za-z0-9_]{2,}")),
    ("RP-004", re.compile(r"https?://\S+|\bwww\.\S+", re.I)),
    ("RP-005", re.compile(
        r"\blink in (my |the )?bio\b|\blike and subscribe\b|\bsmash (that|the)\b"
        r"|\bhit the bell\b|\bswipe up\b|\bretweet\b|\bRT (if|this)\b"
        r"|\bfollow (me )?for more\b|\bsubscribe (to|below|now)\b"
        r"|\bdrop a (like|follow)\b|\bquote[- ]tweet\b|\bsee you in the next (one|video|episode)\b",
        re.I)),
    ("RP-006", re.compile(r"^\s*\[?\(?\d{1,2}:\d{2}(:\d{2})?\)?\]?"
                          r"|^\s*(speaker \d+|host|guest|interviewer|moderator|q|a)\s*:", re.I)),
    ("RP-007", re.compile(r"\b(um+|uh+|erm+|you know|i mean|sort of|kind of|basically"
                          r"|like, |right\?|okay so|so yeah)\b", re.I)),
    ("RP-008", re.compile(
        r"\b(next|previous|this|last) slide\b|\bon (the|this) (slide|screen)\b"
        r"|\bas you can see\b|\bshow of hands\b|\bcan (everyone|you all) hear\b"
        r"|\bthanks? (you )?for having me\b|\bin the (room|audience|back)\b"
        r"|\bany questions\b", re.I)),
    ("RP-009", re.compile(
        r"^\s{0,3}#{1,6}\s|\bin this (article|post|piece|issue|guide|essay)\b"
        r"|\btable of contents\b|\bas (mentioned|discussed|noted) (above|earlier|below)\b"
        r"|\bin the (previous|next|following) section\b|\bread on\b|\[\d{1,2}\]"
        r"|\bdear (reader|subscriber)s?\b", re.I)),
    ("RP-010", re.compile(r"^\s*```|!\[[^\]]*\]\(|^\s*\|.*\|\s*$|<[a-z]+[^>]*>", re.I)),
    ("RP-011", re.compile(
        r"\bas i (tweeted|posted|said in|wrote in)\b|\bin (my|this|the) (last |latest )?"
        r"(video|episode|podcast|newsletter|thread|talk|webinar)\b"
        r"|\boriginally (posted|published|appeared)\b", re.I)),
]

GREETING_RE = re.compile(
    r"^\W*(hi|hello|hey|good (morning|afternoon|evening)|welcome|thanks|thank you"
    r"|so,?|okay|ok,?|alright|right,?|today (i|we)|in this|a thread|quick thread"
    r"|dear)\b", re.I)
MARKER_RE = re.compile(
    r"(?m)^\s*(\[?\(?\d{1,2}:\d{2}(:\d{2})?\)?\]?|\(?\d{1,2}\s*[/)]\s*\d{0,2})\s*")
HASHTAG_RE = re.compile(r"(?<!\w)#[A-Za-z][\w]*")
NUMBER_RE = re.compile(r"\d[\d,]*(?:\.\d+)?")
SENTENCE_RE = re.compile(r"(?<=[.!?])[\"')\]]?\s+|\n+")
WORD_RE = re.compile(r"[A-Za-z0-9'’]+")
FIRST_PERSON_RE = re.compile(r"\b(i|i'm|i've|i'd|we|we're|we've|my|our|me|us)\b", re.I)
NUMBER_WORDS = {
    "zero": "0", "one": "1", "two": "2", "three": "3", "four": "4", "five": "5",
    "six": "6", "seven": "7", "eight": "8", "nine": "9", "ten": "10",
    "eleven": "11", "twelve": "12", "thirteen": "13", "fourteen": "14",
    "fifteen": "15", "sixteen": "16", "seventeen": "17", "eighteen": "18",
    "nineteen": "19", "twenty": "20", "thirty": "30", "forty": "40",
    "fifty": "50", "sixty": "60", "seventy": "70", "eighty": "80",
    "ninety": "90", "hundred": "100", "thousand": "1000",
}


def fail(message: str) -> NoReturn:
    """Print an actionable error to stderr and exit with the bad-input code."""
    print(f"ERROR: {message}", file=sys.stderr)
    sys.exit(2)


def load_text(path: Path, what: str, min_words: int = 1) -> str:
    """Read a UTF-8 text file, exiting with guidance when it cannot be used."""
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        fail(f"cannot read {what} {path}: {getattr(exc, 'strerror', None) or exc}. "
             "Save the text as a UTF-8 .txt or .md file and pass its path.")
    if len(WORD_RE.findall(text)) < min_words:
        fail(f"{what} {path} has fewer than {min_words} words; there is not "
             "enough text to work with.")
    return text.replace("\r\n", "\n").replace("’", "'").replace("“", '"').replace("”", '"')


def strip_markers(text: str) -> str:
    """Remove line-leading thread numbers and timestamps so they are not read as figures."""
    return MARKER_RE.sub("", text)


def stale_opening(opening: str) -> bool:
    """Return True when an opening greets, or refers to its own channel or document."""
    patterns = dict(ARTEFACTS)
    return bool(GREETING_RE.search(opening)) or any(
        patterns[rule].search(opening) for rule in ("RP-008", "RP-009", "RP-011"))


def finding(rule_id: str, evidence: str, lines: List[int]) -> Dict[str, Any]:
    """Build one finding record from the rule catalogue."""
    severity, title, action = RULES[rule_id]
    return {"id": rule_id, "severity": severity, "title": title,
            "evidence": evidence, "lines": lines[:8], "action": action}


def sentences(text: str) -> List[str]:
    """Split text into trimmed sentences of at least three words."""
    parts = [p.strip() for p in SENTENCE_RE.split(text) if p]
    return [p for p in parts if len(WORD_RE.findall(p)) >= 3]


def figures(text: str, with_words: bool = False) -> Set[str]:
    """Return the numbers in the text, normalised (no commas, no trailing zeros).

    With `with_words`, spelled-out small numbers count too, so a draft that
    writes '9' for the source's 'nine' is not treated as a new figure.
    """
    found = set()
    for raw in NUMBER_RE.findall(text):
        value = raw.replace(",", "")
        if "." in value:
            value = value.rstrip("0").rstrip(".")
        found.add(value)
    if with_words:
        found.update(NUMBER_WORDS[w] for w in re.findall(r"[a-z]+", text.lower())
                     if w in NUMBER_WORDS)
    return found


def scan_artefacts(text: str) -> List[Dict[str, Any]]:
    """Find channel artefacts line by line and return one finding per rule."""
    hits: Dict[str, Dict[str, List[Any]]] = {}
    for number, line in enumerate(text.split("\n"), start=1):
        for rule_id, pattern in ARTEFACTS:
            match = pattern.search(line)
            if match:
                slot = hits.setdefault(rule_id, {"lines": [], "samples": []})
                slot["lines"].append(number)
                sample = match.group(0).strip()
                if sample and sample not in slot["samples"]:
                    slot["samples"].append(sample)
        if len(HASHTAG_RE.findall(line)) >= 3:
            slot = hits.setdefault("RP-003", {"lines": [], "samples": []})
            slot["lines"].append(number)
            slot["samples"] = HASHTAG_RE.findall(line)[:4]
    out = []
    for rule_id in sorted(hits):
        slot = hits[rule_id]
        if rule_id == "RP-007" and len(slot["lines"]) < 3:
            continue  # the odd 'kind of' is ordinary writing, not a transcript
        shown = ", ".join(f"'{s}'" for s in slot["samples"][:4])
        out.append(finding(rule_id, f"{len(slot['lines'])} line(s): {shown}",
                           slot["lines"]))
    return out


def main() -> None:
    """Print the rule catalogue and default thresholds."""
    parser = argparse.ArgumentParser(
        description="Show the rules and default thresholds used by "
                    "repurpose_analyzer.py and draft_fidelity_check.py.",
        epilog="Exit codes: 0 rules printed, 2 bad arguments.")
    parser.add_argument("--list-rules", action="store_true",
                        help="Print the catalogue (required; the module has "
                             "no other action).")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                        help="Output format (default: text).")
    args = parser.parse_args()
    if not args.list_rules:
        fail("nothing to do. Pass --list-rules, or run repurpose_analyzer.py "
             "--input <source.txt> to analyse a source.")
    defaults = {"target_min_chars": TARGET_MIN_CHARS,
                "target_max_chars": TARGET_MAX_CHARS, "opening_chars": OPENING_CHARS}
    if args.format == "json":
        print(json.dumps({"defaults": defaults, "rules": {
            k: {"severity": v[0], "title": v[1], "action": v[2]}
            for k, v in RULES.items()}}, indent=2))
        return
    print("Repurposing rules")
    print("=" * 72)
    for rule_id, (severity, title, action) in RULES.items():
        print(f"{rule_id}  [{severity:<7}] {title}\n         do: {action}")
    print("\nDefault thresholds (house heuristics; override on the command line)")
    for key, value in defaults.items():
        print(f"  {key:<18} {value}")


if __name__ == "__main__":
    main()
