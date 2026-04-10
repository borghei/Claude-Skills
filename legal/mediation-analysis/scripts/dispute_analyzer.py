#!/usr/bin/env python3
"""
Dispute Analyzer

Analyzes dispute description text and extracts parties, claims, key issues,
timeline of events, and evidence references. Maps each party's positions
and interests. Identifies overlapping interests and potential ZOPA.

Usage:
    python dispute_analyzer.py --input dispute.txt
    python dispute_analyzer.py --text "Party A claims breach of contract..."
    python dispute_analyzer.py --input dispute.txt --json
    python dispute_analyzer.py --input dispute.txt --output analysis.json
"""

import argparse
import json
import re
import sys
from typing import Any, Dict, List, Optional, Tuple


# Entity/party extraction patterns
PARTY_INDICATORS = [
    r"(?:plaintiff|claimant|petitioner|applicant|complainant)",
    r"(?:defendant|respondent|opposing\s+party)",
    r"(?:party\s+[a-z])",
    r"(?:the\s+(?:company|employer|employee|tenant|landlord|buyer|seller|contractor|client|vendor|supplier|customer|insured|insurer|licensor|licensee))",
]

# Claim type patterns
CLAIM_PATTERNS: Dict[str, List[str]] = {
    "breach_of_contract": [
        r"\bbreach\s+of\s+contract\b", r"\bfailed\s+to\s+perform\b",
        r"\bnon-?performance\b", r"\bcontractual\s+(?:breach|violation)\b",
    ],
    "negligence": [
        r"\bnegligen(?:ce|t)\b", r"\bduty\s+of\s+care\b",
        r"\bfailed\s+to\s+exercise\b", r"\breasonable\s+care\b",
    ],
    "employment": [
        r"\bwrongful\s+(?:termination|dismissal)\b", r"\bdiscrimination\b",
        r"\bharassment\b", r"\bunfair\s+(?:dismissal|treatment)\b",
        r"\bemployment\s+(?:dispute|claim)\b",
    ],
    "intellectual_property": [
        r"\binfringement\b", r"\btrademark\b", r"\bcopyright\b",
        r"\bpatent\b", r"\btrade\s+secret\b", r"\bmisappropriation\b",
    ],
    "property": [
        r"\bland(?:lord|lady)\b", r"\btenant\b", r"\blease\b",
        r"\bproperty\s+(?:damage|dispute)\b", r"\beviction\b",
    ],
    "debt_collection": [
        r"\bowed\b", r"\bunpaid\b", r"\bdebt\b", r"\binvoice\b",
        r"\bpayment\s+(?:due|owed|outstanding)\b",
    ],
    "personal_injury": [
        r"\bpersonal\s+injury\b", r"\bbodily\s+harm\b",
        r"\bmedical\s+(?:expenses|bills)\b", r"\binjured\b",
    ],
    "professional_liability": [
        r"\bmalpractice\b", r"\bprofessional\s+(?:negligence|liability)\b",
        r"\bfiduciary\b", r"\bstandard\s+of\s+care\b",
    ],
}

# Monetary amount patterns
MONEY_PATTERN = re.compile(
    r"(?:(?:USD|EUR|GBP|CAD|AUD)\s*)?[\$\u20ac\u00a3]?\s*\d[\d,]*(?:\.\d{1,2})?\s*"
    r"(?:million|billion|thousand|[MBKmk])?(?:\s*(?:USD|EUR|GBP|CAD|AUD))?",
    re.IGNORECASE,
)

# Date patterns
DATE_PATTERN = re.compile(
    r"\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}[/-]\d{1,2}[/-]\d{1,2}|"
    r"(?:January|February|March|April|May|June|July|August|September|October|November|December)"
    r"\s+\d{1,2},?\s+\d{4}|\d{1,2}\s+"
    r"(?:January|February|March|April|May|June|July|August|September|October|November|December)"
    r"\s+\d{4})",
    re.IGNORECASE,
)

# Evidence reference patterns
EVIDENCE_PATTERNS = [
    (r"\b(?:exhibit|evidence)\s+[A-Z\d]+\b", "formal_exhibit"),
    (r"\b(?:email|correspondence|letter)\s+(?:dated|from|of)\b", "correspondence"),
    (r"\bcontract\s+(?:dated|signed|executed)\b", "contract"),
    (r"\binvoice\s+(?:#|no\.?|number)\s*\w+", "invoice"),
    (r"\bwitness(?:es)?\b", "witness"),
    (r"\bexpert\s+(?:report|opinion|testimony)\b", "expert"),
    (r"\bphoto(?:graph)?s?\b", "photograph"),
    (r"\brecording\b", "recording"),
    (r"\bbank\s+(?:statement|record)\b", "financial_record"),
    (r"\bmedical\s+record\b", "medical_record"),
]

