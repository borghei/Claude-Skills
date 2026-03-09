#!/usr/bin/env python3
"""
NIST CSF 2.0 Control Mapper

Maps NIST CSF 2.0 categories to other compliance frameworks including
ISO 27001:2022, SOC 2 TSC, HIPAA Security Rule, and PCI-DSS v4.0.
Generates unified control matrices for multi-framework compliance programs.

Usage:
    python csf_control_mapper.py --source-framework nist-csf --target-framework iso27001 --output mapping.json
    python csf_control_mapper.py --source-framework nist-csf --target-framework all --output unified.json
    python csf_control_mapper.py --source-framework nist-csf --target-framework soc2 --functions GOVERN,PROTECT --format markdown --output report.md
"""

import argparse
import json
import sys
from datetime import datetime
from typing import Any

# ---------------------------------------------------------------------------
# Cross-framework mapping database
# ---------------------------------------------------------------------------

FRAMEWORK_NAMES = {
    "nist-csf": "NIST CSF 2.0",
    "iso27001": "ISO 27001:2022",
    "soc2": "SOC 2 Type II",
    "hipaa": "HIPAA Security Rule",
    "pci-dss": "PCI-DSS v4.0",
}

# Each CSF category maps to controls in target frameworks
CONTROL_MAPPINGS: dict[str, dict[str, Any]] = {
    "GV.OC": {
        "name": "Organizational Context",
        "function": "GOVERN",
        "iso27001": {
            "controls": ["A.5.1", "A.5.2", "A.5.4"],
            "description": "Information security policies, Organizational roles and responsibilities, Management responsibilities",
        },
        "soc2": {
            "controls": ["CC1.1", "CC1.2", "CC1.3"],
            "description": "Control environment — integrity, ethics, board oversight, organizational structure",
        },
        "hipaa": {
            "controls": ["164.308(a)(1)(i)", "164.308(a)(2)"],
            "description": "Security management process, Assigned security responsibility",
        },
        "pci-dss": {
            "controls": ["12.1", "12.1.1", "12.1.2"],
            "description": "Information security policy, roles and responsibilities",
        },
    },
    "GV.RM": {
        "name": "Risk Management Strategy",
        "function": "GOVERN",
        "iso27001": {
            "controls": ["A.5.3", "6.1", "6.1.2"],
            "description": "Segregation of duties, Actions to address risks, Information security risk assessment",
        },
        "soc2": {
            "controls": ["CC3.1", "CC3.2", "CC3.3"],
            "description": "Risk assessment — objectives, risk identification, risk analysis",
        },
        "hipaa": {
            "controls": ["164.308(a)(1)(ii)(A)", "164.308(a)(1)(ii)(B)"],
            "description": "Risk analysis, Risk management",
        },
        "pci-dss": {
            "controls": ["12.3.1", "12.3.2"],
            "description": "Targeted risk analysis for customized approach, risk analysis for flexible requirements",
        },
    },
    "GV.RR": {
        "name": "Roles, Responsibilities, and Authorities",
        "function": "GOVERN",
        "iso27001": {
            "controls": ["A.5.2", "5.3"],
            "description": "Information security roles and responsibilities, Organizational roles",
        },
        "soc2": {
            "controls": ["CC1.3", "CC1.4"],
            "description": "Board oversight, Accountability structure",
        },
        "hipaa": {
            "controls": ["164.308(a)(2)"],
            "description": "Assigned security responsibility",
        },
        "pci-dss": {
            "controls": ["12.1.2", "12.4.1"],
            "description": "Roles and responsibilities, executive management responsibility",
        },
    },
    "GV.PO": {
        "name": "Policy",
        "function": "GOVERN",
        "iso27001": {
            "controls": ["A.5.1", "A.5.37"],
            "description": "Policies for information security, Documented operating procedures",
        },
        "soc2": {
            "controls": ["CC1.1", "CC5.2"],
            "description": "Control environment policies, Policies and procedures",
        },
        "hipaa": {
            "controls": ["164.316(a)", "164.316(b)"],
            "description": "Policies and procedures, Documentation requirements",
        },
        "pci-dss": {
            "controls": ["12.1", "12.1.1"],
            "description": "Information security policy establishment and maintenance",
        },
    },
    "GV.OV": {
        "name": "Oversight",
        "function": "GOVERN",
        "iso27001": {
            "controls": ["9.1", "9.2", "9.3"],
            "description": "Monitoring, measurement, analysis, Internal audit, Management review",
        },
        "soc2": {
            "controls": ["CC1.2", "CC4.1", "CC4.2"],
            "description": "Board oversight, Monitoring activities, Remediation",
        },
        "hipaa": {
            "controls": ["164.308(a)(1)(ii)(D)", "164.308(a)(8)"],
            "description": "Information system activity review, Evaluation",
        },
        "pci-dss": {
            "controls": ["12.4.2", "12.4.2.1"],
            "description": "Reviews of PCI DSS compliance, documented reviews",
        },
    },
    "GV.SC": {
        "name": "Cybersecurity Supply Chain Risk Management",
        "function": "GOVERN",
        "iso27001": {
            "controls": ["A.5.19", "A.5.20", "A.5.21", "A.5.22", "A.5.23"],
            "description": "Information security in supplier relationships, Supply chain management",
        },
        "soc2": {
            "controls": ["CC9.2"],
            "description": "Vendor and business partner risk management",
        },
        "hipaa": {
            "controls": ["164.308(b)(1)", "164.314(a)"],
            "description": "Business associate contracts, Organizational requirements",
        },
        "pci-dss": {
            "controls": ["12.8", "12.8.1", "12.8.2", "12.8.3", "12.8.4", "12.8.5"],
            "description": "Third-party service provider management",
        },
    },
    "ID.AM": {
        "name": "Asset Management",
        "function": "IDENTIFY",
        "iso27001": {
            "controls": ["A.5.9", "A.5.10", "A.5.11", "A.5.12", "A.5.13", "A.8.1"],
            "description": "Inventory of information assets, Acceptable use, Return of assets, Classification, Labeling, Asset management",
        },
        "soc2": {
            "controls": ["CC6.1"],
            "description": "Logical and physical access to information assets",
        },
        "hipaa": {
            "controls": ["164.310(d)(1)", "164.312(c)(1)"],
            "description": "Device and media controls, Integrity",
        },
        "pci-dss": {
            "controls": ["2.1", "2.2", "9.4", "12.5.1"],
            "description": "System inventory, Secure configurations, Media management, PCI DSS scope documentation",
        },
    },
    "ID.RA": {
        "name": "Risk Assessment",
        "function": "IDENTIFY",
        "iso27001": {
            "controls": ["A.5.7", "A.8.8", "6.1.2"],
            "description": "Threat intelligence, Technical vulnerability management, Risk assessment process",
        },
        "soc2": {
            "controls": ["CC3.1", "CC3.2", "CC3.3", "CC3.4"],
            "description": "Risk assessment — objectives, analysis, estimation, changes",
        },
        "hipaa": {
            "controls": ["164.308(a)(1)(ii)(A)"],
            "description": "Risk analysis",
        },
        "pci-dss": {
            "controls": ["6.3.1", "11.3", "12.3.1"],
            "description": "Vulnerability identification, Penetration testing, Targeted risk analysis",
        },
    },
    "ID.IM": {
        "name": "Improvement",
        "function": "IDENTIFY",
        "iso27001": {
            "controls": ["10.1", "10.2"],
            "description": "Continual improvement, Nonconformity and corrective action",
        },
        "soc2": {
            "controls": ["CC4.2"],
            "description": "Evaluation and remediation of deficiencies",
        },
        "hipaa": {
            "controls": ["164.308(a)(8)"],
            "description": "Evaluation",
        },
        "pci-dss": {
            "controls": ["12.3.3"],
            "description": "Review of cryptographic cipher suites and protocols",
        },
    },
    "PR.AA": {
        "name": "Identity Management, Authentication, and Access Control",
        "function": "PROTECT",
        "iso27001": {
            "controls": ["A.5.15", "A.5.16", "A.5.17", "A.5.18", "A.8.2", "A.8.3", "A.8.4", "A.8.5"],
            "description": "Access control, Identity management, Authentication, Access rights, Privileged access",
        },
        "soc2": {
            "controls": ["CC6.1", "CC6.2", "CC6.3"],
            "description": "Logical and physical access controls, Authentication, Authorization",
        },
        "hipaa": {
            "controls": ["164.312(a)(1)", "164.312(a)(2)(i)", "164.312(a)(2)(iii)", "164.312(d)"],
            "description": "Access control, Unique user identification, Automatic logoff, Person or entity authentication",
        },
        "pci-dss": {
            "controls": ["7.1", "7.2", "7.3", "8.1", "8.2", "8.3", "8.4", "8.5", "8.6"],
            "description": "Restrict access by business need-to-know, Identify and authenticate, MFA, password policies",
        },
    },
    "PR.AT": {
        "name": "Awareness and Training",
        "function": "PROTECT",
        "iso27001": {
            "controls": ["A.6.3", "7.2", "7.3"],
            "description": "Information security awareness training, Competence, Awareness",
        },
        "soc2": {
            "controls": ["CC1.4", "CC2.2"],
            "description": "Training and accountability, Internal communication",
        },
        "hipaa": {
            "controls": ["164.308(a)(5)"],
            "description": "Security awareness and training",
        },
        "pci-dss": {
            "controls": ["12.6", "12.6.1", "12.6.2", "12.6.3"],
            "description": "Security awareness program",
        },
    },
    "PR.DS": {
        "name": "Data Security",
        "function": "PROTECT",
        "iso27001": {
            "controls": ["A.8.10", "A.8.11", "A.8.12", "A.8.24", "A.8.25"],
            "description": "Information deletion, Data masking, Data leakage prevention, Cryptography, SDLC security",
        },
        "soc2": {
            "controls": ["CC6.1", "CC6.5", "CC6.7"],
            "description": "Data protection, Disposal, Encryption in transmission",
        },
        "hipaa": {
            "controls": ["164.312(a)(2)(iv)", "164.312(c)(1)", "164.312(e)(1)", "164.312(e)(2)(ii)"],
            "description": "Encryption/decryption, Integrity, Transmission security",
        },
        "pci-dss": {
            "controls": ["3.1", "3.2", "3.3", "3.4", "3.5", "3.6", "3.7", "4.1", "4.2"],
            "description": "Protect stored account data, Strong cryptography during transmission",
        },
    },
    "PR.PS": {
        "name": "Platform Security",
        "function": "PROTECT",
        "iso27001": {
            "controls": ["A.8.9", "A.8.19", "A.8.20"],
            "description": "Configuration management, Installation of software, Network security",
        },
        "soc2": {
            "controls": ["CC6.6", "CC6.8", "CC7.1"],
            "description": "System boundaries, Malware prevention, Infrastructure monitoring",
        },
        "hipaa": {
            "controls": ["164.310(a)(1)", "164.310(d)(1)"],
            "description": "Facility access controls, Device and media controls",
        },
        "pci-dss": {
            "controls": ["1.1", "1.2", "1.3", "1.4", "1.5", "2.1", "2.2", "2.3", "5.1", "5.2", "5.3", "5.4", "6.1", "6.2", "6.3"],
            "description": "Network security controls, Secure configurations, Malware protection, Secure development",
        },
    },
    "PR.IR": {
        "name": "Technology Infrastructure Resilience",
        "function": "PROTECT",
        "iso27001": {
            "controls": ["A.5.29", "A.5.30", "A.8.6", "A.8.14"],
            "description": "ICT readiness for business continuity, Capacity management, Redundancy",
        },
        "soc2": {
            "controls": ["A1.1", "A1.2", "A1.3"],
            "description": "Availability — capacity, recovery, environmental protection",
        },
        "hipaa": {
            "controls": ["164.308(a)(7)", "164.310(a)(2)(ii)"],
            "description": "Contingency plan, Facility security plan",
        },
        "pci-dss": {
            "controls": ["12.10.1"],
            "description": "Incident response plan",
        },
    },
    "DE.CM": {
        "name": "Continuous Monitoring",
        "function": "DETECT",
        "iso27001": {
            "controls": ["A.8.15", "A.8.16"],
            "description": "Logging, Monitoring activities",
        },
        "soc2": {
            "controls": ["CC7.1", "CC7.2"],
            "description": "Infrastructure and software monitoring, Anomaly detection",
        },
        "hipaa": {
            "controls": ["164.312(b)", "164.308(a)(1)(ii)(D)"],
            "description": "Audit controls, Information system activity review",
        },
        "pci-dss": {
            "controls": ["10.1", "10.2", "10.3", "10.4", "10.5", "10.6", "10.7", "11.1", "11.2", "11.4", "11.5", "11.6"],
            "description": "Log and monitor, Wireless scanning, IDS/IPS, File integrity monitoring, Change detection",
        },
    },
    "DE.AE": {
        "name": "Adverse Event Analysis",
        "function": "DETECT",
        "iso27001": {
            "controls": ["A.5.7", "A.8.15", "A.8.16"],
            "description": "Threat intelligence, Logging, Monitoring for anomalies",
        },
        "soc2": {
            "controls": ["CC7.2", "CC7.3"],
            "description": "Anomaly detection, Security event evaluation",
        },
        "hipaa": {
            "controls": ["164.308(a)(1)(ii)(D)", "164.308(a)(6)(ii)"],
            "description": "Information system activity review, Response and reporting",
        },
        "pci-dss": {
            "controls": ["10.4.1", "10.4.2", "10.4.3", "11.5"],
            "description": "Log analysis, Automated alerting, File integrity monitoring",
        },
    },
    "RS.MA": {
        "name": "Incident Management",
        "function": "RESPOND",
        "iso27001": {
            "controls": ["A.5.24", "A.5.25", "A.5.26"],
            "description": "Incident management planning, Assessment and decision, Response to incidents",
        },
        "soc2": {
            "controls": ["CC7.3", "CC7.4"],
            "description": "Security event evaluation, Incident response",
        },
        "hipaa": {
            "controls": ["164.308(a)(6)(i)", "164.308(a)(6)(ii)"],
            "description": "Security incident procedures, Response and reporting",
        },
        "pci-dss": {
            "controls": ["12.10.1", "12.10.2", "12.10.3", "12.10.4"],
            "description": "Incident response plan and testing",
        },
    },
    "RS.AN": {
        "name": "Incident Analysis",
        "function": "RESPOND",
        "iso27001": {
            "controls": ["A.5.27", "A.5.28"],
            "description": "Learning from incidents, Collection of evidence",
        },
        "soc2": {
            "controls": ["CC7.4", "CC7.5"],
            "description": "Incident analysis, Incident remediation",
        },
        "hipaa": {
            "controls": ["164.308(a)(6)(ii)"],
            "description": "Response and reporting",
        },
        "pci-dss": {
            "controls": ["12.10.5", "12.10.6"],
            "description": "Incident response improvement, Security alerts monitoring",
        },
    },
    "RS.CO": {
        "name": "Incident Response Reporting and Communication",
        "function": "RESPOND",
        "iso27001": {
            "controls": ["A.5.5", "A.5.6", "A.5.26"],
            "description": "Contact with authorities, Contact with special interest groups, Response to incidents",
        },
        "soc2": {
            "controls": ["CC2.3", "CC7.4"],
            "description": "External communication, Incident response",
        },
        "hipaa": {
            "controls": ["164.308(a)(6)(ii)", "164.404", "164.408"],
            "description": "Response and reporting, Breach notification, Notification to HHS",
        },
        "pci-dss": {
            "controls": ["12.10.1", "12.10.5"],
            "description": "Incident response plan communications, Post-incident activities",
        },
    },
    "RS.MI": {
        "name": "Incident Mitigation",
        "function": "RESPOND",
        "iso27001": {
            "controls": ["A.5.26"],
            "description": "Response to information security incidents",
        },
        "soc2": {
            "controls": ["CC7.4", "CC7.5"],
            "description": "Incident containment, Incident remediation",
        },
        "hipaa": {
            "controls": ["164.308(a)(6)(ii)"],
            "description": "Response and reporting — mitigation",
        },
        "pci-dss": {
            "controls": ["12.10.4"],
            "description": "Incident response training",
        },
    },
    "RC.RP": {
        "name": "Incident Recovery Plan Execution",
        "function": "RECOVER",
        "iso27001": {
            "controls": ["A.5.29", "A.5.30"],
            "description": "ICT readiness for business continuity, ICT continuity plans",
        },
        "soc2": {
            "controls": ["CC9.1", "A1.2"],
            "description": "Risk mitigation, Recovery from incidents",
        },
        "hipaa": {
            "controls": ["164.308(a)(7)(ii)(B)", "164.308(a)(7)(ii)(C)"],
            "description": "Disaster recovery plan, Emergency mode operation plan",
        },
        "pci-dss": {
            "controls": ["12.10.2"],
            "description": "Incident response recovery procedures",
        },
    },
    "RC.CO": {
        "name": "Incident Recovery Communication",
        "function": "RECOVER",
        "iso27001": {
            "controls": ["A.5.5", "A.5.6"],
            "description": "Contact with authorities, Contact with special interest groups",
        },
        "soc2": {
            "controls": ["CC2.3"],
            "description": "External communication of recovery activities",
        },
        "hipaa": {
            "controls": ["164.404", "164.406", "164.408"],
            "description": "Notification to individuals, Media notification, HHS notification",
        },
        "pci-dss": {
            "controls": ["12.10.5"],
            "description": "Post-incident activities and communication",
        },
    },
}

