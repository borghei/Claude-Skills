# Red Flags: Release Notes

> Common ways this skill's output goes wrong -- concrete examples, why they're bad, and how to fix them.

## How to use this document

Scan every release-note draft before it ships to customers, in-app, or via email. Each red flag has bad and good quoted examples.

---

## Red Flag 1: Changelog Disguised as Release Notes

**Symptom.** The release note is a list of ticket titles copied from Jira / Linear, with the engineering vocabulary intact.
**Why it's bad.** A changelog is for developers; release notes are for users. Pasting tickets verbatim makes customers parse internal language ("Fixed: SEG-2241"), lowers read-through, and hides genuine value behind noise.
**Bad example:**
> "v3.4 release notes:
> - SEG-2241 Refactor of the user-event ingestion pipeline
> - SEG-2310 Added retry logic to webhook dispatcher
> - SEG-2342 Migrated from Redis 6 to Redis 7"
**Good example:**
> "v3.4 release notes:
> **Events arrive faster.** Webhook events now retry automatically when receivers are slow, reducing the 'missing event' tickets you have been raising by ~80%. No setup needed.
> *(Internal: SEG-2241, 2310, 2342)*"
**How to catch it.** Search the draft for ticket IDs in customer-facing text. Any visible ID = rewrite the line.

---

## Red Flag 2: No Value Framing

**Symptom.** Each item describes what was *built* but never *why a customer should care*.
**Why it's bad.** Customers skim release notes for 8 seconds and look for "what does this do for me?". Bare feature descriptions force them to translate, and they bounce. Adoption lags because no one knows what to try.
**Bad example:**
> "Added: keyboard shortcut Cmd+Shift+E to export."
**Good example:**
> "Export 10x faster from anywhere. New `Cmd+Shift+E` shortcut opens the export dialog from any view -- no more clicking through the menu. Useful for analysts who export several times a day."
**How to catch it.** Each item should answer "what can the customer now do that they could not do before, and why does it matter?". If absent, rewrite.

---

## Red Flag 3: Mixing Internal Refactors with Customer Wins

**Symptom.** Release notes list "migrated to Postgres 16" alongside "added dark mode" with equal weight.
**Why it's bad.** Internal infrastructure changes -- even ones engineers are proud of -- mean nothing to most customers and dilute the high-signal items. Customers learn to skim past your release notes because most lines do not concern them.
**Bad example:**
> "v4.2:
> - Dark mode is here.
> - Migrated from Postgres 14 to 16.
> - Added new pricing page.
> - Refactored the WebSocket reconnection logic."
**Good example:**
> "v4.2 (customer-facing):
> - Dark mode is here.
> - New pricing page lets you compare plans at a glance.
> ---
> v4.2 (under the hood, for our developer customers):
> - Postgres 16 upgrade: queries are 15% faster on average; expect snappier dashboards.
> - WebSocket reconnection is more aggressive: fewer 'disconnected' banners during flaky networks."
**How to catch it.** Items that mention only internal systems and have no observable customer impact = move to a separate "under the hood" section, or drop.

---

## Red Flag 4: No Segmentation by Audience

**Symptom.** One release note goes to all customers regardless of plan, segment, or feature usage.
**Why it's bad.** Enterprise admins want compliance / SSO / audit changes. End-users want UI changes. API customers want SDK / webhook changes. A blast email mixing them gets archived by everyone.
**Bad example:**
> "Hi everyone: SCIM provisioning is now generally available, dark mode is here, the Python SDK is bumped to v3, and our soc 2 audit completed."
**Good example:**
> "Three release notes generated from the same release:
> - For *Admins on Enterprise*: SCIM GA + SOC 2 audit report (link).
> - For *all users*: Dark mode is here.
> - For *API users*: Python SDK v3 with type hints and async support."
**How to catch it.** One draft, one audience. If you have multiple personas, generate multiple notes.

---

## Red Flag 5: Buried Breaking Changes

**Symptom.** A breaking API change is the 11th item in a bulleted list of 14, formatted identically to the rest.
**Why it's bad.** Breaking changes need attention or customers' production systems break. Burying them is a support and trust disaster. They must be at the top, visually distinct, with migration steps.
**Bad example:**
> "v5.0 release notes:
> - Faster searches.
> - New billing portal.
> - ...
> - [item 11] Deprecated /v1/users endpoint."
**Good example:**
> "**v5.0 -- ACTION REQUIRED before June 30**
> The `/v1/users` endpoint is deprecated and will be removed on June 30. Migrate to `/v2/users` (docs: link). Affected: every customer using the legacy SDK < 2.4.
> ---
> Other changes in this release: ..."
**How to catch it.** Search for "deprecated", "removed", "no longer supported". Any such item not in the first 100 words of the note = move to the top.

---

## Red Flag 6: Marketing Copy Replacing Specifics

