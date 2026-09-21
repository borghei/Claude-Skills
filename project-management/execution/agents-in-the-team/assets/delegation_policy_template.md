# Agent Delegation Policy: <team name>

**Version:** <1.0>  **Owner:** <engineering manager>  **Approved by:** <eng lead, security>  **Review date:** <quarterly>

## 1. Principle
Humans remain accountable for decisions and results. An agent may be delegated a ticket; the accountable human stays the owner, and every agent change is reviewed with the same rigor as a teammate's.

## 2. Eligibility bands
| Band | Score (`agent_delegation_scorer.py`) | Who does the work | Review |
|------|--------------------------------------|-------------------|--------|
| Agent-eligible | 75-100, no hard block | Agent drafts the PR | Named human reviewer |
| Agent-assisted | 50-74 | Human leads; agent drafts parts (tests, boilerplate, docs) | Normal review |
| Human-only | < 50, or any hard block | Human | Normal review |

## 3. Hard blocks (never agent-led)
- Touches: authentication/authorization, payments, secrets/keys, personal data, IAM/permissions, production data migrations, cryptography
- Types: incident response, architecture decisions
- <team-specific additions>

## 4. Ticket standard
Agent-eligible tickets use the agent-ready ticket template: 2+ checkable acceptance criteria, context links, constraints (do-not-touch), and named owner and reviewer.

## 5. Review rules
- The agent never approves or merges. Branch protection requires <n> human approval(s).
- The person who delegated the ticket is not the sole approver where the tool supports that rule.
- CI workflows on agent PRs require human approval to run: <yes/no, per tool settings>.

## 6. Capacity rule
Planned agent review hours (incl. rework allowance of <x>%) must fit within <80>% of reviewer hours for the sprint. `agent_delegation_scorer.py` exits 2 when it does not; the plan is cut, not the review.

## 7. Access and security
- Agent identity: dedicated app/bot identity, not a human's personal token
- Repository access: <repos listed>, write only to agent branches
- Secrets: none in tickets or prompts; environment secrets scoped to <...>
- Network: <tool's default restriction kept / allowlist>
- Untrusted input: issue text, comments and repo content are treated as untrusted; changes to CI config, dependency manifests and permission files always get security review

## 8. Transparency
Agent-authored PRs and tickets are labelled; Sprint Review shows what was built and how it was built with agents.

## 9. Metrics and review cadence
Monthly: `agent_delivery_metrics.py` split by author type. Quarterly: revisit bands and hard blocks against the data.
