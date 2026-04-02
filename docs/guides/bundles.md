---
title: Starter Bundles
---

# Starter Bundles

Pre-selected skill sets for common professional roles. Copy the skills you need instead of installing all 224.

## Frontend Developer

**10 skills** for React/Next.js development with testing, accessibility, and performance.

```bash
# Core skills
engineering/senior-frontend        # React, Next.js, TypeScript, Tailwind
engineering/senior-fullstack       # Project scaffolding, code quality
engineering/a11y-audit             # WCAG accessibility scanning
engineering/performance-profiler   # Bundle analysis, Core Web Vitals
engineering/tdd-guide              # Test-driven development
engineering/playwright-pro         # E2E testing
engineering/design-auditor         # UI/UX audit
product-team/design-system-lead   # Component library management
engineering/code-reviewer          # PR review automation
engineering/tech-debt-tracker      # Technical debt tracking
```

## Backend / API Developer

**8 skills** for API design, database optimization, and security.

```bash
engineering/senior-backend         # REST APIs, microservices, GraphQL
engineering/api-design-reviewer    # OpenAPI linting, breaking changes
engineering/api-test-suite-builder # Auth testing, load testing with k6
engineering/database-designer      # Schema design, index optimization
engineering/senior-security        # OWASP, threat modeling
engineering/senior-devops          # CI/CD, containers, IaC
engineering/incident-commander     # Incident response, postmortems
engineering/observability-designer # SLI/SLO, alerting, dashboards
```

## DevOps / Platform Engineer

**9 skills** for infrastructure, deployment, and reliability.

```bash
engineering/senior-devops          # Terraform, Kubernetes, CI/CD
engineering/ci-cd-pipeline-builder # GitHub Actions, GitLab CI
engineering/docker-development     # Dockerfile optimization
engineering/helm-chart-builder     # Kubernetes Helm charts
engineering/terraform-patterns     # IaC security and best practices
engineering/observability-designer # Monitoring and alerting
engineering/incident-commander     # Incident response
engineering/runbook-generator      # Operational runbooks
engineering/secrets-vault-manager  # HashiCorp Vault, secret rotation
```

## Product Manager

**10 skills** for discovery, execution, and stakeholder management.

```bash
product-team/product-manager-toolkit     # RICE, PRDs, discovery
product-team/ux-researcher-designer      # User research, personas
project-management/execution/create-prd  # PRD scaffolding
project-management/execution/brainstorm-okrs  # OKR creation
project-management/discovery/brainstorm-ideas # Opportunity Solution Trees
project-management/discovery/pre-mortem       # Risk analysis
project-management/execution/prioritization-frameworks  # 9 methods
project-management/scrum-master              # Sprint management
product-team/ab-test-setup                   # Experiment design
project-management/execution/release-notes   # Release communication
```

## Marketing Lead

**10 skills** for content, SEO, demand gen, and analytics.

```bash
marketing/content-strategy         # Content pillars, editorial planning
marketing/content-production       # Full content pipeline
marketing/seo-specialist           # Technical SEO, keyword research
marketing/seo-audit                # 85-point SEO audit
marketing/copywriting              # Homepage, landing page copy
marketing/paid-ads                 # Multi-platform ad management
marketing/email-sequence           # Email automation sequences
marketing/campaign-analytics       # Attribution, ROI calculation
marketing/marketing-context        # ICP, positioning, brand voice
marketing/launch-strategy          # Product launch playbooks
```

## Startup Founder

**12 skills** spanning strategy, product, engineering, and growth.

```bash
c-level-advisor/ceo-advisor        # Strategic decision-making
c-level-advisor/cto-advisor        # Technical strategy
c-level-advisor/cfo-advisor        # Financial planning
c-level-advisor/board-deck-builder # Investor updates
business-growth/pricing-strategy   # SaaS pricing design
business-growth/churn-prevention   # Retention optimization
marketing/marketing-strategy-pmm   # Product marketing, GTM
finance/saas-metrics-coach         # MRR/ARR, unit economics
engineering/senior-fullstack       # Development
engineering/saas-scaffolder        # SaaS boilerplate
product-team/product-manager-toolkit  # Feature prioritization
project-management/execution/brainstorm-okrs  # Goal setting
```

## Compliance Officer

**8 skills** for multi-framework compliance management.

```bash
ra-qm-team/soc2-compliance-expert              # SOC 2 Type I/II
ra-qm-team/gdpr-dsgvo-expert                   # GDPR privacy
ra-qm-team/information-security-manager-iso27001 # ISO 27001 ISMS
ra-qm-team/nist-csf-specialist                 # NIST CSF 2.0
ra-qm-team/pci-dss-specialist                  # PCI DSS v4.0
ra-qm-team/eu-ai-act-specialist                # EU AI Act
ra-qm-team/infrastructure-compliance-auditor   # Infrastructure audit
ra-qm-team/ccpa-cpra-privacy-expert            # California privacy
```

## Installing a Bundle

Copy the skills you need:

```bash
# Clone the repo
git clone https://github.com/borghei/Claude-Skills.git

# Copy a bundle's skills to your project
for skill in engineering/senior-frontend engineering/a11y-audit engineering/tdd-guide; do
  cp -r "Claude-Skills/$skill" ".claude/skills/$(basename $skill)"
done
```

Or use the installer:

```bash
python Claude-Skills/scripts/skill-installer.py install senior-frontend a11y-audit tdd-guide --agent claude
```
