---
name: channel-economics
description: >
  Channel economics: design and analyze the financial structure of go-to-market
  channels. Use when picking a channel mix, modeling partner margin or TCO,
  designing partner tiers and rebates, or analyzing channel conflict.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: commercial
  domain: business-growth
  updated: 2026-05-27
  tags: [channel-economics, channel-strategy, partner-program, margin-analysis, gtm, reseller, distributor, marketplace, msp]
---

# Channel Economics

End-to-end financial modeling and design of go-to-market channels: direct sales economics, reseller / distributor margin structures, marketplace fees, partner tier economics, channel conflict resolution, and the TCO frameworks that compare channel options apples-to-apples.

This skill provides the financial backbone for channel strategy. For strategic partnership design (which channel to invest in, how to structure the partnership), see `business-growth/partnerships-architect`. For partner-deal-level approval mechanics, see `business-growth/deal-desk`.

---

## When to use this skill

| Situation | Skill applies |
|-----------|---------------|
| Deciding direct vs partner-led for a new product | Yes — start with **channel model decision tree** |
| Designing a partner tier structure (silver/gold/platinum) | Yes — see **partner tier economics** |
| Modeling a specific partner deal's margin / payback | Yes — `scripts/channel_margin_calculator.py` |
| Analyzing channel conflict (overlapping direct + partner deals) | Yes — see **channel conflict** + `scripts/channel_mix_optimizer.py` |
| Building a partner program rebate / SPIFF structure | Yes — see **rebate design** |
| Comparing AWS Marketplace vs direct list-price economics | Yes — `scripts/channel_margin_calculator.py --channel marketplace` |
| Negotiating a specific partner contract | Use `business-growth/contract-and-proposal-writer` for the contract; this for the economics |
| Strategic partnership design (joint go-to-market, OEM, white-label) | Use `business-growth/partnerships-architect` first |

---

## The channel model decision tree

Six core channel models. Most companies use a mix.

```
What's the product's complexity + price point?

Low complexity, low price (< $10k ACV):
├── Self-serve / PLG → no channel
├── E-commerce → direct via web
└── Marketplace (AWS / Azure / GCP / Salesforce AppExchange) → if buyer already there

Medium complexity, mid-market price ($10k - $250k ACV):
├── Inside sales / SDR-led direct → if buyer journey is well-understood
├── Reseller / VAR (Value-Added Reseller) → if local presence / language matters
├── Marketplace → if buyer prefers procurement via existing relationship
└── Embedded / OEM → if your product is a component in someone else's offering

High complexity, enterprise ($250k+ ACV):
├── Direct field sales → standard for high-touch enterprise
├── Strategic SI / Integrator (Accenture, Deloitte, etc.) → if implementation is a substantial project
├── ISV / Embedded → if you're a feature in a larger platform
└── Reseller / Distributor → for regional or vertical specialty

Operational / managed-service buyer:
└── MSP (Managed Service Provider) → if customer wants outsourced operations
```

See [references/channel-models-direct-partner-marketplace.md](references/channel-models-direct-partner-marketplace.md) for each model in depth: economic structure, typical margin splits, when each works / fails, contract patterns.

---

## Margin and TCO framework

Apples-to-apples channel comparison requires a consistent TCO model. The naive comparison ("direct gets 100%, reseller gets 70%") misses critical costs.

### True channel TCO formula

```
Channel Contribution Margin
  = Channel-attributed Revenue
  − COGS
  − Partner Discount/Commission
  − Channel-specific Sales Cost (allocated)
  − Channel-specific Marketing Cost (MDF, co-marketing)
  − Partner Enablement Cost (training, certification)
  − Channel Operations Cost (channel manager headcount)
  − Channel-specific Support Cost (T1 partner support)
```

### Side-by-side comparison

For a $100k ACV deal:

