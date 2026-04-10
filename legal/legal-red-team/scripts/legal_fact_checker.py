#!/usr/bin/env python3
"""
Legal Fact Checker

Scans legal text for verifiable claims: article/section references, dates,
numerical values, monetary amounts, entity names. Cross-references article
numbering against known statute structures. Flags potential hallucination
patterns. Outputs a verification report with confidence levels.

Usage:
    python legal_fact_checker.py --input document.txt
    python legal_fact_checker.py --text "Under GDPR Article 83(5), fines..."
    python legal_fact_checker.py --input document.txt --json
    python legal_fact_checker.py --input document.txt --output report.json
"""

import argparse
import json
import re
import sys
from typing import Any, Dict, List, Optional, Tuple


# Known statute structures for cross-referencing
KNOWN_STATUTES: Dict[str, Dict[str, Any]] = {
    "GDPR": {
        "full_name": "Regulation (EU) 2016/679",
        "max_article": 99,
        "key_articles": {
            5: "Principles", 6: "Lawful basis", 7: "Consent", 9: "Special categories",
            12: "Transparency", 13: "Info at collection", 14: "Info not from data subject",
            15: "Right of access", 16: "Rectification", 17: "Erasure",
            20: "Portability", 21: "Object", 22: "Automated decisions",
            25: "Data protection by design", 28: "Processor", 30: "Records",
            32: "Security", 33: "Breach notification authority", 34: "Breach notification data subject",
            35: "DPIA", 37: "DPO designation", 44: "Transfer principles",
            83: "Fines", 99: "Entry into force",
        },
        "patterns": [r"\bGDPR\b", r"\bRegulation\s*\(?EU\)?\s*2016/679\b"],
    },
    "EU_AI_ACT": {
        "full_name": "Regulation (EU) 2024/1689",
        "max_article": 113,
        "key_articles": {
            3: "Definitions", 5: "Prohibited practices", 6: "Classification rules",
            9: "Risk management", 10: "Data governance", 11: "Technical documentation",
            13: "Transparency", 14: "Human oversight", 15: "Accuracy/robustness",
            50: "Transparency obligations", 51: "GPAI providers",
            52: "GPAI systemic risk", 72: "Post-market monitoring",
            83: "Penalties", 99: "Codes of practice", 113: "Entry into force",
        },
        "patterns": [r"\bAI\s+Act\b", r"\bRegulation\s*\(?EU\)?\s*2024/1689\b"],
    },
    "NIS2": {
        "full_name": "Directive (EU) 2022/2555",
        "max_article": 46,
        "key_articles": {
            6: "Definitions", 7: "National strategy", 21: "Risk management measures",
            23: "Reporting obligations", 26: "Jurisdiction", 34: "Penalties",
        },
        "patterns": [r"\bNIS\s*2\b", r"\bDirective\s*\(?EU\)?\s*2022/2555\b"],
    },
    "DORA": {
        "full_name": "Regulation (EU) 2022/2554",
        "max_article": 64,
        "key_articles": {
            3: "Definitions", 5: "Governance", 6: "ICT risk framework",
            17: "ICT incident reporting", 24: "Testing", 28: "Third-party risk",
        },
        "patterns": [r"\bDORA\b", r"\bRegulation\s*\(?EU\)?\s*2022/2554\b"],
    },
}

# Citation extraction patterns
CITATION_PATTERNS = [
    ("eu_article", re.compile(
        r"(?:Article|Art\.?)\s+(\d+)(?:\((\d+)\))?(?:\(([a-z])\))?"
    )),
    ("us_section", re.compile(
        r"(?:Section|Sec\.?|§)\s*(\d+(?:\.\d+)?)(?:\(([a-z0-9]+)\))?"
    )),
    ("eu_regulation", re.compile(
        r"(?:Regulation|Directive)\s+\(?(?:EU|EC)\)?\s*(?:No\.?\s*)?(\d{4})/(\d+)"
    )),
    ("us_cfr", re.compile(
        r"(\d+)\s+(?:C\.?F\.?R\.?)\s+(?:§\s*)?(\d+(?:\.\d+)?)"
    )),
    ("us_usc", re.compile(
        r"(\d+)\s+U\.?S\.?C\.?\s+(?:§\s*)?(\d+)"
    )),
    ("recital", re.compile(
        r"(?:Recital|recital)\s+\(?(\d+)\)?"
    )),
    ("annex", re.compile(
        r"(?:Annex|Schedule|Appendix)\s+([IVXLCDM]+|\d+)"
    )),
]

