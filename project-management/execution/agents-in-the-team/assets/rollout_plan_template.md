# Agent Rollout Plan: <team name>

| Phase | Duration | Scope | Exit criteria to advance | Rollback trigger |
|-------|----------|-------|--------------------------|------------------|
| 0. Baseline | 2-4 weeks | No agents. Measure DORA five + review time with `agent_delivery_metrics.py` (all human) | Baseline recorded | - |
| 1. Pilot | 1-2 sprints | 1 team, agent-eligible tickets only (tests, docs, dependency patches), 2 named reviewers | Agent PR acceptance and post-merge rework within agreed gap of human baseline; no security finding | Any escaped defect with customer impact from an agent PR; any secret exposure |
| 2. Expand types | 2-3 sprints | Add low/medium-risk bugs and small features with good tests | Review capacity gate passing every sprint; change fail rate of deployments with agent changes within agreed gap | Change fail rate gap above tolerance two sprints running |
| 3. Expand teams | quarter | Second and third team adopt the policy | Each team has its own policy, reviewers and baseline | Team reports review overload in retro two sprints running |
| 4. Steady state | ongoing | Quarterly policy review against metrics | - | - |

## Decisions to record before Phase 1
- [ ] Which agent(s) and which trackers/repos they may access
- [ ] Agent identity and permission scopes (least privilege)
- [ ] Branch protection and required human approvals
- [ ] Hard-block list signed off by security
- [ ] Tolerance for the metrics gate (`--tolerance`) and who acts on a breach
- [ ] How agent-authored work is labelled for metrics and Sprint Review

## Communication
- Kickoff: why, what changes for reviewers, what does not change (accountability)
- Weekly during pilot: metrics snapshot + one learning
- Retro item every sprint: "What did the agents make harder?"
