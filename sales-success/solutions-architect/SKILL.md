---
name: solutions-architect
description: >
  Expert solutions architecture covering technical requirements, solution design,
  integration planning, and enterprise architecture alignment. Use when conducting
  technical discovery, designing integration architectures, running security assessments,
  scoping proof-of-concept engagements, or creating solution architecture documents.
version: 1.0.0
author: borghei
category: sales-success
tags: [solutions, architecture, technical, integration, enterprise]
---

# Solutions Architect

The agent operates as an expert solutions architect for complex enterprise sales, delivering technical requirements analysis, integration design, security assessment, proof-of-concept scoping, and architecture documentation.

## Workflow

1. **Conduct technical discovery** -- Map the customer's current-state architecture: systems inventory, data landscape, integration points, and constraints. Document functional and non-functional requirements. Validate: discovery template fully populated with all systems, data flows, and requirements prioritized.
2. **Design the solution** -- Create the solution architecture including component design, integration patterns, API specifications, data flows, and security model. Validate: architecture addresses every must-have requirement and identifies gaps for should-have items.
3. **Assess security and compliance** -- Run the security assessment checklist across authentication, authorization, data protection, compliance certifications, and infrastructure. Validate: all checklist items evaluated and any gaps documented with remediation plans.
4. **Scope the proof of concept** -- Define POC objectives, success criteria, in-scope/out-of-scope boundaries, timeline, and resource requirements. Validate: customer and internal team aligned on POC scope and success metrics before kickoff.
5. **Execute and validate** -- Support POC execution, track milestone completion against success criteria, and gather stakeholder feedback. Validate: all success criteria measured and results documented.
6. **Deliver architecture documentation** -- Produce the final solution architecture document including deployment architecture, scalability plan, and implementation roadmap. Validate: document reviewed and signed off by technical and business stakeholders.

## Requirements Analysis

### Discovery Template

```markdown
# Technical Discovery: [Customer Name]

## Current State Architecture

### Systems Inventory
| System | Purpose | Technology | Owner |
|--------|---------|------------|-------|
| [System] | [Purpose] | [Tech] | [Team] |

### Data Landscape
- Data sources: [List]
- Data volumes: [Size]
- Data formats: [Formats]
- Data governance: [Policies]

### Integration Points
| Source | Target | Type | Frequency |
|--------|--------|------|-----------|
| [Source] | [Target] | [API/File/DB] | [Real-time/Batch] |

## Functional Requirements
| ID | Requirement | Priority | Notes |
|----|-------------|----------|-------|
| FR-1 | [Requirement] | Must | [Notes] |
| FR-2 | [Requirement] | Should | [Notes] |

## Non-Functional Requirements
| Category | Requirement | Target |
|----------|-------------|--------|
| Performance | Response time | <500ms P95 |
| Availability | Uptime | 99.9% |
| Scalability | Concurrent users | 10,000 |
| Security | Compliance | SOC 2 Type II |

## Integration Requirements
| Integration | Direction | Protocol | Auth |
|-------------|-----------|----------|------|
| [System] | Inbound | REST API | OAuth 2.0 |
| [System] | Outbound | Webhook | API Key |

## Constraints
- [Constraint 1]

## Risks
| Risk | Impact | Mitigation |
|------|--------|------------|
| [Risk] | [H/M/L] | [Action] |
```

## Solution Design

### Architecture Document Structure

The agent produces architecture documents with these sections:

1. **Executive Summary** -- One paragraph overview of the solution and its business value.
2. **Architecture Overview** -- High-level component diagram showing system boundaries.
3. **Solution Components** -- Each component's purpose, technology, and interfaces.
4. **Integration Architecture** -- Data flows, API specifications, integration patterns (event-driven, request-response, batch).
5. **Security Architecture** -- Authentication (SSO/SAML/OAuth), authorization (RBAC/ABAC), data protection (encryption at rest and in transit).
6. **Deployment Architecture** -- Infrastructure, environments (dev/staging/production), and configuration.
7. **Scalability and Performance** -- Capacity planning, performance targets, growth projections.
8. **Implementation Roadmap** -- Phased delivery with durations and dependencies.

### Example: Context Diagram

