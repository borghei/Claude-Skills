# Product Vision Frameworks Guide

A reference for the five vision frameworks combined in this skill: Pichler, Moore, Raskin, Cagan, Amazon Working Backwards.

---

## 1. Why visions fail (and how to write one that does not)

Most product visions fail in one of three ways:

1. **Too abstract to be useful.** "Empower every team to do their best work" -- could be any SaaS product. Provides no direction for the next roadmap decision.
2. **Too specific to endure.** "Launch SSO and audit logs by Q4" -- this is a roadmap item, not a vision. It will be irrelevant in 6 months.
3. **Too internal to inspire.** Written for the company's benefit, not for the customer's world. "Become the #1 player in the category" describes ambition, not destination.

A working vision is in the middle: specific enough to direct decisions today, abstract enough to outlast any feature, oriented toward the customer's world.

---

## 2. Roman Pichler: The Product Vision Board

Roman Pichler (author of *Strategize* and *How to Lead in Product Management*) developed the Product Vision Board as a one-page diagnostic. It is the fastest way to draft a working vision.

### The five blocks

```
+---------------------------------------------------+
| VISION                                            |
| One sentence: where the product is going          |
+---------------------------------------------------+
| TARGET     | NEEDS      | PRODUCT    | BUSINESS   |
| AUDIENCE   |            |            | GOALS      |
+---------------------------------------------------+
```

### Block-by-block guidance

**Vision (the headline):**

- One sentence
- Names the customer, the outcome, and the bigger outcome
- Format: "Help [audience] [verb] [outcome] so that [bigger outcome]"

**Target Audience:**

- Defined by job-to-be-done, not demographics
- One primary segment; secondary segments listed but not the focus
- Specific enough that you can name the customers (or types of customers)

**Needs:**

- Top 3-5 jobs, pains, gains
- In customer language (from `discovery/value-proposition-canvas/`)
- These are the customer's needs, not the product's "needs"

**Product:**

- Top 3-5 capabilities
- Not features (a feature is a "Slack integration"; a capability is "real-time notifications to where the customer works")
- Each capability addresses one or more needs

**Business Goals:**

- 2-4 long-term outcomes for the business
- Specific where possible ("$20M ARR by year 3"; "category leadership in mid-market")
- Avoid generic ("be the best") and avoid vanity ("most users")

### When to use the Pichler Board

- Fast first draft (2-3 hour workshop)
- One-page artifact suitable for sharing in wikis, decks, onboarding
- Diagnostic for an existing vision -- map a current vision into the board and find the missing block

---

## 3. Geoffrey Moore: The Positioning Statement (Elevator Pitch)

Geoffrey Moore's *Crossing the Chasm* (1991, revised 2014) introduced the positioning statement as a forcing function for clarity. If you cannot fill in every blank, the vision is not yet sharp.

### The format

```text
For [target customer]
who [statement of need or opportunity],
[product name] is a [product category]
that [statement of key benefit -- compelling reason to buy].
Unlike [primary competitive alternative],
our product [statement of primary differentiation].
```

### Why each blank matters

- **Target customer:** Forces segment specificity. "Everyone" fails.
- **Statement of need:** Forces a real pain. "Wants to do their job better" fails.
- **Product category:** Forces a category choice. "Platform" usually fails -- pick a category.
- **Key benefit:** Forces a single benefit. "Many benefits" fails.
- **Competitive alternative:** Forces naming an alternative. "Other tools" fails.
- **Primary differentiation:** Forces a single distinction. "Better in many ways" fails.

### The forcing function

If any blank is generic or hand-waved, the vision is not yet specific. The discipline of completing all six blanks reveals exactly where the strategy is weak.

### When to use the Moore pitch

