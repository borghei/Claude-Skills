#!/usr/bin/env python3
"""
Infrastructure Compliance Audit Runner

Comprehensive infrastructure security audit across 11 domains:
Cloud, DNS, TLS, Endpoints, Access Control, Network, Containers,
CI/CD, Secrets, Logging, and Physical Security.

Maps findings to compliance frameworks: SOC 2, ISO 27001, HIPAA,
GDPR, PCI-DSS, NIS2, DORA, NIST CSF, FedRAMP, CCPA.

Usage:
    python infra_audit_runner.py --config infrastructure.json --output report.json
    python infra_audit_runner.py --config infrastructure.json --frameworks soc2,iso27001 --format markdown
    python infra_audit_runner.py --generate-template --output template.json
"""

import argparse
import json
import sys
import os
from datetime import datetime, timezone
from collections import defaultdict

# ---------------------------------------------------------------------------
# Control Registry — every auditable control lives here
# ---------------------------------------------------------------------------

SEVERITY_WEIGHTS = {
    "Critical": 10,
    "High": 5,
    "Medium": 2,
    "Low": 1,
    "Info": 0,
}

DOMAIN_WEIGHTS = {
    "cloud_infrastructure": 0.15,
    "access_control": 0.15,
    "network_security": 0.12,
    "secrets_management": 0.10,
    "logging_monitoring": 0.10,
    "cicd_pipeline": 0.08,
    "container_kubernetes": 0.08,
    "endpoint_security": 0.07,
    "tls_ssl": 0.05,
    "dns_security": 0.05,
    "physical_security": 0.05,
}

FRAMEWORK_LABELS = {
    "soc2": "SOC 2 Type II",
    "iso27001": "ISO 27001:2022",
    "hipaa": "HIPAA",
    "gdpr": "GDPR",
    "pci_dss": "PCI-DSS v4.0",
    "nis2": "NIS2 Directive",
    "dora": "DORA",
    "nist_csf": "NIST CSF 2.0",
    "fedramp": "FedRAMP",
    "ccpa": "CCPA/CPRA",
}

