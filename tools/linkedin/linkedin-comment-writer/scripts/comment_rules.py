#!/usr/bin/env python3
"""Rule data and text primitives behind the LinkedIn comment linter.

Holds the thresholds, phrase lists and small text helpers that
comment_linter.py applies to a draft comment. Run it directly to read the rule
catalogue without opening the source. Nothing here touches the network.

Usage:
    python3 comment_rules.py --list-rules
    python3 comment_rules.py --list-rules --format json

Exit codes:
    0  catalogue printed
    2  bad arguments (nothing to do without --list-rules)
"""

import argparse
import json
import re
import sys
from typing import Any, Dict, List, Set

# Every threshold is a working heuristic, not a platform rule. Tune them with
# the linter's flags once you know what earns replies in your own niche.
THRESHOLDS: Dict[str, float] = {
    "min_words": 12,            # below this there is no room for a contribution
    "max_words": 90,            # above this the comment competes with the post
    "max_chars": 1000,          # stay well inside whatever cap the product enforces
    "echo_ratio": 0.6,          # share of draft vocabulary lifted from the post
    "anchor_min_shared": 2,     # shared content words that tie the draft to the post
    "duplicate_jaccard": 0.5,   # vocabulary overlap with a comment already posted
    "praise_only_words": 6,     # content words left once the compliments are removed
    "min_question_words": 8,    # a shorter closing question is treated as bait
    "max_emoji": 1,
    "max_mentions": 1,
    "max_paragraphs": 3,
}

EMPTY_PRAISE: List[str] = [
    "great post", "great share", "great point", "great points", "great insight",
    "great insights", "great read", "love this", "love it", "so true", "well said",
    "well put", "spot on", "nailed it", "couldn't agree more", "could not agree more",
    "totally agree", "completely agree", "absolutely agree", "thanks for sharing",
    "thank you for sharing", "this is gold", "pure gold", "so insightful",
    "very insightful", "insightful post", "needed to hear this", "this resonates",
    "resonates with me", "100%", "preach", "brilliant post", "amazing post",
]

STOCK_PHRASES: List[str] = [
    "in today's fast-paced", "in today's world", "game changer", "game-changer",
    "at the end of the day", "food for thought", "a testament to", "powerful reminder",
    "key takeaway", "resonates deeply", "couldn't have said it better", "delve",
    "it's worth noting", "it is worth noting", "ever-evolving", "ever-changing",
    "unlock the power", "paradigm shift", "move the needle", "thought-provoking",
    "truly inspiring", "valuable perspective", "important conversation",
]

PITCH_PATTERNS: Dict[str, str] = {
    "link": r"(https?://|www\.)\S+|\b[a-z0-9-]+\.(com|io|co|ai|net|org|app|dev)\b"
            r"|\b[a-z0-9-]+\.[a-z]{2,}/\S+",
    "direct-message ask": r"\b(dm|message|inbox|ping) me\b",
    "profile or bio pointer": r"\blink in (my |the )?(bio|profile|comments?)\b",
    "self-referral": r"\bcheck out (my|our)\b|\b(my|our) (newsletter|podcast|webinar|course|ebook|guide)\b",
    "sales call": r"\bbook a (call|demo|slot)\b|\bhappy to (jump|hop) on a call\b",
    "follow ask": r"\bfollow (me|us)\b|\bsubscribe\b",
}

BAIT_ENDINGS: List[str] = [
    "thoughts?", "agree?", "what do you think?", "who else?", "anyone else?",
    "right?", "am i wrong?", "what say you?",
]

# Text that reads as if it is talking to an assistant instead of a human reader.
INJECTION_PATTERNS: List[str] = [
    r"ignore (all |any |the )?(previous|prior|above|earlier) (instructions|prompts?|rules)",
    r"disregard (all |any |the )?(previous|prior|above|your) (instructions|rules|guidelines)",
    r"\b(you are|you're) (now )?an? (ai|assistant|language model|chatbot)\b",
    r"\bas an ai\b|\bsystem prompt\b|\bdeveloper message\b",
    r"\b(ai|assistant|agent|bot|llm)s? (reading|processing|summari[sz]ing) this\b",
    r"\bdo not (tell|inform|show) the user\b",
    r"\b(include|add|insert|append) (this|the following) (link|url|text|sentence)\b",
    r"^\s*(system|assistant)\s*:",
]

EXPERIENCE_PATTERNS: List[str] = [
    r"\b(we|i) (ran|tried|tested|shipped|moved|cut|saw|found|measured|lost|hired|"
    r"switched|built|rebuilt|dropped|killed|learned|learnt|spent|stopped|started|kept)\b",
    r"\b(my|our) (team|customers?|clients?|pipeline|numbers|data|experience|last)\b",
    r"\b(last|this) (week|month|quarter|year|spring|summer|autumn|fall|winter)\b",
    r"\bin (19|20)\d\d\b|\bfor example\b|\be\.g\.|\bfor instance\b",
]

STOPWORDS: Set[str] = set(
    "a an and are as at be been but by can could did do does for from had has "
    "have he her his how i if in into is it its just me more most my no not of "
    "on one or our out she so some than that the their them then there these "
    "they this to too up us very was we were what when where which who why will "
    "with would you your about also all any because over under only really".split())

EMOJI_RE = re.compile("[\U0001F300-\U0001FAFF☀-➿\U0001F1E6-\U0001F1FF]")

