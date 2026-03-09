#!/usr/bin/env python3
"""
NIST CSF 2.0 Maturity Assessor

Assesses organizational cybersecurity maturity across all six NIST CSF 2.0
functions. Generates current profile vs target profile gap analysis with
prioritized remediation recommendations.

Usage:
    python csf_maturity_assessor.py --input assessment.json --target-tier 3 --output report.json
    python csf_maturity_assessor.py --input assessment.json --target-tier 4 --format markdown --output report.md
    python csf_maturity_assessor.py --input assessment.json --functions GOVERN,IDENTIFY --target-tier 3 --output report.json
"""

import argparse
import json
import sys
from datetime import datetime
from typing import Any

# ---------------------------------------------------------------------------
# NIST CSF 2.0 Taxonomy
# ---------------------------------------------------------------------------

CSF_TAXONOMY: dict[str, dict[str, dict[str, str]]] = {
    "GOVERN": {
        "GV.OC": {
            "name": "Organizational Context",
            "description": "Mission, stakeholder expectations, legal/regulatory requirements, risk appetite",
        },
        "GV.RM": {
            "name": "Risk Management Strategy",
            "description": "Risk tolerance, risk statements, strategic alignment",
        },
        "GV.RR": {
            "name": "Roles, Responsibilities, and Authorities",
            "description": "Leadership accountability, CISO role, authority delegation",
        },
        "GV.PO": {
            "name": "Policy",
            "description": "Cybersecurity policy framework, update cadence, enforcement",
        },
        "GV.OV": {
            "name": "Oversight",
            "description": "Board reporting, metrics, performance review",
        },
        "GV.SC": {
            "name": "Cybersecurity Supply Chain Risk Management",
            "description": "Supplier requirements, C-SCRM policies, SBOM",
        },
    },
    "IDENTIFY": {
        "ID.AM": {
            "name": "Asset Management",
            "description": "Hardware, software, data, systems inventory",
        },
        "ID.RA": {
            "name": "Risk Assessment",
            "description": "Vulnerability identification, threat intelligence, risk analysis",
        },
        "ID.IM": {
            "name": "Improvement",
            "description": "Lessons learned, continuous improvement tracking",
        },
    },
    "PROTECT": {
        "PR.AA": {
            "name": "Identity Management, Authentication, and Access Control",
            "description": "MFA, FIDO2, SSO, PAM, zero trust, least privilege",
        },
        "PR.AT": {
            "name": "Awareness and Training",
            "description": "Role-based training, phishing simulation, developer training",
        },
        "PR.DS": {
            "name": "Data Security",
            "description": "Encryption at rest/transit, DLP, data classification",
        },
        "PR.PS": {
            "name": "Platform Security",
            "description": "Hardening, patch management, configuration management",
        },
        "PR.IR": {
            "name": "Technology Infrastructure Resilience",
            "description": "Redundancy, failover, capacity planning, DR",
        },
    },
    "DETECT": {
        "DE.CM": {
            "name": "Continuous Monitoring",
            "description": "SIEM, IDS/IPS, EDR, network monitoring, SOC",
        },
        "DE.AE": {
            "name": "Adverse Event Analysis",
            "description": "Correlation, anomaly detection, threat hunting",
        },
    },
    "RESPOND": {
        "RS.MA": {
            "name": "Incident Management",
            "description": "IR plan, escalation, containment procedures",
        },
        "RS.AN": {
            "name": "Incident Analysis",
            "description": "Forensics, root cause analysis, impact assessment",
        },
        "RS.CO": {
            "name": "Incident Response Reporting and Communication",
            "description": "Stakeholder notification, regulatory reporting",
        },
        "RS.MI": {
            "name": "Incident Mitigation",
            "description": "Containment, eradication, recovery initiation",
        },
    },
    "RECOVER": {
        "RC.RP": {
            "name": "Incident Recovery Plan Execution",
            "description": "Recovery procedures, prioritization, validation",
        },
        "RC.CO": {
            "name": "Incident Recovery Communication",
            "description": "Public communications, reputation management",
        },
    },
}

TIER_NAMES = {
    1: "Partial",
    2: "Risk Informed",
    3: "Repeatable",
    4: "Adaptive",
}

# ---------------------------------------------------------------------------
# Remediation recommendations per category per gap severity
# ---------------------------------------------------------------------------

