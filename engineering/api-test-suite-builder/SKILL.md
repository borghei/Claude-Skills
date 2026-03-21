---
name: api-test-suite-builder
description: Generate comprehensive API test suites from route definitions across frameworks. Covers auth testing, input validation, contract testing, load testing with k6, API mocking, and OpenAPI-driven test generation. Use when adding new APIs, auditing test coverage, or building regression suites.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  category: engineering
  domain: api-testing
  tier: POWERFUL
  updated: 2026-03-09
  frameworks: vitest, pytest, supertest, httpx, k6, pact
---

# API Test Suite Builder

**Tier:** POWERFUL
**Category:** Engineering / Testing
**Maintainer:** Claude Skills Team

## Overview

Scan API route definitions across frameworks (Next.js App Router, Express, FastAPI, Django REST, Go net/http), analyze request/response schemas, and generate comprehensive test suites covering authentication, authorization, input validation, error handling, pagination, file uploads, rate limiting, contract testing, and load testing. Outputs ready-to-run test files for Vitest+Supertest (Node), Pytest+httpx (Python), or k6 (load testing).

## Keywords

API testing, test generation, contract testing, load testing, Pact, k6, Supertest, httpx, auth testing, input validation, error matrix, OpenAPI testing, regression suite

## Core Capabilities

### 1. Route Detection and Analysis
- Scan source files to extract all API endpoints with HTTP methods
- Parse request body schemas from types, validators, and decorators
- Detect authentication middleware and authorization rules
- Identify response types and status codes from handler implementations

### 2. Test Matrix Generation
- Authentication: valid/invalid/expired tokens, missing headers, wrong roles
- Input validation: missing fields, wrong types, boundary values, injection
- Error paths: 400/401/403/404/409/422/429/500 for each route
- Pagination: first/last/empty/oversized pages, cursor-based and offset
- File uploads: valid, oversized, wrong MIME, empty, path traversal
- Rate limiting: burst detection, per-user vs global limits

### 3. Contract Testing
- OpenAPI spec to test generation
- Pact consumer-driven contract tests
- Schema snapshot testing for breaking change detection
- Response shape validation with JSON Schema

### 4. Load Testing
- k6 scripts with ramp-up patterns and SLA thresholds
- Artillery scenarios for sustained load profiles
- Latency percentile tracking (P50, P95, P99)
- Concurrent user simulation with realistic data

## When to Use

- New API added — generate test scaffold before implementation (TDD)
- Legacy API with no tests — scan and generate baseline coverage
- Pre-release — ensure all routes have at least smoke tests
- API contract change — detect and test breaking changes
- Security audit — generate adversarial input tests
- Performance validation — create load test baselines

## Route Detection Commands

### Next.js App Router
```bash
# Find all route handlers and extract HTTP methods
find ./app/api -name "route.ts" -o -name "route.js" | while read f; do
  route=$(echo "$f" | sed 's|./app||; s|/route\.[tj]s||')
  methods=$(grep -oE "export (async )?function (GET|POST|PUT|PATCH|DELETE)" "$f" | \
    grep -oE "(GET|POST|PUT|PATCH|DELETE)" | tr '\n' ',')
  echo "$methods $route"
done
```

### Express / Fastify
```bash
grep -rn "router\.\(get\|post\|put\|delete\|patch\)\|app\.\(get\|post\|put\|delete\|patch\)" \
  src/ --include="*.ts" --include="*.js" | \
  grep -oE "\.(get|post|put|delete|patch)\(['\"][^'\"]+['\"]" | \
  sed "s/\.\(.*\)('\(.*\)'/\U\1 \2/"
```

### FastAPI
```bash
grep -rn "@\(app\|router\)\.\(get\|post\|put\|delete\|patch\)" . --include="*.py" | \
  grep -oE "(get|post|put|delete|patch)\(['\"][^'\"]*['\"]"
```

### Go (net/http, Chi, Gin)
```bash
grep -rn "\.HandleFunc\|\.Handle\|\.GET\|\.POST\|\.PUT\|\.DELETE" . --include="*.go" | \
  grep -oE "(GET|POST|PUT|DELETE|HandleFunc)\(['\"][^'\"]*['\"]"
```

## Test Generation Framework

### Auth Test Matrix

For every authenticated endpoint, generate these test cases:

