# Red Flags: Roadmap Communication

> Common ways this skill's output goes wrong -- concrete examples, why they're bad, and how to fix them.

## How to use this document

Scan every roadmap artifact (exec deck, customer-facing roadmap, internal Confluence page) before publishing. Each red flag has bad and good quoted examples.

---

## Red Flag 1: One Roadmap for All Audiences

**Symptom.** The same Gantt chart is shown to the board, to customers, and to engineering.
**Why it's bad.** Each audience has different stakes. The board wants outcomes and confidence levels. Customers want themes and approximate sequencing. Engineering wants dependencies and acceptance criteria. A single artifact fails all three -- it is too detailed for the board and too vague for engineering.
**Bad example:**
> "Q2 Roadmap (single Confluence page, shown to board on Monday, customer advisory on Tuesday, engineering all-hands on Wednesday): 47 line items with dates, owners, and ticket links."
**Good example:**
> "Three views derived from the same source roadmap:
> - **Board view**: 5 strategic bets, each with a confidence level and an outcome metric.
> - **Customer view**: 4 themes with quarterly buckets (Now / Next / Later), no dates.
> - **Engineering view**: 47 initiatives with dependencies, owners, target sprints."
**How to catch it.** Reusing the exact same artifact for two different audiences = generate audience-specific views from one source.

---

## Red Flag 2: Dates Promised as Commitments

**Symptom.** Customer roadmap lists "Feature X: April 2026". Customer reads this as a contract and procurement schedules around it.
**Why it's bad.** A roadmap is an artifact of intent, not a contract. Dates communicated as commitments destroy the team's ability to learn and re-prioritize. The PM either becomes a slave to the date (shipping a worse version) or burns customer trust by missing it.
**Bad example:**
> "Customer roadmap:
> - Bulk-edit: March 15, 2026
> - SCIM: April 30, 2026
> - SOC 2 audit report: May 31, 2026"
**Good example:**
> "Customer roadmap (Now / Next / Later):
> - **Now** (Q2 2026, high confidence): bulk-edit, SOC 2 audit report.
> - **Next** (Q3 2026, medium confidence): SCIM provisioning.
> - **Later** (H2 2026, low confidence): SAML SP-initiated flows.
> Dates above are planning approximations and may shift as we learn. Contractual commitments live in your MSA, not here."
**How to catch it.** Any customer-facing roadmap with calendar dates = replace with Now / Next / Later buckets.

---

## Red Flag 3: Now / Next / Later With No Themes

**Symptom.** Roadmap is a flat list of features in Now / Next / Later, no organizing theme.
**Why it's bad.** Without themes, customers cannot extrapolate where the product is heading. They see features but not direction. Sales cannot pitch the strategic story. Internal teams optimize for feature delivery, not the larger outcome.
**Bad example:**
> "Now: bulk-edit, dark mode, SOC 2.
> Next: SCIM, audit log, OAuth.
> Later: SAML, FedRAMP, advanced roles."
**Good example:**
> "Now -- *Activation*: bulk-edit, dark mode, onboarding redesign.
> Now -- *Enterprise readiness*: SOC 2, audit log.
> Next -- *Activation*: in-product templates.
> Next -- *Enterprise readiness*: SCIM, OAuth.
> Later -- *Enterprise readiness*: SAML, FedRAMP."
**How to catch it.** Roadmap items not bucketed under a theme = add themes; if no themes exist, you do not have a strategy.

---

## Red Flag 4: Roadmap = Feature List (Outputs, Not Outcomes)

**Symptom.** Every item is a feature name; nothing describes the customer outcome.
**Why it's bad.** Output roadmaps lock the team into specific solutions before validation. When a feature does not move the metric, the team ships it anyway because it is on the roadmap. The roadmap becomes an obstacle to learning.
**Bad example:**
> "Q2 roadmap: bulk-edit, dark mode, SCIM."
**Good example:**
> "Q2 roadmap (outcome -> bets):
> - *Outcome*: reduce time-to-second-action from 7 min to 3 min. *Bets*: bulk-edit, in-product templates.
> - *Outcome*: unblock 4 enterprise deals stuck on compliance. *Bets*: SOC 2, audit log, SCIM.
> Bets are revisable as we learn."
**How to catch it.** Outcome column absent = use `outcome-roadmap` skill to transform.

---

## Red Flag 5: Confidence Levels Missing

**Symptom.** Roadmap items appear with equal visual weight, regardless of whether they are a researched bet or a wild guess.
**Why it's bad.** All bets are not equal. Stakeholders need to know which items have high evidence behind them and which are speculative. Without confidence levels, the board treats Later-bucket guesses as plans, and the PM gets pinned to ideas that should still be exploratory.
**Bad example:**
> "Q3 roadmap: SCIM, marketplace, AI agent. (All listed identically.)"
**Good example:**
> "Q3 roadmap:
> - SCIM (Confidence: HIGH; 4 design partners committed)
> - Marketplace (Confidence: MEDIUM; opportunity solution tree validates demand; build approach unvalidated)
> - AI agent (Confidence: LOW; hypothesis only; 2-week spike in Q2 to assess)"
**How to catch it.** No confidence column = add one. Anything without evidence = LOW.

---

## Red Flag 6: Roadmap Updated Annually

