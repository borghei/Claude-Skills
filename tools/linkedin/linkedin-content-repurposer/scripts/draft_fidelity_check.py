#!/usr/bin/env python3
"""Check a repurposed LinkedIn draft against the source it was made from.

Compares two local text files. Blocks on figures and quotations in the draft
that the source does not contain, flags a draft that is mostly copied
sentences, lists channel artefacts that survived the rewrite, and checks the
opening and the length. With an optional story bank file, figures from ready
entries are also accepted and the bank's never-name and no-go lists are
enforced. Nothing is posted, fetched or sent.

Usage:
    python3 draft_fidelity_check.py --source thread.txt --draft draft.txt
    python3 draft_fidelity_check.py --source talk.txt --draft draft.txt \
        --format json
    python3 draft_fidelity_check.py --source thread.txt --draft draft.txt \
        --story-bank story_bank.json --max-copied 0.4 --fail-on blocker

Exit codes:
    0  check completed (and no finding reached the --fail-on level)
    1  gate failed: a finding at or above --fail-on exists
    2  bad input: a file is missing, unreadable, empty, or not a story bank
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

sys.path.insert(0, str(Path(__file__).resolve().parent))
from repurpose_rules import (  # noqa: E402
    OPENING_CHARS, SEVERITY_RANK, TARGET_MAX_CHARS, TARGET_MIN_CHARS, WORD_RE,
    fail, figures, finding, load_text, scan_artefacts, sentences, stale_opening,
    strip_markers)

QUOTE_RE = re.compile(r'"([^"\n]{12,})"')
NAME_RE = re.compile(r"(?<=[a-z,;:] )([A-Z][a-z]+(?:[ -][A-Z][a-z]+)*)")


def squash(text: str) -> str:
    """Lowercase text and reduce it to single-spaced word characters."""
    return " ".join(WORD_RE.findall(text.lower()))


def load_bank(path: Path) -> Dict[str, Any]:
    """Load an optional story bank file, exiting with guidance if it is not one."""
    try:
        bank = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError) as exc:
        fail(f"cannot read story bank {path}: {getattr(exc, 'strerror', None) or exc}")
    except json.JSONDecodeError as exc:
        fail(f"story bank {path} is not valid JSON (line {exc.lineno}): {exc.msg}")
    if not isinstance(bank, dict) or not isinstance(bank.get("entries"), list):
        fail(f"{path} is not a story bank: expected a JSON object with an "
             "'entries' array.")
    return bank


def bank_figures(bank: Dict[str, Any]) -> Set[str]:
    """Collect every figure that appears in the bank's ready entries."""
    allowed: Set[str] = set()
    for entry in bank["entries"]:
        if isinstance(entry, dict) and entry.get("status") == "ready":
            allowed |= figures(json.dumps(entry, ensure_ascii=False), with_words=True)
    return allowed


def check_figures(source: str, draft: str, extra: Set[str]) -> List[Dict[str, Any]]:
    """Flag numbers in the draft that neither the source nor the bank contains."""
    allowed = figures(strip_markers(source), with_words=True) | extra
    new = sorted(figures(draft) - allowed, key=lambda v: (len(v), v))
    if not new:
        return []
    lines = [n for n, line in enumerate(draft.split("\n"), start=1)
             if figures(line) & set(new)]
    return [finding("FD-001", "not in source: " + ", ".join(new), lines)]


def check_quotes(source: str, draft: str) -> List[Dict[str, Any]]:
    """Flag quoted passages of four or more words that the source does not contain."""
    haystack = squash(source)
    missing = [q for q in QUOTE_RE.findall(draft)
               if len(WORD_RE.findall(q)) >= 4 and squash(q) not in haystack]
    if not missing:
        return []
    return [finding("FD-002", "; ".join(f'"{q[:70]}"' for q in missing[:3]), [])]


