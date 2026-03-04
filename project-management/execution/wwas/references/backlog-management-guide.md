# Backlog Management Guide

## WWAS Format Explained

Why-What-Acceptance (WWAS) is a backlog item format designed to ensure strategic alignment without over-specifying implementation. It was developed as a response to two common failure modes:

1. **Backlog items with no strategic context** -- Teams build features without understanding why they matter, leading to disconnected product decisions and difficulty prioritizing.
2. **Backlog items that are over-specified** -- Detailed specifications masquerading as backlog items remove the team's ability to negotiate implementation and slow down refinement.

WWAS solves both by requiring a strategic Why, keeping the What brief, and defining acceptance through observable outcomes.

### The Three Parts

**Why (1-2 sentences):**
Connects the item to a business objective, OKR, or strategic theme. Answers "Why does this matter?" and "Why now?" If you cannot write a compelling Why, the item should not be prioritized.

**What (1-2 paragraphs):**
A reminder of what was discussed during refinement. Not a specification. The team should read this and recall the conversation. Includes a design link if applicable.

**Acceptance Criteria (4+ items):**
Observable outcomes that define done. Not implementation steps. Not test scripts. Just the conditions that must be true for the team to consider the item complete.

## Comparison with User Stories and Job Stories

| Aspect | User Story | Job Story | WWAS |
|--------|-----------|-----------|------|
| **Format** | As a [role], I want [action], so that [benefit] | When [situation], I want [motivation], so I can [outcome] | Why / What / Acceptance |
| **Strength** | Simple, role-centric | Situation-centric, design-friendly | Strategy-centric, business-aligned |
| **Strategic context** | Minimal (the "so that" is often weak) | Minimal (focuses on user outcome) | Explicit (the Why section) |
| **Specification level** | Varies widely | Moderate | Intentionally brief |
| **Best for** | Teams familiar with agile basics | Design-driven product teams | Strategy-conscious product teams |
| **Risk** | Becomes formulaic, loses meaning | Requires deep user research | Why can become boilerplate if not genuine |

### When to Use Each

- **User Stories** -- When the team is agile-fluent and roles are well-defined. Good for CRUD features and internal tools.
- **Job Stories** -- When you need to deeply understand user situations and design for context. Good for consumer products and UX-heavy work.
- **WWAS** -- When strategic alignment is the primary concern. Good for enterprise products, teams with business stakeholders, and roadmap-driven development.

You can mix formats within the same backlog. Use the format that best serves each item.

## INVEST Criteria Deep Dive

### Independent

**Definition:** The item can be developed, tested, and delivered without requiring another item to be completed first.

**Why it matters:** Dependent items create scheduling constraints, block parallel work, and increase the risk of partial delivery.

**How to check:**
- Can the team start this item on day one of the sprint without waiting?
- Can this item be released to users on its own?
- If another item is delayed, does this item still make sense?

**How to fix dependencies:**
- Combine small dependent items into one larger item.
- Redefine the item boundary to include the dependency.
- Extract the shared dependency as its own item and schedule it first.

### Negotiable

**Definition:** The item describes what and why, not how. The implementation approach is open for the team to decide.

**Why it matters:** Prescriptive items prevent the team from applying their expertise, reduce ownership, and miss opportunities for simpler solutions.

**How to check:**
- Does the What section mention specific technologies, UI patterns, or architecture?
- Could the team solve this in at least two different ways?
- Is the design link a constraint or a starting point for discussion?

**How to fix:**
- Remove implementation details from the What.
- Replace "Build a dropdown menu" with "Allow the user to select from available options."
- Move technical specifications to a linked design document.

### Valuable

**Definition:** The item delivers value that a user or business stakeholder cares about.

**Why it matters:** Items without clear value consume capacity without moving the needle. They also demoralize teams who cannot see the impact of their work.

**How to check:**
- Does the Why connect to a real, measurable business objective?
- Would a user notice or care if this item were shipped?
- Can you explain the value to a non-technical stakeholder in one sentence?

