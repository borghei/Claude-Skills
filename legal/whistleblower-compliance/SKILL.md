---
name: whistleblower-compliance
description: >
  Audit whistleblower systems and draft compliant reporting policies. Use when assessing or building whistleblower programs.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: The Glass Room
  category: legal
  domain: compliance
  updated: 2026-04-10
  tags: [whistleblower, compliance, eu-directive-2019-1937, sox, dodd-frank]
---
> **⚠️ EXPERIMENTAL** — This skill is provided for educational and informational purposes only. It does NOT constitute legal advice. All responsibility for usage rests with the user. Consult qualified legal professionals before acting on any output.

# Whistleblower Compliance Skill

## Overview

Production-ready whistleblower compliance toolkit for auditing existing reporting systems and drafting compliant policies. Covers EU Directive 2019/1937, US SOX Section 806, US Dodd-Frank, and UK Public Interest Disclosure Act 1998. Operates in two modes: Mode A (Assessment) runs an 8-phase, 56-checkpoint audit of existing systems; Mode B (Drafting) generates jurisdiction-specific reporting policies.

## Table of Contents

- [Tools](#tools)
- [Reference Guides](#reference-guides)
- [Workflows](#workflows)
- [Troubleshooting](#troubleshooting)
- [Success Criteria](#success-criteria)
- [Scope & Limitations](#scope--limitations)
- [Anti-Patterns](#anti-patterns)
- [Tool Reference](#tool-reference)

## Tools

### 1. Compliance Checker (`scripts/whistleblower_compliance_checker.py`)

Assess an existing whistleblower system against regulatory requirements. Takes organizational parameters and outputs a compliance score with priority-classified gaps.

```bash
python scripts/whistleblower_compliance_checker.py \
  --jurisdiction EU --headcount 300 --sector financial \
  --channels internal,external --has-designated-person \
  --has-confidentiality --has-gdpr-measures --has-dissemination

python scripts/whistleblower_compliance_checker.py \
  --jurisdiction US --headcount 5000 --sector healthcare \
  --channels internal --json

python scripts/whistleblower_compliance_checker.py \
  --jurisdiction UK --headcount 50 --sector technology \
  --channels none
```

### 2. Policy Scaffolder (`scripts/whistleblower_policy_scaffolder.py`)

Generate a whistleblower policy skeleton pre-populated with required sections per regulatory framework.

```bash
python scripts/whistleblower_policy_scaffolder.py \
  --jurisdiction EU --org-type private --headcount 500 \
  --org-name "Acme Corp"

python scripts/whistleblower_policy_scaffolder.py \
  --jurisdiction US --org-type public --headcount 10000 \
  --org-name "MegaCorp Inc" --json

python scripts/whistleblower_policy_scaffolder.py \
  --jurisdiction UK --org-type nonprofit --headcount 100 \
  --org-name "CharityOrg" --output policy-draft.md
```

## Reference Guides

| Reference | Purpose |
|-----------|---------|
| `references/regulatory_framework.md` | Multi-jurisdiction whistleblower regulations, comparison matrix |
| `references/assessment_checklist.md` | 8-phase, 56-checkpoint assessment with priority classifications |

## Workflows

### Mode A: Assessment Workflow

1. **Gather Parameters** -- Collect jurisdiction, headcount, sector, and system description
2. **Run Compliance Checker** -- Execute `whistleblower_compliance_checker.py` with parameters
3. **Review Gaps** -- Prioritize CRITICAL gaps first, then IMPORTANT, then IMPROVEMENT
4. **Cross-Reference Checklist** -- Walk through `assessment_checklist.md` for manual verification
5. **Generate Remediation Plan** -- Address gaps by priority, set deadlines per regulatory timelines

### Mode B: Drafting Workflow

1. **Determine Jurisdiction** -- Identify applicable regulations based on headquarters and operations
2. **Generate Scaffold** -- Run `whistleblower_policy_scaffolder.py` with organization details
3. **Customize Sections** -- Replace placeholders with organization-specific information
4. **Legal Review** -- Route draft through legal counsel for jurisdiction-specific validation
5. **Approval & Publication** -- Obtain board/management approval and disseminate to all personnel

### 8-Phase Assessment Framework

| Phase | Focus | Checkpoints |
|-------|-------|-------------|
| 1. Applicability | Regulatory scope determination | 3 |
| 2. Reception Channel | Reporting channel adequacy | 5 |
| 3. Designated Persons | Personnel and independence | 7 |
| 4. Verification/Processing | Investigation procedures | 8 |
| 5. Confidentiality | Identity and data protection | 9 |
| 6. Dissemination/Information | Awareness and accessibility | 10 |
| 7. Data Protection/GDPR | Privacy compliance | 12 |
| 8. Sector-Specific | Industry requirements | 6 |
| **Total** | | **60** |

### Three Reporting Channels

| Channel | When Used | Key Requirements |
|---------|-----------|-----------------|
| Internal | First preference; report to organization | Acknowledge within 7 days; feedback within 3 months |
| External (Regulatory) | When internal fails or is inappropriate | Report to competent authority; same protections apply |
| Public Disclosure | Last resort; imminent danger or retaliation | Protected only if internal/external channels exhausted |

### Whistleblower Protections

| Protection | Description |
|------------|-------------|
| Civil immunity | No liability for breach of confidentiality obligations |
| Criminal immunity | No criminal liability for acquiring reported information |
| Prohibited retaliation | Dismissal, demotion, harassment, blacklisting, discrimination |
| Burden of proof reversal | Employer must prove action was not retaliatory |
| Interim relief | Provisional protection during investigation |
| Legal aid access | Access to legal counsel and support |

### Priority Classification

| Priority | Definition | Example |
|----------|-----------|---------|
| CRITICAL | Legal non-compliance; immediate regulatory risk | No reporting channel exists; no confidentiality measures |
| IMPORTANT | Significant gap reducing system effectiveness | Acknowledgment timeline exceeds 7 days; no designated person |
| IMPROVEMENT | Enhancement opportunity; not currently non-compliant | Training frequency below best practice; limited channel types |

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| Checker reports all CRITICAL | No system parameters provided | Provide accurate `--channels`, `--has-designated-person`, and other flags |
| Wrong jurisdiction requirements | Multi-jurisdiction entity using single jurisdiction | Run checker separately per jurisdiction; use strictest requirements |
| Policy scaffold missing sections | Jurisdiction flag incorrect | Verify `--jurisdiction` matches EU, US, or UK |
| Headcount threshold confusion | EU directive has different thresholds by entity type | Private sector: 50+ employees; public sector: all municipalities |
| Sector-specific gaps not flagged | Generic sector value used | Use specific sector: `financial`, `healthcare`, `defense`, `nuclear` |
| GDPR checks fail for US entity | US entities may still need GDPR compliance | If processing EU citizen data, add `--has-gdpr-measures` |
| Timeline requirements unclear | Different jurisdictions have different timelines | EU: 7-day ack, 3-month feedback; SOX: 180-day filing deadline |
| Policy output too generic | Minimal parameters provided | Add `--org-name`, `--org-type`, and `--headcount` for specificity |

## Success Criteria

- **Compliance Coverage**: Assessment covers 100% of applicable regulatory requirements for specified jurisdiction
- **Gap Identification**: All CRITICAL and IMPORTANT gaps identified with clear remediation guidance
- **Policy Completeness**: Generated policies include all mandatory sections per applicable regulation
- **Timeline Compliance**: Policies reflect correct acknowledgment (7 days) and feedback (3 months) timelines
- **Audit Readiness**: Assessment output sufficient for regulatory audit preparation and evidence gathering

## Scope & Limitations

**This skill covers:**
- Compliance assessment against EU Directive 2019/1937, US SOX/Dodd-Frank, UK PIDA
- Policy scaffolding with jurisdiction-specific mandatory sections
- Gap analysis with priority classification and remediation guidance
- Multi-sector considerations (financial, healthcare, defense, nuclear, transport)

**This skill does NOT cover:**
- Actual whistleblower case management or investigation procedures
- Legal advice or attorney-client privileged analysis
- Real-time regulatory monitoring or automatic updates when laws change
- Whistleblower hotline software implementation or vendor selection
- Cross-border reporting coordination between multiple regulators

## Anti-Patterns

| Anti-Pattern | Why It Fails | Better Approach |
|--------------|-------------|-----------------|
| Copy-pasting policy from another jurisdiction | Regulations differ materially; EU requires 7-day ack, SOX has 180-day filing | Run scaffolder with correct jurisdiction; customize per local requirements |
| Treating all gaps as equal priority | Wastes resources on improvements while CRITICAL gaps remain | Address CRITICAL first, IMPORTANT second, IMPROVEMENT last |
| Single assessment for multi-jurisdiction org | Each jurisdiction has unique requirements and thresholds | Run separate assessments per jurisdiction; merge into unified policy |
| Skipping sector-specific phase | Regulated sectors (financial, healthcare) have additional requirements | Always complete Phase 8 for regulated industries |
| No periodic reassessment | Regulations evolve; transposition deadlines pass | Schedule annual reassessment; monitor legislative changes |

## Tool Reference

### `scripts/whistleblower_compliance_checker.py`

Assess whistleblower system compliance against regulatory requirements.

```
usage: whistleblower_compliance_checker.py [-h] [--json]
                                           --jurisdiction {EU,US,UK}
                                           --headcount HEADCOUNT
                                           --sector SECTOR
                                           [--channels CHANNELS]
                                           [--has-designated-person]
                                           [--has-confidentiality]
                                           [--has-gdpr-measures]
                                           [--has-dissemination]
                                           [--has-acknowledgment-timeline]
                                           [--has-feedback-timeline]

options:
  -h, --help            Show help message and exit
  --json                Output in JSON format
  --jurisdiction        Regulatory jurisdiction: EU, US, or UK
  --headcount           Number of employees in the organization
  --sector              Industry sector (financial, healthcare, technology, etc.)
  --channels            Comma-separated channel types: internal, external, none
  --has-designated-person  Designated person(s) appointed for handling reports
  --has-confidentiality    Confidentiality measures in place
  --has-gdpr-measures      GDPR/data protection measures implemented
  --has-dissemination      Policy disseminated to all personnel
  --has-acknowledgment-timeline  7-day acknowledgment timeline met
  --has-feedback-timeline  3-month feedback timeline met
```

### `scripts/whistleblower_policy_scaffolder.py`

Generate jurisdiction-specific whistleblower policy skeleton.

```
usage: whistleblower_policy_scaffolder.py [-h] [--json]
                                          --jurisdiction {EU,US,UK}
                                          --org-type {public,private,nonprofit}
                                          --headcount HEADCOUNT
                                          [--org-name ORG_NAME]
                                          [--output OUTPUT]

options:
  -h, --help            Show help message and exit
  --json                Output in JSON format
  --jurisdiction        Regulatory jurisdiction: EU, US, or UK
  --org-type            Organization type
  --headcount           Number of employees
  --org-name            Organization name (used in policy template)
  --output              Write policy to file instead of stdout
```