def copied_share(source: str, draft: str) -> Dict[str, Any]:
    """Measure how many of the draft's sentences are lifted verbatim from the source."""
    haystack = squash(source)
    eligible = [s for s in sentences(draft) if len(WORD_RE.findall(s)) >= 6]
    copied = [s for s in eligible if squash(s) in haystack]
    share = round(len(copied) / len(eligible), 2) if eligible else 0.0
    return {"eligible": len(eligible), "copied": len(copied), "share": share}


def check_shape(draft: str, target_min: int, target_max: int,
                opening_chars: int) -> List[Dict[str, Any]]:
    """Check the draft's length, opening and paragraphing."""
    out: List[Dict[str, Any]] = []
    chars = len(draft.strip())
    if not target_min <= chars <= target_max:
        out.append(finding("FD-005", f"{chars} characters against a band of "
                           f"{target_min}-{target_max}", []))
    opening = draft.strip()[:opening_chars]
    if stale_opening(opening):
        out.append(finding("FD-006", f"opens: '{opening[:80].replace(chr(10), ' ')}...'",
                           [1]))
    paragraphs = [p for p in re.split(r"\n\s*\n", draft) if p.strip()]
    longest = max((len(WORD_RE.findall(p)) for p in paragraphs), default=0)
    if (len(paragraphs) < 2 and chars > 400) or longest > 90:
        out.append(finding("FD-007", f"{len(paragraphs)} paragraph(s), longest "
                           f"{longest} words", []))
    return out


def check_names(source: str, draft: str) -> List[Dict[str, Any]]:
    """Note capitalised names that occur mid-sentence in the draft but not in the source."""
    known = squash(source)
    new: List[str] = []
    for name in NAME_RE.findall(draft):
        if name != "I" and squash(name) not in known and name not in new:
            new.append(name)
    return [finding("FD-008", ", ".join(new[:8]), [])] if new else []


def check_bank_limits(bank: Dict[str, Any], draft: str) -> List[Dict[str, Any]]:
    """Enforce the bank's never-name and no-go lists on the draft."""
    lowered = draft.lower()
    naming = bank.get("naming") if isinstance(bank.get("naming"), dict) else {}
    banned = list(naming.get("never") or []) + list(bank.get("no_go") or [])
    hits = [str(t) for t in banned
            if isinstance(t, str) and t.strip() and t.strip().lower() in lowered]
    return [finding("FD-004", ", ".join(hits), [])] if hits else []


def check(source: str, draft: str, bank: Optional[Dict[str, Any]], target_min: int,
          target_max: int, opening_chars: int, max_copied: float) -> Dict[str, Any]:
    """Run every check and assemble the report."""
    findings = check_figures(source, draft, bank_figures(bank) if bank else set())
    findings += check_quotes(source, draft)
    overlap = copied_share(source, draft)
    if overlap["eligible"] >= 4 and overlap["share"] > max_copied:
        findings.append(finding(
            "FD-003", f"{overlap['copied']} of {overlap['eligible']} sentences are "
            f"verbatim ({overlap['share']:.0%}, limit {max_copied:.0%})", []))
    findings += scan_artefacts(draft)
    findings += check_shape(draft, target_min, target_max, opening_chars)
    findings += check_names(source, draft)
    if bank:
        findings += check_bank_limits(bank, draft)
    findings.sort(key=lambda f: (SEVERITY_RANK[f["severity"]], f["id"]))
    counts = {s: sum(1 for f in findings if f["severity"] == s) for s in SEVERITY_RANK}
    if counts["blocker"]:
        verdict = "do not hand on: the draft says something the source does not"
    elif counts["rework"]:
        verdict = "faithful, but not yet native: rework the listed items"
    else:
        verdict = "faithful and clean: ready for the author to read"
    return {
        "verdict": verdict,
        "draft": {"characters": len(draft.strip()),
                  "words": len(WORD_RE.findall(draft)),
                  "paragraphs": len([p for p in re.split(r"\n\s*\n", draft) if p.strip()])},
        "source": {"characters": len(source.strip()),
                   "words": len(WORD_RE.findall(source))},
        "copied_sentences": overlap, "story_bank_used": bank is not None,
        "counts": counts, "findings": findings,
    }


