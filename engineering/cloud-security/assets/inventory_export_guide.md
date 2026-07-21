# Building the Inventory and IAM Exports

`posture_auditor.py` and `iam_least_privilege.py` consume normalized JSON so
the same review works across providers. This guide describes the shape and how
to populate it from each provider's CLI.

## Inventory schema

```json
{
  "provider": "aws | azure | gcp",
  "account_id": "string",
  "environment": "production",
  "exported": "YYYY-MM-DD",
  "account_settings": {
    "audit_log_enabled": true,
    "root_mfa": true,
    "threat_detection_enabled": true,
    "config_recorder_enabled": true,
    "org_guardrails_enabled": true,
    "log_archive_isolated": true
  },
  "resources": [
    {
      "id": "provider resource id or ARN",
      "name": "short name",
      "type": "storage_bucket | database | data_warehouse | queue | secret_store | key_vault | backup_vault | file_share | compute_instance | kubernetes_cluster | serverless_function | load_balancer | cdn | dns_zone",
      "region": "us-east-1",
      "public": false,
      "encryption": {
        "at_rest": true,
        "customer_managed_key": true,
        "in_transit_enforced": true
      },
      "logging": {"access_logs": true},
      "backup": {"enabled": true, "retention_days": 35},
      "network": {"ingress": [{"protocol": "tcp", "ports": "5432", "source": "10.0.0.0/8"}]},
      "tags": {"env": "prod", "owner": "team-name", "data_classification": "confidential"}
    }
  ]
}
```

Field notes:

- **`type`** drives which checks run. Anything in the data-store family
  (`storage_bucket`, `database`, `data_warehouse`, `queue`, `secret_store`,
  `key_vault`, `backup_vault`, `file_share`) gets encryption, logging, and
  backup checks. `load_balancer`, `cdn`, and `dns_zone` are treated as edge
  resources, so `public: true` on them is expected and not flagged.
- **`tags.data_classification`** escalates severity. Values `confidential`,
  `restricted`, `pii`, `phi`, and `pci` promote unencrypted-at-rest from high
  to critical and TLS-not-enforced from medium to high.
- **`network.ingress[].ports`** accepts a single port (`"22"`), a
  comma-separated list (`"22,3389"`), or `"all"` / `"0-65535"` / `"*"`.
- **`network.ingress[].source`** counts as internet-facing when it is
  `0.0.0.0/0`, `::/0`, `*`, `any`, or `internet`.

## IAM export schema

```json
{
  "provider": "aws",
  "account_id": "string",
  "principals": [
    {
      "name": "ci-deployer",
      "type": "role | user | human | service",
      "last_used_days": 2,
      "access_key_age_days": 30,
      "mfa": true,
      "permission_boundary": "boundary/name",
      "trust": {
        "principals": ["account:111122223333", "service:lambda.amazonaws.com"],
        "approved": ["account:111122223333"],
        "external_id": true
      },
      "policies": [
        {"name": "deploy", "statements": [
          {"effect": "allow",
           "actions": ["s3:GetObject"],
           "resources": ["arn:aws:s3:::bucket/*"],
           "conditions": {"aws:SourceVpce": "vpce-0a1b2c"}}
        ]}
      ]
    }
  ]
}
```

Field notes:

- **`type`** of `user` or `human` triggers the MFA check. Service principals
  are exempt because MFA is meaningless for them — workload identity federation
  is the control instead.
- **`trust.approved`** is your allowlist of accounts. Any entry in
  `trust.principals` starting with `account:` that is absent from `approved`
  raises a cross-account finding, so populate `approved` with your own
  organization's account IDs.
- **`conditions`** being non-empty downgrades unconditioned-write findings.
  Populate it — an unconditioned wildcard write and the same grant bounded by a
  VPC-endpoint condition are materially different risks.
- **`last_used_days`** drives staleness. Omit it only if the provider genuinely
  cannot report it; a missing value silently skips the check.

## Populating the exports

The exports are deliberately provider-agnostic, so the collection step is a
short transform you own. Sketch per provider:

**AWS.** `aws s3api list-buckets` plus `get-bucket-encryption`,
`get-public-access-block`, `get-bucket-logging`; `aws rds describe-db-instances`;
`aws ec2 describe-instances` and `describe-security-groups`;
`aws organizations describe-organization` and `aws cloudtrail describe-trails`
for account settings. For IAM: `aws iam get-account-authorization-details` gives
principals, policies, and statements in one call — it is the right starting
point — and `aws iam generate-credential-report` supplies `last_used_days`,
`mfa`, and `access_key_age_days`.

**Azure.** `az storage account list`, `az sql server list`, `az vm list`,
`az network nsg list` for resources; `az monitor diagnostic-settings list` for
logging; `az role assignment list --all` plus `az ad user list` for principals.

**GCP.** `gcloud asset search-all-resources` returns most of the inventory in
one call; `gcloud projects get-iam-policy` and
`gcloud asset analyze-iam-policy` for principals and effective grants.

## Export hygiene

- **Never commit a real export.** They contain account IDs, internal hostnames,
  and the exact map of what is exposed. Treat them as sensitive; keep them in
  the secure evidence store with the review, not in the repo.
- **Export inventory and IAM on the same day.** Findings correlate — a public
  bucket matters more when an over-permissive role can also write to it — and
  exports taken a week apart cannot be correlated honestly.
- **Record the export date in the file.** A posture report with no export date
  cannot be defended in an audit.
- **Export from every region.** Regional scoping is the most common way a
  scanner misses the forgotten test database that becomes the incident.
