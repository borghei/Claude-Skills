#!/usr/bin/env python3
"""
AI Impact Assessor

Generates comprehensive AI impact assessments evaluating fairness,
transparency, safety, privacy, security, and accountability dimensions.
Maps impacts to interested parties and provides risk treatment recommendations.

Usage:
    python ai_impact_assessor.py --template > ai_system.json
    python ai_impact_assessor.py --input ai_system.json
    python ai_impact_assessor.py --input ai_system.json --format markdown --output report.md
    python ai_impact_assessor.py --input ai_system.json --output report.json
"""

import argparse
import json
import sys
from datetime import datetime
from typing import Any, Dict, List, Tuple


TEMPLATE = {
    "system_info": {
        "name": "",
        "version": "",
        "description": "",
        "purpose": "",
        "domain": "",
        "deployment_status": "",
        "owner": "",
        "assessment_date": ""
    },
    "model_details": {
        "model_type": "",
        "training_approach": "",
        "is_generative": False,
        "is_foundation_model": False,
        "is_fine_tuned": False,
        "makes_autonomous_decisions": False,
        "human_in_the_loop": False,
        "decision_impact_level": "",
        "affected_population_size": 0
    },
    "data_details": {
        "training_data_sources": [],
        "training_data_size": "",
        "includes_personal_data": False,
        "personal_data_categories": [],
        "includes_sensitive_data": False,
        "sensitive_data_categories": [],
        "data_consent_obtained": False,
        "data_quality_assessed": False,
        "bias_assessment_conducted": False,
        "data_provenance_documented": False,
        "data_retention_defined": False,
        "anonymization_applied": False
    },
    "fairness": {
        "protected_attributes_identified": False,
        "protected_attributes_list": [],
        "bias_testing_conducted": False,
        "demographic_parity_measured": False,
        "equalized_odds_measured": False,
        "disparate_impact_assessed": False,
        "fairness_thresholds_defined": False,
        "bias_mitigation_applied": False,
        "ongoing_fairness_monitoring": False,
        "redress_mechanism_available": False
    },
    "transparency": {
        "model_documentation_exists": False,
        "model_card_published": False,
        "decision_explanation_available": False,
        "explainability_method_used": "",
        "users_informed_of_ai_use": False,
        "limitations_documented": False,
        "confidence_scores_provided": False,
        "audit_trail_maintained": False,
        "source_attribution_provided": False,
        "algorithmic_logic_disclosed": False
    },
    "safety": {
        "failure_modes_identified": False,
        "failure_mode_count": 0,
        "edge_cases_tested": False,
        "robustness_testing_conducted": False,
        "human_override_available": False,
        "fallback_mechanism_exists": False,
        "safety_critical_application": False,
        "harm_potential_assessed": False,
        "physical_harm_possible": False,
        "psychological_harm_possible": False,
        "financial_harm_possible": False,
        "kill_switch_available": False,
        "performance_degradation_monitoring": False,
        "rollback_capability": False
    },
    "privacy": {
        "privacy_impact_assessment_done": False,
        "gdpr_applicable": False,
        "ccpa_applicable": False,
        "data_minimization_practiced": False,
        "purpose_limitation_enforced": False,
        "consent_mechanisms_implemented": False,
        "data_subject_rights_supported": False,
        "data_deletion_capability": False,
        "encryption_at_rest": False,
        "encryption_in_transit": False,
        "access_controls_implemented": False,
        "differential_privacy_used": False,
        "federated_learning_used": False
    },
    "security": {
        "threat_model_created": False,
        "adversarial_testing_conducted": False,
        "model_integrity_verified": False,
        "input_validation_implemented": False,
        "output_filtering_implemented": False,
        "prompt_injection_mitigated": False,
        "model_extraction_mitigated": False,
        "data_poisoning_mitigated": False,
        "access_management_implemented": False,
        "api_rate_limiting": False,
        "audit_logging_enabled": False,
        "incident_response_plan": False,
        "model_versioning_controlled": False
    },
    "accountability": {
        "decision_ownership_defined": False,
        "escalation_procedures_exist": False,
        "audit_trail_complete": False,
        "regulatory_compliance_verified": False,
        "ethics_review_conducted": False,
        "stakeholder_consultation_done": False,
        "complaint_mechanism_available": False,
        "liability_framework_defined": False,
        "documentation_up_to_date": False,
        "periodic_review_scheduled": False
    },
    "interested_parties": [
        {
            "party": "",
            "relationship": "",
            "impact_type": "",
            "impact_severity": ""
        }
    ],
    "existing_controls": [],
    "eu_ai_act_context": {
        "risk_category": "",
        "is_high_risk": False,
        "is_gpai": False,
        "is_prohibited": False
    }
}


