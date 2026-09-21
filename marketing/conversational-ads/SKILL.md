---
name: conversational-ads
description: >
  Plan, write and measure ads inside AI assistants and AI search (ChatGPT Ads,
  Google AI Overviews and AI Mode, Microsoft Copilot). Use when testing ChatGPT
  ads, answer-adjacent copy, or incrementality for AI placements.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: marketing
  domain: paid-media
  updated: 2026-09-21
  tags: [chatgpt-ads, ai-overviews-ads, ai-mode, copilot-ads, conversational-ads, incrementality, paid-media, ad-copy]
---

# Conversational Ads

Paid placements next to AI answers: ChatGPT Ads (test began February 2026, self-serve Ads Manager since May 2026), Google ads in AI Overviews and AI Mode, and ads in Microsoft Copilot. This skill covers what is different from search, which platforms your category and market can use, how to write copy that sits next to an answer without borrowing its authority, how to get feeds and landing pages ready, and how to prove incrementality when two of the three platforms give no placement-level reporting.

> Platform facts are **as of September 2026** and come from each platform's own help pages — see [references/platform-specs.md](references/platform-specs.md). These products change monthly; re-check the linked pages before committing budget.

---

## When to use this skill

| Situation | Use |
|-----------|-----|
| "Should we test ChatGPT ads?" / first AI-placement test | `scripts/conversational_ad_planner.py` + test-plan template |
| Writing ad copy for ChatGPT, AI Overviews, AI Mode or Copilot | Creative rules below + `scripts/answer_adjacent_copy_linter.py` |
| Explaining why AI Overviews spend can't be reported or turned off | [platform-specs.md](references/platform-specs.md) |
| Measuring whether AI placements add conversions | Measurement workflow + [playbook](references/conversational-ads-playbook.md) §5 |
| Earning organic citations in AI answers (not paid) | Out of scope — this skill is paid media only |
| Labelling AI-generated creative | Out of scope beyond a lint warning — use a disclosure/compliance process |

---

## Clarify First

Before planning, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Category and markets/language** — sensitive categories are excluded on ChatGPT and AI Overviews, and AI Overviews ads are English-only in 12 countries
- [ ] **Monthly budget and target CPA** — decides how many platforms can be tested with a readable holdout (≥50 conversions per arm)
- [ ] **Real customer prompts** — 20-50 questions people ask assistants, tagged research / compare / purchase / support
- [ ] **Measurement readiness** — server-side conversions and the ability to hold out regions; without these the test cannot be read

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the plan.

---

## Quick start

```bash
# 1. Plan: eligibility, mix, holdout test, KPI targets, readiness (exit 2 = blocked)
python3 scripts/conversational_ad_planner.py assets/sample_plan_input.json
python3 scripts/conversational_ad_planner.py my_brief.json --format json --min-conversions 100

# 2. Lint copy before upload (exit 2 = errors; --strict fails on warnings too)
python3 scripts/answer_adjacent_copy_linter.py assets/sample_ad_copy.json

# 3. Fill assets/test-plan-template.md and freeze it before launch
```

The shipped samples fail on purpose: the planner exits **2** because the Copilot arm is underpowered at USD 12,000/month and a USD 60 CPA; the linter exits **2** with 10 errors across three broken ads (assistant-endorsement copy, unsubstantiated "clinically proven", over-length Google headline, unverified testimonial, http landing URL). Two ads pass clean.

---

## How conversational placements differ from search [RECOMMENDED]

| | Search ad | Answer-adjacent ad |
|---|---|---|
| Intent | Short query | Whole conversation + the answer's content |
| Control | Keywords, placements | Broad matching; Google and Microsoft: no opt-out, no placement targeting |
| Reporting | By placement | ChatGPT: own reporting. Google: counted as Top ads, no AI segment. Microsoft: no Copilot metrics |
| Creative job | Beat nine other links | Add a useful fact the answer lacks |
| Main risk | Low CTR | Looking like you hijacked a trusted answer |

**Position:** optimise inputs (feed, assets, landing pages, negatives) and read outcomes with holdout experiments. Do not try to optimise a placement you cannot see.

---

## Platform snapshot (as of September 2026)

| | ChatGPT Ads | Google AI Overviews / AI Mode | Microsoft Copilot |
|---|---|---|---|
| How to buy | Direct, Ads Manager (beta), CPC or outcome bidding | Indirect: Search with broad match / AI Max, Shopping, PMax | Indirect: PMax, Search with logo, Shopping, Multimedia, some vertical ads |
| Who sees ads | Logged-in adults on Free and Go plans; not Plus/Pro/Business/Enterprise/Edu; not Temporary Chats | English queries in AU, CA, IN, ID, KE, MY, NZ, NG, PK, PH, SG, US (AI Overviews) | Copilot users; negative keywords apply |
| Excluded | Near health, mental health, politics; several categories disallowed; finance/health/legal by manual approval | Adult, alcohol, gambling, finance, healthcare, politics and more | Bing policies; ads not shown in flagged conversations |
| Measurement | Pixel + Conversions API, UTMs, macros | Blended into Top ads | Search term + asset reports only |
| Copy | Title 16-24, copy 32-48 chars (recommended) | RSA 30 / 90 chars (limits) | RSA 30 / 90 chars (limits) |

Perplexity: 2024 ads experiment announced; current availability **unverified** — excluded from the planner.

---

## Workflows

### Workflow: first test plan

