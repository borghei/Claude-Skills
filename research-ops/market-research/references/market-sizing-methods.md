# Market Sizing Methods

Deep reference for constructing, reconciling, and defending a market size.
Read this when the number will be challenged — by an investor, a board, a
finance partner, or a competitor's analyst.

## 1. What each layer actually means


The three-layer model is used loosely everywhere, which is why sizing arguments
so often talk past each other. Fix the definitions before you compute anything.

| Layer | Definition | The question it answers |
|-------|------------|-------------------------|
| **TAM** | Total annual revenue if every entity that has the problem bought a full solution from someone | "How big is the problem, in money?" |
| **SAM** | The share of TAM your product category, business model, geography, and regulatory posture can actually serve | "How much of that could our kind of product serve?" |
| **SOM** | The share of SAM you can win inside a stated horizon given your channels, capacity, and competition | "How much can we actually get, by when?" |

Three rules that prevent most disputes:

1. **TAM is about the problem, not your product.** If a change to your roadmap
   changes your TAM, you have computed a SAM and mislabelled it.
2. **SAM is where product and business-model constraints live.** Self-serve-only?
   That excludes buyers who require procurement. On-prem only? That excludes
   cloud-mandated buyers.
3. **SOM is where time and channel live.** A SOM without a horizon is
   meaningless, and a SOM without a named channel is a wish.

### Annual, recurring, and the flow/stock confusion

TAM is an annual flow figure. The single most common arithmetic error in sizing
is mixing a stock (installed base value, lifetime value, total contract value)
into a flow (annual revenue). Symptoms: a TAM that is 3-5x the plausible figure
and resists reconciliation.

Fix: state the unit as "annual recurring revenue at steady state" and convert
every input to that basis. Multi-year contracts divide by term. One-time
hardware amortises over replacement cycle. Transaction take rates multiply
annual volume, not cumulative volume.

## 2. Top-down construction


### The anchor

A top-down build starts from a published total and cuts it down with named
filters. The anchor's quality is the ceiling on the whole build.

| Anchor source | Trust | Notes |
|---------------|-------|-------|
| Government / statistical agency data | **[PROVEN]** highest | Census, trade bodies, regulators. Slow but auditable. |
| Public company segment disclosures | **[PROVEN]** high | 10-K/annual report segment revenue is audited. Summing public players gives a hard floor. |
| Industry association reports | **[RECOMMENDED]** | Usually member-surveyed; check the member base for bias. |
| Paid analyst market reports | **[RECOMMENDED]** with caution | Methodology is often opaque and definitions are broad by commercial design. |
| Press summaries of analyst reports | **[EXPERIMENTAL]** low | Second-hand; frequently misquotes the segment. Never use as the primary anchor. |
| A competitor's pitch deck | Do not use | Optimised for a different argument. |

### Filter design

Each filter is a multiplicative retention fraction with three attributes:

- **Name** — what it excludes, in plain language
- **Retention** — the fraction that survives it
- **Basis** — the evidence for that fraction

A filter without a basis is a guess wearing a decimal point. In review, every
filter gets challenged individually; the basis line is what survives the
challenge.

**Order filters from most defensible to least.** Geography first (usually
published), then firmographic qualification (usually countable), then
behavioural or competitive qualification (usually estimated). This way, a
reviewer who rejects your weakest filter can still use the layers above it.

### The stacking trap

Multiplicative filters compound fast. Five filters at 0.5 each retain 3%. That
is often correct, but it is also how a plausible TAM becomes an implausibly tiny
SAM without anyone noticing a single unreasonable step.

Guard: after every filter, restate the surviving population in units, not
currency. "We are now down to about 4,000 clinics" is checkable against reality
in a way that "€190M" is not.

### Overlap and double-counting

Filters are only multiplicative if they are independent. "Clinics with 3+
chairs" (0.45) and "clinics with revenue above €500k" (0.5) overlap heavily —
multiplying them to 0.225 understates the survivors badly, because most
large-revenue clinics are the same clinics that have 3+ chairs.

