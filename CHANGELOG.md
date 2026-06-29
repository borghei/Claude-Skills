# Changelog

All notable changes to the Claude Skills Library will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [4.10.0] - 2026-06-29 (Cross-platform surface refresh + single-source manifests)

Realigns every assistant-facing surface with the real library (**339 skills · 17 domains · 774 Python tools**) and unifies the machine catalogs behind one generator so they can no longer drift independently.

### Added

- **Cursor Project Rules** — `.cursor/rules/*.mdc` (modern replacement for `.cursorrules`): `repo-overview.mdc` (always-on), `skill-authoring.mdc` (auto-attaches on `**/SKILL.md`), `python-tools.mdc` (auto-attaches on `**/scripts/*.py`).
- **Per-domain Claude Code plugins** — `plugin.json` for the 9 domains that lacked one (legal, data-analytics, hr-operations, sales-success, personal-productivity, documents, vertical-advisors, research, workflow); all 17 domains now install as plugins.
- **`build_manifest.py` now emits every machine catalog from one source** — in addition to `cli/skills.json` and `registry.json`, it regenerates `.gemini/skills-index.json` (was stale at 203) and the website catalog `skills.json` (was stale at 294). Per-skill entries gained `license`, `category`, `subdomain`, and `tools_count`.

### Changed

- **`.claude-plugin/marketplace.json` → v3.0.0** — corrected per-plugin counts and expanded from 8 to all 17 domain plugins.
- **Prose configs refreshed** — `AGENTS.md`, `GEMINI.md`, `.cursorrules`, `.windsurfrules`, `.clinerules`, `.goosehints`, `CLAUDE.md`, `README.md`, `mkdocs.yml`, and `docs/` updated to 339/17/774; removed references to dead directories (`engineering-team/`, `marketing-skill/`).
- **Website regenerated** — all 339 skill pages, 17 domain pages, `llms.txt`, agents/commands catalogs, and sitemap rebuilt from the refreshed catalog.

### Fixed

- Eliminated count drift across platform surfaces (skills had been reported as 204, 294, 312, and 338 in different files; domains as 13, 15, and 16; tools as 559, 681, 730, and 784).

## [4.9.0] - 2026-06-15 (Token efficiency — progressive disclosure)

Behavior-preserving refactor that cuts the per-invocation token cost of the heaviest skills by moving deep content into load-on-demand `references/` files, following the Anthropic Agent Skills three-tier loading model (description always resident → SKILL.md body on trigger → references on demand).

### Changed

**73 token-heavy skills refactored to progressive disclosure.** Oversized `SKILL.md` bodies were slimmed to lean "maps" (overview, core capabilities, when-to-use, and a `## References` section with "read this when…" pointers), with the deep content (frameworks, procedures, tables, code, checklists) moved **verbatim** into `references/` files. No knowledge was dropped — distinctive-content retention was spot-checked across the affected skills.

- **Top 20 cross-domain offenders** (engineering, marketing, ra-qm-team, business-growth, project-management): bodies cut from 5.6K–18.6K to 1.0K–1.8K tokens each; combined per-trigger cost ~155K → ~28K tokens. 70 new reference files.
- **All 53 token-heavy Project Management skills**: PM-domain Tier-2 body cost 226,646 → 91,516 tokens (−60%); every one of the 66 PM skills now uses progressive disclosure (heavy bodies 53 → 0). 69 reference files added/extended.
- Affected skill `metadata.version` bumped and `metadata.updated` set to 2026-06-15; a few oversized always-resident `description` fields tightened to trigger-rich single sentences.

### Added

- **`scripts/skill_token_audit.py`** — stdlib-only tool that scores every skill on the three loading tiers (description / body / references token cost), flags missing progressive disclosure, orphan references, and oversized bodies/descriptions, and emits a refactor-priority worklist (`table`, `summary`, or `json`).

### Fixed

- **Broken reference links** in several PM skills (`program-manager`, `delivery-manager`, `agile-coach`) that pointed at `references/*.md` files which never existed — content is now created and correctly linked.
- **Orphan references** across 11 skills (9 PM + 2 cross-domain) whose `references/` files existed but were never linked from the body — now linked with "read this when…" notes.

### Notes

- `cli/skills.json` and `registry.json` regenerated.
- Token counts are chars/4 estimates used for ranking, not billing.

## [4.7.0] - 2026-05-22 (Tier 3 of PM depth)

### Added

**Output evaluation harness for artifact-generating PM skills (`evals/`).** Deterministic scoring (no LLM) for any markdown artifact, scored 0-100 against the skill's red-flags + success criteria.

Framework:
- `evals/engine.py` — generic check evaluator. 13 supported check types: regex, regex_not, section_present, section_word_count, section_sentence_count, keyword_any, keyword_all, keyword_none, has_table, has_list, url_count, length_in_range, line_count_range.
- `evals/run.py` — runner. Supports `--all`, `--skill <name>`, `--artifact <path>`, `--format markdown|json`, `--threshold <int>`, `--output <file>`.
- `evals/README.md` — framework documentation.

12 rubrics (190+ criteria total, each anchored to a specific red-flag or success-criterion item):
- create-prd · prfaq · ai-feature-prd · brainstorm-okrs · status-update-generator
- post-mortem · north-star-metric · product-vision · pricing-prd
- roadmap-communication · release-notes · customer-feedback-triage

Smoke-test (all 12 worked examples scored against their own rubric):

| Skill | Score |
|---|---|
| ai-feature-prd | 100 |
| customer-feedback-triage | 100 |
| north-star-metric | 100 |
| post-mortem | 100 |
| product-vision | 100 |
| status-update-generator | 100 |
| brainstorm-okrs | 95 |
| pricing-prd | 95 |
| prfaq | 94 |
| roadmap-communication | 94 |
| release-notes | 90 |
| create-prd | 89 |

12/12 pass at threshold 70. High scores reflect that the worked examples were authored as exemplars; the rubrics are calibrated to catch realistic failures (drafts with missing sections, blame language, output-as-KR, watermelon status, etc.).

