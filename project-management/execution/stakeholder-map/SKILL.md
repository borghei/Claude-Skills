---
name: stakeholder-map
description: >
  Maps stakeholders by power, interest and stance, then plans engagement and
  blocker conversion so objections surface early. Use for a major initiative,
  an enterprise deal, a re-org or a contested roadmap change.
license: MIT + Commons Clause
metadata:
  version: 1.1.0
  author: borghei
  category: project-management
  domain: execution
  updated: 2026-11-08
  python-tools: stakeholder_analyzer.py
  tech-stack: stakeholder-mapping, power-interest, change-management
  tags:
    - stakeholder-mapping
    - power-interest
    - communication-plan
    - change-management
---

# Stakeholder Map

The agent builds a power x interest map with each person's stance, then an engagement plan that matches cadence to influence and gives every blocker a conversion plan. The point is to have no surprise vetoes late in the initiative.

**Done looks like:** stakeholders listed broadly (sponsors, decision-makers, veto holders, implementers, users, external parties), each rated power and interest 1-5 with a stance from champion to blocker; quadrant cadences met (manage closely weekly or tighter with an owner, keep satisfied at least monthly); every skeptic and blocker with a conversion plan; `stakeholder_analyzer.py` exits 0.

## When to Use

- Launching a major initiative (re-platform, pricing change, market expansion)
- An enterprise deal with a buying committee, or a re-org
- A roadmap change that hits several teams, or a pre-board decision
- A post-mortem: who did we fail to engage?

## Clarify First

Before mapping, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **The initiative being mapped:** the specific launch/deal/re-org/roadmap change (defines who counts as a stakeholder at all, Step 1).
- **Each stakeholder's power source:** hierarchy vs veto vs budget vs domain expertise (a compliance lead may outrank a VP; drives the Power axis in Step 2).
- **Each stakeholder's stance:** champion → supporter → neutral → skeptic → blocker (drives Step 3 and the conversion plans in Step 6).
- **Decision/launch deadline:** when the verdict lands (sets engagement cadence per quadrant, Step 5).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Quick Start

```bash
# Six-person billing rollout map with cadences and a skeptic plan: exit 0
python3 project-management/execution/stakeholder-map/scripts/stakeholder_analyzer.py \
  --input project-management/execution/stakeholder-map/assets/sample_stakeholders.json --format markdown
```

```bash
# High-power blocker with no plan, missing owners and cadences: exit 1
python3 project-management/execution/stakeholder-map/scripts/stakeholder_analyzer.py \
  --input project-management/execution/stakeholder-map/assets/sample_stakeholders_flawed.json --format markdown
```

```bash
# Input schema and flags
python3 project-management/execution/stakeholder-map/scripts/stakeholder_analyzer.py --help
```

## Tools Overview

`stakeholder_analyzer.py` is the quality gate for this skill. **What the analyzer checks:** each stakeholder named, with power and interest in 1-5 and a valid stance; manage-closely people with weekly-or-tighter cadence and an owner; keep-satisfied people with at least monthly cadence and an owner; skeptics and blockers with a conversion plan (fail for a blocker with power 4-5); at least one manage-closely stakeholder; a thin list for an initiative labelled "major". It checks only the people listed and cannot find who is missing.

**Exit codes:** `0` no fail findings · `1` at least one fail (an unnamed stakeholder, no stakeholders, a high-power blocker without a plan) · `2` unreadable file, invalid JSON or a top level that is not an object. JSON by default, `--format markdown`, `--output FILE`.

## Workflow

