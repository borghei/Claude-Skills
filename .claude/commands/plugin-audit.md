---
description: Audit installed plugins, extensions, and dependencies for security and health.
---

Audit project plugins and extensions:

1. **Discover installed plugins/dependencies:**
   - npm packages (package.json)
   - Python packages (requirements.txt, pyproject.toml, Pipfile)
   - VS Code extensions (.vscode/extensions.json)
   - Browser extensions referenced in code
   - GitHub Actions used in workflows
   - MCP servers configured
2. **Security check per dependency:**
   - Known CVEs (check against advisory databases)
   - Last published date (flag if > 1 year ago — possibly unmaintained)
   - Download count / popularity (flag low-adoption packages)
   - Permission scope (what does it access?)
   - Maintainer count (single-maintainer risk)
3. **Version health:**
   - How many major versions behind latest?
   - Are there breaking changes in available updates?
   - Is the package deprecated?
4. **License audit:**
   - Identify all license types
   - Flag copyleft licenses (GPL) in proprietary projects
   - Flag missing licenses (unknown risk)
5. **Supply chain risk:**
   - Packages with install scripts (postinstall hooks)
   - Packages with native bindings
   - Transitive dependency count (flag if > 100 deep)
6. **Output** a risk-scored audit report with: package name, version, risk level (high/medium/low), specific concerns, and recommended action (update/replace/remove/accept).
