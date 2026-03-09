#!/usr/bin/env python3
"""
AIMS Readiness Checker

Assesses organizational readiness against all ISO 42001:2023 clauses
and Annex A controls. Scores each clause on a 0-100 scale with maturity
levels and identifies gaps for certification preparation.

Usage:
    python aims_readiness_checker.py --template > org_profile.json
    python aims_readiness_checker.py --input org_profile.json
    python aims_readiness_checker.py --input org_profile.json --json
    python aims_readiness_checker.py --input org_profile.json --output report.json
"""

import argparse
import json
import sys
from datetime import datetime
from typing import Any, Dict, List, Tuple


TEMPLATE = {
    "organization": {
        "name": "",
        "industry": "",
        "ai_systems_count": 0,
        "employees_in_ai_roles": 0,
        "assessment_date": ""
    },
    "clause4_context": {
        "internal_external_issues_documented": False,
        "ai_specific_issues_identified": False,
        "interested_parties_identified": False,
        "stakeholder_requirements_documented": False,
        "aims_scope_defined": False,
        "scope_includes_all_ai_systems": False,
        "aims_established": False,
        "aims_documented": False,
        "aims_maintained": False
    },
    "clause5_leadership": {
        "management_commitment_demonstrated": False,
        "ai_policy_established": False,
        "ai_policy_includes_ethical_principles": False,
        "ai_policy_includes_responsible_ai": False,
        "ai_policy_communicated": False,
        "ai_policy_reviewed_periodically": False,
        "roles_and_responsibilities_defined": False,
        "ai_governance_board_established": False,
        "ai_system_owners_assigned": False,
        "data_stewards_assigned": False,
        "ethics_review_function_exists": False,
        "aims_authority_assigned": False
    },
    "clause6_planning": {
        "risks_and_opportunities_assessed": False,
        "ai_specific_risks_identified": False,
        "risk_assessment_methodology_defined": False,
        "risk_criteria_established": False,
        "risk_acceptance_criteria_defined": False,
        "ai_objectives_defined": False,
        "objectives_measurable": False,
        "objectives_monitored": False,
        "impact_assessment_process_defined": False,
        "impact_assessments_conducted": False,
        "change_planning_process_exists": False
    },
    "clause7_support": {
        "compute_resources_adequate": False,
        "data_resources_adequate": False,
        "ai_expertise_available": False,
        "infrastructure_adequate": False,
        "competence_requirements_defined": False,
        "training_plan_established": False,
        "ai_literacy_program_exists": False,
        "awareness_program_implemented": False,
        "communication_plan_defined": False,
        "internal_communication_established": False,
        "external_communication_established": False,
        "documented_information_controlled": False,
        "document_creation_process": False,
        "document_retention_policy": False
    },
    "clause8_operation": {
        "operational_planning_documented": False,
        "ai_processes_controlled": False,
        "risk_assessments_executed": False,
        "risk_treatment_plans_implemented": False,
        "ai_lifecycle_defined": False,
        "design_controls_implemented": False,
        "development_standards_established": False,
        "testing_validation_procedures": False,
        "deployment_procedures_documented": False,
        "monitoring_in_production": False,
        "retirement_procedures_defined": False,
        "data_quality_management": False,
        "data_provenance_tracking": False,
        "bias_assessment_procedures": False,
        "data_governance_established": False,
        "third_party_evaluation_process": False,
        "supplier_agreements_include_ai_requirements": False,
        "outsourced_ai_controlled": False
    },
    "clause9_performance": {
        "monitoring_metrics_defined": False,
        "ai_performance_measured": False,
        "fairness_metrics_tracked": False,
        "drift_monitoring_implemented": False,
        "kpis_for_aims": False,
        "internal_audit_program": False,
        "audit_schedule_defined": False,
        "audit_findings_documented": False,
        "management_review_conducted": False,
        "review_includes_ai_performance": False,
        "review_includes_risk_status": False,
        "review_outputs_documented": False
    },
    "clause10_improvement": {
        "nonconformity_process_defined": False,
        "corrective_actions_implemented": False,
        "root_cause_analysis_performed": False,
        "continual_improvement_process": False,
        "improvement_opportunities_identified": False,
        "ai_incident_management_process": False,
        "incident_classification_defined": False,
        "incident_response_procedures": False,
        "lessons_learned_captured": False
    },
    "annex_a_controls": {
        "a2_ai_policies": {
            "implemented": False,
            "documented": False,
            "description": ""
        },
        "a3_internal_organization": {
            "implemented": False,
            "documented": False,
            "description": ""
        },
        "a4_resources_for_ai": {
            "implemented": False,
            "documented": False,
            "description": ""
        },
        "a5_impact_assessment": {
            "implemented": False,
            "documented": False,
            "description": ""
        },
        "a6_ai_lifecycle": {
            "implemented": False,
            "documented": False,
            "description": ""
        },
        "a7_data_for_ai": {
            "implemented": False,
            "documented": False,
            "description": ""
        },
        "a8_information_for_stakeholders": {
            "implemented": False,
            "documented": False,
            "description": ""
        },
        "a9_use_of_ai": {
            "implemented": False,
            "documented": False,
            "description": ""
        },
        "a10_third_party_relationships": {
            "implemented": False,
            "documented": False,
            "description": ""
        }
    }
}


