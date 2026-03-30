---
name: pci-dss-specialist
description: >
  PCI DSS v4.0 payment card industry data security standard compliance,
  assessment, and implementation. Use for PCI DSS, payment card security,
  cardholder data, PCI compliance, payment security, PCI assessment, SAQ, ROC,
  QSA, credit card security, payment processing security, PCI scoping,
  tokenization, payment terminal security, CDE security, and merchant
  compliance.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: compliance
  domain: payment-security
  updated: 2026-03-31
  tags: [pci-dss, payment-security, tokenization, cardholder-data]
---
# PCI-DSS v4.0 Specialist

Implement, assess, and maintain compliance with the Payment Card Industry Data Security Standard version 4.0 — the global standard for protecting cardholder data in payment processing environments.

---

## Table of Contents

- [Trigger Phrases](#trigger-phrases)
- [Quick Start](#quick-start)
- [Tools](#tools)
- [PCI DSS v4.0 Overview](#pci-dss-v40-overview)
- [12 Requirements Deep-Dive](#12-requirements-deep-dive)
- [v4.0 Changes from v3.2.1](#v40-changes-from-v321)
- [CDE Scoping](#cardholder-data-environment-scoping)
- [SAQ Types and Selection Guide](#saq-types-and-selection-guide)
- [Assessment Types](#assessment-types)
- [Merchant and Service Provider Levels](#merchant-and-service-provider-levels)
- [Infrastructure Controls](#infrastructure-controls)
- [PCI DSS Compliance Roadmap](#pci-dss-compliance-roadmap)
- [Reference Guides](#reference-guides)
- [Validation Checkpoints](#validation-checkpoints)

---

## Trigger Phrases

Use this skill when you hear:
- "PCI DSS"
- "payment card security"
- "cardholder data"
- "PCI compliance"
- "payment security"
- "PCI assessment"
- "SAQ"
- "ROC"
- "QSA"
- "credit card security"
- "payment processing security"
- "tokenization"
- "CDE scoping"
- "merchant level compliance"

---

## Quick Start

### Check PCI Compliance Status

```bash
python scripts/pci_compliance_checker.py --input controls.json --output compliance_report.json
```

### Determine SAQ Type

```bash
python scripts/pci_scope_analyzer.py --input business_model.json --output scope_report.json
```

### Generate Compliance Gap Report (Markdown)

```bash
python scripts/pci_compliance_checker.py --input controls.json --format markdown --output gap_report.md
```

### Analyze CDE Scope

```bash
python scripts/pci_scope_analyzer.py --input business_model.json --format markdown --output scope_analysis.md
```

---

## Tools

### pci_compliance_checker.py

Comprehensive PCI DSS v4.0 compliance assessment engine.

**Capabilities:**
- Checks against all 12 PCI DSS requirements
- Validates cardholder data environment scope
- Assesses technical controls (encryption, access, logging)
- Scores compliance per requirement (0-100)
- Identifies gaps with remediation priorities
- Generates JSON or Markdown output

**Usage:**

```bash
# Full compliance check
python scripts/pci_compliance_checker.py \
  --input controls.json \
  --output report.json

# Markdown report for stakeholders
python scripts/pci_compliance_checker.py \
  --input controls.json \
  --format markdown \
  --output compliance_report.md

# Check specific requirements only
python scripts/pci_compliance_checker.py \
  --input controls.json \
  --requirements 3,4,7,8 \
  --output data_security_report.json
```

**Input Format (controls.json):**

```json
{
  "organization": "Acme Payments",
  "assessment_date": "2026-03-09",
  "merchant_level": 2,
  "requirements": {
    "1": {
      "network_segmentation": true,
      "firewall_rules_documented": true,
      "waf_deployed": true,
      "inbound_traffic_restricted": true,
      "outbound_traffic_restricted": false,
      "wireless_networks_segmented": true,
      "notes": "Outbound filtering planned for Q2"
    },
    "3": {
      "pan_storage_minimized": true,
      "pan_masked_when_displayed": true,
      "pan_encrypted_at_rest": true,
      "encryption_algorithm": "AES-256",
      "key_management_procedures": true,
      "tokenization_implemented": true,
      "sad_not_stored_after_auth": true,
      "notes": "Tokenization covers 95% of stored PANs"
    }
  }
}
```

### pci_scope_analyzer.py

CDE scoping and SAQ type determination engine.

**Capabilities:**
- Determines appropriate SAQ type based on business model
- Maps cardholder data environment boundaries
- Identifies connected systems and security-impacting systems
- Generates scoping worksheet with system classifications
- Recommends scope reduction strategies

**Usage:**

```bash
# Determine SAQ type and CDE scope
python scripts/pci_scope_analyzer.py \
  --input business_model.json \
  --output scope_report.json

# Markdown scoping worksheet
python scripts/pci_scope_analyzer.py \
  --input business_model.json \
  --format markdown \
  --output scoping_worksheet.md
```

**Input Format (business_model.json):**

```json
{
  "organization": "Acme Payments",
  "business_type": "e-commerce",
  "payment_channels": ["web", "mobile_app"],
  "card_present": false,
  "card_not_present": true,
  "stores_pan": false,
  "processes_pan": false,
  "transmits_pan": false,
  "payment_processor": "Stripe",
  "uses_iframe_redirect": true,
  "uses_p2pe": false,
  "annual_transactions": 500000,
  "card_brands": ["visa", "mastercard", "amex"],
  "systems": [
    {
      "name": "web-frontend",
      "type": "web_server",
      "handles_cardholder_data": false,
      "connected_to_cde": false,
      "security_impacting": true,
      "description": "Customer-facing e-commerce site with iframe payment"
    },
    {
      "name": "payment-api",
      "type": "application_server",
      "handles_cardholder_data": false,
      "connected_to_cde": true,
      "security_impacting": true,
      "description": "API server that communicates with Stripe"
    }
  ]
}
```

---

## PCI DSS v4.0 Overview

### What Is PCI DSS?

The Payment Card Industry Data Security Standard (PCI DSS) is a global security standard developed by the PCI Security Standards Council (PCI SSC), founded by American Express, Discover, JCB, Mastercard, and Visa. It applies to all entities that store, process, or transmit cardholder data (CHD) or sensitive authentication data (SAD).

### PCI DSS v4.0 Timeline

| Date | Milestone |
|------|-----------|
| March 2022 | PCI DSS v4.0 published |
| March 2024 | v3.2.1 retired; v4.0 is the only active version |
| March 31, 2025 | All future-dated requirements become mandatory |

**All organizations must now comply with the full PCI DSS v4.0 standard, including all previously future-dated requirements.**

### What Data Is Protected

**Cardholder Data (CHD):**
- Primary Account Number (PAN) — the credit/debit card number
- Cardholder Name (when stored with PAN)
- Service Code
- Expiration Date

**Sensitive Authentication Data (SAD):** Must NEVER be stored after authorization, even if encrypted.
- Full track data (magnetic stripe, chip)
- CVV/CVC/CAV2/CID (card verification codes)
- PIN and PIN block

---

## 12 Requirements Deep-Dive

### Requirement 1: Install and Maintain Network Security Controls

**Objective:** Protect the cardholder data environment through network security controls.

**Key Sub-Requirements:**
- **1.2.1** — Network security controls (NSCs) are configured and maintained
- **1.2.5** — All services, protocols, and ports allowed are identified and approved
- **1.2.8** — NSC configuration files are secured and synchronized
- **1.3.1** — Inbound traffic to the CDE is restricted to only necessary traffic
- **1.3.2** — Outbound traffic from the CDE is restricted to only necessary traffic
- **1.4.1** — NSCs are implemented between trusted and untrusted networks
- **1.4.5** — Disclosure of internal IP addresses is prevented
- **1.5.1** — Security controls on all computing devices connecting via untrusted networks

**Implementation Guidance:**
- Deploy next-generation firewalls (NGFW) at CDE boundaries
- Implement Web Application Firewalls (WAF) for web-facing payment applications
- Use network segmentation to isolate CDE from corporate network
- Restrict inbound to CDE: only necessary ports/protocols from known sources
- Restrict outbound from CDE: only approved destinations (payment processor, updates)
- Document all firewall rules with business justification
- Review firewall rules at least every 6 months
- Implement micro-segmentation where possible

---

### Requirement 2: Apply Secure Configurations to All System Components

**Objective:** Ensure all systems are configured securely with no unnecessary default settings.

**Key Sub-Requirements:**
- **2.2.1** — Configuration standards developed for all system components
- **2.2.2** — Vendor default accounts managed (changed, disabled, or removed)
- **2.2.3** — Primary functions requiring different security levels are managed (one primary function per server or use containerization)
- **2.2.4** — Only necessary services, protocols, daemons, and functions are enabled
- **2.2.5** — Insecure services are secured if present
- **2.2.6** — System security parameters are configured to prevent misuse
- **2.2.7** — Non-console administrative access is encrypted

**Implementation Guidance:**
- Apply CIS Benchmarks as baseline configurations
- Change ALL vendor default passwords before deployment
- Remove or disable unnecessary services, protocols, and daemon
- Harden operating systems using DISA STIGs or CIS Benchmarks
- Enforce encrypted administrative access (SSH, HTTPS, TLS 1.2+)
- Use configuration management tools for consistency (Ansible, Chef, Puppet)
- Deploy from hardened golden images

---

### Requirement 3: Protect Stored Account Data

**Objective:** Minimize stored data and protect it with strong cryptography.

**Key Sub-Requirements:**
- **3.2.1** — Data retention and disposal policies implemented
- **3.3.1** — SAD not retained after authorization (even if encrypted)
- **3.3.2** — SAD that is stored before authorization is encrypted using strong cryptography
- **3.4.1** — PAN is masked when displayed (show only first 6 and last 4 digits max)
- **3.5.1** — PAN is rendered unreadable anywhere it is stored (encryption, tokenization, truncation, or hashing)
- **3.6.1** — Cryptographic key management procedures are defined and implemented
- **3.7.1-3.7.9** — Comprehensive key management lifecycle

**Implementation Guidance:**
- Minimize PAN storage — do not store unless absolutely necessary
- Use tokenization to replace PANs with non-reversible tokens
- Encrypt stored PAN with AES-256 (or equivalent)
- Never store SAD (CVV, track data, PIN) after authorization — period
- Mask PAN in all displays: show max first 6 / last 4 digits
- Implement HSM-based key management for encryption keys
- Rotate encryption keys at least annually
- Use split knowledge and dual control for key management
- Maintain key inventory with custodian assignments
- Use DUKPT or ANSI X9.24 for key management in POS environments

**Tokenization vs Encryption Decision:**

| Factor | Tokenization | Encryption |
|--------|-------------|------------|
| Reversibility | Non-reversible (preferred) | Reversible with key |
| Scope reduction | Removes systems from CDE scope | Systems remain in scope |
| Performance | Faster lookup (token maps) | Encryption/decryption overhead |
| Use case | Card-on-file, recurring billing | Data that must be recovered |
| Recommendation | Prefer tokenization when possible | Use when PAN recovery is required |

---

### Requirement 4: Protect Cardholder Data with Strong Cryptography During Transmission

**Objective:** Encrypt CHD whenever transmitted over open, public networks.

**Key Sub-Requirements:**
- **4.2.1** — Strong cryptography and security protocols protect CHD during transmission over open, public networks
- **4.2.1.1** — Trusted certificates for PAN transmission over open, public networks
- **4.2.1.2** — Wireless networks transmitting PAN use industry best practices for strong cryptography
- **4.2.2** — PAN is secured with strong cryptography whenever sent via end-user messaging technologies

**Implementation Guidance:**
- Use TLS 1.2 as minimum, prefer TLS 1.3
- Disable SSL, TLS 1.0, TLS 1.1 entirely
- Use strong cipher suites (ECDHE key exchange, AES-GCM)
- Implement certificate pinning for mobile payment apps
- Deploy HSTS (HTTP Strict Transport Security) on all payment pages
- Use mTLS (mutual TLS) between internal CDE components
- Monitor certificate expiration and automate renewal
- Never send PAN via email, chat, or SMS unencrypted

---

### Requirement 5: Protect All Systems and Networks from Malicious Software

**Objective:** Defend all systems against malware.

**Key Sub-Requirements:**
- **5.2.1** — Anti-malware solution(s) deployed on all system components
- **5.2.2** — Anti-malware solution performs periodic and real-time scans
- **5.2.3** — For systems not commonly affected by malware, periodic evaluations performed
- **5.3.1** — Anti-malware mechanisms are kept current
- **5.3.2** — Anti-malware performs periodic and real-time scans
- **5.3.3** — For removable media, anti-malware scans automatically upon insertion
- **5.3.4** — Audit logs for anti-malware are enabled and retained
- **5.3.5** — Anti-malware cannot be disabled or altered by users (except case-by-case with management approval for limited time, logged)
- **5.4.1** — Mechanisms detect and protect against phishing attacks

**Implementation Guidance:**
- Deploy EDR/XDR on all endpoints (workstations, servers, POS terminals)
- Ensure real-time scanning with automatic definition updates
- Enable email-based anti-phishing controls (SPF, DKIM, DMARC, sandbox)
- Implement application allowlisting on POS and critical CDE systems
- Log all anti-malware events and integrate with SIEM
- For Linux/Unix systems: document risk evaluation and deploy appropriate controls

---

### Requirement 6: Develop and Maintain Secure Systems and Software

**Objective:** Protect against vulnerabilities through secure development and timely patching.

**Key Sub-Requirements:**
- **6.2.1** — Custom software developed securely (OWASP, CERT, SANS)
- **6.2.2** — Developer training in secure coding at least annually
- **6.2.3** — Custom software reviewed before release to identify vulnerabilities
- **6.2.4** — Software engineering techniques prevent common vulnerabilities (OWASP Top 10)
- **6.3.1** — Security vulnerabilities identified and managed (vulnerability management process)
- **6.3.2** — Software inventory maintained to enable vulnerability management
- **6.3.3** — Critical and high vulnerabilities patched within defined timeframes
- **6.4.1** — Public-facing web apps protected against known attacks (WAF or code review)
- **6.4.2** — Public-facing web apps have automated technical solution to detect and prevent web-based attacks (WAF in blocking mode)
- **6.4.3** — All payment page scripts managed, authorized, and integrity-ensured
- **6.5.1-6.5.6** — Change management procedures for all CDE system changes

**Implementation Guidance:**
- Implement SDLC with security gates (design review, code review, security testing)
- Train developers annually on secure coding (OWASP Top 10, CWE/SANS Top 25)
- Deploy WAF in blocking mode for all public-facing payment applications
- Patch critical vulnerabilities within 30 days, high within 60 days
- Implement Content Security Policy (CSP) and Subresource Integrity (SRI) for payment pages
- Monitor and authorize all JavaScript on payment pages (6.4.3 is critical for e-commerce)
- Conduct code reviews (manual or automated SAST) for all custom payment code
- Maintain complete software inventory with versions

---

### Requirement 7: Restrict Access to System Components and Cardholder Data by Business Need to Know

**Objective:** Limit access to CHD to only those with a legitimate business need.

**Key Sub-Requirements:**
- **7.2.1** — Access control model defined and includes all system components
- **7.2.2** — Access assigned based on job classification and function
- **7.2.3** — Required privileges approved by authorized personnel
- **7.2.4** — All user accounts and related access privileges reviewed at least every 6 months
- **7.2.5** — All application and system accounts assigned and managed based on least privilege
- **7.2.5.1** — Access for application and system accounts reviewed periodically
- **7.2.6** — All user access to query repositories of stored CHD is restricted

**Implementation Guidance:**
- Implement role-based access control (RBAC) for all CDE systems
- Document access control policy with defined roles and permissions
- Enforce least privilege — users get minimum access needed
- Review all CDE access every 6 months and recertify
- Restrict database query access to CHD (no ad hoc SELECT * from card_data)
- Separate duties — no single person should control all aspects of a transaction
- Use automated identity governance for access provisioning and reviews

---

### Requirement 8: Identify Users and Authenticate Access to System Components

**Objective:** Ensure all access to CDE is identified and strongly authenticated.

**Key Sub-Requirements:**
- **8.2.1** — All users assigned a unique ID before access
- **8.2.2** — Group, shared, or generic accounts not used (exceptions must be documented)
- **8.3.1** — All user access to CDE authenticated with at least one factor
- **8.3.2** — Strong cryptography used for all authentication factors
- **8.3.4** — Invalid authentication attempts limited (lockout after max 10 attempts for min 30 minutes)
- **8.3.6** — New passwords/passphrases: minimum 12 characters (or 8 if system cannot support 12), containing both numeric and alphabetic
- **8.3.9** — Passwords/passphrases changed at least every 90 days (or continuous risk-based approach)
- **8.4.1** — MFA implemented for all non-console access into CDE for administrative access
- **8.4.2** — MFA implemented for all access into the CDE
- **8.4.3** — MFA for all remote network access originating from outside the entity's network
- **8.5.1** — MFA implementation not susceptible to replay attacks, cannot be bypassed
- **8.6.1** — Interactive login for system/service accounts managed, disabled when not needed
- **8.6.2** — Passwords/passphrases for system/service accounts not hard-coded in scripts
- **8.6.3** — Passwords/passphrases for system/service accounts changed periodically and upon suspicion of compromise

**Implementation Guidance:**
- MFA is mandatory for ALL access into the CDE (not just admin) — this is a v4.0 change
- Use phishing-resistant MFA (FIDO2/WebAuthn, hardware keys) where possible
- Minimum 12-character passwords with complexity requirements
- Implement account lockout after 10 failed attempts
- Never use shared accounts in the CDE
- Manage service accounts — no hard-coded passwords, rotate periodically
- Deploy PAM for administrative access to CDE systems
- Log all authentication events and integrate with SIEM

---

### Requirement 9: Restrict Physical Access to Cardholder Data

**Objective:** Prevent unauthorized physical access to systems that store, process, or transmit CHD.

**Key Sub-Requirements:**
- **9.2.1** — Appropriate facility entry controls for CDE
- **9.2.3** — Physical access to wireless access points, gateways, and networking devices restricted
- **9.2.4** — Console access to sensitive areas controlled
- **9.3.1** — Authorization for physical access reviewed at least every 6 months
- **9.3.2** — Procedures for visitor identification and management
- **9.3.3** — Visitor badges or identification surrendered upon departure
- **9.4.1** — Media with CHD physically secured
- **9.4.5** — Inventory of electronic media with CHD maintained
- **9.4.6** — Hard-copy materials with CHD destroyed when no longer needed (cross-cut shred, incinerate)
- **9.4.7** — Electronic media with CHD rendered unrecoverable (degauss, crypto-erase, destroy)
- **9.5.1** — POI (Point of Interaction) devices protected from tampering and substitution

**Implementation Guidance:**
- Implement badge access to server rooms and data centers housing CDE
- Deploy CCTV with 90-day retention for CDE physical locations
- Maintain visitor logs with escort requirements
- Inspect POS terminals regularly for skimming devices (daily/weekly)
- Cross-cut shred all paper containing CHD
- Cryptographically erase or physically destroy media before disposal
- Restrict access to network infrastructure components

---

### Requirement 10: Log and Monitor All Access to System Components and Cardholder Data

**Objective:** Create comprehensive audit trails for all access to CDE and CHD.

**Key Sub-Requirements:**
- **10.2.1** — Audit logs capture all individual user access to CHD
- **10.2.1.1** — Audit logs capture all individual access to CHD
- **10.2.1.2** — All actions by any individual with administrative access are logged
- **10.2.1.3** — Access to all audit logs
- **10.2.1.4** — Invalid logical access attempts
- **10.2.1.5** — Changes to identification and authentication mechanisms
- **10.2.1.6** — Initialization, stopping, or pausing of audit logs
- **10.2.1.7** — Creation and deletion of system-level objects
- **10.2.2** — Audit logs include required details (user ID, event type, date/time, success/failure, origin, data/component affected)
- **10.3.1** — Read access to audit logs is restricted
- **10.3.2** — Audit log files are protected from modification
- **10.3.3** — Audit log files are backed up to a central log server
- **10.3.4** — File integrity monitoring on audit logs
- **10.4.1** — Audit logs reviewed at least daily for security events
- **10.4.1.1** — Automated mechanisms perform audit log reviews
- **10.4.2** — Logs of all CDE components are reviewed periodically
- **10.5.1** — Retain audit log history for at least 12 months (3 months immediately available)
- **10.6.1** — System clocks synchronized using NTP
- **10.6.2** — Time data protected
- **10.6.3** — Time settings received from industry-accepted sources

**Implementation Guidance:**
- Deploy SIEM for centralized log collection and automated review
- Log all access to CHD, administrative actions, and security events
- Protect log integrity with WORM storage or blockchain-based logging
- Retain logs for 12 months minimum (3 months online, remainder archived)
- Synchronize all system clocks to NTP (stratum 2 or better)
- Review logs daily using automated correlation rules
- Alert on suspicious patterns (multiple failed logins, after-hours access, bulk data access)

---

### Requirement 11: Test Security of Systems and Networks Regularly

**Objective:** Regularly test security controls, systems, and networks to verify they work.

**Key Sub-Requirements:**
- **11.2.1** — Authorized and unauthorized wireless access points managed
- **11.2.2** — Wireless analyzer scans at least quarterly
- **11.3.1** — Internal vulnerability scans at least quarterly
- **11.3.1.1** — All other applicable vulnerabilities (non-critical/high) addressed and rescanned
- **11.3.1.3** — Internal scans after significant changes
- **11.3.2** — External vulnerability scans by ASV at least quarterly
- **11.4.1** — External penetration testing at least annually and after significant changes
- **11.4.3** — Internal penetration testing at least annually and after significant changes
- **11.4.4** — Vulnerabilities found during penetration testing are corrected
- **11.4.5** — Network segmentation tested at least annually (every 6 months for service providers)
- **11.5.1** — IDS/IPS deployed to monitor traffic into and within CDE
- **11.5.1.1** — IDS/IPS alerts generated for suspected compromises
- **11.5.2** — Change-detection mechanism (file integrity monitoring) deployed on critical files
- **11.6.1** — A change and tamper-detection mechanism deployed for payment pages

**Implementation Guidance:**
- Quarterly internal vulnerability scans with all high/critical resolved before pass
- Quarterly external ASV scans (must achieve passing scan)
- Annual external and internal penetration tests (by qualified tester)
- Pen tests must test network layer and application layer
- Deploy IDS/IPS at CDE perimeter and critical internal points
- FIM on critical system files, configuration files, and content files
- Wireless scanning quarterly to detect rogue access points
- Test network segmentation annually to verify CDE isolation
- Deploy change/tamper detection on payment page scripts (ties to 6.4.3)

---

### Requirement 12: Support Information Security with Organizational Policies and Programs

**Objective:** Maintain an information security policy that addresses all PCI DSS requirements.

**Key Sub-Requirements:**
- **12.1.1** — Information security policy established, published, maintained, disseminated
- **12.1.2** — Roles and responsibilities defined for all requirements
- **12.1.3** — Information security policy reviewed at least annually
- **12.2.1** — Acceptable use policies for end-user technologies
- **12.3.1** — Targeted risk analysis for each requirement with customized approach flexibility
- **12.3.2** — Targeted risk analysis for each requirement met with customized approach
- **12.4.1** — Executive management establishes responsibility for protection of CHD
- **12.4.2** — Reviews performed at least quarterly (service providers: operations compliance)
- **12.5.1** — PCI DSS scope documented and confirmed annually
- **12.5.2** — PCI DSS scope documented and confirmed upon significant changes
- **12.5.3** — Significant changes resulting in scope changes trigger assessment
- **12.6.1** — Security awareness program implemented
- **12.6.2** — Awareness program reviewed at least annually
- **12.6.3** — Personnel receive awareness training upon hire and at least annually
- **12.6.3.1** — Training includes awareness of threats (phishing, social engineering)
- **12.8.1-12.8.5** — TPSPs (Third-Party Service Providers) managed
- **12.9.1** — TPSPs acknowledge responsibility for CHD security
- **12.10.1** — Incident response plan created and ready for activation
- **12.10.2** — IRP reviewed and tested at least annually
- **12.10.4** — Personnel with incident response responsibilities are trained
- **12.10.5** — IRP includes monitoring and responding to alerts
- **12.10.6** — IRP is updated based on lessons learned and industry developments
- **12.10.7** — Incident response procedures are in place to respond to detection of stored PAN anywhere not expected

**Implementation Guidance:**
- Create comprehensive security policy covering all 12 requirements
- Conduct targeted risk analysis for any customized approach implementations
- Confirm PCI DSS scope annually and after any significant changes
- Deliver security awareness training at hire and annually
- Include phishing awareness, social engineering, and CHD handling in training
- Manage all third-party service providers (maintain list, require compliance attestation)
- Maintain and test incident response plan at least annually
- Include specific procedures for unauthorized PAN discovery

---

## v4.0 Changes from v3.2.1

### Major Changes

**1. Customized Approach (NEW)**
Organizations can now meet PCI DSS requirements using a "customized approach" rather than the traditional "defined approach." This allows organizations to design their own security controls, provided they meet the security objective of each requirement. Requires targeted risk analysis documentation and validation by QSA.

**2. Targeted Risk Analysis**
v4.0 requires organizations to perform documented, targeted risk analyses for certain requirements (e.g., frequency of activities, password/passphrase policies). This replaces the "one-size-fits-all" approach.

**3. Enhanced Authentication Requirements**
- MFA required for ALL access into the CDE (not just remote admin)
- Minimum password length increased to 12 characters (from 7)
- 90-day password rotation or continuous risk-based authentication

**4. Payment Page Script Security (6.4.3)**
All scripts on payment pages must be managed, authorized, and monitored for integrity. This addresses Magecart-style attacks.

**5. Anti-Phishing Mechanisms (5.4.1)**
Organizations must implement automated anti-phishing mechanisms (e.g., DMARC, email sandbox).

**6. Encryption of PAN Over Trusted Internal Networks (4.2.1)**
PAN must now be encrypted during transmission over ALL networks, not just public networks. Internal network encryption required.

**7. Automated Log Review (10.4.1.1)**
Automated mechanisms must perform audit log reviews — manual-only review no longer sufficient.

### Summary of Future-Dated Requirements (Now Mandatory)

All of the following became mandatory as of March 31, 2025:

| Requirement | What Changed |
|---|---|
| 3.3.2 | SAD encrypted before authorization if stored |
| 3.5.1.2 | Disk-level encryption no longer satisfies requirement (must be above disk) |
| 5.3.3 | Anti-malware scans on removable media |
| 5.4.1 | Anti-phishing mechanisms required |
| 6.3.2 | Software inventory for vulnerability management |
| 6.4.2 | WAF in blocking mode for public web apps |
| 6.4.3 | Payment page script management |
| 8.3.6 | 12-character minimum passwords |
| 8.4.2 | MFA for all CDE access |
| 8.5.1 | MFA replay attack protection |
| 8.6.1-3 | System/service account management |
| 10.4.1.1 | Automated log review |
| 10.7.2 | Detect failures of critical security controls |
| 11.3.1.1 | Manage all vulnerabilities (not just high/critical) |
| 11.4.7 | Multi-tenant service provider pen testing |
| 11.5.1.1 | IDS/IPS alerts for suspected compromise |
| 11.6.1 | Payment page tamper detection |
| 12.3.1 | Targeted risk analysis |
| 12.6.3.1 | Phishing/social engineering in awareness training |
| 12.10.7 | Respond to unexpected stored PAN |

---

## Cardholder Data Environment Scoping

### CDE Definition

The Cardholder Data Environment (CDE) includes:
1. **System components that store, process, or transmit CHD/SAD** — These are directly in scope
2. **System components on the same network segment** — These are in scope unless segmented
3. **System components that connect to or provide security services** — Connected-to and security-impacting systems

### System Classification

| Category | Definition | In Scope? | Examples |
|----------|-----------|-----------|---------|
| CDE Systems | Store, process, or transmit CHD | Yes — Full scope | Payment servers, databases with PAN, POS terminals |
| Connected-to | Direct connectivity to CDE | Yes — Full scope | DNS servers for CDE, AD/LDAP for CDE authentication |
| Security-Impacting | Provide security services to CDE | Yes — Full scope | SIEM, AV server, patch management for CDE systems |
| Out of Scope | No connectivity, no CHD, no security impact | No | Isolated HR systems, marketing servers |

### Scope Reduction Strategies

**1. Tokenization:** Replace PAN with non-reversible tokens. Systems that only handle tokens are out of scope.

**2. P2PE (Point-to-Point Encryption):** Validated P2PE solutions encrypt cardholder data at the point of interaction. Merchants using validated P2PE can use SAQ P2PE (reduced scope).

**3. Network Segmentation:** Isolate CDE on a separate network segment with firewalls and strict access controls. Non-CDE segments are out of scope.

**4. Outsource Processing:** Use third-party payment processors (Stripe, Braintree, Adyen) to handle all CHD. The merchant never touches cardholder data.

**5. iFrame/Redirect:** For e-commerce, use the payment processor's hosted payment page (iFrame or redirect). The merchant's systems never receive cardholder data.

---

## SAQ Types and Selection Guide

Self-Assessment Questionnaires (SAQs) are validation tools for merchants and service providers not required to undergo a full on-site assessment (ROC).

| SAQ Type | Applies To | CHD Handling | Questions |
|----------|-----------|-------------|-----------|
| **SAQ A** | E-commerce or MOTO merchants | All payment processing fully outsourced; no electronic storage/processing/transmission of CHD | ~30 |
| **SAQ A-EP** | E-commerce merchants | Payment page elements from third party, but merchant website impacts security of payment transaction | ~140 |
| **SAQ B** | Merchants with standalone POS (dial-out terminals) | Imprint-only or standalone dial-out terminals; no electronic CHD storage | ~40 |
| **SAQ B-IP** | Merchants with standalone IP-connected POS | Standalone POS terminals connected via IP; no electronic CHD storage | ~80 |
| **SAQ C** | Merchants with payment app systems connected to internet | Payment application connected to internet; no electronic CHD storage | ~160 |
| **SAQ C-VT** | Merchants with web-based virtual terminals | Manual entry via virtual terminal from processor's web-based solution; no electronic CHD storage | ~80 |
| **SAQ D (Merchant)** | All other merchants | Does not qualify for other SAQ types | ~330 |
| **SAQ D (Service Provider)** | Service providers | Service providers eligible for SAQ | ~330 |
| **SAQ P2PE** | Merchants using validated P2PE | Hardware terminals with validated P2PE solution; no electronic CHD storage | ~30 |

### SAQ Selection Decision Tree

```
Does your organization store, process, or transmit CHD?
├── No → Not subject to PCI DSS
└── Yes → Continue
    │
    Are you a Service Provider?
    ├── Yes → SAQ D (Service Provider) or ROC
    └── No (Merchant) → Continue
        │
        Do you store CHD electronically?
        ├── Yes → SAQ D (Merchant)
        └── No → Continue
            │
            E-commerce only?
            ├── Yes → Do you fully outsource all payment processing?
            │   ├── Yes (iFrame/redirect, no scripts on payment page) → SAQ A
            │   └── No (payment page on your server or scripts affecting payment) → SAQ A-EP
            ├── Card-present (POS)?
            │   ├── Using validated P2PE? → SAQ P2PE
            │   ├── Standalone dial-out terminal? → SAQ B
            │   ├── Standalone IP-connected terminal? → SAQ B-IP
            │   └── Payment application system? → SAQ C
            └── Virtual terminal only? → SAQ C-VT
```

---

## Assessment Types

### Self-Assessment Questionnaire (SAQ)

**Who:** Level 2-4 merchants (unless acquirer requires ROC)
**What:** Self-assessment using applicable SAQ type
**Frequency:** Annual
**Output:** Completed SAQ + Attestation of Compliance (AOC)

### Report on Compliance (ROC)

**Who:** Level 1 merchants, all Level 1 service providers
**What:** On-site assessment by Qualified Security Assessor (QSA)
**Frequency:** Annual
**Output:** ROC document + AOC

### Attestation of Compliance (AOC)

**Who:** All entities, accompanies SAQ or ROC
**What:** Executive summary confirming compliance status
**Frequency:** Annual, accompanies assessment
**Output:** Signed AOC form

---

## Merchant and Service Provider Levels

### Merchant Levels

| Level | Annual Visa Transactions | Assessment Required |
|-------|------------------------|-------------------|
| **Level 1** | Over 6 million | Annual ROC by QSA + quarterly ASV scan |
| **Level 2** | 1 million to 6 million | Annual SAQ + quarterly ASV scan |
| **Level 3** | 20,000 to 1 million (e-commerce) | Annual SAQ + quarterly ASV scan |
| **Level 4** | Under 20,000 (e-commerce) or up to 1 million (other) | Annual SAQ + quarterly ASV scan (recommended) |

**Note:** Card brands and acquirers may have different thresholds. Check with your acquirer.

### Service Provider Levels

| Level | Annual Transactions | Assessment Required |
|-------|-------------------|-------------------|
| **Level 1** | Over 300,000 | Annual ROC by QSA + quarterly ASV scan |
| **Level 2** | Under 300,000 | Annual SAQ D + quarterly ASV scan |

---

## Infrastructure Controls

### Network Segmentation Validation

**Purpose:** Verify CDE is properly isolated from non-CDE networks.

**Testing Methods:**
- Firewall rule review — verify only approved traffic can cross CDE boundary
- Penetration testing from non-CDE segments attempting to reach CDE
- Traffic analysis confirming no unintended data flows
- VLAN hopping tests
- ARP spoofing tests

**Frequency:** Annually (every 6 months for service providers)

### DNS Security for Payment Systems

- Implement DNSSEC for all CDE domain names
- Use internal DNS servers for CDE (not public resolvers)
- Monitor DNS queries from CDE for data exfiltration indicators
- Restrict CDE DNS queries to approved destinations only
- Implement DNS sinkholing for known malicious domains

### TLS Configuration for Payment Channels

- Minimum TLS 1.2, prefer TLS 1.3 for all payment communications
- Strong cipher suites only: ECDHE key exchange, AES-GCM
- HSTS with long max-age on all payment-related web pages
- Certificate transparency monitoring for payment domains
- Automated certificate renewal (Let's Encrypt, ACME protocol)
- mTLS between CDE microservices
- Certificate pinning for mobile payment applications

### Endpoint Security for POS Systems

- Harden POS operating systems (application allowlisting)
- Deploy endpoint protection with anti-tamper capabilities
- Implement POS-specific network segmentation
- Regular POS terminal inspection for skimming devices
- Remote POS management via encrypted channels only
- Disable USB ports and external interfaces on POS terminals
- Monitor POS terminal integrity

### Cloud Security for Payment Processing

**AWS:**
- Use VPC with private subnets for CDE workloads
- AWS KMS or CloudHSM for encryption key management
- GuardDuty for threat detection in CDE
- Config rules for CDE compliance monitoring
- S3 bucket policies preventing public access to CHD
- Restrict IAM roles accessing CDE resources

**Azure:**
- Azure Virtual Network with NSGs for CDE isolation
- Azure Key Vault (HSM-backed) for key management
- Microsoft Defender for Cloud for CDE monitoring
- Azure Policy for CDE compliance enforcement
- Storage Service Encryption with customer-managed keys

**GCP:**
- VPC Service Controls for CDE isolation
- Cloud KMS or Cloud HSM for key management
- Security Command Center for CDE visibility
- Organization policies restricting CDE resource configuration
- BigQuery with column-level encryption for analytics on payment data

### Container/Kubernetes Security in CDE

- Scan container images for vulnerabilities before deployment
- Use private container registries with signed images
- Implement Kubernetes RBAC with CDE-specific namespaces
- Pod Security Standards (Restricted) for CDE pods
- Network policies isolating CDE pods
- No privileged containers in CDE
- Secrets management via external vault (not Kubernetes secrets)
- Service mesh (Istio, Linkerd) with mTLS for CDE pod-to-pod traffic
- Runtime security monitoring (Falco, Sysdig)

### API Security for Payment APIs

- OAuth 2.0 / OpenID Connect for API authentication
- API rate limiting and throttling
- Input validation and output encoding for all API parameters
- API gateway with WAF protection
- API versioning with deprecated version retirement
- Mutual TLS for server-to-server API calls
- PCI-compliant API logging (mask PAN in logs)
- API security testing (DAST) in CI/CD pipeline

### Tokenization Architecture

```
┌───────────────┐     ┌──────────────────┐     ┌────────────────┐
│   Customer     │────▶│   Payment Page    │────▶│ Token Service  │
│   (Browser)    │     │   (Merchant)      │     │ (Processor)    │
└───────────────┘     └──────────────────┘     └──────┬─────────┘
                                                       │
                                              ┌────────▼────────┐
                                              │   Token Vault    │
                                              │   (PAN → Token)  │
                                              └────────┬────────┘
                                                       │
                                              ┌────────▼────────┐
                                              │  Card Network    │
                                              │  (Detokenize)    │
                                              └─────────────────┘
```

**Key Points:**
- Token format should be indistinguishable from PAN (same length, passes Luhn check is optional)
- Token vault must be PCI DSS compliant
- Tokens should be non-reversible without access to the vault
- Use format-preserving tokens when legacy systems require card-like values

### Encryption Key Management

**DUKPT (Derived Unique Key Per Transaction):**
- Used in POS environments
- Each transaction uses a unique encryption key
- Derived from a Base Derivation Key (BDK)
- Protects against mass compromise from single key exposure

**P2PE (Point-to-Point Encryption):**
- Encrypts at the terminal (point of interaction)
- Decrypts only at the processor's secure environment
- Validated P2PE solutions listed on PCI SSC website
- Significantly reduces merchant's CDE scope

**Key Lifecycle:**
- Generation: Use HSM or certified key generation
- Distribution: Split knowledge, dual control
- Storage: HSM or encrypted key storage
- Usage: Track key usage and enforce permitted operations
- Rotation: Annual rotation minimum; immediately upon suspected compromise
- Destruction: Cryptographic erase with verification

---

## PCI DSS Compliance Roadmap

### Phase 1: Scope and Assess (Months 1-2)

1. **Determine Merchant/SP Level** — Transaction volume determines assessment type
2. **Define CDE Scope** — Map all systems that store, process, or transmit CHD
3. **Identify SAQ Type** — Use the scope analyzer tool
4. **Conduct Gap Assessment** — Use the compliance checker tool
5. **Document Scope** — Create CDE inventory and data flow diagram

**Deliverables:**
- CDE scope document with data flow diagrams
- Gap assessment report with prioritized findings
- SAQ type determination
- Project plan and budget estimate

### Phase 2: Quick Wins and Critical Gaps (Months 3-4)

1. **Stop storing SAD** — Eliminate any storage of CVV, track data, PIN immediately
2. **Enable MFA for CDE** — Deploy MFA for all CDE access (Req 8.4.2)
3. **Enable encryption** — Encrypt stored PAN and PAN in transit (Req 3, 4)
4. **Deploy logging** — Centralize logs from CDE systems (Req 10)
5. **Update passwords** — Enforce 12-character minimum (Req 8.3.6)

### Phase 3: Core Controls (Months 5-7)

1. **Network segmentation** — Isolate CDE, deploy firewalls, restrict traffic (Req 1)
2. **Hardening** — Apply CIS Benchmarks to all CDE systems (Req 2)
3. **Access controls** — Implement RBAC, least privilege, access reviews (Req 7)
4. **Vulnerability management** — Deploy scanning, establish patch SLAs (Req 6, 11)
5. **Anti-malware** — Deploy EDR/XDR, anti-phishing controls (Req 5)

### Phase 4: Advanced Controls (Months 8-10)

1. **WAF deployment** — Deploy in blocking mode for payment web apps (Req 6.4.2)
2. **Payment page security** — Manage scripts, deploy tamper detection (Req 6.4.3, 11.6.1)
3. **Penetration testing** — External and internal pen tests (Req 11.4)
4. **IDS/IPS** — Deploy at CDE perimeter and internal segments (Req 11.5)
5. **Physical security** — Secure data centers, POS terminals, media (Req 9)

### Phase 5: Policy, Training, and Validation (Months 11-12)

1. **Security policy** — Comprehensive policy covering all 12 requirements (Req 12)
2. **Awareness training** — Deploy training program with phishing simulation (Req 12.6)
3. **Third-party management** — Assess and document all TPSPs (Req 12.8)
4. **Incident response** — Develop and test IRP (Req 12.10)
5. **Formal assessment** — Complete SAQ or schedule QSA for ROC

---

## Reference Guides

| Guide | Description |
|-------|-------------|
| [PCI DSS Requirements Guide](references/pci-dss-requirements-guide.md) | Complete 12 requirements with sub-requirements, testing procedures, v4.0 changes |
| [PCI Infrastructure Security](references/pci-infrastructure-security.md) | Network architecture, cloud deployment, tokenization, key management, API security |

---

## Validation Checkpoints

### Before Starting Assessment
- [ ] Merchant/SP level determined based on transaction volume
- [ ] CDE scope defined with data flow diagrams
- [ ] SAQ type identified (or ROC requirement confirmed)
- [ ] All systems in scope inventoried
- [ ] Payment processor compliance attestation obtained

### During Assessment
- [ ] Each requirement assessed with evidence collected
- [ ] Network segmentation validated
- [ ] Encryption verified (at rest and in transit)
- [ ] Access controls tested (RBAC, MFA, least privilege)
- [ ] Logging and monitoring validated (SIEM, log retention)
- [ ] Vulnerability scans and pen test results reviewed

### After Assessment
- [ ] SAQ/ROC completed with all sections addressed
- [ ] AOC signed by authorized officer
- [ ] Quarterly ASV scans scheduled
- [ ] Remediation plan for any findings
- [ ] Next assessment date scheduled
- [ ] Scope re-validation trigger process documented

### Ongoing Compliance
- [ ] Quarterly internal vulnerability scans
- [ ] Quarterly external ASV scans
- [ ] Annual penetration testing
- [ ] Annual security awareness training
- [ ] Annual policy review
- [ ] Annual scope re-validation
- [ ] Semi-annual firewall rule review
- [ ] Semi-annual access review
- [ ] Daily log review (automated)

---

## Troubleshooting

| Problem | Likely Cause | Resolution |
|---------|-------------|------------|
| Compliance checker reports 0% for a requirement | Controls JSON missing the requirement section entirely | Ensure the `requirements` object in the input JSON includes entries for all 12 requirements (keys `"1"` through `"12"`). Use a sample template as a starting point. |
| Scope analyzer returns wrong SAQ type | Business model flags incorrectly set (e.g., `stores_pan` true when using tokenization) | Review all boolean flags: `stores_pan`, `processes_pan`, `transmits_pan`, `uses_iframe_redirect`, `uses_p2pe`. Tokenized PANs are not considered stored CHD. |
| Gap report shows requirements as non-applicable | The `--requirements` flag is filtering scope | Remove the `--requirements` flag to assess all 12 requirements. When specified, only the listed requirements are evaluated. |
| Encryption controls flagged despite AES-256 | Disk-level encryption used instead of file/column-level | PCI DSS v4.0 no longer accepts disk-level encryption as encryption at rest (except removable media). Implement file-level, column-level, or application-layer encryption. |
| MFA requirement flagged even though MFA is deployed | MFA not covering all CDE access paths | PCI DSS v4.0 requires MFA for all access into the CDE, not just remote access. Verify MFA covers console, VPN, API, and administrative access. |
| Payment page script controls failing | Requirements 6.4.3 and 11.6.1 not addressed | Inventory all scripts on payment pages, document authorization and integrity for each, and deploy tamper-detection mechanisms. These became mandatory March 31, 2025. |
| Third-party service provider compliance gaps | TPSP AOC not obtained or expired | Obtain current Attestation of Compliance (AOC) from every third-party service provider handling cardholder data. Verify scope coverage matches your use case. |

---

## Success Criteria

- CDE scope clearly defined with network diagrams, data flow documentation, and system inventory covering all in-scope components
- SAQ type correctly determined and validated against actual business model, payment channels, and data handling practices
- Compliance score of 80%+ across all 12 requirements on initial assessment, trending to 95%+ before formal audit
- All future-dated v4.0 requirements (mandatory since March 31, 2025) fully implemented, including payment page script controls (6.4.3, 11.6.1), targeted risk analysis, and enhanced MFA
- Quarterly ASV scans passing with no exploitable vulnerabilities, and annual penetration testing completed with findings remediated
- Third-party service providers validated with current AOCs covering the services used, and TPSP monitoring procedures documented
- Scope reduction strategies implemented (tokenization, P2PE, network segmentation) reducing the number of in-scope systems by 30%+

---

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

---

## Integration Points

| Skill | Integration |
|-------|------------|
| [infrastructure-compliance-auditor](../infrastructure-compliance-auditor/) | Validates network segmentation, TLS configuration, endpoint security, and logging controls that satisfy PCI DSS Requirements 1, 2, 4, 10, 11 |
| [nist-csf-specialist](../nist-csf-specialist/) | CSF functions map to PCI DSS requirements; use the control mapper to build unified control matrices for dual-compliance programs |
| [soc2-compliance-expert](../soc2-compliance-expert/) | SOC 2 CC6 (access), CC7 (operations), CC8 (change management) overlap significantly with PCI DSS; leverage shared evidence |
| [information-security-manager-iso27001](../information-security-manager-iso27001/) | ISO 27001 Annex A controls provide a management system framework supporting PCI DSS compliance |
| [nis2-directive-specialist](../nis2-directive-specialist/) | EU entities subject to both NIS2 and PCI DSS can map shared controls (encryption, incident response, access control) |

---

## Tool Reference

### pci_compliance_checker.py

Assesses compliance against all 12 PCI DSS v4.0 requirements with per-requirement scoring.

| Flag | Required | Description |
|------|----------|-------------|
| `--input` | Yes | Path to controls JSON file with per-requirement control status (boolean values) |
| `--output` | Yes | Path to write the compliance report |
| `--format` | No | Output format: `json` (default) or `markdown` |
| `--requirements` | No | Comma-separated list of requirement numbers to assess (e.g., `3,4,7,8`). Omit for all 12. |

### pci_scope_analyzer.py

Determines SAQ type and maps CDE boundaries based on business model.

| Flag | Required | Description |
|------|----------|-------------|
| `--input` | Yes | Path to business model JSON file with payment channel, data handling, and system inventory details |
| `--output` | Yes | Path to write the scope analysis report |
| `--format` | No | Output format: `json` (default) or `markdown` |
