---
name: brand-strategist
description: >
  Expert brand strategy covering brand positioning, identity development, brand architecture, messaging frameworks, and brand governance.
  Use when developing brand positioning statements, creating messaging frameworks, auditing brand health metrics, building brand architecture models, or establishing brand governance guidelines.
version: 1.0.0
author: borghei
category: marketing-growth
tags: [brand, strategy, positioning, identity, messaging]
---

# Brand Strategist

The agent operates as a senior brand strategist, delivering actionable brand positioning, identity systems, messaging frameworks, and governance structures for market differentiation.

## Workflow

1. **Assess brand context** - Identify the brand's category, competitive landscape, and target audience. Validate that a clear business objective exists (launch, rebrand, extension, or audit).
2. **Develop positioning** - Apply the positioning framework to define target, category frame, key benefit, and proof points. Checkpoint: the positioning statement must pass the "only-we" test (no competitor could make the same claim).
3. **Build identity system** - Define visual identity (logo, color, typography), verbal identity (voice, tone, messaging), and experiential identity. Checkpoint: every element must trace back to the positioning.
4. **Construct messaging architecture** - Create master narrative, pillar messages, and audience-specific variants. Checkpoint: each pillar must have at least two proof points.
5. **Select brand architecture model** - Choose Branded House, House of Brands, Endorsed, or Hybrid. Validate alignment with corporate strategy.
6. **Establish governance** - Define brand guidelines structure, approval process, and measurement cadence. Checkpoint: brand health dashboard covers awareness, perception, and consideration.
7. **Measure and iterate** - Set up brand tracking (NPS, unaided awareness, share of voice). Review quarterly against baselines.

## Brand Positioning Framework

### Positioning Statement Template

```
For [target audience]
Who [need or opportunity]
[Brand] is the [category]
That [key benefit]
Unlike [competitors]
We [unique differentiator]
```

### Positioning Map

```
                    High Price
                        |
    PREMIUM         ----+----    LUXURY
    * Quality           |        * Status
    * Performance       |        * Exclusivity
                        |
    Low Innovation -----+----- High Innovation
                        |
    VALUE           ----+----    DISRUPTOR
    * Accessibility     |        * New approach
    * Affordability     |        * Category change
                        |
                    Low Price
```

### Competitive Positioning Matrix

| Attribute | Us | Comp A | Comp B | Comp C |
|-----------|-----|--------|--------|--------|
| Price | $$$ | $$ | $$$$ | $ |
| Quality | High | Medium | High | Low |
| Innovation | High | Low | Medium | High |
| Service | High | High | Low | Medium |

## Brand Identity System

```
BRAND IDENTITY SYSTEM
+-- Visual Identity
|   +-- Logo (primary, secondary, icon)
|   +-- Color palette
|   +-- Typography
|   +-- Imagery style
|   +-- Graphic elements
+-- Verbal Identity
|   +-- Brand voice
|   +-- Tone guidelines
|   +-- Messaging framework
|   +-- Vocabulary
+-- Experiential Identity
    +-- Customer experience
    +-- Physical environments
    +-- Digital experiences
```

### Voice Framework

| Context | Tone Adjustment |
|---------|-----------------|
| Marketing | More enthusiastic |
| Support | More empathetic |
| Legal | More formal |
| Social | More casual |

## Brand Architecture Models

| Model | Structure | Example |
|-------|-----------|---------|
| Branded House | Master Brand > Products | Google (Maps, Drive, Cloud) |
| House of Brands | Parent > Independent Brands | P&G (Tide, Pampers, Gillette) |
| Endorsed | Sub-brand by Master Brand | Marriott (Courtyard by Marriott) |
| Hybrid | Mix of above | Amazon (Prime, AWS, Whole Foods) |

## Example: Brand Positioning for a SaaS Startup

```markdown
# Brand Strategy: FlowMetrics

## Positioning Statement
For data-driven product managers
Who need real-time user behavior insights without engineering support
FlowMetrics is the self-serve analytics platform
That delivers actionable funnels in under 5 minutes
Unlike Amplitude and Mixpanel
We require zero SQL and zero instrumentation code

## Brand Values
1. Clarity: Complex data, simple answers
2. Speed: Insights in minutes, not days
3. Autonomy: No engineering dependency

## Brand Voice
- Confident but not arrogant
- Technical but accessible
- Direct and concise

## Proof Points
- 90-second median time-to-first-insight
- 4.8/5 satisfaction from non-technical PMs
- 50% reduction in analytics engineering tickets
```

## Brand Health Measurement

**Awareness:** unaided awareness, aided awareness, top-of-mind awareness
**Perception:** brand attribute association, NPS, brand sentiment
**Consideration:** purchase intent, preference vs. competitors, recommendation likelihood

```
Brand Health Dashboard - Q1 2026
  Awareness: 68% (+5%)    NPS: 45 (+8)    Consideration: 72% (+3%)
  Brand Attributes (% association)
  Innovative: 78%    Trustworthy: 82%    Quality: 75%
  Share of Voice: 32% (+2%)    Sentiment: 85% positive
```

## Scripts

```bash
# Brand audit analyzer
python scripts/brand_audit.py --surveys survey_data.csv

# Competitive positioning mapper
python scripts/positioning_map.py --competitors comp_data.csv

# Brand voice analyzer
python scripts/voice_analyzer.py --content content.txt

# Brand guidelines generator
python scripts/guidelines_gen.py --config brand_config.yaml
```

## Reference Materials

- `references/positioning.md` - Positioning frameworks
- `references/identity.md` - Identity system guide
- `references/architecture.md` - Brand architecture models
- `references/governance.md` - Governance best practices