### Changed

- PM README updated with new "Output evaluation harness" section.

## [4.6.0] - 2026-05-22 (Tier 2 of PM depth)

### Added

**Red-flag / anti-pattern library in every PM skill (54 files, ~12,000 lines).** Each skill now has `references/red-flags.md` with 10-12 concrete anti-patterns, paired bad/good QUOTED artifact snippets, and a "How to catch it" check question. Anchors to canonical authors (Wodtke, Wake, Lawrence, Vacanti, Allspaw, Dekker, Cagan, Klein, Klement, Ellis, McClure, Karpathy, Anthropic RSP, Ramanujam, Westendorp, etc.). Differentiates from generic AI-generated framework summaries.

Highlight red flags:
- status-update-generator: watermelon status (green outside, red inside)
- create-prd: solution-before-problem (Section 7 bloat)
- post-mortem: blame language vs systemic framing
- brainstorm-okrs: output-as-KR, sandbagging, drift mid-quarter
- customer-feedback-triage: squeaky-wheel bias, sales-driven roadmap
- north-star-metric: NSM = revenue (it's not)
- ai-feature-prd: hallucination tolerance hand-waving, no fallback model
- linear-expert: cycle-as-sprint anti-patterns, GraphQL N+1

**Runnable skill-chain pipelines (`pipelines/`).** Five stdlib-only scripts that chain multiple PM skills end-to-end with one command. Each supports `--demo`, `--input <json>`, `--format markdown|json`, `--output <dir>`:
- `feature-end-to-end.py` — discovery → PRD → OKRs → backlog → release (chains 7 skills)
- `weekly-cadence.py` — Jira/Linear adapter → status + flow + dependency (4 skills)
- `customer-discovery.py` — interview-synthesis → assumptions → experiments → NSM (4 skills)
- `post-mortem-flow.py` — post-mortem → pre-mortem follow-ups → dependency-map (3 skills)
- `launch-coordination.py` — beta-program → feature-flag-strategy → launch-playbook → release-notes (4 skills)
- `pipelines/README.md` — when-to-use, inputs/outputs, integration points

Pipelines gracefully degrade — if a downstream skill's tool isn't available, the pipeline stubs that stage and continues, so the chain always completes.

### Changed

- PM README updated with new "Red flags" and "Runnable pipelines" sections.

## [4.5.0] - 2026-05-22 (later)

### Added (Tier 1 of PM depth investment)

**Worked examples in every PM skill (54 files, ~13,000 lines).** Until now, PM skills had frameworks (references/) and blank templates (assets/) but no finished artifact. PMs copy-paste-and-modify; that fails when there's nothing to copy. Now every skill has `examples/<scenario>.md` with a realistic company, the workflow applied, and the full generated artifact. Recurring fictional cast (Acme Analytics, Wayfinder, Northwind, Helix Platform, Pylon) means scenarios cross-reference each other naturally.

Highlight examples:
- `execution/create-prd/examples/shared-dashboards-prd.md` — full 8-section PRD
- `execution/ai-feature-prd/examples/ai-meeting-notes-summarizer.md` — AI PRD with eval spec, guardrails, model fallback
- `execution/post-mortem/examples/payment-processing-outage.md` — blameless RCA for a 47-min outage
- `execution/status-update-generator/examples/acme-search-platform-weekly.md` — Yellow-status weekly exec update
- `execution/activation-funnel/examples/freemium-saas-day-7-retention-diagnosis.md` — AARRR funnel diagnosis
- `discovery/interview-synthesis/examples/wayfinder-8-interview-synthesis.md` — 8 interviews → opportunity tree
- `career/pm-interview-prep/examples/stripe-circles-new-market-product.md` — full CIRCLES answer

**Live data adapters (`tools/adapters/`).** Three stdlib-only scripts that pull from Jira / Linear / Notion APIs and emit JSON in the shapes PM Python tools expect:
- `jira_to_json.py` — Jira REST v3 with JQL; output formats: raw / status-update / cycle-time / dependency-map
- `linear_to_json.py` — Linear GraphQL; output formats: same set
- `notion_to_json.py` — Notion REST query; output formats: raw / prds / okrs / roadmap / feedback

Pipe directly: `jira_to_json.py --format cycle-time | flow_metrics.py --input -`. Auth via env vars (`JIRA_TOKEN`, `LINEAR_API_KEY`, `NOTION_TOKEN`).

**15 PM skills wrapped as MCP tools** in `scripts/mcp_server.py`:
`pm_create_prd`, `pm_status_update`, `pm_funnel_analyze`, `pm_flow_metrics`, `pm_dependency_map`, `pm_feedback_triage`, `pm_nsm_tree`, `pm_refinement_score`, `pm_interview_synthesize`, `pm_prioritize`, `pm_okr_validate`, `pm_roadmap_transform`, `pm_pre_mortem`, `pm_release_notes`, `pm_stakeholder_map`. Each accepts `format` (markdown / json / mermaid / confluence / notion / linear) and `input` (JSON object, JSON string, or file path). Smoke-tested end-to-end through the MCP JSON-RPC interface.

### Changed

- PM README updated with new "Live data adapters" and "MCP tools" sections, plus a Worked-examples highlight table.

## [4.4.0] - 2026-05-22

### Added

**Project Management domain expanded to 54 skills (still the most-used domain).**

- **12 new PM skills:**
  - `discovery/customer-interview-script` — how to RUN a discovery interview (Portigal, Fitzpatrick, Torres, Mom Test)
  - `discovery/value-proposition-canvas` — Strategyzer VPC (Customer Profile + Value Map)
  - `discovery/jtbd-workshop` — full Jobs-To-Be-Done workshop (Christensen, Ulwick, Moesta, Klement)
  - `execution/ai-feature-prd` — PRDs specific to AI/ML features (Karpathy Software 2.0, Anthropic RSP, NIST AI RMF, eval-spec, guardrails, model selection, cost monitoring). Targets the "AI PM" SEO cluster.
  - `execution/activation-funnel` — AARRR funnel design + analyzer (McClure, Ellis activation, Andrew Chen, Balfour Four Fits). Python tool `funnel_analyzer.py` outputs in all 6 SHARED_OUTPUT_SCHEMA formats including Mermaid flowchart with per-arrow conversion %.
  - `execution/feature-flag-strategy` — phased rollouts, kill-switches, flag debt (Fowler 4-category toggle taxonomy: release / experiment / ops / permission)
  - `execution/post-mortem` — blameless incident RCA (Google SRE, Allspaw, Dekker, Perrow). Companion to existing `pre-mortem/`.
  - `execution/customer-feedback-triage` — inbound feedback → cluster → categorize (Kano) → score (RICE + segment) → backlog. Python tool `feedback_triage.py` clusters via Jaccard at 0.12 threshold.
  - `execution/pricing-prd` — pricing experiments and pricing-page PRDs (Ramanujam Monetizing Innovation, Campbell, Van Westendorp PSM, Weinberg)
  - `execution/product-vision` — vision document (Pichler, Moore, Raskin strategic narrative, Cagan, Amazon Working Backwards)
  - `execution/quarterly-planning` — full Q1 cycle (kickoff → mid-Q → close) above OKRs (Wodtke, Cagan, Reforge, RAD ritual)
  - `productboard-expert/` — Productboard administration, Insight inbox triage, Driver scoring, REST API patterns

### Changed

- PM count updated everywhere: 42 → **54**. Library total: 282 → **294** skills, ~700 → **~720+** Python tools.
- PM domain card on `site/index.html` updated with new tags (ai-prd, productboard) and expanded description.
- Skill-count badge on README updated to 294.
- `docs/skills/index.md` Project Management row updated to 54 skills, 70+ tools.
- `docs/skills/project-management.md` retained (count refresh).
- `project-management/CLAUDE.md` skill registry rewritten with corrected numbering (1-54) and new sub-domain breakdown: Role-Based (10), Integrations (3), Discovery (8), Execution (29), Career (4).



### Added

**Project Management domain expanded to 42 skills (most-used domain in the library).**

- **17 new PM skills (wide push, production-ready scaffolds):**
  - `discovery/interview-synthesis` — customer interview → opportunity solution tree (Python tool: 6-format output)
  - `execution/prfaq` — Amazon Working Backwards PR/FAQ as a standalone skill
  - `execution/backlog-refinement` — INVEST + DoR/DoD + splitting playbook (Python tool: refinement scorer)
  - `execution/status-update-generator` — weekly exec status from Jira/Linear data (Python tool: 6-format output)
  - `execution/north-star-metric` — NSM + input metric tree (Python tool: Mermaid tree builder)
  - `execution/roadmap-communication` — exec / customer / internal roadmap variants
  - `execution/beta-program` — closed beta playbook (Kano + cohort design)
  - `execution/launch-playbook` — internal + external launch coordination
  - `execution/cycle-time-analyzer` — flow metrics, CFD, Little's Law (Python tool)
  - `execution/dependency-map` — cross-team dependencies + critical path (Python tool: Mermaid graph LR)
  - `execution/story-splitting` — Lawrence's 9 vertical slicing patterns
  - `career/pm-interview-prep` — APM → Group PM interview prep (CIRCLES, AARM, STAR, Decode and Conquer)
  - `career/pm-career-ladder` — rubrics, gap analysis, growth plan, promo packet
  - `career/pm-onboarding` — 30-60-90 day plan (Watkins + STARS)
  - `career/pm-1on1s` — 1:1 templates by partner type (EM, designer, IC, manager)
  - `linear-expert` — Linear admin, GraphQL queries, Jira → Linear migration
  - `notion-pm` — Notion DBs for PRDs/OKRs/Roadmap/Decisions, REST API patterns
- **`project-management/SHARED_OUTPUT_SCHEMA.md`** — defines `--format json|markdown|mermaid|confluence|notion|linear` convention for all PM Python tools
- **`project-management/examples/feature-end-to-end.md`** — worked scenario showing idea → release notes in 6 commands
- **4 new bundles** in `bundles.json`: `pm-starter-pack` (10 skills), `pm-scrum-master` (8), `pm-discovery-coach` (8), `pm-career-track` (6)

### Changed

- **Project Management bolded as the most-visited domain** in main `README.md`, `docs/SKILLS.md`, and `CLAUDE.md`
- **PM `README.md` rewritten** with hero block, role-based Quick Start (7 roles: APM → CPO), visual gallery, 42-skill catalog
- **PM `CLAUDE.md` rewritten** to cover all 42 skills, shared output schema, Linear/Notion integration patterns, and 6 workflow patterns

### Fixed

- **`scripts/build_manifest.py`** now recurses one level into container folders (e.g., `discovery/`, `execution/`, `career/`) so nested skills appear in the registry. Previously the registry undercounted PM by ~30 nested skills.
- Skill count reconciled across `README.md`, `CLAUDE.md`, `docs/SKILLS.md`, and `project-management/CLAUDE.md` (was inconsistent across 13 / 22 / 25). Authoritative count: **282 total, 42 PM**.

## [4.2.0] - 2026-05-04

### Added

**3 new skill domains (21 new skills total):**

- **`personal-productivity/` — 10 skills:**
  - `resume-tailor` — score resume vs job description, gap analysis, bullet rewrite patterns
  - `lead-researcher` — score leads against ICP, draft signal-led outreach
  - `meeting-insights` — extract decisions, actions, owners, due dates, risks from transcripts
  - `domain-name-brainstormer` — generate and score brand / domain candidates with naming-pattern playbook
  - `invoice-organizer` — categorize receipts, detect duplicates, monthly summary
  - `email-triage` — classify inbox into action buckets (reply now / later / archive / unsubscribe / delete)
  - `calendar-prep` — generate one-page meeting briefings from structured input
  - `investor-update-generator` — validate monthly investor update against rubric (highlights / lowlights / metrics / asks)
  - `pitch-deck-reviewer` — score deck structure against YC / Sequoia / a16z heuristics
  - `weekly-review` — Friday/Sunday weekly review synthesizer (GTD + OKR check-in)

- **`documents/` — 4 skills (stdlib-only OOXML parsing, no `python-docx` / `python-pptx` / `openpyxl` / `pypdf` required):**
  - `docx-toolkit` — audit Word documents (comments, tracked changes, heading hierarchy, style sprawl)
  - `pdf-toolkit` — audit PDFs (metadata leakage, encryption, JavaScript, embedded files)
  - `pptx-toolkit` — audit PowerPoint decks (slide density, hidden slides, speaker notes, animations)
  - `xlsx-toolkit` — audit Excel workbooks (hidden sheets, external links, formula density, named ranges)

- **`vertical-advisors/` — 7 skills (industry-specific strategic advisory, complementing the implementation-focused `ra-qm-team/`):**
  - `fintech` — US/EU regulatory triggers, license-vs-partner playbook, KYC/AML basics, embedded finance patterns
  - `healthtech` — HIPAA scope, FDA SaMD classification, payor/provider/employer GTM patterns, value-based care primer
  - `edtech` — FERPA/COPPA/state student-data laws, K-12 vs higher ed vs corporate L&D market dynamics
  - `ecommerce` — unit economics, fulfillment models (DTC self / 3PL / FBA / dropship / retail), channel strategy
  - `proptech` — segments (transaction / listings / financing / management / services / data), MLS / brokerage, RESPA / fair housing
  - `climate-tech` — climate categories, GHG accounting (Scope 1/2/3), funding stack (DOE / IRA / VC / project finance)
  - `marketplace` — chicken-and-egg strategies, take-rate design, liquidity / network effects

**41 new `cs-*` agents (32 → 67 total cs-* agents, plus 7 personas = 74 total agents):**

- **Engineering specialists (21 new):** mobile-engineer, sre-engineer, platform-engineer, mlops-engineer, llm-architect, prompt-engineer, mcp-developer, data-engineer, pen-tester, qa-automation-lead, accessibility-engineer, computer-vision-engineer, data-scientist, frontend-engineer, backend-engineer, fullstack-engineer, cloud-architect, devops-engineer, secops-engineer, release-manager, database-engineer
- **C-Level expansion (9 new):** coo-advisor, chro-advisor, cro-advisor, cpo-advisor, chief-of-staff, ma-advisor, board-secretary, fundraising-advisor, investor-relations
- **Marketing (4 new):** developer-advocate, pr-comms-lead, community-manager, event-marketing-manager
- **Business Growth (3 new):** customer-experience-lead, partnership-manager, competitive-intel-analyst
- **HR (2 new):** talent-acquisition, people-ops-lead
- **Product (2 new):** ux-researcher, learning-designer
- **Vertical Advisors (7 new — new domain):** fintech-advisor, healthtech-advisor, edtech-strategist, ecommerce-strategist, proptech-advisor, climate-tech-advisor, marketplace-advisor

**21+ new Python tools** including: `regulatory_trigger_checker.py`, `phi_scope_checker.py`, `student_data_compliance_checker.py`, `ecom_unit_economics_calculator.py`, `market_segment_classifier.py`, `carbon_impact_estimator.py`, `marketplace_health_scorer.py`, `docx_auditor.py`, `pdf_auditor.py`, `pptx_auditor.py`, `xlsx_auditor.py`, `email_classifier.py`, `meeting_prep_briefer.py`, `investor_update_validator.py`, `deck_structure_scorer.py`, `weekly_review_synthesizer.py`, plus 5 personal-productivity tools (`resume_matcher.py`, `lead_qualifier.py`, `transcript_analyzer.py`, `name_generator.py`, `invoice_categorizer.py`).

### Changed

- `README.md` — updated headline numbers, badges, domain index
- `CLAUDE.md` (root) — updated Navigation Map and repository structure
- `mkdocs.yml` — updated site description, author updated to Amin Borghei
- `site/index.html` — updated meta tags, hero stats, added 3 new domain cards

### Verification

- All 41 new agent path references verified to resolve (226+ `../../` references across new agents, 0 missing)
- All 21+ new Python tools smoke-tested with sample inputs
- All scripts use stdlib only (no new pip dependencies)
- All scripts support both human-readable and `--json` output

### Meta

- Version: 4.1.1 → 4.2.0 (minor — additive: 3 new domains, 41 new agents, no breaking changes)

## [4.1.1] - 2026-04-21

### Changed

- Adopted the Skill Authoring Standard sections (`Use when`, phase-level validation checkpoints, and `Anti-patterns` tables) across 5 high-traffic skills for more reliable activation and tighter failure-mode coverage:
  - `engineering/focused-fix` -- Added Use-when triggers, per-step validation in the Focused Bugfix Workflow, and 6 anti-patterns covering scope creep, symptom fixes, and dependency bundling
  - `business-growth/pricing-strategy` -- Added Use-when triggers, mode-level validation (Design / Optimize / Price Increase), and 8 anti-patterns covering value-metric sequencing, tier sprawl, and grandfathering
  - `business-growth/referral-program` -- Added Use-when triggers, stage-level validation across the 4-stage referral loop, and 8 anti-patterns covering trigger timing, reward sizing, and K-factor misuse
  - `finance/financial-analyst` -- Added Use-when triggers, phase-level validation across the 5-phase workflow, and 8 anti-patterns covering DCF scenarios, terminal growth caps, WACC staleness, and materiality filtering
  - `project-management/senior-pm` -- Added Use-when triggers, weekly-review validation checkpoints, and 9 anti-patterns covering RAG calibration, portfolio-level decisioning, and quarterly rebalancing cadence
- Additive-only edits: no frontmatter, existing content, or script behavior changed

### Fixed

- `finance/financial-analyst/SKILL.md` -- Corrected broken reference link in anti-patterns table (pointed to non-existent `references/industry-adaptations.md`; now points to industry benchmarks in `references/financial-ratios-guide.md`)

### Docs

- `README.md` -- Added @rohan-tessl (Tessl) to the Contributors table

### Meta

- Version: 4.1.0 → 4.1.1 (patch — content-only improvement, no scripts or frontmatter touched)

## [4.1.0] - 2026-04-10

### Added

**New Domain: Legal (17 skills, EXPERIMENTAL):**

> All legal skills are experimental and provided for educational/informational purposes only. They do NOT constitute legal advice. The entire responsibility for usage rests with the user.

- Contract Analysis: `contract-review`, `nda-triage`, `nda-review`, `tech-contract-negotiation`
- Privacy & Data Protection: `privacy-compliance`, `dpia-assessment`, `data-breach-response`, `privacy-notice-generator`
- Risk & Compliance: `legal-risk-assessment`, `vendor-due-diligence`, `whistleblower-compliance`
- Legal Methodology: `statute-analysis`, `mediation-analysis`, `legal-red-team`
- Legal Operations: `legal-canned-responses`, `legal-meeting-briefing`, `tabular-document-review`

**Python Tools (33 new):**
- `contract_analyzer.py`, `redline_generator.py`, `nda_screener.py`, `nda_checklist.py`, `nda_clause_reviewer.py`
- `negotiation_position_analyzer.py`, `deal_complexity_scorer.py`, `vendor_risk_scorer.py`, `vendor_comparison.py`
- `privacy_regulation_checker.py`, `dsr_tracker.py`, `dpia_threshold_checker.py`, `dpia_risk_register.py`
- `breach_severity_calculator.py`, `breach_timeline_tracker.py`, `privacy_notice_scaffolder.py`, `notice_compliance_checker.py`
- `risk_scorer.py`, `risk_report_generator.py`, `statute_keyword_analyzer.py`, `requirement_classifier.py`
- `dispute_analyzer.py`, `settlement_calculator.py`, `legal_fact_checker.py`, `legal_quality_scorer.py`
- `whistleblower_compliance_checker.py`, `whistleblower_policy_scaffolder.py`, `response_generator.py`, `escalation_detector.py`
- `meeting_brief_generator.py`, `action_item_tracker.py`, `document_discovery.py`, `extraction_aggregator.py`

**Reference Guides (37 new):**
- Contract law, NDA screening criteria, clause analysis, negotiation playbooks, regulatory leverage
- Global privacy regulations (9 frameworks), DPA review checklists, DSR handling, jurisdiction requirements
- EDPB criteria, ENISA breach methodology, notification obligations, risk scoring methodology
- Canons of construction, mediation process, negotiation concepts, hallucination patterns
- Vendor risk framework, regulatory checklists (8 frameworks), monitoring framework
- Whistleblower regulatory framework, assessment checklists, response templates, escalation triggers

**New PM Execution Skills (3):**
- `daci-framework` -- DACI decision facilitation and governance (Driver/Approver/Contributor/Informed)
- `eol-communication` -- End-of-life product messaging and sunset communication framework
- `story-mapping` -- Jeff Patton user story mapping for journey visualization and release planning

**Documentation:**
- `legal/CLAUDE.md` -- Domain guidance with experimental disclaimer
- `docs/skills/legal.md` -- Website catalog page for legal domain
- Updated skills index, skills.json catalog, root CLAUDE.md

### Enhanced

**Product & PM Skill Upgrades (6 skills enhanced):**
- `job-stories` -- Added full JTBD Discovery Canvas (Customer Jobs, Pains, Gains) with canvas-to-story mapping workflow
- `agile-product-owner` -- Added 8-rule story splitting decision logic (Humanizing Work methodology) with split output format and Tiny Acts of Discovery
- `ux-researcher-designer` -- Added proto-persona canvas template; enhanced journey mapping with happy/fail/difficult paths, KPIs per stage, friction analysis and intervention prioritization
- `create-prd` -- Added Problem Framing Canvas (I am/Trying to/But/Because/Feel) and Amazon Working Backwards Press Release as pre-PRD techniques
- `product-manager-toolkit` -- Added Geoffrey Moore positioning statement framework and Recommendation Canvas for product opportunity evaluation
- `product-strategist` -- Added PESTEL macro-environment analysis framework and TAM-SAM-SOM market sizing methodology

### Changed

- Total skill count: 225 → 245 (across 14 domains, up from 13)
- PM execution skills: 8 → 11 (+3 new)
- Total Python tools: 613 → 653
- Total reference guides: 280+ → 317+
- Version: 4.0.0 → 4.1.0

## [4.0.0] - 2026-04-02

### Added

**New Skills (21):**
- Engineering: `docker-development`, `terraform-patterns`, `helm-chart-builder`, `a11y-audit`, `sql-database-assistant`, `threat-detection`, `google-workspace-cli`, `ai-security`, `browser-automation`, `focused-fix`, `llm-cost-optimizer`, `prompt-governance`, `secrets-vault-manager`, `red-team`, `snowflake-development`, `agenthub`
- Finance: `saas-metrics-coach`, `business-investment-advisor`
- Marketing: `video-content-strategist`, `x-twitter-growth`, `ab-test-setup`

**Cross-Domain Personas (7):**
- `startup-cto`, `growth-marketer`, `solo-founder`, `content-strategist`, `devops-engineer`, `finance-lead`, `product-manager`
- Located in `agents/personas/`, usable via `/persona` slash command

**Slash Commands (21 new):**
- `a11y-audit`, `changelog`, `code-to-prd`, `competitive-matrix`, `financial-health`, `focused-fix`, `okr`, `persona`, `pipeline`, `plugin-audit`, `project-health`, `retro`, `rice`, `saas-health`, `security-scan`, `seo-auditor`, `sprint-health`, `sprint-plan`, `tdd`, `tech-debt`, `user-story`

**Compound Sub-Skill Systems (3 systems, 21 sub-skills):**
- Playwright Pro -- advanced browser automation patterns and debugging
- Self-Improving Agent -- agents that evaluate and improve their own performance
- AgentHub -- multi-agent orchestration, tool schemas, communication protocols

**Platform Support:**
- Gemini CLI native support (`.gemini/` directory, `GEMINI.md`, install script)

**CI/CD Workflows (5 new):**
- `enforce-pr-target.yml` -- enforce PR target branch rules
- `skill-security-audit.yml` -- automated skill package security scanning
- `claude-code-review.yml` -- AI-powered code review on PRs
- `virustotal-scan.yml` -- VirusTotal integration for release artifacts
- `sync-codex-skills.yml` -- sync skills to Codex-compatible format

**Standards (2 new):**
- Orchestration Protocol -- 4 multi-agent patterns (sequential, parallel, supervisor, consensus)
- Skill Authoring Standard -- 10 formal patterns for skill creation

**Infrastructure & Tooling:**
- MCP server for skills (`scripts/mcp_server.py`)
- CLI tool (`scripts/cs.py`) with `search`, `install`, `list`, `stats`, `doctor`, `bundle` commands
- Skill quality scoring system (`scripts/skill_quality_scorer.py`)
- Integration test runner (`scripts/integration_test_runner.py`)
- Skill scaffolder (`scripts/create_skill.py`)
- Skill relationship graph generator (`scripts/skill_graph.py`)
- Starter bundles for 8 roles (`bundles.json`)
- Sample data/fixtures for 10 key skills
- MkDocs Material documentation site
- `CONTRIBUTING.md` guide

### Changed
- Quality audit: 7 bloated engineering skills reduced by 67-78% (token savings)
- Quality audit: 15 mid-range engineering skills refined (trigger clauses, agent voice, anti-patterns)
- `CLAUDE.md` updated to v4.0.0 with new stats and structure
- `skills.json` updated with 21 new skill entries
- Repository structure expanded with `.gemini/`, `agents/personas/`, `docs/`
- `README.md` fully rewritten with modern structure

### Stats
- Skills: 204 -> 225 (+21)
- Python tools: 559 -> 613 (+54)
- Agents: 17 -> 32 (+15, including 7 personas)
- Slash commands: 5 -> 26 (+21)
- CI/CD workflows: 1 -> 6 (+5)
- Standards: 5 -> 7 (+2)
- Platform support: 10 -> 11 (+Gemini CLI)

---

## [2.1.0] - 2026-03-18

### Added

**New Skills (5):**
- `qa-browser-automation` — 11-phase browser QA protocol with health scoring (0-100, 10 weighted categories), WCAG accessibility auditing, visual regression tracking, safety controls (50-fix cap, risk accumulator, revert protocol), and 4 Python tools
- `release-orchestrator` — End-to-end release pipeline with pre-flight checks (secret scanning, branch sync, conventional commits), semantic versioning, changelog generation, GO/CONDITIONAL/NO-GO readiness scoring, and 4 Python tools
- `doc-drift-detector` — Documentation drift analysis with staleness scoring (0-100, 5 dimensions), API doc validation via Python AST, link integrity auditing, auto-fix classification, and 4 Python tools
- `sprint-retrospective` — Data-driven sprint retrospectives with velocity analytics, contributor insights (specialization detection, session analysis), code churn analysis (hotspots, oscillation detection), trend tracking, and 4 Python tools
- `design-auditor` — 12-category design audit with AI slop detection (11 pattern types, confidence scoring), WCAG color contrast checking, design system token validation, 3 independent grades (Design/AI Slop/Accessibility), and 4 Python tools

**Python Tools (20 new):**
- `qa_health_scorer.py` — 10-category weighted QA scoring with baseline persistence and trend tracking
- `accessibility_auditor.py` — WCAG 2.1 HTML analysis with 12 automated checks (A/AA/AAA levels)
- `visual_regression_tracker.py` — SHA-256 baseline management with configurable change thresholds
- `test_report_generator.py` — Markdown/JSON QA report generation with executive summaries
- `preflight_checker.py` — 7-check release validation (secrets, branch sync, commits, conflicts)
- `changelog_generator.py` — Conventional commit parsing with Keep a Changelog format output
- `version_bumper.py` — Multi-file semver management (package.json, pyproject.toml, Cargo.toml, etc.)
- `release_readiness_scorer.py` — 7-category deployment readiness with GO/NO-GO decisions
- `drift_analyzer.py` — Git-based doc-code drift detection with 5 drift categories
- `doc_staleness_scorer.py` — Documentation freshness scoring across 5 weighted dimensions
- `api_doc_validator.py` — Python AST-based API doc validation (signatures, parameters, deprecations)
- `link_checker.py` — Markdown link validation (files, anchors, cross-document references)
- `velocity_analyzer.py` — Git velocity metrics with session detection and hourly distribution
- `contributor_insights.py` — Per-contributor analysis with specialization detection and bus factor
- `code_churn_analyzer.py` — File hotspot scoring, oscillation detection, refactoring candidates
- `retro_report_generator.py` — Publication-ready retro reports with tweetable summaries
- `design_scorer.py` — 12-category weighted design scoring with 3 independent grades (A-F)
- `ai_slop_detector.py` — HTML/CSS pattern analysis for AI-generated UI detection
- `color_contrast_checker.py` — WCAG AA/AAA contrast validation with fix suggestions
- `design_system_validator.py` — CSS-to-token compliance checking with deviation reporting

### Changed
- Repository total: 199 → 204 skills, 210 → 230+ Python tools
- Engineering Team: 24 → 28 skills (4 new)
- Project Management: 22 → 23 skills (1 new)

---

## [Unreleased] - 2026-02-27

### Added

**New Skills (3):**
- `claude-code-mastery` — Claude Code expert skill with skill scaffolder, CLAUDE.md optimizer, context analyzer (3 Python tools + 3 references + 2 templates)
- `codex-cli-specialist` — Cross-platform skill authoring for Codex CLI with converter, validator, index builder (3 Python tools + 2 references + 1 template)
- `devops-workflow-engineer` — CI/CD pipeline design with workflow generator, pipeline analyzer, deployment planner (3 Python tools + 3 references + 2 templates)

**Claude Code Subagents (6):**
- `code-reviewer` — Automated code review for quality, security, performance, and best practices
- `doc-generator` — Documentation generation from source code analysis
- `qa-engineer` — Test coverage analysis, bug hunting, and quality metrics
- `changelog-manager` — Changelog generation from git history following Keep a Changelog format
- `security-auditor` — OWASP Top 10 security audits, secrets scanning, and vulnerability detection
- `git-workflow` — Git workflow management with conventional commits and branch protection

**GitHub Workflows (5):**
- `documentation-check.yml` — YAML frontmatter validation, internal link checking, skill inventory
- `qa-validation.yml` — Python syntax check, flake8 lint, bandit security scan, CLI standards
- `changelog-enforcer.yml` — Changelog update enforcement for PRs to main, format validation
- `skill-validation.yml` — Skill package structure validation, cross-reference checking, quality report
- `release-drafter.yml` — Automated release notes generation with skill counts and domain breakdown

**Skill Installer & Auto-Update:**
- `scripts/skill-installer.py` — CLI tool for per-skill installation with one-per-group policy, auto-update support, and multi-agent targeting (Claude, Cursor, VS Code, Codex, Goose)
- `skill-auto-update.yml` — GitHub Action for automated skill update detection and notification

**Infrastructure:**
- YAML frontmatter added to all 12 engineering/ POWERFUL-tier skills
- Domain CLAUDE.md files for data-analytics, hr-operations, sales-success
- Mobile skill upgraded with 3 Python tools and 3 reference guides
- Senior DevOps skill completely rewritten with comprehensive content

**Previous Release Content:**
- **incident-commander** (POWERFUL tier) — Incident response playbook with severity classifier, timeline reconstructor, and PIR generator
- **tech-debt-tracker** (POWERFUL tier) — Codebase debt scanner with AST parsing, debt prioritizer, and trend dashboard
- **api-design-reviewer** (POWERFUL tier) — REST API linter, breaking change detector, and API design scorecard
- **interview-system-designer** (POWERFUL tier) — Interview loop designer, question bank generator, and hiring calibrator
- **migration-architect** (POWERFUL tier) — Migration planner, compatibility checker, and rollback generator
- **observability-designer** (POWERFUL tier) — SLO designer, alert optimizer, and dashboard generator
- **dependency-auditor** (POWERFUL tier) — Multi-language dependency scanner, license compliance checker, and upgrade planner
- **release-manager** (POWERFUL tier) — Automated changelog generator, semantic version bumper, and release readiness checker
- **database-designer** (POWERFUL tier) — Schema analyzer with ERD generation, index optimizer, and migration generator
- **rag-architect** (POWERFUL tier) — RAG pipeline builder, chunking optimizer, and retrieval evaluator
- **agent-designer** (POWERFUL tier) — Multi-agent architect, tool schema generator, and agent performance evaluator
- **skill-tester** (POWERFUL tier) — Meta-skill validator, script tester, and quality scorer
- `campaign-analytics` - Multi-touch attribution, funnel conversion, campaign ROI (3 Python tools)
- `customer-success-manager` - Onboarding, retention, expansion, health scoring (2 Python tools)
- `sales-engineer` - Technical sales, solution design, RFP responses (2 Python tools)
- `revenue-operations` - Pipeline analytics, forecasting, process optimization (2 Python tools)
- `financial-analyst` - DCF valuation, budgeting, forecasting, financial modeling (3 Python tools)
- New `business-growth` domain with 3 skills
- New `finance` domain with 1 skill

### Changed
- Senior DevOps skill completely rewritten with expert-level Docker, Kubernetes, CI/CD, IaC, and monitoring content
- Senior Mobile skill upgraded from stub to production-ready with scripts and references
- All SKILL.md files now have YAML frontmatter (100% coverage)
- Repository now has 97 skills, 178 Python tools, 6 subagents, 12 CI/CD workflows
- INSTALLATION.md updated with Skill Installer CLI docs, auto-update guide, and accurate counts

### Fixed
- CI workflows (smart-sync.yml, pr-issue-auto-close.yml) — PR #193
- Installation documentation (Issue #189) — PR #193

---

## [1.0.0] - 2025-10-21

### Added - Complete Initial Release

**42 Production-Ready Skills across 6 Domains:**

#### Marketing Skills (3)
- `content-creator` - Brand voice analyzer, SEO optimizer, content frameworks
- `marketing-demand-acquisition` - Demand gen, paid media, CAC calculator
- `marketing-strategy-pmm` - Positioning, GTM, competitive intelligence

#### C-Level Advisory (2)
- `ceo-advisor` - Strategy analyzer, financial scenario modeling, board governance
- `cto-advisor` - Tech debt analyzer, team scaling calculator, engineering metrics

#### Product Team (5)
- `product-manager-toolkit` - RICE prioritizer, interview analyzer, PRD templates
- `agile-product-owner` - User story generator, sprint planning
- `product-strategist` - OKR cascade generator, strategic planning
- `ux-researcher-designer` - Persona generator, user research
- `ui-design-system` - Design token generator, component architecture

#### Project Management (6)
- `senior-pm` - Portfolio management, stakeholder alignment
- `scrum-master` - Sprint ceremonies, agile coaching
- `jira-expert` - JQL mastery, configuration, dashboards
- `confluence-expert` - Knowledge management, documentation
- `atlassian-admin` - System administration, security
- `atlassian-templates` - Template design, 15+ ready templates

#### Engineering - Core (9)
- `senior-architect` - Architecture diagrams, dependency analysis, ADRs
- `senior-frontend` - React components, bundle optimization
- `senior-backend` - API scaffolder, database migrations, load testing
- `senior-fullstack` - Project scaffolder, code quality analyzer
- `senior-qa` - Test suite generator, coverage analyzer, E2E tests
- `senior-devops` - CI/CD pipelines, Terraform, deployment automation
- `senior-secops` - Security scanner, vulnerability assessment, compliance
- `code-reviewer` - PR analyzer, code quality checker
- `senior-security` - Threat modeling, security audits, pentesting

#### Engineering - AI/ML/Data (5)
- `senior-data-scientist` - Experiment designer, feature engineering, statistical analysis
- `senior-data-engineer` - Pipeline orchestrator, data quality validator, ETL
- `senior-ml-engineer` - Model deployment, MLOps setup, RAG system builder
- `senior-prompt-engineer` - Prompt optimizer, RAG evaluator, agent orchestrator
- `senior-computer-vision` - Vision model trainer, inference optimizer, video processor

#### Regulatory Affairs & Quality Management (12)
- `regulatory-affairs-head` - Regulatory pathway analyzer, submission tracking
- `quality-manager-qmr` - QMS effectiveness monitor, compliance dashboards
- `quality-manager-qms-iso13485` - QMS compliance checker, design control tracker
- `capa-officer` - CAPA tracker, root cause analyzer, trend analysis
- `quality-documentation-manager` - Document version control, technical file builder
- `risk-management-specialist` - Risk register manager, FMEA calculator
- `information-security-manager-iso27001` - ISMS compliance, security risk assessment
- `mdr-745-specialist` - MDR compliance checker, UDI generator
- `fda-consultant-specialist` - FDA submission packager, QSR compliance
- `qms-audit-expert` - Audit planner, finding tracker
- `isms-audit-expert` - ISMS audit planner, security controls assessor
- `gdpr-dsgvo-expert` - GDPR compliance checker, DPIA generator

### Documentation
- Comprehensive README.md with all 42 skills
- Domain-specific README files (6 domains)
- CLAUDE.md development guide
- Installation and usage guides
- Real-world scenario walkthroughs

### Automation
- 97 Python CLI tools (20+ verified production-ready)
- 90+ comprehensive reference guides
- Atlassian MCP Server integration

### ROI Impact
- $20.8M annual value per organization
- 1,720 hours/month time savings
- 70%+ productivity improvements

---

## [1.0.1] - 2025-10-21

### Added
- GitHub Star History chart to README.md
- Professional repository presentation

### Changed
- README.md table of contents anchor links fixed
- Project management folder reorganized (packaged-skills/ structure)

---

## [1.1.0] - 2025-10-21 - Anthropic Best Practices Refactoring

### Changed - Marketing & C-Level Skills (Phase 1 of 4)

**Enhanced with Anthropic Agent Skills Specification:**

**Marketing Skills (3 skills):**
- Added professional metadata (license, version, category, domain)
- Added keywords sections for better discovery
- Enhanced descriptions with explicit triggers
- Added python-tools and tech-stack documentation

**C-Level Skills (2 skills):**
- Added professional metadata with frameworks
- Added keywords sections (20+ keywords per skill)
- Enhanced descriptions for better Claude activation
- Added technical and strategic terminology

### Added
- `documentation/implementation/SKILLS_REFACTORING_PLAN.md` - Complete 4-phase refactoring roadmap
- `documentation/PYTHON_TOOLS_AUDIT.md` - Comprehensive tools quality assessment

**Refactoring Progress:** 5/42 skills complete (12%)

---

## [1.0.2] - 2025-10-21

### Added
- `LICENSE` file - Official MIT License
- `CONTRIBUTING.md` - Contribution guidelines and standards
- `CODE_OF_CONDUCT.md` - Community standards (Contributor Covenant 2.0)
- `SECURITY.md` - Security policy and vulnerability reporting
- `CHANGELOG.md` - This file, version history tracking

### Documentation
- Complete GitHub repository setup for open source
- Professional community health files
- Clear contribution process
- Security vulnerability handling

---

## Version History Summary

| Version | Date | Key Changes |
|---------|------|-------------|
| 4.1.0 | 2026-04-10 | 245 skills, 17 legal skills, 3 new PM skills, 6 enhanced product/PM skills, 33 new Python tools |
| 4.0.0 | 2026-04-02 | 225 skills, 21 new skills, 7 personas, 26 slash commands, MCP server, Gemini CLI support |
| 2.1.0 | 2026-03-18 | 204 skills, 5 new skills (QA, release, doc-drift, retro, design), 20 new Python tools |
| 2.0.0 | 2026-02-27 | 97+ skills, 6 subagents, 11 workflows, 3 new skills, 170+ Python tools |
| 1.1.0 | 2025-10-21 | Anthropic best practices refactoring (5 skills) |
| 1.0.2 | 2025-10-21 | GitHub repository pages (LICENSE, CONTRIBUTING, etc.) |
| 1.0.1 | 2025-10-21 | Star History, link fixes |
| 1.0.0 | 2025-10-21 | Initial release - 42 skills, 6 domains |

---

## Upcoming Releases

### v5.0.0 (Planned - Q3 2026)
- 250+ skills target
- Blockchain, web3 specializations
- Advanced analytics and ML pipeline skills
- Plugin marketplace and skill registry
- Cross-platform agent orchestration improvements

---

## Notes

**Semantic Versioning:**
- **Major (x.0.0):** Breaking changes, major new domains
- **Minor (1.x.0):** New skills, significant enhancements
- **Patch (1.0.x):** Bug fixes, documentation updates, minor improvements

**Contributors:**
All contributors will be credited in release notes for their specific contributions.

---

[Unreleased]: https://github.com/borghei/Claude-Skills/compare/v4.0.0...HEAD
[4.0.0]: https://github.com/borghei/Claude-Skills/compare/v2.1.0...v4.0.0
[2.1.0]: https://github.com/borghei/Claude-Skills/compare/v2.0.0...v2.1.0
[1.1.0]: https://github.com/borghei/Claude-Skills/compare/v1.0.1...v1.1.0
[1.0.2]: https://github.com/borghei/Claude-Skills/compare/v1.0.1...v1.0.2
[1.0.1]: https://github.com/borghei/Claude-Skills/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/borghei/Claude-Skills/releases/tag/v1.0.0
