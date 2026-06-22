---
name: stakeholder-map
description: >
  Map stakeholders by power × interest and design a communication plan
  that prevents surprise objections. Use when launching a major
  initiative, navigating an enterprise deal, planning a re-org, or
  pre-empting resistance to a roadmap change.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: project-management
  domain: execution
  updated: 2026-05-27
  python-tools: stakeholder_analyzer.py
  tech-stack: stakeholder-mapping, power-interest, change-management
---

# Stakeholder Map

A 2x2 grid of stakeholders, plus a tactical engagement plan derived from
the map. Used to pre-empt resistance, route decisions correctly, and
match communication cadence to influence.

## When to use this skill

- **Major initiative launch** (re-platform, pricing change, market expansion)
- **Enterprise deal navigation** (multiple buying-committee members)
- **Org re-design / re-org planning**
- **Roadmap change** affecting multiple stakeholders
- **Pre-board / pre-exec strategic decisions**
- **Post-mortem stakeholder map** (who didn't we engage that we should have?)

## The 2x2: Power × Interest

|                 | **Low Power**     | **High Power**       |
|-----------------|--------------------|----------------------|
| **High Interest** | Keep informed    | Manage closely        |
| **Low Interest**  | Monitor          | Keep satisfied        |

### Quadrants
- **Manage closely (HP/HI):** key decisions; influence + engaged. Highest investment.
- **Keep satisfied (HP/LI):** authority but not engaged. Don't let them surprise you.
- **Keep informed (LP/HI):** advocates and detractors who care. Use them.
- **Monitor (LP/LI):** light touch.

## Clarify First

Before mapping, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **The initiative being mapped** — the specific launch/deal/re-org/roadmap change (defines who counts as a stakeholder at all, Step 1)
- [ ] **Each stakeholder's power source** — hierarchy vs veto vs budget vs domain expertise (a compliance lead may outrank a VP; drives the Power axis in Step 2)
- [ ] **Each stakeholder's stance** — champion → supporter → neutral → skeptic → blocker (drives Step 3 and the conversion plans in Step 6)
- [ ] **Decision/launch deadline** — when the verdict lands (sets engagement cadence per quadrant, Step 5)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Workflow

### Step 1 — List all stakeholders
Brainstorm:
- Executive sponsors
- Decision-makers
- Influencers
- Implementers
- Users / customers
- Adjacent teams
- External parties (vendors, regulators, partners)

Don't filter yet. List broadly, prune later.

### Step 2 — Rate Power + Interest (1-5)
For each:
- **Power:** can they kill or accelerate this? authority? budget? veto?
- **Interest:** how much do they care about the outcome?

### Step 3 — Add Support (stance)
Each stakeholder is also somewhere on:
- **Champion** (actively supports)
- **Supporter** (positive but passive)
- **Neutral**
- **Skeptic**
- **Blocker** (actively opposes)

This complements Power×Interest with directionality.

### Step 4 — Identify the matrix sweet spot
The critical stakeholders: high power + high interest + not-yet-supporters.

These are who you need to convert.

### Step 5 — Design engagement plan per quadrant

| Quadrant | Engagement pattern |
|----------|---------------------|
| Manage closely | Weekly 1:1, deep involvement, co-author key docs |
| Keep satisfied | Monthly check-in, pre-brief major decisions |
| Keep informed | Email updates, FYI inclusion, surface their concerns publicly |
| Monitor | Quarterly newsletter; no proactive |

### Step 6 — Address blockers explicitly
For each blocker:
- What's their objection?
- What evidence might change their view?
- Who do they listen to?
- Can we convert, neutralize, or out-vote?

Ignoring blockers = late surprise objection that derails the initiative.

### Step 7 — Run `stakeholder_analyzer.py`
Audit for: missing key stakeholders by role, blockers without plans,
power-without-interest gaps, no engagement plan.

```bash
python3 project-management/execution/stakeholder-map/scripts/stakeholder_analyzer.py \
  --input stakeholders.json --format markdown
```

## Decision frameworks

### Power dimensions (be specific)
- Hierarchical authority (CEO/board > VP > Director)
- Budget control (who allocates $)
- Veto power (legal, compliance, infosec)
- Domain expertise (the one person who actually understands X)
- Coalition power (who their faction follows)
- External legitimacy (analyst, customer reference, regulator)

A "low-hierarchy / high-veto" stakeholder (e.g., compliance lead) often
has more power than a "high-hierarchy / low-domain" one.

### Interest dimensions
- Outcome impact (will this affect their world?)
- Personal stake (career, comp, ego)
- Resource impact (their team, their budget)
- Public visibility (their reputation tied to this)

### Common engagement patterns

**For executive sponsor (HP/HI):**
- Weekly 1:1 (you bring updates + asks)
- Co-author the strategic narrative
- Defend at board level
- Veto power to be used selectively

**For powerful skeptic (HP/HI, low support):**
- Discover the actual objection (often different than stated)
- Find evidence that addresses it
- Pre-brief before big decisions
- Make their support visible to their peers

**For powerless advocate (LP/HI, high support):**
- Use them to influence others
- Amplify their voice publicly
- Don't burn them with surprise asks

**For powerful absent leader (HP/LI):**
- Don't let them tune in late and veto
- Pre-brief before key decisions
- Make engagement low-friction (5-min readouts)

### When to escalate vs route around
- Escalate when: stakeholder's authority is structurally needed
- Route around when: stakeholder is tangential and adding friction
- Never route around: legal, security, compliance, finance approvers

## Common engagements

### "Help me build a stakeholder map for the launch"
1. Brainstorm 20+ stakeholders.
2. Rate Power, Interest, Support per stakeholder.
3. Plot the 2x2.
4. Identify the critical 5-10 (HP/HI).
5. For each blocker, design conversion plan.
6. Document engagement cadence per quadrant.

### "Audit a recent failed launch"
1. Map the stakeholders involved.
2. Identify who derailed it (often a HP/LI we missed).
3. Identify who could have helped but wasn't engaged.
4. Update default stakeholder template for next launch.

### "Navigate an enterprise deal with 8 buying-committee members"
1. Map all 8 + 4-5 unofficial influencers.
2. Identify economic buyer, technical buyer, user, executive sponsor.
3. Engagement plan per role.
4. Address blockers (legal, security) early; don't wait for procurement.

## Anti-patterns to avoid

- **No stakeholder map.** Trust the org chart; surprised by lateral resistance.
- **Map without engagement plan.** Knowing isn't acting.
- **Ignoring blockers.** They surface at the worst moment.
- **Treating power as just hierarchy.** Vetoes matter; expertise matters.
- **No HP/LI engagement.** Sleeping authority becomes late veto.
- **Static map.** Power + stance shift; refresh per quarter / per phase.
- **Mapping without input from someone politically savvy.** Solo maps miss reality.

## References

- `references/stakeholder-mapping-framework.md` — power dimensions, support spectrum, engagement plans
- `references/stakeholder-anti-patterns.md` — common failures + worked fixes

## Related skills

- `project-management/execution/daci-framework` — decision-rights model
- `project-management/execution/summarize-meeting` — communication artifacts
- `c-level-advisor/ceo-advisor` — executive context
- `c-level-advisor/general-counsel-advisor` — legal stakeholder navigation
- `business-growth/sales-engineer` — buying-committee mapping