**How to fix:**
- Rewrite the Why with a specific objective and metric.
- If the item is purely technical (refactoring, upgrades), frame the Why in terms of what it enables or unblocks.
- If no value can be articulated, reconsider whether the item belongs in the backlog.

### Estimable

**Definition:** The team can estimate the effort required with reasonable confidence.

**Why it matters:** Unestimable items indicate insufficient understanding, which leads to surprises during implementation.

**How to check:**
- Can the team provide a story point estimate or T-shirt size?
- Is the team's confidence level above 60%?
- Are there known unknowns that would change the estimate significantly?

**How to fix:**
- Add more context to the What section.
- Conduct a time-boxed spike to reduce uncertainty.
- Split the item so the uncertain part becomes its own research item.

### Small

**Definition:** The item can be completed within one sprint.

**Why it matters:** Large items are harder to estimate, harder to test, and create integration risk. They also delay feedback.

**How to fix (splitting strategies):**
- **By outcome:** Split acceptance criteria into separate items.
- **By scope:** Deliver the happy path first, edge cases second.
- **By user segment:** Build for one segment first, extend to others later.
- **By operation:** Split CRUD operations into separate items.

### Testable

**Definition:** The acceptance criteria can be verified through observation or measurement.

**Why it matters:** Untestable items cannot be definitively completed, leading to ambiguity about done-ness and scope creep.

**How to check:**
- Can QA write test cases from the acceptance criteria alone?
- Is each criterion binary (pass/fail), not subjective?
- Are edge cases covered?

**How to fix:**
- Replace vague criteria ("it works") with specific outcomes ("the page loads in under 2 seconds").
- Add error state criteria ("if the payment fails, the user sees an error message with a retry option").
- Remove subjective criteria ("the UI is intuitive") or replace with measurable proxies ("new users complete the flow without help text in under 3 minutes").

## Backlog Refinement Best Practices

### Before Refinement

1. **Product owner prepares draft items** with Why and What filled in. Acceptance criteria can be rough.
2. **Share items 24 hours in advance** so the team can review and come with questions.
3. **Limit the agenda** to 5-8 items per session. Quality over quantity.

### During Refinement

1. **Start with the Why.** Before discussing What or How, ensure the team understands and agrees with the strategic context.
2. **Discuss, do not dictate.** The product owner presents the item; the team asks questions and proposes approaches.
3. **Write acceptance criteria together.** The team's input ensures criteria are realistic and testable.
4. **Apply INVEST.** Check each criterion before moving to the next item.
5. **Estimate after discussion.** Estimation is more accurate when the team has discussed the item.
6. **Timebox each item.** If an item takes more than 10 minutes, park it and schedule a deeper discussion.

### After Refinement

1. **Update items** with the discussed changes.
2. **Link design artifacts** if new designs were referenced.
3. **Flag items that need spikes** and schedule the spike for the current sprint.
4. **Communicate priority changes** to stakeholders if the order shifted.

## Definition of Ready Checklist

An item is ready for sprint planning when:

- [ ] **Why** is written and connects to a current team objective
- [ ] **What** is clear enough that the team recalls the discussion
- [ ] **Acceptance criteria** include 4+ observable outcomes
- [ ] **Design** is linked (if applicable) and reviewed by the team
- [ ] **INVEST criteria** are satisfied
- [ ] **Estimate** has been provided by the team
- [ ] **Dependencies** are resolved or explicitly managed
- [ ] **Questions** from refinement are answered

## When to Use WWAS vs Other Formats

| Signal | Recommended Format |
|--------|-------------------|
| Stakeholders ask "Why are we building this?" | WWAS -- the Why section directly answers this |
| Team builds features that do not move metrics | WWAS -- forces strategic connection |
| Designers need more context about user situations | Job Stories -- situation component drives design |
| Team is new to structured requirements | User Stories -- simplest format to learn |
| Backlog items are over-specified | WWAS -- the What is intentionally brief |
| Backlog items are under-specified | WWAS or Job Stories -- both require meaningful context |
| Mix of strategic and tactical items | WWAS for strategic, simple tasks for tactical |
