---
name: release-manager
description: Automates release management with changelog generation, semantic versioning, and release readiness checks. Use when preparing releases, generating changelogs, bumping versions, or validating release candidates.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  category: engineering
  domain: devops
  tier: POWERFUL
---

# Release Manager

**Tier:** POWERFUL
**Category:** Engineering
**Domain:** Software Release Management & DevOps

## Overview

The Release Manager skill provides comprehensive tools and knowledge for managing software releases end-to-end. From parsing conventional commits to generating changelogs, determining version bumps, and orchestrating release processes, this skill ensures reliable, predictable, and well-documented software releases.

## Core Capabilities

- **Automated Changelog Generation** from git history using conventional commits
- **Semantic Version Bumping** based on commit analysis and breaking changes
- **Release Readiness Assessment** with comprehensive checklists and validation
- **Release Planning & Coordination** with stakeholder communication templates
- **Rollback Planning** with automated recovery procedures
- **Hotfix Management** for emergency releases
- **Feature Flag Integration** for progressive rollouts

## Key Components

### Scripts

1. **changelog_generator.py** - Parses git logs and generates structured changelogs
2. **version_bumper.py** - Determines correct version bumps from conventional commits
3. **release_planner.py** - Assesses release readiness and generates coordination plans

### Documentation

- Comprehensive release management methodology
- Conventional commits specification and examples
- Release workflow comparisons (Git Flow, Trunk-based, GitHub Flow)
- Hotfix procedures and emergency response protocols

## Release Management Methodology

### Semantic Versioning (SemVer)

Semantic Versioning follows the MAJOR.MINOR.PATCH format where:

- **MAJOR** version when you make incompatible API changes
- **MINOR** version when you add functionality in a backwards compatible manner  
- **PATCH** version when you make backwards compatible bug fixes

#### Pre-release Versions

Pre-release versions are denoted by appending a hyphen and identifiers:
- `1.0.0-alpha.1` - Alpha releases for early testing
- `1.0.0-beta.2` - Beta releases for wider testing
- `1.0.0-rc.1` - Release candidates for final validation

#### Version Precedence

Version precedence is determined by comparing each identifier:
1. `1.0.0-alpha` < `1.0.0-alpha.1` < `1.0.0-alpha.beta` < `1.0.0-beta`
2. `1.0.0-beta` < `1.0.0-beta.2` < `1.0.0-beta.11` < `1.0.0-rc.1`
3. `1.0.0-rc.1` < `1.0.0`

### Conventional Commits

Conventional Commits provide a structured format for commit messages that enables automated tooling:

#### Format
```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

#### Types
- **feat**: A new feature (correlates with MINOR version bump)
- **fix**: A bug fix (correlates with PATCH version bump)
- **docs**: Documentation only changes
- **style**: Changes that do not affect the meaning of the code
- **refactor**: A code change that neither fixes a bug nor adds a feature
- **perf**: A code change that improves performance
- **test**: Adding missing tests or correcting existing tests
- **chore**: Changes to the build process or auxiliary tools
- **ci**: Changes to CI configuration files and scripts
- **build**: Changes that affect the build system or external dependencies
- **breaking**: Introduces a breaking change (correlates with MAJOR version bump)

#### Examples
```
feat(user-auth): add OAuth2 integration

fix(api): resolve race condition in user creation

docs(readme): update installation instructions

feat!: remove deprecated payment API
BREAKING CHANGE: The legacy payment API has been removed
```

### Automated Changelog Generation

Changelogs are automatically generated from conventional commits, organized by:

#### Structure
```markdown
# Changelog

## [Unreleased]
### Added
### Changed  
### Deprecated
### Removed
### Fixed
### Security

