---
name: senior-secops
description: >
  Comprehensive SecOps skill for application security, vulnerability management,
  compliance, and secure development practices. Includes security scanning,
  vulnerability assessment, compliance checking, and security automation. Use
  when implementing security controls, conducting security audits, responding to
  vulnerabilities, or ensuring compliance requirements.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: engineering
  domain: security-operations
  updated: 2026-03-31
  tags:
    - security-operations
    - vulnerability-management
    - incident-response
    - siem
---
# Senior SecOps Engineer

Complete toolkit for Security Operations including vulnerability management, compliance verification, secure coding practices, and security automation.

---

## Table of Contents

- [Trigger Terms](#trigger-terms)
- [Core Capabilities](#core-capabilities)
- [Workflows](#workflows)
- [Tool Reference](#tool-reference)
- [Security Standards](#security-standards)
- [Compliance Frameworks](#compliance-frameworks)
- [Best Practices](#best-practices)

---

## Trigger Terms

Use this skill when you encounter:

| Category | Terms |
|----------|-------|
| **Vulnerability Management** | CVE, CVSS, vulnerability scan, security patch, dependency audit, npm audit, pip-audit |
| **OWASP Top 10** | injection, XSS, CSRF, broken authentication, security misconfiguration, sensitive data exposure |
| **Compliance** | SOC 2, PCI-DSS, HIPAA, GDPR, compliance audit, security controls, access control |
| **Secure Coding** | input validation, output encoding, parameterized queries, prepared statements, sanitization |
| **Secrets Management** | API key, secrets vault, environment variables, HashiCorp Vault, AWS Secrets Manager |
| **Authentication** | JWT, OAuth, MFA, 2FA, TOTP, password hashing, bcrypt, argon2, session management |
| **Security Testing** | SAST, DAST, penetration test, security scan, Snyk, Semgrep, CodeQL, Trivy |
| **Incident Response** | security incident, breach notification, incident response, forensics, containment |
| **Network Security** | TLS, HTTPS, HSTS, CSP, CORS, security headers, firewall rules, WAF |
| **Infrastructure Security** | container security, Kubernetes security, IAM, least privilege, zero trust |
| **Cryptography** | encryption at rest, encryption in transit, AES-256, RSA, key management, KMS |
| **Monitoring** | security monitoring, SIEM, audit logging, intrusion detection, anomaly detection |

---

## Core Capabilities

### 1. Security Scanner

Scan source code for security vulnerabilities including hardcoded secrets, SQL injection, XSS, command injection, and path traversal.

```bash
# Scan project for security issues
python scripts/security_scanner.py /path/to/project

# Filter by severity
python scripts/security_scanner.py /path/to/project --severity high

# JSON output for CI/CD
python scripts/security_scanner.py /path/to/project --json --output report.json
```

**Detects:**
- Hardcoded secrets (API keys, passwords, AWS credentials, GitHub tokens, private keys)
- SQL injection patterns (string concatenation, f-strings, template literals)
- XSS vulnerabilities (innerHTML assignment, unsafe DOM manipulation, React unsafe patterns)
- Command injection (shell=True, exec, eval with user input)
- Path traversal (file operations with user input)

### 2. Vulnerability Assessor

Scan dependencies for known CVEs across npm, Python, and Go ecosystems.

```bash
# Assess project dependencies
python scripts/vulnerability_assessor.py /path/to/project

# Critical/high only
python scripts/vulnerability_assessor.py /path/to/project --severity high

# Export vulnerability report
python scripts/vulnerability_assessor.py /path/to/project --json --output vulns.json
```

**Scans:**
- `package.json` and `package-lock.json` (npm)
- `requirements.txt` and `pyproject.toml` (Python)
- `go.mod` (Go)

**Output:**
- CVE IDs with CVSS scores
- Affected package versions
- Fixed versions for remediation
- Overall risk score (0-100)

### 3. Compliance Checker

Verify security compliance against SOC 2, PCI-DSS, HIPAA, and GDPR frameworks.

```bash
# Check all frameworks
python scripts/compliance_checker.py /path/to/project

# Specific framework
python scripts/compliance_checker.py /path/to/project --framework soc2
python scripts/compliance_checker.py /path/to/project --framework pci-dss
python scripts/compliance_checker.py /path/to/project --framework hipaa
python scripts/compliance_checker.py /path/to/project --framework gdpr

# Export compliance report
python scripts/compliance_checker.py /path/to/project --json --output compliance.json
```

**Verifies:**
- Access control implementation
- Encryption at rest and in transit
- Audit logging
- Authentication strength (MFA, password hashing)
- Security documentation
- CI/CD security controls

---

## Workflows

### Workflow 1: Security Audit

Complete security assessment of a codebase.

```bash
# Step 1: Scan for code vulnerabilities
python scripts/security_scanner.py . --severity medium

# Step 2: Check dependency vulnerabilities
python scripts/vulnerability_assessor.py . --severity high

# Step 3: Verify compliance controls
python scripts/compliance_checker.py . --framework all

# Step 4: Generate combined report
python scripts/security_scanner.py . --json --output security.json
python scripts/vulnerability_assessor.py . --json --output vulns.json
python scripts/compliance_checker.py . --json --output compliance.json
```

### Workflow 2: CI/CD Security Gate

Integrate security checks into deployment pipeline.

```yaml
# .github/workflows/security.yml
name: Security Scan

on:
  pull_request:
    branches: [main, develop]

jobs:
  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Security Scanner
        run: python scripts/security_scanner.py . --severity high

      - name: Vulnerability Assessment
        run: python scripts/vulnerability_assessor.py . --severity critical

      - name: Compliance Check
        run: python scripts/compliance_checker.py . --framework soc2
```

### Workflow 3: CVE Triage

Respond to a new CVE affecting your application.

```
1. ASSESS (0-2 hours)
   - Identify affected systems using vulnerability_assessor.py
   - Check if CVE is being actively exploited
   - Determine CVSS environmental score for your context

2. PRIORITIZE
   - Critical (CVSS 9.0+, internet-facing): 24 hours
   - High (CVSS 7.0-8.9): 7 days
   - Medium (CVSS 4.0-6.9): 30 days
   - Low (CVSS < 4.0): 90 days

3. REMEDIATE
   - Update affected dependency to fixed version
   - Run security_scanner.py to verify fix
   - Test for regressions
   - Deploy with enhanced monitoring

4. VERIFY
   - Re-run vulnerability_assessor.py
   - Confirm CVE no longer reported
   - Document remediation actions
```

### Workflow 4: Incident Response

Security incident handling procedure.

```
PHASE 1: DETECT & IDENTIFY (0-15 min)
- Alert received and acknowledged
- Initial severity assessment (SEV-1 to SEV-4)
- Incident commander assigned
- Communication channel established

PHASE 2: CONTAIN (15-60 min)
- Affected systems identified
- Network isolation if needed
- Credentials rotated if compromised
- Preserve evidence (logs, memory dumps)

PHASE 3: ERADICATE (1-4 hours)
- Root cause identified
- Malware/backdoors removed
- Vulnerabilities patched (run security_scanner.py)
- Systems hardened

PHASE 4: RECOVER (4-24 hours)
- Systems restored from clean backup
- Services brought back online
- Enhanced monitoring enabled
- User access restored

PHASE 5: POST-INCIDENT (24-72 hours)
- Incident timeline documented
- Root cause analysis complete
- Lessons learned documented
- Preventive measures implemented
- Stakeholder report delivered
```

---

## Tool Reference

### security_scanner.py

| Option | Description |
|--------|-------------|
| `target` | Directory or file to scan |
| `--severity, -s` | Minimum severity: critical, high, medium, low |
| `--verbose, -v` | Show files as they're scanned |
| `--json` | Output results as JSON |
| `--output, -o` | Write results to file |

**Exit Codes:**
- `0`: No critical/high findings
- `1`: High severity findings
- `2`: Critical severity findings

### vulnerability_assessor.py

| Option | Description |
|--------|-------------|
| `target` | Directory containing dependency files |
| `--severity, -s` | Minimum severity: critical, high, medium, low |
| `--verbose, -v` | Show files as they're scanned |
| `--json` | Output results as JSON |
| `--output, -o` | Write results to file |

**Exit Codes:**
- `0`: No critical/high vulnerabilities
- `1`: High severity vulnerabilities
- `2`: Critical severity vulnerabilities

### compliance_checker.py

| Option | Description |
|--------|-------------|
| `target` | Directory to check |
| `--framework, -f` | Framework: soc2, pci-dss, hipaa, gdpr, all |
| `--verbose, -v` | Show checks as they run |
| `--json` | Output results as JSON |
| `--output, -o` | Write results to file |

**Exit Codes:**
- `0`: Compliant (90%+ score)
- `1`: Non-compliant (50-69% score)
- `2`: Critical gaps (<50% score)

---

## Security Standards

### OWASP Top 10 Prevention

| Vulnerability | Prevention |
|--------------|------------|
| **A01: Broken Access Control** | Implement RBAC, deny by default, validate permissions server-side |
| **A02: Cryptographic Failures** | Use TLS 1.2+, AES-256 encryption, secure key management |
| **A03: Injection** | Parameterized queries, input validation, escape output |
| **A04: Insecure Design** | Threat modeling, secure design patterns, defense in depth |
| **A05: Security Misconfiguration** | Hardening guides, remove defaults, disable unused features |
| **A06: Vulnerable Components** | Dependency scanning, automated updates, SBOM |
| **A07: Authentication Failures** | MFA, rate limiting, secure password storage |
| **A08: Data Integrity Failures** | Code signing, integrity checks, secure CI/CD |
| **A09: Security Logging Failures** | Comprehensive audit logs, SIEM integration, alerting |
| **A10: SSRF** | URL validation, allowlist destinations, network segmentation |

### Secure Coding Checklist

```markdown
## Input Validation
- [ ] Validate all input on server side
- [ ] Use allowlists over denylists
- [ ] Sanitize for specific context (HTML, SQL, shell)

## Output Encoding
- [ ] HTML encode for browser output
- [ ] URL encode for URLs
- [ ] JavaScript encode for script contexts

## Authentication
- [ ] Use bcrypt/argon2 for passwords
- [ ] Implement MFA for sensitive operations
- [ ] Enforce strong password policy

## Session Management
- [ ] Generate secure random session IDs
- [ ] Set HttpOnly, Secure, SameSite flags
- [ ] Implement session timeout (15 min idle)

## Error Handling
- [ ] Log errors with context (no secrets)
- [ ] Return generic messages to users
- [ ] Never expose stack traces in production

## Secrets Management
- [ ] Use environment variables or secrets manager
- [ ] Never commit secrets to version control
- [ ] Rotate credentials regularly
```

---

## Compliance Frameworks

### SOC 2 Type II Controls

| Control | Category | Description |
|---------|----------|-------------|
| CC1 | Control Environment | Security policies, org structure |
| CC2 | Communication | Security awareness, documentation |
| CC3 | Risk Assessment | Vulnerability scanning, threat modeling |
| CC6 | Logical Access | Authentication, authorization, MFA |
| CC7 | System Operations | Monitoring, logging, incident response |
| CC8 | Change Management | CI/CD, code review, deployment controls |

### PCI-DSS v4.0 Requirements

| Requirement | Description |
|-------------|-------------|
| Req 3 | Protect stored cardholder data (encryption at rest) |
| Req 4 | Encrypt transmission (TLS 1.2+) |
| Req 6 | Secure development (input validation, secure coding) |
| Req 8 | Strong authentication (MFA, password policy) |
| Req 10 | Audit logging (all access to cardholder data) |
| Req 11 | Security testing (SAST, DAST, penetration testing) |

### HIPAA Security Rule

| Safeguard | Requirement |
|-----------|-------------|
| 164.312(a)(1) | Unique user identification for PHI access |
| 164.312(b) | Audit trails for PHI access |
| 164.312(c)(1) | Data integrity controls |
| 164.312(d) | Person/entity authentication (MFA) |
| 164.312(e)(1) | Transmission encryption (TLS) |

### GDPR Requirements

| Article | Requirement |
|---------|-------------|
| Art 25 | Privacy by design, data minimization |
| Art 32 | Security measures, encryption, pseudonymization |
| Art 33 | Breach notification (72 hours) |
| Art 17 | Right to erasure (data deletion) |
| Art 20 | Data portability (export capability) |

---

## Best Practices

### Secrets Management

```python
# BAD: Hardcoded secret
API_KEY = "sk-1234567890abcdef"

# GOOD: Environment variable
import os
API_KEY = os.environ.get("API_KEY")

# BETTER: Secrets manager
from your_vault_client import get_secret
API_KEY = get_secret("api/key")
```

### SQL Injection Prevention

```python
# BAD: String concatenation
query = f"SELECT * FROM users WHERE id = {user_id}"

# GOOD: Parameterized query
cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
```

### XSS Prevention

```javascript
// BAD: Direct innerHTML assignment is vulnerable
// GOOD: Use textContent (auto-escaped)
element.textContent = userInput;

// GOOD: Use sanitization library for HTML
import DOMPurify from 'dompurify';
const safeHTML = DOMPurify.sanitize(userInput);
```

### Authentication

```javascript
// Password hashing
const bcrypt = require('bcrypt');
const SALT_ROUNDS = 12;

// Hash password
const hash = await bcrypt.hash(password, SALT_ROUNDS);

// Verify password
const match = await bcrypt.compare(password, hash);
```

### Security Headers

```javascript
// Express.js security headers
const helmet = require('helmet');
app.use(helmet());

// Or manually set headers:
app.use((req, res, next) => {
  res.setHeader('X-Content-Type-Options', 'nosniff');
  res.setHeader('X-Frame-Options', 'DENY');
  res.setHeader('X-XSS-Protection', '1; mode=block');
  res.setHeader('Strict-Transport-Security', 'max-age=31536000; includeSubDomains');
  res.setHeader('Content-Security-Policy', "default-src 'self'");
  next();
});
```

---

## Reference Documentation

| Document | Description |
|----------|-------------|
| `references/security_standards.md` | OWASP Top 10, secure coding, authentication, API security |
| `references/vulnerability_management_guide.md` | CVE triage, CVSS scoring, remediation workflows |
| `references/compliance_requirements.md` | SOC 2, PCI-DSS, HIPAA, GDPR requirements |

---

## Tech Stack

**Security Scanning:**
- Snyk (dependency scanning)
- Semgrep (SAST)
- CodeQL (code analysis)
- Trivy (container scanning)
- OWASP ZAP (DAST)

**Secrets Management:**
- HashiCorp Vault
- AWS Secrets Manager
- Azure Key Vault
- 1Password Secrets Automation

**Authentication:**
- bcrypt, argon2 (password hashing)
- jsonwebtoken (JWT)
- passport.js (authentication middleware)
- speakeasy (TOTP/MFA)

**Logging & Monitoring:**
- Winston, Pino (Node.js logging)
- Datadog, Splunk (SIEM)
- PagerDuty (alerting)

**Compliance:**
- Vanta (SOC 2 automation)
- Drata (compliance management)
- AWS Config (configuration compliance)

---

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| Security scanner reports zero findings on a known-vulnerable project | Test and spec files are excluded by the false-positive filter | Rename the file to remove `test`/`spec` from the path, or review the `_is_false_positive` method |
| Vulnerability assessor misses a CVE for a listed dependency | The package or CVE is not in the built-in `KNOWN_CVES` database | Supplement with an external feed (Snyk, OSV, `npm audit`) and use the assessor for triage prioritization |
| Compliance checker shows `CRITICAL_GAPS` despite controls being present | Pattern-based file search did not match the specific naming convention used in your codebase | Run with `--verbose` to see which checks fail, then verify the matching code patterns or filenames |
| `--json` output is printed to stdout even when `--output` is specified | Both flags are set correctly; this is expected behavior (summary prints to stderr-style console, JSON to file) | Redirect stdout if you need a clean pipe: `python script.py . --json --output report.json > /dev/null` |
| Exit code is 0 despite medium-severity findings | Exit codes only trigger on critical (exit 2) or high (exit 1) severity findings | Use `--severity medium` to surface medium findings in the report, and parse the JSON output for CI/CD gating |
| Scanner is slow on large monorepos | All files matching `SCAN_EXTENSIONS` are read in full | Narrow the target to a subdirectory, or exclude heavy vendor directories by placing them in `SKIP_DIRS` |
| Compliance score appears inflated because many controls show `warning` | Warnings score 0.5 (partial credit) in the weighted calculation | Treat any control below `passed` as requiring remediation; filter the JSON output for `status != "passed"` |

---

## Success Criteria

- **Zero critical CVEs in production** -- all critical-severity vulnerabilities are patched or mitigated before deployment.
- **Mean time to patch under 48 hours** -- critical and high-severity findings are remediated within two business days of detection.
- **Compliance score at or above 90%** -- the compliance checker returns `COMPLIANT` status for every applicable framework before each release.
- **100% of secrets externalized** -- the security scanner reports zero hardcoded secrets (API keys, passwords, private keys) across the entire codebase.
- **CI/CD security gate pass rate above 95%** -- fewer than 5% of pull requests are blocked by security scans, indicating proactive secure coding practices.
- **Incident response time under 15 minutes** -- security incidents are acknowledged and an incident commander assigned within the Phase 1 detection window.
- **Quarterly dependency audit cadence** -- the vulnerability assessor is executed against all ecosystems (npm, Python, Go) at least once per quarter with results documented.

---

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

---

## Integration Points

| Skill | Integration | Data Flow |
|-------|-------------|-----------|
| `senior-devops` | Infrastructure hardening and CI/CD pipeline configuration | Security scan results feed into deployment gates; DevOps provides container and IaC scanning |
| `senior-backend` | Secure coding patterns and input validation in server-side code | SecOps scanner findings drive backend remediation; backend applies parameterized queries and output encoding |
| `senior-qa` | Security test cases and regression verification after patches | Vulnerability reports generate QA test cases; QA confirms fixes do not introduce regressions |
| `senior-architect` | Threat modeling, defense-in-depth design, and zero-trust architecture | Compliance gaps inform architecture decisions; architect provides security design patterns |
| `code-reviewer` | Security-focused code review and pre-merge analysis | Scanner findings prioritize review focus areas; reviewer enforces secure coding standards |
| `senior-fullstack` | End-to-end security across frontend and API layers (XSS, CSRF, auth) | SecOps identifies frontend and API vulnerabilities; fullstack applies framework-level mitigations |

---

## Tool Reference

### security_scanner.py

**Purpose:** Scan source code for security vulnerabilities including hardcoded secrets, SQL injection, XSS, command injection, and path traversal patterns.

**Usage:**

```bash
python scripts/security_scanner.py <target> [options]
```

**Flags:**

| Flag | Short | Type | Default | Description |
|------|-------|------|---------|-------------|
| `target` | -- | positional | *(required)* | Directory or file to scan |
| `--severity` | `-s` | choice | `low` | Minimum severity to report: `critical`, `high`, `medium`, `low`, `info` |
| `--verbose` | `-v` | flag | off | Print each file path as it is scanned |
| `--json` | -- | flag | off | Output results as JSON (to stdout or combined with `--output`) |
| `--output` | `-o` | string | -- | Write results to the specified file path |

**Example:**

```bash
# Scan current directory for high and critical findings, export JSON
python scripts/security_scanner.py . --severity high --json --output security-report.json
```

**Output Formats:**

- **Human-readable (default):** Prints a summary table with severity counts and the top 5 findings including file path, line number, and description.
- **JSON (`--json`):** Full structured report with `status`, `files_scanned`, `scan_duration_seconds`, `total_findings`, `severity_counts`, and a `findings` array. Each finding includes `rule_id`, `severity`, `category`, `title`, `description`, `file_path`, `line_number`, `code_snippet`, and `recommendation`.

**Exit Codes:** `0` = no critical/high findings, `1` = high-severity findings present, `2` = critical-severity findings present.

---

### vulnerability_assessor.py

**Purpose:** Scan project dependency manifests (package.json, requirements.txt, pyproject.toml, package-lock.json, go.mod) for known CVEs and calculate an overall risk score.

**Usage:**

```bash
python scripts/vulnerability_assessor.py <target> [options]
```

**Flags:**

| Flag | Short | Type | Default | Description |
|------|-------|------|---------|-------------|
| `target` | -- | positional | *(required)* | Directory containing dependency files |
| `--severity` | `-s` | choice | `low` | Minimum severity to report: `critical`, `high`, `medium`, `low` |
| `--verbose` | `-v` | flag | off | Print each dependency file path as it is scanned |
| `--json` | -- | flag | off | Output results as JSON (to stdout or combined with `--output`) |
| `--output` | `-o` | string | -- | Write results to the specified file path |

**Example:**

```bash
# Assess dependencies, show only critical vulnerabilities
python scripts/vulnerability_assessor.py /path/to/project --severity critical --verbose
```

**Output Formats:**

- **Human-readable (default):** Prints a summary with files scanned, packages scanned, risk score (0-100), risk level (NONE/LOW/MEDIUM/HIGH/CRITICAL), severity counts, and the top 5 vulnerabilities sorted by CVSS score.
- **JSON (`--json`):** Full structured report with `status`, `target`, `files_scanned`, `packages_scanned`, `scan_duration_seconds`, `total_vulnerabilities`, `risk_score`, `risk_level`, `severity_counts`, and a `vulnerabilities` array. Each vulnerability includes `cve_id`, `package`, `installed_version`, `fixed_version`, `severity`, `cvss_score`, `description`, `ecosystem`, and `recommendation`.

**Exit Codes:** `0` = no critical/high vulnerabilities, `1` = high-severity vulnerabilities present, `2` = critical-severity vulnerabilities present.

---

### compliance_checker.py

**Purpose:** Verify security compliance against SOC 2 Type II, PCI-DSS v4.0, HIPAA Security Rule, and GDPR by scanning project files for evidence of required controls.

**Usage:**

```bash
python scripts/compliance_checker.py <target> [options]
```

**Flags:**

| Flag | Short | Type | Default | Description |
|------|-------|------|---------|-------------|
| `target` | -- | positional | *(required)* | Directory to check for compliance |
| `--framework` | `-f` | choice | `all` | Compliance framework: `soc2`, `pci-dss`, `hipaa`, `gdpr`, `all` |
| `--verbose` | `-v` | flag | off | Print each framework check as it runs |
| `--json` | -- | flag | off | Output results as JSON (to stdout or combined with `--output`) |
| `--output` | `-o` | string | -- | Write results to the specified file path |

**Example:**

```bash
# Check SOC 2 compliance and export report
python scripts/compliance_checker.py . --framework soc2 --json --output soc2-report.json
```

**Output Formats:**

- **Human-readable (default):** Prints compliance score as a percentage with level (COMPLIANT/PARTIALLY_COMPLIANT/NON_COMPLIANT/CRITICAL_GAPS), a passed/failed/warning/N/A breakdown, and the top 5 failed controls with severity and remediation recommendations.
- **JSON (`--json`):** Full structured report with `status`, `target`, `framework`, `scan_duration_seconds`, `compliance_score`, `compliance_level`, `summary` (passed/failed/warnings/not_applicable/total), and a `controls` array. Each control includes `control_id`, `framework`, `category`, `title`, `description`, `status`, `evidence`, `recommendation`, and `severity`.

**Exit Codes:** `0` = compliant (90%+ score), `1` = non-compliant (50-69% score), `2` = critical gaps (<50% score).
