---
name: product-research
description: >
  Continuous product discovery research operations — picking the method that
  fits the question, recruiting and screening participants, building interview
  guides, and scoring evidence into insights. Use when planning or running discovery.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: research-ops
  domain: product-discovery
  updated: 2026-07-21
  tags: [discovery, user-research, interviews, screener, synthesis, research-ops]
---

# Product Research

The operational layer of continuous product discovery: choosing a method that
actually answers the question asked, recruiting the right people without
poisoning the sample, running interviews that surface behaviour rather than
opinion, and converting a pile of session notes into insights with an honest
confidence attached.

## When to use this skill

- **A team is about to build something** and the evidence behind it is three
  sales anecdotes and a strongly held opinion
- **Choosing a method** — someone has asked for "a survey" or "some user
  interviews" before anyone has written down the question
- **Designing a screener** for a study where recruiting the wrong participants
  would be worse than not running it
- **Writing an interview guide** that has to be run consistently by several
  people across a dozen sessions
- **Synthesising evidence into insights** after a round of discovery, with a
  defensible confidence level on each claim
- **Standing up a continuous discovery cadence** — a repeatable weekly rhythm
  rather than one-off project research

## Inputs the skill expects

- The decision the research feeds, and who makes it
- The question in interrogative form — what you do not know, not what you want
  confirmed
- Decision reversibility — can this be undone in a sprint, or is it a one-way door
- Timeline and budget for the study
- Access to participants: existing customers, prospects, panel, or none
- Existing evidence already on hand (tickets, session recordings, sales calls)

## Clarify First

Before generating, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **The decision this research informs, and its reversibility** — a one-way door justifies weeks of evidence; a reversible change is often better answered by shipping an experiment
- [ ] **The question in interrogative form** — "do users want X" and "how do users currently accomplish X" call for completely different methods
- [ ] **Participant access** — whether you can reach real users determines whether the plan is feasible at all, and it is the constraint teams discover last
- [ ] **Timeline** — a two-day answer and a three-week answer are different studies, not the same study rushed

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Workflows

### Workflow 1 — Pick the method before anyone books a session

1. Write the question in interrogative form. If it starts with "should we," it
   is a decision, not a research question — rewrite it as what you would need to
   know to decide.
2. Classify the question: generative (what is going on), evaluative (does this
   work), or descriptive (how many, how often).
3. Rate decision reversibility and state the timeline and participant access.
4. Run the recommender. It returns a primary method, a cheaper fallback, the
   minimum sample, and the methods it explicitly ruled out with reasons.
5. If the recommendation is "ship an experiment instead," take that seriously.
   For reversible decisions, an experiment usually beats a study on both speed
   and evidence quality.

```bash
python3 research-ops/product-research/scripts/method_recommender.py \
  --input research-ops/product-research/assets/sample_research_question.json \
  --format text
```

### Workflow 2 — Validate the screener before recruiting opens

1. Draft the screener: qualifying criteria, disqualifying criteria, and the
   items that test each.
2. Run the validator. It checks for transparent qualifying answers, missing
   disqualification logic, professional-respondent exposure, quota coverage,
   and criteria that no item actually tests.
3. Fix every `fail`. A screener defect costs you the whole study — you find out
   only during the sessions, by which point the incentives are spent.

```bash
python3 research-ops/product-research/scripts/screener_validator.py \
  --input research-ops/product-research/assets/sample_screener.json \
  --format text
```

### Workflow 3 — Score insight confidence during synthesis

1. Draft each candidate insight as a claim, and attach the evidence items that
   support it — each with its source type, participant, and whether it is
   observed behaviour or reported opinion.
2. Run the scorer. It weights observed evidence above reported evidence, rewards
   source and participant diversity, and penalises claims resting on a single
   session or a single channel.
3. Ship only the insights scoring `moderate` or above as decision inputs.
   Everything below that is a hypothesis and must be labelled as one.

```bash
python3 research-ops/product-research/scripts/insight_confidence_scorer.py \
  --input research-ops/product-research/assets/sample_evidence.json \
  --format text
```

## Decision frameworks

### Method by question type

| Question type | Example | Primary method | Minimum sample |
|---------------|---------|----------------|----------------|
| Generative — what is going on | "How do support agents currently triage tickets?" | **[PROVEN]** Contextual inquiry or semi-structured interview | 6-8 |
| Evaluative — does this work | "Can users complete onboarding unaided?" | **[PROVEN]** Moderated usability test | 5-8 |
| Comparative — which is better | "Which of two flows converts?" | **[PROVEN]** A/B experiment | Powered by traffic |
| Descriptive — how many, how often | "What share of accounts hit this limit?" | **[PROVEN]** Instrumentation or log analysis | Full population |
| Prioritisation — which matters most | "Which of five problems is most acute?" | **[RECOMMENDED]** Survey with forced trade-offs | 100+ |
| Desirability — would people want this | "Would customers use X?" | **[RECOMMENDED]** Painted-door or pre-commitment test | Traffic-dependent |
| Diagnostic — why did this drop | "Why did activation fall 12%?" | **[RECOMMENDED]** Funnel analysis first, then targeted interviews | 5-6 after analysis |

