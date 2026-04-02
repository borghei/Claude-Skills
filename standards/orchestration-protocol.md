---
name: orchestration-protocol
description: Multi-agent coordination framework for combining skills, agents, and personas
version: 1.0.0
updated: 2026-04-02
---

# Orchestration Protocol

## Overview

This protocol defines how to combine skills, agents, and personas into coordinated workflows for complex, cross-functional projects. It provides four repeatable patterns so users can tackle multi-component work without reinventing coordination logic every time.

**Scope:** Any workflow involving two or more skills, agents, or personas working together.

## Core Concepts

### Skills = "How to Execute"

Neutral, task-specific packages containing domain expertise, tools, and templates. No personality or strategic perspective.

- **Stateless**, **Composable**, **Deterministic**
- Examples: `seo-audit`, `code-reviewer`, `database-designer`, `financial-modeler`

### Agents = "What to Do"

Professional, domain-bound coordinators that select and sequence skills, interpret results, and make domain-specific decisions.

- **Domain-scoped**, **Workflow-aware**, **Decision-capable**
- Examples: `cs-content-creator`, `cs-cto-advisor`, `cs-product-manager`

### Personas = "Who Thinks"

Personality-driven, cross-domain thinkers that shape *why* something matters and *which tradeoffs* to accept.

- **Cross-domain**, **Opinionated**, **Contextual**
- Examples: `solo-founder`, `startup-cto`, `enterprise-architect`

### Hierarchy

```
Persona (strategic direction)
  └── Agent (domain coordination)
        └── Skill (task execution)
```

A persona activates agents. An agent sequences skills. A skill produces output. Information flows up (outputs, findings) and down (goals, constraints).

## Pattern 1: Solo Sprint

**One persona switches across skills through project phases.**

### When to Use

Single-person projects, time-constrained sprints, early-stage prototyping where breadth matters more than depth.

### Flow

```
Persona → Skill 1 → Skill 2 → Skill 3
   ↑                                |
   └── context carries forward ─────┘
```

### Example: Solo Founder Launch

```yaml
persona: solo-founder
phases:
  - phase: Strategy
    skill: launch-strategy
    output: Go-to-market plan with positioning, channels, timeline
  - phase: Content
    skill: content-creator
    input: Go-to-market plan
    output: Landing page copy, email sequences, social posts
  - phase: Optimization
    skill: seo-audit
    input: Landing page copy
    output: SEO-optimized content with keyword targets
  - phase: Analytics
    skill: campaign-analytics
    input: Channel strategy from phase 1
    output: KPI dashboard, tracking plan, attribution model
```

### Rules

1. **Context accumulates** — each phase receives outputs from all previous phases
2. **Persona decides transitions** — the persona determines when a phase is complete
3. **Backtracking is allowed** — if phase 3 reveals issues, return to phase 1
4. **Time-box phases** — set explicit time limits to prevent over-optimization

### Anti-Patterns

- Running all skills simultaneously (defeats the purpose of phased thinking)
- Skipping context handoff between phases (each skill starts cold)
- Using Solo Sprint when you need deep expertise (use Domain Deep-Dive instead)

## Pattern 2: Domain Deep-Dive

**One persona stacks multiple skills from the same domain for comprehensive analysis.**

### When to Use

Deep expertise needed in one area — architecture decisions, compliance reviews, or any situation where one skill provides insufficient depth.

### Flow

```
Persona + Skill A ──┐
         Skill B ──┤── Synthesized domain expertise
         Skill C ──┘
```

### Example: Technical Architecture Review

```yaml
persona: startup-cto
domain: engineering
skills:
  - skill: senior-architect
    focus: System design, component boundaries, scaling strategy
  - skill: database-designer
    focus: Data model, query patterns, storage tradeoffs
  - skill: performance-profiler
    focus: Bottleneck identification, caching strategy, load projections
  - skill: security-scan
    focus: Attack surface, authentication model, data protection
synthesis:
  method: Persona merges all skill outputs into unified architecture decision
  output: Architecture Decision Record with tradeoffs documented
```

### Rules

1. **Same domain only** — cross-domain stacking is Pattern 3, not Pattern 2
2. **Persona synthesizes** — skills produce raw analysis, persona interprets
3. **Contradictions are valuable** — when skills disagree, the persona must resolve and document the tradeoff
4. **Depth over breadth** — prefer fewer skills explored deeply over many explored shallowly

### Anti-Patterns

- Stacking skills from different domains (use Multi-Agent Handoff instead)
- Treating skill outputs as final answers (persona must synthesize)
- Adding skills past diminishing returns (3-5 skills is the practical maximum)

## Pattern 3: Multi-Agent Handoff

**Multiple personas review each other's work for cross-functional validation.**

### When to Use

Cross-functional decisions, risk mitigation through adversarial review, or any workflow where a single perspective creates blind spots.

