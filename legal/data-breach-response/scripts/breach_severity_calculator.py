#!/usr/bin/env python3
"""
Breach Severity Calculator

Calculates ENISA breach severity score using the formula SE = (DPC x EI) + CB.
Determines severity verdict (LOW/MEDIUM/HIGH/VERY HIGH) and notification
obligations under GDPR, CCPA, HIPAA, PCI DSS, and NIS2.

Usage:
    python breach_severity_calculator.py --dpc 3 --ei 0.75 --confidentiality 0.5 --malicious
    python breach_severity_calculator.py --dpc 2 --ei 0.5 --confidentiality 0.5 --json
    python breach_severity_calculator.py --dpc 3 --ei 1.0 --confidentiality 0.5 --t0 "2026-04-10T08:00:00" --json
    python breach_severity_calculator.py --template
"""

import argparse
import json
import sys
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple


DPC_LABELS: Dict[int, str] = {1: "Simple demographic data", 2: "Behavioral or financial data", 3: "Sensitive personal data", 4: "Special category or highly sensitive data"}
EI_LABELS: Dict[float, str] = {0.25: "Negligible", 0.50: "Limited", 0.75: "Significant", 1.00: "Maximum (direct identifiers)"}
GDPR_HOURS, NIS2_EW_HOURS, NIS2_HOURS, PCI_HOURS = 72, 24, 72, 24


def calculate_cb(
    confidentiality: float,
    integrity: float,
    availability: float,
    malicious: bool,
) -> Tuple[float, Dict[str, float]]:
    """Calculate Circumstances of Breach (CB) component."""
    components: Dict[str, float] = {
        "confidentiality_loss": confidentiality,
        "integrity_loss": integrity,
        "availability_loss": availability,
        "malicious_intent": 0.5 if malicious else 0.0,
    }
    # CB is the sum of loss types minus overlap (max 1.0 practical cap)
    # but ENISA allows it to go negative with encryption offset
    cb = sum(components.values())
    return cb, components


def calculate_severity(
    dpc: int, ei: float, cb: float
) -> Tuple[float, str, str]:
    """Calculate ENISA severity score and return (score, verdict, description)."""
    se = (dpc * ei) + cb
    se = round(se, 2)

    if se < 2:
        verdict = "LOW"
        description = "Internal documentation only. No SA or data subject notification required."
    elif se < 3:
        verdict = "MEDIUM"
        description = "Notify supervisory authority within 72 hours (GDPR Art. 33)."
    elif se < 4:
        verdict = "HIGH"
        description = "Notify SA within 72h + notify individual data subjects without undue delay (GDPR Art. 34)."
    else:
        verdict = "VERY HIGH"
        description = "Notify SA + data subjects + consider public notice. Activate crisis management."

    return se, verdict, description


def get_notification_obligations(verdict: str) -> List[Dict[str, str]]:
    """Return notification obligations based on severity verdict."""
    obligations: List[Dict[str, str]] = []

    # Internal documentation always required
    obligations.append({
        "regulation": "GDPR Art. 33(5)",
        "action": "Document breach in internal breach register",
        "deadline": "Immediately",
        "required": "Always",
    })

    if verdict in ("MEDIUM", "HIGH", "VERY HIGH"):
        obligations.append({
            "regulation": "GDPR Art. 33",
            "action": "Notify supervisory authority",
            "deadline": "72 hours from T0",
            "required": "Yes",
        })

    if verdict in ("HIGH", "VERY HIGH"):
        obligations.append({
            "regulation": "GDPR Art. 34",
            "action": "Notify affected data subjects",
            "deadline": "Without undue delay",
            "required": "Yes — high risk to rights and freedoms",
        })

    if verdict == "VERY HIGH":
        obligations.append({
            "regulation": "GDPR Art. 34 / national law",
            "action": "Consider public communication",
            "deadline": "Without undue delay",
            "required": "When individual notification is disproportionate effort",
        })

    # Cross-regulation obligations (always assess)
    obligations.append({
        "regulation": "CCPA",
        "action": "Notify affected California residents",
        "deadline": "Most expedient time possible",
        "required": "If unencrypted PI of CA residents compromised",
    })
    obligations.append({
        "regulation": "NIS2 Art. 23",
        "action": "Early warning to CSIRT + full notification",
        "deadline": "24h early warning + 72h notification",
        "required": "If essential/important entity with significant incident",
    })
    obligations.append({
        "regulation": "HIPAA",
        "action": "Notify HHS and affected individuals",
        "deadline": "60 days; if >500: media notification",
        "required": "If unsecured PHI compromised",
    })
    obligations.append({
        "regulation": "PCI DSS",
        "action": "Notify card brands",
        "deadline": "24 hours",
        "required": "If cardholder data compromised",
    })

    return obligations


