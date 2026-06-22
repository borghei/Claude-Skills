---
name: gdpr-audit-prep
description: >
  GDPR audit-prep playbook: sprint to prepare for a supervisory authority inquiry,
  DPA audit, or internal review. Use when an audit is scheduled, when readiness gaps
  surface, or when ROPA (Records of Processing Activities) needs completion.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: compliance
  domain: ra-qm-team
  updated: 2026-05-27
  tags: [gdpr, audit-prep, ropa, dpia, data-protection, dpo-engagement, eu-privacy]
---

# GDPR Audit Prep

Operational playbook for GDPR audit preparation — whether triggered by a Data Protection Authority (DPA) inquiry, customer-side DPA review, internal compliance audit, or annual self-assessment.

When to use this skill vs. gdpr-dsgvo-expert:
- **This skill**: audit imminent (4-12 weeks); need execution sprint
- **gdpr-dsgvo-expert**: building GDPR program; designing DPIA process; multi-quarter

---

## When to use this skill

| Situation | Skill applies |
|-----------|---------------|
| Supervisory authority inquiry received | Yes — start immediately; engage DPO |
| Customer DPA audit / questionnaire | Yes — `scripts/gdpr_readiness_score.py` first |
| Annual internal GDPR audit | Yes — standard sprint |
| ROPA needs rapid update | Yes — `scripts/ropa_completeness_checker.py` |
| New high-risk processing → DPIA needed | Use `ra-qm-team/gdpr-dsgvo-expert` for DPIA design |

---

## The audit-prep sprint at a glance

### 4-week sprint (well-prepared org, periodic review)

```
Week 1: ROPA review + DPO engagement plan
Week 2: Gap remediation (policies, notices, technical)
Week 3: Evidence compilation + walkthroughs
Week 4: Audit week / submission
```

### 8-week sprint (gaps remaining)

```
Weeks 1-2: ROPA update + gap identification
Weeks 3-5: Gap closure (DPAs, notices, security, retention)
Weeks 6-7: Evidence + walkthroughs
Week 8: Audit
```

### 12-week sprint (DPA inquiry response)

```
Weeks 1-2: Inquiry analysis + response strategy + DPO engagement
Weeks 3-8: Targeted evidence collection + remediation
Weeks 9-10: Formal response drafting + legal review
Weeks 11-12: Submission + ongoing dialogue
```

See [references/gdpr-pre-audit-checklist.md](references/gdpr-pre-audit-checklist.md) for the full pre-audit punch list and [references/dpo-engagement-playbook.md](references/dpo-engagement-playbook.md) for DPO-coordinated audit response.

---

## Critical GDPR audit areas

### 1. ROPA (Records of Processing Activities, Article 30)

Every processing activity documented:
- Purpose of processing
- Categories of data subjects + data types
- Recipients (internal + external)
- International transfers (and lawful basis)
- Retention periods
- Security measures
- Lawful basis (consent, contract, legitimate interest, etc.)
- DPIA reference (if high-risk)

Audit gap: ROPA incomplete, stale, or missing for processing activities surfaced during audit.

### 2. Privacy Notices (Article 13/14)

- Privacy notice published + current
- Contains all required information (data controller, purposes, lawful basis, retention, rights, complaints contact, etc.)
- Easily accessible (no dark patterns)
- Translated for EU member states (where required)

### 3. Data Subject Rights (Article 12-23)

- Process documented + tested
- Response time tracked (< 1 month standard; extension possible)
- Identity verification
- Records of requests and responses (last 12 months)

### 4. Data Protection Impact Assessments (DPIAs, Article 35)

- High-risk processing activities identified
- DPIA conducted for each
- Mitigations documented
- DPO consulted (Article 35.2)

### 5. Data Processing Agreements (Article 28)

- DPA with every processor (vendor, sub-service org)
- Covers required clauses (Article 28.3)
- Annual review

### 6. Security Measures (Article 32)

- Technical and organizational measures documented
- Risk-appropriate (encryption, access control, backup, etc.)
- Tested and reviewed

### 7. Breach Notification (Article 33/34)

- Process documented
- 72-hour authority notification capability
- Past-period breaches: notified appropriately + documented

### 8. International Transfers (Chapter V)

- Mechanism for each transfer (SCCs, BCRs, adequacy decision)
- Transfer Impact Assessment (TIA) for non-adequacy countries
- Schrems II compliance for US transfers

---

## Clarify First

Before running the audit-prep, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Audit trigger** — supervisory-authority inquiry, customer DPA audit, internal audit, or annual self-assessment (sets the 4/8/12-week sprint and whether formal response drafting is needed)
- [ ] **Org readiness** — well-prepared vs gaps remaining (picks the 4-week vs 8-week sprint)
- [ ] **Processing scope and role** — controller vs processor, and which activities/ROPA are in scope (drives the ROPA and DPA focus)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the readiness assessment.

## Quick start

1. **Run readiness score**: `python3 scripts/gdpr_readiness_score.py --config gdpr-controls.yaml`
2. **Check ROPA completeness**: `python3 scripts/ropa_completeness_checker.py --ropa ropa.yaml`
3. **Engage DPO**: Walk through findings with DPO; finalize sprint scope
4. **Execute sprint** per [references/gdpr-pre-audit-checklist.md](references/gdpr-pre-audit-checklist.md)

---

## Common GDPR audit failures

- **ROPA missing or out-of-date.** Often the first thing an auditor asks.
- **Privacy notice generic** — boilerplate not actually reflecting actual processing.
- **DPIA missing for high-risk processing** (AI / profiling / large-scale monitoring / sensitive data).
- **DPAs not signed with all processors** — easy oversight; substantial finding.
- **International transfer mechanism** unclear post-Schrems II.
- **Breach notification process untested** — first breach is the test.
- **Consent not freely given** — bundled consent, pre-ticked boxes, take-it-or-leave-it.
- **No DPO appointed** when required (Article 37 — public authority, large-scale monitoring, etc.).
- **Data subject rights process untested** — request comes in, no one knows what to do.

---

## Tooling

| Script | Purpose |
|--------|---------|
| `scripts/gdpr_readiness_score.py` | Score current state per GDPR area; identify gaps |
| `scripts/ropa_completeness_checker.py` | Validate ROPA structure and completeness per Article 30 |

---

## References

- [gdpr-pre-audit-checklist.md](references/gdpr-pre-audit-checklist.md) — full checklist per GDPR area
- [dpo-engagement-playbook.md](references/dpo-engagement-playbook.md) — DPO-coordinated audit response

---

## Related skills

- `ra-qm-team/gdpr-dsgvo-expert` — deep GDPR program management
- `ra-qm-team/audit-prep/compliance-readiness` — multi-framework readiness (GDPR + ISO 27001 + SOC 2)
- `ra-qm-team/ccpa-cpra-privacy-expert` — US privacy counterpart
- `ra-qm-team/audit-prep/ai-act-readiness` — EU AI Act overlay for AI processing