### Flow

```
Persona A ──produces──→ Artifact
Persona B ──reviews───→ Artifact (annotated)
Persona C ──validates──→ Final decision
```

### Example: Product Launch Decision

```yaml
handoff_chain:
  - persona: product-manager
    action: produce
    skill: product-requirements
    output: PRD with user stories, success metrics, timeline

  - persona: startup-cto
    action: review
    skill: technical-feasibility
    input: PRD from product-manager
    output: Technical assessment — feasibility, effort, risks, alternatives

  - persona: finance-lead
    action: review
    skill: financial-modeler
    input: PRD + technical assessment
    output: ROI analysis, resource cost, payback period

  - persona: product-manager
    action: decide
    input: All reviews
    output: Go/no-go decision with documented tradeoffs
```

### Handoff Protocol

Each handoff must include: (1) the artifact being passed, (2) context on why it was produced, (3) specific questions for the next persona, and (4) non-negotiable constraints from previous reviewers.

### Rules

1. **Explicit handoff points** — never assume context transfers automatically
2. **Each persona adds value** — if a review pass adds nothing, remove it
3. **Conflict resolution** — when personas disagree, document both positions and let the decision-maker choose
4. **Maximum 4 handoffs** — beyond this, diminishing returns set in rapidly
5. **Final persona decides** — the chain must end with a clear decision-maker

### Anti-Patterns

- Circular reviews with no decision-maker (review loops forever)
- Handoffs without explicit questions (reviewer does not know what to evaluate)
- Too many reviewers (dilutes accountability, slows velocity)
- Same domain reviewing itself (use Domain Deep-Dive instead)

## Pattern 4: Skill Chain

**Sequential skills without persona, pure execution pipeline.**

### When to Use

Well-defined pipelines, CI/CD-like flows, batch processing — any automation where consistency matters more than creativity.

### Flow

```
Skill 1 output → Skill 2 input → Skill 3 input → Final output
```

### Example: Code Quality Pipeline

```yaml
chain:
  - skill: code-reviewer
    input: Pull request diff
    output: Code review findings (JSON)

  - skill: security-scan
    input: Code review findings + source code
    output: Security assessment (JSON)

  - skill: tech-debt-analyzer
    input: Source code + code review findings
    output: Tech debt report (JSON)

  - skill: changelog-generator
    input: All previous outputs + commit history
    output: Changelog entry (Markdown)
```

### Rules

Each skill in a chain must declare its input/output format (JSON, Markdown, or plain text) and required fields.

1. **No persona needed** — if you need judgment between steps, use Pattern 1 or 3
2. **Strict contracts** — each skill must declare its input/output format
3. **Fail-fast** — if a skill produces invalid output, stop the chain immediately
4. **Idempotent** — running the chain twice on the same input produces the same output
5. **Observable** — log each step's input/output for debugging

### Anti-Patterns

- Adding personas to a pure execution chain (adds latency without value)
- Chains longer than 6 steps (debug complexity grows exponentially)
- Skills that modify their input in place (breaks traceability)
- Missing error handling between steps (silent failures corrupt downstream output)

## Orchestration Rules

### Pattern Selection Guide

| Situation | Pattern | Reason |
|-----------|---------|--------|
| One person, multiple phases | Solo Sprint | Context continuity matters |
| Deep analysis in one domain | Domain Deep-Dive | Depth over breadth |
| Cross-functional decision | Multi-Agent Handoff | Multiple perspectives needed |
| Repeatable automation | Skill Chain | No judgment needed between steps |
| Unsure which pattern | Solo Sprint | Safest default, easiest to evolve |

### Combining Patterns

Patterns can nest (maximum 2 levels). A Multi-Agent Handoff might include a Domain Deep-Dive at one review step. The outer pattern controls flow; inner patterns are black boxes. Document nesting explicitly.

### Error Handling

1. **Skill failure:** Retry once. If it fails again, escalate to a persona.
2. **Handoff failure:** Return to previous persona with specific questions.
3. **Chain failure:** Stop, log the failure point, report completed steps.
4. **Pattern mismatch:** Stop and re-evaluate pattern selection.

## Anti-Patterns

- **The Kitchen Sink:** Activating every skill and persona for a simple task. Start with minimum viable orchestration.
- **The Echo Chamber:** Same-domain personas reviewing each other. This produces agreement, not validation.
- **The Infinite Loop:** Review chains without a decision-maker. Set max review cycles (recommended: 2).
- **The Premature Pipeline:** Building a Skill Chain before the workflow is proven. Use Solo Sprint first to explore.
- **The Context Dropout:** Failing to pass context between steps. Summarize if needed, but never drop silently.

---

**Last Updated:** April 2, 2026
**Version:** 1.0.0
**Status:** Active standard for all multi-component workflows
