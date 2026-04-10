---
name: data-breach-response
description: >
  Data breach incident response with ENISA severity scoring, notification
  timelines, and compliance tracking. Use for breach assessment and response.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: The Glass Room
  category: legal
  domain: incident-response
  updated: 2026-04-10
  tags: [data-breach, gdpr, enisa, incident-response, notification]
---
> **⚠️ EXPERIMENTAL** — This skill is provided for educational and informational purposes only. It does NOT constitute legal advice. All responsibility for usage rests with the user. Consult qualified legal professionals before acting on any output.

# Data Breach Response

Incident response and legal compliance for personal data breaches under GDPR Art. 33/34, CCPA, HIPAA, NIS2, PCI DSS, and other regulations. Calculates breach severity, tracks notification deadlines, and manages response timelines.

---

## Table of Contents

- [Tools](#tools)
  - [Breach Severity Calculator](#breach-severity-calculator)
  - [Breach Timeline Tracker](#breach-timeline-tracker)
- [Reference Guides](#reference-guides)
- [Workflows](#workflows)
- [ENISA Severity Formula](#enisa-severity-formula)
- [Notification Decision Matrix](#notification-decision-matrix)
- [Troubleshooting](#troubleshooting)
- [Success Criteria](#success-criteria)
- [Scope & Limitations](#scope--limitations)
- [Anti-Patterns](#anti-patterns)
- [Tool Reference](#tool-reference)

---

## Tools

### Breach Severity Calculator

Calculates ENISA breach severity score from breach parameters. Determines notification obligations based on severity verdict.

```bash
# Calculate severity from parameters
python scripts/breach_severity_calculator.py \
  --dpc 3 --ei 0.75 \
  --confidentiality 0.5 --integrity 0.25 --availability 0 \
  --malicious

# JSON output
python scripts/breach_severity_calculator.py \
  --dpc 2 --ei 0.5 --confidentiality 0.5 --json

# With T0 timestamp for countdown
python scripts/breach_severity_calculator.py \
  --dpc 3 --ei 1.0 --confidentiality 0.5 \
  --t0 "2026-04-10T08:00:00" --json

# Generate input template
python scripts/breach_severity_calculator.py --template
```

**Output includes:**
- ENISA severity score (SE)
- Severity verdict: LOW / MEDIUM / HIGH / VERY HIGH
- Notification obligations (SA, data subjects, public)
- Time remaining for GDPR 72h notification from T0

---

### Breach Timeline Tracker

Tracks breach response timeline from T0 (moment of awareness). Records events, monitors deadlines, and generates status dashboards.

```bash
# Initialize a new breach timeline
python scripts/breach_timeline_tracker.py init \
  --breach-id "BR-2026-001" --t0 "2026-04-10T08:00:00" \
  --description "Unauthorized database access" \
  --output breach_timeline.json

# Record an event
python scripts/breach_timeline_tracker.py event \
  --timeline breach_timeline.json \
  --action "Containment team activated" --category containment

# View status dashboard
python scripts/breach_timeline_tracker.py status --timeline breach_timeline.json

# Check deadlines
python scripts/breach_timeline_tracker.py deadlines --timeline breach_timeline.json

# JSON status output
python scripts/breach_timeline_tracker.py status --timeline breach_timeline.json --json
```

**Tracks:**
- GDPR 72-hour SA notification deadline
- DPA contractual deadlines (24h / 48h processor notification)
- NIS2 24-hour early warning and 72-hour notification
- Completed vs. pending response actions
- Time elapsed and time remaining per deadline

---

## Reference Guides

### ENISA Methodology
`references/enisa_methodology.md`

Complete ENISA breach severity methodology:
- DPC (Data Processing Context) scoring 1-4
- EI (Ease of Identification) scoring 0.25-1.00
- CB (Circumstances of Breach) additive scoring
- Formula: SE = (DPC x EI) + CB
- Adjustments for encryption, pseudonymization, volume
- EDPB case matching (18 reference cases)

### Notification Obligations
`references/notification_obligations.md`

Multi-regulation notification requirements:
- GDPR Art. 33 (SA within 72h) and Art. 34 (data subjects)
- CCPA, HIPAA, PCI DSS, NIS2, state breach notification
- Controller vs. Processor obligation matrix
- Cross-border notification rules
- AI Act Art. 62 serious incident reporting

---

## Workflows

### Workflow 1: Standard Breach Response

```
Step 1: Emergency check — is there <12h remaining on any deadline?
        → If yes, skip to Step 4 (emergency notification)

Step 2: Initialize breach timeline
        → python scripts/breach_timeline_tracker.py init --breach-id "BR-2026-001" \
          --t0 "2026-04-10T08:00:00" --description "Description"

Step 3: Calculate severity
        → python scripts/breach_severity_calculator.py --dpc N --ei N \
          --confidentiality N --integrity N --availability N [--malicious]

Step 4: Based on severity verdict, determine notifications
        → LOW (<2): Internal log only, no external notification
        → MEDIUM (2 to <3): Notify supervisory authority within 72h
        → HIGH (3 to <4): Notify SA + individual data subjects
        → VERY HIGH (>=4): Notify SA + data subjects + consider public notice

Step 5: Execute containment and record events
        → python scripts/breach_timeline_tracker.py event --timeline breach.json \
          --action "Action taken" --category containment

Step 6: Monitor deadlines continuously
        → python scripts/breach_timeline_tracker.py deadlines --timeline breach.json

Step 7: Complete notification obligations and document
```

### Workflow 2: Emergency Mode (<12h Remaining)

```
Step 1: Calculate severity immediately
        → python scripts/breach_severity_calculator.py --dpc N --ei N \
          --confidentiality N --t0 "original-t0" --json

Step 2: If MEDIUM or higher, prepare phased notification
        → Art. 33(4) allows phased notification when full information unavailable
        → Initial notification: what is known + promise of update
        → Supplementary notification: full details when available

Step 3: File initial SA notification before deadline expires

Step 4: Initialize timeline for ongoing tracking
        → Continue gathering information for supplementary notification

Step 5: Document emergency timeline and decisions
```

### Workflow 3: Processor Breach Notification

```
Step 1: Processor becomes aware of breach
        → T0 for processor = moment of awareness

Step 2: Processor must notify controller "without undue delay"
        → Check DPA for specific contractual deadline (24h/48h common)

Step 3: Controller's T0 starts when controller becomes aware
        → Controller's 72h clock starts at this point

Step 4: Controller assesses severity independently
        → python scripts/breach_severity_calculator.py (controller's assessment)

Step 5: Controller makes notification decisions
        → Processor provides information; controller decides on SA/subject notification
```

---

## ENISA Severity Formula

```
SE = (DPC x EI) + CB
```

| Component | Range | Description |
|-----------|-------|-------------|
| DPC | 1-4 | Data Processing Context — nature and sensitivity of data |
| EI | 0.25-1.0 | Ease of Identification — how easily individuals can be identified |
| CB | -0.5 to +1.0 | Circumstances of Breach — additive factors (malicious intent, volume, loss type) |

### Severity Verdicts

| Score Range | Verdict | Notification Obligations |
|-------------|---------|--------------------------|
| <2 | LOW | Internal log only. No SA or subject notification required |
| 2 to <3 | MEDIUM | Notify supervisory authority within 72h (Art. 33) |
| 3 to <4 | HIGH | Notify SA within 72h + notify individual data subjects (Art. 34) |
| >=4 | VERY HIGH | Notify SA + data subjects + consider public notice; crisis management |

---

## Notification Decision Matrix

Quick reference for notification obligations per regulation and severity.

| Regulation | Authority Notification | Individual Notification | Trigger |
|------------|----------------------|------------------------|---------|
| GDPR Art. 33 | SA within 72h | N/A | Unless unlikely to result in risk to rights/freedoms |
| GDPR Art. 34 | N/A | Without undue delay | When likely to result in high risk |
| CCPA | State AG | Affected consumers | Unencrypted personal information compromised |
| HIPAA | HHS within 60 days | Affected individuals | Unsecured PHI; >500: notify media |
| PCI DSS | Card brands within 24h | Cardholders (via issuer) | Cardholder data compromised |
| NIS2 Art. 23 | CSIRT within 24h (early warning), 72h (notification) | N/A | Significant incident |
| AI Act Art. 62 | Market surveillance within 15 days | N/A | Serious incident involving AI system |

### Controller vs. Processor Obligations

| Obligation | Controller | Processor |
|------------|-----------|-----------|
| Notify supervisory authority | Yes (Art. 33) | No (notify controller only) |
| Notify data subjects | Yes (Art. 34) | No |
| Document all breaches | Yes (Art. 33(5)) | Yes (assist controller) |
| Notify controller | N/A | Yes, without undue delay (Art. 33(2)) |
| Conduct severity assessment | Yes | Assist (provide information) |
| Timeline starts (T0) | When controller becomes aware | When processor becomes aware |

---

## Troubleshooting

| Problem | Possible Cause | Resolution |
|---------|---------------|------------|
| Severity score is borderline between MEDIUM and HIGH | Parameters are at threshold boundaries | Score conservatively — if near 3.0, treat as HIGH and notify data subjects; document the borderline analysis |
| 72-hour deadline approaching with incomplete information | Complex breach requiring ongoing investigation | Use Art. 33(4) phased notification — notify SA with available information and supplement later |
| Processor discovered breach but delayed notifying controller | DPA contractual deadline may have been missed | Document the delay; assess whether processor's delay affected controller's ability to comply; review DPA terms |
| Cross-border breach — unclear which SA to notify | Multi-jurisdictional processing with unclear lead SA | Notify the SA of your main establishment (one-stop-shop); if unclear, notify the SA where most affected subjects reside |
| Breach involves encrypted data — unclear if notification needed | Encryption may lower severity or eliminate notification | If encryption was effective (strong algorithm, key not compromised), this may make notification unnecessary per Art. 34(3)(a); document the analysis |
| AI system involved in breach — unclear additional obligations | AI Act Art. 62 may apply alongside GDPR | Assess whether AI system is high-risk under AI Act; if serious incident, notify market surveillance authority within 15 days in addition to GDPR obligations |

---

## Success Criteria

- **Breach severity calculated within 2 hours of awareness** -- ENISA methodology applied with documented parameters and scoring rationale
- **SA notification filed within 72 hours of T0** -- for MEDIUM or higher severity breaches, phased notification used when full information unavailable
- **Data subject notification completed without undue delay** -- for HIGH or higher severity breaches, clear communication of impact and protective measures
- **All response actions tracked with timestamps** -- breach timeline maintained from T0 through closure with all events recorded
- **Cross-regulation obligations identified and met** -- GDPR, CCPA, HIPAA, PCI DSS, NIS2, and AI Act obligations assessed and fulfilled per applicable law
- **Post-breach documentation complete** -- internal breach log maintained per Art. 33(5) regardless of notification decision

---

## Scope & Limitations

**In Scope:**
- ENISA breach severity calculation with full parameter support
- GDPR Art. 33/34 notification timeline tracking
- Multi-regulation notification obligation assessment (GDPR, CCPA, HIPAA, PCI DSS, NIS2, AI Act)
- Controller vs. processor obligation guidance
- Cross-border breach notification routing
- Phased notification guidance per Art. 33(4)
- Breach response event tracking and deadline monitoring

**Out of Scope:**
- Technical incident containment (network isolation, forensics, malware removal)
- Filing notifications with supervisory authorities (document preparation only)
- Insurance claim processing or coverage analysis
- Law enforcement coordination
- Public relations or crisis communications strategy
- Forensic investigation methodology

---

## Anti-Patterns

- **Delaying T0 determination to buy more time** -- T0 is the moment the controller becomes "aware" of the breach, not when full details are known; deliberately delaying awareness to extend the 72-hour window is a compliance violation and will be treated as such by regulators
- **Defaulting to no notification without documented analysis** -- every breach must be documented and assessed, even if the conclusion is that notification is not required; "we decided not to notify" without documented severity analysis is indefensible
- **Treating processor notification as controller notification** -- processor notifying its own SA does not satisfy the controller's Art. 33 obligation; the controller must make its own independent notification decision and filing
- **Using encryption as an automatic notification exemption** -- Art. 34(3)(a) exemption requires that the encrypted data was rendered unintelligible AND the encryption key was not compromised; weak encryption or compromised keys do not qualify
- **Ignoring AI Act obligations for AI-involved breaches** -- if the breach involves a high-risk AI system, Art. 62 serious incident reporting (15 days to market surveillance authority) applies in addition to GDPR; these are separate obligations with different timelines

---

## Tool Reference

### breach_severity_calculator.py

Calculates ENISA breach severity score and determines notification obligations.

| Flag | Required | Description |
|------|----------|-------------|
| `--dpc <1-4>` | Yes | Data Processing Context: 1=Simple demographic, 2=Behavioral/financial, 3=Sensitive personal, 4=Special category/highly sensitive |
| `--ei <0.25-1.0>` | Yes | Ease of Identification: 0.25=Negligible, 0.5=Limited, 0.75=Significant, 1.0=Maximum |
| `--confidentiality <0/0.25/0.5>` | No | Confidentiality loss score (default 0) |
| `--integrity <0/0.25/0.5>` | No | Integrity loss score (default 0) |
| `--availability <0/0.25/0.5>` | No | Availability loss score (default 0) |
| `--malicious` | No | Flag for malicious intent (adds +0.5 to CB) |
| `--t0 <ISO datetime>` | No | T0 timestamp for deadline calculation |
| `--template` | No | Generate input template |
| `--json` | No | Output in JSON format |

### breach_timeline_tracker.py

Tracks breach response timeline, events, and regulatory deadlines.

| Subcommand | Description |
|------------|-------------|
| `init` | Initialize breach timeline (`--breach-id`, `--t0`, `--description` required, `--output` optional) |
| `event` | Record event (`--timeline`, `--action`, `--category` required) |
| `status` | View status dashboard (`--timeline` required, `--json` optional) |
| `deadlines` | Check deadline status (`--timeline` required, `--json` optional) |
