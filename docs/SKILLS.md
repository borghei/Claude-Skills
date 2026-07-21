# Skills Reference

Complete reference for **368 skills across 20 domains**. Each skill is a self-contained package with documentation (`SKILL.md`), Python CLI tools (`scripts/`), knowledge bases (`references/`), and user templates (`assets/`).

> **Note:** The per-domain tables below are the canonical listing and are generated against `cli/skills.json`. The dated *Additions* sections that follow are a historical changelog — the skills they mention also appear in their domain table.

---

## Jul 2026 Additions (25 new skills, 3 new domains)

Three new domains plus fill-in across engineering, PM, productivity, marketing, data and finance.

### Business Operations — NEW DOMAIN (+6)
- [capacity-planner](../business-operations/capacity-planner/SKILL.md) — Effective capacity from raw headcount; hire/contract/defer scenarios (3 tools)
- [process-mapper](../business-operations/process-mapper/SKILL.md) — SIPOC + swimlane capture, cycle-time and bottleneck analysis (3 tools)
- [vendor-management](../business-operations/vendor-management/SKILL.md) — Selection scorecards, risk tiering, renewal tracking (3 tools)
- [internal-comms](../business-operations/internal-comms/SKILL.md) — Sequence and pressure-test internal announcements (3 tools)
- [knowledge-ops](../business-operations/knowledge-ops/SKILL.md) — Wiki staleness, ownership gaps, orphans, findability (3 tools)
- [procurement-optimizer](../business-operations/procurement-optimizer/SKILL.md) — Seat utilisation, redundant tools, renewal leverage (3 tools)

### Research Ops — NEW DOMAIN (+4)
- [market-research](../research-ops/market-research/SKILL.md) — TAM/SAM/SOM reconciled top-down and bottom-up (3 tools)
- [product-research](../research-ops/product-research/SKILL.md) — Method selection, recruiting, interview guides, evidence scoring (3 tools)
- [clinical-research](../research-ops/clinical-research/SKILL.md) — Protocol structure, endpoints, power planning, site feasibility (5 tools)
- [research-finance](../research-ops/research-finance/SKILL.md) — Study budgets, cost per insight, burn against milestones (3 tools)

### Markdown-HTML — NEW DOMAIN (+4)
- [md-document](../markdown-html/md-document/SKILL.md) — Markdown → self-contained HTML report with TOC and cross-refs (4 tools)
- [md-slides](../markdown-html/md-slides/SKILL.md) — Markdown → HTML deck with speaker notes and density linter (4 tools)
- [md-review](../markdown-html/md-review/SKILL.md) — Pre-publication gate: structure, links, readability, a11y (3 tools)
- [design-system](../markdown-html/design-system/SKILL.md) — Design tokens, light/dark theming, WCAG contrast validation (3 tools)

### Fill-in across existing domains (+11)
- Engineering: [code-tour](../engineering/code-tour/SKILL.md), [spec-driven-workflow](../engineering/spec-driven-workflow/SKILL.md), [write-a-skill](../engineering/write-a-skill/SKILL.md), [agent-harness](../engineering/agent-harness/SKILL.md), [cloud-security](../engineering/cloud-security/SKILL.md)
- Project Management: [meeting-analyzer](../project-management/meeting-analyzer/SKILL.md), [team-communications](../project-management/team-communications/SKILL.md)
- Personal Productivity: [capture](../personal-productivity/capture/SKILL.md), [deep-work](../personal-productivity/deep-work/SKILL.md), [reflect](../personal-productivity/reflect/SKILL.md)
- Data & Analytics: [statistical-analyst](../data-analytics/statistical-analyst/SKILL.md)

---

## May 2026 Tier-3 Additions (12 new PM skills)

Atomic PM skills covering classic strategy frameworks, GTM, and execution. Adds two new PM subfolders.

### Strategy frameworks — `project-management/strategy-frameworks/` (+5)
- [business-model-canvas](../project-management/strategy-frameworks/business-model-canvas/SKILL.md) — Osterwalder 9-block + cross-block coherence validator (1 tool)
- [lean-canvas](../project-management/strategy-frameworks/lean-canvas/SKILL.md) — Ash Maurya startup canvas + unfair-advantage discipline (1 tool)
- [swot-analysis](../project-management/strategy-frameworks/swot-analysis/SKILL.md) — SWOT + TOWS matrix + evidence audit (1 tool)
- [porters-five-forces](../project-management/strategy-frameworks/porters-five-forces/SKILL.md) — Industry analysis + strategy translation (1 tool)
- [ansoff-matrix](../project-management/strategy-frameworks/ansoff-matrix/SKILL.md) — Growth quadrants + stage-appropriate investment mix (1 tool)

### Go-to-market — `project-management/gtm/` (+2)
- [gtm-strategy](../project-management/gtm/gtm-strategy/SKILL.md) — ICP × motion × channels × messaging + T-90 → T+90 sequence (1 tool)
- [ideal-customer-profile](../project-management/gtm/ideal-customer-profile/SKILL.md) — 8-dimension ICP + qualification rubric + scoring (1 tool, 2 modes)

### Discovery additions (+2)
- [opportunity-solution-tree](../project-management/discovery/opportunity-solution-tree/SKILL.md) — Teresa Torres OST: outcome → opportunity → solution → test (1 tool)
- [metrics-dashboard](../project-management/discovery/metrics-dashboard/SKILL.md) — NS + inputs + guardrails + operational; anti-vanity audit (1 tool)

### Execution additions (+3)
- [stakeholder-map](../project-management/execution/stakeholder-map/SKILL.md) — Power × Interest 2x2 + DACI + blocker conversion plans (1 tool)
- [test-scenarios](../project-management/execution/test-scenarios/SKILL.md) — 7-category coverage (happy / edge / error / empty / concurrent / a11y / security) (1 tool)
- [sprint-plan](../project-management/execution/sprint-plan/SKILL.md) — Capacity math + commit/stretch discipline + DoD audit (1 tool)

**Tier 3 totals:** 12 skills · 12 stdlib Python validators · 24 reference docs · ~12K lines

---

## May 2026 Tier-2 Additions (14 new skills)

### C-Level Advisory (+5)
- [chief-ai-officer-advisor](../c-level-advisor/chief-ai-officer-advisor/SKILL.md) — AI strategy, governance, risk register, investment planner, maturity assessor (3 tools)
- [chief-data-officer-advisor](../c-level-advisor/chief-data-officer-advisor/SKILL.md) — Data strategy, governance audit (DAMA-DMBOK), platform evaluator, maturity assessor (3 tools)
- [chief-customer-officer-advisor](../c-level-advisor/chief-customer-officer-advisor/SKILL.md) — CX strategy, churn intervention planner, VoC program designer, CX maturity scorer (3 tools)
- [general-counsel-advisor](../c-level-advisor/general-counsel-advisor/SKILL.md) — Legal risk register, contract portfolio analyzer, regulatory calendar generator (3 tools)
- [vpe-advisor](../c-level-advisor/vpe-advisor/SKILL.md) — Engineering org health scorer, DORA/DevEx productivity dashboard, capacity planner (3 tools)

### Product Team (+5)
- [product-analytics](../product-team/product-analytics/SKILL.md) — Metric tree designer, event taxonomy auditor, retention cohort analyzer (3 tools)
- [apple-hig-expert](../product-team/apple-hig-expert/SKILL.md) — HIG compliance checker, component pattern lookup, accessibility auditor (3 tools)
- [research-summarizer](../product-team/research-summarizer/SKILL.md) — Synthesis organizer, insight quality scorer, findings brief generator (3 tools)
- [spec-to-repo](../product-team/spec-to-repo/SKILL.md) — PRD-to-tickets decomposer, branch-naming validator, PR scope analyzer (3 tools)
- [roadmap-communicator](../product-team/roadmap-communicator/SKILL.md) — Audience translator, confidence band generator, roadmap diff reporter (3 tools)

### Research — NEW DOMAIN (+4)
- [litreview](../research/litreview/SKILL.md) — Search strategy builder (PRISMA-aligned), source quality scorer, thematic synthesis builder (3 tools)
- [grants](../research/grants/SKILL.md) — Funder fit scorer, proposal structure validator (NIH/NSF/SBIR/foundation/DARPA), budget realism checker (3 tools)
- [patent](../research/patent/SKILL.md) — Prior-art search planner, claim landscape mapper, patentability scorer (5-dim) (3 tools)
- [dossier](../research/dossier/SKILL.md) — Dossier outline generator, source triangulation validator (Admiralty Code), fact/inference separator (3 tools)

**Tier 2 totals:** 14 skills · 42 stdlib Python scripts · 42 reference docs · ~24K lines

---

