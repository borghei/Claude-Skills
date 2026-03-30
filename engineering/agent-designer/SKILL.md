---
name: agent-designer
description: >
  Designs multi-agent system architectures with orchestration patterns, tool
  schemas, and performance evaluation. Use when building AI agent systems,
  designing agent workflows, creating tool schemas, or evaluating agent
  performance.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: engineering
  domain: ai-agents
  tier: POWERFUL
  updated: 2026-03-31
---
# Agent Designer - Multi-Agent System Architecture

**Tier:** POWERFUL
**Category:** Engineering
**Tags:** AI agents, architecture, system design, orchestration, multi-agent systems

## Overview

Agent Designer is a comprehensive toolkit for designing, architecting, and evaluating multi-agent systems. It provides structured approaches to agent architecture patterns, tool design principles, communication strategies, and performance evaluation frameworks for building robust, scalable AI agent systems.

## Core Capabilities

### 1. Agent Architecture Patterns

#### Single Agent Pattern
- **Use Case:** Simple, focused tasks with clear boundaries
- **Pros:** Minimal complexity, easy debugging, predictable behavior
- **Cons:** Limited scalability, single point of failure
- **Implementation:** Direct user-agent interaction with comprehensive tool access

#### Supervisor Pattern
- **Use Case:** Hierarchical task decomposition with centralized control
- **Architecture:** One supervisor agent coordinating multiple specialist agents
- **Pros:** Clear command structure, centralized decision making
- **Cons:** Supervisor bottleneck, complex coordination logic
- **Implementation:** Supervisor receives tasks, delegates to specialists, aggregates results

#### Swarm Pattern
- **Use Case:** Distributed problem solving with peer-to-peer collaboration
- **Architecture:** Multiple autonomous agents with shared objectives
- **Pros:** High parallelism, fault tolerance, emergent intelligence
- **Cons:** Complex coordination, potential conflicts, harder to predict
- **Implementation:** Agent discovery, consensus mechanisms, distributed task allocation

#### Hierarchical Pattern
- **Use Case:** Complex systems with multiple organizational layers
- **Architecture:** Tree structure with managers and workers at different levels
- **Pros:** Natural organizational mapping, clear responsibilities
- **Cons:** Communication overhead, potential bottlenecks at each level
- **Implementation:** Multi-level delegation with feedback loops

#### Pipeline Pattern
- **Use Case:** Sequential processing with specialized stages
- **Architecture:** Agents arranged in processing pipeline
- **Pros:** Clear data flow, specialized optimization per stage
- **Cons:** Sequential bottlenecks, rigid processing order
- **Implementation:** Message queues between stages, state handoffs

### 2. Agent Role Definition

#### Role Specification Framework
- **Identity:** Name, purpose statement, core competencies
- **Responsibilities:** Primary tasks, decision boundaries, success criteria
- **Capabilities:** Required tools, knowledge domains, processing limits
- **Interfaces:** Input/output formats, communication protocols
- **Constraints:** Security boundaries, resource limits, operational guidelines

#### Common Agent Archetypes

**Coordinator Agent**
- Orchestrates multi-agent workflows
- Makes high-level decisions and resource allocation
- Monitors system health and performance
- Handles escalations and conflict resolution

**Specialist Agent**
- Deep expertise in specific domain (code, data, research)
- Optimized tools and knowledge for specialized tasks
- High-quality output within narrow scope
- Clear handoff protocols for out-of-scope requests

**Interface Agent**
- Handles external interactions (users, APIs, systems)
- Protocol translation and format conversion
- Authentication and authorization management
- User experience optimization

**Monitor Agent**
- System health monitoring and alerting
- Performance metrics collection and analysis
- Anomaly detection and reporting
- Compliance and audit trail maintenance

### 3. Tool Design Principles

#### Schema Design
- **Input Validation:** Strong typing, required vs optional parameters
- **Output Consistency:** Standardized response formats, error handling
- **Documentation:** Clear descriptions, usage examples, edge cases
- **Versioning:** Backward compatibility, migration paths

