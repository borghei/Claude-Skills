# Access Control Standards Reference

Comprehensive guide to identity, authentication, authorization, and access governance covering MFA, SSO, PAM, Zero Trust, and hardware security key deployment.

---

## 1. Multi-Factor Authentication (MFA) Implementation

### MFA Factor Types (Ranked by Security)

| Rank | Factor Type | Technology | Phishing Resistant | Recommendation |
|------|------------|------------|-------------------|----------------|
| 1 | Hardware Security Key | FIDO2/WebAuthn, U2F | Yes | Required for admins and high-value targets |
| 2 | Biometric + Hardware | YubiKey Bio, Windows Hello | Yes | Preferred for shared workstations |
| 3 | Platform Authenticator | Touch ID, Face ID, Windows Hello | Yes | Good for employee endpoints |
| 4 | Push Notification | Okta Verify, Duo Push, MS Authenticator | Partially (number matching helps) | Acceptable for standard users with number matching |
| 5 | TOTP | Google Authenticator, Authy, 1Password | No | Minimum acceptable factor |
| 6 | SMS/Voice | Text message, phone call | No | PROHIBITED — SIM swap vulnerable |
| 7 | Email | One-time code via email | No | PROHIBITED — trivially phishable |

### MFA Enforcement Policy

```
MANDATORY: MFA for 100% of accounts, no exceptions.

Privileged accounts (IdP admins, cloud admins, prod access):
  → FIDO2/WebAuthn hardware security key REQUIRED
  → TOTP and push DISABLED as fallback
  → Number matching enforced if push is used anywhere

Standard accounts (all employees):
  → TOTP minimum, FIDO2 preferred
  → Push with number matching acceptable
  → SMS/Email PROHIBITED

Service accounts:
  → No interactive MFA (machine accounts)
  → Use managed identity, Workload Identity, or OIDC federation
  → Short-lived credentials (STS, dynamic secrets)

External users (contractors, partners):
  → TOTP minimum
  → FIDO2 required for any admin access
  → Access time-limited and scoped
```

### MFA Rollout Plan

**Phase 1 — Admins (Week 1-2)**
1. Procure hardware keys (2 per admin)
2. Register primary key with IdP
3. Register backup key, store securely
4. Configure IdP policy: require phishing-resistant MFA for admin roles
5. Disable TOTP/push fallback for admin accounts
6. Test authentication flow

**Phase 2 — All Employees (Week 3-6)**
1. Announce MFA requirement (2 weeks notice)
2. Provide self-service TOTP enrollment guide
3. Offer hardware key for employees who request it
4. Configure IdP policy: require MFA for all users
5. Grace period: 7 days to enroll
6. Auto-enforce after grace period (block unenrolled users)

**Phase 3 — External Users (Week 7-8)**
1. Notify external users of MFA requirement
2. Provide enrollment guide for TOTP
3. Enable MFA requirement for external identities
4. Support team trained for MFA help

### Phishing-Resistant MFA Deep Dive

**Why FIDO2/WebAuthn?**
- Cryptographic proof bound to the specific website origin
- Cannot be phished — key will not respond to wrong origin
- No shared secrets (unlike TOTP which has a shared seed)
- Immune to real-time phishing proxies (evilginx, modlishka)
- Resistant to social engineering (no code to share)

**How FIDO2 works:**
```
Registration:
1. User visits IdP login
2. Browser prompts for security key
3. Key generates unique public/private key pair for that origin
4. Public key stored by IdP
5. Private key never leaves the hardware key

Authentication:
1. User visits IdP login, enters username
2. IdP sends challenge
3. Browser checks origin (example.okta.com) — MUST match registration
4. Key signs challenge with private key (requires touch + PIN)
5. IdP verifies signature with stored public key
6. If attacker's proxy presents wrong origin → key refuses to sign
```

---

## 2. Hardware Security Key Deployment (YubiKey)

### YubiKey Product Selection

| Model | FIDO2 | PIV | TOTP | OpenPGP | NFC | Biometric | Use Case |
|-------|-------|-----|------|---------|-----|-----------|----------|
| YubiKey 5 NFC | Yes | Yes | Yes | Yes | Yes | No | Standard employee key |
| YubiKey 5C NFC | Yes | Yes | Yes | Yes | Yes | No | USB-C + NFC |
| YubiKey 5Ci | Yes | Yes | Yes | Yes | No | No | iPhone Lightning + USB-C |
| YubiKey Bio - FIDO Edition | Yes | No | No | No | No | Yes | Shared workstations |
| YubiKey 5 FIPS | Yes | Yes | Yes | Yes | No | No | FedRAMP/government |