# Master control definitions keyed by check_id
# Each control: (domain, check_id, title, severity, frameworks[], check_key, expected)
CONTROLS = [
    # --- Cloud Infrastructure: AWS IAM ---
    ("cloud_infrastructure", "AWS-IAM-001", "Root account has MFA enabled", "Critical",
     ["soc2", "iso27001", "pci_dss", "nist_csf", "hipaa", "fedramp"],
     "aws.iam.root_mfa_enabled", True),
    ("cloud_infrastructure", "AWS-IAM-002", "Root account has no access keys", "Critical",
     ["soc2", "iso27001", "pci_dss", "nist_csf"],
     "aws.iam.root_access_keys", False),
    ("cloud_infrastructure", "AWS-IAM-003", "No wildcard IAM policies (Action:* Resource:*)", "Critical",
     ["soc2", "iso27001", "pci_dss", "nist_csf"],
     "aws.iam.wildcard_policies_exist", False),
    ("cloud_infrastructure", "AWS-IAM-004", "All IAM users have MFA enabled", "High",
     ["soc2", "iso27001", "pci_dss", "hipaa"],
     "aws.iam.all_users_mfa", True),
    ("cloud_infrastructure", "AWS-IAM-005", "Password policy minimum 14 characters", "Medium",
     ["soc2", "iso27001", "pci_dss", "nist_csf"],
     "aws.iam.min_password_length", 14),
    ("cloud_infrastructure", "AWS-IAM-007", "Unused credentials (>90d) disabled", "Medium",
     ["soc2", "iso27001", "pci_dss"],
     "aws.iam.unused_credentials_disabled", True),
    ("cloud_infrastructure", "AWS-IAM-008", "IAM Access Analyzer enabled", "Medium",
     ["soc2", "iso27001"],
     "aws.iam.access_analyzer_enabled", True),

    # --- Cloud Infrastructure: AWS S3 ---
    ("cloud_infrastructure", "AWS-S3-001", "S3 Block Public Access at account level", "Critical",
     ["soc2", "iso27001", "pci_dss", "hipaa", "gdpr"],
     "aws.s3.account_block_public_access", True),
    ("cloud_infrastructure", "AWS-S3-002", "No S3 buckets with public ACLs or policies", "Critical",
     ["soc2", "iso27001", "pci_dss", "hipaa"],
     "aws.s3.public_buckets_exist", False),
    ("cloud_infrastructure", "AWS-S3-003", "Server-side encryption enabled", "High",
     ["soc2", "iso27001", "pci_dss", "hipaa", "gdpr"],
     "aws.s3.encryption_enabled", True),
    ("cloud_infrastructure", "AWS-S3-005", "Access logging enabled for all buckets", "Medium",
     ["soc2", "iso27001", "pci_dss"],
     "aws.s3.access_logging_enabled", True),

    # --- Cloud Infrastructure: AWS VPC ---
    ("cloud_infrastructure", "AWS-VPC-001", "VPC Flow Logs enabled", "High",
     ["soc2", "iso27001", "pci_dss", "nist_csf"],
     "aws.vpc.flow_logs_enabled", True),
    ("cloud_infrastructure", "AWS-VPC-003", "No SG allows 0.0.0.0/0 on SSH/RDP", "Critical",
     ["soc2", "iso27001", "pci_dss", "nist_csf"],
     "aws.vpc.open_ssh_rdp", False),
    ("cloud_infrastructure", "AWS-VPC-004", "Private subnets for databases", "High",
     ["soc2", "iso27001", "pci_dss"],
     "aws.vpc.db_private_subnets", True),

    # --- Cloud Infrastructure: AWS RDS ---
    ("cloud_infrastructure", "AWS-RDS-001", "RDS encryption at rest enabled", "High",
     ["soc2", "iso27001", "pci_dss", "hipaa"],
     "aws.rds.encryption_at_rest", True),
    ("cloud_infrastructure", "AWS-RDS-002", "RDS SSL/TLS enforced", "High",
     ["soc2", "iso27001", "pci_dss"],
     "aws.rds.ssl_enforced", True),
    ("cloud_infrastructure", "AWS-RDS-005", "RDS not publicly accessible", "Critical",
     ["soc2", "pci_dss"],
     "aws.rds.publicly_accessible", False),

    # --- Cloud Infrastructure: AWS CloudTrail ---
    ("cloud_infrastructure", "AWS-CT-001", "CloudTrail enabled in all regions", "Critical",
     ["soc2", "iso27001", "pci_dss", "hipaa", "nist_csf", "fedramp"],
     "aws.cloudtrail.enabled_all_regions", True),
    ("cloud_infrastructure", "AWS-CT-002", "CloudTrail log file validation enabled", "High",
     ["soc2", "iso27001", "pci_dss"],
     "aws.cloudtrail.log_validation", True),
    ("cloud_infrastructure", "AWS-CT-005", "GuardDuty enabled", "High",
     ["soc2", "nist_csf"],
     "aws.guardduty.enabled", True),
    ("cloud_infrastructure", "AWS-CT-007", "AWS Config enabled", "High",
     ["soc2", "iso27001", "nist_csf", "fedramp"],
     "aws.config.enabled", True),

    # --- Cloud Infrastructure: AWS KMS ---
    ("cloud_infrastructure", "AWS-KMS-001", "Customer-managed KMS keys for sensitive data", "High",
     ["soc2", "iso27001", "pci_dss"],
     "aws.kms.customer_managed_keys", True),
    ("cloud_infrastructure", "AWS-KMS-002", "KMS key rotation enabled", "Medium",
     ["soc2", "iso27001", "pci_dss"],
     "aws.kms.key_rotation_enabled", True),

    # --- Cloud Infrastructure: Azure ---
    ("cloud_infrastructure", "AZ-AD-001", "Global Admin MFA enforced", "Critical",
     ["soc2", "iso27001", "pci_dss"],
     "azure.ad.global_admin_mfa", True),
    ("cloud_infrastructure", "AZ-AD-005", "PIM enabled for admin roles", "High",
     ["soc2", "iso27001"],
     "azure.ad.pim_enabled", True),
    ("cloud_infrastructure", "AZ-NET-001", "NSG least privilege (no allow-all inbound)", "High",
     ["soc2", "iso27001", "pci_dss"],
     "azure.network.nsg_least_privilege", True),
    ("cloud_infrastructure", "AZ-KV-002", "Key Vault soft delete + purge protection", "High",
     ["soc2", "iso27001"],
     "azure.keyvault.soft_delete_purge_protection", True),
    ("cloud_infrastructure", "AZ-MON-005", "Microsoft Defender for Cloud enabled", "High",
     ["soc2", "nist_csf"],
     "azure.defender.enabled", True),
    ("cloud_infrastructure", "AZ-ST-002", "Storage account public access disabled", "Critical",
     ["soc2", "iso27001"],
     "azure.storage.public_access_disabled", True),

    # --- Cloud Infrastructure: GCP ---
    ("cloud_infrastructure", "GCP-IAM-002", "No service accounts with Owner/Editor roles", "Critical",
     ["soc2", "iso27001"],
     "gcp.iam.no_owner_editor_sa", True),
    ("cloud_infrastructure", "GCP-VPC-005", "No firewall rules allow 0.0.0.0/0 SSH/RDP", "Critical",
     ["soc2", "pci_dss"],
     "gcp.vpc.no_open_ssh_rdp", True),
    ("cloud_infrastructure", "GCP-SEC-001", "Security Command Center enabled", "High",
     ["soc2", "nist_csf"],
     "gcp.scc.enabled", True),
    ("cloud_infrastructure", "GCP-SEC-003", "Cloud Audit Logs enabled", "High",
     ["soc2", "iso27001"],
     "gcp.audit_logs.enabled", True),

    # --- DNS Security ---
    ("dns_security", "DNS-SPF-001", "SPF record exists", "High",
     ["soc2", "iso27001", "nist_csf"],
     "dns.spf.exists", True),
    ("dns_security", "DNS-SPF-002", "SPF uses -all (hard fail)", "High",
     ["soc2", "iso27001"],
     "dns.spf.hard_fail", True),
    ("dns_security", "DNS-SPF-003", "SPF < 10 DNS lookups", "Medium",
     ["soc2"],
     "dns.spf.lookup_count_ok", True),
    ("dns_security", "DNS-SPF-004", "SPF does not use +all", "Critical",
     ["soc2", "iso27001"],
     "dns.spf.no_plus_all", True),
    ("dns_security", "DNS-DKIM-001", "DKIM record exists", "High",
     ["soc2", "iso27001"],
     "dns.dkim.exists", True),
    ("dns_security", "DNS-DKIM-002", "DKIM key minimum 2048-bit", "High",
     ["soc2", "iso27001"],
     "dns.dkim.min_2048_bit", True),
    ("dns_security", "DNS-DMARC-001", "DMARC record exists", "High",
     ["soc2", "iso27001", "nist_csf"],
     "dns.dmarc.exists", True),
    ("dns_security", "DNS-DMARC-002", "DMARC policy is p=reject", "High",
     ["soc2", "iso27001"],
     "dns.dmarc.policy_reject", True),
    ("dns_security", "DNS-DMARC-003", "DMARC aggregate reporting configured", "Medium",
     ["soc2", "iso27001"],
     "dns.dmarc.rua_configured", True),
    ("dns_security", "DNS-SEC-001", "DNSSEC signing enabled", "High",
     ["soc2", "iso27001", "nist_csf"],
     "dns.dnssec.enabled", True),
    ("dns_security", "DNS-CAA-001", "CAA record exists", "High",
     ["soc2", "iso27001"],
     "dns.caa.exists", True),
    ("dns_security", "DNS-MTA-001", "MTA-STS policy published", "Medium",
     ["iso27001"],
     "dns.mta_sts.enabled", True),
    ("dns_security", "DNS-DOM-001", "Registrar lock enabled", "High",
     ["soc2", "iso27001"],
     "dns.domain.registrar_lock", True),
    ("dns_security", "DNS-DOM-003", "2FA on registrar account", "Critical",
     ["soc2", "iso27001"],
     "dns.domain.registrar_2fa", True),
    ("dns_security", "DNS-DOM-005", "Subdomain inventory maintained", "High",
     ["soc2", "iso27001"],
     "dns.domain.subdomain_inventory", True),
    ("dns_security", "DNS-DOM-006", "No dangling CNAME records", "High",
     ["soc2"],
     "dns.domain.no_dangling_cnames", True),

    # --- TLS/SSL ---
    ("tls_ssl", "TLS-PROTO-001", "TLS 1.2 minimum (1.0/1.1 disabled)", "Critical",
     ["soc2", "iso27001", "pci_dss", "nist_csf", "hipaa"],
     "tls.min_version_1_2", True),
    ("tls_ssl", "TLS-PROTO-002", "TLS 1.3 preferred", "Medium",
     ["soc2", "nist_csf"],
     "tls.tls_1_3_preferred", True),
    ("tls_ssl", "TLS-CIPHER-001", "Forward secrecy enabled (ECDHE/DHE)", "High",
     ["soc2", "iso27001", "pci_dss"],
     "tls.forward_secrecy", True),
    ("tls_ssl", "TLS-CIPHER-002", "AEAD cipher suites only", "High",
     ["soc2", "pci_dss"],
     "tls.aead_only", True),
    ("tls_ssl", "TLS-CIPHER-003", "No weak ciphers (RC4, 3DES, NULL, EXPORT)", "Critical",
     ["pci_dss", "nist_csf"],
     "tls.no_weak_ciphers", True),
    ("tls_ssl", "TLS-HSTS-001", "HSTS max-age >= 1 year", "High",
     ["soc2", "iso27001", "pci_dss", "nist_csf"],
     "tls.hsts.max_age_1_year", True),
    ("tls_ssl", "TLS-HSTS-002", "HSTS includeSubDomains", "High",
     ["soc2"],
     "tls.hsts.include_subdomains", True),
    ("tls_ssl", "TLS-HSTS-003", "HSTS preload", "Medium",
     ["soc2"],
     "tls.hsts.preload", True),
    ("tls_ssl", "TLS-CERT-001", "Certificates from trusted CA", "High",
     ["soc2", "iso27001", "pci_dss"],
     "tls.cert.trusted_ca", True),
    ("tls_ssl", "TLS-CERT-002", "Automated certificate renewal (ACME)", "Medium",
     ["soc2"],
     "tls.cert.automated_renewal", True),
    ("tls_ssl", "TLS-CERT-003", "Certificate expiration monitoring", "High",
     ["soc2", "iso27001"],
     "tls.cert.expiry_monitoring", True),
    ("tls_ssl", "TLS-CERT-007", "OCSP stapling enabled", "Medium",
     ["soc2"],
     "tls.cert.ocsp_stapling", True),
    ("tls_ssl", "TLS-INT-001", "mTLS for service-to-service", "High",
     ["soc2", "iso27001", "pci_dss"],
     "tls.internal.mtls", True),
    ("tls_ssl", "TLS-INT-004", "Database connections use TLS", "High",
     ["soc2", "pci_dss", "hipaa"],
     "tls.internal.db_tls", True),

    # --- Endpoint Security ---
    ("endpoint_security", "EP-MDM-001", "MDM solution deployed", "High",
     ["soc2", "iso27001", "hipaa", "nist_csf"],
     "endpoint.mdm.deployed", True),
    ("endpoint_security", "EP-MDM-002", "All corporate devices enrolled in MDM", "High",
     ["soc2", "iso27001"],
     "endpoint.mdm.all_enrolled", True),
    ("endpoint_security", "EP-ENC-001", "Full disk encryption on all endpoints", "Critical",
     ["soc2", "iso27001", "pci_dss", "hipaa", "gdpr", "nist_csf"],
     "endpoint.encryption.full_disk", True),
    ("endpoint_security", "EP-ENC-002", "Encryption recovery keys escrowed", "High",
     ["soc2", "iso27001"],
     "endpoint.encryption.keys_escrowed", True),
    ("endpoint_security", "EP-AV-001", "EDR deployed on all endpoints", "High",
     ["soc2", "iso27001", "pci_dss", "hipaa", "nist_csf"],
     "endpoint.edr.deployed", True),
    ("endpoint_security", "EP-AV-002", "Real-time protection enabled", "High",
     ["soc2", "pci_dss"],
     "endpoint.edr.realtime_protection", True),
    ("endpoint_security", "EP-PATCH-001", "Critical patches within 24h", "Critical",
     ["soc2", "iso27001", "pci_dss", "nist_csf"],
     "endpoint.patching.critical_24h", True),
    ("endpoint_security", "EP-PATCH-002", "High patches within 72h", "High",
     ["soc2", "iso27001", "pci_dss"],
     "endpoint.patching.high_72h", True),
    ("endpoint_security", "EP-LOCK-001", "Screen lock after 5 min inactivity", "Medium",
     ["soc2", "iso27001", "pci_dss", "hipaa"],
     "endpoint.screen_lock.5_min", True),
    ("endpoint_security", "EP-USB-001", "USB storage blocked or controlled", "Medium",
     ["soc2", "iso27001", "pci_dss"],
     "endpoint.usb.controlled", True),
    ("endpoint_security", "EP-WIPE-001", "Remote wipe capability verified", "High",
     ["soc2", "iso27001", "hipaa"],
     "endpoint.remote_wipe.enabled", True),
    ("endpoint_security", "EP-FW-001", "Host-based firewall enabled", "Medium",
     ["soc2", "iso27001", "pci_dss"],
     "endpoint.firewall.enabled", True),

    # --- Access Control ---
    ("access_control", "AC-IDP-001", "Centralized IdP deployed", "High",
     ["soc2", "iso27001", "pci_dss", "hipaa", "nist_csf", "fedramp"],
     "access.idp.deployed", True),
    ("access_control", "AC-IDP-003", "IdP admin MFA with hardware key", "Critical",
     ["soc2", "iso27001", "pci_dss"],
     "access.idp.admin_hardware_mfa", True),
    ("access_control", "AC-SSO-001", "SSO via SAML 2.0 or OIDC", "High",
     ["soc2", "iso27001", "nist_csf"],
     "access.sso.saml_oidc", True),
    ("access_control", "AC-SSO-004", "SCIM provisioning enabled", "High",
     ["soc2", "iso27001", "nist_csf"],
     "access.sso.scim_enabled", True),
    ("access_control", "AC-SSO-005", "Deprovisioning revokes SSO sessions", "High",
     ["soc2", "iso27001"],
     "access.sso.deprovision_revoke", True),
    ("access_control", "AC-MFA-001", "MFA enforced for ALL accounts", "Critical",
     ["soc2", "iso27001", "pci_dss", "hipaa", "nist_csf", "gdpr", "nis2", "dora", "fedramp"],
     "access.mfa.enforced_all", True),
    ("access_control", "AC-MFA-002", "Phishing-resistant MFA for privileged accounts", "Critical",
     ["soc2", "iso27001", "nist_csf", "fedramp"],
     "access.mfa.phishing_resistant_admins", True),
    ("access_control", "AC-MFA-003", "SMS-based MFA prohibited", "High",
     ["soc2", "nist_csf"],
     "access.mfa.sms_prohibited", True),
    ("access_control", "AC-MFA-005", "Hardware security keys for all admins", "High",
     ["soc2", "iso27001", "nist_csf"],
     "access.mfa.hardware_keys_admins", True),
    ("access_control", "AC-PAM-001", "JIT access for privileged roles", "High",
     ["soc2", "iso27001", "pci_dss", "nist_csf"],
     "access.pam.jit_enabled", True),
    ("access_control", "AC-PAM-004", "Privileged sessions recorded", "High",
     ["soc2", "iso27001", "pci_dss"],
     "access.pam.session_recording", True),
    ("access_control", "AC-PAM-006", "Privileged account inventory reviewed quarterly", "High",
     ["soc2", "iso27001", "pci_dss"],
     "access.pam.inventory_reviewed", True),
    ("access_control", "AC-RBAC-001", "RBAC model documented", "High",
     ["soc2", "iso27001", "pci_dss", "hipaa", "nist_csf"],
     "access.rbac.documented", True),
    ("access_control", "AC-RBAC-002", "Access recertification quarterly", "High",
     ["soc2", "iso27001", "pci_dss"],
     "access.rbac.quarterly_review", True),
    ("access_control", "AC-RBAC-003", "Separation of duties enforced", "High",
     ["soc2", "iso27001", "pci_dss"],
     "access.rbac.sod_enforced", True),
    ("access_control", "AC-SVC-001", "No shared service account credentials", "Critical",
     ["soc2", "iso27001", "pci_dss"],
     "access.service_accounts.no_shared_creds", True),
    ("access_control", "AC-SVC-003", "Service account credentials rotate <=90 days", "High",
     ["soc2", "iso27001", "pci_dss"],
     "access.service_accounts.rotation_90d", True),
    ("access_control", "AC-SVC-004", "Service account inventory maintained", "High",
     ["soc2", "iso27001"],
     "access.service_accounts.inventory", True),
    ("access_control", "AC-SSH-001", "SSH keys ED25519 or RSA >= 4096", "High",
     ["soc2", "iso27001"],
     "access.ssh.strong_keys", True),
    ("access_control", "AC-SSH-006", "Root SSH login disabled", "High",
     ["soc2", "iso27001", "pci_dss"],
     "access.ssh.root_login_disabled", True),
    ("access_control", "AC-SSH-007", "SSH password auth disabled", "High",
     ["soc2", "iso27001"],
     "access.ssh.password_auth_disabled", True),
    ("access_control", "AC-ZT-001", "Identity-based access (verify user+device+context)", "High",
     ["soc2", "iso27001", "nist_csf"],
     "access.zero_trust.identity_based", True),
    ("access_control", "AC-ZT-002", "Device posture checked", "High",
     ["soc2", "iso27001"],
     "access.zero_trust.device_posture", True),

    # --- Network Security ---
    ("network_security", "NET-FW-001", "Default deny firewall policy", "Critical",
     ["soc2", "iso27001", "pci_dss", "nist_csf"],
     "network.firewall.default_deny", True),
    ("network_security", "NET-FW-002", "Egress filtering enabled", "High",
     ["soc2", "iso27001", "pci_dss"],
     "network.firewall.egress_filtering", True),
    ("network_security", "NET-FW-005", "No any/any firewall rules", "Critical",
     ["soc2", "pci_dss"],
     "network.firewall.no_any_any", True),
    ("network_security", "NET-SEG-001", "Network segmentation (prod/staging/dev)", "High",
     ["soc2", "iso27001", "pci_dss", "hipaa"],
     "network.segmentation.env_isolation", True),
    ("network_security", "NET-SEG-003", "Database tier isolated", "High",
     ["soc2", "iso27001", "pci_dss"],
     "network.segmentation.db_isolated", True),
    ("network_security", "NET-WAF-001", "WAF deployed for public web apps", "High",
     ["soc2", "iso27001", "pci_dss", "nist_csf"],
     "network.waf.deployed", True),
    ("network_security", "NET-WAF-002", "OWASP Top 10 rules enabled", "High",
     ["soc2", "pci_dss"],
     "network.waf.owasp_rules", True),
    ("network_security", "NET-WAF-004", "WAF in blocking mode", "High",
     ["soc2", "pci_dss"],
     "network.waf.blocking_mode", True),
    ("network_security", "NET-DDOS-001", "DDoS protection enabled", "High",
     ["soc2", "iso27001", "nist_csf"],
     "network.ddos.protection_enabled", True),
    ("network_security", "NET-VPN-001", "VPN uses WireGuard or IPSec", "High",
     ["soc2", "iso27001", "pci_dss", "nist_csf"],
     "network.vpn.secure_protocol", True),
    ("network_security", "NET-VPN-003", "VPN requires MFA", "High",
     ["soc2", "iso27001", "pci_dss"],
     "network.vpn.mfa_required", True),
    ("network_security", "NET-IDS-001", "IDS/IPS at network perimeter", "High",
     ["soc2", "iso27001", "pci_dss", "nist_csf", "hipaa"],
     "network.ids.deployed", True),

    # --- Container/Kubernetes ---
    ("container_kubernetes", "K8S-IMG-003", "No running as root in containers", "High",
     ["soc2", "iso27001", "pci_dss"],
     "k8s.images.no_root", True),
    ("container_kubernetes", "K8S-IMG-004", "Container images scanned for vulnerabilities", "High",
     ["soc2", "iso27001", "pci_dss", "nist_csf"],
     "k8s.images.vulnerability_scanning", True),
    ("container_kubernetes", "K8S-IMG-005", "No secrets in container images", "Critical",
     ["soc2", "pci_dss"],
     "k8s.images.no_secrets", True),
    ("container_kubernetes", "K8S-IMG-007", "Image signing verified", "High",
     ["soc2", "nist_csf"],
     "k8s.images.signing_verified", True),
    ("container_kubernetes", "K8S-RT-004", "No privileged containers", "Critical",
     ["soc2", "iso27001", "pci_dss"],
     "k8s.runtime.no_privileged", True),
    ("container_kubernetes", "K8S-RBAC-001", "K8s RBAC least privilege", "High",
     ["soc2", "iso27001", "pci_dss"],
     "k8s.rbac.least_privilege", True),
    ("container_kubernetes", "K8S-RBAC-002", "No cluster-admin for app workloads", "Critical",
     ["soc2", "iso27001"],
     "k8s.rbac.no_cluster_admin_apps", True),
    ("container_kubernetes", "K8S-NET-001", "Network Policies for all namespaces", "High",
     ["soc2", "iso27001", "pci_dss"],
     "k8s.network.policies_defined", True),
    ("container_kubernetes", "K8S-NET-002", "Default deny network policy", "High",
     ["soc2", "pci_dss"],
     "k8s.network.default_deny", True),
    ("container_kubernetes", "K8S-POD-001", "Pod Security Standards enforced (restricted)", "High",
     ["soc2", "iso27001"],
     "k8s.pods.security_standards", True),
    ("container_kubernetes", "K8S-SEC-001", "External Secrets Operator for secrets", "High",
     ["soc2", "pci_dss"],
     "k8s.secrets.external_operator", True),
    ("container_kubernetes", "K8S-SEC-002", "Etcd encrypted at rest", "High",
     ["soc2", "iso27001"],
     "k8s.secrets.etcd_encrypted", True),
    ("container_kubernetes", "K8S-ADM-001", "Admission controllers (OPA/Kyverno)", "High",
     ["soc2", "iso27001"],
     "k8s.admission.controllers_enabled", True),
    ("container_kubernetes", "K8S-REG-001", "Private container registry", "High",
     ["soc2", "iso27001"],
     "k8s.registry.private", True),

    # --- CI/CD Pipeline ---
    ("cicd_pipeline", "CICD-SCM-001", "Branch protection on main/production", "High",
     ["soc2", "iso27001", "pci_dss", "nist_csf"],
     "cicd.scm.branch_protection", True),
    ("cicd_pipeline", "CICD-SCM-002", "Minimum 2 approvals for production merges", "Medium",
     ["soc2", "iso27001", "pci_dss"],
     "cicd.scm.min_2_approvals", True),
    ("cicd_pipeline", "CICD-SCM-004", "Signed commits enforced", "Medium",
     ["soc2", "iso27001"],
     "cicd.scm.signed_commits", True),
    ("cicd_pipeline", "CICD-SCM-005", "Force push prohibited on protected branches", "High",
     ["soc2", "iso27001"],
     "cicd.scm.no_force_push", True),
    ("cicd_pipeline", "CICD-SCAN-001", "Secret scanning enabled", "Critical",
     ["soc2", "iso27001", "pci_dss"],
     "cicd.scanning.secret_scanning", True),
    ("cicd_pipeline", "CICD-SCAN-002", "Pre-commit hooks for secrets", "High",
     ["soc2", "pci_dss"],
     "cicd.scanning.precommit_hooks", True),
    ("cicd_pipeline", "CICD-SCAN-003", "Dependency scanning automated", "High",
     ["soc2", "iso27001", "pci_dss", "nist_csf"],
     "cicd.scanning.dependency_scanning", True),
    ("cicd_pipeline", "CICD-SCAN-004", "SAST in CI pipeline", "High",
     ["soc2", "iso27001", "pci_dss", "nist_csf"],
     "cicd.scanning.sast", True),
    ("cicd_pipeline", "CICD-SCAN-005", "DAST for staging", "Medium",
     ["soc2", "iso27001", "pci_dss"],
     "cicd.scanning.dast", True),
    ("cicd_pipeline", "CICD-SCAN-007", "Container image scanning in CI", "High",
     ["soc2", "iso27001", "pci_dss"],
     "cicd.scanning.container_images", True),
    ("cicd_pipeline", "CICD-SCAN-008", "IaC scanning (tfsec/checkov/KICS)", "High",
     ["soc2", "iso27001"],
     "cicd.scanning.iac", True),
    ("cicd_pipeline", "CICD-SC-001", "SBOM generated for releases", "High",
     ["soc2", "nist_csf", "nis2"],
     "cicd.supply_chain.sbom", True),
    ("cicd_pipeline", "CICD-SC-002", "Artifact signing (Sigstore/cosign)", "High",
     ["soc2", "nist_csf"],
     "cicd.supply_chain.artifact_signing", True),
    ("cicd_pipeline", "CICD-DEP-001", "Deployment approval gates for production", "High",
     ["soc2", "iso27001", "pci_dss"],
     "cicd.deploy.approval_gates", True),
    ("cicd_pipeline", "CICD-DEP-002", "Production deployments audited", "High",
     ["soc2", "iso27001", "pci_dss"],
     "cicd.deploy.audit_trail", True),
    ("cicd_pipeline", "CICD-DEP-004", "Deploy creds via secrets manager", "High",
     ["soc2", "pci_dss"],
     "cicd.deploy.secrets_manager", True),

    # --- Secrets Management ---
    ("secrets_management", "SEC-MGR-001", "Centralized secrets manager deployed", "High",
     ["soc2", "iso27001", "pci_dss", "hipaa", "nist_csf"],
     "secrets.manager.deployed", True),
    ("secrets_management", "SEC-MGR-003", "Secrets access audited", "High",
     ["soc2", "iso27001", "pci_dss"],
     "secrets.manager.access_audited", True),
    ("secrets_management", "SEC-MGR-004", "Dynamic secrets where possible", "Medium",
     ["soc2", "iso27001"],
     "secrets.manager.dynamic_secrets", True),
    ("secrets_management", "SEC-ROT-001", "DB credentials rotate <=90 days", "High",
     ["soc2", "iso27001", "pci_dss"],
     "secrets.rotation.db_90d", True),
    ("secrets_management", "SEC-ROT-002", "API keys rotate <=90 days", "High",
     ["soc2", "iso27001"],
     "secrets.rotation.api_keys_90d", True),
    ("secrets_management", "SEC-ROT-006", "Rotation is automated", "Medium",
     ["soc2"],
     "secrets.rotation.automated", True),
    ("secrets_management", "SEC-CODE-001", "No secrets in source code", "Critical",
     ["soc2", "iso27001", "pci_dss"],
     "secrets.code.no_secrets_in_code", True),
    ("secrets_management", "SEC-CODE-002", ".env files in .gitignore", "High",
     ["soc2", "pci_dss"],
     "secrets.code.env_gitignored", True),
    ("secrets_management", "SEC-CODE-003", "Pre-commit hooks block secrets", "High",
     ["soc2", "pci_dss"],
     "secrets.code.precommit_hooks", True),
    ("secrets_management", "SEC-CODE-005", "Historical leaked secrets rotated", "Critical",
     ["soc2"],
     "secrets.code.historical_rotated", True),
    ("secrets_management", "SEC-HSM-001", "HSM for root CA keys", "High",
     ["soc2", "iso27001", "pci_dss", "fedramp"],
     "secrets.hsm.root_ca_keys", True),

    # --- Logging & Monitoring ---
    ("logging_monitoring", "LOG-CEN-001", "Centralized logging platform deployed", "High",
     ["soc2", "iso27001", "pci_dss", "hipaa", "nist_csf", "fedramp"],
     "logging.centralized.deployed", True),
    ("logging_monitoring", "LOG-CEN-002", "Logs cover auth, authz, data access, system changes", "High",
     ["soc2", "iso27001", "pci_dss"],
     "logging.centralized.coverage", True),
    ("logging_monitoring", "LOG-CEN-003", "Logs include timestamp, source, user, action, result, IP", "High",
     ["soc2", "iso27001", "pci_dss"],
     "logging.centralized.required_fields", True),
    ("logging_monitoring", "LOG-CEN-005", "Time synchronized via NTP", "Medium",
     ["soc2", "pci_dss"],
     "logging.centralized.ntp_sync", True),
    ("logging_monitoring", "LOG-SIEM-001", "SIEM with correlation rules", "High",
     ["soc2", "iso27001", "pci_dss", "nist_csf", "nis2"],
     "logging.siem.deployed", True),
    ("logging_monitoring", "LOG-SIEM-003", "SIEM alerts have response procedures", "Medium",
     ["soc2", "iso27001", "nist_csf"],
     "logging.siem.response_procedures", True),
    ("logging_monitoring", "LOG-RET-001", "Log retention minimum 1 year", "High",
     ["soc2", "iso27001", "pci_dss", "hipaa"],
     "logging.retention.min_1_year", True),
    ("logging_monitoring", "LOG-RET-002", "Logs immutable", "High",
     ["soc2", "iso27001", "pci_dss"],
     "logging.retention.immutable", True),
    ("logging_monitoring", "LOG-ALERT-001", "Alerts for failed auth, priv esc, data exfil", "High",
     ["soc2", "iso27001", "pci_dss", "nist_csf"],
     "logging.alerting.security_alerts", True),
    ("logging_monitoring", "LOG-ALERT-002", "Alert escalation matrix documented", "Medium",
     ["soc2", "iso27001"],
     "logging.alerting.escalation_matrix", True),
    ("logging_monitoring", "LOG-ALERT-006", "File integrity monitoring deployed", "High",
     ["soc2", "iso27001", "pci_dss"],
     "logging.alerting.fim_deployed", True),

    # --- Physical Security ---
    ("physical_security", "PHYS-DC-001", "Cloud provider SOC 2 report reviewed annually", "High",
     ["soc2", "iso27001", "pci_dss"],
     "physical.datacenter.soc2_report_reviewed", True),
    ("physical_security", "PHYS-DC-002", "Data center physical access restricted", "High",
     ["soc2", "iso27001", "pci_dss"],
     "physical.datacenter.access_restricted", True),
    ("physical_security", "PHYS-OFF-001", "Badge access for office entry", "Medium",
     ["soc2", "iso27001"],
     "physical.office.badge_access", True),
    ("physical_security", "PHYS-OFF-004", "Server/network rooms locked", "Medium",
     ["soc2", "iso27001", "pci_dss"],
     "physical.office.server_room_locked", True),
    ("physical_security", "PHYS-DISP-001", "Media disposal follows NIST 800-88", "High",
     ["soc2", "iso27001", "pci_dss", "hipaa", "nist_csf"],
     "physical.disposal.nist_800_88", True),
    ("physical_security", "PHYS-DISP-002", "Certificate of destruction obtained", "High",
     ["soc2", "iso27001", "pci_dss"],
     "physical.disposal.certificate", True),
    ("physical_security", "PHYS-DISP-004", "Electronic media cryptographically erased", "High",
     ["soc2", "pci_dss", "hipaa"],
     "physical.disposal.crypto_erase", True),
]