```typescript
// tests/api/[resource]/auth.test.ts
import { describe, it, expect } from 'vitest'
import request from 'supertest'
import { createTestApp } from '../../helpers/app'
import { createTestUser, generateToken, generateExpiredToken } from '../../helpers/auth'

describe('GET /api/v1/projects - Authentication', () => {
  const app = createTestApp()

  it('returns 401 when no Authorization header is sent', async () => {
    const res = await request(app).get('/api/v1/projects')
    expect(res.status).toBe(401)
    expect(res.body.error).toMatchObject({
      code: 'UNAUTHORIZED',
      message: expect.any(String),
    })
  })

  it('returns 401 when token format is invalid', async () => {
    const res = await request(app)
      .get('/api/v1/projects')
      .set('Authorization', 'InvalidFormat')
    expect(res.status).toBe(401)
  })

  it('returns 401 when token is expired', async () => {
    const token = generateExpiredToken({ userId: 'user_123' })
    const res = await request(app)
      .get('/api/v1/projects')
      .set('Authorization', `Bearer ${token}`)
    expect(res.status).toBe(401)
    expect(res.body.error.code).toBe('TOKEN_EXPIRED')
  })

  it('returns 403 when user lacks required role', async () => {
    const user = await createTestUser({ role: 'viewer' })
    const token = generateToken(user)
    const res = await request(app)
      .get('/api/v1/projects')
      .set('Authorization', `Bearer ${token}`)
    expect(res.status).toBe(403)
  })

  it('returns 401 when token belongs to a deleted user', async () => {
    const user = await createTestUser()
    const token = generateToken(user)
    await deleteUser(user.id)
    const res = await request(app)
      .get('/api/v1/projects')
      .set('Authorization', `Bearer ${token}`)
    expect(res.status).toBe(401)
  })

  it('returns 200 with valid token and correct role', async () => {
    const user = await createTestUser({ role: 'member' })
    const token = generateToken(user)
    const res = await request(app)
      .get('/api/v1/projects')
      .set('Authorization', `Bearer ${token}`)
    expect(res.status).toBe(200)
    expect(res.body).toHaveProperty('data')
  })
})
```

### Input Validation Matrix

```typescript
// tests/api/[resource]/validation.test.ts
describe('POST /api/v1/projects - Input Validation', () => {
  const validPayload = {
    name: 'My Project',
    description: 'A test project',
    visibility: 'private',
  }

  it('returns 422 when body is empty', async () => {
    const res = await authedRequest('POST', '/api/v1/projects', {})
    expect(res.status).toBe(422)
    expect(res.body.error.details).toEqual(
      expect.arrayContaining([
        expect.objectContaining({ field: 'name', rule: 'required' }),
      ])
    )
  })

  it.each([
    ['name', undefined, 'required'],
    ['name', '', 'min_length'],
    ['name', 'a'.repeat(256), 'max_length'],
    ['name', 123, 'type'],
    ['visibility', 'invalid', 'enum'],
    ['description', 'a'.repeat(10001), 'max_length'],
  ])('returns 422 when %s is %s (%s)', async (field, value, rule) => {
    const payload = { ...validPayload, [field]: value }
    if (value === undefined) delete payload[field]
    const res = await authedRequest('POST', '/api/v1/projects', payload)
    expect(res.status).toBe(422)
    expect(res.body.error.details).toEqual(
      expect.arrayContaining([
        expect.objectContaining({ field, rule }),
      ])
    )
  })

  it('rejects SQL injection in string fields', async () => {
    const res = await authedRequest('POST', '/api/v1/projects', {
      ...validPayload,
      name: "'; DROP TABLE projects; --",
    })
    // Should either reject (422) or sanitize and succeed (201)
    expect([201, 422]).toContain(res.status)
    if (res.status === 201) {
      expect(res.body.data.name).not.toContain('DROP TABLE')
    }
  })

  it('rejects XSS payloads in string fields', async () => {
    const res = await authedRequest('POST', '/api/v1/projects', {
      ...validPayload,
      name: '<script>alert("xss")</script>',
    })
    if (res.status === 201) {
      expect(res.body.data.name).not.toContain('<script>')
    }
  })

  it('accepts valid payload and returns 201 with created resource', async () => {
    const res = await authedRequest('POST', '/api/v1/projects', validPayload)
    expect(res.status).toBe(201)
    expect(res.body.data).toMatchObject({
      id: expect.any(String),
      name: validPayload.name,
      visibility: validPayload.visibility,
      created_at: expect.any(String),
    })
    // Verify sensitive fields are NOT in response
    expect(res.body.data).not.toHaveProperty('internal_id')
  })
})
```