Fix: collapse correlated filters into one qualification criterion with a single
retention fraction derived from the joint distribution, not the product of the
marginals.

## 3. Bottom-up construction


### The unit base

Bottom-up starts from a countable population. The strength of the whole build
comes from the countability of that base.

Strongest to weakest unit bases:

1. **Regulated registries** — licensed practices, registered vehicles, certified
   installers. Published, audited, and updated.
2. **Employment statistics** — headcount in an occupation, from national labour
   data. Good proxy when the buyer is a role rather than an entity.
3. **Business registration data** — company counts by industry code. Watch for
   dormant registrations inflating the count, often 15-30%.
4. **Directory or platform counts** — listings on a marketplace or map service.
   Fast but includes duplicates and closures.
5. **Extrapolation from your own funnel** — valid only if your inbound is not
   segment-skewed, which it almost always is.

### Value per unit

Three ways to derive annual value per unit, in descending order of strength:

- **[PROVEN] Observed** — your own average contract value for that segment, or a
  public competitor's revenue divided by its disclosed customer count.
- **[RECOMMENDED] Budget-share** — the buyer's spend on the adjacent category
  multiplied by a substitution share. Works when you displace a known line item.
- **[EXPERIMENTAL] Value-share** — the economic value you create multiplied by
  the share you can capture, typically 10-25%. Defensible only with a documented
  value model and at least one closed deal at that price.

Do not use survey-stated willingness to pay as the value-per-unit input.
Stated WTP overstates realised price by a wide margin in most B2B categories.
Use it to rank options, not to size a market.

### Reach and win rate

SOM in a bottom-up build is `qualified units x reach x win rate x value`.

- **Reach** is the share of qualified units a named channel can put in front of
  a buying conversation inside the horizon. Derive it from channel capacity:
  sales headcount times meetings per rep per year, partner coverage by market,
  or realistic paid-acquisition volume at a tolerable CAC.
- **Win rate** is what fraction of those conversations close. Use your observed
  rate. If you have none, use 15-25% for a competitive replacement sale and
  30-40% for a greenfield sale where the alternative is doing nothing manually.

A reach figure above 40% in year one is almost always wrong. Channel capacity is
the binding constraint on nearly every early-stage SOM, and it is the constraint
most often left out of the model entirely.

## 4. Reconciliation


Building both chains is not busywork — the gap between them is the most
informative output of the exercise.

### Reading the divergence

| Pattern | Usual cause | Action |
|---------|-------------|--------|
| Top-down TAM >> bottom-up TAM | The published anchor covers a broader category or geography than your definition | Narrow the anchor or add an explicit scope filter; document which |
| Bottom-up TAM >> top-down TAM | Value per unit is too high, or the unit base includes non-buyers | Re-derive value per unit from observed contracts |
| TAMs agree, SAMs diverge | The two chains apply different qualification criteria | Align the qualification definition; usually one chain qualifies on firmographics and the other on behaviour |
| SAMs agree, SOMs diverge | Different implicit horizons or channel assumptions | State the horizon on both chains explicitly |
| Both chains agree exactly | Suspicious | Check whether the bottom-up inputs were back-solved from the top-down result |

That last row matters. Perfect agreement between two genuinely independent
builds is rare. When it happens, someone usually tuned one to match the other,
which destroys the entire value of doing both.

### The acceptable band

Within 3x at every layer is a healthy build. Between 3x and 10x, the memo needs
a paragraph naming the definitional difference. Above 10x, the two chains are
sizing different markets and the number is not ready to present.

## 5. Growth bridges


An anchor with a vintage older than about 18 months needs an explicit bridge to
the current period.

```
current_value = anchor_value * (1 + cagr) ** years_elapsed
```

Rules for the bridge:

- Show the raw anchor and the bridged figure side by side. Never silently
  present the bridged number.
- Source the CAGR separately from the anchor where possible. Using the same
  report's forecast CAGR compounds that report's optimism.
