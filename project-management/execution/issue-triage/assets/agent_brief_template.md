# Agent Brief Template

Post this as a comment on the issue or pull request at the moment it moves to
`state:ready-for-agent` or `state:ready-for-human`. The brief is the contract;
the original report and thread are background. Lint it before posting:

```bash
python3 project-management/execution/issue-triage/scripts/agent_brief_linter.py --input brief.md
```

Rules of thumb while filling it in:

- Describe behaviour and contracts, never file paths or line numbers. The
  issue may wait weeks; code moves, behaviour does not.
- Each acceptance criterion is one observable check that passes or fails on
  its own. No "works", "correctly", "properly", "fast".
- Out of scope is mandatory. It is the fence that stops gold-plating.
- When the item is a pull request, use "Current behavior" for what the branch
  already does, and scope the brief to the remaining work on that branch.

---

## Agent Brief

**ID:** <#issue or PR number>
**Target state:** ready-for-agent | ready-for-human
**Category:** bug | enhancement | chore | docs
**Summary:** <one line, under 120 characters, naming the observable change>

**Current behavior:**
<What happens today. For a bug: the broken behaviour plus the trigger that
reproduces it. For an enhancement: the status quo the change builds on. For a
PR: what the diff already does and which gaps remain.>

**Desired behavior:**
<What is true when the work is done, including edge cases and error paths.
State outcomes, not steps.>

**Key interfaces:**
- `<TypeOrFunction>` — <what changes in its contract, or "unchanged">
- <Config key, CLI flag, API field, event name the agent should look for>

**Acceptance criteria:**
- [ ] <Single observable check 1>
- [ ] <Single observable check 2 — usually an edge case or error path>
- [ ] <Regression guard: what must stay exactly as it is>

**Out of scope:**
- <Adjacent change the agent must not make>
- <Tempting refactor that belongs in another issue>

**Why not delegated:** <ready-for-human only — the judgment call, access,
manual test, or contract approval that keeps this with a person>

**Verification:** `<exact command or check that proves the criteria>`