# Date extraction
DATE_PATTERN = re.compile(
    r"\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}[/-]\d{1,2}[/-]\d{1,2}|"
    r"(?:January|February|March|April|May|June|July|August|September|October|November|December)"
    r"\s+\d{1,2},?\s+\d{4}|\d{1,2}\s+"
    r"(?:January|February|March|April|May|June|July|August|September|October|November|December)"
    r"\s+\d{4})\b",
    re.IGNORECASE,
)

# Monetary amounts
MONEY_PATTERN = re.compile(
    r"(?:EUR|USD|GBP)?\s*[€$£]?\s*(\d[\d,]*(?:\.\d{1,2})?)\s*"
    r"(?:million|billion|thousand|[MBK])?\s*(?:EUR|USD|GBP)?",
    re.IGNORECASE,
)

# Hallucination flag patterns
HALLUCINATION_FLAGS = [
    {
        "id": "H1",
        "name": "Plausible but suspicious article number",
        "pattern": re.compile(r"(?:Article|Art\.?)\s+(\d+)\((\d+)\)", re.IGNORECASE),
        "check": "high_subsection",
        "description": "Article with high subsection number (>6) may not exist",
    },
    {
        "id": "H2",
        "name": "Confident implementation date",
        "pattern": re.compile(
            r"(?:will\s+(?:apply|enter\s+into\s+force|become\s+applicable)|effective|deadline)\s+"
            r"(?:from|on|by)\s+\d{1,2}\s+\w+\s+\d{4}",
            re.IGNORECASE,
        ),
        "check": "date_confidence",
        "description": "Specific implementation date stated with high confidence -- verify against official timeline",
    },
    {
        "id": "H3",
        "name": "Guidance stated as requirement",
        "pattern": re.compile(
            r"(?:(?:ENISA|EDPB|CNIL|ICO|FTC|NIST)\s+(?:requires?|mandates?|obligates?))|"
            r"(?:guidance|recommendation|guideline|best\s+practice)\s+(?:requires?|mandates?|must)",
            re.IGNORECASE,
        ),
        "check": "guidance_as_law",
        "description": "Non-binding guidance or recommendations stated as binding legal requirements",
    },
    {
        "id": "H4",
        "name": "Outdated reference indicator",
        "pattern": re.compile(
            r"(?:Directive\s+95/46|Data\s+Protection\s+Directive|Safe\s+Harbor)|"
            r"(?:repealed|superseded|replaced\s+by|no\s+longer\s+in\s+(?:force|effect))",
            re.IGNORECASE,
        ),
        "check": "outdated_ref",
        "description": "Reference to potentially repealed or superseded legal instrument",
    },
    {
        "id": "H5",
        "name": "Arithmetic in timeline",
        "pattern": re.compile(
            r"(\d+)\s+(?:days?|months?|years?)\s+(?:from|after|before|until)\s+",
            re.IGNORECASE,
        ),
        "check": "timeline_arithmetic",
        "description": "Timeline calculation that should be independently verified",
    },
]

