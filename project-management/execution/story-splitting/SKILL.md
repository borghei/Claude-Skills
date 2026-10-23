---
name: story-splitting
description: >
  Vertical-slicing playbook with 9 canonical Lawrence patterns for splitting
  epics into shippable user stories without losing user value. Use when a story
  is too big, exceeds cycle time, or fails INVEST-S.
license: MIT + Commons Clause
metadata:
  version: 1.0.1
  author: borghei
  category: project-management
  domain: pm-execution
  updated: 2026-06-15
  tech-stack: story-splitting, vertical-slicing, lawrence-flowchart, invest
  tags:
    - story-splitting
    - vertical-slicing
    - epics
    - user-stories
---
# Story Splitting (Vertical Slicing Patterns)

## Overview

A pattern catalog for splitting epics and large stories into smaller, shippable, end-to-end slices that still deliver user value. Built on Richard Lawrence's canonical story-splitting flowchart (the 9 patterns most product teams converge on) with worked before/after examples and a quick-reference decision tree.

The single most common reason teams fail to deliver predictably is that stories are too large. Large stories balloon in cycle time (see `cycle-time-analyzer/`), create coordination overhead, and resist incremental release. The remedy is not to estimate more carefully; it is to split smaller — vertically, so each slice (1) delivers value the end user can perceive, (2) fits in a single sprint, (3) is independently shippable, and (4) passes INVEST quality gates (see `wwas/`). The skill is pattern-based — no Python tool is needed; the value is the recipes and the worked examples.

## Core Capabilities

- **9 canonical Lawrence patterns** — workflow steps, business-rule variations, happy/unhappy path, input/output variations, data variations, data-entry methods, deferred performance/quality, CRUD operations, and break-out-a-spike (plus optional "Major Effort First").
- **Vertical-slicing decision tree** — a top-down tree that names the first applicable pattern for any oversized story.
- **Vertical-vs-horizontal discipline** — keeps every slice end-to-end and demoable instead of layer-by-layer.
- **Ordering & INVEST gating** — sequences slices smallest-value-first and verifies each against I-N-V-E-S-T.

## When to Use

- **Sprint refinement** -- A story exceeds the team's 85th-percentile cycle time or fails the INVEST-S (Small) test.
- **Epic decomposition** -- An epic from `create-prd/` or `story-mapping/` needs to be broken into a release backlog.
- **Stuck story** -- A story has been "almost done" for two sprints; usually a sign it should have been split.
- **New team onboarding** -- A team's stories are routinely too large; introduce the patterns explicitly.
- **Release planning** -- Need to find a thin slice that ships in 2 weeks instead of 8.

### When NOT to Use

- The work is a true atomic operation that genuinely cannot be split (rare; usually a sign of incomplete analysis).
- The team is splitting horizontally by layer (DB, API, UI) -- that produces non-shippable slices and defeats the point.
- The work is a spike (timeboxed investigation); spikes are intentionally not user-facing.

## Clarify First

Before splitting, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **The original story's user value in one sentence:** no clear value means reframe the problem (`create-prd/`), not split (gates the whole procedure, Step 1).
- **What ships next:** beta cohort vs general availability (changes which pattern applies: happy-path-only vs full business rules).
- **Why it's too big:** exceeds cycle time, fails INVEST-S, or has been "almost done" for sprints (points to the first applicable pattern in the decision tree).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Quick Start

