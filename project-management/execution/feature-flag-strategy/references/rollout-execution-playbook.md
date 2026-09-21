# Rollout Execution Playbook

Read this when planning the operational detail of a flagged rollout: choosing a flag type, picking a ramp shape, defining the kill-switch, designing holdouts, naming the flag, governing dependencies/approvals, and running the end-to-end workflow with troubleshooting and success criteria.

## Flag taxonomy (Fowler)

Martin Fowler's taxonomy classifies flags by **purpose** because lifespan and ownership differ dramatically.

| Flag type | Purpose | Lifespan | Ownership | Examples |
|---|---|---|---|---|
| **Release toggle** | Deploy code before release; decouple ship from launch | Days to weeks; **must retire after launch** | Owning team (Eng + PM) | "new_checkout_flow_v2", "search_relevance_v3" |
| **Experiment toggle** | A/B test variants; decide based on stat-sig | Days to weeks; **must retire when experiment concludes** | Owning team + analytics | "checkout_button_color_test", "onboarding_v2_experiment" |
| **Ops toggle** | Operational control: throttle, circuit-break, degrade-mode | Permanent or long-lived | Infra / SRE | "search_circuit_breaker", "rate_limit_premium_tier" |
| **Permission toggle** | Gate features by user, plan, role, tenant | Permanent (lives with the product) | Product + Eng | "enterprise_admin_panel", "beta_program_access" |

The error mode is treating a release toggle as a permission toggle ("we never turned it off, so it's now permanent"). The result is **flag debt**: thousands of dead branches in code, conflicting flag combinations, mystery behaviors.

**Rule:** every release toggle and experiment toggle has a *retirement date* set at creation. Operationally, a flag without a retirement date is treated as a defect.

## Rollout shapes

The shape of a ramp tells the team how much risk they are absorbing per step.

### Shape A: Linear ramp

```
0% -> 1% -> 5% -> 10% -> 25% -> 50% -> 100%
```

The default. Each step held for 1-3 days while metrics settle. Use for new features without strong segment hypotheses.

### Shape B: Segmented (audience-first)

```
Internal employees -> Friends-and-family -> Beta opt-in -> Free tier -> Paid tier -> All
```

Use when you have explicit risk gradients across segments -- enterprise customers wait until pro customers have validated; consumer flagship waits for ToS-aware beta opt-in.

### Shape C: Geographic / regulatory-aware

```
Single low-risk region -> Region cluster -> Global, excluding regulated regions -> Global, all regions
```

Use for features with regulatory variance (EU AI Act, GDPR-specific UI, payment-method constraints, age-verification rules).

### Shape D: A/B split with holdout

```
Variant A (control): 50%
Variant B (test): 45%
Holdout (no exposure): 5%
```

Use for experiments. The holdout group is never exposed even after rollout, so the team can measure long-term lift weeks after the experiment concludes.

### Shape E: Dark launch (shadow)

```
Code shipped to 100% -- no user-visible behavior
Backend runs the new path in shadow; results discarded but logged
```

Use to validate performance, error rate, and side effects before any user sees the new behavior. Standard for high-traffic system changes; also standard for AI features (pair with `ai-feature-prd/` Section 11.3).

### Shape F: Reverse ramp (sunset)

```
100% -> 75% -> 50% -> 25% -> 10% -> 0%
```

Use for retiring a feature. The ramp gives users time to migrate; analytics monitor whether users are healthy on the new path. Pair with `eol-communication/`.

### Shape G: Forced-upgrade (mobile)

```
Server-side flag check -> app refuses to start on old client -> user must upgrade
```

Special case for mobile when the new feature requires a client version. Always have a transition window; never flag-flip on day 1 of release.

## Kill-switch decision tree

A kill-switch is the on-call's emergency control. Three rules:

1. **Every release toggle has a kill-switch path.** "Turn the flag off" must be a single config change, not a code rollback.
2. **The kill-switch threshold is pre-agreed.** Define it during planning, not in the heat of incident.
3. **The on-call has authority to flip without escalation.** If the rollback requires VP sign-off, the system is too slow.

### Decision tree