# Speculation language patterns
SPECULATION_PATTERNS = [
    (re.compile(r"\b(?:will\s+likely|is\s+likely\s+to|probably|may\s+well)\b", re.I), "prediction"),
    (re.compile(r"\b(?:it\s+is\s+(?:expected|anticipated|believed))\b", re.I), "expectation"),
    (re.compile(r"\b(?:should\s+be\s+(?:interpreted|understood|read))\b", re.I), "interpretation"),
    (re.compile(r"\b(?:in\s+(?:our|my)\s+(?:view|opinion|assessment))\b", re.I), "opinion"),
    (re.compile(r"\b(?:courts?\s+(?:will|would|might|could)\s+(?:likely|probably))\b", re.I), "judicial_prediction"),
]


def extract_sentences(text: str) -> List[str]:
    """Split text into sentences."""
    abbrevs = ["Art.", "Sec.", "No.", "para.", "e.g.", "i.e.", "et al.", "cf.", "v.", "Ltd.", "Inc."]
    protected = text
    for abbr in abbrevs:
        protected = protected.replace(abbr, abbr.replace(".", "<DOT>"))
    sentences = re.split(r'(?<=[.!?])\s+', protected)
    return [s.replace("<DOT>", ".").strip() for s in sentences if s.strip()]


def identify_statutes(text: str) -> List[str]:
    """Identify which known statutes are referenced in the text."""
    found = []
    for statute_key, info in KNOWN_STATUTES.items():
        for pat in info["patterns"]:
            if re.search(pat, text, re.IGNORECASE):
                found.append(statute_key)
                break
    return found


def extract_citations(text: str) -> List[Dict[str, Any]]:
    """Extract all legal citations from text."""
    citations = []
    sentences = extract_sentences(text)
    for sent in sentences:
        for cit_type, pattern in CITATION_PATTERNS:
            for m in pattern.finditer(sent):
                citation = {
                    "type": cit_type,
                    "full_match": m.group(),
                    "groups": [g for g in m.groups() if g is not None],
                    "context": sent.strip()[:200],
                    "verification_status": "unverified",
                    "flags": [],
                }
                citations.append(citation)
    return citations


def validate_citations(citations: List[Dict], referenced_statutes: List[str]) -> List[Dict]:
    """Validate citations against known statute structures."""
    for citation in citations:
        if citation["type"] == "eu_article" and citation["groups"]:
            article_num = int(citation["groups"][0])
            subsection = int(citation["groups"][1]) if len(citation["groups"]) > 1 else None

            for statute_key in referenced_statutes:
                info = KNOWN_STATUTES.get(statute_key, {})
                max_art = info.get("max_article", 999)

                if article_num > max_art:
                    citation["flags"].append({
                        "severity": "CRITICAL",
                        "message": f"Article {article_num} exceeds maximum article ({max_art}) "
                                   f"in {info.get('full_name', statute_key)}",
                    })
                    citation["verification_status"] = "likely_invalid"
                elif article_num in info.get("key_articles", {}):
                    citation["verification_status"] = "plausible"
                    citation["known_topic"] = info["key_articles"][article_num]

                if subsection and subsection > 6:
                    citation["flags"].append({
                        "severity": "HIGH",
                        "message": f"Subsection ({subsection}) unusually high -- verify existence",
                    })
    return citations


def check_hallucination_patterns(text: str) -> List[Dict[str, Any]]:
    """Check for known AI hallucination patterns."""
    flags = []
    sentences = extract_sentences(text)

    for sent in sentences:
        for h in HALLUCINATION_FLAGS:
            for m in h["pattern"].finditer(sent):
                flag = {
                    "pattern_id": h["id"],
                    "pattern_name": h["name"],
                    "matched_text": m.group(),
                    "context": sent.strip()[:200],
                    "description": h["description"],
                    "action": "Verify against official source",
                }

                # Additional checks per pattern type
                if h["check"] == "high_subsection":
                    groups = m.groups()
                    if len(groups) > 1 and groups[1]:
                        sub = int(groups[1])
                        if sub > 6:
                            flag["severity"] = "HIGH"
                        else:
                            flag["severity"] = "MODERATE"
                    else:
                        flag["severity"] = "MODERATE"
                elif h["check"] == "guidance_as_law":
                    flag["severity"] = "HIGH"
                elif h["check"] == "outdated_ref":
                    flag["severity"] = "HIGH"
                elif h["check"] == "date_confidence":
                    flag["severity"] = "MODERATE"
                elif h["check"] == "timeline_arithmetic":
                    flag["severity"] = "MODERATE"
                else:
                    flag["severity"] = "MODERATE"

                flags.append(flag)
    return flags


