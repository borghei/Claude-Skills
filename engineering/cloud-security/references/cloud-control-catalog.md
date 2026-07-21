# Cloud Control Catalog — AWS / Azure / GCP

The posture controls that matter, mapped across the three major providers. Each
section states the control, the service that implements it per provider, and
the threshold that counts as passing.

---

## 1. Identity and least privilege

| Control | AWS | Azure | GCP | Passing threshold |
|---------|-----|-------|-----|-------------------|
| Human identity federated, not cloud-local | IAM Identity Center + external IdP | Entra ID | Cloud Identity + external IdP | Zero long-lived IAM users with console access |
| Phishing-resistant MFA on humans | FIDO2 via Identity Center | Conditional Access, FIDO2 | Titan / passkey enforcement | 100% of human principals |
| Root / global admin sealed | Root MFA + no access keys + alert on use | Break-glass accounts excluded from CA, monitored | Org admin restricted, no keys | Root use alerts within 5 minutes |
| Workload identity, not static keys | IAM roles, IRSA, OIDC federation | Managed identities, workload identity federation | Workload Identity Federation | Zero static keys older than 90 days |
| Permission boundary on privileged principals | IAM permission boundaries | Azure Policy deny assignments | Org policy + role restrictions | Every principal at admin/write-broad tier |
| Blast-radius cap on wildcards | Access Analyzer unused-access findings | Entra Permissions Management | Policy Intelligence / recommender | Zero `*:*` on `*` outside break-glass |

### Privilege-escalation paths to hunt for explicitly

These are the grants that convert a mid-privilege identity into an admin. Each
one is a single finding, not an aggregate score:

| Path | Trigger grants |
|------|----------------|
| PassRole to compute | `iam:PassRole` + any of `ec2:RunInstances`, `lambda:CreateFunction`, `ecs:RunTask`, `cloudformation:CreateStack` |
| Policy version rewrite | `iam:CreatePolicyVersion` or `iam:SetDefaultPolicyVersion` |
| Self-attach admin | `iam:AttachRolePolicy`, `iam:AttachUserPolicy`, `iam:PutRolePolicy`, `iam:PutUserPolicy` |
| Trust rewrite | `iam:UpdateAssumeRolePolicy` |
| Function code overwrite | `lambda:UpdateFunctionCode` + `iam:PassRole` |
| Service-account impersonation (GCP) | `iam.serviceAccounts.actAs`, `.getAccessToken`, `iam.serviceAccountKeys.create` |
| Project IAM rewrite (GCP) | `resourcemanager.projects.setIamPolicy` |
| Role assignment write (Azure) | `Microsoft.Authorization/roleAssignments/write` |

**[PROVEN] Hunt escalation paths before you chase wildcard counts.** A tidy
policy with 40 scoped actions that happens to include `iam:PassRole` plus
`ec2:RunInstances` is a full account compromise; a sloppy `s3:*` on one bucket
is not. Posture tools that rank by wildcard count invert the priority order.

### Reviewing a grant: the three questions

1. **What has this principal actually called in 90 days?** Derive the target
   policy from access-analyzer or audit-log data, never from what the developer
   thinks they need.
2. **What is the worst thing this grant permits?** Not the intended use — the
   worst use.
3. **Is there a condition that bounds it?** Source VPC endpoint, source IP,
   tag match, region, MFA presence. An unconditioned write on `*` is the
   default state of every over-permissive policy in the wild.

---

## 2. Network exposure

| Control | AWS | Azure | GCP | Passing threshold |
|---------|-----|-------|-----|-------------------|
| No admin ports from the internet | Security groups, no 0.0.0.0/0 on 22/3389 | NSG rules, no Any source | VPC firewall, no 0.0.0.0/0 | Zero, with no exceptions |
| Administrative access brokered | SSM Session Manager | Azure Bastion | IAP TCP forwarding | Bastion hosts with public IPs are not a passing answer |
| Data stores private | RDS/Redshift in private subnets | Private Endpoints | Private Service Connect | Zero public database endpoints |
| Egress controlled | VPC endpoints + egress firewall | Azure Firewall + service endpoints | VPC-SC + Cloud NAT logging | Egress to arbitrary internet from data-plane subnets is a finding |
| Public object storage prevented | S3 Block Public Access at account level | Storage account public access disabled | Public Access Prevention at org level | Enforced at org/account level, not per-resource |

