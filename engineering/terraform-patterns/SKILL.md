---
name: terraform-patterns
description: >
  Terraform module design and review: complexity and documentation analysis plus an AWS-focused
  misconfiguration scan. Use when writing or reviewing Terraform modules or gating IaC changes.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: engineering
  domain: infrastructure-as-code
  updated: 2026-11-08
  tags: [terraform, iac, security, cloud, infrastructure]
---
# Terraform Patterns

> **Category:** Engineering
> **Domain:** Infrastructure as Code

## Overview

The **Terraform Patterns** skill provides automated analysis of Terraform configurations for module complexity, security misconfigurations, and infrastructure best practices. It catches open ports, public buckets, missing encryption, and overly permissive IAM policies before they reach production.

## When to Use

- Designing a new module (inputs, outputs, versioning, state layout).
- Reviewing a Terraform pull request for structure and security problems.
- Adding an IaC security gate to CI for AWS configurations.

## Module Design Rules

- **One responsibility per module, composed in a root module.** A module that creates a VPC, a cluster and a database is three modules. [PROVEN]
- **Typed, described inputs; minimal outputs.** Every variable has `type` and `description`; validate with `validation` blocks; output only what callers need. [PROVEN]
- **`for_each` over `count` for collections.** `count` re-indexes and destroys resources when an item is removed from the middle of a list; `for_each` keys by name. Use `count` only for on/off toggles. [PROVEN]
- **Pin versions deliberately.** Constrain `required_version` and each provider with `~>` to the major you tested, commit `.terraform.lock.hcl`, and version shared modules with git tags or a registry. Upgrade providers on purpose, reading the upgrade guide for each major. [PROVEN]
- **Remote, locked state per environment.** One state per environment and component (S3 with locking, or the platform's backend); never share state across environments. [PROVEN]
- **Move, don't recreate.** Use `moved` blocks when refactoring addresses so `plan` shows a move rather than a destroy and create. [RECOMMENDED]

## Clarify First

Before analyzing or scanning, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Target path:** the module or environment directory to analyze (`--path`; the subject).
- **Task:** module complexity/quality analysis vs security misconfiguration scan (selects `tf_module_analyzer` vs `tf_security_scanner`).
- **Minimum severity / gate:** the severity bar for findings and whether it blocks a PR (`--min-severity`; changes the report and CI pass/fail).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Quick Start

```bash
# Analyze Terraform module structure and complexity
python scripts/tf_module_analyzer.py --path ./modules/vpc

# Scan for security misconfigurations
python scripts/tf_security_scanner.py --path ./environments/production

# JSON output for CI pipelines
python scripts/tf_security_scanner.py --path . --format json

# Recursive analysis of all modules
python scripts/tf_module_analyzer.py --path . --recursive
```

## Tools Overview

| Tool | What it checks | Key flags |
|------|----------------|-----------|
| `tf_module_analyzer.py` | 0-100 complexity (resources, variables, nesting), dependencies and data sources, variables missing type/description, output docs, naming | `--path`, `--recursive`, `--format text/json` |
| `tf_security_scanner.py` | AWS rules: 0.0.0.0/0 ingress, public S3/RDS/instances, missing encryption, wildcard IAM, missing CloudTrail/flow/access logs | `--path`, `--min-severity`, `--format text/json` |

The security rules target AWS resource types; Azure and Google Cloud configurations get
little coverage, so pair them with a multi-cloud scanner (Checkov, Trivy, tfsec rules) there.
Exit codes: `0` no finding at or above `--min-severity`; `1` findings at or above it (the CI
gate); `2` bad input (path not found).

```bash
python scripts/tf_security_scanner.py --path examples   # bundled sample: open SSH, public-read ACL, wildcard IAM
python scripts/tf_module_analyzer.py --path examples
```

## Workflows

### Security Review Workflow

1. **Scan** - Run tf_security_scanner.py across all environments
2. **Triage** - Prioritize critical findings (public data, open access)
3. **Remediate** - Apply recommended fixes per finding
4. **Verify** - Re-scan to confirm fixes resolved issues
5. **Gate** - Add scanner to PR checks for continuous enforcement

### Module Quality Workflow

1. **Analyze** - Run tf_module_analyzer.py on each module
2. **Score** - Review complexity scores, identify modules over threshold
3. **Refactor** - Break down modules scoring above 60/100 complexity (the analyzer flags 61-80 as high and 81-100 as critical)
4. **Document** - Fill in missing variable and output descriptions
5. **Standardize** - Apply consistent naming and file organization

### CI Integration

```bash
# Security gate
python scripts/tf_security_scanner.py --path . --format json --min-severity high
if [ $? -ne 0 ]; then
  echo "Security scan failed - blocking merge"
  exit 1
fi

# Module quality check
python scripts/tf_module_analyzer.py --path . --recursive --format json
```

## Scope & Limitations

**In Scope:**
- Module analysis with `tf_module_analyzer.py`: a 0-100 complexity score, dependency and data source mapping, variable and output documentation checks and naming checks, with `--recursive` for many modules.
- Security misconfiguration scanning of `.tf` files with `tf_security_scanner.py`: open CIDR ranges, public access, missing encryption, wildcard IAM and logging gaps, filtered by `--min-severity` with a non-zero exit code for CI.
- Module design, file layout, state management, naming and provider pinning guidance in `references/terraform-patterns.md`.

**Out of Scope:**
- Running `terraform init`, `validate`, `plan` or `apply`, or reading state files.
- Live cloud account posture (see `engineering/cloud-security/`) and compliance audits of infrastructure (see `ra-qm-team/infrastructure-compliance-auditor/`).
- Helm chart review (see `engineering/helm-chart-builder/`).
- Writing new modules. The scripts review existing configuration.

**Important Caveats:**
- Both scripts match patterns in raw `.tf` text. Variables, locals, module inputs and dynamic blocks are not evaluated, so values set elsewhere can hide or create findings.
- The security rules are written for AWS resource types. Azure and Google Cloud configurations get little or no security coverage.
- A clean scan does not mean the infrastructure is secure. Provider resource names and arguments change between versions, so rules can fall behind.

## Reference Documentation

- [Terraform Patterns](references/terraform-patterns.md) - Module design, state management, naming conventions

## Common Patterns Quick Reference

### Module Structure
```
modules/vpc/
  main.tf           # Primary resources
  variables.tf      # Input variables with descriptions
  outputs.tf        # Module outputs
  versions.tf       # Required providers and versions
  locals.tf         # Local values and computed expressions
```

### Security Checklist
| Resource | Check | Rule |
|----------|-------|------|
| Security Groups | No 0.0.0.0/0 ingress | Restrict to known CIDRs |
| S3 Buckets | No public ACLs | Use bucket policies instead |
| RDS | No public access | Set publicly_accessible = false |
| EBS/S3/RDS | Encryption enabled | Add encryption configuration |
| IAM | No wildcard actions | Use least-privilege policies |
| CloudTrail | Enabled in all regions | is_multi_region_trail = true |
| VPC | Flow logs enabled | Create flow log resources |

### Complexity Scoring
| Score | Rating | Action |
|-------|--------|--------|
| 0-30 | Low | No action needed |
| 31-60 | Medium | Consider splitting |
| 61-80 | High | Should refactor |
| 81-100 | Critical | Must refactor |

## Anti-Patterns

### `count` for Named Collections
**Mistake:** `count = length(var.subnets)` with `var.subnets[count.index]`.
**Why it happens:** It is the first loop construct most people learn.
**Instead:** `for_each = { for s in var.subnets : s.name => s }`. Removing one subnet then removes one resource instead of shifting and recreating the rest.

### Unpinned Providers
**Mistake:** No version constraint, or `>=` with no upper bound.
**Why it happens:** It works today.
**Instead:** `~>` on the tested major plus a committed lock file; a new provider major can change defaults and break `plan` without any code change.

### Scanning Instead of Planning
**Mistake:** Treating a clean static scan as proof the change is safe.
**Why it happens:** The scanner is fast and runs without credentials.
**Instead:** Read `terraform plan` for every change: destroys, replacements and IAM changes are visible there and nowhere else.

## Files

| File | Purpose |
|------|---------|
| `scripts/tf_module_analyzer.py` | Module complexity, documentation and naming analysis |
| `scripts/tf_security_scanner.py` | AWS-focused misconfiguration scan with a CI exit code |
| `examples/main.tf` | Three-resource sample with deliberate misconfigurations |
| `references/terraform-patterns.md` | Module design, state management, naming, provider pinning |
