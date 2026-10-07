#!/usr/bin/env python3
"""Opening-line pattern data behind the LinkedIn hook classifier.

Defines the cue detectors (what to look for in an opening line) and the
pattern table (which cues add up to which pattern, and how reusable that
pattern is). hook_classifier.py imports both. Run this file directly to list
the patterns or show the cues and weights for one.

Usage:
    python3 hook_patterns.py --list
    python3 hook_patterns.py --show dated-error
    python3 hook_patterns.py --list --format json

Exit codes: 0 ok, 2 bad input (unknown pattern slug).
"""

import argparse
import json
import re
import sys
from typing import Any, Dict, List

_DAYS = "monday|tuesday|wednesday|thursday|friday|saturday|sunday"
_MONTHS = "jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec"
_COUNT = r"\d+|two|three|four|five|six|seven|eight|nine|ten|a few|a couple of"
_FULL_MONTHS = ("january|february|march|april|june|july|august|september|october|"
                "november|december")

# cue name -> pattern, matched case-insensitively against the opening line
_CUE_SOURCES = {
    "number": r"\d",
    "starts_number": r"^\W*(?:\d|[$£€])",
    "money": r"[$£€]\s?\d|\b\d[\d,.]*\s?(?:k|m)?\s?(?:dollars|euros|pounds|usd|eur|gbp)\b",
    "percent": r"\d\s?%|\bpercent\b",
    "time_anchor": rf"\b(?:{_COUNT}|a|one) (?:days?|weeks?|months?|years?) ago\b|"
                   rf"\b(?:last |this |in |since |between |and |by )?(?:{_FULL_MONTHS})\b|"
                   rf"\blast (?:week|month|year|spring|summer|autumn|winter|quarter|{_DAYS})\b|"
                   rf"\bon (?:the )?\d{{1,2}}(?:st|nd|rd|th)?\b|\b(?:{_MONTHS})\w* \d{{1,2}}\b|"
                   rf"\b\d{{1,2}} (?:{_MONTHS})\w*\b|\bin (?:19|20)\d\d\b|\byesterday\b|"
                   rf"\bthis morning\b|\bon (?:{_DAYS})\b",
    "first_person": r"\b(?:i|we|my|our|i'm|i've|i'd|we've|we'd)\b",
    "error": r"\b(?:mistake|wrong|lost|failed|broke|missed|regret\w*|fired|outage|churned|"
             r"cancelled|canceled|botched|blew|rejected|ignored|dismissed|overpaid|"
             r"underestimated|cost (?:us|me))\b",
    "belief": r"\bused to (?:think|believe|say|argue|tell)\b|\bi (?:thought|believed|assumed)\b|"
              r"\bchanged my mind\b|\bfor (?:years|months|a long time),? i\b|"
              r"\bi was (?:sure|convinced|certain)\b",
    "counter": r"\boverrated\b|\bis a myth\b|\b(?:doesn't|don't|won't) work\b|"
               r"\byou don't need\b|\bis (?:wrong|backwards|broken|dead|a waste)\b|"
               r"\bmost (?:\w+ ){1,3}(?:is|are) (?:wrong|bad|a waste|useless)\b|"
               r"\bnobody needs\b|\bbad advice\b|\bunpopular\b",
    "gap": r"\bfrom [^.]{0,30}\d[^.]{0,25} to [^.]{0,20}\d|\bwent from\b|"
           r"\b(?:cut|grew|dropped|rose|fell|doubled|halved|tripled)\b[^.]*\d|"
           r"\d[^.]{0,25}(?:→|->| vs\.? | versus )[^.]{0,15}\d|\b\d[\d,.]*%? (?:\w+ ){0,2}to \d",
    "quote": r"^\W*[\"“'‘]\w|[\"“][^\"”]{8,}[\"”]",
    "said": r"\b(?:said|told me|told us|wrote|texted|emailed|messaged)\b",
    "rule": r"\b(?:my|our|one|the) (?:\w+ )?rule\b|\b(?:i|we) (?:never|always)\b|"
            r"\bnon-negotiable\b",
    "sample": r"\b(?:i|we|i've|we've) (?:\w+ )?(?:reviewed|read|interviewed|audited|"
              r"analy[sz]ed|looked at|talked to|spoke to|hired|sat in on|tested|graded|"
              r"watched|ran)\b[^.]*\d",
    "asked": r"\basked (?:me|us)\b|\bkeep getting asked\b|\bquestion i get\b|"
             r"\bsomeone asked\b|\bpeople (?:keep )?ask(?:ing)?\b",
    "thanks": r"\bthank(?:s| you)\b|\bgrateful\b|\bshout-?out\b|\bcredit (?:to|goes)\b|"
              r"\bi owe\b|\bcouldn't have\b",
    "define": r"\bin plain (?:english|words|terms)\b|\bexplained\b|\b(?:actually|really) means\b|"
              r"\bis just\b|\bwhat (?:is|are) (?:a |an |the )?\w+",
    "bet": r"\bby (?:20\d\d|the end of|next (?:year|quarter)|q[1-4])\b|\bi predict\b|"
           r"\bmy bet\b|\bprediction\b|\bwithin \w+ (?:months|years)\b|"
           r"\bwill be (?:gone|dead|standard|normal|obsolete)\b",
    "list": rf"^\W*(?:{_COUNT}) (?:\w+ ){{0,3}}(?:things|ways|lessons|rules|mistakes|questions|"
            r"signs|steps|reasons|tools|habits|checks|tips)\b",
    "question": r"\?\s*$",
    "announce": r"\b(?:excited|thrilled|happy|proud|pleased|delighted|humbled|honou?red) to "
                r"(?:share|announce|say|join)\b|\bi'm joining\b|\bwe're hiring\b|\bbig news\b",
    "tease_word": r"\b(?:this|here's|nobody|no one|secret|truth|everything|what happened)\b",
    "command": r"^\W*(?:stop|start|quit|never|always|don't|do not|try|remember|forget|delete)\b",
    "scene": rf"^\W*(?:\d{{1,2}}[:.]\d\d|it was|at \d|i was (?:sitting|standing|in|on|halfway)|"
             rf"we were|the (?:room|call|line|email|meeting|office|phone) )|"
             rf"\b(?:midnight|a\.m\.|p\.m\.)|\b\d{{1,2}}\s?(?:am|pm)\b",
}
CUES = {name: re.compile(src, re.IGNORECASE) for name, src in _CUE_SOURCES.items()}
PROPER_RE = re.compile(r"(?<=[a-z0-9,;:] )(?!LinkedIn)[A-Z][A-Za-z]{2,}")

