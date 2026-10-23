---
name: roadmap-communicator
description: >
  Translate one internal roadmap into audience-appropriate formats with
  confidence-band discipline. Use when preparing a roadmap readout, tailoring it
  for an exec, customer, eng, or sales audience, or auditing over-promise risk.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: product-team
  domain: roadmap
  updated: 2026-05-27
  tags: [roadmap, communication, prd, now-next-later, themes, board, customer]
---

# Roadmap Communicator

A skill focused on **communicating the roadmap** — different audiences
need different formats and confidence levels. Distinct from `product-strategist`
(which builds the strategy) and `agile-product-owner` (which manages sprint
execution).

## When to use this skill

- Preparing a **roadmap readout** for execs, board, customers, or sales
- Translating a single internal roadmap to multiple audience formats
- Auditing **roadmap commitments** for over-promise risk
- Building a **now-next-later** view of priorities
- Communicating **roadmap changes** to stakeholders
- Preparing a **what-changed/what's-next** memo

## Inputs the advisor expects

- The internal roadmap (themes, initiatives, target dates, confidence)
- Target audience(s) for the communication
- Recent roadmap changes (added, removed, slipped)
- Cross-functional commitments (engineering, sales, marketing)

## Clarify First

Before generating the roadmap communication, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Target audience:** board/exec, customer, sales, or engineering (selects the audience-format matrix row and granularity).
- **Confidence band per item:** commit, plan, aspire, or strategic intent (drives the language and over-promise guardrails).
- **Recent changes:** what was added, removed, or slipped since the last readout (drives the what-changed diff memo).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Workflows

### Workflow 1 — Translate roadmap for a specific audience

1. Capture the master roadmap with confidence bands.
2. Run `roadmap_audience_translator.py` with target audience.
3. Review the audience-specific output; tune language.

```bash
python3 roadmap-communicator/scripts/roadmap_audience_translator.py \
  --input roadmap.json --audience customer --format markdown
```

### Workflow 2 — Apply confidence bands to commitments

1. List proposed roadmap items.
2. Run `confidence_band_generator.py` with team velocity history + estimation context.
3. Adjust item commitments based on output (commit / aspire / explore).

```bash
python3 roadmap-communicator/scripts/confidence_band_generator.py \
  --input items.json --format markdown
```

### Workflow 3 — Generate a roadmap diff report

1. Capture previous roadmap snapshot + current roadmap.
2. Run `roadmap_diff_reporter.py` to produce what-changed memo.

```bash
python3 roadmap-communicator/scripts/roadmap_diff_reporter.py \
  --previous roadmap_q1.json --current roadmap_q2.json --format markdown
```

## Decision frameworks

### Audience-format matrix

| Audience | Right format | Wrong format |
|----------|--------------|--------------|
| Board / exec | Themes + bets + KPIs (1 page) | Feature list |
| Customers / public | What's new + what's next (themes; no dates) | Internal commit list |
| Sales | Themes + competitive positioning + customer-ask coverage | Engineering jargon |
| Engineering | Themes + quarter commitments + scoped detail | Vague aspirations |
| Internal company | Themes + progress + asks | Confidential strategy |
| Partner / integrator | API-relevant changes + breaking-change calendar | All-up roadmap |

Same roadmap; different formats. Don't send the engineering commit list to customers.

### Confidence bands

Apply per item:

| Band | Language | Audience expectation |
|------|----------|----------------------|
| **Commit** | "Will ship" with target date | Hold us to this |
| **Plan** | "Plan to ship" with target window | Confident but conditional |
| **Aspire** | "Investigating" / "Exploring" | Don't depend on this |
| **Strategic intent** | "We believe X matters" | Direction, not deliverable |

Common errors:
- Treating "plan" as "commit" — sets up disappointment
- Communicating "commit" as "plan" — under-delivers excitement
- No confidence band — every line read as commit

### Now-next-later structure

A useful skeleton across audiences:

- **Now** (in progress, < 1 quarter): commit-level items
- **Next** (1-2 quarters out): plan-level items
- **Later** (2-4 quarters): aspire-level items
- **Strategic intent** (>4 quarters): direction only