def extract_dates_with_context(text: str) -> List[Dict[str, str]]:
    """Extract dates for verification."""
    dates = []
    sentences = extract_sentences(text)
    for sent in sentences:
        for m in DATE_PATTERN.finditer(sent):
            dates.append({
                "date": m.group().strip(),
                "context": sent.strip()[:200],
                "status": "requires_verification",
            })
    return dates


def detect_speculation(text: str) -> List[Dict[str, str]]:
    """Detect speculative or opinion language."""
    speculations = []
    sentences = extract_sentences(text)
    for sent in sentences:
        for pattern, spec_type in SPECULATION_PATTERNS:
            for m in pattern.finditer(sent):
                speculations.append({
                    "type": spec_type,
                    "matched_text": m.group(),
                    "context": sent.strip()[:200],
                    "action": "Verify if stated as fact or properly qualified",
                })
    return speculations


def check_disclaimers(text: str) -> Dict[str, Any]:
    """Check for required disclaimers."""
    text_lower = text.lower()
    checks = {
        "not_legal_advice": bool(re.search(
            r"(?:not\s+(?:constitute|intended\s+as)\s+legal\s+advice|"
            r"does\s+not\s+constitute\s+legal\s+advice|"
            r"for\s+informational\s+purposes\s+only)",
            text_lower,
        )),
        "jurisdiction_limitation": bool(re.search(
            r"(?:jurisdiction|applicable\s+(?:in|to)|"
            r"may\s+(?:vary|differ)\s+(?:by|across)\s+jurisdiction)",
            text_lower,
        )),
        "date_of_preparation": bool(re.search(
            r"(?:as\s+of|prepared\s+(?:on|as\s+of)|current\s+as\s+of|"
            r"last\s+(?:updated|reviewed))",
            text_lower,
        )),
        "professional_consultation": bool(re.search(
            r"(?:consult\s+(?:a\s+)?(?:qualified\s+)?(?:legal\s+)?(?:counsel|lawyer|attorney|professional|adviser)|"
            r"seek\s+(?:legal\s+)?(?:advice|counsel))",
            text_lower,
        )),
        "ai_generated_disclosure": bool(re.search(
            r"(?:ai[- ]generated|generated\s+(?:by|using)\s+ai|"
            r"artificial\s+intelligence|machine\s+generated|"
            r"assisted\s+by\s+ai)",
            text_lower,
        )),
        "accuracy_limitations": bool(re.search(
            r"(?:accuracy\s+(?:not\s+)?guaranteed|verify\s+(?:independently|against)|"
            r"no\s+(?:warranty|guarantee)\s+(?:of|as\s+to)\s+accuracy)",
            text_lower,
        )),
    }
    present = sum(1 for v in checks.values() if v)
    checks["score"] = f"{present}/6"
    checks["adequate"] = present >= 4
    return checks


def compute_summary(
    citations: List, hallucination_flags: List, dates: List,
    speculations: List, disclaimers: Dict
) -> Dict[str, Any]:
    """Compute verification summary."""
    severity_counts = {"CRITICAL": 0, "HIGH": 0, "MODERATE": 0, "LOW": 0}

    for cit in citations:
        for flag in cit.get("flags", []):
            sev = flag.get("severity", "MODERATE")
            severity_counts[sev] = severity_counts.get(sev, 0) + 1

    for h in hallucination_flags:
        sev = h.get("severity", "MODERATE")
        severity_counts[sev] = severity_counts.get(sev, 0) + 1

    if not disclaimers.get("adequate"):
        severity_counts["MODERATE"] += 1

    return {
        "total_citations": len(citations),
        "total_dates": len(dates),
        "total_speculations": len(speculations),
        "total_hallucination_flags": len(hallucination_flags),
        "findings_by_severity": severity_counts,
        "disclaimer_score": disclaimers.get("score", "0/6"),
    }


