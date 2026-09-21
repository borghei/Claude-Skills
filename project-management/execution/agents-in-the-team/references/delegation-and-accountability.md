# Delegation, Ticket-Writing and Accountability

Deep reference for deciding **which work an AI agent may take**, **how to write tickets agents can execute**, and **who stays accountable**. Tool facts are dated: they reflect vendor documentation as of September 2026 and change often. Re-check the linked pages before relying on a specific capability.

---

## 1. Delegation policy: the five factors

`agent_delegation_scorer.py` scores each ticket 0-100. The weights encode one idea: **an agent should take work whose correctness a reviewer can check cheaply and whose failure is contained.**

| Factor | Points | Why it matters for agents |
|--------|--------|---------------------------|
| **Clarity**: 2+ checkable acceptance criteria | 0 / 10 / 20 | Agents do not ask clarifying questions in a hallway. Ambiguity turns into plausible-looking wrong work. |
| **Context**: links to files/patterns + explicit constraints | 0 / 5 / 10 | An agent works from what it can reach. "Follow the pattern in X, do not touch Y" prevents scope creep. |
| **Risk**: low / medium / high | 25 / 12 / 0 | Business and user consequence if the change is wrong. |
| **Blast radius**: isolated / module / service / cross-system or customer-data | 20 / 15 / 8 / 0 | How far a defect propagates before anyone sees it. |
| **Verifiability**: automated test coverage good / partial / none | 15 / 8 / 0 | Tests are the cheapest reviewer. No tests means the human reviewer must re-derive correctness. |
| **Type fit** | 0-10 | Tests, docs and dependency patches fit well; incidents and architecture do not. |

### Bands [RECOMMENDED]

- **75-100 agent-eligible:** the agent drafts the PR; a named human reviews and merges.
- **50-74 agent-assisted:** a human leads. The agent drafts parts (tests, boilerplate, docs, a first pass), or the ticket is rewritten until it scores 75+.
- **< 50 human-only.**

### Hard blocks (score irrelevant) [RECOMMENDED]

Authentication/authorization, payments, secrets/keys, personal data, IAM/permissions, production data migrations, cryptography, incident response, architecture decisions. These are the areas where a subtle error is expensive and hard to spot in review, or where the work is judgement rather than execution. Teams can relax a block deliberately (with security sign-off) once their own metrics justify it, not before.

### Calibrating the weights

The weights are a starting policy, not a law. After two or three sprints, compare `agent_delivery_metrics.py` output by ticket type and band. If agent-eligible bugs show high post-merge rework, lower `TYPE_FIT["bug"]` or require `test_coverage: good` for bugs. Keep the policy file and the script constants in sync.

---

## 2. Writing tickets agents can execute

Use `assets/agent_ticket_template.md`. The rules that matter most:

1. **Outcome first, then criteria.** One or two sentences of goal, then checkable acceptance criteria (Given/When/Then, named tests, numeric bars).
2. **Point at code, not concepts.** Paths to start from, a link to an existing example of the pattern to follow.
3. **Say what not to touch.** Public interfaces, schemas, config, unrelated files. Agents over-reach when a fix "looks related".
4. **Bound the size.** One PR, a rough changed-lines ceiling; split larger work. Large generated diffs are hard to review, and small batches are one of the DORA AI capabilities (see metrics reference).
5. **Name the humans.** Accountable owner and reviewer on every agent ticket.
6. **No secrets, tokens, customer data or internal credentials** in ticket text. Ticket text is input to the agent: treat it like code.
7. **Bugs need a reproduction.** Steps, input, expected vs actual. Without it the agent guesses the bug.

### Before / after

| Before (scores ~25) | After (scores ~80) |
|---------------------|--------------------|
| "Improve checkout" | "Show inline validation error for expired card on checkout payment step (web/checkout/PaymentForm)" |
| No criteria | "Given an expired card, when the user leaves the expiry field, then the message 'Card expired' appears below the field within 200 ms"; "Unit test `test_expired_card_message` added" |
| No context | "Follow the pattern in `AddressForm` inline errors; strings in `i18n/en.json`" |
| No constraints | "Do not change the payment API call or the submit button logic" |

