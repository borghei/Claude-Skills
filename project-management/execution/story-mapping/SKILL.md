---
name: story-mapping
description: >
  Jeff Patton-style user story mapping for visualizing user journeys and
  translating product strategy into prioritized, deliverable work. Use for
  release planning, MVP definition, backlog sequencing, and cross-team
  alignment on what to build and in what order.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: project-management
  domain: pm-execution
  updated: 2026-04-10
  tech-stack: story-mapping, user-stories, release-planning, jeff-patton
---
# User Story Mapping Expert

## Overview

Visualize the user journey and translate strategy into prioritized, deliverable work using Jeff Patton's user story mapping technique. Story maps shift teams from feature-first thinking to flow-first thinking -- understanding the complete user experience before deciding what to build and in what order.

### When to Use

- **MVP definition** -- When you need to draw a clear line between "must ship" and "can wait."
- **Release planning** -- When sequencing work across multiple releases or sprints.
- **Cross-team alignment** -- When multiple teams need a shared understanding of the user journey.
- **Backlog reorganization** -- When a flat backlog has lost context and priority clarity.
- **New product kickoff** -- When starting from scratch and need to decompose a vision into work.

### When NOT to Use

- When work is purely technical infrastructure with no user journey (use technical spikes instead).
- When the team already has a well-prioritized, context-rich backlog.
- For single-feature work that doesn't span multiple user activities.

## Story Map Anatomy

A story map has three layers arranged in a 2D grid:

```
                    USER JOURNEY (left to right) →
                    
    ┌──────────────────────────────────────────────────┐
    │  Activities    Activity 1    Activity 2    Act 3  │  ← Backbone
    ├──────────────────────────────────────────────────┤
    │  Steps         Step 1.1      Step 2.1     Step   │  ← Backbone
    │                Step 1.2      Step 2.2      3.1   │
    ├──────────────────────────────────────────────────┤
    │  Tasks         Task A        Task D       Task G │  ← Body
    │  (Release 1)   Task B        Task E              │  ← MVP line
    │  ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ │
    │  Tasks         Task C        Task F       Task H │  ← Body
    │  (Release 2)                                     │  ← Follow-up
    └──────────────────────────────────────────────────┘
    
    PRIORITY (top to bottom) ↓
```

| Layer | What It Contains | Granularity |
|---|---|---|
| **Activities** | High-level user goals (what are they trying to accomplish?) | Epic-level |
| **Steps** | Sequential actions within each activity | Feature-level |
| **Tasks** | Specific implementation items for each step | Story-level |

### Key Principle: Flow First, Then Priority

- **Horizontal axis (left to right):** The user's journey through time -- activities and steps in the order users experience them.
- **Vertical axis (top to bottom):** Priority -- most critical tasks at the top, nice-to-haves at the bottom.
- **MVP line:** A horizontal line drawn across the map separating "Release 1" from "Later."

## Building a Story Map

### Step 1: Define Who and What

| Element | Description |
|---|---|
| **Segment** | The target user segment for this map |
| **Persona** | The specific persona experiencing this journey |
| **Narrative/JTBD** | The job or goal the user is trying to accomplish |
| **Decision** | What this map should inform (MVP scope, release plan, sequencing) |

### Step 2: Map the Backbone (Activities)

Walk through the user's journey and identify 3-7 high-level activities:

```markdown
#### Activities:
1. [Discover the product]
2. [Sign up and onboard]
3. [Complete core task]
4. [Review results]
5. [Share with team]
```

**Tips:**
- Use active verbs ("Discover," "Configure," "Review") not nouns.
- Keep to 3-7 activities -- more means you need to zoom out.
- Arrange left to right in the order users experience them.

### Step 3: Break Activities into Steps

For each activity, identify 3-5 sequential steps:

```markdown
#### Steps for "Sign up and onboard":
- Step 1: Create account
- Step 2: Verify email
- Step 3: Set up profile
- Step 4: Complete tutorial
- Step 5: Invite team members
```

### Step 4: Decompose Steps into Tasks

For each step, list specific implementation tasks:

```markdown
#### Tasks for "Create account":
- Email/password registration
- Social login (Google, GitHub)
- SSO integration
- Terms acceptance
- Password strength validation
```

### Step 5: Prioritize Vertically

Arrange tasks within each column from top (highest priority) to bottom (lowest):

- **Top:** Must-have for the journey to work at all.
- **Middle:** Important for a good experience.
- **Bottom:** Nice-to-have, can defer.

### Step 6: Draw Release Lines

Draw horizontal lines across the map to define releases:

```
═══════════════════════════ Release 1 (MVP) ═══════════
- Email/password registration
- Verify email
- Basic profile setup
- Core task (minimal)
- View results

═══════════════════════════ Release 2 ═══════════════════
- Social login
- Team invitations
- Advanced tutorial
- Share results
- Export results

═══════════════════════════ Release 3 (Polish) ══════════
- SSO integration
- Custom branding
- Advanced analytics
- API access
```

