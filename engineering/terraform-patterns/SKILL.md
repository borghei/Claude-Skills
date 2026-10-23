---
name: terraform-patterns
description: >
  This skill should be used when the user asks to "analyze Terraform modules",
  "scan IaC for security issues", "review Terraform configurations",
  "check infrastructure code for misconfigurations", or "audit cloud resources".
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: engineering
  domain: infrastructure-as-code
  updated: 2026-04-02
  tags: [terraform, iac, security, cloud, infrastructure]
---
# Terraform Patterns

> **Category:** Engineering
> **Domain:** Infrastructure as Code

## Overview

The **Terraform Patterns** skill provides automated analysis of Terraform configurations for module complexity, security misconfigurations, and infrastructure best practices. It catches open ports, public buckets, missing encryption, and overly permissive IAM policies before they reach production.

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

### tf_module_analyzer.py

Analyzes Terraform modules for complexity, structure, dependencies, and documentation quality.

| Feature | Description |
|---------|-------------|
| Complexity scoring | Scores modules by resource count, variable count, nesting |
| Dependency mapping | Maps module dependencies and data source usage |
| Variable analysis | Checks for missing types, defaults, descriptions |
| Output completeness | Validates output documentation and coverage |
| Naming conventions | Checks resource and variable naming patterns |

### tf_security_scanner.py

Scans Terraform configurations for security misconfigurations and compliance violations. The rules are written for AWS resource types and argument names, so Azure and Google Cloud configurations get little or no coverage.

| Feature | Description |
|---------|-------------|
| Open ports | Detects 0.0.0.0/0 CIDR in security groups |
| Public access | Flags public S3 buckets, databases, instances |
| Encryption gaps | Checks for missing encryption at rest and in transit |
| IAM overreach | Identifies wildcard actions and overly broad policies |
| Logging gaps | Verifies CloudTrail, flow logs, access logging |

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
