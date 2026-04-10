---
name: legal-risk-assessment
description: >
  Structured legal risk assessment with 5x5 Severity x Likelihood matrix. Use
  for risk scoring, risk registers, escalation decisions, and risk memos.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: The Glass Room
  category: legal
  domain: risk-management
  updated: 2026-04-10
  tags: [legal-risk, risk-matrix, risk-register, escalation, compliance]
---
> **⚠️ EXPERIMENTAL** — This skill is provided for educational and informational purposes only. It does NOT constitute legal advice. All responsibility for usage rests with the user. Consult qualified legal professionals before acting on any output.

# Legal Risk Assessment

Structured legal risk assessment using a quantitative 5x5 Severity x Likelihood matrix. Scores risks, maintains registers, generates assessment memos, and guides escalation decisions.

---

## Table of Contents

- [Tools](#tools)
  - [Risk Scorer](#risk-scorer)
  - [Risk Report Generator](#risk-report-generator)
- [Reference Guides](#reference-guides)
- [Workflows](#workflows)
- [Troubleshooting](#troubleshooting)
- [Success Criteria](#success-criteria)
- [Scope & Limitations](#scope--limitations)
- [Anti-Patterns](#anti-patterns)
- [Tool Reference](#tool-reference)

---

## Tools

### Risk Scorer

Calculates risk scores from severity and likelihood inputs, assigns color-coded risk levels, and generates summary statistics.

```bash
# Score a single risk
python scripts/risk_scorer.py --severity 4 --likelihood 3 \
  --category "Contract" --description "Vendor SLA non-compliance"

# JSON output
python scripts/risk_scorer.py --severity 4 --likelihood 3 \
  --category "Contract" --description "Vendor SLA breach" --json

# Batch mode from risk register file
python scripts/risk_scorer.py --input risks.json --json

# Batch mode with human-readable output
python scripts/risk_scorer.py --input risks.json
```

**Input JSON format (batch mode):**
```json
{
  "risks": [
    {"severity": 4, "likelihood": 3, "category": "Contract", "description": "Vendor SLA breach"},
    {"severity": 2, "likelihood": 2, "category": "Regulatory", "description": "Minor filing delay"}
  ]
}
```

**Output includes:**
- Risk score (Severity x Likelihood)
- Color-coded level (GREEN / YELLOW / ORANGE / RED)
- Recommended action (Accept / Monitor / Mitigate / Escalate)
- Batch summary statistics (count per level, average score)

---

### Risk Report Generator

Generates a formatted risk assessment memo in markdown from a risk register JSON file.

```bash
# Generate memo from risk register
python scripts/risk_report_generator.py --input risk_register.json

# Save to file
python scripts/risk_report_generator.py --input risk_register.json --output memo.md

# JSON metadata output
python scripts/risk_report_generator.py --input risk_register.json --json
```

**Report includes:**
- ASCII risk matrix visualization
- Risk distribution summary (counts and percentages per level)
- Top risks ranked by score
- Recommended actions per risk with owner assignments
- Monitoring plan suggestions
- Escalation recommendations

---

## Reference Guides

### Risk Framework
`references/risk_framework.md`

Complete Severity x Likelihood matrix reference:
- Severity levels 1-5 with financial exposure percentages
- Likelihood levels 1-5 with probability ranges
- Risk matrix visualization
- Risk classification (GREEN/YELLOW/ORANGE/RED) with actions
- Documentation standards for memos and register entries

### Escalation Guide
`references/escalation_guide.md`

When to engage outside counsel:
- Mandatory engagement triggers (litigation, investigation, criminal)
- Strongly recommended scenarios (novel issues, material exposure)
- Consider scenarios (complex disputes, employment, data incidents)
- Risk category definitions and contributing/mitigating factors

---

## Workflows

### Workflow 1: New Risk Assessment

```
Step 1: Identify risk category and description
        → Use references/risk_framework.md category definitions

Step 2: Score severity (1-5) and likelihood (1-5)
        → python scripts/risk_scorer.py --severity N --likelihood N \
          --category "Category" --description "Description"

Step 3: Review risk level and recommended action
        → GREEN: Accept and document
        → YELLOW: Assign owner and monitor
        → ORANGE: Escalate to senior counsel
        → RED: Immediate escalation, crisis management

Step 4: Determine outside counsel need
        → Consult references/escalation_guide.md

Step 5: Document in risk register
        → Add entry to register JSON file
```

### Workflow 2: Periodic Risk Register Review

```
Step 1: Load current risk register
        → python scripts/risk_scorer.py --input register.json

Step 2: Generate assessment memo
        → python scripts/risk_report_generator.py --input register.json --output memo.md

Step 3: Review top risks and distribution
        → Focus on ORANGE and RED risks first

Step 4: Update severity/likelihood for changed risks
        → Re-score and regenerate report

Step 5: Distribute memo to stakeholders
```

### Workflow 3: Escalation Decision

```
Step 1: Score the risk
        → python scripts/risk_scorer.py --severity N --likelihood N \
          --category "Category" --description "Description"

Step 2: Check escalation triggers
        → Mandatory: active litigation, government investigation, criminal exposure
        → Strongly Recommended: novel issues, jurisdictional complexity, material exposure
        → Consider: complex disputes, employment matters, data incidents

Step 3: Document escalation rationale
        → Include risk score, level, and specific trigger in memo

Step 4: Select outside counsel if needed
        → See references/escalation_guide.md criteria
```

---

## Troubleshooting

| Problem | Possible Cause | Resolution |
|---------|---------------|------------|
| Risk score seems too low for a serious matter | Severity or likelihood underestimated; qualitative factors not captured | Review severity descriptions in risk_framework.md; consider worst-case financial exposure; add contributing factors to description |
| Multiple risks in same category but different scores | Risks have different severity/likelihood combinations | This is expected; each risk is independent; review category-level trends in report |
| Batch mode fails on input file | Malformed JSON or missing required fields | Verify JSON structure matches expected format; ensure each risk has severity, likelihood, category, description |
| Report generator produces empty matrix | No risks in input file or all risks have invalid scores | Check that input JSON contains valid risks with severity 1-5 and likelihood 1-5 |
| Escalation guide suggests outside counsel but budget is constrained | Risk score indicates material exposure | Document the budget constraint and residual risk acceptance; consider limited-scope engagement |
| Risk register grows unwieldy | Risks not being closed or consolidated | Archive resolved risks; consolidate related risks; review register quarterly |

---

## Success Criteria

- **All identified legal risks scored and documented** -- every risk has severity, likelihood, category, description, and recommended action in the register
- **Risk distribution reviewed quarterly** -- memo generated and distributed to stakeholders with trend analysis
- **ORANGE and RED risks have assigned owners and mitigation plans** -- no high-severity risk without accountability
- **Escalation decisions documented with rationale** -- outside counsel engagement triggers clearly recorded
- **Risk register maintained as living document** -- risks updated, resolved, or archived as status changes

---

## Scope & Limitations

**In Scope:**
- Quantitative risk scoring using 5x5 Severity x Likelihood matrix
- Risk register management and batch processing
- Risk assessment memo generation with matrix visualization
- Escalation guidance for outside counsel engagement
- Risk categorization (Contract, Regulatory, Litigation, IP, Data Privacy, Employment, Corporate)

**Out of Scope:**
- Legal advice on specific risk mitigation strategies -- consult legal counsel
- Insurance coverage analysis or actuarial calculations
- Regulatory filing or submission preparation
- Contract drafting or review
- Litigation strategy or case management

---

## Anti-Patterns

- **Scoring by committee consensus without criteria** -- use the defined severity and likelihood scales consistently; do not negotiate scores to make stakeholders comfortable; a risk scored as 4 severity should match the framework definition
- **Treating the risk register as a one-time exercise** -- risk registers are living documents; risks change as circumstances evolve; schedule quarterly reviews and update scores accordingly
- **Escalating everything to outside counsel** -- the escalation guide defines specific triggers; not every YELLOW risk needs external counsel; over-escalation wastes budget and creates dependency
- **Ignoring GREEN risks entirely** -- GREEN risks still require documentation and periodic monitoring; a GREEN risk can escalate to YELLOW or ORANGE if circumstances change
- **Using risk scores as the sole decision factor** -- scores are inputs to judgment, not substitutes; qualitative factors like reputational impact or strategic importance may warrant action beyond what the score suggests

---

## Tool Reference

### risk_scorer.py

Calculates risk scores and assigns color-coded risk levels with recommended actions.

| Flag | Required | Description |
|------|----------|-------------|
| `--severity <1-5>` | Yes (single mode) | Severity rating: 1=Negligible, 2=Minor, 3=Moderate, 4=Major, 5=Critical |
| `--likelihood <1-5>` | Yes (single mode) | Likelihood rating: 1=Remote, 2=Unlikely, 3=Possible, 4=Likely, 5=Almost Certain |
| `--category <text>` | Yes (single mode) | Risk category: Contract, Regulatory, Litigation, IP, Data Privacy, Employment, Corporate |
| `--description <text>` | Yes (single mode) | Risk description |
| `--input <file>` | Yes (batch mode) | Path to JSON file containing multiple risks |
| `--json` | No | Output results in JSON format |

### risk_report_generator.py

Generates formatted risk assessment memo from a risk register JSON file.

| Flag | Required | Description |
|------|----------|-------------|
| `--input <file>` | Yes | Path to risk register JSON file |
| `--output <file>` | No | Save memo to specified file path (markdown format) |
| `--json` | No | Output report metadata in JSON format |
