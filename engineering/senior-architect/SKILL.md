---
name: senior-architect
description: Expert software architecture covering system design, distributed systems, microservices, scalability patterns, and technical decision-making.
version: 1.0.0
author: Claude Skills
category: engineering
tags: [architecture, system-design, distributed-systems, scalability, patterns]
---

# Senior Software Architect

Expert-level software architecture for scalable systems.

## Core Competencies

- System design
- Distributed systems
- Microservices architecture
- Scalability patterns
- Technical decision-making
- Architecture documentation
- Technology evaluation
- Performance optimization

## Architecture Patterns

### Monolith vs Microservices

| Aspect | Monolith | Microservices |
|--------|----------|---------------|
| Complexity | Lower initially | Higher |
| Deployment | Single unit | Independent |
| Scaling | Vertical/Horizontal | Service-level |
| Team Size | Small teams | Multiple teams |
| Data | Single DB | Distributed |
| Best For | Startups, MVPs | Scale, large orgs |

### Service Architecture Patterns

**Layered Architecture:**
```
┌─────────────────────────────────────┐
│         Presentation Layer          │
├─────────────────────────────────────┤
│         Application Layer           │
├─────────────────────────────────────┤
│           Domain Layer              │
├─────────────────────────────────────┤
│        Infrastructure Layer         │
└─────────────────────────────────────┘
```

**Hexagonal Architecture:**
```
                 ┌─────────┐
         ┌──────│   API   │──────┐
         │      └─────────┘      │
    ┌────▼────┐           ┌──────▼──────┐
    │   CLI   │           │  Database   │
    └────┬────┘           └──────┬──────┘
         │      ┌─────────┐      │
         └──────│  Core   │──────┘
                │ Domain  │
         ┌──────│         │──────┐
         │      └─────────┘      │
    ┌────▼────┐           ┌──────▼──────┐
    │  Queue  │           │  External   │
    └─────────┘           │   Service   │
                          └─────────────┘
```

**Event-Driven Architecture:**
```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Service A  │────▶│   Event     │────▶│  Service B  │
└─────────────┘     │    Bus      │     └─────────────┘
                    │             │
┌─────────────┐     │             │     ┌─────────────┐
│  Service C  │◀────│             │────▶│  Service D  │
└─────────────┘     └─────────────┘     └─────────────┘
```

## Distributed Systems

### CAP Theorem

- **Consistency**: All nodes see same data simultaneously
- **Availability**: Every request receives response
- **Partition Tolerance**: System continues despite network failures

**Choose Two:**
- CA: Traditional RDBMS (single node)
- CP: Distributed databases (MongoDB, HBase)
- AP: DNS, Cassandra, DynamoDB

### Consistency Patterns

**Strong Consistency:**
- All reads return most recent write
- Use: Financial transactions, inventory
- Trade-off: Higher latency

**Eventual Consistency:**
- Reads may return stale data temporarily
- Use: Social media feeds, analytics
- Trade-off: Complexity in application

**Causal Consistency:**
- Preserves cause-effect relationships
- Use: Collaborative editing, messaging
- Trade-off: Moderate complexity

### Distributed Transactions

**Saga Pattern:**
```
┌─────────────────────────────────────────────────────────┐
│                    Choreography Saga                     │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Order        Inventory       Payment       Shipping     │
│  Service      Service         Service       Service      │
│    │             │               │             │         │
│    │──Create────▶│               │             │         │
│    │             │───Reserve────▶│             │         │
│    │             │               │───Charge───▶│         │
│    │             │               │             │──Ship   │
│    │◀───────────────────────────────────Complete│        │
│                                                          │
│  Compensation (on failure):                              │
│    │◀─Release───│◀──Refund─────│◀──Cancel────│          │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

**Two-Phase Commit:**
```
Phase 1 (Prepare):
  Coordinator → All Participants: "Prepare"
  All Participants → Coordinator: "Ready" or "Abort"

Phase 2 (Commit/Abort):
  If all Ready:
    Coordinator → All Participants: "Commit"
  Else:
    Coordinator → All Participants: "Abort"
```

## Scalability Patterns

### Horizontal Scaling

**Load Balancing Strategies:**
- Round Robin: Simple rotation
- Least Connections: Route to least busy
- IP Hash: Sticky sessions
- Weighted: Based on server capacity

**Stateless Design:**
```
┌─────────────┐     ┌─────────────┐
│   Client    │────▶│   Load      │
└─────────────┘     │  Balancer   │
                    └──────┬──────┘
           ┌───────────────┼───────────────┐
           ▼               ▼               ▼
    ┌──────────┐    ┌──────────┐    ┌──────────┐
    │ Server 1 │    │ Server 2 │    │ Server 3 │
    └────┬─────┘    └────┬─────┘    └────┬─────┘
         │               │               │
         └───────────────┼───────────────┘
                         ▼
              ┌─────────────────────┐
              │   Shared State      │
              │   (Redis/DB)        │
              └─────────────────────┘