CSF_FUNCTIONS = {
    "GOVERN": ["GV.OC", "GV.RM", "GV.RR", "GV.PO", "GV.OV", "GV.SC"],
    "IDENTIFY": ["ID.AM", "ID.RA", "ID.IM"],
    "PROTECT": ["PR.AA", "PR.AT", "PR.DS", "PR.PS", "PR.IR"],
    "DETECT": ["DE.CM", "DE.AE"],
    "RESPOND": ["RS.MA", "RS.AN", "RS.CO", "RS.MI"],
    "RECOVER": ["RC.RP", "RC.CO"],
}


def generate_mapping(
    target_framework: str,
    filter_functions: list[str] | None = None,
) -> dict:
    """Generate control mapping from NIST CSF to target framework."""
    mappings: list[dict] = []
    overlap_analysis: dict[str, list[str]] = {}

    for cat_id, cat_data in CONTROL_MAPPINGS.items():
        func = cat_data["function"]
        if filter_functions and func not in filter_functions:
            continue

        target_data = cat_data.get(target_framework)
        if not target_data:
            continue

        mapping = {
            "csf_category": cat_id,
            "csf_category_name": cat_data["name"],
            "csf_function": func,
            "target_framework": FRAMEWORK_NAMES.get(target_framework, target_framework),
            "target_controls": target_data["controls"],
            "target_description": target_data["description"],
        }
        mappings.append(mapping)

        # Track control overlaps
        for ctrl in target_data["controls"]:
            overlap_analysis.setdefault(ctrl, []).append(cat_id)

    # Identify controls that satisfy multiple CSF categories
    overlaps = {
        ctrl: cats for ctrl, cats in overlap_analysis.items() if len(cats) > 1
    }

    return {
        "source_framework": "NIST CSF 2.0",
        "target_framework": FRAMEWORK_NAMES.get(target_framework, target_framework),
        "generated": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "total_mappings": len(mappings),
        "mappings": mappings,
        "control_overlaps": overlaps,
        "overlap_summary": f"{len(overlaps)} target controls satisfy multiple CSF categories",
    }