REMEDIATION_GUIDANCE: dict[str, dict[str, Any]] = {
    "GV.OC": {
        "priority": "HIGH",
        "effort": "Medium",
        "recommendations": [
            "Document organizational mission and cybersecurity alignment",
            "Create regulatory obligations register with quarterly review cadence",
            "Conduct stakeholder mapping exercise to identify cybersecurity interests",
            "Define and document risk appetite and tolerance statements",
        ],
    },
    "GV.RM": {
        "priority": "HIGH",
        "effort": "Medium",
        "recommendations": [
            "Establish formal risk management strategy approved by leadership",
            "Define quantitative risk tolerance thresholds per asset class",
            "Integrate cybersecurity risk into enterprise risk management",
            "Implement quarterly risk posture reporting to the board",
        ],
    },
    "GV.RR": {
        "priority": "HIGH",
        "effort": "Low",
        "recommendations": [
            "Define CISO role with direct report to CEO or board",
            "Create RACI matrix for all cybersecurity functions",
            "Include cybersecurity objectives in executive performance reviews",
            "Establish cybersecurity steering committee with cross-functional representation",
        ],
    },
    "GV.PO": {
        "priority": "HIGH",
        "effort": "Medium",
        "recommendations": [
            "Develop hierarchical policy framework (Policy > Standard > Procedure > Guideline)",
            "Establish annual policy review and update cycle",
            "Implement automated policy distribution and acknowledgment tracking",
            "Create exception management process for policy deviations",
        ],
    },
    "GV.OV": {
        "priority": "MEDIUM",
        "effort": "Medium",
        "recommendations": [
            "Define KPIs and KRIs for cybersecurity program performance",
            "Establish quarterly board reporting cadence with standardized metrics",
            "Implement management review process for cybersecurity program",
            "Track MTTD, MTTR, vulnerability remediation, and training metrics",
        ],
    },
    "GV.SC": {
        "priority": "HIGH",
        "effort": "High",
        "recommendations": [
            "Tier suppliers by criticality and data access level",
            "Require SOC 2 Type II or equivalent from critical suppliers",
            "Include cybersecurity requirements and right-to-audit in contracts",
            "Implement SBOM requirements for critical software suppliers",
            "Monitor supplier breach disclosures and vulnerability announcements",
        ],
    },
    "ID.AM": {
        "priority": "HIGH",
        "effort": "Medium",
        "recommendations": [
            "Deploy automated asset discovery (agent-based and network scanning)",
            "Establish and maintain CMDB with owner, criticality, and classification tags",
            "Conduct quarterly asset reconciliation and shadow IT discovery",
            "Map data flows between systems, networks, and external parties",
        ],
    },
    "ID.RA": {
        "priority": "HIGH",
        "effort": "Medium",
        "recommendations": [
            "Adopt standardized risk assessment methodology (NIST 800-30 or FAIR)",
            "Maintain risk register with assigned owners and treatment plans",
            "Integrate threat intelligence feeds into risk assessment process",
            "Conduct risk assessments for new systems and major changes",
        ],
    },
    "ID.IM": {
        "priority": "MEDIUM",
        "effort": "Low",
        "recommendations": [
            "Schedule blameless post-mortems within 2 weeks of incidents",
            "Maintain improvement action tracker with deadlines and owners",
            "Conduct annual program maturity benchmarking",
            "Participate in industry information sharing organizations",
        ],
    },
    "PR.AA": {
        "priority": "CRITICAL",
        "effort": "High",
        "recommendations": [
            "Deploy MFA for all users, FIDO2/hardware keys for privileged access",
            "Implement PAM with session recording and credential vaulting",
            "Adopt zero trust architecture with network micro-segmentation",
            "Automate user provisioning/deprovisioning tied to HR systems",
            "Conduct monthly privileged access reviews, quarterly for standard access",
        ],
    },
    "PR.AT": {
        "priority": "MEDIUM",
        "effort": "Low",
        "recommendations": [
            "Implement annual security awareness training for all personnel",
            "Conduct quarterly phishing simulations with progressive difficulty",
            "Provide secure coding training for developers (OWASP Top 10)",
            "Deliver role-based training for executives, IT admins, and general staff",
        ],
    },
    "PR.DS": {
        "priority": "CRITICAL",
        "effort": "High",
        "recommendations": [
            "Encrypt all data at rest (AES-256) and in transit (TLS 1.2+)",
            "Deploy endpoint, network, and cloud DLP solutions",
            "Implement data classification taxonomy and automate labeling",
            "Manage encryption keys using HSM or cloud KMS with annual rotation",
        ],
    },
    "PR.PS": {
        "priority": "HIGH",
        "effort": "Medium",
        "recommendations": [
            "Apply CIS Benchmarks Level 1+ across all systems",
            "Establish patch SLAs: critical 72h, high 30d, medium 90d",
            "Deploy configuration management and drift detection tools",
            "Maintain golden images for standard deployments",
        ],
    },
    "PR.IR": {
        "priority": "HIGH",
        "effort": "High",
        "recommendations": [
            "Define RPO/RTO for each critical system",
            "Implement redundancy and failover for Tier 1 systems",
            "Maintain 3-2-1 backup strategy and test restores quarterly",
            "Conduct annual disaster recovery exercises",
        ],
    },
    "DE.CM": {
        "priority": "CRITICAL",
        "effort": "High",
        "recommendations": [
            "Deploy SIEM with centralized log collection from all critical systems",
            "Implement EDR/XDR on all endpoints",
            "Establish SOC (internal or managed) with 24/7 coverage for Tier 1 assets",
            "Deploy UEBA for behavioral anomaly detection",
            "Retain logs minimum 1 year (90 days hot storage)",
        ],
    },
    "DE.AE": {
        "priority": "HIGH",
        "effort": "Medium",
        "recommendations": [
            "Map detection rules to MITRE ATT&CK techniques",
            "Conduct monthly threat hunting exercises",
            "Implement SOAR for automated alert triage",
            "Track detection efficacy metrics (true positive rate, MTTD)",
        ],
    },
    "RS.MA": {
        "priority": "CRITICAL",
        "effort": "Medium",
        "recommendations": [
            "Develop and maintain incident response plan tested annually",
            "Define incident severity classification (P1-P4) with response SLAs",
            "Maintain on-call rotation for incident response team",
            "Conduct quarterly tabletop exercises and annual full simulations",
        ],
    },
    "RS.AN": {
        "priority": "HIGH",
        "effort": "Medium",
        "recommendations": [
            "Maintain forensic toolkit and trained forensic analysts",
            "Establish evidence preservation procedures with chain of custody",
            "Document root cause analysis methodology",
            "Maintain relationships with external forensic firms and law enforcement",
        ],
    },
    "RS.CO": {
        "priority": "HIGH",
        "effort": "Low",
        "recommendations": [
            "Pre-draft notification templates for common incident types",
            "Document regulatory notification timelines (GDPR 72h, HIPAA 60d, etc.)",
            "Designate single point of communication per incident",
            "Have legal counsel review all external communication templates",
        ],
    },
    "RS.MI": {
        "priority": "CRITICAL",
        "effort": "Medium",
        "recommendations": [
            "Pre-define containment strategies for common attack types",
            "Maintain containment playbooks for ransomware, data breach, insider threat",
            "Validate eradication of all persistence mechanisms before recovery",
            "Monitor compromised systems for 90 days post-incident",
        ],
    },
    "RC.RP": {
        "priority": "HIGH",
        "effort": "High",
        "recommendations": [
            "Prioritize recovery by system criticality tier",
            "Verify backup integrity before restore operations",
            "Rebuild from golden images rather than cleaning compromised systems",
            "Obtain business owner sign-off before declaring recovery complete",
        ],
    },
    "RC.CO": {
        "priority": "MEDIUM",
        "effort": "Low",
        "recommendations": [
            "Establish recovery communication cadence per severity level",
            "Prepare customer-facing FAQ templates for significant incidents",
            "Issue post-incident summary within 30 days",
            "Communicate corrective actions taken to rebuild stakeholder trust",
        ],
    },
}


