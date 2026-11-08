---
name: self-improving-agent
description: >
  Curates agent memory and turns repeated lessons into reviewed rules: memory health checks,
  pattern extraction, feedback and regression analysis. Use when managing auto-memory or
  building agents that learn from their own sessions.
license: MIT + Commons Clause
metadata:
  version: 2.2.0
  author: borghei
  category: engineering
  domain: ai-agents
  tier: POWERFUL
  updated: 2026-11-08
  tags: [self-improvement, ai-agents, feedback-loops, auto-memory, meta-learning, memory-curation]
  frameworks: feedback-loops, memory-curation, meta-learning, performance-regression
---
# Self-Improving Agent

The agent captures what went wrong or right in a session, curates it in memory, and proposes promoting a lesson into a permanent rule only when it has recurred and a person has approved it. Rules compound: a wrong rule repeats its mistake in every later session, so promotion is a reviewed change, never an automatic one.

## Core Capabilities

- **Memory curation** — a layered memory stack (CLAUDE.md → MEMORY.md → session), review protocol, and promotion criteria for graduating learnings into enforced rules.
- **Feedback loops** — outcome classification, signal extraction, and a capture template that turn every task result into a structured learning.
- **Regression detection** — metrics, thresholds, and a response protocol that flags performance degradation within a few sessions.
- **Skill extraction** — criteria and a 4-step process to graduate proven patterns into standalone skill packages.
- **Meta-learning** — adaptive capture strategy and anti-pattern detection so the agent learns *what* is worth learning.
- **Continuous calibration** — confidence scoring and belief revision for resolving contradictions across learned knowledge.

## When to Use

- Building agents intended to improve over time rather than stay stateless.
- Managing auto-memory (MEMORY.md) and deciding what to keep, promote, or retire.
- Designing self-correcting feedback loops and regression alarms for agent behavior.
- Graduating recurring solutions into reusable skill packages.

## Clarify First

Before capturing or promoting learnings, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Loop stage:** remember / extract / promote / review (routes the sub-skill and the whole workflow).
- **Source data:** which session logs, `MEMORY.md`, and rules dir to operate on (the subject the tools read and write).
- **Promotion bar:** min occurrences / confidence threshold for graduating a learning into an enforced rule (`--min-occurrences`; decides what is kept vs discarded).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Sub-Skills

Compound sub-skill architecture — each file in `skills/` handles one step of the improvement loop:

| Sub-Skill | File | Purpose |
|-----------|------|---------|
| **Remember** | `skills/remember.md` | Capture errors and learnings from current session |
| **Extract** | `skills/extract.md` | Extract reusable patterns from completed work |
| **Promote** | `skills/promote.md` | Graduate proven patterns to permanent rules |
| **Review** | `skills/review.md` | Audit memory health, prune stale entries |
| **Status** | `skills/status.md` | Dashboard showing memory state and learning progress |

Flow: `Remember → Extract → Promote → Review`, with `Status` providing visibility back into the cycle.

## Workflow

1. **Check memory health:** `memory_health_checker.py --memory <MEMORY.md>`. It reads both layouts: `## ` section entries, and index files whose lines point at topic files (Claude Code auto-memory), where it reads each topic file's frontmatter and age and flags pointers to missing files.
2. **Find recurring lessons** in session or feedback logs with `pattern_extractor.py` and `feedback_analyzer.py patterns`.
3. **Propose a promotion:** `rule_promoter.py --entry-title ... --dry-run` prints the rule text and whether it meets the bar (recurrence, confidence).
4. **Get approval:** show the user the proposed rule and where it will land (CLAUDE.md or `.claude/rules/`), and apply with `--apply` only after an explicit yes.
5. **Watch for regressions** after a rule change with `regression_detector.py compare`; roll the rule back if first-attempt success or corrections get worse.
6. Done when memory has no broken pointers or over-limit files, every promoted rule was approved, and the regression check after the change is clean.

## Quick Start

```bash
# from engineering/self-improving-agent/
python3 scripts/memory_health_checker.py --memory assets/memory_index/MEMORY.md   # flags one broken pointer
python3 scripts/feedback_analyzer.py analyze --input assets/sample_feedback.jsonl
python3 scripts/regression_detector.py compare --input assets/sample_metrics.json  # REGRESSION DETECTED after a rule change
```

## Tools Overview

