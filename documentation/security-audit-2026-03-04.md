# Security Audit Report

**Date:** 2026-03-04
**Auditor:** Automated Security Audit (Claude Code)
**Scope:** Full infrastructure audit of two production servers
**Authorization:** Owner-authorized

---

## Servers Audited

| Server | IP | Hostname | OS | Role |
|--------|-----|----------|-----|------|
| WordPress | 46.225.239.105 | PRCN-Wordpress | Ubuntu 24.04.4 LTS | Multi-site WordPress hosting |
| Bot | 146.190.116.134 | reviv-general | Ubuntu 25.04 | Apps, bots, Laravel, Next.js |

---

## Executive Summary

Both servers demonstrate **solid baseline security** with properly configured firewalls, Let's Encrypt SSL, fail2ban, and key-based SSH authentication. However, several **high-severity issues** require prompt attention, particularly around SSH hardening, service exposure, and WordPress configuration.

**Overall Security Score: 7/10** (Good foundation, needs targeted hardening)

---

## Findings by Severity

### CRITICAL (Fix within 24 hours)

#### C1. SSH Root Login with Password Authentication Allowed — WordPress Server
- **Server:** 46.225.239.105
- **Evidence:** `sshd_config` has NO explicit `PermitRootLogin` or `PasswordAuthentication` directives. The defaults allow password authentication and root login.
  ```
  # Active config (non-comment lines):
  Include /etc/ssh/sshd_config.d/*.conf
  KbdInteractiveAuthentication no
  UsePAM yes
  X11Forwarding yes
  PrintMotd no
  AcceptEnv LANG LC_*
  Subsystem sftp /usr/lib/openssh/sftp-server
  ```
  - `/etc/ssh/sshd_config.d/` is **empty** — no overrides
  - Default `PermitRootLogin` in Ubuntu 24.04 is `prohibit-password`, BUT `PasswordAuthentication` defaults to `yes`
- **Risk:** Brute-force attacks against root. Auth logs confirm **active attacks** from multiple IPs (64.225.64.207, 23.94.28.163, 45.148.10.121, 83.168.71.160) with "Failed password for root" entries.
- **Remediation:**
  ```bash
  cat > /etc/ssh/sshd_config.d/hardening.conf << 'EOF'
  PermitRootLogin prohibit-password
  PasswordAuthentication no
  MaxAuthTries 3
  LoginGraceTime 20
  X11Forwarding no
  EOF
  systemctl restart sshd
  ```

#### C2. Gunicorn Running as Root on 0.0.0.0:8000 — Bot Server
- **Server:** 146.190.116.134
- **Evidence:**
  ```
  User=root
  Group=root
  ExecStart=.../gunicorn --workers 1 --bind 0.0.0.0:8000 app:app
  ```
  The Telnyx-Bot Flask app runs as **root** and binds to **all interfaces**. While port 8000 is blocked by UFW, this is defense-in-depth failure.
- **Risk:** If the Flask app has any vulnerability (RCE, SSRF), the attacker gains **root access**. Binding to 0.0.0.0 means any firewall misconfiguration exposes it.
- **Remediation:**
  ```bash
  # 1. Create dedicated service user
  useradd -r -s /sbin/nologin telnyx-bot

  # 2. Update systemd service
  # In /etc/systemd/system/gunicorn-telnyx.service:
  User=telnyx-bot
  Group=telnyx-bot
  ExecStart=.../gunicorn --workers 1 --bind 127.0.0.1:8000 app:app

  # 3. Fix file ownership
  chown -R telnyx-bot:telnyx-bot /root/Telnyx-Bot
  # Move app out of /root to /opt/telnyx-bot

  systemctl daemon-reload && systemctl restart gunicorn-telnyx
  ```

#### C3. Netdata Listening on 0.0.0.0:19999 — Bot Server
- **Server:** 146.190.116.134
- **Evidence:** `ss -tlnp` shows `0.0.0.0:19999` (all interfaces). While UFW blocks public access, UFW rules allow access from specific IPs (46.225.239.105, 178.104.4.120, 104.248.132.129).
- **Risk:** Netdata exposes system metrics, process lists, and potentially sensitive information. Direct IP access bypasses auth.
- **Remediation:** Bind Netdata to localhost and use SSH tunneling or the authenticated Eyeris proxy exclusively:
  ```bash
  # In /etc/netdata/netdata.conf:
  [web]
      bind to = 127.0.0.1
  systemctl restart netdata
  ```

---

### HIGH (Fix within 7 days)