def load_assessment(path: str) -> dict:
    """Load assessment data from a JSON file."""
    try:
        with open(path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Assessment file not found: {path}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in assessment file: {e}", file=sys.stderr)
        sys.exit(1)


def validate_assessment(data: dict) -> list[str]:
    """Validate assessment data structure and return any warnings."""
    warnings: list[str] = []
    functions_data = data.get("functions", {})

    for func_name, categories in CSF_TAXONOMY.items():
        if func_name not in functions_data:
            warnings.append(f"Function {func_name} not found in assessment — will be scored as 0")
            continue
        for cat_id in categories:
            if cat_id not in functions_data.get(func_name, {}):
                warnings.append(f"Category {cat_id} not found in assessment — will be scored as 0")

    for func_name, func_data in functions_data.items():
        if func_name not in CSF_TAXONOMY:
            warnings.append(f"Unknown function in assessment: {func_name}")
            continue
        for cat_id, cat_data in func_data.items():
            if cat_id not in CSF_TAXONOMY[func_name]:
                warnings.append(f"Unknown category in assessment: {cat_id}")
                continue
            score = cat_data.get("score", 0)
            if not isinstance(score, (int, float)) or score < 0 or score > 4:
                warnings.append(f"Invalid score for {cat_id}: {score} (must be 0-4)")

    return warnings


def assess_maturity(
    data: dict, target_tier: int, filter_functions: list[str] | None = None
) -> dict:
    """Perform maturity assessment and gap analysis."""
    functions_data = data.get("functions", {})
    results: dict[str, Any] = {
        "metadata": {
            "organization": data.get("organization", "Unknown"),
            "assessment_date": data.get("assessment_date", datetime.now().strftime("%Y-%m-%d")),
            "assessor": data.get("assessor", "Unknown"),
            "target_tier": target_tier,
            "target_tier_name": TIER_NAMES.get(target_tier, "Unknown"),
            "report_generated": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        },
        "summary": {},
        "functions": {},
        "gaps": [],
        "remediation_plan": [],
    }

    total_score = 0.0
    total_categories = 0
    function_scores: dict[str, dict[str, Any]] = {}

    for func_name, categories in CSF_TAXONOMY.items():
        if filter_functions and func_name not in filter_functions:
            continue

        func_total = 0.0
        func_count = 0
        category_results: dict[str, Any] = {}

        for cat_id, cat_info in categories.items():
            cat_data = functions_data.get(func_name, {}).get(cat_id, {})
            score = cat_data.get("score", 0)
            evidence = cat_data.get("evidence", "No evidence provided")
            notes = cat_data.get("notes", "")

            gap = max(0, target_tier - score)
            gap_severity = _classify_gap(gap)

            category_results[cat_id] = {
                "name": cat_info["name"],
                "description": cat_info["description"],
                "current_score": score,
                "current_tier": TIER_NAMES.get(int(score), "Not Assessed") if score > 0 else "Not Assessed",
                "target_tier": target_tier,
                "gap": gap,
                "gap_severity": gap_severity,
                "evidence": evidence,
                "notes": notes,
            }

            if gap > 0:
                guidance = REMEDIATION_GUIDANCE.get(cat_id, {})
                gap_entry = {
                    "category": cat_id,
                    "category_name": cat_info["name"],
                    "function": func_name,
                    "current_score": score,
                    "target_tier": target_tier,
                    "gap": gap,
                    "gap_severity": gap_severity,
                    "priority": guidance.get("priority", "MEDIUM"),
                    "effort": guidance.get("effort", "Medium"),
                    "recommendations": guidance.get("recommendations", []),
                }
                results["gaps"].append(gap_entry)

            func_total += score
            func_count += 1
            total_score += score
            total_categories += 1

        avg_score = round(func_total / func_count, 2) if func_count > 0 else 0
        function_scores[func_name] = {
            "average_score": avg_score,
            "average_tier": TIER_NAMES.get(round(avg_score), "Not Assessed"),
            "categories_assessed": func_count,
            "categories_at_target": sum(
                1 for c in category_results.values() if c["gap"] == 0
            ),
            "categories_below_target": sum(
                1 for c in category_results.values() if c["gap"] > 0
            ),
            "categories": category_results,
        }

    results["functions"] = function_scores

    # Summary
    overall_avg = round(total_score / total_categories, 2) if total_categories > 0 else 0
    results["summary"] = {
        "overall_average_score": overall_avg,
        "overall_tier": TIER_NAMES.get(round(overall_avg), "Not Assessed"),
        "target_tier": target_tier,
        "target_tier_name": TIER_NAMES.get(target_tier, "Unknown"),
        "total_categories_assessed": total_categories,
        "categories_at_target": sum(
            f["categories_at_target"] for f in function_scores.values()
        ),
        "categories_below_target": sum(
            f["categories_below_target"] for f in function_scores.values()
        ),
        "total_gaps": len(results["gaps"]),
        "critical_gaps": sum(1 for g in results["gaps"] if g["gap_severity"] == "CRITICAL"),
        "high_gaps": sum(1 for g in results["gaps"] if g["gap_severity"] == "HIGH"),
        "medium_gaps": sum(1 for g in results["gaps"] if g["gap_severity"] == "MEDIUM"),
        "low_gaps": sum(1 for g in results["gaps"] if g["gap_severity"] == "LOW"),
    }

    # Sort gaps by priority for remediation plan
    priority_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
    sorted_gaps = sorted(results["gaps"], key=lambda g: (priority_order.get(g["priority"], 4), -g["gap"]))
    results["remediation_plan"] = _build_remediation_plan(sorted_gaps)
    results["gaps"] = sorted_gaps

    return results


def _classify_gap(gap: int) -> str:
    """Classify gap severity."""
    if gap >= 3:
        return "CRITICAL"
    elif gap == 2:
        return "HIGH"
    elif gap == 1:
        return "MEDIUM"
    return "LOW"


def _build_remediation_plan(sorted_gaps: list[dict]) -> list[dict]:
    """Build phased remediation plan from sorted gaps."""
    phases: list[dict] = []

    # Phase 1: Critical and high-priority items
    phase1_items = [g for g in sorted_gaps if g["priority"] in ("CRITICAL",) and g["gap"] >= 2]
    if phase1_items:
        phases.append({
            "phase": 1,
            "name": "Immediate — Critical Gap Remediation",
            "timeline": "Months 1-3",
            "items": [
                {
                    "category": g["category"],
                    "category_name": g["category_name"],
                    "current_score": g["current_score"],
                    "target": g["target_tier"],
                    "recommendations": g["recommendations"],
                }
                for g in phase1_items
            ],
        })

    # Phase 2: High-priority items
    phase2_items = [g for g in sorted_gaps if g["priority"] == "HIGH" or (g["priority"] == "CRITICAL" and g["gap"] == 1)]
    if phase2_items:
        phases.append({
            "phase": 2,
            "name": "Short-Term — High Priority Improvements",
            "timeline": "Months 4-6",
            "items": [
                {
                    "category": g["category"],
                    "category_name": g["category_name"],
                    "current_score": g["current_score"],
                    "target": g["target_tier"],
                    "recommendations": g["recommendations"],
                }
                for g in phase2_items
            ],
        })

    # Phase 3: Medium and low priority
    phase3_items = [g for g in sorted_gaps if g["priority"] in ("MEDIUM", "LOW")]
    if phase3_items:
        phases.append({
            "phase": 3,
            "name": "Medium-Term — Maturity Enhancement",
            "timeline": "Months 7-12",
            "items": [
                {
                    "category": g["category"],
                    "category_name": g["category_name"],
                    "current_score": g["current_score"],
                    "target": g["target_tier"],
                    "recommendations": g["recommendations"],
                }
                for g in phase3_items
            ],
        })

    return phases


def format_markdown(results: dict) -> str:
    """Format assessment results as Markdown."""
    lines: list[str] = []
    meta = results["metadata"]
    summary = results["summary"]

    lines.append(f"# NIST CSF 2.0 Maturity Assessment Report")
    lines.append("")
    lines.append(f"**Organization:** {meta['organization']}")
    lines.append(f"**Assessment Date:** {meta['assessment_date']}")
    lines.append(f"**Assessor:** {meta['assessor']}")
    lines.append(f"**Target Tier:** {meta['target_tier']} — {meta['target_tier_name']}")
    lines.append(f"**Report Generated:** {meta['report_generated']}")
    lines.append("")

    # Executive Summary
    lines.append("## Executive Summary")
    lines.append("")
    lines.append(f"| Metric | Value |")
    lines.append(f"|--------|-------|")
    lines.append(f"| Overall Average Score | {summary['overall_average_score']} ({summary['overall_tier']}) |")
    lines.append(f"| Target Tier | {summary['target_tier']} ({summary['target_tier_name']}) |")
    lines.append(f"| Categories Assessed | {summary['total_categories_assessed']} |")
    lines.append(f"| At Target | {summary['categories_at_target']} |")
    lines.append(f"| Below Target | {summary['categories_below_target']} |")
    lines.append(f"| Critical Gaps | {summary['critical_gaps']} |")
    lines.append(f"| High Gaps | {summary['high_gaps']} |")
    lines.append(f"| Medium Gaps | {summary['medium_gaps']} |")
    lines.append("")

    # Function Scores
    lines.append("## Function Scores")
    lines.append("")
    lines.append("| Function | Avg Score | Tier | At Target | Below Target |")
    lines.append("|----------|-----------|------|-----------|-------------|")
    for func_name, func_data in results["functions"].items():
        lines.append(
            f"| {func_name} | {func_data['average_score']} | "
            f"{func_data['average_tier']} | {func_data['categories_at_target']} | "
            f"{func_data['categories_below_target']} |"
        )
    lines.append("")

    # Detailed Category Scores
    lines.append("## Detailed Category Scores")
    lines.append("")
    for func_name, func_data in results["functions"].items():
        lines.append(f"### {func_name}")
        lines.append("")
        lines.append("| Category | Name | Score | Gap | Severity |")
        lines.append("|----------|------|-------|-----|----------|")
        for cat_id, cat_data in func_data["categories"].items():
            lines.append(
                f"| {cat_id} | {cat_data['name']} | {cat_data['current_score']} | "
                f"{cat_data['gap']} | {cat_data['gap_severity']} |"
            )
        lines.append("")

    # Gap Analysis
    if results["gaps"]:
        lines.append("## Gap Analysis — Prioritized")
        lines.append("")
        for gap in results["gaps"]:
            lines.append(f"### {gap['category']} — {gap['category_name']}")
            lines.append("")
            lines.append(f"- **Function:** {gap['function']}")
            lines.append(f"- **Current Score:** {gap['current_score']}")
            lines.append(f"- **Target:** {gap['target_tier']}")
            lines.append(f"- **Gap:** {gap['gap']} ({gap['gap_severity']})")
            lines.append(f"- **Priority:** {gap['priority']}")
            lines.append(f"- **Effort:** {gap['effort']}")
            lines.append(f"- **Recommendations:**")
            for rec in gap["recommendations"]:
                lines.append(f"  - {rec}")
            lines.append("")

    # Remediation Plan
    if results["remediation_plan"]:
        lines.append("## Remediation Roadmap")
        lines.append("")
        for phase in results["remediation_plan"]:
            lines.append(f"### Phase {phase['phase']}: {phase['name']} ({phase['timeline']})")
            lines.append("")
            for item in phase["items"]:
                lines.append(f"**{item['category']} — {item['category_name']}** (Current: {item['current_score']}, Target: {item['target']})")
                for rec in item["recommendations"]:
                    lines.append(f"- {rec}")
                lines.append("")

    return "\n".join(lines)


def write_output(results: dict, output_path: str | None, fmt: str) -> None:
    """Write results to file or stdout."""
    if fmt == "markdown":
        content = format_markdown(results)
    else:
        content = json.dumps(results, indent=2)

    if output_path:
        with open(output_path, "w") as f:
            f.write(content)
        print(f"Report written to {output_path}", file=sys.stderr)
    else:
        print(content)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="NIST CSF 2.0 Maturity Assessor — assess cybersecurity maturity and generate gap analysis"
    )
    parser.add_argument(
        "--input", "-i", required=True,
        help="Path to assessment JSON file"
    )
    parser.add_argument(
        "--target-tier", "-t", type=int, required=True, choices=[1, 2, 3, 4],
        help="Target maturity tier (1=Partial, 2=Risk Informed, 3=Repeatable, 4=Adaptive)"
    )
    parser.add_argument(
        "--output", "-o",
        help="Output file path (stdout if not specified)"
    )
    parser.add_argument(
        "--format", "-f", choices=["json", "markdown"], default="json",
        help="Output format (default: json)"
    )
    parser.add_argument(
        "--functions",
        help="Comma-separated list of functions to assess (e.g., GOVERN,IDENTIFY,PROTECT)"
    )

    args = parser.parse_args()

    # Load and validate
    data = load_assessment(args.input)
    warnings = validate_assessment(data)
    for w in warnings:
        print(f"Warning: {w}", file=sys.stderr)

    # Parse function filter
    filter_functions = None
    if args.functions:
        filter_functions = [f.strip().upper() for f in args.functions.split(",")]
        invalid = [f for f in filter_functions if f not in CSF_TAXONOMY]
        if invalid:
            print(f"Error: Unknown functions: {', '.join(invalid)}", file=sys.stderr)
            print(f"Valid functions: {', '.join(CSF_TAXONOMY.keys())}", file=sys.stderr)
            sys.exit(1)

    # Assess
    results = assess_maturity(data, args.target_tier, filter_functions)

    # Output
    write_output(results, args.output, args.format)


if __name__ == "__main__":
    main()