### Pagination Testing

```typescript
describe('GET /api/v1/projects - Pagination', () => {
  beforeAll(async () => {
    await seedProjects(25) // Create 25 test projects
  })

  it('returns first page with default limit', async () => {
    const res = await authedRequest('GET', '/api/v1/projects')
    expect(res.status).toBe(200)
    expect(res.body.data.length).toBeLessThanOrEqual(20) // default limit
    expect(res.body.meta).toMatchObject({
      total: 25,
      page: 1,
      has_more: true,
    })
  })

  it('returns second page correctly', async () => {
    const res = await authedRequest('GET', '/api/v1/projects?page=2&limit=10')
    expect(res.status).toBe(200)
    expect(res.body.data.length).toBe(10)
    expect(res.body.meta.page).toBe(2)
  })

  it('returns empty array for page beyond data', async () => {
    const res = await authedRequest('GET', '/api/v1/projects?page=100')
    expect(res.status).toBe(200)
    expect(res.body.data).toEqual([])
    expect(res.body.meta.has_more).toBe(false)
  })

  it('rejects limit above maximum', async () => {
    const res = await authedRequest('GET', '/api/v1/projects?limit=1000')
    expect(res.status).toBe(422)
  })

  it('returns consistent results with cursor-based pagination', async () => {
    const page1 = await authedRequest('GET', '/api/v1/projects?limit=5')
    const cursor = page1.body.meta.next_cursor
    const page2 = await authedRequest('GET', `/api/v1/projects?limit=5&cursor=${cursor}`)
    // No overlapping items between pages
    const ids1 = new Set(page1.body.data.map(p => p.id))
    const ids2 = new Set(page2.body.data.map(p => p.id))
    const overlap = [...ids1].filter(id => ids2.has(id))
    expect(overlap).toHaveLength(0)
  })
})
```

## Contract Testing with Pact

```typescript
// tests/contracts/projects.pact.test.ts
import { PactV3, MatchersV3 } from '@pact-foundation/pact'

const { like, eachLike, string, integer, iso8601DateTimeWithMillis } = MatchersV3

const provider = new PactV3({
  consumer: 'frontend-app',
  provider: 'projects-api',
})

describe('Projects API Contract', () => {
  it('returns a list of projects', async () => {
    provider
      .given('projects exist')
      .uponReceiving('a request for projects')
      .withRequest({
        method: 'GET',
        path: '/api/v1/projects',
        headers: { Authorization: like('Bearer token123') },
      })
      .willRespondWith({
        status: 200,
        headers: { 'Content-Type': 'application/json' },
        body: {
          data: eachLike({
            id: string('proj_abc123'),
            name: string('My Project'),
            visibility: string('private'),
            created_at: iso8601DateTimeWithMillis('2026-01-15T10:30:00.000Z'),
            owner: {
              id: string('user_xyz'),
              name: string('Jane Doe'),
            },
          }),
          meta: {
            total: integer(1),
            page: integer(1),
            has_more: false,
          },
        },
      })

    await provider.executeTest(async (mockServer) => {
      const response = await fetch(`${mockServer.url}/api/v1/projects`, {
        headers: { Authorization: 'Bearer token123' },
      })
      expect(response.status).toBe(200)
      const body = await response.json()
      expect(body.data[0]).toHaveProperty('id')
      expect(body.data[0]).toHaveProperty('name')
      expect(body.meta).toHaveProperty('total')
    })
  })
})
```

## Load Testing with k6

