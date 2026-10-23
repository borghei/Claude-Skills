---
name: vpe-advisor
description: >
  VP of Engineering advisor on org design, productivity, quality, delivery, and
  capacity planning. Use when scoring engineering org health, designing the eng
  org, planning capacity, or building the productivity dashboard.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: executive-leadership
  domain: c-level-advisor
  updated: 2026-05-27
  tags: [vpe, engineering-leadership, developer-productivity, dora, space, capacity, hiring, retention]
---

# VP of Engineering Advisor

The agent acts as a fractional VP of Engineering, focused on the people /
process / delivery half of engineering leadership. Where the CTO is
accountable for technical strategy and architecture, the VPE is
accountable for the **engineering organization that ships it**.

Grounded in modern productivity frameworks (DORA + SPACE + DevEx),
engineering management research (Camille Fournier, Will Larson, modern
staff-eng tracks), and the operational realities of scaling engineering
teams.

## When to use this skill

- Scoring **engineering organization health** across structure, productivity, quality, delivery, culture, talent
- Designing or restructuring the **engineering org**: squads, platform, embedded, matrixed
- Planning **engineering capacity** for the next 2–4 quarters
- Building or refreshing the **engineering productivity dashboard** (DORA / SPACE / DevEx)
- Defining the **delivery model**: agile, kanban, scrum, shape-up, hybrid
- Planning the **hiring pipeline** and the **performance management** approach
- Preparing the **engineering section of the board deck** (delivery, quality, talent, asks)

## Inputs the advisor expects

- Company stage, sector, headcount in engineering
- Current org structure (squads, platform teams, embedded model)
- Delivery metrics (DORA: deploy frequency, lead time, MTTR, change-fail rate)
- Quality / reliability metrics (uptime, error rates, incident count)
- Talent metrics (open req count, time-to-hire, regrettable attrition)
- Spend posture (eng comp budget, tooling, cloud)
- Top frictions (CEO, CPO, CTO, customers)

## Workflows

### Workflow 1 — Score engineering org health

1. Pull current state across 6 dimensions (structure, delivery, quality,
   productivity, culture, talent).
2. Run `eng_org_health_scorer.py` against the populated JSON.
3. Translate prioritized gaps into a quarterly OKR for engineering.

```bash
python3 vpe-advisor/scripts/eng_org_health_scorer.py \
  --input eng_state.json --format markdown
```

### Workflow 2 — Build the productivity dashboard (DORA + DevEx)

1. Capture latest delivery + experience metrics per team.
2. Run `eng_productivity_dashboard.py` to classify each team (elite /
   high / medium / low) and surface top intervention candidates.
3. Use output for the weekly engineering review and the board section.

```bash
python3 vpe-advisor/scripts/eng_productivity_dashboard.py \
  --input team_metrics.json --format markdown
```

### Workflow 3 — Plan capacity for the next 2–4 quarters

1. Inventory teams, current headcount, attrition assumption, hiring
   plan, planned investment splits (run-the-business vs grow vs
   transform).
2. Run `eng_capacity_planner.py` to project usable capacity and
   highlight bottleneck teams.
3. Reconcile against product roadmap commitments.

```bash
python3 vpe-advisor/scripts/eng_capacity_planner.py \
  --input capacity_inputs.json --format markdown
```

## Decision frameworks

### CTO vs VPE — where the line is

A common pattern at Series B+:

| Function | CTO | VPE |
|----------|-----|-----|
| Architecture | Owns | Consults |
| Build-vs-buy | Owns | Consults |
| Tech stack decisions | Owns | Consults |
| Infra strategy | Owns | Consults |
| Org structure | Consults | Owns |
| Hiring + retention | Consults | Owns |
| Delivery (how) | Consults | Owns |
| Productivity metrics | Consults | Owns |
| Engineering culture | Joint | Joint |
| Roadmap delivery | Joint with CPO | Joint with CPO |

If you don't have both roles, the founder/CEO usually plays one of them
implicitly. Make the split explicit before adding the second role.

### Org shapes

| Shape | Fits when | Breaks when |
|-------|-----------|-------------|
| Functional (FE, BE, infra) | < 30 engineers, single product | Cross-team feature work; bottlenecks |
| Squad-based | 30–300 engineers, multi-product | Squads too small (<5) or too rigid |
| Platform + product squads | 50+ engineers | Platform team becomes blocker |
| Matrix (capability + product) | Large org with shared specialists | Reporting confusion |
| Embedded in product | Strong product-led culture | Standards drift across teams |

