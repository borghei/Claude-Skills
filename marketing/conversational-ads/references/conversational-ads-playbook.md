# Conversational Ads Playbook

How ads next to AI answers differ from search ads, and how to plan, write, launch and read a first test. Platform facts live in [platform-specs.md](platform-specs.md); this file is the method.

---

## 1. What is actually different

| Dimension | Classic search ad | Answer-adjacent ad |
|-----------|-------------------|--------------------|
| Intent signal | A 2-4 word query | A multi-turn conversation; platforms match on the conversation and on the answer content (Google: query **and** AI Overview content; Microsoft: the entire conversation; OpenAI: conversation context) |
| Control | Keywords, match types, placements | Mostly none: broad match / PMax / contextual matching; Google and Microsoft give no opt-out and no placement reporting |
| User state | Scanning ten links | Reading one synthesised answer they already trust |
| Creative job | Win the click against nine competitors | Add something the answer did not: a specific spec, price, availability, a next step |
| Failure mode | Low CTR | Looking like you hijacked the answer — a trust cost to both brand and platform |
| Measurement | Placement-level reporting | ChatGPT: own reporting. Google/Microsoft: blended with Top ads / search; needs incrementality tests |

**Consequence:** you cannot optimise conversational placements the way you optimise keywords. You optimise **inputs** (feeds, assets, landing pages, negatives) and **read outcomes with experiments**.

---

## 2. Planning sequence [RECOMMENDED]

1. **Collect real prompts.** 20-50 prompts customers actually ask assistants about your category — from sales calls, support tickets, site search, and your own tests in each assistant. Tag each with a stage: `research`, `compare`, `purchase`, `support`.
2. **Check eligibility first.** Category (sensitive verticals are excluded on ChatGPT and AI Overviews), market, language. `conversational_ad_planner.py` does this.
3. **Fix inputs before spend:**
   - Product feed complete: title with the attributes people ask about (width, material, compatibility), price, availability, GTIN.
   - Logo and image assets (Microsoft requires a logo for Search ads to appear in Copilot).
   - Landing page that answers the prompt in the first screen — not a generic home page.
   - Negative keywords (they apply in Copilot) and brand exclusions where available.
4. **Pick the test design** (section 5) and the minimum budget that gives ≥50 conversions per arm.
5. **Write copy per platform** (section 4), then run `answer_adjacent_copy_linter.py`.
6. **Launch, hold 2 weeks for learning, read at 6 weeks.** Do not change bids, budgets or creatives in the holdout-comparison window.

---

## 3. Channel roles

| Platform | Best-fit stage | Why | Lever you actually pull |
|----------|----------------|-----|-------------------------|
| ChatGPT Ads | Research, compare | Long, exploratory conversations; direct buying with own reporting | Campaign, ad group, creative variations, bids, product feed |
| Google (AI Overviews / AI Mode) | Compare, purchase | Shopping ads and feed-based matching inside commercial queries | Broad match / AI Max, Shopping and PMax feeds, assets, negatives |
| Microsoft Copilot | Research, compare (B2B skew on desktop) | Conversation-level matching; PMax recommended | PMax, logo and image extensions, feeds, negatives |

The planner turns your prompt list into a mix using these stage weights. Override it when your own data disagrees.

---

## 4. Creative guidelines for answer-adjacent ads

### Do [RECOMMENDED]
- **Lead with a concrete fact** the answer may not contain: size range, weight, price, delivery time, compatibility.
- **One idea per variation.** OpenAI's guidance: distinct angles per title/copy, many variations, useful and accurate.
- **Match the prompt's vocabulary.** If people ask about "wide feet", say "wide fit", not "inclusive sizing".
- **Use a soft, specific CTA:** "Compare widths", "See sizes", "Check delivery date".
- **Keep ChatGPT titles at 16-24 characters and copy at 32-48** (OpenAI recommendation); Google/Microsoft RSA hard limits are 30/90.
- **Keep claims provable.** Superlatives and health, environmental or price claims need evidence on file.

### Don't
- Don't imply the assistant endorses you ("ChatGPT recommends", "Copilot's pick", "AI-verified"). The platforms separate ads from answers on purpose; OpenAI prohibits false endorsements.
- Don't use urgency or pressure copy next to a neutral answer.
- Don't quote testimonials or star ratings unless verified and disclosed (FTC 16 CFR Part 465 / 255).
- Don't mirror answer formatting to look organic. The "Sponsored" label is there regardless, and mimicry erodes trust.
- Don't write copy for sensitive prompts (health, money trouble, legal problems) — ads won't be eligible there and the attempt reads as exploitative.

---

## 5. Test design and measurement

### Design options

| Design | When | How | Readout |
|--------|------|-----|---------|
| **Geo holdout** [RECOMMENDED] | ≥ 10 comparable regions (states, DMAs, provinces) | Match regions on past conversions; turn conversational spend off in 10-20% | Incremental conversions = treated − holdout (scaled to treated size) |
| **Time-based on/off** | Few regions, stable demand | Alternate 2-week on/off blocks, at least 3 cycles | Difference-in-means across blocks; weaker, confounded by seasonality |
| **Platform conversion lift** | Platform offers a lift study | Use when available for the account | Cross-check with your own geo read |
| **Pre/post** [not recommended] | Never as the only read | — | Confounded by everything |

For Google and Microsoft there is **no AI-placement switch**, so the holdout tests the **whole campaign change** that made you eligible (e.g. moving to broad match / AI Max / PMax). Say so in the readout.

### Measurement stack
1. **Server-side conversions** on every platform (OpenAI Conversions API, Google enhanced conversions, Microsoft UET + offline conversions), deduplicated against browser tags.
2. **UTMs** on every destination URL: `utm_source=chatgpt|google|bing`, `utm_medium=cpc`, campaign IDs via macros (`{campaign_id}` etc. on ChatGPT). Paid traffic then stays out of GA4's organic **AI Assistant** channel.
3. **Incrementality read** at the end of the test; platform-reported conversions are a secondary metric.
4. **Brand-search lift** in holdout vs treated regions — conversational ads often show up as brand search later.

### KPI targets
- Learning-period CPA ceiling: target CPA × 1.3.
- Readable test: ≥ 50 conversions per arm (planner default; raise to 100 for tighter intervals).
- Success: incremental CPA ≤ target CPA, or incremental ROAS ≥ AOV / target CPA.
- CTR: no public benchmarks exist yet for these placements — set your own baseline in weeks 1-2 rather than borrowing search CTRs.

---

## 6. Risks and how to handle them

| Risk | Mitigation |
|------|------------|
| Ads appear next to answers you disagree with (competitor recommended, wrong facts) | You cannot choose the answer. Fix the facts on your own pages and feed; that is what the answer draws on |
| No placement reporting (Google, Microsoft) | Incrementality design; do not attribute blended lift to AI placements alone |
| Brand safety in open-ended conversations | Negatives, brand exclusions, sensitive-topic exclusions are platform-side; audit search-term and asset reports weekly |
| Category ineligible (health, finance, alcohol...) | Plan classic search/social instead; ChatGPT finance/health/legal via manual approval only |
| Platform facts change mid-test | Re-check platform-specs.md sources at test start and at readout; log any change in the test record |
| AI-generated creative | Label where required (EU, India, New York; Google AI label setting) |
