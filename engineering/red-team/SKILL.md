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

## Clarify First

Before planning the engagement, settle the inputs below. When one is missing or vague and would change the result, ask about it; when it wouldn't, use a sensible default and say which one you used.

- **Authorization & ROE owner:** who has signed off and the escalation contacts (no engagement plan without confirmed authorization).
- **In-scope targets & boundaries:** the exact assets in and explicitly out of bounds (drives scope and `--target`).
- **Engagement type:** red-team / pentest / purple-team / app-security (sets stealth, methodology, and `--type`). The planner has no bug bounty type.
- **Compliance framework:** e.g. pci-dss (maps test cases to controls via `--compliance`).

Ask about the two or three inputs that matter most for this request, not the whole list. If the user wants a result straight away, produce it and state your assumptions at the top.

## Quick Start

```bash
# Plan a red team engagement
python scripts/engagement_planner.py --type red-team --target web-application --duration 2w

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

## Scope & Limitations

**In Scope:**
- Engagement plans from `engagement_planner.py` for four engagement types (red-team, pentest, purple-team, app-security) and the targets listed in its `--help`.
- Plan content: scope, rules of engagement, methodology choice, phases with dates, communication and escalation, and a deliverables checklist, in text or JSON.
- Optional mapping to a compliance framework with `--compliance` (pci-dss, soc2, hipaa, iso27001).
- Frameworks, rules-of-engagement elements and phase guidance in `references/red-team-methodology.md`.

**Out of Scope:**
- Carrying out an engagement. The skill produces planning documents and runs nothing against any system.
- Source-level vulnerability review of a repository (see `engineering/security-audit/`).
- Threat modeling and secure design review (see `engineering/senior-security/`), and detecting attacks in logs (see `engineering/threat-detection/`).
- Running a compliance program or audit (see `ra-qm-team/pci-dss-specialist/` and `ra-qm-team/soc2-compliance-expert/`).
- Legal review of authorization letters or engagement contracts.

**Important Caveats:**
- The skill is for authorized engagements only. Confirmed authorization comes first, as Clarify First requires, and the generated rules of engagement are not a substitute for written sign-off from the asset owner.
- Plans are built from fixed templates. Dates, phase lengths, contacts and test lists are defaults that need adjusting to the real engagement.
- An engagement covers only what was in scope during its time box. Its findings are not a guarantee that no other vulnerabilities exist.
- Compliance mappings are a starting point. The assessor and the current version of the framework decide what evidence is required.

## Reference Documentation

- [Red Team Methodology](references/red-team-methodology.md) - Frameworks, attack phases, and engagement standards

## Common Patterns

### Engagement Types
- **Red Team**: Full adversary simulation, stealth required, tests detection/response
- **Penetration Test**: Authorized vulnerability exploitation, known to defenders
- **Purple Team**: Collaborative attack/defense, real-time knowledge sharing
- **Application Security Assessment**: Focused testing of web, mobile and API applications
