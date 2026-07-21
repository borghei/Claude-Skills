#!/usr/bin/env python3
"""Lint a specification for ambiguity that blocks verifiable implementation.

Flags unquantified adjectives, passive requirements with no named actor, missing
modality, undefined pronouns, compound requirements, placeholders, and normative
statements with no acceptance criteria.

Usage:
  python3 spec_lint.py --spec assets/sample_spec.md
  python3 spec_lint.py --spec assets/sample_spec.md --format json
  python3 spec_lint.py --spec assets/sample_spec.md --max-findings 0
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List

UNQUANTIFIED = (
    "fast", "quick", "quickly", "slow", "scalable", "performant", "efficient",
    "user-friendly", "intuitive", "simple", "easy", "robust", "reliable", "secure",
    "flexible", "seamless", "modern", "clean", "appropriate", "reasonable",
    "sufficient", "adequate", "minimal", "optimal", "significant", "acceptable",
)
VAGUE_QUANTIFIERS = ("some", "several", "many", "few", "most", "various", "etc", "and so on")
PLACEHOLDERS = ("tbd", "tbc", "todo", "fixme", "???", "to be determined", "tba")
PASSIVE_RE = re.compile(
    r"\b(?:is|are|be|been|being|will be|shall be|must be|should be)\s+\w+(?:ed|en)\b", re.IGNORECASE)
ACTOR_RE = re.compile(r"\b(?:by|via)\s+(?:the\s+)?[a-z][\w-]*", re.IGNORECASE)
MODALITY_RE = re.compile(r"\b(must not|must|shall|should not|should|may|can)\b", re.IGNORECASE)
ACCEPTANCE_RE = re.compile(r"^\s*[-*]\s*(?:AC|acceptance|given|when|then)\b", re.IGNORECASE)
PRONOUN_RE = re.compile(r"^(?:it|they|this|that|these|those)\b", re.IGNORECASE)
COMPOUND_RE = re.compile(r"\band\/or\b|\b(?:and|as well as)\b.*\b(?:must|shall|should)\b", re.IGNORECASE)

SEVERITY_ORDER = {"error": 0, "warn": 1}


@dataclass
class Finding:
    """One ambiguity finding located at a specific line of the spec."""

    line: int
    rule: str
    severity: str
    message: str
    excerpt: str


def lint_line(number: int, text: str, has_criteria: bool) -> List[Finding]:
    """Apply every ambiguity rule to one normative line and return its findings."""
    out: List[Finding] = []
    lowered = text.lower()
    excerpt = text[:80]

    hits = [word for word in UNQUANTIFIED if re.search(rf"\b{re.escape(word)}\b", lowered)]
    if hits:
        out.append(Finding(number, "unquantified-adjective", "error",
                           f"unmeasurable term(s): {', '.join(hits)} — replace with a number and unit",
                           excerpt))
    vague = [word for word in VAGUE_QUANTIFIERS
             if re.search(rf"(?<!at )(?<!no )\b{re.escape(word)}\b", lowered)]
    if vague:
        out.append(Finding(number, "vague-quantifier", "warn",
                           f"vague quantifier(s): {', '.join(vague)} — state an exact count or range", excerpt))
    marks = [word for word in PLACEHOLDERS if word in lowered]
    if marks:
        out.append(Finding(number, "placeholder", "error",
                           f"unresolved placeholder: {', '.join(marks)} — a spec with TBDs cannot gate a merge",
                           excerpt))
    if not MODALITY_RE.search(text):
        out.append(Finding(number, "no-modality", "warn",
                           "no must/shall/should/may — statement is descriptive, not normative", excerpt))
    if PASSIVE_RE.search(text) and not ACTOR_RE.search(text):
        out.append(Finding(number, "passive-no-actor", "error",
                           "passive voice with no named actor — say which component performs the action",
                           excerpt))
    if PRONOUN_RE.match(text.strip()):
        out.append(Finding(number, "undefined-antecedent", "warn",
                           "opens with a pronoun — name the subject so the requirement stands alone", excerpt))
    if COMPOUND_RE.search(text):
        out.append(Finding(number, "compound-requirement", "warn",
                           "multiple obligations in one statement — split so each can be verified alone",
                           excerpt))
    if MODALITY_RE.search(text) and not has_criteria:
        out.append(Finding(number, "no-acceptance-criteria", "error",
                           "normative statement with no acceptance criteria — not verifiable", excerpt))
    return out


def lint_spec(path: str) -> Dict[str, Any]:
    """Lint every non-code line of a spec and return a structured findings report."""
    try:
        lines = Path(path).read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        raise SystemExit(f"error: spec file not found: {path}")
    except UnicodeDecodeError:
        raise SystemExit(f"error: spec file is not valid UTF-8 text: {path}")

    findings: List[Finding] = []
    in_code = False
    normative: List[int] = []

    for index, raw in enumerate(lines):
        stripped = raw.strip()
        if stripped.startswith("```"):
            in_code = not in_code
            continue
        if in_code or not stripped or stripped.startswith("#") or ACCEPTANCE_RE.match(raw):
            continue
        if not MODALITY_RE.search(stripped):
            continue
        normative.append(index)
        has_criteria = any(ACCEPTANCE_RE.match(lines[j]) for j in range(index + 1, min(index + 6, len(lines))))
        findings.extend(lint_line(index + 1, stripped.lstrip("-*0123456789. ").strip(), has_criteria))

    findings.sort(key=lambda f: (SEVERITY_ORDER[f.severity], f.line))
    by_rule: Dict[str, int] = {}
    for finding in findings:
        by_rule[finding.rule] = by_rule.get(finding.rule, 0) + 1
    errors = sum(1 for f in findings if f.severity == "error")
    clean = max(0, len(normative) - len({f.line for f in findings}))
    ratio = round(clean / len(normative), 2) if normative else 0.0
    return {
        "spec": path,
        "normative_statements": len(normative),
        "clean_statements": clean,
        "precision_ratio": ratio,
        "errors": errors,
        "warnings": len(findings) - errors,
        "by_rule": dict(sorted(by_rule.items(), key=lambda kv: -kv[1])),
        "findings": [asdict(f) for f in findings],
    }


def output(report: Dict[str, Any], fmt: str) -> None:
    """Print the ambiguity report as text or JSON."""
    if fmt == "json":
        print(json.dumps(report, indent=2))
        return
    print(f"{report['spec']}: {report['normative_statements']} normative statements, "
          f"precision ratio {report['precision_ratio']:.2f}")
    print(f"  {report['errors']} errors, {report['warnings']} warnings\n")
    for item in report["findings"]:
        print(f"L{item['line']:<5} [{item['severity']:5}] {item['rule']}")
        print(f"        {item['message']}")
        print(f"        > {item['excerpt']}")
    if report["by_rule"]:
        print("\nMost frequent rules:")
        for rule, count in list(report["by_rule"].items())[:5]:
            print(f"  {count:3}  {rule}")


def main() -> None:
    """Parse arguments, lint the spec, and exit non-zero when findings exceed the budget."""
    parser = argparse.ArgumentParser(description="Lint a specification for ambiguity.")
    parser.add_argument("--spec", required=True, help="path to the markdown specification")
    parser.add_argument("--max-findings", type=int, default=0,
                        help="error findings tolerated before exiting 1 (default: 0)")
    parser.add_argument("--min-precision", type=float, default=0.0,
                        help="minimum clean-statement ratio required to pass (default: 0.0)")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="output format (default: text)")
    args = parser.parse_args()
    try:
        report = lint_spec(args.spec)
        output(report, args.format)
    except SystemExit:
        raise
    except OSError as exc:
        print(f"error: could not read spec: {exc}", file=sys.stderr)
        sys.exit(1)
    failed = report["errors"] > args.max_findings or report["precision_ratio"] < args.min_precision
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
