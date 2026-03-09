---
name: self-improving-agent
description: Patterns for building AI agents that learn from their own execution, detect failure modes, and improve autonomously. Covers feedback loops, performance regression detection, memory curation, skill extraction, and meta-learning architectures. Use when building agents that need to get better over time, managing auto-memory, or designing self-correcting systems.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: engineering
  domain: ai-agents
  tier: POWERFUL
  updated: 2026-03-09
  frameworks: feedback-loops, memory-curation, meta-learning, performance-regression
---

# Self-Improving Agent - Autonomous Learning Patterns

**Tier:** POWERFUL
**Category:** Engineering
**Tags:** self-improvement, AI agents, feedback loops, auto-memory, meta-learning, performance tracking

## Overview

Self-Improving Agent provides architectural patterns for AI agents that get better with use. Most agents are stateless -- they make the same mistakes repeatedly because they lack mechanisms to learn from their own execution. This skill addresses that gap with concrete patterns for feedback capture, memory curation, skill extraction, and regression detection.

The key insight: auto-memory captures everything, but curation is what turns noise into knowledge.

## Core Architecture

### The Improvement Loop

```
┌──────────────────────────────────────────────────────────┐
│                   SELF-IMPROVEMENT CYCLE                  │
│                                                          │
│  ┌─────────┐    ┌──────────┐    ┌─────────────┐        │
│  │ Execute  │───▶│ Evaluate │───▶│ Extract     │        │
│  │ Task     │    │ Outcome  │    │ Learnings   │        │
│  └─────────┘    └──────────┘    └─────────────┘        │
│       ▲                               │                  │
│       │                               ▼                  │
│  ┌─────────┐    ┌──────────┐    ┌─────────────┐        │
│  │ Apply   │◀───│ Promote  │◀───│ Validate    │        │
│  │ Rules   │    │ to Rules │    │ Learnings   │        │
│  └─────────┘    └──────────┘    └─────────────┘        │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Improvement Maturity Levels

| Level | Name | Mechanism | Example |
|-------|------|-----------|---------|
| 0 | Stateless | No memory between sessions | Default agent behavior |
| 1 | Recording | Captures observations, no action | Auto-memory logging |
| 2 | Curating | Organizes and deduplicates observations | Memory review + cleanup |
| 3 | Promoting | Graduates patterns to enforced rules | MEMORY.md entries become CLAUDE.md rules |
| 4 | Extracting | Creates reusable skills from proven patterns | Recurring solutions become skill packages |
| 5 | Meta-Learning | Adapts learning strategy itself | Adjusts what to capture based on what proved useful |

Most agents operate at Level 0-1. This skill provides the machinery for Levels 2-5.

## Core Capabilities

### 1. Memory Curation System

#### The Memory Stack

```
┌─────────────────────────────────────────────────┐
│  CLAUDE.md / .claude/rules/                      │
│  Highest authority. Enforced every session.       │
│  Capacity: Unlimited. Load: Full file.           │
├─────────────────────────────────────────────────┤
│  MEMORY.md (auto-memory)                         │
│  Project learnings. Auto-captured by Claude.     │
│  Capacity: First 200 lines loaded. Overflow to   │
│  topic files.                                    │
├─────────────────────────────────────────────────┤
│  Session Context                                  │
│  Current conversation. Ephemeral.                │
│  Capacity: Context window.                       │
└─────────────────────────────────────────────────┘
```

#### Memory Review Protocol

Run periodically (weekly or after every 10 sessions):

```
Step 1: Read MEMORY.md and all topic files
Step 2: Classify each entry

  Categories:
  - PROMOTE: Pattern proven 3+ times, should be a rule
  - CONSOLIDATE: Multiple entries saying the same thing
  - STALE: References deleted files, old patterns, resolved issues
  - KEEP: Still relevant, not yet proven enough to promote
  - EXTRACT: Recurring solution that should be a reusable skill

Step 3: Execute actions
  - PROMOTE entries → move to CLAUDE.md or .claude/rules/
  - CONSOLIDATE entries → merge into single clear entry
  - STALE entries → delete
  - EXTRACT entries → create skill package (see Skill Extraction)

Step 4: Verify MEMORY.md is under 200 lines
  - If over 200: move topic-specific entries to topic files
  - Topic files: ~/.claude/projects/<path>/memory/<topic>.md
