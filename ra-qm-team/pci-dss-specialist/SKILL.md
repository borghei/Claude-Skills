---
name: pci-dss-specialist
description: >
  PCI DSS v4.0 payment card data security compliance, assessment, and
  implementation. Use for PCI DSS scoping, cardholder data environment (CDE)
  security, SAQ and ROC preparation, QSA engagement, tokenization, and merchant
  compliance.
license: MIT + Commons Clause
metadata:
  version: 1.1.0
  author: borghei
  category: compliance
  domain: payment-security
  updated: 2026-06-15
  tags: [pci-dss, payment-security, tokenization, cardholder-data]
---
# PCI-DSS v4.0 Specialist

Implement, assess, and maintain compliance with the Payment Card Industry Data Security Standard version 4.0 — the global standard for protecting cardholder data in payment processing environments. Covers CDE scoping, SAQ/ROC selection, gap assessment against all 12 requirements, scope reduction (tokenization, P2PE, segmentation), and the future-dated v4.0 controls that became mandatory March 31, 2025.

## Core Capabilities

- **Compliance assessment** — score against all 12 PCI DSS v4.0 requirements, identify gaps, and prioritize remediation (`pci_compliance_checker.py`)
- **Scoping & SAQ selection** — map the cardholder data environment, classify connected and security-impacting systems, and determine the correct SAQ type or ROC requirement (`pci_scope_analyzer.py`)
- **Scope reduction** — tokenization, P2PE, network segmentation, and outsourced/iFrame processing to remove systems from scope
- **v4.0 readiness** — MFA for all CDE access, 12-char passwords, payment-page script controls (6.4.3/11.6.1), anti-phishing, automated log review, targeted risk analysis
- **Infrastructure controls** — network segmentation, TLS/DNS, endpoint/POS, cloud (AWS/Azure/GCP), container, and API security; encryption key lifecycle and DUKPT

## When to Use

Trigger on: "PCI DSS", "payment card security", "cardholder data", "PCI compliance", "payment security", "PCI assessment", "SAQ", "ROC", "QSA", "credit card security", "payment processing security", "tokenization", "CDE scoping", or "merchant level compliance".

## Clarify First

Before running the assessment or scoping, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Business model / payment flow** — how cards are accepted (e-commerce, terminal, P2PE, fully outsourced/iFrame) (determines the CDE scope and correct SAQ type)
- [ ] **Merchant / service-provider level** — annual transaction volume (sets the validation path: SAQ vs ROC)
- [ ] **CDE scope** — which systems store, process, or transmit cardholder data plus connected systems (drives which of the 12 requirements are in scope)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the report.

## Quick Start

```bash
# Check PCI compliance status (JSON report)
python scripts/pci_compliance_checker.py --input controls.json --output compliance_report.json

# Compliance gap report for stakeholders (Markdown)
python scripts/pci_compliance_checker.py --input controls.json --format markdown --output gap_report.md

# Determine SAQ type / analyze CDE scope
python scripts/pci_scope_analyzer.py --input business_model.json --output scope_report.json
python scripts/pci_scope_analyzer.py --input business_model.json --format markdown --output scope_analysis.md
```

Run `--requirements 3,4,7,8` to scope the checker to specific requirements. Full tool detail, input JSON formats, and flag reference live in the tools reference below.

## References

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/requirements-and-changes.md](references/requirements-and-changes.md)** — PCI DSS overview, the 12 requirements deep-dive (objective + key sub-requirements + implementation guidance each), and the v4.0 changes / future-dated requirements summary. Read when implementing or explaining a requirement.
- **[references/pci-dss-requirements-guide.md](references/pci-dss-requirements-guide.md)** — tabular reference: every sub-requirement with testing procedures and v4.0 change status. Read when you need exact sub-requirement IDs or auditor testing procedures.
- **[references/scoping-and-assessment.md](references/scoping-and-assessment.md)** — CDE definition and system classification, scope reduction strategies, SAQ types + selection decision tree, assessment types (SAQ/ROC/AOC), and merchant/service-provider levels. Read when scoping or choosing a validation path.
- **[references/infrastructure-controls-and-roadmap.md](references/infrastructure-controls-and-roadmap.md)** — technical controls (segmentation, DNS/TLS, endpoint/POS, cloud, container, API, tokenization architecture, key management) and the 5-phase 12-month compliance roadmap. Read when building or planning the program.
- **[references/pci-infrastructure-security.md](references/pci-infrastructure-security.md)** — deep architecture: reference network diagrams, per-cloud build-outs, mPOS, e-commerce script controls, and Kubernetes manifests. Read when designing CDE infrastructure in detail.
- **[references/tools-validation-troubleshooting.md](references/tools-validation-troubleshooting.md)** — full tool capabilities, input JSON formats, CLI flag tables, validation checkpoints, troubleshooting table, and success criteria. Read when running the tools or validating an engagement.

## Scope & Limitations

**In Scope:**
- PCI DSS v4.0/v4.0.1 compliance assessment against all 12 requirements
- SAQ type determination based on business model and payment processing architecture
- CDE scoping with connected system and security-impacting system identification
- Technical control validation (encryption, access control, logging, network segmentation)
- Compliance scoring with per-requirement gap analysis and remediation priorities
- Scope reduction strategy recommendations (tokenization, segmentation, P2PE)

**Out of Scope:**
- Approved Scanning Vendor (ASV) vulnerability scans (requires PCI SSC-approved ASV vendor)
- Qualified Security Assessor (QSA) on-site assessment or Report on Compliance (ROC) generation
- Payment application security validation (PA-DSS / PCI SSF scope)
- PIN Transaction Security (PTS) device certification
- Card brand-specific program requirements (Visa, Mastercard, Amex each have additional program rules)
- Legal advice on contractual obligations with acquiring banks or card brands
- Real-time transaction monitoring or fraud detection

## Integration Points

| Skill | Integration |
|-------|------------|
| [infrastructure-compliance-auditor](../infrastructure-compliance-auditor/) | Validates network segmentation, TLS configuration, endpoint security, and logging controls that satisfy PCI DSS Requirements 1, 2, 4, 10, 11 |
| [nist-csf-specialist](../nist-csf-specialist/) | CSF functions map to PCI DSS requirements; use the control mapper to build unified control matrices for dual-compliance programs |
| [soc2-compliance-expert](../soc2-compliance-expert/) | SOC 2 CC6 (access), CC7 (operations), CC8 (change management) overlap significantly with PCI DSS; leverage shared evidence |
| [information-security-manager-iso27001](../information-security-manager-iso27001/) | ISO 27001 Annex A controls provide a management system framework supporting PCI DSS compliance |
| [nis2-directive-specialist](../nis2-directive-specialist/) | EU entities subject to both NIS2 and PCI DSS can map shared controls (encryption, incident response, access control) |