**Symptom.** "Revolutionary new collaboration experience powered by AI." -- no concrete behavior described.
**Why it's bad.** Customers cannot try a "revolutionary experience". They try features. Vague hype copy in release notes signals the team is hiding either the feature is small or it does not actually solve a problem.
**Bad example:**
> "Game-changing AI-powered insights now live across the platform!"
**Good example:**
> "AI summaries on dashboards. When a dashboard has >= 6 charts, a 3-sentence summary appears at the top describing the most notable change since last week. Available on Pro and Enterprise plans. Disable in Settings -> AI."
**How to catch it.** Search for "revolutionary", "game-changing", "powered by AI", "next-generation". Each one needs a specific behavior + plan + opt-out.

---

## Red Flag 7: No Visual

**Symptom.** A UI change described in words only, no screenshot or short GIF.
**Why it's bad.** Visual changes are 3-5x more likely to drive adoption when shown vs described. Customers skim, see the screenshot, and immediately try the feature. Without a visual, the line is invisible.
**Bad example:**
> "We redesigned the dashboard navigation."
**Good example:**
> "We redesigned the dashboard navigation. [Annotated screenshot showing before / after, 30 KB, alt text describing the change]. The most-used 5 destinations are now in a left rail; everything else is in a 'More' menu. No action needed on your part."
**How to catch it.** Any line describing a UI change without an attached image = add or rewrite.

---

## Red Flag 8: No Version Number or Date

**Symptom.** Release note headline is "What's new!" with no version or date.
**Why it's bad.** Customers cite release notes in support tickets, internal change-management, and procurement reviews. Without a version + date, they cannot reference the note unambiguously, and support cannot disambiguate ("which 'what's new' are you on?").
**Bad example:**
> "# What's new!
> Dark mode and faster searches!"
**Good example:**
> "# v4.2 -- released June 14, 2026
> ## Highlights
> Dark mode and faster searches. Full notes below."
**How to catch it.** Top of the note must have a version and a date. No exceptions.

---

## Red Flag 9: Generated from Tickets That Were Never Closed Correctly

**Symptom.** Items appear in the release notes that were not actually shipped, because the underlying tickets were marked Done in Jira but the feature was reverted in code.
**Why it's bad.** Promising features that did not ship is a credibility disaster. Customers report bugs against features that do not exist, support has no answer, and trust drops.
**Bad example:**
> "v4.2: 'Granular permissions for projects' (ticket SEG-2400 marked Done in Jira)."
> ... but the feature was reverted in PR #4220 due to a security review.
**Good example:**
> "Before building `changes.json`, the PM runs `git log v4.1..v4.2` and checks each Jira Done ticket against the shipped commits. Tickets with no commit in the range go to human review. SEG-2400 caught; left out of the input, so it never reaches the notes."
**How to catch it.** `scripts/release_notes_generator.py` formats whatever entries it is given and does not look at git. Cross-check the Jira / Linear "Done" list against `git log <previous-tag>..<release-tag>` before you write the input file.

---

## Red Flag 10: Same Release Note Used Internally and Externally

**Symptom.** The internal Slack announcement and the customer-facing post are identical.
**Why it's bad.** Internal notes need known issues, on-call instructions, rollback procedures, and the rationale for sequencing. External notes need value framing and migration steps. Mashing them confuses both audiences.
**Bad example:**
> "Customer email contains: 'Known issue: occasional 502 on Safari, rollback in progress, on-call: @ana'."
**Good example:**
> "Two artifacts from the same release:
> - Internal: changelog + known issues + on-call + rollback steps + post-release-check checklist.
> - External: value-framed, audience-segmented, breaking-changes-first, with visuals.
> Both built from the same ticket list: run `scripts/release_notes_generator.py` once per audience, each time with its own input file (internal entries keep known issues and rollback notes; external entries keep value framing and migration steps)."
**How to catch it.** Audit any release note for the words 'rollback', 'known issue: internal', 'on-call'. If present in customer-facing copy, split.

---

## Red Flag Quick Reference

| # | Anti-pattern | One-line check |
|---|---|---|
| 1 | Changelog disguised as notes | Are ticket IDs visible in customer copy? |
| 2 | No value framing | Does each item answer "why care"? |
| 3 | Internal refactors mixed in | Are infra changes in a separate section? |
| 4 | No segmentation | One audience per draft? |
| 5 | Buried breaking changes | Are deprecations in the first 100 words? |
| 6 | Marketing copy replacing specifics | Does every "AI-powered" line have a concrete behavior? |
| 7 | No visual | UI changes have images? |
| 8 | No version + date | Top of note has both? |
| 9 | Generated from stale Jira | Was the Done list checked against `git log` before generating? |
| 10 | Internal = external | Are 'rollback' / 'on-call' in customer copy? |

## Related Reading

- `SKILL.md` -- release-note structure
- `scripts/release_notes_generator.py --help` -- the generator (formats JSON entries as text or JSON; it does not read git)
- Sibling skill: `execution/launch-playbook/` -- coordinated launch sequence
- Sibling skill: `execution/feature-flag-strategy/` -- handle gradual rollouts that span releases
- Sibling skill: `execution/roadmap-communication/` -- audience-segmented messaging patterns
