#!/usr/bin/env python3
"""
Legal Quality Scorer

Scores legal document quality across 6 verification categories: Factual
Accuracy, Legal Authority Citations, Arithmetic Validation, Source
Verification, Speculation Detection, and Disclaimer Adequacy. Calculates
composite quality score and distribution readiness.

Usage:
    python legal_quality_scorer.py --input document.txt
    python legal_quality_scorer.py --input document.txt --json
    python legal_quality_scorer.py --input document.txt --verbose
    python legal_quality_scorer.py --input document.txt --output assessment.json
"""

import argparse
import json
import re
import sys
from typing import Any, Dict, List, Tuple


# Scoring weights for each category
CATEGORY_WEIGHTS = {
    "factual_accuracy": 0.25,
    "legal_authority": 0.25,
    "arithmetic": 0.15,
    "source_verification": 0.15,
    "speculation_control": 0.10,
    "disclaimer_adequacy": 0.10,
}

QUALITY_RATINGS = {
    5: {"label": "Distribution Ready", "description": "Safe to distribute. Zero CRITICAL/HIGH issues."},
    4: {"label": "Minor Revisions", "description": "Safe after small fixes. Zero CRITICAL, 1-2 HIGH."},
    3: {"label": "Moderate Revisions", "description": "Needs work before distribution. 3+ HIGH issues."},
    2: {"label": "Major Revisions", "description": "Not safe to distribute. 1+ CRITICAL issues."},
    1: {"label": "Not Distribution Ready", "description": "Requires complete rework. Multiple CRITICAL."},
}

# Pattern sets for scoring
CITATION_PATTERN = re.compile(
    r"(?:Article|Art\.?|Section|Sec\.?|§)\s*\d+(?:\(\d+\))?(?:\([a-z]\))?",
    re.IGNORECASE,
)

SPECIFIC_CITATION_PATTERN = re.compile(
    r"(?:Regulation|Directive)\s+\(?(?:EU|EC)\)?\s*(?:No\.?\s*)?\d{4}/\d+|"
    r"\d+\s+(?:C\.?F\.?R\.?|U\.?S\.?C\.?)\s+(?:§\s*)?\d+",
    re.IGNORECASE,
)

DATE_PATTERN = re.compile(
    r"\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}[/-]\d{1,2}[/-]\d{1,2}|"
    r"(?:January|February|March|April|May|June|July|August|September|October|November|December)"
    r"\s+\d{1,2},?\s+\d{4})\b",
    re.IGNORECASE,
)

NUMBER_PATTERN = re.compile(
    r"(?:EUR|USD|GBP)?\s*[€$£]?\s*\d[\d,]*(?:\.\d+)?\s*"
    r"(?:million|billion|thousand|%|percent|days?|months?|years?|hours?)?\b",
    re.IGNORECASE,
)

SPECULATION_PATTERNS = [
    re.compile(r"\b(?:will\s+likely|is\s+likely\s+to|probably|may\s+well)\b", re.I),
    re.compile(r"\b(?:it\s+is\s+(?:expected|anticipated|believed))\b", re.I),
    re.compile(r"\b(?:should\s+be\s+(?:interpreted|understood))\b", re.I),
    re.compile(r"\b(?:in\s+(?:our|my)\s+(?:view|opinion|assessment))\b", re.I),
    re.compile(r"\b(?:courts?\s+(?:will|would|might|could)\s+(?:likely|probably))\b", re.I),
]

CERTAINTY_PATTERNS = [
    re.compile(r"\b(?:certainly|definitely|undoubtedly|clearly|obviously|always|never)\b", re.I),
    re.compile(r"\b(?:there\s+is\s+no\s+doubt)\b", re.I),
    re.compile(r"\b(?:it\s+is\s+(?:certain|clear|obvious|evident))\b", re.I),
]

HEDGING_PATTERNS = [
    re.compile(r"\b(?:may|might|could|potentially|possibly|arguably)\b", re.I),
    re.compile(r"\b(?:it\s+(?:appears|seems)\s+(?:that|to))\b", re.I),
    re.compile(r"\b(?:subject\s+to\s+(?:interpretation|debate))\b", re.I),
]

