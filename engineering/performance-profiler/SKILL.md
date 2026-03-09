---
name: performance-profiler
description: Systematic performance profiling for Node.js, Python, and Go applications. Covers CPU flamegraphs, memory leak detection, bundle analysis, database query optimization, N+1 detection, load testing with k6, and before/after measurement methodology. Use when diagnosing slow endpoints, memory growth, large bundles, or preparing for traffic spikes.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  category: engineering
  domain: performance-engineering
  tier: POWERFUL
  updated: 2026-03-09
  frameworks: clinic, py-spy, pprof, k6, webpack-bundle-analyzer
---

# Performance Profiler

**Tier:** POWERFUL
**Category:** Engineering / Performance
**Maintainer:** Claude Skills Team

## Overview

Systematic performance profiling for Node.js, Python, and Go applications. Identifies CPU bottlenecks with flamegraphs, detects memory leaks with heap snapshots, analyzes bundle sizes, optimizes database queries, detects N+1 patterns, and runs load tests with k6 and Artillery. Enforces a measure-first methodology: establish baseline, identify bottleneck, fix, and verify improvement.

## Keywords

performance profiling, flamegraph, memory leak, bundle analysis, N+1 queries, load testing, k6, latency, P99, CPU profiling, heap snapshot, database optimization

## Golden Rule: Measure First

```
WRONG: "I think the N+1 query is slow, let me fix it"
RIGHT: Profile → Confirm bottleneck → Fix → Measure again → Verify improvement

Every optimization must have:
1. Baseline metrics (before)
2. Profiler evidence (what's actually slow)
3. The fix
4. Post-fix metrics (after)
5. Delta calculation (improvement %)
```

## Core Capabilities

### 1. CPU Profiling
- Node.js: Clinic.js flamegraphs, V8 CPU profiles
- Python: py-spy flamegraphs, cProfile, scalene
- Go: pprof CPU profiles, trace visualization
- Browser: Chrome DevTools Performance panel

### 2. Memory Profiling
- Heap snapshots and comparison (before/after)
- Garbage collection pressure analysis
- Memory leak detection patterns
- Retained object graph analysis

### 3. Database Optimization
- EXPLAIN ANALYZE for query plan analysis
- N+1 query detection and batching
- Slow query log analysis
- Missing index identification
- Connection pool sizing

### 4. Bundle Analysis
- webpack-bundle-analyzer visualization
- Next.js bundle analyzer
- Tree-shaking effectiveness
- Dynamic import opportunities
- Heavy dependency identification

### 5. Load Testing
- k6 scripts with ramp-up patterns
- SLA threshold enforcement in CI
- Latency percentile tracking (P50, P95, P99)
- Concurrent user simulation

## When to Use

- App is slow and you do not know where the bottleneck is
- P99 latency exceeds SLA before a release
- Memory usage grows over time (suspected leak)
- Bundle size increased after adding dependencies
- Preparing for a traffic spike (load test before launch)
- Database queries taking >100ms
- After a dependency upgrade to verify no regressions

## Node.js CPU Profiling

### Method 1: Clinic.js Flamegraph

```bash
# Install
npm install -g clinic

# Generate flamegraph (starts server, applies load, generates HTML report)
clinic flame -- node server.js

# With specific load profile
clinic flame --autocannon [ /api/endpoint -c 10 -d 30 ] -- node server.js

# Analyze specific scenario
clinic flame --on-port 'autocannon -c 50 -d 60 http://localhost:$PORT/api/heavy-endpoint' -- node server.js
```

### Method 2: V8 CPU Profile

```bash
# Start Node with inspector
node --inspect server.js

# Or profile on demand
node --cpu-prof --cpu-prof-dir=./profiles server.js
# Load the .cpuprofile file in Chrome DevTools > Performance

# Programmatic profiling of a specific function
const { Session } = require('inspector');
const session = new Session();
session.connect();

session.post('Profiler.enable', () => {
  session.post('Profiler.start', () => {
    // Run the code you want to profile
    runHeavyOperation();

    session.post('Profiler.stop', (err, { profile }) => {
      require('fs').writeFileSync('profile.cpuprofile', JSON.stringify(profile));
    });
  });
});
```

## Memory Leak Detection

### Node.js Heap Snapshots