def calculate_countdown(t0_str: str) -> Dict[str, Any]:
    """Calculate time remaining for various deadlines from T0."""
    try:
        t0 = datetime.fromisoformat(t0_str)
    except ValueError:
        return {"error": f"Invalid T0 format: {t0_str}. Use ISO: YYYY-MM-DDTHH:MM:SS"}
    now = datetime.now()
    elapsed_hours = (now - t0).total_seconds() / 3600
    deadlines: Dict[str, Any] = {}
    dl_defs = [("gdpr_72h", GDPR_HOURS, 12), ("nis2_24h_ew", NIS2_EW_HOURS, 6),
               ("nis2_72h", NIS2_HOURS, 12), ("pci_24h", PCI_HOURS, 6)]
    for name, hours, urgent_thresh in dl_defs:
        deadline_time = t0 + timedelta(hours=hours)
        remaining = (deadline_time - now).total_seconds() / 3600
        status = "EXPIRED" if remaining <= 0 else "URGENT" if remaining <= urgent_thresh else "OK"
        deadlines[name] = {"deadline": deadline_time.isoformat(), "remaining_hours": round(remaining, 1),
                           "expired": remaining <= 0, "status": status}
    return {"t0": t0.isoformat(), "current_time": now.isoformat(),
            "elapsed_hours": round(elapsed_hours, 1), "deadlines": deadlines}


def generate_template() -> Dict[str, Any]:
    """Generate input template."""
    return {"dpc": {"value": 0, "options": "1=Simple demographic, 2=Behavioral/financial, 3=Sensitive, 4=Special category"},
            "ei": {"value": 0, "options": "0.25=Negligible, 0.5=Limited, 0.75=Significant, 1.0=Maximum"},
            "confidentiality_loss": 0, "integrity_loss": 0, "availability_loss": 0,
            "malicious_intent": False, "t0": "YYYY-MM-DDTHH:MM:SS"}


def format_human(
    dpc: int, ei: float, cb: float, cb_components: Dict[str, float],
    se: float, verdict: str, description: str,
    obligations: List[Dict[str, str]], countdown: Optional[Dict[str, Any]],
) -> str:
    """Format results for human-readable output."""
    lines: List[str] = ["=" * 65, "DATA BREACH SEVERITY ASSESSMENT", "=" * 65, "",
        f"  DPC: {dpc} ({DPC_LABELS.get(dpc, '?')})  |  EI: {ei} ({EI_LABELS.get(ei, '?')})", ""]
    lines.append("  CB components: " + ", ".join(f"{k.replace('_',' ').title()}: {v}" for k, v in cb_components.items()))
    lines.append(f"\n  SE = ({dpc} x {ei}) + {round(cb, 2)} = {se}")
    lines.append(f"\n  VERDICT: {verdict}\n  {description}\n")
    if countdown and "error" not in countdown:
        lines.append(f"DEADLINES (T0: {countdown['t0']}, elapsed: {countdown['elapsed_hours']}h):")
        for name, dl in countdown["deadlines"].items():
            icon = "!!!" if dl["status"] == "EXPIRED" else ">>>" if dl["status"] == "URGENT" else "   "
            lines.append(f"  {icon} {name}: {dl['remaining_hours']}h [{dl['status']}]")
        lines.append("")
    lines.append("NOTIFICATION OBLIGATIONS:")
    for ob in obligations:
        lines.append(f"  [{ob['regulation']}] {ob['action']} | Deadline: {ob['deadline']} | {ob['required']}")
    lines.append("=" * 65)
    return "\n".join(lines)


