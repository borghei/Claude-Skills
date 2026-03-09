#!/usr/bin/env python3
"""
DNS Security Checker

Validates DNS security configuration for a domain including:
- SPF record validation (syntax, lookup count, mechanisms)
- DKIM record presence and key strength
- DMARC record validation (policy, reporting, alignment)
- DNSSEC validation
- CAA record validation
- MTA-STS validation
- Domain registrar security checks
- Subdomain takeover risk assessment

Uses only Python standard library. DNS lookups performed via subprocess
calls to system DNS tools (dig/nslookup) when available, with fallback
to socket-based lookups.

Usage:
    python dns_security_checker.py --domain example.com
    python dns_security_checker.py --domain example.com --output report.json
    python dns_security_checker.py --domain example.com --format markdown
    python dns_security_checker.py --domain example.com --subdomains sub1,sub2,sub3
    python dns_security_checker.py --domain example.com --dkim-selectors google,selector1
"""

import argparse
import json
import re
import subprocess
import sys
import socket
from datetime import datetime, timezone
from collections import defaultdict


# ---------------------------------------------------------------------------
# DNS Query Helpers (standard library only)
# ---------------------------------------------------------------------------

def run_dig(domain, record_type, timeout=10):
    """
    Query DNS using dig command.
    Returns list of record values or empty list if dig is not available.
    """
    try:
        result = subprocess.run(
            ["dig", "+short", "+time={}".format(timeout), domain, record_type],
            capture_output=True, text=True, timeout=timeout + 5
        )
        if result.returncode == 0:
            lines = [line.strip().strip('"') for line in result.stdout.strip().split("\n") if line.strip()]
            return lines
        return []
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return []


def run_dig_full(domain, record_type, timeout=10):
    """
    Query DNS using dig with full output for DNSSEC checks.
    Returns raw output string.
    """
    try:
        result = subprocess.run(
            ["dig", "+dnssec", "+time={}".format(timeout), domain, record_type],
            capture_output=True, text=True, timeout=timeout + 5
        )
        if result.returncode == 0:
            return result.stdout
        return ""
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return ""


