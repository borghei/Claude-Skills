---
title: Changelog
---

# Changelog

For the complete version history and release notes, see [CHANGELOG.md](https://github.com/borghei/Claude-Skills/blob/main/CHANGELOG.md) in the repository.

## Current Version

**v4.13.9** (October 2026)

- Nine data-science, ML-engineering and DevOps tools that were placeholders now work: A/B test sizing, feature profiling, model evaluation, deployment manifests, RAG planning, drift monitoring, CI pipeline generation, Terraform scaffolding and deployment planning

**v4.13.8** (October 2026)

- Every skill now has a Scope & Limitations section
- No skill points to a tool that doesn't exist; the AWS architect tools run from the command line
- Tool bugs fixed in Snowflake, Terraform, a11y, red-team, prompt-governance and the markdown-html converters; docs corrected to match what each tool does

**v4.13.7** (October 2026)

- EU AI Act high-risk deadlines updated to the Digital Omnibus: 2 December 2027 (Annex III) and 2 August 2028 (Annex I); transparency stays at 2 August 2026
- Reference files and examples match what each tool really does
- Scope & Limitations in 63 more skills
- New social preview card and two-line README badges

**v4.13.6** (October 2026)

- Every skill has a Clarify First section, now written as rules with reasons instead of checkboxes and commands
- The authoring standard, scaffold and linter use the same style

**v4.13.5** (October 2026)

- Every project-management skill, and five of the most-used skills elsewhere, now lists its three most damaging mistakes in SKILL.md
- New README header: a treemap of all 385 skills by domain
- The website's link preview image works again

**v4.13.4** (October 2026)

- A shorter README: how to add the library wherever you work, one real run, and a starter table by task
- Every skill has a domain and tags, and tags now reach the website and CLI search for all 385 skills
- `skill-tester` checks sections by meaning instead of five fixed headings

**v4.13.3** (October 2026)

- `skill-tester` validates and scores the frontmatter schema the library actually uses, so real skills no longer fail its frontmatter check

**v4.13.2** (October 2026)

- Thirteen Python tools that crashed on start now run, and every tool answers `--help`
- `skill-tester` and the pipeline orchestrator no longer need PyYAML
- `build_manifest.py --check` reports out-of-date manifests without writing them
- Counts corrected everywhere: 385 skills, 21 domains, 906 Python tools, 76 agents, 6 CI/CD workflows

**v4.13.1** (October 2026)

- README badge corrected to 21 domains, matching the domain list and every other count

**v4.13.0** (October 2026)

- New `tools/` domain with the 12-skill LinkedIn suite: story interviews, planning, post writing, hook analysis, humanizing, repurposing, comments, replies, thread tracking, profile, employee advocacy and engagement analytics. Offline tools; nothing is posted for you
- New `security-audit` engineering skill and `cs-security-auditor` agent: multi-agent source audit with a coverage ledger, independent verification and machine-validated findings, at a breadth tier chosen per run
- 385 production-ready skills across 21 domains, 900 Python automation tools, 77 agents

**v4.12.3** (September 2026)

- Every script a skill, domain guide or agent tells you to run now exists; references to tools that were never written are gone

- Current-Claude accuracy pass: four skill descriptions restored, the real Claude Code subagent format in `claude-code-mastery`, current model IDs and prices in every example and cost tool

- 372 production-ready skills across 20 domains, 867 Python automation tools, 76 agents
- 4 new AI-era skills: `ai-content-disclosure` and `conversational-ads` (marketing), `ai-prototyping` and `agents-in-the-team` (project management)
- Marketing and PM skills refreshed against 2025–2026 changes: retired rich results, AI crawler and Search Console AI controls, Advantage+ / AI Max, GA4 AI Assistant channel, Productboard API v2, Jira enhanced search, Notion data sources, DORA 2024 benchmarks, EU AI Act Omnibus
- Workflow templates hardened against shell injection (CWE-78)
- Full skills and agents references published on the site; complete PM and marketing catalogs

## Previous Releases

### v4.1.0 – v4.11.0

April to June 2026: PM depth tiers, the research domain, C-suite Tier 2 advisors, progressive disclosure, cross-platform manifests and AI-modernization engineering skills. See [CHANGELOG.md](https://github.com/borghei/Claude-Skills/blob/main/CHANGELOG.md).

### v3.0.0

- Restructured repository with modular documentation
- Added 5 production agents
- Branch protection and workflow documentation
- Agent template system

### v2.0.0

- Expanded from engineering-only to 13 domains
- Added compliance frameworks (SOC 2, GDPR, ISO 27001, etc.)
- Introduced role-based agents
- Cross-platform configuration files

### v1.0.0

- Initial release with 28 engineering skills
- Python CLI tools for code quality and analysis
- Claude Code integration