```javascript
// Take heap snapshots programmatically
const v8 = require('v8');
const fs = require('fs');

function takeHeapSnapshot(label) {
  const snapshotPath = `heap-${label}-${Date.now()}.heapsnapshot`;
  const stream = v8.writeHeapSnapshot(snapshotPath);
  console.log(`Heap snapshot written to: ${snapshotPath}`);
  return snapshotPath;
}

// Leak detection pattern: compare two snapshots
// 1. Take snapshot at startup
takeHeapSnapshot('baseline');

// 2. Run operations that you suspect leak
// ... process 1000 requests ...

// 3. Force GC and take another snapshot
if (global.gc) global.gc(); // requires --expose-gc flag
takeHeapSnapshot('after-load');

// Load both .heapsnapshot files in Chrome DevTools > Memory
// Use "Comparison" view to find objects that grew
```

### Python Memory Profiling

```bash
# Install tracemalloc-based profiler
pip install memray

# Profile a script
memray run my_script.py
memray flamegraph memray-output.bin -o flamegraph.html

# Profile a specific function
python -c "
import tracemalloc
tracemalloc.start()

# Run your code
from my_module import heavy_function
heavy_function()

snapshot = tracemalloc.take_snapshot()
top_stats = snapshot.statistics('lineno')
print('Top 10 memory allocations:')
for stat in top_stats[:10]:
    print(stat)
"
```

## Database Query Optimization

### EXPLAIN ANALYZE Workflow

```sql
-- Step 1: Get the actual execution plan (not just estimated)
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT t.*, p.name as project_name
FROM tasks t
JOIN projects p ON p.id = t.project_id
WHERE p.workspace_id = 'ws_abc123'
  AND t.status = 'in_progress'
  AND t.deleted_at IS NULL
ORDER BY t.updated_at DESC
LIMIT 20;

-- What to look for in the output:
-- Seq Scan on tasks  → MISSING INDEX (should be Index Scan)
-- Rows Removed by Filter: 99000  → INDEX NOT SELECTIVE ENOUGH
-- Sort Method: external merge  → NOT ENOUGH work_mem
-- Nested Loop with inner Seq Scan  → MISSING INDEX ON JOIN COLUMN
-- Actual rows=1000 vs estimated rows=1  → STALE STATISTICS (run ANALYZE)
```

### N+1 Query Detection

```typescript
// PROBLEM: N+1 query pattern
async function getProjectsWithTasks(workspaceId: string) {
  const projects = await db.query.projects.findMany({
    where: eq(projects.workspaceId, workspaceId),
  });

  // This executes N additional queries (one per project)
  for (const project of projects) {
    project.tasks = await db.query.tasks.findMany({
      where: eq(tasks.projectId, project.id),
    });
  }
  return projects;
}
// Total queries: 1 + N (where N = number of projects)

// FIX: Single query with JOIN or relation loading
async function getProjectsWithTasks(workspaceId: string) {
  return db.query.projects.findMany({
    where: eq(projects.workspaceId, workspaceId),
    with: {
      tasks: true,  // Drizzle generates a single JOIN or subquery
    },
  });
}
// Total queries: 1-2 (depending on ORM strategy)
```

### N+1 Detection Script

```bash
# Log query count per request (add to middleware)
# Node.js with Drizzle:
let queryCount = 0;
const originalQuery = db.execute;
db.execute = (...args) => { queryCount++; return originalQuery.apply(db, args); };

// After request completes:
if (queryCount > 10) {
  console.warn(`N+1 ALERT: ${req.method} ${req.path} executed ${queryCount} queries`);
}
```

## Bundle Analysis

### Next.js Bundle Analyzer

```bash
# Install
pnpm add -D @next/bundle-analyzer

# next.config.js
const withBundleAnalyzer = require('@next/bundle-analyzer')({
  enabled: process.env.ANALYZE === 'true',
});
module.exports = withBundleAnalyzer(nextConfig);

# Run analysis
ANALYZE=true pnpm build
# Opens browser with interactive treemap
```

### Quick Bundle Size Check

```bash
# Check what you're shipping
npx source-map-explorer .next/static/chunks/*.js

# Size of individual imports
npx import-cost  # VS Code extension for inline size

# Find heavy dependencies
npx depcheck --json | jq '.dependencies'
npx bundlephobia-cli <package-name>
```

### Common Bundle Wins

| Before | After | Savings |
|--------|-------|---------|
| `import _ from 'lodash'` | `import groupBy from 'lodash/groupBy'` | ~70KB |
| `import moment from 'moment'` | `import { format } from 'date-fns'` | ~60KB |
| `import { icons } from 'lucide-react'` | `import { Search } from 'lucide-react'` | ~50KB |
| Static import of heavy component | `dynamic(() => import('./HeavyChart'))` | Deferred |
| All routes in one chunk | Code splitting per route (automatic in Next.js) | Per-route |