**Recommendation:** YubiKey 5C NFC for most employees (works with USB-C laptops and NFC-capable phones).

### YubiKey Enrollment Process

**Prerequisites:**
- IdP supports FIDO2/WebAuthn (Okta, Azure AD, Google Workspace)
- User has 2 YubiKey devices (primary + backup)
- IT admin has configured FIDO2 as allowed authentication method

**Step-by-Step Enrollment (Okta Example):**

```
1. User logs into Okta dashboard
2. Navigate to Settings > Security Methods
3. Click "Set up" next to "Security Key or Biometric"
4. Insert YubiKey and click "Set up"
5. Browser prompts for security key
6. Touch the YubiKey sensor
7. Set a PIN when prompted (FIDO2 User Verification)
8. Key is registered — name it "Primary YubiKey"
9. Repeat steps 3-8 for backup key — name it "Backup YubiKey"
10. Store backup key in secure location (home safe, locked drawer)
```

**Step-by-Step Enrollment (Azure AD/Entra ID):**

```
1. Navigate to https://mysignins.microsoft.com/security-info
2. Click "Add sign-in method"
3. Select "Security key"
4. Choose "USB device"
5. Click "Next" — browser prompts for security key
6. Insert YubiKey and touch sensor
7. Create a PIN when prompted
8. Name the key and click "Done"
9. Repeat for backup key
```

**Step-by-Step Enrollment (Google Workspace):**

```
1. Go to myaccount.google.com/security
2. Under "Signing in to Google" click "2-Step Verification"
3. Click "Add security key"
4. Click "USB or Bluetooth"
5. Insert YubiKey and touch sensor
6. Name the key
7. Repeat for backup key
8. Admin: Enable Advanced Protection Program for admin accounts
```

### YubiKey Policy Requirements

```yaml
enrollment:
  keys_per_user: 2  # primary + backup
  backup_storage: "secure location (home safe, locked drawer, IT vault)"
  pin_required: true  # FIDO2 User Verification
  touch_required: true  # always require physical touch

key_management:
  inventory:
    track: [serial_number, assigned_user, issuance_date, status]
    review: quarterly
  lost_key_process:
    1: "User reports lost key immediately to IT"
    2: "IT revokes lost key in IdP within 1 hour"
    3: "User authenticates via backup key"
    4: "Identity reverification (video call + manager confirmation)"
    5: "New primary key issued and enrolled"
    6: "Incident logged in security ticketing system"
  stolen_key_process:
    1: "Same as lost key process"
    2: "Additional: security team assesses risk of compromised PIN"
    3: "If PIN may be compromised: force password reset + re-enroll all keys"

enforcement:
  admin_accounts:
    required: true
    fallback_allowed: false  # no TOTP/push fallback
  standard_accounts:
    required: false  # encouraged but not mandatory
    fallback_allowed: true  # TOTP fallback OK
  high_value_access:
    required: true  # production, financial, customer data
    fallback_allowed: false
```

### YubiKey Inventory Spreadsheet Template

| Serial Number | Model | Assigned To | Role | Enrollment Date | Status | Backup Key Serial | Last Verified |
|--------------|-------|-------------|------|-----------------|--------|-------------------|---------------|
| 12345678 | 5C NFC | jane.admin | IdP Admin | 2026-01-15 | Active | 12345679 | 2026-03-01 |
| 12345679 | 5C NFC | jane.admin | IdP Admin (BACKUP) | 2026-01-15 | Backup | - | 2026-03-01 |

---

## 3. Single Sign-On (SSO) Configuration

### Protocol Selection

| Protocol | Use Case | Security | Recommendation |
|----------|----------|----------|----------------|
| SAML 2.0 | Web applications, enterprise SSO | Strong (XML signatures) | Standard for enterprise apps |
| OIDC / OAuth 2.0 | Modern web/mobile apps, APIs | Strong (JWT tokens) | Preferred for new applications |
| LDAP/LDAPS | Legacy directory integration | Varies (LDAPS required) | Migrate to SAML/OIDC when possible |
| Password-based SSO | Form-fill SSO | Weak | PROHIBITED — use SAML/OIDC |
| WS-Federation | Microsoft-centric environments | Strong | Legacy — migrate to OIDC |

### SSO Security Requirements

