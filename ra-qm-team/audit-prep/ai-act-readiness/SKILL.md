---
name: ai-act-readiness
description: >
  EU AI Act readiness assessment and sprint playbook. Use when preparing for the
  high-risk AI system deadlines (Dec 2027 / Aug 2028), when a notified-body conformity assessment
  is scheduled, or when GPAI (general-purpose AI) obligations apply.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: compliance
  domain: ra-qm-team
  updated: 2026-05-27
  tags: [eu-ai-act, ai-readiness, high-risk-ai, gpai, conformity-assessment, compliance, ai-governance]
---

# EU AI Act Readiness

Operational playbook for EU AI Act compliance readiness — focused on the sprint to demonstrate readiness for the high-risk AI deadlines (2 Dec 2027 for Annex III systems, 2 Aug 2028 for Annex I products) and ongoing conformity assessments.

When to use this skill vs. eu-ai-act-specialist:
- **This skill**: assessment imminent; need readiness sprint
- **eu-ai-act-specialist**: building AI Act compliance program; classifying systems; designing conformity processes

---

## When to use this skill

| Situation | Skill applies |
|-----------|---------------|
| High-risk deadline approaching (Dec 2027 Annex III, Aug 2028 Annex I) | Yes — readiness sprint |
| Notified body conformity assessment scheduled | Yes — full prep |
| GPAI model obligations apply (Aug 2025+) | Yes — GPAI-specific checklist |
| Annual readiness review | Yes — periodic sprint |
| Building AI Act program from scratch | Use `ra-qm-team/eu-ai-act-specialist` |
| AI system classification | Use `ra-qm-team/eu-ai-act-specialist` |

---

## Key AI Act timelines

| Date | Requirement |
|------|-------------|
| Aug 1, 2024 | AI Act enters into force |
| Feb 2, 2025 | Prohibited practices effective; AI literacy requirements |
| Aug 2, 2025 | GPAI provider obligations effective |
| Aug 2, 2026 | Article 50 transparency obligations effective |
| Dec 2, 2027 | High-risk requirements for Annex III systems (moved from Aug 2, 2026) |
| Aug 2, 2028 | High-risk requirements for AI in Annex I products (moved from Aug 2, 2027) |