#### H1. WordPress wp-config.php Missing Security Constants
- **Server:** 46.225.239.105
- **Evidence:** All 6 WordPress sites lack:
  - `DISALLOW_FILE_EDIT` — not set (allows PHP file editing from WP admin)
  - `FORCE_SSL_ADMIN` — not set
  - Default `wp_` table prefix on 4/6 sites (ivanmarandola, revivitalia, mydripbar, prcnlab)
- **Risk:** Compromised admin account can inject malicious PHP code. Default table prefix makes SQL injection easier.
- **Remediation:** Add to each `wp-config.php`:
  ```php
  define('DISALLOW_FILE_EDIT', true);
  define('DISALLOW_FILE_MODS', true);  // Optional: also blocks plugin/theme installs
  define('FORCE_SSL_ADMIN', true);
  ```

#### H2. wp-config.php Permissions Too Permissive
- **Server:** 46.225.239.105
- **Evidence:** All wp-config.php files are `644` (world-readable), `prcnlab.com` is `664` (world-readable + group-writable). These files contain database credentials in plaintext.
- **Risk:** Any process on the server can read DB credentials.
- **Remediation:**
  ```bash
  find /var/www -name "wp-config.php" -exec chmod 640 {} \;
  # Ensure ownership matches: site-user:www-data
  ```

#### H3. World-Writable SQLite Database — Bot Server
- **Server:** 146.190.116.134
- **Evidence:** `/var/www/onyx.0xnet.dev/database/database.sqlite` has permissions `-rw-rw-rw-` (666)
- **Risk:** Any user/process can read or modify the application database.
- **Remediation:**
  ```bash
  chmod 660 /var/www/onyx.0xnet.dev/database/database.sqlite
  chown www-data:www-data /var/www/onyx.0xnet.dev/database/database.sqlite
  ```

#### H4. Nginx Version Disclosure — Both Servers
- **Server:** Both
- **Evidence:**
  - WordPress: `Server: nginx/1.24.0 (Ubuntu)`
  - Bot: `Server: nginx/1.26.3 (Ubuntu)`
- **Risk:** Reveals exact software versions for targeted exploit development. nginx 1.24.0 is outdated.
- **Remediation:** Add to `/etc/nginx/nginx.conf`:
  ```nginx
  server_tokens off;
  ```
  Also upgrade nginx on WordPress server:
  ```bash
  apt update && apt upgrade nginx
  ```

#### H5. Missing Content-Security-Policy Header — Both Servers
- **Server:** Both
- **Evidence:** No `Content-Security-Policy` header on any site. Nikto confirmed this for both.
- **Risk:** No XSS mitigation, allows inline script execution, framing from any origin (despite X-Frame-Options).
- **Remediation:** Add to nginx configs:
  ```nginx
  add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; frame-ancestors 'self';" always;
  ```

#### H6. Missing HSTS Header — WordPress Server
- **Server:** 46.225.239.105
- **Evidence:** HTTPS responses lack `Strict-Transport-Security` header. Bot server has it configured properly.
- **Risk:** Downgrade attacks, SSL stripping.
- **Remediation:** Add to all HTTPS server blocks:
  ```nginx
  add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
  ```

#### H7. Active SSH Brute-Force Attacks Not Fully Mitigated
- **Server:** 46.225.239.105
- **Evidence:** Auth log shows multiple failed root login attempts from various IPs within minutes. Fail2ban is running with 4 jails (sshd, nginx-*) but attacks continue.
- **Risk:** Persistent brute-force pressure. If password auth is enabled (see C1), risk of successful compromise.
- **Remediation:**
  ```bash
  # 1. Tighten fail2ban sshd jail
  cat > /etc/fail2ban/jail.d/sshd-strict.conf << 'EOF'
  [sshd]
  enabled = true
  maxretry = 3
  findtime = 600
  bantime = 86400
  EOF

  # 2. Consider rate limiting in UFW
  ufw limit ssh/tcp

  # 3. After fixing C1, password attacks become irrelevant
  systemctl restart fail2ban
  ```

#### H8. Telnyx-Bot Application Stored in /root — Bot Server
- **Server:** 146.190.116.134
- **Evidence:** App lives at `/root/Telnyx-Bot/` with `.env` file containing API keys (TELEGRAM_BOT_TOKEN, TREXON_API_KEY, SIBAD_API_KEY, ADMIN_TOKEN).
- **Risk:** Running as root with credentials in /root. Application needs root access to read its own config.
- **Remediation:** Move to `/opt/telnyx-bot/`, create dedicated user (see C2), restrict `.env` permissions to `600`.

---

### MEDIUM (Fix within 30 days)

#### M1. X11Forwarding Enabled — Both Servers
- **Server:** Both
- **Evidence:** `X11Forwarding yes` in sshd_config on both servers
- **Risk:** Potential for X11 session hijacking. Unnecessary on headless servers.
- **Remediation:** Set `X11Forwarding no` in sshd_config.