def get_nested_value(data, dotted_key):
    """Retrieve a value from nested dict using dot notation."""
    keys = dotted_key.split(".")
    current = data
    for k in keys:
        if isinstance(current, dict) and k in current:
            current = current[k]
        else:
            return None
    return current


def evaluate_control(config, check_key, expected):
    """
    Evaluate a single control against the config.

    Returns:
        "pass" — control is satisfied
        "fail" — control is violated
        "not_applicable" — key not present in config (domain not in scope)
    """
    value = get_nested_value(config, check_key)
    if value is None:
        return "not_applicable"

    if isinstance(expected, bool):
        return "pass" if bool(value) == expected else "fail"
    elif isinstance(expected, int):
        try:
            return "pass" if int(value) >= expected else "fail"
        except (ValueError, TypeError):
            return "fail"
    else:
        return "pass" if value == expected else "fail"


REMEDIATION_MAP = {
    "aws.iam.root_mfa_enabled": "Enable MFA on the AWS root account. Use a hardware security key (YubiKey) for maximum protection. Go to IAM > Security credentials > MFA.",
    "aws.iam.root_access_keys": "Delete all access keys from the root account. Use IAM users/roles for programmatic access. AWS Console > IAM > Security credentials.",
    "aws.iam.wildcard_policies_exist": "Review and replace IAM policies with Action:* Resource:*. Apply least-privilege permissions per service and resource.",
    "aws.iam.all_users_mfa": "Enforce MFA for all IAM users via IAM policy. Consider using AWS Organizations SCP to prevent API calls without MFA.",
    "aws.iam.min_password_length": "Update IAM password policy to require minimum 14 characters. IAM > Account settings > Password policy.",
    "aws.s3.account_block_public_access": "Enable S3 Block Public Access at account level. AWS Console > S3 > Block Public Access settings for this account.",
    "aws.s3.public_buckets_exist": "Identify and remediate S3 buckets with public ACLs or bucket policies. Use S3 Access Analyzer.",
    "aws.s3.encryption_enabled": "Enable default encryption (SSE-S3 minimum, SSE-KMS preferred) on all S3 buckets.",
    "aws.vpc.flow_logs_enabled": "Enable VPC Flow Logs for all VPCs. Send to CloudWatch Logs or S3 for analysis.",
    "aws.vpc.open_ssh_rdp": "Remove security group rules allowing 0.0.0.0/0 on ports 22 (SSH) and 3389 (RDP). Use bastion hosts or Systems Manager Session Manager.",
    "aws.cloudtrail.enabled_all_regions": "Enable CloudTrail in all regions with a single multi-region trail. Enable log file validation.",
    "aws.guardduty.enabled": "Enable GuardDuty in all regions. Configure findings export to S3 or Security Hub.",
    "aws.config.enabled": "Enable AWS Config with required rules in all active regions.",
    "aws.rds.encryption_at_rest": "Enable encryption at rest for RDS instances using KMS. Note: requires instance recreation for existing unencrypted instances.",
    "aws.rds.publicly_accessible": "Set RDS instances to not publicly accessible. Use private subnets and VPC security groups.",
    "azure.ad.global_admin_mfa": "Enforce MFA for all Global Admin accounts via Conditional Access policy. Require phishing-resistant MFA (FIDO2).",
    "azure.storage.public_access_disabled": "Disable public access on all Azure Storage accounts. Storage account > Configuration > Allow blob public access: Disabled.",
    "gcp.iam.no_owner_editor_sa": "Remove Owner and Editor roles from service accounts. Grant specific IAM roles per the principle of least privilege.",
    "gcp.vpc.no_open_ssh_rdp": "Remove firewall rules allowing 0.0.0.0/0 on ports 22 and 3389. Use IAP for SSH access.",
    "dns.spf.exists": "Add SPF TXT record: v=spf1 include:<your-email-providers> -all",
    "dns.spf.hard_fail": "Change SPF record from ~all to -all for hard fail enforcement.",
    "dns.spf.no_plus_all": "URGENT: Remove +all from SPF record. This allows ANY server to send email as your domain.",
    "dns.dkim.exists": "Configure DKIM signing with your email provider. Add the DKIM TXT record at selector._domainkey.yourdomain.com.",
    "dns.dmarc.exists": "Add DMARC record: _dmarc.yourdomain.com TXT 'v=DMARC1; p=reject; rua=mailto:dmarc@yourdomain.com'",
    "dns.dmarc.policy_reject": "Upgrade DMARC policy to p=reject. If currently p=none, follow rollout: none > quarantine > reject.",
    "dns.dnssec.enabled": "Enable DNSSEC signing at your DNS provider. Publish DS record in parent zone.",
    "dns.caa.exists": "Add CAA record restricting certificate issuance to authorized CAs: yourdomain.com CAA 0 issue 'letsencrypt.org'",
    "dns.domain.registrar_2fa": "Enable 2FA on your domain registrar account immediately. This is a critical control.",
    "tls.min_version_1_2": "Disable TLS 1.0 and 1.1. Configure minimum TLS version to 1.2 on all services.",
    "tls.no_weak_ciphers": "Remove RC4, 3DES, DES, NULL, and EXPORT cipher suites from TLS configuration.",
    "tls.hsts.max_age_1_year": "Add HSTS header: Strict-Transport-Security: max-age=31536000; includeSubDomains; preload",
    "endpoint.encryption.full_disk": "Enable full disk encryption on all endpoints: FileVault (macOS), BitLocker (Windows), LUKS (Linux).",
    "endpoint.edr.deployed": "Deploy EDR solution (CrowdStrike, SentinelOne, or Microsoft Defender for Endpoint) on all endpoints.",
    "endpoint.patching.critical_24h": "Implement automated patch management. Critical patches must be applied within 24 hours of release.",
    "access.mfa.enforced_all": "Enforce MFA for ALL user accounts with no exceptions. This is the single most impactful security control.",
    "access.mfa.phishing_resistant_admins": "Deploy FIDO2/WebAuthn hardware security keys for all admin accounts. Disable TOTP/SMS fallback for admins.",
    "access.mfa.sms_prohibited": "Disable SMS-based MFA. SMS is vulnerable to SIM swap attacks. Use TOTP, push, or FIDO2 instead.",
    "access.mfa.hardware_keys_admins": "Issue YubiKey 5 Series to all admin users. Require 2 keys per admin (primary + backup).",
    "access.service_accounts.no_shared_creds": "Assign unique credentials to each service account. Never share passwords or keys between services.",
    "network.firewall.default_deny": "Configure firewall with default deny (drop all) policy. Add explicit allow rules for required traffic only.",
    "network.firewall.no_any_any": "Remove all any/any firewall rules. Replace with specific source/destination/port rules.",
    "secrets.code.no_secrets_in_code": "Scan entire git history for secrets. Rotate any found secrets. Install pre-commit hooks (gitleaks) to prevent future leaks.",
    "secrets.code.historical_rotated": "All secrets found in git history MUST be rotated, even if the commit was reverted. Secrets in git history are considered compromised.",
    "logging.centralized.deployed": "Deploy centralized logging (ELK, Splunk, Datadog, or CloudWatch). Forward logs from all infrastructure.",
    "logging.siem.deployed": "Deploy SIEM with correlation rules for security event detection.",
    "logging.retention.min_1_year": "Configure log retention for minimum 365 days. PCI-DSS requires 3 months immediately available, 1 year total.",
    "logging.retention.immutable": "Configure write-once log storage. Use S3 Object Lock, immutable storage, or WORM-compliant storage.",
    "physical.disposal.nist_800_88": "Follow NIST SP 800-88 for media disposal. Use Clear for reuse, Purge for recycling, Destroy for disposal.",
    "k8s.images.no_secrets": "Remove all secrets from container images. Use Kubernetes Secrets, External Secrets Operator, or Vault sidecar.",
    "k8s.runtime.no_privileged": "Remove privileged: true from all container specs. Use specific Linux capabilities instead.",
    "k8s.rbac.no_cluster_admin_apps": "Remove cluster-admin ClusterRoleBindings from application workloads. Create namespace-scoped roles.",
    "cicd.scanning.secret_scanning": "Enable GitHub Advanced Security secret scanning or GitLab secret detection in all repositories.",
}