## Story Map Template

```markdown
## User Story Map

### Context
- **Segment:** [Target segment]
- **Persona:** [Persona name and key characteristics]
- **Narrative:** [The job or goal being mapped]
- **Decision:** [What this map informs]

### Backbone

#### Activities:
1. [Activity 1]
2. [Activity 2]
3. [Activity 3]
4. [Activity 4]
5. [Activity 5]

#### Steps:
**[Activity 1]:**
- Step 1: [Description]
- Step 2: [Description]
- Step 3: [Description]

**[Activity 2]:**
- Step 1: [Description]
- Step 2: [Description]
- Step 3: [Description]

[Continue for each activity]

#### Tasks:
**[Activity 1, Step 1]:**
- Task 1: [Description]
- Task 2: [Description]
- Task 3: [Description]

[Continue for each step]

### Release Slices

**Release 1 (MVP):**
- [Task list -- minimum viable journey]

**Release 2:**
- [Task list -- improved experience]

**Release 3:**
- [Task list -- full vision]

### Assumptions to Validate
- [Assumption 1]
- [Assumption 2]
- [Assumption 3]

### Risks and Dependencies
- [Risk or dependency 1]
- [Risk or dependency 2]
```

## Common Story Map Patterns

### Pattern 1: Walking Skeleton

Map the thinnest possible end-to-end journey first:

```
Activity 1 → Activity 2 → Activity 3 → Activity 4
    ↓             ↓             ↓             ↓
  1 task        1 task        1 task        1 task
```

One task per activity, proving the full flow works. Then add depth.

### Pattern 2: Thick Slice

When one activity is the core value, go deep there first:

```
Activity 1 → Activity 2 → Activity 3 → Activity 4
    ↓             ↓             ↓             ↓
  1 task        5 tasks       1 task        1 task
                (core)
```

### Pattern 3: Progressive Enhancement

Layer capabilities across releases:

```
Release 1:  Basic flow    (all activities, minimum tasks)
Release 2:  Error handling (edge cases, validation)
Release 3:  Power features (automation, customization)
Release 4:  Scale          (performance, enterprise)
```

## Facilitation Guide

### Running a Story Mapping Workshop

| Phase | Duration | Activity |
|---|---|---|
| **Setup** | 10 min | Define persona, narrative, and decision scope |
| **Backbone** | 20 min | Map activities and steps (sticky notes on wall or Miro) |
| **Body** | 30 min | Decompose into tasks (everyone contributes) |
| **Prioritize** | 15 min | Arrange vertically by priority |
| **Slice** | 15 min | Draw release lines; debate MVP scope |
| **Review** | 10 min | Identify risks, dependencies, and assumptions |

**Total:** ~100 minutes for a focused session.

**Materials:** Sticky notes (3 colors: activities, steps, tasks), markers, large wall or whiteboard, or Miro/FigJam for remote.

**Key facilitation rules:**
- Keep each sticky note to 4-8 words.
- Activities and steps first; resist jumping to tasks.
- Everyone writes, not just the PM.
- Debate the MVP line, not individual task priority.

## Integration with Other Skills

- Use `job-stories/` JTBD discovery canvas to define the narrative before mapping.
- Feed Release 1 tasks into `create-prd/` for detailed requirements.
- Use `prioritization-frameworks/` RICE scoring to prioritize within release slices.
- Use `brainstorm-okrs/` to align release slices with quarterly objectives.
- Convert tasks into user stories or job stories using `job-stories/` or `wwas/`.

## Troubleshooting

| Problem | Likely Cause | Resolution |
|---|---|---|
| Map has 10+ activities | Scope too broad; multiple journeys mapped as one | Split into separate maps per persona or JTBD; each map should cover one narrative |
| Tasks are too vague ("make it work") | Jumped to tasks without defining steps clearly | Revisit steps layer; ensure each step is a concrete user action |
| MVP line includes everything | Team can't say no; fear of shipping incomplete | Apply the "walking skeleton" pattern -- what's the minimum journey that works? |
| Map doesn't match backlog | Story map created once and never referenced | Post map in team space; reference it during sprint planning and refinement |
| Remote workshop produces shallow map | Digital tools don't create the same energy as physical sticky notes | Use breakout rooms for parallel step decomposition; time-box strictly |
| Activities are features, not user goals | Feature-first thinking; activities named after product features | Rewrite activities as user actions: "Configure dashboard" → "Understand my performance" |

## Success Criteria

- Story map covers one persona and one narrative end-to-end
- 3-7 activities spanning the complete user journey
- Each activity has 3-5 observable steps
- MVP line drawn with team consensus
- Release 1 (MVP) is a complete walking skeleton -- every activity has at least one task
- All tasks are independently deliverable (pass INVEST criteria)
- Map reviewed and updated at sprint boundaries

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

## References

- Jeff Patton, *User Story Mapping* (2014)
- Jeff Patton, "The New User Story Backlog Is a Map" (2005)
- Inspired by Productside story mapping workshops
