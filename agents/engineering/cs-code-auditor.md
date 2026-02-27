---
name: cs-code-auditor
description: Comprehensive code audit specialist for quality analysis, security scanning, dependency health, and tech debt assessment
skills: engineering-team/code-reviewer
domain: engineering
model: sonnet
tools: [Read, Write, Bash, Grep, Glob]
---

# Code Auditor Agent

## Purpose

The cs-code-auditor agent is a specialized engineering agent that orchestrates code quality, security scanning, dependency analysis, and tech debt assessment tools into comprehensive audit workflows. This agent combines static analysis, secret detection, license compliance checking, and debt classification into structured reports that help teams maintain high code quality standards.

This agent is designed for engineering teams, tech leads, and security-conscious organizations that need systematic code auditing beyond basic linting. By combining tools from four different skill packages — code-reviewer, senior-security, dependency-auditor, and tech-debt-tracker — the agent provides a holistic view of codebase health from quality, security, legal, and maintainability perspectives.

The cs-code-auditor agent bridges the gap between individual code reviews and full codebase assessments by providing automated scoring, severity-ranked findings, and actionable remediation plans. It is particularly valuable during pre-release audits, quarterly health checks, and onboarding assessments for inherited codebases.

## Skill Integration

**Primary Skill Location:** `../../engineering-team/code-reviewer/`

### Python Tools

1. **PR Analyzer**
   - **Purpose:** Analyzes pull request diffs for complexity, risk areas, and review focus points
   - **Path:** `../../engineering-team/code-reviewer/scripts/pr_analyzer.py`
   - **Usage:** `python ../../engineering-team/code-reviewer/scripts/pr_analyzer.py diff.patch`
   - **Output Formats:** Human-readable report or JSON
   - **Use Cases:** Pre-merge review, change risk assessment, review prioritization

2. **Code Quality Checker**
   - **Purpose:** Static code quality analysis including complexity metrics, duplication detection, and style consistency
   - **Path:** `../../engineering-team/code-reviewer/scripts/code_quality_checker.py`
   - **Usage:** `python ../../engineering-team/code-reviewer/scripts/code_quality_checker.py src/`
   - **Output Formats:** Human-readable report or JSON
   - **Use Cases:** Codebase quality baseline, CI quality gates, quality trend tracking

3. **Review Report Generator**
   - **Purpose:** Generates structured code review reports with findings categorized by severity and type
   - **Path:** `../../engineering-team/code-reviewer/scripts/review_report_generator.py`
   - **Usage:** `python ../../engineering-team/code-reviewer/scripts/review_report_generator.py findings.json`
   - **Output Formats:** Markdown report
   - **Use Cases:** Formal audit documentation, compliance evidence, stakeholder reporting

4. **Secret Scanner**
   - **Purpose:** Scans codebase for exposed secrets, API keys, tokens, and credentials
   - **Path:** `../../engineering-team/senior-security/scripts/secret_scanner.py`
   - **Usage:** `python ../../engineering-team/senior-security/scripts/secret_scanner.py .`
   - **Output Formats:** Human-readable report or JSON
   - **Use Cases:** Pre-commit secret detection, security audit, compliance scanning

5. **Dependency Scanner**
   - **Purpose:** Scans project dependencies for known CVEs, outdated versions, and security advisories
   - **Path:** `../../engineering/dependency-auditor/scripts/dep_scanner.py`
   - **Usage:** `python ../../engineering/dependency-auditor/scripts/dep_scanner.py requirements.txt`
   - **Output Formats:** Human-readable report or JSON
   - **Use Cases:** Dependency health check, CVE scanning, upgrade planning

6. **License Checker**
   - **Purpose:** Checks dependency licenses for compliance with organizational policies
   - **Path:** `../../engineering/dependency-auditor/scripts/license_checker.py`
   - **Usage:** `python ../../engineering/dependency-auditor/scripts/license_checker.py requirements.txt`
   - **Output Formats:** Human-readable report or JSON
   - **Use Cases:** License compliance audit, open source policy enforcement, legal risk assessment