DIMENSION_WEIGHTS = {
    "fairness": 0.20,
    "transparency": 0.15,
    "safety": 0.25,
    "privacy": 0.15,
    "security": 0.15,
    "accountability": 0.10
}


def score_dimension(data: Dict, dimension: str, checks: List[Tuple[str, str, float]]) -> Tuple[float, str, List[Dict]]:
    """Score a dimension and return score, risk level, and findings."""
    section = data.get(dimension, {})
    findings = []
    weighted_total = 0
    max_weight = 0

    for key, description, weight in checks:
        value = section.get(key, False)
        max_weight += weight
        if value:
            weighted_total += weight
        findings.append({
            "check": description,
            "status": "pass" if value else "fail",
            "weight": weight,
            "dimension": dimension
        })

    score = (weighted_total / max_weight * 100) if max_weight > 0 else 0

    if score >= 80:
        risk_level = "Low"
    elif score >= 60:
        risk_level = "Medium"
    elif score >= 40:
        risk_level = "High"
    else:
        risk_level = "Critical"

    return score, risk_level, findings


FAIRNESS_CHECKS = [
    ("protected_attributes_identified", "Protected attributes identified", 2.0),
    ("bias_testing_conducted", "Bias testing conducted", 2.0),
    ("demographic_parity_measured", "Demographic parity measured", 1.5),
    ("equalized_odds_measured", "Equalized odds measured", 1.5),
    ("disparate_impact_assessed", "Disparate impact assessed", 1.5),
    ("fairness_thresholds_defined", "Fairness thresholds defined", 1.0),
    ("bias_mitigation_applied", "Bias mitigation applied", 2.0),
    ("ongoing_fairness_monitoring", "Ongoing fairness monitoring", 1.5),
    ("redress_mechanism_available", "Redress mechanism available for affected individuals", 1.0),
]

TRANSPARENCY_CHECKS = [
    ("model_documentation_exists", "Model documentation exists", 2.0),
    ("model_card_published", "Model card published", 1.0),
    ("decision_explanation_available", "Decision explanation available to users", 2.0),
    ("users_informed_of_ai_use", "Users informed of AI use", 2.0),
    ("limitations_documented", "Limitations and known issues documented", 1.5),
    ("confidence_scores_provided", "Confidence scores provided with outputs", 1.0),
    ("audit_trail_maintained", "Audit trail maintained for decisions", 1.5),
    ("source_attribution_provided", "Source attribution provided (if applicable)", 0.5),
    ("algorithmic_logic_disclosed", "Algorithmic logic disclosed to stakeholders", 1.0),
]

SAFETY_CHECKS = [
    ("failure_modes_identified", "Failure modes identified and documented", 2.0),
    ("edge_cases_tested", "Edge cases tested", 1.5),
    ("robustness_testing_conducted", "Robustness/stress testing conducted", 1.5),
    ("human_override_available", "Human override available for decisions", 2.0),
    ("fallback_mechanism_exists", "Fallback mechanism exists for failures", 2.0),
    ("harm_potential_assessed", "Harm potential assessed", 2.0),
    ("kill_switch_available", "Kill switch / emergency stop available", 1.5),
    ("performance_degradation_monitoring", "Performance degradation monitoring", 1.5),
    ("rollback_capability", "Rollback capability to previous version", 1.0),
]

