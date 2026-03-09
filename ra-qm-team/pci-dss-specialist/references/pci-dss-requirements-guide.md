# PCI DSS v4.0 Requirements Guide — Complete Reference

This reference provides all 12 PCI DSS v4.0 requirements with sub-requirements, testing procedures, guidance, v4.0 changes, and customized approach considerations.

---

## Requirement 1: Install and Maintain Network Security Controls

**Goal:** Protect the cardholder data environment through network security controls (NSCs) such as firewalls, cloud security groups, and other traffic-filtering technologies.

### Sub-Requirements

| ID | Requirement | Testing Procedure | v4.0 Change |
|---|---|---|---|
| 1.1.1 | All security policies and operational procedures identified and kept current | Review documents, interview personnel | Clarified |
| 1.1.2 | Roles and responsibilities documented and understood | Review documentation, interview | Clarified |
| 1.2.1 | NSC configuration standards defined and implemented | Review standards, examine configurations | Updated |
| 1.2.2 | All changes to network connections and NSCs approved and managed | Review change records | Updated |
| 1.2.3 | Accurate network diagram maintained showing all connections | Examine diagram, compare to environment | Clarified |
| 1.2.4 | Accurate data-flow diagram maintained | Examine diagram | Clarified |
| 1.2.5 | All services, protocols, and ports allowed are identified, approved, and have defined business need | Review configurations, documentation | Updated |
| 1.2.6 | Security features defined for insecure services/protocols | Review configurations | Evolved |
| 1.2.7 | NSC configurations reviewed at least every 6 months | Review records | Updated |
| 1.2.8 | NSC configuration files secured from unauthorized access | Examine file permissions | New |
| 1.3.1 | Inbound traffic to CDE restricted | Examine NSC configs | Updated |
| 1.3.2 | Outbound traffic from CDE restricted | Examine NSC configs | Updated |
| 1.3.3 | NSCs installed between wireless networks and CDE | Examine configs, network diagrams | Updated |
| 1.4.1 | NSCs between trusted and untrusted networks | Examine network configs | Updated |
| 1.4.2 | Inbound traffic from untrusted restricted to authorized | Examine NSC configs | Updated |
| 1.4.3 | Anti-spoofing measures | Examine NSC configs | Updated |
| 1.4.4 | CHD cannot flow from untrusted to CDE without authorization | Test traffic flows | Updated |
| 1.4.5 | Disclosure of internal IPs prevented | Examine configurations | Updated |
| 1.5.1 | Security controls for computing devices on untrusted networks | Examine device configurations | Updated |

### Guidance and Good Practices

- Document every firewall rule with a business justification and owner
- Use deny-all default rules with explicit allow rules only
- Implement micro-segmentation within the CDE for defense in depth
- Review and clean up unused firewall rules during 6-month reviews
- Consider zero trust network architecture (ZTNA) as a long-term strategy

### Customized Approach Considerations

The security objective is to control traffic at CDE boundaries. Alternative controls could include software-defined perimeters, micro-segmentation platforms, or service mesh with mTLS, provided they meet the objective of restricting unauthorized traffic to and from the CDE.

---

## Requirement 2: Apply Secure Configurations to All System Components

**Goal:** Malicious individuals exploit vendor default settings and passwords. Ensure all systems are hardened before deployment.

### Sub-Requirements

| ID | Requirement | Testing Procedure | v4.0 Change |
|---|---|---|---|
| 2.1.1 | All security policies and procedures documented | Review documents | Clarified |
| 2.1.2 | Roles and responsibilities defined | Interview, review docs | Clarified |
| 2.2.1 | Configuration standards developed for all system types | Review standards | Updated |
| 2.2.2 | Vendor default accounts managed | Examine system configurations | Updated |
| 2.2.3 | Primary functions with different security levels managed | Examine configurations | Updated |
| 2.2.4 | Only necessary services enabled | Examine configurations | Updated |
| 2.2.5 | Insecure services secured if used | Examine documentation, configs | Clarified |
| 2.2.6 | System security parameters configured to prevent misuse | Examine configs | Updated |
| 2.2.7 | Non-console admin access encrypted | Examine configs | Updated |

### Guidance