# slug -> name, core cues (any one must fire), weighted cues, reuse status, reuse note
_P = [
    ("receipt", "Receipt line", ["number"],
     {"starts_number": 2, "money": 2, "number": 1, "percent": 1, "first_person": 1}, "reusable",
     "Needs your own figure and what it counts. A borrowed number is a false claim."),
    ("dated-error", "Dated mistake", ["error"],
     {"error": 2, "time_anchor": 2, "first_person": 1, "number": 1}, "reusable",
     "Needs a real date and a real cost. Without first person it is gossip."),
    ("cold-scene", "Cold scene", ["scene"],
     {"scene": 3, "first_person": 1, "quote": 1}, "reusable",
     "Needs a moment you were in. Keep the setup out; the scene is the setup."),
    ("belief-flip", "Changed mind", ["belief"],
     {"belief": 4, "first_person": 1, "time_anchor": 1}, "reusable",
     "State the old belief fairly; the post must show what ended it."),
    ("counter-position", "Counter-position", ["counter"],
     {"counter": 3, "number": 1}, "reusable",
     "Only with evidence and a stated boundary. Otherwise it is a provocation."),
    ("gap", "Measured gap", ["gap"],
     {"gap": 3, "time_anchor": 1, "percent": 1, "number": 1}, "reusable",
     "Both figures and the time span must be yours and measured the same way."),
    ("borrowed-line", "Borrowed line", ["quote"],
     {"quote": 3, "said": 2}, "reusable",
     "Quote the words as said; describe the speaker by role if they did not agree to be named."),
    ("house-rule", "House rule", ["rule"],
     {"rule": 3, "first_person": 1}, "reusable",
     "The rule must be one you keep; the post owes the incident that created it."),
    ("field-count", "Field count", ["sample"],
     {"sample": 4, "number": 1}, "reusable",
     "Say how the sample was chosen. A count without a method is a receipt line at best."),
    ("asked-question", "Reported question", ["asked"],
     {"asked": 4, "quote": 1, "said": 1}, "reusable",
     "A question you were really asked, attributed by role."),
    ("credit", "Named credit", ["thanks"],
     {"thanks": 3, "proper": 2}, "reusable",
     "Name the specific act. A list of tagged names is a different, weaker thing."),
    ("plain-definition", "Plain definition", ["define"],
     {"define": 4, "quote": 1}, "reusable",
     "Works when the term is one your audience uses without defining."),
    ("dated-bet", "Dated bet", ["bet"],
     {"bet": 4, "number": 1}, "reusable",
     "Include the date and what would prove you wrong."),
    ("list-promise", "Counted list", ["list"],
     {"list": 5}, "reusable",
     "Every item needs its own detail, or the count is the only content."),
    ("direct-question", "Question to the reader", ["question"],
     {"question": 3}, "caution",
     "Opens by asking for attention before earning it. Put the question last instead."),
    ("announcement", "Announcement", ["announce"],
     {"announce": 5}, "caution",
     "The feeling is not the news. Open with the news."),
    ("teaser", "Teaser", ["teaser"],
     {"teaser": 4}, "caution",
     "Withholds the subject. Reusable only if the payoff arrives in the next line."),
    ("command", "Command", ["command"],
     {"command": 3}, "caution",
     "Tells the reader what to do before giving a reason. Lead with the reason."),
]
PATTERNS: Dict[str, Dict[str, Any]] = {
    slug: {"slug": slug, "name": name, "core": core, "weights": weights,
           "reuse": reuse, "note": note}
    for slug, name, core, weights, reuse, note in _P}


