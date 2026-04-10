#!/usr/bin/env python3
"""
Whistleblower Policy Scaffolder

Generates a whistleblower policy skeleton pre-populated with required sections
per regulatory framework (EU Directive 2019/1937, US SOX/Dodd-Frank, UK PIDA).

Usage:
    python whistleblower_policy_scaffolder.py --jurisdiction EU --org-type private --headcount 500 --org-name "Acme Corp"
    python whistleblower_policy_scaffolder.py --jurisdiction US --org-type public --headcount 10000 --json
    python whistleblower_policy_scaffolder.py --jurisdiction UK --org-type nonprofit --headcount 100 --output policy.md
"""

import argparse
import json
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional


# Section definitions per jurisdiction
COMMON_SECTIONS = [
    "Purpose and Scope",
    "Definitions",
    "Who Can Report",
    "What Can Be Reported",
    "Reporting Channels",
    "How to Make a Report",
    "Handling of Reports",
    "Confidentiality",
    "Protections Against Retaliation",
    "Record Keeping and Data Protection",
    "Review and Updates",
]

JURISDICTION_SECTIONS: Dict[str, List[str]] = {
    "EU": [
        "Internal Reporting Channel",
        "External Reporting to Competent Authority",
        "Public Disclosure Conditions",
        "Acknowledgment and Feedback Timelines",
        "Designated Person(s)",
        "GDPR and Data Protection Compliance",
        "Cross-Border Reporting",
        "National Transposition Specifics",
    ],
    "US": [
        "SOX Section 806 Compliance",
        "Dodd-Frank Whistleblower Provisions",
        "SEC Reporting and Bounty Program",
        "OSHA Complaint Process",
        "Filing Deadlines",
        "Audit Committee Oversight",
        "Anti-Retaliation Provisions",
    ],
    "UK": [
        "Qualifying Disclosures",
        "Prescribed Persons",
        "Employment Tribunal Rights",
        "Public Interest Test",
        "Reasonable Belief Standard",
        "GDPR UK and Data Protection Act 2018",
        "Disclosure to Legal Advisors",
    ],
}

SECTOR_SECTIONS: Dict[str, List[str]] = {
    "financial": ["Financial Regulatory Reporting", "Anti-Money Laundering Integration"],
    "healthcare": ["Patient Safety Reporting", "Clinical Governance Alignment"],
    "defense": ["Classified Information Handling", "Security Clearance Considerations"],
    "nuclear": ["Nuclear Safety Authority Notification", "Radiation Safety Integration"],
    "technology": ["Cybersecurity Incident Reporting Integration"],
}