- Maintain hardened golden images for all standard system types
- Use CIS Benchmarks Level 2 for CDE systems
- Automate hardening verification with compliance scanning tools
- Include containers and serverless functions in hardening standards
- Remove or rename all default accounts; change all default passwords

---

## Requirement 3: Protect Stored Account Data

**Goal:** Minimize data storage and protect any stored account data.

### Sub-Requirements

| ID | Requirement | v4.0 Change |
|---|---|---|
| 3.1.1 | All security policies documented | Clarified |
| 3.1.2 | Roles and responsibilities defined | Clarified |
| 3.2.1 | Data retention and disposal policies | Updated |
| 3.3.1 | SAD not stored after authorization | Critical — unchanged |
| 3.3.1.1 | Full track data not stored | Critical — unchanged |
| 3.3.1.2 | CVV/CVC not stored | Critical — unchanged |
| 3.3.1.3 | PIN/PIN block not stored | Critical — unchanged |
| 3.3.2 | SAD encrypted prior to authorization if stored | **New (was future-dated, now mandatory)** |
| 3.3.3 | Additional requirement for issuers storing SAD | Updated |
| 3.4.1 | PAN masked when displayed | Updated |
| 3.4.2 | PAN secured with technical controls preventing copy | **New** |
| 3.5.1 | PAN rendered unreadable anywhere stored | Updated |
| 3.5.1.1 | Hashes keyed using cryptographic keyed hashing | **New** |
| 3.5.1.2 | Disk/partition-level encryption only for removable media | **New (was future-dated, now mandatory)** |
| 3.5.1.3 | Disk/partition-level encryption not used to render PAN unreadable on non-removable media | **New requirement** |
| 3.6.1 | Cryptographic key management processes defined | Updated |
| 3.6.1.1 | Additional requirement for service providers | SP-specific |
| 3.7.1-3.7.9 | Key lifecycle management | Updated |

### Critical Points

- **NEVER store SAD after authorization** — this is absolute. Not even encrypted SAD.
- Disk-level/partition-level encryption (e.g., BitLocker, LUKS) no longer satisfies 3.5.1 for non-removable storage. Must use database-level, column-level, or file-level encryption.
- Tokenization is the preferred approach as it removes systems from scope.

---

## Requirement 4: Protect CHD During Transmission

**Goal:** Encrypt CHD during transmission to prevent interception.

### Sub-Requirements

| ID | Requirement | v4.0 Change |
|---|---|---|
| 4.1.1 | Policies documented | Clarified |
| 4.1.2 | Roles defined | Clarified |
| 4.2.1 | Strong cryptography for transmission over open/public networks | Updated — includes internal networks |
| 4.2.1.1 | Trusted keys and certificates used | Updated |
| 4.2.1.2 | Wireless transmission encryption | Updated |
| 4.2.2 | PAN secured when sent via end-user messaging | Updated |

### Key Changes in v4.0

- PAN must be encrypted during transmission over ALL networks, not just public/open networks. This is a significant expansion.
- Only TLS 1.2+ is acceptable. SSL and TLS 1.0/1.1 are explicitly prohibited.

---

## Requirement 5: Protect from Malicious Software

**Goal:** Deploy and maintain anti-malware defenses.

### Sub-Requirements

| ID | Requirement | v4.0 Change |
|---|---|---|
| 5.1.1 | Policies documented | Clarified |
| 5.1.2 | Roles defined | Clarified |
| 5.2.1 | Anti-malware deployed on all applicable systems | Updated |
| 5.2.2 | Anti-malware performs periodic and real-time scans | Updated |
| 5.2.3 | Systems not commonly affected by malware periodically evaluated | Updated |
| 5.2.3.1 | Frequency of periodic evaluations via targeted risk analysis | **New** |
| 5.3.1 | Anti-malware solutions kept current | Updated |
| 5.3.2 | Scans performed and definitions current | Updated |
| 5.3.3 | Removable media scanned automatically | **New (was future-dated, now mandatory)** |
| 5.3.4 | Anti-malware logs enabled and retained | Updated |
| 5.3.5 | Anti-malware cannot be disabled without authorization | Updated |
| 5.4.1 | Anti-phishing mechanisms deployed | **New (was future-dated, now mandatory)** |