```
  CUSTOMER ENVIRONMENT
  +----------+  +----------+  +----------+  +----------+
  |   CRM    |  |   ERP    |  |  Data    |  |   IdP    |
  |  System  |  |  System  |  |  Lake    |  |  (Auth)  |
  +----+-----+  +----+-----+  +----+-----+  +----+-----+
       |             |             |             |
       +-------------+------+------+-------------+
                            |
                   +--------v--------+
                   | Integration     |
                   | Layer (iPaaS)   |
                   +--------+--------+
                            |
                   +--------v--------+
                   |  OUR PLATFORM   |
                   |  +----------+   |
                   |  |   API    |   |
                   |  +----------+   |
                   |  | Services |   |
                   |  +----------+   |
                   +-----------------+
```

### Example: API Specification

| Endpoint | Method | Purpose | Auth | Rate Limit |
|----------|--------|---------|------|------------|
| /api/v1/accounts | GET | List accounts | OAuth 2.0 | 100/min |
| /api/v1/accounts | POST | Create account | OAuth 2.0 | 50/min |
| /api/v1/webhooks | POST | Receive events | API Key | 1000/min |

## Security Assessment Checklist

```
AUTHENTICATION
[ ] SSO integration supported (SAML 2.0 / OIDC)
[ ] MFA available and configurable
[ ] Session management with configurable timeout
[ ] Password policies meet enterprise requirements

AUTHORIZATION
[ ] Role-based access control implemented
[ ] Fine-grained permissions at resource level
[ ] Audit logging for all access events
[ ] Admin controls for user management

DATA PROTECTION
[ ] Encryption at rest (AES-256)
[ ] Encryption in transit (TLS 1.2+)
[ ] Data residency options (region selection)
[ ] Backup and disaster recovery documented

COMPLIANCE
[ ] SOC 2 Type II certified
[ ] GDPR compliant (DPA available)
[ ] HIPAA ready (BAA available if applicable)
[ ] Penetration test results available

INFRASTRUCTURE
[ ] Cloud security posture (AWS/GCP/Azure)
[ ] Network isolation and segmentation
[ ] DDoS protection enabled
[ ] Vulnerability management program active
```

## Proof of Concept

### POC Scope Template

```markdown
# POC Scope: [Customer Name]

## Objectives
1. [Primary objective with measurable outcome]
2. [Secondary objective with measurable outcome]

## Success Criteria
| Criteria | Target | Measurement Method |
|----------|--------|--------------------|
| [Criteria] | [Target] | [How to measure] |

## In Scope
- [Feature 1]
- [Integration 1]

## Out of Scope
- [Feature X] -- deferred to Phase 2
- [Integration Y] -- not required for validation

## Timeline
| Milestone | Target Date |
|-----------|-------------|
| Environment setup complete | [Date] |
| Testing complete | [Date] |
| Results review meeting | [Date] |

## Resources
- Customer: [Names/roles]
- Internal: [Names/roles]
```

### POC Success Metrics

The agent tracks three dimensions of POC success:

- **Technical** -- Feature requirements met (X/Y), performance benchmarks passed, integrations functional.
- **Business** -- Time savings demonstrated, ease-of-use rating, stakeholder approval obtained.
- **Relationship** -- Engagement level high, champion confirmed, decision maker participated in review.

## Implementation Roadmap Example

| Phase | Scope | Duration | Dependencies |
|-------|-------|----------|-------------|
| Phase 1 | Core integration + SSO | 4 weeks | IdP access, API credentials |
| Phase 2 | Advanced features + data migration | 4 weeks | Phase 1 complete |
| Phase 3 | Performance tuning + go-live | 2 weeks | UAT sign-off |

## Scripts

```bash
# Requirements analyzer
python scripts/requirements_analyzer.py --input requirements.xlsx

# Architecture diagram generator
python scripts/arch_diagram.py --config solution.yaml

# Security assessment
python scripts/security_assess.py --customer "Customer Name"

# POC tracker
python scripts/poc_tracker.py --customer "Customer Name"
```

## Reference Materials

- `references/architecture_patterns.md` -- Common patterns
- `references/integration_guide.md` -- Integration best practices
- `references/security_framework.md` -- Security requirements
- `references/poc_playbook.md` -- POC execution guide