## Apr 2026 Tier-1 Additions (17 new skills)

### Engineering (+6)
- [feature-flags-architect](../engineering/feature-flags-architect/SKILL.md) — Flag types, rollout playbooks, kill switches, debt cleanup (3 tools)
- [chaos-engineering](../engineering/chaos-engineering/SKILL.md) — Hypothesis-driven fault injection; gameday playbooks; maturity model (3 tools)
- [kubernetes-operator](../engineering/kubernetes-operator/SKILL.md) — Operator pattern, CRDs, reconciliation, finalizers (3 tools)
- [azure-cloud-architect](../engineering/azure-cloud-architect/SKILL.md) — Azure-specific service selection, WAF, cost (3 tools)
- [gcp-cloud-architect](../engineering/gcp-cloud-architect/SKILL.md) — GCP-specific service selection, CAF, cost (3 tools)
- [data-quality-auditor](../engineering/data-quality-auditor/SKILL.md) — DQ dimensions, check catalog, incident response (3 tools)

### Business & Growth — Commercial mechanics (+4)
- [deal-desk](../business-growth/deal-desk/SKILL.md) — Charter, approval matrix, packet, velocity (3 tools)
- [channel-economics](../business-growth/channel-economics/SKILL.md) — Channel models, TCO, tier economics, mix (3 tools)
- [partnerships-architect](../business-growth/partnerships-architect/SKILL.md) — Partnership types, deal structures, eval, ROI (3 tools)
- [commercial-policy](../business-growth/commercial-policy/SKILL.md) — Policy charter, compliance, deviation, generator (3 tools)

### RA/QM — Audit-prep playbooks (+6, new `audit-prep/` subfolder)
- [soc2-audit-prep](../ra-qm-team/audit-prep/soc2-audit-prep/SKILL.md) — 4/8/12-week SOC 2 sprint (2 tools)
- [gdpr-audit-prep](../ra-qm-team/audit-prep/gdpr-audit-prep/SKILL.md) — DPA inquiry + customer audit response (2 tools)
- [fda-qsr-audit-prep](../ra-qm-team/audit-prep/fda-qsr-audit-prep/SKILL.md) — 21 CFR 820 / QMSR + 483/WL response (2 tools)
- [ai-act-readiness](../ra-qm-team/audit-prep/ai-act-readiness/SKILL.md) — EU AI Act conformity prep + GPAI obligations (2 tools)
- [aims-audit](../ra-qm-team/audit-prep/aims-audit/SKILL.md) — ISO 42001 AIMS certification prep (2 tools)
- [compliance-readiness](../ra-qm-team/audit-prep/compliance-readiness/SKILL.md) — Multi-framework orchestrator with shared evidence (3 tools)

### Marketing (+1)
- [aeo](../marketing/aeo/SKILL.md) — Answer Engine Optimization for LLM citation (ChatGPT/Claude/Gemini) (3 tools)

---

## Engineering (91)

Core software engineering expertise with Python automation tools.

### Core Engineering (28)

| Skill | Description | Tools |
|-------|-------------|-------|
| [senior-architect](../engineering/senior-architect/SKILL.md) | System design, distributed systems, architectural patterns | 2 |
| [senior-frontend](../engineering/senior-frontend/SKILL.md) | React patterns, state management, performance, accessibility | 2 |
| [senior-backend](../engineering/senior-backend/SKILL.md) | API design, microservices, databases, caching, queues | 2 |
| [senior-fullstack](../engineering/senior-fullstack/SKILL.md) | React, Node.js, databases, API design, system architecture | 3 |
| [senior-qa](../engineering/senior-qa/SKILL.md) | Test strategy, automation frameworks, performance testing | 2 |
| [senior-devops](../engineering/senior-devops/SKILL.md) | Docker, Kubernetes, Terraform, CI/CD, monitoring, SRE | 2 |
| [senior-secops](../engineering/senior-secops/SKILL.md) | Security operations, vulnerability management, incident response | 2 |
| [senior-security](../engineering/senior-security/SKILL.md) | OWASP, threat modeling, penetration testing, compliance | 2 |
| [senior-mobile](../engineering/senior-mobile/SKILL.md) | React Native, iOS, Android, cross-platform, app store | 3 |
| [senior-cloud-architect](../engineering/senior-cloud-architect/SKILL.md) | AWS, GCP, Azure, multi-cloud, cost optimization | - |
| [senior-data-scientist](../engineering/senior-data-scientist/SKILL.md) | A/B testing, statistical analysis, feature engineering | 3 |
| [senior-data-engineer](../engineering/senior-data-engineer/SKILL.md) | Airflow, Spark, data pipelines, warehousing | 3 |
| [senior-ml-engineer](../engineering/senior-ml-engineer/SKILL.md) | ML pipelines, model deployment, MLOps, RAG systems | 3 |
| [senior-prompt-engineer](../engineering/senior-prompt-engineer/SKILL.md) | Prompt optimization, LLM evaluation, agents | 3 |
| [senior-computer-vision](../engineering/senior-computer-vision/SKILL.md) | Object detection, image segmentation, model training | 3 |
| [aws-solution-architect](../engineering/aws-solution-architect/SKILL.md) | Serverless patterns, CloudFormation, cost optimization | 2 |
| [code-reviewer](../engineering/code-reviewer/SKILL.md) | PR analysis, code quality checking, review automation | 2 |
| [incident-commander](../engineering/incident-commander/SKILL.md) | Incident response, severity classification, RCA | 3 |
| [ms365-tenant-manager](../engineering/ms365-tenant-manager/SKILL.md) | Office 365/Azure AD administration | 2 |
| [tdd-guide](../engineering/tdd-guide/SKILL.md) | Test-driven development workflow | 2 |
| [tech-stack-evaluator](../engineering/tech-stack-evaluator/SKILL.md) | Framework comparison, TCO analysis | 2 |
| [claude-code-mastery](../engineering/claude-code-mastery/SKILL.md) | CLAUDE.md optimization, skill authoring, subagents, hooks | 3 |
| [codex-cli-specialist](../engineering/codex-cli-specialist/SKILL.md) | Cross-platform skill authoring, Codex CLI, conversion tools | 3 |
| [devops-workflow-engineer](../engineering/devops-workflow-engineer/SKILL.md) | GitHub Actions, CI/CD pipelines, deployment strategies | 3 |
| [qa-browser-automation](../engineering/qa-browser-automation/SKILL.md) | 11-phase browser QA, health scoring, WCAG audit, visual regression | 4 |
| [release-orchestrator](../engineering/release-orchestrator/SKILL.md) | Release pipeline, pre-flight checks, versioning, readiness scoring | 4 |
| [doc-drift-detector](../engineering/doc-drift-detector/SKILL.md) | Documentation drift analysis, staleness scoring, API doc validation | 4 |
| [design-auditor](../engineering/design-auditor/SKILL.md) | 12-category design audit, AI slop detection, color contrast checking | 4 |

### Advanced Engineering (32)

Enterprise-grade skills with sophisticated analysis tooling.