### Key v4.0 Addition: Anti-Phishing (5.4.1)

Organizations must implement automated anti-phishing mechanisms. Examples include:
- Email gateway with anti-phishing filters
- DMARC enforcement (p=reject)
- URL filtering and link protection
- Phishing-resistant MFA (FIDO2/WebAuthn)
- Domain-based anti-spoofing controls

---

## Requirement 6: Secure Systems and Software

### Sub-Requirements (Key)

| ID | Requirement | v4.0 Change |
|---|---|---|
| 6.2.1 | Custom software developed securely | Updated |
| 6.2.2 | Developer training annually | Updated |
| 6.2.3 | Code review before release | Updated |
| 6.2.4 | OWASP Top 10 vulnerabilities addressed | Updated |
| 6.3.1 | Vulnerabilities identified and managed | Updated |
| 6.3.2 | Software inventory maintained | **New (was future-dated, now mandatory)** |
| 6.3.3 | Critical/high vulnerabilities patched | Updated |
| 6.4.1 | Public web apps protected | Updated |
| 6.4.2 | WAF in blocking mode for public web apps | **New (was future-dated, now mandatory)** |
| 6.4.3 | Payment page scripts managed and authorized | **New (was future-dated, now mandatory)** |
| 6.5.1 | Change management procedures | Updated |

### Critical v4.0 Changes

**6.4.3 — Payment Page Script Management:** All scripts loaded and executed on payment pages must be:
- Managed (inventory of all scripts maintained)
- Authorized (explicitly approved for use)
- Integrity assured (SRI hashes, CSP policies)
- Monitored for unauthorized changes

This directly addresses Magecart/web-skimming attacks.

---

## Requirement 7: Restrict Access

### Sub-Requirements (Key)

| ID | Requirement | v4.0 Change |
|---|---|---|
| 7.2.1 | Access control model defined | Updated |
| 7.2.2 | Access based on job classification | Updated |
| 7.2.3 | Privileges approved by authorized personnel | Updated |
| 7.2.4 | Accounts and privileges reviewed every 6 months | Updated |
| 7.2.5 | System accounts managed on least privilege | **New** |
| 7.2.5.1 | System account access reviewed periodically | **New (was future-dated, now mandatory)** |
| 7.2.6 | Query access to stored CHD restricted | Updated |

---

## Requirement 8: Identify and Authenticate

### Sub-Requirements (Key)

| ID | Requirement | v4.0 Change |
|---|---|---|
| 8.2.1 | Unique IDs for all users | Updated |
| 8.2.2 | No shared/generic accounts | Updated |
| 8.3.1 | All access authenticated | Updated |
| 8.3.4 | Account lockout (max 10 attempts, 30 min) | Updated |
| 8.3.6 | Minimum 12-character passwords | **Changed (was 7, now 12)** |
| 8.3.9 | Passwords changed every 90 days or continuous risk assessment | Updated |
| 8.4.1 | MFA for admin access to CDE | Updated |
| 8.4.2 | MFA for ALL access to CDE | **New (was future-dated, now mandatory)** |
| 8.4.3 | MFA for remote access | Updated |
| 8.5.1 | MFA replay-resistant | **New (was future-dated, now mandatory)** |
| 8.6.1 | System/service account interactive login managed | **New (was future-dated, now mandatory)** |
| 8.6.2 | No hard-coded passwords for system accounts | **New (was future-dated, now mandatory)** |
| 8.6.3 | Service account passwords rotated | **New (was future-dated, now mandatory)** |

### Critical v4.0 Change: MFA for All CDE Access (8.4.2)

MFA is now required for ALL access into the CDE — not just remote administrative access. This includes:
- All users accessing CDE systems
- Application access that reaches CDE databases
- Operator access to CDE infrastructure

---

## Requirement 9: Physical Access

### Sub-Requirements (Key)