```
Incident detected.
|
+-- Customer impact? -- No --> Monitor; document; do not flip.
|        |
|        Yes
|        |
|        v
+-- Within feature-flagged surface? -- No --> Standard incident response.
|        |
|        Yes
|        |
|        v
+-- Error rate > threshold OR major-customer-blocked? -- No --> Throttle / partial degrade.
|        |
|        Yes
|        |
|        v
+-- Flip kill-switch -- 0% rollout -- Notify owner + customers.
         |
         v
   Post-incident: root cause; flag stays off until fix lands; never re-enable without re-ramp.
```

### Kill-switch thresholds (defaults to tune per surface)

| Surface | Default threshold |
|---|---|
| Critical (checkout, auth, billing) | Error rate > 0.5% sustained for 5 min |
| Core (search, signup, dashboard) | Error rate > 2% sustained for 10 min OR top-tier-customer blocked |
| Non-critical | Error rate > 5% sustained for 15 min |
| Latency | p95 > 2x baseline for 10 min |
| Customer reports | >= 3 independent reports of the same issue from paid customers |

## Holdouts

A holdout is a slice of users (typically 1-10%) who never see the feature, even after general availability. Two uses:

**Short-term holdout** -- to measure the lift of the feature with statistical confidence over time. Required for any experiment where the team wants to attribute long-term impact.

**Long-term ("global") holdout** -- a slice that never sees *any* of the team's experiments for a quarter. Allows leadership to attribute aggregate lift to the team. Most experimentation-mature orgs run a global holdout.

### Holdout governance

- **Size**: 1-10%; smaller holdouts have less statistical power but cost less in lost feature exposure.
- **Composition**: random or stratified (by segment, geo, plan tier).
- **Duration**: at least one full retention horizon (D30 or D60); often 1-2 quarters.
- **Documentation**: holdout configuration in source control; never modified mid-experiment.
- **Re-exposure**: when the holdout ends, members are merged back; the team should plan for the conversion event.

## Flag debt and retirement

Every feature flag is technical debt by default. A live flag has a maintenance cost (test matrix, code branches, config integrity). Successful teams treat flag retirement as a first-class engineering activity.

### Retirement checklist (release toggle)

- [ ] Feature is at 100% for at least 2 weeks with stable metrics.
- [ ] No regression has been triaged that the flag would mitigate.
- [ ] Flag owner has filed a retirement PR removing both branches of code.
- [ ] Test matrix updated to remove the flag combinations.
- [ ] Config entry removed from the flag service.
- [ ] Documentation updated (runbook, customer-facing docs if any).
- [ ] Final state archived (what the flag controlled, when it retired, who owned it).

### Retirement signals

- Flag has been at 100% for 30+ days -> retire.
- Flag has been at 0% for 30+ days and the feature is dead -> retire.
- Flag has not been flipped in 60+ days and no plan to flip -> investigate and retire or convert to a permission/ops flag with explicit ownership.
- Flag is referenced in fewer than 3 places in code -> trivially retirable; remove.

### Flag-debt audit cadence

Run a flag audit at least quarterly:
- List of all live flags.
- For each: type, owner, last toggle date, retirement date.
- Flag count delta vs last quarter.
- "Aged flag" report: flags older than 90 days that are not Ops or Permission.

## Naming conventions

A flag name is read more often than it is written. Conventions:

```
<scope>__<feature>__<purpose>__<version>
```

Examples:
- `web__checkout__new_flow__v2` (release toggle on web for new checkout flow v2)
- `api__search__relevance__experiment_q3` (experiment toggle in API)
- `infra__search__circuit_breaker` (ops toggle, permanent)
- `product__enterprise_admin__permission` (permission toggle, permanent)

Rules:
- **Scope first** -- web / mobile / api / infra. Lets you search "all checkout flags on web."
- **Feature second** -- the system surface, not the marketing name.
- **Purpose third** -- release / experiment / ops / permission. Often baked into name (`__test`, `__experiment`, `__permission`, `__rollout`).
- **Version when applicable** -- experiments and major UX redesigns benefit from version suffixes.
- **No team names in the flag name** -- teams reorg; flags outlive the team.
- **No customer names** -- exception: enterprise-specific permission flags can include the tenant id.
- **lowercase + underscores or double-underscores** -- avoid camelCase to keep search predictable.