The ports that turn an open ingress rule from medium to critical: 22 (SSH),
3389 (RDP), 3306 / 5432 / 1433 (databases), 27017 (Mongo), 6379 (Redis),
9200 (Elasticsearch), 2375 (unauthenticated Docker API), 11211 (Memcached).
The last four are the ones found unauthenticated most often, because they were
designed for trusted networks and shipped with no auth by default.

---

## 3. Encryption

| Control | AWS | Azure | GCP | Passing threshold |
|---------|-----|-------|-----|-------------------|
| At rest, everywhere | Default encryption on S3/EBS/RDS | Storage Service Encryption | Default at-rest encryption | Provider default is the floor, not the goal |
| Customer-managed keys on sensitive data | KMS CMK | Key Vault CMK | Cloud KMS CMEK | Any store classified confidential/PCI/PHI |
| Key rotation | Automatic annual KMS rotation | Key Vault rotation policy | KMS rotation schedule | Rotation enabled and evidenced |
| TLS enforced in transit | `aws:SecureTransport` deny, TLS 1.2 min | "Secure transfer required", TLS 1.2 min | HTTPS-only, SSL required on Cloud SQL | Plaintext connections rejected, not just discouraged |
| Key access separated from data access | Separate KMS key policy | Separate Key Vault RBAC | Separate KMS IAM | The data-plane role must not also administer the key |

**[RECOMMENDED] Customer-managed keys matter less for confidentiality than for
revocability and audit.** Provider-managed encryption already defeats stolen
disks. What a CMK buys you is a separate access-control surface, a key-use
audit trail, and the ability to make data unreadable in one action. Do not
spend a quarter migrating everything to CMK — apply it to classified stores
and move on to the exposure findings, which are what actually get exploited.

---

## 4. Logging and detection coverage

| Layer | AWS | Azure | GCP | Retention floor |
|-------|-----|-------|-----|-----------------|
| Control plane | CloudTrail (org-wide, multi-region, log-file validation) | Activity Log | Cloud Audit Logs (Admin Activity) | 400 days |
| Data plane | S3 data events, CloudTrail Lake | Storage diagnostic logs | Data Access audit logs | 90 days |
| Network flow | VPC Flow Logs | NSG Flow Logs | VPC Flow Logs | 90 days |
| DNS | Route 53 Resolver query logs | Azure DNS analytics | Cloud DNS logging | 90 days |
| Managed detection | GuardDuty | Defender for Cloud | Security Command Center | Enabled all regions |
| Config state | AWS Config | Azure Policy compliance | Cloud Asset Inventory | Continuous |

Three coverage rules that decide whether an investigation is possible:

1. **The log archive lives in a separate account/subscription/project** with no
   workload administrator access. If an attacker who compromises the workload
   account can delete the logs, you have no logs.
2. **Data-plane logging is on for classified stores.** Control-plane logs show
   that a role read from a bucket; only data-plane logs show *which objects*.
   The difference decides whether a breach notification names 12 records or
   assumes all 4 million.
3. **Detection findings route to a queue with an owner and an SLA.** GuardDuty
   enabled with findings nobody reads is a compliance checkbox, not a control.

---

## 5. Resilience and data governance

| Control | Threshold |
|---------|-----------|
| Automated backups on primary data stores | Enabled, retention ≥ recovery objective |
| Backup copies outside the primary account | Required for anything tier-1; ransomware deletes in-account backups first |
| Restore tested | At least once per quarter, timed, documented |
| Deletion protection on production stores | Enabled |
| Every resource tagged `owner`, `env`, `data_classification` | Enforced at provision time via policy, not audited after |

Untagged resources are not a cosmetic problem. Without `owner` there is nobody
to page; without `data_classification` you cannot derive the encryption,
logging, and retention requirements, so every downstream control becomes a
judgement call made by whoever is on call at 3am.

---

## 6. Severity calibration

Use these bands so findings from different reviewers are comparable:

| Severity | Definition | Examples |
|----------|------------|----------|
| **Critical** | Direct path to data exposure or account takeover, exploitable now | Public bucket with confidential data; admin port open to internet; `*:*` on `*`; wildcard role trust; control-plane audit logging off |
| **High** | Significant weakening, exploitable with one additional step | Service-wide wildcard grant; unencrypted classified store; no backups on a primary store; log archive not isolated; human without MFA |
| **Medium** | Defence-in-depth gap or missing detection | Data-plane access logs off; no permission boundary on a privileged principal; provider-managed keys on classified data |
| **Low** | Governance and hygiene | Missing owner tag; missing classification tag |

A single critical finding outranks any number of mediums. Posture scores that
average severities let ten low findings mask one public database — always sort
by severity, and gate on critical count rather than on the score.
