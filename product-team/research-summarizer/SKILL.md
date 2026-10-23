---
name: research-summarizer
description: >
  Synthesize raw user research (interviews, surveys, tickets) into themed
  findings and decision-ready briefs. Use when synthesizing user interviews,
  building a findings brief, or communicating research to stakeholders.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: product-team
  domain: user-research
  updated: 2026-05-27
  tags: [user-research, synthesis, insights, qualitative, ux, communication]
---

# Research Summarizer

A skill focused on **synthesizing and communicating** research — the part
that comes after you've collected the data. Distinct from the research
collection skills which guide interview design, recruiting, and protocol.

This skill assumes you have raw inputs (transcripts, notes, survey
responses) and need to turn them into trustworthy insights that drive
product decisions.

## When to use this skill

- Synthesizing a batch of **user interviews** (typically 5-30)
- Pulling **themes from open-text survey responses**
- Synthesizing **support tickets** for product-truth analysis
- Building a **findings brief** for stakeholders
- Separating **signal from anecdote** in qualitative data
- Auditing existing **research summaries** for bias and reliability
- Preparing a **research readout** for execs / cross-functional teams

## Inputs the advisor expects

- Type of research artifacts (interviews, surveys, tickets, observations, sales notes)
- Volume and recency
- Research question(s) the synthesis is answering
- Audience for the output (PM team / exec / engineering)
- Decision the output should inform

## Clarify First