```
Session Management:
  - Session timeout: maximum 8 hours for standard apps
  - Session timeout: maximum 1 hour for sensitive apps (finance, admin)
  - Idle timeout: 30 minutes
  - Force re-authentication for sensitive operations
  - Session tokens stored securely (HttpOnly, Secure, SameSite cookies)

Token Configuration:
  - SAML assertion validity: maximum 5 minutes
  - OIDC access token lifetime: maximum 1 hour
  - OIDC refresh token lifetime: maximum 8 hours (or until session timeout)
  - Token binding to client (if supported)

SAML Security:
  - Assertions MUST be signed
  - Assertions SHOULD be encrypted
  - NameID format: persistent or email
  - Single Logout (SLO) configured
  - Certificate rotation plan documented

OIDC Security:
  - Authorization Code flow with PKCE (not implicit flow)
  - State parameter used (CSRF protection)
  - Nonce parameter used (replay protection)
  - Token endpoint authentication: private_key_jwt or client_secret_post
  - Redirect URIs exactly match (no wildcards)
```

### SCIM Provisioning

```
SCIM (System for Cross-domain Identity Management) v2.0:

Benefits:
- Automated user creation when employee joins
- Automated deactivation when employee leaves
- Group membership sync for RBAC
- Attribute sync (name, email, title, department)

Required SCIM Events:
1. User created → account provisioned in all integrated apps
2. User deactivated → account disabled in all apps within 1 hour
3. User group changed → permissions updated in all apps
4. User attribute changed → profile updated in all apps

Deprovisioning Checklist:
- [ ] IdP account disabled
- [ ] All SSO sessions revoked immediately
- [ ] All SCIM-provisioned accounts deactivated
- [ ] API keys revoked
- [ ] SSH keys revoked
- [ ] VPN access revoked
- [ ] Hardware security keys returned and deregistered
- [ ] Shared drives access removed
- [ ] Email forwarding configured (if needed)
- [ ] Offboarding ticket closed
```

---

## 4. Privileged Access Management (PAM)

### PAM Architecture

```
Standard Access:
  User → IdP (SSO + MFA) → Application

Privileged Access:
  User → IdP (SSO + FIDO2) → PAM Platform → Approval Workflow → Time-Limited Session → Target System
                                                    ↓
                                              Session Recording
                                                    ↓
                                              Audit Log → SIEM
```

### JIT (Just-In-Time) Access Implementation

```yaml
jit_access:
  principles:
    - Zero standing privileges (no permanent admin access)
    - Access granted on demand, revoked automatically
    - Every access request requires justification
    - Time-limited sessions (maximum 4 hours)
    - All sessions recorded

  workflow:
    1_request:
      - User submits access request via PAM portal
      - Specifies: target system, role, duration, justification
    2_approval:
      - Auto-approve: pre-authorized break-glass (triggers alert)
      - Manager approval: standard privileged access
      - Security team approval: cross-environment access
      - Approval SLA: 30 minutes during business hours
    3_activation:
      - Temporary credentials generated
      - Session time limit enforced
      - Recording started
    4_deactivation:
      - Credentials automatically revoked at expiry
      - Session recording stored for 1 year
      - Activity logged to SIEM

  platform_options:
    - Azure PIM (Privileged Identity Management)
    - CyberArk Privileged Access Manager
    - HashiCorp Vault + Boundary
    - AWS IAM Identity Center
    - Okta Privileged Access
    - Teleport (SSH + K8s + DB access)
```

### Break-Glass Procedure

```yaml
break_glass:
  purpose: "Emergency access when normal approval workflow is unavailable"

  accounts:
    - Stored in physical safe + password manager (dual control)
    - Known to minimum 3 people (CTO, VP Engineering, Security Lead)
    - MFA configured with dedicated hardware keys stored with credentials
    - Tested quarterly (documented test results)

  activation_process:
    1: "Declare emergency (must be documented)"
    2: "Retrieve break-glass credentials (dual authorization)"
    3: "Activate account (triggers immediate alert to security team + management)"
    4: "Perform emergency actions"
    5: "Deactivate account immediately after use"
    6: "Rotate break-glass credentials"
    7: "Post-incident review within 48 hours"
    8: "Document all actions taken during break-glass session"

  monitoring:
    - Break-glass account login → immediate PagerDuty alert
    - All actions logged to immutable audit trail
    - Post-use review mandatory within 48 hours
    - Credentials rotated after every use
```

---

## 5. Role-Based Access Control (RBAC)

### RBAC Model Design