CLAUSE_DEFINITIONS = {
    "clause4_context": {
        "title": "Context of the Organization",
        "clause": "4",
        "description": "Understanding the organization and its context, interested parties, "
                       "scope, and AIMS establishment.",
        "keys": [
            ("internal_external_issues_documented", "Internal and external issues documented", "critical"),
            ("ai_specific_issues_identified", "AI-specific issues identified", "high"),
            ("interested_parties_identified", "Interested parties identified", "critical"),
            ("stakeholder_requirements_documented", "Stakeholder requirements documented", "high"),
            ("aims_scope_defined", "AIMS scope defined", "critical"),
            ("scope_includes_all_ai_systems", "Scope includes all relevant AI systems", "high"),
            ("aims_established", "AIMS established", "critical"),
            ("aims_documented", "AIMS documented", "critical"),
            ("aims_maintained", "AIMS maintained and improved", "high")
        ]
    },
    "clause5_leadership": {
        "title": "Leadership",
        "clause": "5",
        "description": "Management commitment, AI policy, organizational roles and "
                       "responsibilities, governance structure.",
        "keys": [
            ("management_commitment_demonstrated", "Top management commitment demonstrated", "critical"),
            ("ai_policy_established", "AI policy established", "critical"),
            ("ai_policy_includes_ethical_principles", "AI policy includes ethical principles", "critical"),
            ("ai_policy_includes_responsible_ai", "AI policy includes responsible AI commitment", "high"),
            ("ai_policy_communicated", "AI policy communicated to organization", "high"),
            ("ai_policy_reviewed_periodically", "AI policy reviewed periodically", "medium"),
            ("roles_and_responsibilities_defined", "AIMS roles and responsibilities defined", "critical"),
            ("ai_governance_board_established", "AI governance board or committee established", "high"),
            ("ai_system_owners_assigned", "AI system owners assigned", "high"),
            ("data_stewards_assigned", "Data stewards assigned", "medium"),
            ("ethics_review_function_exists", "Ethics review function exists", "high"),
            ("aims_authority_assigned", "AIMS authority assigned to specific role", "critical")
        ]
    },
    "clause6_planning": {
        "title": "Planning",
        "clause": "6",
        "description": "Risks and opportunities, AI risk assessment, objectives, "
                       "and impact assessment.",
        "keys": [
            ("risks_and_opportunities_assessed", "Risks and opportunities assessed", "critical"),
            ("ai_specific_risks_identified", "AI-specific risks identified", "critical"),
            ("risk_assessment_methodology_defined", "Risk assessment methodology defined", "critical"),
            ("risk_criteria_established", "Risk criteria established", "high"),
            ("risk_acceptance_criteria_defined", "Risk acceptance criteria defined", "high"),
            ("ai_objectives_defined", "AI objectives defined", "critical"),
            ("objectives_measurable", "Objectives are measurable", "high"),
            ("objectives_monitored", "Objectives are monitored", "high"),
            ("impact_assessment_process_defined", "Impact assessment process defined", "critical"),
            ("impact_assessments_conducted", "Impact assessments conducted for AI systems", "critical"),
            ("change_planning_process_exists", "Change planning process exists", "medium")
        ]
    },
    "clause7_support": {
        "title": "Support",
        "clause": "7",
        "description": "Resources, competence, awareness, communication, "
                       "and documented information.",
        "keys": [
            ("compute_resources_adequate", "Compute resources adequate", "high"),
            ("data_resources_adequate", "Data resources adequate", "high"),
            ("ai_expertise_available", "AI expertise available", "critical"),
            ("infrastructure_adequate", "Infrastructure adequate", "high"),
            ("competence_requirements_defined", "Competence requirements defined for AI roles", "critical"),
            ("training_plan_established", "Training plan established", "high"),
            ("ai_literacy_program_exists", "AI literacy program exists", "high"),
            ("awareness_program_implemented", "Awareness program implemented", "medium"),
            ("communication_plan_defined", "Communication plan defined", "medium"),
            ("internal_communication_established", "Internal communication on AI established", "medium"),
            ("external_communication_established", "External communication on AI established", "medium"),
            ("documented_information_controlled", "Documented information controlled", "critical"),
            ("document_creation_process", "Document creation process defined", "high"),
            ("document_retention_policy", "Document retention policy exists", "high")
        ]
    },
    "clause8_operation": {
        "title": "Operation",
        "clause": "8",
        "description": "Operational planning, AI risk assessment execution, AI system "
                       "lifecycle, data management, and third-party management.",
        "keys": [
            ("operational_planning_documented", "Operational planning documented", "critical"),
            ("ai_processes_controlled", "AI processes controlled", "critical"),
            ("risk_assessments_executed", "Risk assessments executed per methodology", "critical"),
            ("risk_treatment_plans_implemented", "Risk treatment plans implemented", "critical"),
            ("ai_lifecycle_defined", "AI system lifecycle defined", "critical"),
            ("design_controls_implemented", "Design controls implemented", "high"),
            ("development_standards_established", "Development standards established", "high"),
            ("testing_validation_procedures", "Testing and validation procedures exist", "critical"),
            ("deployment_procedures_documented", "Deployment procedures documented", "high"),
            ("monitoring_in_production", "Production monitoring implemented", "critical"),
            ("retirement_procedures_defined", "Retirement/decommissioning procedures defined", "medium"),
            ("data_quality_management", "Data quality management in place", "critical"),
            ("data_provenance_tracking", "Data provenance tracking implemented", "high"),
            ("bias_assessment_procedures", "Bias assessment procedures exist", "critical"),
            ("data_governance_established", "Data governance established", "high"),
            ("third_party_evaluation_process", "Third-party/supplier evaluation process exists", "high"),
            ("supplier_agreements_include_ai_requirements", "Supplier agreements include AI requirements", "high"),
            ("outsourced_ai_controlled", "Outsourced AI services controlled", "high")
        ]
    },
    "clause9_performance": {
        "title": "Performance Evaluation",
        "clause": "9",
        "description": "Monitoring, measurement, internal audit, and management review.",
        "keys": [
            ("monitoring_metrics_defined", "Monitoring and measurement metrics defined", "critical"),
            ("ai_performance_measured", "AI system performance measured", "critical"),
            ("fairness_metrics_tracked", "Fairness metrics tracked", "high"),
            ("drift_monitoring_implemented", "Drift monitoring implemented", "high"),
            ("kpis_for_aims", "KPIs defined for AIMS effectiveness", "high"),
            ("internal_audit_program", "Internal audit program established", "critical"),
            ("audit_schedule_defined", "Audit schedule defined", "high"),
            ("audit_findings_documented", "Audit findings documented", "high"),
            ("management_review_conducted", "Management review conducted", "critical"),
            ("review_includes_ai_performance", "Review includes AI system performance", "high"),
            ("review_includes_risk_status", "Review includes risk treatment status", "high"),
            ("review_outputs_documented", "Management review outputs documented", "high")
        ]
    },
    "clause10_improvement": {
        "title": "Improvement",
        "clause": "10",
        "description": "Nonconformity, corrective action, continual improvement, "
                       "and AI incident management.",
        "keys": [
            ("nonconformity_process_defined", "Nonconformity and corrective action process defined", "critical"),
            ("corrective_actions_implemented", "Corrective actions implemented and tracked", "critical"),
            ("root_cause_analysis_performed", "Root cause analysis performed for nonconformities", "high"),
            ("continual_improvement_process", "Continual improvement process established", "high"),
            ("improvement_opportunities_identified", "Improvement opportunities identified and tracked", "medium"),
            ("ai_incident_management_process", "AI incident management process defined", "critical"),
            ("incident_classification_defined", "Incident classification scheme defined", "high"),
            ("incident_response_procedures", "Incident response procedures documented", "high"),
            ("lessons_learned_captured", "Lessons learned captured from incidents", "medium")
        ]
    }
}


