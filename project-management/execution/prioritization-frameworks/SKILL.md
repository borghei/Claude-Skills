---
name: prioritization-frameworks
description: Comprehensive prioritization framework expert covering 9 methods with scoring tools and decision guidance for product managers.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: project-management
  domain: pm-execution
  updated: 2026-03-04
  python-tools: prioritization_scorer.py
  tech-stack: rice, ice, kano, moscow, eisenhower, opportunity-score, prioritization
---

# Prioritization Framework Expert

## Overview

A comprehensive reference to 9 prioritization frameworks with automated scoring, ranking, and guidance on which framework to use in which situation. The core principle: prioritize problems (opportunities), not features. Features are solutions to problems. If you prioritize features directly, you skip the step of understanding whether the problem is worth solving.

### When to Use

- **Backlog Grooming** -- Too many items, need to rank them objectively.
- **Quarterly Planning** -- Deciding which initiatives to invest in.
- **Stakeholder Alignment** -- Need a structured way to resolve competing priorities.
- **Feature Triage** -- Quick sorting of a long list into actionable categories.

## Framework Decision Tree

Use this to pick the right framework for your situation:

```
START: What are you prioritizing?
  |
  +-- Customer problems/opportunities
  |     -> Opportunity Score (recommended)
  |
  +-- Features or initiatives
  |     |
  |     +-- Need a quick sort (< 15 items)?
  |     |     -> ICE or Impact vs Effort
  |     |
  |     +-- Need rigorous scoring (15+ items)?
  |     |     -> RICE
  |     |
  |     +-- Need stakeholder buy-in on criteria?
  |     |     -> Weighted Decision Matrix
  |     |
  |     +-- Need to categorize requirements?
  |           -> MoSCoW
  |
  +-- Personal PM tasks
  |     -> Eisenhower Matrix
  |
  +-- High-uncertainty initiatives
  |     -> Risk vs Reward
  |
  +-- Understanding user expectations (not prioritizing)
        -> Kano Model
```

## The 9 Frameworks

### 1. Opportunity Score (Recommended for Customer Problems)

**Source:** Dan Olsen, *Lean Product Playbook*

**Formula:** `Score = Importance x (1 - Satisfaction)`

- **Importance** (0-10): How important is this problem to the customer?
- **Satisfaction** (0-1): How well do existing solutions satisfy this need? (0 = not at all, 1 = perfectly)

**Why it works:** It identifies the biggest gaps between what customers need and what they currently have. High importance + low satisfaction = high opportunity.

**Example:**

| Problem | Importance | Satisfaction | Score |
|---------|-----------|-------------|-------|
| Finding products quickly | 9 | 0.3 | 6.3 |
| Comparing prices | 7 | 0.8 | 1.4 |
| Tracking order status | 8 | 0.6 | 3.2 |

"Finding products quickly" scores highest because it is very important and poorly solved today.

### 2. ICE -- Impact x Confidence x Ease

**Best for:** Quick prioritization of a short list (under 15 items).

**Formula:** `Score = Impact x Confidence x Ease`

All three scored 1-10:
- **Impact:** How much will this move the target metric?
- **Confidence:** How sure are we about the impact estimate?
- **Ease:** How easy is this to implement? (10 = trivial, 1 = massive effort)

**Strengths:** Fast, simple, includes uncertainty.
**Weakness:** Subjective. Different people give different scores. Best used as a starting point for discussion, not a final answer.

### 3. RICE -- (Reach x Impact x Confidence) / Effort

**Best for:** Rigorous prioritization of a longer list.

**Formula:** `Score = (Reach x Impact x Confidence) / Effort`

- **Reach:** How many users/customers will this affect in a given time period? (number)
- **Impact:** How much will it affect each user? (3 = massive, 2 = high, 1 = medium, 0.5 = low, 0.25 = minimal)
- **Confidence:** How sure are we? (100% = high, 80% = medium, 50% = low)
- **Effort:** Person-months of work required (number)

**Strengths:** Reach adds a dimension that ICE misses. Effort is estimated in real units, not abstract scores.
**Weakness:** Requires more data (reach estimates, effort sizing).

### 4. Eisenhower Matrix

**Best for:** Personal task management for PMs, not product prioritization.

**Quadrants:**

|  | Urgent | Not Urgent |
|--|--------|------------|
| **Important** | Do First | Schedule |
| **Not Important** | Delegate | Eliminate |

