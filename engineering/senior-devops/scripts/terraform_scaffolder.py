#!/usr/bin/env python3
"""Scaffold a Terraform module with per-environment root modules and remote state.

Creates modules/<name>/ (main.tf, variables.tf, outputs.tf, versions.tf) holding a
hardened storage bucket as a starting resource, and environments/<env>/ root modules
with a remote-state backend (S3 + DynamoDB lock, GCS or azurerm), provider config
and terraform.tfvars. Existing files are never overwritten unless --force is given.

Usage:
    python terraform_scaffolder.py <target-path> --provider aws --name app
    python terraform_scaffolder.py <target-path> --provider gcp --envs dev,prod --json
    python terraform_scaffolder.py <target-path> --provider azure --dry-run
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List

PROVIDERS = {
    "aws": {"source": "hashicorp/aws", "version": "~> 6.0", "local": "aws", "backend": "s3"},
    "gcp": {"source": "hashicorp/google", "version": "~> 7.0", "local": "google", "backend": "gcs"},
    "azure": {"source": "hashicorp/azurerm", "version": "~> 4.0", "local": "azurerm", "backend": "azurerm"},
}
AZ_ENV_ANCHOR = '    error_message = "environment must be one of: ENVS_TEXT."\n  }\n'
AZ_ENV_VALIDATION = ('\n  validation {\n    condition     = length(replace(var.environment, "-", "")) <= 12\n'
                     '    error_message = "environment may have at most 12 non-hyphen characters (Azure storage account names are 24)."\n  }\n')
NAME_RE = r"[a-z][a-z0-9]*(?:-[a-z0-9]+)*"  # no leading, trailing or doubled hyphens (Azure container rules)
KEEP_IF_PRESENT = ("README.md", ".gitignore")  # never overwritten, even with --force
UNIQUE = {"aws": "`<name>-<environment>`", "gcp": "`<project_id>-<name>-<environment>`",
          "azure": "`st<name without hyphens, trimmed><environment>`, at most 24 characters"}
REGION = {"aws": ("region", "eu-central-1"), "gcp": ("region", "europe-west3"), "azure": ("location", "westeurope")}

VARIABLES_COMMON = '''variable "name" {
  description = "Base name for every resource in this module (lowercase letters, digits, hyphens)."
  type        = string

  validation {
    condition     = length(var.name) >= 3 && length(var.name) <= 31 && can(regex("^[a-z][a-z0-9]*(-[a-z0-9]+)*$", var.name))
    error_message = "name must be 3-31 characters of lowercase letters, digits and single inner hyphens, starting with a letter."
  }
}

variable "environment" {
  description = "Deployment environment. Drives naming and labels."
  type        = string

  validation {
    condition     = contains([ENVS], var.environment)
    error_message = "environment must be one of: ENVS_TEXT."
  }
}

variable "tags" {
  description = "Extra tags/labels merged onto every resource."
  type        = map(string)
  default     = {}
}

variable "force_destroy" {
  description = "Allow destroying the bucket while it still holds objects. Keep false outside throwaway environments."
  type        = bool
  default     = false
}
'''

MAIN = {
    "aws": '''locals {
  bucket_name = "${var.name}-${var.environment}"
  tags        = merge({ environment = var.environment, managed-by = "terraform", module = "NAME" }, var.tags)
}

resource "aws_s3_bucket" "this" {
  bucket        = local.bucket_name
  force_destroy = var.force_destroy
  tags          = local.tags
}

resource "aws_s3_bucket_versioning" "this" {
  bucket = aws_s3_bucket.this.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "this" {
  bucket = aws_s3_bucket.this.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "aws:kms"
    }
    bucket_key_enabled = true
  }
}

resource "aws_s3_bucket_public_access_block" "this" {
  bucket                  = aws_s3_bucket.this.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
''',
    "gcp": '''locals {
  labels = merge({ environment = var.environment, managed-by = "terraform", module = "NAME" }, var.tags)
}

resource "google_storage_bucket" "this" {
  name                        = "${var.project_id}-${var.name}-${var.environment}"
  project                     = var.project_id
  location                    = var.region
  force_destroy               = var.force_destroy
  uniform_bucket_level_access = true
  public_access_prevention    = "enforced"
  labels                      = local.labels

  versioning {
    enabled = true
  }
}
''',
    "azure": '''# Storage account names are global and 3-24 lowercase alphanumerics: trim the name part, always keep the environment.
locals {
  tags                 = merge({ environment = var.environment, managed-by = "terraform", module = "NAME" }, var.tags)
  env_short            = replace(var.environment, "-", "")
  storage_account_name = "st${substr(replace(var.name, "-", ""), 0, 22 - length(local.env_short))}${local.env_short}"
}

resource "azurerm_resource_group" "this" {
  name     = "rg-${var.name}-${var.environment}"
  location = var.location
  tags     = local.tags
}

resource "azurerm_storage_account" "this" {
  name                            = local.storage_account_name
  resource_group_name             = azurerm_resource_group.this.name
  location                        = azurerm_resource_group.this.location
  account_tier                    = "Standard"
  account_replication_type        = var.environment == "prod" ? "GRS" : "LRS"
  min_tls_version                 = "TLS1_2"
  allow_nested_items_to_be_public = false
  tags                            = local.tags

  blob_properties {
    versioning_enabled = true
  }
}

resource "azurerm_storage_container" "this" {
  name                  = var.name
  storage_account_id    = azurerm_storage_account.this.id
  container_access_type = "private"
}
''',
}

OUTPUTS = {
    "aws": [("bucket_id", "aws_s3_bucket.this.id", "Name of the bucket."),
            ("bucket_arn", "aws_s3_bucket.this.arn", "ARN of the bucket, for IAM policies.")],
    "gcp": [("bucket_name", "google_storage_bucket.this.name", "Name of the bucket."),
            ("bucket_url", "google_storage_bucket.this.url", "gs:// URL of the bucket.")],
    "azure": [("resource_group_name", "azurerm_resource_group.this.name", "Resource group holding the module's resources."),
              ("storage_account_id", "azurerm_storage_account.this.id", "ID of the storage account.")],
}


def versions_tf(provider: str) -> str:
    """Return a versions.tf pinning Terraform and the provider."""
    p = PROVIDERS[provider]
    return (f'terraform {{\n  required_version = ">= 1.6.0, < 2.0.0"\n\n  required_providers {{\n'
            f'    {p["local"]} = {{\n      source  = "{p["source"]}"\n      version = "{p["version"]}"\n    }}\n  }}\n}}\n')


def backend_tf(provider: str, name: str, env: str) -> str:
    """Return a backend block for remote state with locking; bucket names are placeholders to replace."""
    if provider == "aws":
        return (f'terraform {{\n  backend "s3" {{\n    bucket         = "CHANGE-ME-terraform-state"\n'
                f'    key            = "{name}/{env}/terraform.tfstate"\n    region         = "{REGION["aws"][1]}"\n'
                f'    dynamodb_table = "terraform-locks" # On Terraform >= 1.10, use_lockfile = true replaces this.\n'
                f'    encrypt        = true\n  }}\n}}\n')
    if provider == "gcp":
        return (f'terraform {{\n  # GCS locks state natively; enable object versioning on the state bucket.\n'
                f'  backend "gcs" {{\n    bucket = "CHANGE-ME-terraform-state"\n    prefix = "{name}/{env}"\n  }}\n}}\n')
    return (f'terraform {{\n  # azurerm locks state with a blob lease.\n  backend "azurerm" {{\n'
            f'    resource_group_name  = "CHANGE-ME-tfstate-rg"\n    storage_account_name = "changemetfstate"\n'
            f'    container_name       = "tfstate"\n    key                  = "{name}/{env}/terraform.tfstate"\n  }}\n}}\n')


def align(pairs: List[tuple], indent: str = "") -> str:
    """Render key = value lines with the = signs aligned, as terraform fmt does."""
    width = max(len(k) for k, _ in pairs)
    return "".join(f"{indent}{k:<{width}} = {v}\n" for k, v in pairs)


def plan_files(provider: str, name: str, envs: List[str]) -> Dict[str, str]:
    """Return {relative path: content} for the whole scaffold."""
    region_var, region_default = REGION[provider]
    env_list = ", ".join(f'"{e}"' for e in envs)
    extra = {"aws": "", "gcp": 'variable "project_id" {\n  description = "GCP project that owns the resources."\n  type        = string\n}\n\n'
             'variable "region" {\n  description = "GCS bucket location."\n  type        = string\n}\n',
             "azure": 'variable "location" {\n  description = "Azure region for the resource group."\n  type        = string\n}\n'}[provider]
    if provider == "azure":
        variables_common = VARIABLES_COMMON.replace(AZ_ENV_ANCHOR, AZ_ENV_ANCHOR + AZ_ENV_VALIDATION)
    else:
        variables_common = VARIABLES_COMMON
    variables = variables_common.replace("[ENVS]", f"[{env_list}]").replace("ENVS_TEXT", ", ".join(envs)) + ("\n" + extra if extra else "")
    outputs = "\n".join(f'output "{o}" {{\n  description = "{d}"\n  value       = {v}\n}}\n' for o, v, d in OUTPUTS[provider])
    mod = f"modules/{name}"
    files = {f"{mod}/main.tf": MAIN[provider].replace("NAME", name), f"{mod}/variables.tf": variables,
             f"{mod}/outputs.tf": outputs, f"{mod}/versions.tf": versions_tf(provider)}
    provider_block = {"aws": f'provider "aws" {{\n  region = var.region\n\n  default_tags {{\n    tags = {{ environment = var.environment }}\n  }}\n}}\n',
                      "gcp": 'provider "google" {\n  project = var.project_id\n  region  = var.region\n}\n',
                      "azure": 'provider "azurerm" {\n  subscription_id = var.subscription_id\n  features {}\n}\n'}[provider]
    root_vars = [("environment", "Environment name.")] + {
        "aws": [("region", "AWS region for this environment.")],
        "gcp": [("project_id", "GCP project ID."), ("region", "GCP region for this environment.")],
        "azure": [("location", "Azure region for this environment."),
                  ("subscription_id", "Azure subscription ID (azurerm 4.x requires it, here or in ARM_SUBSCRIPTION_ID).")]}[provider]
    module_args = [("name", f'"{name}"'), ("environment", "var.environment")]
    module_args += [(v, f"var.{v}") for v, _ in root_vars if v in ("project_id", "region", "location") and provider != "aws"]
    for env in envs:
        d = f"environments/{env}"
        files[f"{d}/backend.tf"] = backend_tf(provider, name, env)
        files[f"{d}/versions.tf"] = versions_tf(provider)
        files[f"{d}/providers.tf"] = provider_block
        files[f"{d}/variables.tf"] = "\n".join(f'variable "{v}" {{\n  description = "{desc}"\n  type        = string\n}}\n'
                                               for v, desc in root_vars)
        args = module_args + [("force_destroy", "true" if env == "dev" else "false")]
        files[f"{d}/main.tf"] = (f'module "{name.replace("-", "_")}" {{\n  source = "../../{mod}"\n\n'
                                 + align(args, "  ") + "}\n")
        tfvars = [("environment", f'"{env}"'), (region_var, f'"{region_default}"')]
        tfvars += {"gcp": [("project_id", '"CHANGE-ME-project-id"')],
                   "azure": [("subscription_id", '"CHANGE-ME-subscription-id"')]}.get(provider, [])
        files[f"{d}/terraform.tfvars"] = align(tfvars)
    files["README.md"] = (
        f"# {name} infrastructure ({provider})\n\nLayout: `modules/{name}/` holds the reusable module; each directory under "
        f"`environments/` is a root module with its own state.\n\n## First run\n\n1. Create the state storage once "
        f"({PROVIDERS[provider]['backend']} backend) and replace every `CHANGE-ME` value in `environments/*/backend.tf` and "
        f"`terraform.tfvars`{' (including `subscription_id`, which azurerm 4.x requires)' if provider == 'azure' else ''}."
        f"\n2. In an environment directory: `terraform init`, `terraform fmt -check`, `terraform validate`, "
        f"`terraform plan -out=plan.tfplan`.\n3. Apply only a reviewed plan: `terraform apply plan.tfplan`.\n\n## Rules\n\n"
        f"- One state per environment. Never commit `.terraform/`, `*.tfstate` or plan files.\n- Promote changes dev, then "
        f"staging, then prod, running the same module version.\n- Provider versions are pinned in `versions.tf`; commit "
        f"`.terraform.lock.hcl` after `terraform init`.\n- Environments: {', '.join(envs)}.\n"
        f"- `dev` sets `force_destroy = true` on the data bucket, so `terraform destroy` there deletes its objects too. "
        f"Other environments keep `false`.\n- Bucket and storage account names are globally unique ({UNIQUE[provider]}). "
        f"If the name is taken, add a short suffix to `name` (for example `{name[:26].rstrip("-")}-a1b2`, within the 31-character limit) or a `name_suffix` variable.\n")
    files[".gitignore"] = ".terraform/\n*.tfstate\n*.tfstate.*\n*.tfplan\ncrash.log\n.terraform.tfstate.lock.info\n"
    return files


def tree(paths: List[str], root: str) -> str:
    """Render relative paths as an indented tree."""
    lines, seen = [f"{root}/"], set()
    for p in sorted(paths):
        parts = p.split("/")
        for i in range(len(parts)):
            key = "/".join(parts[: i + 1])
            if key not in seen:
                seen.add(key)
                lines.append("  " * (i + 1) + parts[i] + ("" if i == len(parts) - 1 else "/"))
    return "\n".join(lines)


def main() -> None:
    """Parse arguments, build the file plan, check for conflicts and write the scaffold."""
    ap = argparse.ArgumentParser(description="Scaffold a Terraform module with environments and remote state.")
    ap.add_argument("target", help="directory to create the scaffold in (created if missing)")
    ap.add_argument("--provider", choices=sorted(PROVIDERS), default="aws", help="cloud provider (default: aws)")
    ap.add_argument("--name", default="app", help="module and resource base name (default: app)")
    ap.add_argument("--envs", default="dev,staging,prod", help="comma-separated environments (default: dev,staging,prod)")
    ap.add_argument("--force", action="store_true", help="overwrite files that already exist")
    ap.add_argument("--dry-run", action="store_true", help="show what would be written without writing")
    ap.add_argument("--json", action="store_true", help="print a JSON report instead of text")
    ap.add_argument("--verbose", "-v", action="store_true", help="also print the content of versions.tf and one backend.tf")
    args = ap.parse_args()
    try:
        if not (3 <= len(args.name) <= 31 and re.fullmatch(NAME_RE, args.name)):
            raise ValueError("--name must be 3-31 characters of lowercase letters, digits and single inner hyphens, "
                             "starting with a letter (e.g. orders-api)")
        envs = [e.strip() for e in args.envs.split(",") if e.strip()]
        if not envs or any(not re.fullmatch(NAME_RE, e) for e in envs) or len(set(envs)) != len(envs):
            raise ValueError("--envs must be a comma-separated list of unique lowercase names, e.g. dev,staging,prod")
        short = [e.replace("-", "") for e in envs]
        if args.provider == "azure" and (max(map(len, short)) > 12 or len(set(short)) != len(short)):
            raise ValueError("for azure, each environment needs at most 12 non-hyphen characters and must stay unique "
                             "without hyphens (storage account names keep the environment suffix)")
        root = Path(args.target)
        if root.exists() and not root.is_dir():
            raise ValueError(f"target exists and is not a directory: {root}")
        files = plan_files(args.provider, args.name, envs)
        kept = [p for p in KEEP_IF_PRESENT if (root / p).exists()]
        files = {p: c for p, c in files.items() if p not in kept}
        existing = [p for p in files if (root / p).exists()]
        if existing and not args.force:
            raise ValueError(f"{len(existing)} file(s) already exist (first: {existing[0]}); rerun with --force to overwrite")
        if not args.dry_run:
            for rel, content in files.items():
                (root / rel).parent.mkdir(parents=True, exist_ok=True)
                (root / rel).write_text(content, encoding="utf-8")
    except (ValueError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)
    report = {"target": str(root), "provider": args.provider, "backend": PROVIDERS[args.provider]["backend"],
              "name": args.name, "environments": envs, "dry_run": args.dry_run, "files": sorted(files),
              "overwritten": sorted(existing), "kept_existing": kept,
              "next_steps": ["Replace CHANGE-ME values in backend.tf and terraform.tfvars",
                             "cd environments/<env> && terraform init && terraform plan"]}
    if args.json:
        print(json.dumps(report, indent=2))
        return
    verb = "Would create" if args.dry_run else "Created"
    print(f"{verb} {len(files)} files ({args.provider}, {report['backend']} backend, envs: {', '.join(envs)})")
    print(tree(list(files), root.name or str(root)))
    if existing:
        print(f"Overwrote {len(existing)} existing file(s).")
    if kept:
        print(f"Kept existing {', '.join(kept)} (never overwritten).")
    if args.verbose:
        print("\n# versions.tf\n" + files[f"modules/{args.name}/versions.tf"] + f"\n# environments/{envs[0]}/backend.tf\n"
              + files[f"environments/{envs[0]}/backend.tf"])
    print("Next: replace CHANGE-ME values, then terraform init and plan in each environment directory.")


if __name__ == "__main__":
    main()