PRIVACY_CHECKS = [
    ("privacy_impact_assessment_done", "Privacy impact assessment completed", 2.0),
    ("data_minimization_practiced", "Data minimization practiced", 1.5),
    ("purpose_limitation_enforced", "Purpose limitation enforced", 1.5),
    ("consent_mechanisms_implemented", "Consent mechanisms implemented", 1.5),
    ("data_subject_rights_supported", "Data subject rights supported", 1.5),
    ("data_deletion_capability", "Data deletion capability", 1.0),
    ("encryption_at_rest", "Encryption at rest", 1.5),
    ("encryption_in_transit", "Encryption in transit", 1.5),
    ("access_controls_implemented", "Access controls implemented", 1.5),
]

SECURITY_CHECKS = [
    ("threat_model_created", "Threat model created", 2.0),
    ("adversarial_testing_conducted", "Adversarial testing conducted", 1.5),
    ("model_integrity_verified", "Model integrity verified", 1.5),
    ("input_validation_implemented", "Input validation implemented", 1.5),
    ("output_filtering_implemented", "Output filtering implemented", 1.0),
    ("prompt_injection_mitigated", "Prompt injection mitigated (if applicable)", 1.0),
    ("data_poisoning_mitigated", "Data poisoning risks mitigated", 1.0),
    ("access_management_implemented", "Access management implemented", 1.5),
    ("audit_logging_enabled", "Audit logging enabled", 1.5),
    ("incident_response_plan", "Incident response plan for AI security events", 1.5),
    ("model_versioning_controlled", "Model versioning controlled", 1.0),
]

ACCOUNTABILITY_CHECKS = [
    ("decision_ownership_defined", "Decision ownership defined", 2.0),
    ("escalation_procedures_exist", "Escalation procedures exist", 1.5),
    ("audit_trail_complete", "Audit trail complete", 1.5),
    ("regulatory_compliance_verified", "Regulatory compliance verified", 2.0),
    ("ethics_review_conducted", "Ethics review conducted", 1.5),
    ("stakeholder_consultation_done", "Stakeholder consultation done", 1.0),
    ("complaint_mechanism_available", "Complaint mechanism available", 1.0),
    ("liability_framework_defined", "Liability framework defined", 1.0),
    ("documentation_up_to_date", "Documentation up to date", 1.0),
    ("periodic_review_scheduled", "Periodic review scheduled", 1.0),
]