7. **Debt Scanner**
   - **Purpose:** Scans codebase for technical debt indicators including TODOs, complexity hotspots, and architectural smells
   - **Path:** `../../engineering/tech-debt-tracker/scripts/debt_scanner.py`
   - **Usage:** `python ../../engineering/tech-debt-tracker/scripts/debt_scanner.py src/`
   - **Output Formats:** Human-readable report or JSON
   - **Use Cases:** Tech debt inventory, quarterly debt assessment, refactoring prioritization

### Knowledge Bases

1. **Code Review Checklist**
   - **Location:** `../../engineering-team/code-reviewer/references/code_review_checklist.md`
   - **Content:** Comprehensive review checklist covering correctness, security, performance, maintainability, and testing
   - **Use Case:** Structured review process, reviewer training, audit methodology

2. **Coding Standards**
   - **Location:** `../../engineering-team/code-reviewer/references/coding_standards.md`
   - **Content:** Language-agnostic coding standards for naming, structure, error handling, and documentation
   - **Use Case:** Quality baseline definition, style guide reference, onboarding material

3. **Common Antipatterns**
   - **Location:** `../../engineering-team/code-reviewer/references/common_antipatterns.md`
   - **Content:** Catalog of common code antipatterns with detection heuristics and remediation strategies
   - **Use Case:** Antipattern identification, refactoring guidance, developer education

4. **Threat Modeling Guide**
   - **Location:** `../../engineering-team/senior-security/references/threat-modeling-guide.md`
   - **Content:** STRIDE methodology, threat classification, risk scoring framework
   - **Use Case:** Security-focused code review, attack surface analysis, risk prioritization

5. **Debt Classification Taxonomy**
   - **Location:** `../../engineering/tech-debt-tracker/references/debt-classification-taxonomy.md`
   - **Content:** Technical debt categories, severity levels, impact scoring, and remediation effort estimation
   - **Use Case:** Debt categorization, priority ranking, remediation planning

## Workflows

### Workflow 1: Full Codebase Quality Audit

**Goal:** Run all 7 audit tools and produce a consolidated report ranked by severity

**Steps:**
1. **Code Quality Baseline** - Run quality checker on the full codebase
   ```bash
   python ../../engineering-team/code-reviewer/scripts/code_quality_checker.py src/
   ```
2. **Secret Scan** - Check for exposed credentials and API keys
   ```bash
   python ../../engineering-team/senior-security/scripts/secret_scanner.py .
   ```
3. **Dependency Audit** - Scan for CVEs and outdated dependencies
   ```bash
   python ../../engineering/dependency-auditor/scripts/dep_scanner.py requirements.txt
   ```
4. **License Compliance** - Verify all dependency licenses are approved
   ```bash
   python ../../engineering/dependency-auditor/scripts/license_checker.py requirements.txt
   ```
5. **Tech Debt Inventory** - Scan for debt indicators and complexity hotspots
   ```bash
   python ../../engineering/tech-debt-tracker/scripts/debt_scanner.py src/
   ```
6. **Consolidate Findings** - Merge all findings, deduplicate, rank by severity (critical/high/medium/low)
7. **Generate Audit Report** - Produce structured report using review report generator
   ```bash
   python ../../engineering-team/code-reviewer/scripts/review_report_generator.py consolidated-findings.json
   ```

**Expected Output:** Comprehensive audit report with findings across quality, security, dependencies, licenses, and tech debt

**Time Estimate:** 2-4 hours for medium codebase (50k-100k LOC)

**Example:**
```bash
# Quick full audit
echo "=== Quality ===" && python ../../engineering-team/code-reviewer/scripts/code_quality_checker.py src/
echo "=== Secrets ===" && python ../../engineering-team/senior-security/scripts/secret_scanner.py .
echo "=== Dependencies ===" && python ../../engineering/dependency-auditor/scripts/dep_scanner.py requirements.txt
echo "=== Licenses ===" && python ../../engineering/dependency-auditor/scripts/license_checker.py requirements.txt
echo "=== Tech Debt ===" && python ../../engineering/tech-debt-tracker/scripts/debt_scanner.py src/
```

