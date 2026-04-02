# Prompt Governance Framework

## Purpose

A prompt governance framework ensures that all prompts deployed in production LLM applications are secure, safe, unbiased, and effective. It provides the policies, processes, and tools needed to manage prompts as first-class artifacts.

## Core Principles

1. **Prompts are Code**: Treat prompts with the same rigor as production code - version control, review, testing, deployment gates
2. **Defense in Depth**: Layer multiple safety checks rather than relying on a single mechanism
3. **Least Privilege**: Prompts should grant the minimum capabilities needed for the task
4. **Auditability**: Every prompt change should be traceable to an author, reviewer, and approval

## Governance Policies

### P1: Prompt Approval Required
No prompt enters production without passing automated audits and human review.

### P2: Version Control Mandatory
All prompts must be stored in a versioned catalog with full change history.

### P3: Regular Re-Audit
Production prompts must be re-audited quarterly or when the underlying model changes.

### P4: Incident Response
When a prompt-related incident occurs, the prompt must be immediately flagged for review.

## Audit Categories

### 1. Injection Vulnerability Assessment
- Direct injection vectors (user input in prompt)
- Indirect injection vectors (external data in prompt)
- Jailbreak resistance
- System prompt leakage risk

### 2. Bias Detection
- Demographic bias in instructions
- Stereotyping language
- Exclusionary terminology
- Cultural assumptions

### 3. Safety Assessment
- Harmful content generation potential
- PII handling compliance
- Content policy adherence
- Output scope restrictions

### 4. Quality Assessment
- Clarity of instructions
- Completeness of context
- Consistency of tone
- Error handling coverage

## Severity Levels

| Level | Description | Required Action |
|-------|-------------|-----------------|
| CRITICAL | Active exploitation possible | Block deployment, immediate fix |
| HIGH | Significant risk, exploitable | Fix before deployment |
| MEDIUM | Moderate risk, specific conditions | Fix within next sprint |
| LOW | Minor concern, theoretical | Track and address at convenience |
| INFO | Suggestion for improvement | Optional optimization |

## Prompt Catalog Schema

```yaml
name: prompt-name
version: 1.0.0
author: author-name
status: draft|review|approved|deployed|retired
created: 2026-01-01
updated: 2026-01-15
model_target: [gpt-4o, claude-sonnet]
audit_status: passed|failed|pending
last_audit: 2026-01-15
tags: [customer-support, billing]
content: |
  The actual prompt text...
```

## Review Checklist

- [ ] No user input directly concatenated into prompt
- [ ] System prompt does not leak when challenged
- [ ] No biased or exclusionary language
- [ ] PII handling instructions included if applicable
- [ ] Output format and scope clearly defined
- [ ] Error cases addressed
- [ ] Token usage optimized
- [ ] Compatible with target models