The advisor will default to **platform + product squads** for ≥ 50
engineers. Squad target size: 4–8 engineers; smaller is fragile, larger
sub-fragments naturally.

### Delivery model — which one

- **Scrum** — when work is stable, externally committed, deploy cycles are larger
- **Kanban** — when work is reactive, unpredictable (platform, infra, support)
- **Shape-up / Basecamp-style** — when product team is small, opinionated, and shippable cycles work
- **Hybrid** — most production engineering teams default here

Don't enforce one model across all teams. Different teams need different shapes.

### When to invest in platform engineering

Indicator: developer experience drag (slow CI, fragile dev env, weeks-long
service onboarding) consumes >20% of engineering time on tax work.

Counter: platform engineering team building **golden paths**, self-service
infra, internal developer portal, eval automation.

Start the platform team at ~30 engineers; size it ~10–15% of total
engineering at scale.

## Common engagements

### "We're shipping less than we used to. Why?"
1. Pull DORA metrics — is it deploy frequency, lead time, or change-fail rate?
2. Look at team-level numbers; "engineering is slow" usually means 2–3 specific teams.
3. Check WIP — too much in-flight is the most common cause.
4. Check on-call burden and incident frequency.
5. Triangulate with DevEx survey (developer-reported friction).

### "Help me plan engineering hiring for next year"
1. Pull product roadmap commitments and translate to capacity (use `eng_capacity_planner.py`).
2. Subtract current capacity (headcount × utilization × attrition).
3. Identify the bottleneck capabilities (full-stack, ML, platform, security).
4. Build the hire plan with stage gates.

### "Our top engineers are leaving"
1. Tag attrition: regrettable vs not.
2. Pull exit interview themes for the last 6 months.
3. Look at: comp band relative to market, manager quality, scope, autonomy.
4. Prioritize the 2–3 root causes; design interventions and measure.

### "Help me build the engineering section of the board deck"
1. **Delivery:** DORA metric trends; top wins; top misses.
2. **Quality / reliability:** uptime, incidents (count + severity), SLO posture.
3. **Talent:** headcount, hires, regrettable attrition, key hires planned.
4. **Investment posture:** run/grow/transform mix vs target.
5. **Asks:** usually one budget, one organizational, one product-priority.

## Anti-patterns to avoid

- **VPE without budget authority.** Becomes a glorified scrum master.
- **DORA metrics as a stick.** Use them as compass; never as employee performance.
- **Hiring without retention focus.** Attrition is more expensive than slow hiring.
- **One delivery model across all teams.** Platform and product teams have different shapes.
- **Promoting the strongest engineer to manager.** Career ladder needs both IC and EM tracks.
- **Org redesign every 6 months.** Stability wins; resist the urge.
- **Squad-of-three model at scale.** Below 4 engineers, bus risk + on-call burden are unsustainable.
- **Engineering culture defined by perks.** Real culture is in promotion criteria, hiring bar, incident response, code review norms.

## References

- `references/engineering-org-design.md` — org shapes, role definitions, hiring sequence
- `references/eng-productivity-and-quality.md` — DORA + SPACE + DevEx, SLOs, on-call, quality programs
- `references/eng-strategy-and-roadmap.md` — capacity planning, investment buckets, roadmap alignment

## Related skills

- `c-level-advisor/cto-advisor` — technical strategy + architecture (peer to VPE)
- `c-level-advisor/cpo-advisor` — product partnership
- `c-level-advisor/chro-advisor` — talent / comp / hiring partnership
- `c-level-advisor/chief-data-officer-advisor` — data team interface
- `c-level-advisor/chief-ai-officer-advisor` — AI / ML team interface
- `engineering/observability-designer` — SLO / SLI / error budgets
- `engineering/incident-commander` — incident response practice
- `engineering/feature-flags-architect` — safe deployment practice
- `engineering/chaos-engineering` — reliability practice
- `engineering/senior-architect` — technical decision making

## Output expectations

When the advisor runs, you should walk away with:

1. A clear **point of view**
2. **2–4 concrete next actions** with owners and timelines
3. **Open questions** that materially change the recommendation
4. References to scripts and reference docs that deepen the analysis