DISCLAIMER_CHECKS = {
    "not_legal_advice": re.compile(
        r"(?:not\s+(?:constitute|intended\s+as)\s+legal\s+advice|"
        r"for\s+informational\s+purposes\s+only)", re.I
    ),
    "jurisdiction_limitation": re.compile(
        r"(?:jurisdiction|applicable\s+(?:in|to)|"
        r"may\s+(?:vary|differ)\s+(?:by|across)\s+jurisdiction)", re.I
    ),
    "date_of_preparation": re.compile(
        r"(?:as\s+of|prepared\s+(?:on|as\s+of)|current\s+as\s+of|"
        r"last\s+(?:updated|reviewed))", re.I
    ),
    "professional_consultation": re.compile(
        r"(?:consult\s+(?:a\s+)?(?:qualified\s+)?(?:legal\s+)?(?:counsel|lawyer|attorney|professional)|"
        r"seek\s+(?:legal\s+)?(?:advice|counsel))", re.I
    ),
    "ai_generated_disclosure": re.compile(
        r"(?:ai[- ]generated|generated\s+(?:by|using)\s+ai|"
        r"artificial\s+intelligence|assisted\s+by\s+ai)", re.I
    ),
    "accuracy_limitations": re.compile(
        r"(?:accuracy\s+(?:not\s+)?guaranteed|verify\s+(?:independently|against)|"
        r"no\s+(?:warranty|guarantee))", re.I
    ),
}

# High-subsection article pattern (hallucination indicator)
HIGH_SUBSECTION = re.compile(r"(?:Article|Art\.?)\s+\d+\(([7-9]|\d{2,})\)", re.I)

# Guidance-as-law pattern
GUIDANCE_AS_LAW = re.compile(
    r"(?:(?:ENISA|EDPB|CNIL|ICO|FTC|NIST)\s+(?:requires?|mandates?|obligates?))|"
    r"(?:guidance|recommendation|guideline|best\s+practice)\s+(?:requires?|mandates?|must)",
    re.I,
)


def extract_sentences(text: str) -> List[str]:
    """Split into sentences."""
    abbrevs = ["Art.", "Sec.", "No.", "para.", "e.g.", "i.e.", "et al.", "cf.", "v."]
    protected = text
    for abbr in abbrevs:
        protected = protected.replace(abbr, abbr.replace(".", "<DOT>"))
    sentences = re.split(r'(?<=[.!?])\s+', protected)
    return [s.replace("<DOT>", ".").strip() for s in sentences if s.strip()]


def score_factual_accuracy(text: str, sentences: List[str]) -> Tuple[int, List[Dict]]:
    """Score factual accuracy (dates, numbers, entities)."""
    findings = []
    deductions = 0

    # Check for high-subsection articles (hallucination pattern)
    for m in HIGH_SUBSECTION.finditer(text):
        findings.append({
            "severity": "HIGH",
            "category": "factual_accuracy",
            "detail": f"Unusually high subsection number: {m.group()}",
            "action": "Verify article subsection exists in source statute",
        })
        deductions += 1

    # Check for guidance stated as binding law
    for m in GUIDANCE_AS_LAW.finditer(text):
        findings.append({
            "severity": "HIGH",
            "category": "factual_accuracy",
            "detail": f"Non-binding guidance possibly stated as requirement: {m.group()}",
            "action": "Verify if cited source is binding legislation vs guidance",
        })
        deductions += 1

    # Check for overcertainty about predictions
    for sent in sentences:
        for p in CERTAINTY_PATTERNS:
            if p.search(sent):
                findings.append({
                    "severity": "MODERATE",
                    "category": "factual_accuracy",
                    "detail": f"Overcertain language: {sent[:100]}",
                    "action": "Verify claim or soften language",
                })
                deductions += 0.5
                break

    score = max(1, 5 - deductions)
    return min(5, round(score)), findings


