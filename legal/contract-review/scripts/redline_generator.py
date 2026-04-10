#!/usr/bin/env python3
"""
Redline Generator

Takes contract analysis JSON and generates formatted redline suggestions
with priority tiers, rationale, and fallback positions.

Usage:
    python redline_generator.py analysis.json
    python redline_generator.py analysis.json --json
    python redline_generator.py analysis.json --output redlines.md
"""

import argparse
import json
import os
import sys
from typing import Dict, List, Optional


# Redline templates keyed by risk flag ID
REDLINE_TEMPLATES = {
    "uncapped_liability": {
        "tier": 1,
        "tier_label": "Must-Have",
        "clause_type": "Limitation of Liability",
        "issue": "Uncapped Liability",
        "preferred": (
            'Add: "The aggregate liability of either party under this Agreement '
            'shall not exceed the total fees paid or payable by Customer in the '
            'twelve (12) month period immediately preceding the claim."'
        ),
        "rationale": (
            "Uncapped liability creates unlimited financial exposure. Market standard "
            "for SaaS and services agreements is 12 months of fees."
        ),
        "fallback": (
            'Accept: "Aggregate liability shall not exceed the greater of (a) fees '
            'paid in the prior 24 months or (b) $1,000,000."'
        ),
        "negotiation_note": (
            "If counterparty insists on higher cap, ensure super-cap carveouts "
            "(IP infringement, confidentiality breach, willful misconduct) are explicit."
        ),
    },
    "no_consequential_damages_exclusion": {
        "tier": 2,
        "tier_label": "Should-Have",
        "clause_type": "Limitation of Liability",
        "issue": "Consequential Damages Not Excluded",
        "preferred": (
            'Add: "Neither party shall be liable for any indirect, incidental, '
            'special, consequential, or punitive damages, including loss of profits, '
            'data, or business opportunity."'
        ),
        "rationale": (
            "Consequential damages exposure is unpredictable and potentially massive. "
            "Mutual exclusion is market standard."
        ),
        "fallback": (
            'Accept mutual exclusion with carveouts for: (a) indemnification obligations, '
            '(b) breach of confidentiality, (c) willful misconduct.'
        ),
        "negotiation_note": (
            "Most sophisticated counterparties will accept mutual consequential damages "
            "exclusion. Push hard on this one."
        ),
    },
    "unilateral_indemnification": {
        "tier": 2,
        "tier_label": "Should-Have",
        "clause_type": "Indemnification",
        "issue": "Unilateral Indemnification",
        "preferred": (
            'Revise to: "Each party shall indemnify, defend, and hold harmless the '
            'other party from and against any third-party claims arising from the '
            "indemnifying party's breach of this Agreement or negligence.\""
        ),
        "rationale": (
            "One-sided indemnification shifts all risk to one party. Mutual "
            "indemnification balanced by scope is market standard."
        ),
        "fallback": (
            'Accept one-sided indemnification if: (a) subject to the liability cap, '
            '(b) limited to third-party claims only, (c) standard indemnification '
            'procedures apply (notice, control, cooperation).'
        ),
        "negotiation_note": (
            "If vendor refuses mutual indemnification, ensure the obligation is capped "
            "and includes proper indemnification procedures."
        ),
    },
    "broad_ip_assignment": {
        "tier": 1,
        "tier_label": "Must-Have",
        "clause_type": "Intellectual Property",
        "issue": "Broad IP Assignment",
        "preferred": (
            'Revise to: "All pre-existing IP remains the property of the originating '
            "party. Deliverables created specifically for Customer shall be assigned "
            'to Customer upon full payment. Provider retains rights to general tools, '
            'methodologies, and know-how."'
        ),
        "rationale": (
            "Blanket IP assignment may transfer pre-existing IP and tools, preventing "
            "the provider from serving other clients. Scope IP assignment to deliverables only."
        ),
        "fallback": (
            'Accept: Provider grants Customer an exclusive, perpetual, royalty-free '
            'license to all deliverables, with Provider retaining ownership of '
            'pre-existing IP and general tools.'
        ),
        "negotiation_note": (
            "IP ownership is often the hardest clause to negotiate. Be prepared to "
            "discuss work-for-hire vs. license models in detail."
        ),
    },
    "perpetual_term": {
        "tier": 1,
        "tier_label": "Must-Have",
        "clause_type": "Term & Termination",
        "issue": "Perpetual Term",
        "preferred": (
            'Revise to: "This Agreement shall have an initial term of [12/24/36] '
            "months, with renewal upon mutual written agreement. Either party may "
            'terminate with [30/60/90] days written notice."'
        ),
        "rationale": (
            "Perpetual terms lock parties into agreements with no exit path. "
            "Fixed terms with renewal options are market standard."
        ),
        "fallback": (
            'Accept: Perpetual term with either party having the right to terminate '
            'for convenience with 90 days written notice.'
        ),
        "negotiation_note": (
            "If counterparty needs long-term commitment, offer a longer initial term "
            "(36 months) with termination for convenience after the initial period."
        ),
    },
    "auto_renewal_no_opt_out": {
        "tier": 3,
        "tier_label": "Nice-to-Have",
        "clause_type": "Term & Termination",
        "issue": "Automatic Renewal",
        "preferred": (
            'Add: "This Agreement shall automatically renew for successive [12]-month '
            "periods unless either party provides written notice of non-renewal at "
            'least [60] days prior to the end of the then-current term."'
        ),
        "rationale": (
            "Auto-renewal is acceptable if the opt-out window is reasonable (30-90 days) "
            "and clearly documented."
        ),
        "fallback": (
            'Accept auto-renewal with 30-day opt-out window and no penalty for '
            'non-renewal.'
        ),
        "negotiation_note": "This is a common concession candidate. Easy to accept with minor tweaks.",
    },
    "no_cure_period": {
        "tier": 2,
        "tier_label": "Should-Have",
        "clause_type": "Term & Termination",
        "issue": "No Cure Period",
        "preferred": (
            'Add: "Upon material breach, the non-breaching party shall provide '
            "written notice specifying the breach. The breaching party shall have "
            '[30] days to cure the breach before termination takes effect."'
        ),
        "rationale": (
            "Immediate termination without cure leaves no opportunity to remediate. "
            "30-day cure periods are market standard."
        ),
        "fallback": (
            'Accept: 15-day cure period for material breach, with immediate '
            'termination only for breach of confidentiality or insolvency.'
        ),
        "negotiation_note": (
            "Most counterparties will agree to a cure period. Push for 30 days, "
            "accept 15 if necessary."
        ),
    },
    "unlimited_audit_rights": {
        "tier": 3,
        "tier_label": "Nice-to-Have",
        "clause_type": "Data Protection",
        "issue": "Unlimited Audit Rights",
        "preferred": (
            'Revise to: "Audits shall be conducted no more than once per twelve-month '
            "period, with at least 30 days' prior written notice, during normal "
            'business hours, and at the auditing party\'s expense."'
        ),
        "rationale": (
            "Unlimited audit rights create operational burden. Annual audits with "
            "notice are market standard."
        ),
        "fallback": (
            'Accept: Up to two audits per year with 15 days notice, with provision '
            'for additional audits upon reasonable suspicion of breach.'
        ),
        "negotiation_note": "Good concession candidate -- accept with reasonable frequency limits.",
    },
    "no_data_breach_notification": {
        "tier": 1,
        "tier_label": "Must-Have",
        "clause_type": "Data Protection",
        "issue": "No Breach Notification Obligation",
        "preferred": (
            'Add: "In the event of a data breach affecting personal data, the '
            "processing party shall notify the other party without undue delay and "
            'in no event later than 72 hours after becoming aware of the breach."'
        ),
        "rationale": (
            "Breach notification is required by GDPR (72 hours), state laws, and "
            "most compliance frameworks. Absence creates legal and regulatory exposure."
        ),
        "fallback": (
            'Accept: Notification within 5 business days of confirmed breach, '
            'with preliminary notice within 72 hours of suspected breach.'
        ),
        "negotiation_note": "Non-negotiable in regulated industries. Most counterparties expect this.",
    },
    "unfavorable_jurisdiction": {
        "tier": 2,
        "tier_label": "Should-Have",
        "clause_type": "Governing Law",
        "issue": "Potentially Unfavorable Jurisdiction",
        "preferred": (
            'Revise to: "This Agreement shall be governed by and construed in '
            'accordance with the laws of [your preferred state/country], without '
            'regard to conflict of laws principles."'
        ),
        "rationale": (
            "Home jurisdiction reduces litigation cost and increases predictability. "
            "Neutral jurisdictions (Delaware, England) are common alternatives."
        ),
        "fallback": (
            'Accept: Neutral jurisdiction (Delaware, New York, England) with '
            'option for arbitration under ICC or AAA rules.'
        ),
        "negotiation_note": "Jurisdiction is often traded for other concessions. Know your priorities.",
    },
    "jury_waiver": {
        "tier": 3,
        "tier_label": "Nice-to-Have",
        "clause_type": "Governing Law",
        "issue": "Jury Trial Waiver",
        "preferred": (
            "Remove jury trial waiver clause and retain right to jury trial."
        ),
        "rationale": (
            "Jury trial waivers benefit the party with more resources. Retaining "
            "jury rights preserves optionality."
        ),
        "fallback": (
            'Accept: Jury trial waiver if coupled with binding arbitration clause '
            'under mutually agreed rules (AAA, JAMS).'
        ),
        "negotiation_note": "Low-priority item. Trade this for a Tier 1 or Tier 2 win.",
    },
    "as_is_no_warranty": {
        "tier": 2,
        "tier_label": "Should-Have",
        "clause_type": "Representations & Warranties",
        "issue": "Full Warranty Disclaimer",
        "preferred": (
            'Add: "Provider represents and warrants that (a) the services will '
            "perform materially in accordance with the documentation, (b) services "
            "will be provided in a professional and workmanlike manner, and (c) "
            'Provider has the authority to enter into this Agreement."'
        ),
        "rationale": (
            "A complete warranty disclaimer shifts all performance risk to the buyer. "
            "Minimum warranties for conformance and authority are market standard."
        ),
        "fallback": (
            'Accept: Limited warranty for 90 days post-delivery that services '
            'materially conform to specifications.'
        ),
        "negotiation_note": "Warranty scope depends on deal size. Larger deals warrant stronger warranties.",
    },
}

