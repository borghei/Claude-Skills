---
name: cs-onboard
description: Structured C-suite onboarding through a founder interview that captures company context across 7 dimensions. Generates a persistent company context file used by all C-level advisory skills. Includes quarterly refresh protocol, context quality scoring, and graceful handling of missing information. Use when setting up advisory context for the first time, refreshing stale company context, or onboarding a new executive.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: c-level
  domain: orchestration
  tier: POWERFUL
  updated: 2026-03-09
  frameworks: founder-interview, context-capture, quarterly-refresh
---

# C-Suite Onboarding

**Tier:** POWERFUL
**Category:** C-Level Advisory
**Tags:** onboarding, company context, founder interview, advisor setup, context capture, executive onboarding

## Overview

C-Suite Onboarding captures the company context that powers every C-level advisory skill. One structured conversation produces a persistent context file that transforms generic advice into specific, situationally-aware guidance. Without context, advisory skills give textbook answers. With context, they give your-company answers.

---

## Commands

| Command | Duration | Purpose |
|---------|----------|---------|
| `/cs:setup` | 45 minutes | Full onboarding interview across 7 dimensions |
| `/cs:update` | 15 minutes | Quarterly refresh -- what changed since last capture |
| `/cs:score` | 5 minutes | Assess context completeness and freshness |

---

## Interview Principles

This is a conversation, not a form. Follow these rules:

1. **One question at a time.** Never list multiple questions.
2. **Follow threads.** When something interesting surfaces, go deeper before moving on.
3. **Reflect back.** "So the real issue sounds like X -- is that right?"
4. **Watch for what they skip.** Avoidance signals the most important areas.
5. **Never read from a list.** Use the framework as a map, not a script.
6. **Earn the hard questions.** Start easy, build trust, then ask about weaknesses and fears.

**Opening line:**
> "Tell me about the company in your own words -- what are you building and why does it matter?"

Then let the conversation flow naturally across the 7 dimensions.

---

## The 7 Interview Dimensions

### Dimension 1: Company Identity

**What to capture:** What they do, who it is for, the real founding "why," one-sentence pitch, non-negotiable values.

**Key probes:**
- "If you had to explain this to your grandmother in one sentence, what would you say?"
- "What is a value you would fire someone over violating?"
- "What do you refuse to compromise on, even if it costs you?"

**Red flags:**
- Values that sound like marketing copy ("we empower synergies")
- Cannot articulate the founding "why" beyond "I saw a market opportunity"
- Mission statement that could apply to any company in the industry

### Dimension 2: Stage & Scale

**What to capture:** Headcount (FT vs contractors), revenue range, runway, stage label, what broke in the last 90 days.

**Key probes:**
- "If you had to label your stage -- still finding PMF, scaling what works, or optimizing -- which is it?"
- "What broke in the last 90 days that you did not expect?"
- "What is the one metric you check every morning?"

**Stage Definitions:**

| Stage | Signal | Typical Challenges |
|-------|--------|-------------------|
| Pre-PMF | <$500K ARR, pivoting, searching | Finding the right customer/problem/solution fit |
| Early PMF | $500K-$2M ARR, repeatable sales | Hiring, process, not breaking what works |
| Scaling | $2M-$10M ARR, growth machine building | Middle management, culture preservation, unit economics |
| Optimizing | $10M+ ARR, efficiency focus | Innovation stagnation, org complexity, market defense |

### Dimension 3: Founder Profile

**What to capture:** Self-identified superpower, acknowledged blind spots, archetype, what actually keeps them up at night.

**Key probes:**
- "What would your co-founder (or closest advisor) say you should stop doing?"
- "When things go wrong, what is your instinctive first reaction?"
- "What part of running this company do you secretly dislike?"

**Founder Archetypes:**

| Archetype | Strength | Blind Spot | Advisory Focus |
|-----------|----------|-----------|----------------|
| Product | Deep user empathy, product vision | Sales, go-to-market, delegation | Revenue strategy, hiring |
| Technical | Engineering excellence, technical moats | Business model, communication | GTM, storytelling, team |
| Sales | Revenue generation, relationships | Product depth, technical debt | Product strategy, engineering |
| Operator | Execution, processes, efficiency | Vision, innovation, risk-taking | Strategy, long-term planning |

