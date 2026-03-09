# Cloud Security Baseline Reference

Comprehensive security baselines for AWS, Azure, and GCP aligned with CIS Benchmarks and compliance framework requirements.

---

## AWS Security Baseline

### CIS AWS Foundations Benchmark v3.0 Summary

The CIS AWS Foundations Benchmark provides prescriptive guidance for configuring security options in AWS. The following summarizes the most impactful controls.

#### 1. Identity and Access Management

**1.1 Root Account Security**

```
Required Configuration:
- MFA enabled on root account (hardware MFA strongly preferred)
- No access keys on root account
- Root account used only for account-level operations
- Security contact configured on root account
- AWS Organizations SCP restricts root usage
```

Root account checklist:
- [ ] Hardware MFA (YubiKey or AWS-compatible TOTP device)
- [ ] Zero access keys (delete any existing keys)
- [ ] Contact information current (email + phone)
- [ ] Root activity triggers CloudWatch alarm
- [ ] Root API usage tracked via CloudTrail

**1.2 IAM Users and Policies**

```
Required Configuration:
- No wildcard permissions (Action:* Resource:*)
- MFA required for all IAM users
- Password policy: 14+ chars, complexity, 90-day expiry
- Unused credentials disabled (>90 days inactive)
- Access keys rotated every 90 days
- IAM Access Analyzer enabled
- No inline policies (use managed policies)
```

Example IAM password policy (CLI):
```bash
aws iam update-account-password-policy \
  --minimum-password-length 14 \
  --require-symbols \
  --require-numbers \
  --require-uppercase-characters \
  --require-lowercase-characters \
  --allow-users-to-change-password \
  --max-password-age 90 \
  --password-reuse-prevention 24
```

**1.3 IAM Roles and Trust Policies**

```
Best Practices:
- Use roles (not users) for applications and services
- External ID required for cross-account roles
- Condition keys restrict by source IP, VPC, or MFA
- Role session duration limited (1h for sensitive roles)
- Regular review of trust policies
```

Example trust policy with external ID:
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {"AWS": "arn:aws:iam::ACCOUNT-ID:root"},
    "Action": "sts:AssumeRole",
    "Condition": {
      "StringEquals": {
        "sts:ExternalId": "unique-external-id"
      }
    }
  }]
}
```

#### 2. Storage Security

**2.1 S3 Bucket Security**

```
Required Configuration:
- Account-level Block Public Access: ALL four settings enabled
- Bucket-level Block Public Access: ALL four settings enabled
- Default encryption: SSE-S3 minimum, SSE-KMS preferred
- Versioning enabled for data buckets
- Access logging enabled
- Lifecycle policies for cost and compliance
- MFA Delete for critical buckets
- S3 Object Lock for compliance (WORM)
```

Enable account-level block public access:
```bash
aws s3control put-public-access-block \
  --account-id $ACCOUNT_ID \
  --public-access-block-configuration \
    "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"
```

Enable default encryption:
```bash
aws s3api put-bucket-encryption \
  --bucket my-bucket \
  --server-side-encryption-configuration '{
    "Rules": [{
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "aws:kms",
        "KMSMasterKeyID": "arn:aws:kms:region:account:key/key-id"
      },
      "BucketKeyEnabled": true
    }]
  }'
```

#### 3. Networking

**3.1 VPC Security**

```
Required Configuration:
- VPC Flow Logs enabled (ALL traffic, sent to CloudWatch or S3)
- Default security group: deny all inbound, deny all outbound
- No security groups allow 0.0.0.0/0 on SSH (22) or RDP (3389)
- Private subnets for databases, application tiers
- VPC endpoints for AWS services (avoid public internet)
- NACLs as defense-in-depth (not primary control)
```

Enable VPC Flow Logs:
```bash
aws ec2 create-flow-logs \
  --resource-type VPC \
  --resource-ids vpc-12345678 \
  --traffic-type ALL \
  --log-destination-type cloud-watch-logs \
  --log-group-name vpc-flow-logs \
  --deliver-logs-permission-arn arn:aws:iam::ACCOUNT:role/flow-logs-role
