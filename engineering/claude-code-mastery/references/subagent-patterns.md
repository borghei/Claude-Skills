# Subagent Patterns

Comprehensive guide to creating and using Claude Code subagents for parallel work,
specialized review, automated workflows, and task delegation.

---

## Table of Contents

- [What Are Subagents](#what-are-subagents)
- [Built-in Agent Support](#built-in-agent-support)
- [Custom Agent Creation](#custom-agent-creation)
- [Agent File Anatomy](#agent-file-anatomy)
- [Tool Access Patterns](#tool-access-patterns)
- [Delegation Patterns](#delegation-patterns)
- [Memory and State](#memory-and-state)
- [Isolation Modes](#isolation-modes)
- [Hooks Integration](#hooks-integration)
- [Production Recipes](#production-recipes)

---

## What Are Subagents

Subagents are specialized Claude Code instances that run with their own system
prompts, tool restrictions, and behavioral instructions. They operate in
isolation from the main conversation but can return results.

**Key properties:**
- Run with their own system prompt (the Markdown body of the agent file)
- Can be restricted to specific tools (the `tools` frontmatter field)
- Execute in the same project directory
- Return their output to the calling conversation
- Do not share conversation history with the main session

**When to use subagents:**
- Specialized review tasks (security, performance, accessibility)
- Parallel research across multiple files
- Automated generation with strict constraints
- Tasks that benefit from a fresh context window

---

## Built-in Agent Support

Claude Code ships with several built-in agents that are always available
without custom configuration.

### Explore Agent

**Purpose:** Read-only codebase exploration and analysis.

**Capabilities:**
- Read files, search with Glob and Grep
- Navigate directory structures
- Cannot modify any files

**When to use:**
- Understanding unfamiliar codebases
- Finding where a feature is implemented
- Tracing data flow across files
- Answering "where is X defined" questions

**Invocation:**
```
Use the Explore subagent to find how authentication is implemented in this project
```

### Plan Agent

**Purpose:** Generate implementation plans without making changes.

**Capabilities:**
- Full read access to the codebase
- Produces structured plans with file lists and step-by-step instructions
- Cannot modify any files

**When to use:**
- Before starting a large refactor
- Planning a new feature across multiple files
- Estimating scope of a change

**Invocation:**
```
Use the Plan subagent to plan the migration from REST to GraphQL for the user service
```

### General-Purpose Subagent

**Purpose:** A delegated Claude Code instance with full capabilities.

**Capabilities:**
- All tools available (same as main session)
- Runs in an isolated context
- Results summarized back to parent

**When to use:**
- Parallel task execution
- Tasks that would flood the main context
- Work that benefits from a clean context slate

### Custom Agents Directory

Custom agents live in `.claude/agents/`:

```
.claude/
└── agents/
    ├── security-reviewer.md
    ├── test-writer.md
    ├── doc-generator.md
    └── migration-helper.md
```

**Invocation** -- there is no `/agents/<name>` command. Claude delegates on its own
when a request matches an agent's `description`, or you ask for one explicitly:

```
Use the security-reviewer subagent to review the authentication module for vulnerabilities
@"test-writer (agent)" write unit tests for src/services/payment.ts
claude --agent doc-generator     # run the whole session as that agent
```

The `@` form comes from typing `@` and picking the agent from the typeahead.
`/agents` no longer opens a wizard; create agents by editing `.claude/agents/`
directly or by asking Claude to write the file.

---

## Custom Agent Creation

### Step 1: Define the Agent's Purpose

Every agent needs a narrow, well-defined scope. Good agents do one thing well.

**Good scopes:**
- "Reviews code changes for security vulnerabilities"
- "Writes comprehensive test suites for TypeScript modules"
- "Generates OpenAPI documentation from route handlers"
- "Analyzes database queries for N+1 problems"

**Bad scopes:**
- "Helps with coding" (too broad)
- "Does everything" (defeats the purpose of specialization)
- "Reviews and fixes code" (conflates review and modification)

### Step 2: Create the Agent File

Save the agent as `.claude/agents/security-reviewer.md` (project scope) or
`~/.claude/agents/security-reviewer.md` (all your projects). The file is YAML
frontmatter followed by a Markdown body, and **the body is the system prompt**.
There is no `.yaml` agent file and no `custom-instructions` or `allowed-tools`
key for agents: Claude Code silently ignores unknown keys, so an agent written
that way gets every tool and an empty prompt.

```markdown
---
name: security-reviewer
description: Reviews code changes for security vulnerabilities and compliance issues. Use proactively after changes to auth, input handling, or dependencies.
tools: Read, Glob, Grep, Bash
model: sonnet
---

You are a security-focused code reviewer. Use Bash only for read-only git
commands (`git diff`, `git log`, `git show`). For every change you review:

1. Check for hardcoded secrets, credentials, API keys, or tokens
2. Identify injection vulnerabilities (SQL, XSS, command injection)
3. Verify authentication and authorization patterns
4. Flag insecure dependencies or deprecated crypto functions
5. Check for information disclosure in error messages

## Output Format

### Security Review Summary
- **Risk Level:** HIGH / MEDIUM / LOW / CLEAN
- **Issues Found:** N

### Issues
For each issue:
- File and line number
- Severity (Critical / High / Medium / Low / Info)
- Description
- Recommended fix

### Recommendations
Prioritized list of actions.
```

### Step 3: Test the Agent

```
Use the security-reviewer subagent to review the changes in the last commit
```

Verify that:
- The agent activates correctly
- Tool restrictions are enforced
- Output follows the specified format
- It stays within its defined scope

---

## Agent File Anatomy

### Required Fields

```yaml
name: agent-name           # Kebab-case identifier
description: What it does  # Brief description for discovery
```

### Optional Fields

```markdown
model: sonnet          # sonnet | opus | haiku | inherit (default: inherit)
tools: Read, Glob      # Tool allowlist, comma-separated (omit to inherit all tools)
disallowedTools: Write # Tools to remove from the inherited set
maxTurns: 25           # Cap on agentic turns
permissionMode: plan   # default | acceptEdits | auto | dontAsk | bypassPermissions | plan
isolation: worktree    # Run in a temporary git worktree
---

Your behavioral instructions here. The markdown body below the
frontmatter is the agent's system prompt.
```

### Field Details

**`name`** -- Lowercase, hyphenated identifier. Used when you ask for the agent
by name or @-mention it. Must be unique; the frontmatter `name`, not the file
path, identifies the agent.

**`description`** -- Claude reads this to decide when to delegate to the agent.
Say what it does and when to use it ("Use proactively after code changes").

**`model`** -- Override the model for this agent. Use an alias so the agent
tracks the current model in each tier (`inherit` uses the session model):
- `opus` -- Complex analysis, architecture review
- `sonnet` -- General coding, standard review
- `haiku` -- Simple formatting, quick checks

**`tools`** -- Allowlist of tool names the agent can use (comma-separated; a YAML
list also works). Omit it and the agent inherits every tool, MCP tools included:
- `Read` -- Read files
- `Glob` -- Find files
- `Grep` -- Search content
- `Edit` -- Modify files
- `Write` -- Create files
- `Bash` -- Run shell commands
- `WebFetch` -- Fetch URLs
- `WebSearch` -- Search the web

`tools` works at the tool level only. A specifier such as `Bash(git diff *)`
does not narrow Bash to matching commands. To limit which commands an agent
may run, grant `Bash` and add deny rules to `permissions.deny` in
`.claude/settings.json`, or gate commands with a `PreToolUse` hook.

**Body** -- The markdown below the frontmatter is the system prompt. This is where
you define the agent's workflow, output format, and constraints.

---

## Tool Access Patterns

### Read-Only Agent (Safe for Review)

```yaml
tools: Read, Glob, Grep
```

Best for: Code review, security audit, documentation analysis, architecture review.

### Read + Commands

```yaml
tools: Read, Glob, Grep, Bash
```

Best for: Review tasks that need git context or test results. Name the allowed
commands in the system prompt, and enforce the limit with permission rules
(see Restricted Bash below), because `tools` cannot scope Bash by command.

### Write-Capable Agent

```yaml
tools: Read, Write, Edit, Glob, Grep
```

Best for: Code generation, test writing, documentation generation.

### Full Access Agent

```yaml
# Omit tools entirely to inherit every tool (including MCP tools)
# Or list them explicitly:
tools: Read, Write, Edit, Glob, Grep, Bash, WebFetch, WebSearch
```

Best for: Complex multi-step tasks that need all capabilities.

### Restricted Bash

Command-level limits live in settings, not in the agent file. Give the agent
`Bash` in `tools`, then deny what it must never run in `.claude/settings.json`:

```json
{
  "permissions": {
    "deny": [
      "Bash(git push *)",
      "Bash(rm -rf *)",
      "Bash(docker compose down *)"
    ]
  }
}
```

Deny rules apply to the main session and every subagent. For a rule that only
one agent should obey, add a `PreToolUse` hook under that agent's `hooks`
frontmatter field.

---

## Delegation Patterns

### Pattern 1: Review Then Act

Use a read-only agent to review, then act on the findings yourself.

```
# Step 1: Agent reviews
Use the security-reviewer subagent to review all files changed in the last 5 commits

# Step 2: Human or main session acts on findings
Fix the SQL injection vulnerability identified in src/db/queries.ts line 45
```

### Pattern 2: Generate Then Review

Use a write agent to generate code, then a review agent to check it.

```
# Step 1: Generate
Use the test-writer subagent to write comprehensive tests for src/services/auth.ts

# Step 2: Review
Use the security-reviewer subagent to review the newly generated test file for security issues
```

### Pattern 3: Parallel Research

Use multiple agents to research different aspects simultaneously.

```
Run these in parallel: the architecture-analyst subagent analyzes the data flow
in the payment processing module, and the performance-profiler subagent
identifies potential bottlenecks in the checkout flow
```

### Pattern 4: Specialized Transformation

Use agents for specific, repeatable transformations.

```
# Convert JavaScript to TypeScript
@"ts-migrator (agent)" convert src/utils/helpers.js to TypeScript with strict mode

# Generate API docs from code
@"doc-generator (agent)" create an OpenAPI spec from src/routes/*.ts
```

### Pattern 5: Guardrail Agent

Use a pre-check agent before making changes.

```
# Check if change is safe
Use the impact-analyzer subagent: what files and tests would be affected by renaming the User model to Account?

# Then proceed with the change
Rename the User model to Account across the entire codebase
```

---

## Memory and State

### Agent Memory Scope

Subagents do NOT have access to:
- The main conversation history
- Previous agent invocation results
- Other agents' outputs

Subagents DO have access to:
- All project files (subject to `tools`)
- CLAUDE.md files (loaded automatically)
- The current git state

### Persisting Agent Output

Agent output appears in the main conversation. To preserve findings:

1. **Ask the agent to write to a file:**
   Add to the agent's system prompt (the file body): "Write your findings to a file."

2. **Capture in conversation:**
   The agent's output is visible in the main session's context.

3. **Use a handoff document:**
   ```
   Use the analyzer subagent to analyze the codebase and write a summary to .claude/analysis.md
   ```

### Cross-Agent Communication

Agents cannot communicate directly. Use files as the communication channel:

```
# Agent A writes findings
Use the security-reviewer subagent to review the code and write findings to /tmp/security-review.md

# Agent B reads findings
Use the fix-planner subagent to read /tmp/security-review.md and create a prioritized fix plan
```

---

## Isolation Modes

### Default Isolation

Agents run in the same project directory but with a fresh conversation context.
They share the filesystem but not conversation state.

### Worktree Isolation

For agents that modify files, set `isolation: worktree` in the frontmatter. The
agent then runs in a temporary git worktree, so its edits never touch your
checkout; the worktree is cleaned up if the agent makes no changes.

```markdown
---
name: refactor-worker
description: Performs large mechanical refactors in an isolated worktree
tools: Read, Edit, Write, Glob, Grep, Bash
isolation: worktree
---

Apply the requested refactor, run the tests, and report the branch and diff summary.
```

### Permission Isolation

Use `tools` to create hard boundaries:

```yaml
# Agent cannot modify anything
tools: Read, Glob, Grep

# Agent can edit, but its system prompt says "Only edit files in __tests__/"
tools: Read, Glob, Grep, Edit, Write
```

Note: `tools` enforces tool-level restrictions. Path-level restrictions written
in the system prompt are advisory; to enforce them, add `Edit`/`Write` deny rules
in settings or a `PreToolUse` hook.

---

## Hooks Integration

Hooks can enhance agent workflows by running scripts before or after tool use.

### Pre-Agent Validation Hook

Validate that an agent is appropriate for the current context:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Agent",
        "command": "/path/to/validate-agent-context.sh"
      }
    ]
  }
}
```

### Post-Agent Logging Hook

Log all agent invocations for audit:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Agent",
        "command": "echo \"$(date) Agent invoked: $CLAUDE_TOOL_INPUT\" >> .claude/agent-log.txt"
      }
    ]
  }
}
```

### Auto-Format After Agent Writes

Ensure agent-generated code matches project style:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "command": "prettier --write \"$CLAUDE_FILE_PATH\" 2>/dev/null || true"
      }
    ]
  }
}
```

---

## Production Recipes

### Recipe 1: Security Review Agent

```markdown
---
name: security-reviewer
description: Reviews code for security vulnerabilities, secrets, and compliance issues
model: sonnet
tools: Read, Glob, Grep, Bash
---

You are a senior security engineer performing code review.
Use Bash only for read-only git commands (`git diff`, `git log`, `git show`).

Review Checklist:
1. Hardcoded secrets (API keys, passwords, tokens, connection strings)
2. Injection vulnerabilities (SQL, XSS, command, LDAP, template)
3. Authentication flaws (broken auth, missing checks, weak tokens)
4. Authorization gaps (IDOR, privilege escalation, missing RBAC)
5. Cryptographic issues (weak algorithms, missing encryption, bad RNG)
6. Information disclosure (verbose errors, stack traces, debug endpoints)
7. Dependency vulnerabilities (known CVEs, outdated packages)

Output a structured markdown report with severity levels.
Always end with a risk score: CRITICAL / HIGH / MEDIUM / LOW / CLEAN.
```

### Recipe 2: Test Writer Agent

```markdown
---
name: test-writer
description: Generates comprehensive test suites with edge cases and mocking
model: sonnet
tools: Read, Write, Glob, Grep, Bash
---

You write comprehensive test suites. Use Bash only to run the test suite
(`npm test`, `npx jest`). For every module you test:

1. Read the source code thoroughly
2. Identify all public functions and methods
3. Write tests covering:
   - Happy path for each function
   - Edge cases (null, empty, boundary values)
   - Error cases (invalid input, network failures)
   - Integration points (mocked external dependencies)
4. Use the project's existing test framework and patterns
5. Run the tests to verify they pass

Naming: describe("ModuleName", () => { it("should verb when condition", ...) })
Target: 90%+ line coverage for the tested module.
```

### Recipe 3: Documentation Generator

```markdown
---
name: doc-generator
description: Generates API documentation, code comments, and README files
model: sonnet
tools: Read, Write, Glob, Grep
---

You generate clear, accurate documentation from source code.

Documentation Types:
- API docs: Extract routes, parameters, response shapes from code
- Code comments: Add JSDoc/docstrings to undocumented functions
- README: Generate project overview from codebase analysis

Rules:
- Never invent features that don't exist in the code
- Include realistic examples based on actual code paths
- Use the project's existing documentation style
- Mark any assumptions with [ASSUMPTION] tag
```

### Recipe 4: Database Migration Agent

```markdown
---
name: migration-helper
description: Generates database migration scripts and validates schema changes
model: sonnet
tools: Read, Write, Glob, Grep, Bash
---

You create safe database migration scripts.
Use Bash only for `npx prisma` and `npm run migrate` commands.

Safety Rules:
1. NEVER drop columns or tables without explicit user confirmation
2. Always create reversible migrations (up AND down)
3. Add NOT NULL constraints in two steps (add nullable, backfill, alter)
4. Create indexes CONCURRENTLY when possible
5. Estimate data migration time for large tables

Output: Migration file + summary of changes + rollback plan.
```

### Recipe 5: Performance Profiler Agent

```markdown
---
name: performance-profiler
description: Analyzes code for performance bottlenecks, N+1 queries, and memory leaks
model: sonnet
tools: Read, Glob, Grep, Bash
---

You are a performance engineering specialist.
Use Bash only for `git log`, to find recently changed hot paths.

Analysis Areas:
1. N+1 query patterns in ORM usage
2. Missing database indexes for common queries
3. Unbounded list operations (no pagination)
4. Memory leaks (event listeners, closures, caches without eviction)
5. Synchronous operations that should be async
6. Missing caching opportunities
7. Large payload responses without pagination

Severity Levels:
- P0: Will cause outage under load
- P1: Significant performance degradation
- P2: Noticeable slowdown
- P3: Optimization opportunity

Output a prioritized list with file:line references and fix suggestions.
```

---

## When to Use Subagents vs Skills

| Criterion | Use a Skill | Use a Subagent |
|-----------|-------------|----------------|
| Needs isolated context | No | Yes |
| Needs restricted tools | No | Yes |
| Provides reusable knowledge | Yes | No |
| Has executable tools (scripts) | Yes | Optional |
| Defines a persona | No | Yes |
| Runs a focused, scoped task | Either | Yes |
| Bundles templates/references | Yes | No |
| Needs a different model | Either | Yes |

**Rules of thumb:**

1. **Knowledge + tools + templates** -> Make it a skill.
2. **Focused task + persona + restrictions** -> Make it an agent.
3. **Reads many files, want clean context** -> Subagent (fresh context window).
4. **Quick question using conversation history** -> Skill or inline prompt.
5. **Repeatable specialized review** -> Agent (security-reviewer, test-runner).
6. **Domain expertise for multiple workflows** -> Skill (covers broader scope).

---

**Last Updated:** February 2026
