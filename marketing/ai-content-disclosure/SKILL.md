---
name: ai-content-disclosure
description: >
  Check AI-generated marketing content and reviews for required disclosures under
  the EU AI Act, FTC rules and platform AI-label policies. Use when labelling AI
  ads, deepfakes, chatbots, influencer posts or testimonials.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: marketing
  domain: marketing-compliance
  updated: 2026-09-21
  tags: [ai-disclosure, eu-ai-act, ftc, fake-reviews, endorsements, deepfake-labels, synthetic-media, ad-compliance]
---

# AI Content Disclosure

Decide, asset by asset, which disclosures AI-generated or AI-assisted marketing content needs — by jurisdiction and by platform — and block publication when a high-risk item is unresolved. Covers EU AI Act Article 50 (applies from 2 August 2026), the FTC Consumer Reviews and Testimonials Rule (16 CFR Part 465), the FTC Endorsement Guides (16 CFR Part 255), EU and UK fake-review law, New York's synthetic performer ad law, India's synthetic-content labelling rules, and the AI-label policies of YouTube, TikTok, Meta and Google Ads.

> **Not legal advice.** This skill turns public rules into a repeatable pre-publication check. It does not replace counsel, and every rule links its official source so you can verify it. Rules were checked against primary sources in September 2026.

---

## When to use this skill

| Situation | Use |
|-----------|-----|
| Launching a campaign with AI-generated video, images, voice or avatars | `scripts/disclosure_checker.py` on the content manifest |
| Publishing AI-drafted articles, reports or press notes to EU audiences | Decision tree Q4 + checker (`public_interest`, `human_review`) |
| Deploying a website chatbot or AI voice agent in the EU | Checker (`type: chatbot`) + wording library |
| Importing, soliciting or displaying reviews and testimonials | `scripts/review_authenticity_linter.py` |
| Briefing influencers or virtual influencers | Label templates §6 + Endorsement Guides summary |
| Checking a platform's own AI-label rule | [references/platform-ai-label-policies.md](references/platform-ai-label-policies.md) |
| Political or electoral advertising | Out of scope beyond platform checkboxes — route to counsel |

---

## Clarify First

Before running the check, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Audience regions** — EU, US, New York, UK, India (each switches on different rules; "global" means all of them)
- [ ] **AI involvement per asset** — none / assistive / partial / generated (assistive editing triggers no AI label; generated realistic media usually does)
- [ ] **Is anything a review, testimonial or endorsement?** — and who wrote it, and what they received (fake and undisclosed-connection reviews are the highest-penalty items)
- [ ] **Paid or organic, and which platform** — platform rules differ for ads, and TikTok rejects undisclosed AIGC ads

Stop rule: ask only the 2-3 that most change the output. If the user says "just check it," proceed with the manifest as given and list your assumptions at the top of the report.

---

## Quick start

```bash
# 1. Fill the manifest (one entry per asset)
cp assets/content_manifest_template.json my_campaign.json

# 2. Check disclosures — exits 2 if any high-risk item is unresolved
python3 scripts/disclosure_checker.py my_campaign.json
python3 scripts/disclosure_checker.py my_campaign.json --format json --fail-on medium

# 3. Lint reviews/testimonials before display
python3 scripts/review_authenticity_linter.py reviews.json

# 4. Apply wording from references/disclosure-wording-library.md and record it
#    in assets/disclosure-label-templates.md (§1 asset disclosure record)
```

The shipped samples fail on purpose: `sample_content_manifest.json` exits **2** with 7 unresolved high-risk findings (a deepfake without an on-asset label, an unreviewed AI press note, AI-written testimonials, an undisclosed employee review); `sample_reviews.json` exits **2** with 6 high-risk findings.

---

## Core workflow: pre-publication disclosure gate

1. **Inventory** every asset in the release into the manifest. Include reviews shown in ads and on landing pages, chatbots and voice agents — not just "creative". [PROVEN]
2. **Classify AI involvement honestly.** "Assistive" means standard editing (spelling, colour, crop, background clean-up). If AI changed what the viewer sees or reads, it is `partial` or `generated`. [RECOMMENDED]
3. **Run the checker.** Read findings top-down by risk. `FIX` lines are unresolved; `OK` lines are satisfied by the disclosures you declared.
4. **Remove, don't label, what cannot be labelled.** AI-written testimonials presented as customer reviews and sentiment-conditioned incentives are prohibited outright — the checker marks them unfixable. [PROVEN]
5. **Apply disclosures in three layers:** legal label on the asset, platform toggle, endorsement disclosure. They stack; none substitutes for another. [RECOMMENDED]
6. **Record evidence** in the asset disclosure record (label text, placement, screenshots, reviewer for the editorial-control exception).
7. **Re-run until exit 0**, then wire the checker into the release pipeline so new assets cannot skip it.