def format_human_report(result: Dict[str, Any]) -> str:
    """Format as human-readable report."""
    lines = []
    lines.append("=" * 72)
    lines.append("LEGAL FACT-CHECK REPORT")
    lines.append("=" * 72)

    s = result["summary"]
    lines.append(f"\nCitations found:       {s['total_citations']}")
    lines.append(f"Dates found:           {s['total_dates']}")
    lines.append(f"Speculation instances:  {s['total_speculations']}")
    lines.append(f"Hallucination flags:   {s['total_hallucination_flags']}")
    lines.append(f"Disclaimer score:      {s['disclaimer_score']}")

    sev = s["findings_by_severity"]
    lines.append(f"\nFindings: CRITICAL={sev['CRITICAL']}  HIGH={sev['HIGH']}  "
                 f"MODERATE={sev['MODERATE']}  LOW={sev['LOW']}")

    if result["hallucination_flags"]:
        lines.append(f"\n--- HALLUCINATION FLAGS ({len(result['hallucination_flags'])}) ---")
        for h in result["hallucination_flags"]:
            lines.append(f"\n  [{h['severity']}] {h['pattern_name']}")
            lines.append(f"    Matched: {h['matched_text']}")
            lines.append(f"    Context: {h['context'][:120]}")
            lines.append(f"    Action:  {h['action']}")

    flagged_citations = [c for c in result["citations"] if c.get("flags")]
    if flagged_citations:
        lines.append(f"\n--- FLAGGED CITATIONS ({len(flagged_citations)}) ---")
        for c in flagged_citations:
            lines.append(f"\n  Citation: {c['full_match']}")
            lines.append(f"  Status:   {c['verification_status']}")
            for f in c["flags"]:
                lines.append(f"    [{f['severity']}] {f['message']}")

    if result["speculations"]:
        lines.append(f"\n--- SPECULATION ({len(result['speculations'])}) ---")
        for sp in result["speculations"]:
            lines.append(f"  [{sp['type']}] {sp['matched_text']}")
            lines.append(f"    {sp['context'][:120]}")

    d = result["disclaimers"]
    lines.append(f"\n--- DISCLAIMERS ---")
    for key in ["not_legal_advice", "jurisdiction_limitation", "date_of_preparation",
                 "professional_consultation", "ai_generated_disclosure", "accuracy_limitations"]:
        status = "PRESENT" if d.get(key) else "MISSING"
        lines.append(f"  {key:30s} {status}")
    lines.append(f"  Adequate: {'YES' if d.get('adequate') else 'NO'}")

    lines.append("\n" + "=" * 72)
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Scan legal text for verifiable claims and flag hallucination patterns."
    )
    parser.add_argument("--input", "-i", type=str, help="Path to legal document")
    parser.add_argument("--text", "-t", type=str, help="Inline legal text")
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

        referenced_statutes = identify_statutes(text)
        citations = extract_citations(text)
        citations = validate_citations(citations, referenced_statutes)
        hallucination_flags = check_hallucination_patterns(text)
        dates = extract_dates_with_context(text)
        speculations = detect_speculation(text)
        disclaimers = check_disclaimers(text)
        summary = compute_summary(citations, hallucination_flags, dates, speculations, disclaimers)

        result = {
            "referenced_statutes": referenced_statutes,
            "citations": citations,
            "hallucination_flags": hallucination_flags,
            "dates": dates,
            "speculations": speculations,
            "disclaimers": disclaimers,
            "summary": summary,
        }

        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"Report saved to {args.output}")
        elif args.json:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(format_human_report(result))

    except FileNotFoundError:
        print(f"Error: File not found: {args.input}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