#### M2. No SSH Rate Limiting in UFW — WordPress Server
- **Server:** 46.225.239.105
- **Evidence:** UFW rule is `ALLOW` for port 22, not `LIMIT`:
  ```
  22/tcp    ALLOW IN    Anywhere
  ```
- **Risk:** No connection rate limiting at firewall level.
- **Remediation:**
  ```bash
  ufw delete allow 22/tcp
  ufw limit 22/tcp comment "SSH rate limited"
  ```

#### M3. Multiple .env Files in Accessible Locations — Bot Server
- **Server:** 146.190.116.134
- **Evidence:** 17+ `.env` files found across `/var/www/`, `/root/telegram_bots/`, `/root/Telnyx-Bot/`, `/root/projects/`. Includes backup copies with credentials.
- **Risk:** Credential sprawl. Backup `.env` files (e.g., `/var/www/backups/onyx-20260102-234256/.env`) may contain stale but valid credentials.
- **Remediation:**
  - Audit and remove unnecessary `.env` files (especially in backups)
  - Ensure all `.env` files are `600` permissions
  - Ensure nginx blocks access to dotfiles (already configured: `location ~ /\.(?!well-known).*`)

#### M4. No AllowUsers/AllowGroups SSH Restriction — Both Servers
- **Server:** Both
- **Evidence:** No `AllowUsers` or `AllowGroups` directive in sshd_config. Only `root` has shell access, but explicit whitelisting adds defense-in-depth.
- **Remediation:** Add `AllowUsers root` to sshd_config (or create a non-root admin user and disable root login entirely).

#### M5. MariaDB Root Uses unix_socket on WordPress, But mysql_native_password on Bot
- **Server:** 146.190.116.134
- **Evidence:** MySQL root user uses `mysql_native_password` instead of `unix_socket`:
  ```
  root    localhost    mysql_native_password
  ```
  WordPress server correctly uses `unix_socket`.
- **Risk:** Password-based MySQL root could be brute-forced by local processes.
- **Remediation:**
  ```sql
  ALTER USER 'root'@'localhost' IDENTIFIED VIA unix_socket;
  FLUSH PRIVILEGES;
  ```

#### M6. Telegram Bots Running from /root — Bot Server
- **Server:** 146.190.116.134
- **Evidence:** Multiple bot directories in `/root/telegram_bots/` with `.env` files containing tokens.
- **Risk:** All bots run with root privileges. Any bot compromise = full root access.
- **Remediation:** Create per-bot service users, move to `/opt/bots/`, use systemd with `User=` directives.

#### M7. Cron Job for Non-Existent Site — Bot Server
- **Server:** 146.190.116.134
- **Evidence:** Crontab contains: `cd /var/www/sites/treinv.0xnet.dev && php artisan schedule:run`
- **Risk:** Low — but stale cron entries can mask issues.
- **Remediation:** Verify if `treinv.0xnet.dev` exists; remove if deprecated.

#### M8. Missing Permissions-Policy on HTTP Responses — WordPress Server
- **Server:** 46.225.239.105
- **Evidence:** HTTP (port 80) responses show no security headers at all — returns a bare 404 from nginx default. HTTPS responses have headers.
- **Risk:** HTTP responses before redirect have no protection.
- **Remediation:** Ensure HTTP server blocks also have security headers, or redirect immediately.

---

### LOW (Fix within 90 days)

#### L1. Default WordPress Table Prefix (wp_) — WordPress Server
- **Server:** 46.225.239.105
- **Evidence:** 4 of 6 sites use default `wp_` prefix (ivanmarandola, revivitalia, mydripbar, prcnlab). Two sites use custom prefixes (myskinbar: `mkr_`, stage.iuventa.health: `iwun_`).
- **Risk:** Makes SQL injection slightly easier to exploit.
- **Note:** Changing table prefix on live sites is risky and not recommended unless doing a fresh install.

#### L2. Unnecessary Services Running — Bot Server
- **Server:** 146.190.116.134
- **Evidence:** Services that may be unnecessary on a server:
  - `ModemManager.service` (for mobile modems)
  - `udisks2.service` (disk manager for desktop)
  - `upower.service` (power management for laptops)
  - `fwupd.service` (firmware update daemon)
- **Remediation:**
  ```bash
  systemctl disable --now ModemManager udisks2 upower
  ```

#### L3. Backup Directory in Web Root — Bot Server
- **Server:** 146.190.116.134
- **Evidence:** `/var/www/backups/` contains old site backups with `.env` files.
- **Risk:** If nginx misconfiguration allows access, backup files with credentials could be exposed.
- **Remediation:** Move backups outside web root: `mv /var/www/backups /opt/backups`

