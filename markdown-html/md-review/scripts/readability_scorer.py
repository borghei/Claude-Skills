#!/usr/bin/env python3
"""Readability, sentence-health, and terminology consistency scorer for Markdown.

Implements Flesch Reading Ease and Flesch-Kincaid Grade Level from a built-in syllable counter,
flags long sentences and passive constructions, and audits prose against a configurable
preferred/disallowed term map. No network, no external packages.
Usage: python3 readability_scorer.py --input article.md --config review_config.json [--format json]
Exit codes: 0 = within thresholds, 1 = tool error, 2 = thresholds breached.
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

VOWELS = "aeiouy"
BE_VERBS = {"is", "are", "was", "were", "be", "been", "being", "am", "get", "gets", "got"}
PARTICIPLES = {"done", "made", "given", "taken", "seen", "known", "written", "shown", "held", "built",
               "sent", "kept", "left", "found", "lost", "told", "put", "set", "run", "read", "brought",
               "caught", "chosen", "drawn", "driven", "eaten", "fallen", "forgotten", "hidden", "meant",
               "paid", "spent", "thrown", "understood"}
ADVERBS = {"not", "also", "already", "being", "then", "still", "never", "always", "often"}
SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")
WORD_RE = re.compile(r"[A-Za-z][A-Za-z'-]*")
FLESCH_BANDS = [(90.0, "very easy (5th grade)"), (80.0, "easy (6th grade)"),
                (70.0, "fairly easy (7th grade)"), (60.0, "plain english (8th-9th grade)"),
                (50.0, "fairly difficult (10th-12th grade)"), (30.0, "difficult (college)"),
                (0.0, "very difficult (graduate)")]


@dataclass
class Issue:
    """A readability, sentence-health, or terminology finding tied to a source line."""
    rule: str
    severity: str
    line: int
    message: str


def load_config(path: str) -> Dict[str, Any]:
    """Load a review config JSON file; return {} when no path is given."""
    if not path:
        return {}
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise SystemExit(f"error: config file not found: {path}")
    except json.JSONDecodeError as exc:
        raise SystemExit(f"error: config file is not valid JSON ({exc})")

def extract_prose(path: Path) -> List[Tuple[int, str]]:
    """Return (line_number, text) prose lines, stripped of frontmatter, code, tables, and markup."""
    try:
        raw = path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        raise SystemExit(f"error: input file not found: {path}")
    except UnicodeDecodeError:
        raise SystemExit(f"error: input file is not UTF-8 text: {path}")
    start = 0
    if raw and raw[0].strip() == "---":
        start = next((i + 1 for i in range(1, len(raw)) if raw[i].strip() == "---"), 0)
    prose: List[Tuple[int, str]] = []
    fenced = False
    for number, line in enumerate(raw[start:], start=start + 1):
        stripped = line.strip()
        if stripped.startswith(("```", "~~~")):
            fenced = not fenced
            continue
        if fenced or not stripped or stripped.startswith(("|", "#")) or line.startswith("    "):
            continue
        text = re.sub(r"!\[[^\]]*\]\([^)]*\)", " ", line)
        text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
        text = re.sub(r"https?://\S+", " ", re.sub(r"`[^`]*`", " ", text))
        text = re.sub(r"[*_>#]", " ", text)
        if text.strip():
            prose.append((number, text.strip()))
    return prose

def count_syllables(word: str) -> int:
    """Count syllables in an English word using a vowel-group heuristic with silent-e handling."""
    token = re.sub(r"[^a-z]", "", word.lower())
    if not token:
        return 0
    if len(token) <= 3:
        return 1
    token = re.sub(r"^y", "", re.sub(r"(?:[^laeiouy]es|ed|[^laeiouy]e)$", "", token))
    total = len(re.findall(r"[aeiouy]+", token))
    lowered = word.lower()
    if lowered.endswith(("le", "les")) and len(word) > 2 and word[-3].lower() not in VOWELS:
        total += 1
    if lowered.endswith(("ia", "io", "ua", "eo")):
        total += 1
    return max(1, total)

def split_sentences(prose: List[Tuple[int, str]]) -> List[Tuple[int, str]]:
    """Join wrapped prose lines into blocks, then split them into (line_number, sentence) pairs."""
    blocks: List[Tuple[int, str]] = []
    buffer, anchor = "", 0
    for number, text in prose:
        if not buffer:
            anchor = number
        buffer = f"{buffer} {text}".strip()
        if re.search(r"[.!?][\"')\]]?$", buffer):
            blocks.append((anchor, buffer))
            buffer = ""
    if buffer:
        blocks.append((anchor, buffer))
    return [(number, piece.strip()) for number, block in blocks
            for piece in SENTENCE_SPLIT_RE.split(block) if len(WORD_RE.findall(piece)) >= 3]

def score_readability(sentences: List[Tuple[int, str]]) -> Dict[str, float]:
    """Compute Flesch Reading Ease, Flesch-Kincaid grade, and density stats over the sentences."""
    words = [w for _, sentence in sentences for w in WORD_RE.findall(sentence)]
    if not sentences or not words:
        return {"sentences": 0, "words": 0, "syllables": 0, "flesch": 0.0, "fk_grade": 0.0,
                "mean_sentence_words": 0.0, "complex_word_pct": 0.0}
    syllables = [count_syllables(w) for w in words]
    wps, spw = len(words) / len(sentences), sum(syllables) / len(words)
    return {"sentences": len(sentences), "words": len(words), "syllables": sum(syllables),
            "flesch": round(206.835 - 1.015 * wps - 84.6 * spw, 1),
            "fk_grade": round(0.39 * wps + 11.8 * spw - 15.59, 1),
            "mean_sentence_words": round(wps, 1),
            "complex_word_pct": round(100.0 * sum(1 for s in syllables if s >= 3) / len(words), 1)}

def band_for(flesch: float) -> str:
    """Return the human-readable band label for a Flesch Reading Ease score."""
    return next((label for floor, label in FLESCH_BANDS if flesch >= floor), "very difficult (graduate)")

def find_long_sentences(sentences: List[Tuple[int, str]], cfg: Dict[str, Any]) -> List[Issue]:
    """Flag sentences beyond the configured long and very-long word thresholds."""
    limit, hard = int(cfg.get("long_sentence_words", 30)), int(cfg.get("very_long_sentence_words", 45))
    issues: List[Issue] = []
    for number, sentence in sentences:
        count = len(WORD_RE.findall(sentence))
        if count >= hard:
            issues.append(Issue("readability.very-long-sentence", "error", number,
                                f"{count}-word sentence; split it: \"{sentence[:60]}...\""))
        elif count > limit:
            issues.append(Issue("readability.long-sentence", "warning", number,
                                f"{count}-word sentence (limit {limit}): \"{sentence[:60]}...\""))
    return issues

def find_passive(sentences: List[Tuple[int, str]]) -> List[Issue]:
    """Flag likely passive-voice constructions, at most one issue per sentence."""
    issues: List[Issue] = []
    for number, sentence in sentences:
        hits: List[str] = []
        lowered = [w.lower() for w in WORD_RE.findall(sentence)]
        for idx, word in enumerate(lowered):
            if word not in BE_VERBS:
                continue
            for offset in range(1, 4):
                if idx + offset >= len(lowered):
                    break
                nxt = lowered[idx + offset]
                if (nxt.endswith("ed") and len(nxt) > 4) or nxt in PARTICIPLES:
                    hits.append(f"{word} {nxt}")
                    break
                if nxt not in ADVERBS:
                    break
        if hits:
            issues.append(Issue("readability.passive-voice", "info", number,
                                f"{len(hits)} passive construction(s): " + ", ".join(f"'{h}'" for h in hits[:3])))
    return issues

def check_terminology(prose: List[Tuple[int, str]], term_map: Dict[str, List[str]]) -> List[Issue]:
    """Flag disallowed spellings from the preferred/disallowed term map, longest variant first."""
    issues: List[Issue] = []
    claimed: Set[Tuple[int, int, int]] = set()
    for preferred, variants in term_map.items():
        for variant in sorted(variants, key=len, reverse=True):
            flags = 0 if any(c.isupper() for c in variant) else re.IGNORECASE
            pattern = re.compile(r"(?<![\w-])" + re.escape(variant) + r"(?![\w-])", flags)
            for number, text in prose:
                for match in pattern.finditer(text):
                    span = (number, match.start(), match.end())
                    if match.group(0) == preferred or span in claimed:
                        continue
                    claimed.add(span)
                    issues.append(Issue("terminology.disallowed-term", "warning", number,
                                        f"'{match.group(0)}' should be '{preferred}'"))
    return issues

def evaluate(scores: Dict[str, float], issues: List[Issue], cfg: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Apply readability thresholds and return (passed, breach reasons).

    Only the lower Flesch bound blocks. Scoring above the band means the prose is easier than the
    audience requires, which is recorded as info and never fails the run.
    """
    reasons: List[str] = []
    low, high = float(cfg.get("target_flesch_min", 0.0)), float(cfg.get("target_flesch_max", 100.0))
    if scores["sentences"] and scores["flesch"] < low:
        reasons.append(f"Flesch {scores['flesch']} below target floor {low} (harder than the audience band)")
    elif scores["sentences"] and scores["flesch"] > high:
        issues.append(Issue("readability.simpler-than-band", "info", 1,
                            f"Flesch {scores['flesch']} above band ceiling {high}; easier than required"))
    if scores["fk_grade"] > float(cfg.get("max_grade_level", 99.0)):
        reasons.append(f"FK grade {scores['fk_grade']} above max {cfg.get('max_grade_level')}")
    if not scores["sentences"]:
        return not reasons, reasons
    long_pct = 100.0 * sum(1 for i in issues if i.rule.endswith("long-sentence")) / scores["sentences"]
    if long_pct > float(cfg.get("max_long_sentence_pct", 100.0)):
        reasons.append(f"{long_pct:.1f}% long sentences above max {cfg.get('max_long_sentence_pct')}%")
    passive_pct = 100.0 * sum(1 for i in issues if i.rule == "readability.passive-voice") / scores["sentences"]
    if passive_pct > float(cfg.get("max_passive_pct", 100.0)):
        reasons.append(f"{passive_pct:.1f}% passive sentences above max {cfg.get('max_passive_pct')}%")
    return not reasons, reasons