```
Principle: Users get ZERO permissions by default.
Access granted ONLY through role assignment.
Roles map to job functions, NOT individuals.

Role Hierarchy Example:
├── Viewer (read-only access to assigned resources)
├── Editor (create/update in assigned resources)
├── Admin (full control of assigned resources)
├── Security Admin (security configuration, audit access)
├── Super Admin (organization-wide admin — JIT only)
└── Break-Glass (emergency full access — monitored)
```

### Access Recertification Process

```
Quarterly Access Review:

Week 1: Generate access report
  - Export all user-role assignments from IdP
  - Export all service account permissions
  - Export all API key assignments
  - Flag: dormant accounts (>60 days no login)
  - Flag: excessive permissions (admin roles)
  - Flag: cross-environment access

Week 2: Manager review
  - Each manager reviews their team's access
  - For each access grant: Certify (keep) or Revoke
  - Must provide business justification for admin access
  - Deadline: 5 business days

Week 3: Remediation
  - Revoked access removed within 24 hours
  - Dormant accounts disabled
  - Excessive permissions right-sized
  - Missing access grants processed

Week 4: Report
  - Compliance report generated
  - Exceptions documented and approved
  - Metrics: total reviews, revocations, exceptions
  - Report filed as compliance evidence
```

### Separation of Duties Matrix

| Role A | Role B | Conflict | Reason |
|--------|--------|----------|--------|
| Code Developer | Code Deployer | Yes | Prevents unauthorized code deployment |
| Payment Initiator | Payment Approver | Yes | Prevents fraudulent payments |
| User Creator | Access Approver | Yes | Prevents unauthorized access grants |
| Security Admin | System Admin | Yes | Independent security oversight |
| Audit Reviewer | System Operator | Yes | Independent audit function |
| Database Admin | Application Admin | Conditional | Separate if handling sensitive data |

---

## 6. Zero Trust Architecture

### Zero Trust Principles

```
1. Never trust, always verify
   - Every access request verified regardless of network location
   - Internal network provides NO implicit trust
   - VPN does not equal trust

2. Least privilege access
   - Minimum permissions for the task
   - Time-limited access (JIT)
   - Scoped to specific resources

3. Assume breach
   - Design as if attackers are already inside
   - Microsegmentation limits lateral movement
   - Continuous monitoring for anomalies
   - Rapid detection and response

4. Verify explicitly
   - User identity (MFA, risk-based auth)
   - Device identity (MDM, device certificates)
   - Device posture (patched, encrypted, EDR running)
   - Request context (location, time, behavior)

5. Use data-driven decisions
   - Risk scoring for access decisions
   - Behavioral analytics (UEBA)
   - Continuous assessment (not just at login)
```

### Zero Trust Implementation Roadmap

**Phase 1 — Identity Foundation (Month 1-3)**
1. Deploy centralized IdP with SSO
2. Enforce MFA for all users (FIDO2 for admins)
3. Implement SCIM provisioning
4. Remove shared accounts
5. Establish access review process

**Phase 2 — Device Trust (Month 3-6)**
1. Deploy MDM (Jamf, Intune, Kandji)
2. Enforce device compliance:
   - Disk encryption
   - OS version minimum
   - EDR running
   - Screen lock enabled
3. Device posture checked before access
4. BYOD containerization

**Phase 3 — Application Security (Month 6-9)**
1. All applications behind identity-aware proxy
2. SSO enforced (local auth disabled)
3. Session management configured
4. API authentication with OAuth 2.0 / OIDC
5. Service mesh for service-to-service auth

**Phase 4 — Network Transformation (Month 9-12)**
1. Microsegmentation deployed
2. VPN replaced with ZTNA
3. Network no longer determines trust
4. Egress filtering enforced
5. DNS security (DoH/DoT) deployed

**Phase 5 — Continuous Verification (Month 12+)**
1. Risk-based authentication (step-up MFA)
2. Continuous session evaluation
3. UEBA for anomaly detection
4. Automated response to high-risk events
5. Regular red team exercises to validate

### Zero Trust Technology Stack

| Layer | Purpose | Tools |
|-------|---------|-------|
| Identity | User authentication | Okta, Azure AD, Google Workspace |
| Device | Device trust | Jamf, Intune, Kandji, Kolide |
| Network | Access proxy | Cloudflare Access, Zscaler, Tailscale, Twingate |
| Application | Service auth | Service mesh (Istio, Linkerd), mTLS |
| Data | Data protection | DLP, encryption, tokenization |
| Monitoring | Visibility | SIEM, UEBA, NDR |

