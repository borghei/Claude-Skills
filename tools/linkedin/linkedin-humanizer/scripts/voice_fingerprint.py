#!/usr/bin/env python3
"""Build a voice fingerprint from an author's own past posts, or compare a draft to it.

Reads a text file of past posts separated by lines containing only '---',
measures the habits that make the writing recognisable (sentence length,
contractions, first-person rate, dashes, fragments, emoji, recurring words)
and lists which audit rules those habits should be protected from. With
--compare it measures a draft the same way and reports where it drifts.

Usage:
    python3 voice_fingerprint.py --input past_posts.txt
    python3 voice_fingerprint.py --input past_posts.txt --format json > voice.json
    python3 voice_fingerprint.py --input past_posts.txt --compare draft.txt --max-drift 2

Exit codes:
    0  fingerprint built, or draft within tolerance
    1  gate failed (--compare only: more drifting measures than --max-drift)
    2  bad input (missing, empty or unreadable file; no posts found)
"""

import argparse
import json
import math
import re
import statistics
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List

sys.path.insert(0, str(Path(__file__).resolve().parent))
from tell_rules import fail, normalise, paragraphs, read_text, sentences, words  # noqa: E402

STOPWORDS = set("""a about after again all also am an and any are as at back be because been
before being but by can could did do does doing done down each even every for from get go got
had has have he her here him his how i if in into is it its just like made make many me more
most much my new no not now of off on one only or other our out over own said same she so some
still such than that the their them then there these they thing things this those through time
to too two up us very was way we well were what when where which while who why will with would
you your i'm it's don't didn't that's we're i've can't wasn't last next took went that actually""".split())
DASH_RE = re.compile(r"[—–]|(?<=\s)--(?=\s)")
CONTRACTION_RE = re.compile(r"\b\w+'(?:t|s|re|ve|ll|d|m)\b", re.IGNORECASE)
FIRST_PERSON_RE = re.compile(r"\b(?:I|I'm|I've|I'd|I'll|[Ww]e|[Mm]y|[Oo]ur|[Mm]e)\b")
EMOJI_RE = re.compile("[\U0001F300-\U0001FAFF☀-➿⬀-⯿]")
TRIPLE_RE = re.compile(r"\b[\w'-]+, [\w'-]+(?: [\w'-]+)?,? (?:and|or) [\w'-]+\b")

# measure -> (label, relative tolerance, absolute floor) used by --compare
COMPARED = {
    "words_per_sentence": ("words per sentence", 0.35, 3.0),
    "words_per_paragraph": ("words per paragraph", 0.50, 8.0),
    "first_person_per_100": ("first-person words per 100", 0.50, 1.5),
    "contractions_per_100": ("contractions per 100", 0.60, 1.0),
    "dashes_per_100": ("dashes per 100", 1.00, 0.6),
    "fragments": ("fragments per post", 1.00, 2.0),
    "emoji": ("emoji per post", 1.00, 1.0),
    "questions": ("questions per post", 1.00, 1.0),
}
# rule id -> (measure, threshold, reason) for habits the audit should not strip
PROTECTABLE = {
    "RD-11": ("dashes_per_100", 0.8, "the author's own posts carry about this many dashes"),
    "RD-06": ("fragments", 3.0, "short fragments are part of how the author writes"),
    "RD-07": ("tiny_paragraphs", 1.5, "the author regularly uses a one-word paragraph"),
    "RD-05": ("triples", 1.5, "the author lists in threes more than once a post"),
    "RD-17": ("label_lines", 1.5, "the author labels takeaways in their own posts"),
}


def split_posts(text: str) -> List[str]:
    """Split a file of past posts on lines that contain only three or more dashes."""
    return [p.strip() for p in re.split(r"(?m)^\s*-{3,}\s*$", text) if p.strip()]


def measure(post: str) -> Dict[str, float]:
    """Measure one post and return its habit profile as plain numbers."""
    norm = normalise(post)
    toks = words(norm)
    total = max(1, len(toks))
    sents = sentences(norm)
    lengths = [len(words(s)) for s in sents] or [0]
    paras = paragraphs(norm)
    rows = [ln.strip() for ln in norm.splitlines() if ln.strip()]
    per_100 = 100.0 / total
    return {
        "words": float(len(toks)),
        "words_per_sentence": statistics.mean(lengths),
        "sentence_spread": statistics.pstdev(lengths),
        "words_per_paragraph": len(toks) / max(1, len(paras)),
        "first_person_per_100": len(FIRST_PERSON_RE.findall(norm)) * per_100,
        "contractions_per_100": len(CONTRACTION_RE.findall(norm)) * per_100,
        "dashes_per_100": len(DASH_RE.findall(norm)) * per_100,
        "fragments": float(sum(1 for n in lengths if 0 < n <= 3)),
        "tiny_paragraphs": float(sum(1 for p in paras if len(words(p)) <= 2)),
        "triples": float(len(TRIPLE_RE.findall(norm))),
        "label_lines": float(sum(1 for r in rows if re.match(r"[A-Za-z .;']{2,20}:\s", r))),
        "emoji": float(len(EMOJI_RE.findall(post))),
        "questions": float(norm.count("?")),
        "exclamations": float(norm.count("!")),
        "opening_chars": float(len(rows[0]) if rows else 0),
        "lowercase_starts": float(sum(1 for r in rows if r[0].islower())),
        "closes_on_question": 1.0 if rows and rows[-1].endswith("?") else 0.0,
    }


