---
name: test-scenarios
description: >
  Generate test scenario coverage from a feature spec — happy paths, edge
  cases, error handling, accessibility, security, and performance — with a
  coverage analyzer that flags gaps. Use to define what to test before QA
  writes the test plan.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: project-management
  domain: execution
  updated: 2026-05-27
  python-tools: test_scenario_generator.py
  tech-stack: test-scenarios, qa, edge-cases, acceptance-criteria
---

# Test Scenarios

Generate complete scenario coverage from a feature spec before tests
are written. Closes the gap between "we built it" and "it survives
production."

## When to use this skill

- After **PRD approval** but before engineering implementation
- During **sprint planning** to size testing effort
- During **code review** to verify test coverage
- During **QA planning** to scope test pass
- During **bug-bash** prep
- After a **production incident** to validate scenario gaps

## The 7 scenario categories

For every feature, generate scenarios across:

1. **Happy paths** — primary user goals achieved cleanly
2. **Edge cases** — boundary conditions, unusual inputs
3. **Error handling** — what users see when things go wrong
4. **Empty states** — first-use, no data, after-delete
5. **Concurrent operations** — race conditions, optimistic locking
6. **Accessibility** — keyboard nav, screen reader, contrast, motion
7. **Security + privacy** — auth, permissions, PII, injection

Plus when applicable:
- Performance scenarios (load, latency, throughput)
- Localization (RTL, long-string, currency, date format)
- Cross-platform (browsers, devices, OS versions)

## Clarify First

Before generating scenarios, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Feature type** — form, browse/list, real-time/collab, file upload, payment, or bulk operation (drives the scenario count per category in the coverage rubric)
- [ ] **Risk / sensitivity profile** — auth, payment, or PII involved (scales up security and concurrency coverage in the risk-weighted selection)
- [ ] **The spec's inputs, outputs, and side effects** — what users provide, expect, and what changes in the system (drives edge cases in Step 3 and error handling in Step 4)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Workflow

### Step 1 — Spec read
Read the PRD / user story / acceptance criteria. Identify:
- User goals (what they want to do)
- Inputs (what they provide)
- Outputs (what they expect)
- Side effects (what changes in the system)

### Step 2 — Happy path
For each user goal, write the primary flow:
- Preconditions
- Steps
- Expected result

Aim for 1-3 happy paths per feature.

### Step 3 — Edge cases
For each input, ask:
- What's the empty value?
- What's the minimum?
- What's the maximum?
- What's just below min / just above max?
- What's the wrong type?
- What's the weird-but-valid (very long, special chars, Unicode, emoji)?

### Step 4 — Error handling
For each failure mode:
- Network failure
- Server error (5xx)
- Validation error (4xx)
- Timeout
- Concurrent modification
- Auth expired / lost

For each: what does the user see? Recover-from / try-again UX?

### Step 5 — Empty / first-use / after-action states
- First use (no data)
- After delete (last item)
- After error (partial state)
- After timeout
- After cancel

### Step 6 — Concurrent / race scenarios
Two users simultaneously:
- Editing same record
- Triggering same action
- Submitting same form
- Reaching capacity limit

### Step 7 — Accessibility
- Tab through with keyboard
- Use with screen reader
- High contrast / inverted colors
- Reduced motion preference
- Large text scaling
- Voice control

### Step 8 — Security + privacy
- Logged out user accesses
- Unauthorized user accesses
- Permission downgrade mid-action
- PII handling
- Injection attempts (XSS, SQLi)
- Rate limiting

### Step 9 — Run `test_scenario_generator.py`
Audit a candidate scenario list for category coverage; flag gaps.

```bash
python3 project-management/execution/test-scenarios/scripts/test_scenario_generator.py \
  --input feature_spec.json --format markdown
```

## Decision frameworks

### How many scenarios per category?

| Feature type | Happy | Edge | Error | Empty | Concur | A11y | Security |
|--------------|-------|------|-------|-------|--------|------|----------|
| Form / submission | 1-3 | 4-8 | 4-6 | 2 | 1-2 | 4 | 3-5 |
| Browse / list | 2-3 | 3-5 | 2-3 | 2-3 | 1 | 3 | 2 |
| Real-time / collab | 3 | 4-6 | 4-6 | 2 | 4-6 (essential) | 3 | 3 |
| File upload | 2 | 6-10 (sizes/types) | 4-6 | 1 | 1-2 | 2 | 5+ (file abuse) |
| Payment / financial | 3 | 6-10 | 8+ (critical) | 2 | 4-6 (idempotency!) | 3 | 8+ |
| Bulk operation | 2 | 4-6 (sizes) | 4-6 | 1 | 2-4 (partial fail) | 2 | 3 |

Adjust for risk profile of the specific feature.

### Risk-weighted scenario selection

Not all scenarios need full QA coverage. Apply:
- **Happy path:** always test
- **Edge cases:** test those that matter (likelihood × severity)
- **Error handling:** test all paths that user can recover from
- **Empty state:** always test (first impression!)
- **Concurrent:** test for data-integrity-critical features
- **Accessibility:** baseline coverage on all UI; full coverage on user-facing
- **Security:** scale with sensitivity (full coverage on auth/payment)

### Manual vs automated

| Scenario type | Default |
|----------------|---------|
| Happy path | Automated (E2E or integration) |
| Edge cases (input validation) | Unit tests |
| Error handling | Mix (mocked errors in unit; real in integration) |
| Empty state | Visual regression + manual |
| Concurrent | Hard — usually manual + targeted integration |
| Accessibility | Automated (axe-core) + manual screen-reader |
| Security | SAST + DAST + manual review for critical paths |
| Performance | Automated load tests |
| Localization | Pseudo-localization + manual spot-check |

## Common engagements

### "Generate test scenarios for this new feature"
1. Read the PRD / spec.
2. Apply the 7 categories.
3. Generate scenarios; estimate count per category.
4. Run validator; address gaps.
5. Hand to QA for implementation.

### "Audit our test plan for completeness"
1. Categorize existing scenarios.
2. Identify under-covered categories.
3. Score by risk × likelihood.
4. Recommend additions.

### "Post-incident scenario gap analysis"
1. Pull the incident scenario.
2. Map: which category was missed?
3. Add scenario; verify regression coverage.
4. Update default-coverage rubric for that feature type.

## Anti-patterns to avoid

- **Only happy paths.** Production fails on edges; you skipped them.
- **No empty state.** First-use is broken.
- **"QA will figure it out."** No, QA tests what's specified.
- **Generic acceptance criteria.** "Should work" is not testable.
- **No accessibility scenarios.** Excludes users; fails compliance.
- **No security scenarios.** Vulnerable paths ship.
- **No performance scenarios for performance-sensitive features.** Surprise at scale.
- **Skipping concurrent for collaborative features.** Race conditions ship.

## References

- `references/scenario-categories.md` — deep on the 7+ categories with examples
- `references/coverage-anti-patterns.md` — common gaps + fixes

## Related skills

- `project-management/execution/create-prd` — upstream spec
- `project-management/execution/wwas` — acceptance criteria
- `engineering/senior-qa` — implementation
- `engineering/code-reviewer` — review coverage
- `product-team/spec-to-repo` — translating spec to tickets
