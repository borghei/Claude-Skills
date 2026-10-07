#!/usr/bin/env python3
"""Gate a LinkedIn draft against the machine-tell catalogue before it is pasted.

Reads a plain-text draft, applies the remove / reduce / review tiers from
tell_rules.py, and reports each rule that fired with the matching text and
the fix. Works offline on text you supply; it never posts, fetches or scores
the draft against any outside service.

Usage:
    python3 tell_audit.py --input draft.txt
    python3 tell_audit.py --input draft.txt --tier review --why
    python3 tell_audit.py --input draft.txt --voice voice.json --format json
    pbpaste | python3 tell_audit.py --input - --max-load 4

Exit codes:
    0  gate passed
    1  gate failed (any remove-tier hit, or reduce-tier load above --max-load)
    2  bad input (missing, empty or unreadable file; malformed --voice JSON)
"""

import argparse
import json
import re
import statistics
import sys
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent))
from tell_rules import (  # noqa: E402
    CATALOGUE, STOCK_RE, TIERS, fail, normalise, paragraphs, read_text, sentences, words)

DASH_RE = re.compile(r"[—–]|(?<=\s)--(?=\s)")
CONTRACTION_RE = re.compile(r"\b\w+'(?:t|s|re|ve|ll|d|m)\b", re.IGNORECASE)
FIRST_PERSON_RE = re.compile(r"\b(?:I|[Ww]e|[Mm]y|[Oo]ur|[Mm]e)\b")
PROPER_RE = re.compile(r"(?<=[a-z0-9,;:] )(?!LinkedIn)[A-Z][A-Za-z]{2,}")
LIST_LINE_RE = re.compile(r"^(?:\d+[.)]|[-•*#]|P\.?S\.?)")
PER_RULE_LOAD_CAP = 6
Computed = Dict[str, Tuple[int, int, List[str]]]


def snippet(text: str, start: int, end: int) -> str:
    """Return the matched span with a little context, flattened to one line."""
    left, right = max(0, start - 18), min(len(text), end + 18)
    piece = " ".join(text[left:right].split())
    return ("..." if left else "") + piece + ("..." if right < len(text) else "")


def scoped(rule: Dict[str, Any], raw: str, norm: str) -> str:
    """Return the slice of the draft a rule applies to (opening, close, or all)."""
    rows = [ln for ln in norm.splitlines() if ln.strip()]
    if rule["scope"] == "first":
        return rows[0] if rows else ""
    if rule["scope"] == "last":
        return "\n".join(rows[-2:])
    return raw if rule["scope"] == "raw" else norm


def regex_hits(rule: Dict[str, Any], raw: str, norm: str) -> List[str]:
    """Collect evidence snippets for every match of a pattern rule."""
    target = scoped(rule, raw, norm)
    return [snippet(target, m.start(), m.end()) for m in rule["regex"].finditer(target)]