- **Q1 (Do First):** Crisis, deadline-driven. Handle immediately.
- **Q2 (Schedule):** Strategic work, planning, prevention. This is where PMs should spend most of their time.
- **Q3 (Delegate):** Interruptions, some meetings, some emails. Hand off if possible.
- **Q4 (Eliminate):** Time-wasters, unnecessary meetings. Stop doing these.

### 5. Impact vs Effort (2x2 Matrix)

**Best for:** Quick visual triage in a group setting.

**Quadrants:**

|  | Low Effort | High Effort |
|--|-----------|-------------|
| **High Impact** | Quick Wins (do first) | Major Projects (plan carefully) |
| **Low Impact** | Fill-ins (do if time allows) | Money Pits (avoid) |

**How to use:** Plot items on a whiteboard. Discuss placement. The conversation matters more than the exact position.

### 6. Risk vs Reward

**Best for:** Initiatives with significant uncertainty.

**Extension of Impact vs Effort** that adds an uncertainty dimension:

- **Reward** = Expected impact if successful
- **Risk** = Probability of failure x cost of failure

**Quadrants:**

|  | Low Risk | High Risk |
|--|---------|-----------|
| **High Reward** | Safe Bets (prioritize) | Bold Bets (invest selectively) |
| **Low Reward** | Incremental (batch) | Avoid |

### 7. Kano Model

**Best for:** Understanding customer expectations. Not for prioritization directly.

**Categories:**

- **Must-Be (Basic):** Customers expect these. Absence causes dissatisfaction. Presence does not cause delight. (Example: a login page works.)
- **One-Dimensional (Performance):** More is better, linearly. (Example: faster page loads = happier users.)
- **Attractive (Delighters):** Unexpected features that create excitement. Absence does not cause dissatisfaction. (Example: automatic dark mode based on system setting.)
- **Indifferent:** Customers do not care either way.
- **Reverse:** Some customers actively dislike this feature.

**Use Kano to understand**, then use another framework (RICE, ICE) to prioritize.

### 8. Weighted Decision Matrix

**Best for:** Multi-factor decisions that need stakeholder buy-in.

**Process:**
1. Define criteria (e.g., customer impact, revenue potential, technical feasibility, strategic alignment).
2. Assign weights to each criterion (must sum to 100%).
3. Score each option against each criterion (1-5 or 1-10).
4. Multiply scores by weights and sum.
5. Rank by total weighted score.

**Strengths:** Transparent, auditable, gets stakeholders to agree on criteria before scoring.
**Weakness:** Time-consuming. Best for 5-10 high-stakes decisions, not 50-item backlogs.

### 9. MoSCoW

**Best for:** Requirements categorization within a fixed scope.

**Categories:**
- **Must Have:** Non-negotiable. Without these, the release has no value.
- **Should Have:** Important but not critical. Painful to leave out but the release still works.
- **Could Have:** Desirable. Include if time and resources allow.
- **Won't Have (this time):** Explicitly out of scope. Acknowledged but deferred.

**Rule of thumb:** Must-Haves should be no more than 60% of the total effort. If everything is a Must-Have, nothing is.

## Core Principle: Prioritize Problems, Not Features

Features are solutions. Problems are what matter. Two teams can build different features to solve the same problem. If you prioritize features, you lock in a solution before understanding the problem space.

**Workflow:**
1. List customer problems (use Opportunity Score to rank them).
2. Pick the top problems to solve.
3. Generate multiple solution ideas for each problem.
4. Prioritize solutions using RICE or ICE.
5. Build the highest-scoring solutions.

This two-step approach (prioritize problems, then prioritize solutions) produces better outcomes than a single pass over a feature list.

## Tools

| Tool | Purpose | Command |
|------|---------|---------|
| `prioritization_scorer.py` | Score and rank items | `python scripts/prioritization_scorer.py --input items.json --framework rice` |
| `prioritization_scorer.py` | Demo with sample data | `python scripts/prioritization_scorer.py --demo --framework rice` |

Supported frameworks: `rice`, `ice`, `opportunity`, `moscow`, `weighted`

## References

- `references/prioritization-guide.md` -- Detailed formulas, decision tree, and facilitation tips
- `assets/prioritization_matrix_template.md` -- Scoring templates for each framework
