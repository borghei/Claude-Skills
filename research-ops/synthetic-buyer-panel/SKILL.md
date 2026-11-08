---
name: synthetic-buyer-panel
description: >
  Simulated buyer panel: deal reproducible persona cards, run one agent per
  buyer, tally buy rates, objections and price corridors. Use when asking
  "would people buy this", pre-testing a pitch, or finding objections fast.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: research-ops
  domain: concept-testing
  updated: 2026-11-08
  tags: [synthetic-personas, concept-testing, objections, demand-validation, pricing-research, buyer-panel]
---

# Synthetic Buyer Panel

Before spending money on a launch, put the pitch in front of a panel of
simulated buyers drawn from the target customer, each with a different income,
life stage, buying habit and starting doubt, and see who buys, who passes and
why. The panel is fast and cheap, and it is good at one thing: surfacing
objections, segment differences and wording before real people are asked.

The agent acts as moderator. It builds the customer profile with the user,
deals the cards, dispatches one isolated buyer agent per brief, and tallies the
answers. It never answers for a buyer, and it never presents a simulated answer
as customer evidence.

## When to use this skill

- **"Would people buy this?"** for an idea, product or service not yet launched
- **Pre-testing a pitch** for confusing, missing or off-putting information
- **Finding objections** a type of buyer is likely to raise, in their words
- **Comparing segments** to see who reacts differently to the same offer
- **Comparing two variants** (price, delivery option, offer) on identical buyers
- **Getting a first price corridor** to take into a real price test

## Inputs the skill expects

- The offer and the pitch a real customer would see, with price and unit
- The price unit the four price answers refer to when the pitch lists several prices
- A target customer sentence: who, where, and what they do today
- Two to four segments with shares and income ranges (optionally age ranges)
- Four to eight buying behaviours with shares
- Three to eight real objections, ideally from reviews, tickets or interviews
- Everyday contexts that make each buyer concrete
- Panel size and seed

## Clarify First

The customer profile shapes this output more than anything else: a wrong
profile produces a confident, wrong panel. Settle the inputs below before
producing anything. When one is missing or vague and would change the result,
ask about it; when it wouldn't, use a sensible default and say which one you
used.

- **Who the target customer is today:** the agents reason from this sentence;
  a vague target returns generic answers the tally cannot separate.
- **Where the objections come from:** objections from real reviews or calls give
  the panel something true to push against; invented ones only echo the founder.
- **The exact pitch and price:** every buyer sees it word for word, and price
  answers are meaningless without a price and unit.
- **What decision the panel feeds:** a first look needs 20 buyers; comparing
  segments or variants needs 40 to 60.

Ask about the two or three inputs that matter most for this request, not the
whole list. If the user wants a result straight away, produce it and state your
assumptions at the top, marking which parts of the profile are guesses.

## Quick Start

```bash
# 1. Check the profile and deal 40 cards plus one brief per buyer
python3 research-ops/synthetic-buyer-panel/scripts/panel_deal.py \
  --profile research-ops/synthetic-buyer-panel/assets/sample_customer_profile.json \
  --n 40 --seed 7 --out-dir panel-run

# 2. Dispatch one isolated agent per brief (see Workflow 2)

# 3. Validate and tally the answers
python3 research-ops/synthetic-buyer-panel/scripts/panel_tally.py \
  --cards research-ops/synthetic-buyer-panel/assets/sample_panel_cards.json \
  --answers research-ops/synthetic-buyer-panel/assets/sample_panel_answers.json
```

## Tools Overview

| Tool | Input | Output | Exit codes |
|------|-------|--------|------------|
| `panel_deal.py` | Customer profile JSON | Profile checks, exact-quota cards, one brief per buyer | 0 dealt, 1 profile fails a check, 2 bad input |
| `panel_tally.py` | Cards + answers (list or folder) | Buy rate by segment and behaviour, pass reasons, flips, price corridor, reliability findings | 0 readable, 1 reliability fails, 2 bad input |

Both are stdlib-only and deterministic, with `--format text|json`. The same
profile, size and seed always deal the same buyers.

## Workflows

### Workflow 1 — Build the profile and deal

1. Draft the profile with the user: target sentence, segments, behaviours,
   objections and contexts. Pull objections from competitor reviews, support
   tickets or interview notes where they exist, and mark guesses as guesses.
2. Write the pitch exactly as a shopper would meet it: the product, its price
   per unit, where it is sold, and any launch deal. Keep it plain, no hype.
3. Show the profile to the user in a few lines and let them correct it.
4. Run `panel_deal.py`. It must pass its checks: shares sum to 1.0, target
   specific enough, a price in the pitch, at least three objections. A FAIL
   deals nothing; fix the profile rather than editing cards.

```bash
python3 research-ops/synthetic-buyer-panel/scripts/panel_deal.py \
  --profile profile.json --n 40 --seed 7 --out-dir panel-run
```

### Workflow 2 — Run the buyers

1. Tell the user how many agent runs the panel needs and offer a 20-buyer
   first look before a large run.
2. Dispatch one sub-agent per brief, about ten per message, each told only:
   read this brief, follow it exactly, write the JSON answer to
   `answers/<id>.json`. Each agent sees its own brief and nothing else.
3. Wait for each wave to finish before starting the next.
4. Re-run invalid or missing buyers once with the same brief. A buyer that fails
   twice stays missing. The moderator never writes or completes an answer.

Full dispatch and retry rules: `references/running-the-panel.md`.

### Workflow 3 — Tally and read out

1. Run the tally. Its reliability checks are a quality gate and must pass
   before any result is read: at least 20 valid answers and 90%+ coverage.