**Red flags:**
- No acknowledged blind spots
- Weakness framed as strength ("I'm too much of a perfectionist")
- Co-founder dynamics described as "fine" with no specifics

### Dimension 4: Team & Culture

**What to capture:** Team described in 3 words, last real conflict and how it was resolved, which values are real vs aspirational, strongest and weakest leader.

**Key probes:**
- "Which of your stated values is most real? Which is a poster on the wall?"
- "Tell me about the last real disagreement in the leadership team."
- "Who is the one person you cannot afford to lose, and why?"

**Red flags:**
- "We have no conflict" -- every healthy team has conflict
- Cannot name a weak leader -- either lying or not paying attention
- Culture described only in positive terms with no self-awareness

### Dimension 5: Market & Competition

**What to capture:** Who is winning and why (honest version), real unfair advantage, the competitive move that could hurt them.

**Key probes:**
- "What is your real unfair advantage -- not the investor pitch version?"
- "If your best competitor had unlimited funding, what would they do that scares you?"
- "What do your competitors do better than you? Be honest."

**Red flags:**
- "We have no real competition" -- you always have competition, even if it is the status quo
- Unfair advantage is a feature that can be copied in 6 months
- No awareness of competitor strategy

### Dimension 6: Current Challenges

**What to capture:** Priority stack-rank across product/growth/people/money/operations, the decision they have been avoiding, the "one extra day" answer.

**Key probes:**
- "If you had one extra day per week, what would you spend it on?" (Reveals true priority)
- "What is the decision you have been putting off for weeks?"
- "Rank these: product, growth, people, money, operations. What is number 1 right now?"

**The "avoided decision" is often the most valuable insight.** Common avoided decisions:
- Firing an underperformer who is well-liked
- Pivoting away from a product that is not working
- Having an honest conversation with a co-founder
- Raising prices
- Cutting a feature or initiative

### Dimension 7: Goals & Ambition

**What to capture:** 12-month target (specific and measurable), 36-month target (directional), exit vs build-forever orientation, personal success definition.

**Key probes:**
- "What does 12 months from now look like if everything goes right?"
- "What does success look like for you personally -- separate from the company?"
- "Are you building to sell, building forever, or haven't decided?"

**Red flags:**
- 12-month target that is vague ("grow a lot")
- Personal and company goals completely disconnected
- Exit orientation that conflicts with stated mission

---

## Context Output Structure

After the interview, generate the context file at `~/.claude/company-context.md`:

```markdown
# Company Context
**Last updated:** [Date]
**Freshness:** Fresh (< 90 days)
**Completeness:** [X/7 dimensions captured]
**Interviewed:** [Founder name and role]

## 1. Company Identity
**What we do:** [One sentence]
**Who it's for:** [Target customer]
**Why it matters:** [Founding motivation -- the real version]
**One-line pitch:** [Elevator pitch]
**Non-negotiable values:** [Values they would fire over]

## 2. Stage & Scale
**Stage:** [Pre-PMF / Early PMF / Scaling / Optimizing]
**Headcount:** [X FT + Y contractors]
**Revenue:** [$X ARR / MRR]
**Runway:** [X months at current burn]
**Morning metric:** [What they check first]
**Recent break:** [What broke in last 90 days]

## 3. Founder Profile
**Archetype:** [Product / Technical / Sales / Operator]
**Superpower:** [Self-identified strength]
**Blind spot:** [Acknowledged weakness]
**Up-at-night:** [Current anxiety]
**Co-founder dynamic:** [Healthy / Strained / Solo]

## 4. Team & Culture
**Team in 3 words:** [Their words]
**Real values:** [Values that are actually lived]
**Aspirational values:** [Values that are work-in-progress]
**Key person risk:** [Who they cannot lose]
**Weakest link:** [Leadership gap]
**Last conflict:** [What happened and how resolved]

## 5. Market & Competition
**Winning competitor:** [Who and why]
**Real unfair advantage:** [Not the investor version]
**Kill-shot risk:** [Competitive move that could hurt them]
**Market position:** [Leader / Challenger / Niche / Emerging]

## 6. Current Challenges
**Priority #1:** [Top challenge area]
**Priority stack:** [Rank of product/growth/people/money/ops]
**Avoided decision:** [What they have been putting off]
**One-extra-day:** [What they would spend time on]

## 7. Goals & Ambition
**12-month target:** [Specific, measurable]
**36-month target:** [Directional]
**Orientation:** [Build to sell / Build forever / Undecided]
**Personal success:** [What success means for the founder personally]

## Notes
[Observations, inferred patterns, things to watch]
[CONTEXT UPDATE entries from subsequent sessions]
```

