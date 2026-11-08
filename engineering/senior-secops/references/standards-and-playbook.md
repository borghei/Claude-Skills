# Security Standards, Compliance Tables & Operational Playbook

Read this when applying OWASP Top 10 prevention, working a secure-coding checklist, mapping a control to a framework (SOC 2 / PCI-DSS / HIPAA / GDPR), applying secure-coding code patterns, or diagnosing scanner behavior (anti-patterns, troubleshooting, success criteria).

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

## Anti-Patterns

- **Relying solely on automated scanning** -- SAST tools miss business logic flaws and authorization issues; combine with manual code review for auth-sensitive code
- **Ignoring medium-severity findings** -- exit code 0 on medium findings does not mean safe; parse JSON output for comprehensive CI gating
- **Hardcoding secrets in test fixtures** -- test files with example tokens trigger false positives; use environment variables or mock values even in tests
- **Compliance score as a goal** -- a 90% compliance score with failed encryption controls is worse than 80% with all critical controls passing; prioritize by severity
- **One-time security audits** -- running the scanner once per quarter misses regressions; integrate into every PR via CI/CD
- **Treating warnings as passed** -- compliance checker scores warnings at 0.5 (partial credit); any control below `passed` needs remediation

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| Security scanner reports zero findings on a known-vulnerable project | Test and spec files are excluded by the false-positive filter | Rename the file to remove `test`/`spec` from the path, or review the `_is_false_positive` method |
| Vulnerability assessor misses a CVE for a listed dependency | The package or CVE is not in the built-in `KNOWN_CVES` database | Supplement with an external feed (Snyk, OSV, `npm audit`) and use the assessor for triage prioritization |
| Compliance checker shows `CRITICAL_GAPS` despite controls being present | Pattern-based file search did not match the specific naming convention used in your codebase | Run with `--verbose` to see which checks fail, then verify the matching code patterns or filenames |
| `--json` output is printed to stdout even when `--output` is specified | Both flags are set correctly; this is expected behavior (summary prints to stderr-style console, JSON to file) | Redirect stdout if you need a clean pipe: `python script.py . --json --output report.json > /dev/null` |
| Exit code is 0 despite medium-severity findings | Exit code 1 triggers only on critical or high findings (exit 2 means bad input) | Use `--severity medium` to surface medium findings in the report, and parse the JSON output for CI/CD gating |
| Scanner is slow on large monorepos | All files matching `SCAN_EXTENSIONS` are read in full | Narrow the target to a subdirectory, or exclude heavy vendor directories by placing them in `SKIP_DIRS` |
| Compliance score appears inflated because many controls show `warning` | Warnings score 0.5 (partial credit) in the weighted calculation | Treat any control below `passed` as requiring remediation; filter the JSON output for `status != "passed"` |

## Success Criteria

- **Zero critical CVEs in production** -- all critical-severity vulnerabilities are patched or mitigated before deployment.
- **Mean time to patch under 48 hours** -- critical and high-severity findings are remediated within two business days of detection.
- **Compliance score at or above 90%** -- the compliance checker returns `COMPLIANT` status for every applicable framework before each release.
- **100% of secrets externalized** -- the security scanner reports zero hardcoded secrets (API keys, passwords, private keys) across the entire codebase.
- **CI/CD security gate pass rate above 95%** -- fewer than 5% of pull requests are blocked by security scans, indicating proactive secure coding practices.
- **Incident response time under 15 minutes** -- security incidents are acknowledged and an incident commander assigned within the Phase 1 detection window.
- **Quarterly dependency audit cadence** -- the vulnerability assessor is executed against all ecosystems (npm, Python, Go) at least once per quarter with results documented.
