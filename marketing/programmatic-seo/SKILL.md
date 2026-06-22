---
name: programmatic-seo
description: >
  Programmatic page generation at scale using template-based SEO and data
  pipelines: keyword pattern mining, template architecture, and indexation for
  100-100K+ pages. Use when building SEO pages at scale or scoping a programmatic
  SEO build.
license: MIT + Commons Clause
metadata:
  version: 1.1.0
  author: borghei
  category: marketing-growth
  updated: 2026-06-15
  tags: [seo, programmatic, templates, content-at-scale, data-driven-seo]
---
# Programmatic SEO

Production-grade framework for building SEO page sets at scale. Covers the full lifecycle from keyword pattern discovery through template design, data pipeline construction, quality assurance, and post-launch optimization. Designed for deployments ranging from 50 to 100,000+ pages.

## Core Capabilities

- **Opportunity assessment & playbook selection** — validate demand, rate data sources (Tier S-F), score the competitive moat, then pick from 14 page-set playbooks via the selection matrix and the weighted build-vs-skip decision matrix.
- **Keyword pattern mining** — extract repeating `[variable]` structures, map head/torso/long-tail/zero-volume distribution, and classify search intent.
- **Data pipeline design** — source → extraction → transformation → enrichment → validation → publication, with per-record quality gates and per-data-type update cadence.
- **Template architecture & quality control** — 6-zone page structure, the 3-of-5 uniqueness rule, URL conventions, pre-publication QA, thin-content detection, and hub-and-spoke internal linking.
- **Indexation & optimization** — crawl-budget strategy, tiered indexation priority, IndexNow, phased launch sequence, post-launch metrics dashboard, and anti-pattern / penalty avoidance.

## When to Use

**Use this skill when:**
- You have a repeating keyword pattern with 50+ variations
- You have (or can acquire) structured data to populate pages
- The search intent is consistent across variations
- Your domain has sufficient authority to compete

**Do NOT use when:**
- Each page requires unique editorial content (use content-creator instead)
- Total addressable pages < 30 (manual content is more effective)
- You lack a data source and would be generating thin placeholder content
- Your domain authority is below DR 20 and competitors are DR 60+

## Clarify First

Before scoping the build, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Keyword pattern** — the repeating `[variable]` structure with 50+ variations (drives keyword mining and template variables)
- [ ] **Structured data source** — the dataset that populates pages and its quality tier (drives the data pipeline and the 3-of-5 uniqueness rule; thin-content risk)
- [ ] **Search intent** — whether intent is consistent across all variations (drives playbook selection and template architecture)
- [ ] **Domain authority & scale** — your DR vs competitors and target page count (drives the build-vs-skip decision and indexation strategy)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Quick Start

```bash
# Analyze keyword patterns for pSEO opportunities
python scripts/keyword_pattern_miner.py --keywords keywords.csv --json

# Score page templates for content quality and uniqueness
python scripts/template_scorer.py --template template.html --data sample_data.json

# Validate data quality for pSEO data pipeline
python scripts/data_validator.py --file data.csv --rules rules.json --json
```

## References

Load the reference that matches the phase you are in — keep this file lean and pull detail on demand:

- **[references/strategy-and-playbooks.md](references/strategy-and-playbooks.md)** — initial assessment (opportunity validation, data-source tiers, competitive moat), the 14 playbooks, playbook selection matrix, and the build-vs-skip decision matrix. Read when scoping an opportunity and choosing what to build.
- **[references/keyword-and-data.md](references/keyword-and-data.md)** — keyword pattern identification, volume distribution analysis, intent classification, and the full data pipeline (quality gates, update cadence). Read when mining keywords or designing the data feed.
- **[references/templates-and-quality.md](references/templates-and-quality.md)** — 6-zone page architecture, uniqueness requirements, URL structure, pre-publication QA checklist, thin-content detection, hub-and-spoke linking, and anti-patterns. Read when designing templates and QA gates.
- **[references/launch-and-optimization.md](references/launch-and-optimization.md)** — crawl-budget management, indexation priority, IndexNow, phased launch sequence, post-launch metrics dashboard, troubleshooting table, output artifacts, and success criteria. Read when launching and monitoring the page set.

## Scope & Limitations

**In scope:**
- Keyword pattern mining and volume distribution analysis
- Data pipeline design (source > extraction > transformation > validation > publication)
- Template architecture with uniqueness requirements
- Quality control frameworks including thin content detection
- Hub-and-spoke internal linking for pSEO page sets
- Phased indexation strategy and crawl budget management
- Post-launch optimization and monitoring dashboards

**Out of scope:**
- Individual editorial content creation (use Content Production)
- Data collection or web scraping implementation
- CMS or static site generator setup and configuration
- Server infrastructure for large-scale deployments
- Paid acquisition for pSEO pages
- Legal compliance for data usage rights

**Known limitations:**
- Google's 2026 helpful content system can deindex large page sets retroactively if quality drops below threshold
- Programmatic SEO at Tier F data (public/scraped) carries high penalty risk regardless of template quality
- Engagement metrics (bounce rate, time on page) now influence indexation decisions for pSEO pages
- AI content detection is improving — fully automated content generation without human oversight is increasingly risky
- Travel site case study: 50,000 city-swap pages had 98% deindexed within 3 months (per 2025 industry data)

## Related Skills

- **seo-audit** -- Run after pSEO pages are live to diagnose indexation issues, thin content warnings, or ranking problems across the page set.
- **schema-markup** -- Add structured data to pSEO templates (Product, FAQ, LocalBusiness) for rich snippet eligibility at scale.
- **site-architecture** -- Plan hub-and-spoke structure and crawl budget management for large pSEO deployments (500+ pages).
- **competitor-alternatives** -- Use the Comparisons playbook when building "[X] vs [Y]" pages; competitor-alternatives has dedicated comparison page frameworks.
- **content-creator** -- Use when individual pages in the set need editorial-quality unique content beyond template generation.