## [1.2.0] - 2024-01-15
### Added
- OAuth2 authentication support (#123)
- User preference dashboard (#145)

### Fixed
- Race condition in user creation (#134)
- Memory leak in image processing (#156)

### Breaking Changes
- Removed legacy payment API
```

#### Grouping Rules
- **Added** for new features (feat)
- **Fixed** for bug fixes (fix)
- **Changed** for changes in existing functionality
- **Deprecated** for soon-to-be removed features
- **Removed** for now removed features
- **Security** for vulnerability fixes

#### Metadata Extraction
- Link to pull requests and issues: `(#123)`
- Breaking changes highlighted prominently
- Scope-based grouping: `auth:`, `api:`, `ui:`
- Co-authored-by for contributor recognition

### Version Bump Strategies

Version bumps are determined by analyzing commits since the last release:

#### Automatic Detection Rules
1. **MAJOR**: Any commit with `BREAKING CHANGE` or `!` after type
2. **MINOR**: Any `feat` type commits without breaking changes
3. **PATCH**: `fix`, `perf`, `security` type commits
4. **NO BUMP**: `docs`, `style`, `test`, `chore`, `ci`, `build` only

#### Pre-release Handling
```python
# Alpha: 1.0.0-alpha.1 → 1.0.0-alpha.2
# Beta: 1.0.0-alpha.5 → 1.0.0-beta.1  
# RC: 1.0.0-beta.3 → 1.0.0-rc.1
# Release: 1.0.0-rc.2 → 1.0.0
```

#### Multi-package Considerations
For monorepos with multiple packages:
- Analyze commits affecting each package independently
- Support scoped version bumps: `@scope/package@1.2.3`
- Generate coordinated release plans across packages

### Release Branch Workflows

#### Git Flow
```
main (production) ← release/1.2.0 ← develop ← feature/login
                                           ← hotfix/critical-fix
```

**Advantages:**
- Clear separation of concerns
- Stable main branch
- Parallel feature development
- Structured release process

**Process:**
1. Create release branch from develop: `git checkout -b release/1.2.0 develop`
2. Finalize release (version bump, changelog)
3. Merge to main and develop
4. Tag release: `git tag v1.2.0`
5. Deploy from main

#### Trunk-based Development
```
main ← feature/login (short-lived)
    ← feature/payment (short-lived)  
    ← hotfix/critical-fix
```

**Advantages:**
- Simplified workflow
- Faster integration
- Reduced merge conflicts
- Continuous integration friendly

**Process:**
1. Short-lived feature branches (1-3 days)
2. Frequent commits to main
3. Feature flags for incomplete features
4. Automated testing gates
5. Deploy from main with feature toggles

#### GitHub Flow
```
main ← feature/login
    ← hotfix/critical-fix
```

**Advantages:**
- Simple and lightweight
- Fast deployment cycle
- Good for web applications
- Minimal overhead

**Process:**
1. Create feature branch from main
2. Regular commits and pushes
3. Open pull request when ready
4. Deploy from feature branch for testing
5. Merge to main and deploy

### Feature Flag Integration

Feature flags enable safe, progressive rollouts:

#### Types of Feature Flags
- **Release flags**: Control feature visibility in production
- **Experiment flags**: A/B testing and gradual rollouts
- **Operational flags**: Circuit breakers and performance toggles
- **Permission flags**: Role-based feature access

#### Implementation Strategy
```python
# Progressive rollout example
if feature_flag("new_payment_flow", user_id):
    return new_payment_processor.process(payment)
else:
    return legacy_payment_processor.process(payment)
```

#### Release Coordination
1. Deploy code with feature behind flag (disabled)
2. Gradually enable for percentage of users
3. Monitor metrics and error rates
4. Full rollout or quick rollback based on data
5. Remove flag in subsequent release

### Release Readiness Checklists

#### Pre-Release Validation
- [ ] All planned features implemented and tested
- [ ] Breaking changes documented with migration guide
- [ ] API documentation updated
- [ ] Database migrations tested
- [ ] Security review completed for sensitive changes
- [ ] Performance testing passed thresholds
- [ ] Internationalization strings updated
- [ ] Third-party integrations validated

#### Quality Gates
- [ ] Unit test coverage ≥ 85%
- [ ] Integration tests passing
- [ ] End-to-end tests passing
- [ ] Static analysis clean
- [ ] Security scan passed
- [ ] Dependency audit clean
- [ ] Load testing completed

#### Documentation Requirements
- [ ] CHANGELOG.md updated
- [ ] README.md reflects new features
- [ ] API documentation generated
- [ ] Migration guide written for breaking changes
- [ ] Deployment notes prepared
- [ ] Rollback procedure documented

#### Stakeholder Approvals
- [ ] Product Manager sign-off
- [ ] Engineering Lead approval
- [ ] QA validation complete
- [ ] Security team clearance
- [ ] Legal review (if applicable)
- [ ] Compliance check (if regulated)

### Deployment Coordination

#### Communication Plan
**Internal Stakeholders:**
- Engineering team: Technical changes and rollback procedures
- Product team: Feature descriptions and user impact
- Support team: Known issues and troubleshooting guides
- Sales team: Customer-facing changes and talking points

**External Communication:**
- Release notes for users
- API changelog for developers
- Migration guide for breaking changes
- Downtime notifications if applicable

#### Deployment Sequence
1. **Pre-deployment** (T-24h): Final validation, freeze code
2. **Database migrations** (T-2h): Run and validate schema changes  
3. **Blue-green deployment** (T-0): Switch traffic gradually
4. **Post-deployment** (T+1h): Monitor metrics and logs
5. **Rollback window** (T+4h): Decision point for rollback

#### Monitoring & Validation
- Application health checks
- Error rate monitoring
- Performance metrics tracking
- User experience monitoring
- Business metrics validation
- Third-party service integration health

### Hotfix Procedures

Hotfixes address critical production issues requiring immediate deployment:

#### Severity Classification
**P0 - Critical**: Complete system outage, data loss, security breach
- **SLA**: Fix within 2 hours
- **Process**: Emergency deployment, all hands on deck
- **Approval**: Engineering Lead + On-call Manager

**P1 - High**: Major feature broken, significant user impact
- **SLA**: Fix within 24 hours  
- **Process**: Expedited review and deployment
- **Approval**: Engineering Lead + Product Manager

**P2 - Medium**: Minor feature issues, limited user impact
- **SLA**: Fix in next release cycle
- **Process**: Normal review process
- **Approval**: Standard PR review

#### Emergency Response Process
1. **Incident declaration**: Page on-call team
2. **Assessment**: Determine severity and impact
3. **Hotfix branch**: Create from last stable release
4. **Minimal fix**: Address root cause only
5. **Expedited testing**: Automated tests + manual validation
6. **Emergency deployment**: Deploy to production
7. **Post-incident**: Root cause analysis and prevention

### Rollback Planning

Every release must have a tested rollback plan:

#### Rollback Triggers
- **Error rate spike**: >2x baseline within 30 minutes
- **Performance degradation**: >50% latency increase
- **Feature failures**: Core functionality broken
- **Security incident**: Vulnerability exploited
- **Data corruption**: Database integrity compromised

#### Rollback Types
**Code Rollback:**
- Revert to previous Docker image
- Database-compatible code changes only
- Feature flag disable preferred over code rollback

**Database Rollback:**
- Only for non-destructive migrations
- Data backup required before migration
- Forward-only migrations preferred (add columns, not drop)

**Infrastructure Rollback:**
- Blue-green deployment switch
- Load balancer configuration revert
- DNS changes (longer propagation time)

#### Automated Rollback
```python
# Example rollback automation
def monitor_deployment():
    if error_rate() > THRESHOLD:
        alert_oncall("Error rate spike detected")
        if auto_rollback_enabled():
            execute_rollback()
```

### Release Metrics & Analytics

#### Key Performance Indicators
- **Lead Time**: From commit to production
- **Deployment Frequency**: Releases per week/month
- **Mean Time to Recovery**: From incident to resolution
- **Change Failure Rate**: Percentage of releases causing incidents

#### Quality Metrics
- **Rollback Rate**: Percentage of releases rolled back
- **Hotfix Rate**: Hotfixes per regular release
- **Bug Escape Rate**: Production bugs per release
- **Time to Detection**: How quickly issues are identified

#### Process Metrics
- **Review Time**: Time spent in code review
- **Testing Time**: Automated + manual testing duration
- **Approval Cycle**: Time from PR to merge
- **Release Preparation**: Time spent on release activities

### Tool Integration

#### Version Control Systems
- **Git**: Primary VCS with conventional commit parsing
- **GitHub/GitLab**: Pull request automation and CI/CD
- **Bitbucket**: Pipeline integration and deployment gates

#### CI/CD Platforms
- **Jenkins**: Pipeline orchestration and deployment automation
- **GitHub Actions**: Workflow automation and release publishing
- **GitLab CI**: Integrated pipelines with environment management
- **CircleCI**: Container-based builds and deployments

#### Monitoring & Alerting
- **DataDog**: Application performance monitoring
- **New Relic**: Error tracking and performance insights
- **Sentry**: Error aggregation and release tracking
- **PagerDuty**: Incident response and escalation

#### Communication Platforms
- **Slack**: Release notifications and coordination
- **Microsoft Teams**: Stakeholder communication
- **Email**: External customer notifications
- **Status Pages**: Public incident communication

## Best Practices

### Release Planning
1. **Regular cadence**: Establish predictable release schedule
2. **Feature freeze**: Lock changes 48h before release
3. **Risk assessment**: Evaluate changes for potential impact
4. **Stakeholder alignment**: Ensure all teams are prepared

### Quality Assurance
1. **Automated testing**: Comprehensive test coverage
2. **Staging environment**: Production-like testing environment
3. **Canary releases**: Gradual rollout to subset of users
4. **Monitoring**: Proactive issue detection

### Communication
1. **Clear timelines**: Communicate schedules early
2. **Regular updates**: Status reports during release process
3. **Issue transparency**: Honest communication about problems
4. **Post-mortems**: Learn from incidents and improve

### Automation
1. **Reduce manual steps**: Automate repetitive tasks
2. **Consistent process**: Same steps every time
3. **Audit trails**: Log all release activities
4. **Self-service**: Enable teams to deploy safely

## Common Anti-patterns

### Process Anti-patterns
- **Manual deployments**: Error-prone and inconsistent
- **Last-minute changes**: Risk introduction without proper testing
- **Skipping testing**: Deploying without validation
- **Poor communication**: Stakeholders unaware of changes

### Technical Anti-patterns
- **Monolithic releases**: Large, infrequent releases with high risk
- **Coupled deployments**: Services that must be deployed together
- **No rollback plan**: Unable to quickly recover from issues
- **Environment drift**: Production differs from staging

### Cultural Anti-patterns
- **Blame culture**: Fear of making changes or reporting issues
- **Hero culture**: Relying on individuals instead of process
- **Perfectionism**: Delaying releases for minor improvements
- **Risk aversion**: Avoiding necessary changes due to fear

## Getting Started

1. **Assessment**: Evaluate current release process and pain points
2. **Tool setup**: Configure scripts for your repository
3. **Process definition**: Choose appropriate workflow for your team
4. **Automation**: Implement CI/CD pipelines and quality gates
5. **Training**: Educate team on new processes and tools
6. **Monitoring**: Set up metrics and alerting for releases
7. **Iteration**: Continuously improve based on feedback and metrics

The Release Manager skill transforms chaotic deployments into predictable, reliable releases that build confidence across your entire organization.

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| Changelog generator produces empty output | Non-conventional commit messages that don't match the `type(scope): description` pattern | Ensure all commits follow conventional commit format; non-matching messages default to `chore` type which is excluded from user-facing changelogs |
| Version bumper recommends `none` despite meaningful commits | Commits use types in the ignore list (`test`, `ci`, `build`, `chore`, `docs`, `style`) | Use `feat` for new features and `fix` for bug fixes; override with `--custom-rules` to map additional types to bump levels |
| Release planner reports `blocked` status unexpectedly | Missing required approvals (`pm_approved`, `qa_approved`) on features or failed required quality gates | Review the `blocking_issues` array in the assessment output; ensure all features have the necessary approval flags set to `true` in the input JSON |
| Pre-release version not incrementing correctly | Existing pre-release type does not match the requested `--prerelease` type, causing a reset to `.1` | When promoting from alpha to beta or beta to rc, the counter resets to 1 by design; to stay on the same track, pass the same pre-release type |
| Git log parsing misses commits | Input uses full `git log` format but lines are not properly indented with 4 spaces | Use `git log --oneline` for the simplest input format, or ensure the full format output preserves the standard 4-space commit message indent |
| Readiness score seems too low | Quality gates default to `pending` status when not explicitly set, and pending gates score zero points | Provide explicit `quality_gates` with accurate `status` values in the release plan JSON, or complete the gates before running assessment |
| Rollback time estimate is inaccurate | Default rollback steps use generic time estimates that don't reflect your infrastructure | Supply custom `rollback_steps` in the release plan JSON with `estimated_time` values that match your actual deployment environment |

## Success Criteria

- **Changelog accuracy**: 100% of conventional commits are correctly categorized (feat to Added, fix to Fixed, etc.) with zero miscategorized entries
- **Version bump correctness**: Recommended version matches SemVer rules in all cases -- breaking changes produce MAJOR, features produce MINOR, fixes produce PATCH
- **Readiness assessment coverage**: All blocking issues (missing approvals, failed quality gates, overdue timelines) are surfaced with zero false negatives
- **Release cycle time reduction**: Teams using the planner reduce release preparation time by 40% or more compared to manual checklist tracking
- **Rollback preparedness**: Every release assessed by the planner has a complete, actionable rollback runbook with time estimates and verification steps
- **Stakeholder communication**: Communication plans cover all identified stakeholders with appropriate timing (T-48h external, T-24h internal, T+1h post-deploy)
- **Tool integration time**: New teams can configure and run all three scripts against their repository within 30 minutes of initial setup

## Scope & Limitations

**This skill covers:**
- Parsing conventional commits and generating structured changelogs in Markdown and JSON formats
- Determining semantic version bumps (major/minor/patch) with pre-release support (alpha, beta, rc)
- Assessing release readiness across features, quality gates, approvals, and timelines
- Generating rollback runbooks, communication plans, and release checklists from structured input

**This skill does NOT cover:**
- Actual CI/CD pipeline execution or deployment automation (see `engineering/ci-cd-pipeline-generator`)
- Live monitoring, alerting, or incident response during deployments (see `engineering/monitoring-alerting-setup`)
- Code review processes or pull request management (see `engineering/code-review-automation`)
- Infrastructure provisioning, container orchestration, or environment management (see `engineering/infrastructure-as-code`)

## Integration Points

| Skill | Integration | Data Flow |
|-------|-------------|-----------|
| `engineering/ci-cd-pipeline-generator` | Embed changelog generation and version bumping as pipeline stages | Git log output flows into `changelog_generator.py`; version bump output feeds pipeline tagging steps |
| `engineering/code-review-automation` | Validate that PR commits follow conventional commit format before merge | Commit messages validated upstream ensure clean input for changelog generation |
| `engineering/monitoring-alerting-setup` | Define rollback triggers based on monitoring thresholds from the rollback runbook | Rollback trigger thresholds (error rate >2x, latency >50%) feed into alert rule configuration |
| `engineering/api-design-reviewer` | Breaking API changes flagged by the reviewer map to MAJOR version bumps | API review findings populate `breaking_changes` arrays in the release plan JSON |
| `engineering/infrastructure-as-code` | Deployment steps in the rollback runbook reference infrastructure rollback commands | Rollback runbook `command` fields contain infrastructure-specific commands (kubectl, DNS, load balancer) |
| `project-management/release-planning` | Release plan JSON structure aligns with PM release tracking artifacts | PM feature lists and approval statuses feed directly into `release_planner.py` input format |

## Tool Reference

### changelog_generator.py

**Purpose:** Parses git log output in conventional commit format and generates structured changelogs. Groups commits by type (Added, Fixed, Changed, etc.), extracts scope and issue references, and highlights breaking changes.

**Usage:**
```bash
git log --oneline v1.0.0..HEAD | python changelog_generator.py
python changelog_generator.py --input commits.txt --version 2.0.0 --format json
cat commits.json | python changelog_generator.py --input-format json --summary
```

**Flags/Parameters:**

| Flag | Short | Type | Default | Description |
|------|-------|------|---------|-------------|
| `--input` | `-i` | string | stdin | Input file path; reads from stdin if omitted |
| `--format` | `-f` | choice | `markdown` | Output format: `markdown`, `json`, or `both` |
| `--version` | `-v` | string | `Unreleased` | Version label for the changelog section header |
| `--date` | `-d` | string | today | Release date in YYYY-MM-DD format |
| `--base-url` | `-u` | string | empty | Base repository URL for commit links (e.g., `https://github.com/org/repo`) |
| `--input-format` | | choice | `git-log` | Input format: `git-log` (oneline or full) or `json` (array of commit objects) |
| `--output` | `-o` | string | stdout | Output file path; prints to stdout if omitted |
| `--summary` | `-s` | flag | false | Append release summary statistics (total commits, by type, breaking changes, issue references) |

**Example:**
```bash
git log --oneline v1.2.0..HEAD | python changelog_generator.py \
  --version 1.3.0 \
  --date 2026-03-21 \
  --base-url https://github.com/myorg/myapp \
  --format both \
  --summary
```

**Output Formats:**
- **markdown**: Keep a Changelog format with sections for Breaking Changes, Added, Changed, Deprecated, Removed, Fixed, Security. Commits grouped by scope within each section.
- **json**: Structured object with `version`, `date`, `summary` (counts by type, by author, scopes, issue references), and `categories` (arrays of commit objects per category).
- **both**: Markdown changelog followed by JSON output, each with a heading separator.

---

### version_bumper.py

**Purpose:** Analyzes conventional commits since the last tag to determine the correct semantic version bump (major/minor/patch). Supports pre-release versions (alpha, beta, rc) and generates version bump commands for npm, Python, Rust, Git, and Docker.

**Usage:**
```bash
git log --oneline v1.2.0..HEAD | python version_bumper.py --current-version 1.2.0
python version_bumper.py -c 2.0.0-beta.3 -i commits.json --input-format json --prerelease rc
git log --oneline v1.0.0..HEAD | python version_bumper.py -c 1.0.0 -f json --analysis --include-commands
```

**Flags/Parameters:**

| Flag | Short | Type | Default | Description |
|------|-------|------|---------|-------------|
| `--current-version` | `-c` | string | **required** | Current version (e.g., `1.2.3`, `v1.2.3`, `1.0.0-beta.2`) |
| `--input` | `-i` | string | stdin | Input file with commits; reads from stdin if omitted |
| `--input-format` | | choice | `git-log` | Input format: `git-log` (oneline) or `json` (array of commit objects) |
| `--prerelease` | `-p` | choice | none | Generate pre-release version: `alpha`, `beta`, or `rc` |
| `--output-format` | `-f` | choice | `text` | Output format: `text`, `json`, or `commands` |
| `--output` | `-o` | string | stdout | Output file path; prints to stdout if omitted |
| `--include-commands` | | flag | false | Include version bump commands for npm, Python, Rust, Git, and Docker |
| `--include-files` | | flag | false | Include file update snippets for package.json, pyproject.toml, setup.py, Cargo.toml, __init__.py |
| `--custom-rules` | | string | none | JSON string mapping commit types to bump levels (e.g., `'{"perf": "minor"}'`) |
| `--ignore-types` | | string | `test,ci,build,chore,docs,style` | Comma-separated list of commit types to ignore for bump determination |
| `--analysis` | `-a` | flag | false | Include detailed commit analysis (breaking changes list, features list, fixes list, ignored list) |

**Example:**
```bash
git log --oneline v2.1.0..HEAD | python version_bumper.py \
  --current-version 2.1.0 \
  --output-format json \
  --analysis \
  --include-commands \
  --include-files
```

**Output Formats:**
- **text**: Human-readable summary with current version, recommended version, bump type, and optional analysis/commands.
- **json**: Structured object with `current_version`, `recommended_version`, `bump_type`, and optional `analysis`, `commands`, and `file_updates` fields.
- **commands**: Shell-ready version bump commands organized by platform (npm, Python, Rust, Git, Docker).

---

### release_planner.py

**Purpose:** Takes a release plan JSON (features, quality gates, stakeholders, target date) and assesses release readiness. Generates a readiness report with scoring, a release checklist, a stakeholder communication plan with message templates, and a rollback runbook.

**Usage:**
```bash
python release_planner.py --input release-plan.json
python release_planner.py -i plan.json -f json --include-checklist --include-rollback
python release_planner.py -i plan.json -f markdown --include-checklist --include-communication --include-rollback
```

**Flags/Parameters:**

| Flag | Short | Type | Default | Description |
|------|-------|------|---------|-------------|
| `--input` | `-i` | string | **required** | Path to release plan JSON file |
| `--output-format` | `-f` | choice | `text` | Output format: `json`, `markdown`, or `text` |
| `--output` | `-o` | string | stdout | Output file path; prints to stdout if omitted |
| `--include-checklist` | | flag | false | Include the full release checklist (pre-release validation, quality gates, approvals, documentation, deployment) |
| `--include-communication` | | flag | false | Include stakeholder communication plan with timeline and message templates |
| `--include-rollback` | | flag | false | Include rollback runbook with step-by-step procedures, triggers, and verification checks |
| `--min-coverage` | | float | `80.0` | Minimum test coverage threshold percentage for quality gate validation |

**Example:**
```bash
python release_planner.py \
  --input release-plan.json \
  --output-format json \
  --output readiness-report.json \
  --include-checklist \
  --include-communication \
  --include-rollback \
  --min-coverage 85.0
```

**Input JSON Structure:**
The input file expects a JSON object with keys: `release_name`, `version`, `target_date` (ISO format), `features` (array of feature objects with `id`, `title`, `type`, `status`, `risk_level`, approvals, etc.), `quality_gates` (optional array), `stakeholders` (optional array), and `rollback_steps` (optional array). When `quality_gates` or `rollback_steps` are omitted, sensible defaults are generated automatically.

**Output Formats:**
- **text**: Plain text report with status, readiness score, blocking issues, warnings, recommendations, feature summary, and quality gate summary.
- **markdown**: Formatted Markdown report with headings, status icons, and structured feature/checklist sections.
- **json**: Complete structured object with `assessment`, `checklist`, `communication_plan`, and `rollback_runbook` fields (null when not requested).