**Rules:**
- Write `[not captured]` for unknowns -- never leave blank
- Use their actual words when possible, not corporate paraphrasing
- Note confidence level for inferred information
- Never silently modify -- always confirm before updating

---

## Context Quality Scoring

### Completeness Score

| Dimensions Captured | Score | Label |
|--------------------|-------|-------|
| 7/7 | 100% | Complete |
| 5-6/7 | 70-85% | Good (identify gaps) |
| 3-4/7 | 40-55% | Partial (schedule follow-up) |
| 1-2/7 | 15-25% | Minimal (re-interview needed) |

### Freshness Score

| Age | Score | Label | Action |
|-----|-------|-------|--------|
| < 30 days | Fresh | High confidence | Use directly |
| 30-90 days | Aging | Medium confidence | Use, flag what may have changed |
| 90-180 days | Stale | Low confidence | Prompt for /cs:update |
| > 180 days | Expired | Very low confidence | Re-interview recommended |

### Quality Signals

| Signal | Confidence Impact |
|--------|------------------|
| Full interview completed | +High |
| Update done within 90 days | +Medium |
| Key fields populated with specifics | +High |
| Fields contain vague/generic answers | -Medium |
| Financial fields missing | -High (for CFO/CEO skills) |
| "Not captured" in 3+ fields | -High |

---

## Quarterly Refresh Protocol (`/cs:update`)

**Trigger:** Every 90 days or after a major event (fundraise, reorg, pivot, key hire/departure).

**Opening:** "It has been [X time] since we captured your company context. Let's do a quick refresh. What has changed?"

**Walk each dimension with a single "what changed?" question:**

| Dimension | Refresh Question |
|-----------|-----------------|
| Identity | "Still the same mission, or has it shifted?" |
| Stage & Scale | "Team size, revenue, and runway now?" |
| Founder | "Has your role changed? What is stretching you?" |
| Team | "Any leadership changes? New key players?" |
| Market | "Any competitive surprises? Market shifts?" |
| Challenges | "What is the #1 problem now vs 90 days ago?" |
| Goals | "Still on track for the 12-month target?" |

**After refresh:**
- Update relevant sections in context file
- Update `Last updated` timestamp
- Reset freshness to `Fresh`
- Note what changed in the Notes section

---

## Context Enrichment During Sessions

During advisory conversations, new information surfaces. Capture it without disrupting flow.

**Triggers for enrichment:**
- New metric or number shared
- Key person mentioned for the first time
- Priority shift expressed
- New constraint or risk surfaces
- Timeline or deadline revealed

**Protocol:**
1. Note internally during conversation
2. At session end: "I picked up a few things that would be useful to add to your context. Want me to update the file?"
3. If yes: append to relevant section, update timestamp
4. If no: respect the decision

**Never silently modify the context file.** Always confirm before changes.

---

## Privacy Rules

### Never Send Externally
- Specific revenue or burn rate figures
- Customer names (unless publicly known)
- Employee names (unless publicly known)
- Investor names (unless publicly announced)
- Specific runway months
- Watch list contents
- Avoided decisions

### Safe to Use Externally (Anonymized)
- Stage label (seed, Series A, etc.)
- Team size ranges (1-10, 10-50, 50-200+)
- Industry vertical
- Challenge category (not specifics)
- Market position descriptor

### Before Any External API Call
- Numbers become ranges or stage-relative descriptors
- Names become roles ("the CTO" not "Sarah")
- Revenue becomes stage labels ("early revenue" not "$800K ARR")
- Customers become "Customer A, B, C"

---

## Missing Context Handling

Handle gracefully -- never block the conversation.

| Missing | Approach |
|---------|----------|
| Stage | "Just to calibrate -- are you still finding PMF or scaling what works?" |
| Financials | Use stage + team size to infer. Note the inference. |
| Founder profile | Infer from conversation style. Mark as inferred. |
| Multiple founders | Context reflects interviewee. Note co-founder perspective may differ. |
| Recent context | "It's been a while since your last update. Should I assume things are roughly the same, or has something big changed?" |

---

## Integration with C-Suite Skills