| Skill | Description | Tools |
|-------|-------------|-------|
| [agent-designer](../engineering/agent-designer/SKILL.md) | Multi-agent architecture, tool schema generation | 3 |
| [api-design-reviewer](../engineering/api-design-reviewer/SKILL.md) | REST API linting, breaking change detection, scoring | 3 |
| [database-designer](../engineering/database-designer/SKILL.md) | Schema analysis, ERD generation, index optimization | 3 |
| [dependency-auditor](../engineering/dependency-auditor/SKILL.md) | Multi-language dependency scanning, license compliance | 3 |
| [interview-system-designer](../engineering/interview-system-designer/SKILL.md) | Interview loop design, question banks, calibration | 3 |
| [migration-architect](../engineering/migration-architect/SKILL.md) | Zero-downtime migration planning, rollback strategies | 3 |
| [observability-designer](../engineering/observability-designer/SKILL.md) | SLO design, alert optimization, dashboard generation | 3 |
| [rag-architect](../engineering/rag-architect/SKILL.md) | RAG pipeline building, chunking optimization | 3 |
| [release-manager](../engineering/release-manager/SKILL.md) | Automated changelog, semantic versioning | 3 |
| [skill-tester](../engineering/skill-tester/SKILL.md) | Meta-skill validator, quality scoring | 3 |
| [tech-debt-tracker](../engineering/tech-debt-tracker/SKILL.md) | AST parsing, debt prioritization, trend analysis | 3 |
| [agent-protocol](../engineering/agent-protocol/SKILL.md) | AI agent communication protocols, MCP, A2A, tool schemas | - |
| [agent-workflow-designer](../engineering/agent-workflow-designer/SKILL.md) | Multi-agent orchestration, workflow DAGs, agent routing | - |
| [api-test-suite-builder](../engineering/api-test-suite-builder/SKILL.md) | API testing frameworks, contract testing, load testing | - |
| [ci-cd-pipeline-builder](../engineering/ci-cd-pipeline-builder/SKILL.md) | CI/CD design, GitHub Actions, GitLab CI, deployment strategies | - |
| [codebase-onboarding](../engineering/codebase-onboarding/SKILL.md) | New developer onboarding, codebase docs, architecture guides | - |
| [database-schema-designer](../engineering/database-schema-designer/SKILL.md) | Schema design, normalization, migration planning, ERD | - |
| [env-secrets-manager](../engineering/env-secrets-manager/SKILL.md) | Secrets management, .env security, Vault, rotation policies | - |
| [git-worktree-manager](../engineering/git-worktree-manager/SKILL.md) | Git worktree workflows, parallel development, branches | - |
| [mcp-server-builder](../engineering/mcp-server-builder/SKILL.md) | MCP server development, tool definition, transport protocols | - |
| [monorepo-navigator](../engineering/monorepo-navigator/SKILL.md) | Monorepo tooling, workspace management, build caching | - |
| [performance-profiler](../engineering/performance-profiler/SKILL.md) | Performance analysis, flame graphs, memory profiling | - |
| [playwright-pro](../engineering/playwright-pro/SKILL.md) | E2E testing with Playwright, page objects, CI integration | - |
| [changelog-generator](../engineering/changelog-generator/SKILL.md) | Automated changelogs, conventional commits, release notes | - |
| [pr-review-expert](../engineering/pr-review-expert/SKILL.md) | PR review best practices, automated checks, checklists | - |
| [runbook-generator](../engineering/runbook-generator/SKILL.md) | Operational runbooks, incident procedures, automation | - |
| [saas-scaffolder](../engineering/saas-scaffolder/SKILL.md) | SaaS boilerplate, auth, billing, multi-tenancy | - |
| [skill-security-auditor](../engineering/skill-security-auditor/SKILL.md) | Security audit for AI skills, prompt injection detection | - |
| [context-engine](../engineering/context-engine/SKILL.md) | Context management for AI agents, memory systems | - |
| [self-improving-agent](../engineering/self-improving-agent/SKILL.md) | Self-improving AI patterns, feedback loops, metrics | - |
| [prompt-engineer-toolkit](../engineering/prompt-engineer-toolkit/SKILL.md) | Prompt engineering frameworks, evaluation, optimization | - |
| [stripe-integration-expert](../engineering/stripe-integration-expert/SKILL.md) | Stripe API, payment flows, subscriptions, webhooks | - |

### Cloud, Infrastructure & Reliability (8)

| Skill | Description | Tools |
|-------|-------------|-------|
| [azure-cloud-architect](../engineering/azure-cloud-architect/SKILL.md) | Azure service selection, Well-Architected Framework, cost | 3 |
| [gcp-cloud-architect](../engineering/gcp-cloud-architect/SKILL.md) | GCP service selection, Cloud Adoption Framework, cost | 3 |
| [kubernetes-operator](../engineering/kubernetes-operator/SKILL.md) | Operator pattern, CRDs, reconciliation, finalizers | 3 |
| [helm-chart-builder](../engineering/helm-chart-builder/SKILL.md) | Helm chart analysis, values validation, dependency audit | 2 |
| [terraform-patterns](../engineering/terraform-patterns/SKILL.md) | Terraform module analysis, IaC misconfiguration scanning | 2 |
| [docker-development](../engineering/docker-development/SKILL.md) | Dockerfile analysis, layer optimization, compose validation | 2 |
| [chaos-engineering](../engineering/chaos-engineering/SKILL.md) | Hypothesis-driven fault injection, gameday playbooks, maturity model | 3 |
| [secrets-vault-manager](../engineering/secrets-vault-manager/SKILL.md) | Vault configuration, secret rotation planning, audit log analysis | 3 |

### Security & Threat (4)

| Skill | Description | Tools |
|-------|-------------|-------|
| [cloud-security](../engineering/cloud-security/SKILL.md) | AWS/Azure/GCP posture: IAM least privilege, exposure, encryption, logging | 4 |
| [ai-security](../engineering/ai-security/SKILL.md) | AI/ML pipeline security, prompt injection, data poisoning risk | 1 |
| [red-team](../engineering/red-team/SKILL.md) | Engagement scoping, rules of engagement, adversary simulation planning | 1 |
| [threat-detection](../engineering/threat-detection/SKILL.md) | Log threat analysis, brute force and injection detection, access anomalies | 1 |

### Data & Databases (3)

| Skill | Description | Tools |
|-------|-------------|-------|
| [sql-database-assistant](../engineering/sql-database-assistant/SKILL.md) | Query optimization, schema exploration, migration SQL generation | 3 |
| [snowflake-development](../engineering/snowflake-development/SKILL.md) | Snowflake query performance, warehouse sizing, cost troubleshooting | 1 |
| [data-quality-auditor](../engineering/data-quality-auditor/SKILL.md) | DQ dimensions, check catalog, incident response | 3 |

### AI Systems, Agents & LLM Ops (8)

| Skill | Description | Tools |
|-------|-------------|-------|
| [agenthub](../engineering/agenthub/SKILL.md) | Multi-agent DAG orchestration, agent spawning, output merging | 4 |
| [agent-harness](../engineering/agent-harness/SKILL.md) | Agent eval harness: scenario suites, deterministic replay, regression diffing | 2 |
| [agentic-evaluation-framework](../engineering/agentic-evaluation-framework/SKILL.md) | LLM-as-judge, eval rubrics, pairwise comparison, agent quality | 2 |
| [extended-thinking-architect](../engineering/extended-thinking-architect/SKILL.md) | Reasoning effort, thinking budgets, reasoning-vs-cost tuning | 2 |
| [batch-api-orchestrator](../engineering/batch-api-orchestrator/SKILL.md) | Batch vs realtime cost modelling, bulk LLM job design | 2 |
| [llm-cost-optimizer](../engineering/llm-cost-optimizer/SKILL.md) | Token counting, prompt cost estimation, model pricing comparison | 3 |
| [computer-use-automation](../engineering/computer-use-automation/SKILL.md) | Computer-use agents, screenshot-driven actions, GUI vs API tradeoffs | 2 |
| [prompt-governance](../engineering/prompt-governance/SKILL.md) | Prompt catalog, versioning, injection audit, quality and compliance review | 2 |

### Developer Workflow & Quality (8)

| Skill | Description | Tools |
|-------|-------------|-------|
| [write-a-skill](../engineering/write-a-skill/SKILL.md) | Author, lint, and publish skill packages against the authoring standard | 4 |
| [spec-driven-workflow](../engineering/spec-driven-workflow/SKILL.md) | Executable specs, traceable requirement IDs, merge-time coverage gates | 3 |
| [code-tour](../engineering/code-tour/SKILL.md) | Ordered annotated codebase tours with anchors that resist rot | 3 |
| [focused-fix](../engineering/focused-fix/SKILL.md) | Minimal-blast-radius bugfixes, change scope analysis | 1 |
| [feature-flags-architect](../engineering/feature-flags-architect/SKILL.md) | Flag types, rollout playbooks, kill switches, debt cleanup | 3 |
| [a11y-audit](../engineering/a11y-audit/SKILL.md) | WCAG compliance scanning, HTML a11y violations, color contrast | 2 |
| [browser-automation](../engineering/browser-automation/SKILL.md) | Web automation scripts, scraping, form filling, detection checks | 3 |
| [google-workspace-cli](../engineering/google-workspace-cli/SKILL.md) | Google Workspace audit, security settings, admin configuration review | 3 |

## C-Level Advisory (31)

Strategic decision-making for executive leadership.

