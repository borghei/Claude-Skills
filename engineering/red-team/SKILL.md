---
name: red-team
description: >
  This skill should be used when the user asks to "plan a red team engagement",
  "scope a penetration test", "design a security assessment methodology",
  "create rules of engagement", or "plan an adversary simulation".
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: engineering
  domain: offensive-security
  updated: 2026-04-02
  tags: [red-team, penetration-testing, security-assessment, adversary-simulation, engagement-planning]
---

# Red Team

> **Category:** Engineering
> **Domain:** Offensive Security

## Overview

The **Red Team** skill provides tools for planning and scoping security engagements. It helps define rules of engagement, select methodologies, scope targets, plan attack phases, and generate engagement documentation.

## Quick Start

```bash
# Plan a red team engagement
python scripts/engagement_planner.py --type red-team --target "web application" --duration 2w

# Plan a penetration test
python scripts/engagement_planner.py --type pentest --target "api,network" --duration 1w --compliance pci-dss

# Generate rules of engagement document
python scripts/engagement_planner.py --type red-team --target "full-org" --output engagement_plan.json --format json
```

## Tools Overview

| Tool | Purpose | Key Flags |
|------|---------|-----------|
| `engagement_planner.py` | Plan red team engagements with scope, rules, and methodology | `--type`, `--target`, `--duration`, `--compliance` |

### engagement_planner.py

Generates comprehensive engagement plans including:
- Scope definition and boundaries
- Rules of engagement (ROE)
- Methodology selection (MITRE ATT&CK, OWASP, PTES, etc.)
- Phase breakdown with timelines
- Communication and escalation procedures
- Deliverables checklist

## Workflows

### Full Red Team Engagement
1. Define engagement objectives and scope with `engagement_planner.py`
2. Review generated rules of engagement with stakeholders
3. Get formal sign-off on scope and ROE
4. Execute phases per the plan timeline
5. Document findings throughout
6. Deliver final report

### Compliance-Driven Pentest
1. Run planner with `--compliance` flag for framework-specific requirements
2. Map test cases to compliance controls
3. Execute against compliance-specific checklist
4. Generate evidence for auditors

## Reference Documentation

- [Red Team Methodology](references/red-team-methodology.md) - Frameworks, attack phases, and engagement standards

## Common Patterns

### Engagement Types
- **Red Team**: Full adversary simulation, stealth required, tests detection/response
- **Penetration Test**: Authorized vulnerability exploitation, known to defenders
- **Purple Team**: Collaborative attack/defense, real-time knowledge sharing
- **Bug Bounty Triage**: Structured vulnerability validation from external reports
