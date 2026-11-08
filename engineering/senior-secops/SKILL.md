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
  updated: 2026-11-08
  tags:
    - security-operations
    - vulnerability-management
    - incident-response
    - siem
---
# Senior SecOps Engineer

The agent scans source code for common vulnerability patterns (hardcoded secrets, SQL injection, XSS, command injection), checks dependency pins against a small built-in advisory list for npm/Python/Go, and collects code-level evidence for SOC 2, PCI-DSS, HIPAA and GDPR controls.

All three tools are regex and lookup based. They catch obvious, local patterns and miss anything that flows through helpers, variables or runtime config, and the advisory list is a sample, not a CVE feed. Use them as a fast first pass and CI tripwire; confirm with a real SAST tool (Semgrep, CodeQL) and a live advisory source (`pip-audit`, `npm audit`, OSV) before calling a codebase clean.

## Core Capabilities

- **Security scanner** — detect hardcoded secrets, SQL injection, XSS, command injection, and path traversal in source code.
- **Vulnerability assessor** — match npm / Python / Go dependency pins against a built-in advisory sample with CVSS scores, fixed versions, and a 0-100 risk score.
- **Compliance checker** — an evidence checklist: looks for code and config evidence of SOC 2, PCI-DSS, HIPAA and GDPR controls (access control, encryption, audit logging, auth strength). A failed control means "no evidence in the repo", not "control absent".
- **Security workflows** — audit, CI/CD security gate, CVE triage (with SLA tiers), and 5-phase incident response.
- **Standards & secure coding** — OWASP Top 10 prevention, secure-coding checklist, and language-specific BAD/GOOD patterns.

## When to Use

- Implementing security controls or hardening a codebase.
- Conducting a security audit or pre-release security pass.
- Responding to or triaging a newly disclosed CVE.
- Meeting SOC 2, PCI-DSS, HIPAA, or GDPR compliance requirements.
- Wiring SAST/dependency/compliance gates into CI/CD.

## Clarify First

Before the security pass, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Target path:** the codebase or dependency manifest to scan (the subject of every scanner).
- **Compliance framework:** SOC 2 / PCI-DSS / HIPAA / GDPR (`--framework`; changes which controls are verified).
- **Severity threshold:** the minimum severity to report or gate on (`--severity`; changes the report and CI pass/fail).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Tools

| Tool | Purpose | Example (runs as written) |
|------|---------|---------|
| `security_scanner.py` | Regex scan for secrets, SQL/command injection, XSS, path traversal (`--severity`, `--json`, `-o`, `-v`) | `python scripts/security_scanner.py assets/sample_app_flawed --severity high` |
| `vulnerability_assessor.py` | Match dependency pins against the built-in advisory sample; risk score (`--severity`, `--json`, `-o`) | `python scripts/vulnerability_assessor.py assets/sample_app_flawed` |
| `compliance_checker.py` | Code-evidence checklist per framework (`--framework soc2/pci-dss/hipaa/gdpr/all`, `--json`, `-o`) | `python scripts/compliance_checker.py assets/sample_app_sound --framework soc2` |

Exit codes: `security_scanner` and `vulnerability_assessor` exit `0` with no critical/high
findings and `1` when any remain; `compliance_checker` exits `0` at a code-evidence score of
70% or more and `1` below. All three exit `2` on bad input (target not found), so a typo in a
CI gate fails loudly. With `--json`, progress text goes to stderr and stdout is pure JSON.

Samples: `assets/sample_app_flawed/` (hardcoded secret, %-formatted and f-string SQL,
`os.system` concatenation, old pins) exits 1 on all three; `assets/sample_app_sound/` exits 0
on all three (use `--framework soc2` for the checker).

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
- Dependency pin checks against a built-in advisory sample for npm, Python, and Go ecosystems.
- Code-evidence checklists for SOC 2 Type II, PCI-DSS v4.0, HIPAA Security Rule, and GDPR.
- Security workflow orchestration including CI/CD gating, CVE triage, and incident response procedures.

**This skill does NOT cover:**

- Dynamic application security testing (DAST) or runtime analysis -- use OWASP ZAP or Burp Suite for live scanning.
- Infrastructure-as-code security (Terraform, CloudFormation misconfigurations) -- see the `senior-devops` skill for IaC hardening.
- Container image scanning or Kubernetes admission control -- see the `senior-devops` skill or use Trivy directly.
- Penetration testing execution or red-team operations -- these require specialized tooling and authorized human operators.

## Anti-Patterns

### Treating a Clean Scan as a Clean Bill of Health
**Mistake:** Reporting "no vulnerabilities" because `security_scanner.py` returned exit 0.
**Why it happens:** The exit code looks like a verdict.
**Instead:** Say what was checked. The scanner sees single-line patterns only; injection through a helper or a query builder is invisible to it. Pair it with a dataflow-aware SAST tool for anything release-gating.

### Quoting the Compliance Score to an Auditor
**Mistake:** Presenting the checker's percentage as SOC 2 or HIPAA readiness.
**Why it happens:** It is labelled with framework control IDs.
**Instead:** Use the failed list as an evidence to-do list. Most controls (policies, HR, vendor management, incident drills) live outside the code and must be evidenced separately.

### Relying on the Bundled Advisory List
**Mistake:** Taking a 0 from `vulnerability_assessor.py` to mean dependencies have no known CVEs.
**Why it happens:** The output looks like a CVE scan.
**Instead:** The list is a small sample for demonstration and CI wiring. Run the ecosystem's live auditor (`pip-audit`, `npm audit`, `govulncheck`, OSV) for real coverage.

## Files

| File | Purpose |
|------|---------|
| `scripts/security_scanner.py` | Source-code pattern scanner |
| `scripts/vulnerability_assessor.py` | Dependency pin check and risk score |
| `scripts/compliance_checker.py` | Framework code-evidence checklist |
| `assets/sample_app_flawed/` | Deliberately vulnerable app and old pins (all tools exit 1) |
| `assets/sample_app_sound/` | Parameterised, authenticated, logged app with evidence files (all tools exit 0) |
| `references/*.md` | Workflows, standards, CVE triage and compliance detail |
