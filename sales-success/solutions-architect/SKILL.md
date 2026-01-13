---
name: solutions-architect
description: Expert solutions architecture covering technical requirements, solution design, integration planning, and enterprise architecture alignment.
version: 1.0.0
author: Claude Skills
category: sales-success
tags: [solutions, architecture, technical, integration, enterprise]
---

# Solutions Architect

Expert-level solutions architecture for complex sales.

## Core Competencies

- Technical requirements analysis
- Solution design
- Integration architecture
- Enterprise alignment
- Technical presentations
- Proof of concept design
- Security and compliance
- Stakeholder management

## Solutions Process

### Engagement Model

```
DISCOVERY → DESIGN → VALIDATE → IMPLEMENT → OPTIMIZE

1. DISCOVERY
   ├── Business requirements
   ├── Technical landscape
   ├── Integration needs
   └── Success criteria

2. DESIGN
   ├── Solution architecture
   ├── Integration design
   ├── Data flow mapping
   └── Security model

3. VALIDATE
   ├── Technical proof of concept
   ├── Performance testing
   ├── Security review
   └── Stakeholder sign-off

4. IMPLEMENT
   ├── Implementation plan
   ├── Migration strategy
   ├── Training design
   └── Go-live support

5. OPTIMIZE
   ├── Performance tuning
   ├── Feature adoption
   ├── Architecture evolution
   └── Continuous improvement
```

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

## Requirements

### Functional Requirements
| ID | Requirement | Priority | Notes |
|----|-------------|----------|-------|
| FR-1 | [Requirement] | Must | [Notes] |
| FR-2 | [Requirement] | Should | [Notes] |

### Non-Functional Requirements
| Category | Requirement | Target |
|----------|-------------|--------|
| Performance | Response time | <500ms |
| Availability | Uptime | 99.9% |
| Scalability | Users | 10,000 |
| Security | Compliance | SOC 2 |

### Integration Requirements
| Integration | Direction | Protocol | Auth |
|-------------|-----------|----------|------|
| [System] | Inbound | REST API | OAuth |
| [System] | Outbound | Webhook | API Key |

## Constraints
- [Constraint 1]
- [Constraint 2]

## Assumptions
- [Assumption 1]
- [Assumption 2]

## Risks
| Risk | Impact | Mitigation |
|------|--------|------------|
| [Risk] | [H/M/L] | [Action] |
```

## Solution Design

### Architecture Document

```markdown
# Solution Architecture: [Customer Name]

## Executive Summary
[One paragraph overview of the solution]

## Architecture Overview
[High-level diagram]

## Solution Components

### Component 1: [Name]
- Purpose: [Description]
- Technology: [Tech stack]
- Interfaces: [APIs, etc.]

### Component 2: [Name]
...

## Integration Architecture

### Data Flow
[Data flow diagram]

### API Specifications
| Endpoint | Method | Purpose | Auth |
|----------|--------|---------|------|
| /api/v1/resource | GET | List resources | OAuth |

### Integration Patterns
- Pattern: [Event-driven/Request-response/Batch]
- Protocol: [REST/GraphQL/SOAP]
- Format: [JSON/XML/CSV]

## Security Architecture

### Authentication
- Method: [SSO/SAML/OAuth]
- Provider: [IdP]

### Authorization
- Model: [RBAC/ABAC]
- Roles: [List]

### Data Protection
- Encryption at rest: [Yes/No]
- Encryption in transit: [TLS version]
- Data masking: [Requirements]

## Deployment Architecture

### Infrastructure
[Infrastructure diagram]

### Environments
| Environment | Purpose | Config |
|-------------|---------|--------|
| Dev | Development | [Config] |
| Staging | Testing | [Config] |
| Production | Live | [Config] |

## Scalability & Performance

### Capacity Planning
- Expected users: [Number]
- Peak load: [Requests/sec]
- Data growth: [Rate]

### Performance Targets
| Metric | Target | Measurement |
|--------|--------|-------------|
| Response time | <500ms | P95 |
| Throughput | 1000 rps | Average |
| Availability | 99.9% | Monthly |

## Implementation Roadmap
| Phase | Scope | Duration |
|-------|-------|----------|
| Phase 1 | Core integration | 4 weeks |
| Phase 2 | Advanced features | 4 weeks |
| Phase 3 | Optimization | 2 weeks |
```

### Architecture Diagrams

**Context Diagram:**
```
┌─────────────────────────────────────────────────────────────┐
│                     CUSTOMER ENVIRONMENT                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │   CRM    │  │   ERP    │  │   Data   │  │   Auth   │   │
│  │ System   │  │ System   │  │   Lake   │  │  (IdP)   │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
│       │             │             │             │          │
│       └─────────────┴──────┬──────┴─────────────┘          │
│                            │                                │
│                    ┌───────▼───────┐                       │
│                    │  Integration  │                       │
│                    │     Layer     │                       │
│                    └───────┬───────┘                       │
│                            │                                │
└────────────────────────────┼────────────────────────────────┘
                             │
                    ┌────────▼────────┐
                    │  OUR PLATFORM   │
                    │                 │
                    │  ┌───────────┐  │
                    │  │    API    │  │
                    │  └───────────┘  │
                    │  ┌───────────┐  │
                    │  │  Service  │  │
                    │  └───────────┘  │
                    └─────────────────┘
```

## Proof of Concept

### POC Scope Definition

```markdown
# POC Scope: [Customer Name]

## Objectives
1. [Objective 1]
2. [Objective 2]

## In Scope
- [Feature 1]
- [Integration 1]

## Out of Scope
- [Feature X]
- [Integration Y]

## Success Criteria
| Criteria | Target | Measurement |
|----------|--------|-------------|
| [Criteria] | [Target] | [How] |

## Technical Setup
- Environment: [Details]
- Data: [Sample data]
- Users: [Test accounts]

## Timeline
| Milestone | Date |
|-----------|------|
| Setup complete | [Date] |
| Testing complete | [Date] |
| Review meeting | [Date] |

## Resources Required
- Customer: [Names/roles]
- Our team: [Names/roles]
```

## Security Review

### Security Assessment Checklist

```
AUTHENTICATION
□ SSO integration supported
□ MFA available
□ Session management secure
□ Password policies configurable

AUTHORIZATION
□ Role-based access control
□ Fine-grained permissions
□ Audit logging enabled
□ Admin controls available

DATA PROTECTION
□ Encryption at rest (AES-256)
□ Encryption in transit (TLS 1.2+)
□ Data residency options
□ Backup and recovery

COMPLIANCE
□ SOC 2 Type II certified
□ GDPR compliant
□ HIPAA ready (if applicable)
□ Industry-specific certifications

INFRASTRUCTURE
□ Cloud security (AWS/GCP/Azure)
□ Network isolation
□ DDoS protection
□ Vulnerability management
```

## Reference Materials

- `references/architecture_patterns.md` - Common patterns
- `references/integration_guide.md` - Integration best practices
- `references/security_framework.md` - Security requirements
- `references/poc_playbook.md` - POC execution guide

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