def output(path: Path, scores: Dict[str, float], issues: List[Issue], passed: bool,
           reasons: List[str], fmt: str) -> None:
    """Emit the readability and terminology report as human-readable text or JSON."""
    if fmt == "json":
        print(json.dumps({"file": str(path), "passed": passed, "breaches": reasons, "scores": scores,
                          "flesch_band": band_for(scores["flesch"]),
                          "issues": [i.__dict__ for i in issues]}, indent=2))
        return
    print(f"Readability & terminology — {path}\n  sentences {scores['sentences']}   "
          f"words {scores['words']}   syllables {scores['syllables']}")
    print(f"  Flesch Reading Ease : {scores['flesch']}  ({band_for(scores['flesch'])})")
    print(f"  Flesch-Kincaid grade: {scores['fk_grade']}")
    print(f"  mean sentence length: {scores['mean_sentence_words']} words   "
          f"3+ syllable words: {scores['complex_word_pct']}%\n" + "-" * 72)
    if not issues:
        print("  no sentence or terminology issues")
    for issue in sorted(issues, key=lambda i: (i.line, i.rule)):
        print(f"  [{issue.severity.upper():7}] line {issue.line:>4}  {issue.rule}: {issue.message}")
    print("-" * 72)
    for reason in reasons:
        print(f"  breach: {reason}")
    print(f"  RESULT: {'PASS' if passed else 'FAIL'}")