def signature_words(posts: List[str], limit: int) -> List[str]:
    """Return content words that recur across at least a third of the posts."""
    totals: Counter = Counter()
    spread: Counter = Counter()
    for post in posts:
        toks = [w.lower() for w in words(normalise(post))
                if len(w) >= 4 and w.isalpha() and w.lower() not in STOPWORDS]
        totals.update(toks)
        spread.update(set(toks))
    need = max(2, math.ceil(len(posts) / 3))
    keep = [w for w in totals if spread[w] >= need]
    return sorted(keep, key=lambda w: (-totals[w], w))[:limit]


def build(posts: List[str]) -> Dict[str, Any]:
    """Aggregate per-post measures into the fingerprint (medians across posts)."""
    rows = [measure(p) for p in posts]
    medians = {key: round(statistics.median(r[key] for r in rows), 2) for key in rows[0]}
    protected = [{"id": rid, "reason": reason, "measure": key, "value": medians[key]}
                 for rid, (key, threshold, reason) in PROTECTABLE.items()
                 if medians[key] >= threshold]
    confidence = ("thin: under 3 posts, treat every number as a guess" if len(posts) < 3
                  else "usable" if len(posts) < 6 else "solid")
    return {"posts_analysed": len(posts), "confidence": confidence, "medians": medians,
            "signature_words": signature_words(posts, 12), "protected_rules": protected}


def compare(fingerprint: Dict[str, Any], draft: str, max_drift: int) -> Dict[str, Any]:
    """Measure a draft and report which measures fall outside the author's range."""
    seen = measure(draft)
    drifts = []
    for key, (label, rel, floor) in COMPARED.items():
        base = fingerprint["medians"][key]
        allowed = max(floor, abs(base) * rel)
        gap = round(seen[key] - base, 2)
        if abs(gap) > allowed:
            drifts.append({"measure": key, "label": label, "author": base,
                           "draft": round(seen[key], 2), "gap": gap,
                           "direction": "higher" if gap > 0 else "lower"})
    draft_words = {w.lower() for w in words(normalise(draft))}
    used = [w for w in fingerprint["signature_words"] if w in draft_words]
    return {"drifts": drifts, "max_drift": max_drift, "passed": len(drifts) <= max_drift,
            "signature_words_used": used,
            "draft": {k: round(v, 2) for k, v in seen.items()}}


def output(fingerprint: Dict[str, Any], result: Dict[str, Any], fmt: str) -> None:
    """Print the fingerprint (and comparison, when present) as JSON or text."""
    if fmt == "json":
        print(json.dumps({**fingerprint, **({"comparison": result} if result else {})},
                         indent=2, ensure_ascii=False))
        return
    med = fingerprint["medians"]
    print(f"Voice fingerprint from {fingerprint['posts_analysed']} posts "
          f"(confidence: {fingerprint['confidence']})")
    print("=" * 72)
    print(f"Length        {med['words']:.0f} words, opening line {med['opening_chars']:.0f} chars")
    print(f"Sentences     {med['words_per_sentence']} words on average, "
          f"spread {med['sentence_spread']}")
    print(f"Paragraphs    {med['words_per_paragraph']} words each")
    print(f"Person        {med['first_person_per_100']} first-person words per 100; "
          f"{med['contractions_per_100']} contractions per 100")
    print(f"Punctuation   {med['dashes_per_100']} dashes per 100 words, "
          f"{med['questions']:.0f} questions, {med['exclamations']:.0f} exclamation marks")
    print(f"Habits        {med['fragments']:.0f} fragments, {med['triples']:.0f} triples, "
          f"{med['emoji']:.0f} emoji per post")
    print(f"Recurring     {', '.join(fingerprint['signature_words']) or '(none shared)'}")
    for item in fingerprint["protected_rules"]:
        print(f"Protect       {item['id']}: {item['reason']} ({item['measure']}={item['value']})")
    if not fingerprint["protected_rules"]:
        print("Protect       no audit rule needs waiving for this author")
    if not result:
        return
    print("-" * 72)
    print(f"Draft comparison: {len(result['drifts'])} measure(s) outside the author's range "
          f"(limit {result['max_drift']}) -> {'PASS' if result['passed'] else 'FAIL'}")
    for item in result["drifts"]:
        print(f"  {item['label']}: draft {item['draft']} vs author {item['author']} "
              f"({item['direction']})")
    print(f"  recurring words present: {', '.join(result['signature_words_used']) or 'none'}")


def main() -> None:
    """Parse arguments, build the fingerprint, optionally compare, set the exit code."""
    parser = argparse.ArgumentParser(
        description="Build a voice fingerprint from past posts, or compare a draft to it.",
        epilog="Exit codes: 0 ok, 1 draft drifts on more measures than --max-drift, "
               "2 bad input. Posts are separated by a line containing only '---'.")
    parser.add_argument("--input", required=True,
                        help="Text file of the author's own past posts, separated by '---' lines.")
    parser.add_argument("--compare", metavar="DRAFT",
                        help="Plain-text draft to measure against the fingerprint.")
    parser.add_argument("--max-drift", type=int, default=2,
                        help="Drifting measures tolerated before exit 1 (default: 2).")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                        help="Output format (default: text).")
    args = parser.parse_args()
    if args.max_drift < 0:
        fail("--max-drift must be zero or a positive whole number.")

    posts = split_posts(read_text(args.input))
    if not posts or all(len(words(p)) < 15 for p in posts):
        fail(f"{args.input} has no usable posts. Paste at least three full posts, "
             "separated by a line containing only ---")
    if len(posts) < 3:
        print(f"WARNING: only {len(posts)} post(s) supplied; five or more gives a "
              "fingerprint worth trusting.", file=sys.stderr)
    fingerprint = build(posts)
    result = compare(fingerprint, read_text(args.compare), args.max_drift) if args.compare else {}
    output(fingerprint, result, args.format)
    sys.exit(0 if not result or result["passed"] else 1)


if __name__ == "__main__":
    main()
