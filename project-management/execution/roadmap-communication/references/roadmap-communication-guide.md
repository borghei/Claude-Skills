# Roadmap Communication Guide

A reference on roadmap framing across audiences. Covers the origin of Now/Next/Later, Marty Cagan's "right-size the roadmap" principle, the outcome-vs-feature debate (Cagan, Torres), and worked examples of all three variants for the same project.

---

## Part 1: The Now / Next / Later structure

Janna Bastow (co-founder of ProdPad) introduced the **Now / Next / Later** framework in 2014 as an antidote to Gantt-style roadmaps that promised features 12 months out and then disappointed. The structure is simple:

- **Now (in flight or starting imminently)** -- specific commitments, dates, high confidence
- **Next (next 1-2 quarters)** -- themes, not features; medium confidence
- **Later (beyond)** -- directions and bets; low confidence by design

It worked because it made the **confidence gradient explicit**. A team can commit to "Now" with conviction; "Next" is a working hypothesis; "Later" is a north star. Audiences understand the gradient because the structure encodes it.

### Why the alternatives fail

| Format | Why it fails |
|--------|--------------|
| Gantt by feature | Implies commitments at every date the bar crosses; teams cannot honor 9-month feature commitments |
| Quarter columns ("Q1 / Q2 / Q3 / Q4 features") | Same problem; teams over-promise far quarters to look complete |
| Backlog as roadmap | Backlog is prioritization, not commitment; cannot be shared upstream |
| One-pager "we will do these 30 things this year" | Confidence-blind; treats year-out items as equivalent to next-week items |

---

## Part 2: Cagan's "right-size the roadmap"

Marty Cagan argues that the right format for a roadmap depends on **how confident the team can be** at each horizon. His rule of thumb:

| Horizon | Confidence | Right level of commitment |
|---------|------------|---------------------------|
| 2-4 weeks | High (>80%) | Specific feature with date |
| 1 quarter | Medium-high (~70%) | Specific feature with target sprint |
| 2 quarters | Medium (~50%) | Theme, not feature |
| 1 year | Low (<30%) | Direction or bet |
| Multi-year | Very low | Vision statement only |

Roadmap formats that ignore this gradient (committing to specific features 12 months out) trade short-term clarity for long-term credibility loss. Customers learn that roadmap items at the right end of the timeline are decorative.

---

## Part 3: Outcome vs feature roadmaps

A second axis: what is the unit of work on the roadmap -- a customer outcome (something the user achieves) or a feature (something the team builds)?

### The outcome case (Cagan, Torres)

Marty Cagan and Teresa Torres (Continuous Discovery Habits) argue that outcomes are the only durable roadmap unit:

- An outcome ("reduce onboarding from 14 days to 3 days") survives scope changes
- A feature ("ship guided onboarding wizard") binds you to a specific solution
- If the wizard solution fails, the outcome is still the goal
- Outcomes can be measured; features can only be delivered

### The feature case (pragmatic)

Outcomes work well at the executive and customer variant level, but engineering execution requires features. A team cannot estimate "reduce onboarding from 14 days to 3 days" -- they can estimate "build the wizard" or "build verification step bypass." The internal roadmap therefore tracks features, with each feature mapped to its parent outcome.

### The reconciliation

| Variant | Default orientation |
|---------|---------------------|
| Executive | Outcomes |
| Customer | Themes (outcomes), with Now items occasionally named as features |
| Internal | Features, each mapped to an outcome and a KR |

This matches the audience: executives plan for outcomes, customers buy outcomes, engineers ship features.

---

## Part 4: Confidence ratings on roadmaps

The executive variant should include confidence ratings per Now-quarter item. The standard scale:

| Rating | Definition | When to use |
|--------|------------|-------------|
| **High** | >=80% chance to deliver on time, on scope | In flight, on schedule, no major risks |
| **Medium** | 50-80% chance | One or two known risks with credible mitigations |
| **Low** | <50% chance | Material risks; dependency on external party; or recent slip |

Ratings are honest, not optimistic. A Medium rating tells the executive "watch this." A Low rating tells the executive "ask me about it." A team that publishes 5 of 5 High ratings every quarter is either coasting or lying.

---

## Part 5: The triangulation check

Before publishing, perform a triangulation check on one item per variant:

1. Pick an item from the Now bucket
2. Find its representation in the internal variant (e.g., "Feature: SAML SSO with Okta + Azure AD")
3. Find its representation in the executive variant (e.g., "Outcome: Enterprise customers can log in via their identity provider; supports $2M expansion target")
4. Find its representation in the customer variant (e.g., "Theme: Single sign-on for enterprise. Available this quarter.")

If all three are recognizably the same thing, the variants are aligned. If a customer reading variant 3 could not predict the internal feature in variant 1, the customer variant is misleading or the internal is incomplete. Adjust.

---

## Part 6: Worked example -- same roadmap, three variants

### Source of truth: internal variant (excerpt)

