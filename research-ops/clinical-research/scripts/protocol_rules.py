#!/usr/bin/env python3
"""Rule definitions for protocol_auditor.py — what a protocol must contain.

Holds the ICH E6 required-section table and its guidance strings, the thresholds
the checks compare against, the severity ordering used when reporting, and the
Finding accumulator the check rules write into. Separated from the auditor so
the domain content can be reviewed and revised by clinical and regulatory
readers without touching traversal or reporting logic.

The section descriptions are user-facing guidance: they are what a study planner
reads to learn what belongs in a missing section, and several track ICH E6
section naming. Revise them for accuracy, never to save space.

Helper module: imported by its sibling, not run directly.
"""

from __future__ import annotations

from dataclasses import dataclass

# Protocol contents expected by ICH E6, normalised to short keys.
REQUIRED_SECTIONS: dict[str, str] = {
    "general_information": "Protocol ID, sponsor, investigators, sites",
    "background": "Rationale, prior data, benefit-risk justification",
    "objectives": "Primary and secondary objectives",
    "design": "Trial design, randomisation, blinding, duration",
    "eligibility": "Selection and withdrawal of subjects",
    "treatment": "Treatment of subjects, dose, concomitant medication rules",
    "efficacy_assessment": "Efficacy endpoints, methods, timing",
    "safety_assessment": "Safety parameters, AE definitions and reporting",
    "statistics": "Statistical methods, sample size, analysis populations",
    "source_data_access": "Direct access to source data and documents",
    "quality_control": "Quality control and quality assurance",
    "ethics": "Ethics committee review, informed consent",
    "data_handling": "Data handling and record keeping, retention period",
    "financing_insurance": "Financing and insurance arrangements",
    "publication_policy": "Publication policy",
}

# Endpoint measures naming only a direction of travel, with no instrument,
# scale, or counted event behind them — unanalysable as written.
VAGUE_MEASURE_TERMS = ("improvement", "benefit", "efficacy", "effectiveness",
                       "response", "success", "outcome", "quality")

# Confirmatory phases, where independent safety oversight is the expectation
# rather than a design choice.
PHASES_REQUIRING_DSMB = ("3", "III", "4", "IV")

# ICH E6 expects serious adverse events to reach the sponsor immediately;
# 24 hours is the window a reviewer will look for.
MAX_SAE_WINDOW_HOURS = 24

# Report ordering: blocking defects before advisory ones.
SEVERITY_ORDER: dict[str, int] = {"fail": 0, "warn": 1}

DISCLAIMER = ("Structural and consistency check only. Not a regulatory "
              "review; requires qualified regulatory affairs and clinical "
              "sign-off before submission.")


@dataclass
class Finding:
    """A defect or gap detected in the protocol outline."""

    severity: str
    area: str
    message: str


class Findings(list):
    """Accumulator for findings, so each check reads as one line per rule."""

    def add(self, severity: str, area: str, message: str) -> None:
        """Record one finding."""
        self.append(Finding(severity, area, message))