def score_legal_authority(text: str, sentences: List[str]) -> Tuple[int, List[Dict]]:
    """Score citation quality and presence."""
    findings = []
    citations = CITATION_PATTERN.findall(text)
    specific_citations = SPECIFIC_CITATION_PATTERN.findall(text)
    word_count = len(text.split())

    # Citation density
    citation_density = len(citations) / max(word_count / 500, 1)

    if len(citations) == 0 and word_count > 200:
        findings.append({
            "severity": "CRITICAL",
            "category": "legal_authority",
            "detail": "No legal citations found in document",
            "action": "Add specific statutory references for all legal claims",
        })
        return 1, findings

    if citation_density < 0.5 and word_count > 500:
        findings.append({
            "severity": "HIGH",
            "category": "legal_authority",
            "detail": f"Low citation density: {len(citations)} citations in {word_count} words",
            "action": "Add more specific citations to support legal claims",
        })

    if len(specific_citations) == 0 and word_count > 300:
        findings.append({
            "severity": "MODERATE",
            "category": "legal_authority",
            "detail": "No full statute references (e.g., Regulation (EU) 2024/1689)",
            "action": "Include complete statute references for traceability",
        })

    deductions = 0
    for f in findings:
        if f["severity"] == "CRITICAL":
            deductions += 3
        elif f["severity"] == "HIGH":
            deductions += 1.5
        elif f["severity"] == "MODERATE":
            deductions += 0.5

    return max(1, min(5, round(5 - deductions))), findings


def score_arithmetic(text: str, sentences: List[str]) -> Tuple[int, List[Dict]]:
    """Score arithmetic and numerical content."""
    findings = []
    numbers = NUMBER_PATTERN.findall(text)
    dates = DATE_PATTERN.findall(text)

    # Flag any timeline calculations for verification
    timeline_pattern = re.compile(
        r"(\d+)\s+(?:days?|months?|years?)\s+(?:from|after|before|until)\s+",
        re.IGNORECASE,
    )
    for m in timeline_pattern.finditer(text):
        findings.append({
            "severity": "MODERATE",
            "category": "arithmetic",
            "detail": f"Timeline calculation requires verification: {m.group()[:80]}",
            "action": "Independently calculate and verify",
        })

    # Flag percentage calculations
    pct_pattern = re.compile(r"(\d+(?:\.\d+)?)\s*%\s*of\s+", re.I)
    for m in pct_pattern.finditer(text):
        findings.append({
            "severity": "LOW",
            "category": "arithmetic",
            "detail": f"Percentage calculation: {m.group()[:80]}",
            "action": "Verify arithmetic",
        })

    # Score based on findings
    high_count = sum(1 for f in findings if f["severity"] in ("CRITICAL", "HIGH"))
    mod_count = sum(1 for f in findings if f["severity"] == "MODERATE")

    if high_count > 0:
        score = max(1, 3 - high_count)
    elif mod_count > 3:
        score = 3
    elif mod_count > 0:
        score = 4
    else:
        score = 5

    return score, findings


def score_source_verification(text: str, sentences: List[str]) -> Tuple[int, List[Dict]]:
    """Score source verifiability."""
    findings = []

    # Check for unsourced definitive claims
    definitive_claims = re.compile(
        r"(?:the\s+law\s+(?:requires|mandates|prohibits))|"
        r"(?:(?:companies|organizations|entities)\s+(?:must|shall|are\s+required))",
        re.I,
    )
    citations_present = len(CITATION_PATTERN.findall(text)) > 0

    claim_count = 0
    for sent in sentences:
        if definitive_claims.search(sent) and not CITATION_PATTERN.search(sent):
            claim_count += 1
            if claim_count <= 5:  # Limit reported findings
                findings.append({
                    "severity": "MODERATE",
                    "category": "source_verification",
                    "detail": f"Legal claim without citation: {sent[:100]}",
                    "action": "Add specific statutory reference",
                })

    if claim_count > 5:
        findings.append({
            "severity": "HIGH",
            "category": "source_verification",
            "detail": f"{claim_count} legal claims without specific citations",
            "action": "Systematically add citations for all legal claims",
        })

    deductions = claim_count * 0.3
    return max(1, min(5, round(5 - deductions))), findings


