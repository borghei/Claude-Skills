---
description: Design or review a CI/CD pipeline for the current project.
---

Design or review a CI/CD pipeline:

1. **Detect project stack** — scan for package.json (Node), requirements.txt/pyproject.toml (Python), go.mod (Go), Cargo.toml (Rust), Gemfile (Ruby), pom.xml (Java), etc.
2. **Identify existing CI** — check for .github/workflows/, .gitlab-ci.yml, Jenkinsfile, .circleci/, bitbucket-pipelines.yml.
3. **Design pipeline stages:**
   - **Lint**: language-appropriate linters (eslint, ruff, golangci-lint)
   - **Type Check**: TypeScript, mypy, etc. if applicable
   - **Unit Tests**: with coverage reporting
   - **Integration Tests**: if test infrastructure exists
   - **Security Scan**: dependency audit, SAST, secret detection
   - **Build**: compile/bundle/containerize
   - **Deploy**: staging then production, with approval gates
4. **Generate workflow YAML** for the detected CI platform (default: GitHub Actions).
5. **Identify missing quality gates:**
   - No test step? Flag it.
   - No security scan? Recommend one.
   - No branch protection? Suggest rules.
   - No deployment approval? Add manual gate for production.
6. **Output** the complete pipeline configuration file ready to commit.
