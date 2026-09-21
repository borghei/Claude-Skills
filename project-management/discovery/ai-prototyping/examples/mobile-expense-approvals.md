# Worked Example: Mobile Expense Approvals

A fictional B2B expense-management product. Finance approvers batch approvals into a weekly desktop session; employees wait for reimbursement and flood support with chasers. The PM has four hypotheses and ten working days.

## Step 1 - Plan the prototypes

Input: [`../assets/hypotheses_sample.json`](../assets/hypotheses_sample.json)

```bash
python3 scripts/prototype_plan.py --input assets/hypotheses_sample.json
# exit 0 - every hypothesis has a metric, a threshold and a segment
```

What the plan says, and what the PM does with it:

| ID | Uncertainty | Rung | Decision |
|----|-------------|------|----------|
| H2 | usability | F3 working, synthetic data | Top priority: no evidence, high impact. The flow has dynamic states (policy badge, reject reason), so a clickable mock would hide the hard part. |
| H1 | desirability | F2 clickable | Push-notification concept with a waitlist ask. Two variants: "approve from the notification" vs "open a daily digest". |
| H4 | viability | F0 | No prototype. Pricing conversations with 8 Standard-tier buyers, run by the PM and sales. |
| H3 | feasibility | F3 (downgraded from F4) | The tool flags that real receipts are not approved. The spike runs on a synthetic receipt set; the real-data run waits for data-owner and security sign-off. |

Total prototype timebox: 10 days, exactly on budget.

The contrast case, [`../assets/hypotheses_untestable.json`](../assets/hypotheses_untestable.json), exits **2**: "Sales reps will love an auto-generated call recap" has no metric, no threshold and no segment, so there is nothing a test could falsify.

## Step 2 - Generate and test

- Prototype briefs written from [`../assets/prototype_brief_template.md`](../assets/prototype_brief_template.md), one per variant. Synthetic receipts only.
- H1: 10 approvers saw variant A or B; 7 of 10 joined the pilot waitlist (threshold 6 of 10). Variant A won on stated preference *and* on waitlist sign-ups.
- H2: 6 approvers, moderated, three goal-based tasks. 5 of 6 completed "reject an out-of-policy receipt" unassisted, median 48 seconds. One participant never noticed the policy badge, so the badge moved above the approve button before the handoff.
- H3: spike still running on synthetic data. It is carried as a risk, not as a finding.

## Step 3 - Hand off

The handoff below uses [`../assets/handoff_template.md`](../assets/handoff_template.md). It is also available as structured JSON in [`../assets/handoff_complete.json`](../assets/handoff_complete.json).

```bash
python3 scripts/prototype_handoff_checker.py --input examples/mobile-expense-approvals.md
# exit 0
python3 scripts/prototype_handoff_checker.py --input assets/handoff_incomplete.json
# exit 2 - real call recordings uploaded without approval, no throwaway list,
#          no security or accessibility notes, a "finding" with zero participants
```

---

# Prototype Handoff: Mobile Expense Approvals

**Owner (PM):** Priya N.  **Engineering lead:** Tomas R.  **Date:** 2026-09-21

## Prototype link
- https://example.internal/prototypes/mobile-approvals-v3 (variant A, build of 2026-09-18)

## Disposition
- Throwaway. Engineering rebuilds on the production mobile stack; reuse the flow, copy and badge placement only.

## Problem and users
- Finance approvers at 50-500 employee customers batch approvals into a weekly desktop session, so submitting employees wait days for reimbursement and open duplicate support tickets. Evidence: 14 discovery interviews, support ticket tagging for Q2, approval-latency data from the product database.

## Success metrics
- Median submit-to-approval time - baseline 6 days, target 2 days, window 90 days after GA
- Share of approvals completed on mobile - baseline 0%, target 30%, window 90 days after GA

## Validated findings
- H1 desirability - 10 participants - threshold at least 6 of 10 join the pilot waitlist - result 7 of 10 joined - validated
- H2 usability - 6 participants - threshold at least 5 of 6 unassisted, median under 60 s - result 5 of 6, median 48 s - validated after moving the policy badge
- H3 feasibility - spike on synthetic receipts - threshold at least 90% precision - open, carried as a risk

## Acceptance criteria
- Given a pending expense, when the approver taps the push notification, then the expense detail opens in under 2 seconds on a mid-range device
- Given an out-of-policy line, when the approver views the expense, then the violation badge and the policy rule text appear above the approve button
- Given the approver rejects, when they submit, then a reason is mandatory and the employee is notified within 1 minute
- All approval screens must meet WCAG 2.2 AA for contrast, labels and switch/keyboard access

## Non-goals
- Submitting expenses on mobile (already shipped)
- Multi-level approval chains (desktop only in v1)
- Offline approvals

## Constraints
- Ship on the existing mobile release train; no new OCR vendor in v1

## Risks and open questions
- H3 OCR precision unproven on real receipts - engineering lead - spike on approved data before sprint 2
- Android push opt-in rate unknown - PM - instrument in the pilot

## Throwaway list (what the prototype skipped)
- Auth: hard-coded demo login; build on the production SSO and session layer
- Error states: offline, timeout and partial-sync states not designed
- Accessibility: generated UI not audited; receipt viewer lacks screen reader labels
- Security: no input validation, no rate limiting, generated code never security-reviewed
- Performance: 40 synthetic receipts; no pagination or image compression
- Data model: flat JSON mock; engineering designs the real schema and audit trail

## Data and privacy
- Real customer data used in prototype tools: no
- 40 synthetic receipts built from public templates; the prototype tool's retention setting was checked before upload

## Security
- No production secrets or internal URLs in prompts or code; prototype repo archived read-only; generated code will not be merged

## Accessibility
- Production baseline WCAG 2.2 AA; known gaps from testing are listed in the throwaway list

## IP and licensing
- Prototype tool terms reviewed by legal on 2026-09-02: outputs owned by us; no restricted fonts or third-party assets used