def generate_unified_matrix(filter_functions: list[str] | None = None) -> dict:
    """Generate unified control matrix across all target frameworks."""
    target_frameworks = ["iso27001", "soc2", "hipaa", "pci-dss"]
    matrix: list[dict] = []

    for cat_id, cat_data in CONTROL_MAPPINGS.items():
        func = cat_data["function"]
        if filter_functions and func not in filter_functions:
            continue

        row: dict[str, Any] = {
            "csf_category": cat_id,
            "csf_category_name": cat_data["name"],
            "csf_function": func,
            "frameworks": {},
        }

        for fw in target_frameworks:
            fw_data = cat_data.get(fw, {})
            row["frameworks"][FRAMEWORK_NAMES.get(fw, fw)] = {
                "controls": fw_data.get("controls", []),
                "description": fw_data.get("description", "No direct mapping"),
                "mapped": bool(fw_data.get("controls")),
            }

        matrix.append(row)

    # Coverage analysis
    coverage: dict[str, dict[str, int]] = {}
    for fw in target_frameworks:
        fw_name = FRAMEWORK_NAMES.get(fw, fw)
        mapped = sum(1 for row in matrix if row["frameworks"][fw_name]["mapped"])
        coverage[fw_name] = {
            "mapped_categories": mapped,
            "total_categories": len(matrix),
            "coverage_percent": round(mapped / len(matrix) * 100, 1) if matrix else 0,
        }

    return {
        "source_framework": "NIST CSF 2.0",
        "target_frameworks": [FRAMEWORK_NAMES[fw] for fw in target_frameworks],
        "generated": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "total_categories": len(matrix),
        "matrix": matrix,
        "coverage_analysis": coverage,
    }