| Skill | Description | Tools |
|-------|-------------|-------|
| [ceo-advisor](../c-level-advisor/ceo-advisor/SKILL.md) | Strategic planning, board governance, investor relations, M&A | 2 |
| [cto-advisor](../c-level-advisor/cto-advisor/SKILL.md) | Technical strategy, architecture decisions, engineering leadership | 2 |
| [cfo-advisor](../c-level-advisor/cfo-advisor/SKILL.md) | Financial planning, fundraising, unit economics, treasury | - |
| [cmo-advisor](../c-level-advisor/cmo-advisor/SKILL.md) | Brand strategy, demand generation, marketing leadership | - |
| [coo-advisor](../c-level-advisor/coo-advisor/SKILL.md) | Operations strategy, process optimization, scaling | - |
| [chief-of-staff](../c-level-advisor/chief-of-staff/SKILL.md) | Executive operations, cross-functional alignment, strategic initiatives | - |
| [chro-advisor](../c-level-advisor/chro-advisor/SKILL.md) | People strategy, org design, compensation, workforce planning | - |
| [ciso-advisor](../c-level-advisor/ciso-advisor/SKILL.md) | Security strategy, risk quantification, compliance roadmap | - |
| [cpo-advisor](../c-level-advisor/cpo-advisor/SKILL.md) | Product strategy, portfolio management, product-market fit | - |
| [cro-advisor](../c-level-advisor/cro-advisor/SKILL.md) | Revenue strategy, sales/CS alignment, NRR optimization | - |
| [culture-architect](../c-level-advisor/culture-architect/SKILL.md) | Company culture design, values, engagement, remote culture | - |
| [decision-logger](../c-level-advisor/decision-logger/SKILL.md) | Decision documentation, ADRs, decision frameworks | - |
| [executive-mentor](../c-level-advisor/executive-mentor/SKILL.md) | Executive coaching, leadership development, board prep | - |
| [founder-coach](../c-level-advisor/founder-coach/SKILL.md) | Founder coaching, fundraising, pivots, co-founder dynamics | - |
| [org-health-diagnostic](../c-level-advisor/org-health-diagnostic/SKILL.md) | Organization assessment, health scoring, alignment analysis | - |
| [board-deck-builder](../c-level-advisor/board-deck-builder/SKILL.md) | Board presentation design, investor updates, narrative structure | - |
| [board-meeting](../c-level-advisor/board-meeting/SKILL.md) | Board meeting facilitation, agenda, minutes, governance | - |
| [change-management](../c-level-advisor/change-management/SKILL.md) | Organizational change, ADKAR, Kotter's 8 steps, transformation | - |
| [company-os](../c-level-advisor/company-os/SKILL.md) | Operating system for companies, cadences, OKRs, rituals | - |
| [competitive-intel](../c-level-advisor/competitive-intel/SKILL.md) | Competitive analysis, battlecards, market intelligence | - |
| [intl-expansion](../c-level-advisor/intl-expansion/SKILL.md) | International expansion, market entry, localization | - |
| [ma-playbook](../c-level-advisor/ma-playbook/SKILL.md) | M&A strategy, due diligence, integration playbook | - |
| [strategic-alignment](../c-level-advisor/strategic-alignment/SKILL.md) | Strategy alignment, OKR cascade, cross-functional sync | - |
| [internal-narrative](../c-level-advisor/internal-narrative/SKILL.md) | Internal communications, all-hands, company narratives | - |
| [scenario-war-room](../c-level-advisor/scenario-war-room/SKILL.md) | Scenario planning, war gaming, crisis simulation | - |
| [cs-onboard](../c-level-advisor/cs-onboard/SKILL.md) | C-suite onboarding, first 90 days, stakeholder mapping | - |
| [chief-ai-officer-advisor](../c-level-advisor/chief-ai-officer-advisor/SKILL.md) | AI strategy, governance, risk register, investment planning, maturity | 3 |
| [chief-data-officer-advisor](../c-level-advisor/chief-data-officer-advisor/SKILL.md) | Data strategy, DAMA-DMBOK governance audit, platform evaluation | 3 |
| [chief-customer-officer-advisor](../c-level-advisor/chief-customer-officer-advisor/SKILL.md) | CX strategy, churn intervention, VoC program design, CX maturity | 3 |
| [general-counsel-advisor](../c-level-advisor/general-counsel-advisor/SKILL.md) | Legal risk register, contract portfolio analysis, regulatory calendar | 3 |
| [vpe-advisor](../c-level-advisor/vpe-advisor/SKILL.md) | Engineering org health, DORA/DevEx dashboards, capacity planning | 3 |

## Marketing (39)

Data-driven marketing with Python automation tools.

| Skill | Description | Tools |
|-------|-------------|-------|
| [content-creator](../marketing/content-creator/SKILL.md) | Brand voice analyzer, SEO optimizer, content frameworks | 2 |
| [marketing-demand-acquisition](../marketing/marketing-demand-acquisition/SKILL.md) | Demand gen, paid media, SEO, partnerships | 1 |
| [marketing-strategy-pmm](../marketing/marketing-strategy-pmm/SKILL.md) | Positioning, GTM, competitive intelligence | - |
| [app-store-optimization](../marketing/app-store-optimization/SKILL.md) | ASO for iOS & Android | - |
| [campaign-analytics](../marketing/campaign-analytics/SKILL.md) | Multi-touch attribution, funnel analysis, ROI | 3 |
| [social-media-analyzer](../marketing/social-media-analyzer/SKILL.md) | Social media performance tracking, engagement metrics | - |
| [brand-strategist](../marketing/brand-strategist/SKILL.md) | Brand positioning, identity systems, brand architecture | - |
| [growth-marketer](../marketing/growth-marketer/SKILL.md) | Experimentation, funnel optimization, viral loops, retention | - |
| [marketing-analyst](../marketing/marketing-analyst/SKILL.md) | Attribution modeling, ROI analysis, campaign optimization | - |
| [seo-specialist](../marketing/seo-specialist/SKILL.md) | Technical SEO, keyword research, link building, analytics | - |
| [ad-creative](../marketing/ad-creative/SKILL.md) | Ad creative design, A/B testing, platform-specific formats | - |
| [ai-seo](../marketing/ai-seo/SKILL.md) | AI-powered SEO, SGE optimization, semantic search | - |
| [brand-guidelines](../marketing/brand-guidelines/SKILL.md) | Brand identity systems, style guides, voice & tone | - |
| [cold-email](../marketing/cold-email/SKILL.md) | Cold outreach, personalization, sequences, deliverability | - |
| [content-humanizer](../marketing/content-humanizer/SKILL.md) | Natural writing patterns, AI detection avoidance, authenticity | - |
| [content-production](../marketing/content-production/SKILL.md) | Content ops, editorial calendar, workflow management | - |
| [content-strategy](../marketing/content-strategy/SKILL.md) | Content pillars, audience research, funnel mapping | - |
| [copywriting](../marketing/copywriting/SKILL.md) | Persuasive writing, PAS, AIDA, BAB frameworks | - |
| [copy-editing](../marketing/copy-editing/SKILL.md) | Style consistency, grammar, editorial standards | - |
| [landing-page-generator](../marketing/landing-page-generator/SKILL.md) | Landing page design, conversion optimization, CTA strategy | - |
| [marketing-context](../marketing/marketing-context/SKILL.md) | Market research, customer insights, positioning context | - |
| [marketing-ideas](../marketing/marketing-ideas/SKILL.md) | Campaign ideation, creative brainstorming, trend analysis | - |
| [marketing-ops](../marketing/marketing-ops/SKILL.md) | Marketing automation, MarTech stack, data management | - |
| [marketing-psychology](../marketing/marketing-psychology/SKILL.md) | Behavioral psychology, cognitive biases, persuasion | - |
| [paid-ads](../marketing/paid-ads/SKILL.md) | PPC campaigns, Google/Meta/LinkedIn Ads, budget optimization | - |
| [social-content](../marketing/social-content/SKILL.md) | Social media content creation, platform-specific formats | - |
| [programmatic-seo](../marketing/programmatic-seo/SKILL.md) | Programmatic page generation, template-based SEO at scale | - |
| [schema-markup](../marketing/schema-markup/SKILL.md) | Structured data, JSON-LD, rich snippets, Knowledge Graph | - |
| [seo-audit](../marketing/seo-audit/SKILL.md) | Technical SEO audits, Core Web Vitals, crawl analysis | - |
| [site-architecture](../marketing/site-architecture/SKILL.md) | Information architecture, URL structure, internal linking | - |
| [analytics-tracking](../marketing/analytics-tracking/SKILL.md) | GTM, event tracking, conversion tracking, GA4 | - |
| [email-sequence](../marketing/email-sequence/SKILL.md) | Email automation, drip campaigns, nurture flows | - |
| [email-template-builder](../marketing/email-template-builder/SKILL.md) | Email HTML templates, responsive design, deliverability | - |
| [social-media-manager](../marketing/social-media-manager/SKILL.md) | Social media management, scheduling, community management | - |
| [launch-strategy](../marketing/launch-strategy/SKILL.md) | Product launch playbooks, pre/post-launch analysis | - |
| [aeo](../marketing/aeo/SKILL.md) | Answer Engine Optimization for LLM citation and AI-assistant answers | 3 |
| [ab-test-setup](../marketing/ab-test-setup/SKILL.md) | Sample size, test duration, significance for conversion experiments | 3 |
| [video-content-strategist](../marketing/video-content-strategist/SKILL.md) | Video calendars, video SEO, thumbnail and title optimization | 3 |
| [x-twitter-growth](../marketing/x-twitter-growth/SKILL.md) | Tweet analysis, thread building, posting schedule, follower growth | 3 |