def generate_risk_treatments(dimension: str, risk_level: str, findings: List[Dict]) -> List[Dict]:
    """Generate risk treatment recommendations for a dimension."""
    treatments = []
    failed = [f for f in findings if f["status"] == "fail"]

    treatment_map = {
        "fairness": {
            "protected_attributes_identified": {
                "action": "Identify and document all protected attributes relevant to the AI system",
                "type": "Mitigate",
                "priority": "High",
                "effort": "Low"
            },
            "bias_testing_conducted": {
                "action": "Conduct comprehensive bias testing using standard fairness metrics",
                "type": "Mitigate",
                "priority": "Critical",
                "effort": "Medium"
            },
            "bias_mitigation_applied": {
                "action": "Apply bias mitigation techniques (pre-processing, in-processing, or post-processing)",
                "type": "Mitigate",
                "priority": "Critical",
                "effort": "High"
            },
            "ongoing_fairness_monitoring": {
                "action": "Implement continuous fairness monitoring in production",
                "type": "Mitigate",
                "priority": "High",
                "effort": "Medium"
            },
        },
        "transparency": {
            "model_documentation_exists": {
                "action": "Create comprehensive model documentation including architecture, training, and limitations",
                "type": "Mitigate",
                "priority": "Critical",
                "effort": "Medium"
            },
            "users_informed_of_ai_use": {
                "action": "Implement clear disclosure to users that they are interacting with AI",
                "type": "Mitigate",
                "priority": "Critical",
                "effort": "Low"
            },
            "decision_explanation_available": {
                "action": "Implement explainability mechanism (SHAP, LIME, attention visualization)",
                "type": "Mitigate",
                "priority": "High",
                "effort": "High"
            },
        },
        "safety": {
            "failure_modes_identified": {
                "action": "Conduct failure mode and effects analysis (FMEA) for the AI system",
                "type": "Mitigate",
                "priority": "Critical",
                "effort": "Medium"
            },
            "human_override_available": {
                "action": "Implement human override mechanism for all AI decisions",
                "type": "Mitigate",
                "priority": "Critical",
                "effort": "Medium"
            },
            "fallback_mechanism_exists": {
                "action": "Design and implement fallback mechanism for AI system failures",
                "type": "Mitigate",
                "priority": "Critical",
                "effort": "Medium"
            },
            "harm_potential_assessed": {
                "action": "Assess potential for physical, psychological, and financial harm",
                "type": "Mitigate",
                "priority": "Critical",
                "effort": "Low"
            },
        },
        "privacy": {
            "privacy_impact_assessment_done": {
                "action": "Conduct Privacy Impact Assessment (PIA) / DPIA",
                "type": "Mitigate",
                "priority": "Critical",
                "effort": "Medium"
            },
            "data_minimization_practiced": {
                "action": "Review and minimize data collection to what is strictly necessary",
                "type": "Mitigate",
                "priority": "High",
                "effort": "Medium"
            },
            "encryption_at_rest": {
                "action": "Implement encryption at rest for all data stores",
                "type": "Mitigate",
                "priority": "High",
                "effort": "Medium"
            },
        },
        "security": {
            "threat_model_created": {
                "action": "Create AI-specific threat model covering adversarial attacks, data poisoning, model extraction",
                "type": "Mitigate",
                "priority": "Critical",
                "effort": "Medium"
            },
            "adversarial_testing_conducted": {
                "action": "Conduct adversarial robustness testing",
                "type": "Mitigate",
                "priority": "High",
                "effort": "High"
            },
            "incident_response_plan": {
                "action": "Develop AI-specific incident response plan",
                "type": "Mitigate",
                "priority": "Critical",
                "effort": "Medium"
            },
        },
        "accountability": {
            "decision_ownership_defined": {
                "action": "Assign clear ownership for AI system decisions and outcomes",
                "type": "Mitigate",
                "priority": "Critical",
                "effort": "Low"
            },
            "regulatory_compliance_verified": {
                "action": "Verify compliance with applicable regulations (EU AI Act, GDPR, sector-specific)",
                "type": "Mitigate",
                "priority": "Critical",
                "effort": "High"
            },
            "ethics_review_conducted": {
                "action": "Conduct ethics review with diverse stakeholder representation",
                "type": "Mitigate",
                "priority": "High",
                "effort": "Medium"
            },
        }
    }

    dim_treatments = treatment_map.get(dimension, {})
    for finding in failed:
        check_key = None
        for key, desc, _ in (FAIRNESS_CHECKS + TRANSPARENCY_CHECKS + SAFETY_CHECKS +
                              PRIVACY_CHECKS + SECURITY_CHECKS + ACCOUNTABILITY_CHECKS):
            if desc == finding["check"]:
                check_key = key
                break

        if check_key and check_key in dim_treatments:
            treatments.append(dim_treatments[check_key])
        elif check_key:
            treatments.append({
                "action": f"Address: {finding['check']}",
                "type": "Mitigate",
                "priority": "Medium",
                "effort": "Medium"
            })

    return treatments