| Feature | PM | EM | Status | Target | KR mapped | Dependencies | Risks |
|---------|----|----|--------|--------|-----------|--------------|-------|
| SAML SSO with Okta and Azure AD | Jane Doe | Sara Lee | In flight | Sprint 24 (2026-06-12) | KR2 (Enterprise activation rate) | Identity provider documentation | Vendor cert renewal in window |
| SCIM user provisioning | Jane Doe | Sara Lee | Sprint 25 | 2026-06-26 | KR2 | SSO must ship first | Spec ambiguity |
| Audit log export (CSV) | Jane Doe | Tom Kim | In flight | Sprint 24 | KR3 (Enterprise retention) | None | Storage cost spike |
| Search latency optimization | Liam Wu | Tom Kim | Sprint 24 | 2026-06-12 | KR1 (latency p95 <250ms) | Index rebuild | Rollout window contention |

### Executive variant (1 page)

```markdown
# Acme Platform -- Q2 2026 Roadmap

**Strategy:** Win enterprise mid-market by removing top-3 procurement objections.
**Sponsor:** VP Product

## Now (Q2 2026)

| Outcome | Metric | Confidence | Lead PM |
|---------|--------|------------|---------|
| Enterprise customers can log in via their identity provider | KR2: Enterprise activation rate 38% -> 55% | High | Jane Doe |
| Admins can pull audit data for compliance | KR3: Enterprise retention 91% -> 94% | High | Jane Doe |
| Search performance no longer cited as objection | KR1: p95 latency 480ms -> 250ms | High | Liam Wu |

## Next (Q3 2026)

- Automated user provisioning for enterprise admins (Medium confidence)
- Self-serve enterprise contract upgrade (Medium)
- Multi-region data residency (Medium)

## Later (H2 2026)

- AI-assisted search relevance ranking
- Cross-product data unification

## Not this period

- Mobile app parity work (sequenced for 2027)
- Workflow automation themes (in discovery, not committed)
```

### Customer variant (themed cards)

```markdown
# What's Coming in 2026

> This roadmap is directional and may change as we learn from customers.
> Items in "Exploring" are not commitments. Dates may shift.

## Shipping this quarter

**Single sign-on for enterprise**
Log in with your company identity provider. Supports SAML 2.0 with major providers.

**Audit log export**
Export account audit data for compliance reviews.

**Faster search**
Search responses significantly faster for large workspaces.

## In development -- later this year

**Automated team provisioning**
Sync user accounts from your identity provider so admins do not manage them manually.

**Self-serve enterprise upgrades**
Upgrade to enterprise tier directly in product, without sales involvement for standard plans.

**Multi-region data residency**
Choose where your data is stored to meet regional requirements.

## Exploring

**AI-assisted search**
We are exploring how AI can improve search result quality for large knowledge bases.

**Cross-product data unification**
Working on bringing your data across products into one view.
```

### Internal variant (operational table)

See above. The internal variant is the full source-of-truth table with all columns: PM, EM, status, target sprint, KR mapping, dependencies, risks. Updated weekly.

### Triangulation

Pick **SAML SSO** as the test item:

- **Internal:** "Feature: SAML SSO with Okta and Azure AD. Sprint 24."
- **Executive:** "Enterprise customers can log in via their identity provider." (Outcome framing)
- **Customer:** "Single sign-on for enterprise. Shipping this quarter." (Benefit framing)

All three are the same item, appropriately framed. Pass.

---

## Part 7: Common failure modes

| Failure | Symptom | Fix |
|---------|---------|-----|
| One roadmap for all audiences | Sales quotes internal dates; execs see feature lists; customers feel misled | Publish three variants; segment distribution |
| Customer variant has dates beyond current quarter | "Q3: ship X, Q4: ship Y" | Replace with "later this year" and "exploring" |
| Executive variant has features instead of outcomes | "We will ship the wizard, the API, and the export" | Replace each with the customer outcome the feature delivers |
| Internal variant lacks risks | Pretty table, no real visibility | Make risks and dependencies mandatory fields |
| Variants drift over the quarter | Updates happen only when there's news | Set a fixed quarterly republication date |
| Customer variant is identical to internal | Lazy export | Spend the translation time; the customer variant is a public-trust asset |

---

## Part 8: When you cannot publish three variants

Three variants are work. If the team cannot sustain quarterly republication of all three, publish only:

- **Internal** (always required; this is the source of truth)
- **Customer** (when prospects or partners need forward visibility)

Skip the executive variant and instead present the customer variant + an exec-only verbal walkthrough that adds risks and confidence ratings. This is honest -- you are admitting the team does not have the bandwidth for a fully separate executive artifact.

---

## Further reading

- Janna Bastow -- originator of the Now-Next-Later roadmap format
- Marty Cagan, "Empowered" (Wiley, 2020) -- Chapter on right-sized roadmaps
- Teresa Torres, "Continuous Discovery Habits" (2021) -- Opportunity Solution Trees as outcome inputs
- C. Todd Lombardo et al., "Product Roadmaps Relaunched" (O'Reilly, 2017)

---

**Last Updated:** 2026-05-21