# Missing clause redline templates
MISSING_CLAUSE_REDLINES = {
    "limitation_of_liability": {
        "tier": 1,
        "tier_label": "Must-Have",
        "clause_type": "Limitation of Liability",
        "issue": "Missing Liability Cap",
        "preferred": (
            'Add entire section: "LIMITATION OF LIABILITY. The aggregate liability '
            "of either party shall not exceed the total fees paid in the 12 months "
            'preceding the claim. Neither party shall be liable for indirect, '
            'incidental, special, or consequential damages."'
        ),
        "rationale": "No liability cap means unlimited exposure for both parties.",
        "fallback": "Accept 24-month cap with mutual consequential damages exclusion.",
        "negotiation_note": "Absence of this clause is unusual and should be addressed immediately.",
    },
    "indemnification": {
        "tier": 2,
        "tier_label": "Should-Have",
        "clause_type": "Indemnification",
        "issue": "Missing Indemnification Section",
        "preferred": (
            'Add mutual indemnification clause covering third-party claims '
            'arising from breach, negligence, and IP infringement.'
        ),
        "rationale": "Without indemnification, parties have no contractual right to defense and hold-harmless.",
        "fallback": "Accept IP-only indemnification from provider at minimum.",
        "negotiation_note": "Critical for any agreement involving third-party deliverables or IP.",
    },
    "data_protection": {
        "tier": 1,
        "tier_label": "Must-Have",
        "clause_type": "Data Protection",
        "issue": "Missing Data Protection Provisions",
        "preferred": (
            'Add: Data Processing Addendum covering roles, purposes, sub-processors, '
            'breach notification (72 hours), cross-border transfers, and audit rights.'
        ),
        "rationale": "Required by GDPR, CCPA, and most compliance frameworks when personal data is processed.",
        "fallback": "Accept reference to provider standard DPA with annual review right.",
        "negotiation_note": "Non-negotiable if personal data is involved. Regulatory requirement.",
    },
    "force_majeure": {
        "tier": 3,
        "tier_label": "Nice-to-Have",
        "clause_type": "Force Majeure",
        "issue": "Missing Force Majeure Clause",
        "preferred": (
            'Add: "Neither party shall be liable for failure to perform obligations '
            'due to events beyond reasonable control, including natural disasters, '
            'pandemics, government actions, or infrastructure failures, provided '
            'the affected party notifies the other within 5 business days."'
        ),
        "rationale": "Protects both parties from liability for unforeseeable disruptions.",
        "fallback": "Accept limitation of force majeure to 90 days before termination right triggers.",
        "negotiation_note": "Common clause, easy to add. Good goodwill item.",
    },
    "confidentiality": {
        "tier": 2,
        "tier_label": "Should-Have",
        "clause_type": "Confidentiality",
        "issue": "Missing Confidentiality Section",
        "preferred": (
            'Add mutual confidentiality obligations with 3-year survival, '
            'standard carveouts, and return/destruction upon termination.'
        ),
        "rationale": "Without confidentiality provisions, shared information has no contractual protection.",
        "fallback": "Accept reference to separate mutual NDA if already executed.",
        "negotiation_note": "If separate NDA exists, ensure it covers the scope of this agreement.",
    },
    "governing_law": {
        "tier": 2,
        "tier_label": "Should-Have",
        "clause_type": "Governing Law",
        "issue": "Missing Governing Law Clause",
        "preferred": (
            'Add: "This Agreement shall be governed by the laws of [preferred jurisdiction]."'
        ),
        "rationale": "Without governing law, disputes default to complex conflict-of-laws analysis.",
        "fallback": "Accept neutral jurisdiction (Delaware, New York, England).",
        "negotiation_note": "Straightforward to add. Most counterparties will agree to a neutral venue.",
    },
    "intellectual_property": {
        "tier": 1,
        "tier_label": "Must-Have",
        "clause_type": "Intellectual Property",
        "issue": "Missing IP Ownership Provisions",
        "preferred": (
            'Add: Clear IP ownership clause specifying pre-existing IP, deliverable '
            'ownership, license grants, and feedback/improvements handling.'
        ),
        "rationale": "Without IP provisions, ownership of deliverables and work product is ambiguous.",
        "fallback": "Accept license-based model with exclusive rights to deliverables.",
        "negotiation_note": "Critical for any engagement producing deliverables or custom work.",
    },
}