def computed_hits(norm: str) -> Computed:
    """Evaluate the rules that need counting rather than a pattern.

    Returns rule id -> (count, allowance, evidence). An allowance of -1 means
    'use the catalogue value'.
    """
    out: Computed = {}
    total = max(1, len(words(norm)))
    sents = [s for s in sentences(norm) if not LIST_LINE_RE.match(s) and not s.endswith(":")]
    frags = [s for s in sents if len(words(s)) <= 3]
    out["RD-06"] = (len(frags), -1, frags[:4])
    tiny = [p for p in paragraphs(norm) if len(words(p)) <= 2 and not LIST_LINE_RE.match(p)]
    out["RD-07"] = (len(tiny), -1, tiny[:4])

    dashes = [snippet(norm, m.start(), m.end()) for m in DASH_RE.finditer(norm)]
    dash_allow = max(1, total // 100)
    out["RD-11"] = (len(dashes), dash_allow, dashes[:3])
    out["RV-01"] = (1 if 0 < len(dashes) <= dash_allow else 0, 0, dashes[:1])

    lengths = [len(words(s)) for s in sents if len(words(s)) >= 4]
    flat = len(lengths) >= 6 and statistics.pstdev(lengths) < 3.0
    out["RD-15"] = (1 if flat else 0, -1,
                    [f"{len(lengths)} sentences, all within a few words of "
                     f"{round(statistics.mean(lengths))} words"] if flat else [])

    missing = []
    if not re.search(r"\d", norm):
        missing.append("a figure")
    if not PROPER_RE.search(norm):
        missing.append("a named person, company or place")
    if not FIRST_PERSON_RE.search(norm):
        missing.append("a first-person statement")
    out["RD-16"] = (len(missing), -1, ["missing: " + ", ".join(missing)] if missing else [])

    dense = [p for p in paragraphs(norm) if len(STOCK_RE.findall(p)) >= 3]
    out["RD-19"] = (len(dense), -1, [" ".join(p.split())[:90] + "..." for p in dense[:2]])
    stiff = total >= 120 and not CONTRACTION_RE.search(norm)
    out["RV-07"] = (1 if stiff else 0, 0, [f"{total} words, no contractions"] if stiff else [])
    return out


def load_protected(path_arg: str) -> Set[str]:
    """Read the protected rule ids from a voice fingerprint JSON file."""
    try:
        data = json.loads(Path(path_arg).read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError):
        fail(f"cannot read voice file {path_arg}. Create it with "
             "voice_fingerprint.py --input posts.txt --format json > voice.json")
    except json.JSONDecodeError as exc:
        fail(f"{path_arg} is not valid JSON (line {exc.lineno}): {exc.msg}")
    if not isinstance(data, dict) or not isinstance(data.get("protected_rules"), list):
        fail(f"{path_arg} has no 'protected_rules' list. Regenerate it with voice_fingerprint.py.")
    return {str(item.get("id", "") if isinstance(item, dict) else item).upper()
            for item in data["protected_rules"]}


def audit(raw: str, max_load: int, protected: Set[str]) -> Dict[str, Any]:
    """Run every rule against the draft and return the full gate report."""
    norm = normalise(raw)
    computed = computed_hits(norm)
    findings: List[Dict[str, Any]] = []
    counts: Dict[str, int] = {}
    for rule in CATALOGUE:
        rid, allow = rule["id"], rule["allow"]
        if rule["regex"] is not None:
            evidence = regex_hits(rule, raw, norm)
            count = len(evidence)
        elif rid == "RV-02":
            count, evidence = (1, []) if counts.get("RD-05") == 1 else (0, [])
        else:
            count, dyn_allow, evidence = computed[rid]
            allow = allow if dyn_allow < 0 else dyn_allow
        counts[rid] = count
        excess = count if rule["tier"] != "reduce" else max(0, count - allow)
        if excess <= 0:
            continue
        waived = rid in protected and rule["tier"] != "remove"
        load = 0 if waived or rule["tier"] == "review" else min(
            PER_RULE_LOAD_CAP, excess * rule["weight"])
        findings.append({
            "id": rid, "tier": rule["tier"], "name": rule["name"], "count": count,
            "allowance": allow, "excess": excess, "load": load, "waived": waived,
            "evidence": evidence[:3], "why": rule["why"], "fix": rule["fix"],
            "keep_when": rule["keep_when"]})

    blockers = sum(1 for f in findings if f["tier"] == "remove")
    habit_load = sum(f["load"] for f in findings if f["tier"] == "reduce")
    if blockers:
        verdict = "blocked: tool residue is still in the draft"
    elif habit_load > max_load:
        verdict = "rework: rewrite the flagged paragraphs, then re-run"
    elif habit_load > max_load // 2:
        verdict = "edit: fix the flagged lines; the draft is close"
    elif habit_load:
        verdict = "touch up: one or two habits left, safe to paste after a read-through"
    else:
        verdict = "clean: nothing in the remove or reduce tiers fired"
    return {
        "words": len(words(norm)), "sentences": len(sentences(norm)),
        "paragraphs": len(paragraphs(norm)), "blockers": blockers,
        "habit_load": habit_load, "max_load": max_load, "verdict": verdict,
        "passed": not blockers and habit_load <= max_load, "findings": findings}


def output(report: Dict[str, Any], fmt: str, tier: str, why: bool, source: str) -> None:
    """Print the gate report as JSON or as a readable findings list."""
    depth = TIERS.index(tier)
    shown = [f for f in report["findings"] if TIERS.index(f["tier"]) <= depth]
    if fmt == "json":
        print(json.dumps({**report, "source": source, "findings": shown},
                         indent=2, ensure_ascii=False))
        return
    print(f"Machine-tell audit: {source}")
    print(f"Words {report['words']} | sentences {report['sentences']} | "
          f"paragraphs {report['paragraphs']}")
    print(f"Blockers: {report['blockers']}   Habit load: {report['habit_load']} "
          f"(limit {report['max_load']})")
    print(f"Verdict: {'PASS' if report['passed'] else 'FAIL'} - {report['verdict']}")
    print("=" * 72)
    for item in shown:
        note = "  (kept: author habit)" if item["waived"] else ""
        print(f"[{item['tier'].upper():<6}] {item['id']} {item['name']} "
              f"x{item['count']} (allowed {item['allowance']}){note}")
        for seen in item["evidence"]:
            print(f"    seen: {seen}")
        if why:
            print(f"    why : {item['why']}")
            print(f"    keep: {item['keep_when']}")
        print(f"    fix : {item['fix']}")
    if not shown:
        print(f"No findings at tier '{tier}' or above.")
    if report["words"] < 40:
        print("Note: under 40 words, the density rules have little to measure. "
              "Read the result as a spot check.")


def main() -> None:
    """Parse arguments, run the audit, print the report and set the exit code."""
    parser = argparse.ArgumentParser(
        description="Gate a LinkedIn draft against the machine-tell catalogue (offline).",
        epilog="Exit codes: 0 gate passed, 1 gate failed, 2 bad input. "
               "The gate always counts the remove and reduce tiers; --tier only "
               "changes how much is displayed.")
    parser.add_argument("--input", required=True,
                        help="Plain-text draft to audit, or '-' to read stdin.")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                        help="Output format (default: text).")
    parser.add_argument("--tier", choices=TIERS, default="reduce",
                        help="Deepest tier to display (default: reduce). "
                             "'review' adds the author's-call notes.")
    parser.add_argument("--max-load", type=int, default=6,
                        help="Reduce-tier load above which the gate fails (default: 6).")
    parser.add_argument("--voice", metavar="VOICE_JSON",
                        help="Fingerprint JSON from voice_fingerprint.py; reduce-tier "
                             "rules it lists as protected are shown but not counted.")
    parser.add_argument("--why", action="store_true",
                        help="Print why each rule fired and when it is right to keep the text.")
    args = parser.parse_args()
    if args.max_load < 0:
        fail("--max-load must be zero or a positive whole number.")

    raw = read_text(args.input)
    protected = load_protected(args.voice) if args.voice else set()
    report = audit(raw, args.max_load, protected)
    output(report, args.format, args.tier, args.why,
           "stdin" if args.input == "-" else args.input)
    sys.exit(0 if report["passed"] else 1)


if __name__ == "__main__":
    main()