```

#### Promotion Criteria

An entry is ready for promotion when:

| Criterion | Threshold | Why |
|-----------|-----------|-----|
| Recurrence | Seen in 3+ sessions | Not a one-off |
| Consistency | Same solution every time | Not context-dependent |
| Impact | Prevented errors or saved significant time | Worth enforcing |
| Stability | Underlying code/system unchanged | Won't immediately become stale |
| Clarity | Can be stated in 1-2 sentences | Rules must be unambiguous |

#### Promotion Targets

| Pattern Type | Promote To | Example |
|-------------|-----------|---------|
| Coding convention | `.claude/rules/<area>.md` | "Always use `type` not `interface` for object shapes" |
| Project architecture | `CLAUDE.md` | "All API routes go through middleware chain" |
| Tool preference | `CLAUDE.md` | "Use pnpm, not npm" |
| Debugging pattern | `.claude/rules/debugging.md` | "When tests fail, check env vars first" |
| File-scoped rule | `.claude/rules/<scope>.md` with `paths:` | "In migrations/, always add down migration" |

### 2. Feedback Loop Design

#### Outcome Classification

Every agent task produces an outcome. Classify it:

```
SUCCESS         - Task completed, user accepted result
PARTIAL         - Task completed but required corrections
FAILURE         - Task failed, user had to redo
REJECTION       - User explicitly rejected approach
TIMEOUT         - Task exceeded time/token budget
ERROR           - Technical error (tool failure, API error)
```

#### Signal Extraction from Outcomes

| Outcome | Signal | Memory Action |
|---------|--------|---------------|
| SUCCESS (first try) | Approach works well | Reinforce (increment confidence) |
| SUCCESS (after correction) | Initial approach had gap | Log the correction pattern |
| PARTIAL (user edited result) | Output format or content gap | Log what user changed |
| FAILURE | Approach fundamentally wrong | Log anti-pattern with context |
| REJECTION | Misunderstood requirements | Log clarification pattern |
| Repeated ERROR | Tool or environment issue | Log workaround or fix |

#### Feedback Capture Template

```markdown
## Learning: [Short description]

**Context:** [What task was being performed]
**What happened:** [Outcome description]
**Root cause:** [Why the outcome occurred]
**Correct approach:** [What should have been done]
**Confidence:** [High/Medium/Low]
**Recurrence:** [First time / Seen N times]
**Action:** [KEEP / PROMOTE / EXTRACT]
```

### 3. Performance Regression Detection

#### Metrics to Track

| Metric | Measurement | Regression Signal |
|--------|-------------|-------------------|
| First-attempt success rate | Tasks accepted without correction | Dropping below 70% |
| Correction count per task | User edits after agent output | Rising above 2 per task |
| Tool error rate | Failed tool calls / total calls | Rising above 5% |
| Context relevance | Retrieved context actually used | Dropping below 60% |
| Task completion time | Turns to complete task | Rising trend over 5 sessions |

#### Regression Response Protocol

```
1. DETECT: Metric crosses threshold
2. DIAGNOSE: Compare recent sessions vs baseline
   - What changed? (New code? New patterns? New tools?)
   - Which task types are affected?
   - Is it a memory issue or a capability issue?
3. RESPOND:
   - Memory issue → Review and curate MEMORY.md
   - Stale rules → Update CLAUDE.md
   - New code patterns → Add rules for new patterns
   - Capability gap → Extract as skill request
4. VERIFY: Track metric for next 3 sessions
```

### 4. Skill Extraction

When a solution pattern is proven and reusable, extract it into a standalone skill.

#### Extraction Criteria

```
A pattern is ready for extraction when:
- Used successfully 5+ times across different contexts
- Solution is generalizable (not project-specific)
- Takes more than trivial effort to recreate from scratch
- Would benefit other projects/users
```

#### Extraction Process

```
Step 1: Document the pattern
  - What problem does it solve?
  - What's the step-by-step approach?
  - What are the inputs and outputs?
  - What are the edge cases?

Step 2: Generalize
  - Remove project-specific details
  - Identify configurable parameters
  - Add handling for common variations

Step 3: Package as skill
  - Create SKILL.md with frontmatter
  - Add references/ for knowledge bases
  - Add scripts/ if automatable
  - Add assets/ for templates

Step 4: Validate
  - Test on a different project
  - Have another person/agent use it
  - Iterate on unclear instructions