#### Error Handling Patterns
- **Graceful Degradation:** Partial functionality when dependencies fail
- **Retry Logic:** Exponential backoff, circuit breakers, max attempts
- **Error Propagation:** Structured error responses, error classification
- **Recovery Strategies:** Fallback methods, alternative approaches

#### Idempotency Requirements
- **Safe Operations:** Read operations with no side effects
- **Idempotent Writes:** Same operation can be safely repeated
- **State Management:** Version tracking, conflict resolution
- **Atomicity:** All-or-nothing operation completion

### 4. Communication Patterns

#### Message Passing
- **Asynchronous Messaging:** Decoupled agents, message queues
- **Message Format:** Structured payloads with metadata
- **Delivery Guarantees:** At-least-once, exactly-once semantics
- **Routing:** Direct messaging, publish-subscribe, broadcast

#### Shared State
- **State Stores:** Centralized data repositories
- **Consistency Models:** Strong, eventual, weak consistency
- **Access Patterns:** Read-heavy, write-heavy, mixed workloads
- **Conflict Resolution:** Last-writer-wins, merge strategies

#### Event-Driven Architecture
- **Event Sourcing:** Immutable event logs, state reconstruction
- **Event Types:** Domain events, system events, integration events
- **Event Processing:** Real-time, batch, stream processing
- **Event Schema:** Versioned event formats, backward compatibility

### 5. Guardrails and Safety

#### Input Validation
- **Schema Enforcement:** Required fields, type checking, format validation
- **Content Filtering:** Harmful content detection, PII scrubbing
- **Rate Limiting:** Request throttling, resource quotas
- **Authentication:** Identity verification, authorization checks

#### Output Filtering
- **Content Moderation:** Harmful content removal, quality checks
- **Consistency Validation:** Logic checks, constraint verification
- **Formatting:** Standardized output formats, clean presentation
- **Audit Logging:** Decision trails, compliance records

#### Human-in-the-Loop
- **Approval Workflows:** Critical decision checkpoints
- **Escalation Triggers:** Confidence thresholds, risk assessment
- **Override Mechanisms:** Human judgment precedence
- **Feedback Loops:** Human corrections improve system behavior

### 6. Evaluation Frameworks

#### Task Completion Metrics
- **Success Rate:** Percentage of tasks completed successfully
- **Partial Completion:** Progress measurement for complex tasks
- **Task Classification:** Success criteria by task type
- **Failure Analysis:** Root cause identification and categorization

#### Quality Assessment
- **Output Quality:** Accuracy, relevance, completeness measures
- **Consistency:** Response variability across similar inputs
- **Coherence:** Logical flow and internal consistency
- **User Satisfaction:** Feedback scores, usage patterns

#### Cost Analysis
- **Token Usage:** Input/output token consumption per task
- **API Costs:** External service usage and charges
- **Compute Resources:** CPU, memory, storage utilization
- **Time-to-Value:** Cost per successful task completion

#### Latency Distribution
- **Response Time:** End-to-end task completion time
- **Processing Stages:** Bottleneck identification per stage
- **Queue Times:** Wait times in processing pipelines
- **Resource Contention:** Impact of concurrent operations

### 7. Orchestration Strategies

#### Centralized Orchestration
- **Workflow Engine:** Central coordinator manages all agents
- **State Management:** Centralized workflow state tracking
- **Decision Logic:** Complex routing and branching rules
- **Monitoring:** Comprehensive visibility into all operations

#### Decentralized Orchestration
- **Peer-to-Peer:** Agents coordinate directly with each other
- **Service Discovery:** Dynamic agent registration and lookup
- **Consensus Protocols:** Distributed decision making
- **Fault Tolerance:** No single point of failure

#### Hybrid Approaches
- **Domain Boundaries:** Centralized within domains, federated across
- **Hierarchical Coordination:** Multiple orchestration levels
- **Context-Dependent:** Strategy selection based on task type
- **Load Balancing:** Distribute coordination responsibility

### 8. Memory Patterns

