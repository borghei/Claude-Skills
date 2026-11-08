---
name: threat-detection
description: >
  Scan auth and access logs for brute force, injection, path traversal, admin probing and
  request floods, with triage guidance. Use when analyzing logs for threats or reviewing
  suspicious activity after an alert.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: engineering
  domain: security
  updated: 2026-11-08
  tags: [security, threat-detection, logs, monitoring, incident-response]
---
# Threat Detection

> **Category:** Engineering
> **Domain:** Security Operations

## Overview

The **Threat Detection** skill provides automated analysis of log files for suspicious patterns including brute force attempts, injection attempts, path traversal, admin path probing and request flooding. It helps security teams triage log data and identify threats before they escalate.

## When to Use

- Triage after an alert: which IPs sent injection or traversal payloads, and did any succeed?
- A periodic review of auth or access logs for brute force and probing.
- Checking a log excerpt someone pasted for obvious attack patterns.

For live monitoring and alert routing use a SIEM; this skill reads one file per run.

## Clarify First

Before analyzing logs, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Log file & source type:** auth / access / application logs to analyze (`--file`; the subject of detection).
- **Threat category:** injection / auth (brute force) / traversal / probe / rate (`--category`; focuses the scan).
- **Minimum severity:** the reporting/alert threshold (`--min-severity`; changes which signals surface and any SIEM/CI gate).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Quick Start

```bash
# Bundled sample: SQLi (plain and URL-encoded), traversal, command injection, XSS,
# admin probes and a brute-force run -> 10 signals, exit 1
python scripts/threat_signal_analyzer.py --file assets/sample_access_log.txt

# Clean traffic (including URL fragments and "--" in queries) -> no signals, exit 0
python scripts/threat_signal_analyzer.py --file assets/sample_clean_log.txt

# Analyze with specific threat category
python scripts/threat_signal_analyzer.py --file access.log --category injection

# JSON output for SIEM integration
python scripts/threat_signal_analyzer.py --file auth.log --format json

# Set minimum severity
python scripts/threat_signal_analyzer.py --file access.log --min-severity high
```

Exit codes: `0` no critical signal; `1` at least one critical signal (SQL or command
injection); `2` bad input (file missing or unreadable). High-severity signals alone exit 0,
so gate on the JSON `summary` if you need to fail on them.

Request lines are URL-decoded (twice) before matching, so `%27%20OR%20%271%27%3D%271` is
caught as a quoted tautology; evidence keeps the raw line. Brute force and flooding counts
cover the whole file, so for a long log slice it by time window first (for example one hour
with `awk '$2 >= "09:00" && $2 < "10:00"'`) or every busy IP looks like a flood.

## Tools Overview

### threat_signal_analyzer.py

Analyzes log files for suspicious activity patterns across multiple threat categories.

| Feature | Description |
|---------|-------------|
| Brute force detection | Counts failed login lines per source IP across the whole file |
| Injection scanning | Detects SQL injection, XSS, command injection in requests |
| Path traversal | Detects `../` sequences, their URL-encoded forms and direct requests for `/etc/passwd`, `/etc/shadow`, `win.ini` |
| Admin probing | Flags requests to admin and sensitive paths such as `/admin`, `/.env` and `/.git` that returned 401, 403 or 404 |
| Rate analysis | Counts requests per source IP across the whole file and flags high volumes |

## Workflows

### Log Analysis Workflow

1. **Collect** - Gather logs from auth, access, application sources
2. **Analyze** - Run threat_signal_analyzer.py across log files
3. **Triage** - Review critical and high severity findings first
4. **Correlate** - Cross-reference findings across log sources
5. **Respond** - Block IPs, reset credentials, escalate as needed

### Incident Investigation Workflow

1. **Scope** - Identify time window and affected systems
2. **Scan** - Run analyzer on all relevant log files
3. **Timeline** - Build timeline from threat signals
4. **Impact** - Assess what was accessed or modified
5. **Contain** - Block threat actors and patch vulnerabilities

### Continuous Monitoring

```bash
# Cron job: analyze auth logs every hour
python scripts/threat_signal_analyzer.py --file /var/log/auth.log --format json --min-severity high > /tmp/threat_report.json

# CI/CD: scan application logs on deployment
python scripts/threat_signal_analyzer.py --file app.log --category injection --format json
```