ANNEX_A_DEFINITIONS = {
    "a2_ai_policies": {
        "control": "A.2",
        "title": "AI Policies",
        "description": "Policies for responsible AI aligned with organizational objectives",
        "requirements": "Document and communicate AI policies covering ethical principles, "
                        "responsible development, deployment, and use of AI systems."
    },
    "a3_internal_organization": {
        "control": "A.3",
        "title": "Internal Organization for AI",
        "description": "Roles, responsibilities, and segregation of duties for AI",
        "requirements": "Define organizational structure for AI governance including "
                        "clear roles, responsibilities, and accountability."
    },
    "a4_resources_for_ai": {
        "control": "A.4",
        "title": "Resources for AI Systems",
        "description": "Compute, data, tools, and expertise management",
        "requirements": "Ensure adequate resources (compute, data, expertise, tools) "
                        "are available for AI system development and operation."
    },
    "a5_impact_assessment": {
        "control": "A.5",
        "title": "Assessing AI System Impact",
        "description": "Impact assessment processes for AI systems",
        "requirements": "Establish and conduct impact assessments for AI systems "
                        "evaluating effects on individuals, groups, and society."
    },
    "a6_ai_lifecycle": {
        "control": "A.6",
        "title": "AI System Lifecycle",
        "description": "Controls across design, development, deployment, and retirement",
        "requirements": "Implement controls across all AI system lifecycle stages "
                        "from design through retirement."
    },
    "a7_data_for_ai": {
        "control": "A.7",
        "title": "Data for AI Systems",
        "description": "Data quality, provenance, bias, governance, and protection",
        "requirements": "Manage data used in AI systems including quality, provenance, "
                        "bias assessment, governance, and protection measures."
    },
    "a8_information_for_stakeholders": {
        "control": "A.8",
        "title": "Information for Interested Parties",
        "description": "Transparency, disclosure, and communication",
        "requirements": "Provide appropriate information to interested parties about "
                        "AI systems including transparency and disclosure."
    },
    "a9_use_of_ai": {
        "control": "A.9",
        "title": "Use of AI Systems",
        "description": "Acceptable use policies, human oversight, and user guidance",
        "requirements": "Define acceptable use policies, implement human oversight, "
                        "and provide user guidance for AI systems."
    },
    "a10_third_party_relationships": {
        "control": "A.10",
        "title": "Third-Party Relationships",
        "description": "Supplier management, outsourced AI, and component evaluation",
        "requirements": "Manage third-party relationships including supplier evaluation, "
                        "outsourced AI controls, and component assessment."
    }
}


