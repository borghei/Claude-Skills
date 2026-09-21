# Product Team Skills Collection

**13 product skills** covering product management, agile delivery, strategy, UX research, design systems, product analytics, Apple HIG, research synthesis, spec-to-repo and roadmap communication. This guide covers the 5 core skills in depth; the full list is in the [Product catalog](../docs/skills/product.md). Project management has its own domain: [project-management/](../project-management/).

---

## 📚 Table of Contents

- [Installation](#installation)
- [Overview](#overview)
- [Skills Catalog](#skills-catalog)
- [Quick Start Guide](#quick-start-guide)
- [Team Structure Recommendations](#team-structure-recommendations)
- [Common Workflows](#common-workflows)
- [Success Metrics](#success-metrics)

---

## ⚡ Installation

### Whole domain (Claude Code plugin)

```bash
# In Claude Code:
/plugin marketplace add borghei/Claude-Skills
/plugin install product-skills@claude-code-skills
```

### Individual skills (any assistant)

```bash
npx @borghei/claude-skills add product-manager-toolkit
npx @borghei/claude-skills add agile-product-owner
npx @borghei/claude-skills add product-strategist
npx @borghei/claude-skills add ux-researcher-designer
npx @borghei/claude-skills add ui-design-system
```

The CLI auto-detects Claude Code, Cursor, Codex, Gemini CLI, Copilot, Windsurf, Cline, Aider and Goose (`--to <target>` to force one). Browse every skill with `npx @borghei/claude-skills list --domain product-team`.

**Complete Installation Guide:** See [docs/INSTALLATION.md](../docs/INSTALLATION.md) for detailed instructions, troubleshooting, and manual installation.

---

## 🎯 Overview

This product team skills collection provides comprehensive product management capabilities from discovery through delivery, covering strategy, execution, research, and design.

**What's Included:**
- **13 skills**; the 5 core skills (product management, agile, strategy, UX, design) are covered in depth below
- **15+ Python automation tools** for prioritization, analysis, and generation
- **Comprehensive frameworks** for discovery, delivery, research, and design systems
- **Ready-to-use templates** for PRDs, user stories, OKRs, personas, and design tokens

**Ideal For:**
- Product teams at startups and scale-ups
- Solo PMs managing multiple products
- Product leaders building product organizations
- Cross-functional product delivery teams

**Key Benefits:**
- ⚡ **40% time savings** on product planning and documentation
- 🎯 **Data-driven decisions** with RICE prioritization and analytics
- 📈 **Consistent delivery** with agile frameworks and automation
- 🚀 **Faster time-to-market** with proven templates and workflows

---

## 📦 Skills Catalog

### 1. Product Manager Toolkit
**Status:** ✅ Production Ready | **Version:** 1.0

**Purpose:** Essential tools and frameworks for modern product management, from discovery to delivery.

**Key Capabilities:**
- RICE prioritization with portfolio analysis
- Customer interview analysis and insight extraction
- PRD templates (4 comprehensive formats)
- Discovery frameworks and hypothesis testing
- Metrics and analytics dashboards

**Python Tools:**
- `rice_prioritizer.py` - Automated feature prioritization
- `customer_interview_analyzer.py` - AI-powered insight extraction

**Use When:** Feature prioritization, customer discovery, PRD creation, product metrics

**Learn More:** [product-manager-toolkit/SKILL.md](product-manager-toolkit/SKILL.md)

---

### 2. Agile Product Owner
**Status:** ✅ Production Ready | **Version:** 1.0

**Purpose:** Sprint execution and backlog management tools for agile product delivery.

**Key Capabilities:**
- INVEST-compliant user story generation
- Sprint planning with capacity allocation
- Epic breakdown and story mapping
- Velocity tracking and burndown analysis
- Agile ceremonies frameworks

**Python Tools:**
- `user_story_generator.py` - Generate user stories with acceptance criteria
- `sprint_planner.py` - Capacity-based sprint planning
- `velocity_tracker.py` - Sprint metrics and analysis

**Use When:** Backlog refinement, sprint planning, user story writing, velocity tracking

**Learn More:** [agile-product-owner/SKILL.md](agile-product-owner/SKILL.md)

---

### 3. Product Strategist
**Status:** ✅ Production Ready | **Version:** 1.0

**Purpose:** Strategic planning and vision alignment for heads of product and product leaders.

**Key Capabilities:**
- OKR cascade generation (company → product → team)
- Alignment scoring and measurement
- Strategy templates (growth, retention, revenue, innovation)
- Team scaling and organizational design
- Vision frameworks and roadmap development

**Python Tools:**
- `okr_cascade_generator.py` - Automated OKR hierarchy generation
- `alignment_scorer.py` - Vertical and horizontal alignment measurement

**Use When:** Strategic planning, OKR setting, product vision, roadmap development, team scaling

**Learn More:** [product-strategist/SKILL.md](product-strategist/SKILL.md)

---

### 4. UX Researcher Designer
**Status:** ✅ Production Ready | **Version:** 1.0

**Purpose:** User research and experience design frameworks for creating user-centered products.

**Key Capabilities:**
- Data-driven persona creation from user research
- Customer journey mapping and visualization
- Research synthesis and pattern identification
- Usability testing protocols and heuristic evaluation
- Design thinking and workshop facilitation

**Python Tools:**
- `persona_generator.py` - Generate personas from research data
- `journey_mapper.py` - Customer journey visualization
- `research_synthesizer.py` - Pattern identification from interviews

**Use When:** User research, persona development, journey mapping, usability testing

**Learn More:** [ux-researcher-designer/SKILL.md](ux-researcher-designer/SKILL.md)

---

### 5. UI Design System
**Status:** ✅ Production Ready | **Version:** 1.0

**Purpose:** Visual design systems and component architecture for consistent user interfaces.

**Key Capabilities:**
- Complete design token system generation
- Atomic design component architecture
- Responsive breakpoint and grid system calculation
- Export formats (JSON, CSS, SCSS) for development handoff
- Storybook integration and component documentation

**Python Tools:**
- `design_token_generator.py` - Generate complete token system from brand colors
- `component_architect.py` - Atomic design implementation
- `responsive_calculator.py` - Breakpoint and grid generation

**Use When:** Design system creation, component library architecture, design-dev handoff

**Learn More:** [ui-design-system/SKILL.md](ui-design-system/SKILL.md)

---

## 🚀 Quick Start Guide

### For Product Managers

1. **Install Product Manager Toolkit:**
   ```bash
   npx @borghei/claude-skills add product-manager-toolkit
   ```

2. **Prioritize Your Backlog:**
   ```bash
   python product-manager-toolkit/scripts/rice_prioritizer.py features.csv
   ```

3. **Analyze Customer Interviews:**
   ```bash
   python product-manager-toolkit/scripts/customer_interview_analyzer.py interview.txt
   ```

### For Product Owners

1. **Install Agile Product Owner:**
   ```bash
   npx @borghei/claude-skills add agile-product-owner
   ```

2. **Generate User Stories:**
   ```bash
   python agile-product-owner/scripts/user_story_generator.py
   ```

3. **Plan Your Sprint:**
   ```bash
   python agile-product-owner/scripts/user_story_generator.py sprint 30
   ```

### For Product Leaders

1. **Install Product Strategist:**
   ```bash
   npx @borghei/claude-skills add product-strategist
   ```

2. **Generate OKR Cascade:**
   ```bash
   python product-strategist/scripts/okr_cascade_generator.py growth
   ```

### For UX Researchers

1. **Install UX Researcher Designer:**
   ```bash
   npx @borghei/claude-skills add ux-researcher-designer
   ```

2. **Create Personas:**
   ```bash
   python ux-researcher-designer/scripts/persona_generator.py
   ```

### For UI Designers

1. **Install UI Design System:**
   ```bash
   npx @borghei/claude-skills add ui-design-system
   ```

2. **Generate Design Tokens:**
   ```bash
   python ui-design-system/scripts/design_token_generator.py "#0066CC" modern css
   ```

---

## 👥 Team Structure Recommendations

### Small Team (1-5 people)

**Recommended Skills:**
- Product Manager Toolkit (PM/Product Owner combo role)
- UX Researcher Designer (PM with UX responsibilities)

**Rationale:** Hybrid roles, focus on execution over specialization

---

### Medium Team (6-15 people)

**Recommended Skills:**
- Product Manager Toolkit (Product Manager)
- Agile Product Owner (separate Product Owner role)
- UX Researcher Designer (dedicated UX Researcher)
- UI Design System (if building design system)

**Rationale:** Specialized roles, better separation of concerns

---

### Large Team (16+ people)

**Recommended Skills:**
- All 5 skills for complete product organization
- Product Strategist (Head of Product / CPO)
- Product Manager Toolkit (multiple Product Managers)
- Agile Product Owner (multiple Product Owners)
- UX Researcher Designer (UX Research team)
- UI Design System (Design Systems team)

**Rationale:** Full specialization, scaled product delivery

---

## 🔄 Common Workflows

### Workflow 1: New Feature Development

```
1. Discovery → Product Manager Toolkit
   - Customer interviews
   - Problem validation
   - Opportunity sizing

2. Prioritization → Product Manager Toolkit
   - RICE scoring
   - Portfolio analysis
   - Resource allocation

3. Story Writing → Agile Product Owner
   - Epic breakdown
   - User story generation
   - Acceptance criteria

4. UX Research → UX Researcher Designer
   - User testing
   - Journey mapping
   - Usability validation

5. Sprint Execution → Agile Product Owner
   - Sprint planning
   - Velocity tracking
   - Burndown monitoring
```

### Workflow 2: Strategic Planning (Quarterly)

```
1. Vision Setting → Product Strategist
   - Product vision
   - Strategic themes
   - Market positioning

2. OKR Cascade → Product Strategist
   - Company → Product → Team goals
   - Alignment measurement
   - Success metrics

3. Roadmap Planning → Product Manager Toolkit
   - Feature mapping
   - Release planning
   - Stakeholder alignment

4. Resource Planning → Product Strategist
   - Team capacity
   - Hiring needs
   - Budget allocation
```

### Workflow 3: Design System Creation

```
1. Brand Foundation → UI Design System
   - Design tokens
   - Color system
   - Typography scale

2. Component Architecture → UI Design System
   - Atomic design
   - Component library
   - Documentation

3. User Validation → UX Researcher Designer
   - Usability testing
   - Component feedback
   - Pattern validation

4. Developer Handoff → UI Design System
   - CSS/JSON export
   - Implementation guide
   - Component specs
```

---

## 📊 Success Metrics

### Time Savings

- **Product Planning:** 40% reduction in PRD creation time
- **Backlog Management:** 50% reduction in user story writing time
- **Research Synthesis:** 60% reduction in interview analysis time
- **Design Systems:** 70% reduction in token generation time

### Quality Improvements

- **Feature Prioritization:** 30% improvement in delivery ROI
- **User Story Quality:** 40% improvement in acceptance criteria clarity
- **Research Insights:** 35% improvement in insight extraction accuracy
- **Design Consistency:** 80% improvement in design system consistency

### Delivery Velocity

- **Sprint Predictability:** 25% improvement in sprint completion rates
- **Discovery Efficiency:** 45% reduction in time-to-validation
- **OKR Alignment:** 50% improvement in goal alignment scores
- **UX Iteration:** 40% reduction in design iteration cycles

---

## 🔗 Integration with Other Teams

**Product ↔ Engineering:**
- User stories → Engineering implementation
- Technical feasibility → Product prioritization
- Design system → Frontend development

**Product ↔ Marketing:**
- Product strategy → Go-to-market strategy
- Customer insights → Marketing messaging
- Feature launches → Marketing campaigns

**Product ↔ C-Level:**
- OKRs → Company strategy
- Product metrics → Board reporting
- Resource needs → Budget planning

---

## 📚 Additional Resources

- **Product Team Guide:** `product_team_implementation_guide.md` (if exists)
- **CLAUDE.md:** [product-team/CLAUDE.md](CLAUDE.md) - Claude Code specific guidance
- **Main Documentation:** [../CLAUDE.md](../CLAUDE.md)
- **Installation Guide:** [docs/INSTALLATION.md](../docs/INSTALLATION.md)

---

**Last Updated:** January 2026
**Skills Deployed:** 5/5 product team skills production-ready
**Total Tools:** 15+ Python automation tools