2. Read differences before levels: the segment and behaviour rows furthest from
   the average, then the top pass reasons, then the flips.
3. Treat the buy rate as a ceiling. Validate any big call with a priced real
   test, and say so once in the readout.
4. Fill `assets/panel-readout-template.md` and end with one real-world test
   aimed at the top pass reason.

```bash
python3 research-ops/synthetic-buyer-panel/scripts/panel_tally.py \
  --cards panel-run/cards.json --answers panel-run/answers/ --format json
```

### Workflow 4 — Compare two variants

1. Keep profile and seed fixed and change only the pitch lines under test.
2. Deal into a second folder; the buyers are identical.
3. Compare the pass-reason mix and segment rates. A variant that removes the top
   pass reason matters more than one that nudges the overall rate.

## Decision frameworks

### Panel size

| Purpose | Size |
|---------|------|
| First look, objection list | **[RECOMMENDED]** 20 |
| Segment or behaviour comparison | **[RECOMMENDED]** 40-60 (8-10 per group) |
| Variant comparison | 40-60 per variant, same seed |
| Over 200 | Rarely worth it: correlated error does not shrink with n |

### Reading the result

| Signal | What it means | Action |
|--------|---------------|--------|
| A segment 20+ points above average | **[RECOMMENDED]** A lead on who to target first | Aim the first real test at that segment |
| One pass reason over 40% of passes | The main barrier | Change the offer, channel or price that addresses it, then re-run |
| Buy rate over 60% | **[PROVEN]** Agreeable panel or hyped pitch | Re-read pitch and briefs before trusting anything |
| Many identical reasons | Buyers not differentiated | Add concrete contexts and real objections |
| Price corridor below current price | Price is a likely barrier | Test two prices with real buyers before changing it |

**[PROVEN]** Simulated panels lean agreeable. Use them to decide what to test
with real people, never as the test.

## Anti-Patterns

### The Moderator Who Answers
**Mistake:** Filling in a missing or broken answer "the way that buyer would have answered".
**Why it happens:** A gap in the tally looks untidy and the moderator thinks they know the persona.
**Instead:** Re-run the buyer once with the same brief; if it fails again it stays
missing. The tally fails below 90% coverage so a thin panel cannot pass quietly.

### Panel Quotes as Testimonials
**Mistake:** Pasting simulated reasons into a deck, landing page or investor memo as customer voice.
**Why it happens:** The quotes read naturally and nobody marks where they came from.
**Instead:** Label every quoted answer as simulated, in the same sentence. Real
testimonials come only from real customers.

### The Founder's Objections
**Mistake:** Writing the objections list from the founder's own guesses about what buyers might worry about.
**Why it happens:** It is the fastest way to fill the profile.
**Instead:** Pull objections from competitor reviews, support tickets, sales
calls or interviews. Invented objections produce a panel that confirms the founder.

### Shared Context Between Buyers
**Mistake:** Running every brief in one conversation, or letting agents see each other's answers.
**Why it happens:** It is simpler than dispatching isolated agents.
**Instead:** One isolated agent per brief. Shared context makes answers converge,
which the duplicate-reason check will usually catch.

### Different Seeds for Variant Tests
**Mistake:** Comparing two pitches on panels dealt with different seeds.
**Why it happens:** The second run is started fresh with defaults changed.
**Instead:** Keep profile and seed fixed so only the pitch differs.

## Reference Documentation

- `references/panel-design-and-bias.md` — what panels are good and bad at,
  building the profile, writing the pitch, biases and counter-measures, sizing,
  reading the tally, ethics
- `references/running-the-panel.md` — folder layout, dealing, dispatching agents
  in waves, retries, moderator checklist, variant comparison, readout

## Files

| File | Purpose |
|------|---------|
| `scripts/panel_deal.py` | Profile checks, exact-quota card dealing, per-buyer briefs |
| `scripts/panel_tally.py` | Answer validation, rates by group, pass reasons, flips, price corridor, reliability findings |
| `references/panel-design-and-bias.md` | Profile design, bias counter-measures, interpretation |
| `references/running-the-panel.md` | Moderator operations from deal to readout |
| `assets/sample_customer_profile.json` | Sound profile: refill shop (deals, exit 0) |
| `assets/sample_customer_profile_flawed.json` | Deliberately flawed profile (nothing dealt, exit 1) |
| `assets/sample_panel_cards.json` | Cards dealt from the sound profile, n=40, seed 7 |
| `assets/sample_panel_answers.json` | 40 sample answers (tally exit 0) |
| `assets/sample_panel_answers_flawed.json` | Thin, agreeable, partly invalid answers (tally exit 1) |
| `assets/panel-readout-template.md` | The readout a panel result ships in |

## Scope & Limitations

**In Scope:**
- Building and checking a target customer profile, then dealing reproducible
  persona cards and briefs with `panel_deal.py`
- Moderating one isolated agent per buyer, with retry and no-fill rules
- Validating and tallying answers with `panel_tally.py`: buy rate by segment and
  behaviour, pass reasons, flips, objections and a price corridor
- Comparing two pitch variants on identical buyers

**Out of Scope:**
- Recruiting, paying or surveying real people
- Market sizing and demand forecasting
- Final price setting; the corridor is an input to a real price test
- Calling any model or API from the scripts: agents are run by the assistant, not the tools

**Important Caveats:**
- Simulated buyers lean agreeable and share one model's priors. Buy rates are
  ceilings, and n buyers are not n independent samples; no confidence intervals
  are reported for that reason.
- Results reflect only what the profile and pitch say. Location, brand and timing
  effects the profile omits are invisible to the panel.
- Segment on behaviour, life stage and context. Do not build personas around
  protected traits.