def format_markdown(result: dict) -> str:
    """Format mapping results as Markdown."""
    lines: list[str] = []

    if "matrix" in result:
        return _format_unified_markdown(result)

    lines.append(f"# NIST CSF 2.0 Control Mapping Report")
    lines.append("")
    lines.append(f"**Source:** {result['source_framework']}")
    lines.append(f"**Target:** {result['target_framework']}")
    lines.append(f"**Generated:** {result['generated']}")
    lines.append(f"**Total Mappings:** {result['total_mappings']}")
    lines.append("")

    # Group by function
    by_function: dict[str, list[dict]] = {}
    for m in result["mappings"]:
        by_function.setdefault(m["csf_function"], []).append(m)

    for func, mappings in by_function.items():
        lines.append(f"## {func}")
        lines.append("")
        lines.append("| CSF Category | Name | Target Controls | Description |")
        lines.append("|---|---|---|---|")
        for m in mappings:
            ctrls = ", ".join(m["target_controls"])
            lines.append(f"| {m['csf_category']} | {m['csf_category_name']} | {ctrls} | {m['target_description']} |")
        lines.append("")

    # Overlaps
    if result["control_overlaps"]:
        lines.append("## Control Overlaps")
        lines.append("")
        lines.append("These target controls satisfy multiple CSF categories:")
        lines.append("")
        lines.append("| Target Control | CSF Categories |")
        lines.append("|---|---|")
        for ctrl, cats in result["control_overlaps"].items():
            lines.append(f"| {ctrl} | {', '.join(cats)} |")
        lines.append("")

    return "\n".join(lines)


