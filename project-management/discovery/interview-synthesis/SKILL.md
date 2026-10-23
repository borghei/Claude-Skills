---
name: interview-synthesis
description: >
  Customer interview synthesis: raw transcripts to themed insights, an opportunity
  solution tree, and follow-up questions (Teresa Torres continuous discovery). Use
  for post-interview synthesis, opportunity mapping, and evidence gap analysis.
license: MIT + Commons Clause
metadata:
  version: 1.0.1
  author: borghei
  category: project-management
  domain: pm-discovery
  updated: 2026-06-15
  python-tools: interview_synthesizer.py
  tech-stack: customer-interviews, opportunity-solution-tree, jobs-to-be-done
  tags:
    - interview-synthesis
    - insights
    - continuous-discovery
    - opportunity-solution-tree
---
# Customer Interview Synthesis Expert

## Overview

Turn customer interview transcripts into actionable product opportunities. This skill takes raw question-and-answer transcripts and produces three artifacts: (1) themed insight clusters, (2) an opportunity solution tree mapping outcomes to opportunities and candidate solutions, and (3) a prioritized list of follow-up questions to close evidence gaps.

The synthesis approach is grounded in Teresa Torres' Continuous Discovery Habits (opportunity solution trees), Steve Portigal's interview methodology (looking for stories and contradictions), and the Jobs-To-Be-Done synthesis approach popularized by Alan Klement (situation-motivation-outcome decomposition).

## Core Capabilities

- **Snippet extraction & coding** — stories, contradictions, surprises, emotions coded by need/job/pain/gain and evidence strength
- **Theme clustering** — evidence thresholds (>=3 snippets from >=2 participants) with scannable headlines
- **Opportunity solution tree** — measurable outcome → customer-side opportunities → candidate solutions, with intact evidence trails
- **Follow-up generation** — story-prompt questions targeting weak-evidence themes and unmapped assumptions
- **Multi-format output** — markdown, JSON, mermaid, confluence, notion, linear

### When to Use

- **Post-interview synthesis** -- You have 3-20 interview transcripts and need to extract themes before they become stale.
- **Opportunity space mapping** -- Building an opportunity solution tree before committing to solutions.
- **Discovery sprint readout** -- Sharing findings with the product trio (PM, Design, Engineering) and stakeholders.
- **Evidence gap analysis** -- Identifying which assumptions still lack interview evidence and need targeted follow-ups.

### When NOT to Use

- Quantitative survey synthesis -- use a data analysis skill instead.
- Usability test debriefs -- use a UX research-specific workflow.
- Sales call analysis for win/loss -- use `business-growth/` skills.

## Clarify First

Before synthesizing, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **The transcripts:** how many (3-20) and their quality (synthesis is bounded by interview quality; thin input yields thin themes).
- **Target outcome:** the measurable outcome that becomes the root of the opportunity solution tree.
- **Evidence threshold:** what counts as a theme (default ≥3 snippets from ≥2 participants; raising/lowering it changes which clusters surface).
- **Output consumer:** markdown / mermaid / Notion / Linear (sets the `--format` and shape of the deliverable).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Quick Start

```bash
python scripts/interview_synthesizer.py --input interviews.json --format markdown --output synthesis.md
python scripts/interview_synthesizer.py --input interviews.json --format mermaid   # tree only
```

Prepare input per `assets/interview_input_template.json` (one entry per interview: participant id, role, q/a pairs). See the references for the full framework and flag reference.

## Anti-Patterns

### Synthesis that confirms the starting hypothesis
**Mistake:** Every theme matches what the PM believed before the interviews. Transcripts also mention pricing, trust or confusion, but none of it reaches the theme list.
**Why it happens:** People pattern-match toward the answer they expect, and a solo pass has nothing to force a second reading.
**Instead:** Require at least one finding that contradicts or expands the original hypothesis. Code surprises and contradictions as snippets, and have the product trio code independently before merging.

### One theme pooled across segments
**Mistake:** A theme says "users want better onboarding" but draws on admins setting up the workspace and end users in week 1 as if they were one group.
**Why it happens:** Each segment alone looks too thin to support a theme, so pooling feels like more evidence.
**Instead:** Tag every theme with the segment it applies to. If two segments share a theme, apply the evidence threshold (3 or more snippets from 2 or more participants) to each segment separately.

### Percentages from a handful of interviews
**Mistake:** "60% of users want feature X", when 3 of 5 interviewees mentioned it.
**Why it happens:** A percentage looks more rigorous in a readout than a raw count.
**Instead:** Write "X of N" for any sample under 20. Treat the theme as a candidate to survey or test quantitatively before anyone calls it a population-level finding.

Nine more, each with a bad and a good example: `references/red-flags.md`.

## References

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/synthesis-framework-and-tooling.md](references/synthesis-framework-and-tooling.md)** — the full 5-step framework (snippet extraction, coding, theme clustering, opportunity solution tree, follow-ups), end-to-end workflow, troubleshooting, success criteria, and the `interview_synthesizer.py` flag reference. Read when doing the synthesis or running the tool.
- **[references/synthesis-methodology-guide.md](references/synthesis-methodology-guide.md)** — full methodology with worked examples bundling Torres, Portigal, and Klement. Read for the deeper "why" and end-to-end playbook.
- **[references/red-flags.md](references/red-flags.md)** — concrete bad-vs-good examples of how synthesis output goes wrong and how to fix it. Read before sharing themes, a tree, or a readout.
- **[assets/interview_input_template.json](assets/interview_input_template.json)** — JSON schema for interview transcripts.
- **[assets/opportunity_tree_template.md](assets/opportunity_tree_template.md)** — editable opportunity solution tree template.

## Scope & Limitations

**In Scope:**
- Qualitative synthesis of 3-20 customer interview transcripts
- Theme clustering with evidence thresholds
- Opportunity solution tree generation (Mermaid + Markdown)
- Follow-up question generation for evidence gaps
- Multi-format output (Markdown, JSON, Mermaid, Confluence, Notion, Linear)

**Out of Scope:**
- Live interview facilitation -- this skill works on completed transcripts
- Quantitative analysis (survey statistics, click-stream data)
- Sentiment scoring via ML -- the tool uses deterministic keyword and code matching only
- Win/loss analysis -- use `business-growth/` skills
- Persona generation -- the output is opportunity-centric, not persona-centric

**Important Caveats:**
- Synthesis quality is bounded by interview quality. Garbage in, garbage out.
- The opportunity solution tree is a thinking aid, not a roadmap. Solutions still need experiment validation.
- Teresa Torres' methodology assumes continuous discovery (weekly touchpoints). One-off interview rounds produce shallower trees.

## Integration Points

| Integration | Direction | What Flows |
|-------------|-----------|------------|
| `discovery/brainstorm-experiments/` | Feeds into | Validated opportunities become hypotheses for lean experiments |
| `discovery/identify-assumptions/` | Bidirectional | Assumptions inform follow-up questions; interview evidence resolves assumptions |
| `discovery/brainstorm-ideas/` | Feeds into | Themed insights seed Product Trio ideation sessions |
| `discovery/pre-mortem/` | Feeds into | Pain themes surface candidate risks for pre-mortem analysis |
| `execution/create-prd/` | Feeds into | Top opportunities + supporting evidence populate PRD Background and Market Segments sections |
| `execution/job-stories/` | Feeds into | Klement-format job codes convert directly into When/Want/So job stories |
