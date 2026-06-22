---
name: business-model-canvas
description: >
  Build, evaluate, and stress-test a Business Model Canvas (Osterwalder)
  across all 9 blocks. Use when designing or refreshing a business model,
  auditing a canvas for gaps, exploring monetization, or aligning on the
  model's assumptions.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: project-management
  domain: strategy-frameworks
  updated: 2026-05-27
  python-tools: canvas_validator.py
  tech-stack: business-model-canvas, osterwalder, strategy
---

# Business Model Canvas

A working Business Model Canvas (BMC) — Alexander Osterwalder's 9-block
strategic management template that captures how an organization creates,
delivers, and captures value.

## When to use this skill

- Designing the **business model** for a new product or company
- Refreshing the BMC after a strategic pivot
- Stress-testing the **assumptions** in an existing model
- Aligning leadership on **how value flows** through the business
- Comparing two or more candidate business models
- Onboarding a new exec / investor to the business

## The 9 building blocks

1. **Customer Segments** — Who do we serve? (mass market, niche, segmented, diversified, multi-sided)
2. **Value Propositions** — What value do we deliver to each segment?
3. **Channels** — How do we reach customers? (own, partner; direct, indirect; physical, digital)
4. **Customer Relationships** — How do we acquire, keep, and grow each segment?
5. **Revenue Streams** — How does the customer pay? (one-time, subscription, usage, licensing, advertising)
6. **Key Resources** — What assets are required? (physical, intellectual, human, financial)
7. **Key Activities** — What do we do to deliver value? (production, problem-solving, platform/network)
8. **Key Partnerships** — Who helps us? (strategic alliances, JVs, supplier relationships)
9. **Cost Structure** — Where do costs come from? (cost-driven vs value-driven; fixed vs variable)

## Clarify First

Before building the canvas, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Customer segment(s)** — who you serve, specifically (drives Value Prop, Channels, Relationships, Revenue — "everyone" collapses the whole canvas)
- [ ] **Revenue model** — how the customer pays: subscription / usage / licensing / advertising (must reconcile against Cost Structure or unit economics break)
- [ ] **Stage** — new model / pivot / mature operating business (determines whether Lean Canvas is the better tool)
- [ ] **Cost-driven vs value-driven posture** — shapes Cost Structure and Key Activities (trying both produces mediocre everything)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Workflow

### Step 1 — Draft per block
Start with **Customer Segments** and **Value Propositions** (these drive everything else).
Then fill: Channels, Customer Relationships, Revenue Streams. Then: Key Resources,
Activities, Partnerships. Finish with Cost Structure.

### Step 2 — Validate the chain
For each Customer Segment, trace: Segment → Value Prop → Channel → Relationship →
Revenue. If you can't connect these, the model has a gap.

### Step 3 — Stress-test assumptions
For each block, list the top 2-3 assumptions and rate (high / medium / low) on:
- Evidence (do we know this is true?)
- Riskiness (what breaks if wrong?)
- Testability (can we run a cheap experiment?)

### Step 4 — Run `canvas_validator.py`
Audit the canvas for: empty blocks, ungrounded value-prop / segment matches,
revenue / cost imbalance, segment-channel-relationship coherence.

```bash
python3 project-management/strategy-frameworks/business-model-canvas/scripts/canvas_validator.py \
  --input canvas.json --format markdown
```

### Step 5 — Iterate
Most first drafts are wrong in interesting ways. Plan to revise 3-5 times.

## Decision frameworks

### Which type of business model?

| Pattern | Examples | Characteristics |
|---------|----------|-----------------|
| **Unbundled** | Investment banking (advisor + product) | Different segments; different value props |
| **Long Tail** | Netflix, Amazon | Niche x volume |
| **Multi-sided platform** | Visa, Airbnb | Connects 2+ segments; network effects |
| **Free / Freemium** | Spotify, LinkedIn | One segment pays for another's free use |
| **Open** | Open-source + services | Free product, paid expertise/services |

Most modern SaaS = multi-sided OR freemium variant.

### Cost-driven vs value-driven

| Cost-driven | Value-driven |
|-------------|--------------|
| Lean cost structure | Focus on premium value |
| Low-price value prop | High-value, often high-price |
| Maximum automation | High-touch service |
| Extensive outsourcing | In-house excellence |

Most companies need to pick ONE — trying both produces mediocre everything.

### Common BMC anti-patterns

- **Generic value proposition.** "Better, faster, cheaper" — applies to anything; means nothing.
- **One segment listed as "everyone."** Forces commodity positioning.
- **Revenue streams with no channel.** How does money flow?
- **Costs that don't sum to revenue model.** Unit economics broken.
- **Partnerships listed without specific roles.** What do they actually do?
- **No coherent customer journey across blocks.** Segment doesn't connect to channel.

## Output expectations

After using this skill, you should have:

1. A populated **9-block canvas** with specific (not generic) statements
2. A **validation report** flagging gaps, ungrounded assumptions, coherence issues
3. **2-3 prioritized experiments** to test the riskiest assumptions
4. References to other strategy skills (lean canvas for startup-stage; value-proposition-canvas for the VP block)

## References

- `references/canvas-framework.md` — the 9 blocks deep, patterns, examples
- `references/examples-anti-patterns.md` — worked examples + common failures

## Related skills

- `project-management/strategy-frameworks/lean-canvas` — startup-stage variant
- `project-management/strategy-frameworks/swot-analysis` — internal/external strengths-weaknesses
- `project-management/strategy-frameworks/porters-five-forces` — competitive dynamics
- `project-management/discovery/value-proposition-canvas` — deeper on the value-prop block
- `project-management/execution/north-star-metric` — what to measure once model is set
- `business-growth/pricing-strategy` — pricing depth for the revenue block
- `c-level-advisor/ceo-advisor` — strategic context for the model