1. **List broadly.** Sponsors, decision-makers, veto holders, influencers, implementers, users, adjacent teams, vendors, regulators. Prune later; the person you skip is usually the one who objects.
2. **Rate power and interest (1-5).** Power is more than hierarchy: budget control, veto (legal, compliance, security), domain expertise, coalition and external legitimacy. A compliance lead with a veto often outranks a VP. Ratings of 4-5 count as high.
3. **Add stance:** champion, supporter, neutral, skeptic, blocker.
4. **Find the people to convert:** high power, high interest, not yet supporters.
5. **Set engagement per quadrant.** Manage closely: weekly 1:1 and co-authoring. Keep satisfied: monthly pre-briefs so they do not tune in late and veto. Keep informed: updates and a visible place for their concerns. Monitor: light touch.
6. **Plan each blocker.** The real objection (often not the stated one), the evidence that might move them, who they listen to, and whether to convert, neutralise or out-vote. Escalate when their authority is structurally needed; never route around legal, security, compliance or finance approvers.
7. **Audit.** Write the map as JSON (schema in `--help`; `assets/sample_stakeholders.json`) and run the analyzer. It must pass with no fail findings; then verify that each warning is fixed. Refresh the map each quarter or project phase.

Engagement patterns for sponsors, powerful skeptics, powerless advocates and absent leaders are in the appendix of `references/stakeholder-mapping-framework.md`.

## Anti-Patterns

### Power read off the org chart
**Mistake:** Only VPs and above are rated high power.
**Why it happens:** Hierarchy is visible; vetoes and expertise are not.
**Instead:** Rate budget, veto, expertise and coalition power too. The security reviewer who can block go-live belongs in manage closely or keep satisfied.

### The sleeping authority
**Mistake:** A high-power, low-interest executive hears about the initiative at the final review and vetoes it.
**Why it happens:** Low interest reads as low priority.
**Instead:** Give every keep-satisfied stakeholder an owner and a monthly pre-brief; five-minute readouts are enough.

### A map with no plan
**Mistake:** The 2x2 is drawn and filed.
**Why it happens:** Mapping feels like the work.
**Instead:** Every quadrant gets a cadence and an owner, and every blocker a conversion plan with a date.

More with fixes: `references/stakeholder-anti-patterns.md`.

## Scope & Limitations

**In Scope:**
- A Power x Interest 2x2 with 1-5 ratings and four quadrants: manage closely, keep satisfied, keep informed and monitor
- A support stance per stakeholder from champion to blocker, and the high-power, high-interest, not-yet-supportive group to convert
- Engagement cadence per quadrant and conversion plans for blockers and skeptics
- A map audit for cadence and owners by quadrant, blockers and skeptics without plans, and missing decision-makers (`stakeholder_analyzer.py`)
- Launch, re-org, enterprise buying-committee and failed-launch post-mortem maps

**Out of Scope:**
- Assigning decision rights for a specific decision (see `project-management/execution/daci-framework/`)
- Writing the status updates and communications that the engagement plan calls for (see `project-management/execution/status-update-generator/` and `project-management/team-communications/`)
- Running a sales deal strategy beyond the stakeholder map (see `business-growth/sales-engineer/`)
- Legal and regulatory review of the initiative (see `c-level-advisor/general-counsel-advisor/`)

**Important Caveats:**
- Power, interest and support ratings are judgment calls entered by hand. The tool audits the map it is given and cannot discover missing people.
- The skill recommends building the map with someone politically aware. A solo map often misses lateral resistance.
- Power and stance shift. The map goes stale unless it is refreshed each quarter or project phase.
- The map can hold sensitive opinions about named colleagues. Who sees it is the team's call.

## Files

| File | Purpose |
|------|---------|
| `scripts/stakeholder_analyzer.py` | Stakeholder map audit |
| `assets/sample_stakeholders.json` | Billing rollout map; exits 0 |
| `assets/sample_stakeholders_flawed.json` | Map with an unplanned high-power blocker; exits 1 |
| `assets/stakeholder_map_template.md` | Fill-in template |

## Reference Documentation

- [references/stakeholder-mapping-framework.md](references/stakeholder-mapping-framework.md): Power and interest dimensions, support spectrum, engagement patterns
- [references/stakeholder-anti-patterns.md](references/stakeholder-anti-patterns.md): Common failures and fixes

## Related skills

- `project-management/execution/daci-framework` — decision-rights model
- `project-management/execution/summarize-meeting` — communication artifacts
- `c-level-advisor/ceo-advisor` — executive context
- `c-level-advisor/general-counsel-advisor` — legal stakeholder navigation
- `business-growth/sales-engineer` — buying-committee mapping
