# Blameless Culture Guide

## What blameless really means

Blameless post-mortems are a practice imported from the safety-critical industries (aviation, healthcare, nuclear) and adapted by Google SRE and Etsy in the early 2010s. The core claim is empirical: organizations that punish individuals for incidents produce sanitized, defensive incident reports, learn nothing from them, and continue to suffer the same incidents. Organizations that explicitly remove personal blame from the learning process produce richer, more honest reports and reduce recurrence.

Blameless does **not** mean:
- No accountability. People are still accountable for following process, communicating clearly, and completing the action items they own.
- No consequences ever. Gross negligence and policy violations are addressed — but in HR or legal channels, not in the post-mortem document.
- Everyone is right. The post-mortem can name decisions that, in hindsight, were the wrong call. It just names them as decisions made by a system, not character flaws of a person.

Blameless **does** mean:
- Assume everyone acted reasonably given what they knew at the time.
- Focus on the conditions (code, process, tooling, organization) that produced the decision.
- Separate the learning artifact (the post-mortem) from the management artifact (performance review).

## The Dekker reframe

Sidney Dekker, in *The Field Guide to Understanding "Human Error"*, distinguishes between the **Old View** and the **New View** of human error:

| Old View | New View |
|---|---|
| Human error is the cause | Human error is a symptom |
| The system is mostly safe, humans introduce risk | The system is mostly unsafe, humans manage to make it work |
| Investigation finds the bad apple | Investigation finds the conditions that made the action locally rational |
| Fix: discipline, retraining, replacement | Fix: change the conditions |

A blameless post-mortem operates strictly in the New View. The question is never "why did Sarah deploy on a Friday?" It is "what conditions in our deploy process made a Friday deploy seem like a reasonable action to a competent engineer?"

## The Allspaw test

After writing the post-mortem, ask:

> "Would I send this document to the engineer who took the action that triggered the incident, and would they recognize their experience as fairly represented?"

If the answer is no, the document still contains blame, hindsight bias, or counterfactuals. Common signals to look for:

- Use of the word "should" (especially "should have").
- Use of "if only" or "had X happened".
- Phrases like "obvious", "clearly", "any competent X would have".
- A single person named in the narrative outside the contacts and action-item owner columns.
- The word "fault" appearing anywhere.

## Blameful vs blameless phrasing

| Blameful | Blameless |
|---|---|
| The on-call engineer should have noticed the queue depth alert. | The dashboard did not alert on queue depth exceeding 10,000 messages. |
| Sarah pushed the broken deploy. | A deploy at 16:42 UTC introduced the regression; the CI suite did not cover the affected code path. |
| The team failed to test the migration. | The migration test environment lacked production-scale data, so the lock contention pattern did not surface in pre-production. |
| Joe forgot to update the runbook. | The runbook update step is not part of the deploy checklist; runbook drift is not detected automatically. |
| If only we had run the canary properly, we would have caught it. | The canary deploy was configured to skip the affected service; canary coverage is not enforced at the service level. |
| The new engineer didn't know about the failover process. | The failover process is documented only in one engineer's personal notes; onboarding does not include a failover drill. |
| Management decided to skip the load test to ship faster. | The release calendar created pressure to ship by a specific date; the load test was deprioritized in a tradeoff decision documented in DECISION-1234. |
| Customer Support should have escalated faster. | The escalation criteria from Support to Engineering require a manager approval that the on-call manager was not paged for; the rotation for that page was stale. |

Notice the pattern: every blameless version names a system property (a dashboard threshold, a test fixture, a checklist, a documentation gap, a process gate). System properties are things the team can change. People are not.

## Hindsight bias

Hindsight bias is the cognitive distortion that makes past events seem more predictable than they actually were. Once you know the outcome, it is impossible not to see the steps that led to it. The post-mortem author's job is to deliberately strip out hindsight.

Test for hindsight bias: ask "at this moment in the timeline, what did the person know? what alerts had fired? what dashboards had they checked?" Reconstruct the information state. Often you discover that the "wrong" decision was the only reasonable decision given the information available.

A useful heuristic: if reading the timeline makes you think "well, obviously they should have done X next" — that's hindsight bias. They didn't have your view of the whole timeline. They had a noisy signal in the moment.

## Counterfactuals are not causes