## Product Team (13)

User-centered product development with automation tools.

| Skill | Description | Tools |
|-------|-------------|-------|
| [product-manager-toolkit](../product-team/product-manager-toolkit/SKILL.md) | RICE prioritizer, interview analyzer, PRD templates | 2 |
| [agile-product-owner](../product-team/agile-product-owner/SKILL.md) | User stories, sprint planning, velocity tracking | 1 |
| [product-strategist](../product-team/product-strategist/SKILL.md) | OKR cascade, market analysis, vision setting | 1 |
| [ui-design-system](../product-team/ui-design-system/SKILL.md) | Design tokens, component documentation, responsive design | 1 |
| [ux-researcher-designer](../product-team/ux-researcher-designer/SKILL.md) | Personas, journey mapping, usability research | 1 |
| [product-designer](../product-team/product-designer/SKILL.md) | UI/UX design, prototyping, user research, design systems | - |
| [design-system-lead](../product-team/design-system-lead/SKILL.md) | Design tokens, component libraries, documentation | - |
| [ab-test-setup](../product-team/ab-test-setup/SKILL.md) | A/B testing design, statistical significance, feature flags | - |
| [product-analytics](../product-team/product-analytics/SKILL.md) | Metric tree designer, event taxonomy auditor, retention cohorts | 3 |
| [apple-hig-expert](../product-team/apple-hig-expert/SKILL.md) | HIG compliance checking, component patterns, accessibility audit | 3 |
| [research-summarizer](../product-team/research-summarizer/SKILL.md) | Synthesis organizer, insight quality scoring, findings briefs | 3 |
| [spec-to-repo](../product-team/spec-to-repo/SKILL.md) | PRD-to-tickets decomposition, branch naming, PR scope analysis | 3 |
| [roadmap-communicator](../product-team/roadmap-communicator/SKILL.md) | Audience translation, confidence bands, roadmap diff reporting | 3 |

## Project Management (68) ★ most-visited domain