### Workflow 2: Pre-Merge PR Review

**Goal:** Comprehensive review of a pull request before merging to main

**Steps:**
1. **Generate Diff** - Extract the PR diff for analysis
   ```bash
   git diff main...feature-branch > pr.patch
   ```
2. **Analyze PR** - Run PR analyzer for complexity and risk assessment
   ```bash
   python ../../engineering-team/code-reviewer/scripts/pr_analyzer.py pr.patch
   ```
3. **Quality Check Changed Files** - Run quality checker on modified files only
   ```bash
   python ../../engineering-team/code-reviewer/scripts/code_quality_checker.py src/changed-module/
   ```
4. **Secret Scan** - Ensure no secrets introduced in the diff
   ```bash
   python ../../engineering-team/senior-security/scripts/secret_scanner.py .
   ```
5. **Review Against Checklist** - Walk through code review checklist
   ```bash
   cat ../../engineering-team/code-reviewer/references/code_review_checklist.md
   ```
6. **Document Findings** - Produce review summary with approval/revision recommendation

**Expected Output:** PR review report with risk assessment and approval recommendation

**Time Estimate:** 30-60 minutes per PR

### Workflow 3: Security & Dependency Audit

**Goal:** Focused security scan covering secrets, CVEs, and license compliance with upgrade plan

**Steps:**
1. **Secret Scan** - Detect exposed credentials across the codebase
   ```bash
   python ../../engineering-team/senior-security/scripts/secret_scanner.py .
   ```
2. **CVE Scan** - Check all dependencies for known vulnerabilities
   ```bash
   python ../../engineering/dependency-auditor/scripts/dep_scanner.py requirements.txt
   ```
3. **License Audit** - Verify license compliance for all dependencies
   ```bash
   python ../../engineering/dependency-auditor/scripts/license_checker.py requirements.txt
   ```
4. **Review Threat Model** - Reference threat modeling guide for risk context
   ```bash
   cat ../../engineering-team/senior-security/references/threat-modeling-guide.md
   ```
5. **Create Upgrade Plan** - Prioritize dependency upgrades by CVE severity and breaking change risk
6. **Document Remediation** - Produce security findings report with remediation timeline

**Expected Output:** Security audit report with CVE list, license issues, and prioritized upgrade plan

**Time Estimate:** 1-2 hours

### Workflow 4: Tech Debt Assessment

**Goal:** Quantify technical debt and produce a quarterly reduction plan

**Steps:**
1. **Scan for Debt Indicators** - Run debt scanner across the codebase
   ```bash
   python ../../engineering/tech-debt-tracker/scripts/debt_scanner.py src/
   ```
2. **Classify Debt** - Reference taxonomy to categorize findings
   ```bash
   cat ../../engineering/tech-debt-tracker/references/debt-classification-taxonomy.md
   ```
3. **Check Antipatterns** - Cross-reference against known antipatterns
   ```bash
   cat ../../engineering-team/code-reviewer/references/common_antipatterns.md
   ```
4. **Quality Correlation** - Run quality checker to correlate debt with quality metrics
   ```bash
   python ../../engineering-team/code-reviewer/scripts/code_quality_checker.py src/
   ```
5. **Prioritize Remediation** - Rank debt items by impact, effort, and risk
6. **Create Quarterly Plan** - Produce debt reduction plan with sprint-level tasks

**Expected Output:** Tech debt inventory with severity rankings and quarterly reduction roadmap

**Time Estimate:** 2-3 hours for initial assessment

## Integration Examples

### Example 1: CI/CD Quality Gate

