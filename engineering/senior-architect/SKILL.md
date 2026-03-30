---
name: senior-architect
description: >
  This skill should be used when the user asks to "design system architecture",
  "evaluate microservices vs monolith", "create architecture diagrams", "analyze
  dependencies", "choose a database", "plan for scalability", "make technical
  decisions", or "review system design". Use for architecture decision records
  (ADRs), tech stack evaluation, system design reviews, dependency analysis, and
  generating architecture diagrams in Mermaid, PlantUML, or ASCII format.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: engineering
  domain: system-design
  updated: 2026-03-31
  tags: [system-design, distributed-systems, architecture, adr, scalability]
---
# Senior Architect

Architecture design and analysis tools for making informed technical decisions.

## Table of Contents

- [Quick Start](#quick-start)
- [Tools Overview](#tools-overview)
  - [Architecture Diagram Generator](#1-architecture-diagram-generator)
  - [Dependency Analyzer](#2-dependency-analyzer)
  - [Project Architect](#3-project-architect)
- [Decision Workflows](#decision-workflows)
  - [Database Selection](#database-selection-workflow)
  - [Architecture Pattern Selection](#architecture-pattern-selection-workflow)
  - [Monolith vs Microservices](#monolith-vs-microservices-decision)
- [Reference Documentation](#reference-documentation)
- [Tech Stack Coverage](#tech-stack-coverage)
- [Common Commands](#common-commands)

---

## Quick Start

```bash
# Generate architecture diagram from project
python scripts/architecture_diagram_generator.py ./my-project --format mermaid

# Analyze dependencies for issues
python scripts/dependency_analyzer.py ./my-project --output json

# Get architecture assessment
python scripts/project_architect.py ./my-project --verbose
```

---

## Tools Overview

### 1. Architecture Diagram Generator

Generates architecture diagrams from project structure in multiple formats.

**Solves:** "I need to visualize my system architecture for documentation or team discussion"

**Input:** Project directory path
**Output:** Diagram code (Mermaid, PlantUML, or ASCII)

**Supported diagram types:**
- `component` - Shows modules and their relationships
- `layer` - Shows architectural layers (presentation, business, data)
- `deployment` - Shows deployment topology

**Usage:**
```bash
# Mermaid format (default)
python scripts/architecture_diagram_generator.py ./project --format mermaid --type component

# PlantUML format
python scripts/architecture_diagram_generator.py ./project --format plantuml --type layer

# ASCII format (terminal-friendly)
python scripts/architecture_diagram_generator.py ./project --format ascii

# Save to file
python scripts/architecture_diagram_generator.py ./project -o architecture.md
```

**Example output (Mermaid):**
```mermaid
graph TD
    A[API Gateway] --> B[Auth Service]
    A --> C[User Service]
    B --> D[(PostgreSQL)]
    C --> D
```

---

### 2. Dependency Analyzer

Analyzes project dependencies for coupling, circular dependencies, and outdated packages.

**Solves:** "I need to understand my dependency tree and identify potential issues"

**Input:** Project directory path
**Output:** Analysis report (JSON or human-readable)

**Analyzes:**
- Dependency tree (direct and transitive)
- Circular dependencies between modules
- Coupling score (0-100)
- Outdated packages

**Supported package managers:**
- npm/yarn (`package.json`)
- Python (`requirements.txt`, `pyproject.toml`)
- Go (`go.mod`)
- Rust (`Cargo.toml`)

**Usage:**
```bash
# Human-readable report
python scripts/dependency_analyzer.py ./project

# JSON output for CI/CD integration
python scripts/dependency_analyzer.py ./project --output json

# Check only for circular dependencies
python scripts/dependency_analyzer.py ./project --check circular

# Verbose mode with recommendations
python scripts/dependency_analyzer.py ./project --verbose
```

**Example output:**
```
Dependency Analysis Report
==========================
Total dependencies: 47 (32 direct, 15 transitive)
Coupling score: 72/100 (moderate)

Issues found:
- CIRCULAR: auth → user → permissions → auth
- OUTDATED: lodash 4.17.15 → 4.17.21 (security)

Recommendations:
1. Extract shared interface to break circular dependency
2. Update lodash to fix CVE-2020-8203
```

---

### 3. Project Architect

Analyzes project structure and detects architectural patterns, code smells, and improvement opportunities.

**Solves:** "I want to understand the current architecture and identify areas for improvement"

**Input:** Project directory path
**Output:** Architecture assessment report

**Detects:**
- Architectural patterns (MVC, layered, hexagonal, microservices indicators)
- Code organization issues (god classes, mixed concerns)
- Layer violations
- Missing architectural components

**Usage:**
```bash
# Full assessment
python scripts/project_architect.py ./project

# Verbose with detailed recommendations
python scripts/project_architect.py ./project --verbose

# JSON output
python scripts/project_architect.py ./project --output json

# Check specific aspect
python scripts/project_architect.py ./project --check layers
```

**Example output:**
```
Architecture Assessment
=======================
Detected pattern: Layered Architecture (confidence: 85%)

Structure analysis:
  ✓ controllers/  - Presentation layer detected
  ✓ services/     - Business logic layer detected
  ✓ repositories/ - Data access layer detected
  ⚠ models/       - Mixed domain and DTOs

Issues:
- LARGE FILE: UserService.ts (1,847 lines) - consider splitting
- MIXED CONCERNS: PaymentController contains business logic

Recommendations:
1. Split UserService into focused services
2. Move business logic from controllers to services
3. Separate domain models from DTOs
```

---

## Decision Workflows

### Database Selection Workflow

Use when choosing a database for a new project or migrating existing data.

**Step 1: Identify data characteristics**
| Characteristic | Points to SQL | Points to NoSQL |
|----------------|---------------|-----------------|
| Structured with relationships | ✓ | |
| ACID transactions required | ✓ | |
| Flexible/evolving schema | | ✓ |
| Document-oriented data | | ✓ |
| Time-series data | | ✓ (specialized) |

**Step 2: Evaluate scale requirements**
- <1M records, single region → PostgreSQL or MySQL
- 1M-100M records, read-heavy → PostgreSQL with read replicas
- >100M records, global distribution → CockroachDB, Spanner, or DynamoDB
- High write throughput (>10K/sec) → Cassandra or ScyllaDB

**Step 3: Check consistency requirements**
- Strong consistency required → SQL or CockroachDB
- Eventual consistency acceptable → DynamoDB, Cassandra, MongoDB

**Step 4: Document decision**
Create an ADR (Architecture Decision Record) with:
- Context and requirements
- Options considered
- Decision and rationale
- Trade-offs accepted

**Quick reference:**
```
PostgreSQL → Default choice for most applications
MongoDB    → Document store, flexible schema
Redis      → Caching, sessions, real-time features
DynamoDB   → Serverless, auto-scaling, AWS-native
TimescaleDB → Time-series data with SQL interface
```

---

### Architecture Pattern Selection Workflow

Use when designing a new system or refactoring existing architecture.

**Step 1: Assess team and project size**
| Team Size | Recommended Starting Point |
|-----------|---------------------------|
| 1-3 developers | Modular monolith |
| 4-10 developers | Modular monolith or service-oriented |
| 10+ developers | Consider microservices |

**Step 2: Evaluate deployment requirements**
- Single deployment unit acceptable → Monolith
- Independent scaling needed → Microservices
- Mixed (some services scale differently) → Hybrid

**Step 3: Consider data boundaries**
- Shared database acceptable → Monolith or modular monolith
- Strict data isolation required → Microservices with separate DBs
- Event-driven communication fits → Event-sourcing/CQRS

**Step 4: Match pattern to requirements**

| Requirement | Recommended Pattern |
|-------------|-------------------|
| Rapid MVP development | Modular Monolith |
| Independent team deployment | Microservices |
| Complex domain logic | Domain-Driven Design |
| High read/write ratio difference | CQRS |
| Audit trail required | Event Sourcing |
| Third-party integrations | Hexagonal/Ports & Adapters |

See `references/architecture_patterns.md` for detailed pattern descriptions.

---

### Monolith vs Microservices Decision

**Choose Monolith when:**
- [ ] Team is small (<10 developers)
- [ ] Domain boundaries are unclear
- [ ] Rapid iteration is priority
- [ ] Operational complexity must be minimized
- [ ] Shared database is acceptable

**Choose Microservices when:**
- [ ] Teams can own services end-to-end
- [ ] Independent deployment is critical
- [ ] Different scaling requirements per component
- [ ] Technology diversity is needed
- [ ] Domain boundaries are well understood

**Hybrid approach:**
Start with a modular monolith. Extract services only when:
1. A module has significantly different scaling needs
2. A team needs independent deployment
3. Technology constraints require separation

---

## Reference Documentation

Load these files for detailed information:

| File | Contains | Load when user asks about |
|------|----------|--------------------------|
| `references/architecture_patterns.md` | 9 architecture patterns with trade-offs, code examples, and when to use | "which pattern?", "microservices vs monolith", "event-driven", "CQRS" |
| `references/system_design_workflows.md` | 6 step-by-step workflows for system design tasks | "how to design?", "capacity planning", "API design", "migration" |
| `references/tech_decision_guide.md` | Decision matrices for technology choices | "which database?", "which framework?", "which cloud?", "which cache?" |

---

## Tech Stack Coverage

**Languages:** TypeScript, JavaScript, Python, Go, Swift, Kotlin, Rust
**Frontend:** React, Next.js, Vue, Angular, React Native, Flutter
**Backend:** Node.js, Express, FastAPI, Go, GraphQL, REST
**Databases:** PostgreSQL, MySQL, MongoDB, Redis, DynamoDB, Cassandra
**Infrastructure:** Docker, Kubernetes, Terraform, AWS, GCP, Azure
**CI/CD:** GitHub Actions, GitLab CI, CircleCI, Jenkins

---

## Common Commands

```bash
# Architecture visualization
python scripts/architecture_diagram_generator.py . --format mermaid
python scripts/architecture_diagram_generator.py . --format plantuml
python scripts/architecture_diagram_generator.py . --format ascii

# Dependency analysis
python scripts/dependency_analyzer.py . --verbose
python scripts/dependency_analyzer.py . --check circular
python scripts/dependency_analyzer.py . --output json

# Architecture assessment
python scripts/project_architect.py . --verbose
python scripts/project_architect.py . --check layers
python scripts/project_architect.py . --output json
```

---

## Getting Help

1. Run any script with `--help` for usage information
2. Check reference documentation for detailed patterns and workflows
3. Use `--verbose` flag for detailed explanations and recommendations

---

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| Diagram shows zero components | Project uses non-standard directory structure or all directories are in the ignore list (e.g., `node_modules`, `.venv`) | Ensure source code lives in named subdirectories at the project root, not solely in ignored folders |
| Circular dependency detection misses cycles | Import statements use aliases, dynamic imports, or barrel files that obscure the dependency chain | Run `dependency_analyzer.py --verbose` to inspect resolved module graph; refactor barrel re-exports into explicit imports |
| Coupling score always reads 0 | Project has only one internal module (flat file structure with no subdirectories) | Organize code into multiple top-level directories so the analyzer can map inter-module relationships |
| Layer assignment shows all directories as "unknown" | Directory names do not match built-in layer indicators (e.g., `src/` instead of `services/`, `controllers/`) | Rename directories to conventional names or use the JSON output to manually map layers in your ADR |
| `--format plantuml` output renders incorrectly | Component names contain special characters (brackets, quotes) that PlantUML cannot escape | Rename directories to use alphanumeric and hyphen characters only |
| Dependency parser reports 0 dependencies | Package manifest file (`package.json`, `requirements.txt`, `go.mod`, `Cargo.toml`) is missing or malformed | Verify the manifest exists in the project root and passes its native validation (`npm ls`, `pip check`, `go mod verify`) |
| Architecture assessment confidence below 30% | Project mixes multiple patterns or has a flat structure without clear layering | Pick a target pattern from `references/architecture_patterns.md` and restructure directories to match its conventions |

---

## Success Criteria

- **Coupling score below 30**: The dependency analyzer reports a coupling score under 30/100, indicating loosely coupled modules with clear boundaries.
- **Zero circular dependencies**: Running `dependency_analyzer.py --check circular` exits with code 0 and reports no cycles.
- **Zero layer violations**: Running `project_architect.py --check layers` detects no cross-layer dependency violations.
- **Architecture pattern confidence above 70%**: The project architect detects a recognized pattern (layered, clean, hexagonal, MVC) with at least 70% confidence.
- **No god classes detected**: Every class in the codebase stays below 300 lines, with no `god_class` issues in the assessment report.
- **Average file size under 250 lines**: The code quality metrics show `avg_file_lines` well below the 500-line threshold, indicating well-decomposed modules.
- **ADR created for every major decision**: Each architecture decision is documented using the ADR template from the database selection or pattern selection workflow.

---

## Scope & Limitations

**What this skill covers:**
- System-level architecture analysis: pattern detection, layer validation, and component diagramming for existing codebases.
- Technology-agnostic dependency analysis across npm, pip, Poetry, Go modules, and Cargo.
- Architecture decision workflows for database selection, pattern selection, and monolith-vs-microservices trade-offs.
- Diagram generation in Mermaid, PlantUML, and ASCII formats for documentation and team review.

**What this skill does NOT cover:**
- Runtime performance profiling or load testing -- use `senior-devops` for infrastructure capacity planning and `senior-qa` for performance test harnesses.
- Security vulnerability scanning of dependencies -- use `senior-security` or `senior-secops` for CVE detection and SAST/DAST analysis.
- Frontend component architecture and design system auditing -- use `senior-frontend` for React/Vue/Angular component patterns and `design-auditor` for UI consistency checks.
- CI/CD pipeline design and deployment orchestration -- use `senior-devops` for pipeline configuration and `release-orchestrator` for release workflows.

---

## Integration Points

| Skill | Integration | Data Flow |
|-------|-------------|-----------|
| `senior-backend` | Architecture patterns inform backend service boundaries and API contract design | Architect assessment output (detected pattern, layer assignments) feeds into backend module scaffolding |
| `senior-devops` | Deployment diagrams and technology detection drive infrastructure-as-code decisions | Deployment diagram type output + detected technologies list consumed by DevOps for Terraform/K8s config |
| `senior-security` | Dependency analysis surfaces packages that need security review | Dependency list JSON (`--output json`) passed to security scanning for CVE correlation |
| `senior-fullstack` | Architecture pattern selection determines which fullstack scaffold template to use | Pattern selection workflow result (e.g., modular monolith) maps to `project_scaffolder.py --type` flag |
| `code-reviewer` | Layer violation and god-class findings become review checklist items | `project_architect.py --output json` issues array integrated into code review checklists |
| `tech-stack-evaluator` | Technology detection results feed tech stack evaluation for upgrade/migration decisions | Detected technologies list and dependency versions inform stack evaluation decision matrices |

---

## Tool Reference

### architecture_diagram_generator.py

- **Purpose**: Generates architecture diagrams from project directory structure in Mermaid, PlantUML, or ASCII format.
- **Usage**: `python scripts/architecture_diagram_generator.py <project_path> [flags]`
- **Flags**:

| Flag | Short | Type | Default | Description |
|------|-------|------|---------|-------------|
| `project_path` | -- | positional | required | Path to the project directory to scan |
| `--format` | `-f` | choice: `mermaid`, `plantuml`, `ascii` | `mermaid` | Output diagram format |
| `--type` | `-t` | choice: `component`, `layer`, `deployment` | `component` | Diagram type to generate |
| `--output` | `-o` | string | stdout | File path to write the diagram to |
| `--verbose` | `-v` | flag | off | Print scanning progress (components found, relationships, technologies) |
| `--json` | -- | flag | off | Output raw scan results as JSON instead of a diagram |

- **Example**:

```bash
python scripts/architecture_diagram_generator.py ./my-app --format mermaid --type layer -v
```

```
Scanning project: /home/user/my-app
Found 6 components
Found 4 relationships
Technologies: node, react, docker
graph TB
    subgraph Presentation Layer
        components["components"]
        pages["pages"]
    end

    subgraph Business Layer
        services["services"]
    end

    subgraph Data Layer
        models["models"]
        repositories["repositories"]
    end
```

- **Output Formats**: Mermaid diagram code (copy into any Mermaid renderer), PlantUML markup (render via PlantUML server), ASCII art (paste into terminal or plain-text docs), or raw JSON scan data (`--json`).

---

### dependency_analyzer.py

- **Purpose**: Analyzes project dependencies for coupling score, circular dependencies, and package health across multiple package managers.
- **Usage**: `python scripts/dependency_analyzer.py <project_path> [flags]`
- **Flags**:

| Flag | Short | Type | Default | Description |
|------|-------|------|---------|-------------|
| `project_path` | -- | positional | required | Path to the project directory to analyze |
| `--output` | `-o` | choice: `human`, `json` | `human` | Output format for the report |
| `--check` | -- | choice: `all`, `circular`, `coupling` | `all` | Restrict analysis to a specific check; `circular` exits non-zero if cycles found, `coupling` exits non-zero if score >70 |
| `--verbose` | `-v` | flag | off | Print progress details (package manager detected, dependency counts, module scan count) |
| `--save` | `-s` | string | none | Save JSON report to the specified file path |

- **Example**:

```bash
python scripts/dependency_analyzer.py ./my-app --output json --save report.json
```

```json
{
  "project_path": "/home/user/my-app",
  "package_manager": "npm",
  "summary": {
    "direct_dependencies": 23,
    "dev_dependencies": 15,
    "internal_modules": 8,
    "coupling_score": 42,
    "circular_dependencies": 1,
    "issues": 1
  },
  "circular_dependencies": [["auth", "user", "permissions", "auth"]],
  "recommendations": [
    "Extract shared interfaces or create a common module to break circular dependencies"
  ]
}
```

- **Output Formats**: Human-readable terminal report (default) with summary, issues, and recommendations; JSON structured report for CI/CD pipeline integration or programmatic consumption.

---

### project_architect.py

- **Purpose**: Detects architectural patterns, code organization issues, layer violations, and god classes in a project, then generates improvement recommendations.
- **Usage**: `python scripts/project_architect.py <project_path> [flags]`
- **Flags**:

| Flag | Short | Type | Default | Description |
|------|-------|------|---------|-------------|
| `project_path` | -- | positional | required | Path to the project directory to assess |
| `--output` | `-o` | choice: `human`, `json` | `human` | Output format for the assessment report |
| `--check` | -- | choice: `all`, `pattern`, `layers`, `code` | `all` | Restrict to a specific check; `pattern` prints detected pattern only, `layers` exits non-zero on violations, `code` exits non-zero on warnings |
| `--verbose` | `-v` | flag | off | Print analysis progress (pattern detection, issue counts, violation counts) |
| `--save` | `-s` | string | none | Save JSON report to the specified file path |

- **Example**:

```bash
python scripts/project_architect.py ./my-app --check layers --verbose
```

```
Analyzing project: /home/user/my-app
Detected pattern: layered (confidence: 78%)
Found 2 code issues
Found 1 layer violations
Found 1 layer violation(s):
  controllers/PaymentController.ts: presentation layer should not depend on infrastructure layer
```

- **Output Formats**: Human-readable terminal report (default) with pattern detection, layer assignments, code issues, and prioritized recommendations; JSON structured report for automated quality gates and dashboard integration.
