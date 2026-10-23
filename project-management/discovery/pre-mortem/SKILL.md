---
name: pre-mortem
description: >
  Pre-mortem risk analysis expert that classifies risks as Tigers, Paper Tigers,
  and Elephants to surface launch-blocking issues before they happen.
license: MIT + Commons Clause
metadata:
  version: 1.0.1
  author: borghei
  category: project-management
  domain: product-discovery
  updated: 2026-06-15
  python-tools: risk_categorizer.py
  tech-stack: pre-mortem, risk-analysis, gary-klein, prospective-hindsight
  tags:
    - pre-mortem
    - risk-analysis
    - launch-readiness
    - discovery
---
# Pre-Mortem Risk Analysis Expert

## Overview

A pre-mortem is a prospective hindsight exercise: imagine that your product has launched and failed, then work backward to identify why. This skill uses the Tiger / Paper Tiger / Elephant classification to categorize risks by type and urgency, ensuring launch-blocking issues are addressed before launch while avoiding wasted effort on unlikely risks.

## Core Capabilities

- **Prospective hindsight framing** — "It is 14 days after launch, and we failed. Why?" surfaces specific, honest risks.
- **Tiger / Paper Tiger / Elephant classification** — separate real evidenced risks (Tigers) from anxiety (Paper Tigers) and unspoken concerns (Elephants).
- **Urgency triage** — tag each Tiger Launch-Blocking, Fast-Follow, or Track with owner and decision date.
- **6-phase facilitation** — scene-setting, silent generation, cluster, classify, mitigate, address elephants in 60-90 minutes.
- **Automated categorization** — `risk_categorizer.py` summarizes distribution and flags elephants needing escalation.

## When to Use

- Before committing significant resources to build (post-ideation, post-validation).
- Before a major launch, migration, or architectural change.
- When the team has "a bad feeling" they cannot articulate.
- When stakeholder confidence is high and you need to stress-test it.

## Clarify First

Before running the pre-mortem, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **The thing being stress-tested:** the specific launch/build/migration that "failed 14 days after launch" (anchors the prospective-hindsight framing).
- **Failure horizon:** the date/milestone you imagine looking back from (a vague horizon produces vague risks).
- **Who's in the room:** the 4-8 participants and whether psychological safety exists (elephants only surface with candor and the right people).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Quick Start

```bash
python3 scripts/risk_categorizer.py --demo            # built-in sample (7 risks)
python3 scripts/risk_categorizer.py input.json        # categorize your risks
python3 scripts/risk_categorizer.py input.json --format json
```

Each risk needs `description`, `category` (`tiger`/`paper_tiger`/`elephant`), `evidence`, and `urgency` (`launch_blocking`/`fast_follow`/`track`) for tigers. Document the session with `assets/pre_mortem_template.md`.

## Anti-Patterns

### Mitigating Paper Tigers
**Mistake:** "AWS regional outage on launch day" is classed as a Tiger and gets weeks of redundancy work, with no evidence that it is likely.
**Why it happens:** A frightening consequence feels like a high probability.
**Instead:** For every Tiger, write the `evidence` that it could actually happen. A described consequence alone does not count. With no evidence, reclassify it as `paper_tiger` and cover it with a standard runbook.

### Risks too vague to act on
**Mistake:** The list holds "stakeholder issues", "scope creep" and "technical risk".
**Why it happens:** Generic labels are safe to say aloud and need no evidence.
**Instead:** Describe each risk as a concrete failure scenario in 1-2 sentences, such as "the CRO blocks launch on Day -7 because the enterprise SKU was cut". Translate worries ("the design feels weak") into a measurable consequence, or drop them.

### Running the pre-mortem too late
**Mistake:** The session happens a week before launch and surfaces a Tiger that needs four weeks of work. The team launches anyway.
**Why it happens:** Pre-mortems get scheduled as a launch-readiness check instead of a planning step.
**Instead:** Run the first pre-mortem at project kickoff and a second one around Day -30. For each risk, confirm it can still be mitigated in the time left.

Nine more, each with a bad and a good example: `references/red-flags.md`.

## References

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/methodology-and-tools.md](references/methodology-and-tools.md)** — the thought experiment, full Tiger/Paper Tiger/Elephant classification with examples, urgency table, the 6-phase facilitation script, `risk_categorizer.py` usage and flags, output formats, troubleshooting, success criteria, and bibliography. Read when running or scripting a session.
- **[references/pre-mortem-guide.md](references/pre-mortem-guide.md)** — Gary Klein's origin and why pre-mortems work, when (and when not) to run one, deep classification criteria across domains, the facilitation timeline, and a worked SaaS launch example. Read for the theory and a full example.
- **[references/red-flags.md](references/red-flags.md)** — 12 anti-patterns (mitigation theater, groupthink, vague risks, over-mitigated elephants, late pre-mortems, missing owners) with bad/good examples and one-line checks. Read before sharing pre-mortem output.

## Scope & Limitations

**In Scope:** prospective hindsight using the "14 days after launch failure" framing; Tiger / Paper Tiger / Elephant classification with urgency levels; automated elephant escalation detection; risk registry generation; facilitation methodology for in-person and remote teams.

**Out of Scope:** ongoing risk management and tracking (see `senior-pm/risk_matrix_analyzer.py`); quantitative probability/impact scoring (`senior-pm/`); product discovery and hypothesis validation (`brainstorm-experiments/`); technical architecture risk assessment (`engineering/` skills).

**Important Caveats:** most effective with 4-8 participants; the elephant escalation keyword check is a heuristic; pre-mortems complement, not replace, assumption mapping (`identify-assumptions/`); psychological safety is a prerequisite.

## Integration Points

| Integration | Direction | Description |
|------------|-----------|-------------|
| `brainstorm-ideas/` | Receives from | Ideas that passed initial validation are subject to pre-mortem before full build |
| `brainstorm-experiments/` | Receives from | Post-experiment, pre-mortem stress-tests the build decision |
| `identify-assumptions/` | Bidirectional | Launch-blocking tigers may surface new assumptions; elephants often reveal avoided assumptions |
| `execution/create-prd/` | Feeds into | Tiger mitigations become PRD risk sections and assumption validation plans |
| `senior-pm/` | Feeds into | Launch-blocking tigers escalate into portfolio risk registers via `risk_matrix_analyzer.py` |
| `scrum-master/` | Feeds into | Fast-follow tigers become sprint backlog items with mitigation-focused stories |