def score_speculation(text: str, sentences: List[str]) -> Tuple[int, List[Dict]]:
    """Score speculation control -- proper hedging vs overcertainty."""
    findings = []
    speculation_count = 0
    hedging_count = 0

    for sent in sentences:
        for p in SPECULATION_PATTERNS:
            if p.search(sent):
                speculation_count += 1
                break
        for p in HEDGING_PATTERNS:
            if p.search(sent):
                hedging_count += 1
                break

    total_sentences = len(sentences)
    speculation_ratio = speculation_count / max(total_sentences, 1)

    if speculation_ratio > 0.3:
        findings.append({
            "severity": "HIGH",
            "category": "speculation_control",
            "detail": f"High speculation ratio: {speculation_ratio:.0%} of sentences contain speculative language",
            "action": "Replace speculation with verified facts or clearly mark as opinion",
        })
    elif speculation_ratio > 0.15:
        findings.append({
            "severity": "MODERATE",
            "category": "speculation_control",
            "detail": f"Moderate speculation: {speculation_count} speculative statements",
            "action": "Verify speculative claims or add qualifiers",
        })

    # Unqualified predictions are worse than hedged ones
    for sent in sentences:
        for p in CERTAINTY_PATTERNS:
            if p.search(sent):
                for sp in SPECULATION_PATTERNS:
                    if sp.search(sent):
                        findings.append({
                            "severity": "HIGH",
                            "category": "speculation_control",
                            "detail": f"Prediction stated with false certainty: {sent[:100]}",
                            "action": "Add uncertainty qualifier or remove certainty language",
                        })
                        break

    high = sum(1 for f in findings if f["severity"] in ("CRITICAL", "HIGH"))
    if high >= 2:
        score = 2
    elif high == 1:
        score = 3
    elif speculation_ratio > 0.15:
        score = 4
    else:
        score = 5

    return score, findings


def score_disclaimers(text: str) -> Tuple[int, List[Dict]]:
    """Score disclaimer adequacy."""
    findings = []
    present = 0
    missing = []

    for name, pattern in DISCLAIMER_CHECKS.items():
        if pattern.search(text):
            present += 1
        else:
            missing.append(name)

    for m in missing:
        label = m.replace("_", " ").title()
        severity = "HIGH" if m in ("not_legal_advice", "professional_consultation") else "MODERATE"
        findings.append({
            "severity": severity,
            "category": "disclaimer_adequacy",
            "detail": f"Missing disclaimer: {label}",
            "action": f"Add {label} disclaimer",
        })

    if present >= 5:
        score = 5
    elif present >= 4:
        score = 4
    elif present >= 3:
        score = 3
    elif present >= 2:
        score = 2
    else:
        score = 1

    return score, findings


def calculate_composite_score(category_scores: Dict[str, int]) -> Tuple[int, float]:
    """Calculate weighted composite score."""
    weighted = sum(
        category_scores[cat] * weight
        for cat, weight in CATEGORY_WEIGHTS.items()
    )
    rounded = max(1, min(5, round(weighted)))
    return rounded, round(weighted, 2)