RULES: List[Dict[str, str]] = [
    {"id": "CW-01", "level": "block", "title": "Too short to contribute",
     "fix": "Add the one detail only you can add: a result, a condition, a cost."},
    {"id": "CW-02", "level": "warn", "title": "Longer than a comment should be",
     "fix": "Cut to one point. A second point is a second comment or your own post."},
    {"id": "CW-03", "level": "block", "title": "Compliment with nothing behind it",
     "fix": "Delete the praise and say what you would add, question or dispute."},
    {"id": "CW-04", "level": "block", "title": "Echoes the post back to its author",
     "fix": "Stop summarising. Start from the sentence where your view departs."},
    {"id": "CW-05", "level": "warn", "title": "Not anchored to this post",
     "fix": "Name the specific claim you are responding to."},
    {"id": "CW-06", "level": "block", "title": "No checkable specific",
     "fix": "Add a number, a named case, a dated event, or a real question."},
    {"id": "CW-07", "level": "block", "title": "Pitches from someone else's thread",
     "fix": "Remove links, product names and asks. Earn the profile visit instead."},
    {"id": "CW-08", "level": "block", "title": "Tags people who are not in the thread",
     "fix": "Address the author by name at most; drop the other mentions."},
    {"id": "CW-09", "level": "warn", "title": "Stock phrasing",
     "fix": "Replace the phrase with the plain claim it is standing in for."},
    {"id": "CW-10", "level": "warn", "title": "Closes on engagement bait",
     "fix": "Ask a question only the author can answer, or end on your point."},
    {"id": "CW-11", "level": "block", "title": "Repeats a comment already posted",
     "fix": "Pick a different move or reply under that comment instead."},
    {"id": "CW-12", "level": "warn", "title": "Decoration: hashtags, emoji, formatting",
     "fix": "Plain sentences. Hashtags and bullet lists belong in posts, if anywhere."},
    {"id": "CW-13", "level": "block", "title": "Uses something the story bank rules out",
     "fix": "Remove the name or topic; anonymise it or pick a different detail."},
]


def words(text: str) -> List[str]:
    """Split text into lowercase word tokens, keeping digits and apostrophes."""
    return re.findall(r"[a-z0-9][a-z0-9'%]*", text.lower().replace("’", "'"))


def content_words(text: str) -> Set[str]:
    """Return the set of meaningful words, crudely singularised for matching."""
    out: Set[str] = set()
    for token in words(text):
        token = token.replace("'s", "").strip("'")
        if len(token) < 3 or token in STOPWORDS:
            continue
        if token.endswith("s") and len(token) > 4 and not token.endswith("ss"):
            token = token[:-1]
        out.add(token)
    return out


def share_from(draft: str, source: str) -> float:
    """Fraction of the draft's content vocabulary that also appears in source."""
    mine = content_words(draft)
    if not mine:
        return 0.0
    return len(mine & content_words(source)) / len(mine)


def jaccard(first: str, second: str) -> float:
    """Vocabulary overlap between two texts as intersection over union."""
    left, right = content_words(first), content_words(second)
    if not left or not right:
        return 0.0
    return len(left & right) / len(left | right)


def find_phrases(text: str, phrases: List[str]) -> List[str]:
    """Return the phrases from the list that occur in the text."""
    lowered = text.lower().replace("’", "'")
    return [p for p in phrases if p in lowered]


def find_patterns(text: str, patterns: List[str]) -> List[str]:
    """Return the matched snippets for every regex in the list that hits."""
    hits: List[str] = []
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
        if match:
            hits.append(match.group(0).strip())
    return hits


def strip_phrases(text: str, phrases: List[str]) -> str:
    """Remove every listed phrase from the text, case-insensitively."""
    lowered = text.lower().replace("’", "'")
    for phrase in sorted(phrases, key=len, reverse=True):
        lowered = lowered.replace(phrase, " ")
    return lowered


def catalogue() -> Dict[str, Any]:
    """Assemble the printable rule catalogue with thresholds and list sizes."""
    return {
        "thresholds": THRESHOLDS,
        "rules": RULES,
        "vocabulary": {
            "empty_praise": len(EMPTY_PRAISE),
            "stock_phrases": len(STOCK_PHRASES),
            "pitch_patterns": sorted(PITCH_PATTERNS),
            "bait_endings": BAIT_ENDINGS,
            "injection_patterns": len(INJECTION_PATTERNS),
        },
    }


def output(data: Dict[str, Any], fmt: str) -> None:
    """Print the catalogue as JSON or as a readable table."""
    if fmt == "json":
        print(json.dumps(data, indent=2))
        return
    print("LinkedIn comment linter — rule catalogue")
    print("=" * 72)
    for rule in data["rules"]:
        print(f"[{rule['level'].upper():<5}] {rule['id']}  {rule['title']}")
        print(f"         fix: {rule['fix']}")
    print("-" * 72)
    print("Thresholds (heuristics, override with the linter's flags):")
    for name, value in data["thresholds"].items():
        print(f"  {name:<20} {value:g}")
    vocab = data["vocabulary"]
    print(f"Vocabulary: {vocab['empty_praise']} praise phrases, "
          f"{vocab['stock_phrases']} stock phrases, "
          f"{len(vocab['pitch_patterns'])} pitch patterns, "
          f"{vocab['injection_patterns']} injection patterns")


def main() -> None:
    """Parse arguments and print the rule catalogue."""
    parser = argparse.ArgumentParser(
        description="Print the rule catalogue used by comment_linter.py. "
                    "Offline; reads nothing and writes nothing.",
        epilog="Exit codes: 0 catalogue printed, 2 bad arguments.")
    parser.add_argument("--list-rules", action="store_true",
                        help="Print every rule with its level, fix and thresholds.")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                        help="Output format (default: text).")
    args = parser.parse_args()
    if not args.list_rules:
        print("ERROR: nothing to do. Pass --list-rules to print the catalogue, "
              "or run comment_linter.py to lint a draft.", file=sys.stderr)
        sys.exit(2)
    output(catalogue(), args.format)


if __name__ == "__main__":
    main()