- Cap the bridge at three years. Beyond that the category definition itself has
  usually drifted and the bridge is compounding an obsolete taxonomy.
- For categories in active disruption, a bridge is inappropriate. Rebuild
  bottom-up instead.

## 6. Segmentation that changes decisions


A segmentation is only useful if the segments differ on something that changes
what you do. Test every proposed cut against three criteria:

1. **Differential** — do the segments have measurably different win rates,
   contract values, or retention? A difference under about 20% is noise.
2. **Addressable** — can you actually target the segment? A segment you cannot
   identify before the sale is a post-hoc description, not a targeting strategy.
3. **Stable** — will membership persist over the sales cycle and contract term?

### Variables ranked by usefulness

| Variable class | Examples | Typical usefulness |
|----------------|----------|--------------------|
| **Trigger event** | Funding round, regulatory deadline, system end-of-life, leadership change | **[PROVEN]** highest — predicts timing, not just fit |
| **Existing tooling** | Incumbent system, spreadsheet-based, nothing | **[PROVEN]** high — determines the sales motion and the objection set |
| **Regulatory obligation** | In scope for a specific standard or not | **[PROVEN]** high in regulated categories — obligation creates budget |
| **Operational structure** | Centralised vs distributed teams, in-house vs outsourced | **[RECOMMENDED]** — determines who the buyer is |
| **Firmographics** | Employee count, revenue band, industry code | **[RECOMMENDED]** as a proxy only — available but rarely causal |
| **Geography** | Country, region | Necessary for SAM, weak as a behavioural segment |
| **Persona archetypes** | Named fictional buyer profiles | **[EXPERIMENTAL]** — useful for communication, dangerous for sizing |

Start from firmographics because that data exists, then earn your way to trigger
events by instrumenting the funnel to capture why each deal started.

## 7. Presenting the number


The sizing memo should let a reviewer reconstruct the number without asking you
a question. Minimum contents:

1. **Market definition sentence** — one sentence, including geography and buyer
2. **Headline figures** — TAM, SAM, SOM with horizon, in one line each
3. **Both chains** — every step with its retention and basis
4. **The reconciliation gap** — stated, quantified, and explained
5. **The three assumptions the number is most sensitive to** — with the range
6. **What would change the answer** — the specific observations that would move
   it materially

### Sensitivity is not optional

Every sizing has two or three assumptions that dominate the result. Identify
them by varying each input by ±50% and ranking by the swing in SOM. Report the
top three with their plausible ranges. A memo that presents a point estimate
without a sensitivity range invites the reviewer to assume the point estimate
was chosen to flatter the conclusion.

### Ranges beat point estimates

Present SOM as a band with a stated base case: "€8-15M obtainable within three
years, base case €11M." A single number implies a precision the method does not
have, and reviewers who know that will discount the whole memo. A band
communicates the same central estimate while being honest about the method.

## 8. Growth and forecast modelling


A market size is a snapshot. Most decisions need a trajectory.

### Three forecast approaches

| Approach | Mechanism | Best for |
|----------|-----------|----------|
| **Category CAGR applied** | Grow the whole market at a published rate | Established categories with credible published growth |
| **Adoption curve** | Model penetration over time toward a ceiling | New categories replacing an existing behaviour |
| **Driver-based** | Model the underlying units and value separately | When units and price move independently |

**[RECOMMENDED]** Driver-based wherever you can get the inputs. Applying a single
CAGR hides the case where unit growth is strong and price is collapsing — which
is common in software categories and completely changes the investment case.

### Adoption ceilings

A penetration model needs a ceiling, and the ceiling is usually not 100%. Some
share of any market will never adopt: they lack the trigger, are contractually
locked in, or the alternative genuinely suits them better.

Setting the ceiling from a comparable category's observed plateau is more
defensible than assuming full penetration. State it explicitly — an unstated
ceiling of 100% is a large hidden assumption.

## 9. Competitive structure