Before generating the synthesis or brief, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **The research question:** what decision this synthesis answers (drives the brief's lead and which themes matter).
- **Audience and the decision it informs:** PM team, exec, or engineering (sets brief altitude, length, and format).
- **Artifact type and volume:** interviews/surveys/tickets and how many (drives confidence, sample-size adequacy, and bias checks).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Workflows

### Workflow 1 — Organize and theme raw research

1. Capture raw research items (one per row) with source, date, segment.
2. Run `research_synthesis_organizer.py` to surface theme clusters
   based on tagging, computed frequencies, and segment cross-cuts.
3. Refine themes manually; promote to insights.

```bash
python3 research-summarizer/scripts/research_synthesis_organizer.py \
  --input research_items.json --format markdown
```

### Workflow 2 — Score insight quality

1. List proposed insights with supporting evidence count + segment coverage.
2. Run `insight_quality_scorer.py` to grade each insight on Confidence,
   Specificity, Action-readiness, and Bias risk.
3. Keep High / Medium insights; demote Low to "questions for further research."

```bash
python3 research-summarizer/scripts/insight_quality_scorer.py \
  --input insights.json --format markdown
```

### Workflow 3 — Generate a findings brief

1. Capture the question, top insights, supporting evidence, decisions.
2. Run `findings_brief_generator.py` to produce the structured brief.

```bash
python3 research-summarizer/scripts/findings_brief_generator.py \
  --input findings.json --format markdown
```

## Decision frameworks

### Observation → Pattern → Insight → Recommendation

A clean synthesis ladder:

1. **Observation** — direct quote or behavior ("user X said Y")
2. **Pattern** — repeats across users ("4 of 7 users said Y")
3. **Insight** — interpreted explanation ("users avoid Y because Z")
4. **Recommendation** — action implied ("redesign Z to address Y avoidance")

Each level requires more confidence than the last. Don't skip from
observation directly to recommendation.

### Insight quality dimensions

- **Confidence:** how many independent sources support it
- **Specificity:** is the insight specific enough to action?
- **Bias risk:** is the sample / interpretation biased?
- **Decision impact:** does this insight change anything?

A high-quality insight scores well on all four. Most rough notes are
strong on confidence but weak on specificity (or vice versa).

### Sample size for qualitative research

A rough heuristic for how many interviews are enough:

| Goal | Suggested N |
|------|-------------|
| Discover the space (early product) | 5-8 |
| Validate hypotheses | 8-12 |
| Persona definition | 12-20 |
| Detect quantitative signal in qual | 20-30+ |
| Validate cross-segment | 5-8 per segment |

Diminishing returns after the patterns repeat 2-3 times. If you keep
hearing new things, you're not done.

### When qualitative data lies (common biases)

- **Confirmation bias** — interviewers pull the quotes they expected to hear
- **Acquiescence bias** — participants agree to be polite
- **Recall bias** — what users remember vs what they did
- **Selection bias** — who agreed to interview is not representative
- **Recency bias** — recent interviews carry disproportionate weight
- **Anchor bias** — first interview shapes interpretation of later ones
- **Demand characteristics** — participants guess what you want to hear

Counter: use a **second coder**, structure your guide, sample diversely,
and report negative evidence.

## Common engagements

### "Help me synthesize 12 user interviews"
1. Make sure you have transcripts (or detailed notes).
2. Tag each interview by demographic, journey stage, key behaviors.
3. Surface 5-10 themes from initial tagging.
4. For each theme, count: how many users? from which segments? evidence quality?
5. Promote 3-5 themes to insights; demote the rest to "questions for next round."
6. Add 1-2 unexpected findings (the "we didn't expect this" insight).

### "Translate the research into a one-pager for execs"
1. Lead with the question being asked.
2. Lead with the answer (1-2 sentences); details follow.
3. 3-5 insights with evidence; not more.
4. Decisions / recommendations that follow.
5. What you don't know yet (research limits + next-step questions).
6. Methodology one-liner (N, segments, dates).

### "Our research found contradictory things"
1. First: is one finding from a different segment? Often the contradiction is segment-based.
2. Second: was sample biased toward one side?
3. Third: maybe both are true and the system has tensions worth surfacing.

## Anti-patterns to avoid

- **Cherry-picked quotes.** Always provide the count + context.
- **Insight without evidence.** "Users want X" without supporting observations.
- **Anecdotal generalization.** One angry user doesn't define the population.
- **Reporting interview-by-interview.** Synthesis means seeing across users.
- **Hiding the negative evidence.** Disconfirming evidence is valuable.
- **Brief that's longer than needed.** Briefer = better-read.
- **Mixing facts and interpretations.** Be clear which is which.
- **Skipping methodology.** Readers need to evaluate the trust level.

## Scope & Limitations

**In Scope:**
- Organizing raw research items into theme clusters with `research_synthesis_organizer.py`, with frequency, segment cross-cuts and quality flags such as single-session themes
- Scoring proposed insights on confidence, specificity, bias risk and decision impact with `insight_quality_scorer.py`, with a keep, refine or demote call
- Generating a findings brief (one-pager, extended memo and quote bank) with `findings_brief_generator.py`
- The observation, pattern, insight, recommendation ladder, qualitative sample-size heuristics and a catalog of common research biases

**Out of Scope:**
- Designing the study, recruiting and writing interview guides (see `product-team/ux-researcher-designer/` and `research-ops/product-research/`)
- Quantitative product data analysis (see `product-team/product-analytics/`)
- Statistical testing of survey results (see `data-analytics/statistical-analyst/`)
- Transcribing recordings

**Important Caveats:**
- The tools do not read transcripts or free text for meaning. Themes come from tags the user assigns to each item, so the clustering is only as good as the tagging.
- Insight scores are heuristics built from the evidence counts and segment coverage entered. They do not replace a second coder or a check against the raw data.
- The sample-size table gives rough ranges for qualitative work. It is not a statistical power calculation.

## References

- `references/research-synthesis-frameworks.md` — affinity, thematic analysis, frameworks
- `references/insight-quality-and-bias.md` — quality dimensions, bias catalog, validation
- `references/communicating-research-findings.md` — brief formats, presentation patterns

## Related skills

- `product-team/ux-researcher-designer` — research design + collection
- `product-team/product-strategist` — strategic input from insights
- `product-team/product-analytics` — quant complement to qual
- `c-level-advisor/chief-customer-officer-advisor` — VoC program context
