---
name: soc2-audit-prep
description: >
  SOC 2 audit-prep playbook: the 4/8/12-week sprint to audit-ready for a Type I or
  Type II observation. Use when the audit is scheduled, when readiness assessment
  surfaced gaps and you need a sprint plan, or when evidence is missing or stale.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: compliance
  domain: ra-qm-team
  updated: 2026-05-27
  tags: [soc2, audit-prep, trust-services-criteria, evidence-collection, sprint-planning, compliance]
---

# SOC 2 Audit Prep

Operational playbook for SOC 2 audit preparation. Designed to be picked up 4-12 weeks before an audit and run as a sprint to closure. Pairs with our deep `ra-qm-team/soc2-compliance-expert` skill (which builds the program from scratch).

When to use this skill vs. soc2-compliance-expert:
- **This skill**: audit scheduled in 4-12 weeks; gaps known; need to execute the sprint
- **soc2-compliance-expert**: building the SOC 2 program; designing controls; multi-quarter effort

---

## When to use this skill

| Situation | Skill applies |
|-----------|---------------|
| SOC 2 audit scheduled, need readiness sprint | Yes — start here |
| Type I audit in 4-12 weeks | Yes — use 4 or 8-week sprint plan |
| Type II observation period closing soon | Yes — use 12-week sprint plan |
| Readiness assessment surfaced gaps | Yes — `scripts/soc2_readiness_score.py` + `evidence_gap_finder.py` |
| Building SOC 2 program from scratch | Use `ra-qm-team/soc2-compliance-expert` instead |

---

## The audit-prep sprint at a glance

### 4-week sprint (Type I, mostly ready)

```
Week 1: Inventory + scoping
  - Confirm Trust Services Criteria scope (always Security; plus chosen others)
  - Pull current evidence per criterion
  - Identify gaps via scripts/evidence_gap_finder.py
  - Auditor kickoff scheduled

Week 2: Gap closure
  - Policy updates / approvals
  - Technical control fixes (MFA universal, logging coverage, etc.)
  - Evidence retrieval (access reviews, change tickets, on-call records)
  - Auditor information request preparation

Week 3: Evidence finalization
  - All evidence packets compiled per criterion
  - Walkthroughs / interviews scheduled with key control owners
  - Findings remediation
  - Pre-audit checkpoint with auditor (informal)

Week 4: Audit week
  - Walkthroughs executed
  - Sample testing
  - Q&A
  - Management responses to findings
```

### 8-week sprint (Type I, gaps remaining)

```
Weeks 1-2: Inventory + scoping + gap identification (same as 4-week W1)
Weeks 3-5: Gap closure (policies, technical, process)
Weeks 6-7: Evidence finalization + walkthroughs
Week 8: Audit week
```

### 12-week sprint (Type II observation prep)

```
Weeks 1-2: Inventory + scope + gap identification + auditor kickoff
Weeks 3-4: Gap closure
Weeks 5-12: Observation period (controls operating; evidence accumulating)
After observation period: audit week
```

See [references/evidence-collection-sprint-plan.md](references/evidence-collection-sprint-plan.md) for the detailed week-by-week plans.

---

## The pre-audit punch list

Standard pre-audit punch list, organized by Trust Services Criterion:

### CC1-CC5 (Common Criteria — control environment)
- [ ] Information security policy approved + dated within 12 months
- [ ] Org chart current (reflects actual reporting lines)
- [ ] Risk assessment performed + documented within 12 months
- [ ] Board / leadership oversight evidence (minutes referencing security)
- [ ] Code of conduct signed by all employees
- [ ] Background checks documented for all hires

### CC6 (Logical and Physical Access)
- [ ] SSO enforced for all production systems
- [ ] MFA universal (no exceptions documented for production access)
- [ ] Access review evidence (quarterly minimum)
- [ ] Privileged access management (PAM) for admin/root accounts
- [ ] Physical security evidence (office badge logs, data center attestation)
- [ ] Encryption at rest / in transit verified