#### Short-Term Memory
- **Context Windows:** Working memory for current tasks
- **Session State:** Temporary data for ongoing interactions
- **Cache Management:** Performance optimization strategies
- **Memory Pressure:** Handling capacity constraints

#### Long-Term Memory
- **Persistent Storage:** Durable data across sessions
- **Knowledge Base:** Accumulated domain knowledge
- **Experience Replay:** Learning from past interactions
- **Memory Consolidation:** Transferring from short to long-term

#### Shared Memory
- **Collaborative Knowledge:** Shared learning across agents
- **Synchronization:** Consistency maintenance strategies
- **Access Control:** Permission-based memory access
- **Memory Partitioning:** Isolation between agent groups

### 9. Scaling Considerations

#### Horizontal Scaling
- **Agent Replication:** Multiple instances of same agent type
- **Load Distribution:** Request routing across agent instances
- **Resource Pooling:** Shared compute and storage resources
- **Geographic Distribution:** Multi-region deployments

#### Vertical Scaling
- **Capability Enhancement:** More powerful individual agents
- **Tool Expansion:** Broader tool access per agent
- **Context Expansion:** Larger working memory capacity
- **Processing Power:** Higher throughput per agent

#### Performance Optimization
- **Caching Strategies:** Response caching, tool result caching
- **Parallel Processing:** Concurrent task execution
- **Resource Optimization:** Efficient resource utilization
- **Bottleneck Elimination:** Systematic performance tuning

### 10. Failure Handling

#### Retry Mechanisms
- **Exponential Backoff:** Increasing delays between retries
- **Jitter:** Random delay variation to prevent thundering herd
- **Maximum Attempts:** Bounded retry behavior
- **Retry Conditions:** Transient vs permanent failure classification

#### Fallback Strategies
- **Graceful Degradation:** Reduced functionality when systems fail
- **Alternative Approaches:** Different methods for same goals
- **Default Responses:** Safe fallback behaviors
- **User Communication:** Clear failure messaging

#### Circuit Breakers
- **Failure Detection:** Monitoring failure rates and response times
- **State Management:** Open, closed, half-open circuit states
- **Recovery Testing:** Gradual return to normal operation
- **Cascading Failure Prevention:** Protecting upstream systems

## Implementation Guidelines

### Architecture Decision Process
1. **Requirements Analysis:** Understand system goals, constraints, scale
2. **Pattern Selection:** Choose appropriate architecture pattern
3. **Agent Design:** Define roles, responsibilities, interfaces
4. **Tool Architecture:** Design tool schemas and error handling
5. **Communication Design:** Select message patterns and protocols
6. **Safety Implementation:** Build guardrails and validation
7. **Evaluation Planning:** Define success metrics and monitoring
8. **Deployment Strategy:** Plan scaling and failure handling

### Quality Assurance
- **Testing Strategy:** Unit, integration, and system testing approaches
- **Monitoring:** Real-time system health and performance tracking
- **Documentation:** Architecture documentation and runbooks
- **Security Review:** Threat modeling and security assessments

### Continuous Improvement
- **Performance Monitoring:** Ongoing system performance analysis
- **User Feedback:** Incorporating user experience improvements
- **A/B Testing:** Controlled experiments for system improvements
- **Knowledge Base Updates:** Continuous learning and adaptation

This skill provides the foundation for designing robust, scalable multi-agent systems that can handle complex tasks while maintaining safety, reliability, and performance at scale.

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

## Scope & Limitations

**Covers:**
- Multi-agent architecture pattern selection (single agent, supervisor, swarm, hierarchical, pipeline)
- Agent role definition with responsibilities, capabilities, tools, and communication interfaces
- Tool schema generation in OpenAI and Anthropic formats with validation rules and error handling
- Performance evaluation from execution logs including bottleneck analysis and optimization recommendations

**Does NOT cover:**
- Runtime agent orchestration or execution engines (see `engineering/agent-workflow-designer` for workflow execution)
- LLM prompt engineering or system prompt design (see `engineering/prompt-engineer-toolkit`)
- MCP server implementation or protocol details (see `engineering/mcp-server-builder`)
- Self-improving agent feedback loops or autonomous learning (see `engineering/self-improving-agent`)