def score_clause(data: Dict, clause_key: str) -> Tuple[float, List[Dict]]:
    """Score a clause based on boolean checks."""
    clause_def = CLAUSE_DEFINITIONS[clause_key]
    section = data.get(clause_key, {})
    findings = []
    passed = 0
    total = len(clause_def["keys"])

    for key, description, severity in clause_def["keys"]:
        value = section.get(key, False)
        status = "pass" if value else "fail"
        if value:
            passed += 1
        findings.append({
            "check": description,
            "status": status,
            "severity": severity,
            "clause": clause_def["clause"]
        })

    score = (passed / total * 100) if total > 0 else 0
    return score, findings


def score_annex_a(data: Dict) -> Tuple[float, List[Dict]]:
    """Score Annex A controls."""
    annex = data.get("annex_a_controls", {})
    findings = []
    total_score = 0
    control_count = len(ANNEX_A_DEFINITIONS)

    for control_key, control_def in ANNEX_A_DEFINITIONS.items():
        control_data = annex.get(control_key, {})
        implemented = control_data.get("implemented", False)
        documented = control_data.get("documented", False)

        if implemented and documented:
            status = "Implemented"
            control_score = 100
        elif implemented:
            status = "Partial"
            control_score = 60
        elif documented:
            status = "Partial"
            control_score = 30
        else:
            status = "Not Implemented"
            control_score = 0

        total_score += control_score

        findings.append({
            "control": control_def["control"],
            "title": control_def["title"],
            "status": status,
            "implemented": implemented,
            "documented": documented,
            "requirements": control_def["requirements"],
            "score": control_score
        })

    avg_score = total_score / control_count if control_count > 0 else 0
    return avg_score, findings


