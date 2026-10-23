# Infrastructure as Code

Read this when laying out a Terraform codebase, configuring remote state, or extending what `scripts/terraform_scaffolder.py` produced.

## Layout

The scaffolder writes one reusable module and one root module per environment:

```
infra/
  modules/<name>/        main.tf, variables.tf, outputs.tf, versions.tf
  environments/
    dev/                 main.tf, backend.tf, providers.tf, variables.tf, versions.tf, terraform.tfvars
    staging/
    prod/
  README.md
  .gitignore
```

- **Modules hold logic, environments hold values.** An environment's `main.tf` only calls modules; differences between environments live in `terraform.tfvars` and module arguments.
- **One state per environment per component.** A mistake in dev cannot touch prod state, and `plan` stays fast. Split large estates further (network, data, compute) when a plan takes minutes.
- **Directories, not workspaces, for environments.** Workspaces share one backend config and make it easy to apply to the wrong environment. Directories make the target visible in the path.
- **Providers are configured in root modules only.** A module declares `required_providers` but never a `provider` block, so callers can pass aliases.

## Versions

```hcl
terraform {
  required_version = ">= 1.6.0, < 2.0.0"
  required_providers {
    aws = { source = "hashicorp/aws", version = "~> 6.0" }
  }
}
```

- `~> 6.0` allows minor and patch updates within major 6 and blocks the next major, which is where breaking changes land.
- Commit `.terraform.lock.hcl` from the root module after `terraform init`. It pins exact provider builds and checksums; update it deliberately with `terraform init -upgrade`.
- The scaffolder pins AWS `~> 6.0`, Google `~> 7.0` and AzureRM `~> 4.0`. Check the provider changelog before raising a major.

## Remote State and Locking

| Backend | Locking | Required setup |
|---------|---------|----------------|
| `s3` | DynamoDB table with a `LockID` string hash key, or `use_lockfile = true` on Terraform 1.10 and later | Versioned, encrypted bucket with public access blocked |
| `gcs` | Native | Bucket with object versioning |
| `azurerm` | Blob lease, native | Storage account and container; restrict network access |

AzureRM 4.x requires a subscription ID. The scaffolder passes `subscription_id = var.subscription_id` in each Azure `providers.tf` with a `CHANGE-ME` value in `terraform.tfvars`; setting `ARM_SUBSCRIPTION_ID` in CI works too.

- Create the state bucket and lock table once, outside the stacks that use them (a small bootstrap stack with local state, or by hand), and protect them from deletion.
- Keys follow `<name>/<env>/terraform.tfstate` so every state file has an obvious owner.
- Backend blocks cannot use variables. Replace the scaffolder's `CHANGE-ME` placeholders, or keep them generic and pass `-backend-config=backend.hcl` per environment.
- State contains secrets in plain text (generated passwords, keys). Restrict read access to the bucket as tightly as production access itself.
- A stuck lock after an interrupted apply: confirm nothing is running, then `terraform force-unlock <LOCK_ID>`.

## Variables

- Global names: S3 and GCS bucket names and Azure storage account names are unique across all customers. The scaffolder names buckets `<name>-<environment>` (GCS prefixes the project ID). Azure storage accounts are `st` + the name without hyphens, trimmed so that the environment suffix always fits in 24 characters, which keeps dev, staging and prod distinct; Azure environments are therefore limited to 12 characters without hyphens, enforced by the script and by a module `validation` block. If a name is taken, add a short suffix to `name` or introduce a `name_suffix` variable.
- Names: the scaffolder accepts 3 to 31 lowercase letters and digits with single hyphens between them (`orders-api`), no leading, trailing or doubled hyphens, because Azure container and storage names reject those. Environment names follow the same rule.
- Give every variable a `type` and a `description`. Add `validation` where a bad value would only fail at apply time: names, environment lists, CIDR ranges, sizes.
- Default only what is safe everywhere. `force_destroy` defaults to `false`; the scaffolder sets it to `true` only in dev.
- Mark secrets `sensitive = true`, and better still read them from a secret manager data source instead of tfvars.
- Never commit secrets in `terraform.tfvars`. The scaffolder's tfvars hold only environment, region and project ID.

## Starter Resource

The scaffolded module creates one storage bucket with the hardening that reviewers ask for first, so a fresh module already shows the patterns:

| Provider | Resources | Defaults |
|----------|-----------|----------|
| AWS | `aws_s3_bucket` + versioning, SSE (KMS), public access block | Versioning on, all public access blocked |
| GCP | `google_storage_bucket` | Uniform bucket-level access, public access prevention enforced, versioning |
| Azure | resource group, storage account, private container | TLS 1.2 minimum, no public blobs, GRS in prod |

Replace or extend it with the resources the user needs, keeping the naming (`<name>-<environment>`) and tag merge pattern.

## Workflow

1. `terraform fmt -check -recursive` and `terraform validate` on every change (validate needs `terraform init -backend=false`).
2. `terraform plan -out=plan.tfplan` in CI on pull requests; post the plan summary for review.
3. Apply the saved plan after approval: `terraform apply plan.tfplan`. Applying a fresh plan can apply changes nobody reviewed.
4. Promote dev, then staging, then prod with the same module version.
5. Drift detection: a scheduled `terraform plan -detailed-exitcode` (0 clean, 1 error, 2 drift) that alerts on exit code 2.

Static checks such as `tflint`, `checkov` or `trivy config` catch insecure defaults before plan; the sibling `engineering/terraform-patterns/` skill reviews modules in depth.

## Anti-Patterns

- One state file for every environment and component.
- State on a laptop or in git.
- `provider` blocks inside reusable modules.
- Unpinned providers, or pins without a committed lock file.
- Applying from a workstation with admin credentials instead of from CI with a scoped role.
- Copy-pasting a whole environment directory instead of calling a module.
