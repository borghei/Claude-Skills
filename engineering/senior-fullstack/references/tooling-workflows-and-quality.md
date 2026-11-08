# Tooling, Workflows & Quality Bar

Read this when running the scaffolder or quality analyzer in depth, executing an
end-to-end project workflow, looking up the stack decision matrix / common issues,
troubleshooting tool behavior, or checking generated work against the quality bar.

## Tools

### Project Scaffolder

Generates fullstack project structures with boilerplate code.

**Supported Templates:**
- `nextjs` - Next.js 16 with App Router, React 19, TypeScript, Tailwind CSS v4
- `fastapi-react` - FastAPI backend + React frontend + PostgreSQL
- `mern` - MongoDB, Express, React, Node.js with TypeScript
- `django-react` - Django REST Framework + React frontend

**Usage:**

```bash
# List available templates
python scripts/project_scaffolder.py --list-templates

# Create Next.js project
python scripts/project_scaffolder.py nextjs my-app

# Create FastAPI + React project
python scripts/project_scaffolder.py fastapi-react my-api

# Create MERN stack project
python scripts/project_scaffolder.py mern my-project

# Create Django + React project
python scripts/project_scaffolder.py django-react my-app

# Specify output directory
python scripts/project_scaffolder.py nextjs my-app --output ./projects

# JSON output
python scripts/project_scaffolder.py nextjs my-app --json
```

**Parameters:**

| Parameter | Description |
|-----------|-------------|
| `template` | Template name (nextjs, fastapi-react, mern, django-react) |
| `project_name` | Name for the new project directory |
| `--output, -o` | Output directory (default: current directory) |
| `--list-templates, -l` | List all available templates |
| `--json` | Output in JSON format |

**Output includes:**
- Project structure with all necessary files
- Package configurations (package.json, requirements.txt)
- TypeScript configuration
- Docker and docker-compose setup
- Environment file templates
- Next steps for running the project

---

### Code Quality Analyzer

Analyzes fullstack codebases for quality issues.

**Analysis Categories:**
- Security vulnerabilities (hardcoded secrets, injection risks)
- Code complexity metrics (cyclomatic complexity, nesting depth)
- Dependency health (outdated packages, known CVEs)
- Test coverage estimation
- Documentation quality

**Usage:**

```bash
# Analyze current directory
python scripts/code_quality_analyzer.py .

# Analyze specific project
python scripts/code_quality_analyzer.py /path/to/project

# Verbose output with detailed findings
python scripts/code_quality_analyzer.py . --verbose

# JSON output
python scripts/code_quality_analyzer.py . --json

# Save report to file
python scripts/code_quality_analyzer.py . --output report.json
```

**Parameters:**

| Parameter | Description |
|-----------|-------------|
| `project_path` | Path to project directory (default: current directory) |
| `--verbose, -v` | Show detailed findings |
| `--json` | Output in JSON format |
| `--output, -o` | Write report to file |

**Output includes:**
- Overall score (0-100) with letter grade
- Security issues by severity (critical, high, medium, low)
- High complexity files
- Vulnerable dependencies with CVE references
- Test coverage estimate
- Documentation completeness
- Prioritized recommendations

**Sample Output:**

```
============================================================
CODE QUALITY ANALYSIS REPORT
============================================================

Overall Score: 75/100 (Grade: C)
Files Analyzed: 45
Total Lines: 12,500

--- SECURITY ---
  Critical: 1
  High: 2
  Medium: 5

--- COMPLEXITY ---
  Average Complexity: 8.5
  High Complexity Files: 3

--- RECOMMENDATIONS ---
1. [P0] SECURITY
   Issue: Potential hardcoded secret detected
   Action: Remove or secure sensitive data at line 42
```

---

## Workflows

### Workflow 1: Start New Project

1. Choose appropriate stack based on requirements
2. Scaffold project structure
3. Run initial quality check
4. Set up development environment

```bash
# 1. Scaffold project
python scripts/project_scaffolder.py nextjs my-saas-app

# 2. Navigate and install
cd my-saas-app
npm install

# 3. Configure environment
cp .env.example .env.local

# 4. Run quality check
python ../scripts/code_quality_analyzer.py .

# 5. Start development
npm run dev
```

### Workflow 2: Audit Existing Codebase

1. Run code quality analysis
2. Review security findings
3. Address critical issues first
4. Plan improvements

```bash
# 1. Full analysis
python scripts/code_quality_analyzer.py /path/to/project --verbose

# 2. Generate detailed report
python scripts/code_quality_analyzer.py /path/to/project --json --output audit.json

# 3. Address P0 issues immediately
# 4. Create tickets for P1/P2 issues
```

### Workflow 3: Stack Selection

Use the tech stack guide to evaluate options:

1. **SEO Required?** → Next.js with SSR
2. **API-heavy backend?** → Separate FastAPI or NestJS
3. **Real-time features?** → Add WebSocket layer
4. **Team expertise** → Match stack to team skills

See `references/tech_stack_guide.md` for detailed comparison.

---

## Quick Reference

### Stack Decision Matrix

| Requirement | Recommendation |
|-------------|---------------|
| SEO-critical site | Next.js with SSR |
| Internal dashboard | React + Vite |
| API-first backend | FastAPI or Fastify |
| Enterprise scale | NestJS + PostgreSQL |
| Rapid prototype | Next.js API routes |
| Document-heavy data | MongoDB |
| Complex queries | PostgreSQL |

