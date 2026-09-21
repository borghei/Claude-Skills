# Conversational Ads Test Plan — [Product]

**Owner:** [name] · **Dates:** [start] → [readout] · **Platform facts verified on:** [date, links re-checked]

## 1. Hypothesis
Adding [ChatGPT Ads / broad-match + AI Max / PMax for Copilot] in [markets] will deliver incremental conversions at an incremental CPA ≤ [target] within [N] weeks.

## 2. Prompts in scope
| # | Prompt (as customers phrase it) | Stage | Weight | Sensitive? |
|---|----------------------------------|-------|--------|-----------|
| 1 | | research / compare / purchase / support | | yes / no |

## 3. Eligibility (from `conversational_ad_planner.py`)
| Platform | Eligible | Buy mechanism | Notes |
|----------|----------|---------------|-------|
| ChatGPT Ads | | direct | |
| Google AI Overviews / AI Mode | | via Search broad / AI Max / Shopping / PMax | no opt-out, no segment reporting |
| Microsoft Copilot | | via PMax / Search with logo / Shopping | no opt-out, no Copilot metrics |

## 4. Design
- Type: geo holdout / time-based on-off
- Treated regions: [list] · Holdout regions: [list] ([x]% of volume)
- Matching method: [past 8 weeks conversions, correlation ≥ 0.9]
- Freeze rules: no bid, budget or creative changes from week 3 to readout

## 5. Budget and power
| Arm | Test spend | Expected conversions | Readable (≥ 50)? |
|-----|-----------|----------------------|------------------|

## 6. KPIs
| KPI | Target | Source |
|-----|--------|--------|
| Incremental CPA | ≤ [target] | geo readout |
| Platform-reported CPA | ≤ [target × 1.3] in learning | platform |
| Brand-search lift | > 0 | search console / ads |
| CTR baseline | set in weeks 1-2 | platform |

## 7. Readiness checklist
- [ ] Server-side conversions live and deduplicated (OpenAI Conversions API / Google enhanced conversions / Microsoft UET)
- [ ] UTMs: `utm_source=<platform>&utm_medium=cpc&utm_campaign=<macro>`
- [ ] Product feed audited (attributes customers ask about, price, availability)
- [ ] Landing pages answer the top prompts in the first screen
- [ ] Logo + image assets uploaded (Copilot eligibility)
- [ ] Copy passed `answer_adjacent_copy_linter.py` (exit 0)
- [ ] AI-generated creative labelled where required

## 8. Readout (fill at end)
| Arm | Treated conv. | Holdout conv. (scaled) | Incremental | Incremental CPA | Decision |
|-----|---------------|------------------------|-------------|-----------------|----------|

Decision rule: scale if incremental CPA ≤ target; iterate inputs if within 30%; stop otherwise.
