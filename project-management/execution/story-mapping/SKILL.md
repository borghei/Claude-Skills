---
name: story-mapping
description: >
  Jeff Patton-style user story mapping for visualizing user journeys, MVP
  definition, release planning, backlog sequencing, and cross-team alignment.
license: MIT + Commons Clause
metadata:
  version: 1.0.1
  author: borghei
  category: project-management
  domain: pm-execution
  updated: 2026-06-15
  tech-stack: story-mapping, user-stories, release-planning, jeff-patton
  tags:
    - story-mapping
    - user-journey
    - mvp
    - release-planning
---
# User Story Mapping Expert

## Overview

Visualize the user journey and translate strategy into prioritized, deliverable work using Jeff Patton's user story mapping technique. Story maps shift teams from feature-first thinking to flow-first thinking -- understanding the complete user experience before deciding what to build and in what order.

A story map is a 2D grid: the **backbone** (activities → steps) runs left-to-right in the order users experience the journey, the **body** (tasks) hangs below each step ranked top-to-bottom by priority, and a horizontal **MVP line** separates Release 1 from later. See the playbook reference for full anatomy and the 6-step build sequence.

## When to Use

- **MVP definition** -- Draw a clear line between "must ship" and "can wait."
- **Release planning** -- Sequence work across multiple releases or sprints.
- **Cross-team alignment** -- Give multiple teams a shared understanding of the user journey.
- **Backlog reorganization** -- Restore context and priority to a flat backlog.
- **New product kickoff** -- Decompose a vision into work from scratch.

### When NOT to Use

- Purely technical infrastructure work with no user journey (use technical spikes).
- The team already has a well-prioritized, context-rich backlog.
- Single-feature work that doesn't span multiple user activities.

## Clarify First

Before building the map, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **The user and their end-to-end journey:** who travels it and the activities → steps in order (defines the backbone, the left-to-right spine of the map).
- **The target release / MVP:** what must ship first vs can wait (sets where the MVP line is drawn between Release 1 and later).
- **The map's goal:** MVP definition vs release sequencing vs cross-team alignment (changes how the body tasks are sliced and prioritized).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Anti-Patterns

### Skipping the walking skeleton
**Mistake:** Release 1 polishes sign-up and activation but has no cards under Pay or Upgrade, so users can't finish a real workflow.
**Why it happens:** The first steps of the journey are the most familiar, so the team fills them in depth before reaching the end.
**Instead:** Make R1 the thinnest end-to-end slice: 1-3 stories under every backbone step, each minimal. If any backbone column has zero R1 cards, there is no walking skeleton yet. Enrich steps in R2 where data shows friction.

### Implementation tasks on the map
**Mistake:** Cards read "set up Postgres", "configure Auth0", "write /users endpoint" instead of what the user does.
**Why it happens:** Engineers think in build tasks, and those tasks feel like the real work to plan.
**Instead:** Every card describes a user action ("enter email and password", "verify via email link"). Keep implementation work as sub-tickets in the tracker. If a card describes a system or code, rewrite it as a user story.

### Building the map alone
**Mistake:** The PM builds the map over a weekend and presents it to the team on Monday.
**Why it happens:** Solo work is easier to schedule than a workshop, and the PM already holds most of the context.
**Instead:** Build the map in a workshop with PM, design lead, eng lead and someone close to customers, using the facilitation guide in `references/playbook.md`. The shared understanding is the output. A map with a single author should be redone as a workshop.

Seven more, each with a bad and a good example: `references/red-flags.md`.

## References

- **[references/playbook.md](references/playbook.md)** — read this when building a map: story-map anatomy, the 6-step build sequence, the artifact template, map patterns (walking skeleton / thick slice / progressive enhancement), the workshop facilitation guide, troubleshooting, and success criteria.
- **[references/red-flags.md](references/red-flags.md)** — read this before using a map for release planning: common ways a story map goes wrong with bad/good quoted examples and fixes.

## Scope & Limitations

**In Scope:** User story map creation, backbone and body decomposition, release slice definition, MVP scoping, facilitation guidance, workshop planning, template and pattern library.

**Out of Scope:** Individual story writing and acceptance criteria (see `job-stories/` or agile-product-owner), technical architecture decisions, detailed effort estimation, sprint planning mechanics.

**Important Caveats:** Story maps are planning tools, not contracts. They should be updated as the team learns. A map created before building will always be wrong in details -- the value is in the shared understanding, not the artifact itself. Jeff Patton: "The map is not the territory; the conversation is the territory."

## Integration Points

| Integration | Direction | What Flows |
|---|---|---|
| `job-stories/` | Receives from | JTBD discovery canvas defines the narrative for mapping |
| `create-prd/` | Feeds into | Release 1 tasks inform PRD scope (Sections 7 and 8) |
| `prioritization-frameworks/` | Complements | RICE scoring prioritizes within release slices |
| `brainstorm-okrs/` | Complements | Release slices align with quarterly OKR targets |
| `outcome-roadmap/` | Feeds into | Release slices map to Now/Next/Later roadmap horizons |
| `wwas/` | Feeds into | Tasks become WWAS backlog items with strategic context |

## Further Reading

- Jeff Patton, *User Story Mapping* (2014)
- Jeff Patton, "The New User Story Backlog Is a Map" (2005)
- Inspired by Productside story mapping workshops
