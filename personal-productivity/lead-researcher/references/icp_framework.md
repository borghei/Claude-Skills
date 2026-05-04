# ICP Framework

An Ideal Customer Profile (ICP) is a structured definition of which accounts are worth pursuing. A good ICP retroactively predicts your wins and disqualifies your worst-fit losses. A bad one is wishful thinking dressed up in a spreadsheet.

---

## What an ICP Is — and Is Not

| Is | Is Not |
|----|--------|
| A scored set of must-haves and disqualifiers | A persona |
| Derived from your closed-won customers | A pitch deck slide |
| Versioned and refreshed quarterly | A static document written once |
| Predictive of deal velocity | A list of every company you'd "love to sell to" |

A persona describes the buyer (their role, pain, day-to-day). The ICP describes the **account** (industry, size, geography, signals). You need both, but the ICP is what powers prospecting.

---

## Building an ICP From Existing Data

1. **Pull last 20-50 closed-won customers.** Skip anyone you closed under unusual circumstances (relationship deal, M&A win, etc.).
2. **List the shared attributes** — industry, employee count, ARR or revenue band, geography, tech stack, growth stage, funding round.
3. **Find the differentiators** — attributes that describe wins but *not* losses.
4. **Categorize**: Must-have, Nice-to-have, or Disqualifier.
5. **Pressure-test**: Score last quarter's closed-lost accounts. Most should land below your A tier. If they don't, your ICP is too loose.

---

## Must-Have Attributes

These are non-negotiable. A lead missing one drops a tier. Examples:

- **Company size:** "50-1000 employees" — your product breaks below 50 and the buyer profile changes above 1000.
- **Industry:** "B2B SaaS" — you don't have the playbook for marketplaces or services businesses.
- **Geography:** "US, UK, EU" — you don't ship to anywhere with extra compliance overhead yet.
- **Tech stack signal:** "Uses Snowflake or BigQuery" — your product integrates with these and not with smaller warehouses.

---

## Nice-to-Have Attributes

Half-weighted. Stack enough of these and a borderline account moves up. Examples:

- **Recent funding round** (signals budget)
- **Hiring spike in target buyer's department** (signals pain)
- **Public quote about the problem you solve** (signals self-aware buyer)
- **Already buys an adjacent / complementary product**

---

## Disqualifiers

Any hit immediately drops the lead. Examples:

- **Existing competitor contract under 12 months old** (you'll lose the cycle)
- **Revenue under $1M ARR** (can't afford your floor)
- **Industry: government or defense** (you don't have FedRAMP)
- **Customer of a known parent company already on a global enterprise contract**

---

## ICP by GTM Motion

ICPs differ structurally by motion:

| Motion | What ICP emphasizes |
|--------|---------------------|
| **Sales-led (mid-market+)** | Account-level fit (size, industry, contract value), buying-committee composition |
| **PLG / self-serve** | Individual buyer fit (role, team size), product-usage signals over firmographic data |
| **Channel / partner** | Partner economics (margin per deal, partner-led pipeline %), end-customer fit secondary |

If you mix motions, **maintain separate ICPs**. A merged ICP is a vague ICP.

---

## Worked Example

A B2B SaaS analytics product targeting mid-market SaaS companies:

```json
{
  "name": "Mid-Market SaaS — Data Team Buyer",
  "must_have": [
    { "field": "industry", "value": ["saas", "software"], "weight": 20 },
    { "field": "size", "min": 100, "max": 2000, "weight": 20 },
    { "field": "country", "value": ["US", "UK", "DE", "FR", "NL"], "weight": 10 }
  ],
  "nice_to_have": [
    { "field": "signals", "value": ["snowflake", "bigquery", "dbt"], "weight": 10 },
    { "field": "signals", "value": ["series b", "series c"], "weight": 10 },
    { "field": "signals", "value": ["hiring data engineer", "head of data"], "weight": 10 }
  ],
  "disqualifiers": [
    { "field": "industry", "value": ["government", "defense"] },
    { "field": "size", "min": 0, "max": 50 }
  ]
}
```

---

## Refresh Cadence

- **Quarterly:** Re-score last quarter's wins and losses; tune weights.
- **After major product changes:** New integrations or capabilities reshape the ICP.
- **After major market changes:** Funding climate, regulation, competitor moves.

If your ICP is older than a year, it's lying to you.

---

## Common Mistakes

- **Including every customer in the derivation.** Outliers (referral wins, unusual contracts) bias the model.
- **All must-haves, no disqualifiers.** Disqualifiers are where the leverage is — they protect rep time.
- **Static weights.** Re-tune based on which signals actually predicted wins.
- **Confusing TAM with ICP.** Total Addressable Market is who *could* buy. ICP is who *should* be hunted today.
