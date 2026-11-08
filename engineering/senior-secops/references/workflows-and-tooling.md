# SecOps Workflows & Tooling Reference

Read this when running a security audit, wiring security into CI/CD, triaging a CVE, handling an incident, or invoking the scanner / assessor / compliance scripts with specific flags.

## Capability Command Reference

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

## Tool Reference (quick)

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
- `1`: Critical or high findings
- `2`: Bad input (target not found)

### vulnerability_assessor.py

| Option | Description |
|--------|-------------|
| `target` | Directory containing dependency files |
| `--severity, -s` | Minimum severity: critical, high, medium, low |
| `--verbose, -v` | Show files as they're scanned |
| `--json` | Output results as JSON |
| `--output, -o` | Write results to file |

**Exit Codes:**
- `0`: No critical/high findings
- `1`: Critical or high findings
- `2`: Bad input (target not found)

### compliance_checker.py

| Option | Description |
|--------|-------------|
| `target` | Directory to check |
| `--framework, -f` | Framework: soc2, pci-dss, hipaa, gdpr, all |
| `--verbose, -v` | Show checks as they run |
| `--json` | Output results as JSON |
| `--output, -o` | Write results to file |

**Exit Codes:**
- `0`: Code-evidence score 70% or higher
- `1`: Score below 70% (NON_COMPLIANT / CRITICAL_GAPS)
- `2`: Bad input (target not found)

## Tool Reference (detailed)

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

**Exit Codes:** `0` = no critical/high findings, `1` = critical or high findings present, `2` = bad input.

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

**Exit Codes:** `0` = no critical/high vulnerabilities, `1` = critical or high vulnerabilities present, `2` = bad input.

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

**Exit Codes:** `0` = code-evidence score 70%+, `1` = below 70%, `2` = bad input.

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
