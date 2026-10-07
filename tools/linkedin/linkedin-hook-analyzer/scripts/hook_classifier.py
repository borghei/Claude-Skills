#!/usr/bin/env python3
"""Extract and classify the opening-line pattern of saved LinkedIn posts.

Reads posts the user pasted into a text file (separated by lines containing
only '---', each optionally starting with a '# label' line) or a JSON list of
{"label", "text"} objects. For each post it isolates the opening, scores it
against the pattern table in hook_patterns.py, and prints the pattern, a
confidence, the cues that fired, a slot template for reuse, the body shape,
the close type and any cautions. Offline only: it reads the file you give it.

Usage:
    python3 hook_classifier.py --input saved_posts.txt
    python3 hook_classifier.py --input saved_posts.txt --format json
    python3 hook_classifier.py --input swipe.json --fold-chars 200 --summary-only

Exit codes:
    0  posts classified
    2  bad input (missing, empty, unreadable or malformed file; no posts found)
"""

import argparse
import json
import re
import statistics
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent))
from hook_patterns import CUES, PATTERNS, PROPER_RE, detect_cues, fail  # noqa: E402

BAIT_RE = re.compile(r"what do you think\?|\bagree\?|tag someone|repost if|follow (?:me )?for more|"
                     r"comment .{1,25} (?:below|and i'll)", re.IGNORECASE)
HASHTAG_RE = re.compile(r"(?<!\w)#[A-Za-z]\w*")
# (pattern, slot) applied in order to turn an opening into a reusable template
SLOT_SUBS = [
    (re.compile(r"[\"“][^\"”]{4,}[\"”]"), '"{their exact words}"'),
    (re.compile(r"[$£€]\s?\d[\d,.]*(?:\s?(?:k|m|bn)\b)?", re.IGNORECASE), "{amount}"),
    (re.compile(r"\d[\d,.]*\s?%"), "{percent}"),
    (CUES["time_anchor"], "{when}"),
    (re.compile(r"\b\d[\d,.:]*\b"), "{number}"),
    (PROPER_RE, "{name}"),
]


def load_posts(path_arg: str) -> List[Dict[str, str]]:
    """Load posts from a '---'-separated text file or a JSON list; exit 2 on problems."""
    try:
        raw = Path(path_arg).read_text(encoding="utf-8")
    except (FileNotFoundError, IsADirectoryError):
        fail(f"no readable file at {path_arg}. Pass a .txt of pasted posts or a .json list.")
    except (OSError, UnicodeDecodeError) as exc:
        fail(f"cannot read {path_arg} as UTF-8 text ({exc.__class__.__name__}).")
    posts: List[Dict[str, str]] = []
    if path_arg.lower().endswith(".json"):
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            fail(f"{path_arg} is not valid JSON (line {exc.lineno}): {exc.msg}")
        rows = data.get("posts") if isinstance(data, dict) else data
        if not isinstance(rows, list):
            fail("JSON input must be a list of {\"label\", \"text\"} objects, or an object "
                 "with a 'posts' list.")
        for index, row in enumerate(rows, 1):
            text = row.get("text", "") if isinstance(row, dict) else str(row)
            label = row.get("label", "") if isinstance(row, dict) else ""
            if str(text).strip():
                posts.append({"label": str(label) or f"post {index}", "text": str(text).strip()})
    else:
        for index, chunk in enumerate(re.split(r"(?m)^\s*-{3,}\s*$", raw), 1):
            rows = [ln for ln in chunk.strip().splitlines()]
            label = f"post {index}"
            if rows and rows[0].startswith("# "):
                label, rows = rows[0][2:].strip(), rows[1:]
            text = "\n".join(rows).strip()
            if text:
                posts.append({"label": label, "text": text})
    if not posts:
        fail(f"{path_arg} contains no posts. Paste each post's full text, separated by a "
             "line containing only ---")
    return posts


def score_patterns(fired: List[str]) -> List[Tuple[str, int]]:
    """Score every pattern whose core cue fired; highest first, table order on ties."""
    scored = []
    for order, (slug, pattern) in enumerate(PATTERNS.items()):
        if not any(core in fired for core in pattern["core"]):
            continue
        total = sum(weight for cue, weight in pattern["weights"].items() if cue in fired)
        scored.append((slug, total, order))
    scored.sort(key=lambda row: (-row[1], row[2]))
    return [(slug, total) for slug, total, _ in scored]


def body_shape(rows: List[str], paragraphs: List[str]) -> str:
    """Describe how the body after the opening is laid out."""
    numbered = sum(1 for r in rows if re.match(r"\d+[.)]\s", r))
    bullets = sum(1 for r in rows if re.match(r"[-•*→▪✓]\s", r))
    single = sum(1 for p in paragraphs if "\n" not in p and len(p.split()) <= 25)
    if numbered >= 3:
        return f"numbered list ({numbered} items)"
    if bullets >= 3:
        return f"bulleted list ({bullets} items)"
    if len(paragraphs) <= 2:
        return "single block"
    if single / len(paragraphs) >= 0.7:
        return f"one-line paragraphs ({len(paragraphs)})"
    return f"story paragraphs ({len(paragraphs)})"


def close_type(rows: List[str]) -> str:
    """Classify the final prose line of a post."""
    prose = [r for r in rows if not HASHTAG_RE.match(r)] or rows
    last = prose[-1]
    if BAIT_RE.search(" ".join(prose[-2:])):
        return "stock engagement ask"
    if re.match(r"p\.?s\.?\b", last, re.IGNORECASE):
        return "postscript"
    if re.search(r"https?://|link in (?:the )?(?:first )?comment", last, re.IGNORECASE):
        return "pointer to a link"
    return "question" if last.endswith("?") else "statement"