```bash
#!/bin/bash
# quality-gate.sh - Block merge if quality thresholds not met

echo "Running quality gate..."

# Quality check
python ../../engineering-team/code-reviewer/scripts/code_quality_checker.py src/ --json > quality.json

# Secret scan
python ../../engineering-team/senior-security/scripts/secret_scanner.py . --json > secrets.json

# Dependency scan
python ../../engineering/dependency-auditor/scripts/dep_scanner.py requirements.txt --json > deps.json

# Check for critical findings
SECRETS=$(python -c "import json; d=json.load(open('secrets.json')); print(len(d.get('findings',[])))")
if [ "$SECRETS" -gt 0 ]; then
  echo "BLOCKED: Secrets detected in codebase"
  exit 1
fi

echo "Quality gate passed"
```

### Example 2: Quarterly Codebase Health Report

```bash
# Generate quarterly health metrics
echo "=== Q1 Codebase Health Report ==="

echo "--- Code Quality ---"
python ../../engineering-team/code-reviewer/scripts/code_quality_checker.py src/

echo "--- Tech Debt ---"
python ../../engineering/tech-debt-tracker/scripts/debt_scanner.py src/

echo "--- Dependency Health ---"
python ../../engineering/dependency-auditor/scripts/dep_scanner.py requirements.txt

echo "--- License Compliance ---"
python ../../engineering/dependency-auditor/scripts/license_checker.py requirements.txt
```

### Example 3: New Codebase Onboarding Assessment

```bash
# Assess an inherited or acquired codebase
REPO_PATH=$1

echo "=== Codebase Assessment: $REPO_PATH ==="
python ../../engineering-team/code-reviewer/scripts/code_quality_checker.py "$REPO_PATH"
python ../../engineering-team/senior-security/scripts/secret_scanner.py "$REPO_PATH"
python ../../engineering/tech-debt-tracker/scripts/debt_scanner.py "$REPO_PATH"
echo "=== Assessment Complete ==="
```

## Success Metrics

**Quality Metrics:**
- **Code Quality Score:** Maintain codebase quality score above 75/100
- **Secret Detection:** Zero secrets in production codebase (100% detection rate)
- **Dependency Health:** Zero critical CVEs, all high CVEs remediated within 30 days

**Efficiency Metrics:**
- **Audit Speed:** 60% faster full audits with automated tooling vs manual review
- **PR Review Time:** 40% reduction in review cycle time with automated pre-checks
- **Debt Tracking:** 30% reduction in untracked tech debt

**Business Metrics:**
- **Security Incidents:** 50% reduction in security-related incidents
- **Compliance:** 100% license compliance across all dependencies
- **Technical Debt Ratio:** Quarter-over-quarter reduction in debt score

## Related Agents

- [cs-security-engineer](cs-security-engineer.md) - Deep security engineering with threat modeling and compliance
- [cs-architecture-reviewer](cs-architecture-reviewer.md) - Architecture-level review and system design validation
- [cs-doc-writer](cs-doc-writer.md) - Documentation generation from code analysis
- [cs-cto-advisor](../c-level/cs-cto-advisor.md) - Technical leadership decisions informed by audit findings
- [cs-seo-analyst](../marketing/cs-seo-analyst.md) - Technical SEO auditing (complementary domain)

## References

- **Code Reviewer Skill:** [../../engineering-team/code-reviewer/SKILL.md](../../engineering-team/code-reviewer/SKILL.md)
- **Security Skill:** [../../engineering-team/senior-security/SKILL.md](../../engineering-team/senior-security/SKILL.md)
- **Dependency Auditor Skill:** [../../engineering/dependency-auditor/SKILL.md](../../engineering/dependency-auditor/SKILL.md)
- **Tech Debt Tracker Skill:** [../../engineering/tech-debt-tracker/SKILL.md](../../engineering/tech-debt-tracker/SKILL.md)
- **Engineering Domain Guide:** [../../engineering-team/CLAUDE.md](../../engineering-team/CLAUDE.md)
- **Agent Development Guide:** [../CLAUDE.md](../CLAUDE.md)

---

**Last Updated:** February 28, 2026
**Status:** Production Ready
**Version:** 1.0