def format_human_report(result: Dict[str, Any], verbose: bool = False) -> str:
    """Format as human-readable report."""
    lines = []
    lines.append("=" * 72)
    lines.append("LEGAL QUALITY ASSESSMENT")
    lines.append("=" * 72)

    cs = result["composite_score"]
    rating = QUALITY_RATINGS[cs]
    lines.append(f"\nQuality Score:  {cs}/5 -- {rating['label']}")
    lines.append(f"Weighted Score: {result['weighted_score']}/5.00")
    lines.append(f"Assessment:     {rating['description']}")
    lines.append(f"Distribution:   {'APPROVED' if cs >= 4 else 'NOT APPROVED'}")

    lines.append("\n--- CATEGORY SCORES ---")
    for cat, score in result["category_scores"].items():
        label = cat.replace("_", " ").title()
        weight = CATEGORY_WEIGHTS[cat]
        lines.append(f"  {label:30s} {score}/5  (weight: {weight:.0%})")

    sev = result["severity_summary"]
    lines.append(f"\n--- FINDINGS ---")
    lines.append(f"  CRITICAL: {sev['CRITICAL']}  HIGH: {sev['HIGH']}  "
                 f"MODERATE: {sev['MODERATE']}  LOW: {sev['LOW']}")

    if verbose or cs < 4:
        # Show all findings for low scores, or when verbose
        lines.append("\n--- DETAILED FINDINGS ---")
        for f in result["findings"]:
            lines.append(f"\n  [{f['severity']}] ({f['category']})")
            lines.append(f"    {f['detail']}")
            lines.append(f"    Action: {f['action']}")

    lines.append("\n--- RECOMMENDATIONS ---")
    for rec in result["recommendations"]:
        lines.append(f"  - {rec}")

    lines.append("\n" + "=" * 72)
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Score legal document quality across 6 verification categories."
    )
    parser.add_argument("--input", "-i", type=str, help="Path to legal document")
    parser.add_argument("--text", "-t", type=str, help="Inline legal text")
    parser.add_argument("--output", "-o", type=str, help="Path to save output (JSON)")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed findings")
    args = parser.parse_args()

    if not args.input and not args.text:
        parser.print_help()
        sys.exit(1)

    try:
        if args.input:
            with open(args.input, "r", encoding="utf-8") as f:
                text = f.read()
        else:
            text = args.text

        if not text or not text.strip():
            print("Error: Empty input text.", file=sys.stderr)
            sys.exit(1)

        sentences = extract_sentences(text)
        all_findings: List[Dict] = []

        fa_score, fa_findings = score_factual_accuracy(text, sentences)
        la_score, la_findings = score_legal_authority(text, sentences)
        ar_score, ar_findings = score_arithmetic(text, sentences)
        sv_score, sv_findings = score_source_verification(text, sentences)
        sp_score, sp_findings = score_speculation(text, sentences)
        di_score, di_findings = score_disclaimers(text)

        all_findings.extend(fa_findings)
        all_findings.extend(la_findings)
        all_findings.extend(ar_findings)
        all_findings.extend(sv_findings)
        all_findings.extend(sp_findings)
        all_findings.extend(di_findings)

        # Sort by severity
        severity_order = {"CRITICAL": 0, "HIGH": 1, "MODERATE": 2, "LOW": 3}
        all_findings.sort(key=lambda x: severity_order.get(x["severity"], 4))

        category_scores = {
            "factual_accuracy": fa_score,
            "legal_authority": la_score,
            "arithmetic": ar_score,
            "source_verification": sv_score,
            "speculation_control": sp_score,
            "disclaimer_adequacy": di_score,
        }

        composite, weighted = calculate_composite_score(category_scores)

        # Override: CRITICAL findings force score down
        critical_count = sum(1 for f in all_findings if f["severity"] == "CRITICAL")
        if critical_count > 0 and composite > 2:
            composite = 2

        severity_summary = {"CRITICAL": 0, "HIGH": 0, "MODERATE": 0, "LOW": 0}
        for f in all_findings:
            severity_summary[f["severity"]] = severity_summary.get(f["severity"], 0) + 1

        # Generate recommendations
        recommendations = []
        if critical_count > 0:
            recommendations.append("Fix all CRITICAL issues before any distribution")
        if severity_summary["HIGH"] > 0:
            recommendations.append(f"Address {severity_summary['HIGH']} HIGH-severity findings")
        if la_score < 4:
            recommendations.append("Improve citation coverage and specificity")
        if di_score < 4:
            recommendations.append("Add missing disclaimers")
        if sp_score < 4:
            recommendations.append("Reduce speculation or add proper qualifiers")
        if composite >= 4:
            recommendations.append("Document is suitable for distribution after final review")

        result = {
            "composite_score": composite,
            "weighted_score": weighted,
            "rating": QUALITY_RATINGS[composite]["label"],
            "distribution_ready": composite >= 4 and critical_count == 0,
            "category_scores": category_scores,
            "severity_summary": severity_summary,
            "findings": all_findings,
            "recommendations": recommendations,
            "statistics": {
                "word_count": len(text.split()),
                "sentence_count": len(sentences),
                "total_findings": len(all_findings),
            },
        }

        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"Assessment saved to {args.output}")
        elif args.json:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(format_human_report(result, verbose=args.verbose))

    except FileNotFoundError:
        print(f"Error: File not found: {args.input}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