## Scope & Limitations

**In Scope:**
- Rule-based scanning of a single log file with `threat_signal_analyzer.py` for SQL injection, XSS, command injection, path traversal, failed authentication and brute force, admin path probing, and request flooding.
- Filtering by `--category` (injection, auth, traversal, probe, rate) and `--min-severity`, with text or JSON output.
- Attack categories, severity levels, common log formats, scanner indicators and an incident response playbook in `references/threat-indicators.md`.

**Out of Scope:**
- Real-time monitoring, alert routing or SIEM integration. The script reads one file per run.
- Running an incident response (see `engineering/incident-commander/`) and building a security operations program (see `engineering/senior-secops/`).
- Vault audit log analysis (see `engineering/secrets-vault-manager/`).
- Blocking IPs or changing any system. The script reports signals only.

**Important Caveats:**
- Detection uses regular expressions on log lines and simple counts. Encoded or new attack strings can be missed, and legitimate traffic can match.
- Brute force and flooding thresholds count events per IP across the whole file, not within a time window.
- The script does not detect privilege escalation, check IP reputation or flag unusual access times.
- A quiet report does not mean no attack took place. Findings need correlation with other sources before any response.

## Reference Documentation

- [Threat Indicators](references/threat-indicators.md) - Common attack patterns, indicators of compromise, response playbooks

## Common Patterns Quick Reference

### Threat Categories
| Category | Signals | Severity |
|----------|---------|----------|
| Brute force | 5+ failed logins from same IP in the file (3-4 is Medium) | High |
| SQL injection | UNION SELECT, OR 1=1, DROP TABLE in requests | Critical |
| XSS | script tags, javascript: URIs, event handlers in input | High |
| Path traversal | ../ sequences, /etc/passwd access attempts | High |
| Command injection | `; cat`, `| nc`, `$( )`, backticks | Critical |
| Admin probing | /admin, /wp-admin, /phpmyadmin access attempts | Medium |
| Rate flooding | More than 500 requests from a single IP in the file (more than 200 is Medium) | High |

### Severity Levels
- **CRITICAL** - Active exploitation attempt (injection, RCE)
- **HIGH** - Likely attack in progress (brute force, XSS, path traversal, flooding)
- **MEDIUM** - Suspicious activity requiring investigation
- **LOW** - Informational, possible false positive

### Response Actions
| Severity | Immediate Action | Follow-Up |
|----------|-----------------|-----------|
| Critical | Block IP, alert SOC | Incident report, forensics |
| High | Rate limit, monitor | Review access, check damage |
| Medium | Log and monitor | Weekly review |
| Low | Log only | Monthly trend analysis |

## Anti-Patterns

### Blocking on a Single Regex Hit
**Mistake:** Blocking every IP that produced a signal.
**Why it happens:** The report says "Block source IP" next to each finding.
**Instead:** Check whether the request succeeded (status code, response size, application logs) and whether the IP belongs to a scanner you run or a shared NAT. Block on confirmed malicious intent, not on one pattern match.

### Reading a Quiet Report as "No Attack"
**Mistake:** Closing an investigation because the analyzer found nothing.
**Why it happens:** No output feels like a clean bill of health.
**Instead:** The rules see common, single-line patterns. Obfuscated payloads, slow brute force spread across IPs and post-login abuse are invisible to it. Correlate with other sources before concluding.

### Whole-Month Logs in One Run
**Mistake:** Running the analyzer on 30 days of access logs and acting on the flooding and brute-force counts.
**Why it happens:** It is one command.
**Instead:** Counts are per file. Slice by hour or day first so thresholds mean "per window".

## Files

| File | Purpose |
|------|---------|
| `scripts/threat_signal_analyzer.py` | Log scanner for injection, traversal, auth failures, probes and floods |
| `assets/sample_access_log.txt` | Hostile sample: 10 signals across six categories (exit 1) |
| `assets/sample_clean_log.txt` | Benign traffic, including look-alikes such as `#` fragments and `--` in queries (exit 0) |
| `references/threat-indicators.md` | Attack categories, log formats, scanner indicators and response playbook |
