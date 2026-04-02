# Google Workspace Administration Guide

## Security Configuration

### 2-Step Verification (2FA)
**Priority: Critical**

Admin Console > Security > Authentication > 2-Step Verification

Recommended settings:
- Enforcement: ON for all organizational units
- Methods: Allow security keys, Google prompts, authenticator apps
- Grace period: 1 week for new users
- Disable SMS verification (vulnerable to SIM swapping)

### Password Policy
**Priority: Critical**

Admin Console > Security > Password management

Recommended settings:
- Minimum length: 12 characters
- Require password change: Every 365 days (NIST recommends no forced rotation)
- Prevent password reuse: Last 5 passwords
- Allow users to recover: No (for super admins)

### Session Management
Admin Console > Security > Google session control

- Web session duration: 12 hours (balance security and usability)
- Mobile session: 30 days with device trust
- Require re-authentication for sensitive actions

## Email Security

### SPF Configuration
Add TXT record to domain DNS:
```
v=spf1 include:_spf.google.com ~all
```

Use `~all` (softfail) during initial setup, migrate to `-all` (hardfail) after confirming all legitimate senders are included.

### DKIM Configuration
1. Admin Console > Apps > Google Workspace > Gmail > Authenticate email
2. Click "Generate New Record"
3. Select DKIM key bit length (2048 recommended)
4. Add the generated CNAME record to your DNS
5. Return to Admin Console and click "Start Authentication"

### DMARC Configuration
Add TXT record at `_dmarc.yourdomain.com`:

**Phase 1 - Monitoring:**
```
v=DMARC1; p=none; rua=mailto:dmarc@yourdomain.com
```

**Phase 2 - Quarantine:**
```
v=DMARC1; p=quarantine; pct=25; rua=mailto:dmarc@yourdomain.com
```

**Phase 3 - Reject:**
```
v=DMARC1; p=reject; rua=mailto:dmarc@yourdomain.com
```

## Drive Security

### Sharing Settings
Admin Console > Apps > Google Workspace > Drive and Docs > Sharing settings

Recommended:
- External sharing: Restricted to allowlisted domains
- Link sharing default: Restricted (only people with access)
- Disable download, print, copy for external viewers
- File ownership transfer: Admin only

### Data Loss Prevention (DLP)
- Create DLP rules for PII, financial data, confidential docs
- Set to warn or block external sharing of sensitive content
- Review DLP reports monthly

## API Access

### OAuth App Whitelisting
Admin Console > Security > API Controls > App Access Control

1. Set default policy: "Block third-party API access"
2. Whitelist approved applications
3. Review and remove unused app grants quarterly

### Service Account Scopes
Grant minimum required scopes:

| Use Case | Minimum Scopes |
|----------|---------------|
| User provisioning | `admin.directory.user` |
| Group management | `admin.directory.group` |
| Audit logs | `admin.reports.audit.readonly` |
| Drive listing | `drive.readonly` |
| Email sending | `gmail.send` |

## Admin Roles

### Role Hierarchy
1. **Super Admin** - Full access (limit to 2-3 accounts)
2. **Groups Admin** - Manage groups only
3. **User Admin** - Manage users (no billing, no settings)
4. **Help Desk Admin** - Reset passwords, view user info
5. **Services Admin** - Manage specific Google services

### Best Practices
- Assign least-privilege roles
- Review admin assignments quarterly
- Super admin accounts should use physical security keys
- No super admin should be a regular daily-use account
- Enable admin audit logging

## Mobile Device Management

### Basic Management
- Require screen lock
- Wipe on failed password attempts

### Advanced Management
- Require device encryption
- Enable remote wipe capability
- Block rooted/jailbroken devices
- Require approved device list for access
- Set app management policies

## Monitoring and Auditing

### Key Reports
- Admin Console > Reports > Audit and Investigation
- Login audit: Failed logins, suspicious locations
- Drive audit: External sharing activity
- Admin audit: Settings changes
- OAuth audit: Third-party app grants

### Alert Center
Admin Console > Security > Alert Center
- Configure alerts for suspicious login activity
- Enable government-backed attack warnings
- Set up data export notifications
- Monitor phishing attempt reports