def map_eu_ai_act(data: Dict) -> Dict:
    """Map assessment to EU AI Act risk categories."""
    context = data.get("eu_ai_act_context", {})
    safety = data.get("safety", {})
    model = data.get("model_details", {})

    mapping = {
        "declared_risk_category": context.get("risk_category", "Not classified"),
        "is_high_risk": context.get("is_high_risk", False),
        "is_gpai": context.get("is_gpai", False),
        "is_prohibited": context.get("is_prohibited", False),
        "relevant_articles": [],
        "obligations": []
    }

    if context.get("is_prohibited"):
        mapping["relevant_articles"].append("Article 5 — Prohibited AI practices")
        mapping["obligations"].append("System must not be deployed — falls under prohibited practices")

    if context.get("is_high_risk"):
        mapping["relevant_articles"].extend([
            "Article 9 — Risk management system",
            "Article 10 — Data and data governance",
            "Article 11 — Technical documentation",
            "Article 13 — Transparency and provision of information",
            "Article 14 — Human oversight",
            "Article 15 — Accuracy, robustness and cybersecurity",
            "Article 17 — Quality management system"
        ])
        mapping["obligations"].extend([
            "Implement risk management system throughout AI lifecycle",
            "Ensure data governance for training, validation, and testing datasets",
            "Maintain technical documentation per Annex IV",
            "Provide transparency information to deployers",
            "Enable effective human oversight",
            "Achieve appropriate accuracy, robustness, and cybersecurity",
            "Establish quality management system"
        ])

    if context.get("is_gpai"):
        mapping["relevant_articles"].extend([
            "Article 53 — Obligations for providers of GPAI models",
            "Article 55 — Obligations for systemic risk GPAI"
        ])
        mapping["obligations"].extend([
            "Maintain technical documentation",
            "Provide information to downstream providers",
            "Comply with copyright Directive",
            "Publish summary of training data"
        ])

    return mapping


def map_iso42001_controls(dimension_scores: Dict) -> List[Dict]:
    """Map assessment results to ISO 42001 Annex A controls."""
    control_mapping = []

    annex_map = {
        "fairness": [
            {"control": "A.5", "title": "Assessing AI System Impact",
             "relevance": "Fairness assessment is core to impact evaluation"},
            {"control": "A.7", "title": "Data for AI Systems",
             "relevance": "Data bias assessment directly affects fairness"}
        ],
        "transparency": [
            {"control": "A.8", "title": "Information for Interested Parties",
             "relevance": "Transparency disclosures for stakeholders"},
            {"control": "A.9", "title": "Use of AI Systems",
             "relevance": "User guidance and acceptable use documentation"}
        ],
        "safety": [
            {"control": "A.6", "title": "AI System Lifecycle",
             "relevance": "Safety controls across design, testing, deployment"},
            {"control": "A.5", "title": "Assessing AI System Impact",
             "relevance": "Safety impact assessment for individuals and society"}
        ],
        "privacy": [
            {"control": "A.7", "title": "Data for AI Systems",
             "relevance": "Data protection and governance"},
            {"control": "A.2", "title": "AI Policies",
             "relevance": "Privacy policies for AI data handling"}
        ],
        "security": [
            {"control": "A.4", "title": "Resources for AI Systems",
             "relevance": "Secure infrastructure and resource management"},
            {"control": "A.6", "title": "AI System Lifecycle",
             "relevance": "Security controls in development and deployment"}
        ],
        "accountability": [
            {"control": "A.3", "title": "Internal Organization for AI",
             "relevance": "Organizational roles and accountability structure"},
            {"control": "A.10", "title": "Third-Party Relationships",
             "relevance": "Accountability in supplier and partner relationships"}
        ]
    }

    for dimension, score_data in dimension_scores.items():
        controls = annex_map.get(dimension, [])
        for ctrl in controls:
            control_mapping.append({
                "dimension": dimension,
                "dimension_risk_level": score_data["risk_level"],
                "iso42001_control": ctrl["control"],
                "control_title": ctrl["title"],
                "relevance": ctrl["relevance"]
            })

    return control_mapping