### Common Issues

| Issue | Solution |
|-------|----------|
| N+1 queries | Use DataLoader or eager loading |
| Slow builds | Check bundle size, lazy load |
| Auth complexity | Use Auth.js or Clerk |
| Type errors | Enable strict mode in tsconfig |
| CORS issues | Configure middleware properly |

---

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| Scaffolder creates empty files | Template name misspelled or unsupported | Run `python project_scaffolder.py --list-templates` to verify available templates |
| Quality analyzer reports 0 files analyzed | Project path points to wrong directory or contains only non-code files | Confirm the path contains `.ts`, `.tsx`, `.js`, `.jsx`, `.py`, `.go`, `.java`, `.rb`, `.php`, or `.cs` files outside `node_modules/`, `.git/`, `dist/`, and other skip directories |
| False-positive hardcoded secret warnings | Regex matches long strings assigned to variables named `password`, `secret`, `token`, etc. | Review flagged lines manually; suppress by renaming variables or extracting values to `.env` files |
| Cyclomatic complexity score seems inflated | Analyzer counts all decision points (`if`, `else`, `for`, `while`, `&&`, `\|\|`) across the entire file, not per function | Use the score as a relative indicator; pair with `--verbose` to identify specific high-complexity files for refactoring |
| Dependency vulnerability check misses packages | Only a built-in subset of known CVEs is checked (lodash, axios, minimist, jsonwebtoken) | Supplement with `npm audit` or `pip-audit` for comprehensive CVE coverage |
| Docker Compose fails after scaffolding | Port 5432 already in use by a local PostgreSQL instance | Stop the local instance or remap the port in `docker-compose.yml` |
| Scaffolded Next.js project fails `npm install` | Node.js version below 18 or conflicting global packages | Use Node.js 18+ and run `npm install` in a clean shell without global `next` conflicts |

---

## Success Criteria

- **Quality score >= 80/100 (Grade B or higher)** on the code quality analyzer for all production codebases
- **Zero P0 (critical) security findings** before merging to main branch
- **Test file ratio >= 70%** of source files (estimated coverage target reported by the analyzer)
- **Average cyclomatic complexity < 15** across all analyzed files
- **No high-complexity files with nesting depth > 4** without documented justification
- **Scaffolded projects build and start successfully** on first run after `npm install` / `pip install`
- **Documentation score >= 75/100** (README, LICENSE, and either CONTRIBUTING or API docs present)

---

## Tool Reference

### project_scaffolder.py

**Purpose:** Generates complete fullstack project structures with boilerplate code, configuration files, Docker setup, and environment templates for four supported stack templates.

**Usage:**

```bash
python scripts/project_scaffolder.py <template> <project_name> [options]
python scripts/project_scaffolder.py --list-templates
```

**Flags:**

| Flag | Short | Type | Default | Description |
|------|-------|------|---------|-------------|
| `template` | -- | positional | (required) | Template name: `nextjs`, `fastapi-react`, `mern`, or `django-react` |
| `project_name` | -- | positional | (required) | Name for the new project directory |
| `--output` | `-o` | string | `.` (current directory) | Output directory where the project folder is created |
| `--list-templates` | `-l` | flag | false | List all available templates and exit |
| `--json` | -- | flag | false | Output result in JSON format |

**Example:**

```bash
# Scaffold a FastAPI + React project in a custom directory
python scripts/project_scaffolder.py fastapi-react my-api --output ./projects --json
```

**Output Formats:**

- **Human-readable (default):** Prints project name, template used, location on disk, file count, and numbered next steps for getting started.
- **JSON (`--json`):** Returns a structured object with keys: `success`, `project_name`, `template`, `description`, `location`, `files_created`, `directories_created`, `next_steps`. On failure, returns `success: false` with an `error` message and `available` templates list.

---

### code_quality_analyzer.py

**Purpose:** Performs comprehensive static analysis of fullstack codebases, reporting on security vulnerabilities, cyclomatic complexity, dependency health, test coverage estimation, documentation quality, and an overall quality score with prioritized recommendations.

**Usage:**

```bash
python scripts/code_quality_analyzer.py [project_path] [options]
```

**Flags:**

| Flag | Short | Type | Default | Description |
|------|-------|------|---------|-------------|
| `project_path` | -- | positional | `.` (current directory) | Path to the project directory to analyze |
| `--verbose` | `-v` | flag | false | Show detailed findings including individual security issue locations |
| `--json` | -- | flag | false | Output full analysis in JSON format |
| `--output` | `-o` | string | (none) | Write the report to a file (writes JSON regardless of `--json` flag when used with human-readable mode) |

**Example:**

```bash
# Full verbose analysis with JSON report saved to disk
python scripts/code_quality_analyzer.py /path/to/project --verbose --json --output audit.json
```

**Output Formats:**

- **Human-readable (default):** Prints a formatted report with sections for overall score/grade, language breakdown, security issue counts by severity, complexity metrics, dependency status, test coverage estimate, documentation checklist, and up to 10 prioritized recommendations. Use `--verbose` to expand individual security findings with file paths and line numbers.
- **JSON (`--json`):** Returns a structured object with keys: `summary`, `languages`, `security` (categorized by severity), `complexity`, `code_smells`, `dependencies`, `tests`, `documentation`, `overall_score`, `grade`, `recommendations`. Each recommendation includes `priority` (P0/P1/P2), `category`, `issue`, and `action`.