This protects confidence: the closer in time, the firmer the commitment.

### Themes vs features

Communicate at the right granularity:

- **External / strategic:** themes ("better collaboration")
- **Customer-specific:** outcomes ("you'll be able to X")
- **Internal:** features + tickets

Telling a customer "we're adding X in Q3" makes a commitment that may
not be precise enough. Telling the team "we're going to improve
collaboration somehow" is too vague.

## Common engagements

### "Help me write the customer roadmap section"
1. Start with what they care about (outcomes, not features).
2. Use themes + outcomes; avoid specific dates beyond the current quarter.
3. Group: launching soon, in development, exploring.
4. Avoid: features that depend on uncertain technical bets.
5. Always include a "we'd love your input" hook.

### "Help me prep the board roadmap section"
1. Start with strategic themes (3-5).
2. For each theme: what's shipped, what's coming, what's the bet.
3. Tie to business outcomes (NRR impact, new revenue, cost saving).
4. Surface 1-2 strategic risks transparently.
5. End with 2-3 specific asks.

### "Our customer is asking 'when will X ship?'"
1. First check: is X actually committed? (Probably plan or aspire.)
2. If commit: give a target window with caveats.
3. If plan: "We're planning to ship in [window]; we'll know more by [date]."
4. If aspire: "We're exploring; not in our committed roadmap."
5. Document the customer asks; feed them back into prioritization.

## Anti-patterns to avoid

- **One-size-fits-all roadmap.** Different audiences get over- or under-served.
- **Date-only roadmap.** Dates without confidence bands set up over-promise.
- **Public commitments engineering didn't sign off on.** Trust breaks.
- **Roadmap that never changes.** Reality changes; roadmap must.
- **Roadmap silence between updates.** Customers / sales speculate.
- **Hiding strategic risks.** Boards prefer honest risks over surprise misses.
- **Big bang annual roadmap with no quarterly delta.** Misses change cycles.
- **Feature names instead of outcomes.** "Notifications v2" tells the customer nothing.

## Scope & Limitations

**In Scope:**
- Translating a master roadmap into a format for one audience (for example board or customer) with `roadmap_audience_translator.py`
- Recommending a confidence band (commit, plan, aspire, strategic intent) per item with `confidence_band_generator.py`, from readiness, dependency risk and velocity history
- What-changed memos from two roadmap snapshots with `roadmap_diff_reporter.py`: added, removed, slipped, re-prioritized and confidence-changed items
- The audience-format matrix, now-next-later structure, and themes versus features guidance

**Out of Scope:**
- Setting product strategy and deciding what goes on the roadmap (see `product-team/product-strategist/` and `project-management/execution/prioritization-frameworks/`)
- Sprint planning and backlog execution (see `product-team/agile-product-owner/`)
- Syncing with roadmap tools such as Productboard (see `project-management/productboard-expert/`)
- The PM-domain variant that writes executive, customer and internal roadmap versions (see `project-management/execution/roadmap-communication/`)

**Important Caveats:**
- The tools read roadmap JSON prepared by the user. They do not pull from Jira, Productboard or any other planning tool, so the output is only as current as the snapshot.
- Confidence bands are a heuristic recommendation from the attributes entered. Engineering still has to agree to any item communicated as a commitment.
- Generated audience text is a draft. Wording for customers, sales and the board needs review before it is sent.

## References

- `references/roadmap-communication-patterns.md` — format catalog + when to use
- `references/audience-specific-formats.md` — per-audience templates
- `references/now-next-later-and-themes.md` — structural patterns

## Related skills

- `product-team/product-strategist` — strategy upstream of roadmap
- `product-team/agile-product-owner` — sprint-level execution
- `product-team/product-manager-toolkit` — broader PM tooling
- `c-level-advisor/cpo-advisor` — CPO partnership
- `c-level-advisor/ceo-advisor` — CEO / board alignment
- `business-growth/customer-success-manager` — customer comms
- `marketing/` skills — external messaging alignment
