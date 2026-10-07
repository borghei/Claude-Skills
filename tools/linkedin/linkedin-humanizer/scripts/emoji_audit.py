#!/usr/bin/env python3
"""Score the emoji pattern of a LinkedIn draft: placement, repetition, stock choices.

Counting emoji is not the point. One emoji the author always uses is a voice
habit; the same decorative set stamped at the start of every line is a
template. This tool scores the pattern from 0 to 100 and names each placement
rule that fired, working only on the text you supply.

Usage:
    python3 emoji_audit.py --input draft.txt
    python3 emoji_audit.py --input draft.txt --format json --fail-under 70
    python3 emoji_audit.py --input draft.txt --usual 2

Exit codes:
    0  score at or above --fail-under
    1  gate failed (score below --fail-under)
    2  bad input (missing, empty or unreadable file; invalid option value)
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List

sys.path.insert(0, str(Path(__file__).resolve().parent))
from tell_rules import fail, read_text, words  # noqa: E402

_BASE = "[\U0001F300-\U0001FAFF☀-➿⬀-⯿\U0001F1E6-\U0001F1FF]"
_MOD = "(?:️|[\U0001F3FB-\U0001F3FF])?"
EMOJI_RE = re.compile(f"{_BASE}{_MOD}(?:‍{_BASE}{_MOD})*")

# Heuristic: decorations that tend to arrive as section markers in templated
# drafts. This is an editorial list, not a measured frequency table.
STOCK_SET = set("🚀💡✨👉✅🔥🎯📈💪🙌🔑⚡🧵👇📌🌟💼🤝🧠⭐🏆💯📊🔍")

# id -> (name, penalty, why, fix)
CHECKS = {
    "EM-01": ("Density above the cap", 15,
              "More emoji than the text can carry turns them into wallpaper.",
              "Keep the one or two that add meaning or are the author's habit; cut the rest."),
    "EM-02": ("Emoji bullet run", 25,
              "Three or more consecutive lines that each start with an emoji is the layout "
              "of a generated listicle.",
              "Use plain numbered lines, or prose if the items are not really parallel."),
    "EM-03": ("Emoji in the opening line", 10,
              "The opening line is read before anything else; a decoration there spends "
              "attention on nothing.",
              "Open with words. Move the emoji later or drop it."),
    "EM-04": ("Emoji heading", 15,
              "An emoji followed by a short Title Case label and a colon or dash is a slide "
              "heading, not a sentence.",
              "Turn the label into the first words of a real sentence."),
    "EM-05": ("Stock decoration set", 15,
              "Most of the emoji come from the small set that decorates templated posts.",
              "Replace with nothing, or with the one emoji the author would type themselves."),
    "EM-06": ("Emoji cluster", 10,
              "Two or more emoji side by side shout without adding information.",
              "Keep one."),
    "EM-07": ("Line-end decoration", 10,
              "Several lines each ending in an emoji read as punctuation by sticker.",
              "End the sentence with a full stop."),
    "EM-08": ("Pointing closer", 5,
              "A downward pointer after a call for comments is a stock engagement prompt.",
              "Ask a specific question and stop."),
}


def find_emoji(text: str) -> List[str]:
    """Return every emoji sequence in the text, in order of appearance."""
    return EMOJI_RE.findall(text)


def longest_bullet_run(rows: List[str]) -> int:
    """Return the longest streak of consecutive non-empty lines that start with an emoji."""
    best = run = 0
    for row in rows:
        run = run + 1 if EMOJI_RE.match(row) else 0
        best = max(best, run)
    return best


def score(text: str, cap: float, usual: int) -> Dict[str, Any]:
    """Evaluate every placement rule and return the scored report."""
    rows = [ln.strip().lstrip("*_ ") for ln in text.splitlines() if ln.strip()]
    found = find_emoji(text)
    total_words = max(1, len(words(text)))
    density = round(len(found) * 100 / total_words, 2)
    fired: Dict[str, str] = {}

    if len(found) >= 3 and len(found) > usual and density > cap:
        fired["EM-01"] = f"{len(found)} emoji in {total_words} words = {density} per 100 (cap {cap})"
    run = longest_bullet_run(rows)
    if run >= 3:
        fired["EM-02"] = f"{run} consecutive lines open with an emoji"
    if rows and find_emoji(rows[0]):
        fired["EM-03"] = f"opening line: {rows[0][:60]}"
    headings = [r for r in rows if re.match(
        rf"{EMOJI_RE.pattern}\s*[*_]*[A-Z][\w' ]{{2,40}}?[*_]*\s*(?:[:—–]|-\s)", r)]
    if headings:
        fired["EM-04"] = f"{len(headings)} heading line(s), e.g. {headings[0][:50]}"
    stock = [e for e in found if e[0] in STOCK_SET]
    if len(found) >= 3 and len(stock) / len(found) >= 0.6:
        fired["EM-05"] = (f"{len(stock)} of {len(found)} from the stock set: "
                          + " ".join(sorted(set(stock))))
    clusters = re.findall(rf"(?:{EMOJI_RE.pattern}\s?){{2,}}", text)
    if clusters:
        fired["EM-06"] = f"{len(clusters)} cluster(s), e.g. {clusters[0].strip()}"
    enders = [r for r in rows if re.search(rf"{EMOJI_RE.pattern}\s*$", r) and len(words(r)) > 2]
    if len(enders) >= 3:
        fired["EM-07"] = f"{len(enders)} lines end in an emoji"
    if rows and re.search(r"[👇⬇]", " ".join(rows[-2:])):
        fired["EM-08"] = f"closing lines: {' '.join(rows[-2:])[:60]}"

    findings = [{"id": cid, "name": CHECKS[cid][0], "penalty": CHECKS[cid][1],
                 "evidence": evidence, "why": CHECKS[cid][2], "fix": CHECKS[cid][3]}
                for cid, evidence in fired.items()]
    total = max(0, 100 - sum(f["penalty"] for f in findings))
    if not found:
        band = "no emoji: nothing to score"
    elif total >= 85:
        band = "hand-placed: reads like a person chose each one"
    elif total >= 60:
        band = "noticeable pattern: fix the flagged placements"
    else:
        band = "templated: the emoji layout is doing the formatting"
    return {"emoji_count": len(found), "distinct": sorted(set(found)), "words": total_words,
            "per_100_words": density, "score": total, "band": band, "findings": findings}


def output(report: Dict[str, Any], fmt: str, source: str, threshold: int) -> None:
    """Print the emoji report as JSON or readable text."""
    passed = report["score"] >= threshold
    if fmt == "json":
        print(json.dumps({**report, "source": source, "fail_under": threshold,
                          "passed": passed}, indent=2, ensure_ascii=False))
        return
    print(f"Emoji pattern audit: {source}")
    print(f"Emoji {report['emoji_count']} ({' '.join(report['distinct']) or 'none'}) | "
          f"{report['per_100_words']} per 100 words")
    print(f"Score: {report['score']}/100 ({report['band']})   "
          f"Gate: {'PASS' if passed else 'FAIL'} at {threshold}")
    print("=" * 72)
    for item in report["findings"]:
        print(f"[-{item['penalty']:>2}] {item['id']} {item['name']}")
        print(f"      seen: {item['evidence']}")
        print(f"      why : {item['why']}")
        print(f"      fix : {item['fix']}")
    if not report["findings"]:
        print("No placement rule fired.")


def main() -> None:
    """Parse arguments, score the draft, print the report and set the exit code."""
    parser = argparse.ArgumentParser(
        description="Score the emoji pattern of a LinkedIn draft (offline, heuristic).",
        epilog="Exit codes: 0 score at or above --fail-under, 1 below it, 2 bad input. "
               "Thresholds are editorial heuristics; tune --cap and --usual to the author.")
    parser.add_argument("--input", required=True,
                        help="Plain-text draft to score, or '-' to read stdin.")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                        help="Output format (default: text).")
    parser.add_argument("--cap", type=float, default=2.0,
                        help="Emoji per 100 words above which density is flagged (default: 2.0).")
    parser.add_argument("--usual", type=int, default=0,
                        help="Emoji count the author normally uses per post; drafts at or "
                             "below it skip the density rule (default: 0).")
    parser.add_argument("--fail-under", type=int, default=60,
                        help="Exit 1 when the score is below this value (default: 60).")
    args = parser.parse_args()
    if args.cap <= 0 or args.usual < 0 or not 0 <= args.fail_under <= 100:
        fail("--cap must be above 0, --usual 0 or more, and --fail-under between 0 and 100.")

    report = score(read_text(args.input), args.cap, args.usual)
    output(report, args.format, "stdin" if args.input == "-" else args.input, args.fail_under)
    sys.exit(0 if report["score"] >= args.fail_under else 1)


if __name__ == "__main__":
    main()
