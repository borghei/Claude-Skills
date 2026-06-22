---
name: skill-security-auditor
description: >
  Security audit and vulnerability scanning for AI agent skills before install. Detects prompt
  injection, dangerous code, exfiltration, credential harvesting, and supply chain risks. Use
  when evaluating untrusted skills or gating installs.
license: MIT + Commons Clause
metadata:
  version: 1.1.0
  author: borghei
  category: engineering
  domain: ai-security
  tier: POWERFUL
  updated: 2026-06-17
  frameworks: static-analysis, supply-chain-security
---
# Skill Security Auditor

Scan and audit AI agent skills for security risks before installation. Performs static analysis on code files for dangerous patterns, scans markdown files for prompt injection, validates dependency supply chains, checks file system boundaries, and detects obfuscation. Produces a structured PASS / WARN / FAIL verdict with findings categorized by severity and actionable remediation guidance.

**Keywords:** skill security, AI security, prompt injection, code audit, supply chain, dependency scanning, data exfiltration, credential harvesting, obfuscation detection, pre-install security

## Core Capabilities

- **Code execution risk detection** — command injection (`os.system`, `subprocess shell=True`, backticks), `eval`/`exec`/`compile`, obfuscation (base64/hex/`chr()`), network exfiltration, credential harvesting (`~/.ssh`, `~/.aws`), privilege escalation.
- **Prompt injection detection** — system-prompt overrides, role hijacking, safety bypass, hidden zero-width/HTML-comment instructions, data-extraction directives, excessive-permission requests.
- **Supply chain analysis** — known-vulnerable pins, typosquatting, unpinned versions, inline `pip`/`npm install`, low-reputation packages.
- **File system & structure validation** — out-of-scope paths, hidden/credential files, unexpected binaries, escaping symlinks, oversized payloads.
- **Verdict & reporting** — PASS / WARN / FAIL with severity-categorized findings, remediation, and a strict mode for CI gates.

## When to Use

- Evaluating a skill from an untrusted source before installation
- Pre-install security gate for CI/CD pipelines
- Auditing a skill directory or git repository for malicious code
- Reviewing skills before adding them to a team's approved list
- Post-incident scanning of installed skills

## Clarify First

Before the audit, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Target path** — the skill file or directory to scan (the subject of every scanner)
- [ ] **Scan dimensions** — code execution / prompt injection / supply chain (selects which of the three scanners run)
- [ ] **Strict mode / gate threshold** — whether any HIGH finding forces FAIL (CI gate vs advisory report changes the verdict)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Tools

| Tool | Purpose | Command |
|------|---------|---------|
| `code_scanner.py` | Scan Python scripts for eval/exec, subprocess, network exfiltration, credential harvesting, obfuscation, unsafe imports | `python scripts/code_scanner.py <target> --strict --json` |
| `prompt_injection_scanner.py` | Scan markdown/text for prompt-injection patterns and hidden directives | `python scripts/prompt_injection_scanner.py <target> --strict --json` |
| `supply_chain_checker.py` | Check imports/requirements for typosquatting, unpinned versions, inline installs | `python scripts/supply_chain_checker.py <target> --strict --json` |

All tools take a `target` (file or directory), and support `--strict` (any HIGH → FAIL) and `--json`.

## References

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/threat-model-and-patterns.md](references/threat-model-and-patterns.md)** — the attack-vector threat model, trust boundaries, full regex pattern sets for code-execution and prompt-injection detection, and known evasion techniques. Read when deciding what to scan for or tuning detection.
- **[references/audit-output-and-workflow.md](references/audit-output-and-workflow.md)** — the report format, verdict criteria (incl. strict mode), CI/CD integration YAML, and the manual audit checklist. Read when producing or interpreting an audit.
- **[references/quality-and-best-practices.md](references/quality-and-best-practices.md)** — static-analysis limitations, common pitfalls, best practices, troubleshooting matrix, and success criteria. Read before shipping or relying on an audit.

## Scope & Limitations

**This skill covers:**
- Static pattern-based detection of dangerous code constructs in Python, Bash, JavaScript, and TypeScript files
- Prompt injection scanning across all markdown files within a skill package
- Dependency supply chain validation for `requirements.txt` and `package.json`
- File structure boundary checks including symlinks, binaries, hidden files, and oversized payloads

**This skill does NOT cover:**
- Runtime or dynamic analysis — code is never executed during the audit (see `skill-tester` for runtime validation)
- Live CVE database lookups or real-time vulnerability feeds (see `dependency-auditor` for active CVE scanning)
- Infrastructure-level security controls such as network segmentation, container hardening, or cloud IAM policies (see `infrastructure-compliance-auditor` in ra-qm-team)
- Compliance framework certification against ISO 27001, SOC 2, GDPR, or other regulatory standards (see `information-security-manager-iso27001` and `gdpr-dsgvo-expert` in ra-qm-team)

## Integration Points

| Skill | Integration | Data Flow |
|-------|-------------|-----------|
| `dependency-auditor` | Feed audit findings into live CVE scanning for flagged dependencies | Security audit report → dependency-auditor for real-time vulnerability lookup |
| `ci-cd-pipeline-builder` | Embed the audit workflow as a required check in generated CI/CD pipelines | Pipeline template ← audit job YAML from this skill's CI/CD section |
| `skill-tester` | Run dynamic runtime tests on skills that pass static analysis | PASS verdict from this skill → skill-tester for behavioral validation |
| `infrastructure-compliance-auditor` | Extend auditing scope from skill-level to infrastructure-level security controls | Skill audit findings → infrastructure auditor for environment-wide posture review |
| `env-secrets-manager` | Cross-reference credential harvesting findings with secrets management policy | Credential-access flags from audit → env-secrets-manager for policy verification |
| `pr-review-expert` | Surface audit findings as inline PR review comments on flagged lines | Audit report line references → PR review annotations for developer visibility |
