# Marketplace Dynamics

Two-sided and multi-sided marketplaces have distinctive economics that don't translate from SaaS or ecommerce playbooks. This guide is the founder's-eye view.

---

## The Chicken and Egg Problem

A new marketplace has nothing on either side. Suppliers won't join without buyers; buyers won't come without suppliers. This is the chicken-and-egg problem and it's the largest reason new marketplaces fail.

### Strategies for cracking it

**1. Subsidize the constrained side.**
- For most marketplaces, supply is the harder side to acquire.
- Pay (or heavily subsidize) early supply to build a base.
- Examples: Uber paying drivers minimum hourly during ramp; Airbnb paying photographers to upgrade listings.
- Risk: subsidy doesn't end gracefully; the side becomes dependent.

**2. Single-player mode.**
- Build a tool one side can use even without a marketplace.
- Once enough single-player users exist, flip on the marketplace dynamics.
- Examples: OpenTable started as restaurant software; Calendly started as scheduling tool; some B2B marketplaces start as supplier CRM.
- Best when one side has a real standalone value prop.

**3. Vertical wedge.**
- Pick a narrow vertical and dominate it.
- Once liquid in that vertical, expand horizontally.
- Examples: Etsy (handmade), Houzz (home renovation), Upwork (freelance specifics by category).

**4. Geographic concentration.**
- Build to liquidity in one city, then replicate.
- Examples: Uber, DoorDash, every food-delivery and ride-share.
- Critical metric: don't expand to a new city until the current one is liquid.

**5. Bring an existing audience.**
- A founder with access to an existing audience starts above zero.
- Examples: Substack (writers leveraging existing followers), creator-economy marketplaces.

**6. Curated / hand-built supply.**
- Manually onboard the first 100-1000 supply units to bootstrap.
- Examples: Airbnb founders going door-to-door; many B2B marketplace founders cold-outreaching for first suppliers.

---

## Liquidity

The single most important marketplace metric.

**Definition:** A marketplace is **liquid** when buyers can reasonably expect to find what they need, and suppliers can reasonably expect their listings to transact.

**Liquidity proxies:**
- **Fill rate:** % of listings / requests that result in a transaction
- **Search-to-purchase rate:** % of searches converting to a transaction
- **Time-to-fill:** how long a listing / request takes to match
- **Repeat usage:** liquid marketplaces drive repeat behavior

**The minimum viable market unit:**

Liquidity is local. A marketplace can be liquid in San Francisco for food delivery and not liquid in Sacramento. Always measure liquidity at the **smallest market unit** at which liquidity matters:
- Geographic (city, ZIP code, neighborhood)
- Category (cuisine type, product subcategory, service type)
- Time (weekend brunch, weekday rush)

The single biggest mistake new marketplace founders make is measuring liquidity globally instead of per-market-unit.

---

## Supply / Demand Balance

A marketplace can have plenty of both supply and demand and still fail if they don't match in time, place, or attribute.

**Imbalance patterns:**
- **Over-supply:** Many suppliers, few buyers per supplier. Suppliers churn from low transaction volume.
- **Under-supply:** Many buyers, few suppliers. Buyers search and don't find. Quality drops as supply scrambles to match.
- **Quality mismatch:** Supply exists but doesn't match buyer specifications.
- **Time mismatch:** Supply is available 9-5 weekdays; buyers want it weekends.
- **Geographic mismatch:** Supply concentrated in one part of city; buyers spread.

**Diagnosing imbalance:**
- High search-to-purchase: under-supply or quality mismatch (buyers can't find what they want)
- Low transactions per supplier: over-supply (suppliers idle)
- High supplier churn: over-supply or quality decline

---

## Network Effects: Real and Fake

Many "marketplaces" don't actually have network effects.

**Real network effects:**
- More supply → buyers more likely to find what they want → more buyer demand
- More buyers → suppliers more likely to transact → more supply attracted
- Result: switching cost grows with marketplace growth; defensibility compounds

**Common fake network effects:**
- "More users = more brand awareness" — that's brand, not network effects
- "More users = more data" — that's a data flywheel, not strict network effects
- "More content" — only network effect if content is contributed by users *and* attracts more users

**Question to ask:** if a competitor copies your product perfectly, does your existing scale provide defense? If yes, real network effects. If no, you're not really a marketplace — you're a directory or a shop.

---

## Cross-Side Network Effects vs. Same-Side

**Cross-side (positive):** more buyers attracts more suppliers and vice versa. The good kind.

**Same-side (positive):** more buyers attracts more buyers (e.g., social proof, FOMO).

**Same-side (negative):** more suppliers competes against existing suppliers (commoditization). This can hurt the platform — suppliers feel commodified and disengage.

Strong marketplaces have positive cross-side and ideally positive same-side. Negative same-side requires careful management (e.g., curation, artificial scarcity, branding to differentiate suppliers).

---

## Vertical vs. Horizontal Marketplaces

| Vertical | Horizontal |
|----------|-----------|
| Single category specialization | Multi-category |
| Examples: Houzz, Stitch Fix, Convoy | Examples: Amazon, eBay, Mercado Libre |
| Easier to reach liquidity | Network effects compound across categories |
| Tighter fit / better experience | Lower per-category quality |
| Smaller TAM but defensible | Larger TAM, harder to defend at start |

**Default:** start vertical. Horizontal expansion often comes after winning a vertical.

---

## Off-Platform Leakage

Once buyers and suppliers connect on a marketplace, they may transact off-platform to avoid the take rate. This is the "leakage" problem.

**Why it happens:**
- Take rate too high relative to perceived platform value
- Repeat transactions where the relationship is established
- Personalized / customized work where matching value is concentrated in the first match

**Mitigations:**
- Add value-adds beyond matching: payments, insurance, escrow, dispute resolution, fulfillment, financing, scheduling
- Tie ongoing transactions to platform-only features (reviews, scheduling, history)
- Subscription models for repeat buyers / suppliers
- Penalize off-platform transactions in trust / ranking

If leakage is high, the marketplace is essentially infrastructure for the first match only.

---

## Common Mistakes

1. **Measuring liquidity globally.** Always per-market-unit.
2. **Premature horizontal expansion.** Adding categories before the first is liquid.
3. **Subsidy without exit plan.** Subsidies that can't end become structural costs.
4. **Ignoring leakage.** Off-platform transactions kill GMV-derived economics.
5. **Confusing GMV with health.** A marketplace with $10M GMV across 50 cities is mostly broken.
6. **Pricing the take rate by guess.** Take rate determines supplier economics; benchmarks matter.
7. **Building marketplace mechanics without enough supply / demand asymmetry to justify a marketplace.** Some "marketplaces" should have been single-product businesses.

---

## Resources

- **a16z marketplace content:** a16z.com/marketplaces
- **Greylock marketplace playbook**
- **Lenny Rachitsky's marketplace newsletter** — Hacks marketplace economics
- **Sangeet Paul Choudary — Platform Revolution** — book
