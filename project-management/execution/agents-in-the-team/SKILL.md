---
name: agents-in-the-team
description: >
  Run delivery when AI coding and ops agents take tickets. Use when setting
  agent delegation policy, writing agent-ready tickets, planning review
  capacity, measuring agent vs human delivery, or rolling agents out safely.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: project-management
  domain: pm-execution
  updated: 2026-09-21
  python-tools: agent_delegation_scorer.py, agent_delivery_metrics.py
  tech-stack: ai-agents, delivery-management, dora-metrics, code-review, scrum
---

# Agents in the Team

AI coding and ops agents now take tickets directly from issue trackers: Linear delegates issues to agents, Jira work items can be handed to Rovo and partner agents, and GitHub issues can be assigned to Copilot. The agent opens a pull request; a human still has to decide whether it is right. That moves the bottleneck from writing code to **reviewing** it, and it moves the delivery manager's job from assigning people to deciding **which work an agent may take, how it must be specified, who is accountable, and how to see quality slipping early**.

The agent treats this as a delivery system, not a tooling choice: a delegation policy with hard blocks, agent-ready tickets, named human accountability, a review-capacity gate, metrics split by author type, security controls, and a phased rollout. Two stdlib tools do the arithmetic.

## When to use

- Deciding which backlog items an agent may take, and writing that down as policy
- Rewriting tickets so an agent can execute them without guessing
- Sprint planning with agents: will reviewers keep up?
- Monthly review: are agent PRs holding quality vs human PRs, and vs the DORA metrics?
- Designing access, secrets and prompt-injection controls for agents on trackers and repos
- Rolling agents out from pilot to multiple teams

**When NOT to use:** choosing or evaluating an AI coding tool itself (vendor evaluation); building an agent (engineering agent-design skills); individual developers using an AI assistant in their editor with no ticket delegation (normal code review applies).

## Clarify First

Before producing a policy or plan, confirm these inputs. If any is unknown or vague, ASK - do not assume:

- [ ] **Which agents and trackers** - which agent(s), on which tracker and repos, with what identity (drives access controls and which vendor safeguards exist)
- [ ] **Reviewer capacity** - named reviewers and realistic review hours per sprint (drives the capacity gate)
- [ ] **Risk areas** - what the team owns that is sensitive: auth, payments, personal data, infra (drives hard blocks)
- [ ] **Baseline** - do you have pre-agent delivery metrics? (without one, instability cannot be attributed)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Quick Start

```bash
# Sprint planning: score tickets, check review capacity (exit 2 = over capacity or policy breach)
python3 project-management/execution/agents-in-the-team/scripts/agent_delegation_scorer.py \
  --input backlog.json

# Monthly: delivery metrics split human vs agent, DORA split, optional regression gate
python3 project-management/execution/agents-in-the-team/scripts/agent_delivery_metrics.py \
  --input records.json --gate --tolerance 0.05
```

## Tools Overview

| Tool | Input | Output | Gate (exit 2) |
|------|-------|--------|---------------|
| `scripts/agent_delegation_scorer.py` | Backlog JSON: tickets (type, risk, blast radius, test coverage, acceptance criteria, context, constraints, touches, points, planned assignee) + team reviewers and review model | Per-ticket 0-100 score, band (agent-eligible / agent-assisted / human-only) with reasons, review hours; review load vs budget | Planned agent review hours exceed `reviewer hours x max utilization`, or a ticket planned for an agent is human-only / hard-blocked |
| `scripts/agent_delivery_metrics.py` | PRs (author type, state, timestamps, changes requested, review minutes, `fix_of`, reverted), deployments (PRs, failed, recovered, unplanned), production defects | By author: acceptance, review rework, post-merge rework, time to first review, open-to-merge, reviewer minutes, escaped defects; DORA change fail rate, deployment rework rate, failed deployment recovery time split by deployments with vs without agent changes | With `--gate`: agent cohort exceeds human cohort by more than `--tolerance` on post-merge rework, change fail rate or escaped defects |