def get_maturity_level(score: float) -> str:
    """Determine maturity level from score."""
    if score >= 90:
        return "Optimized"
    elif score >= 70:
        return "Managed"
    elif score >= 50:
        return "Defined"
    elif score >= 25:
        return "Developing"
    else:
        return "Initial"


def get_certification_readiness(overall_score: float, clause_scores: Dict) -> str:
    """Determine certification readiness."""
    # All clauses must be at least 50 for near-ready
    min_clause = min(clause_scores.values()) if clause_scores else 0

    if overall_score >= 80 and min_clause >= 60:
        return "Ready"
    elif overall_score >= 60 and min_clause >= 40:
        return "Near Ready"
    else:
        return "Significant Gaps"


def run_assessment(data: Dict) -> Dict:
    """Run full ISO 42001 readiness assessment."""
    results = {
        "assessment_date": datetime.now().isoformat(),
        "framework": "ISO/IEC 42001:2023",
        "organization": data.get("organization", {}).get("name", "Unknown"),
        "industry": data.get("organization", {}).get("industry", ""),
        "ai_systems_count": data.get("organization", {}).get("ai_systems_count", 0),
        "clauses": {},
        "annex_a": {},
        "overall_score": 0.0,
        "certification_readiness": "",
        "summary": {
            "critical_gaps": [],
            "high_gaps": [],
            "recommendations": []
        }
    }

    clause_scores = {}

    # Score each clause
    for clause_key, clause_def in CLAUSE_DEFINITIONS.items():
        score, findings = score_clause(data, clause_key)
        maturity = get_maturity_level(score)
        clause_scores[clause_key] = score

        results["clauses"][clause_key] = {
            "title": clause_def["title"],
            "clause": clause_def["clause"],
            "score": round(score, 1),
            "maturity": maturity,
            "findings": findings
        }

    # Score Annex A
    annex_score, annex_findings = score_annex_a(data)
    results["annex_a"] = {
        "score": round(annex_score, 1),
        "maturity": get_maturity_level(annex_score),
        "controls": annex_findings
    }

    # Calculate overall score (clauses weighted 70%, Annex A weighted 30%)
    clause_avg = sum(clause_scores.values()) / len(clause_scores) if clause_scores else 0
    overall = clause_avg * 0.7 + annex_score * 0.3
    results["overall_score"] = round(overall, 1)

    # Certification readiness
    results["certification_readiness"] = get_certification_readiness(overall, clause_scores)

    # Collect gaps
    for clause_key, clause_data in results["clauses"].items():
        for finding in clause_data["findings"]:
            if finding["status"] == "fail":
                gap = {
                    "clause": clause_data["title"],
                    "clause_number": clause_data["clause"],
                    "check": finding["check"],
                    "severity": finding["severity"]
                }
                if finding["severity"] == "critical":
                    results["summary"]["critical_gaps"].append(gap)
                elif finding["severity"] == "high":
                    results["summary"]["high_gaps"].append(gap)

    for control in results["annex_a"]["controls"]:
        if control["status"] == "Not Implemented":
            results["summary"]["critical_gaps"].append({
                "clause": f"Annex A - {control['title']}",
                "clause_number": control["control"],
                "check": control["requirements"],
                "severity": "high"
            })

    # Generate recommendations
    weakest_clauses = sorted(clause_scores.items(), key=lambda x: x[1])[:3]
    for clause_key, score in weakest_clauses:
        if score < 70:
            clause_def = CLAUSE_DEFINITIONS[clause_key]
            results["summary"]["recommendations"].append(
                f"Strengthen {clause_def['title']} (Clause {clause_def['clause']}): "
                f"Current score {score:.0f}/100. {clause_def['description']}"
            )

    if annex_score < 50:
        results["summary"]["recommendations"].append(
            "Implement Annex A controls — current coverage is insufficient for certification. "
            "Prioritize A.5 (Impact Assessment), A.6 (Lifecycle), and A.7 (Data) controls."
        )

    if results["certification_readiness"] == "Significant Gaps":
        results["summary"]["recommendations"].append(
            "Significant gaps exist across multiple clauses. Consider engaging an ISO 42001 "
            "consultant and plan for 6-12 months of implementation before Stage 1 audit."
        )
    elif results["certification_readiness"] == "Near Ready":
        results["summary"]["recommendations"].append(
            "Organization is approaching readiness. Focus on closing critical gaps "
            "and conduct a pre-certification internal audit within 3 months."
        )

    return results