**Symptom.** Roadmap published in January, never revised, presented at year-end with most items either shipped late or never shipped.
**Why it's bad.** A roadmap that does not revise loses signal value -- everyone learns to ignore it. Worse, customers anchor on the original version and feel betrayed when reality diverges.
**Bad example:**
> "Roadmap v1, January 2026. (Last edit: January 2026.)"
**Good example:**
> "Roadmap reviewed monthly in the leadership sync, revised quarterly with explicit changelog. Customers subscribed via Productboard get a monthly digest of changes ('Moved SAML from Q3 -> Q4 because the design partner pulled; added in-app templates to Q2 based on Q1 NSM data')."
**How to catch it.** Last-edit timestamp older than 6 weeks on a customer-facing roadmap = update or pull down.

---

## Red Flag 7: Wishlist Items Treated as Roadmap

**Symptom.** Sales team adds features to the roadmap whenever a customer asks. The roadmap balloons to 60+ items.
**Why it's bad.** Roadmaps need to be selective to be useful. Adding everything anyone has requested produces an unfilterable list that customers cannot act on and engineering cannot deliver. The roadmap becomes a wishlist.
**Bad example:**
> "Q2 / Q3 / Q4 roadmap (60+ items added by sales, success, and product over the year): every feature a customer has ever asked for."
**Good example:**
> "Roadmap shows only validated bets that survived prioritization (RICE-scored, top quartile). Unvalidated requests live in Productboard's insights inbox and feed into discovery, not the roadmap. Sales / Success can see the inbox; only the PM moves items onto the roadmap."
**How to catch it.** Roadmap item count > 20 per quarter = the roadmap is a wishlist; separate it from the inbox.

---

## Red Flag 8: No Visualization for the Customer View

**Symptom.** Customer-facing roadmap is a wall of bullet points.
**Why it's bad.** Customers and executives are visual. A wall of bullets is harder to scan, retain, and reference than a swimlane / Kanban / GO product roadmap visual. Adoption (the audience actually opening the roadmap) drops.
**Bad example:**
> "[5 pages of nested bullets]"
**Good example:**
> "Customer roadmap: a single-page Now / Next / Later board with theme swimlanes and color-coded confidence levels, drawn as a Mermaid diagram. Bullet detail lives in the appendix for those who want it."
**How to catch it.** Customer-facing roadmap with no visual = generate one.

---

## Red Flag 9: Promising Roadmap Items in Contracts

**Symptom.** A sales contract MSA lists 3 roadmap features as "to be delivered by Q3 2026".
**Why it's bad.** Roadmap items are intent, not commitments. Embedding them in contracts creates legal liability for things that should remain revisable. The PM loses agency to learn and re-prioritize.
**Bad example:**
> "MSA Schedule A: 'Vendor will deliver SCIM, audit log, and SAML by Q3 2026.'"
**Good example:**
> "MSA Schedule A names a *delivery commitment* (SOC 2 audit report by June 30 -- a deliverable, not a feature) and a *roadmap notification* clause ('Vendor will give 60 days' notice of material changes to the roadmap shared in CRM/Productboard'). Features are not promised in MSAs."
**How to catch it.** Pull sales contracts; search for roadmap feature names. Any presence = escalate to legal + sales-ops.

---

## Red Flag 10: Internal Roadmap That Hides Bad News

**Symptom.** Internal roadmap is "all green", but everyone in the team knows two initiatives are deeply in trouble.
**Why it's bad.** Hidden bad news compounds. By the time leadership finds out (usually from a missed launch), it is too late to redirect. Teams learn that the roadmap is a marketing document, not a coordination tool, and stop trusting it.
**Bad example:**
> "Internal roadmap shows all 7 initiatives 'on track'. In team standups, two are 4 weeks behind."
**Good example:**
> "Internal roadmap has a red/yellow/green status column updated weekly by initiative lead. Two initiatives currently red, with a documented mitigation plan (descope to MVP for one; pull in engineer from another initiative for the second). Leadership reviews changes weekly."
**How to catch it.** Internal roadmap shows > 95% green for > 2 weeks = the status column is theater. See `status-update-generator/references/red-flags.md` Red Flag 1.

---

## Red Flag Quick Reference

| # | Anti-pattern | One-line check |
|---|---|---|
| 1 | One roadmap for all audiences | Are there audience-specific views? |
| 2 | Dates promised as commitments | Customer view uses Now / Next / Later? |
| 3 | No themes | Items bucketed under strategic themes? |
| 4 | Outputs, not outcomes | Outcome column present? |
| 5 | No confidence levels | Each item has H / M / L confidence? |
| 6 | Annual updates | Last edit < 6 weeks ago? |
| 7 | Wishlist treated as roadmap | Item count per quarter < 20? |
| 8 | No visual for customer view | Customer roadmap has a visualization? |
| 9 | Roadmap items in contracts | MSAs reference deliverables, not features? |
| 10 | Internal roadmap hides bad news | > 95% green for weeks = theater |

## Related Reading

- `SKILL.md` -- the 3-audience pattern
- `references/audience-patterns.md` -- exec / customer / internal variants
- Sibling skill: `execution/outcome-roadmap/` -- output -> outcome transformation
- Sibling skill: `execution/status-update-generator/` -- the weekly status that feeds the internal roadmap
- Sibling skill: `productboard-expert/` -- the insights inbox that feeds discovery
- Sibling skill: `execution/quarterly-planning/` -- the planning cycle the roadmap reflects