Both support `--format markdown` (default) or `--format json` (wrapped as `{"schema", "generated_at", "data"}` per `SHARED_OUTPUT_SCHEMA.md`) and `--output <file>`.

### Exit code contract [PROVEN]

| Code | Meaning | Who fixes it |
|------|---------|--------------|
| 0 | Pass | Nobody |
| 1 | Tool error: bad path, invalid JSON, invalid enum or timestamp | Whoever produced the input |
| 2 | Gate failed: over review capacity / policy breach (scorer), agent regression beyond tolerance (metrics, `--gate` only) | Delivery lead: cut or re-plan agent work, narrow the bands |

## Workflow

### Step 1 - Set the delegation policy [RECOMMENDED]

Score every candidate ticket on five factors (clarity, context, risk, blast radius, verifiability) plus type fit:

| Band | Score | Who does the work |
|------|-------|-------------------|
| **Agent-eligible** | 75-100, no hard block | Agent drafts the PR; named human reviews and merges |
| **Agent-assisted** | 50-74 | Human leads; agent drafts parts - or rewrite the ticket until it scores 75+ |
| **Human-only** | < 50 or any hard block | Human |

**Hard blocks** (score irrelevant): auth, payments, secrets, personal data, IAM, production data migrations, crypto, incident response, architecture decisions. Relax one only deliberately, with security sign-off, once your own metrics justify it. Write the policy with [assets/delegation_policy_template.md](assets/delegation_policy_template.md). Factor weights and calibration: [references/delegation-and-accountability.md](references/delegation-and-accountability.md).

### Step 2 - Write agent-ready tickets

Use [assets/agent_ticket_template.md](assets/agent_ticket_template.md). An agent reads only the ticket and what it can reach:

1. Outcome in one or two sentences, then **2+ checkable acceptance criteria**
2. **Context**: paths to start from, a link to an existing example of the pattern
3. **Constraints**: what not to touch, no new dependencies, scope ceiling (one PR, small diff)
4. **Named accountable owner and reviewer**
5. **No secrets, tokens or customer data** - ticket text is input to the agent; treat it like code
6. Bugs: a reproduction (steps, input, expected vs actual)

### Step 3 - Keep humans accountable [PROVEN]

The Scrum Guide Expansion Pack's "AI and Scrum" expansion (v2026.1) states that "humans remain accountable for decisions and results", that "AI may recommend, but humans decide", and that "every piece of AI-generated code must be reviewed with the same rigor as if a teammate wrote it"; it asks teams to strengthen, not relax, the Definition of Output Done and to flag AI-generated work items. Trackers model the same idea: Linear's docs say assigning an issue to an agent delegates it "while the human teammate remains the primary assignee and owner".

Team rules: every agent ticket has a named human owner; agent PRs use the same branch protection and review as human PRs; the agent never approves or merges; where supported, the delegating person is not the only approver; agent work is labelled and shown at Sprint Review. Tracker-by-tracker detail (as of September 2026): [references/delegation-and-accountability.md](references/delegation-and-accountability.md).

### Step 4 - Plan review capacity

Review hours are the constraint. Before committing the sprint, run `agent_delegation_scorer.py`. It estimates review hours per planned agent ticket (points, risk multiplier, rework allowance) and compares the total with `reviewer hours x max utilization`. The defaults (0.5 h base, 0.5 h/point, 30% rework allowance, 80% utilization) are **planning assumptions**; replace them with your measured review rework rate and reviewer minutes per PR after two sprints. When the gate fails, **cut the plan, not the review**. Formula and tuning: [references/metrics-and-capacity.md](references/metrics-and-capacity.md).

### Step 5 - Measure by author type

Run `agent_delivery_metrics.py` monthly (or per sprint). DORA's 2025 report found AI adoption positively related to throughput and product performance but still negatively related to software delivery stability, and describes AI as an amplifier of existing strengths and weaknesses. So watch stability first:

- **DORA instability and recovery** (dora.dev definitions): change fail rate, deployment rework rate, failed deployment recovery time - split by deployments with vs without agent changes
- **Agent-specific**: PR acceptance rate, review rework rate, post-merge rework rate, time to first review, reviewer minutes per PR, escaped defects per 10 merged PRs

Cohorts under 10 merged PRs are flagged as directional. Set the `--tolerance` in the rollout plan; a breach narrows the bands. Do not measure lines of code, PR counts or agent "utilization" as productivity.

### Step 6 - Secure the setup [RECOMMENDED]

Least privilege (dedicated agent identity, named repos, agent-only branches); no secrets in tickets; secret scanning on agent PRs; human approval before CI runs on agent PRs where supported; network restrictions kept on. Treat tickets, comments and repository content as **untrusted input** - OWASP ranks prompt injection first (LLM01:2025) and its indirect form covers instructions hidden in external content the model reads, such as tickets and files. Extra review for agent PRs touching CI config, dependency manifests or permission files. Threat table and a vendor-control checklist: [references/security-and-rollout.md](references/security-and-rollout.md).

### Step 7 - Roll out in phases

Baseline (no agents) -> pilot (one team, agent-eligible only) -> expand ticket types -> expand teams -> quarterly policy review, each with explicit advance and rollback criteria. Template: [assets/rollout_plan_template.md](assets/rollout_plan_template.md).

## Worked Example

[examples/payments-platform-sprint.md](examples/payments-platform-sprint.md) - a payments team plans Sprint 42 with agents, fails the capacity gate, re-plans, and reviews a month of metrics. Sample runs (all data fictional):

| Command | Exit | Why |
|---------|------|-----|
| `agent_delegation_scorer.py --input assets/backlog_sample.json` | 2 | 7 tickets planned for the agent need 30.88 review hours vs a 12.8-hour budget; PAY-105 touches payments and secrets (hard block) |
| `agent_delegation_scorer.py --input assets/backlog_within_capacity.json` | 0 | Re-planned: 4 agent-eligible tickets, 10.4 review hours |
| `agent_delivery_metrics.py --input assets/delivery_records_sample.json` | 0 | Report only; findings listed |
| `agent_delivery_metrics.py --input assets/delivery_records_sample.json --gate` | 2 | Agent post-merge rework, change fail rate and escaped defects exceed human cohort by more than 0.05 |

## Scoring rubric - agent delivery maturity

Score each 0-2; 10+ of 14 is ready to expand beyond a pilot.

| Dimension | 2 looks like |
|-----------|--------------|
| Policy | Written bands and hard blocks, signed off by eng lead and security |
| Tickets | Agent tickets meet the template; scorer shows most planned agent work at 75+ |
| Accountability | Named human owner and reviewer on every agent ticket; agent never approves or merges |
| Capacity | Capacity gate passes every sprint without cutting review depth |
| Metrics | Baseline exists; monthly human/agent split; tolerance agreed |
| Security | Dedicated identity, least privilege, secret scanning, CI approval, injection-aware review |
| Transparency | Agent work labelled; Sprint Review shows how work was built |

## Anti-Patterns

### The Review Flood
**Mistake:** Assigning every eligible ticket to agents at sprint start, then discovering reviewers cannot keep up; PRs age, get rubber-stamped, or merge late in a batch.
**Why it happens:** Agents make starting work nearly free, so the plan is sized by agent throughput instead of review throughput.
**Instead:** Size agent work by reviewer hours. Run the capacity gate before committing; cut the plan, not the review.

### The Unowned Ticket
**Mistake:** The agent is the only assignee; when its PR causes an incident, nobody owned the decision.
**Why it happens:** Tracker UIs make an agent look like a teammate.
**Instead:** Every agent ticket names an accountable human owner and reviewer. Humans remain accountable for decisions and results.