| ID | Requirement | v4.0 Change |
|---|---|---|
| 9.2.1 | Facility entry controls | Updated |
| 9.3.1 | Physical access reviewed every 6 months | Updated |
| 9.3.2 | Visitor management | Updated |
| 9.4.1 | Media physically secured | Updated |
| 9.4.5 | Electronic media inventory | Updated |
| 9.4.6 | Hard-copy materials destroyed | Updated |
| 9.4.7 | Electronic media rendered unrecoverable | Updated |
| 9.5.1 | POI device protection | Updated |
| 9.5.1.2 | POI device inspection frequency via targeted risk analysis | **New** |

---

## Requirement 10: Logging and Monitoring

### Sub-Requirements (Key)

| ID | Requirement | v4.0 Change |
|---|---|---|
| 10.2.1 | Audit logs capture all access to CHD | Updated |
| 10.2.1.1-7 | Specific event types logged | Updated |
| 10.2.2 | Log details include required fields | Updated |
| 10.3.1-4 | Log protection (read access, modification, centralization, FIM) | Updated |
| 10.4.1 | Logs reviewed daily | Updated |
| 10.4.1.1 | Automated log review mechanisms | **New (was future-dated, now mandatory)** |
| 10.5.1 | 12-month retention (3 months online) | Updated |
| 10.6.1-3 | NTP synchronization | Updated |
| 10.7.1 | Critical security control failures detected | Updated |
| 10.7.2 | Failures of critical security controls detected and reported | **New (was future-dated, now mandatory)** |

### Critical v4.0 Change: Automated Log Review (10.4.1.1)

Manual log review alone is no longer sufficient. Organizations must deploy automated mechanisms (SIEM, log analytics) to perform log reviews. Manual review supplements but cannot replace automation.

---

## Requirement 11: Security Testing

### Sub-Requirements (Key)

| ID | Requirement | v4.0 Change |
|---|---|---|
| 11.2.1-2 | Wireless scanning quarterly | Updated |
| 11.3.1 | Internal vulnerability scans quarterly | Updated |
| 11.3.1.1 | All non-critical/high vulnerabilities managed | **New (was future-dated, now mandatory)** |
| 11.3.2 | External ASV scans quarterly | Updated |
| 11.4.1 | External pen test annually | Updated |
| 11.4.3 | Internal pen test annually | Updated |
| 11.4.5 | Segmentation testing annually (6 months for SP) | Updated |
| 11.4.7 | Multi-tenant SP pen testing | **New** |
| 11.5.1 | IDS/IPS deployed | Updated |
| 11.5.1.1 | IDS/IPS alerts for suspected compromise | **New (was future-dated, now mandatory)** |
| 11.5.2 | FIM deployed | Updated |
| 11.6.1 | Payment page tamper detection | **New (was future-dated, now mandatory)** |

### Critical v4.0 Change: Payment Page Tamper Detection (11.6.1)

A change-and-tamper-detection mechanism must be deployed on payment pages to alert personnel of unauthorized modifications. This directly supports 6.4.3 (script management) and protects against web-skimming attacks.

---

## Requirement 12: Policies and Programs

### Sub-Requirements (Key)

| ID | Requirement | v4.0 Change |
|---|---|---|
| 12.1.1 | Security policy established | Updated |
| 12.1.2 | Roles and responsibilities defined | Updated |
| 12.2.1 | Acceptable use policies | Updated |
| 12.3.1 | Targeted risk analysis for each requirement | **New (was future-dated, now mandatory)** |
| 12.3.2 | Customized approach risk analysis | **New** |
| 12.4.1 | Executive responsibility for CHD protection | Updated |
| 12.4.2 | Quarterly operations reviews (SP) | Updated |
| 12.5.1 | PCI DSS scope documented annually | Updated |
| 12.5.2 | Scope documented upon significant changes | **New** |
| 12.6.1 | Security awareness program | Updated |
| 12.6.3 | Training upon hire and annually | Updated |
| 12.6.3.1 | Phishing/social engineering in training | **New (was future-dated, now mandatory)** |
| 12.8.1-5 | TPSP management | Updated |
| 12.10.1 | Incident response plan | Updated |
| 12.10.2 | IRP tested annually | Updated |
| 12.10.4 | IR personnel trained | Updated |
| 12.10.5 | IRP includes monitoring alerts | Updated |
| 12.10.7 | Response to unexpected stored PAN | **New (was future-dated, now mandatory)** |