def format_json_output(
    dpc: int, ei: float, cb: float, cb_components: Dict[str, float],
    se: float, verdict: str, description: str,
    obligations: List[Dict[str, str]],
    countdown: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    """Format results as JSON."""
    result: Dict[str, Any] = {
        "calculated": datetime.now().isoformat(),
        "parameters": {
            "dpc": {"value": dpc, "label": DPC_LABELS.get(dpc, "Unknown")},
            "ei": {"value": ei, "label": EI_LABELS.get(ei, "Unknown")},
            "cb": {"value": round(cb, 2), "components": cb_components},
        },
        "formula": f"SE = ({dpc} x {ei}) + {round(cb, 2)} = {se}",
        "severity_score": se,
        "verdict": verdict,
        "description": description,
        "notification_obligations": obligations,
    }
    if countdown:
        result["countdown"] = countdown
    return result


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Breach Severity Calculator — ENISA methodology"
    )
    parser.add_argument("--dpc", type=int, choices=[1, 2, 3, 4],
                        help="Data Processing Context (1-4)")
    parser.add_argument("--ei", type=float,
                        help="Ease of Identification (0.25, 0.5, 0.75, 1.0)")
    parser.add_argument("--confidentiality", type=float, default=0.0,
                        help="Confidentiality loss (0, 0.25, 0.5)")
    parser.add_argument("--integrity", type=float, default=0.0,
                        help="Integrity loss (0, 0.25, 0.5)")
    parser.add_argument("--availability", type=float, default=0.0,
                        help="Availability loss (0, 0.25, 0.5)")
    parser.add_argument("--malicious", action="store_true",
                        help="Breach involved malicious intent")
    parser.add_argument("--t0", type=str,
                        help="T0 timestamp (ISO format) for deadline calculation")
    parser.add_argument("--template", action="store_true",
                        help="Generate input template")
    parser.add_argument("--json", action="store_true",
                        help="Output in JSON format")

    args = parser.parse_args()

    if args.template:
        print(json.dumps(generate_template(), indent=2))
        return

    if args.dpc is None or args.ei is None:
        parser.error("--dpc and --ei are required (or use --template)")

    # Validate EI
    valid_ei = [0.25, 0.5, 0.75, 1.0]
    if args.ei not in valid_ei:
        print(f"Error: --ei must be one of {valid_ei}", file=sys.stderr)
        sys.exit(1)

    # Validate loss values
    valid_loss = [0.0, 0.25, 0.5]
    for name, val in [("confidentiality", args.confidentiality),
                      ("integrity", args.integrity),
                      ("availability", args.availability)]:
        if val not in valid_loss:
            print(f"Error: --{name} must be one of {valid_loss}", file=sys.stderr)
            sys.exit(1)

    # Calculate
    cb, cb_components = calculate_cb(
        args.confidentiality, args.integrity, args.availability, args.malicious
    )
    se, verdict, description = calculate_severity(args.dpc, args.ei, cb)
    obligations = get_notification_obligations(verdict)

    countdown = None
    if args.t0:
        countdown = calculate_countdown(args.t0)

    if args.json:
        result = format_json_output(
            args.dpc, args.ei, cb, cb_components,
            se, verdict, description, obligations, countdown
        )
        print(json.dumps(result, indent=2))
    else:
        output = format_human(
            args.dpc, args.ei, cb, cb_components,
            se, verdict, description, obligations, countdown
        )
        print(output)


if __name__ == "__main__":
    main()
