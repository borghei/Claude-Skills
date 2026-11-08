# Troubleshooting, Success Criteria & Tool Reference

Read this when a tool misbehaves, when validating a design against the quality bar, or when you need the full CLI parameter reference for `agent_planner.py`, `agent_evaluator.py`, or `tool_schema_generator.py`.

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| Pattern selection returns single_agent for complex systems | Low complexity score due to vague task descriptions | Provide detailed task descriptions including keywords like "parallel", "sequential", or "distributed" to improve heuristic matching |
| Supervisor bottleneck under high agent count | All specialist agents report to one supervisor, overwhelming its coordination capacity | Switch to hierarchical pattern for teams exceeding 8 agents, or introduce sub-supervisors within the supervisor pattern |
| Swarm agents produce conflicting outputs | No consensus mechanism configured; agents act on stale shared state | Set `consensus_threshold` above 0.6 and implement event-driven communication with conflict resolution strategies |
| Pipeline stage timeouts cascade downstream | A slow stage blocks the entire sequential chain with no backpressure handling | Add per-stage circuit breakers, increase `stage_timeout`, and implement buffered message queues between stages |
| Generated Mermaid diagrams render incorrectly | Agent names contain special characters or spaces that break Mermaid syntax | Use snake_case agent names without special characters; the planner sanitizes names automatically |
| Tool schema validation failures in production | Input schemas generated without sufficient constraints for edge-case data | Run `tool_schema_generator.py` with `--validate` to catch schema gaps before deployment |
| Evaluation report shows 0 throughput | Execution logs missing or malformed `start_time`/`end_time` fields | Ensure logs use ISO 8601 datetime format (e.g., `2026-01-15T10:30:00Z`) for all timestamp fields |

## Success Criteria

- **Architecture pattern accuracy:** Selected pattern matches system requirements in 90%+ of evaluations (validated by team review)
- **Agent role completeness:** Every task in the requirements maps to at least one agent's responsibilities with no orphaned tasks
- **Communication topology coverage:** All agent pairs that need to exchange data have explicit communication links defined
- **Tool schema compliance:** 100% of generated schemas pass validation against both OpenAI function calling and Anthropic tool use formats
- **Evaluation report actionability:** Performance reports identify at least 3 concrete optimization recommendations with estimated impact
- **Design-to-implementation time:** Architecture designs reduce multi-agent system implementation time by 40%+ compared to ad-hoc design
- **Failure handling coverage:** Every agent in the design has defined retry policies, fallback strategies, and escalation paths

## Tool Reference

### agent_planner.py

**Purpose:** Designs multi-agent system architectures from system requirements. Selects an architecture pattern, defines agent roles, generates communication topology, produces a Mermaid diagram, and creates an implementation roadmap.

**Usage:**
```bash
python scripts/agent_planner.py <input_file> [-o OUTPUT] [--format {json,yaml,both}]
```

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `input_file` | positional | Yes | -- | JSON file containing system requirements (goal, description, tasks, constraints, team_size, performance_requirements, safety_requirements, integration_requirements, scale_requirements) |
| `-o`, `--output` | string | No | none: summary to stdout | Output file prefix for generated files; nothing is written without it |
| `--format` | choice | No | `both` | Output format: `json`, `yaml`, or `both` |

**Example:**
```bash
python scripts/agent_planner.py requirements.json -o my_system --format both
```

**Output Formats:**
- `{prefix}.json` -- Full architecture design including agents, communication topology, guardrails, scaling strategy, and metadata
- `{prefix}_diagram.mmd` -- Mermaid diagram of the agent architecture (generated when format is `both`)
- `{prefix}_roadmap.json` -- Implementation roadmap with phases, tasks, deliverables, risks, and success criteria (generated when format is `both`)
- Console summary showing pattern, agent count, communication links, and estimated duration

---

### agent_evaluator.py

**Purpose:** Evaluates multi-agent system performance from execution logs. Calculates success rates, cost analysis, latency distribution, error patterns, bottleneck identification, and optimization recommendations.

**Usage:**
```bash
python scripts/agent_evaluator.py <input_file> [-o OUTPUT] [--format {json,both}] [--detailed]
```

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `input_file` | positional | Yes | -- | JSON file containing execution logs (array of log entries with task_id, agent_id, task_type, status, duration_ms, tokens_used, cost_usd, tools_used, error_details, etc.) |
| `-o`, `--output` | string | No | none: summary to stdout | Output file prefix for generated report files; nothing is written without it |
| `--format` | choice | No | `both` | Output format: `json` or `both` |
| `--detailed` | flag | No | off | Include detailed per-agent and per-task-type breakdowns in the report |

**Example:**
```bash
python scripts/agent_evaluator.py execution_logs.json -o perf_report --format both --detailed
```

**Output Formats:**
- `{prefix}.json` -- Complete evaluation report with system metrics, agent metrics, task type metrics, tool usage analysis, error analysis, bottleneck analysis, and optimization recommendations
- Console summary with key performance indicators (when format is `both`, additional breakdowns are written to separate files)

---

### tool_schema_generator.py

**Purpose:** Generates structured tool schemas compatible with OpenAI function calling and Anthropic tool use formats. Includes input validation rules, error response formats, example calls, and rate limit suggestions.

**Usage:**
```bash
python scripts/tool_schema_generator.py <input_file> [-o OUTPUT] [--format {json,both}] [--validate]
```

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `input_file` | positional | Yes | -- | JSON file containing tool descriptions (array of objects with name, purpose, category, inputs, outputs, error_conditions, side_effects, idempotent, rate_limits, dependencies, examples, security_requirements) |
| `-o`, `--output` | string | No | none: summary to stdout | Output file prefix for generated schema files; nothing is written without it |
| `--format` | choice | No | `both` | Output format: `json` or `both` |
| `--validate` | flag | No | off | Validate generated schemas against JSON Schema standards and report any issues |

**Example:**
```bash
python scripts/tool_schema_generator.py tools.json -o my_tools --format both --validate
```

**Output Formats:**
- `{prefix}.json` -- Complete tool schemas including OpenAI format, Anthropic format, validation rules, error responses, rate limits, and example usage for each tool
- Console summary with schema count, validation results (when `--validate` is used), and any detected issues