def build_section_content(section: str, org_name: str, jurisdiction: str,
                          org_type: str, headcount: int) -> str:
    """Generate placeholder content for a policy section."""
    placeholders: Dict[str, str] = {
        "Purpose and Scope": (
            f"This policy establishes the framework for reporting suspected wrongdoing "
            f"at {org_name}. It applies to all employees, contractors, consultants, "
            f"temporary workers, and business partners.\n\n"
            f"[CUSTOMIZE: Define specific scope based on organizational structure and "
            f"geographic operations.]"
        ),
        "Definitions": (
            "For the purposes of this policy:\n\n"
            "- **Whistleblower/Reporter**: Any person who reports information about "
            "breaches acquired in a work-related context.\n"
            "- **Report**: A disclosure of information about suspected wrongdoing.\n"
            "- **Retaliation**: Any direct or indirect act or omission that causes or "
            "may cause unjustified detriment to the reporter.\n"
            "- **Designated Person**: The individual(s) responsible for receiving and "
            "following up on reports.\n"
            "- **Breach**: Acts or omissions that are unlawful or defeat the object "
            "or purpose of applicable rules.\n\n"
            "[CUSTOMIZE: Add organization-specific definitions as needed.]"
        ),
        "Who Can Report": (
            "The following persons are entitled to protection under this policy:\n\n"
            "- Current and former employees\n"
            "- Job applicants and candidates\n"
            "- Contractors, subcontractors, and suppliers\n"
            "- Shareholders and members of management bodies\n"
            "- Volunteers and unpaid trainees\n"
            "- Persons assisting the reporter (facilitators)\n"
            "- Third parties connected with the reporter\n\n"
            "[CUSTOMIZE: Adjust based on applicable jurisdiction and organizational structure.]"
        ),
        "What Can Be Reported": (
            "This policy covers reports of suspected breaches including:\n\n"
            "- Fraud, corruption, and bribery\n"
            "- Financial irregularities and accounting manipulation\n"
            "- Health and safety violations\n"
            "- Environmental offenses\n"
            "- Data protection and privacy breaches\n"
            "- Discrimination and harassment\n"
            "- Competition law violations\n"
            "- Tax evasion and avoidance\n"
            "- Product safety and compliance failures\n"
            "- Obstruction of justice or regulatory proceedings\n\n"
            "[CUSTOMIZE: Add sector-specific reportable matters.]"
        ),
        "Reporting Channels": (
            f"## Internal Reporting Channel\n\n"
            f"{org_name} provides the following internal reporting channels:\n\n"
            f"- **Online portal**: [INSERT URL]\n"
            f"- **Email**: [INSERT DEDICATED EMAIL]\n"
            f"- **Phone/Hotline**: [INSERT NUMBER]\n"
            f"- **In person**: By appointment with [INSERT DESIGNATED PERSON]\n"
            f"- **Written submission**: Marked 'Confidential' to [INSERT ADDRESS]\n\n"
            f"Reports may be submitted anonymously where permitted by law.\n\n"
            f"[CUSTOMIZE: Specify available channels and contact details.]"
        ),
        "How to Make a Report": (
            "When making a report, include as much of the following as possible:\n\n"
            "1. Description of the suspected breach or wrongdoing\n"
            "2. Names of persons involved (if known)\n"
            "3. Dates and locations of the events\n"
            "4. Any evidence or documentation supporting the report\n"
            "5. Whether the matter has been reported elsewhere\n\n"
            "Reports do not need to be proven. A reasonable belief that the "
            "information is true at the time of reporting is sufficient."
        ),
        "Handling of Reports": (
            "Upon receipt of a report, the following process applies:\n\n"
            "1. **Acknowledgment**: The reporter receives written acknowledgment "
            f"{'within 7 calendar days' if jurisdiction == 'EU' else 'promptly'}.\n"
            "2. **Initial Assessment**: The designated person assesses whether the "
            "report falls within scope and determines next steps.\n"
            "3. **Investigation**: An impartial investigation is conducted by "
            "qualified personnel with no conflict of interest.\n"
            "4. **Feedback**: The reporter is informed of the outcome "
            f"{'within 3 months of acknowledgment' if jurisdiction == 'EU' else 'as soon as practicable'}.\n"
            "5. **Closure**: The investigation is closed with documented findings "
            "and any corrective actions.\n\n"
            "[CUSTOMIZE: Define specific investigation procedures and escalation paths.]"
        ),
        "Confidentiality": (
            "The identity of the reporter shall not be disclosed to anyone beyond "
            "authorized staff without the explicit consent of the reporter, unless "
            "required by law in the context of judicial proceedings.\n\n"
            "Confidentiality measures include:\n\n"
            "- Access restricted to designated person(s) only\n"
            "- Secure storage of all report documentation\n"
            "- Anonymization of information shared for investigation purposes\n"
            "- Disciplinary action for unauthorized disclosure\n\n"
            "[CUSTOMIZE: Specify technical and organizational confidentiality measures.]"
        ),
        "Protections Against Retaliation": (
            "Retaliation against a reporter is strictly prohibited. Prohibited forms "
            "of retaliation include, but are not limited to:\n\n"
            "- Dismissal, suspension, or demotion\n"
            "- Reduction in duties, salary, or benefits\n"
            "- Harassment, intimidation, or bullying\n"
            "- Negative performance references or evaluations\n"
            "- Blacklisting within the industry\n"
            "- Early termination of contract or license\n"
            "- Psychiatric or medical referrals\n\n"
            f"{'The burden of proof in retaliation claims rests with the employer. ' if jurisdiction == 'EU' else ''}"
            f"{'Reporters may seek compensatory damages through employment tribunal proceedings. ' if jurisdiction == 'UK' else ''}"
            f"{'Reporters may file complaints with OSHA within 180 days and may be eligible for SEC bounty awards. ' if jurisdiction == 'US' else ''}\n\n"
            "[CUSTOMIZE: Specify organizational anti-retaliation procedures and remedies.]"
        ),
        "Record Keeping and Data Protection": (
            "All reports and related documentation shall be retained in accordance "
            "with applicable data protection laws and organizational retention policies.\n\n"
            "- Reports retained for the duration of the investigation plus [INSERT PERIOD]\n"
            "- Personal data processed only for investigation purposes\n"
            "- Data subjects informed of processing (except where it would compromise the investigation)\n"
            f"{'- Data Protection Impact Assessment completed for whistleblower processing' if jurisdiction in ['EU', 'UK'] else ''}\n"
            f"{'- Processing based on Art. 6(1)(c) GDPR (legal obligation) or Art. 6(1)(e) (public interest)' if jurisdiction in ['EU', 'UK'] else ''}\n\n"
            "[CUSTOMIZE: Specify retention periods, legal basis, and technical measures.]"
        ),
        "Review and Updates": (
            f"This policy shall be reviewed [annually/biannually] by {org_name}'s "
            "legal department and updated to reflect changes in applicable law, "
            "regulatory guidance, and organizational structure.\n\n"
            "- Last reviewed: [INSERT DATE]\n"
            "- Next review due: [INSERT DATE]\n"
            "- Policy owner: [INSERT NAME/TITLE]\n"
            "- Approved by: [INSERT NAME/TITLE/BOARD]\n\n"
            "[CUSTOMIZE: Specify review frequency and approval workflow.]"
        ),
        "Internal Reporting Channel": (
            "In accordance with EU Directive 2019/1937, this organization maintains "
            "internal reporting channels that are secure, ensure confidentiality, and "
            "allow written, oral, and in-person reporting.\n\n"
            "[CUSTOMIZE: Describe channel implementation details.]"
        ),
        "External Reporting to Competent Authority": (
            "Reporters may report directly to the competent national authority if:\n\n"
            "- Internal reporting would be ineffective\n"
            "- There is risk of retaliation\n"
            "- There is an imminent or manifest danger to the public interest\n\n"
            "Competent authority: [INSERT NATIONAL AUTHORITY]\n\n"
            "[CUSTOMIZE: Identify the relevant national competent authority.]"
        ),
        "Public Disclosure Conditions": (
            "Public disclosure is protected only when:\n\n"
            "1. The reporter first reported internally and/or externally but no "
            "appropriate action was taken within prescribed timelines; or\n"
            "2. There is an imminent or manifest danger to the public interest; or\n"
            "3. External reporting would risk retaliation or destruction of evidence.\n\n"
            "[CUSTOMIZE: Clarify organizational position on public disclosure.]"
        ),
        "Acknowledgment and Feedback Timelines": (
            "- **Acknowledgment**: Within 7 calendar days of receipt\n"
            "- **Feedback**: Within 3 months from date of acknowledgment\n"
            "- Feedback includes: confirmation of receipt, status of follow-up, "
            "and planned or taken actions (without compromising the investigation)\n\n"
            "[CUSTOMIZE: Specify internal workflow to meet these mandatory timelines.]"
        ),
        "Designated Person(s)": (
            "The following person(s) are designated to receive and follow up on reports:\n\n"
            "- Primary: [INSERT NAME, TITLE, CONTACT]\n"
            "- Alternate: [INSERT NAME, TITLE, CONTACT]\n\n"
            "Designated persons are selected for their independence, competence, "
            "and absence of conflicts of interest.\n\n"
            "[CUSTOMIZE: Appoint designated persons and define their mandate.]"
        ),
    }

    return placeholders.get(section, f"[CUSTOMIZE: Complete this section for {org_name}.]\n")