### Workflow: reviews and testimonials

1. Export the review set you plan to display or quote (own site, marketplace, ad copy).
2. Mark `source`, `incentive`, `incentive_conditioned_on_sentiment`, `generated_by_ai`, `suppressed` for each.
3. Run `review_authenticity_linter.py`. Remove every `fake-or-ai-review`, `sentiment-conditioned-incentive`, `review-hijacking` item; add disclosures for insider and incentivised items.
4. Publish a review-page statement (wording library) saying how reviews are verified — required in the EU (UCPD Art. 7(6)).
5. Treat `near-duplicate` and `posting-burst` as investigation leads, not verdicts.

### Workflow: EU text on matters of public interest

1. Decide whether the piece informs the public on a matter of public interest (news-like, policy, health, safety, finance, elections). Product copy normally does not.
2. If yes, choose: **label** it, or put it under **documented editorial control** (named reviewer with authority to approve, alter or reject, and an entity holding editorial responsibility).
3. Editorial control is the better default for brands that publish thought leadership — it improves quality and removes the labelling duty. Keep the evidence. [RECOMMENDED]

---

## Rule map (what the checker encodes)

| Rule ID | Trigger | Default risk | Fix |
|---------|---------|--------------|-----|
| EU-AIA-50(1) | Chatbot, EU | high | AI-interaction notice at first interaction |
| EU-AIA-50(4)-deepfake | Realistic AI image/audio/video, EU | high | On-asset label |
| EU-AIA-50(4)-deepfake-artistic | Same, evidently artistic/satirical | medium | Non-disruptive disclosure |
| EU-AIA-50(4)-text | AI public-interest text, EU, no editorial control | high | Label or editorial control |
| EU-AIA-50(2)-marking | You provide the generator | medium | Machine-readable marking (legacy systems: 2 Dec 2026) |
| FTC-465.2-fake-review | AI-generated review/testimonial | high, unfixable | Remove |
| FTC-255-material-connection / FTC-465.5-insider | Connection or insider | high | Disclose in the endorsement |
| FTC-255-virtual-influencer | Virtual influencer | medium | "#ad" + virtual persona disclosure |
| NY-synthetic-performer | Paid image/video ad with synthetic performer, NY | high | Conspicuous disclosure |
| EU-UCPD-* / UK-DMCC-* | Fake or undisclosed-connection reviews | high | Remove / disclose |
| IN-IT-Rules-SGI | Realistic AI media, India | medium | Visible label |
| YT / TT / META / GADS | Platform AI-label rules | medium-high | Platform toggle and/or label |

Full summaries with official links: [references/regulation-summaries.md](references/regulation-summaries.md).

---

## Key dates and numbers (verify before use)

| Item | Value | Source |
|------|-------|--------|
| EU AI Act Art. 50 applies | 2 Aug 2026 | eur-lex.europa.eu; digital-strategy.ec.europa.eu |
| Art. 50(2) marking, systems placed on market before 2 Aug 2026 | 2 Dec 2026 | Digital Omnibus on AI; Commission Art. 50 FAQ |
| EU AI Act fine for Art. 50 breaches | up to EUR 15m or 3% of worldwide turnover | Art. 99(4) |
| FTC Reviews Rule effective | 21 Oct 2024 | ftc.gov |
| FTC civil penalty per violation | USD 53,088 (2025 adjustment; see 16 CFR 1.98 for current) | ftc.gov; ecfr.gov |
| UK DMCC fake-review ban | from 6 Apr 2025; fines up to 10% of global turnover | CMA guidance |
| New York synthetic performer ad law | in effect June 2026 | governor.ny.gov |
| India IT Rules SGI amendment | in force 20 Feb 2026 | meity.gov.in |
| Google Ads AI label setting | rolled out July 2026 | support.google.com/adspolicy |
| Meta automated AI detection on ads | from 1 Jun 2026 | about.fb.com |

---

## Exit code contract [PROVEN]