# Interest category patterns
INTEREST_PATTERNS: Dict[str, List[str]] = {
    "legal": [
        r"\bright\b", r"\bentitle\b", r"\bliabilit", r"\bobligat",
        r"\bprecedent\b", r"\blaw\b", r"\blegal\b",
    ],
    "commercial": [
        r"\bbusiness\b", r"\brevenue\b", r"\bprofit\b", r"\bcost\b",
        r"\bmarket\b", r"\breputation\b", r"\bfinancial\b",
    ],
    "relational": [
        r"\brelationship\b", r"\bpartnership\b", r"\bongoing\b",
        r"\bfuture\s+(?:business|dealings)\b", r"\btrust\b",
    ],
    "emotional": [
        r"\bfairness\b", r"\brespect\b", r"\backnowledg", r"\bapolog",
        r"\bfrustr", r"\banger\b", r"\bdisappoint\b", r"\bprincipl",
    ],
    "procedural": [
        r"\bspeed\b", r"\bquick\b", r"\bprivac(?:y|ate)\b",
        r"\bconfidential\b", r"\bcontrol\b", r"\bvoice\b",
    ],
}


def extract_sentences(text: str) -> List[str]:
    """Split into sentences."""
    abbrevs = ["Mr.", "Mrs.", "Ms.", "Dr.", "Jr.", "Sr.", "No.", "Art.", "Sec.", "v."]
    protected = text
    for abbr in abbrevs:
        protected = protected.replace(abbr, abbr.replace(".", "<DOT>"))
    sentences = re.split(r'(?<=[.!?])\s+', protected)
    return [s.replace("<DOT>", ".").strip() for s in sentences if s.strip()]


def extract_parties(text: str) -> List[Dict[str, Any]]:
    """Extract party references from text."""
    parties = []
    seen_labels = set()
    text_lower = text.lower()

    # Named parties: "X v Y" or "X vs Y" or "X versus Y"
    vs_match = re.search(r'([A-Z][\w\s&,.]+?)\s+(?:v\.?|vs\.?|versus)\s+([A-Z][\w\s&,.]+?)(?:\.|,|\s{2})', text)
    if vs_match:
        for i, group in enumerate([vs_match.group(1).strip(), vs_match.group(2).strip()], 1):
            label = f"Party {i}"
            parties.append({"name": group, "label": label, "role": "claimant" if i == 1 else "respondent"})
            seen_labels.add(label)

    # Role-based extraction
    for pat in PARTY_INDICATORS:
        for m in re.finditer(pat, text_lower):
            matched = m.group().strip()
            if matched not in seen_labels:
                seen_labels.add(matched)
                role = "claimant" if any(w in matched for w in ["plaintiff", "claimant", "petitioner", "applicant"]) else "respondent"
                parties.append({"name": matched.title(), "label": matched.title(), "role": role})

    if not parties:
        parties = [
            {"name": "Party A", "label": "Party A", "role": "claimant"},
            {"name": "Party B", "label": "Party B", "role": "respondent"},
        ]
    return parties


def extract_claims(text: str) -> List[Dict[str, Any]]:
    """Extract and classify claims from text."""
    claims = []
    text_lower = text.lower()
    sentences = extract_sentences(text)

    for claim_type, patterns in CLAIM_PATTERNS.items():
        for pat in patterns:
            for m in re.finditer(pat, text_lower):
                # Find the sentence containing this match
                for sent in sentences:
                    if m.group() in sent.lower():
                        claims.append({
                            "type": claim_type,
                            "matched_phrase": m.group(),
                            "context": sent.strip()[:200],
                        })
                        break
                break  # One match per pattern group is enough

    # Deduplicate by type
    seen_types = set()
    unique = []
    for c in claims:
        if c["type"] not in seen_types:
            seen_types.add(c["type"])
            unique.append(c)
    return unique


def extract_monetary_amounts(text: str) -> List[Dict[str, str]]:
    """Extract monetary amounts from text."""
    amounts = []
    sentences = extract_sentences(text)
    for sent in sentences:
        for m in MONEY_PATTERN.finditer(sent):
            val = m.group().strip()
            if val and any(c.isdigit() for c in val) and len(val) > 1:
                amounts.append({
                    "amount": val,
                    "context": sent.strip()[:200],
                })
    return amounts


def extract_dates(text: str) -> List[Dict[str, str]]:
    """Extract dates and build timeline."""
    dates = []
    sentences = extract_sentences(text)
    for sent in sentences:
        for m in DATE_PATTERN.finditer(sent):
            dates.append({
                "date": m.group().strip(),
                "context": sent.strip()[:200],
            })
    return dates


def extract_evidence(text: str) -> List[Dict[str, str]]:
    """Extract evidence references."""
    evidence = []
    sentences = extract_sentences(text)
    for sent in sentences:
        for pat, etype in EVIDENCE_PATTERNS:
            for m in re.finditer(pat, sent, re.IGNORECASE):
                evidence.append({
                    "type": etype,
                    "reference": m.group().strip(),
                    "context": sent.strip()[:200],
                })
    return evidence


