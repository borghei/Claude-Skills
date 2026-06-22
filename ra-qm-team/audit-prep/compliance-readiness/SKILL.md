---
name: compliance-readiness
description: >
  Cross-framework compliance readiness orchestrator. Use when preparing for
  multi-framework certification (SOC 2 + ISO 27001 + NIST CSF), building a
  shared-evidence strategy, sequencing certifications, or mapping a control across
  frameworks.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: compliance
  domain: ra-qm-team
  updated: 2026-05-27
  tags: [compliance-readiness, multi-framework, shared-evidence, control-mapping, soc2, iso27001, nist, gdpr, hipaa]
---

# Compliance Readiness (Cross-Framework)

The orchestrator skill for organizations pursuing multiple compliance frameworks. Reduces duplication, accelerates certification, and shares evidence across SOC 2, ISO 27001, NIST CSF, GDPR, HIPAA, and others.

When to use this skill vs. framework-specific audit-prep:
- **This skill**: 2+ frameworks pursued in parallel; need shared-evidence strategy
- **Framework-specific** (`soc2-audit-prep`, `gdpr-audit-prep`, etc.): single-framework sprint

---

## When to use this skill

| Situation | Skill applies |
|-----------|---------------|
| Pursuing SOC 2 + ISO 27001 + NIST CSF in parallel | Yes — start here |
| Healthcare org pursuing SOC 2 + HIPAA + ISO 27001 | Yes |
| Building shared-evidence platform | Yes — see **shared evidence strategy** |
| Mapping one control to multiple frameworks | Yes — `scripts/shared_evidence_finder.py` |
| Deciding which framework to certify first | Yes — see **sequencing decisions** |
| Generating multi-framework roadmap | Yes — `scripts/readiness_roadmap_generator.py` |
| Single-framework audit prep | Use framework-specific skill |

---

## The strategic insight

Most controls are shared across compliance frameworks. A well-designed control catalog satisfies multiple frameworks simultaneously. Without coordination, you build separate evidence + procedures per framework — 3x the work, 3x the maintenance, 3x the auditor confusion.

Common shared controls:

| Control area | SOC 2 | ISO 27001 | NIST CSF | NIS2 | DORA | PCI-DSS | HIPAA | GDPR |
|--------------|-------|-----------|----------|------|------|---------|-------|------|
| Access control | CC6.1 | A.8.5 | PR.AA | Art.21.2.j | Art.9.4 | Req 7-8 | §164.312(d) | Art.32 |
| Encryption | CC6.7 | A.8.24 | PR.DS | Art.21.2.h | Art.9.2 | Req 3-4 | §164.312(a)(2)(iv) | Art.32 |
| Incident response | CC7.4 | A.5.24 | RS.MA | Art.23 | Art.17 | Req 12.10 | §164.308(a)(6) | Art.33 |
| Risk assessment | CC3.1 | Cl.6.1 | ID.RA | Art.21.1 | Art.6 | Req 12.2 | §164.308(a)(1) | Art.35 |
| Logging | CC7.2 | A.8.15 | DE.CM | Art.21.2.b | Art.10 | Req 10 | §164.312(b) | Art.30 |
| Vendor management | CC9.2 | A.5.19 | GV.SC | Art.21.2.d | Art.28 | Req 12.8 | §164.308(b) | Art.28 |

See [references/control-mapping-soc2-iso27001-nist.md](references/control-mapping-soc2-iso27001-nist.md) for the full mapping.

---

## Sequencing decisions

Which framework to pursue first?

### Common patterns

**SaaS / Tech (B2B enterprise customers):**
- SOC 2 Type I first (3-6 months) — customer-demanded entry ticket
- SOC 2 Type II (next 6-12 months after Type I)
- ISO 27001 (often after SOC 2 Type II; substantial overlap)
- NIST CSF (as internal framework; supports SOC 2 / ISO 27001)
- GDPR (separately, ongoing)

**Healthcare (US):**
- HIPAA (immediately if covered entity / BA)
- SOC 2 (for tech-side customer requirements)
- ISO 27001 (for international expansion)

**FinTech / financial services (EU):**
- DORA (mandatory effective Jan 2025)
- NIS2 (mandatory)
- PCI-DSS (if handling card data)
- ISO 27001 (standard)
- SOC 2 (for B2B customers)

**Medical devices:**
- ISO 13485 / 14971 / MDR / FDA (industry mandatory)
- ISO 27001 (for digital health components)
- SOC 2 (for SaaS components)

### Sequencing factors

1. **Customer demand** — what blocks deals?
2. **Regulatory mandate** — what's required by law?
3. **Time to certify** — SOC 2 Type I (3-6 mo) vs ISO 27001 (6-12 mo)
4. **Shared-evidence opportunity** — frameworks that overlap (SOC 2 + ISO 27001)
5. **Cost** — certification + ongoing surveillance

---

## Shared evidence strategy

### Strategy 1: Common control catalog