def format_text_report(results: Dict) -> str:
    """Format results as human-readable text report."""
    lines = []
    lines.append("=" * 70)
    lines.append("ISO 42001:2023 AIMS READINESS ASSESSMENT")
    lines.append("=" * 70)
    lines.append(f"Organization: {results['organization']}")
    lines.append(f"Industry: {results.get('industry', 'N/A')}")
    lines.append(f"AI Systems in Scope: {results.get('ai_systems_count', 'N/A')}")
    lines.append(f"Assessment Date: {results['assessment_date']}")
    lines.append(f"Overall Score: {results['overall_score']}/100")
    lines.append(f"Certification Readiness: {results['certification_readiness']}")
    lines.append("")

    # Clause scores
    lines.append("-" * 70)
    lines.append("CLAUSE SCORES")
    lines.append("-" * 70)
    for clause_key, clause_data in results["clauses"].items():
        score = clause_data["score"]
        maturity = clause_data["maturity"]
        bar_len = int(score / 5)
        bar = "#" * bar_len + "." * (20 - bar_len)
        lines.append(
            f"  Clause {clause_data['clause']} - {clause_data['title']:<35} "
            f"[{bar}] {score:>5.1f}  ({maturity})"
        )
    lines.append("")

    # Annex A
    lines.append("-" * 70)
    lines.append(f"ANNEX A CONTROLS (Score: {results['annex_a']['score']}/100)")
    lines.append("-" * 70)
    for control in results["annex_a"]["controls"]:
        status_marker = {
            "Implemented": "[OK]",
            "Partial": "[~~]",
            "Not Implemented": "[  ]"
        }.get(control["status"], "[??]")
        lines.append(
            f"  {status_marker} {control['control']} - {control['title']:<40} "
            f"({control['status']})"
        )
    lines.append("")

    # Critical gaps
    critical = results["summary"]["critical_gaps"]
    if critical:
        lines.append("-" * 70)
        lines.append(f"CRITICAL GAPS ({len(critical)})")
        lines.append("-" * 70)
        for gap in critical:
            lines.append(f"  [CRITICAL] Clause {gap['clause_number']} - {gap['clause']}")
            lines.append(f"    {gap['check']}")
            lines.append("")

    # High gaps
    high = results["summary"]["high_gaps"]
    if high:
        lines.append("-" * 70)
        lines.append(f"HIGH GAPS ({len(high)})")
        lines.append("-" * 70)
        for gap in high[:10]:  # Limit to top 10
            lines.append(f"  [HIGH] Clause {gap['clause_number']} - {gap['clause']}")
            lines.append(f"    {gap['check']}")
            lines.append("")
        if len(high) > 10:
            lines.append(f"  ... and {len(high) - 10} more high-severity gaps")
            lines.append("")

    # Recommendations
    recs = results["summary"]["recommendations"]
    if recs:
        lines.append("-" * 70)
        lines.append("RECOMMENDATIONS")
        lines.append("-" * 70)
        for i, rec in enumerate(recs, 1):
            lines.append(f"  {i}. {rec}")
            lines.append("")

    lines.append("=" * 70)
    lines.append("End of Report")
    lines.append("=" * 70)

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="AIMS Readiness Checker — assesses organizational readiness "
                    "against ISO/IEC 42001:2023 requirements."
    )
    parser.add_argument(
        "--input", "-i",
        help="Path to JSON file with organization AIMS profile"
    )
    parser.add_argument(
        "--template", "-t",
        action="store_true",
        help="Output a blank AIMS profile template (JSON)"
    )
    parser.add_argument(
        "--output", "-o",
        help="Path to write the assessment report"
    )
    parser.add_argument(
        "--json", "-j",
        action="store_true",
        help="Output results as JSON (default is human-readable text)"
    )
    args = parser.parse_args()

    if args.template:
        print(json.dumps(TEMPLATE, indent=2))
        return

    if not args.input:
        parser.error("--input is required (or use --template to generate a blank profile)")

    try:
        with open(args.input, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found: {args.input}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {args.input}: {e}", file=sys.stderr)
        sys.exit(1)

    results = run_assessment(data)

    if args.json:
        output = json.dumps(results, indent=2)
    else:
        output = format_text_report(results)

    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
        print(f"Report written to {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