## Dependency chains

A flag depends on another when feature A only makes sense if feature B is also enabled. Two rules:

1. **The dependency is encoded explicitly** in the flag service (e.g., LaunchDarkly prerequisites) or in code with a clear check.
2. **The rollout plan reflects the dependency** -- ramp the parent flag first, hold until stable, then ramp the child.

Dependency chains beyond 2-3 levels become unmanageable. If a flag depends on three other flags, the rollout plan needs flattening.

## Approval and audit trail

Flag flips on critical surfaces should require:
- **Pre-approved owner** -- who can flip without further sign-off (usually the team's PM + the on-call engineer).
- **Change log entry** -- automatic; every flip logged with who, when, what, why.
- **Two-person rule** for high-tier surfaces -- billing, auth, data deletion. One person proposes, another approves before flip.
- **Audit retention** -- 90+ days of flag-change history available to the on-call.

## Workflow

1. **Classify the flag** (release / experiment / ops / permission). The lifespan and ownership follow.
2. **Pick the rollout shape** (A-G above) and the gate criteria between stages.
3. **Define the kill-switch** thresholds and authority.
4. **Set the retirement date** (release/experiment toggles only). Add it to the team's flag-audit list.
5. **Name the flag** using the convention.
6. **Document the plan** in the `assets/rollout_plan_template.md`. Share with eng, on-call, sponsor.
7. **Wire the flag** (engineering side; PM does not do this).
8. **Ramp** through the stages, holding each step long enough for metrics to settle.
9. **Monitor**. Watch the same dashboard for each step. Declare each step a "green pass" before advancing.
10. **Retire** the flag when GA is stable. Add to next sprint's retirement PRs.
11. **Audit** flag inventory quarterly; remove stragglers.

## Tools

This skill is template-based; no Python tool. Artifacts are markdown plans.

| Template | Purpose |
|---|---|
| `assets/rollout_plan_template.md` | Per-feature rollout plan with stages, gates, owners, dates |
| `assets/kill_switch_decision_tree.md` | Pre-incident thresholds + authority + flip steps |
| `assets/flag_debt_retirement_checklist.md` | Flag-retirement workflow + quarterly audit |
| `assets/flag_naming_convention.md` | Naming sheet for the team |

## Troubleshooting

| Symptom | Likely Cause | Resolution |
|---|---|---|
| Flag inventory has 200+ live flags | No retirement discipline; release toggles never deleted | Run a quarterly audit; mass-retire anything 100% > 30 days; lock new flag creation behind a retirement-date requirement |
| Rollback during incident requires a code revert | Flag is on but the rollback path is not wired | Every release toggle has a kill-switch path (single config change); rehearse the flip in non-prod once a quarter |
| Mobile feature flag broke users on old app version | Flag flipped before client adoption; no version gate | Always gate mobile flags on minimum client version; transition window of at least one release cycle |
| Two flags interact in unexpected ways | Implicit dependency; flag combinations not tested | Encode dependencies in the flag service; cover the cross-product in test matrix; flatten dependency chains > 2 levels |
| Experiment "shipped" but holdout was killed | Holdout retired with the experiment; no long-term measurement | Keep the holdout open for at least one retention horizon after launch; document re-exposure as a separate step |
| Owner of a flag has left the company | No ownership succession on flags | Flag ownership is by team, not by individual; team owner reviews the flag list during onboarding |
| Flag-flip incident: wrong person flipped | Permissions too loose; no two-person rule on critical flags | Critical surfaces require two-person approval; rotate the kill-switch authority to the on-call rota |
| Feature ramped to 100% but metrics never validated | No gate criteria between stages | Pre-agree the gate metrics; do not advance without a "green pass" from the owner |

## Success Criteria

- Every release / experiment toggle has a documented type, owner, kill-switch threshold, and retirement date.
- The rollout plan names the gate metric between each stage.
- The kill-switch can be flipped by the on-call without escalation.
- Mobile flags are gated on a minimum client version.
- Quarterly flag audit runs; flag count is stable or decreasing over time.
- Naming convention is enforced (linter or PR review).
- Experiments include a holdout that survives launch.
- Flag-debt retirement is part of every sprint, not a periodic cleanup.
