# Installation Guide - AI Skills Library

Complete installation guide for all 97 production-ready skills across 13 domains, 178 Python tools, 6 subagents, and 12 GitHub workflows. Works with Claude Code, Cursor, Copilot, Codex, Windsurf, Cline, Aider, Goose, and more.

## Table of Contents

- [Quick Start](#quick-start)
- [Skill Installer CLI (New!)](#skill-installer-cli-new)
- [Claude Code Native Marketplace](#claude-code-native-marketplace-new)
- [Universal Installer](#universal-installer)
- [OpenAI Codex Installation](#openai-codex-installation)
- [Per-Skill Installation](#per-skill-installation)
- [Auto-Update](#auto-update)
- [Multi-Agent Setup](#multi-agent-setup)
- [Manual Installation](#manual-installation)
- [Verification & Testing](#verification--testing)
- [Troubleshooting](#troubleshooting)
- [Uninstallation](#uninstallation)

---

## Quick Start

**Choose your agent:**

### For Claude Code Users (Recommended)

```bash
# In Claude Code, run:
/plugin marketplace add borghei/Claude-Skills
/plugin install marketing-skills@claude-code-skills
```

Native integration with automatic updates and version management.

### For OpenAI Codex Users

```bash
# Option 1: Universal installer
npx agent-skills-cli add borghei/Claude-Skills --agent codex

# Option 2: Direct installation script
git clone https://github.com/borghei/Claude-Skills.git
cd claude-skills
./scripts/codex-install.sh
```

Skills install to `~/.codex/skills/`. See [OpenAI Codex Installation](#openai-codex-installation) for detailed instructions.

### For Windsurf Users

```bash
git clone https://github.com/borghei/Claude-Skills.git
cd Claude-Skills
python scripts/skill-installer.py install senior-fullstack --agent windsurf
```

Windsurf auto-detects the `.windsurfrules` config file from the project root.

### For Cline Users

```bash
git clone https://github.com/borghei/Claude-Skills.git
cd Claude-Skills
python scripts/skill-installer.py install senior-fullstack --agent cline
```

Cline auto-detects the `.clinerules` config file from the project root.

### For Aider Users

```bash
git clone https://github.com/borghei/Claude-Skills.git
cd Claude-Skills
# Aider reads AGENTS.md automatically
python scripts/skill-installer.py list
```

### For All Other Agents (Goose, Jules, RooCode, etc.)

```bash
npx agent-skills-cli add borghei/Claude-Skills
```

This single command installs all skills to all supported agents automatically.

**What this does:**
- ✅ Detects all 53 skills automatically
- ✅ Installs to Claude, Cursor, Copilot, Windsurf, Cline, and 37+ other AI agents
- ✅ Works across all skill formats

Learn more: https://www.agentskills.in

---

## Skill Installer CLI (New!)

Install **one skill per domain group** into your project with built-in auto-update support. This is the recommended way to pick individual skills.

### List Available Skills

```bash
# List all 97 skills across 13 domains
python scripts/skill-installer.py list

# List skills in a specific group
python scripts/skill-installer.py list --group engineering-team
python scripts/skill-installer.py list --group marketing-skill
python scripts/skill-installer.py list --group ra-qm-team
```

### Install a Skill

```bash
# Install to generic .skills/ directory (default)
python scripts/skill-installer.py install content-creator

# Install to a specific agent
python scripts/skill-installer.py install senior-fullstack --agent claude
python scripts/skill-installer.py install ceo-advisor --agent cursor
python scripts/skill-installer.py install product-manager-toolkit --agent vscode

# Install with auto-update enabled
python scripts/skill-installer.py install senior-devops --agent claude --auto-update
```

**One-per-group policy:** By default, you can install one skill per domain group (e.g., one from `engineering-team`, one from `marketing-skill`). Use `--force` to override.

### Update Installed Skills

```bash
# Update all skills with auto-update enabled
python scripts/skill-installer.py update

# Update a specific skill (even without auto-update)
python scripts/skill-installer.py update content-creator
```

### Check Status

```bash
# Show all installed skills
python scripts/skill-installer.py status
python scripts/skill-installer.py status --agent claude
```

### Remove a Skill

```bash
python scripts/skill-installer.py uninstall content-creator
```

### Available Domain Groups

| Group | Skills | Highlights |
|-------|--------|------------|
| **engineering-team** | 24 | fullstack, devops, security, AI/ML, mobile, cloud |
| **engineering** | 12 | agent-designer, rag-architect, database-designer |
| **ra-qm-team** | 12 | ISO 13485, MDR, FDA, GDPR, audit |
| **marketing-skill** | 10 | content, SEO, ASO, analytics, growth |
| **project-management** | 9 | PM, scrum, Jira, Confluence, delivery |
| **product-team** | 7 | product manager, UX, design systems |
| **c-level-advisor** | 5 | CEO, CTO, CFO, CMO, COO |
| **data-analytics** | 5 | data analyst, BI, analytics engineer |
| **sales-success** | 5 | account exec, sales engineer, CS |
| **hr-operations** | 4 | talent, people analytics, HR partner |
| **business-growth** | 3 | customer success, revenue ops |
| **finance** | 1 | financial analyst |

---

## Claude Code Native Marketplace (New!)

**Best for Claude Code users** - Native integration with Claude Code's plugin system.

### Add the Marketplace

```bash
# In Claude Code, run:
/plugin marketplace add borghei/Claude-Skills
```

This adds the skills library to your available marketplaces.

### Install Skill Bundles

```bash
# Install by domain (bundles of skills)
/plugin install marketing-skills@claude-code-skills     # 6 marketing skills
/plugin install engineering-skills@claude-code-skills   # 18 engineering skills
/plugin install product-skills@claude-code-skills       # 5 product skills
/plugin install c-level-skills@claude-code-skills       # 2 C-level advisory skills
/plugin install pm-skills@claude-code-skills            # 6 project management skills
/plugin install ra-qm-skills@claude-code-skills         # 12 regulatory/quality skills
```

### Install Individual Skills

```bash
# Marketing
/plugin install content-creator@claude-code-skills
/plugin install demand-gen@claude-code-skills

# Engineering
/plugin install fullstack-engineer@claude-code-skills
/plugin install aws-architect@claude-code-skills

# Product
/plugin install product-manager@claude-code-skills

# Project Management
/plugin install scrum-master@claude-code-skills
```

### Update Skills

```bash
# Update all installed plugins
/plugin update

# Update specific plugin
/plugin update marketing-skills
```

### Remove Skills

```bash
# Remove specific plugin
/plugin remove marketing-skills

# Remove marketplace
/plugin marketplace remove claude-code-skills
```

**Benefits:**
- ✅ Native Claude Code integration
- ✅ Automatic updates with `/plugin update`
- ✅ Version management with git tags
- ✅ Skills installed to `~/.claude/skills/`
- ✅ Managed through Claude Code UI

---

## Universal Installer

The universal installer uses the [Agent Skills CLI](https://github.com/Karanjot786/agent-skills-cli) package to install skills across multiple agents simultaneously.

### Install All Skills

```bash
# Install to all supported agents
npx agent-skills-cli add borghei/Claude-Skills
```

**This installs to:**
- Claude Code → `~/.claude/skills/`
- Cursor → `.cursor/skills/`
- VS Code/Copilot → `.github/skills/`
- Goose → `~/.config/goose/skills/`
- Amp → Platform-specific location
- Codex → Platform-specific location
- Letta → Platform-specific location
- OpenCode → Platform-specific location

### Install to Specific Agent

```bash
# Claude Code only
npx agent-skills-cli add borghei/Claude-Skills --agent claude

# Cursor only
npx agent-skills-cli add borghei/Claude-Skills --agent cursor

# VS Code/Copilot only
npx agent-skills-cli add borghei/Claude-Skills --agent vscode

# Goose only
npx agent-skills-cli add borghei/Claude-Skills --agent goose

# Project-specific installation (portable)
npx agent-skills-cli add borghei/Claude-Skills --agent project
```

### Preview Before Installing

```bash
# Dry run to see what will be installed
npx agent-skills-cli add borghei/Claude-Skills --dry-run
```

---

## Per-Skill Installation

Install individual skills instead of the entire library:

### Marketing Skills

```bash
# Content Creator
npx agent-skills-cli add borghei/Claude-Skills/marketing-skill/content-creator

# Demand Generation & Acquisition
npx agent-skills-cli add borghei/Claude-Skills/marketing-skill/marketing-demand-acquisition

# Product Marketing Strategy
npx agent-skills-cli add borghei/Claude-Skills/marketing-skill/marketing-strategy-pmm

# App Store Optimization
npx agent-skills-cli add borghei/Claude-Skills/marketing-skill/app-store-optimization

# Social Media Analyzer
npx agent-skills-cli add borghei/Claude-Skills/marketing-skill/social-media-analyzer
```

### C-Level Advisory Skills

```bash
# CEO Advisor
npx agent-skills-cli add borghei/Claude-Skills/c-level-advisor/ceo-advisor

# CTO Advisor
npx agent-skills-cli add borghei/Claude-Skills/c-level-advisor/cto-advisor
```

### Product Team Skills

```bash
# Product Manager Toolkit
npx agent-skills-cli add borghei/Claude-Skills/product-team/product-manager-toolkit

# Agile Product Owner
npx agent-skills-cli add borghei/Claude-Skills/product-team/agile-product-owner

# Product Strategist
npx agent-skills-cli add borghei/Claude-Skills/product-team/product-strategist

# UX Researcher Designer
npx agent-skills-cli add borghei/Claude-Skills/product-team/ux-researcher-designer

# UI Design System
npx agent-skills-cli add borghei/Claude-Skills/product-team/ui-design-system
```

### Project Management Skills

```bash
# Senior PM Expert
npx agent-skills-cli add borghei/Claude-Skills/project-management/senior-pm-expert

# Scrum Master Expert
npx agent-skills-cli add borghei/Claude-Skills/project-management/scrum-master-expert

# Atlassian Jira Expert
npx agent-skills-cli add borghei/Claude-Skills/project-management/atlassian-jira-expert

# Atlassian Confluence Expert
npx agent-skills-cli add borghei/Claude-Skills/project-management/atlassian-confluence-expert

# Atlassian Administrator
npx agent-skills-cli add borghei/Claude-Skills/project-management/atlassian-administrator

# Atlassian Template Creator
npx agent-skills-cli add borghei/Claude-Skills/project-management/atlassian-template-creator
```

### Engineering Team Skills

```bash
# Core Engineering
npx agent-skills-cli add borghei/Claude-Skills/engineering-team/senior-architect
npx agent-skills-cli add borghei/Claude-Skills/engineering-team/senior-frontend
npx agent-skills-cli add borghei/Claude-Skills/engineering-team/senior-backend
npx agent-skills-cli add borghei/Claude-Skills/engineering-team/senior-fullstack
npx agent-skills-cli add borghei/Claude-Skills/engineering-team/senior-qa
npx agent-skills-cli add borghei/Claude-Skills/engineering-team/senior-devops
npx agent-skills-cli add borghei/Claude-Skills/engineering-team/senior-secops
npx agent-skills-cli add borghei/Claude-Skills/engineering-team/code-reviewer
npx agent-skills-cli add borghei/Claude-Skills/engineering-team/senior-security

# Cloud & Enterprise
npx agent-skills-cli add borghei/Claude-Skills/engineering-team/aws-solution-architect
npx agent-skills-cli add borghei/Claude-Skills/engineering-team/ms365-tenant-manager

# Development Tools
npx agent-skills-cli add borghei/Claude-Skills/engineering-team/tdd-guide
npx agent-skills-cli add borghei/Claude-Skills/engineering-team/tech-stack-evaluator

# AI/ML/Data
npx agent-skills-cli add borghei/Claude-Skills/engineering-team/senior-data-scientist
npx agent-skills-cli add borghei/Claude-Skills/engineering-team/senior-data-engineer
npx agent-skills-cli add borghei/Claude-Skills/engineering-team/senior-ml-engineer
npx agent-skills-cli add borghei/Claude-Skills/engineering-team/senior-prompt-engineer
npx agent-skills-cli add borghei/Claude-Skills/engineering-team/senior-computer-vision
```

### Regulatory Affairs & Quality Management Skills

```bash
# Regulatory & Quality Leadership
npx agent-skills-cli add borghei/Claude-Skills/ra-qm-team/regulatory-affairs-head
npx agent-skills-cli add borghei/Claude-Skills/ra-qm-team/quality-manager-qmr
npx agent-skills-cli add borghei/Claude-Skills/ra-qm-team/quality-manager-qms-iso13485

# Quality Processes
npx agent-skills-cli add borghei/Claude-Skills/ra-qm-team/capa-officer
npx agent-skills-cli add borghei/Claude-Skills/ra-qm-team/quality-documentation-manager
npx agent-skills-cli add borghei/Claude-Skills/ra-qm-team/risk-management-specialist

# Security & Privacy
npx agent-skills-cli add borghei/Claude-Skills/ra-qm-team/information-security-manager-iso27001
npx agent-skills-cli add borghei/Claude-Skills/ra-qm-team/gdpr-dsgvo-expert

# Regional Compliance
npx agent-skills-cli add borghei/Claude-Skills/ra-qm-team/mdr-745-specialist
npx agent-skills-cli add borghei/Claude-Skills/ra-qm-team/fda-consultant-specialist

# Audit & Assessment
npx agent-skills-cli add borghei/Claude-Skills/ra-qm-team/qms-audit-expert
npx agent-skills-cli add borghei/Claude-Skills/ra-qm-team/isms-audit-expert
```

---

## Auto-Update

Keep your installed skills up to date automatically.

### Method 1: Skill Installer CLI (Recommended)

```bash
# Pull latest repository changes
git pull origin main

# Update all skills with auto-update enabled
python scripts/skill-installer.py update

# Update a specific skill
python scripts/skill-installer.py update senior-fullstack --agent claude
```

### Method 2: GitHub Action (CI/CD)

The repository includes a `skill-auto-update.yml` workflow that:
- Runs daily at 6 AM UTC
- Detects which skills changed
- Generates an update manifest
- Can be triggered manually via `workflow_dispatch`

To use in your own project, add this to your CI:

```yaml
# .github/workflows/update-skills.yml
name: Update Claude Skills
on:
  schedule:
    - cron: '0 6 * * 1'  # Weekly on Monday
  workflow_dispatch:

jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: |
          git clone https://github.com/borghei/Claude-Skills.git /tmp/claude-skills
          cd /tmp/claude-skills
          python scripts/skill-installer.py update --agent project
```

### Method 3: Git Submodule

For tighter integration, add the skills repo as a submodule:

```bash
# Add as submodule
git submodule add https://github.com/borghei/Claude-Skills.git .claude-skills

# Update to latest
git submodule update --remote .claude-skills
```

### Update Manifest

When you install skills with `--auto-update`, a `.claude-skills.json` manifest is created in your target directory. This tracks:
- Which skills are installed
- Which group each skill belongs to
- When each skill was last updated
- Whether auto-update is enabled per skill

---

## Multi-Agent Setup

Install the same skills across different agents for team consistency:

### Example: Marketing Team Setup

```bash
# Install marketing skills to Claude Code (for content strategist)
npx agent-skills-cli add borghei/Claude-Skills/marketing-skill/content-creator --agent claude

# Install same skills to Cursor (for developer working on content)
npx agent-skills-cli add borghei/Claude-Skills/marketing-skill/content-creator --agent cursor

# Install to VS Code (for SEO specialist)
npx agent-skills-cli add borghei/Claude-Skills/marketing-skill/content-creator --agent vscode
```

### Example: Engineering Team Setup

```bash
# Full engineering suite to Claude Code
npx agent-skills-cli add borghei/Claude-Skills/engineering-team --agent claude

# Same suite to Cursor
npx agent-skills-cli add borghei/Claude-Skills/engineering-team --agent cursor
```

---

## Manual Installation

For development, customization, or offline use:

### Prerequisites

- **Python 3.7+** (for running analysis scripts)
- **Git** (for cloning repository)
- **Claude AI account** or **Claude Code** (for using skills)

### Step 1: Clone Repository

```bash
git clone https://github.com/borghei/Claude-Skills.git
cd claude-skills
```

### Step 2: Install Dependencies (Optional)

Most scripts use Python standard library only:

```bash
# Optional dependencies for future features
pip install pyyaml
```

### Step 3: Manual Copy to Agent Directory

#### For Claude Code

```bash
# Copy all skills
cp -r marketing-skill ~/.claude/skills/
cp -r c-level-advisor ~/.claude/skills/
cp -r product-team ~/.claude/skills/
cp -r project-management ~/.claude/skills/
cp -r engineering-team ~/.claude/skills/
cp -r ra-qm-team ~/.claude/skills/

# Or copy single skill
cp -r marketing-skill/content-creator ~/.claude/skills/content-creator
```

#### For Cursor

```bash
# Copy to project directory
mkdir -p .cursor/skills
cp -r marketing-skill .cursor/skills/
```

#### For VS Code/Copilot

```bash
# Copy to project directory
mkdir -p .github/skills
cp -r engineering-team .github/skills/
```

### Step 4: Verify Python Tools

```bash
# Test marketing tools
python marketing-skill/content-creator/scripts/brand_voice_analyzer.py --help
python marketing-skill/content-creator/scripts/seo_optimizer.py --help

# Test C-level tools
python c-level-advisor/cto-advisor/scripts/tech_debt_analyzer.py --help
python c-level-advisor/ceo-advisor/scripts/strategy_analyzer.py --help

# Test product tools
python product-team/product-manager-toolkit/scripts/rice_prioritizer.py --help
python product-team/ui-design-system/scripts/design_token_generator.py --help
```

---

## Verification & Testing

### Verify Universal Installer Installation

```bash
# Check Claude Code installation
ls ~/.claude/skills/

# Check Cursor installation
ls .cursor/skills/

# Check VS Code installation
ls .github/skills/

# Check Goose installation
ls ~/.config/goose/skills/
```

### Test Skill Usage

#### In Claude Code

1. Open Claude Code
2. Start a new conversation
3. Test a skill:
   ```
   Using the content-creator skill, analyze this text for brand voice:
   "Our platform revolutionizes data analytics..."
   ```

#### In Cursor

1. Open Cursor
2. Use Cmd+K or Ctrl+K
3. Reference skill:
   ```
   @content-creator analyze brand voice for this file
   ```

### Test Python Tools Locally

```bash
# Create test file
echo "Sample content for analysis" > test-article.txt

# Run brand voice analysis
python ~/.claude/skills/content-creator/scripts/brand_voice_analyzer.py test-article.txt

# Run SEO optimization
python ~/.claude/skills/content-creator/scripts/seo_optimizer.py test-article.txt "sample keyword"
```

---

## Troubleshooting

### Universal Installer Issues

#### Issue: "Command not found: npx"

**Solution:** Install Node.js and npm

```bash
# macOS
brew install node

# Ubuntu/Debian
sudo apt-get install nodejs npm

# Windows
# Download from https://nodejs.org/
```

#### Issue: "Failed to install skills"

**Solution:** Check network connection and permissions

```bash
# Check network
curl https://github.com/borghei/Claude-Skills

# Check write permissions
ls -la ~/.claude/
```

#### Issue: "Skills not showing in agent"

**Solution:** Restart agent and verify installation location

```bash
# Verify installation
ls -R ~/.claude/skills/

# Restart Claude Code
# Close and reopen application
```

### Manual Installation Issues

#### Issue: Python scripts not executable

**Solution:** Add execute permissions

```bash
chmod +x marketing-skill/content-creator/scripts/*.py
chmod +x c-level-advisor/*/scripts/*.py
chmod +x product-team/*/scripts/*.py
```

#### Issue: "Module not found" errors

**Solution:** Install required dependencies

```bash
# Install Python dependencies
pip install pyyaml

# Or use Python 3 specifically
pip3 install pyyaml
```

#### Issue: Skills not recognized by agent

**Solution:** Verify SKILL.md format and location

```bash
# Check SKILL.md exists
ls ~/.claude/skills/content-creator/SKILL.md

# Verify YAML frontmatter
head -20 ~/.claude/skills/content-creator/SKILL.md
```

### Agent-Specific Issues

#### Claude Code

```bash
# Reset skills directory
rm -rf ~/.claude/skills/
mkdir -p ~/.claude/skills/

# Reinstall
npx agent-skills-cli add borghei/Claude-Skills --agent claude
```

#### Cursor

```bash
# Cursor uses project-local skills
# Verify project directory has .cursor/skills/

ls .cursor/skills/
```

#### VS Code/Copilot

```bash
# GitHub Copilot uses .github/skills/
# Verify directory structure

ls .github/skills/
```

---

## Uninstallation

### Universal Installer (All Agents)

```bash
# Remove from Claude Code
rm -rf ~/.claude/skills/borghei/Claude-Skills/

# Remove from Cursor
rm -rf .cursor/skills/borghei/Claude-Skills/

# Remove from VS Code
rm -rf .github/skills/borghei/Claude-Skills/

# Remove from Goose
rm -rf ~/.config/goose/skills/borghei/Claude-Skills/
```

### Manual Installation

```bash
# Clone directory
rm -rf claude-skills/

# Copied skills
rm -rf ~/.claude/skills/marketing-skill/
rm -rf ~/.claude/skills/engineering-team/
# etc.
```

### Remove Individual Skills

```bash
# Example: Remove content-creator from Claude Code
rm -rf ~/.claude/skills/content-creator/

# Example: Remove fullstack-engineer from Cursor
rm -rf .cursor/skills/fullstack-engineer/
```

---

## OpenAI Codex Installation

OpenAI Codex users can install skills using the methods below. This repository provides full Codex compatibility through a `.codex/skills/` directory with symlinks to all 43 skills.

### Method 1: Universal Installer (Recommended)

```bash
# Install all skills to Codex
npx agent-skills-cli add borghei/Claude-Skills --agent codex

# Preview before installing
npx agent-skills-cli add borghei/Claude-Skills --agent codex --dry-run
```

### Method 2: Direct Installation Script

For manual installation using the provided scripts:

**macOS/Linux:**
```bash
# Clone repository
git clone https://github.com/borghei/Claude-Skills.git
cd claude-skills

# Generate symlinks (if not already present)
python scripts/sync-codex-skills.py

# Install all skills to ~/.codex/skills/
./scripts/codex-install.sh

# Or install specific category
./scripts/codex-install.sh --category marketing
./scripts/codex-install.sh --category engineering

# Or install single skill
./scripts/codex-install.sh --skill content-creator

# List available skills
./scripts/codex-install.sh --list
```

**Windows:**
```cmd
REM Clone repository
git clone https://github.com/borghei/Claude-Skills.git
cd claude-skills

REM Generate structure (if not already present)
python scripts\sync-codex-skills.py

REM Install all skills to %USERPROFILE%\.codex\skills\
scripts\codex-install.bat

REM Or install single skill
scripts\codex-install.bat --skill content-creator

REM List available skills
scripts\codex-install.bat --list
```

### Method 3: Manual Installation

```bash
# Clone repository
git clone https://github.com/borghei/Claude-Skills.git
cd claude-skills

# Copy skills (following symlinks) to Codex directory
mkdir -p ~/.codex/skills
cp -rL .codex/skills/* ~/.codex/skills/
```

### Verification

```bash
# Check installed skills
ls ~/.codex/skills/

# Verify skill structure
ls ~/.codex/skills/content-creator/
# Should show: SKILL.md, scripts/, references/, assets/

# Check total skill count
ls ~/.codex/skills/ | wc -l
# Should show: 53
```

### Available Categories

| Category | Skills | Examples |
|----------|--------|----------|
| **c-level** | 2 | ceo-advisor, cto-advisor |
| **engineering** | 18 | senior-fullstack, aws-solution-architect, senior-ml-engineer |
| **marketing** | 6 | content-creator, marketing-demand-acquisition, social-media-analyzer |
| **product** | 5 | product-manager-toolkit, agile-product-owner, ui-design-system |
| **project-management** | 6 | scrum-master, senior-pm, jira-expert, confluence-expert |
| **ra-qm** | 12 | regulatory-affairs-head, quality-manager-qms-iso13485, gdpr-dsgvo-expert |
| **business-growth** | 3 | customer-success-manager, sales-engineer, revenue-operations |
| **finance** | 1 | financial-analyst |

See `.codex/skills-index.json` for the complete manifest with descriptions.

---

## Advanced: Installation Locations Reference

| Agent | Default Location | Flag | Notes |
|-------|------------------|------|-------|
| **Claude Code** | `~/.claude/skills/` | `--agent claude` | User-level installation |
| **Cursor** | `.cursor/skills/` | `--agent cursor` | Project-level installation |
| **VS Code/Copilot** | `.github/skills/` | `--agent vscode` | Project-level installation |
| **Goose** | `~/.config/goose/skills/` | `--agent goose` | User-level installation |
| **Amp** | Platform-specific | `--agent amp` | Varies by platform |
| **Codex** | `~/.codex/skills/` | `--agent codex` | User-level installation |
| **Letta** | Platform-specific | `--agent letta` | Varies by platform |
| **OpenCode** | Platform-specific | `--agent opencode` | Varies by platform |
| **Project** | `.skills/` | `--agent project` | Portable, project-specific |

---

## Support

**Installation Issues?**
- Check [Troubleshooting](#troubleshooting) section above
- Review [Agent Skills CLI documentation](https://github.com/Karanjot786/agent-skills-cli)
- Open issue: https://github.com/borghei/Claude-Skills/issues

**Feature Requests:**
- Submit via GitHub Issues with `enhancement` label

**General Questions:**
- Visit: https://borghei.me
- Blog: https://medium.com/@borghei

---

**Last Updated:** February 2026
**Skills Version:** 2.0 (97 production skills, 178 Python tools, 6 subagents, 12 workflows)
**Universal Installer:** [Agent Skills CLI](https://github.com/Karanjot786/agent-skills-cli)