def get_remediation(check_key):
    """Return remediation guidance for a failed control."""
    return REMEDIATION_MAP.get(check_key, "Review the control requirements and implement the necessary configuration changes.")


def run_audit(config, filter_frameworks=None):
    """
    Run the full infrastructure audit against the provided configuration.

    Args:
        config: dict — infrastructure configuration
        filter_frameworks: list or None — if set, only report controls relevant to these frameworks

    Returns:
        dict with audit results
    """
    findings = []
    domain_stats = defaultdict(lambda: {"passed": 0, "failed": 0, "na": 0, "weighted_passed": 0, "weighted_total": 0})

    for domain, check_id, title, severity, frameworks, check_key, expected in CONTROLS:
        # Framework filter
        if filter_frameworks:
            if not any(f in frameworks for f in filter_frameworks):
                continue

        result = evaluate_control(config, check_key, expected)
        weight = SEVERITY_WEIGHTS.get(severity, 0)

        finding = {
            "check_id": check_id,
            "domain": domain,
            "title": title,
            "severity": severity,
            "frameworks": frameworks,
            "result": result,
            "check_key": check_key,
        }

        if result == "pass":
            domain_stats[domain]["passed"] += 1
            domain_stats[domain]["weighted_passed"] += weight
            domain_stats[domain]["weighted_total"] += weight
        elif result == "fail":
            domain_stats[domain]["failed"] += 1
            domain_stats[domain]["weighted_total"] += weight
            finding["remediation"] = get_remediation(check_key)
        else:
            domain_stats[domain]["na"] += 1

        findings.append(finding)

    # Calculate domain scores
    domain_scores = {}
    for domain, stats in domain_stats.items():
        total = stats["weighted_total"]
        if total > 0:
            score = round((stats["weighted_passed"] / total) * 100, 1)
        else:
            score = 100.0  # All N/A = perfect (nothing to audit)
        domain_scores[domain] = {
            "score": score,
            "passed": stats["passed"],
            "failed": stats["failed"],
            "not_applicable": stats["na"],
            "total_assessed": stats["passed"] + stats["failed"],
        }

    # Overall score (weighted average of domain scores)
    overall_score = 0.0
    total_weight = 0.0
    for domain, weight in DOMAIN_WEIGHTS.items():
        if domain in domain_scores and domain_scores[domain]["total_assessed"] > 0:
            overall_score += domain_scores[domain]["score"] * weight
            total_weight += weight

    if total_weight > 0:
        overall_score = round(overall_score / total_weight, 1)
    else:
        overall_score = 0.0

    # Rating
    if overall_score >= 90:
        rating = "Excellent"
    elif overall_score >= 80:
        rating = "Good"
    elif overall_score >= 70:
        rating = "Fair"
    elif overall_score >= 60:
        rating = "Poor"
    else:
        rating = "Critical"

    # Failure summary by severity
    severity_counts = defaultdict(int)
    for f in findings:
        if f["result"] == "fail":
            severity_counts[f["severity"]] += 1

    # Framework coverage
    framework_coverage = defaultdict(lambda: {"passed": 0, "failed": 0, "total": 0})
    for f in findings:
        if f["result"] in ("pass", "fail"):
            for fw in f["frameworks"]:
                framework_coverage[fw]["total"] += 1
                if f["result"] == "pass":
                    framework_coverage[fw]["passed"] += 1
                else:
                    framework_coverage[fw]["failed"] += 1

    framework_scores = {}
    for fw, stats in framework_coverage.items():
        if stats["total"] > 0:
            framework_scores[fw] = {
                "label": FRAMEWORK_LABELS.get(fw, fw),
                "score": round((stats["passed"] / stats["total"]) * 100, 1),
                "passed": stats["passed"],
                "failed": stats["failed"],
                "total": stats["total"],
            }

    return {
        "audit_metadata": {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "tool": "infrastructure-compliance-auditor",
            "version": "1.0.0",
            "total_controls_evaluated": sum(1 for f in findings if f["result"] != "not_applicable"),
            "total_controls_skipped": sum(1 for f in findings if f["result"] == "not_applicable"),
            "frameworks_filter": filter_frameworks,
        },
        "overall_score": overall_score,
        "overall_rating": rating,
        "severity_summary": {
            "critical_failures": severity_counts.get("Critical", 0),
            "high_failures": severity_counts.get("High", 0),
            "medium_failures": severity_counts.get("Medium", 0),
            "low_failures": severity_counts.get("Low", 0),
        },
        "domain_scores": domain_scores,
        "framework_scores": framework_scores,
        "findings": findings,
    }