```

**3.2 Security Group Best Practices**

```
Rules:
- Default deny (no rules = deny)
- Source restrictions: specific IPs or security groups, never 0.0.0.0/0 for admin ports
- Protocol-specific rules (not "all traffic")
- Description on every rule (business justification)
- Regular review (quarterly minimum)
```

#### 4. Logging and Monitoring

**4.1 CloudTrail**

```
Required Configuration:
- Multi-region trail enabled
- Log file validation enabled
- S3 bucket access logging enabled for CloudTrail bucket
- CloudTrail integrated with CloudWatch Logs
- KMS encryption for CloudTrail logs
- S3 bucket policy prevents public access
```

Create multi-region trail:
```bash
aws cloudtrail create-trail \
  --name organization-trail \
  --s3-bucket-name cloudtrail-logs-bucket \
  --is-multi-region-trail \
  --enable-log-file-validation \
  --kms-key-id arn:aws:kms:region:account:key/key-id \
  --include-global-service-events
```

**4.2 CloudWatch Alarms (CIS Required)**

Create alarms for these events:
- Unauthorized API calls
- Console sign-in without MFA
- Root account usage
- IAM policy changes
- CloudTrail configuration changes
- S3 bucket policy changes
- Security group changes
- NACL changes
- Network gateway changes
- Route table changes
- VPC changes
- AWS Organizations changes
- Failed console sign-ins (>3 in 5 min)

**4.3 GuardDuty**

```
Required Configuration:
- Enabled in all active regions
- S3 protection enabled
- EKS protection enabled (if using EKS)
- Malware protection enabled
- Findings exported to Security Hub
- High/Critical findings trigger SNS notification
```

**4.4 AWS Config**

```
Required Configuration:
- Enabled in all active regions
- Recording all resource types
- Conformance packs deployed (CIS Benchmark, SOC 2)
- Non-compliant resources trigger remediation
```

#### 5. Encryption and Key Management

**5.1 KMS**

```
Required Configuration:
- Customer-managed keys (CMK) for sensitive data
- Annual key rotation enabled
- Key policies follow least privilege
- Key aliases for identification
- Cross-account key sharing uses grants (not key policies)
- Key deletion requires 30-day waiting period
```

Enable key rotation:
```bash
aws kms enable-key-rotation --key-id $KEY_ID
```

**5.2 RDS Encryption**

```
Required Configuration:
- Encryption at rest enabled (KMS)
- SSL/TLS connections enforced (parameter: rds.force_ssl = 1)
- Automated backups with 7+ day retention
- Multi-AZ for production
- Not publicly accessible
- Enhanced monitoring enabled
- Deletion protection enabled
- IAM authentication enabled (where supported)
```

---

## Azure Security Baseline

### CIS Azure Foundations Benchmark v2.1 Summary

#### 1. Identity and Access Management

**1.1 Azure AD / Entra ID**

```
Required Configuration:
- Security Defaults enabled (if no Conditional Access)
- Maximum 5 Global Administrator accounts
- All Global Admins have MFA (phishing-resistant preferred)
- Conditional Access policies configured:
  - Require MFA for all users
  - Block legacy authentication
  - Require compliant device for sensitive apps
  - Require approved client apps
- Privileged Identity Management (PIM) enabled
  - JIT activation for admin roles
  - Approval required for Global Admin activation
  - Maximum activation duration: 4 hours
- Guest user access restricted
- Self-service password reset configured with MFA
```

**1.2 Conditional Access (Key Policies)**

| Policy | Target | Requirement |
|--------|--------|-------------|
| Require MFA | All users | MFA for all cloud apps |
| Block legacy auth | All users | Block protocols: IMAP, POP3, SMTP, ActiveSync |
| Require compliant device | All users | MDM enrollment required |
| Require phishing-resistant MFA | Admins | FIDO2 security key required |
| Block high-risk sign-ins | All users | Block when sign-in risk is High |
| Require password change | All users | When user risk is High |
| Restrict admin portal | Global Admins | Require phishing-resistant MFA + compliant device |

#### 2. Security Center and Defender

```
Required Configuration:
- Microsoft Defender for Cloud enabled (all plans):
  - Defender for Servers (Plan 2)
  - Defender for App Service
  - Defender for SQL
  - Defender for Storage
  - Defender for Key Vault
  - Defender for Containers
  - Defender for DNS
