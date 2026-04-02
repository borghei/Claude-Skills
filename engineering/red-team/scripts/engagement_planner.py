#!/usr/bin/env python3
"""
Engagement Planner - Plan red team and penetration testing engagements.

Generates comprehensive engagement plans including scope, rules of engagement,
methodology selection, phase timelines, and deliverable checklists.

Author: Claude Skills Engineering Team
License: MIT
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional


ENGAGEMENT_TYPES = {
    "red-team": {
        "name": "Red Team Assessment",
        "description": "Full adversary simulation testing detection, response, and resilience capabilities.",
        "stealth": True,
        "default_phases": ["planning", "reconnaissance", "initial-access", "persistence",
                           "lateral-movement", "objective", "reporting"],
    },
    "pentest": {
        "name": "Penetration Test",
        "description": "Authorized vulnerability exploitation to identify security weaknesses.",
        "stealth": False,
        "default_phases": ["planning", "reconnaissance", "vulnerability-analysis",
                           "exploitation", "post-exploitation", "reporting"],
    },
    "purple-team": {
        "name": "Purple Team Exercise",
        "description": "Collaborative attack/defense exercise with real-time knowledge sharing.",
        "stealth": False,
        "default_phases": ["planning", "scenario-development", "execution",
                           "detection-tuning", "reporting"],
    },
    "app-security": {
        "name": "Application Security Assessment",
        "description": "Focused security testing of web/mobile/API applications.",
        "stealth": False,
        "default_phases": ["planning", "reconnaissance", "static-analysis",
                           "dynamic-testing", "business-logic", "reporting"],
    },
}

TARGET_TYPES = {
    "web-application": {
        "methodology": "OWASP Testing Guide v4.2",
        "tools_suggested": ["Burp Suite", "OWASP ZAP", "Nikto", "SQLMap", "ffuf"],
        "test_categories": [
            "Information Gathering", "Configuration Testing", "Identity Management",
            "Authentication", "Authorization", "Session Management",
            "Input Validation", "Error Handling", "Cryptography",
            "Business Logic", "Client-Side", "API Testing",
        ],
    },
    "network": {
        "methodology": "PTES + NIST SP 800-115",
        "tools_suggested": ["Nmap", "Metasploit", "Responder", "CrackMapExec", "BloodHound"],
        "test_categories": [
            "Network Mapping", "Service Enumeration", "Vulnerability Scanning",
            "Exploitation", "Credential Attacks", "Lateral Movement",
            "Active Directory Assessment", "Wireless Testing",
        ],
    },
    "api": {
        "methodology": "OWASP API Security Top 10",
        "tools_suggested": ["Postman", "Burp Suite", "ffuf", "jwt_tool", "GraphQL Voyager"],
        "test_categories": [
            "Broken Object Level Authorization", "Broken Authentication",
            "Excessive Data Exposure", "Lack of Resources & Rate Limiting",
            "Broken Function Level Authorization", "Mass Assignment",
            "Security Misconfiguration", "Injection", "Improper Assets Management",
            "Insufficient Logging & Monitoring",
        ],
    },
    "cloud": {
        "methodology": "CIS Benchmarks + Cloud-specific guides",
        "tools_suggested": ["ScoutSuite", "Prowler", "CloudSploit", "Pacu", "enumerate-iam"],
        "test_categories": [
            "IAM Configuration", "Storage Security", "Network Configuration",
            "Logging & Monitoring", "Encryption", "Serverless Security",
            "Container Security", "Data Exposure",
        ],
    },
    "full-org": {
        "methodology": "MITRE ATT&CK Enterprise",
        "tools_suggested": ["Cobalt Strike", "BloodHound", "Covenant", "Mythic", "Sliver"],
        "test_categories": [
            "OSINT/Reconnaissance", "Social Engineering", "Initial Access",
            "Privilege Escalation", "Lateral Movement", "Data Exfiltration",
            "Detection Evasion", "Persistence",
        ],
    },
}

COMPLIANCE_MAPPINGS = {
    "pci-dss": {
        "name": "PCI-DSS v4.0",
        "requirements": [
            "11.3.1: Internal vulnerability scans quarterly",
            "11.3.2: External vulnerability scans quarterly",
            "11.4.1: Penetration testing annually",
            "11.4.3: Segmentation testing every 6 months",
            "6.2.4: Web application security testing",
        ],
        "scope_notes": "All systems in the Cardholder Data Environment (CDE) and connected systems.",
    },
    "soc2": {
        "name": "SOC 2 Type II",
        "requirements": [
            "CC7.1: Detect and respond to security incidents",
            "CC7.2: Monitor system components for anomalies",
            "CC6.1: Logical and physical access controls",
            "CC8.1: Change management controls",
        ],
        "scope_notes": "Systems processing, storing, or transmitting customer data per Trust Services Criteria.",
    },
    "hipaa": {
        "name": "HIPAA Security Rule",
        "requirements": [
            "164.308(a)(8): Periodic technical evaluation",
            "164.312(a): Access controls",
            "164.312(c): Integrity controls",
            "164.312(e): Transmission security",
        ],
        "scope_notes": "All systems handling Protected Health Information (PHI).",
    },
    "iso27001": {
        "name": "ISO 27001:2022",
        "requirements": [
            "A.5.35: Independent review of information security",
            "A.8.8: Management of technical vulnerabilities",
            "A.8.16: Monitoring activities",
        ],
        "scope_notes": "Systems within the Information Security Management System (ISMS) scope.",
    },
}

PHASE_DETAILS = {
    "planning": {"pct": 10, "desc": "Scope definition, ROE agreement, logistics, tool preparation"},
    "reconnaissance": {"pct": 15, "desc": "OSINT gathering, network mapping, service enumeration"},
    "initial-access": {"pct": 15, "desc": "Phishing, exploit public apps, credential attacks"},
    "vulnerability-analysis": {"pct": 15, "desc": "Vulnerability scanning, manual testing, analysis"},
    "exploitation": {"pct": 20, "desc": "Vulnerability exploitation, payload delivery, initial access"},
    "post-exploitation": {"pct": 15, "desc": "Privilege escalation, credential harvesting, pivoting"},
    "persistence": {"pct": 10, "desc": "Establishing persistent access, backdoor deployment"},
    "lateral-movement": {"pct": 15, "desc": "Moving through the network, accessing additional systems"},
    "objective": {"pct": 10, "desc": "Achieving engagement objectives, data access, impact demonstration"},
    "reporting": {"pct": 10, "desc": "Finding documentation, risk scoring, remediation recommendations"},
    "scenario-development": {"pct": 15, "desc": "Attack scenario design, TTP selection, detection mapping"},
    "execution": {"pct": 30, "desc": "Running attack scenarios with blue team observation"},
    "detection-tuning": {"pct": 15, "desc": "Analyzing detection gaps, tuning alerts, improving response"},
    "static-analysis": {"pct": 15, "desc": "Source code review, configuration analysis"},
    "dynamic-testing": {"pct": 25, "desc": "Runtime testing, fuzzing, injection testing"},
    "business-logic": {"pct": 15, "desc": "Business logic flaws, workflow bypasses, authorization issues"},
}


def parse_duration(duration_str: str) -> int:
    """Parse duration string to business days (e.g., '2w', '10d', '3w')."""
    match = re.match(r'(\d+)\s*([dwm])', duration_str.lower())
    if not match:
        return 10  # default 2 weeks

    num = int(match.group(1))
    unit = match.group(2)

    if unit == 'd':
        return num
    elif unit == 'w':
        return num * 5
    elif unit == 'm':
        return num * 22
    return num


@dataclass
class EngagementPlan:
    """Complete engagement plan."""
    engagement_type: str
    engagement_name: str
    description: str
    targets: List[str]
    duration_days: int
    start_date: str
    end_date: str
    methodology: List[str]
    phases: List[Dict]
    rules_of_engagement: Dict
    deliverables: List[str]
    tools_suggested: List[str]
    test_categories: List[str]
    compliance: Optional[Dict] = None
    risk_notes: List[str] = field(default_factory=list)


def generate_roe(engagement_type: Dict, targets: List[str]) -> Dict:
    """Generate rules of engagement."""
    is_stealth = engagement_type.get("stealth", False)

    return {
        "authorization": "Written authorization required from asset owner before engagement begins.",
        "scope": f"Testing limited to: {', '.join(targets)}",
        "out_of_scope": [
            "Production data modification or deletion",
            "Denial of service attacks",
            "Physical security testing (unless explicitly authorized)",
            "Social engineering of non-consenting individuals",
            "Third-party systems or infrastructure",
        ],
        "testing_windows": {
            "primary": "Business hours (9am-6pm) unless stealth testing requires off-hours",
            "maintenance_window": "For high-risk tests: Saturday 2am-6am with on-call support",
            "blackout_periods": "No testing during: month-end processing, major releases, holidays",
        },
        "stealth_rules": {
            "stealth_required": is_stealth,
            "notification": "Blue team NOT notified" if is_stealth else "Blue team notified of testing",
            "detection_response": "If detected, testers will pause and coordinate with engagement lead" if is_stealth else "N/A",
        },
        "communication": {
            "daily_standup": not is_stealth,
            "critical_finding_notification": "Within 1 hour of discovery",
            "emergency_contact": "Security team on-call: [FILL IN]",
            "escalation_path": "Tester -> Engagement Lead -> CISO -> CTO",
        },
        "data_handling": {
            "credentials_found": "Log hash only, do not store plaintext",
            "sensitive_data": "Document existence, do not exfiltrate actual data",
            "evidence_retention": "Encrypted storage, destroyed 90 days after final report",
            "pii_handling": "No PII in reports, use anonymized references",
        },
        "prohibited_actions": [
            "Accessing systems outside defined scope",
            "Modifying production data",
            "Installing persistent backdoors without explicit approval",
            "Sharing findings with unauthorized parties",
            "Using zero-day exploits without prior approval",
            "Conducting denial of service attacks",
        ],
    }


def generate_phases(engagement_type: Dict, duration_days: int,
                    start_date: datetime) -> List[Dict]:
    """Generate phase breakdown with timeline."""
    phase_names = engagement_type["default_phases"]
    phases = []

    # Normalize percentages
    total_pct = sum(PHASE_DETAILS.get(p, {"pct": 10})["pct"] for p in phase_names)
    current_date = start_date

    for phase_name in phase_names:
        details = PHASE_DETAILS.get(phase_name, {"pct": 10, "desc": phase_name})
        pct = details["pct"] / total_pct
        phase_days = max(1, round(duration_days * pct))

        end_date = current_date + timedelta(days=phase_days)

        phases.append({
            "name": phase_name.replace("-", " ").title(),
            "duration_days": phase_days,
            "start": current_date.strftime("%Y-%m-%d"),
            "end": end_date.strftime("%Y-%m-%d"),
            "description": details["desc"],
            "allocation_pct": round(pct * 100),
        })

        current_date = end_date

    return phases


def generate_deliverables(engagement_type_key: str) -> List[str]:
    """Generate deliverables checklist."""
    base = [
        "Executive summary (1-2 pages, non-technical)",
        "Methodology description and scope confirmation",
        "Finding inventory with CVSS severity ratings",
        "Detailed finding descriptions with evidence",
        "Remediation recommendations (prioritized)",
        "Re-test plan and timeline",
    ]

    if engagement_type_key == "red-team":
        base.extend([
            "Attack narrative / kill chain documentation",
            "Detection gap analysis",
            "MITRE ATT&CK technique mapping",
            "Recommendations for detection improvements",
        ])
    elif engagement_type_key == "purple-team":
        base.extend([
            "Detection coverage matrix",
            "Alert tuning recommendations",
            "Updated detection rules/signatures",
            "Response procedure improvements",
        ])
    elif engagement_type_key == "app-security":
        base.extend([
            "OWASP Top 10 mapping",
            "API-specific findings (if applicable)",
            "Secure coding recommendations",
        ])

    base.append("Raw data and tool output appendix (encrypted)")
    return base


def plan_engagement(engagement_type_key: str, target_list: List[str],
                    duration_str: str, compliance_key: Optional[str] = None) -> EngagementPlan:
    """Generate a complete engagement plan."""
    eng_type = ENGAGEMENT_TYPES.get(engagement_type_key, ENGAGEMENT_TYPES["pentest"])
    duration_days = parse_duration(duration_str)
    start = datetime.now() + timedelta(days=7)  # 1 week lead time

    # Collect methodologies and tools from targets
    methodologies = set()
    tools = set()
    categories = []
    for target in target_list:
        t = target.lower().replace(" ", "-")
        if t in TARGET_TYPES:
            info = TARGET_TYPES[t]
            methodologies.add(info["methodology"])
            tools.update(info["tools_suggested"])
            categories.extend(info["test_categories"])

    if not methodologies:
        methodologies.add("PTES (Penetration Testing Execution Standard)")

    phases = generate_phases(eng_type, duration_days, start)
    roe = generate_roe(eng_type, target_list)
    deliverables = generate_deliverables(engagement_type_key)

    end_date = start + timedelta(days=duration_days)

    plan = EngagementPlan(
        engagement_type=eng_type["name"],
        engagement_name=f"{eng_type['name']} - {', '.join(target_list)}",
        description=eng_type["description"],
        targets=target_list,
        duration_days=duration_days,
        start_date=start.strftime("%Y-%m-%d"),
        end_date=end_date.strftime("%Y-%m-%d"),
        methodology=sorted(methodologies),
        phases=phases,
        rules_of_engagement=roe,
        deliverables=deliverables,
        tools_suggested=sorted(tools),
        test_categories=categories,
    )

    if compliance_key and compliance_key in COMPLIANCE_MAPPINGS:
        plan.compliance = COMPLIANCE_MAPPINGS[compliance_key]

    # Add risk notes
    if duration_days < 5:
        plan.risk_notes.append("Very short engagement. Coverage will be limited. Prioritize critical areas.")
    if len(target_list) > 3:
        plan.risk_notes.append("Multiple target types. Consider phased approach or additional resources.")
    if engagement_type_key == "red-team" and duration_days < 10:
        plan.risk_notes.append("Red team engagements typically require 2+ weeks for meaningful results.")

    return plan


def format_human(plan: EngagementPlan) -> str:
    """Format for human reading."""
    lines = []
    lines.append("=" * 70)
    lines.append(f"ENGAGEMENT PLAN: {plan.engagement_name}")
    lines.append("=" * 70)
    lines.append(f"Type: {plan.engagement_type}")
    lines.append(f"Description: {plan.description}")
    lines.append(f"Targets: {', '.join(plan.targets)}")
    lines.append(f"Duration: {plan.duration_days} business days ({plan.start_date} to {plan.end_date})")
    lines.append(f"Methodology: {', '.join(plan.methodology)}")
    lines.append("")

    if plan.risk_notes:
        lines.append("Risk Notes:")
        for note in plan.risk_notes:
            lines.append(f"  ! {note}")
        lines.append("")

    if plan.compliance:
        lines.append(f"Compliance: {plan.compliance['name']}")
        lines.append(f"  Scope: {plan.compliance['scope_notes']}")
        lines.append("  Requirements:")
        for req in plan.compliance["requirements"]:
            lines.append(f"    - {req}")
        lines.append("")

    lines.append("PHASES:")
    lines.append("-" * 60)
    for p in plan.phases:
        lines.append(f"  {p['name']} ({p['duration_days']}d, {p['allocation_pct']}%)")
        lines.append(f"    {p['start']} to {p['end']}")
        lines.append(f"    {p['description']}")
    lines.append("")

    lines.append("RULES OF ENGAGEMENT:")
    lines.append("-" * 60)
    roe = plan.rules_of_engagement
    lines.append(f"  Authorization: {roe['authorization']}")
    lines.append(f"  Scope: {roe['scope']}")
    lines.append(f"  Stealth: {'Yes' if roe['stealth_rules']['stealth_required'] else 'No'}")
    lines.append("  Out of Scope:")
    for item in roe["out_of_scope"]:
        lines.append(f"    - {item}")
    lines.append("  Prohibited Actions:")
    for item in roe["prohibited_actions"]:
        lines.append(f"    - {item}")
    lines.append("")

    lines.append("TEST CATEGORIES:")
    for cat in plan.test_categories:
        lines.append(f"  [ ] {cat}")
    lines.append("")

    if plan.tools_suggested:
        lines.append(f"Suggested Tools: {', '.join(plan.tools_suggested)}")
        lines.append("")

    lines.append("DELIVERABLES:")
    for d in plan.deliverables:
        lines.append(f"  [ ] {d}")

    lines.append("\n" + "=" * 70)
    return "\n".join(lines)


def format_json(plan: EngagementPlan) -> str:
    """Format as JSON."""
    return json.dumps(asdict(plan), indent=2)


def main():
    parser = argparse.ArgumentParser(
        description="Engagement Planner - Plan red team and penetration testing engagements"
    )
    parser.add_argument("--type", required=True, choices=list(ENGAGEMENT_TYPES.keys()),
                        help="Engagement type")
    parser.add_argument("--target", required=True,
                        help="Comma-separated targets: web-application,network,api,cloud,full-org")
    parser.add_argument("--duration", default="2w",
                        help="Duration (e.g., 2w, 10d, 1m). Default: 2w")
    parser.add_argument("--compliance", choices=list(COMPLIANCE_MAPPINGS.keys()),
                        help="Compliance framework to map against")
    parser.add_argument("--output", help="Write plan to file")
    parser.add_argument("--format", choices=["human", "json"], default="human",
                        help="Output format (default: human)")

    args = parser.parse_args()

    targets = [t.strip() for t in args.target.split(",")]
    plan = plan_engagement(args.type, targets, args.duration, args.compliance)

    if args.format == "json":
        output = format_json(plan)
    else:
        output = format_human(plan)

    if args.output:
        Path(args.output).write_text(output)
        print(f"Plan written to: {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