The pattern worth internalising: **quantitative methods tell you what and how
many; qualitative methods tell you why and how.** Reaching for interviews to
answer a "how many" question, or for a survey to answer a "why" question, is the
most common and most expensive method error in product research.

### Reversibility gate

| Decision type | Evidence bar | Typical spend |
|---------------|--------------|---------------|
| **Reversible in a sprint** | Ship it behind a flag and measure | Hours. Research here is usually waste. |
| **Reversible in a quarter** | 5-6 interviews or one experiment | Days |
| **Costly to reverse** — pricing, data model, public API | Mixed methods; qual for the why, quant for the size | 1-3 weeks |
| **One-way door** — platform, contract, market entry | Triangulated across 3+ independent sources | Weeks, and worth it |

**[PROVEN]** Match evidence spend to reversibility, not to how interesting the
question is. The most common research-ops failure is not too little research —
it is expensive research on reversible decisions while one-way doors get decided
on intuition.

### Saturation — when to stop interviewing

Track new themes per session. Stop when two consecutive sessions produce no new
theme.

| Sessions run | Typical state |
|--------------|---------------|
| 1-3 | Every session is new. Do not synthesise yet — you are pattern-matching on noise. |
| 4-6 | Themes start repeating. First real patterns appear. |
| 7-9 | Saturation for a homogeneous segment. Diminishing returns set in hard. |
| 10-12 | Needed only when covering 2+ distinct segments — treat each segment as its own count. |
| 15+ | Almost always over-research, unless the segments are genuinely many |

The count that matters is **per segment**, not in total. Eight sessions spread
across four segments is two per segment, which is anecdote.

## Anti-Patterns

### The Confirmation Study
**Mistake:** Running research after the decision is made, with a question phrased
to validate it — "we want to check users like the new dashboard."
**Why it happens:** The team needs air cover for a choice already funded, and
nobody wants to be the person whose study kills the roadmap item.
**Instead:** Write down, before recruiting, what result would cause you to change
course. If no such result exists, cancel the study and save the money — you are
buying decoration, not evidence. Getting that sentence written is also the
fastest way to discover the decision was never really open.

### Asking Users to Design
**Mistake:** "What features would you like to see?" and treating the answers as a
roadmap.
**Why it happens:** It feels maximally user-centred, and it produces concrete
output quickly.
**Instead:** Ask about the last time they hit the problem — what they were doing,
what they tried, what it cost them. People are reliable reporters of their own
experience and unreliable designers of solutions. Extract the problem from the
story; the solution is your job.

### Sample of Convenience
**Mistake:** Interviewing whoever answers the recruiting email — usually your
most engaged power users — and generalising to the whole base.
**Why it happens:** They respond fastest, they are pleasant to talk to, and the
sessions feel productive.
**Instead:** Recruit against a quota that includes the segments you most need to
hear from — churned users, low-engagement accounts, people who evaluated you and
chose a competitor. Those are harder to reach and worth several times more per
session. If you can only get power users, say so explicitly in the writeup and
scope the conclusion to them.

### Synthesis by Highlight Reel
**Mistake:** Building the findings deck from the most quotable moments across
sessions.
**Why it happens:** Vivid quotes are persuasive and memorable, and a striking
quote from one participant carries more weight in a readout than a pattern
across six.
**Instead:** Count first, quote second. Establish how many participants exhibited
each theme, then select a quote to illustrate a theme you have already
quantified. A quote is an illustration of evidence, never the evidence itself.

### Research Theatre on a Reversible Decision
**Mistake:** A three-week study to decide something that could be shipped behind
a flag on Tuesday and measured by Friday.
**Why it happens:** A research process exists, so it gets applied uniformly
regardless of what is at stake.
**Instead:** Run the reversibility gate first. If the decision is reversible in a
sprint, ship the experiment — it produces better evidence (observed behaviour at
real scale) faster and cheaper than any study. Reserve the research capacity for
the one-way doors that are currently being decided on nothing at all.

## Files

| File | Purpose |
|------|---------|
| `scripts/method_recommender.py` | Recommends a research method from question type, reversibility, timeline, and access |
| `scripts/screener_validator.py` | Checks a screener for transparency, missing disqualification logic, and quota coverage |
| `scripts/insight_confidence_scorer.py` | Scores insight confidence from evidence count, type, and source diversity |
| `references/method-selection-guide.md` | Every method with cost, sample, output, and the questions it cannot answer |
| `references/interview-craft.md` | Guide construction, probing technique, moderator failure modes, synthesis mechanics |
| `assets/interview-guide-template.md` | The structure a semi-structured discovery guide ships in |
| `assets/sample_research_question.json` | Runnable input for the method recommender |
| `assets/sample_screener.json` | Runnable input for the screener validator |
| `assets/sample_evidence.json` | Runnable input for the insight confidence scorer |