def run_assessment(data: Dict) -> Dict:
    """Run full AI impact assessment."""
    results = {
        "assessment_date": datetime.now().isoformat(),
        "framework": "ISO 42001:2023 AI Impact Assessment",
        "system": data.get("system_info", {}),
        "model": data.get("model_details", {}),
        "dimensions": {},
        "overall_risk_score": 0.0,
        "overall_risk_level": "",
        "interested_parties_impact": [],
        "risk_treatments": {},
        "eu_ai_act_mapping": {},
        "iso42001_control_mapping": [],
        "summary": {
            "high_risk_dimensions": [],
            "critical_findings_count": 0,
            "recommendations": []
        }
    }

    dimension_configs = [
        ("fairness", FAIRNESS_CHECKS),
        ("transparency", TRANSPARENCY_CHECKS),
        ("safety", SAFETY_CHECKS),
        ("privacy", PRIVACY_CHECKS),
        ("security", SECURITY_CHECKS),
        ("accountability", ACCOUNTABILITY_CHECKS)
    ]

    dimension_scores = {}
    weighted_sum = 0

    for dim_name, checks in dimension_configs:
        score, risk_level, findings = score_dimension(data, dim_name, checks)
        treatments = generate_risk_treatments(dim_name, risk_level, findings)

        dimension_scores[dim_name] = {
            "score": round(score, 1),
            "risk_level": risk_level
        }

        results["dimensions"][dim_name] = {
            "score": round(score, 1),
            "risk_level": risk_level,
            "findings": findings
        }
        results["risk_treatments"][dim_name] = treatments
        weighted_sum += score * DIMENSION_WEIGHTS.get(dim_name, 0)

        if risk_level in ("High", "Critical"):
            results["summary"]["high_risk_dimensions"].append({
                "dimension": dim_name,
                "score": round(score, 1),
                "risk_level": risk_level
            })

    results["overall_risk_score"] = round(weighted_sum, 1)
    if weighted_sum >= 80:
        results["overall_risk_level"] = "Low"
    elif weighted_sum >= 60:
        results["overall_risk_level"] = "Medium"
    elif weighted_sum >= 40:
        results["overall_risk_level"] = "High"
    else:
        results["overall_risk_level"] = "Critical"

    # Interested parties impact
    for party in data.get("interested_parties", []):
        if party.get("party"):
            results["interested_parties_impact"].append(party)

    # EU AI Act mapping
    results["eu_ai_act_mapping"] = map_eu_ai_act(data)

    # ISO 42001 control mapping
    results["iso42001_control_mapping"] = map_iso42001_controls(dimension_scores)

    # Count critical findings
    for dim_data in results["dimensions"].values():
        for finding in dim_data.get("findings", []):
            if finding["status"] == "fail" and finding["weight"] >= 2.0:
                results["summary"]["critical_findings_count"] += 1

    # Recommendations
    if results["summary"]["high_risk_dimensions"]:
        dims = ", ".join(d["dimension"] for d in results["summary"]["high_risk_dimensions"])
        results["summary"]["recommendations"].append(
            f"Prioritize risk treatment for high/critical risk dimensions: {dims}"
        )

    safety = data.get("safety", {})
    if safety.get("safety_critical_application") and not safety.get("human_override_available"):
        results["summary"]["recommendations"].append(
            "URGENT: Safety-critical application without human override — implement immediately"
        )

    model = data.get("model_details", {})
    if model.get("makes_autonomous_decisions") and not model.get("human_in_the_loop"):
        results["summary"]["recommendations"].append(
            "Autonomous decision-making without human-in-the-loop — assess if human oversight is required"
        )

    if data.get("eu_ai_act_context", {}).get("is_high_risk"):
        results["summary"]["recommendations"].append(
            "EU AI Act high-risk classification — ensure compliance with Articles 9-15, 17"
        )

    return results


