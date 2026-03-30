---
name: infrastructure-compliance-auditor
description: >
  Cross-cutting infrastructure security audit skill that checks cloud
  infrastructure, DNS, TLS, endpoints, access control, network security,
  containers, CI/CD pipelines, secrets management, logging, and physical
  security against ALL major compliance frameworks. Use for infrastructure
  audit, cloud security audit, infrastructure compliance, DNS security audit,
  TLS audit, endpoint security, access control audit, network security
  assessment, infrastructure security, cloud compliance, Vanta alternative,
  compliance automation, security posture assessment, hardware security keys,
  YubiKey compliance.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: compliance
  domain: infrastructure-security
  updated: 2026-03-31
  tags: [infrastructure-audit, cloud-security, dns, tls, compliance-automation]
---
# Infrastructure Compliance Auditor

Cross-cutting infrastructure security audit across ALL compliance frameworks. Replaces manual Vanta-style checks with deterministic, repeatable, evidence-generating infrastructure audits covering cloud, DNS, TLS, endpoints, access control, network, containers, CI/CD, secrets, logging, and physical security.

---

## Table of Contents

- [Trigger Phrases](#trigger-phrases)
- [Quick Start](#quick-start)
- [Tools](#tools)
- [Audit Domains](#audit-domains)
  - [1. Cloud Infrastructure Security](#1-cloud-infrastructure-security)
  - [2. DNS Security](#2-dns-security)
  - [3. TLS/SSL Security](#3-tlsssl-security)
  - [4. Endpoint Security](#4-endpoint-security)
  - [5. Access Control and Authentication](#5-access-control-and-authentication)
  - [6. Network Security](#6-network-security)
  - [7. Container and Kubernetes Security](#7-container-and-kubernetes-security)
  - [8. CI/CD Pipeline Security](#8-cicd-pipeline-security)
  - [9. Secrets Management](#9-secrets-management)
  - [10. Logging and Monitoring](#10-logging-and-monitoring)
  - [11. Physical Security](#11-physical-security)
  - [12. Compliance Framework Mapping](#12-compliance-framework-mapping)
- [Workflows](#workflows)
- [Reference Guides](#reference-guides)
- [Validation Checkpoints](#validation-checkpoints)
- [Scoring Methodology](#scoring-methodology)

---

## Trigger Phrases

Use this skill when you hear:
- "infrastructure audit"
- "cloud security audit"
- "infrastructure compliance"
- "DNS security audit"
- "TLS audit"
- "endpoint security"
- "access control audit"
- "network security assessment"
- "infrastructure security"
- "cloud compliance"
- "Vanta alternative"
- "compliance automation"
- "security posture assessment"
- "hardware security keys"
- "YubiKey compliance"

---

## Quick Start

### Run Full Infrastructure Audit

```bash
python scripts/infra_audit_runner.py --config infrastructure.json --output audit_report.json
```

### Audit DNS Security for a Domain

```bash
python scripts/dns_security_checker.py --domain example.com --output dns_report.json
```

### Audit Access Controls

```bash
python scripts/access_control_auditor.py --config access_controls.json --output access_report.json
```

### Generate Compliance-Mapped Report

```bash
python scripts/infra_audit_runner.py --config infrastructure.json --frameworks soc2,iso27001,hipaa --format markdown --output compliance_report.md
```

---

## Tools

| Tool | Purpose | Input |
|------|---------|-------|
| `infra_audit_runner.py` | Full infrastructure audit across all 11 domains | JSON config describing infrastructure |
| `dns_security_checker.py` | DNS-specific security audit (SPF, DKIM, DMARC, DNSSEC, CAA, MTA-STS) | Domain name |
| `access_control_auditor.py` | Access control, MFA, SSO, PAM, RBAC audit | JSON config describing access controls |

---

## Audit Domains

### 1. Cloud Infrastructure Security

#### AWS Security Audit Checklist

**IAM Policies and Roles**

| Check ID | Control | Severity | Frameworks |
|----------|---------|----------|------------|
| AWS-IAM-001 | Root account has MFA enabled (hardware MFA preferred) | Critical | SOC 2 CC6.1, ISO 27001 A.9.2.1, PCI-DSS 8.3, NIST CSF PR.AC-1, HIPAA 164.312(d), FedRAMP AC-2 |
| AWS-IAM-002 | Root account has no access keys | Critical | SOC 2 CC6.1, ISO 27001 A.9.2.3, PCI-DSS 2.1, NIST CSF PR.AC-4 |
| AWS-IAM-003 | No IAM policies with `"Effect": "Allow", "Action": "*", "Resource": "*"` | Critical | SOC 2 CC6.3, ISO 27001 A.9.4.1, PCI-DSS 7.1, NIST CSF PR.AC-4 |
| AWS-IAM-004 | All IAM users have MFA enabled | High | SOC 2 CC6.1, ISO 27001 A.9.4.2, PCI-DSS 8.3, HIPAA 164.312(d) |
| AWS-IAM-005 | IAM password policy enforces minimum 14 characters | Medium | SOC 2 CC6.1, ISO 27001 A.9.4.3, PCI-DSS 8.2.3, NIST CSF PR.AC-1 |
| AWS-IAM-006 | IAM roles use external ID for cross-account access | Medium | SOC 2 CC6.3, ISO 27001 A.9.2.1 |
| AWS-IAM-007 | Unused IAM credentials (>90 days) are disabled | Medium | SOC 2 CC6.2, ISO 27001 A.9.2.6, PCI-DSS 8.1.4 |
| AWS-IAM-008 | IAM Access Analyzer is enabled in all regions | Medium | SOC 2 CC6.1, ISO 27001 A.9.2.5 |
| AWS-IAM-009 | No inline IAM policies (use managed policies) | Low | ISO 27001 A.9.2.2 |
| AWS-IAM-010 | IAM policy conditions restrict by source IP or VPC where possible | Low | SOC 2 CC6.6, NIST CSF PR.AC-3 |

**S3 Bucket Security**

| Check ID | Control | Severity | Frameworks |
|----------|---------|----------|------------|
| AWS-S3-001 | S3 Block Public Access enabled at account level | Critical | SOC 2 CC6.6, ISO 27001 A.13.1.1, PCI-DSS 1.3, HIPAA 164.312(e)(1), GDPR Art.32 |
| AWS-S3-002 | No S3 buckets with public ACLs or policies | Critical | SOC 2 CC6.6, ISO 27001 A.13.1.1, PCI-DSS 1.3, HIPAA 164.312(e)(1) |
| AWS-S3-003 | Server-side encryption enabled (SSE-S3 minimum, SSE-KMS preferred) | High | SOC 2 CC6.7, ISO 27001 A.10.1.1, PCI-DSS 3.4, HIPAA 164.312(a)(2)(iv), GDPR Art.32 |
| AWS-S3-004 | Versioning enabled on critical data buckets | Medium | SOC 2 CC6.7, ISO 27001 A.12.3.1 |
| AWS-S3-005 | Access logging enabled for all buckets | Medium | SOC 2 CC7.2, ISO 27001 A.12.4.1, PCI-DSS 10.2 |
| AWS-S3-006 | Lifecycle policies configured for log retention | Low | SOC 2 CC7.2, ISO 27001 A.12.4.1 |
| AWS-S3-007 | MFA Delete enabled for critical buckets | Medium | SOC 2 CC6.7, ISO 27001 A.12.3.1 |
| AWS-S3-008 | S3 Object Lock enabled for compliance data (WORM) | Medium | SEC Rule 17a-4, HIPAA 164.312(c)(1) |

**VPC Configuration**

| Check ID | Control | Severity | Frameworks |
|----------|---------|----------|------------|
| AWS-VPC-001 | VPC Flow Logs enabled for all VPCs | High | SOC 2 CC7.2, ISO 27001 A.12.4.1, PCI-DSS 10.2, NIST CSF DE.CM-1 |
| AWS-VPC-002 | Default security group restricts all inbound/outbound | High | SOC 2 CC6.6, ISO 27001 A.13.1.1, PCI-DSS 1.2 |
| AWS-VPC-003 | No security groups allow 0.0.0.0/0 on SSH (22) or RDP (3389) | Critical | SOC 2 CC6.6, ISO 27001 A.13.1.1, PCI-DSS 1.3, NIST CSF PR.AC-5 |
| AWS-VPC-004 | Private subnets used for databases and application tiers | High | SOC 2 CC6.6, ISO 27001 A.13.1.3, PCI-DSS 1.3 |
| AWS-VPC-005 | NACLs configured as additional defense layer | Medium | SOC 2 CC6.6, PCI-DSS 1.2 |
| AWS-VPC-006 | VPC endpoints used for AWS service access (avoid public internet) | Medium | SOC 2 CC6.6, ISO 27001 A.13.1.1 |
| AWS-VPC-007 | Transit Gateway or VPC Peering uses non-overlapping CIDRs | Low | ISO 27001 A.13.1.1 |

**RDS Security**

| Check ID | Control | Severity | Frameworks |
|----------|---------|----------|------------|
| AWS-RDS-001 | Encryption at rest enabled (KMS) | High | SOC 2 CC6.7, ISO 27001 A.10.1.1, PCI-DSS 3.4, HIPAA 164.312(a)(2)(iv) |
| AWS-RDS-002 | SSL/TLS connections enforced (`rds.force_ssl = 1`) | High | SOC 2 CC6.7, ISO 27001 A.10.1.1, PCI-DSS 4.1 |
| AWS-RDS-003 | Automated backups enabled with minimum 7-day retention | Medium | SOC 2 CC6.7, ISO 27001 A.12.3.1, HIPAA 164.308(a)(7)(ii)(A) |
| AWS-RDS-004 | Multi-AZ deployment for production databases | Medium | SOC 2 A1.2, ISO 27001 A.17.1.1 |
| AWS-RDS-005 | Database instances not publicly accessible | Critical | SOC 2 CC6.6, PCI-DSS 1.3 |
| AWS-RDS-006 | Enhanced monitoring enabled | Low | SOC 2 CC7.2, ISO 27001 A.12.4.1 |
| AWS-RDS-007 | Deletion protection enabled for production instances | Medium | SOC 2 CC6.7 |

**CloudTrail and Monitoring**

| Check ID | Control | Severity | Frameworks |
|----------|---------|----------|------------|
| AWS-CT-001 | CloudTrail enabled in all regions | Critical | SOC 2 CC7.2, ISO 27001 A.12.4.1, PCI-DSS 10.1, HIPAA 164.312(b), NIST CSF DE.CM-1, FedRAMP AU-2 |
| AWS-CT-002 | CloudTrail log file validation enabled | High | SOC 2 CC7.2, ISO 27001 A.12.4.3, PCI-DSS 10.5 |
| AWS-CT-003 | CloudTrail logs delivered to S3 with encryption | High | SOC 2 CC7.2, ISO 27001 A.12.4.1, PCI-DSS 10.5 |
| AWS-CT-004 | CloudTrail integrated with CloudWatch Logs | Medium | SOC 2 CC7.2, ISO 27001 A.12.4.1 |
| AWS-CT-005 | GuardDuty enabled in all regions | High | SOC 2 CC7.2, NIST CSF DE.CM-1 |
| AWS-CT-006 | Security Hub enabled with CIS AWS Foundations Benchmark | Medium | SOC 2 CC7.2, NIST CSF DE.CM-1 |
| AWS-CT-007 | AWS Config enabled with required rules | High | SOC 2 CC7.2, ISO 27001 A.12.4.1, NIST CSF DE.CM-1, FedRAMP CM-8 |

**KMS and Encryption**

| Check ID | Control | Severity | Frameworks |
|----------|---------|----------|------------|
| AWS-KMS-001 | Customer-managed KMS keys used for sensitive data | High | SOC 2 CC6.7, ISO 27001 A.10.1.2, PCI-DSS 3.5 |
| AWS-KMS-002 | KMS key rotation enabled (annual automatic rotation) | Medium | SOC 2 CC6.7, ISO 27001 A.10.1.2, PCI-DSS 3.6.4 |
| AWS-KMS-003 | KMS key policies follow least privilege | Medium | SOC 2 CC6.3, ISO 27001 A.10.1.2 |
| AWS-KMS-004 | KMS keys have alias and description for identification | Low | ISO 27001 A.10.1.2 |

**Lambda and Serverless Security**

| Check ID | Control | Severity | Frameworks |
|----------|---------|----------|------------|
| AWS-LAM-001 | Lambda functions use IAM roles with least privilege | High | SOC 2 CC6.3, ISO 27001 A.9.4.1 |
| AWS-LAM-002 | Lambda functions do not store secrets in environment variables (use Secrets Manager) | High | SOC 2 CC6.7, PCI-DSS 3.4 |
| AWS-LAM-003 | Lambda functions deployed in VPC when accessing private resources | Medium | SOC 2 CC6.6, ISO 27001 A.13.1.1 |
| AWS-LAM-004 | Lambda function code is signed | Medium | SOC 2 CC7.1 |
| AWS-LAM-005 | Dead letter queues configured for async invocations | Low | SOC 2 A1.2 |

**EKS/ECS Container Security**

| Check ID | Control | Severity | Frameworks |
|----------|---------|----------|------------|
| AWS-EKS-001 | EKS cluster endpoint not publicly accessible (or restricted by CIDR) | High | SOC 2 CC6.6, ISO 27001 A.13.1.1 |
| AWS-EKS-002 | EKS control plane logging enabled (api, audit, authenticator) | High | SOC 2 CC7.2, ISO 27001 A.12.4.1 |
| AWS-EKS-003 | EKS managed node groups use latest AMI | Medium | SOC 2 CC7.1 |
| AWS-EKS-004 | ECS tasks use awsvpc networking mode | Medium | SOC 2 CC6.6 |
| AWS-EKS-005 | ECR image scanning enabled on push | High | SOC 2 CC7.1, NIST CSF PR.IP-12 |

#### Azure Security Audit Checklist

**Azure AD / Entra ID**

| Check ID | Control | Severity | Frameworks |
|----------|---------|----------|------------|
| AZ-AD-001 | Global Administrator accounts have MFA enforced | Critical | SOC 2 CC6.1, ISO 27001 A.9.2.1, PCI-DSS 8.3 |
| AZ-AD-002 | Maximum 5 Global Administrator accounts | High | SOC 2 CC6.1, ISO 27001 A.9.2.3 |
| AZ-AD-003 | Conditional Access Policies configured | High | SOC 2 CC6.1, ISO 27001 A.9.4.2 |
| AZ-AD-004 | Security Defaults enabled (if no Conditional Access) | High | SOC 2 CC6.1 |
| AZ-AD-005 | Privileged Identity Management (PIM) enabled for admin roles | High | SOC 2 CC6.1, ISO 27001 A.9.2.3 |
| AZ-AD-006 | Guest user access restricted | Medium | SOC 2 CC6.1, ISO 27001 A.9.2.2 |
| AZ-AD-007 | Sign-in risk policy configured (requires P2) | Medium | SOC 2 CC6.1 |

**Azure Network Security**

| Check ID | Control | Severity | Frameworks |
|----------|---------|----------|------------|
| AZ-NET-001 | NSG rules follow least privilege (no allow-all inbound) | High | SOC 2 CC6.6, ISO 27001 A.13.1.1, PCI-DSS 1.2 |
| AZ-NET-002 | Azure Firewall or third-party NVA deployed | Medium | SOC 2 CC6.6, PCI-DSS 1.1 |
| AZ-NET-003 | DDoS Protection Standard enabled for public IPs | Medium | SOC 2 A1.2, ISO 27001 A.13.1.1 |
| AZ-NET-004 | Private endpoints used for PaaS services | Medium | SOC 2 CC6.6, ISO 27001 A.13.1.1 |
| AZ-NET-005 | Network Watcher enabled in all regions | Medium | SOC 2 CC7.2, ISO 27001 A.12.4.1 |

**Azure Key Vault**

| Check ID | Control | Severity | Frameworks |
|----------|---------|----------|------------|
| AZ-KV-001 | Key Vault uses RBAC (not legacy access policies) | High | SOC 2 CC6.3, ISO 27001 A.10.1.2 |
| AZ-KV-002 | Soft delete and purge protection enabled | High | SOC 2 CC6.7, ISO 27001 A.10.1.2 |
| AZ-KV-003 | Key Vault diagnostic logging enabled | Medium | SOC 2 CC7.2, ISO 27001 A.12.4.1 |
| AZ-KV-004 | Key rotation policy configured | Medium | SOC 2 CC6.7, PCI-DSS 3.6.4 |
| AZ-KV-005 | Key Vault firewall enabled (restrict to VNet/IP) | Medium | SOC 2 CC6.6, ISO 27001 A.13.1.1 |

**Azure Monitoring**

| Check ID | Control | Severity | Frameworks |
|----------|---------|----------|------------|
| AZ-MON-001 | Azure Monitor activity log alerts configured | High | SOC 2 CC7.2, ISO 27001 A.12.4.1 |
| AZ-MON-002 | Microsoft Sentinel (SIEM) deployed | Medium | SOC 2 CC7.2, NIST CSF DE.AE-2 |
| AZ-MON-003 | Diagnostic settings enabled for all resources | Medium | SOC 2 CC7.2, ISO 27001 A.12.4.1 |
| AZ-MON-004 | Azure Policy assignments enforcing compliance | High | SOC 2 CC7.1, ISO 27001 A.18.2.2 |
| AZ-MON-005 | Microsoft Defender for Cloud enabled (all plans) | High | SOC 2 CC7.2, NIST CSF DE.CM-1 |

**Azure Storage Security**

| Check ID | Control | Severity | Frameworks |
|----------|---------|----------|------------|
| AZ-ST-001 | Storage accounts require HTTPS transfer | High | SOC 2 CC6.7, ISO 27001 A.10.1.1, PCI-DSS 4.1 |
| AZ-ST-002 | Storage account public access disabled | Critical | SOC 2 CC6.6, ISO 27001 A.13.1.1 |
| AZ-ST-003 | Storage accounts use customer-managed keys | Medium | SOC 2 CC6.7, PCI-DSS 3.5 |
| AZ-ST-004 | Shared Access Signatures (SAS) use short expiry | Medium | SOC 2 CC6.1, ISO 27001 A.9.4.2 |

**AKS Security**

| Check ID | Control | Severity | Frameworks |
|----------|---------|----------|------------|
| AZ-AKS-001 | AKS uses managed identity (not service principal) | High | SOC 2 CC6.1, ISO 27001 A.9.4.1 |
| AZ-AKS-002 | Azure Policy for AKS enabled | Medium | SOC 2 CC7.1 |
| AZ-AKS-003 | AKS API server authorized IP ranges configured | High | SOC 2 CC6.6, ISO 27001 A.13.1.1 |
| AZ-AKS-004 | AKS uses Azure CNI (not kubenet) for network policies | Medium | SOC 2 CC6.6 |

#### GCP Security Audit Checklist

**GCP IAM and Service Accounts**

| Check ID | Control | Severity | Frameworks |
|----------|---------|----------|------------|
| GCP-IAM-001 | Organization-level IAM policies use groups, not individual users | High | SOC 2 CC6.1, ISO 27001 A.9.2.2 |
| GCP-IAM-002 | Service accounts do not have Owner/Editor roles | Critical | SOC 2 CC6.3, ISO 27001 A.9.4.1 |
| GCP-IAM-003 | User-managed service account keys rotate every 90 days | High | SOC 2 CC6.1, PCI-DSS 3.6.4 |
| GCP-IAM-004 | Domain-restricted sharing enabled via Organization Policy | Medium | SOC 2 CC6.1, ISO 27001 A.9.2.2 |
| GCP-IAM-005 | Workload Identity used for GKE (no service account keys) | High | SOC 2 CC6.1, ISO 27001 A.9.4.1 |

**GCP VPC and Network**

| Check ID | Control | Severity | Frameworks |
|----------|---------|----------|------------|
| GCP-VPC-001 | VPC Service Controls configured for sensitive projects | High | SOC 2 CC6.6, ISO 27001 A.13.1.3 |
| GCP-VPC-002 | Cloud Armor WAF rules protect public-facing services | High | SOC 2 CC6.6, ISO 27001 A.13.1.1 |
| GCP-VPC-003 | VPC Flow Logs enabled for all subnets | High | SOC 2 CC7.2, ISO 27001 A.12.4.1 |
| GCP-VPC-004 | Private Google Access enabled for private subnets | Medium | SOC 2 CC6.6 |
| GCP-VPC-005 | Firewall rules do not allow 0.0.0.0/0 on SSH/RDP | Critical | SOC 2 CC6.6, PCI-DSS 1.3 |

**GCP Security Services**

| Check ID | Control | Severity | Frameworks |
|----------|---------|----------|------------|
| GCP-SEC-001 | Security Command Center (SCC) enabled (Premium) | High | SOC 2 CC7.2, NIST CSF DE.CM-1 |
| GCP-SEC-002 | Cloud KMS keys have rotation scheduled | Medium | SOC 2 CC6.7, PCI-DSS 3.6.4 |
| GCP-SEC-003 | Cloud Audit Logs enabled for all services | High | SOC 2 CC7.2, ISO 27001 A.12.4.1 |
| GCP-SEC-004 | Binary Authorization enabled for GKE | Medium | SOC 2 CC7.1 |
| GCP-SEC-005 | Organization Policy Service enforces constraints | High | SOC 2 CC7.1, ISO 27001 A.18.2.2 |

**GKE Security**

| Check ID | Control | Severity | Frameworks |
|----------|---------|----------|------------|
| GCP-GKE-001 | GKE uses private cluster (no public endpoint) or authorized networks | High | SOC 2 CC6.6, ISO 27001 A.13.1.1 |
| GCP-GKE-002 | GKE Shielded Nodes enabled | Medium | SOC 2 CC6.7 |
| GCP-GKE-003 | GKE node auto-upgrade enabled | Medium | SOC 2 CC7.1, NIST CSF PR.IP-12 |
| GCP-GKE-004 | GKE workload identity enabled (no node service account keys) | High | SOC 2 CC6.1 |
| GCP-GKE-005 | Container-Optimized OS used for nodes | Medium | SOC 2 CC7.1 |

---

### 2. DNS Security

#### Email Authentication Chain

SPF, DKIM, and DMARC form a layered email authentication system. ALL three must be configured correctly for effective protection against spoofing and phishing.

**SPF (Sender Policy Framework)**

| Check ID | Control | Severity | Frameworks |
|----------|---------|----------|------------|
| DNS-SPF-001 | SPF record exists for primary domain | High | SOC 2 CC6.6, ISO 27001 A.13.2.1, NIST CSF PR.AC-3 |
| DNS-SPF-002 | SPF record uses `-all` (hard fail) not `~all` (soft fail) | High | SOC 2 CC6.6, ISO 27001 A.13.2.1 |
| DNS-SPF-003 | SPF record has fewer than 10 DNS lookups (RFC 7208 limit) | Medium | SOC 2 CC6.6 |
| DNS-SPF-004 | SPF record does not use `+all` (permits all senders) | Critical | SOC 2 CC6.6, ISO 27001 A.13.2.1 |
| DNS-SPF-005 | Non-sending domains have `v=spf1 -all` to prevent spoofing | Medium | ISO 27001 A.13.2.1 |
| DNS-SPF-006 | SPF record avoids deprecated PTR mechanism | Low | RFC 7208 |
| DNS-SPF-007 | SPF flattening used if approaching lookup limit | Low | Best practice |

SPF syntax reference:
```
v=spf1 include:_spf.google.com include:sendgrid.net ip4:203.0.113.0/24 -all
```

**Key rules:**
- Maximum 10 DNS lookups (include, a, mx, ptr, exists, redirect each count as 1)
- `ip4` and `ip6` mechanisms do NOT count toward the 10-lookup limit
- Nested includes count toward the limit
- Record must be a single TXT record (no multiple SPF records)
- Maximum 255 characters per DNS string (use string concatenation for longer records)

**DKIM (DomainKeys Identified Mail)**

| Check ID | Control | Severity | Frameworks |
|----------|---------|----------|------------|
| DNS-DKIM-001 | DKIM record exists for all sending domains | High | SOC 2 CC6.6, ISO 27001 A.13.2.1 |
| DNS-DKIM-002 | DKIM key is minimum 2048-bit RSA | High | SOC 2 CC6.7, ISO 27001 A.10.1.1 |
| DNS-DKIM-003 | DKIM keys rotate every 6-12 months | Medium | SOC 2 CC6.7, ISO 27001 A.10.1.2 |
| DNS-DKIM-004 | Multiple DKIM selectors for different sending services | Low | Best practice |
| DNS-DKIM-005 | DKIM testing mode (`t=y`) removed for production domains | Medium | SOC 2 CC6.6 |

DKIM record format:
```
selector._domainkey.example.com IN TXT "v=DKIM1; k=rsa; p=MIIBIjANBgkq..."
```

**DMARC (Domain-based Message Authentication, Reporting, and Conformance)**

| Check ID | Control | Severity | Frameworks |
|----------|---------|----------|------------|
| DNS-DMARC-001 | DMARC record exists at `_dmarc.example.com` | High | SOC 2 CC6.6, ISO 27001 A.13.2.1, NIST CSF PR.AC-3 |
| DNS-DMARC-002 | DMARC policy is `p=reject` (maximum enforcement) | High | SOC 2 CC6.6, ISO 27001 A.13.2.1 |
| DNS-DMARC-003 | DMARC `rua` (aggregate reporting) tag configured | Medium | SOC 2 CC7.2, ISO 27001 A.12.4.1 |
| DNS-DMARC-004 | DMARC `ruf` (forensic reporting) tag configured | Low | SOC 2 CC7.2 |
| DNS-DMARC-005 | DMARC subdomain policy `sp=reject` configured | Medium | ISO 27001 A.13.2.1 |
| DNS-DMARC-006 | DMARC alignment modes — `adkim=s` and `aspf=s` (strict) preferred | Medium | SOC 2 CC6.6 |
| DNS-DMARC-007 | DMARC `pct=100` (applies to all messages) | Medium | SOC 2 CC6.6 |

DMARC record format:
```
_dmarc.example.com IN TXT "v=DMARC1; p=reject; sp=reject; adkim=s; aspf=s; rua=mailto:dmarc-agg@example.com; ruf=mailto:dmarc-forensic@example.com; pct=100"
```

**DMARC rollout strategy** (avoid disrupting legitimate email):
1. `p=none; rua=mailto:...` — Monitor for 2-4 weeks
2. `p=quarantine; pct=10` — Quarantine 10% of failing messages
3. `p=quarantine; pct=50` — Increase gradually
4. `p=quarantine; pct=100` — Full quarantine
5. `p=reject; pct=100` — Full enforcement

**DNSSEC**

| Check ID | Control | Severity | Frameworks |
|----------|---------|----------|------------|
| DNS-SEC-001 | DNSSEC signing enabled for domain | High | SOC 2 CC6.6, ISO 27001 A.13.1.1, NIST CSF PR.DS-2 |
| DNS-SEC-002 | DS record published in parent zone | High | SOC 2 CC6.6, ISO 27001 A.13.1.1 |
| DNS-SEC-003 | DNSSEC algorithm is ECDSAP256SHA256 (13) or newer | Medium | SOC 2 CC6.7 |
| DNS-SEC-004 | DNSSEC key rotation schedule documented | Medium | SOC 2 CC6.7, ISO 27001 A.10.1.2 |

**CAA (Certificate Authority Authorization)**

| Check ID | Control | Severity | Frameworks |
|----------|---------|----------|------------|
| DNS-CAA-001 | CAA record exists restricting certificate issuance | High | SOC 2 CC6.7, ISO 27001 A.10.1.2 |
| DNS-CAA-002 | CAA `iodef` tag configured for certificate issuance notifications | Medium | SOC 2 CC7.2 |
| DNS-CAA-003 | Only authorized CAs listed in CAA record | High | SOC 2 CC6.7 |

CAA record format:
```
example.com IN CAA 0 issue "letsencrypt.org"
example.com IN CAA 0 issue "digicert.com"
example.com IN CAA 0 issuewild "letsencrypt.org"
example.com IN CAA 0 iodef "mailto:security@example.com"
```

**MTA-STS and TLS-RPT**

| Check ID | Control | Severity | Frameworks |
|----------|---------|----------|------------|
| DNS-MTA-001 | MTA-STS policy published at `/.well-known/mta-sts.txt` | Medium | ISO 27001 A.13.2.1 |
| DNS-MTA-002 | MTA-STS DNS record `_mta-sts.example.com` exists | Medium | ISO 27001 A.13.2.1 |
| DNS-MTA-003 | MTA-STS mode is `enforce` (not `testing` or `none`) | Medium | ISO 27001 A.13.2.1 |
| DNS-MTA-004 | TLS-RPT record `_smtp._tls.example.com` configured | Low | ISO 27001 A.12.4.1 |

MTA-STS policy (at `https://mta-sts.example.com/.well-known/mta-sts.txt`):
```
version: STSv1
mode: enforce
mx: mail.example.com
mx: *.example.com
max_age: 604800
```

**Domain Security**

| Check ID | Control | Severity | Frameworks |
|----------|---------|----------|------------|
| DNS-DOM-001 | Registrar lock enabled (clientTransferProhibited) | High | SOC 2 CC6.7, ISO 27001 A.13.1.1 |
| DNS-DOM-002 | WHOIS privacy enabled | Low | GDPR Art.5 |
| DNS-DOM-003 | 2FA enabled on domain registrar account | Critical | SOC 2 CC6.1, ISO 27001 A.9.4.2 |
| DNS-DOM-004 | Domain expiration monitored (>60 days before expiry) | Medium | SOC 2 A1.2 |
| DNS-DOM-005 | Subdomain inventory maintained (prevent subdomain takeover) | High | SOC 2 CC6.6, ISO 27001 A.13.1.1 |
| DNS-DOM-006 | Dangling DNS records (CNAME to deprovisioned services) monitored | High | SOC 2 CC6.6 |
| DNS-DOM-007 | DNS monitoring alerts configured for unauthorized changes | Medium | SOC 2 CC7.2, ISO 27001 A.12.4.1 |

---

### 3. TLS/SSL Security

#### Certificate Management

| Check ID | Control | Severity | Frameworks |
|----------|---------|----------|------------|
| TLS-CERT-001 | Certificates issued by trusted CA (not self-signed for public services) | High | SOC 2 CC6.7, ISO 27001 A.10.1.1, PCI-DSS 4.1 |
| TLS-CERT-002 | Automated certificate renewal via ACME (Let's Encrypt, ZeroSSL) | Medium | SOC 2 CC6.7 |
| TLS-CERT-003 | Certificate expiration monitored (alert at 30, 14, 7 days) | High | SOC 2 A1.2, ISO 27001 A.10.1.2 |
| TLS-CERT-004 | Certificate Transparency (CT) log monitoring enabled | Medium | SOC 2 CC7.2 |
| TLS-CERT-005 | No wildcard certificates for high-security domains | Medium | SOC 2 CC6.7, PCI-DSS 4.1 |
| TLS-CERT-006 | Certificate validity period 90 days maximum (Let's Encrypt standard) | Low | Best practice |
| TLS-CERT-007 | OCSP stapling enabled | Medium | SOC 2 CC6.7 |
| TLS-CERT-008 | Certificate pinning only for mobile apps (not web — risk of bricking) | Info | Best practice |

#### Protocol and Cipher Configuration

| Check ID | Control | Severity | Frameworks |
|----------|---------|----------|------------|
| TLS-PROTO-001 | TLS 1.2 minimum (TLS 1.0 and 1.1 disabled) | Critical | SOC 2 CC6.7, ISO 27001 A.10.1.1, PCI-DSS 4.1, NIST CSF PR.DS-2, HIPAA 164.312(e)(1) |
| TLS-PROTO-002 | TLS 1.3 preferred where supported | Medium | SOC 2 CC6.7, NIST CSF PR.DS-2 |
| TLS-PROTO-003 | SSL 2.0 and 3.0 disabled | Critical | PCI-DSS 4.1, NIST CSF PR.DS-2 |
| TLS-CIPHER-001 | Forward secrecy enabled (ECDHE or DHE key exchange) | High | SOC 2 CC6.7, ISO 27001 A.10.1.1, PCI-DSS 4.1 |
| TLS-CIPHER-002 | AEAD cipher suites only (GCM, ChaCha20-Poly1305) | High | SOC 2 CC6.7, PCI-DSS 4.1 |
| TLS-CIPHER-003 | No RC4, 3DES, DES, NULL, or EXPORT ciphers | Critical | PCI-DSS 4.1, NIST CSF PR.DS-2 |
| TLS-CIPHER-004 | No CBC mode ciphers (BEAST/POODLE vulnerability) | High | PCI-DSS 4.1 |
| TLS-CIPHER-005 | RSA key exchange disabled (no forward secrecy) | Medium | SOC 2 CC6.7 |

**Recommended TLS 1.2 cipher suites (in order):**
```
TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384
TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384
TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256
TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256
TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256
TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256
```

**TLS 1.3 cipher suites (always use all three):**
```
TLS_AES_256_GCM_SHA384
TLS_CHACHA20_POLY1305_SHA256
TLS_AES_128_GCM_SHA256
```

#### HTTP Security Headers

| Check ID | Control | Severity | Frameworks |
|----------|---------|----------|------------|
| TLS-HSTS-001 | HSTS enabled with `max-age` >= 31536000 (1 year) | High | SOC 2 CC6.7, ISO 27001 A.10.1.1, PCI-DSS 4.1, NIST CSF PR.DS-2 |
| TLS-HSTS-002 | HSTS `includeSubDomains` directive set | High | SOC 2 CC6.7 |
| TLS-HSTS-003 | HSTS preload submitted to hstspreload.org | Medium | SOC 2 CC6.7 |
| TLS-HSTS-004 | HTTP to HTTPS redirect configured (301 permanent) | High | SOC 2 CC6.7, PCI-DSS 4.1 |

#### Internal TLS

| Check ID | Control | Severity | Frameworks |
|----------|---------|----------|------------|
| TLS-INT-001 | mTLS configured for service-to-service communication | High | SOC 2 CC6.7, ISO 27001 A.13.1.1, PCI-DSS 4.1 (if CDE) |
| TLS-INT-002 | Internal PKI with short-lived certificates (24h-7d) | Medium | SOC 2 CC6.7, ISO 27001 A.10.1.2 |
| TLS-INT-003 | Service mesh (Istio/Linkerd) manages mTLS transparently | Medium | SOC 2 CC6.7 |
| TLS-INT-004 | Database connections use TLS | High | SOC 2 CC6.7, PCI-DSS 4.1, HIPAA 164.312(e)(1) |

---

### 4. Endpoint Security

#### Mobile Device Management (MDM)

| Check ID | Control | Severity | Frameworks |
|----------|---------|----------|------------|
| EP-MDM-001 | MDM solution deployed (Jamf, Intune, Kandji) | High | SOC 2 CC6.7, ISO 27001 A.6.2.1, HIPAA 164.310(d)(1), NIST CSF PR.AC-3 |
| EP-MDM-002 | All corporate devices enrolled in MDM | High | SOC 2 CC6.7, ISO 27001 A.6.2.1 |
| EP-MDM-003 | MDM compliance policies enforced (auto-remediate non-compliant devices) | Medium | SOC 2 CC6.7 |
| EP-MDM-004 | MDM reports integrated into security dashboard | Low | SOC 2 CC7.2 |

#### Disk Encryption

| Check ID | Control | Severity | Frameworks |
|----------|---------|----------|------------|
| EP-ENC-001 | Full disk encryption enabled on all endpoints (FileVault/BitLocker/LUKS) | Critical | SOC 2 CC6.7, ISO 27001 A.10.1.1, PCI-DSS 3.4, HIPAA 164.312(a)(2)(iv), GDPR Art.32, NIST CSF PR.DS-1 |
| EP-ENC-002 | Encryption recovery keys escrowed in MDM or central key management | High | SOC 2 CC6.7, ISO 27001 A.10.1.2 |
| EP-ENC-003 | Encryption status verified on every endpoint via MDM | Medium | SOC 2 CC6.7 |
| EP-ENC-004 | Mobile devices have device encryption enabled | High | SOC 2 CC6.7, HIPAA 164.312(a)(2)(iv) |

#### Antivirus and EDR

| Check ID | Control | Severity | Frameworks |
|----------|---------|----------|------------|
| EP-AV-001 | EDR solution deployed on all endpoints (CrowdStrike, SentinelOne, Defender for Endpoint) | High | SOC 2 CC6.8, ISO 27001 A.12.2.1, PCI-DSS 5.1, HIPAA 164.308(a)(5)(ii)(B), NIST CSF DE.CM-4 |
| EP-AV-002 | Real-time protection enabled and cannot be disabled by users | High | SOC 2 CC6.8, PCI-DSS 5.1 |
| EP-AV-003 | Definitions updated automatically (maximum 24h staleness) | Medium | SOC 2 CC6.8, PCI-DSS 5.2 |
| EP-AV-004 | EDR telemetry centralized for threat hunting | Medium | SOC 2 CC7.2, NIST CSF DE.AE-2 |
| EP-AV-005 | Automatic quarantine/isolation for critical threats | Medium | SOC 2 CC6.8, NIST CSF RS.MI-1 |

#### OS Patch Management

| Check ID | Control | Severity | Frameworks |
|----------|---------|----------|------------|
| EP-PATCH-001 | Critical patches applied within 24 hours | Critical | SOC 2 CC7.1, ISO 27001 A.12.6.1, PCI-DSS 6.2, NIST CSF PR.IP-12 |
| EP-PATCH-002 | High patches applied within 72 hours | High | SOC 2 CC7.1, ISO 27001 A.12.6.1, PCI-DSS 6.2 |
| EP-PATCH-003 | Medium patches applied within 7 days | Medium | SOC 2 CC7.1, ISO 27001 A.12.6.1 |
| EP-PATCH-004 | Low patches applied within 30 days | Low | SOC 2 CC7.1, ISO 27001 A.12.6.1 |
| EP-PATCH-005 | Patch compliance reported weekly | Medium | SOC 2 CC7.1, ISO 27001 A.12.6.1 |
| EP-PATCH-006 | Emergency patch process documented and tested | Medium | SOC 2 CC7.1, NIST CSF RS.MI-3 |

#### Additional Endpoint Controls

| Check ID | Control | Severity | Frameworks |
|----------|---------|----------|------------|
| EP-LOCK-001 | Screen lock after 5 minutes of inactivity | Medium | SOC 2 CC6.1, ISO 27001 A.11.2.8, PCI-DSS 8.1.8, HIPAA 164.310(b) |
| EP-USB-001 | USB storage devices blocked or controlled via MDM | Medium | SOC 2 CC6.7, ISO 27001 A.8.3.1, PCI-DSS 9.7 |
| EP-BRW-001 | Browser extension allow-listing enforced | Medium | SOC 2 CC6.8, ISO 27001 A.12.2.1 |
| EP-BRW-002 | Safe browsing / web filtering enabled | Low | SOC 2 CC6.8, ISO 27001 A.13.1.1 |
| EP-WIPE-001 | Remote wipe capability verified for all corporate devices | High | SOC 2 CC6.7, ISO 27001 A.6.2.1, HIPAA 164.310(d)(2)(iii) |
| EP-BYOD-001 | BYOD policy documented and enforced via MDM container | Medium | SOC 2 CC6.7, ISO 27001 A.6.2.1, GDPR Art.32 |
| EP-FW-001 | Host-based firewall enabled on all endpoints | Medium | SOC 2 CC6.6, ISO 27001 A.13.1.1, PCI-DSS 1.4 |

---

### 5. Access Control and Authentication

#### Identity Provider (IdP) Configuration

| Check ID | Control | Severity | Frameworks |
|----------|---------|----------|------------|
| AC-IDP-001 | Centralized IdP deployed (Okta, Azure AD/Entra ID, Google Workspace) | High | SOC 2 CC6.1, ISO 27001 A.9.2.1, PCI-DSS 8.1, HIPAA 164.312(d), NIST CSF PR.AC-1, FedRAMP AC-2 |
| AC-IDP-002 | All applications integrated with IdP via SSO | High | SOC 2 CC6.1, ISO 27001 A.9.4.2 |
| AC-IDP-003 | IdP has admin MFA enforced (hardware key required for admin) | Critical | SOC 2 CC6.1, ISO 27001 A.9.4.2, PCI-DSS 8.3 |
| AC-IDP-004 | IdP audit logs exported to SIEM | Medium | SOC 2 CC7.2, ISO 27001 A.12.4.1 |

#### Single Sign-On (SSO)

| Check ID | Control | Severity | Frameworks |
|----------|---------|----------|------------|
| AC-SSO-001 | SSO implemented via SAML 2.0 or OIDC (no password-based SSO) | High | SOC 2 CC6.1, ISO 27001 A.9.4.2, NIST CSF PR.AC-1 |
| AC-SSO-002 | SSO session timeout configured (maximum 8 hours) | Medium | SOC 2 CC6.1, ISO 27001 A.9.4.2, PCI-DSS 8.1.8 |
| AC-SSO-003 | SSO enforced (local authentication disabled where possible) | High | SOC 2 CC6.1, ISO 27001 A.9.4.2 |
| AC-SSO-004 | SCIM provisioning enabled for automated user lifecycle | High | SOC 2 CC6.2, ISO 27001 A.9.2.1, NIST CSF PR.AC-1 |
| AC-SSO-005 | Deprovisioning triggers immediate SSO session revocation | High | SOC 2 CC6.2, ISO 27001 A.9.2.6 |

#### Multi-Factor Authentication (MFA)

| Check ID | Control | Severity | Frameworks |
|----------|---------|----------|------------|
| AC-MFA-001 | MFA enforced for ALL user accounts (no exceptions) | Critical | SOC 2 CC6.1, ISO 27001 A.9.4.2, PCI-DSS 8.3, HIPAA 164.312(d), NIST CSF PR.AC-7, GDPR Art.32, NIS2 Art.21, DORA Art.9, FedRAMP IA-2 |
| AC-MFA-002 | Phishing-resistant MFA (FIDO2/WebAuthn) required for privileged accounts | Critical | SOC 2 CC6.1, ISO 27001 A.9.4.2, NIST CSF PR.AC-7, FedRAMP IA-2(6) |
| AC-MFA-003 | SMS-based MFA prohibited (SIM swap vulnerability) | High | SOC 2 CC6.1, NIST CSF PR.AC-7 |
| AC-MFA-004 | TOTP (time-based one-time password) accepted as minimum MFA | Medium | SOC 2 CC6.1 |
| AC-MFA-005 | Hardware security keys (YubiKey 5 Series, Bio Series) deployed for all admins | High | SOC 2 CC6.1, ISO 27001 A.9.4.2, NIST CSF PR.AC-7 |
| AC-MFA-006 | MFA recovery process documented (not bypass, requires identity verification) | Medium | SOC 2 CC6.1, ISO 27001 A.9.2.4 |
| AC-MFA-007 | MFA enrollment status reported (100% coverage target) | Medium | SOC 2 CC6.1 |

**Hardware Security Key (YubiKey) Implementation:**

Enrollment process:
1. User registers primary YubiKey to IdP (Okta, Azure AD, Google Workspace)
2. User registers backup YubiKey (stored in secure location)
3. IdP policy updated to require FIDO2/WebAuthn for user
4. TOTP/push fallback disabled for privileged accounts

YubiKey policy requirements:
- Each user has minimum 2 registered keys (primary + backup)
- Backup key stored in secure, documented location
- PIN configured on YubiKey (FIDO2 user verification)
- Touch required for every authentication
- Bio Series (fingerprint) preferred for shared workstations
- Inventory of all issued keys maintained
- Lost key process: immediate revocation, identity reverification, new key issuance

IdP-specific configuration:
- **Okta:** Enroll YubiKey via FIDO2 (WebAuthn) factor, set Authentication Policy to require phishing-resistant MFA
- **Azure AD/Entra ID:** Configure FIDO2 security key in Authentication Methods, create Conditional Access policy requiring authentication strength "Phishing-resistant MFA"
- **Google Workspace:** Enroll security key in 2-Step Verification, enable Advanced Protection Program for admins

#### Privileged Access Management (PAM)

| Check ID | Control | Severity | Frameworks |
|----------|---------|----------|------------|
| AC-PAM-001 | Just-in-time (JIT) access implemented for privileged roles | High | SOC 2 CC6.1, ISO 27001 A.9.2.3, PCI-DSS 7.1, NIST CSF PR.AC-4 |
| AC-PAM-002 | Privileged access requests require approval workflow | High | SOC 2 CC6.1, ISO 27001 A.9.2.3 |
| AC-PAM-003 | Privileged session time-limited (maximum 4 hours, re-approval needed) | Medium | SOC 2 CC6.1, ISO 27001 A.9.2.3 |
| AC-PAM-004 | Privileged sessions recorded (screen recording or command logging) | High | SOC 2 CC7.2, ISO 27001 A.12.4.1, PCI-DSS 10.2 |
| AC-PAM-005 | Break-glass procedure documented and tested quarterly | Medium | SOC 2 CC6.1, ISO 27001 A.9.2.3, NIST CSF PR.AC-4 |
| AC-PAM-006 | Privileged account inventory maintained and reviewed quarterly | High | SOC 2 CC6.2, ISO 27001 A.9.2.5, PCI-DSS 7.1 |
| AC-PAM-007 | Standing privileged access eliminated (no permanent admin accounts) | High | SOC 2 CC6.1, ISO 27001 A.9.2.3, NIST CSF PR.AC-4 |

#### Role-Based Access Control (RBAC)

| Check ID | Control | Severity | Frameworks |
|----------|---------|----------|------------|
| AC-RBAC-001 | RBAC model documented with role definitions and permissions | High | SOC 2 CC6.3, ISO 27001 A.9.2.2, PCI-DSS 7.1, HIPAA 164.312(a)(1), NIST CSF PR.AC-4 |
| AC-RBAC-002 | Role assignments reviewed quarterly (access recertification) | High | SOC 2 CC6.2, ISO 27001 A.9.2.5, PCI-DSS 7.1.1 |
| AC-RBAC-003 | Separation of duties enforced (no single user has conflicting roles) | High | SOC 2 CC6.3, ISO 27001 A.6.1.2, PCI-DSS 6.4.2 |
| AC-RBAC-004 | Default deny — users get minimum necessary permissions | High | SOC 2 CC6.3, ISO 27001 A.9.4.1 |
| AC-RBAC-005 | Role changes logged and auditable | Medium | SOC 2 CC7.2, ISO 27001 A.12.4.1 |

#### Service Account and API Key Governance

| Check ID | Control | Severity | Frameworks |
|----------|---------|----------|------------|
| AC-SVC-001 | No shared credentials for service accounts | Critical | SOC 2 CC6.1, ISO 27001 A.9.2.4, PCI-DSS 8.5 |
| AC-SVC-002 | Service account permissions follow least privilege | High | SOC 2 CC6.3, ISO 27001 A.9.4.1 |
| AC-SVC-003 | Service account credentials rotate every 90 days maximum | High | SOC 2 CC6.1, ISO 27001 A.9.2.4, PCI-DSS 8.2.4 |
| AC-SVC-004 | Service account inventory maintained with owner assignment | High | SOC 2 CC6.2, ISO 27001 A.9.2.5 |
| AC-SVC-005 | API keys scoped to minimum required permissions | High | SOC 2 CC6.3, ISO 27001 A.9.4.1 |
| AC-SVC-006 | API keys have expiration dates (maximum 1 year) | Medium | SOC 2 CC6.1, ISO 27001 A.9.2.4 |
| AC-SVC-007 | API key usage monitored and anomalous access alerted | Medium | SOC 2 CC7.2, ISO 27001 A.12.4.1 |

#### SSH Key Management

| Check ID | Control | Severity | Frameworks |
|----------|---------|----------|------------|
| AC-SSH-001 | ED25519 keys required (or RSA >= 4096 bit) | High | SOC 2 CC6.7, ISO 27001 A.10.1.1 |
| AC-SSH-002 | SSH certificate-based authentication for infrastructure | Medium | SOC 2 CC6.7, ISO 27001 A.9.4.2 |
| AC-SSH-003 | SSH key passphrase required | Medium | SOC 2 CC6.1, ISO 27001 A.9.4.2 |
| AC-SSH-004 | SSH key inventory maintained with owner assignment | Medium | SOC 2 CC6.2, ISO 27001 A.9.2.5 |
| AC-SSH-005 | SSH keys rotate annually at minimum | Medium | SOC 2 CC6.1, PCI-DSS 3.6.4 |
| AC-SSH-006 | Root SSH login disabled | High | SOC 2 CC6.1, ISO 27001 A.9.4.2, PCI-DSS 2.1 |
| AC-SSH-007 | SSH password authentication disabled (key-only) | High | SOC 2 CC6.1, ISO 27001 A.9.4.2 |

#### Zero Trust Architecture

| Check ID | Control | Severity | Frameworks |
|----------|---------|----------|------------|
| AC-ZT-001 | Identity-based access (verify user, device, and context) | High | SOC 2 CC6.1, ISO 27001 A.9.4.2, NIST CSF PR.AC-4 |
| AC-ZT-002 | Device posture checked before granting access | High | SOC 2 CC6.1, ISO 27001 A.6.2.1 |
| AC-ZT-003 | Network location is not trusted (no implicit trust for internal network) | High | SOC 2 CC6.6, ISO 27001 A.13.1.1, NIST CSF PR.AC-5 |
| AC-ZT-004 | Continuous verification (re-authenticate for sensitive operations) | Medium | SOC 2 CC6.1, NIST CSF PR.AC-7 |
| AC-ZT-005 | Microsegmentation between services | Medium | SOC 2 CC6.6, ISO 27001 A.13.1.3, PCI-DSS 1.2 |

---

### 6. Network Security

#### Firewall Configuration

| Check ID | Control | Severity | Frameworks |
|----------|---------|----------|------------|
| NET-FW-001 | Default deny policy (deny all, allow by exception) | Critical | SOC 2 CC6.6, ISO 27001 A.13.1.1, PCI-DSS 1.2, NIST CSF PR.AC-5 |
| NET-FW-002 | Egress filtering enabled (restrict outbound traffic) | High | SOC 2 CC6.6, ISO 27001 A.13.1.1, PCI-DSS 1.3 |
| NET-FW-003 | Firewall rules reviewed quarterly | Medium | SOC 2 CC6.6, PCI-DSS 1.1.7 |
| NET-FW-004 | Firewall rule documentation (business justification for each rule) | Medium | SOC 2 CC6.6, PCI-DSS 1.1.6 |
| NET-FW-005 | No "any/any" rules in firewall ruleset | Critical | SOC 2 CC6.6, PCI-DSS 1.2 |
| NET-FW-006 | Firewall change management process documented | Medium | SOC 2 CC6.6, PCI-DSS 1.1.1 |

#### Network Segmentation

| Check ID | Control | Severity | Frameworks |
|----------|---------|----------|------------|
| NET-SEG-001 | Network segmentation isolates sensitive environments (production, staging, dev) | High | SOC 2 CC6.6, ISO 27001 A.13.1.3, PCI-DSS 1.2, HIPAA 164.312(e)(1) |
| NET-SEG-002 | Cardholder Data Environment (CDE) segmented from general network | Critical | PCI-DSS 1.3 |
| NET-SEG-003 | Database tier isolated from public-facing tier | High | SOC 2 CC6.6, ISO 27001 A.13.1.3, PCI-DSS 1.3 |
| NET-SEG-004 | Microsegmentation for East-West traffic | Medium | SOC 2 CC6.6, ISO 27001 A.13.1.3, NIST CSF PR.AC-5 |
| NET-SEG-005 | Management network separated from production | High | SOC 2 CC6.6, PCI-DSS 1.2 |
| NET-SEG-006 | Guest WiFi isolated from corporate network | Medium | SOC 2 CC6.6, ISO 27001 A.13.1.3 |

#### Web Application Firewall (WAF)

| Check ID | Control | Severity | Frameworks |
|----------|---------|----------|------------|
| NET-WAF-001 | WAF deployed for all public-facing web applications | High | SOC 2 CC6.6, ISO 27001 A.13.1.1, PCI-DSS 6.6, NIST CSF PR.IP-1 |
| NET-WAF-002 | OWASP Top 10 rules enabled | High | SOC 2 CC6.6, PCI-DSS 6.6 |
| NET-WAF-003 | Rate limiting configured | Medium | SOC 2 CC6.6, ISO 27001 A.13.1.1 |
| NET-WAF-004 | WAF in blocking mode (not just detection) | High | SOC 2 CC6.6, PCI-DSS 6.6 |
| NET-WAF-005 | WAF rules regularly updated | Medium | SOC 2 CC6.6, PCI-DSS 6.6 |
| NET-WAF-006 | Custom rules for application-specific attack patterns | Low | SOC 2 CC6.6 |

#### DDoS Protection

| Check ID | Control | Severity | Frameworks |
|----------|---------|----------|------------|
| NET-DDOS-001 | DDoS protection enabled (Cloudflare, AWS Shield, Azure DDoS Protection) | High | SOC 2 A1.2, ISO 27001 A.13.1.1, NIST CSF PR.DS-4 |
| NET-DDOS-002 | Layer 7 DDoS protection configured | Medium | SOC 2 A1.2, ISO 27001 A.13.1.1 |
| NET-DDOS-003 | DDoS response plan documented | Medium | SOC 2 A1.2, ISO 27001 A.16.1.1, NIST CSF RS.RP-1 |
| NET-DDOS-004 | DDoS alert thresholds configured | Medium | SOC 2 A1.2, ISO 27001 A.12.4.1 |

#### VPN Configuration

| Check ID | Control | Severity | Frameworks |
|----------|---------|----------|------------|
| NET-VPN-001 | VPN uses WireGuard or IPSec (no PPTP or L2TP without IPSec) | High | SOC 2 CC6.7, ISO 27001 A.13.1.1, PCI-DSS 4.1, NIST CSF PR.DS-2 |
| NET-VPN-002 | Split tunneling disabled for compliance environments | Medium | SOC 2 CC6.7, PCI-DSS 1.4 |
| NET-VPN-003 | VPN requires MFA for connection | High | SOC 2 CC6.1, ISO 27001 A.9.4.2, PCI-DSS 8.3 |
| NET-VPN-004 | VPN access logged and monitored | Medium | SOC 2 CC7.2, ISO 27001 A.12.4.1, PCI-DSS 10.2 |
| NET-VPN-005 | VPN being replaced or augmented by ZTNA (Zero Trust Network Access) | Info | NIST CSF PR.AC-5 |

#### Intrusion Detection/Prevention

| Check ID | Control | Severity | Frameworks |
|----------|---------|----------|------------|
| NET-IDS-001 | IDS/IPS deployed at network perimeter | High | SOC 2 CC6.6, ISO 27001 A.13.1.1, PCI-DSS 11.4, NIST CSF DE.CM-1, HIPAA 164.312(e)(1) |
| NET-IDS-002 | IDS/IPS signatures updated regularly | Medium | SOC 2 CC6.6, PCI-DSS 11.4 |
| NET-IDS-003 | IDS alerts integrated with SIEM | Medium | SOC 2 CC7.2, ISO 27001 A.12.4.1 |
| NET-IDS-004 | Network traffic monitoring for anomalies | Medium | SOC 2 CC7.2, NIST CSF DE.AE-1 |

---

### 7. Container and Kubernetes Security

#### Base Image Security

| Check ID | Control | Severity | Frameworks |
|----------|---------|----------|------------|
| K8S-IMG-001 | Base images from trusted registries only (verified publishers) | High | SOC 2 CC7.1, ISO 27001 A.14.2.7, NIST CSF PR.IP-12 |
| K8S-IMG-002 | Minimal base images (distroless, Alpine, scratch) | Medium | SOC 2 CC7.1, ISO 27001 A.14.2.7 |
| K8S-IMG-003 | No running as root in containers (USER directive in Dockerfile) | High | SOC 2 CC6.1, ISO 27001 A.9.4.1, PCI-DSS 2.1 |
| K8S-IMG-004 | Container images scanned for vulnerabilities (Trivy, Snyk, Grype) | High | SOC 2 CC7.1, ISO 27001 A.12.6.1, PCI-DSS 6.2, NIST CSF DE.CM-8 |
| K8S-IMG-005 | No secrets baked into container images | Critical | SOC 2 CC6.7, PCI-DSS 3.4 |
| K8S-IMG-006 | Images tagged with specific version/digest (no `latest` tag) | Medium | SOC 2 CC7.1 |
| K8S-IMG-007 | Image signing verified before deployment (cosign, Notary) | High | SOC 2 CC7.1, NIST CSF PR.IP-1 |

#### Container Runtime Security

| Check ID | Control | Severity | Frameworks |
|----------|---------|----------|------------|
| K8S-RT-001 | Seccomp profiles applied (runtime default minimum) | Medium | SOC 2 CC6.6, ISO 27001 A.13.1.1 |
| K8S-RT-002 | AppArmor/SELinux profiles applied | Medium | SOC 2 CC6.6, ISO 27001 A.13.1.1 |
| K8S-RT-003 | Read-only root filesystem for containers | Medium | SOC 2 CC6.7, ISO 27001 A.12.4.3 |
| K8S-RT-004 | No privileged containers | Critical | SOC 2 CC6.1, ISO 27001 A.9.4.1, PCI-DSS 2.1 |
| K8S-RT-005 | No host PID/network/IPC namespace sharing | High | SOC 2 CC6.6, ISO 27001 A.13.1.3 |
| K8S-RT-006 | Resource limits set (CPU, memory) to prevent resource abuse | Medium | SOC 2 A1.2, ISO 27001 A.12.1.3 |

#### Kubernetes Cluster Security

| Check ID | Control | Severity | Frameworks |
|----------|---------|----------|------------|
| K8S-RBAC-001 | RBAC enabled with least-privilege role bindings | High | SOC 2 CC6.3, ISO 27001 A.9.4.1, PCI-DSS 7.1 |
| K8S-RBAC-002 | No cluster-admin bindings for application workloads | Critical | SOC 2 CC6.3, ISO 27001 A.9.4.1 |
| K8S-RBAC-003 | Default ServiceAccount token automounting disabled | Medium | SOC 2 CC6.1 |
| K8S-NET-001 | Network Policies defined for all namespaces | High | SOC 2 CC6.6, ISO 27001 A.13.1.3, PCI-DSS 1.2 |
| K8S-NET-002 | Default deny network policy in place | High | SOC 2 CC6.6, PCI-DSS 1.2 |
| K8S-POD-001 | Pod Security Standards enforced (restricted profile) | High | SOC 2 CC6.6, ISO 27001 A.14.2.7 |
| K8S-SEC-001 | External Secrets Operator or Sealed Secrets for secret management | High | SOC 2 CC6.7, PCI-DSS 3.4 |
| K8S-SEC-002 | Etcd encrypted at rest | High | SOC 2 CC6.7, ISO 27001 A.10.1.1 |
| K8S-ADM-001 | Admission controllers configured (OPA Gatekeeper or Kyverno) | High | SOC 2 CC7.1, ISO 27001 A.14.2.7 |
| K8S-ADM-002 | Image pull policy set to Always for production | Medium | SOC 2 CC7.1 |
| K8S-MESH-001 | Service mesh deployed for mTLS between services (Istio, Linkerd) | Medium | SOC 2 CC6.7, ISO 27001 A.13.1.1 |
| K8S-REG-001 | Private container registry with authentication | High | SOC 2 CC6.6, ISO 27001 A.13.1.1 |
| K8S-REG-002 | Registry vulnerability scanning enabled | Medium | SOC 2 CC7.1 |
| K8S-REG-003 | Image retention policies configured | Low | SOC 2 CC6.7 |

---

### 8. CI/CD Pipeline Security

#### Source Code Management

| Check ID | Control | Severity | Frameworks |
|----------|---------|----------|------------|
| CICD-SCM-001 | Branch protection on main/production branches (required reviews) | High | SOC 2 CC7.1, ISO 27001 A.14.2.2, PCI-DSS 6.4.2, NIST CSF PR.IP-1 |
| CICD-SCM-002 | Minimum 2 approvals for production branch merges | Medium | SOC 2 CC7.1, ISO 27001 A.14.2.2, PCI-DSS 6.4.2 |
| CICD-SCM-003 | Status checks required before merge | Medium | SOC 2 CC7.1, ISO 27001 A.14.2.2 |
| CICD-SCM-004 | Signed commits enforced (GPG or SSH signing) | Medium | SOC 2 CC7.1, ISO 27001 A.14.2.2 |
| CICD-SCM-005 | Force push to protected branches prohibited | High | SOC 2 CC7.1, ISO 27001 A.14.2.2 |
| CICD-SCM-006 | Repository access follows least privilege | High | SOC 2 CC6.3, ISO 27001 A.9.4.1 |
| CICD-SCM-007 | Code owners configured for critical paths | Medium | SOC 2 CC7.1 |

#### Security Scanning

| Check ID | Control | Severity | Frameworks |
|----------|---------|----------|------------|
| CICD-SCAN-001 | Secret scanning enabled in all repositories | Critical | SOC 2 CC6.7, ISO 27001 A.9.4.3, PCI-DSS 3.4 |
| CICD-SCAN-002 | Pre-commit hooks prevent secret commits (gitleaks, truffleHog) | High | SOC 2 CC6.7, PCI-DSS 3.4 |
| CICD-SCAN-003 | Dependency scanning automated (Dependabot, Snyk, Renovate) | High | SOC 2 CC7.1, ISO 27001 A.12.6.1, PCI-DSS 6.2, NIST CSF PR.IP-12 |
| CICD-SCAN-004 | SAST in CI pipeline (Semgrep, SonarQube, CodeQL) | High | SOC 2 CC7.1, ISO 27001 A.14.2.8, PCI-DSS 6.3.2, NIST CSF PR.IP-1 |
| CICD-SCAN-005 | DAST for staging/pre-production (OWASP ZAP, Burp Suite) | Medium | SOC 2 CC7.1, ISO 27001 A.14.2.8, PCI-DSS 6.6 |
| CICD-SCAN-006 | SCA (Software Composition Analysis) for license compliance | Medium | SOC 2 CC7.1, ISO 27001 A.18.1.2 |
| CICD-SCAN-007 | Container image scanning in CI pipeline | High | SOC 2 CC7.1, ISO 27001 A.12.6.1, PCI-DSS 6.2 |
| CICD-SCAN-008 | Infrastructure as Code scanning (tfsec, checkov, KICS) | High | SOC 2 CC7.1, ISO 27001 A.14.2.8 |

#### Supply Chain Security

| Check ID | Control | Severity | Frameworks |
|----------|---------|----------|------------|
| CICD-SC-001 | SBOM generated for all releases (CycloneDX or SPDX format) | High | SOC 2 CC7.1, NIST CSF PR.IP-1, NIS2 Art.21 |
| CICD-SC-002 | Artifact signing for all builds (Sigstore/cosign) | High | SOC 2 CC7.1, NIST CSF PR.IP-1 |
| CICD-SC-003 | Dependency pinning (lock files committed, hash verification) | Medium | SOC 2 CC7.1, ISO 27001 A.14.2.7 |
| CICD-SC-004 | Third-party dependency review process | Medium | SOC 2 CC7.1, ISO 27001 A.15.1.1 |
| CICD-SC-005 | CI/CD pipeline hardened (no arbitrary code execution from PRs) | High | SOC 2 CC7.1, ISO 27001 A.14.2.7 |

#### Deployment Security

| Check ID | Control | Severity | Frameworks |
|----------|---------|----------|------------|
| CICD-DEP-001 | Deployment approval gates for production | High | SOC 2 CC7.1, ISO 27001 A.14.2.2, PCI-DSS 6.4.5 |
| CICD-DEP-002 | Production deployments audited (who, what, when) | High | SOC 2 CC7.2, ISO 27001 A.12.4.1, PCI-DSS 10.2 |
| CICD-DEP-003 | Rollback capability tested and documented | Medium | SOC 2 A1.2, ISO 27001 A.14.2.2 |
| CICD-DEP-004 | Deployment credentials managed via secrets manager (not pipeline env vars) | High | SOC 2 CC6.7, PCI-DSS 3.4 |
| CICD-DEP-005 | CI/CD service accounts have minimum required permissions | High | SOC 2 CC6.3, ISO 27001 A.9.4.1 |
| CICD-DEP-006 | Immutable build artifacts (reproducible builds preferred) | Medium | SOC 2 CC7.1 |

---

### 9. Secrets Management

#### Secrets Management Solutions

| Check ID | Control | Severity | Frameworks |
|----------|---------|----------|------------|
| SEC-MGR-001 | Centralized secrets manager deployed (Vault, AWS SM, Azure KV, GCP SM) | High | SOC 2 CC6.7, ISO 27001 A.10.1.2, PCI-DSS 3.5, HIPAA 164.312(a)(2)(iv), NIST CSF PR.DS-1 |
| SEC-MGR-002 | Secrets manager has HA/DR configuration | Medium | SOC 2 A1.2, ISO 27001 A.17.1.1 |
| SEC-MGR-003 | Secrets access audited (who accessed what secret, when) | High | SOC 2 CC7.2, ISO 27001 A.12.4.1, PCI-DSS 10.2 |
| SEC-MGR-004 | Dynamic secrets used where possible (database credentials on demand) | Medium | SOC 2 CC6.7, ISO 27001 A.9.4.2 |

#### Secret Rotation

| Check ID | Control | Severity | Frameworks |
|----------|---------|----------|------------|
| SEC-ROT-001 | Database credentials rotate every 90 days maximum | High | SOC 2 CC6.1, ISO 27001 A.9.2.4, PCI-DSS 8.2.4 |
| SEC-ROT-002 | API keys rotate every 90 days maximum | High | SOC 2 CC6.1, ISO 27001 A.9.2.4 |
| SEC-ROT-003 | Service account passwords rotate every 90 days maximum | High | SOC 2 CC6.1, ISO 27001 A.9.2.4, PCI-DSS 8.2.4 |
| SEC-ROT-004 | TLS private keys rotate annually at minimum | Medium | SOC 2 CC6.7, ISO 27001 A.10.1.2 |
| SEC-ROT-005 | Encryption keys rotate annually (auto-rotation preferred) | Medium | SOC 2 CC6.7, PCI-DSS 3.6.4 |
| SEC-ROT-006 | Rotation is automated (no manual credential changes) | Medium | SOC 2 CC6.1 |

#### Code and Repository Security

| Check ID | Control | Severity | Frameworks |
|----------|---------|----------|------------|
| SEC-CODE-001 | No secrets in source code (scan entire git history) | Critical | SOC 2 CC6.7, ISO 27001 A.9.4.3, PCI-DSS 3.4 |
| SEC-CODE-002 | `.env` files in `.gitignore` | High | SOC 2 CC6.7, PCI-DSS 3.4 |
| SEC-CODE-003 | Pre-commit hooks block secret commits (gitleaks) | High | SOC 2 CC6.7, PCI-DSS 3.4 |
| SEC-CODE-004 | GitHub/GitLab secret scanning alerts enabled and triaged | High | SOC 2 CC6.7, PCI-DSS 3.4 |
| SEC-CODE-005 | Historical leaked secrets rotated (not just removed from code) | Critical | SOC 2 CC6.7 |
| SEC-CODE-006 | Environment-specific secrets never shared between environments | Medium | SOC 2 CC6.7, PCI-DSS 3.4 |

#### Hardware Security Modules (HSM)

| Check ID | Control | Severity | Frameworks |
|----------|---------|----------|------------|
| SEC-HSM-001 | HSM (CloudHSM, Azure Dedicated HSM) used for root CA keys | High | SOC 2 CC6.7, ISO 27001 A.10.1.2, PCI-DSS 3.5, FedRAMP SC-12 |
| SEC-HSM-002 | HSM used for payment processing keys | Critical | PCI-DSS 3.5 |
| SEC-HSM-003 | HSM firmware kept current | Medium | SOC 2 CC7.1, PCI-DSS 3.5 |
| SEC-HSM-004 | HSM access restricted to authorized personnel only | High | SOC 2 CC6.1, PCI-DSS 3.5 |

---

### 10. Logging and Monitoring

#### Centralized Logging

| Check ID | Control | Severity | Frameworks |
|----------|---------|----------|------------|
| LOG-CEN-001 | All systems forward logs to centralized platform (ELK, Splunk, Datadog) | High | SOC 2 CC7.2, ISO 27001 A.12.4.1, PCI-DSS 10.5.3, HIPAA 164.312(b), NIST CSF DE.CM-1, FedRAMP AU-6 |
| LOG-CEN-002 | Log collection covers: authentication, authorization, data access, system changes | High | SOC 2 CC7.2, ISO 27001 A.12.4.1, PCI-DSS 10.2 |
| LOG-CEN-003 | Logs include: timestamp, source, user, action, result, source IP | High | SOC 2 CC7.2, ISO 27001 A.12.4.1, PCI-DSS 10.3 |
| LOG-CEN-004 | Log shipping uses TLS encryption | Medium | SOC 2 CC6.7, PCI-DSS 10.5 |
| LOG-CEN-005 | Log source time synchronized via NTP (max 1 second drift) | Medium | SOC 2 CC7.2, PCI-DSS 10.4 |

#### SIEM

| Check ID | Control | Severity | Frameworks |
|----------|---------|----------|------------|
| LOG-SIEM-001 | SIEM deployed with correlation rules | High | SOC 2 CC7.2, ISO 27001 A.12.4.1, PCI-DSS 10.6, NIST CSF DE.AE-2, NIS2 Art.21 |
| LOG-SIEM-002 | SIEM detection rules cover MITRE ATT&CK framework | Medium | NIST CSF DE.AE-2 |
| LOG-SIEM-003 | SIEM alerts have defined response procedures | Medium | SOC 2 CC7.3, ISO 27001 A.16.1.1, NIST CSF RS.RP-1 |
| LOG-SIEM-004 | SIEM tuned to reduce false positives (<10% false positive rate) | Low | SOC 2 CC7.2 |

#### Retention and Integrity

| Check ID | Control | Severity | Frameworks |
|----------|---------|----------|------------|
| LOG-RET-001 | Log retention minimum 1 year (365 days) | High | SOC 2 CC7.2, ISO 27001 A.12.4.1, PCI-DSS 10.7, HIPAA 164.312(b) |
| LOG-RET-002 | Logs immutable (write-once, no modification or deletion) | High | SOC 2 CC7.2, ISO 27001 A.12.4.3, PCI-DSS 10.5 |
| LOG-RET-003 | Log backup and disaster recovery tested | Medium | SOC 2 A1.2, ISO 27001 A.12.3.1 |
| LOG-RET-004 | PCI-DSS environments retain logs for minimum 1 year, 3 months immediately available | High | PCI-DSS 10.7 |
| LOG-RET-005 | HIPAA environments retain logs for minimum 6 years | High | HIPAA 164.530(j)(2) |

#### Alerting and Detection

| Check ID | Control | Severity | Frameworks |
|----------|---------|----------|------------|
| LOG-ALERT-001 | Alerts for: failed auth attempts (>5 in 5 min), privilege escalation, data exfiltration patterns | High | SOC 2 CC7.2, ISO 27001 A.12.4.1, PCI-DSS 10.6, NIST CSF DE.CM-1 |
| LOG-ALERT-002 | Alert escalation matrix documented (L1 -> L2 -> L3 -> management) | Medium | SOC 2 CC7.3, ISO 27001 A.16.1.1 |
| LOG-ALERT-003 | On-call rotation for security alerts (24/7 coverage) | Medium | SOC 2 CC7.3, ISO 27001 A.16.1.1 |
| LOG-ALERT-004 | Mean time to acknowledge (MTTA) < 15 minutes for critical alerts | Medium | SOC 2 CC7.3 |
| LOG-ALERT-005 | Anomaly detection enabled (UEBA — User and Entity Behavior Analytics) | Medium | SOC 2 CC7.2, NIST CSF DE.AE-1 |
| LOG-ALERT-006 | File integrity monitoring (FIM) deployed for critical files | High | SOC 2 CC7.2, ISO 27001 A.12.4.3, PCI-DSS 11.5 |

---

### 11. Physical Security

#### Data Center Security

| Check ID | Control | Severity | Frameworks |
|----------|---------|----------|------------|
| PHYS-DC-001 | Cloud provider SOC 2 Type II report obtained and reviewed annually | High | SOC 2 CC6.4, ISO 27001 A.11.1.1, PCI-DSS 9.1 |
| PHYS-DC-002 | Data center physical access restricted to authorized personnel | High | SOC 2 CC6.4, ISO 27001 A.11.1.2, PCI-DSS 9.1 |
| PHYS-DC-003 | 24/7 video surveillance at data center | Medium | SOC 2 CC6.4, ISO 27001 A.11.1.2, PCI-DSS 9.1 |
| PHYS-DC-004 | Visitor access logged and escorted | Medium | SOC 2 CC6.4, ISO 27001 A.11.1.2, PCI-DSS 9.4 |
| PHYS-DC-005 | Environmental controls (fire suppression, HVAC, UPS) | Medium | SOC 2 A1.2, ISO 27001 A.11.1.4, PCI-DSS 9.1 |

#### Office Security

| Check ID | Control | Severity | Frameworks |
|----------|---------|----------|------------|
| PHYS-OFF-001 | Badge access for office entry | Medium | SOC 2 CC6.4, ISO 27001 A.11.1.2 |
| PHYS-OFF-002 | Visitor management system (sign-in, badge, escort) | Low | SOC 2 CC6.4, ISO 27001 A.11.1.2 |
| PHYS-OFF-003 | Clean desk policy documented and enforced | Low | SOC 2 CC6.4, ISO 27001 A.11.2.9 |
| PHYS-OFF-004 | Server/network rooms locked with restricted access | Medium | SOC 2 CC6.4, ISO 27001 A.11.1.2, PCI-DSS 9.1 |

#### Media Disposal

| Check ID | Control | Severity | Frameworks |
|----------|---------|----------|------------|
| PHYS-DISP-001 | Media disposal follows NIST 800-88 guidelines (clear, purge, destroy) | High | SOC 2 CC6.5, ISO 27001 A.8.3.2, PCI-DSS 9.8, HIPAA 164.310(d)(2)(i), NIST CSF PR.IP-6 |
| PHYS-DISP-002 | Certificate of destruction obtained for physical media | High | SOC 2 CC6.5, ISO 27001 A.8.3.2, PCI-DSS 9.8 |
| PHYS-DISP-003 | Disposal vendor contracted with background checks | Medium | SOC 2 CC6.5, ISO 27001 A.8.3.2 |
| PHYS-DISP-004 | Electronic media cryptographically erased before disposal | High | SOC 2 CC6.5, PCI-DSS 9.8, HIPAA 164.310(d)(2)(i) |

---

### 12. Compliance Framework Mapping

Each control in this audit maps to one or more compliance frameworks. The mapping enables organizations pursuing multiple certifications to satisfy overlapping requirements with single implementations.

**Supported Frameworks:**

| Framework | Abbreviation | Focus Area |
|-----------|-------------|------------|
| SOC 2 Type II | SOC 2 | Trust Services Criteria (Security, Availability, Processing Integrity, Confidentiality, Privacy) |
| ISO 27001:2022 | ISO 27001 | Information Security Management System (Annex A controls) |
| HIPAA | HIPAA | Healthcare data protection (Security Rule, Privacy Rule) |
| GDPR | GDPR | EU data protection and privacy |
| PCI-DSS v4.0 | PCI-DSS | Payment card data security |
| NIS2 Directive | NIS2 | EU network and information security (critical infrastructure) |
| DORA | DORA | EU Digital Operational Resilience Act (financial services) |
| NIST CSF 2.0 | NIST CSF | Cybersecurity Framework (Identify, Protect, Detect, Respond, Recover) |
| FedRAMP | FedRAMP | US federal cloud security (based on NIST 800-53) |
| CCPA/CPRA | CCPA | California consumer privacy |

**Framework Coverage Summary:**

| Audit Domain | SOC 2 | ISO 27001 | HIPAA | GDPR | PCI-DSS | NIS2 | DORA | NIST CSF | FedRAMP | CCPA |
|-------------|-------|-----------|-------|------|---------|------|------|----------|---------|------|
| Cloud Infrastructure | CC6.1-CC6.7 | A.9, A.10, A.12, A.13 | 164.312 | Art.32 | 1-4, 7-8, 10 | Art.21 | Art.9 | PR.AC, PR.DS, DE.CM | AC, SC, AU | 1798.150 |
| DNS Security | CC6.6 | A.13.1, A.13.2 | - | - | - | Art.21 | - | PR.AC, PR.DS | - | - |
| TLS/SSL | CC6.7 | A.10.1, A.13.1 | 164.312(e) | Art.32 | 4.1 | Art.21 | Art.9 | PR.DS-2 | SC-8, SC-13 | - |
| Endpoint Security | CC6.7-CC6.8 | A.6.2, A.8.3, A.10.1, A.11.2, A.12.2, A.12.6 | 164.310, 164.312 | Art.32 | 1.4, 3.4, 5.1-5.4, 6.2 | Art.21 | Art.9 | PR.AC, PR.DS, PR.IP, DE.CM | - | - |
| Access Control | CC6.1-CC6.3 | A.9.1-A.9.4 | 164.312(a)(d) | Art.32 | 7.1-8.3 | Art.21 | Art.9 | PR.AC | AC, IA | 1798.150 |
| Network Security | CC6.6, A1.2 | A.13.1 | 164.312(e) | Art.32 | 1.1-1.3, 6.6, 11.4 | Art.21 | Art.9 | PR.AC-5, DE.CM-1 | SC, SI | - |
| Container/K8s | CC6.1-CC7.1 | A.9.4, A.13.1, A.14.2 | - | - | 1.2, 2.1, 6.2, 7.1 | Art.21 | - | PR.AC, PR.IP | - | - |
| CI/CD Pipeline | CC7.1-CC7.2 | A.14.2 | - | - | 6.2-6.6 | Art.21 | Art.9 | PR.IP-1, PR.IP-12 | SA, SI | - |
| Secrets Management | CC6.7 | A.9.4, A.10.1 | 164.312(a) | Art.32 | 3.4-3.6, 8.2 | Art.21 | Art.9 | PR.DS-1 | SC-12, SC-28 | - |
| Logging/Monitoring | CC7.2-CC7.3 | A.12.4 | 164.312(b) | Art.32 | 10.1-10.7, 11.5 | Art.21 | Art.9 | DE.AE, DE.CM | AU | - |
| Physical Security | CC6.4-CC6.5 | A.8.3, A.11.1, A.11.2 | 164.310 | Art.32 | 9.1-9.8 | Art.21 | - | PR.IP-6 | PE | - |

**Multi-Framework Evidence Strategy:**

For each control, collect evidence once and map to all applicable frameworks:

1. **Policy Document** — Covers SOC 2, ISO 27001, HIPAA, GDPR (one policy, multiple mappings)
2. **Technical Configuration** — Screenshot/export showing control is active (maps to all technical frameworks)
3. **Audit Log** — Proves ongoing compliance (SOC 2, PCI-DSS, HIPAA all require audit trails)
4. **Review Record** — Quarterly review minutes satisfy multiple framework requirements simultaneously

---

## Workflows

### Workflow 1: Full Infrastructure Audit

```
1. Prepare inventory → Document all cloud accounts, domains, endpoints, services
2. Run infra_audit_runner.py → Generate findings across all 11 domains
3. Triage findings → Prioritize Critical > High > Medium > Low
4. Map to frameworks → Identify which framework requirements are met/unmet
5. Create remediation plan → Assign owners, set deadlines by severity SLA
6. Execute remediation → Fix Critical within 24h, High within 72h
7. Re-audit → Verify fixes, update compliance evidence
8. Generate report → Executive summary + detailed findings + evidence
```

**Severity SLAs:**
| Severity | Remediation Deadline | Re-audit Deadline |
|----------|---------------------|-------------------|
| Critical | 24 hours | 48 hours |
| High | 72 hours | 7 days |
| Medium | 7 days | 14 days |
| Low | 30 days | 45 days |
| Info | No deadline | Next audit cycle |

### Workflow 2: DNS Security Assessment

```
1. Enumerate domains → Primary + all subdomains
2. Run dns_security_checker.py → Check SPF, DKIM, DMARC, DNSSEC, CAA, MTA-STS
3. Validate email chain → SPF → DKIM → DMARC alignment
4. Check domain security → Registrar lock, 2FA, WHOIS, expiration
5. Subdomain audit → Check for dangling CNAME records (takeover risk)
6. Generate DNS report → Findings + remediation DNS records
```

### Workflow 3: Access Control Review

```
1. Export IdP configuration → Users, groups, roles, policies
2. Run access_control_auditor.py → Check MFA, SSO, RBAC, PAM, service accounts
3. Verify MFA coverage → Must be 100%, flag any exceptions
4. Review privileged access → Who has admin? Is JIT in place?
5. Check service accounts → Rotation, ownership, permissions
6. Access recertification → Verify all access is current and justified
7. Generate access report → Gaps + remediation steps
```

### Workflow 4: Continuous Compliance Monitoring

```
1. Schedule automated scans → Weekly infra audit, daily DNS check
2. Track compliance score trends → Score per domain over time
3. Alert on regressions → Score drop or new Critical finding triggers alert
4. Quarterly full audit → Manual review + automated scan
5. Annual certification preparation → Compile evidence for auditors
```

---

## Reference Guides

| Guide | Location | Coverage |
|-------|----------|----------|
| Cloud Security Baseline | `references/cloud-security-baseline.md` | AWS, Azure, GCP CIS Benchmarks |
| Access Control Standards | `references/access-control-standards.md` | MFA, SSO, PAM, Zero Trust, YubiKey |
| Compliance Framework Mapping | `references/compliance-framework-mapping.md` | Control-to-framework master mapping |

---

## Validation Checkpoints

### Pre-Audit Validation
- [ ] Infrastructure inventory is complete and current
- [ ] All cloud accounts identified and accessible
- [ ] Domain list verified (primary + all active subdomains)
- [ ] Endpoint MDM reports available
- [ ] IdP configuration export available
- [ ] Previous audit findings reviewed

### Post-Audit Validation
- [ ] All 11 domains audited with no skipped checks
- [ ] Every finding has severity, framework mapping, and remediation
- [ ] Critical and High findings have assigned owners
- [ ] Compliance score calculated per domain and overall
- [ ] Executive summary prepared
- [ ] Evidence package compiled for applicable frameworks
- [ ] Remediation deadlines set per severity SLA

---

## Scoring Methodology

Each audit domain is scored 0-100 based on the controls assessed:

**Score Calculation:**
```
Domain Score = (Passed Controls * Weight) / (Total Controls * Weight) * 100

Weights by severity:
  Critical = 10
  High = 5
  Medium = 2
  Low = 1
  Info = 0 (informational, not scored)
```

**Overall Score:**
```
Overall Score = Weighted Average of Domain Scores

Domain Weights:
  Cloud Infrastructure: 15%
  Access Control: 15%
  Network Security: 12%
  Secrets Management: 10%
  Logging/Monitoring: 10%
  CI/CD Pipeline: 8%
  Container/K8s: 8%
  Endpoint Security: 7%
  TLS/SSL: 5%
  DNS Security: 5%
  Physical Security: 5%
```

**Score Interpretation:**
| Score Range | Rating | Meaning |
|-------------|--------|---------|
| 90-100 | Excellent | Audit-ready, minimal findings |
| 80-89 | Good | Minor gaps, mostly compliant |
| 70-79 | Fair | Notable gaps, remediation needed before audit |
| 60-69 | Poor | Significant compliance gaps |
| Below 60 | Critical | Major overhaul required, not audit-ready |

---

---

## Troubleshooting

| Problem | Possible Cause | Resolution |
|---------|---------------|------------|
| Infra audit runner returns mostly "UNKNOWN" statuses | Config JSON missing required keys or key paths do not match expected `check_key` format | Generate a fresh template with `--generate-template` and verify all key paths match the control registry (e.g., `aws.iam.root_mfa_enabled`); fill in actual values from your infrastructure |
| DNS security checker cannot resolve records | `dig` command not available on the system or DNS resolver blocking queries | Install `dnsutils` (Linux) or `bind` (macOS via Homebrew); alternatively the tool falls back to socket-based lookups but with reduced functionality; check network connectivity to DNS resolvers |
| Access control auditor shows Critical findings for MFA | SMS/TOTP MFA deployed instead of hardware security keys for admin accounts | Migrate admin accounts to FIDO2/WebAuthn hardware keys (YubiKey 5, Titan); disable SMS MFA for privileged access; use `--generate-template` to review all MFA-related control expectations |
| Framework-filtered report shows zero controls for a specific framework | Framework label mismatch in `--frameworks` flag (e.g., `pci-dss` instead of `pci_dss`) | Use exact framework identifiers: `soc2`, `iso27001`, `hipaa`, `gdpr`, `pci_dss`, `nis2`, `dora`, `nist_csf`, `fedramp`, `ccpa` |
| Overall score low despite strong cloud security | Domain weights distribute score across all 11 domains; weak areas (e.g., physical security, DNS) drag down the average | Review per-domain scores to identify weakest areas; prioritize remediation in highest-weighted domains (Cloud Infrastructure 15%, Access Control 15%, Network Security 12%) |
| Container security audit fails with all controls non-compliant | Organization does not use containers but config JSON contains default/empty container section | Set container controls to `N/A` or remove the container section from the config; tool scores only applicable controls |
| Audit report too large for stakeholder review | Full 250+ control audit generates extensive output | Use `--frameworks` flag to filter to relevant frameworks; use `--format markdown` for human-readable summary; generate separate reports per domain for team-specific remediation |

---

## Success Criteria

- **Overall infrastructure score of 80+ (Good or Excellent)** -- indicating audit-readiness with only minor gaps across all 11 domains
- **Zero Critical findings across all domains** -- all Critical-severity controls (root MFA, no wildcard IAM policies, encryption at rest, hardware key admin MFA) passing
- **Framework-specific compliance above 85%** -- for each targeted compliance framework (SOC 2, ISO 27001, PCI-DSS, etc.), the mapped controls show 85%+ pass rate
- **DNS security fully configured** -- SPF, DKIM, and DMARC (policy=reject) records validated, DNSSEC enabled, CAA records set, and MTA-STS deployed
- **Access control audit passes all Critical and High controls** -- centralized IdP deployed, SSO integrated for all applications, hardware security keys enforced for admin accounts, PAM implemented, and RBAC documented
- **Secrets management score above 90%** -- dedicated secrets vault deployed, automated rotation configured, no secrets in source code (git scanning enabled), and HSM for cryptographic operations
- **Evidence artifacts generated for audit** -- JSON or markdown reports suitable for auditor review, with per-control pass/fail status and framework mapping

---

## Scope & Limitations

**In Scope:**
- Infrastructure security audit across 11 domains: Cloud, DNS, TLS/SSL, Endpoints, Access Control, Network, Containers/K8s, CI/CD, Secrets, Logging/Monitoring, Physical Security
- Framework mapping to 10 compliance standards: SOC 2, ISO 27001, HIPAA, GDPR, PCI-DSS, NIS2, DORA, NIST CSF, FedRAMP, CCPA
- 250+ individual control checks with severity-weighted scoring
- DNS security validation including SPF, DKIM, DMARC, DNSSEC, CAA, MTA-STS, and subdomain takeover risk
- Access control audit covering IdP, SSO, MFA, FIDO2/hardware keys, PAM, RBAC, service accounts, SSH keys, API keys, and Zero Trust
- Evidence-generating reports in JSON and markdown formats for auditor consumption

**Out of Scope:**
- Actual penetration testing, vulnerability scanning, or active exploitation -- this skill performs configuration-based assessment, not active testing
- Cloud provider API calls or live infrastructure scanning -- the tool works with JSON configuration input describing your infrastructure state
- Compliance certification or attestation -- this skill identifies gaps but does not replace formal SOC 2, ISO 27001, or PCI-DSS audits
- Application security testing (SAST/DAST) beyond CI/CD pipeline configuration checks
- Compliance program management, policy writing, or governance documentation

**Important Notes:**
- SOC 2 2026 best practices demand real-time monitoring dashboards flagging control deficiencies within 48 hours; periodic spot-checks are no longer sufficient
- Zero Trust architecture is increasingly expected across all frameworks; perimeter-based security alone is insufficient for SOC 2, ISO 27001, and NIS2
- Compliance automation platforms (Drata, Vanta, Sprinto) complement but do not replace the deterministic checks this tool provides

---

## Integration Points

| Skill | Integration | When to Use |
|-------|-------------|-------------|
| `soc2-compliance-expert` | SOC 2 Trust Services Criteria mapped to infrastructure controls; evidence collection for SOC 2 Type II | When infrastructure audit supports SOC 2 certification |
| `information-security-manager-iso27001` | ISO 27001 Annex A technological controls validated by infrastructure checks | When ISO 27001 certification requires evidence of technical control implementation |
| `nist-csf-specialist` | NIST CSF 2.0 Protect and Detect functions mapped to infrastructure domains | When building unified security posture across NIST and other frameworks |
| `dora-compliance-expert` | DORA Pillar 1 and Pillar 3 controls validated by infrastructure security checks | When financial entity requires infrastructure evidence for DORA compliance |
| `pci-dss-specialist` | PCI-DSS v4.0 network security, encryption, and access control requirements mapped to checks | When cardholder data environment requires infrastructure compliance validation |
| `gdpr-dsgvo-expert` | Technical privacy controls (encryption, access controls, data masking) supporting GDPR Art. 32 | When infrastructure controls support personal data protection requirements |

---

## Tool Reference

### infra_audit_runner.py

Comprehensive infrastructure audit across 11 domains with compliance framework mapping.

| Flag | Required | Description |
|------|----------|-------------|
| `--config <file>` | Yes (unless `--generate-template`) | Path to JSON file describing infrastructure configuration |
| `--generate-template` | No | Generate blank infrastructure configuration template |
| `--frameworks <list>` | No | Comma-separated framework filter (e.g., `soc2,iso27001,hipaa`); uses identifiers: `soc2`, `iso27001`, `hipaa`, `gdpr`, `pci_dss`, `nis2`, `dora`, `nist_csf`, `fedramp`, `ccpa` |
| `--format <fmt>` | No | Output format: `json` (default) or `markdown` |
| `--output <file>` | No | Export report to specified file path |

**Output:** Per-domain scores (0-100), overall weighted score, per-control pass/fail/unknown status, framework-mapped findings with severity, and remediation recommendations.

### dns_security_checker.py

DNS-specific security audit validating email authentication, DNSSEC, certificate authority authorization, and subdomain takeover risk.

| Flag | Required | Description |
|------|----------|-------------|
| `--domain <domain>` | Yes | Domain name to audit (e.g., `example.com`) |
| `--output <file>` | No | Export report to specified file path |
| `--format <fmt>` | No | Output format: `json` (default) or `markdown` |
| `--subdomains <list>` | No | Comma-separated subdomains to check for takeover risk (e.g., `sub1,sub2,sub3`) |
| `--dkim-selectors <list>` | No | Comma-separated DKIM selectors to validate (e.g., `google,selector1`) |

**Checks:** SPF record syntax and lookup count, DKIM record presence and key strength, DMARC policy and reporting configuration, DNSSEC validation, CAA record authorization, MTA-STS policy, and subdomain takeover risk assessment.

### access_control_auditor.py

Access control audit covering identity, authentication, authorization, and privileged access management.

| Flag | Required | Description |
|------|----------|-------------|
| `--config <file>` | Yes (unless `--generate-template`) | Path to JSON file describing access control configuration |
| `--generate-template` | No | Generate blank access control configuration template |
| `--format <fmt>` | No | Output format: `json` (default) or `markdown` |
| `--output <file>` | No | Export report to specified file path |

**Audit Categories:** Identity Provider (IdP) configuration, SSO/SCIM provisioning, MFA enforcement, hardware security key (FIDO2/YubiKey) deployment, Privileged Access Management (PAM), RBAC, service account governance, SSH key management, API key management, and Zero Trust architecture.

---

**Last Updated:** March 2026
**Version:** 1.0.0
**Total Controls:** 250+ across 11 audit domains
**Frameworks Covered:** SOC 2, ISO 27001, HIPAA, GDPR, PCI-DSS, NIS2, DORA, NIST CSF, FedRAMP, CCPA