1. **State the user value** of the original story in one sentence. (No clear value? Reframe the problem via `create-prd/`, don't split.)
2. **Walk the decision tree** (in `references/story-splitting-procedure.md`); stop at the first pattern that applies.
3. **Draft slices** in `wwas/` or `job-stories/` format; verify each is vertical (crosses all layers, independently demoable).
4. **Order slices** smallest-value-first, run the INVEST check, and replace the original story in the backlog.

## Anti-Patterns

### Splitting by acceptance criteria
**Mistake:** A story with 6 acceptance criteria becomes 6 stories: validate inputs, render PDF, attach signature, and so on.
**Why it happens:** The ACs are already a neat list, so they look like ready-made seams.
**Instead:** Treat ACs as checks on done, not as split points. If the story is still too big, walk the decision tree and split by a user-facing operation, such as "send simple offer letter" first. If the slice count exceeds the AC count, rethink the split.

### Splitting to fit sprint capacity
**Mistake:** The sprint is 4 points over, so a 5-point story is carved into "3 + 2" and the 3 is committed.
**Why it happens:** Carving off a piece feels more productive than deferring a story at the capacity wall.
**Instead:** Defer the whole story to the next sprint. Split only in refinement, only for value, and with a named Lawrence pattern. A split made in sprint planning because capacity is tight is a signal to defer instead.

### Slices that always close together
**Mistake:** Story A (backend filter) and story B (filter UI) must merge in the same PR and are marked done together.
**Why it happens:** The split was made for tracking, and nobody checked that each slice could ship alone.
**Instead:** Re-merge the two, or make each independently shippable behind a feature flag so A ships first and B follows. Two stories that always close together fail the Independent test in INVEST.

Seven more, each with a bad and a good example: `references/red-flags.md`.

## References

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/story-splitting-procedure.md](references/story-splitting-procedure.md)** — vertical-vs-horizontal slicing, all 9 patterns with before/after examples, the full decision tree, the optional tenth pattern, the 8-step workflow, an end-to-end worked example, troubleshooting, and success criteria. Read when splitting a specific story.
- **[references/splitting-patterns-guide.md](references/splitting-patterns-guide.md)** — the deepest pattern catalog: each pattern with cues, recipes, multiple worked examples, pattern-selection order, anti-patterns, and the post-split INVEST check. Read for the full theory or when a pattern is ambiguous.
- **[references/red-flags.md](references/red-flags.md)** — common ways splits go wrong, each with bad/good examples. Read before split tickets enter a sprint.
- **[assets/before-after-examples.md](assets/before-after-examples.md)** — 15+ before/after splits across SaaS, mobile, B2B, and platform scenarios. Use as a copy-from library.

## Scope & Limitations

**In Scope:**
- The 9 canonical Lawrence patterns plus optional "Major Effort First"
- Vertical-slicing decision tree
- Worked examples for SaaS, mobile, and B2B scenarios
- Integration with INVEST (via `wwas/`) and story mapping (via `story-mapping/`)

**Out of Scope:**
- User story format itself (use `wwas/`, `job-stories/`)
- Sprint capacity calculation (use `scrum-master/sprint_capacity_calculator.py`)
- Backlog prioritization (use `prioritization-frameworks/`)
- Story mapping at the release level (use `story-mapping/`)

**Important Caveats:**
- Splitting cannot rescue a poorly defined problem. If the story has no clear user value, the answer is problem framing (`create-prd/`), not slicing.
- Slicing has limits. A story may be at the smallest useful size and still feel large because the team has not done the work before. Treat the first few of any new kind of story as a learning tax.
- The "right" split depends on what ships next. The same epic can be split differently for a beta cohort (Pattern 3: happy path only) vs general availability (Pattern 2: full business rules). Choose based on the next release context, not in the abstract.

## Integration Points

| Integration | Direction | What Flows |
|-------------|-----------|------------|
| `wwas/` | Output format | Split slices are written as WWAS items |
| `job-stories/` | Output format | Alternative format for situation-driven slices |
| `create-prd/` | Receives from | Epic-level scope from PRD feeds splitting |
| `story-mapping/` | Complementary | Story map identifies the slices that need splitting |
| `prioritization-frameworks/` | Feeds into | Split slices get individually scored (RICE/ICE) for ordering |
| `cycle-time-analyzer/` | Diagnostic for | Long cycle times indicate stories that should have been split |
| `backlog-refinement/` | Used in | Splitting is the core activity in refinement sessions |
| `scrum-master/` | Improves | Predictability improves dramatically when stories are uniformly small |

## Further Reading

- Lawrence, Richard. "Patterns for Splitting User Stories." 2009. (The original 9-pattern catalog.)
- Lawrence, Richard. *Story Splitting Flowchart*, 2012. (The canonical visual decision tree.)
- Cohn, Mike. *User Stories Applied for Agile Software Development*. Addison-Wesley, 2004. (INVEST criteria.)
- Patton, Jeff. *User Story Mapping*. O'Reilly, 2014. (Vertical slicing in release planning.)