---

## 3. Human accountability and review ownership

### What the Scrum Guide Expansion Pack says

The Scrum Guide Expansion Pack (scrumexpansion.org) includes an **"AI and Scrum"** expansion (v2026.1, updated January 18, 2026). Its position, in its own words:

- Teams "should make it clear that AI is a tool and that humans remain accountable for decisions and results."
- "Scrum Teams must consciously keep a human-in-the-loop attitude: AI may recommend, but humans decide."
- "Every piece of AI-generated code must be reviewed with the same rigor as if a teammate wrote it."
- Successful AI integration "depends on strengthening—not relaxing—the Definition of Output Done", so that every AI-assisted change "meets the same quality bar as any human-written work: integrated, tested, reviewed, and demonstrably safe to release."
- Transparency: "clearly flagging AI-generated work items, sharing the rationale behind AI-driven decisions, and exposing any assumptions the AI made"; the Sprint Review "might be expanded" to show how the increment was built with AI.

Note the Expansion Pack's vocabulary: it uses "Product Developers" and "Definition of Output Done". The 2020 Scrum Guide itself does not address AI.

### Translating that into team rules [RECOMMENDED]

| Principle | Team rule |
|-----------|-----------|
| Humans remain accountable | Every agent ticket names an accountable human owner. The agent is never the owner of record. |
| Same review rigor | Agent PRs go through the same branch protection and review as human PRs. No "light review" lane. |
| Strengthen the Definition of Done | Add to DoD: tests for new behavior, no new dependencies without approval, PR description explains *why*. |
| Transparency | Label agent-authored tickets and PRs; show agent-built work explicitly at Sprint Review; track metrics by author type. |
| Humans decide | The agent drafts; a human approves and merges. Where the tool supports it, the person who delegated is not the only approver. |

### How the major trackers model this (as of September 2026)

| Tracker | How work reaches an agent | Accountability model in the vendor docs |
|---------|---------------------------|------------------------------------------|
| **Linear** | Workspace admins install agents as app users and choose which teams they can access; issues are assigned/delegated to an agent, or the agent is @mentioned | "Agents are not traditional assignees. Assigning an issue to an agent delegates the issue to that agent while the human teammate remains the primary assignee and owner." |
| **Jira (with Rovo)** | Rovo agents and third-party agents (the docs list GitHub Copilot coding agent as a partner agent) can be added via the Agents button on a work item, @mention in a comment, a workflow transition, or a board column; uses Rovo credits | The agent's output lands in the work item's Agents section; "Only you can view, interact with, and share the agent's output" until the user shares it to the work item |
| **GitHub** | Assign an issue to Copilot (Copilot cloud agent), which works in an ephemeral GitHub Actions-powered environment and opens a pull request; available on paid Copilot plans, enabled by an admin on Business/Enterprise | Draft PRs "must be reviewed and merged by a human"; the agent "cannot approve or merge a pull request"; the user who asked for the PR is prevented from approving it |

Other trackers and agents exist and change monthly. The policy in this skill is tool-agnostic: whatever the tracker, keep a named human owner, route agent work through normal review, and label it for metrics.

---

## 4. Sources

- Scrum Guide Expansion Pack, *AI and Scrum* (v2026.1): https://scrumexpansion.org/ai-and-scrum/
- Linear Docs, *Agents in Linear*: https://linear.app/docs/agents-in-linear
- Atlassian Support, *Collaborate on work items with AI agents* (Jira Cloud): https://support.atlassian.com/jira-software-cloud/docs/collaborate-on-work-items-with-ai-agents/
- GitHub Docs, *About GitHub Copilot cloud agent*: https://docs.github.com/en/copilot/concepts/agents/coding-agent/about-coding-agent
- GitHub Docs, *Risks and mitigations for GitHub Copilot cloud agent*: https://docs.github.com/en/copilot/concepts/agents/cloud-agent/risks-and-mitigations
