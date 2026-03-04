# User Story Template

**Story ID:** [PROJECT]-[NUMBER]
**Epic:** [EPIC_NAME]
**Sprint:** [SPRINT_NUMBER] (if assigned)
**Author:** [AUTHOR_NAME]
**Date Created:** [DATE]
**Last Updated:** [DATE]

---

## Story Format

### Option A: Classic User Story

> **As a** [type of user/role],
> **I want** [action or capability],
> **so that** [benefit or value].

### Option B: Job Story

> **When** [situation or trigger],
> **I want to** [motivation or action],
> **so I can** [expected outcome].

**Choose the format that best fits the context:**
- Use **User Story** when the role and persona are important to the requirement
- Use **Job Story** when the context and situation drive the need

---

## Story Details

### Description
[Provide 2-3 sentences of additional context. Explain the user's problem, the business need, or the technical background. This supplements the story statement above.]

### 3 C's Framework

| Component | Description |
|-----------|-------------|
| **Card** | The story statement above (concise, fits on a card) |
| **Conversation** | [Key questions to discuss with the team during refinement] |
| **Confirmation** | The acceptance criteria below (how we verify the story is done) |

---

## INVEST Criteria Checklist

Before this story is considered ready for sprint planning, verify it meets INVEST:

- [ ] **Independent** - Can be developed without depending on other stories in this sprint
- [ ] **Negotiable** - Implementation details are flexible; the team decides the "how"
- [ ] **Valuable** - Delivers clear value to the user or business
- [ ] **Estimable** - Team can estimate the effort with reasonable confidence
- [ ] **Small** - Can be completed within a single sprint
- [ ] **Testable** - Has clear, verifiable acceptance criteria

---

## Acceptance Criteria

Write acceptance criteria using the Given/When/Then format:

### Criterion 1: [SHORT_DESCRIPTION]
```
Given [precondition or initial context]
When  [action performed by the user or system]
Then  [expected result or observable outcome]
```

### Criterion 2: [SHORT_DESCRIPTION]
```
Given [precondition or initial context]
When  [action performed by the user or system]
Then  [expected result or observable outcome]
```

### Criterion 3: [SHORT_DESCRIPTION]
```
Given [precondition or initial context]
When  [action performed by the user or system]
Then  [expected result or observable outcome]
```

### Edge Cases / Negative Scenarios
```
Given [unusual or error condition]
When  [user attempts the action]
Then  [system handles gracefully with appropriate feedback]
```

---

## Definition of Ready Checklist

This story is ready for sprint planning when ALL items are checked:

- [ ] Story statement is complete (User Story or Job Story format)
- [ ] Acceptance criteria are written and reviewed by the Product Owner
- [ ] Story points are assigned by the team
- [ ] Dependencies are identified and documented below
- [ ] UX designs or wireframes are attached (if applicable)
- [ ] Technical approach is understood by at least 2 team members
- [ ] No open questions remain (or questions are documented with owners)
- [ ] Story fits within a single sprint at estimated size

---

## Story Metadata

### Sizing
- **Story Points:** [POINTS]
- **T-Shirt Size:** [XS / S / M / L / XL]
- **Estimated Hours:** [HOURS] (optional, for capacity planning)

### Classification
- **Type:** [Feature / Bug Fix / Technical Debt / Spike / Improvement]
- **Priority:** [Critical / High / Medium / Low]
- **Risk Level:** [High / Medium / Low]

### Dependencies
| Dependency | Type | Status | Owner | Notes |
|------------|------|--------|-------|-------|
| [DEP_1] | [Internal/External/Cross-team] | [Resolved/Pending/Blocked] | [OWNER] | [NOTES] |
| [DEP_2] | [Internal/External/Cross-team] | [Resolved/Pending/Blocked] | [OWNER] | [NOTES] |

### Related Items
- **Parent Epic:** [EPIC_ID] - [EPIC_NAME]
- **Blocked By:** [STORY_ID] (if any)
- **Blocks:** [STORY_ID] (if any)
- **Related Stories:** [STORY_ID_1], [STORY_ID_2]

---

## Story Splitting Strategies

If this story is too large (>8 points or won't fit in a sprint), consider these splitting techniques:

### 1. Split by Workflow Steps
Break a multi-step process into individual steps:
- Story A: User can initiate the process
- Story B: User can complete step 2
- Story C: User receives confirmation

### 2. Split by Business Rules
Separate simple and complex rules:
- Story A: Basic validation (required fields)
- Story B: Advanced validation (cross-field rules)
- Story C: Edge case handling

### 3. Split by Data Variations
Handle different data types or inputs separately:
- Story A: Support text input
- Story B: Support file upload
- Story C: Support bulk import

### 4. Split by Operations (CRUD)
Separate create, read, update, delete:
- Story A: User can create a record
- Story B: User can view records
- Story C: User can edit a record
- Story D: User can delete a record

### 5. Split by Interface
Separate platforms or interaction modes:
- Story A: Web interface
- Story B: Mobile interface
- Story C: API endpoint

### 6. Split by Performance
Deliver functionality first, optimize second:
- Story A: Feature works (basic implementation)
- Story B: Feature performs at scale (optimization)

### 7. Spike + Implementation
Separate research from execution:
- Spike: Investigate approach for [complex area] (timeboxed)
- Story: Implement [feature] based on spike findings

---

## Example Stories

### Example 1: Small Story (1-2 points)
> **As a** registered user,
> **I want** to update my display name in account settings,
> **so that** my name appears correctly across the application.

**Acceptance Criteria:**
```
Given I am logged in and on the Account Settings page
When  I enter a new display name and click Save
Then  my display name is updated and a success message is shown

Given I enter a display name longer than 50 characters
When  I click Save
Then  the system shows a validation error and does not save
```

**Points:** 2 | **Type:** Feature | **Risk:** Low

---

### Example 2: Medium Story (3-5 points)
> **When** I receive a weekly project status email,
> **I want to** see a summary of sprint progress and blockers,
> **so I can** quickly assess project health without opening multiple tools.

**Acceptance Criteria:**
```
Given it is Monday at 9:00 AM
When  the automated email is triggered
Then  all project stakeholders receive an email with velocity, burndown, and active blockers

Given there are no active blockers
When  the email is generated
Then  the blockers section shows "No active blockers" instead of being empty
```

**Points:** 5 | **Type:** Feature | **Risk:** Medium

---

### Example 3: Large Story (8 points - consider splitting)
> **As a** team administrator,
> **I want** to configure custom workflow states and transitions,
> **so that** the tool matches our team's actual development process.

**Acceptance Criteria:**
```
Given I am on the Workflow Configuration page
When  I add a new state and define transitions
Then  the workflow is updated and visible to all team members

Given a workflow state has active items
When  I attempt to delete that state
Then  the system prevents deletion and shows affected items
```

**Points:** 8 | **Type:** Feature | **Risk:** High
**Note:** Consider splitting into: (A) Add/remove states, (B) Define transitions, (C) Validation and error handling

---

## Notes & Discussion Log

| Date | Participant | Note |
|------|------------|------|
| [DATE] | [NAME] | [Discussion point, decision, or open question] |
| [DATE] | [NAME] | [Discussion point, decision, or open question] |

---

*Template maintained by the Scrum Master. Use this template for all new user stories to ensure consistency and readiness for sprint planning.*