## Load Testing with k6

```javascript
// load-test.k6.js
import http from 'k6/http'
import { check, sleep } from 'k6'
import { Trend, Rate } from 'k6/metrics'

const apiLatency = new Trend('api_latency')
const errorRate = new Rate('errors')

export const options = {
  stages: [
    { duration: '1m', target: 20 },    // ramp up
    { duration: '3m', target: 100 },   // sustain
    { duration: '1m', target: 0 },     // ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<200', 'p(99)<500'],
    errors: ['rate<0.01'],
    api_latency: ['p(95)<150'],
  },
}

export default function () {
  const res = http.get(`${__ENV.BASE_URL}/api/v1/projects?limit=20`, {
    headers: { Authorization: `Bearer ${__ENV.TOKEN}` },
  })

  apiLatency.add(res.timings.duration)
  check(res, {
    'status 200': (r) => r.status === 200,
    'body has data': (r) => JSON.parse(r.body).data !== undefined,
  }) || errorRate.add(1)

  sleep(1)
}
```

```bash
# Run locally
k6 run load-test.k6.js -e BASE_URL=http://localhost:3000 -e TOKEN=$TOKEN

# Run with cloud reporting
k6 cloud load-test.k6.js
```

## Before/After Measurement Template

```markdown
## Performance Optimization: [What You Fixed]

**Date:** YYYY-MM-DD
**Ticket:** PROJ-123

### Problem
[1-2 sentences: what was slow, how it was observed]

### Root Cause
[What the profiler revealed — include flamegraph link or screenshot]

### Baseline (Before)
| Metric | Value |
|--------|-------|
| P50 latency | XXms |
| P95 latency | XXms |
| P99 latency | XXms |
| Throughput (RPS) | XX |
| DB queries/request | XX |
| Bundle size | XXkB |

### Fix Applied
[Brief description + link to PR]

### After
| Metric | Before | After | Delta |
|--------|--------|-------|-------|
| P50 | XXms | XXms | -XX% |
| P95 | XXms | XXms | -XX% |
| P99 | XXms | XXms | -XX% |
| RPS | XX | XX | +XX% |
| DB queries/req | XX | XX | -XX% |

### Verification
[Link to k6 output, CI run, or monitoring dashboard]
```

## Quick-Win Optimization Checklist

```
DATABASE
[ ] Missing indexes on WHERE/ORDER BY columns
[ ] N+1 queries (check query count per request)
[ ] SELECT * when only 2-3 columns needed
[ ] No LIMIT on unbounded queries
[ ] Missing connection pool (new connection per request)
[ ] Stale statistics (run ANALYZE on busy tables)

NODE.JS
[ ] Sync I/O (fs.readFileSync) in request handlers
[ ] JSON.parse/stringify of large objects in hot loops
[ ] Missing response compression (gzip/brotli)
[ ] Dependencies loaded inside request handlers (move to module level)
[ ] Sequential awaits that could be Promise.all

BUNDLE
[ ] Full lodash/moment import instead of specific functions
[ ] Static imports of heavy components (use dynamic import)
[ ] Images not optimized / not using next/image
[ ] No code splitting on routes

API
[ ] No pagination on list endpoints
[ ] No Cache-Control headers on stable responses
[ ] Serial fetches that could run in parallel
[ ] Fetching related data in loops instead of JOINs
```

## Common Pitfalls

- **Optimizing without measuring** — you will optimize the wrong thing
- **Testing with development data** — 10 rows in dev vs millions in prod reveals different bottlenecks
- **Ignoring P99** — P50 can look fine while P99 is catastrophic for some users
- **Premature optimization** — fix correctness first, then measure and optimize
- **Not re-measuring after the fix** — always verify the fix actually improved the metrics
- **Load testing production** — use staging with production-sized data volumes instead

## Best Practices

1. **Baseline first, always** — record P50/P95/P99, RPS, and error rate before touching anything
2. **One change at a time** — isolate the variable to confirm causation, not correlation
3. **Profile with realistic data volumes** — performance characteristics change dramatically with scale
4. **Set performance budgets** — `p(95) < 200ms` as a CI gate with k6
5. **Monitor continuously** — add Datadog/Prometheus/Grafana metrics for key code paths
6. **Cache aggressively, invalidate precisely** — cache is the fastest optimization but hardest to debug
7. **Document the win** — before/after in the PR description motivates the team and creates institutional knowledge