| Tool | Purpose | Example |
|------|---------|---------|
| `pattern_extractor.py` | Recurring patterns in session logs (JSONL) | `python3 scripts/pattern_extractor.py --input sessions.jsonl --min-occurrences 3` |
| `memory_health_checker.py` | Line limits, stale and duplicate entries, broken topic pointers, promotion candidates | `python3 scripts/memory_health_checker.py --memory ./MEMORY.md --rules ./.claude/rules/` |
| `rule_promoter.py` | Validate and (after approval) apply a promotion from `## ` section memory to rules | `python3 scripts/rule_promoter.py --memory ./MEMORY.md --list-candidates` |
| `feedback_analyzer.py` | Success rates, corrections, tool errors and opportunities from a feedback log | `python3 scripts/feedback_analyzer.py analyze --input feedback.jsonl` |
| `regression_detector.py` | Baseline vs current session metrics around a rule or memory change | `python3 scripts/regression_detector.py compare --input metrics.json` |
| `rule_manager.py` | CRUD over a JSON rules knowledge base | `python3 scripts/rule_manager.py --db rules_kb.json list` |

**Exit codes:** 0 report produced; 2 unusable input (missing or unreadable file, no entries, no subcommand). A memory path that does not exist is an error, not a "stateless" result. `rule_promoter.py` handles section-style memory only; for an index-style MEMORY.md it says so and the promotion is done by hand.

## Anti-Patterns

**Mistake:** Promoting a lesson into CLAUDE.md or rules without asking.
**Why it matters:** Rules apply to every later session; a rule learned from one bad day keeps steering the agent wrong long after.
**Instead:** Show the dry-run rule text and target, and apply only after the user says yes.

**Mistake:** Promoting after a single occurrence.
**Why it matters:** One-off fixes are often context-specific; as rules they misfire elsewhere.
**Instead:** Wait for the recurrence threshold (3 by default) or an explicit user instruction.

**Mistake:** Letting memory grow without curation.
**Why it matters:** Over-limit or duplicate memory crowds the context window and buries the lessons that matter.
**Instead:** Run the health check on a schedule, consolidate duplicates, and delete pointers to topics that no longer hold.

## Reference Documentation

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/memory-curation-guide.md](references/memory-curation-guide.md)** — the memory stack, review protocol, promotion criteria/targets, the Weekly Memory Health Check workflow, and the continuous-calibration (confidence scoring + belief revision) machinery. Read when curating MEMORY.md or promoting learnings to rules.
- **[references/feedback-loop-patterns.md](references/feedback-loop-patterns.md)** — the core improvement-loop architecture and maturity levels, outcome classification + signal extraction, the capture template, regression metrics/response, the post-session and regression-investigation workflows, common pitfalls, troubleshooting, and the success-criteria bar. Read when designing feedback capture or diagnosing a regression.
- **[references/meta-learning-architectures.md](references/meta-learning-architectures.md)** — skill-extraction criteria and process, the adaptive capture strategy, and anti-pattern detection. Read when the agent should adapt its own learning strategy or extract a proven pattern into a skill.
- **[references/self-improvement-methodology.md](references/self-improvement-methodology.md)** — the five layers of agent learning, the confidence-scoring model, the promotion decision tree, the memory-curation checklist, anti-patterns, and the metrics/thresholds table. Read for the end-to-end methodology overview.

## Scope & Limitations

**This skill covers:**
- Architectural patterns for building agents that learn from execution history and user feedback.
- Memory lifecycle management: capture, curation, promotion, and retirement of learned knowledge.
- Performance regression detection frameworks and response protocols for agent systems.
- Skill extraction methodology for graduating proven patterns into reusable, standalone packages.

**This skill does NOT cover:**
- Runtime agent orchestration or multi-agent coordination -- see `engineering/agent-workflow-designer`.
- Prompt engineering, testing, or versioning of the prompts themselves -- see `engineering/prompt-engineer-toolkit`.
- Infrastructure-level observability (logging, tracing, alerting dashboards) -- see `engineering/observability-designer`.
- Initial agent architecture design, tool selection, or capability planning -- see `engineering/agent-designer`.

## Files

| File | Purpose |
|------|---------|
| `skills/*.md` | Sub-skills: remember, extract, promote, review, status |
| `scripts/*.py` | Six stdlib CLIs (see Tools Overview) |
| `assets/memory_index/` | Index-style MEMORY.md with two topic files and one broken pointer |
| `assets/sample_feedback.jsonl` | Twelve feedback entries with a recurring npm/pnpm correction |
| `assets/sample_metrics.json` | Baseline and current sessions around a rule change (regression) |