def load_analysis(file_path: str) -> Dict:
    """Load contract analysis JSON."""
    if not os.path.isfile(file_path):
        print(f"Error: File not found: {file_path}", file=sys.stderr)
        sys.exit(1)
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {file_path}: {e}", file=sys.stderr)
        sys.exit(1)
    # Validate structure
    if "clauses_found" not in data:
        print("Error: Analysis JSON must contain 'clauses_found' key.", file=sys.stderr)
        sys.exit(1)
    return data


def generate_redlines(analysis: Dict) -> List[Dict]:
    """Generate redline suggestions from analysis findings."""
    redlines: List[Dict] = []
    seen_issues: set = set()

    # Process risk flags from detected clauses
    for clause in analysis.get("clauses_found", []):
        if clause["severity"] == "GREEN":
            continue
        for flag in clause.get("risk_flags", []):
            if flag in REDLINE_TEMPLATES and flag not in seen_issues:
                template = REDLINE_TEMPLATES[flag].copy()
                template["source"] = "risk_flag"
                template["source_clause"] = clause["type"]
                template["source_severity"] = clause["severity"]
                redlines.append(template)
                seen_issues.add(flag)

    # Process missing clauses
    for missing_clause in analysis.get("missing_clauses", []):
        if missing_clause in MISSING_CLAUSE_REDLINES and missing_clause not in seen_issues:
            template = MISSING_CLAUSE_REDLINES[missing_clause].copy()
            template["source"] = "missing_clause"
            template["source_clause"] = missing_clause
            template["source_severity"] = "YELLOW"
            redlines.append(template)
            seen_issues.add(missing_clause)

    # Sort by tier (1 first), then by severity
    severity_order = {"RED": 0, "YELLOW": 1, "GREEN": 2}
    redlines.sort(key=lambda r: (
        r["tier"],
        severity_order.get(r.get("source_severity", "GREEN"), 2),
    ))

    return redlines