Delivery excellence with discovery, execution frameworks, career growth, and Jira / Linear / Notion / Confluence integration. See [Quick Start by role](../project-management/README.md#quick-start-by-role).

### Role-Based Skills (15)

| Skill | Description | Tools |
|-------|-------------|-------|
| [senior-pm](../project-management/senior-pm/SKILL.md) | Portfolio management, stakeholder mapping, risk analysis, WSJF | 4 |
| [scrum-master](../project-management/scrum-master/SKILL.md) | Sprint analytics, velocity forecasting, capacity planning, team health | 4 |
| [delivery-manager](../project-management/delivery-manager/SKILL.md) | Release management, deployment, incident response | - |
| [jira-expert](../project-management/jira-expert/SKILL.md) | JQL mastery, workflows, automation, dashboards | - |
| [linear-expert](../project-management/linear-expert/SKILL.md) ★ NEW | GraphQL queries, cycles, projects, Jira → Linear migration | - |
| [confluence-expert](../project-management/confluence-expert/SKILL.md) | Knowledge management, space architecture | - |
| [notion-pm](../project-management/notion-pm/SKILL.md) ★ NEW | DB design for PRDs/OKRs/Roadmap/Decisions, Notion API patterns | - |
| [atlassian-admin](../project-management/atlassian-admin/SKILL.md) | System administration, security, integrations | - |
| [atlassian-templates](../project-management/atlassian-templates/SKILL.md) | Template design, custom blueprints | - |
| [agile-coach](../project-management/agile-coach/SKILL.md) | Transformation, framework implementation, coaching | - |
| [program-manager](../project-management/program-manager/SKILL.md) | Multi-project coordination, portfolio governance | - |
| [sprint-retrospective](../project-management/sprint-retrospective/SKILL.md) | Data-driven sprint retros, velocity analytics, code churn, trend tracking | 4 |
| [productboard-expert](../project-management/productboard-expert/SKILL.md) | Insight-to-Feature triage, Driver scoring, Releases, REST API automation | - |
| [meeting-analyzer](../project-management/meeting-analyzer/SKILL.md) | Decisions, actions and open questions register; ownerless-item flagging | 3 |
| [team-communications](../project-management/team-communications/SKILL.md) | Channel routing, meeting-load reduction, escalation SLAs, timezone norms | 3 |

### Discovery Skills (10)

| Skill | Description | Tools |
|-------|-------------|-------|
| [brainstorm-ideas](../project-management/discovery/brainstorm-ideas/SKILL.md) | Product Trio ideation, Opportunity Solution Trees | - |
| [brainstorm-experiments](../project-management/discovery/brainstorm-experiments/SKILL.md) | Lean experiment design, XYZ hypotheses | 1 |
| [identify-assumptions](../project-management/discovery/identify-assumptions/SKILL.md) | Assumption mapping across 4-8 risk categories | 1 |
| [pre-mortem](../project-management/discovery/pre-mortem/SKILL.md) | Tiger/Paper Tiger/Elephant risk classification | 1 |
| [interview-synthesis](../project-management/discovery/interview-synthesis/SKILL.md) ★ NEW | Interview transcripts → opportunity solution tree | 1 |
| [opportunity-solution-tree](../project-management/discovery/opportunity-solution-tree/SKILL.md) | Outcome → opportunity → solution → test | 1 |
| [metrics-dashboard](../project-management/discovery/metrics-dashboard/SKILL.md) | North star + inputs + guardrails; anti-vanity audit | 1 |
| [customer-interview-script](../project-management/discovery/customer-interview-script/SKILL.md) | Scripted question hierarchy, behavior-over-opinion probes | - |
| [jtbd-workshop](../project-management/discovery/jtbd-workshop/SKILL.md) | Switch interviews, forces of progress, ODI outcome scoring | - |
| [value-proposition-canvas](../project-management/discovery/value-proposition-canvas/SKILL.md) | Customer Profile + Value Map with fit validation | - |

### Execution Skills (32)

| Skill | Description | Tools |
|-------|-------------|-------|
| [create-prd](../project-management/execution/create-prd/SKILL.md) | PRD scaffolding with 8-section structure | 1 |
| [prfaq](../project-management/execution/prfaq/SKILL.md) ★ NEW | Amazon Working Backwards PR/FAQ as standalone skill | - |
| [brainstorm-okrs](../project-management/execution/brainstorm-okrs/SKILL.md) | OKR brainstorming and validation (Wodtke) | 1 |
| [north-star-metric](../project-management/execution/north-star-metric/SKILL.md) ★ NEW | NSM + input metric tree with leading indicators | 1 |
| [outcome-roadmap](../project-management/execution/outcome-roadmap/SKILL.md) | Output-to-outcome roadmap transformation | 1 |
| [roadmap-communication](../project-management/execution/roadmap-communication/SKILL.md) ★ NEW | Exec / customer / internal roadmap variants | - |
| [prioritization-frameworks](../project-management/execution/prioritization-frameworks/SKILL.md) | Multi-framework scoring (RICE, ICE, MoSCoW) | 1 |
| [backlog-refinement](../project-management/execution/backlog-refinement/SKILL.md) ★ NEW | INVEST + DoR/DoD + splitting playbook | 1 |
| [story-splitting](../project-management/execution/story-splitting/SKILL.md) ★ NEW | 9 vertical slicing patterns (Lawrence) | - |
| [story-mapping](../project-management/execution/story-mapping/SKILL.md) | Jeff Patton user story mapping | - |
| [job-stories](../project-management/execution/job-stories/SKILL.md) | JTBD When/Want/So backlog format | - |
| [wwas](../project-management/execution/wwas/SKILL.md) | Why-What-Acceptance structured backlog items | - |
| [cycle-time-analyzer](../project-management/execution/cycle-time-analyzer/SKILL.md) ★ NEW | Lead time, cycle time, CFD, Little's Law | 1 |
| [dependency-map](../project-management/execution/dependency-map/SKILL.md) ★ NEW | Cross-team dependencies + critical path | 1 |
| [status-update-generator](../project-management/execution/status-update-generator/SKILL.md) ★ NEW | Weekly exec status from Jira/Linear data | 1 |
| [summarize-meeting](../project-management/execution/summarize-meeting/SKILL.md) | Structured meeting summaries with action items | - |
| [daci-framework](../project-management/execution/daci-framework/SKILL.md) | DACI decision facilitation and governance | - |
| [beta-program](../project-management/execution/beta-program/SKILL.md) ★ NEW | Closed beta playbook (Kano + cohort design) | - |
| [launch-playbook](../project-management/execution/launch-playbook/SKILL.md) ★ NEW | Internal + external launch coordination | - |
| [release-notes](../project-management/execution/release-notes/SKILL.md) | Release notes from tickets/changelogs | 1 |
| [eol-communication](../project-management/execution/eol-communication/SKILL.md) | End-of-life messaging and sunset | - |
| [product-vision](../project-management/execution/product-vision/SKILL.md) | Durable 5-10 year narrative above the north-star metric | - |
| [quarterly-planning](../project-management/execution/quarterly-planning/SKILL.md) | Pre-quarter homework → kickoff → weekly rhythm → close retro | - |
| [ai-feature-prd](../project-management/execution/ai-feature-prd/SKILL.md) | AI/ML PRD sections: model selection, evals, guardrails, HITL, cost | - |
| [pricing-prd](../project-management/execution/pricing-prd/SKILL.md) | Packaging, willingness-to-pay, grandfathering, A/B design, rollback | - |
| [activation-funnel](../project-management/execution/activation-funnel/SKILL.md) | AARRR funnel math, drop-off and bottleneck detection | 1 |
| [customer-feedback-triage](../project-management/execution/customer-feedback-triage/SKILL.md) | Categorize, dedupe and score inbound feature requests | 1 |
| [feature-flag-strategy](../project-management/execution/feature-flag-strategy/SKILL.md) | Flag taxonomy, rollout shapes, kill-switch tree, flag debt | - |
| [post-mortem](../project-management/execution/post-mortem/SKILL.md) | Blameless post-mortems for incidents, escalations, failed experiments | - |
| [stakeholder-map](../project-management/execution/stakeholder-map/SKILL.md) | Power × Interest 2x2 + DACI + blocker conversion plans | 1 |
| [test-scenarios](../project-management/execution/test-scenarios/SKILL.md) | 7-category coverage (happy / edge / error / empty / concurrent / a11y / security) | 1 |
| [sprint-plan](../project-management/execution/sprint-plan/SKILL.md) | Capacity math, commit/stretch discipline, DoD audit | 1 |

### Career Skills (4) ★ NEW

PM career growth — interview prep, ladder rubrics, onboarding, 1:1s. Unique to this library.

| Skill | Description | Tools |
|-------|-------------|-------|
| [pm-interview-prep](../project-management/career/pm-interview-prep/SKILL.md) | APM → Group PM interview prep (CIRCLES, AARM, STAR) | - |
| [pm-career-ladder](../project-management/career/pm-career-ladder/SKILL.md) | Rubrics, gap analysis, growth plan, promo packet | - |
| [pm-onboarding](../project-management/career/pm-onboarding/SKILL.md) | 30-60-90 day plan (Watkins + STARS) | - |
| [pm-1on1s](../project-management/career/pm-1on1s/SKILL.md) | 1:1 templates by partner type (EM, designer, IC, manager) | - |

### Strategy Frameworks (5)

| Skill | Description | Tools |
|-------|-------------|-------|
| [business-model-canvas](../project-management/strategy-frameworks/business-model-canvas/SKILL.md) | 9-block canvas + cross-block coherence validator | 1 |
| [lean-canvas](../project-management/strategy-frameworks/lean-canvas/SKILL.md) | Startup canvas + unfair-advantage discipline | 1 |
| [swot-analysis](../project-management/strategy-frameworks/swot-analysis/SKILL.md) | SWOT + TOWS matrix + evidence audit | 1 |
| [porters-five-forces](../project-management/strategy-frameworks/porters-five-forces/SKILL.md) | Industry analysis + strategy translation | 1 |
| [ansoff-matrix](../project-management/strategy-frameworks/ansoff-matrix/SKILL.md) | Growth quadrants + stage-appropriate investment mix | 1 |

### Go-to-Market (2)

| Skill | Description | Tools |
|-------|-------------|-------|
| [gtm-strategy](../project-management/gtm/gtm-strategy/SKILL.md) | ICP × motion × channels × messaging + T-90 → T+90 sequence | 1 |
| [ideal-customer-profile](../project-management/gtm/ideal-customer-profile/SKILL.md) | 8-dimension ICP + qualification rubric + scoring | 1 |

## Regulatory Affairs, Quality Management & Compliance (27)

Enterprise compliance across 18 frameworks.

### Medical Device & Quality (12)

| Skill | Description | Tools |
|-------|-------------|-------|
| [regulatory-affairs-head](../ra-qm-team/regulatory-affairs-head/SKILL.md) | Regulatory strategy, FDA/EU pathways, market access | 1 |
| [quality-manager-qmr](../ra-qm-team/quality-manager-qmr/SKILL.md) | QMS effectiveness, compliance dashboards | 1 |
| [quality-manager-qms-iso13485](../ra-qm-team/quality-manager-qms-iso13485/SKILL.md) | ISO 13485 compliance, design control | 1 |
| [capa-officer](../ra-qm-team/capa-officer/SKILL.md) | CAPA management, root cause analysis | 1 |
| [quality-documentation-manager](../ra-qm-team/quality-documentation-manager/SKILL.md) | Document control, 21 CFR Part 11 | 1 |
| [risk-management-specialist](../ra-qm-team/risk-management-specialist/SKILL.md) | Risk register, FMEA, ISO 14971 | 1 |
| [information-security-manager-iso27001](../ra-qm-team/information-security-manager-iso27001/SKILL.md) | ISO 27001:2022 ISMS, 93 Annex A controls | 2 |
| [gdpr-dsgvo-expert](../ra-qm-team/gdpr-dsgvo-expert/SKILL.md) | GDPR/DSGVO compliance, DPIA, German BDSG | 3 |
| [mdr-745-specialist](../ra-qm-team/mdr-745-specialist/SKILL.md) | EU MDR 2017/745, GSPR, EUDAMED, UDI | 1 |
| [fda-consultant-specialist](../ra-qm-team/fda-consultant-specialist/SKILL.md) | FDA 510(k)/PMA, QSR/QMSR, HIPAA, cybersecurity | 3 |
| [qms-audit-expert](../ra-qm-team/qms-audit-expert/SKILL.md) | ISO 13485 audit planning, nonconformity management | 1 |
| [isms-audit-expert](../ra-qm-team/isms-audit-expert/SKILL.md) | ISO 27001 ISMS audits, security control testing | 1 |

### Information Security & Cybersecurity (3)

| Skill | Description | Tools |
|-------|-------------|-------|
| [soc2-compliance-expert](../ra-qm-team/soc2-compliance-expert/SKILL.md) | SOC 2 Type I/II, Trust Services Criteria, evidence collection | 3 |
| [nist-csf-specialist](../ra-qm-team/nist-csf-specialist/SKILL.md) | NIST CSF 2.0, 6 functions, maturity assessment | 2 |
| [pci-dss-specialist](../ra-qm-team/pci-dss-specialist/SKILL.md) | PCI-DSS v4.0, 12 requirements, CDE scoping, tokenization | 2 |

### AI Governance (2)

| Skill | Description | Tools |
|-------|-------------|-------|
| [eu-ai-act-specialist](../ra-qm-team/eu-ai-act-specialist/SKILL.md) | EU AI Act risk classification, GPAI, conformity assessment | 3 |
| [iso42001-ai-management](../ra-qm-team/iso42001-ai-management/SKILL.md) | ISO 42001:2023 AIMS, AI lifecycle governance | 2 |

### Privacy, Financial & Cybersecurity Directives (3)

| Skill | Description | Tools |
|-------|-------------|-------|
| [ccpa-cpra-privacy-expert](../ra-qm-team/ccpa-cpra-privacy-expert/SKILL.md) | CCPA/CPRA consumer privacy, data mapping, opt-out mechanisms | 2 |
| [dora-compliance-expert](../ra-qm-team/dora-compliance-expert/SKILL.md) | DORA 5 pillars, ICT risk management, resilience testing | 2 |
| [nis2-directive-specialist](../ra-qm-team/nis2-directive-specialist/SKILL.md) | NIS2 10 minimum measures, incident reporting, supply chain security | 2 |

### Cross-Cutting Infrastructure (1)

| Skill | Description | Tools |
|-------|-------------|-------|
| [infrastructure-compliance-auditor](../ra-qm-team/infrastructure-compliance-auditor/SKILL.md) | Cross-framework infrastructure security audit (cloud, DNS, TLS, endpoints, CI/CD) | 4 |

### Audit-Prep Playbooks (6)

| Skill | Description | Tools |
|-------|-------------|-------|
| [soc2-audit-prep](../ra-qm-team/audit-prep/soc2-audit-prep/SKILL.md) | 4/8/12-week SOC 2 readiness sprint | 2 |
| [gdpr-audit-prep](../ra-qm-team/audit-prep/gdpr-audit-prep/SKILL.md) | DPA inquiry + customer audit response | 2 |
| [fda-qsr-audit-prep](../ra-qm-team/audit-prep/fda-qsr-audit-prep/SKILL.md) | 21 CFR 820 / QMSR + 483 and warning-letter response | 2 |
| [ai-act-readiness](../ra-qm-team/audit-prep/ai-act-readiness/SKILL.md) | EU AI Act conformity prep + GPAI obligations | 2 |
| [aims-audit](../ra-qm-team/audit-prep/aims-audit/SKILL.md) | ISO 42001 AIMS certification prep | 2 |
| [compliance-readiness](../ra-qm-team/audit-prep/compliance-readiness/SKILL.md) | Multi-framework orchestrator with shared evidence | 3 |

## Business Growth (20)

Revenue optimization, CRO, pricing strategy, and customer success.

| Skill | Description | Tools |
|-------|-------------|-------|
| [customer-success-manager](../business-growth/customer-success-manager/SKILL.md) | Health scoring, churn prediction, expansion analysis | 3 |
| [revenue-operations](../business-growth/revenue-operations/SKILL.md) | Pipeline analytics, forecast accuracy, GTM efficiency | 3 |
| [sales-engineer](../business-growth/sales-engineer/SKILL.md) | RFP analysis, competitive positioning, POC planning | 3 |
| [form-cro](../business-growth/form-cro/SKILL.md) | Form optimization, field reduction, multi-step forms | - |
| [onboarding-cro](../business-growth/onboarding-cro/SKILL.md) | User onboarding optimization, activation, time-to-value | - |
| [page-cro](../business-growth/page-cro/SKILL.md) | Landing page CRO, above-the-fold, social proof | - |
| [paywall-upgrade-cro](../business-growth/paywall-upgrade-cro/SKILL.md) | Paywall optimization, upgrade triggers, pricing pages | - |
| [popup-cro](../business-growth/popup-cro/SKILL.md) | Exit-intent popups, timing optimization, frequency capping | - |
| [signup-flow-cro](../business-growth/signup-flow-cro/SKILL.md) | Registration optimization, SSO, progressive profiling | - |
| [churn-prevention](../business-growth/churn-prevention/SKILL.md) | Churn prediction, retention strategies, win-back campaigns | - |
| [competitive-teardown](../business-growth/competitive-teardown/SKILL.md) | Competitor analysis, feature comparison, positioning gaps | - |
| [competitor-alternatives](../business-growth/competitor-alternatives/SKILL.md) | Alternative positioning, comparison pages, switching guides | - |
| [free-tool-strategy](../business-growth/free-tool-strategy/SKILL.md) | Free tool marketing, product-led growth, conversion funnels | - |
| [pricing-strategy](../business-growth/pricing-strategy/SKILL.md) | Pricing models, value-based pricing, packaging | - |
| [referral-program](../business-growth/referral-program/SKILL.md) | Referral mechanics, viral loops, incentive design | - |
| [contract-and-proposal-writer](../business-growth/contract-and-proposal-writer/SKILL.md) | Contract templates, proposals, SOW, MSA | - |
| [deal-desk](../business-growth/deal-desk/SKILL.md) | Deal desk charter, approval matrix, deal packet, velocity | 3 |
| [channel-economics](../business-growth/channel-economics/SKILL.md) | Channel models, TCO, tier economics, channel mix | 3 |
| [partnerships-architect](../business-growth/partnerships-architect/SKILL.md) | Partnership types, deal structures, evaluation, ROI | 3 |
| [commercial-policy](../business-growth/commercial-policy/SKILL.md) | Policy charter, compliance, deviation handling, generator | 3 |

## Finance (3)

Financial analysis and valuation.

| Skill | Description | Tools |
|-------|-------------|-------|
| [financial-analyst](../finance/financial-analyst/SKILL.md) | DCF valuation, ratio analysis, budget variance, forecasting | 4 |
| [saas-metrics-coach](../finance/saas-metrics-coach/SKILL.md) | MRR, churn, cohort retention, LTV/CAC, unit economics | 3 |
| [business-investment-advisor](../finance/business-investment-advisor/SKILL.md) | Investment screening, portfolio analysis, due diligence, ROI | 3 |

## Data & Analytics (6)

Data-driven insights and ML operations.

| Skill | Description | Tools |
|-------|-------------|-------|
| [data-analyst](../data-analytics/data-analyst/SKILL.md) | SQL, visualization, statistical analysis, reporting | - |
| [data-scientist](../data-analytics/data-scientist/SKILL.md) | ML modeling, experimentation, statistical inference | - |
| [business-intelligence](../data-analytics/business-intelligence/SKILL.md) | Dashboard design, KPI development, data storytelling | - |
| [analytics-engineer](../data-analytics/analytics-engineer/SKILL.md) | dbt, data modeling, transformation, semantic layer | 4 |
| [ml-ops-engineer](../data-analytics/ml-ops-engineer/SKILL.md) | Model deployment, monitoring, feature stores, pipelines | - |
| [statistical-analyst](../data-analytics/statistical-analyst/SKILL.md) | Test selection, assumption checks, power planning, effect sizes | 4 |

## Sales & Success (5)

Revenue generation and customer success.

| Skill | Description | Tools |
|-------|-------------|-------|
| [account-executive](../sales-success/account-executive/SKILL.md) | MEDDIC, pipeline management, negotiation, closing | - |
| [customer-success-manager](../sales-success/customer-success-manager/SKILL.md) | Onboarding, retention, health scoring, expansion | - |
| [sales-engineer](../sales-success/sales-engineer/SKILL.md) | Technical demos, POC design, RFP responses | - |
| [solutions-architect](../sales-success/solutions-architect/SKILL.md) | Solution design, integration architecture, technical sales | - |
| [sales-operations](../sales-success/sales-operations/SKILL.md) | CRM, territory planning, compensation, forecasting | - |

## HR & People (4)

People operations and workforce analytics.

| Skill | Description | Tools |
|-------|-------------|-------|
| [hr-business-partner](../hr-operations/hr-business-partner/SKILL.md) | Talent strategy, performance management, org design | - |
| [talent-acquisition](../hr-operations/talent-acquisition/SKILL.md) | Recruiting, sourcing, employer branding, hiring analytics | - |
| [operations-manager](../hr-operations/operations-manager/SKILL.md) | Process optimization, resource management, efficiency | - |
| [people-analytics](../hr-operations/people-analytics/SKILL.md) | Workforce analytics, predictive modeling, survey analysis | - |

## Legal (17) — EXPERIMENTAL

Contract, privacy, and dispute workflows. Output is decision support, not legal advice.

| Skill | Description | Tools |
|-------|-------------|-------|
| [contract-review](../legal/contract-review/SKILL.md) | Playbook-based agreement review with GREEN/YELLOW/RED severity | 2 |
| [nda-review](../legal/nda-review/SKILL.md) | Clause-by-clause NDA review with redlines, fallbacks, owners | 1 |
| [nda-triage](../legal/nda-triage/SKILL.md) | Rapid NDA screening, 10-point checklist, approval routing | 2 |
| [tech-contract-negotiation](../legal/tech-contract-negotiation/SKILL.md) | Negotiation frameworks for tech services and B2B agreements | 2 |
| [vendor-due-diligence](../legal/vendor-due-diligence/SKILL.md) | IT vendor risk scoring and regulatory compliance checklists | 2 |
| [privacy-compliance](../legal/privacy-compliance/SKILL.md) | Multi-regulation navigator (GDPR, CCPA, LGPD, PIPL, UK GDPR, …) | 2 |
| [privacy-notice-generator](../legal/privacy-notice-generator/SKILL.md) | GDPR privacy notices — 6 types, 9 jurisdictions, layered checks | 2 |
| [dpia-assessment](../legal/dpia-assessment/SKILL.md) | GDPR Art. 35 DPIA with threshold checks and EDPB criteria scoring | 2 |
| [data-breach-response](../legal/data-breach-response/SKILL.md) | ENISA severity scoring, notification timelines, compliance tracking | 2 |
| [legal-risk-assessment](../legal/legal-risk-assessment/SKILL.md) | 5x5 severity × likelihood matrix, risk registers, escalation memos | 2 |
| [statute-analysis](../legal/statute-analysis/SKILL.md) | Statute interpretation, operative keywords, canons of construction | 2 |
| [mediation-analysis](../legal/mediation-analysis/SKILL.md) | Dispute analysis, settlement ranges, interest mapping, strategy | 2 |
| [tabular-document-review](../legal/tabular-document-review/SKILL.md) | Bulk document extraction into a cited comparison matrix | 2 |
| [legal-red-team](../legal/legal-red-team/SKILL.md) | Adversarial verification of AI-generated legal content, citation checks | 2 |
| [legal-canned-responses](../legal/legal-canned-responses/SKILL.md) | Templated responses to common inquiries with escalation detection | 2 |
| [legal-meeting-briefing](../legal/legal-meeting-briefing/SKILL.md) | Structured briefings for legally relevant meetings, action tracking | 2 |
| [whistleblower-compliance](../legal/whistleblower-compliance/SKILL.md) | Whistleblower system audits and compliant reporting policies | 2 |

## Personal Productivity (13)

Individual operating system — capture, focus, review, and the recurring personal deliverables.

| Skill | Description | Tools |
|-------|-------------|-------|
| [capture](../personal-productivity/capture/SKILL.md) | Trusted capture-and-triage front door so no commitment lives in your head | 2 |
| [deep-work](../personal-productivity/deep-work/SKILL.md) | Block defence, session structure, interruption budgets, deep-work ratio | 2 |
| [weekly-review](../personal-productivity/weekly-review/SKILL.md) | Calendar/tasks/journal → wins, learnings, blockers, next-week priorities | 1 |
| [reflect](../personal-productivity/reflect/SKILL.md) | Score predictions against outcomes; track whether commitments held | 3 |
| [email-triage](../personal-productivity/email-triage/SKILL.md) | Batch email classification and unsubscribe candidates | 1 |
| [calendar-prep](../personal-productivity/calendar-prep/SKILL.md) | One-page meeting briefings from attendees, context, decisions needed | 1 |
| [meeting-insights](../personal-productivity/meeting-insights/SKILL.md) | Transcripts → decisions, actions, owners, due dates, risks | 1 |
| [resume-tailor](../personal-productivity/resume-tailor/SKILL.md) | Keyword extraction, match scoring, impact-rewritten bullets | 1 |
| [lead-researcher](../personal-productivity/lead-researcher/SKILL.md) | ICP qualification, lead-list scoring, personalized outreach hooks | 1 |
| [invoice-organizer](../personal-productivity/invoice-organizer/SKILL.md) | Vendor/expense/tax categorization, duplicate detection, monthly summary | 1 |
| [investor-update-generator](../personal-productivity/investor-update-generator/SKILL.md) | Rubric check for transparency, decision-relevance, specific asks | 1 |
| [pitch-deck-reviewer](../personal-productivity/pitch-deck-reviewer/SKILL.md) | Structure and content scoring against well-known investor heuristics | 1 |
| [domain-name-brainstormer](../personal-productivity/domain-name-brainstormer/SKILL.md) | Generate and score names for memorability and pronounceability | 1 |

## Vertical Advisors (7)

Strategic, not implementation — regulatory triggers, business models, and GTM per vertical.

| Skill | Description | Tools |
|-------|-------------|-------|
| [fintech-advisor](../vertical-advisors/fintech-advisor/SKILL.md) | US/EU regulatory triggers, license-vs-partner, KYC/AML, embedded finance | 1 |
| [healthtech-advisor](../vertical-advisors/healthtech-advisor/SKILL.md) | HIPAA scope, FDA SaMD classification, EHR integration, payor/provider GTM | 1 |
| [edtech-advisor](../vertical-advisors/edtech-advisor/SKILL.md) | FERPA/COPPA, K-12 vs higher-ed vs L&D, district sales, pricing | 1 |
| [ecommerce-advisor](../vertical-advisors/ecommerce-advisor/SKILL.md) | Unit economics, fulfillment models, payments, channel strategy | 1 |
| [proptech-advisor](../vertical-advisors/proptech-advisor/SKILL.md) | Real-estate segments, MLS/brokerage models, licensing, business models | 1 |
| [climate-tech-advisor](../vertical-advisors/climate-tech-advisor/SKILL.md) | Carbon markets, GHG accounting, climate regulation, funding | 1 |
| [marketplace-advisor](../vertical-advisors/marketplace-advisor/SKILL.md) | Chicken-and-egg, take rates, liquidity, network effects | 1 |

## Business Operations (6)

Internal operating machinery — capacity, process, vendors, spend, and internal knowledge flow.

| Skill | Description | Tools |
|-------|-------------|-------|
| [capacity-planner](../business-operations/capacity-planner/SKILL.md) | Effective capacity from headcount; hire/contract/defer scenarios; gap reports | 3 |
| [process-mapper](../business-operations/process-mapper/SKILL.md) | SIPOC and swimlane capture, cycle-time and bottleneck analysis | 3 |
| [vendor-management](../business-operations/vendor-management/SKILL.md) | Selection scorecards, risk tiering, renewal deadlines, spend concentration | 3 |
| [procurement-optimizer](../business-operations/procurement-optimizer/SKILL.md) | Seat utilisation, redundant-tool detection, renewal-timing leverage | 3 |
| [internal-comms](../business-operations/internal-comms/SKILL.md) | Sequence and pressure-test reorg, policy, and product announcements | 3 |
| [knowledge-ops](../business-operations/knowledge-ops/SKILL.md) | Knowledge-base staleness, ownership gaps, orphans, duplication, findability | 3 |

## Research (4)

Academic and formal research work — systematic reviews, funding, IP, and intelligence briefings. Distinct from [Research Ops](#research-ops-4), which is the applied/operational side.

| Skill | Description | Tools |
|-------|-------------|-------|
| [litreview](../research/litreview/SKILL.md) | PRISMA-aligned search strategy, source quality scoring, thematic synthesis | 3 |
| [grants](../research/grants/SKILL.md) | Funder fit scoring, proposal structure validation, budget realism checks | 3 |
| [patent](../research/patent/SKILL.md) | Prior-art search planning, claim landscape mapping, patentability scoring | 3 |
| [dossier](../research/dossier/SKILL.md) | Dossier outlines, source triangulation, fact/inference separation | 3 |

## Research Ops (4)

Applied and operational research — sizing markets, running discovery, and budgeting studies. Distinct from the academic [Research](#research-4) domain above.

| Skill | Description | Tools |
|-------|-------------|-------|
| [market-research](../research-ops/market-research/SKILL.md) | TAM/SAM/SOM top-down and bottom-up reconciled, segmentation, survey design | 3 |
| [product-research](../research-ops/product-research/SKILL.md) | Method selection, recruiting and screening, interview guides, evidence scoring | 3 |
| [clinical-research](../research-ops/clinical-research/SKILL.md) | Protocol structure, endpoints, eligibility, power planning, site feasibility | 5 |
| [research-finance](../research-ops/research-finance/SKILL.md) | Study budgets, cost per participant and per insight, burn vs milestones | 3 |

## Documents (4)

Audit tooling for Office and PDF files — stdlib-only OOXML/PDF parsing, no conversion services.

| Skill | Description | Tools |
|-------|-------------|-------|
| [docx-toolkit](../documents/docx-toolkit/SKILL.md) | Heading hierarchy, comments, tracked changes, cross-refs, style consistency | 1 |
| [xlsx-toolkit](../documents/xlsx-toolkit/SKILL.md) | Formula density, external refs, named ranges, hidden sheets, validation | 1 |
| [pptx-toolkit](../documents/pptx-toolkit/SKILL.md) | Slide count, text density, embedded assets, hidden slides, speaker notes | 1 |
| [pdf-toolkit](../documents/pdf-toolkit/SKILL.md) | Metadata leakage, encryption, JavaScript, embedded files, version | 1 |

## Markdown-HTML (4)

The markdown → HTML publishing pipeline: authored Markdown becomes a self-contained document or deck. Stdlib-only with zero network calls — distinct from [Documents](#documents-4), which parses existing OOXML and PDF files.

| Skill | Description | Tools |
|-------|-------------|-------|
| [md-document](../markdown-html/md-document/SKILL.md) | Self-contained HTML report: TOC, numbered figures/tables, footnotes, print CSS | 4 |
| [md-slides](../markdown-html/md-slides/SKILL.md) | Self-contained HTML deck: layouts, speaker notes, keyboard nav, density linter | 4 |
| [md-review](../markdown-html/md-review/SKILL.md) | Pre-publication gate: heading structure, link resolution, readability, a11y | 3 |
| [design-system](../markdown-html/design-system/SKILL.md) | Design tokens, light/dark theming, WCAG contrast, one inlinable CSS bundle | 3 |

## Workflow (2)

Meta-skills for routing work and handing it off.

| Skill | Description | Tools |
|-------|-------------|-------|
| [skill-router](../workflow/skill-router/SKILL.md) | Match a vague or cross-domain request to the right skill | 1 |
| [handoff](../workflow/handoff/SKILL.md) | Package in-flight work as a context doc for another person or agent | 1 |
