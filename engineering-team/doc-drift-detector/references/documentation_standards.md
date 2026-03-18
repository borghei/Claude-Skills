# Documentation Standards Reference

Expert knowledge for writing, maintaining, and evaluating technical documentation across all common formats.

---

## README Structure Best Practices

A well-structured README is the front door to any project. Follow this ordering for maximum clarity:

### Essential Sections (in order)

1. **Title and Description** -- One sentence explaining what the project does. No jargon in the first paragraph.
2. **Badges** -- Build status, version, license, coverage. Keep to 4-6 maximum.
3. **Table of Contents** -- Required for READMEs longer than 100 lines.
4. **Installation** -- Copy-pasteable commands. Cover all supported platforms. Include prerequisites.
5. **Quick Start / Usage** -- The shortest path from install to working example. Under 10 lines of code.
6. **API Reference** -- Or link to full API docs. Include the most-used functions inline.
7. **Configuration** -- Environment variables, config files, CLI flags. Use tables.
8. **Examples** -- Real-world use cases beyond the quick start. Link to example directory if extensive.
9. **Architecture** -- High-level diagram or description for contributors. Can link to ARCHITECTURE.md.
10. **Contributing** -- Or link to CONTRIBUTING.md. Include setup instructions for development.
11. **License** -- State the license and link to LICENSE file.
12. **Changelog** -- Or link to CHANGELOG.md.

### README Anti-Patterns

- Wall of text with no headings
- Installation instructions that assume specific OS
- Examples that reference files not in the repo
- Badges that point to broken CI pipelines
- "TODO" placeholders left in published README
- Version numbers hardcoded in multiple places
- Screenshots from 3 versions ago

---

## API Documentation Patterns

### Function Documentation

Every public function should document:

- **Purpose** -- One sentence on what it does
- **Parameters** -- Name, type, description, default value, whether required
- **Return value** -- Type and description
- **Exceptions** -- What errors it can raise and when
- **Example** -- At least one usage example
- **Since** -- Version when the function was introduced

### Class Documentation

- **Purpose** -- What the class represents
- **Constructor parameters** -- Same detail as function parameters
- **Public methods** -- Each documented as a function
- **Properties** -- Type and description
- **Usage example** -- Instantiation through common operations

### Module Documentation

- **Overview** -- What the module provides
- **Public API listing** -- All exported classes, functions, constants
- **Dependency notes** -- What this module requires
- **Usage patterns** -- Common import and usage patterns

### API Doc Formats

| Format | Best For | Tooling |
|--------|----------|---------|
| Docstrings (Python) | Python libraries | Sphinx, pdoc, mkdocstrings |
| JSDoc | JavaScript/TypeScript | TypeDoc, documentation.js |
| OpenAPI/Swagger | REST APIs | Swagger UI, Redoc |
| GraphQL SDL | GraphQL APIs | GraphiQL, Apollo Studio |
| gRPC Proto | gRPC services | protoc-gen-doc |

---

## Changelog Conventions

Follow [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) format:

### Structure

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.2.0] - 2026-03-18

### Added
- New drift detection algorithm for renamed files

### Changed
- Improved staleness scoring weights

### Deprecated
- Old `--verbose` flag (use `--log-level` instead)

### Removed
- Python 3.7 support

### Fixed
- False positives in anchor validation

### Security
- Updated dependency to patch CVE-2026-XXXX
```

### Changelog Rules

- Every user-facing change gets an entry
- Group by type (Added, Changed, Deprecated, Removed, Fixed, Security)
- Most recent version first
- Include dates in ISO 8601 format
- Link version headers to git comparison URLs
- Keep an `[Unreleased]` section for in-progress changes
- Write for the user, not the developer ("Added search feature" not "Implemented ElasticSearch integration in SearchService")

---

## Architecture Decision Records (ADRs)

### ADR Format

```markdown
# ADR-NNN: Title

## Status
Proposed | Accepted | Deprecated | Superseded by ADR-NNN

## Context
What is the issue that we are seeing that is motivating this decision?

## Decision
What is the change that we are proposing and/or doing?

## Consequences
What becomes easier or harder to do because of this change?
```

### ADR Best Practices

- Number sequentially, never reuse numbers
- Keep each ADR focused on a single decision
- Record the date of the decision
- Link to related ADRs
- Update status when superseded (do not delete old ADRs)
- Store in `docs/adr/` or `docs/decisions/`
- Include ADR index in project documentation

---

## Documentation-as-Code Principles

### Core Principles

1. **Docs live with code** -- Same repository, same branch, same PR
2. **Docs are reviewed** -- Documentation changes go through code review
3. **Docs are tested** -- Link checking, spell checking, build verification
4. **Docs are versioned** -- Tagged with releases, branches for versions
5. **Docs are automated** -- Generated where possible, validated in CI

### File Organization

```
project/
├── README.md              # Entry point
├── CONTRIBUTING.md        # How to contribute
├── CHANGELOG.md           # Version history
├── LICENSE                # License text
├── docs/
│   ├── getting-started.md # Expanded setup guide
│   ├── architecture.md    # System design
│   ├── api/               # API reference
│   ├── guides/            # How-to guides
│   ├── tutorials/         # Step-by-step tutorials
│   └── adr/               # Architecture decisions
└── src/                   # Source with inline docs
```

### The Four Types of Documentation

Following the Diataxis framework:

| Type | Purpose | Approach |
|------|---------|----------|
| **Tutorials** | Learning-oriented | Step-by-step lessons, hands-on |
| **How-to Guides** | Task-oriented | Practical steps to achieve a goal |
| **Reference** | Information-oriented | Accurate, complete technical description |
| **Explanation** | Understanding-oriented | Clarification, background, reasoning |

Each type serves a different need. A healthy project has all four.

---

**Last Updated:** 2026-03-18