## Integration Points

| Skill | Integration | Data Flow |
|-------|-------------|-----------|
| `engineering/agent-workflow-designer` | Workflow definitions consume architecture designs from Agent Designer | Agent roles and communication topology feed into workflow step definitions |
| `engineering/prompt-engineer-toolkit` | System prompts are crafted per agent role defined by Agent Designer | Agent role specifications and responsibilities inform prompt structure and constraints |
| `engineering/mcp-server-builder` | Tool schemas generated here map to MCP server tool implementations | `tool_schema_generator.py` output provides the schema contract that MCP servers implement |
| `engineering/self-improving-agent` | Evaluation reports feed into self-improvement loops | `agent_evaluator.py` bottleneck analysis drives autonomous optimization decisions |
| `engineering/observability-designer` | Monitoring architecture aligns with agent topology and communication links | Agent definitions and communication patterns define what to instrument and alert on |
| `engineering/agent-protocol` | Protocol standards govern inter-agent message formats designed here | Communication topology patterns must comply with agent protocol specifications |

## Tool Reference

### agent_planner.py

**Purpose:** Designs multi-agent system architectures from system requirements. Selects an architecture pattern, defines agent roles, generates communication topology, produces a Mermaid diagram, and creates an implementation roadmap.

**Usage:**
```bash
python agent_planner.py <input_file> [-o OUTPUT] [--format {json,yaml,both}]
```

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `input_file` | positional | Yes | -- | JSON file containing system requirements (goal, description, tasks, constraints, team_size, performance_requirements, safety_requirements, integration_requirements, scale_requirements) |
| `-o`, `--output` | string | No | `agent_architecture` | Output file prefix for generated files |
| `--format` | choice | No | `both` | Output format: `json`, `yaml`, or `both` |

**Example:**
```bash
python agent_planner.py requirements.json -o my_system --format both
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
python agent_evaluator.py <input_file> [-o OUTPUT] [--format {json,both}] [--detailed]
```

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `input_file` | positional | Yes | -- | JSON file containing execution logs (array of log entries with task_id, agent_id, task_type, status, duration_ms, tokens_used, cost_usd, tools_used, error_details, etc.) |
| `-o`, `--output` | string | No | `evaluation_report` | Output file prefix for generated report files |
| `--format` | choice | No | `both` | Output format: `json` or `both` |
| `--detailed` | flag | No | off | Include detailed per-agent and per-task-type breakdowns in the report |

**Example:**
```bash
python agent_evaluator.py execution_logs.json -o perf_report --format both --detailed
```

**Output Formats:**
- `{prefix}.json` -- Complete evaluation report with system metrics, agent metrics, task type metrics, tool usage analysis, error analysis, bottleneck analysis, and optimization recommendations
- Console summary with key performance indicators (when format is `both`, additional breakdowns are written to separate files)

---

### tool_schema_generator.py

**Purpose:** Generates structured tool schemas compatible with OpenAI function calling and Anthropic tool use formats. Includes input validation rules, error response formats, example calls, and rate limit suggestions.

**Usage:**
```bash
python tool_schema_generator.py <input_file> [-o OUTPUT] [--format {json,both}] [--validate]
```

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `input_file` | positional | Yes | -- | JSON file containing tool descriptions (array of objects with name, purpose, category, inputs, outputs, error_conditions, side_effects, idempotent, rate_limits, dependencies, examples, security_requirements) |
| `-o`, `--output` | string | No | `tool_schemas` | Output file prefix for generated schema files |
| `--format` | choice | No | `both` | Output format: `json` or `both` |
| `--validate` | flag | No | off | Validate generated schemas against JSON Schema standards and report any issues |

**Example:**
```bash
python tool_schema_generator.py tools.json -o my_tools --format both --validate
```

**Output Formats:**
- `{prefix}.json` -- Complete tool schemas including OpenAI format, Anthropic format, validation rules, error responses, rate limits, and example usage for each tool
- Console summary with schema count, validation results (when `--validate` is used), and any detected issues