def _format_unified_markdown(result: dict) -> str:
    """Format unified matrix as Markdown."""
    lines: list[str] = []
    lines.append("# Unified Compliance Control Matrix")
    lines.append("")
    lines.append(f"**Source:** {result['source_framework']}")
    lines.append(f"**Target Frameworks:** {', '.join(result['target_frameworks'])}")
    lines.append(f"**Generated:** {result['generated']}")
    lines.append("")

    # Coverage summary
    lines.append("## Coverage Analysis")
    lines.append("")
    lines.append("| Framework | Mapped Categories | Total | Coverage |")
    lines.append("|---|---|---|---|")
    for fw, cov in result["coverage_analysis"].items():
        lines.append(f"| {fw} | {cov['mapped_categories']} | {cov['total_categories']} | {cov['coverage_percent']}% |")
    lines.append("")

    # Group by function
    by_function: dict[str, list[dict]] = {}
    for row in result["matrix"]:
        by_function.setdefault(row["csf_function"], []).append(row)

    for func, rows in by_function.items():
        lines.append(f"## {func}")
        lines.append("")
        for row in rows:
            lines.append(f"### {row['csf_category']} — {row['csf_category_name']}")
            lines.append("")
            lines.append("| Framework | Controls | Description |")
            lines.append("|---|---|---|")
            for fw_name, fw_data in row["frameworks"].items():
                ctrls = ", ".join(fw_data["controls"]) if fw_data["controls"] else "—"
                desc = fw_data["description"]
                lines.append(f"| {fw_name} | {ctrls} | {desc} |")
            lines.append("")

    return "\n".join(lines)