Dates as amended by the Digital Omnibus on AI (Regulation (EU) 2026/1744, in force 27 July 2026). Check the [Official Journal text](https://eur-lex.europa.eu/eli/reg/2026/1744/oj) before relying on a date; secondary guidance written before July 2026 still shows the old ones.

---

## The readiness sprint

### 8-week sprint (high-risk system, conformity assessment prep)

```
Week 1-2: System classification confirmation; gap analysis
Week 3-5: Documentation buildout (technical file, risk management, data governance)
Week 6-7: Conformity assessment internal dry-run
Week 8: External notified-body engagement / assessment
```

### 4-week sprint (GPAI obligations)

```
Week 1: System classification (provider/deployer/importer/etc.)
Week 2: Documentation prep (model card, training data summary, copyright compliance)
Week 3: Risk assessment + transparency obligations
Week 4: Submission / publication of required information
```

---

## Critical AI Act areas

### Risk classification

Per Article 6 / Annex III, AI systems classify into risk categories:

| Category | Examples | Requirements |
|----------|----------|--------------|
| **Prohibited** | Social scoring; behavior manipulation of vulnerable groups | Cannot deploy |
| **High-risk** | Biometric ID; critical infrastructure; education; employment; access to essential services; law enforcement | Comprehensive obligations |
| **Limited-risk (transparency)** | Chatbots; deepfakes; emotion recognition | Disclosure obligation |
| **Minimal-risk** | Most enterprise AI; spam filters | Voluntary code of conduct |
| **GPAI** | Large language models; foundation models | Separate obligations (Article 51+) |

### High-risk system requirements (Articles 9-15, plus 16-22)

| Requirement | Article |
|-------------|---------|
| Risk management system | Art. 9 |
| Data governance + quality | Art. 10 |
| Technical documentation | Art. 11 |
| Record-keeping (logging) | Art. 12 |
| Transparency to users | Art. 13 |
| Human oversight | Art. 14 |
| Accuracy, robustness, cybersecurity | Art. 15 |
| Quality management system | Art. 17 |
| Conformity assessment | Art. 43 |
| Registration in EU database | Art. 71 |
| Post-market monitoring | Art. 72 |
| Serious incident reporting | Art. 73 |

### GPAI provider obligations (Article 53+)

| Requirement | Detail |
|-------------|--------|
| Technical documentation | Per Annex XI |
| Training data summary (public) | Sufficiently detailed |
| Copyright compliance | Honor opt-outs from text/data mining |
| Information to downstream providers | Enable downstream compliance |
| Code of practice compliance | (Optional but presumed conformity) |

### GPAI with systemic risk (Article 55, models > 10^25 FLOPs training compute)

Additional requirements:
- Model evaluations
- Adversarial testing
- Systemic risk assessment + mitigation
- Serious incident reporting
- Cybersecurity protection

---

## Clarify First

Before running the readiness assessment, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **AI system risk class:** high-risk (Annex III), GPAI, or limited-risk (determines whether to run the 8-week high-risk sprint or the 4-week GPAI sprint, and which checklist applies).
- **Trigger event:** a high-risk deadline (Dec 2027 Annex III, Aug 2028 Annex I), scheduled notified-body conformity assessment, GPAI obligations, or annual review (sets sprint length and scope).
- **Your role:** provider, deployer, or importer (determines which obligation set is assessed).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Quick start

1. **Run readiness score**: `python3 scripts/ai_act_readiness_score.py --config ai-system.yaml`
2. **Check GPAI obligations (if applicable)**: `python3 scripts/gpai_obligation_checker.py --model model.yaml`
3. **Pick sprint length** based on score + system risk class
4. **Execute sprint** per [references/ai-act-readiness-checklist.md](references/ai-act-readiness-checklist.md)

---

## Common AI Act readiness failures

- **Misclassification**: deploying system as "limited-risk" when it's actually "high-risk" (Annex III)
- **Risk management as one-time**: AI Act requires continuous risk management
- **Data governance gaps**: training data without representativeness analysis
- **Logging missing**: post-market monitoring requires logs you don't have
- **Human oversight theater**: oversight that can't actually intervene
- **GPAI training data summary missing**: required since Aug 2025
- **No conformity assessment plan**: assuming notified body assessment is automatic
- **AI literacy training skipped**: required for staff working with AI systems

---

## Tooling

| Script | Purpose |
|--------|---------|
| `scripts/ai_act_readiness_score.py` | Score current AI Act readiness per system |
| `scripts/gpai_obligation_checker.py` | Validate GPAI provider obligations (Article 53+) |

---

## Scope & Limitations

**In Scope:**
- Short-runway EU AI Act readiness sprints: 8 weeks for a high-risk system before conformity assessment, 4 weeks for GPAI provider obligations
- Per-article readiness scoring for one AI system, with Annex III classification warnings and a sprint recommendation, from `ai_act_readiness_score.py`
- GPAI applicability, per-obligation completion (Article 53+) and the Article 55 systemic-risk check from `gpai_obligation_checker.py`
- Punch lists for high-risk requirements (Articles 9-15, 17, 43, 71-73) and common readiness failures

**Out of Scope:**
- Building an AI Act compliance program or classifying systems from scratch (see `ra-qm-team/eu-ai-act-specialist/`)
- ISO 42001 AIMS certification prep (see `ra-qm-team/audit-prep/aims-audit/`)
- GDPR obligations for AI that processes personal data (see `ra-qm-team/audit-prep/gdpr-audit-prep/`)
- Performing the conformity assessment, registering the system in the EU database or reporting incidents

**Important Caveats:**
- Both tools read a YAML file you fill in. They check declared answers; they do not inspect the system, its data or its documentation.
- The readiness score uses the risk class you declare and only warns when the Annex III areas you list conflict with it. The systemic-risk check uses the training compute figure you enter.
- A high score is not a conformity assessment, a notified body opinion or legal advice.
- The timeline table reflects dates set when the skill was written. Application dates can be amended, so check the current text before planning around a deadline.

---

## References

- [ai-act-readiness-checklist.md](references/ai-act-readiness-checklist.md) — full punch list per requirement
- [high-risk-system-readiness-playbook.md](references/high-risk-system-readiness-playbook.md) — high-risk-specific deep prep

---

## Related skills

- `ra-qm-team/eu-ai-act-specialist` — deep AI Act program management
- `ra-qm-team/iso42001-ai-management` — ISO 42001 AIMS (companion AI governance)
- `ra-qm-team/audit-prep/aims-audit` — AIMS audit-prep variant
- `ra-qm-team/audit-prep/gdpr-audit-prep` — GDPR overlay for AI processing personal data
- `ra-qm-team/audit-prep/compliance-readiness` — multi-framework readiness