### The Hallway Ticket
**Mistake:** Delegating a ticket written for a teammate who would ask questions ("Improve checkout").
**Why it happens:** Ticket-writing habits formed with humans who fill gaps from context.
**Instead:** Use the agent-ready template: 2+ checkable criteria, context links, constraints, reproduction for bugs. If it scores under 75, it is not agent work yet.

### Measuring Output Instead of Stability
**Mistake:** Celebrating more PRs and more lines merged after adding agents.
**Why it happens:** Output is easy to count and rises immediately.
**Instead:** Track change fail rate, deployment rework rate, post-merge rework and escaped defects by author type, against a pre-agent baseline.

### Trusting the Ticket Text
**Mistake:** Letting anyone who can comment on an issue steer the agent, and reviewing the PR description instead of the diff.
**Why it happens:** Issue text feels like internal documentation, not input to a program.
**Instead:** Treat tickets, comments and repo content as untrusted; restrict who can trigger agents; review diffs; security-review changes to CI, dependencies and permissions.

## Reference Documentation

- [references/delegation-and-accountability.md](references/delegation-and-accountability.md) - scoring factors and calibration, hard blocks, ticket-writing rules with before/after, Scrum Guide Expansion Pack AI guidance, how Linear, Jira and GitHub model agent delegation (as of September 2026)
- [references/metrics-and-capacity.md](references/metrics-and-capacity.md) - DORA 2025 AI findings, DORA AI Capabilities Model mapping, the five DORA metrics, agent-specific metric definitions, the capacity formula and tuning
- [references/security-and-rollout.md](references/security-and-rollout.md) - threat table, prompt injection controls, vendor control checklist, phased rollout rules
- `assets/agent_ticket_template.md`, `assets/delegation_policy_template.md`, `assets/rollout_plan_template.md`
- `assets/backlog_sample.json` (gate fail), `assets/backlog_within_capacity.json` (pass), `assets/delivery_records_sample.json`

## Related skills

Self-contained; these cover adjacent ground:

- `project-management/execution/sprint-plan/` - capacity math for the human side of the sprint
- `project-management/execution/backlog-refinement/` - INVEST and Definition of Ready, the base agent tickets build on
- `project-management/execution/cycle-time-analyzer/` - flow metrics for the whole system
- `project-management/scrum-master/` - ceremonies and team health, including Sprint Review transparency
- `project-management/execution/post-mortem/` - blameless review when an agent change causes an incident

## Sources

- Scrum Guide Expansion Pack, *AI and Scrum* (v2026.1) - https://scrumexpansion.org/ai-and-scrum/
- DORA, *DORA's software delivery performance metrics* - https://dora.dev/guides/dora-metrics/
- DORA, *State of AI-assisted Software Development 2025* - https://dora.dev/dora-report-2025/
- Google Cloud Blog, *Announcing the 2025 DORA Report* - https://cloud.google.com/blog/products/ai-machine-learning/announcing-the-2025-dora-report
- Google Cloud Blog, *Putting the DORA AI Capabilities Model to work* - https://cloud.google.com/blog/products/ai-machine-learning/from-adoption-to-impact-putting-the-dora-ai-capabilities-model-to-work
- Linear Docs, *Agents in Linear* - https://linear.app/docs/agents-in-linear
- Atlassian Support, *Collaborate on work items with AI agents* - https://support.atlassian.com/jira-software-cloud/docs/collaborate-on-work-items-with-ai-agents/
- GitHub Docs, *About GitHub Copilot cloud agent* - https://docs.github.com/en/copilot/concepts/agents/coding-agent/about-coding-agent
- GitHub Docs, *Risks and mitigations for GitHub Copilot cloud agent* - https://docs.github.com/en/copilot/concepts/agents/cloud-agent/risks-and-mitigations
- OWASP GenAI Security Project, *LLM01:2025 Prompt Injection* - https://genai.owasp.org/llmrisk/llm01-prompt-injection/
