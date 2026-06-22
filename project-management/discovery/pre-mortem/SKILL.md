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

Before running the pre-mortem, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **The thing being stress-tested** — the specific launch/build/migration that "failed 14 days after launch" (anchors the prospective-hindsight framing)
- [ ] **Failure horizon** — the date/milestone you imagine looking back from (a vague horizon produces vague risks)
- [ ] **Who's in the room** — the 4-8 participants and whether psychological safety exists (elephants only surface with candor and the right people)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Quick Start

```bash
python3 scripts/risk_categorizer.py --demo            # built-in sample (7 risks)
python3 scripts/risk_categorizer.py input.json        # categorize your risks
python3 scripts/risk_categorizer.py input.json --format json
```

Each risk needs `description`, `category` (`tiger`/`paper_tiger`/`elephant`), `evidence`, and `urgency` (`launch_blocking`/`fast_follow`/`track`) for tigers. Document the session with `assets/pre_mortem_template.md`.

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
