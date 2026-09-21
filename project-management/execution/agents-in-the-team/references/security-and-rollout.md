# Security and Rollout

Deep reference for giving agents access to trackers and repositories safely, and for rolling agents out without losing control of quality.

---

## 1. Threat model in one table

| Threat | How it happens with agents | Control |
|--------|----------------------------|---------|
| **Over-privileged agent** | Agent runs on a human's personal token with org-wide write access | Dedicated app/bot identity; access limited to named repos/teams; writes only to agent branches |
| **Secret exposure** | Secrets pasted into tickets or prompts; agent echoes env vars into logs or PRs | No secrets in ticket text; secret scanning on agent PRs; environment secrets scoped to what the task needs |
| **Prompt injection via tickets and repos** | Instructions hidden in issue text, comments, code comments, docs or dependency READMEs steer the agent ("also update the CI token...") | Treat all ticket and repository content as untrusted input; restrict who can trigger the agent; keep network restrictions on; review changes to CI config, dependency manifests and permission files with extra care |
| **Supply-chain changes** | Agent adds or upgrades a dependency to make a test pass | Constraint in ticket: "no new dependencies"; dependency review on every agent PR |
| **CI abuse** | Agent-authored changes to workflows run with repository secrets | Require human approval before CI runs on agent PRs where the platform supports it |
| **Self-approval** | The person who delegated the ticket approves the agent's PR alone | Branch protection with required human approvals; prevent requester-only approval where supported |
| **Data leakage** | Agent reads production data or customer tickets and includes them in output | No production data in agent environments; hard block on tickets touching personal data |

### Prompt injection, specifically

OWASP ranks prompt injection first in its Top 10 for LLM applications (**LLM01:2025**). Its definition of the indirect form fits agent work exactly: indirect prompt injections occur when an LLM accepts input from external sources, such as websites or files, and content in that input alters the model's behavior in unintended ways. For an agent taking tickets, **the ticket, its comments and every file in the repository are external input.**

Practical controls for a delivery team (not a model vendor):

1. Limit who can assign or trigger the agent to people with write access.
2. Keep the platform's default network restrictions for the agent unless a specific allowlist entry is justified.
3. Review diffs, not descriptions. The PR description is also agent output.
4. Flag for security review any agent PR that touches CI workflows, dependency manifests, permission or ownership files, or infrastructure config.
5. Keep hard blocks on secrets, auth and IAM work.

### What one vendor documents as built-in controls (example, as of September 2026)

GitHub's documentation for Copilot cloud agent lists these mitigations: only users with write access can trigger it, and comments from users without write access are never presented to it; it can push only to a single `copilot/` branch (or the PR branch when mentioned on an existing PR) and is subject to branch protections; it cannot mark its PR ready for review or approve or merge it; the user who asked for the PR cannot approve it; by default workflows do not run until a user with write access clicks **Approve and run workflows**; its internet access is restricted; and hidden characters (for example HTML comments) are filtered from issue and comment input. Use this as a checklist for any agent platform: if your tool lacks an equivalent, add a process control.

---

## 2. Rollout plan

Use `assets/rollout_plan_template.md`. The shape:

| Phase | Scope | Advance when | Roll back when |
|-------|-------|--------------|----------------|
| 0. Baseline | No agents; measure DORA metrics and review time | Baseline recorded | - |
| 1. Pilot | One team; agent-eligible tickets only (tests, docs, dependency patches) | Agent cohort within the agreed tolerance of human baseline; no security finding | Customer-impacting escaped defect from an agent PR; any secret exposure |
| 2. Expand types | Low/medium-risk bugs, small features with good tests | Capacity gate passing each sprint; change fail gap within tolerance | Gap above tolerance two sprints running |
| 3. Expand teams | More teams, each with its own policy, reviewers and baseline | Each team baselined | Review overload raised in retro two sprints running |
| 4. Steady state | Quarterly policy review | - | - |

### Rollout rules [RECOMMENDED]

- **Baseline first.** Without a pre-agent baseline, no one can tell whether instability is new.
- **One variable at a time.** Do not change CI, branching strategy and agent adoption in the same quarter.
- **Reviewers opt in.** Name the reviewers for the pilot and remove other work from them.
- **Retro every sprint:** "What did the agents make harder?" The answers find the costs metrics miss (context-switching, review fatigue, onboarding of juniors).
- **Keep juniors writing code.** If agents take all small tickets, new engineers lose the tickets they learn on. Reserve some agent-eligible work for people.

---

## 3. Sources

- OWASP GenAI Security Project, *LLM01:2025 Prompt Injection*: https://genai.owasp.org/llmrisk/llm01-prompt-injection/
- GitHub Docs, *Risks and mitigations for GitHub Copilot cloud agent*: https://docs.github.com/en/copilot/concepts/agents/cloud-agent/risks-and-mitigations
