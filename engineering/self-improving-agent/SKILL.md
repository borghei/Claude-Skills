---
name: self-improving-agent
description: >
  Patterns for AI agents that learn from their own execution, detect failure modes, and
  improve autonomously. Use when building agents that get better over time, managing auto-
  memory, or designing self-correcting feedback loops.
license: MIT + Commons Clause
metadata:
  version: 2.1.0
  author: borghei
  category: engineering
  domain: ai-agents
  tier: POWERFUL
  updated: 2026-06-17
  tags: [self-improvement, ai-agents, feedback-loops, auto-memory, meta-learning, memory-curation]
  frameworks: feedback-loops, memory-curation, meta-learning, performance-regression
---
# Self-Improving Agent - Autonomous Learning Patterns

Architectural patterns for AI agents that get better with use. Most agents are stateless -- they repeat mistakes because they cannot learn from their own execution. This skill closes that gap with patterns for feedback capture, memory curation, skill extraction, and regression detection. Key insight: auto-memory captures everything, but **curation** turns noise into knowledge.

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

Before capturing or promoting learnings, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Loop stage** — remember / extract / promote / review (routes the sub-skill and the whole workflow)
- [ ] **Source data** — which session logs, `MEMORY.md`, and rules dir to operate on (the subject the tools read and write)
- [ ] **Promotion bar** — min occurrences / confidence threshold for graduating a learning into an enforced rule (`--min-occurrences`; decides what is kept vs discarded)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

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

## Tools

| Tool | Purpose | Command |
|------|---------|---------|
| `pattern_extractor.py` | Extract reusable patterns from session logs | `python scripts/pattern_extractor.py --input sessions.jsonl --min-occurrences 3` |
| `memory_health_checker.py` | Audit memory for line counts, stale, and promotable entries | `python scripts/memory_health_checker.py --memory ./MEMORY.md --rules ./.claude/rules/` |
| `rule_promoter.py` | Validate and apply promotions from memory to rules | `python scripts/rule_promoter.py --memory ./MEMORY.md --list-candidates` |
| `feedback_analyzer.py` | Analyze feedback logs for success rates and opportunities | `python scripts/feedback_analyzer.py analyze` |
| `regression_detector.py` | Compare baseline vs current performance metrics | `python scripts/regression_detector.py compare` |
| `rule_manager.py` | Manage a learned rules knowledge base with CRUD | `python scripts/rule_manager.py list` |

## References

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
- Runtime agent orchestration or multi-agent coordination -- see `agent-workflow-designer` and `agent-protocol`.
- Prompt engineering, testing, or versioning of the prompts themselves -- see `prompt-engineer-toolkit`.
- Infrastructure-level observability (logging, tracing, alerting dashboards) -- see `observability-designer`.
- Initial agent architecture design, tool selection, or capability planning -- see `agent-designer`.

## Integration Points

| Skill | Integration | Data Flow |
|-------|-------------|-----------|
| **context-engine** | Controls what the agent sees per session; this skill decides what is worth remembering long-term | Promoted rules and curated memory feed context retrieval; context relevance metrics flow back for regression tracking |
| **agent-designer** | Defines the agent's architecture and capabilities; this skill layers learning infrastructure on top | Architecture constraints inform possible feedback loops; extracted skills feed back as new capabilities |
| **prompt-engineer-toolkit** | Prompts degrade as codebases evolve; this skill detects prompt regression via outcome tracking | Performance metrics flag underperforming prompts; prompt updates feed back as CLAUDE.md rule changes |
| **observability-designer** | Provides system-level metrics; this skill provides agent-behavior-level metrics | System telemetry enriches regression diagnosis; agent metrics export to observability dashboards |
| **tech-debt-tracker** | Stale rules and bloated memory are technical debt this can surface alongside code debt | Memory health metrics feed debt scoring; debt prioritization informs which stale rules to retire |
| **agent-workflow-designer** | Multi-step workflows benefit from per-step feedback capture and cross-workflow pattern extraction | Per-step outcome data flows into feedback loops; extracted optimizations update workflow definitions |