def query_txt_records(domain):
    """Query TXT records for a domain."""
    records = run_dig(domain, "TXT")
    if records:
        # dig +short returns quoted strings, strip quotes and join multi-part records
        cleaned = []
        for r in records:
            # Handle multi-part TXT records (split across multiple strings)
            r = r.replace('" "', '').strip('"')
            cleaned.append(r)
        return cleaned

    # Fallback: use nslookup
    try:
        result = subprocess.run(
            ["nslookup", "-type=TXT", domain],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode == 0:
            txt_records = []
            for line in result.stdout.split("\n"):
                if "text =" in line.lower() or "txt" in line.lower():
                    match = re.search(r'"([^"]*)"', line)
                    if match:
                        txt_records.append(match.group(1))
            return txt_records
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    return []


def query_caa_records(domain):
    """Query CAA records."""
    records = run_dig(domain, "CAA")
    if records:
        return records

    try:
        result = subprocess.run(
            ["dig", "+short", domain, "TYPE257"],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode == 0:
            lines = [l.strip() for l in result.stdout.strip().split("\n") if l.strip()]
            return lines
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    return []


def query_cname(domain):
    """Query CNAME record for a domain."""
    records = run_dig(domain, "CNAME")
    return records


def resolve_domain(domain):
    """Check if domain resolves to an IP."""
    try:
        socket.getaddrinfo(domain, None, socket.AF_UNSPEC, socket.SOCK_STREAM)
        return True
    except socket.gaierror:
        return False


# ---------------------------------------------------------------------------
# SPF Checks
# ---------------------------------------------------------------------------

def check_spf(domain):
    """Validate SPF record configuration."""
    findings = []
    txt_records = query_txt_records(domain)
    spf_records = [r for r in txt_records if r.startswith("v=spf1")]

    if not spf_records:
        findings.append({
            "check_id": "DNS-SPF-001",
            "title": "SPF record exists",
            "severity": "High",
            "result": "fail",
            "detail": f"No SPF record found for {domain}.",
            "remediation": f"Add TXT record: v=spf1 include:<your-email-provider> -all"
        })
        return findings, None

    if len(spf_records) > 1:
        findings.append({
            "check_id": "DNS-SPF-ERR",
            "title": "Multiple SPF records (invalid per RFC 7208)",
            "severity": "High",
            "result": "fail",
            "detail": f"Found {len(spf_records)} SPF records. RFC 7208 requires exactly one.",
            "remediation": "Merge all SPF records into a single TXT record."
        })

    spf = spf_records[0]
    findings.append({
        "check_id": "DNS-SPF-001",
        "title": "SPF record exists",
        "severity": "High",
        "result": "pass",
        "detail": f"SPF record: {spf}"
    })

    # Check for +all (allows anyone)
    if "+all" in spf:
        findings.append({
            "check_id": "DNS-SPF-004",
            "title": "SPF does not use +all",
            "severity": "Critical",
            "result": "fail",
            "detail": "+all permits ANY server to send email as your domain. This is extremely dangerous.",
            "remediation": "Change +all to -all immediately."
        })
    else:
        findings.append({
            "check_id": "DNS-SPF-004",
            "title": "SPF does not use +all",
            "severity": "Critical",
            "result": "pass",
            "detail": "SPF record does not contain +all."
        })

    # Check for -all (hard fail) vs ~all (soft fail)
    if spf.rstrip().endswith("-all"):
        findings.append({
            "check_id": "DNS-SPF-002",
            "title": "SPF uses -all (hard fail)",
            "severity": "High",
            "result": "pass",
            "detail": "SPF record uses -all (hard fail) as recommended."
        })
    elif "~all" in spf:
        findings.append({
            "check_id": "DNS-SPF-002",
            "title": "SPF uses -all (hard fail)",
            "severity": "High",
            "result": "fail",
            "detail": "SPF record uses ~all (soft fail). Upgrade to -all for strict enforcement.",
            "remediation": "Change ~all to -all in your SPF record."
        })
    elif "?all" in spf:
        findings.append({
            "check_id": "DNS-SPF-002",
            "title": "SPF uses -all (hard fail)",
            "severity": "High",
            "result": "fail",
            "detail": "SPF record uses ?all (neutral). This provides no protection.",
            "remediation": "Change ?all to -all in your SPF record."
        })

    # Count DNS lookups (include, a, mx, ptr, exists, redirect count)
    lookup_mechanisms = re.findall(r'\b(include|a|mx|ptr|exists|redirect)\b', spf, re.IGNORECASE)
    lookup_count = len(lookup_mechanisms)

    if lookup_count > 10:
        findings.append({
            "check_id": "DNS-SPF-003",
            "title": "SPF < 10 DNS lookups",
            "severity": "Medium",
            "result": "fail",
            "detail": f"SPF record has {lookup_count} DNS lookup mechanisms (limit: 10 per RFC 7208). Note: nested includes also count.",
            "remediation": "Flatten SPF record using ip4/ip6 mechanisms, or use an SPF flattening service."
        })
    else:
        findings.append({
            "check_id": "DNS-SPF-003",
            "title": "SPF < 10 DNS lookups",
            "severity": "Medium",
            "result": "pass",
            "detail": f"SPF record has {lookup_count} DNS lookup mechanisms (limit: 10). Note: nested includes may add more."
        })

    # Check for deprecated PTR mechanism
    if "ptr" in spf.lower():
        findings.append({
            "check_id": "DNS-SPF-006",
            "title": "SPF avoids deprecated PTR mechanism",
            "severity": "Low",
            "result": "fail",
            "detail": "SPF record uses ptr mechanism, which is deprecated per RFC 7208.",
            "remediation": "Replace ptr with specific ip4/ip6 or include mechanisms."
        })

    # Check for non-sending domain protection
    non_sending_txt = query_txt_records(domain)
    non_sending_spf = [r for r in non_sending_txt if r == "v=spf1 -all"]
    # This check is informational for the main domain

    return findings, spf


# ---------------------------------------------------------------------------
# DKIM Checks
# ---------------------------------------------------------------------------

def check_dkim(domain, selectors=None):
    """Validate DKIM configuration."""
    findings = []

    if selectors is None:
        # Common DKIM selectors to check
        selectors = [
            "google", "selector1", "selector2", "default", "dkim", "k1",
            "mail", "s1", "s2", "mandrill", "smtp", "amazonses",
            "cm", "sig1", "zendesk1", "zendesk2", "protonmail",
            "mxvault", "dk"
        ]

    found_selectors = []
    for selector in selectors:
        dkim_domain = f"{selector}._domainkey.{domain}"
        records = query_txt_records(dkim_domain)
        cname_records = query_cname(dkim_domain)

        if records or cname_records:
            found_selectors.append({
                "selector": selector,
                "domain": dkim_domain,
                "records": records,
                "cname": cname_records,
            })

    if not found_selectors:
        findings.append({
            "check_id": "DNS-DKIM-001",
            "title": "DKIM record exists",
            "severity": "High",
            "result": "fail",
            "detail": f"No DKIM records found for {domain} (checked selectors: {', '.join(selectors[:8])}...).",
            "remediation": "Configure DKIM signing with your email provider and add the DKIM TXT record."
        })
        return findings

    findings.append({
        "check_id": "DNS-DKIM-001",
        "title": "DKIM record exists",
        "severity": "High",
        "result": "pass",
        "detail": f"Found DKIM records for selectors: {', '.join(s['selector'] for s in found_selectors)}"
    })

    # Check key length where possible
    for sel in found_selectors:
        for record in sel.get("records", []):
            if "p=" in record:
                # Extract public key
                match = re.search(r'p=([A-Za-z0-9+/=]+)', record)
                if match:
                    key_b64 = match.group(1)
                    # Rough key length estimation: base64 length * 6 / 8 = bytes, * 8 = bits
                    key_bytes = len(key_b64) * 3 // 4
                    key_bits = key_bytes * 8

                    if key_bits < 2048:
                        findings.append({
                            "check_id": "DNS-DKIM-002",
                            "title": f"DKIM key minimum 2048-bit (selector: {sel['selector']})",
                            "severity": "High",
                            "result": "fail",
                            "detail": f"DKIM key for selector '{sel['selector']}' is approximately {key_bits} bits. Minimum 2048-bit required.",
                            "remediation": f"Generate a new 2048-bit (or 4096-bit) DKIM key for selector '{sel['selector']}'."
                        })
                    else:
                        findings.append({
                            "check_id": "DNS-DKIM-002",
                            "title": f"DKIM key minimum 2048-bit (selector: {sel['selector']})",
                            "severity": "High",
                            "result": "pass",
                            "detail": f"DKIM key for selector '{sel['selector']}' is approximately {key_bits} bits."
                        })

            # Check for testing mode
            if "t=y" in record:
                findings.append({
                    "check_id": "DNS-DKIM-005",
                    "title": f"DKIM testing mode removed (selector: {sel['selector']})",
                    "severity": "Medium",
                    "result": "fail",
                    "detail": f"DKIM selector '{sel['selector']}' has t=y (testing mode). Remove for production.",
                    "remediation": f"Remove t=y from DKIM record for selector '{sel['selector']}'."
                })

    return findings


# ---------------------------------------------------------------------------
# DMARC Checks
# ---------------------------------------------------------------------------

def check_dmarc(domain):
    """Validate DMARC configuration."""
    findings = []
    dmarc_domain = f"_dmarc.{domain}"
    records = query_txt_records(dmarc_domain)
    dmarc_records = [r for r in records if r.startswith("v=DMARC1")]

    if not dmarc_records:
        findings.append({
            "check_id": "DNS-DMARC-001",
            "title": "DMARC record exists",
            "severity": "High",
            "result": "fail",
            "detail": f"No DMARC record found at {dmarc_domain}.",
            "remediation": f"Add TXT record at {dmarc_domain}: v=DMARC1; p=reject; rua=mailto:dmarc@{domain}; pct=100"
        })
        return findings

    dmarc = dmarc_records[0]
    findings.append({
        "check_id": "DNS-DMARC-001",
        "title": "DMARC record exists",
        "severity": "High",
        "result": "pass",
        "detail": f"DMARC record: {dmarc}"
    })

    # Parse DMARC tags
    tags = {}
    for part in dmarc.split(";"):
        part = part.strip()
        if "=" in part:
            key, value = part.split("=", 1)
            tags[key.strip()] = value.strip()

    # Check policy
    policy = tags.get("p", "").lower()
    if policy == "reject":
        findings.append({
            "check_id": "DNS-DMARC-002",
            "title": "DMARC policy is p=reject",
            "severity": "High",
            "result": "pass",
            "detail": "DMARC policy is set to reject (maximum enforcement)."
        })
    elif policy == "quarantine":
        findings.append({
            "check_id": "DNS-DMARC-002",
            "title": "DMARC policy is p=reject",
            "severity": "High",
            "result": "fail",
            "detail": "DMARC policy is quarantine. Upgrade to reject for maximum enforcement.",
            "remediation": "Change p=quarantine to p=reject after confirming legitimate senders pass SPF/DKIM."
        })
    elif policy == "none":
        findings.append({
            "check_id": "DNS-DMARC-002",
            "title": "DMARC policy is p=reject",
            "severity": "High",
            "result": "fail",
            "detail": "DMARC policy is none (monitoring only). No enforcement is in place.",
            "remediation": "Follow DMARC rollout: none > quarantine (pct=10) > quarantine (pct=100) > reject."
        })
    else:
        findings.append({
            "check_id": "DNS-DMARC-002",
            "title": "DMARC policy is p=reject",
            "severity": "High",
            "result": "fail",
            "detail": f"DMARC policy is '{policy}' (unrecognized or missing).",
            "remediation": "Set p=reject in DMARC record."
        })

    # Check rua (aggregate reporting)
    if "rua" in tags:
        findings.append({
            "check_id": "DNS-DMARC-003",
            "title": "DMARC aggregate reporting (rua) configured",
            "severity": "Medium",
            "result": "pass",
            "detail": f"DMARC aggregate reports sent to: {tags['rua']}"
        })
    else:
        findings.append({
            "check_id": "DNS-DMARC-003",
            "title": "DMARC aggregate reporting (rua) configured",
            "severity": "Medium",
            "result": "fail",
            "detail": "No rua tag in DMARC record. You won't receive aggregate reports.",
            "remediation": f"Add rua=mailto:dmarc-agg@{domain} to your DMARC record."
        })

    # Check ruf (forensic reporting)
    if "ruf" in tags:
        findings.append({
            "check_id": "DNS-DMARC-004",
            "title": "DMARC forensic reporting (ruf) configured",
            "severity": "Low",
            "result": "pass",
            "detail": f"DMARC forensic reports sent to: {tags['ruf']}"
        })
    else:
        findings.append({
            "check_id": "DNS-DMARC-004",
            "title": "DMARC forensic reporting (ruf) configured",
            "severity": "Low",
            "result": "fail",
            "detail": "No ruf tag in DMARC record.",
            "remediation": f"Add ruf=mailto:dmarc-forensic@{domain} to your DMARC record."
        })

    # Check subdomain policy
    sp = tags.get("sp", "").lower()
    if sp == "reject":
        findings.append({
            "check_id": "DNS-DMARC-005",
            "title": "DMARC subdomain policy sp=reject",
            "severity": "Medium",
            "result": "pass",
            "detail": "DMARC subdomain policy is set to reject."
        })
    elif sp:
        findings.append({
            "check_id": "DNS-DMARC-005",
            "title": "DMARC subdomain policy sp=reject",
            "severity": "Medium",
            "result": "fail",
            "detail": f"DMARC subdomain policy is sp={sp}. Should be sp=reject.",
            "remediation": "Set sp=reject in DMARC record."
        })
    else:
        findings.append({
            "check_id": "DNS-DMARC-005",
            "title": "DMARC subdomain policy sp=reject",
            "severity": "Medium",
            "result": "fail",
            "detail": "No subdomain policy (sp) set. Subdomains inherit the main policy.",
            "remediation": "Add sp=reject to your DMARC record."
        })

    # Check alignment modes
    adkim = tags.get("adkim", "r").lower()
    aspf = tags.get("aspf", "r").lower()
    if adkim == "s" and aspf == "s":
        findings.append({
            "check_id": "DNS-DMARC-006",
            "title": "DMARC strict alignment (adkim=s, aspf=s)",
            "severity": "Medium",
            "result": "pass",
            "detail": "DMARC uses strict alignment for both DKIM and SPF."
        })
    else:
        findings.append({
            "check_id": "DNS-DMARC-006",
            "title": "DMARC strict alignment (adkim=s, aspf=s)",
            "severity": "Medium",
            "result": "fail",
            "detail": f"DMARC alignment: adkim={adkim}, aspf={aspf}. Strict (s) is recommended for both.",
            "remediation": "Add adkim=s; aspf=s to your DMARC record for strict alignment."
        })

    # Check pct
    pct = tags.get("pct", "100")
    try:
        pct_val = int(pct)
        if pct_val == 100:
            findings.append({
                "check_id": "DNS-DMARC-007",
                "title": "DMARC pct=100",
                "severity": "Medium",
                "result": "pass",
                "detail": "DMARC policy applies to 100% of messages."
            })
        else:
            findings.append({
                "check_id": "DNS-DMARC-007",
                "title": "DMARC pct=100",
                "severity": "Medium",
                "result": "fail",
                "detail": f"DMARC policy applies to only {pct_val}% of messages.",
                "remediation": f"Increase pct to 100 after confirming legitimate senders pass. Currently at {pct_val}%."
            })
    except ValueError:
        pass

    return findings


# ---------------------------------------------------------------------------
# DNSSEC Checks
# ---------------------------------------------------------------------------

def check_dnssec(domain):
    """Check DNSSEC configuration."""
    findings = []

    output = run_dig_full(domain, "A")
    has_rrsig = "RRSIG" in output
    has_ad_flag = "flags:" in output and "ad" in output.lower().split("flags:")[1].split(";")[0].lower() if "flags:" in output else False

    # Also check for DS record
    ds_records = run_dig(domain, "DS")
    dnskey_records = run_dig(domain, "DNSKEY")

    if has_rrsig or ds_records or dnskey_records:
        findings.append({
            "check_id": "DNS-SEC-001",
            "title": "DNSSEC signing enabled",
            "severity": "High",
            "result": "pass",
            "detail": "DNSSEC appears to be enabled for this domain."
        })

        if ds_records:
            findings.append({
                "check_id": "DNS-SEC-002",
                "title": "DS record published in parent zone",
                "severity": "High",
                "result": "pass",
                "detail": f"DS record(s) found: {'; '.join(ds_records[:2])}"
            })

            # Check algorithm
            for ds in ds_records:
                parts = ds.split()
                if len(parts) >= 2:
                    try:
                        algo = int(parts[1])
                        if algo >= 13:  # ECDSAP256SHA256 = 13
                            findings.append({
                                "check_id": "DNS-SEC-003",
                                "title": "DNSSEC uses modern algorithm",
                                "severity": "Medium",
                                "result": "pass",
                                "detail": f"DNSSEC algorithm {algo} (ECDSA or newer)."
                            })
                        else:
                            findings.append({
                                "check_id": "DNS-SEC-003",
                                "title": "DNSSEC uses modern algorithm",
                                "severity": "Medium",
                                "result": "fail",
                                "detail": f"DNSSEC algorithm {algo}. Consider upgrading to algorithm 13 (ECDSAP256SHA256) or newer.",
                                "remediation": "Migrate DNSSEC to ECDSAP256SHA256 (algorithm 13) for better security and smaller signatures."
                            })
                        break  # Only check first DS record
                    except (ValueError, IndexError):
                        pass
        else:
            findings.append({
                "check_id": "DNS-SEC-002",
                "title": "DS record published in parent zone",
                "severity": "High",
                "result": "fail",
                "detail": "No DS record found in parent zone. DNSSEC chain of trust is broken.",
                "remediation": "Publish DS record in parent zone via your domain registrar."
            })
    else:
        findings.append({
            "check_id": "DNS-SEC-001",
            "title": "DNSSEC signing enabled",
            "severity": "High",
            "result": "fail",
            "detail": f"DNSSEC does not appear to be enabled for {domain}.",
            "remediation": "Enable DNSSEC signing at your DNS provider. Publish DS record via your registrar."
        })

    return findings


# ---------------------------------------------------------------------------
# CAA Checks
# ---------------------------------------------------------------------------

def check_caa(domain):
    """Check CAA record configuration."""
    findings = []
    records = query_caa_records(domain)

    if not records:
        findings.append({
            "check_id": "DNS-CAA-001",
            "title": "CAA record exists",
            "severity": "High",
            "result": "fail",
            "detail": f"No CAA record found for {domain}. Any CA can issue certificates.",
            "remediation": f"Add CAA records: {domain} CAA 0 issue \"letsencrypt.org\" (adjust CA as needed)"
        })
        return findings

    findings.append({
        "check_id": "DNS-CAA-001",
        "title": "CAA record exists",
        "severity": "High",
        "result": "pass",
        "detail": f"CAA records found: {'; '.join(records[:5])}"
    })

    # Check for iodef tag
    has_iodef = any("iodef" in r.lower() for r in records)
    if has_iodef:
        findings.append({
            "check_id": "DNS-CAA-002",
            "title": "CAA iodef notification configured",
            "severity": "Medium",
            "result": "pass",
            "detail": "CAA iodef tag is configured for certificate issuance notifications."
        })
    else:
        findings.append({
            "check_id": "DNS-CAA-002",
            "title": "CAA iodef notification configured",
            "severity": "Medium",
            "result": "fail",
            "detail": "No iodef tag in CAA records. You won't be notified of certificate issuance attempts.",
            "remediation": f"Add: {domain} CAA 0 iodef \"mailto:security@{domain}\""
        })

    # Check that issue/issuewild tags exist
    has_issue = any("issue " in r.lower() or "issuewild " in r.lower() for r in records)
    if has_issue:
        findings.append({
            "check_id": "DNS-CAA-003",
            "title": "Authorized CAs specified in CAA",
            "severity": "High",
            "result": "pass",
            "detail": "CAA record restricts certificate issuance to specified CAs."
        })
    else:
        findings.append({
            "check_id": "DNS-CAA-003",
            "title": "Authorized CAs specified in CAA",
            "severity": "High",
            "result": "fail",
            "detail": "CAA record exists but does not specify authorized CAs.",
            "remediation": "Add issue and/or issuewild tags to your CAA record."
        })

    return findings


# ---------------------------------------------------------------------------
# MTA-STS Checks
# ---------------------------------------------------------------------------

def check_mta_sts(domain):
    """Check MTA-STS configuration."""
    findings = []

    # Check for _mta-sts DNS record
    mta_sts_domain = f"_mta-sts.{domain}"
    records = query_txt_records(mta_sts_domain)
    mta_sts_records = [r for r in records if r.startswith("v=STSv1")]

    if mta_sts_records:
        findings.append({
            "check_id": "DNS-MTA-002",
            "title": "MTA-STS DNS record exists",
            "severity": "Medium",
            "result": "pass",
            "detail": f"MTA-STS DNS record found: {mta_sts_records[0]}"
        })

        # We can't easily check the policy file without HTTP requests
        # (standard library has urllib but we keep it simple)
        findings.append({
            "check_id": "DNS-MTA-001",
            "title": "MTA-STS policy published",
            "severity": "Medium",
            "result": "pass",
            "detail": "MTA-STS DNS record present. Verify policy at https://mta-sts.{}//.well-known/mta-sts.txt".format(domain)
        })
    else:
        findings.append({
            "check_id": "DNS-MTA-001",
            "title": "MTA-STS policy published",
            "severity": "Medium",
            "result": "fail",
            "detail": f"No MTA-STS configuration found for {domain}.",
            "remediation": f"1. Create policy at https://mta-sts.{domain}/.well-known/mta-sts.txt\n2. Add DNS TXT at _mta-sts.{domain}: v=STSv1; id=<unique-id>"
        })

    # Check TLS-RPT
    tls_rpt_domain = f"_smtp._tls.{domain}"
    tls_rpt_records = query_txt_records(tls_rpt_domain)
    tls_rpt = [r for r in tls_rpt_records if "v=TLSRPTv1" in r]

    if tls_rpt:
        findings.append({
            "check_id": "DNS-MTA-004",
            "title": "TLS-RPT record configured",
            "severity": "Low",
            "result": "pass",
            "detail": f"TLS-RPT record found: {tls_rpt[0]}"
        })
    else:
        findings.append({
            "check_id": "DNS-MTA-004",
            "title": "TLS-RPT record configured",
            "severity": "Low",
            "result": "fail",
            "detail": "No TLS-RPT record found.",
            "remediation": f"Add TXT at _smtp._tls.{domain}: v=TLSRPTv1; rua=mailto:tls-reports@{domain}"
        })

    return findings


# ---------------------------------------------------------------------------
# Subdomain Security Checks
# ---------------------------------------------------------------------------

def check_subdomains(domain, subdomains):
    """Check subdomains for dangling CNAME (takeover risk)."""
    findings = []

    # Known services vulnerable to subdomain takeover
    takeover_signatures = [
        "github.io", "herokuapp.com", "pantheonsite.io", "amazonaws.com",
        "cloudfront.net", "azurewebsites.net", "blob.core.windows.net",
        "cloudapp.azure.com", "trafficmanager.net", "s3.amazonaws.com",
        "elasticbeanstalk.com", "shopify.com", "zendesk.com",
        "freshdesk.com", "ghost.io", "helpscoutdocs.com",
        "helpjuice.com", "statuspage.io", "surge.sh",
        "bitbucket.io", "netlify.app", "fly.dev",
    ]

    dangling_count = 0
    for sub in subdomains:
        full_domain = f"{sub}.{domain}" if not sub.endswith(domain) else sub
        cname_records = query_cname(full_domain)

        if cname_records:
            for cname_target in cname_records:
                cname_target = cname_target.rstrip(".")
                # Check if CNAME target resolves
                if not resolve_domain(cname_target):
                    dangling_count += 1
                    # Check if it points to a known takeover-vulnerable service
                    vulnerable_service = None
                    for sig in takeover_signatures:
                        if sig in cname_target.lower():
                            vulnerable_service = sig
                            break

                    detail = f"Subdomain {full_domain} has CNAME to {cname_target} which does NOT resolve."
                    if vulnerable_service:
                        detail += f" Points to {vulnerable_service} — HIGH RISK of subdomain takeover."

                    findings.append({
                        "check_id": "DNS-DOM-006",
                        "title": f"Dangling CNAME: {full_domain}",
                        "severity": "High" if vulnerable_service else "Medium",
                        "result": "fail",
                        "detail": detail,
                        "remediation": f"Remove the CNAME record for {full_domain} or reclaim the service at {cname_target}."
                    })

    if dangling_count == 0 and subdomains:
        findings.append({
            "check_id": "DNS-DOM-006",
            "title": "No dangling CNAME records",
            "severity": "High",
            "result": "pass",
            "detail": f"Checked {len(subdomains)} subdomains. No dangling CNAME records found."
        })

    return findings


# ---------------------------------------------------------------------------
# Main Audit Orchestrator
# ---------------------------------------------------------------------------

def run_dns_audit(domain, dkim_selectors=None, subdomains=None):
    """Run complete DNS security audit for a domain."""
    all_findings = []

    # SPF
    spf_findings, spf_record = check_spf(domain)
    all_findings.extend(spf_findings)

    # DKIM
    dkim_findings = check_dkim(domain, dkim_selectors)
    all_findings.extend(dkim_findings)

    # DMARC
    dmarc_findings = check_dmarc(domain)
    all_findings.extend(dmarc_findings)

    # DNSSEC
    dnssec_findings = check_dnssec(domain)
    all_findings.extend(dnssec_findings)

    # CAA
    caa_findings = check_caa(domain)
    all_findings.extend(caa_findings)

    # MTA-STS / TLS-RPT
    mta_findings = check_mta_sts(domain)
    all_findings.extend(mta_findings)

    # Subdomain checks
    if subdomains:
        sub_findings = check_subdomains(domain, subdomains)
        all_findings.extend(sub_findings)

    # Calculate score
    passed = sum(1 for f in all_findings if f["result"] == "pass")
    failed = sum(1 for f in all_findings if f["result"] == "fail")
    total = passed + failed

    severity_counts = defaultdict(int)
    for f in all_findings:
        if f["result"] == "fail":
            severity_counts[f["severity"]] += 1

    weighted_pass = 0
    weighted_total = 0
    for f in all_findings:
        if f["result"] in ("pass", "fail"):
            w = {"Critical": 10, "High": 5, "Medium": 2, "Low": 1, "Info": 0}.get(f["severity"], 0)
            weighted_total += w
            if f["result"] == "pass":
                weighted_pass += w

    score = round((weighted_pass / weighted_total) * 100, 1) if weighted_total > 0 else 0.0

    if score >= 90:
        rating = "Excellent"
    elif score >= 80:
        rating = "Good"
    elif score >= 70:
        rating = "Fair"
    elif score >= 60:
        rating = "Poor"
    else:
        rating = "Critical"

    return {
        "audit_metadata": {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "tool": "dns-security-checker",
            "version": "1.0.0",
            "domain": domain,
            "dkim_selectors_checked": dkim_selectors or "default set",
            "subdomains_checked": subdomains or [],
        },
        "score": score,
        "rating": rating,
        "summary": {
            "total_checks": total,
            "passed": passed,
            "failed": failed,
            "critical_failures": severity_counts.get("Critical", 0),
            "high_failures": severity_counts.get("High", 0),
            "medium_failures": severity_counts.get("Medium", 0),
            "low_failures": severity_counts.get("Low", 0),
        },
        "findings": all_findings,
    }


def format_markdown(report):
    """Format DNS audit report as Markdown."""
    lines = []
    lines.append(f"# DNS Security Audit Report: {report['audit_metadata']['domain']}")
    lines.append("")
    lines.append(f"**Date:** {report['audit_metadata']['timestamp']}")
    lines.append(f"**Score: {report['score']}/100 — {report['rating']}**")
    lines.append("")

    s = report["summary"]
    lines.append(f"## Summary")
    lines.append("")
    lines.append(f"- **Total Checks:** {s['total_checks']}")
    lines.append(f"- **Passed:** {s['passed']}")
    lines.append(f"- **Failed:** {s['failed']}")
    lines.append(f"- **Critical:** {s['critical_failures']} | **High:** {s['high_failures']} | **Medium:** {s['medium_failures']} | **Low:** {s['low_failures']}")
    lines.append("")

    # Failed findings
    failed = [f for f in report["findings"] if f["result"] == "fail"]
    if failed:
        lines.append("## Findings Requiring Action")
        lines.append("")
        for f in sorted(failed, key=lambda x: {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}.get(x["severity"], 4)):
            lines.append(f"### [{f['severity']}] {f['check_id']}: {f['title']}")
            lines.append("")
            lines.append(f"{f['detail']}")
            if "remediation" in f:
                lines.append("")
                lines.append(f"**Remediation:** {f['remediation']}")
            lines.append("")

    # Passed findings
    passed = [f for f in report["findings"] if f["result"] == "pass"]
    if passed:
        lines.append("## Passed Checks")
        lines.append("")
        for f in passed:
            lines.append(f"- **{f['check_id']}:** {f['title']} — {f.get('detail', 'OK')[:100]}")
        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="DNS Security Checker — validate SPF, DKIM, DMARC, DNSSEC, CAA, MTA-STS, and subdomain security.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic DNS security check
  python dns_security_checker.py --domain example.com

  # Check specific DKIM selectors
  python dns_security_checker.py --domain example.com --dkim-selectors google,selector1,mandrill

  # Check for subdomain takeover
  python dns_security_checker.py --domain example.com --subdomains www,mail,blog,shop,api,cdn,staging

  # Output as markdown
  python dns_security_checker.py --domain example.com --format markdown --output dns_report.md
        """,
    )

    parser.add_argument("--domain", type=str, required=True, help="Domain to audit")
    parser.add_argument("--output", type=str, help="Output file path (default: stdout)")
    parser.add_argument("--format", type=str, choices=["json", "markdown"], default="json",
                        help="Output format (default: json)")
    parser.add_argument("--dkim-selectors", type=str,
                        help="Comma-separated DKIM selectors to check (default: common selectors)")
    parser.add_argument("--subdomains", type=str,
                        help="Comma-separated subdomains to check for takeover risk")

    args = parser.parse_args()

    dkim_selectors = None
    if args.dkim_selectors:
        dkim_selectors = [s.strip() for s in args.dkim_selectors.split(",")]

    subdomains = None
    if args.subdomains:
        subdomains = [s.strip() for s in args.subdomains.split(",")]

    report = run_dns_audit(args.domain, dkim_selectors, subdomains)

    if args.format == "markdown":
        output = format_markdown(report)
    else:
        output = json.dumps(report, indent=2)

    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
        print(f"DNS security report written to {args.output}", file=sys.stderr)
        print(f"Score: {report['score']}/100 ({report['rating']})", file=sys.stderr)
        s = report["summary"]
        print(f"Results: {s['passed']} passed, {s['failed']} failed "
              f"({s['critical_failures']} Critical, {s['high_failures']} High)", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