def format_text_report(results: Dict) -> str:
    """Format results as human-readable text."""
    lines = []
    system = results.get("system", {})

    lines.append("=" * 70)
    lines.append("AI IMPACT ASSESSMENT REPORT")
    lines.append("=" * 70)
    lines.append(f"System: {system.get('name', 'Unknown')}")
    lines.append(f"Version: {system.get('version', 'N/A')}")
    lines.append(f"Purpose: {system.get('purpose', 'N/A')}")
    lines.append(f"Domain: {system.get('domain', 'N/A')}")
    lines.append(f"Assessment Date: {results['assessment_date']}")
    lines.append(f"Overall Risk Score: {results['overall_risk_score']}/100")
    lines.append(f"Overall Risk Level: {results['overall_risk_level']}")
    lines.append("")

    # Dimension scores
    lines.append("-" * 70)
    lines.append("DIMENSION SCORES")
    lines.append("-" * 70)
    for dim_name, dim_data in results["dimensions"].items():
        score = dim_data["score"]
        risk = dim_data["risk_level"]
        bar_len = int(score / 5)
        bar = "#" * bar_len + "." * (20 - bar_len)
        risk_marker = {"Low": "  ", "Medium": "! ", "High": "!!", "Critical": "XX"}.get(risk, "??")
        lines.append(f"  [{risk_marker}] {dim_name.title():<20} [{bar}] {score:>5.1f}  ({risk})")
    lines.append("")

    # High risk dimensions
    high_risk = results["summary"]["high_risk_dimensions"]
    if high_risk:
        lines.append("-" * 70)
        lines.append("HIGH/CRITICAL RISK DIMENSIONS")
        lines.append("-" * 70)
        for dim in high_risk:
            lines.append(f"  [{dim['risk_level'].upper()}] {dim['dimension'].title()} — Score: {dim['score']}")
        lines.append("")

    # Risk treatments
    lines.append("-" * 70)
    lines.append("RISK TREATMENT RECOMMENDATIONS")
    lines.append("-" * 70)
    for dim_name, treatments in results["risk_treatments"].items():
        if treatments:
            lines.append(f"  {dim_name.title()}:")
            for t in treatments:
                lines.append(f"    [{t['priority']}] {t['action']}")
                lines.append(f"      Type: {t['type']} | Effort: {t['effort']}")
            lines.append("")

    # EU AI Act
    eu_mapping = results.get("eu_ai_act_mapping", {})
    if eu_mapping.get("relevant_articles"):
        lines.append("-" * 70)
        lines.append("EU AI ACT MAPPING")
        lines.append("-" * 70)
        lines.append(f"  Risk Category: {eu_mapping.get('declared_risk_category', 'N/A')}")
        lines.append(f"  High-Risk: {'Yes' if eu_mapping.get('is_high_risk') else 'No'}")
        lines.append(f"  GPAI: {'Yes' if eu_mapping.get('is_gpai') else 'No'}")
        for art in eu_mapping.get("relevant_articles", []):
            lines.append(f"  - {art}")
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