| Component | Direct | Reseller (30% off) | AWS Marketplace |
|-----------|--------|---------------------|-----------------|
| Customer payment | $100,000 | $100,000 | $100,000 |
| Reseller / marketplace fee | $0 | -$30,000 (30% discount) | -$3,000 (3% AWS fee) |
| Revenue to us | $100,000 | $70,000 | $97,000 |
| COGS (15%) | -$15,000 | -$10,500 | -$14,550 |
| Sales cost (allocated CAC) | -$25,000 | -$5,000 | -$8,000 |
| Marketing cost (MDF / listing) | -$2,000 | -$8,000 | -$5,000 |
| Partner enablement (amortized) | $0 | -$3,000 | -$1,500 |
| Channel ops (amortized) | $0 | -$2,000 | -$1,000 |
| Support cost | -$5,000 | -$3,000 | -$5,000 |
| **Net contribution** | **$53,000** | **$38,500** | **$61,950** |
| **% of ACV** | 53% | 38.5% | 62% |

The "30% discount" reseller deal is more like 14.5% margin difference once everything's counted. Marketplace can look better than direct on per-deal basis (Amazon's sales team brings the buyer) — but volume varies.

Use `scripts/channel_margin_calculator.py --deal deal.yaml --channel <type>` to model this for any deal.

See [references/margin-and-tco-frameworks.md](references/margin-and-tco-frameworks.md) for the full TCO framework, per-cost-line guidance, and how to allocate "fully-loaded" sales / marketing / ops costs.

---

## Partner tier economics

Multi-tier partner programs (Authorized → Silver → Gold → Platinum) are common. Designed badly, they reward effort that isn't valuable; designed well, they reward outcomes that drive growth.

### Standard tier structure

| Tier | Annual revenue threshold | Discount % | Other benefits | Requirements |
|------|-------------------------|------------|----------------|--------------|
| Authorized | None | 10% | Standard support | Sign partner agreement; 1 certified person |
| Silver | $100k | 15% | Co-marketing eligible (limited MDF) | $100k achieved; 3 certified people; 2 customer wins |
| Gold | $500k | 20% + 5% rebate at threshold | Dedicated channel manager; MDF; deal registration; lead sharing | $500k achieved; 5 certified; 5 wins; 80% renewal rate |
| Platinum | $2M | 25% + 7% rebate at threshold | Top-tier support; joint roadmap; preferred status; press release rights | $2M achieved; 10 certified; 10 wins; 90% renewal; participation in advisory board |

### Tier design principles

1. **Outcome-based, not effort-based.** Reward revenue + retention, not training hours or marketing event count.
2. **Achievable but stretching.** Each tier should be a 12-18 month stretch from the prior.
3. **Differentiable benefits.** Each tier needs benefits a partner actively wants (not just "more support").
4. **Renewable status.** Tiers re-evaluated annually. Partners can move down if they don't maintain.
5. **Anti-gaming protection.** Discount-stacking, registration gaming, transfer pricing — design out.

Use `scripts/partner_tier_economics.py --tiers tiers.yaml` to model tier economics: gross margin per tier, partner-side incentive, break-even revenue per partner per tier.

---

## Rebate / SPIFF design

Three common reward structures, each with trade-offs:

### Front-end discount

Partner buys from you at a discount; sells to customer at list (or close). Margin = the spread.

**Pros:** Simple. Cash flow goes to partner immediately.
**Cons:** Hard to incentivize specific behaviors. Discount is locked in regardless of performance.

### Back-end rebate

Partner pays full price (or near it); earns rebate quarterly / annually based on revenue / tier achievement.

**Pros:** Ties reward to actual achievement; behaviors can be incentivized (e.g., bonus for selling new products).
**Cons:** Cash-flow burden on partner. Complex to administer.

### MDF (Marketing Development Funds) / SPIFF

Per-deal or per-period bonuses for specific actions: bring leads, attend events, certify staff.

**Pros:** Highly targetable. Rewards specific behaviors you want.
**Cons:** Easy to game; admin overhead high; partners often expect it without producing.

### Typical mix

