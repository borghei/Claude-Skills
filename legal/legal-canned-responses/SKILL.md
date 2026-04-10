---
name: legal-canned-responses
description: >
  Generate templated responses for common legal inquiries with escalation detection. Use when drafting legal responses.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: The Glass Room
  category: legal
  domain: legal-operations
  updated: 2026-04-10
  tags: [legal-responses, templates, escalation, legal-ops, intake]
---
> **⚠️ EXPERIMENTAL** — This skill is provided for educational and informational purposes only. It does NOT constitute legal advice. All responsibility for usage rests with the user. Consult qualified legal professionals before acting on any output.

# Legal Canned Responses Skill

## Overview

Production-ready toolkit for generating templated responses to common legal inquiries with built-in escalation detection. Covers 7 response categories with multiple sub-types each, plus a universal and category-specific escalation trigger system. Designed for legal operations teams handling high volumes of recurring inquiries while ensuring critical matters are routed to counsel.

## Table of Contents

- [Tools](#tools)
- [Reference Guides](#reference-guides)
- [Workflows](#workflows)
- [Response Categories](#response-categories)
- [Escalation System](#escalation-system)
- [Troubleshooting](#troubleshooting)
- [Success Criteria](#success-criteria)
- [Scope & Limitations](#scope--limitations)
- [Anti-Patterns](#anti-patterns)
- [Tool Reference](#tool-reference)

## Tools

### 1. Response Generator (`scripts/response_generator.py`)

Generate formatted legal responses from templates with variable substitution and escalation detection.

```bash
python scripts/response_generator.py \
  --category dsr --sub-type acknowledgment \
  --var requestor_name="Jane Doe" \
  --var request_type="access" \
  --var request_date="2026-04-10"

python scripts/response_generator.py \
  --category nda --sub-type standard-form \
  --var counterparty="Acme Corp" \
  --var purpose="due diligence" --json

python scripts/response_generator.py \
  --category discovery --sub-type initial-notice \
  --var matter_name="Smith v. Corp" \
  --var custodians="Engineering,Sales"
```

### 2. Escalation Detector (`scripts/escalation_detector.py`)

Analyze inquiry text for escalation triggers and recommend routing.

```bash
python scripts/escalation_detector.py \
  --text "We received a subpoena from the DOJ regarding our pricing practices"

python scripts/escalation_detector.py \
  --text "A reporter from the Wall Street Journal is asking about our data practices" --json

python scripts/escalation_detector.py \
  --category vendor \
  --text "The vendor is threatening litigation over the contract dispute"
```

## Reference Guides

| Reference | Purpose |
|-----------|---------|
| `references/response_templates.md` | Complete templates for all 7 categories with sub-types |
| `references/escalation_triggers.md` | Universal and category-specific escalation triggers |

## Workflows

### Template Lifecycle

1. **Creation** -- Draft response template for identified recurring inquiry type
2. **Review** -- Legal counsel reviews template for accuracy, tone, and compliance
3. **Publication** -- Template added to system with metadata, variables, and triggers
4. **Use** -- Staff selects category/sub-type, fills variables, generates response
5. **Feedback** -- Track usage and collect feedback on template effectiveness
6. **Update** -- Revise templates based on feedback, legal changes, or policy updates
7. **Retirement** -- Archive templates that are no longer applicable

### Response Generation Workflow

1. **Classify Inquiry** -- Determine category (DSR, NDA, subpoena, etc.) and sub-type
2. **Check Escalation** -- Run escalation detector on inquiry text
3. **If Escalation Detected** -- Stop; route to counsel with escalation report
4. **If No Escalation** -- Generate response with appropriate template and variables
5. **Review & Send** -- Review generated response before sending; adjust if needed

## Response Categories

| Category | Sub-Types | Description |
|----------|-----------|-------------|
| Data Subject Requests (DSR) | acknowledgment, verification, fulfillment, denial, extension | GDPR/CCPA data subject right requests |
| Discovery/Litigation Holds | initial-notice, reminder, modification, release | Litigation hold management |
| Privacy Inquiries | cookies, data-sharing, children, transfers | General privacy questions |
| Vendor Legal Questions | contract-status, amendments, certifications, audit | Vendor/supplier legal matters |
| NDA Requests | standard-form, counterparty-markup, decline, renewal | Non-disclosure agreement lifecycle |
| Subpoena/Legal Process | acknowledgment, objection, extension, compliance | Legal process responses |
| Insurance Notifications | initial-claim, supplemental-info, reservation-of-rights | Insurance claim management |

### DSR Sub-Types

| Sub-Type | Use When | Key Variables |
|----------|----------|---------------|
| acknowledgment | New DSR received | requestor_name, request_type, request_date |
| verification | Identity verification needed | requestor_name, verification_method |
| fulfillment | Request completed | requestor_name, request_type, data_description |
| denial | Request denied with reason | requestor_name, request_type, denial_reason |
| extension | Need more time | requestor_name, request_type, extension_reason, new_deadline |

### Discovery/Litigation Hold Sub-Types

| Sub-Type | Use When | Key Variables |
|----------|----------|---------------|
| initial-notice | New litigation hold issued | matter_name, custodians, data_types |
| reminder | Periodic hold reminder | matter_name, reminder_number |
| modification | Hold scope changed | matter_name, modification_description |
| release | Hold lifted | matter_name, release_date |

## Escalation System

### Universal Triggers (Always Escalate)

| # | Trigger | Why |
|---|---------|-----|
| 1 | Potential or active litigation | Legal exposure requires counsel assessment |
| 2 | Regulatory investigation or inquiry | Regulatory response requires strategic approach |
| 3 | Government or law enforcement contact | Constitutional and procedural rights at stake |
| 4 | Binding legal commitment requested | Cannot create legal obligations without counsel |
| 5 | Criminal liability exposure | Requires immediate counsel involvement |
| 6 | Media attention or press inquiry | Reputational risk requires coordinated response |
| 7 | Unprecedented or novel situation | No template exists; bespoke legal analysis needed |
| 8 | Multi-jurisdictional conflict | Cross-border legal complexity requires expert analysis |

### Escalation Response Protocol

1. **Stop** -- Do not send any templated response
2. **Alert** -- Notify designated counsel immediately
3. **Explain** -- Provide escalation context with matched triggers
4. **Recommend** -- Suggest routing based on trigger type
5. **Draft** -- Mark any preliminary draft "FOR COUNSEL REVIEW ONLY"

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| Missing variable in output | Required variable not provided | Check template requirements; provide all required `--var` parameters |
| Wrong template selected | Category/sub-type mismatch | Review category descriptions; ensure sub-type matches inquiry type |
| False positive escalation | Common words matching trigger patterns | Provide `--category` to use category-specific triggers; review matched triggers |
| False negative escalation | Inquiry text too vague | Add more context to inquiry text; run both universal and category-specific checks |
| Template too generic | Using default values | Replace all placeholder values with actual organization-specific details |
| Discovery hold sent to wrong custodians | Custodian list outdated | Verify custodian list against current employees and systems |
| Subpoena response not flagged | Missing category context | Always use `--category subpoena` for legal process; subpoena category always escalates |
| Response tone inappropriate | Wrong audience context | Select appropriate sub-type; customize tone per audience |

## Success Criteria

- **Response Time**: Templated responses generated within 5 minutes vs. 30+ minutes manual drafting
- **Escalation Accuracy**: 100% of genuine escalation triggers detected (zero false negatives on CRITICAL triggers)
- **Template Coverage**: Templates cover 80%+ of recurring legal inquiry types
- **Consistency**: All responses within a category use consistent language, tone, and legal caveats
- **Audit Trail**: Every generated response logged with category, sub-type, date, and escalation status

## Scope & Limitations

**This skill covers:**
- Template-based response generation for 7 common legal inquiry categories
- Escalation detection using keyword and pattern matching against known triggers
- Variable substitution for organization-specific customization
- Response metadata generation for audit trail purposes

**This skill does NOT cover:**
- Legal advice or attorney-client privileged analysis
- Automated sending of responses (generation only; human review required)
- Contract drafting, negotiation, or legal document creation
- Case management, docketing, or deadline tracking
- Jurisdiction-specific legal compliance validation of response content

## Anti-Patterns

| Anti-Pattern | Why It Fails | Better Approach |
|--------------|-------------|-----------------|
| Sending templated response without review | May miss context-specific nuances; legal risk | Always review generated response before sending |
| Ignoring escalation triggers | Critical matters mishandled; legal exposure | Run escalation detector on every inquiry; treat all triggers seriously |
| Using templates for novel situations | Templates assume standard scenarios; novel situations need bespoke analysis | Escalate novel situations to counsel; create new template after resolution |
| Hardcoding organization details in templates | Templates become non-portable; updates missed | Use variable substitution; maintain variables in configuration |
| Skipping identity verification for DSRs | GDPR/CCPA require verification before fulfillment | Always send verification sub-type before fulfillment |

## Tool Reference

### `scripts/response_generator.py`

Generate formatted legal responses with variable substitution.

```
usage: response_generator.py [-h] [--json]
                              --category {dsr,discovery,privacy,vendor,nda,subpoena,insurance}
                              --sub-type SUB_TYPE
                              [--var KEY=VALUE [KEY=VALUE ...]]

options:
  -h, --help            Show help message and exit
  --json                Output in JSON format
  --category            Response category
  --sub-type            Response sub-type within category
  --var                 Variable substitution as KEY=VALUE pairs
```

### `scripts/escalation_detector.py`

Analyze inquiry text for escalation triggers.

```
usage: escalation_detector.py [-h] [--json]
                               --text TEXT
                               [--category {dsr,discovery,privacy,vendor,nda,subpoena,insurance}]

options:
  -h, --help            Show help message and exit
  --json                Output in JSON format
  --text                Inquiry text to analyze for escalation triggers
  --category            Optional category for category-specific trigger detection
```
