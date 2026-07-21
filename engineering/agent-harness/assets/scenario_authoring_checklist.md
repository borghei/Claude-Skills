# Scenario Authoring Checklist

Run through this before adding a scenario to a gating suite. A scenario that
fails any of the first five items will cost more in maintenance than it returns
in signal.

## The scenario is complete

- [ ] **Input** — the user turn(s), verbatim
- [ ] **World state** — what the tools will find, pinned (including an `as_of`
      date if correctness depends on time)
- [ ] **Tool behaviour** — recorded results for every tool the agent may call,
      including the error cases
- [ ] **Assertions** — at least one structural assertion, not only text matching
- [ ] **Budget** — latency, cost, and turn ceiling (or explicit reliance on the
      suite defaults)

## The assertions are durable

- [ ] No assertion quotes a full sentence of model output
- [ ] Text assertions target domain tokens (IDs, policy names, numbers), not phrasing
- [ ] At least one `tool_not_called` assertion if the agent can take an
      irreversible action in this scenario
- [ ] Every assertion carries a severity: `critical` / `major` / `minor`
- [ ] `critical` is reserved for safety, money, data loss, and refusals that
      must hold — not for "the answer was a bit worse"

## The scenario earns its place

- [ ] It covers a bucket the suite is thin on (happy / boundary / refusal /
      adversarial / failure-recovery / ambiguity)
- [ ] It came from a real incident, a real customer report, or a real
      disagreement about intended behaviour — not from imagination
- [ ] It fails against the *previous* known-bad behaviour (verify by running it
      against the pre-fix transcript; a scenario that passes both before and
      after tests nothing)
- [ ] Its runtime is acceptable for the suite tier it is joining (core suites
      should stay under 5 minutes end to end)

## Fixture hygiene

- [ ] All PII replaced with stable synthetic values at record time
- [ ] `prompt_sha` and `model` recorded in the run file
- [ ] No secrets, tokens, or internal URLs in the recorded tool results
- [ ] Fixture committed to version control and reviewed like code

## Before it becomes a gate

- [ ] The scenario has passed on two consecutive identical-config runs (a
      scenario that flips on a no-op is flaky, not a gate)
- [ ] The owning team is named and knows they will be paged when it fails
- [ ] There is a documented answer to "what do we do when this fails" beyond
      "investigate"
