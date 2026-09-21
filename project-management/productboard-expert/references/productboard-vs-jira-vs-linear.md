# Productboard vs Jira vs Linear

Productboard, Jira, and Linear all "track work", but they sit at different layers of the product-development stack. Choosing the wrong tool for the layer — or worse, using one tool to do all three jobs — produces predictable failure modes: a Jira instance with a million stale "feature ideas", a Linear workspace with no customer evidence, or a Productboard installation with no engineering follow-through.

This guide explains the layers, the concept translations across the three tools, and when each combination makes sense.

## The three layers

### Layer 1: Customer evidence

The inbound stream — what customers, prospects, and internal stakeholders are asking for. Examples: a Slack message from sales, a Salesforce opportunity note, an Intercom conversation, an NPS verbatim.

- **Productboard**: native fit. Insights are the data model's central concept.
- **Jira**: poor fit. Jira Service Management ingests support requests, but the data model treats them as tickets, not as evidence linked to product candidates.
- **Linear**: partial fit. Linear Triage can receive inbound, but it lacks the customer-evidence relationship and segment-level analytics.

### Layer 2: Product decision

The candidate product changes — features, epics, themes — that the PM scores and prioritizes. Examples: "Shareable read-only link", "AI-powered query assistant", "Audit log for enterprise".

- **Productboard**: native fit. Features + Drivers + Releases are the data model.
- **Jira**: workable. Epics are Jira's analog, but Jira lacks first-class Driver scoring; teams shoe-horn scoring into custom fields.
- **Linear**: workable. Projects are Linear's analog. Linear's Initiative/Project/Issue hierarchy is cleaner than Jira's for outcome-level rollups but still not as PM-focused as Productboard.

### Layer 3: Engineering execution

The implementation breakdown — stories, tasks, subtasks, bugs, deploys. Examples: "API change to support sharing tokens", "Frontend share-link generator UI", "QA test plan".

- **Productboard**: not the right tool. Productboard has Feature lifecycle states but lacks per-issue workflow, code-integration, sprint boards, and the engineering-specific affordances.
- **Jira**: native fit. Jira's flexibility, workflow customization, and ecosystem of integrations is the strongest of the three at this layer.
- **Linear**: native fit. Linear's opinionated, keyboard-driven UI is preferred by engineering teams that prioritize speed and resist Jira's customization complexity.

## When to use each combination

### Pattern 1: Productboard + Jira

Most common at companies with established engineering practices on Jira. Productboard owns layers 1-2; Jira owns layer 3.

- **Pros**: PM gets the right tool for prioritization; engineering keeps its existing Jira workflows; two-way integration is mature.
- **Cons**: Two systems to maintain; subscription cost stacks; integration drift requires monitoring.
- **Best when**: company is on Jira already (typical for companies > 200 employees); PM team wants a dedicated tool; engineering teams use Jira's full feature set (workflows, custom fields, JQL).

### Pattern 2: Productboard + Linear

Increasingly common at modern startups (2024-2026). Productboard owns layers 1-2; Linear owns layer 3.

- **Pros**: Modern, fast, both tools optimized for their layer; UX is consistent in feel between the two.
- **Cons**: Same as Pattern 1 — two systems, two costs, integration to maintain.
- **Best when**: company is a Linear-native team; engineering values Linear's opinionated workflow; PM needs Productboard's depth on prioritization and customer evidence.

### Pattern 3: Productboard alone (no engineering tracker)

Rare and not recommended. Productboard's per-Feature lifecycle doesn't substitute for an engineering tracker. Teams that try this end up with:

- Engineering work tracked in spreadsheets, GitHub Issues, or ad hoc Slack
- Lost work visibility for cross-functional stakeholders
- Friction at the PM-Eng handoff

The exception: very small teams (< 10 engineers) where GitHub Issues + Productboard is sufficient.

### Pattern 4: Linear alone

Common at engineering-led companies that resist a separate PM tool. Linear owns layers 2-3; layer 1 (customer evidence) is handled informally (Slack channels, ad hoc notes).

- **Pros**: One tool, one cost, fast UX, engineering buy-in.
- **Cons**: Customer-evidence layer is shallow; PMs reinvent the Insight inbox using Linear Triage; prioritization criteria are ad hoc.
- **Best when**: PM-to-Engineer ratio is low (1:8+); product is engineering-led; customer feedback volume is manageable in ad hoc channels.

### Pattern 5: Jira alone

Common at enterprise / regulated environments where Jira is the system-of-record by mandate. Jira tries to own all three layers.

- **Pros**: One vendor; existing Atlassian compliance posture.
- **Cons**: Layer 1 (customer evidence) is a poor fit; layer 2 (prioritization) lacks first-class Drivers; PMs work in spreadsheets and paste into Jira.
- **Best when**: company mandates Jira; PM is willing to build prioritization scaffolding in custom fields and Confluence pages.

### Pattern 6: Productboard + Jira + Linear

