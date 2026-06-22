---
name: prioritization-frameworks
description: >
  Comprehensive prioritization framework expert covering 9 methods with scoring
  tools and decision guidance for product managers.
license: MIT + Commons Clause
metadata:
  version: 1.0.1
  author: borghei
  category: project-management
  domain: pm-execution
  updated: 2026-06-15
  python-tools: prioritization_scorer.py
  tech-stack: rice, ice, kano, moscow, eisenhower, opportunity-score, prioritization
---
# Prioritization Framework Expert

## Overview

A comprehensive reference to 9 prioritization frameworks with automated scoring, ranking, and guidance on which framework to use in which situation. The core principle: prioritize problems (opportunities), not features. Features are solutions to problems. If you prioritize features directly, you skip the step of understanding whether the problem is worth solving.

## Core Capabilities

- **9 frameworks** — RICE, ICE, Opportunity Score, Eisenhower, Impact vs Effort, Risk vs Reward, Kano, Weighted Decision Matrix, MoSCoW (full definitions, formulas, and worked examples in `references/frameworks-catalog.md`).
- **Framework selection** — a decision tree maps the thing you are prioritizing (problems, features, personal tasks, high-uncertainty bets) to the right method.
- **Automated scoring** — `prioritization_scorer.py` ranks items for RICE, ICE, Opportunity, MoSCoW, and Weighted Decision Matrix.
- **Two-step discipline** — prioritize problems first (Opportunity Score), then prioritize solutions (RICE/ICE).

## When to Use

- **Backlog Grooming** -- Too many items, need to rank them objectively.
- **Quarterly Planning** -- Deciding which initiatives to invest in.
- **Stakeholder Alignment** -- Need a structured way to resolve competing priorities.
- **Feature Triage** -- Quick sorting of a long list into actionable categories.

## Clarify First

Before scoring, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **What you're ranking** — problems/opportunities vs features vs personal tasks (the decision tree picks the framework from this)
- [ ] **Framework** — rice / ice / opportunity / moscow / weighted (each requires different score fields and emits different rankings)
- [ ] **Quality of the estimates** — measured data vs guesses for reach/impact (guesses make RICE/ICE precision misleading; switch to a coarser method)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Quick Start

| Tool | Purpose | Command |
|------|---------|---------|
| `prioritization_scorer.py` | Score and rank items | `python scripts/prioritization_scorer.py --input items.json --framework rice` |
| `prioritization_scorer.py` | Demo with sample data | `python scripts/prioritization_scorer.py --demo --framework rice` |

Supported frameworks: `rice`, `ice`, `opportunity`, `moscow`, `weighted`. See `references/tool-and-troubleshooting.md` for input JSON schemas and flags.

## References

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/frameworks-catalog.md](references/frameworks-catalog.md)** — full definitions, formulas, strengths/weaknesses, and worked examples for all 9 frameworks, the framework decision tree, and the "prioritize problems, not features" principle. Read when choosing or applying a specific framework.
- **[references/prioritization-guide.md](references/prioritization-guide.md)** — detailed formulas, decision tree, and facilitation tips. Read when facilitating a scoring session with a group.
- **[references/red-flags.md](references/red-flags.md)** — anti-patterns and warning signs in prioritization practice. Read when a process feels off or results are being gamed.
- **[references/tool-and-troubleshooting.md](references/tool-and-troubleshooting.md)** — `prioritization_scorer.py` flags, per-framework input JSON schemas, troubleshooting table, and success criteria. Read when running the tool or diagnosing scoring problems.
- **[assets/prioritization_matrix_template.md](assets/prioritization_matrix_template.md)** — scoring templates for each framework. Use when capturing a manual scoring exercise.

## Scope & Limitations

**In Scope:**
- 9 prioritization frameworks with scoring, ranking, and explanation (RICE, ICE, Opportunity Score, Eisenhower, Impact vs. Effort, Risk vs. Reward, Kano, Weighted Decision Matrix, MoSCoW)
- Automated scoring and ranking for RICE, ICE, Opportunity Score, MoSCoW, and Weighted Decision Matrix
- Framework selection guidance via Decision Tree
- Demo data for each framework to illustrate input/output formats

**Out of Scope:**
- Real-time Jira/Linear backlog integration (manual JSON input required)
- Cost-of-delay or WSJF calculations (see `senior-pm/` skill for SAFe portfolio prioritization)
- User research to gather importance/satisfaction data for Opportunity Score (see `product-team/` skills)
- Strategic portfolio allocation decisions (see `senior-pm/` skill)

**Important Caveats:**
- No framework produces a "correct" answer. Prioritization frameworks are decision-support tools that structure conversation, not algorithms that replace judgment.
- RICE and ICE are best for data-rich environments. If your reach and impact estimates are pure guesses, the precision of the formula is misleading.
- The most successful teams combine frameworks: start with Opportunity Score to identify the right problems, then use RICE to rank solutions.
- For teams with 50+ people or multiple stakeholder groups, use WSJF or Weighted Decision Matrix with agreed criteria to ensure buy-in.

## Integration Points

| Integration | Direction | Description |
|------------|-----------|-------------|
| `execution/outcome-roadmap/` | Feeds into | Prioritized items inform Now/Next/Later horizon placement |
| `execution/create-prd/` | Feeds into | Top-priority items become PRD candidates with P0/P1/P2 feature labels |
| `execution/brainstorm-okrs/` | Complements | Prioritized initiatives inform which OKR theme to focus on this quarter |
| `discovery/identify-assumptions/` | Receives from | Assumption risk scores inform item confidence ratings in RICE/ICE |
| `scrum-master/` | Feeds into | Prioritized backlog items feed sprint planning commitment decisions |
| `senior-pm/` | Receives from | Portfolio-level WSJF or strategic priorities constrain team-level prioritization |