Both scripts share the same contract so they can run as CI gates:

| Code | Meaning | Who fixes it |
|------|---------|--------------|
| 0 | No unresolved findings at or above `--fail-on` (default `high`) | Nobody |
| 1 | Tool error — bad path, malformed JSON, missing `id`/`type`/`text` | Whoever maintains the manifest |
| 2 | Gate failed — unresolved findings at or above `--fail-on` | Asset owner / campaign lead |

Keep 1 and 2 distinct. A malformed manifest is a pipeline problem; a missing label is a content problem.

---

## Anti-Patterns

### The Platform Toggle As Legal Compliance
**Mistake:** Ticking YouTube's or Google's AI toggle and treating the campaign as EU-compliant.
**Why it happens:** The toggle feels official, and the platform shows a label somewhere.
**Instead:** Platform labels can sit in a description or "About this ad" panel. For EU deepfakes, put the label on the asset at first exposure too. Google states its AI label setting does not guarantee regulatory compliance.

### The "Composite" Testimonial
**Mistake:** Asking AI to write testimonials "based on" real survey themes and displaying them with stock names and photos.
**Why it happens:** It feels truthful because the sentiments came from real customers.
**Instead:** A testimonial attributed to a person who did not write it misrepresents the reviewer. Quote real customers verbatim with permission, or present aggregated survey results as statistics.

### The Blanket "May Contain AI" Footer
**Mistake:** One site-wide footer line instead of per-asset labels.
**Why it happens:** It is cheap and feels like cover.
**Instead:** Art. 50(5) requires clear, distinguishable information at first exposure to the specific content. Label the asset; keep the footer as a supplementary policy statement if you like.

### The Invisible Editorial Review
**Mistake:** Relying on the human-review exception for AI-written articles without any record of who reviewed what.
**Why it happens:** Everyone "looked at it" in a shared doc.
**Instead:** Record reviewer, date, substantive changes and the editorial-responsibility holder. Without evidence, the exception is a claim, not a defence.

### Incentive Automations That Filter By Stars
**Mistake:** Sending discount codes only to customers who left 4-5 star ratings, or asking only happy NPS responders to review.
**Why it happens:** Growth tooling makes sentiment-gated flows a checkbox.
**Instead:** Sentiment-conditioned incentives are prohibited by FTC 465.4. Invite every customer (or a random sample) and disclose the incentive.

---

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| Asset shows "no disclosure rule triggered" but used AI | `ai_involvement` set to `assistive` or `regions` empty | Re-classify; add every audience region |
| Checker exits 1 | Missing `id`/`type` or invalid JSON | Validate against `assets/content_manifest_template.json` |
| Finding stays `FIX` after adding a label | Disclosure key not in `needs_one_of` | Use one of the listed keys in `disclosures_present` |
| Linter misses an obvious disclosure | Disclosure phrased unusually | Put the exact text in `disclosure_text`; extend `DISCLOSURE_RE` |
| Too many `near-duplicate` hits on short reviews | Short texts share phrases | Raise `--dup-threshold` to 0.7-0.8 |

---

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/disclosure_checker.py` | Content manifest → required disclosures per jurisdiction/platform, risk, gate |
| `scripts/review_authenticity_linter.py` | Review set → fake/AI, insider, incentive, suppression, hijacking, duplicate and burst findings, gate |

Both: Python 3.8+ standard library only, `--format text|json`, `--fail-on high|medium|low`, deterministic.

## References

- [regulation-summaries.md](references/regulation-summaries.md) — EU AI Act Art. 50, FTC 465 and 255, EU UCPD, UK DMCC, New York, India, with official links and penalties
- [platform-ai-label-policies.md](references/platform-ai-label-policies.md) — YouTube, TikTok, Meta, Google Ads rules as of September 2026
- [disclosure-wording-library.md](references/disclosure-wording-library.md) — label text, placement rules, translations, endorsement wording
- [disclosure-decision-tree.md](references/disclosure-decision-tree.md) — the asset-by-asset decision path and risk levels

## Assets

- `assets/content_manifest_template.json` — manifest schema with field guide
- `assets/sample_content_manifest.json` — failing sample campaign (exit 2)
- `assets/sample_reviews.json` — failing sample review set (exit 2)
- `assets/disclosure-label-templates.md` — evidence record, visual tag spec, bylines, chatbot opener, influencer clause