```

### 5. Meta-Learning Patterns

#### Adaptive Capture Strategy

Not all observations are equally valuable. Adjust what gets captured based on what proved useful:

```
Initial strategy: Capture everything
After 10 sessions: Analyze which captured items led to promotions
After 20 sessions: Adjust capture to focus on high-value categories

High-value categories (typically):
  - Error resolutions (80% promotion rate)
  - User corrections (70% promotion rate)
  - Tool preferences (60% promotion rate)

Low-value categories (typically):
  - File structure observations (10% promotion rate)
  - One-off workarounds (5% promotion rate)
```

#### Anti-Pattern Detection

Beyond capturing what works, actively detect what fails:

| Anti-Pattern | Detection Signal | Response |
|-------------|-----------------|----------|
| Repeated wrong import path | Same correction 3+ times | Add to CLAUDE.md as rule |
| Wrong test framework used | User always changes test approach | Add testing rules |
| Incorrect API usage | Same API error pattern | Add API usage notes |
| Style guide violations | User reformats same patterns | Add style rules |
| Wrong branch workflow | User corrects git operations | Add git workflow rules |

### 6. Continuous Calibration

#### Confidence Scoring

Every piece of learned knowledge carries a confidence score:

```
Confidence = base_score * recency_factor * consistency_factor

base_score:
  - User explicitly stated: 1.0
  - Observed from successful outcome: 0.8
  - Inferred from pattern: 0.6
  - Guessed from context: 0.3

recency_factor:
  - Last 7 days: 1.0
  - 7-30 days: 0.9
  - 30-90 days: 0.7
  - 90+ days: 0.5

consistency_factor:
  - Never contradicted: 1.0
  - Contradicted once, reaffirmed: 0.9
  - Contradicted, not reaffirmed: 0.5
  - Actively contradicted: 0.0 (delete)
```

#### Belief Revision

When new information contradicts existing knowledge:

```
1. Compare confidence scores
2. If new info higher confidence → update knowledge
3. If roughly equal → flag for user confirmation
4. If new info lower confidence → keep existing, note conflict
5. Always log the conflict for review
```

## Workflows

### Workflow 1: Weekly Memory Health Check

```
1. Read all memory files (MEMORY.md + topic files)
2. Count total entries and lines
3. For each entry, classify: PROMOTE / CONSOLIDATE / STALE / KEEP / EXTRACT
4. Execute promotions (with user confirmation)
5. Execute consolidations
6. Delete stale entries
7. Verify under 200-line limit
8. Report: entries promoted, consolidated, deleted, remaining
```

### Workflow 2: Post-Session Learning Capture

```
1. Review session outcomes (successes, corrections, failures)
2. For each correction: log what was wrong and what was right
3. For each failure: log root cause and correct approach
4. Check existing memory for related entries
5. If related entry exists: increment recurrence count
6. If new: add entry with context
7. If recurrence threshold met: flag for promotion
```

### Workflow 3: Regression Investigation

```
1. Identify the degraded metric
2. Pull last 5 sessions' outcomes for that task type
3. Compare against baseline (first 5 sessions)
4. Identify what changed: memory, code, rules, environment
5. Propose fix: update rule, add rule, retrain pattern
6. Apply fix
7. Monitor next 3 sessions
```

## Common Pitfalls

| Pitfall | Why It Happens | Fix |
|---------|---------------|-----|
| Memory bloat | Auto-capture without curation | Weekly review, enforce 200-line limit |
| Stale rules | Code changes, rules don't update | Timestamp rules, periodic re-verification |
| Over-promotion | Promoting one-off patterns as rules | Require 3+ recurrences before promotion |
| Silent regression | No metrics tracking | Implement outcome classification |
| Cargo cult rules | Copying rules without understanding | Each rule must have a "why" annotation |
| Contradiction spirals | New rules conflict with old rules | Belief revision protocol |

## Integration Points

| Skill | Integration |
|-------|-------------|
| **context-engine** | Context Engine manages what the agent sees; Self-Improving Agent manages what the agent remembers |
| **agent-designer** | Agent Designer defines agent architecture; Self-Improving Agent adds the learning layer |
| **prompt-engineer-toolkit** | Prompts that degrade over time are a regression; track and test them |
| **observability-designer** | Monitor agent performance metrics alongside system metrics |

## References

- `references/feedback-loop-patterns.md` - Detailed feedback capture and analysis patterns
- `references/memory-curation-guide.md` - Step-by-step memory review and promotion procedures
- `references/meta-learning-architectures.md` - Advanced patterns for agents that learn how to learn