def fail(message: str) -> None:
    """Print an actionable error to stderr and exit with the bad-input code."""
    print(f"ERROR: {message}", file=sys.stderr)
    sys.exit(2)


def detect_cues(opening: str) -> List[str]:
    """Return the names of every cue that fires on an opening line."""
    plain = opening.replace("’", "'").replace("‘", "'")
    fired = [name for name, pattern in CUES.items() if pattern.search(plain)]
    if PROPER_RE.search(plain):
        fired.append("proper")
    short = len(plain.split()) <= 8
    if short and "tease_word" in fired and "number" not in fired and "proper" not in fired:
        fired.append("teaser")
    return [name for name in fired if name != "tease_word"]


def main() -> None:
    """List the pattern table or show the cues and weights behind one pattern."""
    parser = argparse.ArgumentParser(
        description="List or inspect the opening-line patterns used by hook_classifier.py.",
        epilog="Exit codes: 0 ok, 2 bad input (unknown pattern slug).")
    parser.add_argument("--list", action="store_true", help="List all patterns (default).")
    parser.add_argument("--show", metavar="SLUG", help="Show core cues and weights for a pattern.")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                        help="Output format (default: text).")
    args = parser.parse_args()

    if args.show:
        pattern = PATTERNS.get(args.show.strip().lower())
        if pattern is None:
            fail(f"unknown pattern '{args.show}'. Valid slugs: {', '.join(PATTERNS)}.")
        if args.format == "json":
            print(json.dumps(pattern, indent=2))
            return
        print(f"{pattern['slug']}  {pattern['name']}  [{pattern['reuse']}]")
        print(f"  core cue (one must fire): {', '.join(pattern['core'])}")
        print("  weights: " + ", ".join(f"{k} +{v}" for k, v in pattern["weights"].items()))
        print(f"  reuse note: {pattern['note']}")
        return
    if args.format == "json":
        print(json.dumps(list(PATTERNS.values()), indent=2))
        return
    for pattern in PATTERNS.values():
        print(f"{pattern['slug']:<17} {pattern['reuse']:<9} {pattern['name']}")
    print(f"{len(PATTERNS)} patterns. Use --show SLUG for cues and weights.")


if __name__ == "__main__":
    main()