The context file is loaded by every C-level advisory skill:

| Skill | Uses Context For |
|-------|-----------------|
| **ceo-advisor** | Strategic recommendations calibrated to stage and challenges |
| **cfo-advisor** | Financial guidance calibrated to runway and revenue |
| **cto-advisor** | Technical strategy calibrated to team and architecture |
| **coo-advisor** | Operations advice calibrated to scale and processes |
| **cmo-advisor** | Marketing strategy calibrated to stage and market position |
| **internal-narrative** | Narrative construction based on company truth |
| **scenario-war-room** | Risk variables calibrated to actual threats |

---

## Related Skills

| Skill | Use When |
|-------|----------|
| **ceo-advisor** | Using context for strategic decisions |
| **internal-narrative** | Building narratives from the captured context |
| **scenario-war-room** | Modeling risks based on company context |
| **context-engine** | Technical implementation of context management for AI agents |

---

## Troubleshooting

| Problem | Likely Cause | Resolution |
|---------|-------------|------------|
| Founder gives vague, marketing-speak answers | Interview not building trust; questions too formal | Reset with a personal question; follow a thread they care about; use reflection ("So what you're really saying is...") |
| Key dimensions left as "[not captured]" after interview | Founder avoided topic or interview ran out of time | Note which dimensions were skipped (avoidance signals importance); schedule targeted follow-up for missing areas |
| Context file feels generic, could apply to any company | Interviewer used the framework as a script, not a map | Re-interview with focus on specifics: names, numbers, stories; capture their actual words, not paraphrases |
| Advisory skills still giving textbook answers despite context | Context file too sparse or stale (>90 days) | Run /cs:score to assess completeness and freshness; schedule /cs:update if freshness is Stale or Expired |
| Quarterly refresh takes too long or feels redundant | Refresh covering all 7 dimensions instead of focusing on changes | Lead with "What changed?" per dimension; skip unchanged areas quickly; target 15 minutes total |
| Multiple founders give conflicting context | Different perspectives on stage, challenges, or priorities | Note the conflict explicitly in context file; mark which founder provided which data; flag for resolution |
| Context file modified without founder approval | AI agent or team member updated context silently | Enforce "never silently modify" rule; require explicit founder confirmation before any context update |

---

## Success Criteria

- Context completeness score reaches 7/7 dimensions within first session or first follow-up
- Context freshness maintained at "Fresh" (< 90 days old) through quarterly refresh protocol
- Advisory skills produce company-specific (not generic) recommendations when context is loaded
- Founder reports that AI advisory conversations feel "like talking to someone who knows my business"
- Time to complete full onboarding interview under 45 minutes
- Time to complete quarterly refresh under 15 minutes
- Zero instances of context file modified without founder approval

---

## Scope & Limitations

**In scope:** Structured founder interview across 7 dimensions (identity, stage, founder profile, team/culture, market/competition, challenges, goals), context file generation and maintenance, quarterly refresh protocol, context quality scoring (completeness and freshness), context enrichment during advisory sessions, privacy rules for external data handling, and missing context graceful handling.

**Out of scope:** Company financial modeling (use cfo-advisor), competitive intelligence gathering (use competitive-intel), team assessment or 360 reviews (use hr-operations/), product analytics (use cpo-advisor), and automated context capture from external data sources. This skill captures context through conversation, not data integration.

**Limitations:** Context quality depends entirely on founder candor; evasive or aspirational answers reduce advisory effectiveness. Single-founder interviews may miss co-founder perspectives. Context is a point-in-time snapshot; rapid company changes (pivot, reorg, fundraise) can make context stale before the 90-day refresh. Privacy rules prevent sharing specific context externally, which limits integration with external tools.

---

## Integration Points

- **ceo-advisor** -- Strategic recommendations calibrated to company stage, challenges, and founder archetype
- **cfo-advisor** -- Financial guidance calibrated to runway, revenue range, and growth stage
- **cto-advisor** -- Technical strategy calibrated to team size, architecture maturity, and founder technical depth
- **coo-advisor** -- Operations advice calibrated to scale, process maturity, and headcount
- **cmo-advisor** -- Marketing strategy calibrated to stage, market position, and competitive landscape
- **internal-narrative** -- Narrative construction uses company identity, values, and founder voice from context
- **scenario-war-room** -- Risk variables calibrated to actual competitive threats and company vulnerabilities
