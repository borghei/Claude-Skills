# Release Checklist: v{VERSION}

**Release Date:** {DATE}
**Release Manager:** {NAME}
**Release Type:** {Hotfix | Patch | Minor | Major | Pre-release}

---

## Pre-Flight

- [ ] Branch is up to date with base branch
- [ ] No merge conflicts with base branch
- [ ] No uncommitted changes in working tree
- [ ] No secrets detected in codebase
- [ ] .gitignore covers all sensitive file patterns
- [ ] All commits follow conventional commit format
- [ ] Dependency lock files are consistent

## Tests

- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] All E2E tests pass
- [ ] Code coverage meets threshold (target: 80%+)
- [ ] No new flaky tests introduced
- [ ] Coverage has not regressed from previous release

## Code Quality

- [ ] Linter passes with zero errors
- [ ] Type checker passes
- [ ] No high-complexity functions introduced
- [ ] No significant code duplication added
- [ ] Dead code removed

## Security

- [ ] No secrets in codebase (preflight_checker.py clean)
- [ ] Dependency vulnerabilities resolved (zero critical/high CVEs)
- [ ] SAST scan clean

## Documentation

- [ ] README updated for new features
- [ ] API documentation current
- [ ] Changelog generated
- [ ] Migration guide provided (if breaking changes)

## Breaking Changes

- [ ] Breaking changes documented in release notes
- [ ] Migration path provided for consumers
- [ ] Deprecation notices issued in prior release

## Dependencies

- [ ] Lock files regenerated and committed
- [ ] No yanked packages in dependency tree
- [ ] Major dependency upgrades reviewed and tested

## Deployment

- [ ] Version bumped (version_bumper.py)
- [ ] Changelog generated (changelog_generator.py)
- [ ] Release readiness score >= 80 (release_readiness_scorer.py)
- [ ] Rollback plan documented
- [ ] Database migrations reversible
- [ ] Feature flags in place for new features
- [ ] Monitoring and alerting configured

## Post-Deploy

- [ ] Smoke tests pass in production
- [ ] Key metrics within baseline (error rate, latency)
- [ ] Stakeholders notified
- [ ] Release notes published

---

## Sign-Off

| Role | Name | Approved | Date |
|---|---|---|---|
| Engineering Lead | | [ ] | |
| QA Lead | | [ ] | |
| Product Owner | | [ ] | |

## Notes

{Add any release-specific notes, known issues, or follow-up items here.}
