# PCI DSS v4.0 Infrastructure Security Guide

Comprehensive guide to infrastructure security for PCI DSS compliance, covering network architecture, cloud deployments, tokenization, key management, POS/terminal security, API security, and mobile payments.

---

## Table of Contents

- [Network Architecture](#network-architecture)
- [Cloud Deployment Models](#cloud-deployment-models)
- [Tokenization vs Encryption](#tokenization-vs-encryption)
- [Key Management Lifecycle](#key-management-lifecycle)
- [POS and Payment Terminal Security](#pos-and-payment-terminal-security)
- [API Security for Payment Systems](#api-security-for-payment-systems)
- [Mobile Payment Security (mPOS)](#mobile-payment-security-mpos)
- [E-commerce Security Controls](#e-commerce-security-controls)
- [Container and Kubernetes Security](#container-and-kubernetes-security)

---

## Network Architecture

### Reference CDE Network Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                        INTERNET                               │
└──────────────────────────┬───────────────────────────────────┘
                           │
                    ┌──────▼──────┐
                    │   Perimeter  │
                    │  Firewall/   │
                    │   WAF/DDoS   │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │     DMZ      │
                    │  (Web/API    │
                    │   Frontend)  │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │  Internal    │
                    │  Firewall    │
                    └──────┬──────┘
                           │
     ┌─────────────────────┼─────────────────────┐
     │                     │                     │
┌────▼────┐         ┌─────▼─────┐         ┌─────▼─────┐
│Corporate│         │    CDE     │         │Management │
│ Network │         │  (Payment  │         │  Network  │
│         │         │  Systems)  │         │ (Admin)   │
│No CHD   │         │ PAN stored │         │ PAM/Jump  │
│access   │         │ processed  │         │ servers   │
└─────────┘         └─────┬─────┘         └───────────┘
                          │
                    ┌─────▼─────┐
                    │ Database   │
                    │ Segment    │
                    │ (Encrypted │
                    │  PAN store)│
                    └───────────┘
```

### Segmentation Requirements

**Effective segmentation requires:**
1. Physical or logical network separation between CDE and non-CDE
2. Firewall or equivalent NSC between all segments
3. Default deny all traffic between segments
4. Explicit allow rules only for business-justified traffic
5. Logging of all cross-segment traffic
6. Annual segmentation testing (6 months for service providers)

### Segmentation Validation Tests

| Test | Purpose | Frequency |
|------|---------|-----------|
| Firewall rule review | Verify only approved traffic crosses CDE boundary | Every 6 months |
| Pen test from non-CDE to CDE | Verify no unauthorized access paths | Annual (6 months SP) |
| Traffic analysis | Confirm no unintended data flows | Quarterly |
| VLAN hopping test | Verify VLAN isolation is effective | Annual |
| ARP spoofing test | Verify Layer 2 controls prevent spoofing | Annual |
| DNS resolution test | Verify CDE DNS is isolated | Annual |

### Network Security Controls Checklist

- [ ] Next-generation firewall at CDE perimeter (stateful inspection, application awareness)
- [ ] WAF in blocking mode for all public-facing payment web applications
- [ ] IDS/IPS at CDE perimeter and critical internal points
- [ ] Network micro-segmentation within CDE for defense in depth
- [ ] Outbound traffic filtering — CDE systems only reach approved destinations
- [ ] DDoS protection for internet-facing payment services
- [ ] Network access control (NAC) — only approved devices connect to CDE
- [ ] Wireless networks fully segmented from CDE (separate SSID, VLAN, firewall)
- [ ] VPN with MFA for remote administrative access to CDE
- [ ] Network monitoring with alerting for anomalous CDE traffic patterns

---

## Cloud Deployment Models

### Shared Responsibility for PCI DSS

| Cloud Model | Customer Responsibility | Cloud Provider Responsibility |
|-------------|------------------------|------------------------------|
| **IaaS** (AWS EC2, Azure VM, GCP Compute) | OS, applications, data, access control, patching, logging | Physical security, hypervisor, network infrastructure |
| **PaaS** (AWS RDS, Azure App Service, GCP Cloud Run) | Application, data, access control, logging configuration | Physical, hypervisor, OS, runtime, patching |
| **SaaS** (Payment processor hosted, Stripe) | Data input, access management, policy | Everything else |

### AWS PCI DSS Architecture

**VPC Design:**
- Create a dedicated VPC for CDE workloads — do not mix with non-payment systems
- Use private subnets for all CDE instances (no public IPs)
- Deploy NAT Gateway for outbound traffic (controlled egress)
- Use VPC Flow Logs for network monitoring

**Key AWS Services for PCI:**
| Service | PCI DSS Requirement | Usage |
|---------|---------------------|-------|
| AWS KMS / CloudHSM | Req 3 (encryption), Req 4 (key management) | Encrypt PAN at rest, manage keys |
| AWS WAF | Req 6 (web app protection) | Protect payment web apps |
| AWS Config | Req 2 (config management) | Monitor configuration compliance |
| Amazon GuardDuty | Req 10 (monitoring), Req 11 (testing) | Threat detection |
| AWS CloudTrail | Req 10 (logging) | API activity logging |
| AWS Security Hub | Req 12 (governance) | Aggregated security findings |
| AWS Secrets Manager | Req 8 (credentials) | Rotate service account passwords |
| Amazon Macie | Req 3 (stored data) | Discover and protect stored PAN |

**IAM Hardening:**
- Use IAM roles (not access keys) for CDE workloads
- Enable MFA for all IAM users with CDE access
- Implement least privilege with permission boundaries
- Use Service Control Policies (SCPs) to restrict CDE account actions
- No root account usage except for account-level operations

### Azure PCI DSS Architecture

**Network Design:**
- Dedicated VNET for CDE with Network Security Groups (NSGs)
- Azure Private Link for PaaS services accessed from CDE
- Azure Firewall Premium with IDPS for CDE traffic

**Key Azure Services:**
| Service | PCI DSS Requirement | Usage |
|---------|---------------------|-------|
| Azure Key Vault (HSM) | Req 3, 4 | Key management, encryption |
| Azure WAF | Req 6 | Web app protection |
| Microsoft Defender for Cloud | Req 11 | Vulnerability management, threat detection |
| Azure Monitor / Sentinel | Req 10 | Logging, SIEM |
| Azure Policy | Req 2 | Configuration compliance |
| Azure AD Conditional Access | Req 7, 8 | Access control, MFA |

### GCP PCI DSS Architecture

**Network Design:**
- Dedicated VPC with Shared VPC for CDE isolation
- VPC Service Controls for API-level isolation
- Private Google Access for GCP service connectivity

**Key GCP Services:**
| Service | PCI DSS Requirement | Usage |
|---------|---------------------|-------|
| Cloud KMS / Cloud HSM | Req 3, 4 | Encryption, key management |
| Cloud Armor | Req 6 | WAF, DDoS protection |
| Security Command Center | Req 11 | Vulnerability and threat detection |
| Cloud Logging / Chronicle | Req 10 | Centralized logging, SIEM |
| Organization Policies | Req 2 | Configuration constraints |
| BeyondCorp Enterprise | Req 7, 8 | Zero trust access |

---

## Tokenization vs Encryption

### Decision Framework

| Factor | Tokenization | Encryption |
|--------|-------------|------------|
| **Scope Impact** | Removes systems from PCI scope | Systems remain in PCI scope |
| **Data Recovery** | Non-reversible (preferred) or vault-based | Reversible with decryption key |
| **Performance** | Token lookup (fast) | Encrypt/decrypt overhead |
| **Key Management** | No keys to manage (non-reversible) | Full key lifecycle required |
| **Best For** | Card-on-file, recurring billing, analytics | Systems requiring PAN recovery |
| **Vendor Examples** | Stripe tokens, Braintree, TokenEx | AES-256, RSA, format-preserving encryption |

### When to Use Tokenization

- **Card-on-file:** Store tokens for recurring charges (subscription services)
- **Analytics:** Use tokens for transaction analytics without exposing PAN
- **Multi-system:** Pass tokens between systems to keep them out of scope
- **Data warehousing:** Store tokens in analytical databases

### When to Use Encryption

- **Payment processing:** When your system must decrypt PAN to process a transaction
- **Issuer processing:** Card issuers must recover full PAN
- **Regulatory requirement:** When a regulation requires access to original PAN
- **Legacy integration:** When systems cannot be modified to accept tokens

### Tokenization Architecture Patterns

**Pattern 1: Processor-Managed Tokenization (Recommended for Merchants)**
```
Customer → Merchant Website → Processor.js (iFrame) → Processor (tokenize) → Token returned
Merchant stores token only — never sees PAN — qualifies for SAQ A
```

**Pattern 2: Third-Party Token Vault**
```
Customer → Merchant POS → Token Service Provider → Token Vault (PAN→Token mapping)
Merchant receives token — Token SP handles PCI scope for vault
```

**Pattern 3: On-Premises Token Vault (Highest scope impact)**
```
Customer → Merchant System → On-Premises Tokenization Engine → Internal Vault
Full PCI scope for vault infrastructure — avoid if possible
```

### Format-Preserving Tokenization

Tokens that maintain the same format as the original PAN (e.g., 16-digit number) for compatibility with legacy systems. Uses algorithms like FF1 (NIST SP 800-38G). Helpful when systems validate card number format but do not process actual PANs.

---

## Key Management Lifecycle

### Key Lifecycle Stages

```
Generation → Distribution → Storage → Usage → Rotation → Revocation → Destruction
```

### Key Management Requirements (PCI DSS 3.6-3.7)

| Stage | Requirement | Implementation |
|-------|------------|----------------|
| **Generation** | Strong keys using approved methods | Use HSM or FIPS 140-2/3 certified generator |
| **Distribution** | Secure distribution, never in clear text | Split knowledge, dual control, encrypted transport |
| **Storage** | Encrypted storage, access controlled | Store in HSM, KMS, or encrypted key store |
| **Usage** | Used only for intended purpose | Enforce key usage policies in HSM/KMS |
| **Rotation** | Rotated at defined intervals | Annual minimum; crypto-period based on key type |
| **Revocation** | Revoked when compromised or expired | Immediate revocation capability, CRL/OCSP |
| **Destruction** | Securely destroyed when no longer needed | Zeroize in HSM, cryptographic erasure |

### Key Management Best Practices

**Split Knowledge:** No single person has access to the complete cryptographic key. Key components are held by different custodians.

**Dual Control:** Two or more persons are required to perform a key management operation. Both must be present to load a key into an HSM.

**Key Custodians:**
- Designate primary and alternate key custodians
- Key custodians must sign acknowledgment of responsibilities
- Key custodian list reviewed and updated at least annually
- Background checks required for key custodians

**HSM (Hardware Security Module):**
- Use FIPS 140-2 Level 3 or FIPS 140-3 certified HSMs
- Deploy HSMs in physically secured, access-controlled locations
- Maintain HSM firmware at current supported version
- Back up HSM keys using secure key ceremony procedures
- Cloud: Use AWS CloudHSM, Azure Dedicated HSM, or GCP Cloud HSM

### DUKPT (Derived Unique Key Per Transaction)

Used primarily in POS environments:
- Base Derivation Key (BDK) generates unique keys for each terminal
- Each transaction uses a different derived key
- Compromise of a single transaction key does not expose other transactions
- Terminal-specific Initial PIN Encryption Key (IPEK) derived from BDK
- After approximately 1 million transactions, terminal must be re-injected with new IPEK

### P2PE Key Management

- P2PE encryption key injected at PCI SSC-listed Key Injection Facility (KIF)
- Key management handled entirely by the P2PE solution provider
- Merchant has no access to encryption keys — scope reduction
- Decryption occurs only at the processor's secure decryption environment
- Key rotation managed by P2PE provider per their key management policy

---

## POS and Payment Terminal Security

### Terminal Physical Security

**Daily Inspections:**
- Examine terminals for signs of tampering (loose housing, additional wiring, overlay devices)
- Compare serial numbers against authorized terminal inventory
- Check for skimming devices over card readers
- Verify tamper-evident seals are intact

**Terminal Management:**
- Maintain inventory of all terminals with serial numbers and locations
- Deploy terminals only from authorized, verified shipments
- Use tamper-evident packaging for terminal transport
- Restrict terminal configuration access to authorized personnel
- Update terminal firmware promptly when security patches are available

### Terminal Network Security

```
POS Terminal → Dedicated POS VLAN → POS Firewall → Payment Processor
                    │
                    └── NO direct Internet access
                    └── NO access to corporate email/web
                    └── NO lateral movement to other VLANs
```

**Requirements:**
- POS terminals on dedicated VLAN/network segment
- Firewall rules permit only traffic to payment processor
- No internet browsing capability on POS systems
- USB ports disabled on POS terminals
- Bluetooth disabled unless required for P2PE peripheral
- Wireless POS uses WPA3 with enterprise authentication on isolated SSID

### Terminal Hardening

- Application allowlisting — only authorized POS software executes
- Remove or disable all unnecessary software and services
- Enable auto-screen-lock with PIN/badge unlock
- Disable local admin access for cashier-level users
- Centralize terminal management for consistent configuration
- Enable secure boot to prevent unauthorized OS loading

---

## API Security for Payment Systems

### Payment API Security Architecture

```
┌──────────┐      ┌──────────┐      ┌──────────────┐      ┌─────────────┐
│  Client   │─TLS→│   API     │─mTLS→│   Payment     │─mTLS→│   Processor  │
│  (Web/    │     │  Gateway  │      │   Service     │      │   (Stripe,   │
│   Mobile) │     │  (WAF,    │      │   (Business   │      │    Adyen)    │
│           │     │   Rate    │      │    Logic)     │      │              │
│           │     │   Limit)  │      │              │      │              │
└──────────┘      └──────────┘      └──────────────┘      └─────────────┘
```

### API Security Controls

| Control | Requirement | Implementation |
|---------|-------------|----------------|
| **Authentication** | Req 8 | OAuth 2.0 / API keys with rotation |
| **Authorization** | Req 7 | RBAC per API endpoint, scoped tokens |
| **Encryption** | Req 4 | TLS 1.2+ for all API traffic, mTLS for internal |
| **Input Validation** | Req 6 | Validate all parameters, reject malformed requests |
| **Rate Limiting** | Req 6 | Prevent brute force and abuse |
| **Logging** | Req 10 | Log all API calls, mask PAN in logs |
| **WAF** | Req 6 | API-aware WAF protecting payment endpoints |
| **Versioning** | Req 6 | Manage API versions, retire insecure versions |

### PAN Handling in APIs

**DO:**
- Use tokenization for API responses (return tokens, not PANs)
- Mask PAN in all API logs (show only first 6/last 4)
- Use mTLS between internal payment services
- Validate PAN format (Luhn check) before processing
- Use JWE (JSON Web Encryption) for PAN in request bodies if PAN must be transmitted

**DO NOT:**
- Include PAN in URL paths or query parameters (logged by web servers)
- Log full PAN in any application or API gateway log
- Return full PAN in API responses
- Cache PAN in API gateway or CDN
- Store PAN in API request/response logs

### API Security Testing

- DAST (Dynamic Application Security Testing) in CI/CD pipeline
- SAST (Static Application Security Testing) for API code
- API-specific penetration testing (OWASP API Security Top 10)
- Fuzz testing for API endpoints handling payment data
- Authentication bypass testing
- Authorization testing (vertical and horizontal privilege escalation)

---

## Mobile Payment Security (mPOS)

### mPOS Architecture

```
┌────────────┐    Bluetooth/    ┌──────────────┐      ┌─────────────┐
│  Card       │───Audio Jack───▶│  Smartphone/  │─TLS─▶│   Payment    │
│  Reader     │   (encrypted)   │  Tablet App   │      │   Processor  │
│  (P2PE/     │                 │  (Merchant    │      │              │
│   EMV)      │                 │   App)        │      │              │
└────────────┘                  └──────────────┘      └─────────────┘
```

### mPOS Security Requirements

**Device Security:**
- Use PCI PTS-approved card readers only
- Deploy P2PE-validated mPOS solutions when available
- Enable full-disk encryption on mobile devices
- Implement MDM (Mobile Device Management) for merchant devices
- Remote wipe capability for lost/stolen devices
- Application-level encryption for payment data in transit

**Application Security:**
- Certificate pinning to prevent MitM attacks
- Jailbreak/root detection — refuse to run on compromised devices
- Code obfuscation and anti-tampering
- Secure local storage (no PAN stored locally)
- Session management with automatic timeout
- Biometric or PIN authentication for app access

**Communication Security:**
- TLS 1.2+ for all communication to payment processor
- Certificate pinning for the payment processor endpoint
- Bluetooth security: Use Bluetooth Low Energy (BLE) with encryption for card reader communication
- Disable fallback to insecure communication protocols

---

## E-commerce Security Controls

### Payment Page Security (Critical for v4.0)

**Requirement 6.4.3 — Script Management:**

All scripts on payment pages must be:
1. **Inventoried** — maintain a list of every script (first-party and third-party)
2. **Authorized** — explicitly approved for use on payment pages
3. **Integrity-verified** — use Subresource Integrity (SRI) hashes or Content Security Policy (CSP)

**Implementation:**
```
Content-Security-Policy:
  default-src 'self';
  script-src 'self' https://js.stripe.com 'sha256-<hash>';
  frame-src https://js.stripe.com;
  connect-src https://api.stripe.com;
  style-src 'self' 'unsafe-inline';
```

**Requirement 11.6.1 — Tamper Detection:**

Deploy mechanisms to detect unauthorized changes to payment pages:
- Real-time JavaScript integrity monitoring
- HTTP header monitoring (CSP violation reports)
- DOM change detection on payment page elements
- External monitoring services that periodically check payment page integrity
- Alert on any unauthorized script changes

### iFrame Integration Best Practices

When using processor-hosted iFrame (SAQ A eligible):
- Load iFrame only from processor's domain (strict CSP)
- No JavaScript that interacts with iFrame contents
- No overlays on top of the iFrame
- Validate iFrame source URL integrity
- Monitor for unauthorized changes to iFrame integration code

### HTTPS/TLS Configuration

| Setting | Required Value | Notes |
|---------|---------------|-------|
| Minimum TLS | 1.2 | Prefer TLS 1.3 |
| Key Exchange | ECDHE | Forward secrecy required |
| Cipher | AES-128-GCM or AES-256-GCM | No CBC mode |
| Certificate | 2048-bit RSA or P-256 ECDSA | Prefer ECDSA for performance |
| HSTS | max-age=31536000; includeSubDomains | Enable on all payment domains |
| OCSP Stapling | Enabled | Improve TLS handshake performance |
| Certificate Transparency | Required | Monitor for unauthorized certificates |

### Bot and Fraud Protection

- Deploy CAPTCHA or invisible challenge on payment pages
- Implement velocity checks (max transactions per card/IP/session)
- Use 3D Secure 2.0 (3DS2) for cardholder authentication
- Device fingerprinting for fraud detection
- Address Verification Service (AVS) and CVV verification
- Geolocation checks for suspicious transaction origins

---

## Container and Kubernetes Security

### CDE Container Security Requirements

| Control | Requirement | Implementation |
|---------|-------------|----------------|
| Image Security | Req 6 (secure development) | Scan images for vulnerabilities; use private registry; sign images |
| Runtime Security | Req 5 (malware), Req 10 (monitoring) | Deploy runtime protection (Falco, Sysdig); log all container events |
| Network Policy | Req 1 (network controls) | Kubernetes NetworkPolicies; deny all default; explicit allow |
| Secrets | Req 8 (authentication) | External vault (HashiCorp, AWS Secrets Manager); never K8s secrets for PAN/keys |
| RBAC | Req 7 (access control) | CDE namespace RBAC; separate service accounts per workload |
| Pod Security | Req 2 (hardening) | Pod Security Standards: Restricted; no root; read-only filesystem |
| Service Mesh | Req 4 (encryption) | Istio/Linkerd with automatic mTLS for pod-to-pod |
| Compliance | Req 2 (configuration) | OPA/Gatekeeper policies enforcing PCI controls |

### Kubernetes CDE Namespace Configuration

```yaml
# Network Policy — deny all ingress/egress by default
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-all
  namespace: cde
spec:
  podSelector: {}
  policyTypes:
    - Ingress
    - Egress
---
# Allow only specific ingress from API gateway
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-api-gateway
  namespace: cde
spec:
  podSelector:
    matchLabels:
      app: payment-service
  policyTypes:
    - Ingress
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              name: api-gateway
      ports:
        - protocol: TCP
          port: 8443
```

### Container Image Pipeline

```
Developer → Code Review → Build → SAST → Image Scan → Sign → Private Registry → Deploy
                                    │         │
                                    │    Reject if critical
                                    │    vulnerabilities found
                                    │
                              Reject if security
                              issues found
```

**Image Security Standards:**
- Base images from trusted sources only (verified publisher)
- Scan with multiple scanners (Trivy, Snyk, Anchore)
- No critical or high vulnerabilities in production images
- Sign images with Cosign or Notary
- Enforce signed image verification at admission (Kyverno, OPA)
- Minimal base images (distroless, Alpine) to reduce attack surface
- No secrets baked into images (use runtime injection)
- Rebuild images at least monthly to pick up base image patches