### CC7 (System Operations)
- [ ] Vulnerability management evidence (scans, remediation tracking)
- [ ] Monitoring and alerting documented + tested
- [ ] Incident response plan + documented incidents from past period
- [ ] Business continuity / DR plan + test evidence
- [ ] Backup verification (not just configured — tested restore)

### CC8 (Change Management)
- [ ] Code change tickets with peer review + approval
- [ ] Production deployment evidence (who, what, when, approvers)
- [ ] Emergency change process documented + sample tickets

### CC9 (Risk Mitigation / Vendors)
- [ ] Vendor inventory current
- [ ] Vendor due diligence evidence per vendor
- [ ] Vendor SOC 2 reports collected (annual)

### A1 (Availability — if in scope)
- [ ] SLA monitoring + actuals
- [ ] Capacity planning evidence
- [ ] Recovery objective testing (RTO/RPO)

### PI1 (Processing Integrity — if in scope)
- [ ] Data validation controls documented
- [ ] Error handling + reconciliation evidence

### C1 (Confidentiality — if in scope)
- [ ] Data classification + handling procedures
- [ ] Encryption verified

### P1 (Privacy — if in scope)
- [ ] Privacy notice published + dated
- [ ] Data subject rights process documented
- [ ] Consent management evidence

See [references/soc2-pre-audit-punch-list.md](references/soc2-pre-audit-punch-list.md) for the detailed punch list with evidence templates per item.

---

## Clarify First

Before running the audit-prep sprint, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Audit type** — Type I (point-in-time) vs Type II (observation period) (sets the 4/8 vs 12-week sprint and the evidence-over-time requirement)
- [ ] **TSC scope** — which Trust Services Criteria beyond mandatory Security (Availability, Processing Integrity, Confidentiality, Privacy) (determines which punch-list sections apply)
- [ ] **Readiness score / gap level** — picks the 4-week vs 8-week vs 12-week sprint (or postpone)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the sprint plan.

## Quick start

1. **Run readiness score**: `python3 scripts/soc2_readiness_score.py --config controls.yaml`
2. **Identify evidence gaps**: `python3 scripts/evidence_gap_finder.py --evidence evidence.yaml --tsc CC6`
3. **Pick sprint length** based on score:
   - Score > 90: 4-week sprint
   - Score 75-90: 8-week sprint
   - Score < 75: 12-week sprint or postpone audit
4. **Execute sprint** per [references/evidence-collection-sprint-plan.md](references/evidence-collection-sprint-plan.md)
5. **Pre-audit checkpoint** with auditor 1 week before

---

## Common audit-prep failures

- **No designated audit owner.** Sprint flounders. Assign one person Day 1.
- **Treating evidence as one-time.** Type II requires controls operating over observation period. Evidence must accumulate continuously, not just at the end.
- **Untested backups.** Configuring backups isn't enough; you need restore test evidence.
- **Access review checked but not enforced.** Reviews happen; access not actually removed when flagged.
- **Vendor SOC 2 reports missing or stale.** Audit checks subservice org evidence.
- **No incident in observation period.** Looks suspicious to auditors. Either you had none (unusual) or you're not detecting them.
- **Late discovery of carve-out vs inclusive subservice orgs.** Re-scoping mid-sprint is painful.

---

## Tooling

| Script | Purpose |
|--------|---------|
| `scripts/soc2_readiness_score.py` | Score current state (0-100) per TSC; identify pillars needing attention |
| `scripts/evidence_gap_finder.py` | Cross-reference required evidence vs collected; output gap list with priorities |

---

## References

- [soc2-pre-audit-punch-list.md](references/soc2-pre-audit-punch-list.md) — detailed punch list per TSC with evidence templates
- [evidence-collection-sprint-plan.md](references/evidence-collection-sprint-plan.md) — 4/8/12-week sprint plans with week-by-week deliverables

---

## Related skills

- `ra-qm-team/soc2-compliance-expert` — deep SOC 2 program management (multi-quarter)
- `ra-qm-team/audit-prep/compliance-readiness` — multi-framework readiness (SOC 2 + ISO 27001 + NIST)
- `ra-qm-team/infrastructure-compliance-auditor` — automated infra scanning for evidence
- `engineering/observability-designer` — logging / monitoring evidence
