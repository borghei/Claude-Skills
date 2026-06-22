---
name: aims-audit
description: >
  ISO 42001 AI Management System (AIMS) audit-prep playbook. Use when an ISO 42001
  certification audit is scheduled (Stage 1 or Stage 2), when a surveillance or
  internal AIMS audit is due, or when preparing an AI Impact Assessment (AIIA).
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: compliance
  domain: ra-qm-team
  updated: 2026-05-27
  tags: [iso42001, aims, ai-management-system, audit-prep, certification, ai-governance, ai-impact-assessment]
---

# AIMS Audit Prep (ISO 42001)

Operational playbook for ISO 42001:2023 AI Management System (AIMS) audit preparation. Whether targeting initial certification, surveillance audit, or annual internal audit.

When to use this skill vs. iso42001-ai-management:
- **This skill**: audit imminent; need readiness sprint
- **iso42001-ai-management**: building AIMS from scratch; multi-quarter program

---

## When to use this skill

| Situation | Skill applies |
|-----------|---------------|
| ISO 42001 Stage 1 audit scheduled | Yes — documentation review prep |
| Stage 2 (onsite/operational) audit | Yes — operational evidence sprint |
| Annual surveillance audit | Yes — surveillance prep |
| Internal AIMS audit | Yes — internal audit playbook |
| AI Impact Assessment for new system | Yes — `scripts/ai_impact_assessment_checker.py` |
| Building AIMS from scratch | Use `ra-qm-team/iso42001-ai-management` |

---

## ISO 42001 audit structure

### Stage 1 (documentation review)

- Auditor reviews AIMS documentation (typically 1-3 days)
- Confirms scope, applicability, key documents present
- Identifies gaps before Stage 2
- Typically 2-3 weeks before Stage 2

### Stage 2 (operational assessment)

- Auditor onsite (or remote) verifies AIMS operating effectively
- 3-10 days depending on scope + system count
- Walkthroughs, interviews, evidence sampling
- Conclusion: certification recommended (subject to non-conformity closure) or not

### Surveillance audits

- Annual; reduced scope vs initial
- Typically 1-3 days
- Focus on high-risk areas + changes since prior audit

### Re-certification (year 3)

- Full audit; similar to initial
- Typically every 3 years

---

## AIMS audit-prep sprint

### 4-week sprint (mature AIMS, surveillance audit)

```
Week 1: Internal audit + gap analysis
Week 2: Remediation + AI inventory refresh
Week 3: Documentation review + walkthrough rehearsal
Week 4: Auditor onsite
```

### 8-week sprint (Stage 1 + Stage 2 initial certification)

```
Weeks 1-3: AIMS documentation completion (Annex A controls coverage)
Weeks 4-5: Stage 1 audit + gap closure
Weeks 6-7: Stage 2 operational evidence prep + mock walkthroughs
Week 8: Stage 2 audit
```

---

## ISO 42001 clauses + Annex A controls

### Clauses (4-10): management system

| Clause | Topic |
|--------|-------|
| 4 | Context of the organization |
| 5 | Leadership |
| 6 | Planning (including AI risk + AI objectives) |
| 7 | Support (resources, competence, awareness, communication, documentation) |
| 8 | Operation (AI lifecycle, supplier relationships) |
| 9 | Performance evaluation (monitoring, internal audit, management review) |
| 10 | Improvement (nonconformity, continual improvement) |

### Annex A controls (10 areas)

| Annex A area | Topics |
|--------------|--------|
| A.2 | Policies related to AI |
| A.3 | Internal organization |
| A.4 | Resources for AI systems |
| A.5 | Assessing impacts of AI systems |
| A.6 | AI system lifecycle |
| A.7 | Data for AI systems |
| A.8 | Information for interested parties |
| A.9 | Use of AI systems |
| A.10 | Third-party relationships |

---

## Critical audit areas

### AI Inventory + Impact Assessments