| Partner type | Front-end | Back-end | MDF/SPIFF |
|--------------|-----------|----------|-----------|
| Reseller (transactional) | 70-80% of total comp | 10-20% | 5-10% |
| VAR (consultative selling) | 50-60% | 20-30% | 10-20% |
| Distributor (volume play) | 80-90% | 5-15% | 5% |
| ISV / Embedded | n/a (rev share) | 100% | 0 |
| MSP | 40-60% | 20-30% | 10-30% |

---

## Channel conflict

Channel conflict happens when multiple sales paths chase the same customer. Common forms:

### Direct-vs-partner conflict

| Scenario | Resolution pattern |
|----------|---------------------|
| Direct rep finds opportunity also touched by partner | Deal registration: first to register wins; partner gets credit if they brought it |
| Partner finds direct customer | If direct is already engaged: partner deferred (with consolation MDF perhaps); if not: partner leads |
| Customer asks for direct after partner-led pilot | Honor partner relationship for term; transition at next renewal if appropriate |

### Partner-vs-partner conflict

| Scenario | Resolution pattern |
|----------|---------------------|
| Two resellers both pursuing same account | First-registered wins; second is offered alternative leads / regional swap |
| Vertical specialist vs geographic | Vertical wins (customer values vertical expertise more) |
| New partner pursues incumbent partner's customer | Incumbent has right of first refusal for 90 days |

### Marketplace-vs-direct conflict

Customer can buy via AWS Marketplace OR direct. If price is lower direct, customer feels gamed. If price is same, why not just use marketplace? Common resolution:

