---
name: prompt-governance
description: >
  This skill should be used when the user asks to "audit prompts for safety",
  "check prompts for injection vulnerabilities", "manage a prompt catalog",
  "version control prompts", or "review prompt quality and compliance".
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: engineering
  domain: ai-governance
  updated: 2026-04-02
  tags: [prompt-governance, prompt-safety, prompt-audit, prompt-catalog, ai-compliance]
---

# Prompt Governance

> **Category:** Engineering
> **Domain:** AI Governance

## Overview

The **Prompt Governance** skill provides tools for auditing prompts for security vulnerabilities, bias, and safety issues, plus managing a versioned catalog of approved prompts. Essential for organizations deploying LLM-based applications at scale.

## Clarify First

Before auditing or cataloging, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Target prompt(s):** the exact file/text to audit or the catalog dir to manage (the subject of every check).
- **Task: audit vs catalog management:** selects `prompt_auditor.py` vs `prompt_catalog_manager.py` and the whole workflow.
- **Check focus:** injection / bias / safety (sets which auditor checks run and the pass/fail bar).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Quick Start

```bash
# Audit a prompt for security and safety issues
python scripts/prompt_auditor.py --file system_prompt.txt

# Audit with specific focus
python scripts/prompt_auditor.py --text "You are a helpful assistant..." --checks injection,bias,safety

# Initialize a prompt catalog
python scripts/prompt_catalog_manager.py --init --catalog-dir ./prompts

# Add a prompt to the catalog
python scripts/prompt_catalog_manager.py --add --name "customer-support-v1" --file prompt.txt --catalog-dir ./prompts

# List all prompts in catalog
python scripts/prompt_catalog_manager.py --list --catalog-dir ./prompts
```

## Tools Overview

| Tool | Purpose | Key Flags |
|------|---------|-----------|
| `prompt_auditor.py` | Audit prompts for injection, bias, and safety | `--file`, `--text`, `--checks`, `--format` |
| `prompt_catalog_manager.py` | Manage versioned prompt catalog | `--init`, `--add`, `--list`, `--diff`, `--catalog-dir` |

## Workflows

### Prompt Review Process
1. Author writes or modifies a prompt
2. Run `prompt_auditor.py` for automated checks
3. Review findings and address critical issues
4. Add approved prompt to catalog with `prompt_catalog_manager.py`
5. Deploy from catalog (never from ad-hoc sources)

### Prompt Versioning
1. Store all prompts in the catalog; each `--add` with changed content gets the next patch version (1.0.0, 1.0.1, ...), and identical content is rejected as a duplicate
2. Use `--diff` to compare versions before promotion
3. Move the latest version through draft, review, approved and deployed with `--status`; keep the catalog directory in version control for the audit trail
4. There is no rollback command, and re-adding an earlier version's text is rejected as a duplicate. To roll back, redeploy the previous version's text from `versions/<name>_v<x_y_z>.txt` and mark the bad latest version `retired` with `--status retired` (the CLI changes the latest version only)

## Scope & Limitations

**In Scope:**
- Pattern-based audit of a prompt with `prompt_auditor.py` across four check groups: injection, bias, safety and quality, selectable with `--checks`.
- A local, file-based prompt catalog with `prompt_catalog_manager.py`: init, add with automatic version numbers and a content hash, list, search, diff between versions, and status changes (draft, review, approved, deployed, retired).
- The prompt review and versioning workflows, and the policies, audit categories, severity levels, catalog schema and review checklist in `references/prompt-governance-framework.md`.

**Out of Scope:**
- Testing a deployed model or application against live injection or jailbreak attempts (see `engineering/ai-security/`).
- Measuring output quality or task accuracy of a prompt (see `engineering/agentic-evaluation-framework/`).
- Writing or tuning prompts (see `engineering/senior-prompt-engineer/`) and reducing token cost (see `engineering/llm-cost-optimizer/`).
- Regulatory AI governance such as the EU AI Act or ISO/IEC 42001 (see `ra-qm-team/eu-ai-act-specialist/` and `ra-qm-team/iso42001-ai-management/`).
- Serving prompts to an application or rolling them back at runtime. The catalog records versions and status only.

**Important Caveats:**
- The auditor matches regular expressions against prompt text. It catches known phrasings, misses reworded or new ones, and can flag harmless text. A clean audit is not evidence that a prompt is safe or unbiased.
- The auditor and the catalog are not linked. New catalog entries are stored with audit status `pending`, and running the auditor does not update it.
- The catalog is a local directory with a JSON index and no access control, locking or signing. Approval and audit trail depend on the user's own version control and review process.

## Reference Documentation

- [Prompt Governance Framework](references/prompt-governance-framework.md) - Policies, review processes, and compliance requirements

## Common Patterns

### Prompt Lifecycle
Draft -> Audit -> Review -> Approve -> Deploy -> Monitor -> Retire

### Governance Checklist
- No injection vulnerabilities
- No harmful content generation potential
- Appropriate bias mitigation
- Clear scope boundaries
- Output format constraints
- Error handling instructions