def output(report: Dict[str, Any], fmt: str) -> None:
    """Print the report as JSON or as a human-readable summary."""
    if fmt == "json":
        print(json.dumps(report, indent=2))
        return
    draft, overlap = report["draft"], report["copied_sentences"]
    print(f"Draft fidelity check: {report['verdict']}")
    print(f"Draft: {draft['characters']} characters, {draft['words']} words, "
          f"{draft['paragraphs']} paragraphs   Source: "
          f"{report['source']['characters']} characters")
    print(f"Copied sentences: {overlap['copied']} of {overlap['eligible']} "
          f"({overlap['share']:.0%})   Story bank: "
          f"{'used' if report['story_bank_used'] else 'not supplied'}")
    print("=" * 72)
    print("Findings: " + ", ".join(f"{n} {s}" for s, n in report["counts"].items()))
    for item in report["findings"]:
        where = f"  lines {', '.join(map(str, item['lines']))}" if item["lines"] else ""
        print(f"[{item['severity'].upper():<7}] {item['id']}  {item['title']}{where}"
              f"\n          evidence: {item['evidence']}\n          do: {item['action']}")
    if not report["findings"]:
        print("No findings. The author still reads it before it goes anywhere.")


def main() -> None:
    """Parse arguments, run the check, print the report, apply the gate."""
    parser = argparse.ArgumentParser(
        description="Check a repurposed LinkedIn draft against the source it "
                    "was made from.",
        epilog="Exit codes: 0 check completed, 1 a finding reached --fail-on, "
               "2 bad input.")
    parser.add_argument("--source", required=True,
                        help="Path to the original source text file.")
    parser.add_argument("--draft", required=True,
                        help="Path to the repurposed draft text file.")
    parser.add_argument("--story-bank", default=None,
                        help="Optional story bank JSON; its ready entries widen "
                             "the allowed figures and its never-name and no-go "
                             "lists are enforced.")
    parser.add_argument("--target-min", type=int, default=TARGET_MIN_CHARS,
                        help=f"Lower end of the length band in characters "
                             f"(default: {TARGET_MIN_CHARS}, a house heuristic).")
    parser.add_argument("--target-max", type=int, default=TARGET_MAX_CHARS,
                        help=f"Upper end of the length band in characters "
                             f"(default: {TARGET_MAX_CHARS}, a house heuristic).")
    parser.add_argument("--opening-chars", type=int, default=OPENING_CHARS,
                        help=f"Characters treated as the opening window "
                             f"(default: {OPENING_CHARS}).")
    parser.add_argument("--max-copied", type=float, default=0.5,
                        help="Largest share of draft sentences that may be "
                             "verbatim from the source, 0 to 1 (default: 0.5).")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                        help="Output format (default: text).")
    parser.add_argument("--fail-on", choices=["blocker", "rework"], default=None,
                        help="Exit 1 if any finding at or above this level exists.")
    args = parser.parse_args()
    if not 0 < args.target_min < args.target_max:
        fail("--target-min must be above 0 and below --target-max.")
    if not 0 <= args.max_copied <= 1 or args.opening_chars < 40:
        fail("--max-copied must be between 0 and 1 and --opening-chars 40 or more.")
    source = load_text(Path(args.source), "source", min_words=20)
    draft = load_text(Path(args.draft), "draft", min_words=20)
    bank = load_bank(Path(args.story_bank)) if args.story_bank else None
    try:
        report = check(source, draft, bank, args.target_min, args.target_max,
                       args.opening_chars, args.max_copied)
    except (AttributeError, KeyError, TypeError) as exc:
        fail(f"the story bank has a field of the wrong type ({exc}).")
    output(report, args.format)
    if args.fail_on and any(SEVERITY_RANK[f["severity"]] <= SEVERITY_RANK[args.fail_on]
                            for f in report["findings"]):
        sys.exit(1)


if __name__ == "__main__":
    main()
