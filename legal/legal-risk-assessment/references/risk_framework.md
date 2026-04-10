# Legal Risk Assessment Framework

Complete reference for the 5x5 Severity x Likelihood risk scoring matrix, classification levels, and documentation standards.

---

## Table of Contents

- [Severity Scale](#severity-scale)
- [Likelihood Scale](#likelihood-scale)
- [Risk Matrix](#risk-matrix)
- [Risk Classification Levels](#risk-classification-levels)
- [Risk Categories](#risk-categories)
- [Risk Assessment Memo Format](#risk-assessment-memo-format)
- [Risk Register Entry Format](#risk-register-entry-format)
- [Contributing and Mitigating Factors](#contributing-and-mitigating-factors)

---

## Severity Scale

Severity measures the potential impact if the risk materializes. Each level corresponds to a financial exposure range relative to annual revenue.

| Level | Label | Financial Exposure | Description | Examples |
|-------|-------|--------------------|-------------|----------|
| 1 | Negligible | <0.1% revenue | Minimal impact, easily absorbed | Minor contract amendment needed; administrative filing correction; internal policy clarification |
| 2 | Minor | 0.1-1% revenue | Limited impact, manageable within normal operations | Small claims dispute (<$50K); routine regulatory inquiry; employee grievance without litigation |
| 3 | Moderate | 1-5% revenue | Noticeable impact requiring dedicated resources | Mid-size contract dispute ($50K-$500K); regulatory audit with findings; employment discrimination claim |
| 4 | Major | 5-15% revenue | Significant impact affecting business operations | Large litigation ($500K-$5M); regulatory enforcement action; data breach affecting >10K individuals; patent infringement claim |
| 5 | Critical | >15% revenue | Existential or near-existential impact | Class action lawsuit; government investigation with potential criminal charges; market-moving regulatory penalty; loss of critical license or IP |

### Severity Assessment Guidance

When assessing severity, consider all dimensions of impact:

| Dimension | Questions to Ask |
|-----------|-----------------|
| Financial | What is the maximum monetary exposure (damages, fines, settlements, legal fees)? |
| Operational | Will business operations be disrupted? For how long? |
| Reputational | Will this become public? What is the media risk? Customer impact? |
| Strategic | Does this affect key business relationships, market position, or growth plans? |
| Regulatory | Could this trigger additional regulatory scrutiny or license revocation? |
| Precedential | Could the outcome create adverse precedent for future matters? |

---

## Likelihood Scale

Likelihood measures the probability that the risk will materialize within the assessment period (typically 12 months).

| Level | Label | Probability | Description | Indicators |
|-------|-------|-------------|-------------|------------|
| 1 | Remote | <5% | Extremely unlikely to occur | No known precedent; multiple safeguards in place; theoretical risk only |
| 2 | Unlikely | 5-20% | Could occur but not expected | Historical precedent exists but rare; some controls may have gaps; early warning signs absent |
| 3 | Possible | 20-50% | Reasonable chance of occurring | Similar events have occurred in industry; some warning indicators present; controls partially effective |
| 4 | Likely | 50-80% | More probable than not | Clear warning indicators; known vulnerability; similar events have occurred to organization; regulatory trend toward enforcement |
| 5 | Almost Certain | >80% | Expected to occur | Active threat or demand received; regulatory action announced; deadline approaching with known non-compliance; litigation filed |

### Likelihood Assessment Guidance

| Factor | Increases Likelihood | Decreases Likelihood |
|--------|---------------------|---------------------|
| Regulatory environment | Active enforcement campaigns; new regulations; industry under scrutiny | Regulatory safe harbor; established compliance program; favorable guidance |
| Counterparty behavior | Aggressive counterparty; history of litigation; demand letters received | Cooperative relationship; mutual interest in resolution; history of settlements |
| Internal controls | Control gaps identified; audit findings unresolved; staff turnover | Strong compliance program; recent audit clearance; trained personnel |
| External events | Market downturn; industry consolidation; political changes | Stable market; favorable court rulings; supportive industry associations |
| Temporal factors | Approaching statute of limitations; regulatory deadline imminent | Long time horizon; no known trigger events |

---

## Risk Matrix

```
                         LIKELIHOOD
                 Remote  Unlikely  Possible  Likely  Almost Certain
                  (1)      (2)       (3)      (4)        (5)

Critical  (5)  |  5-Y  |  10-O  |  15-O  |  20-R  |   25-R   |
                |       |        |        |        |          |
Major     (4)  |  4-G  |   8-Y  |  12-O  |  16-R  |   20-R   |
 S              |       |        |        |        |          |
 E  Moderate (3)|  3-G  |   6-Y  |   9-Y  |  12-O  |   15-O   |
 V              |       |        |        |        |          |
 E  Minor    (2)|  2-G  |   4-G  |   6-Y  |   8-Y  |   10-O   |
 R              |       |        |        |        |          |
 I  Negligible(1)| 1-G  |   2-G  |   3-G  |   4-G  |    5-Y   |
 T              |       |        |        |        |          |
 Y

Legend: G=GREEN  Y=YELLOW  O=ORANGE  R=RED
Score = Severity x Likelihood
```

---

## Risk Classification Levels

### GREEN (Score 1-4) — Accept

| Aspect | Guidance |
|--------|----------|
| **Overall posture** | Risk is within acceptable tolerance. No immediate action required. |
| **Documentation** | Record in risk register with description, score, and rationale. |
| **Monitoring** | Review quarterly during regular risk register reviews. |
| **Ownership** | Legal operations or assigned team member. |
| **Escalation** | Not required unless circumstances change. |
| **Reporting** | Include in quarterly risk summary for awareness. |

**Typical actions:**
- Document the risk and rationale for acceptance
- Set a calendar reminder for quarterly review
- Monitor for changes in severity or likelihood triggers
- No dedicated resources required

### YELLOW (Score 5-9) — Monitor and Mitigate

| Aspect | Guidance |
|--------|----------|
| **Overall posture** | Risk requires active attention. Controls should be in place or planned. |
| **Documentation** | Detailed risk register entry with mitigation plan and timeline. |
| **Monitoring** | Monthly review by assigned risk owner. |
| **Ownership** | Named risk owner from legal team with accountability for mitigation. |
| **Escalation** | Escalate to senior counsel if score increases or mitigation stalls. |
| **Reporting** | Monthly update in legal team risk report. |

**Typical actions:**
- Assign a specific risk owner
- Develop and implement mitigation controls
- Set measurable milestones for risk reduction
- Monitor leading indicators monthly
- Document all mitigation activities

### ORANGE (Score 10-15) — Escalate and Plan

| Aspect | Guidance |
|--------|----------|
| **Overall posture** | Significant risk requiring senior attention and proactive response. |
| **Documentation** | Full risk assessment memo with analysis, mitigation plan, and contingency options. |
| **Monitoring** | Bi-weekly review by senior counsel. |
| **Ownership** | Senior counsel with executive sponsor. |
| **Escalation** | Consider engaging outside counsel for specialized expertise. |
| **Reporting** | Bi-weekly update to legal leadership; include in executive risk summary. |

**Typical actions:**
- Escalate to senior counsel or deputy general counsel
- Develop comprehensive mitigation plan with resource allocation
- Create contingency plan for risk materialization
- Evaluate outside counsel engagement (see escalation_guide.md)
- Brief relevant business stakeholders
- Consider litigation hold if appropriate

### RED (Score 16-25) — Immediate Escalation

| Aspect | Guidance |
|--------|----------|
| **Overall posture** | Critical risk requiring immediate response and executive involvement. |
| **Documentation** | Crisis management memo; board reporting as required. |
| **Monitoring** | Weekly review (daily during active response). |
| **Ownership** | General Counsel with board-level oversight. |
| **Escalation** | Engage outside counsel immediately. Brief board or audit committee. |
| **Reporting** | Weekly to executive team; board reporting per governance requirements. |

**Typical actions:**
- Immediate escalation to General Counsel
- Activate crisis management protocol
- Engage outside counsel with appropriate specialization
- Assemble cross-functional response team (legal, comms, business unit)
- Prepare board or audit committee briefing
- Implement litigation hold if applicable
- Establish dedicated communication channel for response team
- Consider disclosure obligations (regulatory, contractual, public)

---

## Risk Categories

| Category | Definition | Common Sources |
|----------|-----------|----------------|
| **Contract** | Risks arising from contractual obligations, breaches, disputes, or inadequate terms | Vendor agreements, customer contracts, partnership deals, SLAs, indemnification clauses |
| **Regulatory** | Risks from non-compliance with laws, regulations, or regulatory actions | Industry regulations, data protection laws, securities rules, environmental requirements |
| **Litigation** | Risks from active or threatened lawsuits, claims, or dispute resolution | Customer disputes, employee claims, competitor actions, product liability, class actions |
| **IP** | Risks to intellectual property rights or from IP infringement claims | Patent disputes, trade secret misappropriation, trademark conflicts, open-source compliance |
| **Data Privacy** | Risks related to personal data handling, breaches, or privacy regulation | GDPR, CCPA, data breaches, consent management, cross-border transfers, AI training data |
| **Employment** | Risks from employment relationships, labor law, or workplace issues | Wrongful termination, discrimination claims, wage disputes, non-compete enforcement, union matters |
| **Corporate** | Risks related to corporate governance, structure, or transactions | M&A due diligence, board governance, shareholder disputes, corporate restructuring, securities compliance |

---

## Risk Assessment Memo Format

A complete risk assessment memo should include the following 10 sections:

| Section | Content |
|---------|---------|
| 1. Executive Summary | 2-3 sentence overview of key findings and highest-priority risks |
| 2. Risk Matrix | Visual representation of all assessed risks by severity and likelihood |
| 3. Risk Distribution | Count and percentage of risks at each level (GREEN/YELLOW/ORANGE/RED) |
| 4. Category Breakdown | Risks grouped by category with average and maximum scores |
| 5. Top Risks | Ranked list of highest-scoring risks with descriptions and scores |
| 6. Recommended Actions | Specific action items for each ORANGE and RED risk |
| 7. Monitoring Plan | Review frequency and responsible parties per risk level |
| 8. Escalation Summary | Outside counsel needs and escalation decisions |
| 9. Trend Analysis | Comparison with previous assessment (if available) |
| 10. Appendix | Detailed risk register entries and supporting documentation |

---

## Risk Register Entry Format

Each risk in the register should capture:

| Field | Description | Required |
|-------|-------------|----------|
| Risk ID | Unique identifier (e.g., LR-2026-001) | Yes |
| Description | Clear, specific description of the risk | Yes |
| Category | One of the 7 defined categories | Yes |
| Severity | 1-5 per severity scale | Yes |
| Likelihood | 1-5 per likelihood scale | Yes |
| Score | Calculated: Severity x Likelihood | Auto |
| Level | GREEN/YELLOW/ORANGE/RED | Auto |
| Owner | Named individual responsible for monitoring | Yes (YELLOW+) |
| Mitigation Plan | Specific actions to reduce risk | Yes (YELLOW+) |
| Target Score | Desired score after mitigation | Optional |
| Status | Open / Mitigating / Monitoring / Closed | Yes |
| Date Identified | When the risk was first identified | Yes |
| Last Reviewed | Date of most recent review | Yes |
| Notes | Additional context, updates, or related matters | Optional |

---

## Contributing and Mitigating Factors

### Contributing Factors (Increase Risk)

| Factor | Impact on Scoring |
|--------|-------------------|
| No existing controls or compliance program | +1 to likelihood |
| History of similar incidents | +1 to likelihood |
| Aggressive counterparty or regulator | +1 to likelihood |
| Public visibility or media interest | +1 to severity |
| Precedential risk (could create adverse precedent) | +1 to severity |
| Multi-jurisdictional exposure | +1 to both severity and likelihood |
| Criminal exposure potential | Automatically severity 5 |
| Class action potential | +2 to severity |

### Mitigating Factors (Decrease Risk)

| Factor | Impact on Scoring |
|--------|-------------------|
| Strong compliance program in place | -1 from likelihood |
| Insurance coverage applicable | -1 from severity (financial dimension only) |
| Favorable legal precedent | -1 from likelihood |
| Cooperative counterparty | -1 from likelihood |
| Strong contractual protections (indemnification, limitation of liability) | -1 from severity |
| Early detection and response | -1 from both severity and likelihood |
| Experienced counsel (internal or external) already engaged | -1 from severity |

**Note:** Adjustments are advisory. Final scoring should reflect professional judgment. Contributing factors cannot push a score above 5 on either axis, and mitigating factors cannot reduce below 1.
