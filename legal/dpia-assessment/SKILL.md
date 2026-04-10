---
name: dpia-assessment
description: >
  GDPR Art. 35 Data Protection Impact Assessment with threshold checking,
  risk registers, and EDPB criteria scoring. Use for DPIA evaluations.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: The Glass Room
  category: legal
  domain: data-protection
  updated: 2026-04-10
  tags: [dpia, gdpr, data-protection, edpb, privacy-risk]
---
> **⚠️ EXPERIMENTAL** — This skill is provided for educational and informational purposes only. It does NOT constitute legal advice. All responsibility for usage rests with the user. Consult qualified legal professionals before acting on any output.

# DPIA Assessment

GDPR Article 35 Data Protection Impact Assessment tooling. Evaluates whether a DPIA is required, manages risk registers with mitigation tracking, and generates documentation meeting supervisory authority expectations.

---

## Table of Contents

- [Tools](#tools)
  - [DPIA Threshold Checker](#dpia-threshold-checker)
  - [DPIA Risk Register](#dpia-risk-register)
- [Reference Guides](#reference-guides)
- [Workflows](#workflows)
- [Legal Precision Points](#legal-precision-points)
- [Output Formats](#output-formats)
- [Troubleshooting](#troubleshooting)
- [Success Criteria](#success-criteria)
- [Scope & Limitations](#scope--limitations)
- [Anti-Patterns](#anti-patterns)
- [Tool Reference](#tool-reference)

---

## Tools

### DPIA Threshold Checker

Evaluates whether a DPIA is required based on processing activity description. Checks Art. 35(3) mandatory triggers and 9 EDPB criteria.

```bash
# Check a processing activity (interactive prompts)
python scripts/dpia_threshold_checker.py --activity "AI-based credit scoring using financial and behavioral data of retail banking customers across EU"

# Check from JSON description
python scripts/dpia_threshold_checker.py --input processing.json

# JSON output
python scripts/dpia_threshold_checker.py --activity "Employee monitoring via CCTV in workplace" --json

# Generate blank input template
python scripts/dpia_threshold_checker.py --template > processing.json
```

**Checks performed:**
- Art. 35(3)(a): Automated decision-making with legal/significant effect
- Art. 35(3)(b): Large-scale processing of special category data (Art. 9) or criminal data (Art. 10)
- Art. 35(3)(c): Systematic monitoring of publicly accessible area on large scale
- 9 EDPB criteria from WP 248 rev.01 with two-criterion presumption rule

**Output:**
- Verdict: Required / Recommended / Not Required
- Art. 35(3) trigger matches
- EDPB criteria scores with reasoning
- Two-criterion presumption analysis

---

### DPIA Risk Register

Manages a DPIA risk register in JSON format. Add risks, apply mitigations, and calculate residual risk.

```bash
# Initialize a new risk register
python scripts/dpia_risk_register.py init --output dpia_risks.json

# Add a risk
python scripts/dpia_risk_register.py add --register dpia_risks.json \
  --description "Unauthorized access to profiling data" \
  --rights-category "right-to-privacy" \
  --likelihood 4 --severity 3

# Add mitigation to a risk
python scripts/dpia_risk_register.py mitigate --register dpia_risks.json \
  --risk-id 1 --measure "Implement role-based access control" \
  --likelihood-reduction 2 --severity-reduction 1

# View risk register table
python scripts/dpia_risk_register.py view --register dpia_risks.json

# Generate residual risk summary
python scripts/dpia_risk_register.py summary --register dpia_risks.json --json

# Check Art. 36 consultation threshold
python scripts/dpia_risk_register.py art36-check --register dpia_risks.json
```

**Rights categories:** right-to-privacy, non-discrimination, freedom-of-expression, right-to-information, right-to-not-be-subject-to-automated-decisions, right-to-physical-safety

---

## Reference Guides

### EDPB Criteria
`references/edpb_criteria.md`

Complete EDPB 9-criteria assessment framework:
- Each criterion with description, indicators, and scoring guidance
- Art. 35(3) mandatory triggers
- Two-criterion presumption rule (WP 248 rev.01)
- Multi-jurisdictional DPIA analysis
- National blacklist/whitelist overview (DE, FR, IE, BE, NL, IT, PL)

### Risk Scoring Methodology
`references/risk_scoring_methodology.md`

DPIA risk scoring from the data subject perspective:
- Likelihood and severity scales (1-5)
- Rights categories per Recital 75
- Risk level thresholds (Low/Medium/High/Very High)
- Mitigation effectiveness scoring
- Residual risk calculation
- Art. 36 consultation triggers
- Risk catalog: 20+ common DPIA risks

---

## Workflows

### Workflow 1: Full DPIA Assessment

```
Step 1: Threshold check — determine if DPIA required
        → python scripts/dpia_threshold_checker.py --activity "description"

Step 2: If Required or Recommended, describe the processing
        → Document purpose, legal basis, data categories, recipients, retention

Step 3: Assess necessity and proportionality
        → Confirm lawful basis (Art. 6, cumulative with Art. 9 if special categories)
        → Verify purpose limitation, data minimization, storage limitation

Step 4: Identify risks from data subject perspective
        → python scripts/dpia_risk_register.py init --output dpia_risks.json
        → Add risks using references/risk_scoring_methodology.md catalog

Step 5: Apply mitigations and calculate residual risk
        → python scripts/dpia_risk_register.py mitigate --register dpia_risks.json ...

Step 6: Check Art. 36 consultation requirement
        → python scripts/dpia_risk_register.py art36-check --register dpia_risks.json

Step 7: Document and review
        → python scripts/dpia_risk_register.py summary --register dpia_risks.json
```

### Workflow 2: Quick Threshold Assessment

```
Step 1: Describe the processing activity
        → python scripts/dpia_threshold_checker.py --template > processing.json
        → Fill in processing details

Step 2: Run threshold check
        → python scripts/dpia_threshold_checker.py --input processing.json --json

Step 3: Review verdict and reasoning
        → Required: proceed to full DPIA (Workflow 1)
        → Recommended: proceed unless strong justification to skip (document)
        → Not Required: document the assessment and rationale
```

### Workflow 3: AI System DPIA

```
Step 1: Classify AI system (EU AI Act risk level if applicable)
        → Map to DPIA triggers (automated decision-making, profiling, scoring)

Step 2: Run threshold check with AI-specific indicators
        → python scripts/dpia_threshold_checker.py --activity "AI system description"

Step 3: Dual-phase risk analysis (EDPB Opinion 28/2024)
        → Phase 1: Training data risks (collection, bias, consent)
        → Phase 2: Inference risks (decisions, profiling, transparency)

Step 4: Assess from data subject perspective
        → Add risks covering both training and inference phases
        → Include algorithmic bias, lack of transparency, unfair outcomes

Step 5: Apply mitigations specific to AI
        → Explainability measures, human oversight, bias testing
        → Document FRIA distinction per EU AI Act Art. 27 if applicable
```

---

## Legal Precision Points

12 points of legal precision that distinguish expert-level DPIA work.

| # | Point | Detail |
|---|-------|--------|
| 1 | **Art. 35(3) absolute triggers** | Three mandatory triggers require DPIA regardless of other analysis: (a) automated decisions with legal effect, (b) large-scale special category/criminal data, (c) systematic public area monitoring |
| 2 | **Two-criterion presumption** | If 2 or more of the 9 EDPB criteria are met, DPIA is presumptively required (WP 248 rev.01). Can rebut only with documented justification |
| 3 | **Art. 9 cumulative with Art. 6** | Special category data requires BOTH an Art. 6 lawful basis AND an Art. 9(2) exception. Neither alone is sufficient |
| 4 | **Large scale four-factor test** | Assess: (a) number of data subjects, (b) volume of data, (c) geographic extent, (d) duration/permanence. No fixed numeric threshold |
| 5 | **National blacklists additive** | SA-published lists of processing operations requiring DPIA add to (not replace) Art. 35(3) and EDPB criteria |
| 6 | **Multi-jurisdictional checking** | If processing spans multiple member states, check each SA's blacklist. Most restrictive list applies |
| 7 | **Pre-processing obligation** | DPIA must be completed BEFORE processing begins (Art. 35(1)). Retroactive DPIAs do not satisfy the requirement |
| 8 | **AI dual-phase analysis** | EDPB Opinion 28/2024: AI systems require separate risk analysis for training phase and inference/deployment phase |
| 9 | **Art. 36 sequential** | Prior consultation with SA (Art. 36) is triggered only AFTER DPIA is completed and residual risk remains high. Cannot skip the DPIA |
| 10 | **Pseudonymization nuance** | EDPB Guidelines 01/2025: pseudonymization reduces risk but does not eliminate DPIA requirement. Still personal data |
| 11 | **Data subject perspective** | All risks must be assessed from the data subject's perspective (Recital 75), not the controller's business perspective |
| 12 | **AI Act FRIA distinction** | EU AI Act Art. 27 requires Fundamental Rights Impact Assessment (FRIA) for high-risk AI. FRIA is separate from GDPR DPIA — both may be required |

---

## Output Formats

### Threshold Verdict

```
VERDICT: DPIA REQUIRED
Reason: Art. 35(3)(a) trigger matched (automated decision-making with legal effect)
        + 4 of 9 EDPB criteria met (two-criterion presumption applies)
Matched triggers: automated_decision_making, evaluation_scoring, sensitive_data, large_scale
```

### Risk Register Table

| ID | Description | Rights Category | L | S | Score | Level | Mitigation | Residual L | Residual S | Residual Score | Residual Level |
|----|-------------|-----------------|---|---|-------|-------|------------|------------|------------|---------------|---------------|
| 1 | Unauthorized profiling | Right to privacy | 4 | 3 | 12 | High | RBAC + encryption | 2 | 2 | 4 | Low |
| 2 | Discriminatory outcomes | Non-discrimination | 3 | 4 | 12 | High | Bias testing + human review | 2 | 3 | 6 | Medium |

### Residual Risk Overview

```
Total risks: 8
Mitigated: 6 (75%)
Residual risk distribution:
  Low:       3 (37.5%)
  Medium:    3 (37.5%)
  High:      2 (25.0%)
  Very High: 0 (0.0%)

Art. 36 consultation: NOT TRIGGERED (no Very High residual risks)
```

---

## Troubleshooting

| Problem | Possible Cause | Resolution |
|---------|---------------|------------|
| Threshold checker says "Not Required" but processing feels risky | Activity description too vague or missing key details | Provide more specific description including data types, scale, automation level, and data subject categories |
| Two-criterion presumption triggered but controller disagrees | Controller must document justification for rebutting presumption | Document specific reasons why DPIA is not needed despite criteria match; SA may challenge this |
| Risk register shows High residual risk after mitigations | Mitigations insufficient or not properly scored | Review mitigation effectiveness; consider additional controls; if residual risk remains high, Art. 36 consultation required |
| Multi-jurisdictional check produces conflicting results | Different SAs have different blacklists and thresholds | Apply the most restrictive requirement; document the analysis for each jurisdiction |
| AI system DPIA unclear on training vs. inference risks | Training and inference phases have different risk profiles | Separate the analysis per EDPB Opinion 28/2024; assess each phase independently then combine |
| Art. 36 check unclear on threshold | Residual risk near the boundary between High and Very High | Document the borderline assessment; consider voluntary consultation as good practice |

---

## Success Criteria

- **All high-risk processing activities assessed** -- threshold check completed before processing begins, with documented verdict and reasoning
- **Risk register complete with mitigations** -- every identified risk has likelihood, severity, rights category, and at least one mitigation measure
- **Residual risk acceptable or Art. 36 consultation initiated** -- no unaddressed Very High residual risks
- **Documentation meets SA expectations** -- assessment follows Art. 35(7) requirements: systematic description, necessity/proportionality, risks, mitigations
- **EDPB criteria properly applied** -- two-criterion presumption correctly evaluated with documented reasoning

---

## Scope & Limitations

**In Scope:**
- DPIA threshold assessment against Art. 35(3) triggers and EDPB criteria
- Risk register management with mitigation tracking and residual risk calculation
- Art. 36 prior consultation threshold assessment
- Multi-jurisdictional blacklist awareness (DE, FR, IE, BE, NL, IT, PL)
- AI system dual-phase DPIA analysis guidance
- Data subject perspective risk assessment per Recital 75

**Out of Scope:**
- Legal advice on lawful basis selection (Art. 6) or Art. 9(2) exception applicability
- Supervisory authority submission or interaction
- Technical implementation of mitigations (encryption, access control)
- DPO appointment or consultation logistics
- National blacklist exhaustive coverage beyond listed jurisdictions
- EU AI Act conformity assessment (see eu-ai-act-specialist)

---

## Anti-Patterns

- **Conducting DPIA after processing has started** -- Art. 35(1) requires DPIA before processing begins; retroactive DPIAs do not satisfy the legal obligation and create enforcement exposure
- **Assessing risk from the controller's perspective** -- DPIA risks must be evaluated from the data subject's perspective per Recital 75; business impact is irrelevant to this analysis; a breach that is minor for the company may be catastrophic for affected individuals
- **Treating pseudonymization as eliminating DPIA need** -- pseudonymized data remains personal data under GDPR (Recital 26); pseudonymization is a mitigation that reduces risk scores, not a basis for skipping the DPIA entirely
- **Skipping Art. 36 consultation when residual risk is high** -- if residual risk remains Very High after mitigations, prior consultation with the supervisory authority is mandatory, not optional
- **Conflating DPIA with FRIA** -- the EU AI Act's Fundamental Rights Impact Assessment (Art. 27) is a separate obligation from GDPR DPIA; completing one does not satisfy the other; both may be required for AI systems processing personal data

---

## Tool Reference

### dpia_threshold_checker.py

Evaluates whether a DPIA is required based on Art. 35(3) triggers and EDPB criteria.

| Flag | Required | Description |
|------|----------|-------------|
| `--activity <text>` | Yes (unless `--input` or `--template`) | Processing activity description |
| `--input <file>` | Yes (unless `--activity`) | Path to JSON processing description |
| `--template` | No | Generate blank input template |
| `--json` | No | Output in JSON format |

### dpia_risk_register.py

Manages DPIA risk register with mitigation tracking and residual risk calculation.

| Subcommand | Description |
|------------|-------------|
| `init` | Create new empty risk register (`--output` required) |
| `add` | Add risk (`--register`, `--description`, `--rights-category`, `--likelihood`, `--severity` required) |
| `mitigate` | Add mitigation (`--register`, `--risk-id`, `--measure`, `--likelihood-reduction`, `--severity-reduction` required) |
| `view` | Display risk register table (`--register` required) |
| `summary` | Generate summary with distribution (`--register` required, `--json` optional) |
| `art36-check` | Check Art. 36 consultation requirement (`--register` required) |