def format_markdown(report):
    """Format audit report as Markdown."""
    lines = []
    lines.append("# Infrastructure Compliance Audit Report")
    lines.append("")
    lines.append(f"**Date:** {report['audit_metadata']['timestamp']}")
    lines.append(f"**Controls Evaluated:** {report['audit_metadata']['total_controls_evaluated']}")
    lines.append(f"**Controls Skipped (N/A):** {report['audit_metadata']['total_controls_skipped']}")
    if report["audit_metadata"]["frameworks_filter"]:
        lines.append(f"**Framework Filter:** {', '.join(report['audit_metadata']['frameworks_filter'])}")
    lines.append("")

    # Overall Score
    lines.append("## Overall Score")
    lines.append("")
    lines.append(f"**Score: {report['overall_score']}/100 — {report['overall_rating']}**")
    lines.append("")
    ss = report["severity_summary"]
    lines.append(f"| Severity | Failures |")
    lines.append(f"|----------|----------|")
    lines.append(f"| Critical | {ss['critical_failures']} |")
    lines.append(f"| High | {ss['high_failures']} |")
    lines.append(f"| Medium | {ss['medium_failures']} |")
    lines.append(f"| Low | {ss['low_failures']} |")
    lines.append("")

    # Domain Scores
    lines.append("## Domain Scores")
    lines.append("")
    lines.append("| Domain | Score | Passed | Failed | N/A |")
    lines.append("|--------|-------|--------|--------|-----|")
    for domain, data in sorted(report["domain_scores"].items(), key=lambda x: x[1]["score"]):
        label = domain.replace("_", " ").title()
        lines.append(f"| {label} | {data['score']}/100 | {data['passed']} | {data['failed']} | {data['not_applicable']} |")
    lines.append("")

    # Framework Scores
    if report["framework_scores"]:
        lines.append("## Framework Compliance Scores")
        lines.append("")
        lines.append("| Framework | Score | Passed | Failed | Total |")
        lines.append("|-----------|-------|--------|--------|-------|")
        for fw, data in sorted(report["framework_scores"].items(), key=lambda x: x[1]["score"]):
            lines.append(f"| {data['label']} | {data['score']}% | {data['passed']} | {data['failed']} | {data['total']} |")
        lines.append("")

    # Critical and High Findings
    critical_high = [f for f in report["findings"] if f["result"] == "fail" and f["severity"] in ("Critical", "High")]
    if critical_high:
        lines.append("## Critical and High Findings (Requires Immediate Action)")
        lines.append("")
        for f in sorted(critical_high, key=lambda x: (0 if x["severity"] == "Critical" else 1, x["check_id"])):
            lines.append(f"### [{f['severity']}] {f['check_id']}: {f['title']}")
            lines.append("")
            lines.append(f"**Domain:** {f['domain'].replace('_', ' ').title()}")
            lines.append(f"**Frameworks:** {', '.join(FRAMEWORK_LABELS.get(fw, fw) for fw in f['frameworks'])}")
            lines.append("")
            if "remediation" in f:
                lines.append(f"**Remediation:** {f['remediation']}")
            lines.append("")

    # Medium and Low Findings
    med_low = [f for f in report["findings"] if f["result"] == "fail" and f["severity"] in ("Medium", "Low")]
    if med_low:
        lines.append("## Medium and Low Findings")
        lines.append("")
        lines.append("| Check ID | Title | Severity | Remediation |")
        lines.append("|----------|-------|----------|-------------|")
        for f in sorted(med_low, key=lambda x: (0 if x["severity"] == "Medium" else 1, x["check_id"])):
            remediation = f.get("remediation", "See SKILL.md for guidance.").replace("|", "/")
            lines.append(f"| {f['check_id']} | {f['title']} | {f['severity']} | {remediation[:120]}{'...' if len(remediation) > 120 else ''} |")
        lines.append("")

    # Passed Controls Summary
    passed = [f for f in report["findings"] if f["result"] == "pass"]
    if passed:
        lines.append("## Passed Controls")
        lines.append("")
        lines.append(f"**{len(passed)} controls passed.** See JSON output for full details.")
        lines.append("")

    return "\n".join(lines)