---

## 7. Service Account Governance

### Service Account Lifecycle

```
1. Creation
   - Business justification required
   - Owner assigned (individual, not team)
   - Minimum permissions (principle of least privilege)
   - Expiration date set (maximum 1 year, renewable)
   - Registered in service account inventory

2. Operation
   - Credentials stored in secrets manager (never in code)
   - Automatic credential rotation (90 days maximum)
   - Usage monitored (anomaly detection)
   - Access logged to SIEM

3. Review (Quarterly)
   - Owner confirms still needed
   - Permissions validated (still minimum required)
   - Last usage checked (disable if >90 days idle)
   - Credentials rotation verified

4. Decommissioning
   - Credentials revoked
   - Service account disabled (not deleted — audit trail)
   - Associated resources reviewed
   - Removal documented
```

### Service Account Security Rules

```
MUST:
- Have a unique identity (never share between services)
- Have an assigned human owner
- Use machine credentials (not human passwords)
- Store credentials in secrets manager
- Rotate credentials every 90 days
- Be inventoried and reviewed quarterly

MUST NOT:
- Use shared credentials between services
- Store credentials in source code
- Have interactive login capability (where possible)
- Have broader permissions than needed
- Persist beyond their required lifetime
- Use long-lived tokens when short-lived alternatives exist
```

---

## 8. SSH Key Management

### SSH Key Best Practices

```
Key Algorithm (Preferred Order):
1. ED25519 (recommended — fast, secure, small keys)
2. ECDSA-SK (hardware-bound, FIDO2 security key)
3. ED25519-SK (hardware-bound, FIDO2 security key)
4. RSA 4096-bit (legacy compatibility)

Generate ED25519 key:
  ssh-keygen -t ed25519 -C "user@company.com"

Generate hardware-bound key (requires YubiKey):
  ssh-keygen -t ecdsa-sk -C "user@company.com"

PROHIBITED:
  - DSA (deprecated, removed from OpenSSH 9.0+)
  - RSA < 2048 bit
  - RSA < 4096 bit (for new keys)
  - ECDSA with NIST curves < 384 bit
```

### SSH Certificate-Based Authentication

```
Benefits over raw public keys:
- Automatic expiration (no stale authorized_keys)
- Central revocation via CA
- No authorized_keys file management
- Audit trail of issued certificates
- Role-based access via certificate principals

Architecture:
  SSH CA (in Vault/Teleport) → Issues short-lived certificates
  User requests cert → CA verifies identity (IdP) → Issues 24h cert
  Server trusts CA → Accepts any valid cert from CA
  No authorized_keys needed on servers

Example (HashiCorp Vault):
  vault write ssh-client-signer/sign/my-role \
    public_key=@$HOME/.ssh/id_ed25519.pub \
    valid_principals="ubuntu,deploy" \
    ttl="24h"

sshd_config on servers:
  TrustedUserCAKeys /etc/ssh/trusted-user-ca-keys.pub
  AuthorizedPrincipalsFile /etc/ssh/auth-principals/%u
```

### sshd_config Hardening

```
# /etc/ssh/sshd_config hardened configuration

# Authentication
PermitRootLogin no
PasswordAuthentication no
ChallengeResponseAuthentication no
PubkeyAuthentication yes
AuthenticationMethods publickey
MaxAuthTries 3
LoginGraceTime 30

# Key algorithms
PubkeyAcceptedAlgorithms ssh-ed25519,sk-ssh-ed25519@openssh.com,ecdsa-sha2-nistp384,sk-ecdsa-sha2-nistp256@openssh.com,rsa-sha2-512,rsa-sha2-256

# Ciphers and MACs
Ciphers chacha20-poly1305@openssh.com,aes256-gcm@openssh.com,aes128-gcm@openssh.com
MACs hmac-sha2-512-etm@openssh.com,hmac-sha2-256-etm@openssh.com
KexAlgorithms sntrup761x25519-sha512@openssh.com,curve25519-sha256,curve25519-sha256@libssh.org

# Session
ClientAliveInterval 300
ClientAliveCountMax 2
MaxSessions 2
X11Forwarding no
AllowTcpForwarding no
AllowAgentForwarding no

# Logging
LogLevel VERBOSE
```

---

**Last Updated:** March 2026
**Covers:** MFA, FIDO2, YubiKey, SSO, SCIM, PAM, RBAC, Zero Trust, Service Accounts, SSH