def write_output(result: dict, output_path: str | None, fmt: str) -> None:
    """Write results to file or stdout."""
    if fmt == "markdown":
        content = format_markdown(result)
    else:
        content = json.dumps(result, indent=2)

    if output_path:
        with open(output_path, "w") as f:
            f.write(content)
        print(f"Mapping written to {output_path}", file=sys.stderr)
    else:
        print(content)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="NIST CSF 2.0 Control Mapper — map CSF categories to other compliance frameworks"
    )
    parser.add_argument(
        "--source-framework", "-s", default="nist-csf",
        help="Source framework (default: nist-csf)"
    )
    parser.add_argument(
        "--target-framework", "-t", required=True,
        choices=["iso27001", "soc2", "hipaa", "pci-dss", "all"],
        help="Target framework to map to (or 'all' for unified matrix)"
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
        help="Comma-separated list of CSF functions to include (e.g., GOVERN,PROTECT)"
    )

    args = parser.parse_args()

    filter_functions = None
    if args.functions:
        filter_functions = [f.strip().upper() for f in args.functions.split(",")]
        valid_functions = set(CSF_FUNCTIONS.keys())
        invalid = [f for f in filter_functions if f not in valid_functions]
        if invalid:
            print(f"Error: Unknown functions: {', '.join(invalid)}", file=sys.stderr)
            print(f"Valid functions: {', '.join(valid_functions)}", file=sys.stderr)
            sys.exit(1)

    if args.target_framework == "all":
        result = generate_unified_matrix(filter_functions)
    else:
        result = generate_mapping(args.target_framework, filter_functions)

    write_output(result, args.output, args.format)


if __name__ == "__main__":
    main()