def format_markdown_report(results: Dict) -> str:
    """Format results as a markdown report."""
    system = results.get("system", {})
    lines = []

    lines.append(f"# AI Impact Assessment: {system.get('name', 'Unknown')}")
    lines.append("")
    lines.append(f"**Version:** {system.get('version', 'N/A')}")
    lines.append(f"**Purpose:** {system.get('purpose', 'N/A')}")
    lines.append(f"**Domain:** {system.get('domain', 'N/A')}")
    lines.append(f"**Assessment Date:** {results['assessment_date']}")
    lines.append(f"**Overall Risk Score:** {results['overall_risk_score']}/100")
    lines.append(f"**Overall Risk Level:** {results['overall_risk_level']}")
    lines.append("")

    # Dimension summary table
    lines.append("## Dimension Scores")
    lines.append("")
    lines.append("| Dimension | Score | Risk Level |")
    lines.append("|-----------|-------|------------|")
    for dim_name, dim_data in results["dimensions"].items():
        lines.append(f"| {dim_name.title()} | {dim_data['score']}/100 | {dim_data['risk_level']} |")
    lines.append("")

    # Per-dimension details
    for dim_name, dim_data in results["dimensions"].items():
        lines.append(f"## {dim_name.title()}")
        lines.append("")
        lines.append(f"**Score:** {dim_data['score']}/100 | **Risk Level:** {dim_data['risk_level']}")
        lines.append("")

        passed = [f for f in dim_data["findings"] if f["status"] == "pass"]
        failed = [f for f in dim_data["findings"] if f["status"] == "fail"]

        if passed:
            lines.append("**Implemented:**")
            for f in passed:
                lines.append(f"- [x] {f['check']}")
        if failed:
            lines.append("")
            lines.append("**Gaps:**")
            for f in failed:
                lines.append(f"- [ ] {f['check']}")
        lines.append("")

        treatments = results["risk_treatments"].get(dim_name, [])
        if treatments:
            lines.append("**Risk Treatments:**")
            lines.append("")
            lines.append("| Priority | Action | Type | Effort |")
            lines.append("|----------|--------|------|--------|")
            for t in treatments:
                lines.append(f"| {t['priority']} | {t['action']} | {t['type']} | {t['effort']} |")
            lines.append("")

    # EU AI Act
    eu_mapping = results.get("eu_ai_act_mapping", {})
    if eu_mapping.get("relevant_articles"):
        lines.append("## EU AI Act Mapping")
        lines.append("")
        lines.append(f"- **Risk Category:** {eu_mapping.get('declared_risk_category', 'N/A')}")
        lines.append(f"- **High-Risk:** {'Yes' if eu_mapping.get('is_high_risk') else 'No'}")
        lines.append(f"- **GPAI:** {'Yes' if eu_mapping.get('is_gpai') else 'No'}")
        lines.append("")
        if eu_mapping.get("obligations"):
            lines.append("**Obligations:**")
            for ob in eu_mapping["obligations"]:
                lines.append(f"- {ob}")
            lines.append("")

    # ISO 42001
    iso_mapping = results.get("iso42001_control_mapping", [])
    if iso_mapping:
        lines.append("## ISO 42001 Control Mapping")
        lines.append("")
        lines.append("| Dimension | Risk | Control | Title | Relevance |")
        lines.append("|-----------|------|---------|-------|-----------|")
        for m in iso_mapping:
            lines.append(
                f"| {m['dimension'].title()} | {m['dimension_risk_level']} | "
                f"{m['iso42001_control']} | {m['control_title']} | {m['relevance']} |"
            )
        lines.append("")

    # Recommendations
    recs = results["summary"]["recommendations"]
    if recs:
        lines.append("## Recommendations")
        lines.append("")
        for i, rec in enumerate(recs, 1):
            lines.append(f"{i}. {rec}")
        lines.append("")

    lines.append("---")
    lines.append(f"*Generated by AI Impact Assessor (ISO 42001:2023)*")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="AI Impact Assessor — generates comprehensive AI system impact "
                    "assessments per ISO 42001:2023 requirements."
    )
    parser.add_argument(
        "--input", "-i",
        help="Path to JSON file describing the AI system"
    )
    parser.add_argument(
        "--template", "-t",
        action="store_true",
        help="Output a blank AI system template (JSON)"
    )
    parser.add_argument(
        "--output", "-o",
        help="Path to write the assessment report"
    )
    parser.add_argument(
        "--json", "-j",
        action="store_true",
        help="Output results as JSON"
    )
    parser.add_argument(
        "--format", "-f",
        choices=["text", "markdown"],
        default="text",
        help="Output format (default: text)"
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
    elif args.format == "markdown":
        output = format_markdown_report(results)
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