- Secure Score monitored (target: 80%+)
- Auto-provisioning enabled for agents
- Security contacts configured (email + phone)
- Alert severity notifications: High and Critical
```

#### 3. Storage Accounts

```
Required Configuration:
- Secure transfer required (HTTPS only)
- Public access disabled
- Customer-managed keys for sensitive data
- Soft delete enabled (14+ days)
- Infrastructure encryption enabled
- Shared Access Signature (SAS) expiry: maximum 1 hour
- Private endpoints for PaaS access
- Storage Analytics logging enabled
- Firewall: deny by default, allow by VNet/IP
```

#### 4. Networking

```
Required Configuration:
- NSG rules: deny all inbound by default, allow by exception
- NSG flow logs enabled (Version 2, retention 90+ days)
- Azure Firewall or NVA deployed
- DDoS Protection Standard for public IPs
- Private endpoints for PaaS services
- Network Watcher enabled in all regions
- No NSG allows any/any inbound
- No NSG allows 0.0.0.0/0 on SSH (22) or RDP (3389)
```

#### 5. Key Vault

```
Required Configuration:
- RBAC authorization (not legacy access policies)
- Soft delete enabled (90 days)
- Purge protection enabled
- Diagnostic logging enabled
- Firewall: allow from specific VNets/IPs only
- Key rotation policy configured
- Private endpoint for access
- Certificate auto-renewal configured
```

#### 6. Monitoring

```
Required Configuration:
- Activity Log alerts for:
  - Create/update/delete NSG
  - Create/update/delete NSG rule
  - Create/update/delete security solution
  - Create/update/delete SQL Server firewall rule
  - Create/update policy assignment
  - Create/update/delete public IP
- Diagnostic settings on all resources
- Log Analytics workspace with 365+ day retention
- Microsoft Sentinel deployed (SIEM)
- Azure Policy assignments enforcing compliance
```

---

## GCP Security Baseline

### CIS GCP Foundations Benchmark v3.0 Summary

#### 1. Identity and Access Management

```
Required Configuration:
- Organization-level policies use groups (not individual users)
- No service accounts with Owner or Editor roles
- User-managed service account keys rotate every 90 days
- Workload Identity for GKE (no service account keys)
- Domain-restricted sharing via Organization Policy
- Essential Contacts configured for Security notifications
- Service Account Key creation disabled via Organization Policy (use Workload Identity)
```

Organization Policy constraints:
```
constraints/iam.disableServiceAccountKeyCreation: true
constraints/iam.allowedPolicyMemberDomains: ["C0xxxxxxx"]
```

#### 2. Logging and Monitoring

```
Required Configuration:
- Cloud Audit Logs enabled for all services:
  - Admin Activity (always on, no charge)
  - Data Access logs enabled for sensitive services
  - System Event logs (always on)
- Log sinks to Cloud Storage or BigQuery for retention
- Log-based metrics for:
  - Project ownership changes
  - Audit configuration changes
  - Custom role changes
  - VPC network changes
  - Firewall rule changes
  - Route changes
  - Network changes
  - Storage IAM changes
  - SQL instance configuration changes
- Alert policies for all log-based metrics
```

#### 3. Networking

```
Required Configuration:
- Default network deleted
- VPC Flow Logs enabled for all subnets (sample rate 100%)
- Firewall rules: no 0.0.0.0/0 on SSH (22) or RDP (3389)
- Private Google Access enabled for private subnets
- VPC Service Controls for sensitive projects
- Cloud Armor WAF for public services
- Cloud DNS DNSSEC enabled
- SSL policies enforce TLS 1.2+ with MODERN profile
```

Firewall audit query (gcloud):
```bash
gcloud compute firewall-rules list \
  --filter="sourceRanges:0.0.0.0/0 AND (allowed.ports:22 OR allowed.ports:3389)" \
  --format="table(name,network,sourceRanges,allowed)"