```javascript
// tests/load/api-load.k6.js
import http from 'k6/http'
import { check, sleep } from 'k6'
import { Rate, Trend } from 'k6/metrics'

const errorRate = new Rate('errors')
const listLatency = new Trend('list_projects_duration')
const createLatency = new Trend('create_project_duration')

export const options = {
  stages: [
    { duration: '30s', target: 10 },   // ramp up to 10 users
    { duration: '1m',  target: 50 },   // ramp up to 50 users
    { duration: '2m',  target: 50 },   // sustain 50 users
    { duration: '30s', target: 0 },    // ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<200', 'p(99)<500'],  // SLA: P95 < 200ms
    errors: ['rate<0.01'],                            // Error rate < 1%
    list_projects_duration: ['p(95)<150'],
    create_project_duration: ['p(95)<300'],
  },
}

const BASE_URL = __ENV.BASE_URL || 'http://localhost:3000'
const AUTH_TOKEN = __ENV.AUTH_TOKEN || 'test-token'

const headers = {
  Authorization: `Bearer ${AUTH_TOKEN}`,
  'Content-Type': 'application/json',
}

export default function () {
  // GET /api/v1/projects
  const listRes = http.get(`${BASE_URL}/api/v1/projects?limit=20`, { headers })
  listLatency.add(listRes.timings.duration)
  check(listRes, {
    'list: status 200': (r) => r.status === 200,
    'list: has data array': (r) => JSON.parse(r.body).data !== undefined,
  }) || errorRate.add(1)

  sleep(1)

  // POST /api/v1/projects
  const createRes = http.post(
    `${BASE_URL}/api/v1/projects`,
    JSON.stringify({
      name: `Load Test Project ${Date.now()}`,
      description: 'Created by k6 load test',
      visibility: 'private',
    }),
    { headers }
  )
  createLatency.add(createRes.timings.duration)
  check(createRes, {
    'create: status 201': (r) => r.status === 201,
    'create: has id': (r) => JSON.parse(r.body).data.id !== undefined,
  }) || errorRate.add(1)

  sleep(1)
}
```

### Run Load Tests

```bash
# Local
k6 run tests/load/api-load.k6.js

# With environment variables
k6 run -e BASE_URL=https://staging.app.com -e AUTH_TOKEN=$STAGING_TOKEN tests/load/api-load.k6.js

# Output to cloud dashboard
k6 cloud tests/load/api-load.k6.js
```

## Test Generation Process

When given a codebase, follow this workflow:

1. **Scan routes** using detection commands for the detected framework
2. **Read each route handler** to understand: request schema, auth middleware, response types, business rules
3. **Generate test file per resource** (not per route) using the matrices above
4. **Name tests descriptively**: `"returns 401 when token is expired"` not `"auth test 3"`
5. **Use factories/fixtures** for test data — never hardcode IDs or tokens
6. **Assert response shape**, not just status codes
7. **Include negative tests** — error paths catch 80% of production bugs
8. **Add contract tests** for any API consumed by external services
9. **Add load tests** for any endpoint expected to handle >100 RPM

## Test Helper Patterns

```typescript
// tests/helpers/auth.ts — reusable auth utilities
import jwt from 'jsonwebtoken'

export function generateToken(user: { id: string; role: string }, expiresIn = '1h') {
  return jwt.sign({ sub: user.id, role: user.role }, process.env.JWT_SECRET!, { expiresIn })
}

export function generateExpiredToken(user: { id: string }) {
  return jwt.sign({ sub: user.id }, process.env.JWT_SECRET!, { expiresIn: '-1h' })
}

// tests/helpers/request.ts — authed request helper
export async function authedRequest(
  method: string,
  path: string,
  body?: any,
  userOverrides?: Partial<User>,
) {
  const user = await createTestUser(userOverrides)
  const token = generateToken(user)
  const req = request(app)[method.toLowerCase()](path)
    .set('Authorization', `Bearer ${token}`)
  if (body) req.send(body)
  return req
}

// tests/helpers/factory.ts — test data factories
export function buildProject(overrides = {}) {
  return {
    name: `Project ${Date.now()}`,
    description: 'Test project',
    visibility: 'private',
    ...overrides,
  }
}
```

## Common Pitfalls

- **Testing only happy paths** — 80% of production bugs live in error paths; test those first
- **Hardcoded IDs and tokens** — use factories; data changes between environments
- **Shared state between tests** — always clean up; one test's data should not affect another
- **Testing implementation, not behavior** — assert what the API returns, not how it does it
- **Missing boundary tests** — off-by-one errors are the most common bug in pagination and limits
- **Ignoring Content-Type** — test that the API rejects wrong content types
- **Not testing token expiry separately from invalid tokens** — they produce different error codes
- **Flaky tests from timing** — never depend on clock time; use deterministic test data

## Best Practices