def generate_template():
    """Generate a template infrastructure configuration JSON."""
    template = {
        "_description": "Infrastructure Compliance Audit Configuration Template",
        "_instructions": "Set each value to true/false based on your infrastructure state. Remove sections that don't apply to your environment.",
        "aws": {
            "iam": {
                "root_mfa_enabled": False,
                "root_access_keys": False,
                "wildcard_policies_exist": False,
                "all_users_mfa": False,
                "min_password_length": 8,
                "unused_credentials_disabled": False,
                "access_analyzer_enabled": False
            },
            "s3": {
                "account_block_public_access": False,
                "public_buckets_exist": False,
                "encryption_enabled": False,
                "access_logging_enabled": False
            },
            "vpc": {
                "flow_logs_enabled": False,
                "open_ssh_rdp": False,
                "db_private_subnets": False
            },
            "rds": {
                "encryption_at_rest": False,
                "ssl_enforced": False,
                "publicly_accessible": False
            },
            "cloudtrail": {
                "enabled_all_regions": False,
                "log_validation": False
            },
            "guardduty": {
                "enabled": False
            },
            "config": {
                "enabled": False
            },
            "kms": {
                "customer_managed_keys": False,
                "key_rotation_enabled": False
            }
        },
        "azure": {
            "ad": {
                "global_admin_mfa": False,
                "pim_enabled": False
            },
            "network": {
                "nsg_least_privilege": False
            },
            "keyvault": {
                "soft_delete_purge_protection": False
            },
            "defender": {
                "enabled": False
            },
            "storage": {
                "public_access_disabled": False
            }
        },
        "gcp": {
            "iam": {
                "no_owner_editor_sa": False
            },
            "vpc": {
                "no_open_ssh_rdp": False
            },
            "scc": {
                "enabled": False
            },
            "audit_logs": {
                "enabled": False
            }
        },
        "dns": {
            "spf": {
                "exists": False,
                "hard_fail": False,
                "lookup_count_ok": False,
                "no_plus_all": True
            },
            "dkim": {
                "exists": False,
                "min_2048_bit": False
            },
            "dmarc": {
                "exists": False,
                "policy_reject": False,
                "rua_configured": False
            },
            "dnssec": {
                "enabled": False
            },
            "caa": {
                "exists": False
            },
            "mta_sts": {
                "enabled": False
            },
            "domain": {
                "registrar_lock": False,
                "registrar_2fa": False,
                "subdomain_inventory": False,
                "no_dangling_cnames": False
            }
        },
        "tls": {
            "min_version_1_2": False,
            "tls_1_3_preferred": False,
            "forward_secrecy": False,
            "aead_only": False,
            "no_weak_ciphers": False,
            "hsts": {
                "max_age_1_year": False,
                "include_subdomains": False,
                "preload": False
            },
            "cert": {
                "trusted_ca": False,
                "automated_renewal": False,
                "expiry_monitoring": False,
                "ocsp_stapling": False
            },
            "internal": {
                "mtls": False,
                "db_tls": False
            }
        },
        "endpoint": {
            "mdm": {
                "deployed": False,
                "all_enrolled": False
            },
            "encryption": {
                "full_disk": False,
                "keys_escrowed": False
            },
            "edr": {
                "deployed": False,
                "realtime_protection": False
            },
            "patching": {
                "critical_24h": False,
                "high_72h": False
            },
            "screen_lock": {
                "5_min": False
            },
            "usb": {
                "controlled": False
            },
            "remote_wipe": {
                "enabled": False
            },
            "firewall": {
                "enabled": False
            }
        },
        "access": {
            "idp": {
                "deployed": False,
                "admin_hardware_mfa": False
            },
            "sso": {
                "saml_oidc": False,
                "scim_enabled": False,
                "deprovision_revoke": False
            },
            "mfa": {
                "enforced_all": False,
                "phishing_resistant_admins": False,
                "sms_prohibited": False,
                "hardware_keys_admins": False
            },
            "pam": {
                "jit_enabled": False,
                "session_recording": False,
                "inventory_reviewed": False
            },
            "rbac": {
                "documented": False,
                "quarterly_review": False,
                "sod_enforced": False
            },
            "service_accounts": {
                "no_shared_creds": False,
                "rotation_90d": False,
                "inventory": False
            },
            "ssh": {
                "strong_keys": False,
                "root_login_disabled": False,
                "password_auth_disabled": False
            },
            "zero_trust": {
                "identity_based": False,
                "device_posture": False
            }
        },
        "network": {
            "firewall": {
                "default_deny": False,
                "egress_filtering": False,
                "no_any_any": False
            },
            "segmentation": {
                "env_isolation": False,
                "db_isolated": False
            },
            "waf": {
                "deployed": False,
                "owasp_rules": False,
                "blocking_mode": False
            },
            "ddos": {
                "protection_enabled": False
            },
            "vpn": {
                "secure_protocol": False,
                "mfa_required": False
            },
            "ids": {
                "deployed": False
            }
        },
        "k8s": {
            "images": {
                "no_root": False,
                "vulnerability_scanning": False,
                "no_secrets": False,
                "signing_verified": False
            },
            "runtime": {
                "no_privileged": False
            },
            "rbac": {
                "least_privilege": False,
                "no_cluster_admin_apps": False
            },
            "network": {
                "policies_defined": False,
                "default_deny": False
            },
            "pods": {
                "security_standards": False
            },
            "secrets": {
                "external_operator": False,
                "etcd_encrypted": False
            },
            "admission": {
                "controllers_enabled": False
            },
            "registry": {
                "private": False
            }
        },
        "cicd": {
            "scm": {
                "branch_protection": False,
                "min_2_approvals": False,
                "signed_commits": False,
                "no_force_push": False
            },
            "scanning": {
                "secret_scanning": False,
                "precommit_hooks": False,
                "dependency_scanning": False,
                "sast": False,
                "dast": False,
                "container_images": False,
                "iac": False
            },
            "supply_chain": {
                "sbom": False,
                "artifact_signing": False
            },
            "deploy": {
                "approval_gates": False,
                "audit_trail": False,
                "secrets_manager": False
            }
        },
        "secrets": {
            "manager": {
                "deployed": False,
                "access_audited": False,
                "dynamic_secrets": False
            },
            "rotation": {
                "db_90d": False,
                "api_keys_90d": False,
                "automated": False
            },
            "code": {
                "no_secrets_in_code": False,
                "env_gitignored": False,
                "precommit_hooks": False,
                "historical_rotated": False
            },
            "hsm": {
                "root_ca_keys": False
            }
        },
        "logging": {
            "centralized": {
                "deployed": False,
                "coverage": False,
                "required_fields": False,
                "ntp_sync": False
            },
            "siem": {
                "deployed": False,
                "response_procedures": False
            },
            "retention": {
                "min_1_year": False,
                "immutable": False
            },
            "alerting": {
                "security_alerts": False,
                "escalation_matrix": False,
                "fim_deployed": False
            }
        },
        "physical": {
            "datacenter": {
                "soc2_report_reviewed": False,
                "access_restricted": False
            },
            "office": {
                "badge_access": False,
                "server_room_locked": False
            },
            "disposal": {
                "nist_800_88": False,
                "certificate": False,
                "crypto_erase": False
            }
        }
    }
    return template