```

#### 4. Cloud Storage

```
Required Configuration:
- Uniform bucket-level access enabled
- Public access prevention enforced (organization policy)
- Customer-managed encryption keys (CMEK) for sensitive data
- Object versioning enabled
- Access logging enabled
- Retention policy for compliance data
- No allUsers or allAuthenticatedUsers in bucket IAM
```

Organization Policy:
```
constraints/storage.publicAccessPrevention: enforced
constraints/storage.uniformBucketLevelAccess: true
```

#### 5. Compute and GKE

```
Required Configuration:
- Compute instances:
  - No default service account
  - No external IP (use NAT or IAP)
  - Shielded VM enabled
  - OS Login enabled
  - Serial port disabled
- GKE:
  - Private cluster (no public endpoint, or authorized networks)
  - Workload Identity enabled
  - Shielded Nodes enabled
  - Node auto-upgrade enabled
  - Container-Optimized OS for nodes
  - Network Policies enabled
  - Binary Authorization enabled
  - Release channel: Regular or Stable
```

#### 6. Security Command Center

```
Required Configuration:
- SCC Premium enabled
- Web Security Scanner enabled
- Event Threat Detection enabled
- Container Threat Detection enabled
- Security Health Analytics enabled
- Findings exported to SIEM
- High/Critical findings trigger notifications
```

---

## Cross-Cloud Security Comparison

| Control | AWS | Azure | GCP |
|---------|-----|-------|-----|
| **Identity** | IAM Users/Roles | Entra ID/PIM | Cloud IAM/Groups |
| **MFA** | IAM MFA, SSO | Conditional Access | Google 2-Step |
| **Encryption at rest** | KMS (CMK) | Key Vault (CMK) | Cloud KMS (CMEK) |
| **Encryption in transit** | ACM + ALB | App Gateway + Front Door | Cloud Load Balancer |
| **Network firewall** | Security Groups, NACLs | NSG, Azure Firewall | VPC Firewall Rules |
| **WAF** | AWS WAF | Azure WAF (App GW/Front Door) | Cloud Armor |
| **DDoS** | Shield Standard/Advanced | DDoS Protection Standard | Cloud Armor |
| **Logging** | CloudTrail, CloudWatch | Activity Log, Monitor | Cloud Audit Logs |
| **SIEM** | Security Hub, Detective | Microsoft Sentinel | Chronicle, SCC |
| **Vulnerability scan** | Inspector | Defender for Cloud | SCC, Web Security Scanner |
| **Container security** | ECR scanning, GuardDuty | Defender for Containers | Container Threat Detection |
| **Secrets** | Secrets Manager | Key Vault | Secret Manager |
| **Config compliance** | AWS Config | Azure Policy | Organization Policy |
| **CIS Benchmark** | CIS AWS v3.0 | CIS Azure v2.1 | CIS GCP v3.0 |

---

## Minimum Viable Security Baseline (Any Cloud)

For organizations just starting, implement these controls first:

### Tier 1 — Immediate (Week 1)
1. Enable MFA for all accounts (hardware keys for admins)
2. Enable audit logging in all regions
3. Block public access to storage (S3/Storage/GCS)
4. Remove wildcard permissions from IAM
5. Enable encryption at rest for databases
6. No open SSH/RDP to the internet

### Tier 2 — Short-term (Month 1)
1. Deploy cloud security posture management (CSPM)
2. Enable VPC/NSG flow logs
3. Configure alerting for security events
4. Enable vulnerability scanning
5. Implement network segmentation
6. Deploy WAF for public applications

### Tier 3 — Medium-term (Quarter 1)
1. Implement least-privilege IAM (review all policies)
2. Deploy SIEM with correlation rules
3. Enable container image scanning
4. Implement secrets management
5. Configure key rotation
6. Establish quarterly access reviews

---

**Last Updated:** March 2026
**CIS Benchmark Versions:** AWS v3.0, Azure v2.1, GCP v3.0
