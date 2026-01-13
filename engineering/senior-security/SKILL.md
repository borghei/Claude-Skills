---
name: senior-security
description: Expert security engineering covering application security, infrastructure security, threat modeling, penetration testing, and compliance.
version: 1.0.0
author: Claude Skills
category: engineering
tags: [security, appsec, pentesting, compliance, devsecops]
---

# Senior Security Engineer

Expert-level security engineering and application security.

## Core Competencies

- Application security (OWASP)
- Infrastructure security
- Threat modeling
- Security code review
- Penetration testing
- Incident response
- Compliance (SOC 2, GDPR, HIPAA)
- Security architecture

## OWASP Top 10

### 1. Broken Access Control

**Vulnerabilities:**
- IDOR (Insecure Direct Object Reference)
- Missing function-level access control
- Privilege escalation

**Prevention:**
```typescript
// Bad: Direct ID access
app.get('/api/users/:id', (req, res) => {
  const user = await db.user.findUnique({ where: { id: req.params.id } });
  res.json(user);
});

// Good: Authorization check
app.get('/api/users/:id', authorize(), (req, res) => {
  if (req.user.role !== 'admin' && req.user.id !== req.params.id) {
    return res.status(403).json({ error: 'Forbidden' });
  }
  const user = await db.user.findUnique({ where: { id: req.params.id } });
  res.json(user);
});
```

### 2. Cryptographic Failures

**Vulnerabilities:**
- Weak encryption
- Exposed secrets
- Missing TLS

**Prevention:**
```typescript
// Password hashing
import bcrypt from 'bcrypt';

const SALT_ROUNDS = 12;

async function hashPassword(password: string): Promise<string> {
  return bcrypt.hash(password, SALT_ROUNDS);
}

async function verifyPassword(password: string, hash: string): Promise<boolean> {
  return bcrypt.compare(password, hash);
}

// Encryption
import { createCipheriv, createDecipheriv, randomBytes } from 'crypto';

function encrypt(text: string, key: Buffer): string {
  const iv = randomBytes(16);
  const cipher = createCipheriv('aes-256-gcm', key, iv);
  const encrypted = Buffer.concat([cipher.update(text, 'utf8'), cipher.final()]);
  const tag = cipher.getAuthTag();
  return Buffer.concat([iv, tag, encrypted]).toString('base64');
}
```

### 3. Injection

**Vulnerabilities:**
- SQL injection
- NoSQL injection
- Command injection
- XSS

**Prevention:**
```typescript
// SQL Injection - Use parameterized queries
// Bad
const query = `SELECT * FROM users WHERE email = '${email}'`;

// Good - Prisma (parameterized by default)
const user = await db.user.findUnique({ where: { email } });

// Good - Raw SQL with parameters
const user = await db.$queryRaw`SELECT * FROM users WHERE email = ${email}`;

// Command Injection
// Bad
exec(`convert ${filename} output.png`);

// Good - Use array form
execFile('convert', [filename, 'output.png']);

// XSS Prevention
// Bad
element.innerHTML = userInput;

// Good - Text content
element.textContent = userInput;

// Good - Sanitization
import DOMPurify from 'dompurify';
element.innerHTML = DOMPurify.sanitize(userInput);
```

### 4. Insecure Design

**Prevention:**
- Threat modeling in design phase
- Security requirements
- Abuse case testing
- Defense in depth

### 5. Security Misconfiguration

**Checklist:**
- [ ] Remove default credentials
- [ ] Disable directory listing
- [ ] Configure security headers
- [ ] Remove stack traces in production
- [ ] Keep dependencies updated

**Security Headers:**
```typescript
import helmet from 'helmet';

app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      scriptSrc: ["'self'"],
      styleSrc: ["'self'", "'unsafe-inline'"],
      imgSrc: ["'self'", "data:", "https:"],
      connectSrc: ["'self'", "https://api.example.com"],
    },
  },
  hsts: {
    maxAge: 31536000,
    includeSubDomains: true,
    preload: true,
  },
  referrerPolicy: { policy: 'strict-origin-when-cross-origin' },
}));
```

## Threat Modeling

### STRIDE Framework

| Threat | Property | Examples |
|--------|----------|----------|
| **S**poofing | Authentication | Session hijacking, credential theft |
| **T**ampering | Integrity | SQL injection, MITM attacks |
| **R**epudiation | Non-repudiation | Missing audit logs |
| **I**nformation Disclosure | Confidentiality | Data breaches, verbose errors |
| **D**enial of Service | Availability | DDoS, resource exhaustion |
| **E**levation of Privilege | Authorization | Privilege escalation |

### Threat Model Template