A counterfactual is a statement about what would have happened if reality had been different: "if only we had run the canary, we would have caught it". Counterfactuals feel like causal claims but they are not. They are wishes.

The blameless reframe of a counterfactual is to find the system property that made the counterfactual scenario impossible or unlikely.

- Counterfactual: "If only the team had reviewed the migration script more carefully, the typo would have been caught."
- System property: "The migration review process did not include a syntax-check or dry-run; reviews relied on visual inspection of SQL."

Now you have something to change. "Review more carefully" is not actionable. "Add a CI step that runs every migration through a syntax checker and a dry-run in a staging schema" is.

## Establishing the culture

Blameless post-mortems do not happen because someone declares them. They happen because:

1. **Leadership says so explicitly and repeatedly.** A one-time email is insufficient. The CTO/VPE talks about blamelessness in all-hands, in 1:1s, and when an incident happens.
2. **Performance reviews are insulated.** Engineers know, in writing, that nothing they say in a post-mortem can be used against them in performance review. This is communicated by management and by HR.
3. **The first few post-mortems set the tone.** When the first Sev 1 happens after the policy is announced, the leadership team treats it as a model. Public praise for the author's honesty, no consequences for the engineer involved, visible action-item follow-through.
4. **Stories are told.** "Remember the time we lost three hours of writes? Here's what we learned." The retold incident becomes a cultural artifact rather than a buried embarrassment.
5. **Action items get done.** If post-mortems generate action items that never ship, engineers learn that post-mortems are theater. Completion rate is the loudest signal of how seriously leadership takes the practice.

## When blameless is genuinely hard

There are scenarios where pure blamelessness is in tension with other obligations:

- **Regulated industries** (medical devices, financial services, aviation): regulators may require named accountability in the formal report. The pattern is to run two artifacts in parallel: an internal blameless learning post-mortem, and a regulator-facing formal report. The two reference each other but serve different audiences.
- **Security incidents involving insider action**: if an engineer deliberately bypassed controls, the incident is not a blameless learning event. It belongs in HR / legal channels. The blameless post-mortem still happens for the *system* (why was the bypass possible?), separately from the personnel matter.
- **Repeated individual pattern**: if the same engineer is the proximate actor in multiple incidents, this is a management conversation about role fit, training, or workload — not a post-mortem matter. Conduct that conversation in 1:1s, not in incident review.

The mantra: blameless in the post-mortem, accountable in the action items, performance-managed in HR. Three separate channels, never mixed.

## References

- John Allspaw, "Blameless PostMortems and a Just Culture" (Etsy, 2012)
- Richard Cook, "How Complex Systems Fail" (1998) — short paper, essential reading
- Sidney Dekker, *The Field Guide to Understanding "Human Error"* (3rd ed., 2014)
- Sidney Dekker, *Just Culture* (3rd ed., 2017)
- Google SRE Book, "Postmortem Culture: Learning from Failure" — https://sre.google/sre-book/postmortem-culture/
- Charles Perrow, *Normal Accidents: Living with High-Risk Technologies* (1984)
- Erik Hollnagel, *Safety-I and Safety-II: The Past and Future of Safety Management* (2014)

---

## Blameless Principles (quick reference from SKILL.md)

The single most-cited reason post-mortems fail to produce learning is that participants feel unsafe. Blameless does not mean "consequence-free" — accountability still exists for following process. It means: assume that everyone involved acted reasonably given what they knew at the time, and focus on the system that surrounded their decision.

### Five blameless ground rules

1. **No names in the narrative.** Refer to roles, not people. "The on-call engineer", not "Sarah". Names appear only in the contacts table and the action-item owner column.
2. **No "should have".** Replace with "the system did not surface". "The on-call should have noticed the queue depth" → "The dashboard did not alert on queue depth above 10,000".
3. **No counterfactuals in the root cause.** "If only X had not happened" is not a cause; it is a wish. Stick to mechanisms.
4. **Human error is a symptom, not a cause** (Dekker). When a human acted "incorrectly", the goal is to understand why that action was the locally rational thing to do.
5. **Hindsight bias is the enemy.** What is obvious now was not obvious then. Reconstruct what was knowable in the moment, not what is knowable now.

### The Allspaw test

Adapted from John Allspaw's writing: after writing the post-mortem, ask: *"Would I send this document to the engineer who pushed the button, and would they feel that it represented their experience fairly?"* If no, rewrite until yes.