- Sales enablement (the talk track derives directly from the pitch)
- Marketing copy (the pitch becomes the homepage hero)
- Board decks (one-sentence position statement on slide 2)
- Hiring (candidates can decide whether the company's direction matches theirs)

---

## 4. Andy Raskin: The Strategic Narrative

Andy Raskin (consultant to Salesforce, Drift, Yammer, Zuora, and others) developed the 5-act strategic narrative as a *vision compressed into a story arc*. The form is borrowed from screenwriting; the effect is that the audience identifies emotionally with the customer as protagonist.

### The 5 acts

#### Act 1: Name the undeniable change

A shift in the world that everyone in the audience agrees is real. The change is not your product's problem -- it is the customer's reality.

**Test:** If the audience disagrees with the change, the rest of the narrative collapses. Pick a change that is uncontroversial.

**Examples:**
- "Finance is being asked to be strategic, but spends 60% of its time on manual reconciliation."
- "Software development used to be a backend craft; now every product team ships software, including non-engineers."
- "Customer support used to be reactive; now customers expect proactive intervention before they ask."

#### Act 2: Show the winners and losers

Who is benefiting from this change? Who is being left behind?

This sets up *moral stakes*. The audience does not want to be a loser; the narrative implies the cost of inaction.

**Examples:**
- "Finance teams who automate are seen as strategic partners. Teams stuck on spreadsheets are seen as cost centers."
- "Product teams who learn to build with AI ship 10x. Teams who don't are 6 months behind."

#### Act 3: Tease the promised land

What does the future look like for the winners? Describe it concretely.

The promised land is emotional. It is not "a better tool" -- it is a different state of work, a different professional identity.

**Examples:**
- "Imagine a finance function that closes in 2 days and spends 60% of its time on forward-looking analysis."
- "Imagine a product team where every PM can prototype, every designer can ship, every engineer can run experiments."

#### Act 4: Identify the obstacles

Why is the promised land hard to reach? Without obstacles, the story has no tension.

The obstacles must be specific -- not "it's hard." Specific obstacles imply specific solutions.

**Examples:**
- "Existing reconciliation tools assume one payment processor. Real businesses have 3-7."
- "Current AI tools require engineering integration. PMs and designers can't access them."

#### Act 5: Position your product as the gift

Your product is what overcomes the obstacles. Not the only path to the promised land -- but the most direct path.

**Examples:**
- "Reconcile unifies reconciliation across every payment processor, GL, and ERP -- so finance teams can finally make the leap."
- "[Product] lets every product team member use AI without engineering integration -- so the whole team can build."

### When to use the Raskin narrative

- Sales pitches and demos (the narrative wraps around the product)
- Board meetings and fundraising (emotional alignment with investors)
- All-hands talks (motivates the team)
- Hiring (candidates feel the stakes)

---

## 5. Marty Cagan: The 10-Year Horizon

Marty Cagan (*Inspired*, *Empowered*, *Transformed*) argues that a product vision should look 10 years into the future. The 10-year horizon does three things that shorter horizons cannot:

1. **Forces abstraction from current technology.** What you can build in 2036 cannot rely on 2026 stack assumptions. The vision must survive the unknown.
2. **Outlasts strategy cycles.** Strategy shifts every 2-3 years as competitive landscape changes. A 10-year vision is more durable than any single strategy.
3. **Aligns hiring and architecture.** A 10-year vision shapes who you hire (people who want to bring that future into being) and how you build (architecture that can carry you there).

### Cagan's vision document structure

A long-form Cagan vision is typically 3-10 pages. Sections:

1. **The world in [year + 10]** -- describe the customer's world in the future, not the product
2. **The product's role in that world** -- where your product fits in the customer's day
3. **Capabilities required** -- what the product must be able to do (not "how it's built")
4. **The path to get there** -- 3-4 phases over 10 years
5. **What stays true** -- principles and values that will not change regardless of how the product evolves

### Tips for the 10-year horizon

- **Describe the customer, not the product.** What is their job? Their day? Their professional identity in 10 years?
- **Avoid current jargon.** If your vision relies on a 2026 term (e.g., "agentic AI"), reframe to the underlying capability.
- **Specific is better than abstract, even at 10 years.** "Finance closes in 2 days" beats "Finance is faster."
- **What stays true is the most important section.** It signals the principles you will not trade.

### When to use the Cagan 10-year horizon

- Multi-year architectural bets (you are deciding what to build over multiple years)
- Executive hiring (executives need to see the long arc)
- Investor relations (Series B+ investors want the 10-year story)
- Annual strategic offsite (forces alignment on principles)

---

## 6. Amazon Working Backwards: The Future Press Release

The Working Backwards method (covered in detail in `execution/prfaq/`) treats the vision as a *future press release* announcing the product as if it already shipped.

### Why include it in vision work

The PR is concrete. It names a customer, a benefit, a quote, a date, a release. It does not allow the abstractions that infect typical visions. If you cannot write a believable future PR about your product, the vision is not yet ready.

### Use as a translation test

Once you have a Pichler Board or Raskin narrative, write the future PR. If the PR feels forced, the underlying vision has a gap. Common gaps:

- The customer benefit is vague ("more productive")
- The differentiation is generic ("easier", "better")
- The launch quote is hollow ("excited to announce")

The PR/FAQ skill (`execution/prfaq/`) walks through the full method.

---

## 7. Choosing a framework

| Situation | Recommended starting framework |
|-----------|--------------------------------|
| New product, no existing vision | Pichler Board (fast first draft) |
| Strategy reset / pivot | Raskin Narrative (emotional realignment) |
| Multi-year architectural bets | Cagan 10-Year Horizon |
| Sales / marketing translation needed | Moore Elevator Pitch + Raskin Narrative |
| Customer + leadership alignment | Amazon Future PR/FAQ (via `execution/prfaq/`) |
| Existing vague vision -- diagnostic | Pichler Board (map current vision, find gaps) |

The best visions are translated across multiple frameworks. A vision that survives translation between Pichler -> Moore -> Raskin is *sharp*. A vision that requires explanation in a second format is not yet ready.

---

## 8. Common vision anti-patterns

| Anti-pattern | Why it fails | Fix |
|--------------|--------------|-----|
| Mission disguised as vision | "We exist to empower X" is a mission; missions don't direct decisions | Add a specific customer + outcome + time horizon |
| Roadmap disguised as vision | "Ship SSO and audit logs" is a roadmap; will be irrelevant in 6 months | Strip feature names; describe the future state of the customer |
| Generic positioning | "Best-in-class platform for modern teams" -- could be anything | Use the Moore pitch to force specificity |
| Internal language | "10x our developer experience" -- engineers, not customers, are described | Rewrite with the customer as protagonist |
| No obstacle | Raskin narrative with no Act 4 -- no tension, no urgency | Add the specific obstacle that your product solves |
| Hides the differentiation | Vision is true of competitors too | Use the Moore "Unlike X" clause to force differentiation |
| Multiple competing visions | Different teams have different versions | Pick one. Commit. Update via formal review, not drift. |

---

## 9. Reviewing and updating a vision

A vision is a long-lived artifact, but not infinitely so. Schedule:

- **Annual vision review.** Did the vision survive the last 12 months of evidence? Are roadmap decisions still tracing to it?
- **Triggered reviews:**
  - Major pivot (product changes direction)
  - Major market shift (new technology, new competitor, new regulation)
  - Founder / CEO transition
  - Series B+ fundraise

A vision can update. The discipline is to update formally -- with documented reasoning, dated diffs, and communication to the team. Drift (the vision quietly changing without acknowledgment) is the opposite of an updated vision.

---

## 10. References

- Pichler, Roman. *Strategize: Product Strategy and Product Roadmap Practices for the Digital Age*. Pichler Consulting, 2016 (and revised editions).
- Moore, Geoffrey A. *Crossing the Chasm*. HarperBusiness, 3rd ed. 2014.
- Raskin, Andy. *The Greatest Sales Deck I've Ever Seen* (2016) -- origin of the strategic-narrative format.
- Cagan, Marty. *Inspired: How to Create Tech Products Customers Love*. Wiley, 2nd ed. 2017.
- Cagan, Marty & Jones, Chris. *Empowered: Ordinary People, Extraordinary Products*. Wiley, 2020.
- Bryar, Colin & Carr, Bill. *Working Backwards: Insights, Stories, and Secrets from Inside Amazon*. St. Martin's Press, 2021.
- Christensen, Clayton M. *Competing Against Luck* (for the jobs-to-be-done layer beneath any vision). HarperBusiness, 2016.