```

### Caching Strategies

**Cache Levels:**
```
┌─────────────────────────────────────────────────────┐
│  L1: Application Cache (in-memory)      ~1ms       │
├─────────────────────────────────────────────────────┤
│  L2: Distributed Cache (Redis)          ~5ms       │
├─────────────────────────────────────────────────────┤
│  L3: CDN Cache                          ~50ms      │
├─────────────────────────────────────────────────────┤
│  L4: Database                           ~100ms     │
└─────────────────────────────────────────────────────┘
```

**Cache Patterns:**

```
Cache-Aside:
  1. Check cache
  2. If miss, read from DB
  3. Store in cache
  4. Return data

Write-Through:
  1. Write to cache
  2. Cache writes to DB
  3. Return success

Write-Behind:
  1. Write to cache
  2. Return success
  3. Cache async writes to DB
```

### Database Scaling

**Read Replicas:**
```
┌────────────┐
│   Master   │◀────── Writes
└─────┬──────┘
      │ Replication
      ├──────────────┬──────────────┐
      ▼              ▼              ▼
┌──────────┐  ┌──────────┐  ┌──────────┐
│ Replica 1│  │ Replica 2│  │ Replica 3│
└────┬─────┘  └────┬─────┘  └────┬─────┘
     │             │             │
     └─────────────┴─────────────┘
                   │
              Reads distributed
```

**Sharding Strategies:**
- Hash-based: Consistent hashing
- Range-based: Date ranges, alphabetical
- Geographic: By region
- Directory-based: Lookup service

## API Design

### REST Maturity Model

**Level 0**: Single URI, POST everything
**Level 1**: Multiple URIs, resources
**Level 2**: HTTP methods (GET, POST, PUT, DELETE)
**Level 3**: HATEOAS (Hypermedia controls)

### API Versioning

```
# URL Path
GET /api/v1/users

# Query Parameter
GET /api/users?version=1

# Header
GET /api/users
Accept: application/vnd.api+json;version=1

# Content Negotiation
GET /api/users
Accept: application/vnd.company.api.v1+json
```

### Rate Limiting

**Token Bucket Algorithm:**
```
Bucket Capacity: 100 tokens
Refill Rate: 10 tokens/second

Request arrives:
  If tokens > 0:
    tokens -= 1
    Process request
  Else:
    Reject (429 Too Many Requests)
```

## Reliability Patterns

### Circuit Breaker

```
States: CLOSED → OPEN → HALF-OPEN → CLOSED

CLOSED:
  - Normal operation
  - Track failures
  - If failure_count > threshold: → OPEN

OPEN:
  - Reject all requests immediately
  - After timeout: → HALF-OPEN

HALF-OPEN:
  - Allow limited requests
  - If success: → CLOSED
  - If failure: → OPEN
```

### Bulkhead

```
┌─────────────────────────────────────────────┐
│               Application                    │
├─────────────┬─────────────┬─────────────────┤
│  Thread     │  Thread     │  Thread         │
│  Pool A     │  Pool B     │  Pool C         │
│  (Orders)   │  (Users)    │  (Analytics)    │
│             │             │                 │
│  [===]      │  [===]      │  [===]          │
│  10 threads │  10 threads │  5 threads      │
└─────────────┴─────────────┴─────────────────┘

If Orders service fails, only Pool A exhausted.
Pools B and C continue operating.
```

### Retry with Backoff

```python
def exponential_backoff(attempt: int, base: float = 1.0, max_delay: float = 60.0):
    delay = min(base * (2 ** attempt), max_delay)
    jitter = random.uniform(0, delay * 0.1)
    return delay + jitter

# Retry pattern
for attempt in range(max_retries):
    try:
        result = make_request()
        break
    except TransientError:
        if attempt == max_retries - 1:
            raise
        time.sleep(exponential_backoff(attempt))
```

## Architecture Documentation

### Architecture Decision Record (ADR)

```markdown
# ADR-001: Use PostgreSQL for primary database

## Status
Accepted

## Context
We need to choose a primary database for our e-commerce platform.
Requirements:
- ACID transactions for orders
- Complex queries for reporting
- Scalability to 10M users

## Decision
We will use PostgreSQL as our primary database.

## Consequences
Positive:
- Strong consistency guarantees
- Rich SQL features
- Excellent JSON support
- Large ecosystem

Negative:
- Manual sharding required at scale
- More complex HA setup than managed NoSQL

## Alternatives Considered
- MongoDB: Better horizontal scaling, but weaker transactions
- CockroachDB: Better scaling, but higher operational complexity
- MySQL: Similar features, but less advanced JSON support
```

### C4 Model

```
Level 1 - System Context:
  [User] → [System] → [External Systems]

Level 2 - Container:
  [Web App] → [API] → [Database]
                ↓
           [Message Queue] → [Worker]

Level 3 - Component:
  API Container:
    [Controllers] → [Services] → [Repositories]

Level 4 - Code:
  Class diagrams, sequence diagrams
```

## Reference Materials

- `references/design_patterns.md` - Architecture patterns catalog
- `references/distributed_systems.md` - Distributed systems guide
- `references/scalability.md` - Scaling strategies
- `references/documentation.md` - Architecture documentation

## Scripts

```bash
# Architecture diagram generator
python scripts/arch_diagram.py --config services.yaml --output diagram.png

# Dependency analyzer
python scripts/dep_analyzer.py --path ./services --output deps.json

# Capacity planner
python scripts/capacity_plan.py --current 10000 --growth 0.5 --period 12

# Service mesh analyzer
python scripts/mesh_analyzer.py --namespace production
```