Rare; usually a transitional state during a Jira → Linear migration. Productboard handles 1-2; some teams have moved to Linear (layer 3) while others remain on Jira. Productboard syncs to both.

- Manageable but operationally complex; not a long-term steady state.

## Concept translation

| Productboard | Jira | Linear |
|---|---|---|
| Workspace | Site / Instance | Workspace |
| Product / Workspace | Project | Team |
| Component (hierarchy) | Component or Epic (parent) | Project or Label |
| Feature | Epic | Project (cross-cycle) or Issue (within-cycle) |
| Parent Feature | Epic with child Epics, or a custom hierarchy in Plans (formerly Advanced Roadmaps) | Project containing Issues |
| Child Feature | Story | Issue or Sub-issue |
| Insight / Note | (no native concept; teams use Jira Service Management or custom fields) | (no native concept; teams use Triage or descriptions) |
| Customer | (no native concept; tracked in linked Salesforce / Jira customer portal) | (no native concept) |
| Driver | Custom field (e.g. RICE score components) | Custom field (limited; labels often substitute) |
| Objective | Strategic Initiative (Plans) | Initiative (top of Linear hierarchy) |
| Release | Version | Cycle, Project (with target date), Milestone |
| Release Group | Release version pattern | Cycle group (informal) |
| Roadmap view | Plans timeline | Roadmap view (filtered Projects) |
| Feature status (Idea → Planned → In Progress → Done) | Issue status workflow (any custom) | Issue state (backlog/unstarted/started/completed/canceled) |

## Migration scenarios

### From Jira-only to Productboard + Jira

The most common adoption path. Steps:

1. **Audit Jira**: how many "ideas" / Epics sit in a "Future" status? Those should move to Productboard.
2. **Set up Productboard**: Component hierarchy, initial Drivers, Customers/Companies sync.
3. **Migrate the idea backlog**: Jira Epics with status "Future" become Productboard Features. Use the Jira API to read, the Productboard API to write.
4. **Install the integration**: connect Productboard ↔ Jira; map statuses and Releases ↔ Versions.
5. **Establish the handoff point**: a Feature pushes from Productboard to Jira when status moves to "Planned" or "In Progress".
6. **Train the team**: PMs operate primarily in Productboard; engineering operates in Jira; the handoff is at "Planned".

### From Linear-only to Productboard + Linear

Less mature pattern but increasingly seen. Steps similar to Jira:

1. Audit Linear Projects in "Planned" or earlier states — those become Productboard Features.
2. Set up Productboard with the Linear integration.
3. Map Productboard Releases to Linear Cycles or Projects.
4. Decide on the handoff point — typically when Feature status moves to "In Progress", create the Linear Project.

### Productboard sunset (back to Jira/Linear alone)

A team that decides Productboard isn't pulling its weight can sunset:

1. Export all Features and Insights via API.
2. Move "active" Features (status >= Planned) into Jira/Linear as Epics/Projects.
3. Archive Insights to a searchable wiki (Confluence/Notion) — they're customer evidence and should not be lost.
4. Cancel the Productboard subscription.

The most common reason for sunsetting Productboard: the team didn't develop a daily Insight inbox triage habit, so the tool degraded into another stale backlog.

## Decision framework

If you can answer "yes" to most of these, Productboard adds value:

- [ ] You receive customer feedback from 3+ channels (support, sales, NPS, etc.) and lose track of it.
- [ ] Your PM team is more than 1 person; consistency across PMs matters.
- [ ] You score Features against more than one criterion (revenue, strategic fit, customer demand, effort).
- [ ] Your engineering tracker has 50+ stale "idea" tickets that nobody triages.
- [ ] Sales asks "did you build that thing customer X asked for?" and you struggle to answer.
- [ ] You want a customer-facing public roadmap.
- [ ] You sync customer data from Salesforce or HubSpot for prioritization context.

If most answers are "no", Linear/Jira alone is sufficient and Productboard is overhead.

## Cost considerations (as of 2026 pricing)

Productboard prices per Maker seat (the PMs and POs); Viewers (read-only) are typically much cheaper. Compare against:

- The cost of an extra PM hour spent on triage in spreadsheets
- The cost of building wrong things because customer evidence is invisible
- The cost of a separate spreadsheet/Notion-based prioritization system

Productboard is most economically defensible at PM team sizes of 3+ and product surface areas of 5+ Components. Below that, the ROI is harder.

## When NOT to add Productboard

- Single-PM team — the overhead exceeds the value
- Pre-PMF startup — the team needs to talk to customers, not score features
- Highly regulated environment where every tool requires compliance review (the cost of vendor onboarding exceeds the gain)
- Internal-only tools — the customer-evidence concept doesn't translate to internal stakeholder requests as cleanly

## See also

- `references/productboard-api-patterns.md` — API call patterns for integrating Productboard with anything
- `jira-expert/SKILL.md` — Jira-side configuration for the integration
- `linear-expert/SKILL.md` — Linear-side configuration for the integration
- `execution/prioritization-frameworks/SKILL.md` — when the Driver model alone isn't enough