| Item | Evidence | Common gap |
|------|----------|------------|
| Complete AI system inventory | Inventory document | Shadow AI not captured |
| AI Impact Assessment (AIIA) per system | Per-system AIIA | Skipped for "low-risk" systems |
| AIIA reviewed periodically | Review records | One-time only |
| Risk classification of systems | Per system | Not documented |

### AI Policy + Governance

| Item | Evidence | Common gap |
|------|----------|------------|
| AI policy approved + dated | Signed policy | Not signed / stale |
| AI ethics principles | Documented principles | Generic; not actionable |
| AI governance body | Charter / minutes | Not formalized |
| Roles + responsibilities | RACI | Not defined |

### AI Lifecycle Management (Annex A.6)

| Item | Evidence | Common gap |
|------|----------|------------|
| AI development lifecycle defined | Process documentation | Not formalized |
| Data quality controls | Per system | Generic only |
| Model validation procedures | Per system | Validation skipped |
| AI system testing | Per system | Inadequate testing |
| Deployment controls | Per system | No controls |
| Operational monitoring | Per system | Drift not monitored |
| Decommissioning procedures | Per system | Not defined |

### Data Governance (Annex A.7)

| Item | Evidence | Common gap |
|------|----------|------------|
| Data sources documented | Per system | Vague |
| Data quality assessed | Quality metrics | Not measured |
| Data lineage tracked | Documentation | Untracked |
| Sensitive data protection | Controls | Insufficient |

### Third-party AI (Annex A.10)

| Item | Evidence | Common gap |
|------|----------|------------|
| Third-party AI inventory | List | Incomplete |
| Vendor due diligence for AI | Per vendor | Generic IT only |
| Contract terms for AI vendors | AI-specific clauses | Standard MSA only |

---

## Clarify First

Before running the audit-prep, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Audit type and stage** — Stage 1 documentation review, Stage 2 operational, surveillance, or internal (sets sprint length and whether the focus is documentation or operational evidence)
- [ ] **AIMS maturity** — mature system vs building from gaps (picks the 4-week vs 8-week sprint)
- [ ] **AI systems in scope** — which systems and how many (drives the AIIA count and Annex A coverage)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the readiness assessment.

## Quick start

1. **Run readiness score**: `python3 scripts/aims_readiness_score.py --config aims-controls.yaml`
2. **Check AIIA per system**: `python3 scripts/ai_impact_assessment_checker.py --aiia system-aiia.yaml`
3. **Pick sprint length** based on score
4. **Execute sprint** per [references/iso42001-aims-readiness-checklist.md](references/iso42001-aims-readiness-checklist.md)

---

## Common AIMS audit findings

- **AI inventory incomplete** — shadow AI not captured
- **AIIA missing** for systems that look "small" but have impact
- **AI lifecycle process** not implemented (designed only)
- **Data governance generic** — not AI-specific
- **Performance monitoring missing** — drift not detected
- **AI policy stale** — written before current AI deployment
- **Third-party AI vendors** not assessed
- **Continual improvement** not evidenced

---

## Tooling

| Script | Purpose |
|--------|---------|
| `scripts/aims_readiness_score.py` | Score AIMS readiness per clause + Annex A area |
| `scripts/ai_impact_assessment_checker.py` | Validate AI Impact Assessment completeness |

---

## References

- [iso42001-aims-readiness-checklist.md](references/iso42001-aims-readiness-checklist.md) — punch list per clause + Annex A
- [aims-internal-audit-playbook.md](references/aims-internal-audit-playbook.md) — internal audit execution playbook

---

## Related skills

- `ra-qm-team/iso42001-ai-management` — deep ISO 42001 AIMS program management
- `ra-qm-team/eu-ai-act-specialist` — EU AI Act regulatory companion
- `ra-qm-team/audit-prep/ai-act-readiness` — AI Act audit-prep variant
- `ra-qm-team/audit-prep/compliance-readiness` — multi-framework readiness