def analyse(post: Dict[str, str], fold: int, floor: float) -> Dict[str, Any]:
    """Classify one post and assemble everything needed to reuse its opening."""
    text = post["text"]
    rows = [ln.strip() for ln in text.splitlines() if ln.strip()]
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    opening = rows[0]
    fired = detect_cues(opening)
    ranked = score_patterns(fired)
    top = ranked[0] if ranked else ("unclassified", 0)
    second = ranked[1] if len(ranked) > 1 else ("", 0)
    confidence = round(top[1] / (top[1] + second[1] + 1.0), 2) if ranked else 0.0
    slug = top[0] if confidence >= floor else "unclassified"
    template = opening
    for pattern, slot in SLOT_SUBS:
        template = pattern.sub(slot, template)
    known = PATTERNS.get(slug)
    cautions = []
    if len(opening) > fold:
        cautions.append(f"opening is {len(opening)} characters; the feed cuts near {fold}")
    if known and known["reuse"] == "caution":
        cautions.append(known["note"])
    if close_type(rows) == "stock engagement ask":
        cautions.append("the close is a stock engagement ask; do not carry it over")
    if len(HASHTAG_RE.findall(text)) > 3:
        cautions.append("more than three hashtags; not part of the pattern")
    if slug == "unclassified":
        cautions.append("no pattern fits with confidence; treat as free-form and study the "
                        "second line instead")
    return {
        "label": post["label"], "opening": opening, "opening_chars": len(opening),
        "second_line": rows[1] if len(rows) > 1 else "", "pattern": slug,
        "pattern_name": known["name"] if known else "Unclassified",
        "reuse": known["reuse"] if known else "study only", "confidence": confidence,
        "confidence_band": "high" if confidence >= 0.6 else "medium" if confidence >= 0.4 else "low",
        "runner_up": second[0], "cues": fired, "template": template,
        "reuse_note": known["note"] if known else "",
        "body_shape": body_shape(rows[1:], paragraphs), "close": close_type(rows),
        "characters": len(text), "cautions": cautions}


def summarise(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Aggregate the per-post results into a view of the whole swipe file."""
    mix = Counter(r["pattern"] for r in results)
    return {"posts": len(results),
            "pattern_mix": dict(sorted(mix.items(), key=lambda kv: (-kv[1], kv[0]))),
            "caution_patterns": sum(1 for r in results if r["reuse"] == "caution"),
            "unclassified": mix.get("unclassified", 0),
            "median_opening_chars": int(statistics.median(r["opening_chars"] for r in results)),
            "close_mix": dict(Counter(r["close"] for r in results).most_common())}


def output(results: List[Dict[str, Any]], summary: Dict[str, Any], fmt: str,
           summary_only: bool) -> None:
    """Print per-post analysis and the swipe-file summary as JSON or text."""
    if fmt == "json":
        print(json.dumps({"summary": summary, "posts": [] if summary_only else results},
                         indent=2, ensure_ascii=False))
        return
    for result in [] if summary_only else results:
        print(f"## {result['label']}")
        print(f"   opening   : {result['opening']}")
        print(f"   pattern   : {result['pattern_name']} [{result['pattern']}] "
              f"confidence {result['confidence']} ({result['confidence_band']})"
              + (f", runner-up {result['runner_up']}" if result["runner_up"] else ""))
        print(f"   cues      : {', '.join(result['cues']) or 'none'}")
        print(f"   template  : {result['template']}")
        print(f"   body/close: {result['body_shape']} / {result['close']} "
              f"({result['characters']} characters)")
        if result["reuse_note"] and result["reuse"] != "caution":
            print(f"   to reuse  : {result['reuse_note']}")
        for caution in result["cautions"]:
            print(f"   caution   : {caution}")
        print()
    print("=" * 72)
    print(f"Swipe file: {summary['posts']} posts, median opening "
          f"{summary['median_opening_chars']} characters")
    print("Pattern mix: " + ", ".join(f"{k} {v}" for k, v in summary["pattern_mix"].items()))
    print("Closes: " + ", ".join(f"{k} {v}" for k, v in summary["close_mix"].items()))
    print(f"Caution-class openings: {summary['caution_patterns']}   "
          f"Unclassified: {summary['unclassified']}")


def main() -> None:
    """Parse arguments, classify every post and print the analysis."""
    parser = argparse.ArgumentParser(
        description="Extract and classify the opening pattern of saved LinkedIn posts (offline).",
        epilog="Exit codes: 0 posts classified, 2 bad input. Classification is a "
               "keyword heuristic: check low-confidence results by eye.")
    parser.add_argument("--input", required=True,
                        help="Text file of posts separated by '---' lines (optional '# label' "
                             "first line per post), or a .json list of {label, text}.")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                        help="Output format (default: text).")
    parser.add_argument("--fold-chars", type=int, default=140,
                        help="Characters shown before the feed truncates (default: 140, a "
                             "conservative estimate as of writing; verify in the product).")
    parser.add_argument("--min-confidence", type=float, default=0.34,
                        help="Below this a post is reported as unclassified (default: 0.34).")
    parser.add_argument("--summary-only", action="store_true",
                        help="Print only the swipe-file summary.")
    args = parser.parse_args()
    if args.fold_chars < 1 or not 0 <= args.min_confidence <= 1:
        fail("--fold-chars must be positive and --min-confidence between 0 and 1.")
    results = [analyse(p, args.fold_chars, args.min_confidence) for p in load_posts(args.input)]
    output(results, summarise(results), args.format, args.summary_only)


if __name__ == "__main__":
    main()