def main():
    parser = argparse.ArgumentParser(
        description="Infrastructure Compliance Audit Runner — audit infrastructure security across 11 domains and 10 compliance frameworks.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate config template
  python infra_audit_runner.py --generate-template --output template.json

  # Run full audit
  python infra_audit_runner.py --config infrastructure.json --output report.json

  # Run audit filtered to specific frameworks
  python infra_audit_runner.py --config infrastructure.json --frameworks soc2,iso27001 --format markdown

  # Output markdown report
  python infra_audit_runner.py --config infrastructure.json --format markdown --output report.md
        """,
    )

    parser.add_argument("--config", type=str, help="Path to infrastructure configuration JSON file")
    parser.add_argument("--output", type=str, help="Output file path (default: stdout)")
    parser.add_argument("--format", type=str, choices=["json", "markdown"], default="json",
                        help="Output format (default: json)")
    parser.add_argument("--frameworks", type=str,
                        help="Comma-separated frameworks to filter (e.g., soc2,iso27001,pci_dss)")
    parser.add_argument("--generate-template", action="store_true",
                        help="Generate a template infrastructure config JSON")

    args = parser.parse_args()

    if args.generate_template:
        template = generate_template()
        output = json.dumps(template, indent=2)
        if args.output:
            with open(args.output, "w") as f:
                f.write(output)
            print(f"Template written to {args.output}", file=sys.stderr)
        else:
            print(output)
        return

    if not args.config:
        parser.error("--config is required (or use --generate-template)")

    # Load config
    try:
        with open(args.config, "r") as f:
            config = json.load(f)
    except FileNotFoundError:
        print(f"Error: Config file not found: {args.config}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in config file: {e}", file=sys.stderr)
        sys.exit(1)

    # Parse framework filter
    filter_frameworks = None
    if args.frameworks:
        filter_frameworks = [f.strip() for f in args.frameworks.split(",")]
        valid = set(FRAMEWORK_LABELS.keys())
        for fw in filter_frameworks:
            if fw not in valid:
                print(f"Warning: Unknown framework '{fw}'. Valid: {', '.join(sorted(valid))}", file=sys.stderr)

    # Run audit
    report = run_audit(config, filter_frameworks)

    # Format output
    if args.format == "markdown":
        output = format_markdown(report)
    else:
        output = json.dumps(report, indent=2)

    # Write output
    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
        print(f"Audit report written to {args.output}", file=sys.stderr)
        print(f"Overall Score: {report['overall_score']}/100 ({report['overall_rating']})", file=sys.stderr)
        ss = report["severity_summary"]
        print(f"Failures: {ss['critical_failures']} Critical, {ss['high_failures']} High, "
              f"{ss['medium_failures']} Medium, {ss['low_failures']} Low", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