def main() -> None:
    """Parse arguments, score the document, print the report, and set the exit code."""
    parser = argparse.ArgumentParser(
        description="Score Markdown prose for Flesch Reading Ease, Flesch-Kincaid grade, long "
                    "sentences, passive voice, and terminology consistency against a term map.",
        epilog="Exit codes: 0 within thresholds, 1 tool error, 2 thresholds breached.")
    parser.add_argument("--input", required=True, help="Markdown file to score.")
    parser.add_argument("--config", default="",
                        help="Review config JSON supplying 'readability' thresholds and the "
                             "'terminology' preferred/disallowed term map.")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format (default: text).")
    parser.add_argument("--fail-on", choices=["any", "readability", "terminology", "never"], default="any",
                        help="What fails the run: 'any' (default), 'readability' band breaches only, "
                             "'terminology' hits only, or 'never'.")
    parser.add_argument("--no-passive", action="store_true", help="Skip the passive-voice heuristic.")
    args = parser.parse_args()
    try:
        path, cfg = Path(args.input), load_config(args.config)
        prose = extract_prose(path)
        sentences = split_sentences(prose)
        scores = score_readability(sentences)
        issues = find_long_sentences(sentences, cfg.get("readability", {}))
        if not args.no_passive:
            issues += find_passive(sentences)
        term_issues = check_terminology(prose, cfg.get("terminology", {}))
        issues += term_issues
        band_ok, reasons = evaluate(scores, issues, cfg.get("readability", {}))
        passed = {"never": True, "readability": band_ok, "terminology": not term_issues,
                  "any": band_ok and not term_issues}[args.fail_on]
        if term_issues and args.fail_on in ("any", "terminology"):
            reasons.append(f"{len(term_issues)} disallowed term usage(s)")
        output(path, scores, issues, passed, reasons, args.format)
        sys.exit(0 if passed else 2)
    except SystemExit:
        raise
    except Exception as exc:  # pragma: no cover - defensive CLI guard
        print(f"error: readability scoring failed: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