def generate_policy(args: argparse.Namespace) -> Dict[str, Any]:
    """Generate the full policy scaffold."""
    jurisdiction = args.jurisdiction
    org_type = args.org_type
    headcount = args.headcount
    org_name = args.org_name or "[ORGANIZATION NAME]"
    sector = getattr(args, "sector", "general")

    # Build section list
    all_sections = list(COMMON_SECTIONS)
    all_sections.extend(JURISDICTION_SECTIONS.get(jurisdiction, []))

    sector_extras = SECTOR_SECTIONS.get(sector, [])
    if sector_extras:
        all_sections.extend(sector_extras)

    # Generate policy document
    policy_lines = []
    policy_lines.append(f"# {org_name} Whistleblower Policy")
    policy_lines.append("")
    policy_lines.append(f"**Effective Date:** [INSERT DATE]")
    policy_lines.append(f"**Version:** 1.0")
    policy_lines.append(f"**Jurisdiction:** {jurisdiction}")
    policy_lines.append(f"**Organization Type:** {org_type.title()}")
    policy_lines.append(f"**Applicable Regulation:** "
                        f"{'EU Directive 2019/1937' if jurisdiction == 'EU' else ''}"
                        f"{'SOX Section 806 / Dodd-Frank' if jurisdiction == 'US' else ''}"
                        f"{'Public Interest Disclosure Act 1998' if jurisdiction == 'UK' else ''}")
    policy_lines.append(f"**Approved By:** [INSERT NAME/TITLE]")
    policy_lines.append("")
    policy_lines.append("---")
    policy_lines.append("")

    # Table of contents
    policy_lines.append("## Table of Contents")
    policy_lines.append("")
    for i, section in enumerate(all_sections, 1):
        anchor = section.lower().replace(" ", "-").replace("/", "").replace("(", "").replace(")", "")
        policy_lines.append(f"{i}. [{section}](#{anchor})")
    policy_lines.append("")
    policy_lines.append("---")
    policy_lines.append("")

    # Sections
    sections_data = []
    for i, section in enumerate(all_sections, 1):
        content = build_section_content(section, org_name, jurisdiction, org_type, headcount)
        policy_lines.append(f"## {i}. {section}")
        policy_lines.append("")
        policy_lines.append(content)
        policy_lines.append("")
        sections_data.append({"number": i, "title": section, "has_content": True})

    policy_lines.append("---")
    policy_lines.append("")
    policy_lines.append(f"*Policy generated on {datetime.now().strftime('%Y-%m-%d')} "
                        f"for {org_name}. This is a template requiring legal review "
                        f"and customization before adoption.*")

    policy_text = "\n".join(policy_lines)

    return {
        "generated_date": datetime.now().strftime("%Y-%m-%d"),
        "jurisdiction": jurisdiction,
        "org_name": org_name,
        "org_type": org_type,
        "headcount": headcount,
        "total_sections": len(all_sections),
        "sections": sections_data,
        "policy_text": policy_text,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a whistleblower policy skeleton based on jurisdiction and org type."
    )
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    parser.add_argument("--jurisdiction", required=True, choices=["EU", "US", "UK"],
                        help="Regulatory jurisdiction")
    parser.add_argument("--org-type", required=True, choices=["public", "private", "nonprofit"],
                        help="Organization type")
    parser.add_argument("--headcount", required=True, type=int,
                        help="Number of employees")
    parser.add_argument("--org-name", default=None,
                        help="Organization name for policy template")
    parser.add_argument("--sector", default="general",
                        help="Industry sector for additional sections")
    parser.add_argument("--output", default=None,
                        help="Write policy to file instead of stdout")

    args = parser.parse_args()

    try:
        result = generate_policy(args)

        if args.output:
            with open(args.output, "w") as f:
                f.write(result["policy_text"])
            print(f"Policy written to {args.output} ({result['total_sections']} sections)")
        elif args.json:
            print(json.dumps(result, indent=2))
        else:
            print(result["policy_text"])
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