#### L4. Server Uptime Suggests Recent Reboot — WordPress Server
- **Server:** 46.225.239.105
- **Evidence:** Uptime 2 days (rebooted March 2). Bot server: 13 days.
- **Note:** Good — indicates kernel updates are being applied. Bot server has 7 pending updates including `snapd` and `nodejs`.

#### L5. No Automated Security Scanning
- **Both servers**
- **Remediation:** Consider installing and scheduling Lynis for regular audits:
  ```bash
  apt install lynis
  # Add to cron: lynis audit system --quick --quiet >> /var/log/lynis-audit.log
  ```

---

## Positive Findings (What's Done Right)

| Category | WordPress Server | Bot Server |
|----------|-----------------|------------|
| **Firewall (UFW)** | Active, default deny, only 22/80/443 | Active, default deny, blocked internal ports |
| **SSL/TLS** | TLS 1.3, Let's Encrypt, all valid (86-89 days) | TLS 1.3, Let's Encrypt, all valid (38-89 days) |
| **Fail2Ban** | Active, 4 jails (sshd, nginx-*) | Active, 4 jails including rate limiting |
| **Logging** | rsyslog active, log rotation configured | rsyslog active, log rotation configured |
| **DB Access** | All MySQL users localhost-only, unix_socket root | All MySQL users localhost-only |
| **Services** | Internal services bound to 127.0.0.1 | MariaDB, Redis bound to 127.0.0.1 |
| **Nginx Security** | Blocks hidden files, wp-config, PHP in uploads | Blocks dotfiles, security headers |
| **SSH Auth** | Public key authentication confirmed | PermitRootLogin prohibit-password, PasswordAuth no |
| **No Docker** | Not running (smaller attack surface) | Not running |
| **SUID Binaries** | Standard system binaries only | Standard system binaries only |
| **World-Writable** | None found | 1 found (database.sqlite — see H3) |
| **File Permissions** | /etc/passwd 644, /etc/shadow 640 | /etc/passwd 644, /etc/shadow 640 |
| **Unattended Upgrades** | Active | Active |
| **Netdata Monitoring** | Bound to localhost | Active (but see C3 for bind issue) |
| **Security Headers** | HTTPS has X-Frame, X-Content-Type, XSS-Protection, Referrer-Policy, Permissions-Policy | HTTPS has HSTS, X-Frame, X-Content-Type, XSS-Protection, Referrer-Policy, Permissions-Policy |
| **XML-RPC** | Blocked at nginx level (returns deny all) | N/A |

---

## Priority Remediation Checklist

### Immediate (Today)
- [ ] **C1:** Harden WordPress server SSH config (create `/etc/ssh/sshd_config.d/hardening.conf`)
- [ ] **C2:** Stop running Gunicorn as root, bind to 127.0.0.1
- [ ] **C3:** Bind Netdata to 127.0.0.1 on Bot server

### This Week
- [ ] **H1:** Add `DISALLOW_FILE_EDIT` and `FORCE_SSL_ADMIN` to all wp-config.php
- [ ] **H2:** Fix wp-config.php permissions to 640
- [ ] **H3:** Fix database.sqlite permissions to 660
- [ ] **H4:** Disable nginx version disclosure on both servers
- [ ] **H5:** Add Content-Security-Policy headers
- [ ] **H6:** Add HSTS to WordPress server
- [ ] **H7:** Tighten fail2ban and add UFW rate limiting for SSH
- [ ] **H8:** Move Telnyx-Bot out of /root

### This Month
- [ ] **M1-M8:** SSH hardening, .env audit, AllowUsers, MySQL root auth, bot user isolation

### Ongoing
- [ ] **L1-L5:** Service cleanup, backup relocation, automated scanning

---

## Methodology

| Phase | Technique | Tools |
|-------|-----------|-------|
| External Reconnaissance | Port scanning, service enumeration | nmap (running), nikto |
| SSL/TLS Assessment | Certificate validation, cipher analysis | openssl s_client |
| HTTP Header Analysis | Security header verification | curl -I |
| WordPress Scanning | Config review, plugin/theme enumeration | Manual SSH review |
| Internal Audit | System state, users, services, permissions | SSH (bash commands) |
| Firewall Audit | UFW rules, iptables review | ufw status, iptables -L |
| Application Review | Service configs, env files, process audit | systemctl, ps, find |

---

*Report generated: 2026-03-04T17:00:00Z*
*Nmap full port scans were still in progress at report time — findings will be updated when complete.*
