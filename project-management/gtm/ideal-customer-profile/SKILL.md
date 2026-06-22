---
name: ideal-customer-profile
description: >
  Define a sharp Ideal Customer Profile (ICP) — firmographics, behavioral
  signals, JTBD, and buyer persona. Use when defining a new ICP, refining
  one from actual closed customers, or auditing why pipeline or conversion
  is poor.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: project-management
  domain: go-to-market
  updated: 2026-05-27
  python-tools: icp_scorer.py
  tech-stack: icp, ideal-customer-profile, firmographics, jtbd
---

# Ideal Customer Profile (ICP)

The sharp definition of who you serve — used by marketing for targeting,
sales for qualification, and product for prioritization.

## When to use this skill

- **Defining ICP** for a new product / segment
- **Refining ICP** from observed closed customers
- **Auditing** when pipeline quality / conversion is poor
- **Pre-fundraise** to articulate market position
- **Sales qualification** rubric build
- **Marketing targeting** for outbound + paid

## The 8 ICP dimensions

1. **Firmographics** — industry, vertical, size, geography, age
2. **Tech-stack signals** — what they use today (and what's missing)
3. **Buyer persona** — role, level, tenure, team size
4. **Jobs-to-be-done (JTBD)** — what they're trying to accomplish
5. **Existing alternatives** — how they solve the JTBD today
6. **Trigger events** — why now (new funding, new exec, regulation, etc.)
7. **Budget authority** — who controls spend
8. **Reachability** — can we find + contact them via channels we have

## ICP vs Persona vs Segment

- **ICP** = the company/account (firmographics + tech + situation)
- **Persona** = the human buyer (role + motivations + objections)
- **Segment** = a cluster of similar ICPs (often by size or vertical)

Use ICP for "which companies." Use persona for "which humans within ICP."

## Clarify First

Before defining the ICP, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Existing customers vs greenfield** — refine from closed-won/best-customer patterns vs design-partner proxy (the real ICP comes from data, not a guess)
- [ ] **The JTBD the product solves** — what customers are trying to accomplish (anchors firmographics, alternatives, and trigger events)
- [ ] **Reachable channels you have** — paid / outbound / events / content / partners (an ICP you can't reach is academic; drives the Reachability dimension)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Workflow

### Step 1 — Start from your best customers
If you have customers:
- List top 20 by health, revenue, expansion
- Find common patterns across them
- That's your real ICP (not what you guessed)

If you don't have customers:
- Use design partners / pilot customers as proxy
- Be ready to revise after 10-20 real customers

### Step 2 — Disqualify common myth-ICPs

Common "ICP" patterns that are wishful thinking:
- "Companies with 100-10,000 employees" — too broad
- "Innovative companies" — meaningless
- "Companies that want to grow" — everyone
- "Enterprise" — undefined; map to size

A real ICP excludes most companies.

### Step 3 — Document the 8 dimensions
Per dimension, be specific.

Example for HR analytics SaaS:

| Dimension | Definition |
|-----------|------------|
| Firmographics | US, mid-market (200-2000 EE), SaaS or services vertical, > $20M revenue, 5+ years old |
| Tech-stack | Workday or BambooHR + ADP or Gusto. Bonus: existing BI tool (Looker / Tableau / Mode) |
| Buyer persona | HR Director or VP People; 5+ years tenure; built career on people analytics |
| JTBD | "I need to be a strategic partner to the CFO/CEO; I'm stuck doing reports manually" |
| Existing alternatives | Excel + analyst (often resigned to it); occasionally hired contractor |
| Trigger events | Annual reporting cycle just done; new CFO joined; HR analyst departed; board asking for better data |
| Budget authority | Director can recommend; VP People approves $50K; CHRO approves $200K+ |
| Reachability | SHRM events, HR Tech podcast, LinkedIn (HR Director groups), HR Brew newsletter |

### Step 4 — Build the qualification rubric
For sales qualification, distill ICP to a scorable checklist:

```
Qualification (BANT-style):
- Industry fit: SaaS/services? (yes/no)
- Size fit: 200-2000 EE? (yes/no)
- Tech fit: Workday/BambooHR + ADP/Gusto? (yes/no)
- Authority: VP People+ in deal? (yes/no)
- Pain: actively trying to solve HR analytics? (yes/no)
- Budget: confirmed > $50K? (yes/no)
- Timeline: decision in next 6 months? (yes/no)
```

5+ yes = strong lead. <3 yes = disqualify.

### Step 5 — Run `icp_scorer.py`
Audit ICP definition for specificity, score account lists against ICP.

```bash
python3 project-management/gtm/ideal-customer-profile/scripts/icp_scorer.py \
  --input icp_spec.json --format markdown
```

### Step 6 — Refresh per quarter
ICP shifts:
- New customers reveal new patterns
- Product evolution opens new segments
- Market shifts (recession, regulation, competition)

Don't refresh weekly. Quarterly is healthy.

## Decision frameworks

### Firmographic specificity test

For each dimension, ask:
- Could I send a list of companies matching this to my BDR tomorrow?
- If not, sharpen.

Vague: "growing SaaS companies"
Sharp: "US-headquartered B2B SaaS companies, $10M-$100M ARR, post-Series B, that have hired their first VP of Sales in last 12 months"

### Tech-stack signals

Tech stack reveals readiness:
- Have a CRM = likely structured sales process
- Have an HRIS = HR team beyond founder/HR-of-1
- Use a specific vendor = open to category
- Built in-house = NIH (Not Invented Here) bias risk

Tools like BuiltWith, G2, Crunchbase + scraping can reveal stack.

### Trigger event types

Strongest triggers (cause buying activity):
- New executive in role (60-day window)
- Funding round closed (have budget; want to spend strategically)
- M&A activity (integration needs)
- Regulatory deadline (compliance pressure)
- Major incident (urgent need)
- Vendor consolidation push
- Annual planning cycle (Q4)
- Reorg / department restructure

Weaker triggers:
- "They might want it"
- "They have the budget"

### Reachability test

For each ICP, can you:
- Find them via paid acquisition? (size of audience; CPC)
- Find them via outbound? (LinkedIn search, ZoomInfo, Apollo)
- Find them at events? (SHRM, RSA, AWS reInvent, etc.)
- Find them via content? (SEO keywords they search)
- Find them via partners? (which adjacent vendors)

If unreachable, ICP is academic.

## Common engagements

### "Define ICP for our new product"
1. Pull design partner / pilot data (or interview 5-10 ideal targets).
2. Document the 8 dimensions.
3. Build qualification rubric.
4. Validate with sales: can they recognize these in inbound?
5. Validate with marketing: can they target this list?

### "Refine ICP from closed customers"
1. List top 20 paying customers by health/expansion.
2. Find patterns: size, vertical, role, trigger, tech stack.
3. Document refined ICP.
4. Compare to original ICP: what's different?
5. Update qualification rubric + targeting.
6. Sunset segments not in refined ICP.

### "Pipeline conversion is bad — is it ICP?"
1. Audit closed-won vs closed-lost ICP fit scores.
2. Common failure: pipeline is full of "near-ICP" that don't convert.
3. Tighten qualification; reject more aggressively at intake.

## Anti-patterns to avoid

- **ICP = "everyone."** Diluted GTM.
- **ICP without trigger event.** Targets without urgency.
- **ICP unreachable via your channels.** Academic exercise.
- **ICP that doesn't disqualify anyone.** Not really an ICP.
- **Same ICP for 3 years post-launch.** Customers reveal real ICP; refresh.
- **ICP defined by product, not customer.** "Companies that need X" = solution-thinking.
- **ICP without qualification rubric.** Sales can't apply it.

## References

- `references/icp-dimensions-deep.md` — 8 dimensions in depth + signals
- `references/icp-refinement-from-data.md` — using closed customers to refine

## Related skills

- `project-management/gtm/gtm-strategy` — uses ICP as input
- `project-management/strategy-frameworks/business-model-canvas` — segments block
- `project-management/discovery/customer-interview-script` — interview-based ICP discovery
- `marketing/competitive-teardown` — competitive context
- `c-level-advisor/cro-advisor` — sales context
- `c-level-advisor/cmo-advisor` — marketing context
