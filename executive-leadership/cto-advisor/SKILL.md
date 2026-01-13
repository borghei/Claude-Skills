---
name: cto-advisor
description: Technical leadership advisor for CTOs on architecture decisions, engineering strategy, team scaling, technical debt management, and technology evaluation.
version: 1.0.0
author: Claude Skills
category: executive-leadership
tags: [technology, architecture, engineering, leadership, technical-strategy]
---

# CTO Advisor

Technical leadership advisory for Chief Technology Officers.

## Core Competencies

- Technology strategy and vision
- System architecture and design
- Engineering team building and scaling
- Technical debt management
- Build vs buy decisions
- Security and compliance
- Platform and infrastructure
- Vendor and technology evaluation

## Architecture Decision Framework

### Decision Record Template (ADR)

```markdown
# ADR-[NUMBER]: [TITLE]

## Status
[Proposed | Accepted | Deprecated | Superseded]

## Context
[What is the issue we're facing?]

## Decision
[What is the change we're proposing?]

## Consequences
[What becomes easier or harder?]

## Alternatives Considered
[What other options were evaluated?]
```

### Technology Evaluation Matrix

| Criteria | Weight | Option A | Option B | Option C |
|----------|--------|----------|----------|----------|
| Technical Fit | 25% | | | |
| Team Capability | 20% | | | |
| Scalability | 20% | | | |
| Total Cost | 15% | | | |
| Vendor Risk | 10% | | | |
| Community/Support | 10% | | | |

## Technical Debt Management

### Debt Classification

**Type 1: Deliberate Tactical**
- Conscious shortcuts for speed
- Known cleanup required
- Documented with timeline
- Example: Hardcoded config for MVP

**Type 2: Accidental/Outdated**
- Requirements changed after build
- Technology evolved
- Better patterns emerged
- Example: Legacy API design

**Type 3: Bit Rot**
- Dependencies outdated
- Security vulnerabilities
- Performance degradation
- Example: Unpatched libraries

### Debt Prioritization Formula

```
Priority Score = (Impact × Reach × Urgency) / Effort

Impact: 1-5 (business/security/reliability impact)
Reach: 1-5 (how much of system affected)
Urgency: 1-5 (time sensitivity)
Effort: 1-5 (engineering investment required)
```

### Debt Budget

Allocate engineering capacity to debt:
- **Startup (< 20 engineers)**: 10-15%
- **Growth (20-100 engineers)**: 15-20%
- **Scale (100+ engineers)**: 20-25%

## Engineering Team Scaling

### Team Structure by Size

**5-15 Engineers:**
- Single team, full-stack ownership
- CTO as technical lead
- Informal processes
- Everyone deploys

**15-40 Engineers:**
- 2-4 feature teams
- Engineering managers introduced
- Sprint/kanban processes
- On-call rotation begins

**40-100 Engineers:**
- Platform team split out
- Tech leads per team
- Architecture review board
- Formal RFC process

**100+ Engineers:**
- Multiple domains/pillars
- Principal engineers
- Developer experience team
- Internal tooling investment

### Hiring Bar

**Junior (0-2 years):**
- Strong fundamentals
- Learning velocity
- Culture fit
- Mentorship capacity available

**Mid-Level (2-5 years):**
- Independent delivery
- Code quality focus
- Collaboration skills
- Can own features end-to-end

**Senior (5+ years):**
- System design capability
- Technical leadership
- Mentoring others
- Cross-team influence

**Staff+ (8+ years):**
- Organizational impact
- Technical vision
- Executive communication
- Industry perspective

### Interview Process

1. **Resume Screen**: Technical background check
2. **Phone Screen**: Communication and basic skills
3. **Technical Interview**: Coding and problem solving
4. **System Design**: Architecture and trade-offs
5. **Team Fit**: Collaboration and culture
6. **Reference Check**: Verification and red flags

## Platform Strategy

### Build vs Buy Framework

**Build When:**
- Core differentiator
- Unique requirements
- Long-term strategic value
- Sufficient engineering capacity
- Acceptable timeline

**Buy When:**
- Commodity capability
- Standard requirements
- Faster time to market
- Cost effective at scale
- Vendor ecosystem strong

### Technology Radar

Categorize technologies into:

**Adopt**: Use in production
**Trial**: Use in limited scope
**Assess**: Explore and evaluate
**Hold**: Do not start new work

Review quarterly with engineering leadership.

## Security Framework

### Security Layers

**Application Security:**
- Input validation
- Authentication/authorization
- Secrets management
- Dependency scanning

**Infrastructure Security:**
- Network segmentation
- Encryption in transit/at rest
- Access controls
- Audit logging

**Operational Security:**
- Incident response
- Vulnerability management
- Penetration testing
- Security training

### Compliance Checklist

- [ ] SOC 2 Type II
- [ ] GDPR compliance
- [ ] Data classification
- [ ] Access reviews (quarterly)
- [ ] Penetration testing (annual)
- [ ] Security awareness training
- [ ] Incident response plan
- [ ] Business continuity plan

## Engineering Metrics

### Productivity Metrics

**DORA Metrics:**
- Deployment Frequency
- Lead Time for Changes
- Mean Time to Recovery
- Change Failure Rate

**Targets by Maturity:**

| Metric | Low | Medium | High | Elite |
|--------|-----|--------|------|-------|
| Deploy Freq | Monthly | Weekly | Daily | On-demand |
| Lead Time | > 6 months | 1-6 months | 1 week-1 month | < 1 day |
| MTTR | > 6 months | 1 day-1 week | < 1 day | < 1 hour |
| Change Fail | > 46% | 16-30% | 0-15% | 0-15% |

### Quality Metrics

- Test coverage percentage
- Bug escape rate
- P0/P1 incident frequency
- Technical debt ratio
- Documentation coverage

## System Design Principles

### Scalability Patterns

**Horizontal Scaling:**
- Stateless services
- Load balancing
- Database sharding
- Cache layers

**Vertical Scaling:**
- Resource optimization
- Query optimization
- Memory management
- Connection pooling

### Reliability Patterns

**Fault Tolerance:**
- Circuit breakers
- Retry with backoff
- Graceful degradation
- Bulkhead isolation

**Observability:**
- Structured logging
- Distributed tracing
- Metrics collection
- Alerting thresholds

## Common Scenarios

### Scenario: Major Outage

Response sequence:
1. Acknowledge and assemble team
2. Identify scope and impact
3. Implement mitigation
4. Communicate to stakeholders
5. Resolve root cause
6. Conduct post-mortem
7. Implement preventive measures

### Scenario: Security Incident

Response sequence:
1. Contain the breach
2. Preserve evidence
3. Assess data exposure
4. Notify legal/compliance
5. Remediate vulnerability
6. External notification if required
7. Post-incident review

### Scenario: Acquisition Due Diligence

Preparation checklist:
- System architecture documentation
- Technology inventory
- Security audit reports
- Scalability assessment
- Technical debt inventory
- Key personnel dependencies
- IP and licensing review

## Reference Materials

- `references/architecture_patterns.md` - System design patterns
- `references/security_framework.md` - Security best practices
- `references/scaling_playbook.md` - Team and system scaling
- `references/tech_evaluation.md` - Technology assessment guide

## Scripts

```bash
# Technical debt analysis
python scripts/tech_debt_analyzer.py --repo /path/to/repo

# Team scaling calculator
python scripts/team_scaling.py --current 25 --growth-rate 0.5

# Architecture diagram generator
python scripts/arch_diagram.py --services services.yaml

# Security scan orchestration
python scripts/security_scan.py --target production
```
