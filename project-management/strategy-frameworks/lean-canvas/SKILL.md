---
name: lean-canvas
description: >
  Lean Canvas (Ash Maurya) — startup adaptation of the Business Model
  Canvas for capturing assumptions and unfair advantages in early-stage
  products. Use at the idea, pre-PMF, or pivot stage, or when you need a
  1-page model fast.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: project-management
  domain: strategy-frameworks
  updated: 2026-05-27
  python-tools: lean_canvas_validator.py
  tech-stack: lean-canvas, ash-maurya, lean-startup, problem-solution-fit
---

# Lean Canvas

A 9-block startup canvas adapted from BMC. Replaces 4 BMC blocks
(Key Resources, Activities, Partnerships, Customer Relationships) with
startup-focused ones (Problem, Solution, Key Metrics, Unfair Advantage).

## When to use this skill

- **Early-stage** (pre-PMF) product or company
- Capturing **assumptions** that need testing
- **20-minute** model sketch (BMC takes longer)
- **Pivot conversations** — what would change?
- Stress-testing **unfair advantage** before building

## The 9 Lean Canvas blocks

1. **Problem** — Top 3 problems for the segment
2. **Customer Segments** — Target customers (especially Early Adopters)
3. **Unique Value Proposition** — Single, clear, compelling message
4. **Solution** — Top 3 features that solve the problems
5. **Channels** — Path to customers
6. **Revenue Streams** — Revenue model + LTV + revenue forecast
7. **Cost Structure** — Customer acquisition cost + distribution + people + hosting
8. **Key Metrics** — Key activities you measure
9. **Unfair Advantage** — Something that cannot be easily copied or bought

## Lean Canvas vs BMC

| Lean Canvas | BMC |
|-------------|-----|
| Problem | Key Partnerships |
| Solution | Key Activities |
| Key Metrics | Key Resources |
| Unfair Advantage | Customer Relationships |

Same outer shape; different inner emphasis. Use Lean when problem +
unfair advantage matter more than ops detail.

## Clarify First

Before building the canvas, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **The specific early-adopter segment** — named, not "everyone" (the Problem, UVP, and Channels blocks all hinge on a concrete early adopter)
- [ ] **The top 3 problems** — for that segment (the Problem block; if you can't name them you have an idea, not a startup)
- [ ] **Existing alternatives** — how customers solve this today (signals whether the problem is real; "they live with it" is important signal)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Workflow

### Step 1 — Problem-Segment first
Start with Problem and Customer Segments. If you can't list the top 3
problems for a specific segment, you don't have a startup — you have an idea.

### Step 2 — Existing alternatives
Within Problem block, list how customers solve this today. If the answer
is "they don't / they live with it," that's important signal.

### Step 3 — Unique Value Proposition
A single sentence that:
- Names the early-adopter segment
- States the differentiating outcome
- Distinguishes from existing alternatives

Template: "[Outcome] for [segment] that [differentiator]."

### Step 4 — Solution (3 features max)
Limit to 3. Founders always want to list 10. Resist.

### Step 5 — Unfair Advantage
The hardest block. What do you have that no one can easily copy?
- Insider information / domain
- Personal authority / reputation
- Dream team
- Personal endorsements
- Existing customer base
- Network effects already in motion
- Patented IP

If empty: most startups have nothing yet. Mark explicitly + plan how to build one.

### Step 6 — Channels, Revenue, Costs, Metrics
Fill remaining blocks. Be specific.

### Step 7 — Run `lean_canvas_validator.py`
Audit for: missing blocks, generic content, no early adopter named,
no existing alternatives, no Key Metrics, vague Unfair Advantage.

```bash
python3 project-management/strategy-frameworks/lean-canvas/scripts/lean_canvas_validator.py \
  --input canvas.json --format markdown
```

## Decision frameworks

### Lean Canvas vs BMC — when to use which

| Use Lean Canvas | Use BMC |
|-----------------|---------|
| < $1M ARR or pre-revenue | Mature company / division |
| Single segment, single product | Multi-product or multi-segment |
| Problem-solution fit hunting | Operating + scaling |
| Pivot conversations | Strategic planning |
| 20-minute sketch | Half-day planning workshop |

### Early adopter heuristic

Early adopters are not "future mainstream users." They are:
- Aware they have the problem
- Actively looking for a solution
- Have cobbled together a workaround (existing alternative)
- Have budget / authority to try yours

If you can't name 5 specific early adopters by name + workaround, you're
not at problem-solution fit yet.

### Unfair Advantage — what counts

**Counts:**
- Insider information (proprietary data, deep customer relationships)
- Personal authority (industry-recognized expertise)
- Existing community / audience
- Network effects already started
- Capital + brand recognition

**Doesn't count:**
- "We work harder"
- "Our team is great"
- "First mover" (in most cases; usually replicable)
- "Better UX" (replicable)
- "AI" (everyone has AI now)
- "Cheaper" (price competition is a race to zero)

If your only unfair advantage is "speed" or "execution," that's a
weakness as a moat.

## Common engagements

### "Help me sketch a canvas for my new idea"
1. Problem + Segment first.
2. Force list the existing alternatives (and what they cost).
3. Write the UVP (one sentence).
4. List Solution as 3 features max.
5. Identify Channels you can realistically test in 4 weeks.
6. Stub Revenue + Cost + Metrics.
7. Honest Unfair Advantage assessment.
8. Identify top 3 riskiest assumptions; design test for each.

### "Should we pivot?"
1. Build current state Lean Canvas.
2. Build proposed state Lean Canvas.
3. Compare: what's different? what's the unfair advantage now?
4. What evidence do we have that the new model works?
5. Run the assumption-test for the riskiest new assumption.

## Anti-patterns to avoid

- **Solution before Problem.** Solution-in-search-of-problem.
- **"Everyone" as segment.** Force a specific early adopter description.
- **No existing alternative listed.** Customers always do something today.
- **UVP that says everything.** Says nothing.
- **5+ solution features listed.** Pick 3 max.
- **Vague Key Metrics.** Pirate metrics (AAARRR) or HEART or similar.
- **Unfair Advantage = "execution".** Not an advantage.
- **No assumption register.** Canvas isn't a plan, it's a hypothesis.

## References

- `references/lean-canvas-framework.md` — the 9 blocks deep, comparison to BMC
- `references/lean-startup-anti-patterns.md` — common mistakes + worked fixes

## Related skills

- `project-management/strategy-frameworks/business-model-canvas` — operating-scale variant
- `project-management/discovery/value-proposition-canvas` — deeper on UVP
- `project-management/discovery/identify-assumptions` — assumption register
- `project-management/discovery/pre-mortem` — risk discovery
- `project-management/execution/north-star-metric` — Key Metric definition
- `c-level-advisor/ceo-advisor` — strategic context