1. Collect prompts and tag each with a stage and a weight (relative volume or value).
2. Write the brief (`assets/sample_plan_input.json` shows every field).
3. Run the planner. Resolve `BLOCKERS` first: drop a platform, raise budget, extend weeks, or install tracking.
4. Resolve `READINESS` items marked `MISSING` — landing pages that answer the prompt and a clean feed matter more than bids. [RECOMMENDED]
5. Copy the plan into `assets/test-plan-template.md`, pick treated and holdout regions, and set the freeze window.

### Workflow: copy for answer-adjacent placements

1. One prompt cluster → 5-10 variations, each with a different angle (spec, price, delivery, fit, compatibility). OpenAI recommends many diverse variations.
2. Lead with a checkable fact; end with a specific soft CTA ("Compare widths").
3. Run the linter. Fix every `ERROR`; review `WARNING`s — ChatGPT length ranges are recommendations, not limits.
4. Record evidence for any claim you keep in `substantiated_claims`.

### Workflow: measurement

1. Server-side conversions on each platform, deduplicated.
2. UTMs with `utm_medium=cpc` so paid clicks stay out of GA4's organic **AI Assistant** channel.
3. Geo holdout (10-20% of matched regions) or time-based on/off if regions are too few. [RECOMMENDED]
4. Two-week learning period, then freeze. Read at week 6: incremental conversions, incremental CPA, brand-search lift.
5. Decide: scale if incremental CPA ≤ target; iterate inputs if within 30%; stop otherwise.

For Google and Microsoft, the holdout measures the **campaign change that made you eligible** (e.g. moving to broad match / AI Max / PMax), not the AI placement alone. State that in the readout.

---

## Exit code contract [PROVEN]

| Code | Planner | Linter | Who fixes it |
|------|---------|--------|--------------|
| 0 | Plan produced, no blockers | No errors (warnings allowed unless `--strict`) | Nobody |
| 1 | Tool error — bad path, malformed JSON, missing field | Tool error — bad path, malformed JSON, unknown platform | Whoever maintains the input file |
| 2 | Blocked — no eligible platform, no conversion tracking, or an underpowered arm | Gate failed — errors (or warnings with `--strict`) | Media planner / copywriter |

---

## Anti-Patterns

### Borrowing The Assistant's Voice
**Mistake:** "ChatGPT's top pick", "Recommended by Copilot", copy styled to look like the answer.
**Why it happens:** The answer carries trust and teams want some of it.
**Instead:** Ads are labelled Sponsored and separated from answers by design, and OpenAI's ad policies prohibit false endorsements. Lead with a fact the answer lacks. The linter blocks this pattern.

### Reading Platform ROAS As Incrementality
**Mistake:** Scaling on platform-reported conversions in week 3.
**Why it happens:** It is the only number available, and Google/Microsoft do not isolate AI placements.
**Instead:** Build the holdout before launch and decide on incremental CPA.

### Budgeting A Placement You Cannot Buy
**Mistake:** A media-plan line called "AI Overviews" with its own budget.
**Why it happens:** Plans expect one line per placement.
**Instead:** On Google and Microsoft, fund the underlying Search broad / AI Max / Shopping / PMax campaigns and test the change that made you eligible.

### Spreading A Small Budget Across Every Assistant
**Mistake:** A few thousand dollars split three ways for a four-week test.
**Why it happens:** Fear of missing the next channel.
**Instead:** Concentrate until each arm can reach ~50 conversions. The planner exits 2 on underpowered arms.

### Feed Neglect
**Mistake:** Polishing creative while product titles lack the attributes people ask about and prices lag the site.
**Why it happens:** Feeds belong to another team.
**Instead:** Treat the feed as creative. Audit the top SKUs against real prompts and use delta feeds for price and availability.

More in [references/anti-patterns.md](references/anti-patterns.md).

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| Planner says Google ineligible for a US brand | `language` not `en` or category in excluded list | Check brief; plan classic search for excluded categories |
| Every arm UNDERPOWERED | Budget/CPA too low for three arms | Drop to one platform or extend `test_weeks` |
| Linter flags a claim you can prove | Claim not listed in `substantiated_claims` | Add the exact term once evidence is on file |
| Linter misses a restricted term | Category regexes are deliberately conservative | Extend `CATEGORY_TERMS` for your vertical |
| GA4 shows paid ChatGPT clicks under "AI Assistant" | Missing `utm_medium=cpc` | Add UTMs or platform macros to every destination URL |

---

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/conversational_ad_planner.py` | Brief → eligibility, placement mix, holdout test plan, KPI targets, readiness, blockers |
| `scripts/answer_adjacent_copy_linter.py` | Ad copy → length, claims, assistant-endorsement, category, pressure, CTA, URL/UTM, price, testimonial, AI-media and style checks |

Both: Python 3.8+ standard library only, `--format text|json`, deterministic.

## References

- [platform-specs.md](references/platform-specs.md) — ChatGPT Ads, Google AI Overviews / AI Mode, Microsoft Copilot, Perplexity status, GA4 AI Assistant channel; official links
- [conversational-ads-playbook.md](references/conversational-ads-playbook.md) — differences from search, planning sequence, channel roles, creative rules, test designs, KPIs, risks
- [anti-patterns.md](references/anti-patterns.md) — extended anti-pattern catalogue

## Assets

- `assets/sample_plan_input.json` — planning brief (exits 2: underpowered arm)
- `assets/sample_ad_copy.json` — five ads, two clean and three broken (exits 2)
- `assets/test-plan-template.md` — hypothesis, prompts, eligibility, design, power, KPIs, readiness, readout
