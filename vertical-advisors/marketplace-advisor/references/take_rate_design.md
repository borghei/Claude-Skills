# Take-Rate Design

Take rate (the % of GMV the marketplace keeps) is the core pricing decision for any marketplace. Too low: the business doesn't have enough margin. Too high: supply churns to alternatives or off-platform.

---

## Take Rate Benchmarks

| Marketplace | Take rate | Notes |
|-------------|-----------|-------|
| eBay | 10-13% | Plus listing fees, payment processing |
| Etsy | 6.5% transaction + 3% payment + ad fees | Lower base; ad-spend-driven uplift |
| Amazon (3P) | 8-15% referral fee | Plus FBA fees, advertising |
| Airbnb | ~14% blended | Split between host (3%) and guest (~14%) |
| Uber / Lyft | 25-30% | Higher because of full-stack: vehicle dispatching, payments, dispute resolution |
| DoorDash | 15-30% | Variable by tier; restaurants negotiate |
| Upwork | 5-20% | Tiered: 20% on first $500/client, scales down to 5% over $10k |
| Stripe Marketplace | 0% (Stripe is payment infra) | Marketplace operator sets their own |
| Wholesale B2B (Faire, etc.) | 15-25% on first order, lower on repeat | High first-order to subsidize discovery |
| Real estate (typical) | 5-6% (split commission) | Post-NAR-settlement structure shifting |
| App Store / Play Store | 15-30% | Heavily-debated; dropped to 15% for small developers and subscriptions in year 2 |
| OpenTable | $1-$2.50 per cover | Per-transaction, not %, suited to thin restaurant margins |
| Bookings (hotels) | 15-20% | Plus paid placement |

---

## Choosing a Take Rate

Two questions drive take rate:

1. **What % of supplier margin are you taking?**
   - Take rate ÷ supplier blended margin = % of margin captured
   - Above ~50% — suppliers feel squeezed; churn risk
   - Below ~25% — you're leaving money on the table or haven't built enough value-adds

2. **What other competitors / alternatives do suppliers have?**
   - Off-platform direct sales — your take rate must be worth the marketplace's value
   - Other marketplaces — their take rate sets the ceiling
   - Owning the customer relationship — for repeat / subscription, take rate too high drives off-platform

### Examples

- **Restaurant pickup/delivery:** restaurants run 5-15% net margin. A 30% take rate eats *all* the margin or more. This is why most restaurants hate delivery platforms.
- **Hotels:** hotels run 30%+ net margin on bookings. A 15-20% take rate is sustainable.
- **Freelance services:** freelancers' "margin" is their hourly rate; a 20% platform fee feels like a tax. Marketplaces bring back leverage by aggregating clients.
- **High-touch services (real estate, law):** historically 5-10% commissions; sustainable because of high deal size.

---

## When to Raise Take Rate

Take rate ratcheting up over time is the most common evolution:

1. Start low to attract supply
2. Add value-adds: payments, escrow, dispute resolution, insurance, fulfillment, financing, marketing tools
3. Each value-add justifies a higher take rate
4. Communicate the increase as "we're now offering X" rather than "we're raising fees"

Common mistakes raising:
- Raising without any new value-add — supplier churn
- Raising in a category with high off-platform substitution — leakage spikes
- Raising on existing inventory in flight — inventory pulled

Common mistakes not raising:
- "We can't ever raise" — eventually someone with deeper pockets undercuts you on take rate. You need higher take rate ammunition.

---

## When to Lower Take Rate

Lowering is rare and usually defensive:
- Competitor with deeper pockets undercuts
- Macro environment compresses supplier margins (Covid, recession, rate environment)
- Supply churn signals take rate is structurally too high

Permanent lowering is worse than expected — a 1% lower take rate forever is a meaningful business model change. Prefer temporary promotional lower take rates over permanent reductions.

---

## Differential Take Rate Strategies

Most mature marketplaces don't have one take rate; they have many.

**By tier:** higher take rate for new suppliers, lower for tenured. Encourages stickiness.

**By transaction size:** Upwork's example — 20% on first $500, 10% on $500-$10k, 5% above $10k. Tiered to align platform's value (matching) with supplier value (managing client relationship).

**By category:** Amazon has different referral rates per category. Reflects different category dynamics.

**By promo / featured placement:** sometimes labeled "advertising" rather than take rate but is effectively take rate uplift.

**By value-add bundle:** core matching at lower rate; full-stack (payments + insurance + financing) at higher rate.

---

## Full-Stack vs. Lean Marketplaces

**Lean marketplace:** matching only. Supply contacts buyer directly post-match. Lower take rate (5-15%). Higher leakage risk. Examples: Craigslist, classifieds.

**Full-stack marketplace:** marketplace owns end-to-end transaction (payments, fulfillment, dispute, sometimes more). Higher take rate (15-30%+). Lower leakage. Examples: Uber, Airbnb, DoorDash, modern B2B marketplaces.

**Trend:** most modern marketplaces are full-stack or moving toward it. The take rate ceiling for lean marketplaces gets squeezed every year.

---

## Same-Side Pricing (Both Sides Pay)

Some marketplaces charge both sides:
- **Eventbrite:** event organizers pay listing/transaction; attendees pay processing
- **Airbnb:** host pays small fee; guest pays larger fee
- **OpenTable:** restaurants pay per-cover; diners free
- **Most B2B marketplaces:** suppliers pay; buyers free or low fee

The decision: who has more elastic willingness to pay? Subsidize the side that's harder to recruit; tax the side that already wants to be there.

---

## Common Mistakes

1. **Setting take rate without supplier-margin context.** A 20% take rate is fine in some categories, kills others.
2. **Static take rate.** Mature marketplaces are tiered, differentiated, evolved.
3. **Confusing "advertising" with "take rate."** From the supplier's perspective, paid placement is a tax.
4. **Ignoring leakage.** Take rate too high drives suppliers to migrate the relationship off-platform.
5. **No value-add expansion plan.** Take rate is sustainable only if the platform keeps adding value.
6. **Cross-side imbalance.** Charging the wrong side drives churn on the harder-to-recruit side.

---

## Take-Rate Decision Worksheet

Before setting take rate:

1. **Estimate supplier blended margin** — gross margin on the transactions running through your platform
2. **Decide capture %** — what % of that margin is sustainable? 25-50% is typical for full-stack; 10-25% for lean
3. **Convert to take rate** — capture % × supplier margin %
4. **Compare to competitors / alternatives** — am I in range? Above? Below?
5. **Plan trajectory** — what value-adds do I add to justify higher take rate over time?
6. **Plan tier structure** — flat or tiered? By size, category, tenure?

Most marketplaces refine take rate quarterly or annually as they learn their unit economics.