def analyze_interests(text: str) -> Dict[str, List[str]]:
    """Identify interest categories present in the text."""
    text_lower = text.lower()
    found: Dict[str, List[str]] = {}
    for category, patterns in INTEREST_PATTERNS.items():
        matches = []
        for pat in patterns:
            for m in re.finditer(pat, text_lower):
                matches.append(m.group())
        if matches:
            found[category] = list(set(matches))
    return found


def assess_complexity(
    parties: List, claims: List, amounts: List, dates: List, evidence: List, text: str
) -> Dict[str, Any]:
    """Assess dispute complexity."""
    word_count = len(text.split())
    factors = {
        "party_count": len(parties),
        "claim_count": len(claims),
        "monetary_references": len(amounts),
        "date_references": len(dates),
        "evidence_references": len(evidence),
        "text_length_words": word_count,
    }
    score = 0
    score += min(len(parties), 4)
    score += min(len(claims) * 2, 8)
    score += min(len(amounts), 3)
    score += min(len(evidence), 3)
    score += 2 if word_count > 2000 else (1 if word_count > 500 else 0)

    if score >= 12:
        level = "high"
    elif score >= 6:
        level = "moderate"
    else:
        level = "low"

    factors["complexity_score"] = score
    factors["complexity_level"] = level
    return factors


def format_human_report(analysis: Dict[str, Any]) -> str:
    """Format analysis as human-readable report."""
    lines = []
    lines.append("=" * 72)
    lines.append("DISPUTE ANALYSIS REPORT")
    lines.append("=" * 72)

    lines.append(f"\nComplexity: {analysis['complexity']['complexity_level'].upper()} "
                 f"(score: {analysis['complexity']['complexity_score']})")

    lines.append("\n--- PARTIES ---")
    for p in analysis["parties"]:
        lines.append(f"  {p['name']} ({p['role']})")

    lines.append(f"\n--- CLAIMS ({len(analysis['claims'])}) ---")
    for c in analysis["claims"]:
        lines.append(f"  Type: {c['type'].replace('_', ' ').title()}")
        lines.append(f"    {c['context'][:150]}")

    if analysis["monetary_amounts"]:
        lines.append(f"\n--- MONETARY AMOUNTS ({len(analysis['monetary_amounts'])}) ---")
        for a in analysis["monetary_amounts"]:
            lines.append(f"  {a['amount']}")
            lines.append(f"    {a['context'][:150]}")

    if analysis["timeline"]:
        lines.append(f"\n--- TIMELINE ({len(analysis['timeline'])}) ---")
        for d in analysis["timeline"]:
            lines.append(f"  {d['date']}: {d['context'][:120]}")

    if analysis["evidence"]:
        lines.append(f"\n--- EVIDENCE REFERENCES ({len(analysis['evidence'])}) ---")
        for e in analysis["evidence"]:
            lines.append(f"  [{e['type']}] {e['reference']}")

    if analysis["interests"]:
        lines.append("\n--- INTEREST CATEGORIES ---")
        for cat, keywords in analysis["interests"].items():
            lines.append(f"  {cat.title()}: {', '.join(keywords)}")

    lines.append("\n--- ZOPA INDICATORS ---")
    if analysis["interests"].get("relational"):
        lines.append("  + Relational interests present -- parties may value ongoing relationship")
    if analysis["interests"].get("procedural"):
        lines.append("  + Procedural interests present -- process matters to parties")
    if analysis["interests"].get("emotional"):
        lines.append("  + Emotional interests present -- consider non-monetary resolution elements")
    shared = set()
    for cat in analysis["interests"]:
        if cat in ("relational", "procedural"):
            shared.add(cat)
    if shared:
        lines.append(f"  Potentially shared interests: {', '.join(shared)}")

    lines.append("\n" + "=" * 72)
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Analyze dispute description and extract structured dispute data."
    )
    parser.add_argument("--input", "-i", type=str, help="Path to dispute description file")
    parser.add_argument("--text", "-t", type=str, help="Inline dispute text")
    parser.add_argument("--output", "-o", type=str, help="Path to save output (JSON)")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
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

        parties = extract_parties(text)
        claims = extract_claims(text)
        amounts = extract_monetary_amounts(text)
        dates = extract_dates(text)
        evidence = extract_evidence(text)
        interests = analyze_interests(text)
        complexity = assess_complexity(parties, claims, amounts, dates, evidence, text)

        analysis = {
            "parties": parties,
            "claims": claims,
            "monetary_amounts": amounts,
            "timeline": dates,
            "evidence": evidence,
            "interests": interests,
            "complexity": complexity,
        }

        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                json.dump(analysis, f, indent=2, ensure_ascii=False)
            print(f"Analysis saved to {args.output}")
        elif args.json:
            print(json.dumps(analysis, indent=2, ensure_ascii=False))
        else:
            print(format_human_report(analysis))

    except FileNotFoundError:
        print(f"Error: File not found: {args.input}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
