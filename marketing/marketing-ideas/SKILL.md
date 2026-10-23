---
name: marketing-ideas
description: >
  Library of 139+ proven marketing strategies organized by category, stage,
  budget, and timeline across content, SEO, paid, social, email, and growth. Use
  when brainstorming marketing ideas, planning growth strategies, or ideating
  campaigns.
license: MIT
metadata:
  version: 1.1.0
  author: borghei
  category: marketing
  domain: strategy
  updated: 2026-06-15
  tags:
    - marketing-ideas
    - growth-tactics
    - brainstorming
    - channel-strategy
---
# Marketing Ideas

139+ proven marketing strategies with implementation guidance matched to stage, budget, and goals. This file is a lean map — browse the full tactic catalog and frameworks in the references below.

## Core Capabilities

- **Curated idea selection** — match 3-5 of 92 cataloged tactics to a team's stage, budget, goal, and timeline
- **Campaign ideation** — run structured sessions that generate, score, and brief fresh ideas against constraints
- **Trend analysis** — identify emerging trends and evaluate them for relevance, risk, and brand fit before committing
- **Prioritization & briefing** — score ideas on impact/effort/alignment and produce execution-ready implementation briefs

## When to Use

- Brainstorming marketing or growth ideas for a specific stage, budget, or goal
- Planning a growth strategy and needing a curated shortlist instead of a generic dump
- Running a campaign ideation session that needs structure and scoring
- Evaluating whether to act on an emerging marketing trend

## Clarify First

What most shapes this skill's output is the team's situation, because the catalog is filtered by stage, budget, goal and timeline. Settle the inputs below before producing anything. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Stage and budget:** the cross-reference tables in `references/idea-catalog.md` and `idea_scorer.py --stage --budget` filter on these. A pre-launch team with no budget and a scaling team with paid spend share very few ideas.
- **Goal and timeline:** leads, authority, retention and awareness draw on different categories, and a team that needs results this quarter should not get ideas whose timeline runs past it.

If a marketing context document exists (the one the marketing-context skill builds), start from it and ask only about the gaps. Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Quick Start

### Get Curated Ideas for Your Situation

1. Define your stage (pre-launch, early, growth, scale)
2. Define your budget (free, low, medium, high)
3. Define your goal (leads, authority, retention, awareness)
4. Use the filtering tables in `references/idea-catalog.md` to find 3-5 matching ideas
5. For each idea: review implementation steps, expected timeline, and resource requirements

### Run a Campaign Ideation Session

1. Define the campaign objective and constraints
2. Use the Campaign Ideation Framework (`references/ideation-and-trends.md`) to generate 15-20 raw ideas
3. Score each idea on effort, impact, and alignment
4. Select the top 3-5 for execution planning
5. Build implementation briefs for each selected idea

## References

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/idea-catalog.md](references/idea-catalog.md)** — the full catalog of 92 tactics across 11 categories, plus cross-reference tables by stage, budget, timeline, and goal. Read when selecting which ideas fit a specific situation.
- **[references/ideation-and-trends.md](references/ideation-and-trends.md)** — the 4-step Campaign Ideation Framework (constraints, raw ideas, scoring, implementation brief) and the Trend Analysis Methodology (sources and evaluation). Read when running an ideation session or assessing a trend.
- **[references/playbook-and-troubleshooting.md](references/playbook-and-troubleshooting.md)** — 10 best practices, a troubleshooting table for common failure modes, and success criteria for an idea-selection cycle. Read when refining your process or diagnosing underperformance.

## Keywords

marketing ideas, growth ideas, marketing strategies, marketing tactics, campaign ideation, creative brainstorming, trend analysis, growth marketing, content marketing ideas, social media ideas, email marketing ideas, paid advertising ideas, partnership marketing, product-led growth, unconventional marketing, guerrilla marketing, viral marketing, community marketing, developer marketing

## Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `scripts/idea_scorer.py` | Score and prioritize marketing ideas by impact, effort, and alignment | `python scripts/idea_scorer.py ideas.json --stage growth --budget medium --goal leads` |
| `scripts/campaign_brief_generator.py` | Generate structured campaign briefs from parameters | `python scripts/campaign_brief_generator.py config.json --demo` |
| `scripts/trend_evaluator.py` | Evaluate marketing trends for relevance, risk, and actionability | `python scripts/trend_evaluator.py trends.json --demo` |

## Integration Points

- **Marketing Context** — Use as the foundation before brainstorming. Ideas work better when matched to ICP and positioning.
- **Content Strategy** — Use when the chosen tactic is content/SEO and a full topic plan is needed.
- **Paid Ads** — Use when the chosen tactic involves paid advertising campaigns.
- **Social Content** — Use when the chosen idea involves social media execution.
- **Cold Email** — Use when the chosen tactic is outbound email outreach.
- **Campaign Analytics** — Use to measure the performance of implemented ideas.

## Scope & Limitations

**In Scope:** 139+ marketing ideas organized by category/stage/budget/timeline, campaign ideation frameworks, idea scoring and prioritization, campaign brief generation, trend identification and evaluation, quick win identification, PLG strategy ideas.

**Out of Scope:** Detailed implementation for each idea (see channel-specific skills), budget allocation optimization (see marketing-analyst skill), execution tracking and analytics (see campaign-analytics skill), content creation (see content-creator skill).

**Limitations:** This skill provides strategy and ideas, not execution. Each idea requires a channel-specific skill for full implementation. Impact estimates (High/Medium/Low) are directional based on benchmarks; actual results depend on execution quality, market fit, and timing. Trend evaluation is subjective and should be combined with data analysis.
