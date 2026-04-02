---
title: Orchestration Patterns
---

# Orchestration Patterns

Four patterns for combining multiple skills and agents into larger workflows.

## Pattern 1: Sequential Pipeline

Run skills one after another, where each step's output feeds the next.

```
Code Review → Security Scan → Performance Profile → Release Readiness
```

**Example:** Pre-release quality gate

```bash
# Step 1: Code quality
python engineering/code-reviewer/scripts/code_quality_analyzer.py .

# Step 2: Security check
python engineering/senior-security/scripts/security_scanner.py .

# Step 3: Performance check
python engineering/performance-profiler/scripts/profiler.py .

# Step 4: Release readiness
python engineering/release-manager/scripts/release_readiness.py .
```

**When to use:** Linear workflows where order matters and each step validates a different dimension.

## Pattern 2: Fan-Out / Fan-In

Run multiple skills in parallel, then merge results.

```
                ┌─ SEO Audit ──────┐
Input Page ─────┼─ A11y Audit ─────┼─── Merged Report
                └─ Performance ────┘
```

**Example:** Comprehensive page audit

Run three independent audits on the same page, then combine findings into a single report sorted by severity.

**When to use:** Independent analyses that can run concurrently. Reduces total wall-clock time.

## Pattern 3: Agent Delegation

A top-level agent delegates subtasks to specialized agents.

```
cs-tech-lead
├── delegates to cs-code-auditor (code quality)
├── delegates to cs-security-engineer (security)
└── synthesizes findings into architecture review
```

**Example:** The `chief-of-staff` skill routes founder questions to the right C-suite advisor (CEO, CTO, CFO, etc.) and synthesizes their responses.

**When to use:** Complex tasks that span multiple domains and need a coordinator.

## Pattern 4: Iterative Refinement

Run a skill, evaluate the output, and re-run with adjustments.

```
Draft Content → SEO Score → Revise → SEO Score → Publish
```

**Example:** Content production loop

1. Generate draft with `content-creator`
2. Score with `seo-specialist` tools
3. If score < threshold, revise and re-score
4. Publish when quality gate passes

**When to use:** Tasks where quality improves through iteration and you have a measurable quality metric.

## Choosing a Pattern

| Pattern | Best For | Complexity |
|---|---|---|
| Sequential | Quality gates, release pipelines | Low |
| Fan-Out/Fan-In | Multi-dimensional analysis | Medium |
| Agent Delegation | Cross-domain strategy | Medium |
| Iterative Refinement | Content, optimization | High |

!!! tip "Start simple"
    Most workflows only need Pattern 1 (sequential). Add complexity only when you have a clear reason.

## Building Custom Workflows

Combine patterns using shell scripts, GitHub Actions, or the `agenthub` skill for DAG-based orchestration:

```bash
# See the agenthub skill for multi-agent DAG orchestration
cat engineering/agenthub/SKILL.md
```
