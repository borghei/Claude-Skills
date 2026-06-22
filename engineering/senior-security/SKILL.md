---
name: senior-security
description: >
  STRIDE threat modeling, DREAD risk scoring, secret detection, and secure architecture
  design. Use when conducting threat models, reviewing code for vulnerabilities, designing
  defense-in-depth, or scanning for hardcoded secrets.
license: MIT + Commons Clause
metadata:
  version: 1.1.0
  author: borghei
  category: engineering
  domain: application-security
  updated: 2026-06-17
  tags: [owasp, threat-modeling, penetration-testing, application-security]
---
# Senior Security Engineer

The agent performs STRIDE threat analysis with DREAD risk scoring, designs defense-in-depth security architectures with Zero Trust principles, conducts secure code reviews against OWASP Top 10, and scans codebases for hardcoded secrets across 20+ credential patterns.

## Core Capabilities

- **Threat modeling** — STRIDE per-element analysis, DREAD risk scoring, DFD creation, attack trees, and mitigation mapping.
- **Security architecture** — defense-in-depth layering, Zero Trust, authentication pattern selection (OAuth/OIDC, JWT, mTLS, FIDO2), and encryption strategy.
- **Vulnerability assessment** — automated (SAST/DAST/dependency/secret) plus manual testing, OWASP Top 10 mapping, severity classification, and remediation tracking.
- **Secure code review** — auth/authz, data handling, and crypto review with a checklist and secure-vs-insecure pattern catalog.
- **Incident response** — triage, containment, eradication, recovery, post-mortem, with severity tiers and runbook checklist.
- **Secret detection** — `secret_scanner.py` finds 20+ credential patterns (AWS/GCP/Azure, GitHub/Slack/Stripe, private keys); CI/CD-ready exit codes.
- **Compliance mapping** — OWASP ASVS, CIS Benchmarks, NIST CSF, PCI-DSS, HIPAA, SOC 2 at the application layer.

## When to Use

- Conducting a threat model or attack-surface analysis on a system or component.
- Reviewing code for vulnerabilities before deployment.
- Designing a secure, defense-in-depth or Zero Trust architecture.
- Scanning a codebase for hardcoded secrets and credentials.
- Running a vulnerability assessment or planning incident response.

## Clarify First

Before the threat model or scan, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Target component/system** — what to threat-model or scan (`--component`; defines the STRIDE analysis scope)
- [ ] **Assets & trust boundaries** — what is being protected and where untrusted input enters (drives DREAD scoring and mitigations)
- [ ] **Task** — threat model / code vuln review / secret scan / incident-response plan (selects the tool and the output)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Tools

| Tool | Purpose | Command |
|------|---------|---------|
| `threat_modeler.py` | STRIDE threat analysis with DREAD risk scoring and mitigation recommendations | `python scripts/threat_modeler.py --component "API Gateway" --json` |
| `secret_scanner.py` | Detect hardcoded secrets/credentials across 20+ patterns (CI/CD-ready exit codes) | `python scripts/secret_scanner.py /path/to/project --severity high` |

## References

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/security-workflows.md](references/security-workflows.md)** — the 5 full workflows (threat modeling, security architecture, vulnerability assessment, secure code review, incident response) with all decision matrices (STRIDE, OWASP Top 10, severity, code-review checklist), the security tools catalog, compliance frameworks, security headers, anti-patterns, troubleshooting table, and success criteria. Read when executing any security workflow.
- **[references/threat-modeling-guide.md](references/threat-modeling-guide.md)** — STRIDE methodology, attack trees, DREAD scoring, DFD creation, threat templates. Read when building a threat model.
- **[references/security-architecture-patterns.md](references/security-architecture-patterns.md)** — Zero Trust, defense-in-depth, authentication patterns (OAuth/PKCE, JWT, MFA), API security, data protection, secret management. Read when designing secure architecture.
- **[references/cryptography-implementation.md](references/cryptography-implementation.md)** — AES-GCM, ChaCha20, RSA, Ed25519, password hashing (Argon2/bcrypt), HMAC, key management/rotation, HSM integration, common crypto mistakes. Read when implementing or reviewing cryptography.
- **[references/tool-reference.md](references/tool-reference.md)** — full flag tables, usage examples, and output formats for `threat_modeler.py` and `secret_scanner.py`. Read when running the bundled scripts.

## Scope & Limitations

**This skill covers:**
- Application-level security: threat modeling, secure code review, secret detection, and vulnerability assessment for web applications and APIs.
- Security architecture design: defense-in-depth layering, Zero Trust patterns, authentication/authorization model selection, and encryption strategy.
- Incident response planning: severity classification, containment procedures, post-mortem frameworks, and runbook creation.
- Compliance mapping: OWASP ASVS, CIS Benchmarks, NIST CSF, PCI-DSS, HIPAA, and SOC 2 alignment at the application layer.

**This skill does NOT cover:**
- Infrastructure and cloud security hardening (see [senior-devops](../senior-devops/) and [aws-solution-architect](../aws-solution-architect/)).
- Runtime security monitoring, SIEM rule authoring, and SOC operations (see [senior-secops](../senior-secops/)).
- Full regulatory compliance programs, audit evidence collection, and certification processes (see [ra-qm-team](../../ra-qm-team/)).
- Network penetration testing tooling, red team operations, and physical security assessments.

## Integration Points

| Skill | Integration | Data Flow |
|-------|-------------|-----------|
| [senior-devops](../senior-devops/) | CI/CD pipeline security gates | Threat model mitigations feed into pipeline hardening requirements; secret scanner runs as a pre-commit or CI step |
| [senior-secops](../senior-secops/) | Security monitoring and incident response | Threat model outputs define detection rules; incident severity levels align with SecOps alerting tiers |
| [senior-backend](../senior-backend/) | Secure API development | Secure code review checklist applied to backend PRs; authentication pattern selection guides API auth implementation |
| [senior-architect](../senior-architect/) | Security architecture decisions | Defense-in-depth layers and Zero Trust principles inform architecture design reviews; STRIDE results feed architecture risk register |
| [senior-qa](../senior-qa/) | Security testing integration | Vulnerability assessment findings become QA regression test cases; OWASP Top 10 mapping drives security test coverage |
| [ra-qm-team](../../ra-qm-team/) | Compliance framework alignment | Security controls mapped to SOC 2, PCI-DSS, and HIPAA requirements; threat model documentation satisfies audit evidence needs |
