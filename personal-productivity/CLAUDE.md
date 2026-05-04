# Personal Productivity Skills

Utility skills for individual workflows that don't fit cleanly into a single business domain — career, prospecting, meetings, naming, and bookkeeping.

## Skills in This Domain

| Skill | Folder | Primary Tool | Use For |
|-------|--------|--------------|---------|
| Resume Tailor | `resume-tailor/` | `resume_matcher.py` | Score resume against a JD; rewrite bullets for impact |
| Lead Researcher | `lead-researcher/` | `lead_qualifier.py` | Score leads against an ICP; draft outreach hooks |
| Meeting Insights | `meeting-insights/` | `transcript_analyzer.py` | Extract decisions, actions, questions, risks from transcripts |
| Domain Name Brainstormer | `domain-name-brainstormer/` | `name_generator.py` | Generate and score brand / domain candidates |
| Invoice Organizer | `invoice-organizer/` | `invoice_categorizer.py` | Categorize receipts, detect duplicates, monthly summary |
| Email Triage | `email-triage/` | `email_classifier.py` | Classify inbox into action buckets; identify unsubscribes |
| Calendar Prep | `calendar-prep/` | `meeting_prep_briefer.py` | Generate one-page meeting briefings from structured input |
| Investor Update Generator | `investor-update-generator/` | `investor_update_validator.py` | Validate monthly investor update against rubric |
| Pitch Deck Reviewer | `pitch-deck-reviewer/` | `deck_structure_scorer.py` | Score pitch deck structure vs YC/Sequoia/a16z heuristics |
| Weekly Review | `weekly-review/` | `weekly_review_synthesizer.py` | Friday/Sunday review synthesizer (GTD + OKR check-in) |

## Design Notes

- All scripts use the Python standard library only — no `pip install` needed.
- Each script supports both human-readable and `--json` output.
- Each skill follows the standard package layout: `SKILL.md`, `scripts/`, `references/`, `assets/`.
- These skills are deliberately scoped to **single-person workflows**. Team-level workflows belong in `business-growth/`, `sales-success/`, `hr-operations/`, or `finance/`.

## Cross-Domain Integration

| If you need… | Pair with |
|--------------|-----------|
| Sales sequence design after lead qualification | `marketing/cold-email/` |
| Content rewriting for a tailored resume cover letter | `marketing/copywriting/` |
| User-story authoring from customer-interview pains | `product-team/user-story/` |
| Cash-flow forecasting from monthly invoice summaries | `c-level-advisor/cs-cfo-advisor` |
| Brand-narrative work after picking a domain name | `marketing/brand-strategist/` |

## Adding a New Skill to This Domain

1. Create folder `personal-productivity/<skill-name>/`
2. Add `SKILL.md` with frontmatter (name, description, keywords) following an existing skill as template
3. Implement Python tool in `scripts/` — stdlib only, dual JSON + human output
4. Write a knowledge base in `references/`
5. Provide a user-facing template in `assets/`
6. Add a row to the table above