Build one control catalog covering all in-scope frameworks. Each control maps to multiple frameworks. One implementation; one evidence trail.

```
Control: Access Reviews (Quarterly)
- SOC 2: CC6.3
- ISO 27001: A.5.18
- NIST CSF: PR.AA-04
- HIPAA: §164.308(a)(4)
- GDPR: Art.32 (security of processing)

Evidence: Quarterly access-review records, signed by team lead
Frequency: Quarterly
Owner: IT Security
```

One artifact satisfies five frameworks.

### Strategy 2: Unified evidence collection

Single source-of-truth for evidence (Drata / Vanta / Thoropass / Sprinto / homegrown):
- Configurations + access reviews + change records auto-collected
- Tagged per framework
- Auditor (per framework) gets relevant subset

### Strategy 3: Single management review

Annual management review covers all frameworks:
- SOC 2 management review
- ISO 27001 management review (Clause 9.3)
- ISO 42001 management review (if AIMS)
- Internal audit findings
- Risk register update
- Continual improvement decisions

### Strategy 4: Single internal audit

Plan internal audit to cover overlapping clauses:
- ISO 27001 Clause 9.2 internal audit
- SOC 2 controls testing
- NIST CSF self-assessment
- All produce one audit report; distributed per framework

---

## Multi-framework readiness sprint

### 16-week sprint (initial: SOC 2 + ISO 27001 in parallel)

```
Weeks 1-4: Common control catalog build; gap analysis per framework
Weeks 5-8: Gap remediation (technical + procedural)
Weeks 9-12: Evidence collection + walkthroughs
Weeks 13-14: SOC 2 audit
Weeks 15-16: ISO 27001 Stage 1
(then ISO 27001 Stage 2 ~4-8 weeks later)
```

### 12-week sprint (annual: SOC 2 + ISO 27001 surveillance)

```
Weeks 1-2: Audit readiness assessment per framework
Weeks 3-6: Gap remediation
Weeks 7-9: Walkthroughs + evidence finalization
Weeks 10-12: Audits (sequential or parallel depending on auditor capacity)
```

---

## Clarify First

Before generating the roadmap, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Target frameworks** — which set (SOC 2, ISO 27001, NIST CSF, GDPR, HIPAA, DORA…) is pursued in parallel (drives the control mapping and shared-evidence strategy)
- [ ] **Industry and region** — determines which frameworks are legally mandated vs customer-demanded, and the sequencing
- [ ] **Initial vs renewal** — first-time certification vs annual surveillance (picks the 16-week vs 12-week sprint)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the roadmap.

## Quick start

1. **Score multi-framework readiness**: `python3 scripts/multi_framework_scorer.py --config controls.yaml`
2. **Find shared evidence opportunities**: `python3 scripts/shared_evidence_finder.py --frameworks SOC2,ISO27001`
3. **Generate roadmap**: `python3 scripts/readiness_roadmap_generator.py --target-frameworks SOC2,ISO27001,GDPR`
4. **Execute sprint** per [references/multi-framework-readiness-matrix.md](references/multi-framework-readiness-matrix.md)

---

## Common multi-framework readiness failures

- **Separate teams per framework** — duplicates work, inconsistent decisions, wasted time
- **Separate evidence collection** — same screenshot taken 3x for 3 frameworks
- **Auditor doesn't accept overlap** — push back; most accept SOC 2 evidence for ISO 27001 controls
- **Framework-specific tooling** — one tool per framework instead of unified GRC platform
- **No control owner** — control exists across frameworks but no single owner
- **Mapping not maintained** — control changes; mappings go stale
- **Auditor cycles cause crunches** — schedule auditors not to overlap (or do overlap by design)

---

## Tooling

| Script | Purpose |
|--------|---------|
| `scripts/multi_framework_scorer.py` | Score readiness across multiple frameworks |
| `scripts/shared_evidence_finder.py` | Identify shared controls; map evidence to frameworks |
| `scripts/readiness_roadmap_generator.py` | Generate multi-framework readiness roadmap |

---

## References

- [multi-framework-readiness-matrix.md](references/multi-framework-readiness-matrix.md) — per-framework requirements + cadences + cost
- [shared-evidence-strategy.md](references/shared-evidence-strategy.md) — implementation patterns for shared evidence
- [control-mapping-soc2-iso27001-nist.md](references/control-mapping-soc2-iso27001-nist.md) — detailed control mapping

---

## Related skills

- `ra-qm-team/soc2-compliance-expert` — deep SOC 2 program
- `ra-qm-team/information-security-manager-iso27001` — deep ISO 27001 program
- `ra-qm-team/nist-csf-specialist` — deep NIST CSF program
- `ra-qm-team/gdpr-dsgvo-expert` — deep GDPR program
- `ra-qm-team/fda-consultant-specialist` — deep FDA program
- `ra-qm-team/infrastructure-compliance-auditor` — cross-framework infra audit
- `ra-qm-team/audit-prep/*` — framework-specific audit-prep skills