- **Same price** direct vs marketplace (customer doesn't get punished for procurement choice)
- **Quota credit** to the direct rep when customer chooses marketplace (so rep isn't disincentivized)
- **Marketplace listing visibility** as a value-add, not as a different pricing channel

See [references/channel-conflict-resolution.md](references/channel-conflict-resolution.md) for the full conflict-resolution playbook including deal registration process, neutral arbitration, conflict-of-interest disclosure.

---

## Clarify First

Before modeling the channel economics, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Channel model(s) in scope** — direct, reseller/VAR, distributor, marketplace, OEM, or MSP (sets which decision-tree branch and TCO comparison to run)
- [ ] **Target ACV / price point** — sub-$10k vs mid-market vs enterprise (selects the viable channel branch and sizes per-deal margin)
- [ ] **Fully-loaded cost lines** — COGS %, allocated sales/marketing/ops/support costs (drives the TCO contribution-margin model, not just the headline discount)
- [ ] **Partner contribution + tier intent** — what the partner does (lead, sell, implement) and whether you're designing tiers/rebates (drives tier economics + rebate/SPIFF mix)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the model.

## End-to-end workflows

### Workflow: Design a new partner program

1. **Pick channel models** — direct + reseller? marketplace? OEM? — using the decision tree
2. **Model the economics** — `scripts/channel_margin_calculator.py` per channel option at expected ACV
3. **Design tier structure** — `scripts/partner_tier_economics.py` to size the gates and benefits
4. **Define rebate / SPIFF mix** — per tier and partner type
5. **Write the partner agreement** (with `business-growth/contract-and-proposal-writer`)
6. **Build channel ops** — deal registration, MDF approval, certification tracking
7. **Hire channel manager(s)** — usually 1 manager per 10-15 active partners
8. **Pilot with 3-5 partners** — measure, iterate, then scale

### Workflow: Evaluate a specific partner deal

1. **Inputs**: ACV, partner discount %, expected close, partner's contribution (lead source? sales effort? implementation?)
2. **Calculate net contribution** — `scripts/channel_margin_calculator.py --deal deal.yaml --channel partner`
3. **Compare to direct alternative** — would this deal have closed direct? at what cost?
4. **Decide**: approve / counter / decline (often via deal desk if it's a non-standard partner discount)

### Workflow: Channel mix analysis

1. **Inputs**: actual revenue by channel for last 4 quarters
2. **Run mix optimizer** — `scripts/channel_mix_optimizer.py --revenue revenue.csv` examines contribution margin per channel + identifies under-/over-invested channels
3. **Recommend rebalancing** — e.g., "Reseller channel: 20% of revenue, 8% of contribution margin — reduce investment; marketplace: 15% of revenue, 25% of contribution — increase listing visibility"
4. **Quarterly review**: present to CRO / CFO

### Workflow: Resolve a channel conflict

1. **Document the conflict** — accounts involved, parties, history
2. **Apply the registration rule** — first-registered partner wins absent overriding facts
3. **Consider exceptions** — strategic logo, customer preference, vertical expertise
4. **Communicate decision** — both parties, with reasoning, in writing
5. **Compensate the loser** — alternative leads, MDF, regional swap; preserve the relationship

---

## Anti-patterns

- **Direct + partner at same price.** Customer feels punished for not using direct (or vice versa); kills partner motivation. Price-to-customer must be consistent across channels.
- **Discount-only partner program.** Partners that only get a discount have no skin in your success; treat you as another vendor; switch easily.
- **Endless partner expansion without enablement.** Signing 200 partners that don't sell anything; channel manager headcount can't scale; partners stale.
- **Marketplace as afterthought.** Listing on AWS Marketplace without dedicated investment (listing optimization, co-sell programs) = marketplace generates nothing.
- **Channel manager as glorified email forwarder.** CM should drive partner pipeline, not just relay leads.
- **Rebates with no audit.** Partner self-reports revenue; you trust it; reality is 20% off. Build verification.
- **MDF spent on activities that don't drive pipeline.** Partner runs a great event, generates no pipeline. MDF should require pipeline outcome.
- **Channel conflict policy that isn't followed.** Policy says first-registered wins, but exec overrides every time → policy is theater.
- **Different commission per channel for same deal.** Direct rep gets 8% on $100k deal, channel rep gets 6% on $100k deal — direct rep refuses partner help; channel rep undercut.
- **OEM / embedded deals priced like resale.** OEM = customer doesn't see you at all; ASP can be 50-80% of list. Resale = customer sees you. Different economics; different price points.

---

## Tooling outputs

| Script | Input | Output |
|--------|-------|--------|
| `scripts/channel_margin_calculator.py` | Deal spec YAML + channel type | Per-channel net contribution margin, cost line breakdown, comparison vs direct baseline |
| `scripts/partner_tier_economics.py` | Tier definitions YAML | Per-tier: gross margin to us, gross margin to partner, partner break-even, tier graduation incentive analysis |
| `scripts/channel_mix_optimizer.py` | Revenue CSV (by channel + quarter) | Per-channel revenue contribution, per-channel margin contribution, recommended rebalancing |

All scripts: stdlib only, argparse CLI, JSON or markdown output.

---

## References

- [channel-models-direct-partner-marketplace.md](references/channel-models-direct-partner-marketplace.md) — 6 channel models in depth + economic structure + when each works
- [margin-and-tco-frameworks.md](references/margin-and-tco-frameworks.md) — full TCO framework, allocation guidance, per-channel cost models
- [channel-conflict-resolution.md](references/channel-conflict-resolution.md) — registration process, conflict patterns, arbitration

---

## Related skills

- `business-growth/partnerships-architect` — strategic partnership design (this skill = the economics; that one = the strategy)
- `business-growth/deal-desk` — approval mechanics for partner deals (this skill = "what does it cost"; deal desk = "should we approve")
- `business-growth/pricing-strategy` — sets list pricing that channel economics deviates from
- `business-growth/revenue-operations` — channel revenue is segmented in RevOps reporting
- `business-growth/contract-and-proposal-writer` — drafts partner agreements
- `sales-success/sales-operations` — runs channel ops (deal registration, MDF approval, certification tracking)
- `c-level-advisor/cs-cro-advisor` — strategic channel-mix decisions are CRO-level
