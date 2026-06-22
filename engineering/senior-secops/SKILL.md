---
name: senior-secops
description: >
  SecOps for application security, vulnerability management, compliance, and secure
  development. Use when implementing security controls, conducting security audits, responding
  to vulnerabilities, or meeting compliance requirements.
license: MIT + Commons Clause
metadata:
  version: 1.1.0
  author: borghei
  category: engineering
  domain: security-operations
  updated: 2026-06-17
  tags:
    - security-operations
    - vulnerability-management
    - incident-response
    - siem
---
# Senior SecOps Engineer

The agent scans source code for security vulnerabilities (hardcoded secrets, SQL injection, XSS, command injection), assesses dependency CVEs across npm/Python/Go ecosystems, and verifies compliance against SOC 2, PCI-DSS, HIPAA, and GDPR frameworks.

## Core Capabilities

- **Security scanner** — detect hardcoded secrets, SQL injection, XSS, command injection, and path traversal in source code.
- **Vulnerability assessor** — scan npm / Python / Go dependency manifests for known CVEs with CVSS scores, fixed versions, and a 0-100 risk score.
- **Compliance checker** — verify SOC 2, PCI-DSS, HIPAA, and GDPR controls (access control, encryption, audit logging, auth strength).
- **Security workflows** — audit, CI/CD security gate, CVE triage (with SLA tiers), and 5-phase incident response.
- **Standards & secure coding** — OWASP Top 10 prevention, secure-coding checklist, and language-specific BAD/GOOD patterns.

## When to Use

- Implementing security controls or hardening a codebase.
- Conducting a security audit or pre-release security pass.
- Responding to or triaging a newly disclosed CVE.
- Meeting SOC 2, PCI-DSS, HIPAA, or GDPR compliance requirements.
- Wiring SAST/dependency/compliance gates into CI/CD.

## Clarify First

Before the security pass, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Target path** — the codebase or dependency manifest to scan (the subject of every scanner)
- [ ] **Compliance framework** — SOC 2 / PCI-DSS / HIPAA / GDPR (`--framework`; changes which controls are verified)
- [ ] **Severity threshold** — the minimum severity to report or gate on (`--severity`; changes the report and CI pass/fail)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Tools

| Tool | Purpose | Command |
|------|---------|---------|
| `security_scanner.py` | Scan source for secrets, injection, XSS, command injection, path traversal | `python scripts/security_scanner.py <target> --severity high --json --output report.json` |
| `vulnerability_assessor.py` | Scan dependency manifests for known CVEs and compute risk score | `python scripts/vulnerability_assessor.py <target> --severity critical` |
| `compliance_checker.py` | Verify SOC 2 / PCI-DSS / HIPAA / GDPR controls | `python scripts/compliance_checker.py <target> --framework soc2 --json --output soc2.json` |

## References

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/workflows-and-tooling.md](references/workflows-and-tooling.md)** — capability command reference, the 4 workflows (audit, CI/CD gate, CVE triage, incident response), full per-script flag/output/exit-code tables, and the tech stack. Read when running a workflow or invoking a script with specific flags.
- **[references/standards-and-playbook.md](references/standards-and-playbook.md)** — OWASP Top 10 prevention table, secure-coding checklist, SOC 2 / PCI-DSS / HIPAA / GDPR control tables, secure-coding BAD/GOOD code patterns, anti-patterns, troubleshooting table, and success criteria. Read when applying standards or diagnosing scanner behavior.
- **[references/security_standards.md](references/security_standards.md)** — deep OWASP Top 10 with code, secure coding practices, authentication standards, API security, and secrets management. Read for in-depth secure-coding guidance.
- **[references/vulnerability_management_guide.md](references/vulnerability_management_guide.md)** — vulnerability lifecycle, CVE triage process, CVSS scoring, remediation workflows, and dependency scanning. Read when managing CVEs end to end.
- **[references/compliance_requirements.md](references/compliance_requirements.md)** — full SOC 2 / PCI-DSS / HIPAA / GDPR control detail, evidence collection, compliance automation, and audit preparation. Read when preparing for an audit.

## Scope & Limitations

**This skill covers:**

- Static analysis of source code for common vulnerability classes (secrets, injection, XSS, command injection, path traversal).
- Dependency vulnerability assessment against a built-in CVE database for npm, Python, and Go ecosystems.
- Compliance verification for SOC 2 Type II, PCI-DSS v4.0, HIPAA Security Rule, and GDPR.
- Security workflow orchestration including CI/CD gating, CVE triage, and incident response procedures.

**This skill does NOT cover:**

- Dynamic application security testing (DAST) or runtime analysis -- use OWASP ZAP or Burp Suite for live scanning.
- Infrastructure-as-code security (Terraform, CloudFormation misconfigurations) -- see the `senior-devops` skill for IaC hardening.
- Container image scanning or Kubernetes admission control -- see the `senior-devops` skill or use Trivy directly.
- Penetration testing execution or red-team operations -- these require specialized tooling and authorized human operators.

## Integration Points

| Skill | Integration | Data Flow |
|-------|-------------|-----------|
| `senior-devops` | Infrastructure hardening and CI/CD pipeline configuration | Security scan results feed into deployment gates; DevOps provides container and IaC scanning |
| `senior-backend` | Secure coding patterns and input validation in server-side code | SecOps scanner findings drive backend remediation; backend applies parameterized queries and output encoding |
| `senior-qa` | Security test cases and regression verification after patches | Vulnerability reports generate QA test cases; QA confirms fixes do not introduce regressions |
| `senior-architect` | Threat modeling, defense-in-depth design, and zero-trust architecture | Compliance gaps inform architecture decisions; architect provides security design patterns |
| `code-reviewer` | Security-focused code review and pre-merge analysis | Scanner findings prioritize review focus areas; reviewer enforces secure coding standards |
| `senior-fullstack` | End-to-end security across frontend and API layers (XSS, CSRF, auth) | SecOps identifies frontend and API vulnerabilities; fullstack applies framework-level mitigations |
