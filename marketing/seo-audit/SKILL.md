---
name: seo-audit
description: >
  Technical SEO auditing covering crawlability, indexation, Core Web Vitals,
  on-page optimization, and competitive gaps, with an 85-point checklist and
  remediation plans. Use when auditing technical SEO or diagnosing indexation
  issues.
license: MIT + Commons Clause
metadata:
  version: 1.1.0
  author: borghei
  category: marketing-growth
  updated: 2026-06-15
  tags:
    - seo
    - audit
    - technical-seo
    - core-web-vitals
    - indexation
    - crawl-analysis
---
# SEO Audit

Production-grade SEO audit framework with an 85-point checklist across 8 dimensions, severity-weighted scoring, automated diagnostic workflows, and prioritized remediation plans. Covers technical SEO, on-page optimization, content quality, competitive positioning, and migration readiness.

## Core Capabilities

- **85-point checklist across 8 dimensions** — crawlability, indexation, Core Web Vitals, on-page, content quality, infrastructure, off-page, analytics
- **Severity-weighted scoring** — Critical/High/Medium/Low multipliers roll up to an A–F health grade
- **Diagnostic deep dives** — CWV optimization stacks, indexation gap analysis, traffic-drop decision tree, cannibalization & intent matching, E-E-A-T and AI-content detection
- **Competitive gap analysis** — your site vs. 3 competitors across technical and content dimensions
- **Prioritized remediation** — P0–P4 priority framework, fix-list template, and migration checklists

## When to Use

Pick the operating mode that matches the situation:

- **Full Site Audit** — comprehensive audit across all 8 dimensions; use for initial assessment or annual reviews.
- **Focused Audit** — single-dimension deep dive when the problem area is already identified (e.g., failing Core Web Vitals, indexation issues).
- **Pre-Migration Audit** — for planned URL changes, platform switches, or redesigns; establishes baseline and redirect mapping.
- **Traffic Drop Diagnosis** — emergency diagnostic when organic traffic drops; follows the traffic-drop decision tree to isolate cause.

## Clarify First

Before auditing, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Audit mode** — full site, single-dimension focused, pre-migration, or traffic-drop diagnosis — sets scope and which of the 8 dimensions to run
- [ ] **Site URL + available data** — GSC, analytics, and crawl exports on hand — determines what can be verified vs. assumed in the findings
- [ ] **Primary symptom or goal** — e.g. ranking drop, indexation gap, failing Core Web Vitals — focuses the diagnostic deep-dives and remediation priority
- [ ] **Competitor set** — the 3 sites to benchmark against — drives the competitive gap analysis

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Quick Start

```bash
# Check redirect chains and status codes
python scripts/redirect_checker.py --url https://example.com/old-page --json

# Analyze XML sitemap for errors
python scripts/sitemap_analyzer.py --sitemap https://example.com/sitemap.xml

# Score content quality for SEO
python scripts/content_scorer.py article.md --json
```

## References

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/audit-checklist.md](references/audit-checklist.md)** — initial scoping questions, the full 85-point checklist across all 8 dimensions, and the severity-weighted scoring formula. Read when starting an audit or scoring results.
- **[references/diagnostics-and-analysis.md](references/diagnostics-and-analysis.md)** — Core Web Vitals optimization stacks, indexation gap analysis, traffic-drop decision tree, cannibalization/intent scoring, AI-content & E-E-A-T detection, competitive gap framework. Read when diagnosing a specific problem area.
- **[references/remediation-and-migration.md](references/remediation-and-migration.md)** — migration checklist (pre/during/post), P0–P4 remediation framework and plan template, output artifacts, troubleshooting table, and success criteria. Read when turning findings into an action plan.

## Scope & Limitations

**In scope:** technical SEO across all 8 audit dimensions, severity-weighted scoring with prioritized remediation, traffic-drop diagnosis, competitive gap analysis, pre/post-migration checklists, AI content quality detection.

**Out of scope:** content creation or rewriting (use Content Creator), structured data implementation (use Schema Markup), site architecture redesign (use Site Architecture), link building execution, paid search audits, server/CDN provisioning.

**Known limitations:** field CWV data requires sufficient traffic for CrUX; off-page signals need third-party tools (Ahrefs, SEMrush); AI Overview impact on CTR varies by query type; Google's algorithm changes 500–600 times/year, so findings are point-in-time.

## Integration Points

- **AI SEO** — run after audit to optimize for AI search citation alongside traditional findings.
- **Schema Markup** — use when audit reveals missing or broken structured data opportunities.
- **Site Architecture** — use when audit uncovers structural issues requiring architectural redesign.
- **Content Humanizer** — use when audit flags AI content detection signals on key pages.
- **Content Strategy / programmatic-seo** — use when audit reveals content gaps or keyword-gap clusters addressable at scale.
