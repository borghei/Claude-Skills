---
name: senior-architect
description: >
  System architecture design and review. Use when designing architecture, evaluating
  microservices vs monolith, writing ADRs, choosing a database, planning for scalability,
  reviewing system design, or generating architecture diagrams.
license: MIT + Commons Clause
metadata:
  version: 1.1.0
  author: borghei
  category: engineering
  domain: system-design
  updated: 2026-06-17
  tags: [system-design, distributed-systems, architecture, adr, scalability]
---
# Senior Architect

Architecture design and analysis tools for making informed technical decisions: visualize system structure, analyze dependencies and coupling, detect architectural patterns, and run decision workflows for databases, patterns, and monolith-vs-microservices trade-offs.

## Core Capabilities

- **Diagram generation** — produce component, layer, and deployment diagrams in Mermaid, PlantUML, or ASCII from a project directory.
- **Dependency analysis** — map the dependency tree, score coupling (0-100), and detect circular dependencies across npm, pip, Poetry, Go modules, and Cargo.
- **Pattern detection** — assess an existing codebase for layered/MVC/hexagonal/clean/microservices patterns, layer violations, god classes, and mixed concerns.
- **Database selection** — match data characteristics, scale, and consistency needs to SQL/NoSQL options with an ADR template.
- **Pattern & topology selection** — choose an architecture pattern by team size, deployment, and data-boundary requirements.
- **Monolith vs microservices** — apply decision checklists and a modular-monolith-first hybrid strategy.

## When to Use

- Designing a new system or refactoring existing architecture.
- Evaluating microservices vs monolith, or choosing a database.
- Writing an ADR, planning for scalability, or reviewing a system design.
- Generating architecture diagrams for documentation or team review.

## Clarify First

Before generating diagrams or an assessment, confirm these inputs. If any is unknown or vague, ASK — do not assume:

- [ ] **Project root** — the codebase directory to analyze (drives pattern detection, dependency scoring, and diagram contents)
- [ ] **Diagram type & format** — component / layer / deployment in Mermaid / PlantUML / ASCII (sets what the generator emits)
- [ ] **Architecture decision in question** — e.g. database choice or monolith vs microservices (selects the decision workflow and ADR)

Stop rule: ask only the 2-3 that most change the output. If the user says "just draft it," proceed and list your assumptions at the top of the artifact.

## Tools

| Tool | Purpose | Command |
|------|---------|---------|
| `architecture_diagram_generator.py` | Generate component/layer/deployment diagrams from project structure | `python scripts/architecture_diagram_generator.py ./project --format mermaid --type component` |
| `dependency_analyzer.py` | Score coupling and find circular dependencies across package managers | `python scripts/dependency_analyzer.py ./project --output json --check circular` |
| `project_architect.py` | Detect architecture pattern, layer violations, and code smells | `python scripts/project_architect.py ./project --check layers --verbose` |

Run any script with `--help` for full flags.

## References

Load the reference that matches the task — keep this file lean and pull detail on demand:

- **[references/architecture_patterns.md](references/architecture_patterns.md)** — 9 architecture patterns (monolith, modular monolith, microservices, event-driven, CQRS, event sourcing, hexagonal, clean, API gateway) with trade-offs and code examples. Read when asked "which pattern?", "microservices vs monolith", "event-driven", or "CQRS".
- **[references/system_design_workflows.md](references/system_design_workflows.md)** — 6 step-by-step workflows: design interview, capacity planning, API design, database schema design, scalability assessment, migration planning. Read when asked "how to design?", "capacity planning", "API design", or "migration".
- **[references/tech_decision_guide.md](references/tech_decision_guide.md)** — decision frameworks and comparison matrices for database, caching, message queue, auth, frontend framework, cloud provider, and API style. Read when asked "which database/framework/cloud/cache?".
- **[references/decision_workflows.md](references/decision_workflows.md)** — the database-selection, architecture-pattern-selection, and monolith-vs-microservices decision workflows with matrices, checklists, and the ADR template. Read when making a documented architecture decision.
- **[references/tools-and-usage.md](references/tools-and-usage.md)** — detailed per-tool usage, example outputs, full flag tables, common-command catalog, tech-stack coverage, troubleshooting table, and success criteria. Read when running the scripts or interpreting their output.

## Scope & Limitations

**Covers:** system-level architecture analysis (pattern detection, layer validation, component diagramming) for existing codebases; technology-agnostic dependency analysis across npm, pip, Poetry, Go modules, and Cargo; architecture decision workflows (database, pattern, monolith-vs-microservices); diagram generation in Mermaid, PlantUML, and ASCII.

**Does NOT cover:**
- Runtime performance profiling or load testing — use `senior-devops` (capacity planning) and `senior-qa` (performance test harnesses).
- Security vulnerability scanning of dependencies — use `senior-security` or `senior-secops` for CVE/SAST/DAST.
- Frontend component architecture and design-system auditing — use `senior-frontend` and `design-auditor`.
- CI/CD pipeline design and deployment orchestration — use `senior-devops` and `release-orchestrator`.

## Integration Points

| Skill | Integration | Data Flow |
|-------|-------------|-----------|
| `senior-backend` | Architecture patterns inform backend service boundaries and API contract design | Architect assessment output (detected pattern, layer assignments) feeds into backend module scaffolding |
| `senior-devops` | Deployment diagrams and technology detection drive infrastructure-as-code decisions | Deployment diagram type output + detected technologies list consumed by DevOps for Terraform/K8s config |
| `senior-security` | Dependency analysis surfaces packages that need security review | Dependency list JSON (`--output json`) passed to security scanning for CVE correlation |
| `senior-fullstack` | Architecture pattern selection determines which fullstack scaffold template to use | Pattern selection workflow result (e.g., modular monolith) maps to `project_scaffolder.py --type` flag |
| `code-reviewer` | Layer violation and god-class findings become review checklist items | `project_architect.py --output json` issues array integrated into code review checklists |
| `tech-stack-evaluator` | Technology detection results feed tech stack evaluation for upgrade/migration decisions | Detected technologies list and dependency versions inform stack evaluation decision matrices |