def format_text_output(redlines: List[Dict], analysis: Dict) -> str:
    """Format redlines as human-readable text."""
    lines = []
    lines.append("REDLINE SUGGESTIONS")
    lines.append("=" * 50)
    lines.append(f"Source: {analysis.get('file', 'unknown')}")
    lines.append(f"Overall Risk: {analysis.get('overall_risk', 'N/A')}")
    lines.append(f"Total Redlines: {len(redlines)}")
    lines.append("")

    # Summary by tier
    tier_counts = {}
    for r in redlines:
        label = r["tier_label"]
        tier_counts[label] = tier_counts.get(label, 0) + 1
    for label in ["Must-Have", "Should-Have", "Nice-to-Have"]:
        if label in tier_counts:
            lines.append(f"  {label}: {tier_counts[label]}")
    lines.append("")

    if not redlines:
        lines.append("No redline suggestions generated. All clauses appear acceptable.")
        return "\n".join(lines)

    current_tier = None
    for r in redlines:
        if r["tier"] != current_tier:
            current_tier = r["tier"]
            lines.append(f"--- TIER {current_tier}: {r['tier_label'].upper()} ---")
            lines.append("")

        lines.append(f"[{r['tier_label'].upper()}] {r['clause_type']} -- {r['issue']}")
        lines.append(f"  Severity: {r.get('source_severity', 'N/A')}")
        lines.append(f"  Preferred: {r['preferred']}")
        lines.append(f"  Rationale: {r['rationale']}")
        lines.append(f"  Fallback:  {r['fallback']}")
        if r.get("negotiation_note"):
            lines.append(f"  Note:      {r['negotiation_note']}")
        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Generate redline suggestions from contract analysis JSON."
    )
    parser.add_argument("analysis_json", help="Path to contract analysis JSON file")
    parser.add_argument("--json", action="store_true", dest="json_output",
                        help="Output in JSON format")
    parser.add_argument("-o", "--output", help="Write output to file")

    args = parser.parse_args()
    analysis = load_analysis(args.analysis_json)
    redlines = generate_redlines(analysis)

    if args.json_output:
        output = json.dumps({"redlines": redlines, "total": len(redlines),
                             "source_file": analysis.get("file", "unknown")}, indent=2)
    else:
        output = format_text_output(redlines, analysis)

    if args.output:
        try:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(output)
            print(f"Output written to {args.output}")
        except IOError as e:
            print(f"Error writing to {args.output}: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print(output)


if __name__ == "__main__":
    main()