```markdown
# Threat Model: [System Name]

## System Overview
[Description of system and its components]

## Assets
1. User credentials
2. Payment information
3. Personal data

## Trust Boundaries
1. Internet → Load Balancer
2. Load Balancer → Application
3. Application → Database

## Data Flows
[Diagram of data flows]

## Threats Identified

### Threat 1: SQL Injection
- **Category**: Tampering
- **Asset**: Database
- **Attack Vector**: User input to search functionality
- **Impact**: High (full database access)
- **Likelihood**: Medium
- **Mitigation**: Parameterized queries, input validation

## Risk Assessment Matrix
[High/Medium/Low ratings for each threat]

## Recommended Controls
[Prioritized list of mitigations]
```

## Security Testing

### Automated Scanning

**SAST (Static Analysis):**
```bash
# Semgrep
semgrep --config=p/owasp-top-ten ./src

# npm audit
npm audit --audit-level=high

# Trivy
trivy fs --severity HIGH,CRITICAL .
```

**DAST (Dynamic Analysis):**
```bash
# OWASP ZAP
zap-cli quick-scan --self-contained -t https://target.com

# Nuclei
nuclei -u https://target.com -t cves/
```

### Manual Testing Checklist

**Authentication:**
- [ ] Brute force protection
- [ ] Account lockout
- [ ] Password complexity
- [ ] MFA implementation
- [ ] Session management
- [ ] Password reset flow

**Authorization:**
- [ ] IDOR testing
- [ ] Privilege escalation
- [ ] Function-level access
- [ ] Data-level access

**Input Validation:**
- [ ] SQL injection
- [ ] XSS (stored, reflected, DOM)
- [ ] Command injection
- [ ] Path traversal
- [ ] SSRF

**API Security:**
- [ ] Rate limiting
- [ ] Input validation
- [ ] Authentication
- [ ] Mass assignment
- [ ] Excessive data exposure

## Incident Response

### Response Phases

**1. Preparation:**
- Incident response plan
- Contact lists
- Runbooks
- Tools and access

**2. Identification:**
- Alert triage
- Scope assessment
- Initial classification

**3. Containment:**
- Short-term (isolate)
- Long-term (patch)
- Evidence preservation

**4. Eradication:**
- Root cause removal
- System hardening
- Vulnerability patching

**5. Recovery:**
- System restoration
- Monitoring enhancement
- Verification testing

**6. Lessons Learned:**
- Incident review
- Process improvement
- Documentation update

### Incident Severity

| Severity | Description | Response Time | Examples |
|----------|-------------|---------------|----------|
| Critical | Active breach | Immediate | Data exfiltration, ransomware |
| High | Imminent threat | 1 hour | Unpatched critical CVE |
| Medium | Potential risk | 24 hours | Suspicious activity |
| Low | Minor issue | 72 hours | Failed login attempts |

## Compliance

### SOC 2 Controls

**Security:**
- Access controls
- Encryption
- Vulnerability management
- Incident response

**Availability:**
- System monitoring
- Disaster recovery
- Capacity planning

**Confidentiality:**
- Data classification
- Encryption at rest
- Access logging

### GDPR Requirements

- [ ] Data inventory
- [ ] Legal basis for processing
- [ ] Privacy notices
- [ ] Data subject rights
- [ ] Data protection impact assessment
- [ ] Breach notification procedures
- [ ] Data processing agreements
- [ ] Cross-border transfer mechanisms

## Security Architecture

### Zero Trust Principles

1. **Verify explicitly**: Always authenticate and authorize
2. **Least privilege**: Minimal access required
3. **Assume breach**: Design for compromise containment

### Defense in Depth

```
Layer 1: Perimeter
├── WAF
├── DDoS protection
└── Network firewall

Layer 2: Network
├── Segmentation
├── IDS/IPS
└── Network monitoring

Layer 3: Application
├── Input validation
├── Authentication
└── Authorization

Layer 4: Data
├── Encryption
├── Access controls
└── Backup/recovery

Layer 5: Endpoint
├── EDR
├── Patching
└── Configuration management
```

## Reference Materials

- `references/owasp_testing.md` - OWASP testing guide
- `references/threat_modeling.md` - Threat modeling methodology
- `references/incident_response.md` - IR procedures
- `references/compliance_checklist.md` - Compliance requirements

## Scripts

```bash
# Security scanner
python scripts/security_scan.py --target ./src --type sast

# Dependency audit
python scripts/dep_audit.py --manifest package.json

# Compliance checker
python scripts/compliance_check.py --framework soc2

# Threat model generator
python scripts/threat_model.py --diagram architecture.yaml
```
