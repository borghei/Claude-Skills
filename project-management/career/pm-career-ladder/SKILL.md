---
name: pm-career-ladder
description: >
  PM career ladder rubrics from APM through VP/CPO across product sense,
  execution, leadership, strategy, and communication. Includes gap analysis,
  growth planning, and promotion packet templates.
license: MIT + Commons Clause
metadata:
  version: 1.0.1
  author: borghei
  category: project-management
  domain: pm-career
  updated: 2026-06-15
  tech-stack: pm-rubric, promotion-packet, growth-plan, career-ladder
  tags:
    - career-ladder
    - pm-levels
    - growth-planning
    - promotion
    - pm-career
---
# PM Career Ladder Expert

## Overview

A consolidated, opinionated PM career ladder for ICs from APM to Group PM and managers from Director to VP/CPO. The ladder spans five capability dimensions -- product sense, execution, leadership, strategy, and communication -- with explicit behaviors per level. It bundles a level-by-level rubric, a gap-analysis worksheet, a 6-month growth plan template, and a promotion packet template. A level is reached when a PM operates at that bar **consistently across all five dimensions for >=2 quarters**, not the high-water mark of a single quarter.

## Core Capabilities

- **Level rubric** -- five dimensions x seven levels (APM, PM, Sr PM, Group PM, Director, VP/CPO) with observable behaviors and promotion signals per level
- **Gap analysis** -- self-score vs. independent manager-score, surface calibration gaps, prioritize 2-3 dimensions to develop
- **Growth planning** -- translate gaps into a 6-month plan of experiments, evidence, and manager support
- **Promo packet** -- scope statement, quantified impact, rubric mapping, partner quotes, growth narrative

## When to Use

- **Mid-cycle self-assessment** -- Calibrate where you are vs. where you want to be in 6-12 months.
- **Growth planning** -- Translate the gap into a concrete 6-month plan with experiments and evidence.
- **Promotion preparation** -- Build a promo packet that lines up your impact against the rubric for the next level.
- **Manager 1:1s** -- Bring the rubric to your 1:1 to make growth conversations concrete instead of vibes-based.
- **Hiring calibration** -- As a hiring manager, use the rubric to level a candidate's interview signal.

**When NOT to use:** interview prep (use `pm-interview-prep/`), new-role onboarding (use `pm-onboarding/`), 1:1 templates (use `pm-1on1s/`).

## Clarify First

Before generating the assessment or plan, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Current and target level:** APM, PM, Sr PM, Group PM, Director, or VP/CPO (sets which rubric bar to score against).
- **Artifact:** gap analysis, 6-month growth plan, or promo packet (each uses a different template and depth).
- **Track:** IC ladder (APM-GPM) vs management ladder (Director-VP/CPO) (shifts which of the 5 dimensions dominate).
- **Evidence base:** quantified impact + partner quotes on hand (a promo packet without evidence is just a self-claim).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Quick Start

1. Self-score the 5x6 rubric for your current and next level; have your manager score independently.
2. Pick 2-3 dimensions where you are below bar.
3. Write a 6-month growth plan (experiments + evidence) and review monthly in your 1:1.
4. Maintain a quarterly written impact summary; assemble the promo packet by the 3-month mark of the cycle.

See `references/ladder-playbook.md` for the full ladder table, rubric detail, gap-analysis steps, growth-plan and promo-packet structures, and troubleshooting.

## Anti-Patterns

### Promo packet with no scope evidence
**Mistake:** The packet lists launches ("shipped feature X") and never shows that the PM's scope grew.
**Why it happens:** Shipped features are easy to list, and scope change is harder to describe.
**Instead:** State the scope shift in the first paragraph, before any feature list. Promotion needs consistent next-level work across all five dimensions for at least two quarters. One strong deliverable is not enough.

### "Influence" with no decision behind it
**Mistake:** The packet says "influenced", "drove alignment" and "championed" but cannot point to a decision that turned on the PM's input.
**Why it happens:** Influence is real but hard to trace, so people describe it in general terms.
**Instead:** Rewrite every such claim as "decision made on [date] in [forum] based on [my artifact]". If you can't fill in the blanks, cut the claim. Back it with a partner quote where you have one.

### Growth plan that changes nothing
**Mistake:** The 6-month plan says "read more product books" and "improve communication."
**Why it happens:** Generic goals are easy to agree on and hard to fail.
**Instead:** For each of the 2-3 gap dimensions, name a behavior an observer could see change, such as a meeting you would not have run before or a document you would not have written. Review it monthly in your 1:1 and set a target promo cycle date.

Nine more, each with a bad and a good example: `references/red-flags.md`.

## References

- **[references/ladder-playbook.md](references/ladder-playbook.md)** — the full 5x6 ladder table, per-level rubric behaviors and promotion signals, gap-analysis process, 6-month growth plan, promo packet structure, workflow, troubleshooting, and success criteria. Read when scoring yourself or building a plan/packet.
- **[references/ladder-rubric-detail.md](references/ladder-rubric-detail.md)** — each dimension expanded across levels with "looks like" behaviors, anti-patterns, and promotion signals. Read when you need fine-grained behavioral detail for one dimension.
- **[references/red-flags.md](references/red-flags.md)** — common ways ladder self-assessments and promo packets go wrong, with fixes. Read before submitting a packet or a self-score.
- `assets/gap_analysis.md` — self-scoring + manager-scoring worksheet.
- `assets/growth_plan.md` — 6-month growth plan template.
- `assets/promo_packet.md` — promotion packet template.

External: Square's published PM ladder; Wodtke, C. *Radical Focus*.

## Scope & Limitations

**In scope:** IC ladder (APM-GPM) and management ladder (Director-VP/CPO); gap analysis, growth planning, promo packet templates; self-scoring rubric across 5 dimensions; conversation prompts for managers and skip-levels.

**Out of scope:** compensation/salary calibration (use levels.fyi, Pave, or comp bands); interviewer-side hiring rubrics; job-change/negotiation strategy; company-specific ladders (this is a consolidated industry baseline).

**Caveats:** Every company calibrates differently — a startup "Sr PM" != a 5,000-person "Sr PM"; adjust for context. Promotion is part meritocratic, part political; the rubric covers the meritocratic half. Growth is non-linear — continuous investment matters more than even-paced advancement.

## Integration Points

| Integration | Direction | What Flows |
|-------------|-----------|------------|
| `pm-interview-prep/` | Bidirectional | The rubric calibrates the bar for external interviews and internal calibration the same way |
| `pm-onboarding/` | Feeds into | New-role onboarding ends with the first ladder self-score |
| `pm-1on1s/` | Bidirectional | Quarterly 1:1s review ladder progress; the ladder structures the conversation |
| `senior-pm/stakeholder-mapper/` | Reuses | Promotion requires stakeholder support; the stakeholder mapper helps map the calibration room |
| `personal-productivity/weekly-review/` | Feeds into | Weekly review captures evidence that aggregates into the monthly impact summary |
