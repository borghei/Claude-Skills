---
name: threat-detection
description: >
  This skill should be used when the user asks to "analyze logs for threats",
  "detect suspicious activity", "scan for brute force attempts",
  "identify injection attacks", or "audit access patterns for anomalies".
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: engineering
  domain: security
  updated: 2026-04-02
  tags: [security, threat-detection, logs, monitoring, incident-response]
---
# Threat Detection

> **Category:** Engineering
> **Domain:** Security Operations

## Overview

The **Threat Detection** skill provides automated analysis of log files for suspicious patterns including brute force attacks, injection attempts, unusual access patterns, and privilege escalation indicators. It helps security teams triage log data and identify threats before they escalate.

## Quick Start

```bash
# Analyze a log file for threat signals
python scripts/threat_signal_analyzer.py --file /var/log/auth.log

# Analyze with specific threat category
python scripts/threat_signal_analyzer.py --file access.log --category injection

# JSON output for SIEM integration
python scripts/threat_signal_analyzer.py --file auth.log --format json

# Set minimum severity
python scripts/threat_signal_analyzer.py --file access.log --min-severity high
```

## Tools Overview

### threat_signal_analyzer.py

Analyzes log files for suspicious activity patterns across multiple threat categories.

| Feature | Description |
|---------|-------------|
| Brute force detection | Identifies repeated failed login attempts from same source |
| Injection scanning | Detects SQL injection, XSS, command injection in requests |
| Access anomalies | Flags unusual access times, forbidden paths, admin probes |
| Privilege escalation | Detects sudo abuse, role changes, permission modifications |
| Rate analysis | Identifies request flooding and denial-of-service patterns |
| IP reputation | Flags known-bad patterns (scanners, bots, TOR indicators) |

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

## Reference Documentation

- [Threat Indicators](references/threat-indicators.md) - Common attack patterns, indicators of compromise, response playbooks

## Common Patterns Quick Reference

### Threat Categories
| Category | Signals | Severity |
|----------|---------|----------|
| Brute force | 5+ failed logins from same IP in 5 min | High |
| SQL injection | UNION SELECT, OR 1=1, DROP TABLE in requests | Critical |
| XSS | script tags, javascript: URIs, event handlers in input | High |
| Path traversal | ../ sequences, /etc/passwd access attempts | High |
| Command injection | ; cat /etc/passwd, | nc, backtick usage | Critical |
| Admin probing | /admin, /wp-admin, /phpmyadmin access attempts | Medium |
| Rate flooding | 100+ requests/minute from single IP | High |

### Severity Levels
- **CRITICAL** - Active exploitation attempt (injection, RCE)
- **HIGH** - Likely attack in progress (brute force, privilege escalation)
- **MEDIUM** - Suspicious activity requiring investigation
- **LOW** - Informational, possible false positive

### Response Actions
| Severity | Immediate Action | Follow-Up |
|----------|-----------------|-----------|
| Critical | Block IP, alert SOC | Incident report, forensics |
| High | Rate limit, monitor | Review access, check damage |
| Medium | Log and monitor | Weekly review |
| Low | Log only | Monthly trend analysis |