Market size alone does not tell you whether the market is worth entering. Two
markets of identical size behave completely differently depending on structure.

| Structure | Signal | Implication |
|-----------|--------|-------------|
| **Fragmented** | No player above ~10% share | Entry is easy, differentiation is hard, consolidation may be the play |
| **Consolidating** | Top 3 gaining share | Window is closing; entry needs a wedge |
| **Concentrated** | Top 2 above 60% combined | Entry requires displacing an incumbent; budget accordingly |
| **Monopolistic** | One player above 70% | Only viable via an underserved segment or a regulatory shift |

### Estimating share without published data

- **Sum the knowable.** Public company disclosures plus credible private
  estimates give a floor. The residual is the long tail.
- **Employee-count proxy.** Competitor headcount in revenue-generating roles,
  times a plausible revenue-per-head for the category, gives an order of
  magnitude.
- **Customer-count proxy.** Public logo counts times a plausible average contract
  value.
- **Win/loss data.** Your own funnel tells you who you actually meet in deals,
  which is a better read on the *addressable* competitive set than any market
  report.

That last one is undervalued. Analyst competitive sets and the competitors you
actually encounter in deals frequently differ, and yours is the one that matters
for your SOM.

## 10. Pricing and value capture


SOM depends on the price you can hold, not the price you list.

| Consideration | Effect on sizing |
|---------------|------------------|
| **Discounting reality** | Model at realised price, not list. A category discounting 20-30% has a SOM 20-30% below the list-price model |
| **Land-and-expand** | Initial contract value understates account value; model both first-year and steady-state |
| **Seat vs consumption pricing** | Consumption revenue grows with customer usage; seat revenue does not. Different growth profiles from the same customer count |
| **Multi-year discounts** | Convert to annual value; do not book total contract value as annual |
| **Channel margin** | Partner-sold revenue nets down by the partner's margin. Model net, and say which you are reporting |

Channel margin is the most commonly missed. A SOM built on gross customer spend
through a channel that takes 25-40% overstates your revenue by that margin.

## 11. Sanity checks before you present


Run all of these. Each has caught a materially wrong number.

- **Reverse the arithmetic.** Divide SOM by your average contract value. Is that
  customer count plausible given your channel capacity and sales headcount?
- **Compare to a known player.** Does your TAM imply the largest incumbent has an
  implausibly small or large share?
- **Check per-unit spend against reality.** Does your value-per-unit imply a
  buyer spending more on this category than they plausibly spend on all software?
- **Check the growth implied.** Does hitting SOM require a growth rate no company
  in the category has achieved?
- **Ask what the number would be if you halved your weakest assumption.** If SOM
  falls by more than half, the memo needs to lead with that sensitivity.
- **Show it to someone hostile.** The reviewer most likely to challenge it should
  see it before the audience that will act on it.

The reverse-arithmetic check is the highest-yield of these. Converting a currency
figure back into customers, and then into sales capacity, exposes implausibility
that no amount of staring at the currency figure will.

## 12. Failure modes checklist


Run this before the number leaves your machine.

- [ ] Market definition is one sentence and includes geography and buyer
- [ ] Every figure is an annual flow, not a stock or a multi-year total
- [ ] Anchor vintage is stated; a bridge is applied and shown if over 18 months
- [ ] Every filter has a named basis, not just a number
- [ ] Correlated filters have been collapsed rather than multiplied
- [ ] Surviving population is restated in units after each layer
- [ ] Bottom-up unit base comes from a countable source, named
- [ ] Value per unit is observed or budget-derived, not survey-stated WTP
- [ ] Reach is derived from a named channel's actual capacity
- [ ] Win rate is observed, or a stated comparable with the comparison named
- [ ] Both chains built independently; neither back-solved from the other
- [ ] Divergence quantified at each layer and explained in prose
- [ ] SOM has an explicit horizon in the headline
- [ ] Top three sensitivities identified with ranges
- [ ] SOM presented as a band with a base case
