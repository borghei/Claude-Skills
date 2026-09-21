# Agent-Ready Ticket Template

<!-- Use for any ticket that may be assigned or delegated to an AI coding/ops agent.
     An agent reads only what is in the ticket and what it can reach in the repo.
     Anything you would explain to a new teammate in a hallway must be written here. -->

**Title:** <verb + object + where, e.g. "Fix off-by-one in invoice list pagination (api/invoices)">

**Accountable human (owner):** <name - stays the assignee/owner even when an agent is delegated>
**Reviewer:** <name - not the person who delegated, where your review rules allow>
**Delegation band:** <agent-eligible | agent-assisted> (from `agent_delegation_scorer.py`)

## Goal
<One or two sentences: the user-visible or system-visible outcome, and why it matters.>

## Acceptance criteria (checkable)
- [ ] Given <state>, when <action>, then <observable result>
- [ ] <Test that must exist or pass, named>
- [ ] <Non-functional bar: performance, accessibility, logging>

## Context
- **Files / modules to start from:** <paths>
- **Patterns to follow:** <link to an existing example in the codebase>
- **Reproduction (bugs):** <steps, input, expected vs actual>
- **Related tickets / decisions:** <links>

## Constraints
- **Do not touch:** <paths, public interfaces, schemas, config>
- **Allowed dependencies:** <none new | list>
- **Scope limit:** <e.g. "one PR, under ~300 changed lines; split otherwise">

## Definition of done
- [ ] PR opened as draft, linked to this ticket, description explains what changed and why
- [ ] All CI checks green; new tests included
- [ ] Human review by the named reviewer; the agent does not approve or merge
- [ ] Ticket labelled `agent-authored` for metrics

<!-- Never paste secrets, tokens, customer data or internal credentials into a ticket.
     Ticket text is input to the agent: treat it as code. -->
