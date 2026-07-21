#!/usr/bin/env python3
"""Score a draft status update for completeness and executive readability.

Usage:
    python3 status_update_scorer.py --input sample_status_update.json
    python3 status_update_scorer.py --input sample_status_update.json --format json
    python3 status_update_scorer.py --text draft.md --audience exec
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

# Cue phrases that mark each of the four load-bearing elements of a status update.
ELEMENT_CUES: Dict[str, List[str]] = {
    "progress": [r"\bshipped\b", r"\blanded\b", r"\bcompleted?\b", r"\bdelivered\b",
                 r"\bprogress\b", r"\bhighlights?\b", r"\bdone this week\b", r"\bmerged\b"],
    "risk": [r"\brisks?\b", r"\bblocked?\b", r"\bblockers?\b", r"\bat risk\b",
             r"\bslip(?:ping|page)?\b", r"\bconcerns?\b", r"\bthreat\b", r"\bdelay(?:ed|s)?\b"],
    "decision": [r"\bdecisions? needed\b", r"\bneed a decision\b", r"\bdecide\b",
                 r"\bapprov(?:e|al)\b", r"\bsign-?off\b", r"\btrade-?off\b", r"\brecommend(?:ation)?\b"],
    "ask": [r"\basks?\b", r"\bwe need\b", r"\brequesting\b", r"\bhelp with\b",
            r"\bunblock\b", r"\bplease\b", r"\bby (?:mon|tue|wed|thu|fri)"],
}
HEDGES = [r"\bsomewhat\b", r"\bfairly\b", r"\bmostly\b", r"\bshould be fine\b", r"\bhopefully\b",
          r"\bmore or less\b", r"\bon track-?ish\b", r"\bwe think\b", r"\bprobably\b", r"\bkind of\b"]
JARGON = [r"\bsynerg", r"\bleverag", r"\bcircle back\b", r"\bboil the ocean\b", r"\bnorth star\b",
          r"\bdouble down\b", r"\bbandwidth\b", r"\blow-hanging fruit\b", r"\bparadigm\b"]
STATUS_TOKENS = [r"\bgreen\b", r"\byellow\b", r"\bamber\b", r"\bred\b",
                 r"\bon track\b", r"\bat risk\b", r"\boff track\b"]


def read_draft(args: argparse.Namespace) -> Dict[str, Any]:
    """Load the draft update from either a JSON payload or a raw text/markdown file."""
    if args.input:
        path = Path(args.input)
        try:
            doc = json.loads(path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            raise SystemExit(f"error: file not found: {path}")
        except json.JSONDecodeError as exc:
            raise SystemExit(f"error: {path} is not valid JSON ({exc.msg}, line {exc.lineno})")
        if "body" not in doc:
            raise SystemExit("error: status JSON needs a 'body' key holding the draft text")
        return doc
    path = Path(args.text)
    try:
        return {"title": path.stem, "audience": args.audience, "body": path.read_text(encoding="utf-8")}
    except FileNotFoundError:
        raise SystemExit(f"error: file not found: {path}")


def sentences(body: str) -> List[str]:
    """Split prose into sentences, ignoring markdown bullets and heading markers."""
    prose = re.sub(r"^[#>\-*\d.\s]+", "", body, flags=re.MULTILINE)
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", prose) if s.strip()]


def score_completeness(body: str) -> Tuple[int, Dict[str, bool], List[str]]:
    """Award up to 40 points for the four required elements: progress, risk, decision, ask."""
    low = body.lower()
    found = {k: any(re.search(p, low) for p in cues) for k, cues in ELEMENT_CUES.items()}
    fixes = []
    labels = {
        "progress": "State what actually moved this period, with a number attached.",
        "risk": "Name the top risk and its owner — silence reads as 'nothing is wrong'.",
        "decision": "Say which decision you need made and by when, or say 'no decisions needed'.",
        "ask": "End with one explicit ask. An update with no ask does not need a reader.",
    }
    for key, ok in found.items():
        if not ok:
            fixes.append(f"Missing {key}: {labels[key]}")
    return sum(10 for ok in found.values() if ok), found, fixes


def score_readability(body: str) -> Tuple[int, Dict[str, Any], List[str]]:
    """Award up to 35 points for lede placement, sentence length, quantification and plain language."""
    fixes: List[str] = []
    sents = sentences(body)
    words = re.findall(r"[A-Za-z']+", body)
    avg_len = round(len(words) / max(len(sents), 1), 1)
    opening = " ".join(sents[:2]).lower() if sents else ""
    lede = any(re.search(p, opening) for p in STATUS_TOKENS)
    numbers = len(re.findall(r"\b\d+(?:[.,]\d+)?%?\b", body))
    hedges = sum(len(re.findall(p, body.lower())) for p in HEDGES)
    jargon = sum(len(re.findall(p, body.lower())) for p in JARGON)

    score = 0
    if lede:
        score += 12
    else:
        fixes.append("Buried lede: put the overall verdict (green/yellow/red, on track/at risk) "
                     "in the first sentence.")
    if avg_len <= 22:
        score += 10
    elif avg_len <= 28:
        score += 5
        fixes.append(f"Sentences average {avg_len} words — trim toward 18-22 for skim readers.")
    else:
        fixes.append(f"Sentences average {avg_len} words — an exec will stop reading. Split them.")
    if numbers >= 3:
        score += 8
    elif numbers >= 1:
        score += 4
        fixes.append("Only one or two quantified claims — attach numbers to progress and risk.")
    else:
        fixes.append("No numbers anywhere. Unquantified progress is indistinguishable from no progress.")
    penalty = min(5, hedges + jargon)
    score += 5 - penalty
    if hedges:
        fixes.append(f"{hedges} hedging phrase(s) — commit to a position or state the unknown plainly.")
    if jargon:
        fixes.append(f"{jargon} jargon phrase(s) — replace with the concrete thing that happened.")
    metrics = {"avg_sentence_words": avg_len, "sentences": len(sents), "quantified_claims": numbers,
               "hedges": hedges, "jargon": jargon, "verdict_in_lede": lede}
    return max(score, 0), metrics, fixes


def score_skimmability(body: str) -> Tuple[int, Dict[str, Any], List[str]]:
    """Award up to 25 points for structure: headings, bullets, paragraph and total length."""
    fixes: List[str] = []
    lines = [ln for ln in body.splitlines() if ln.strip()]
    headings = sum(1 for ln in lines if ln.lstrip().startswith("#"))
    bullets = sum(1 for ln in lines if re.match(r"^\s*[-*+]\s+|^\s*\d+[.)]\s+", ln))
    paragraphs = [p for p in re.split(r"\n\s*\n", body) if p.strip() and not p.lstrip().startswith(("#", "-", "*"))]
    longest = max((len(re.findall(r"[A-Za-z']+", p)) for p in paragraphs), default=0)
    total_words = len(re.findall(r"[A-Za-z']+", body))

    score = 0
    if headings >= 3:
        score += 9
    elif headings >= 1:
        score += 4
        fixes.append("Fewer than 3 headings — a skimmer needs labelled landing zones.")
    else:
        fixes.append("No headings. Add named sections so a reader can jump to the part they own.")
    if bullets >= 4:
        score += 8
    elif bullets >= 1:
        score += 4
    else:
        fixes.append("No bullets — dense prose is the most common reason updates go unread.")
    if longest <= 80:
        score += 4
    else:
        fixes.append(f"Longest paragraph is {longest} words — cap paragraphs at 80.")
    if total_words <= 400:
        score += 4
    else:
        fixes.append(f"{total_words} words total — a weekly update over 400 words loses its audience.")
    return score, {"headings": headings, "bullets": bullets, "longest_paragraph_words": longest,
                   "total_words": total_words}, fixes


def grade(total: int) -> str:
    """Map a 0-100 score onto a send/revise/rewrite verdict."""
    if total >= 85:
        return "SEND"
    if total >= 70:
        return "SEND AFTER QUICK FIXES"
    if total >= 50:
        return "REVISE"
    return "REWRITE"


def output(report: Dict[str, Any], fmt: str) -> None:
    """Print the score report as JSON or as a human-readable report."""
    if fmt == "json":
        print(json.dumps(report, indent=2))
        return
    print(f"STATUS UPDATE SCORE — {report['title']} (audience: {report['audience']})")
    print("=" * 62)
    print(f"Total: {report['score']}/100   Verdict: {report['verdict']}\n")
    for name, sub in report["dimensions"].items():
        print(f"  {name:<16}{sub['score']:>3}/{sub['max']}")
    print("\nELEMENTS PRESENT")
    for key, ok in report["elements"].items():
        print(f"  [{'x' if ok else ' '}] {key}")
    if report["fixes"]:
        print("\nFIXES, HIGHEST LEVERAGE FIRST")
        for i, fix in enumerate(report["fixes"], 1):
            print(f"  {i}. {fix}")
    else:
        print("\nNo fixes required. Send it.")


def main() -> None:
    """Parse arguments, score the draft update and print the report."""
    parser = argparse.ArgumentParser(
        description="Score a draft status update for completeness and executive readability.")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--input", help="path to a JSON draft ({title, audience, body})")
    source.add_argument("--text", help="path to a raw markdown/plain-text draft")
    parser.add_argument("--audience", choices=["exec", "team", "board", "customer"], default="exec",
                        help="reader the draft targets, used when --text is given (default: exec)")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                        help="output format (default: text)")
    args = parser.parse_args()
    try:
        doc = read_draft(args)
        body = str(doc["body"])
        c_score, elements, c_fixes = score_completeness(body)
        r_score, r_metrics, r_fixes = score_readability(body)
        s_score, s_metrics, s_fixes = score_skimmability(body)
        total = c_score + r_score + s_score
        output({
            "title": doc.get("title", "untitled"),
            "audience": doc.get("audience", args.audience),
            "score": total,
            "verdict": grade(total),
            "dimensions": {
                "completeness": {"score": c_score, "max": 40},
                "readability": {"score": r_score, "max": 35, "metrics": r_metrics},
                "skimmability": {"score": s_score, "max": 25, "metrics": s_metrics},
            },
            "elements": elements,
            "fixes": c_fixes + r_fixes + s_fixes,
        }, args.format)
    except SystemExit:
        raise
    except (KeyError, TypeError, ValueError) as exc:
        print(f"error: could not score the draft — {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
