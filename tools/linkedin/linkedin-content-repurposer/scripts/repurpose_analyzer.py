#!/usr/bin/env python3
"""Measure a source text and flag what will not survive the move to LinkedIn.

Reads a thread, transcript, article, talk script or newsletter from a local
text file, guesses its channel, measures it against a target length band,
lists the channel artefacts that must be cut or rebuilt, ranks the sentences
most worth carrying over, and estimates how many separate posts the source
holds. It analyses; it does not write the post, and it contacts nothing.

Usage:
    python3 repurpose_analyzer.py --input thread.txt
    python3 repurpose_analyzer.py --input talk.txt --source-type transcript \
        --format json
    python3 repurpose_analyzer.py --input article.md --target-min 900 \
        --target-max 1400 --fail-on blocker

Exit codes:
    0  analysis completed (and no finding reached the --fail-on level)
    1  gate failed: a finding at or above --fail-on exists
    2  bad input: file missing, unreadable, or too short to analyse
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List

sys.path.insert(0, str(Path(__file__).resolve().parent))
from repurpose_rules import (  # noqa: E402
    ARTEFACTS, FIRST_PERSON_RE, NUMBER_RE, OPENING_CHARS, SEVERITY_RANK,
    TARGET_MAX_CHARS, TARGET_MIN_CHARS, WORD_RE, fail, finding, load_text,
    scan_artefacts, sentences, stale_opening)

SOURCE_TYPES = ["auto", "thread", "transcript", "talk", "article", "newsletter", "note"]
TURN_RE = re.compile(
    r"\b(but|instead|until|turned out|wrong|stopped|actually|except|however"
    r"|used to|no longer|the problem was|what changed)\b", re.I)
RULE_PATTERNS = dict(ARTEFACTS)


def detect_type(text: str) -> str:
    """Guess the source channel from its surface features."""
    lines = text.split("\n")

    def count(rule_id: str) -> int:
        """Count lines matching one artefact rule."""
        return sum(1 for line in lines if RULE_PATTERNS[rule_id].search(line))

    words = len(WORD_RE.findall(text))
    if count("RP-001") >= 3:
        return "thread"
    if count("RP-006") >= 3:
        return "transcript"
    if count("RP-008") >= 2:
        return "talk"
    if sum(1 for line in lines if re.match(r"\s{0,3}#{1,6}\s", line)) >= 2:
        return "article"
    if re.search(r"\bdear (reader|subscriber)s?\b|\bthis (week|month)'s (issue|edition)\b",
                 text, re.I):
        return "newsletter"
    if words > 600:
        return "article"
    if count("RP-007") >= 5:
        return "transcript"
    return "note"


def split_units(text: str, kind: str) -> List[str]:
    """Split the source into its separable points, by channel convention."""
    if kind == "thread":
        parts = re.split(r"(?m)^\s*\(?\d{1,2}\s*[/)]\s*\d{0,2}\s*", text)
    elif kind in ("article", "newsletter"):
        parts = re.split(r"(?m)^\s{0,3}#{1,6}\s.*$", text)
    else:
        parts = re.split(r"\n\s*\n", text)
    units = [p.strip() for p in parts if len(WORD_RE.findall(p)) >= 25]
    return units


def clean(sentence: str) -> str:
    """Strip leading markers, timestamps and labels from a sentence for display."""
    sentence = re.sub(r"^\s*\[?\(?\d{1,2}:\d{2}(:\d{2})?\)?\]?\s*", "", sentence)
    sentence = re.sub(r"^\s*\(?\d{1,2}\s*[/)]\s*\d{0,2}\s*", "", sentence)
    sentence = re.sub(r"^\s{0,3}#{1,6}\s*", "", sentence)
    sentence = re.sub(r"^[A-Z][\w'-]*( [A-Z0-9][\w'-]*)?:\s+", "", sentence)
    return re.sub(r"\s+", " ", sentence).strip()


def rank_spine(text: str, limit: int) -> List[Dict[str, Any]]:
    """Score every sentence for carry-over value and return the best few.

    A sentence scores for holding a figure, a first-person voice, a turn
    (a contrast or change of mind) and a workable length, and loses points
    for carrying a channel artefact. Ties keep source order.
    """
    scored: List[Dict[str, Any]] = []
    for position, raw in enumerate(sentences(text)):
        sentence = clean(raw)
        words = len(WORD_RE.findall(sentence))
        if words < 6:
            continue
        reasons: List[str] = []
        score = 0
        if NUMBER_RE.search(sentence):
            score += 3
            reasons.append("figure")
        if FIRST_PERSON_RE.search(sentence):
            score += 2
            reasons.append("first person")
        if TURN_RE.search(sentence):
            score += 2
            reasons.append("turn")
        if 8 <= words <= 30:
            score += 1
        if any(p.search(sentence) for rule, p in ARTEFACTS if rule != "RP-004"):
            score -= 2
            reasons.append("needs cleaning")
        if score >= 3:
            scored.append({"score": score, "position": position,
                           "reasons": reasons, "sentence": sentence})
    scored.sort(key=lambda s: (-s["score"], s["position"]))
    return scored[:limit]


def shape_findings(text: str, body: str, units: List[str], posts: int,
                   opening_chars: int) -> List[Dict[str, Any]]:
    """Check the opening, voice, concreteness and density of the source."""
    out: List[Dict[str, Any]] = []
    opening = body[:opening_chars]
    if stale_opening(opening) or not (
            NUMBER_RE.search(opening) or FIRST_PERSON_RE.search(opening)):
        out.append(finding("RP-020", f"first {opening_chars} characters: "
                           f"'{opening[:90].replace(chr(10), ' ')}...'", [1]))
    if not FIRST_PERSON_RE.search(text):
        out.append(finding("RP-021", "no I, we, my or our anywhere in the source", []))
    if not NUMBER_RE.search(body):
        out.append(finding("RP-022", "no number or date anywhere in the source", []))
    if posts > 1:
        out.append(finding("RP-023", f"{len(units)} separable points of 25+ words; "
                           f"length suggests about {posts} posts", []))
    lengths = [len(WORD_RE.findall(s)) for s in sentences(text)]
    if lengths and sum(lengths) / len(lengths) > 26:
        out.append(finding("RP-024", f"average sentence is "
                           f"{sum(lengths) / len(lengths):.0f} words", []))
    paragraphs = [p for p in re.split(r"\n\s*\n", text) if p.strip()]
    longest = max((len(WORD_RE.findall(p)) for p in paragraphs), default=0)
    if longest > 90:
        out.append(finding("RP-025", f"longest paragraph is {longest} words", []))
    return out


def analyse(text: str, kind: str, target_min: int, target_max: int,
            opening_chars: int, spine: int) -> Dict[str, Any]:
    """Run the full analysis and assemble the report."""
    kind = detect_type(text) if kind == "auto" else kind
    units = split_units(text, kind)
    body = "\n".join(clean(line) for line in text.split("\n")).strip()
    chars = len(text.strip())
    words = len(WORD_RE.findall(text))
    posts = 1
    if chars > 1.5 * target_max and len(units) >= 3:
        posts = min(len(units), max(2, round(chars / target_min)))
    if posts > 1:
        move = (f"split: the source is {chars / target_max:.1f}x the upper band; "
                f"plan about {posts} posts, one point each")
    elif chars > target_max:
        move = (f"compress: the source is {chars / target_max:.1f}x the upper band; "
                "keep one point and cut the rest")
    elif chars < target_min:
        move = (f"expand: the source is {chars} characters, "
                f"{target_min - chars} short of the band")
    else:
        move = "fits the band: rebuild the delivery, keep the length"
    findings = scan_artefacts(text) + shape_findings(text, body, units, posts,
                                                     opening_chars)
    findings.sort(key=lambda f: (SEVERITY_RANK[f["severity"]], f["id"]))
    return {
        "source_type": kind,
        "measures": {"characters": chars, "words": words,
                     "sentences": len(sentences(text)),
                     "paragraphs": len([p for p in re.split(r"\n\s*\n", text) if p.strip()]),
                     "figures": len(NUMBER_RE.findall(body)),
                     "first_person_uses": len(FIRST_PERSON_RE.findall(text))},
        "target_band": {"min_chars": target_min, "max_chars": target_max,
                        "opening_chars": opening_chars},
        "move": move,
        "posts_in_source": posts,
        "units": [" ".join(clean(u).split()[:12]) + " ..." for u in units],
        "counts": {s: sum(1 for f in findings if f["severity"] == s) for s in SEVERITY_RANK},
        "findings": findings,
        "spine_candidates": rank_spine(text, spine),
    }


def output(report: Dict[str, Any], fmt: str) -> None:
    """Print the report as JSON or as a human-readable summary."""
    if fmt == "json":
        print(json.dumps(report, indent=2))
        return
    m, band = report["measures"], report["target_band"]
    print(f"Repurposing analysis (source type: {report['source_type']})")
    print(f"Size: {m['characters']} characters, {m['words']} words, "
          f"{m['sentences']} sentences, {m['paragraphs']} paragraphs")
    print(f"Carries: {m['figures']} figures, {m['first_person_uses']} first-person uses")
    print(f"Target band: {band['min_chars']}-{band['max_chars']} characters "
          f"(heuristic), opening window {band['opening_chars']}")
    print(f"Move: {report['move']}")
    print(f"Posts in this source: {report['posts_in_source']}")
    print("=" * 72)
    print("Findings: " + ", ".join(f"{n} {s}" for s, n in report["counts"].items()))
    for item in report["findings"]:
        where = f"  lines {', '.join(map(str, item['lines']))}" if item["lines"] else ""
        print(f"[{item['severity'].upper():<7}] {item['id']}  {item['title']}{where}"
              f"\n          evidence: {item['evidence']}\n          do: {item['action']}")
    print("-" * 72)
    print("Spine candidates (carry the idea, rewrite the sentence):")
    for number, item in enumerate(report["spine_candidates"], start=1):
        print(f"{number}. [{item['score']}: {', '.join(item['reasons'])}] {item['sentence']}")
    if not report["spine_candidates"]:
        print("   None scored high enough. Ask the author for the one thing "
              "they want a reader to remember.")
    if report["posts_in_source"] > 1:
        print("-" * 72)
        print("Separable points (one post each):")
        for number, unit in enumerate(report["units"], start=1):
            print(f"{number}. {unit}")


def main() -> None:
    """Parse arguments, analyse the source, print the report, apply the gate."""
    parser = argparse.ArgumentParser(
        description="Measure a source text and flag what will not survive the "
                    "move to LinkedIn.",
        epilog="Exit codes: 0 analysis completed, 1 a finding reached "
               "--fail-on, 2 bad input.")
    parser.add_argument("--input", required=True,
                        help="Path to the source text file (.txt or .md).")
    parser.add_argument("--source-type", choices=SOURCE_TYPES, default="auto",
                        help="Channel the source was made for (default: auto-detect).")
    parser.add_argument("--target-min", type=int, default=TARGET_MIN_CHARS,
                        help=f"Lower end of the target length band in characters "
                             f"(default: {TARGET_MIN_CHARS}, a house heuristic).")
    parser.add_argument("--target-max", type=int, default=TARGET_MAX_CHARS,
                        help=f"Upper end of the target length band in characters "
                             f"(default: {TARGET_MAX_CHARS}, a house heuristic).")
    parser.add_argument("--opening-chars", type=int, default=OPENING_CHARS,
                        help=f"Characters treated as the opening window (default: "
                             f"{OPENING_CHARS}; verify the preview cut-off in the product).")
    parser.add_argument("--spine", type=int, default=5,
                        help="How many spine candidates to list (default: 5).")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                        help="Output format (default: text).")
    parser.add_argument("--fail-on", choices=["blocker", "rework"], default=None,
                        help="Exit 1 if any finding at or above this level exists.")
    args = parser.parse_args()
    if not 0 < args.target_min < args.target_max:
        fail("--target-min must be above 0 and below --target-max.")
    if args.opening_chars < 40 or args.spine < 1:
        fail("--opening-chars must be 40 or more and --spine 1 or more.")
    text = load_text(Path(args.input), "source", min_words=40)
    report = analyse(text, args.source_type, args.target_min, args.target_max,
                     args.opening_chars, args.spine)
    output(report, args.format)
    if args.fail_on and any(SEVERITY_RANK[f["severity"]] <= SEVERITY_RANK[args.fail_on]
                            for f in report["findings"]):
        sys.exit(1)


if __name__ == "__main__":
    main()
