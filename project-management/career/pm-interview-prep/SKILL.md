---
name: pm-interview-prep
description: >
  Structured PM interview preparation across product sense, execution, strategy,
  behavioral, and technical rounds, using CIRCLES, AARM, STAR, and the estimation
  framework. Calibrated to APM, PM, Senior PM, and Group PM rubrics.
license: MIT + Commons Clause
metadata:
  version: 1.0.1
  author: borghei
  category: project-management
  domain: pm-career
  updated: 2026-06-15
  tech-stack: pm-interviews, product-sense, execution, behavioral, frameworks
  tags:
    - pm-interviews
    - product-sense
    - circles
    - star-method
    - pm-career
---
# PM Interview Prep Expert

## Overview

PM interviews test five distinct skills, each with its own format, frameworks, and rubric: product sense, execution, strategy, behavioral, and technical. This skill organizes preparation across all five round types and calibrates expectations to the level you are interviewing for (APM, PM, Senior PM, Group PM). It bundles the most-used PM interview frameworks -- Lewis Lin's CIRCLES Method for product design, the AARM Method for improvement/metric questions, STAR for behavioral, and a 5-step estimation framework for market sizing -- plus question banks per round and structured answer templates calibrated by level.

## Core Capabilities

- **Five round types** -- product sense (design), product improvement, strategy, behavioral, technical/analytical, each with format and primary framework
- **Frameworks** -- CIRCLES, AARM, STAR (+ Reflection for senior), and 5-step estimation, with worked examples and failure modes
- **Level calibration** -- the same question scored differently for APM vs. PM vs. Senior PM vs. Group PM
- **Prep system** -- self-assessment, question banks, 8-12 behavioral story development, and structured mock-interview feedback

## When to Use

- **Preparing for PM interviews** -- You have a loop scheduled and need a structured plan to cover all rounds.
- **Mock interview prep** -- You are interviewing peers and want consistent rubrics.
- **Self-assessment** -- You want to identify your weakest interview category before investing prep time.
- **Switching levels** -- You are an IC PM moving to Senior or Senior moving to Group, and need to understand how the bar shifts.

**When NOT to use:** general career planning (use `pm-career-ladder/`); hiring as an interviewer (this is candidate-side); engineering or design interview prep (this is PM-specific).

## Clarify First

What most shapes this skill's output is the level you are interviewing for and the company running the loop. Settle the inputs below before producing anything. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Target level:** APM, PM, Senior PM and Group PM are scored differently on the same question. The level picks the questions from `references/question-bank.md` and the bar answers are judged against; Senior PM and above are expected to add Reflection to STAR.
- **Company and role:** every company has its own rubric and round mix. A loop heavy on product sense needs CIRCLES practice, a technical-PM screen needs a different plan, and the published guide or recruiter call should set the weighting.
- **Time until the loop:** a week leaves room for the two weakest round types and a few stories. A month allows the full 8-12 story set and 2-3 mocks per round type.
- **Experience to draw on:** behavioral answers are built from real projects with quantified results. Without those, the story worksheet stays empty and answers drift into vague outcomes.

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Quick Start

1. Rate yourself across the five round types (`assets/self_assessment.md`); pick your weakest two.
2. Pull level-targeted questions from `references/question-bank.md` and practice solo with the right framework, timed.
3. Run 2-3 mocks per round type using `assets/mock_feedback_form.md`.
4. Refine 8-12 behavioral stories (`assets/story_worksheet.md`) to under 5 minutes each, quantified.

See `references/round-frameworks-and-prep.md` for the full round reference, framework tables, level-calibration bars, prep workflow, and troubleshooting.

## Anti-Patterns

### Reciting the framework out loud
**Mistake:** The answer opens with "I'll use CIRCLES: Comprehend, Identify, Report..." and then walks through each letter.
**Why it happens:** Prep time goes into memorizing the acronym, so it comes out first under pressure.
**Instead:** Use the framework as hidden structure. The interviewer should feel the structure without hearing the acronym. Record a mock: if you say the framework's name, you are leaning on it too visibly.

### STAR stories with no result
**Mistake:** The behavioral answer spends minutes on Situation, Task and Action, then ends with "it went well and we learned a lot."
**Why it happens:** The action is the part you remember living through, and the numbers were never written down.
**Instead:** State the Result as a number plus a learning in every story. Build the 8-12 stories in `assets/story_worksheet.md` with the quantified result filled in first. That is where interviewers read your level.

### Success metrics with no counter-metric
**Mistake:** "I'd measure success by DAU growth," with nothing on what might break if DAU rises.
**Why it happens:** One clear metric sounds decisive in a timed answer.
**Instead:** Pair every success metric with at least one counter-metric, such as retention or NPS, and say what result would worry you. Interviewers at PM level and above expect it.

Nine more, each with a bad and a good example: `references/red-flags.md`.

## References

- **[references/round-frameworks-and-prep.md](references/round-frameworks-and-prep.md)** — the five round types, full CIRCLES/AARM/STAR/Estimation frameworks with failure modes, per-level calibration tables, prep workflow, question excerpts, troubleshooting, and success criteria. Read when preparing any round.
- **[references/framework-deep-dive.md](references/framework-deep-dive.md)** — fully worked examples for CIRCLES, AARM, STAR, and Estimation. Read when you want to see a framework executed end-to-end on a real question.
- **[references/question-bank.md](references/question-bank.md)** — 100+ questions organized by round type and level (APM/PM/SR/GPM). Read when building your practice set.
- **[references/red-flags.md](references/red-flags.md)** — common ways interview answers go wrong, with fixes. Read before mocks and the real loop.
- `assets/self_assessment.md` — pre-prep diagnostic across the five round types.
- `assets/mock_feedback_form.md` — structured feedback form for mock interviews.
- `assets/story_worksheet.md` — worksheet for the 12 canonical behavioral stories.

External: Lin, L. *Decode and Conquer* (CIRCLES); McDowell, G. & Bavaro, J. *Cracking the PM Interview*; Lin, L. *The Product Manager Interview* (AARM + 165 questions); Bock, L. *Work Rules!*

## Scope & Limitations

**In scope:** framework-based prep for all five PM round types; level calibration APM-Group PM; question banks and answer templates; behavioral story development and STAR refinement; self-assessment and mock-feedback tools.

**Out of scope:** Director/VP/CPO interviews (executive judgment, board influence, P&L — use leadership coaching); company-specific technical-PM screens (consult the role's rubric); salary negotiation/offer evaluation; resume and outreach prep (use `personal-productivity/resume/`).

**Caveats:** Frameworks are scaffolds, not scripts — interviewers down-rank verbatim recitation; internalize so the structure is invisible. Every company has its own rubric; adjust by the published guide and recruiter call. Mocking with a current PM at the target company beats any book.

## Integration Points

| Integration | Direction | What Flows |
|-------------|-----------|------------|
| `pm-career-ladder/` | Bidirectional | Use the ladder rubric to understand the level you are interviewing for |
| `pm-onboarding/` | Feeds into | Once hired, the onboarding skill takes over for first 90 days |
| `personal-productivity/resume/` | Feeds from | A clean resume with quantified impact feeds the behavioral stories |
| `discovery/brainstorm-ideas/` | Reuses | Product sense rounds reuse the same ideation discipline as Product Trio sessions |
| `execution/prioritization-frameworks/` | Reuses | RICE, ICE, and Opportunity Score reasoning shows up in CIRCLES Step 4 (Cut through) |