1. One describe block per endpoint, nested by concern (auth, validation, business logic)
2. Seed only the minimal data each test needs — do not load the entire database
3. Assert specific error codes and field names, not just HTTP status
4. Test that sensitive fields (password, secret_key) are never present in responses
5. For contract tests, run them in CI against both consumer and provider
6. For load tests, set SLA thresholds (`p(95)<200`) and fail the build if violated
7. Keep test files colocated with the code they test or in a parallel `tests/` tree

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| Generated tests fail with `Cannot find module` errors | Test helper imports reference paths that don't exist in target project | Update import paths in generated files to match the project's `tsconfig.json` paths or Jest `moduleNameMapper` configuration |
| Auth tests all return 200 instead of 401/403 | Test app instance is not using the same auth middleware as production | Ensure `createTestApp()` loads the full middleware stack including auth guards; check that `JWT_SECRET` env var is set in the test environment |
| Pact contract verification fails on CI but passes locally | Provider state callbacks are missing or the provider is running a different version | Pin the provider version in CI, ensure all `given()` states have matching provider state handlers, and verify the Pact broker URL is correct |
| k6 load tests report 0 requests or instant completion | `BASE_URL` environment variable is not set or points to an unreachable host | Pass `-e BASE_URL=http://localhost:3000` explicitly and verify the server is running before starting the k6 run |
| Pagination tests fail with inconsistent ordering | The API does not enforce a default sort order, so results vary between runs | Add an explicit `ORDER BY` clause to the API query or include `?sort=created_at` in test requests to guarantee deterministic ordering |
| Input validation tests pass but miss real-world edge cases | Generated boundary values use generic limits (256 chars) that don't match actual schema constraints | Read the schema or validator definitions (Zod, Joi, Pydantic) and adjust boundary values to match declared `maxLength`, `minimum`, and `enum` values |
| Tests are flaky due to database state leakage between runs | Tests share a database and don't clean up after themselves | Wrap each test in a transaction that rolls back, or use `beforeEach` to truncate relevant tables; avoid relying on auto-increment IDs |

## Success Criteria

- **Route coverage >= 95%**: Every API endpoint in the codebase has at least one generated test file covering auth, validation, and happy path scenarios
- **Error path ratio >= 3:1**: At least three negative/error test cases exist for every happy-path test case per endpoint
- **Test execution time < 60s**: The full generated unit/integration test suite runs in under 60 seconds (excluding load tests)
- **Zero hardcoded secrets**: No test file contains hardcoded API keys, tokens, or passwords; all credentials come from environment variables or factories
- **Contract test coverage for all external APIs**: Every endpoint consumed by an external service or frontend client has a corresponding Pact or schema snapshot test
- **Load test SLA thresholds defined**: Every load-tested endpoint has explicit P95 and P99 latency thresholds and an error rate ceiling configured in the k6 script
- **CI integration complete**: Generated tests run automatically in the CI pipeline with clear pass/fail reporting and no manual intervention required

## Scope & Limitations

**This skill covers:**
- Generating test suites from route definitions for REST APIs across Node.js, Python, and Go frameworks
- Authentication, authorization, input validation, pagination, and error-path test generation
- Consumer-driven contract testing with Pact and schema snapshot validation
- Load and performance testing script generation with k6 and Artillery

**This skill does NOT cover:**
- GraphQL API testing (see `engineering/api-design-reviewer` for schema review patterns)
- End-to-end browser testing or UI interaction testing (see `engineering/playwright-pro`)
- Database migration testing or schema validation (see `engineering/database-schema-designer`)
- Security penetration testing beyond input sanitization checks (see `engineering/skill-security-auditor`)

## Integration Points

| Skill | Integration | Data Flow |
|-------|------------|-----------|
| `engineering/api-design-reviewer` | Validate API design before generating tests | Design review output defines the endpoint contracts that this skill generates tests for |
| `engineering/ci-cd-pipeline-builder` | Embed generated tests into CI/CD pipelines | Generated test files and k6 scripts are added as pipeline stages with pass/fail gates |
| `engineering/playwright-pro` | Complement API tests with E2E browser tests | API test suite validates backend behavior; Playwright tests validate the frontend consuming those APIs |
| `engineering/database-schema-designer` | Align test fixtures with database schema | Schema definitions inform factory functions and seed data used in generated test helpers |
| `engineering/observability-designer` | Monitor test-covered endpoints in production | Load test thresholds (P95, P99) feed into alerting rules for the same endpoints in production dashboards |
| `engineering/performance-profiler` | Investigate endpoints that fail load test thresholds | k6 results identify slow endpoints; the profiler skill traces root causes at the code level |
