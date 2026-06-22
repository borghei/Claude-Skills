---
name: fda-qsr-audit-prep
description: >
  FDA Quality System Regulation (21 CFR 820 / QMSR) audit-prep playbook for medical
  devices. Use when an FDA inspection is announced, when preparing for the new QMSR
  (2026), or when a 483 / Warning Letter response is needed.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: compliance
  domain: ra-qm-team
  updated: 2026-05-27
  tags: [fda, qsr, qmsr, 21-cfr-820, medical-devices, audit-prep, 483-response, warning-letter]
---

# FDA QSR / QMSR Audit Prep

Operational playbook for FDA inspection preparation under Quality System Regulation (21 CFR 820) and the transitioning Quality Management System Regulation (QMSR, fully effective 2026, harmonizing with ISO 13485:2016).

When to use this skill vs. fda-consultant-specialist:
- **This skill**: FDA inspection imminent OR 483/Warning Letter received; need sprint
- **fda-consultant-specialist**: building / maintaining QMS; multi-quarter

---

## When to use this skill

| Situation | Skill applies |
|-----------|---------------|
| FDA inspection announced (or unannounced visit imminent) | Yes — start immediately |
| Form 483 observation received | Yes — `scripts/qsr_readiness_score.py` to assess + plan response |
| Warning Letter received | Yes — plus engage outside FDA counsel |
| Annual readiness assessment | Yes — periodic sprint |
| Building QMS from scratch | Use `ra-qm-team/fda-consultant-specialist` |
| Medical device submission (510k / PMA) | Use `ra-qm-team/fda-consultant-specialist` |

---

## The audit-prep sprint at a glance

### 2-week sprint (announced inspection, mature QMS)

```
Week 1: Inventory, walkthrough rehearsal, gap remediation
Week 2: Inspection week (front room + back room operation)
```

### 8-week sprint (gaps identified, scheduled inspection)

```
Weeks 1-2: Readiness assessment + 483 / WL prior issue review
Weeks 3-6: Gap remediation (DHF, CAPA, complaint records, etc.)
Weeks 7-8: Mock inspection + final remediation + inspection prep
```

### Reactive: 483 / Warning Letter response

```
- 483: 15 business days to respond (then ongoing)
- Warning Letter: 15 business days to respond (then full corrective action plan)
- Approach: Acknowledge + investigate root cause + corrective action plan + commitment + evidence
```

---

## QSR / QMSR key audit areas

| 21 CFR 820 Subpart | Topic | Audit focus |
|--------------------|-------|-------------|
| Subpart B | Quality system | Management responsibility, quality policy, planning |
| Subpart C | Design controls | Design history file (DHF), design reviews, V&V |
| Subpart D | Document controls | Document approval, change control, distribution |
| Subpart E | Purchasing controls | Supplier qualification, agreements, evaluations |
| Subpart F | Identification and traceability | Product ID, lot/batch traceability |
| Subpart G | Production and process controls | Process validation, environmental controls, equipment maintenance |
| Subpart H | Acceptance activities | Receiving, in-process, finished device acceptance |
| Subpart I | Nonconforming product | Identification, segregation, disposition |
| Subpart J | Corrective and preventive action (CAPA) | CAPA process, root cause analysis, effectiveness verification |
| Subpart K | Labeling and packaging | Label inspection, packaging validation |
| Subpart L | Handling, storage, distribution | Procedures, shelf-life, distribution records |
| Subpart M | Records | Device Master Record (DMR), Device History Record (DHR), QSR records |
| Subpart N | Servicing | Servicing procedures, complaint review |
| Subpart O | Statistical techniques | Sampling, statistical methods |

**QMSR transition (effective Feb 2026)**: Harmonizes 21 CFR 820 with ISO 13485:2016. Adds requirements for risk management (ISO 14971), software lifecycle (IEC 62304), usability (IEC 62366).

---

## Clarify First

Before running the audit-prep, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Trigger** — announced inspection, Form 483 received, Warning Letter, or annual readiness (chooses between the sprint track and the reactive 15-day response track, and sets deadlines)
- [ ] **Framework** — legacy QSR (21 CFR 820) vs QMSR (ISO 13485-harmonized, effective Feb 2026) (changes which requirements and subparts apply)
- [ ] **QMS maturity and known issues** — mature vs gaps, plus prior 483/WL findings (picks the 2-week vs 8-week sprint)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the readiness assessment.

## Quick start

1. **Run readiness score**: `python3 scripts/qsr_readiness_score.py --config qsr-controls.yaml`
2. **Check DHF completeness for in-scope devices**: `python3 scripts/dhf_completeness_checker.py --dhf device-dhf.yaml`
3. **Pick sprint length** based on score + known issues
4. **Execute sprint** per [references/fda-qsr-pre-inspection-checklist.md](references/fda-qsr-pre-inspection-checklist.md)

---

## Common FDA inspection findings (highest 483 / Warning Letter trigger)

1. **CAPA failures** — root cause not addressed, ineffective corrective action
2. **Complaint handling** — complaints not investigated, MDR (Medical Device Reporting) missed
3. **Design controls (Subpart C)** — DHF incomplete, V&V gaps, no design reviews
4. **Process validation** — processes not validated, validation stale
5. **Supplier controls** — suppliers not qualified, agreements missing, evaluations skipped
6. **Document control** — old procedures in use, no document approval evidence
7. **Management responsibility** — no management review, no quality policy, no objectives
8. **Records (DHR)** — incomplete records, missing lot traceability

See [references/483-warning-letter-prevention.md](references/483-warning-letter-prevention.md) for prevention patterns + response templates.

---

## Inspection-week operations

### Front room (where inspector works)

- Designated front room (conference room, not someone's office)
- Front-room lead (often Quality Manager) accompanies inspector all day
- All requests routed through front-room lead
- Inspector requests evidence; front-room asks back-room

### Back room (where requests are fulfilled)

- Cross-functional team available
- Document retrieval, witness preparation, technical questions answered
- Inspector requests evidence; back-room delivers (filtered through front-room lead)

### Daily debrief

- End of each inspection day: review what was inspected, observations, next-day topics
- Prepare overnight any evidence needed for next day

### After inspection

- Form 483 review (if issued): consult with QA Lead + outside counsel
- 15 business days to respond
- Full corrective action plan
- Ongoing engagement with FDA office

---

## Tooling

| Script | Purpose |
|--------|---------|
| `scripts/qsr_readiness_score.py` | Score current QSR/QMSR state per subpart |
| `scripts/dhf_completeness_checker.py` | Validate Design History File completeness per device |

---

## References

- [fda-qsr-pre-inspection-checklist.md](references/fda-qsr-pre-inspection-checklist.md) — full pre-inspection punch list per subpart
- [483-warning-letter-prevention.md](references/483-warning-letter-prevention.md) — common triggers + prevention + response patterns

---

## Related skills

- `ra-qm-team/fda-consultant-specialist` — deep FDA program (510k, PMA, QMSR build)
- `ra-qm-team/quality-manager-qms-iso13485` — ISO 13485 QMS (QMSR harmonized)
- `ra-qm-team/risk-management-specialist` — ISO 14971 (required for QMSR)
- `ra-qm-team/capa-officer` — CAPA process specialist
- `ra-qm-team/qms-audit-expert` — internal/external QMS audits
- `ra-qm-team/audit-prep/compliance-readiness` — multi-framework readiness
