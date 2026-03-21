---
name: api-design-reviewer
description: Reviews REST API designs for quality, consistency, and breaking changes. Lints OpenAPI specs, generates API scorecards, and detects breaking changes between versions. Use when designing APIs, reviewing API contracts, or managing API versioning.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  category: engineering
  domain: api-design
  tier: POWERFUL
---

# API Design Reviewer

**Tier:** POWERFUL
**Category:** Engineering / Architecture
**Maintainer:** Claude Skills Team

## Overview

The API Design Reviewer skill provides comprehensive analysis and review of API designs, focusing on REST conventions, best practices, and industry standards. This skill helps engineering teams build consistent, maintainable, and well-designed APIs through automated linting, breaking change detection, and design scorecards.

## Core Capabilities

### 1. API Linting and Convention Analysis
- **Resource Naming Conventions**: Enforces kebab-case for resources, camelCase for fields
- **HTTP Method Usage**: Validates proper use of GET, POST, PUT, PATCH, DELETE
- **URL Structure**: Analyzes endpoint patterns for consistency and RESTful design
- **Status Code Compliance**: Ensures appropriate HTTP status codes are used
- **Error Response Formats**: Validates consistent error response structures
- **Documentation Coverage**: Checks for missing descriptions and documentation gaps

### 2. Breaking Change Detection
- **Endpoint Removal**: Detects removed or deprecated endpoints
- **Response Shape Changes**: Identifies modifications to response structures
- **Field Removal**: Tracks removed or renamed fields in API responses
- **Type Changes**: Catches field type modifications that could break clients
- **Required Field Additions**: Flags new required fields that could break existing integrations
- **Status Code Changes**: Detects changes to expected status codes

### 3. API Design Scoring and Assessment
- **Consistency Analysis** (30%): Evaluates naming conventions, response patterns, and structural consistency
- **Documentation Quality** (20%): Assesses completeness and clarity of API documentation
- **Security Implementation** (20%): Reviews authentication, authorization, and security headers
- **Usability Design** (15%): Analyzes ease of use, discoverability, and developer experience
- **Performance Patterns** (15%): Evaluates caching, pagination, and efficiency patterns

## REST Design Principles

### Resource Naming Conventions
```
✅ Good Examples:
- /api/v1/users
- /api/v1/user-profiles
- /api/v1/orders/123/line-items

❌ Bad Examples:
- /api/v1/getUsers
- /api/v1/user_profiles
- /api/v1/orders/123/lineItems
```

### HTTP Method Usage
- **GET**: Retrieve resources (safe, idempotent)
- **POST**: Create new resources (not idempotent)
- **PUT**: Replace entire resources (idempotent)
- **PATCH**: Partial resource updates (not necessarily idempotent)
- **DELETE**: Remove resources (idempotent)

### URL Structure Best Practices
```
Collection Resources: /api/v1/users
Individual Resources: /api/v1/users/123
Nested Resources: /api/v1/users/123/orders
Actions: /api/v1/users/123/activate (POST)
Filtering: /api/v1/users?status=active&role=admin
```

## Versioning Strategies

### 1. URL Versioning (Recommended)
```
/api/v1/users
/api/v2/users
```
**Pros**: Clear, explicit, easy to route  
**Cons**: URL proliferation, caching complexity

### 2. Header Versioning
```
GET /api/users
Accept: application/vnd.api+json;version=1
```
**Pros**: Clean URLs, content negotiation  
**Cons**: Less visible, harder to test manually

### 3. Media Type Versioning
```
GET /api/users
Accept: application/vnd.myapi.v1+json
```
**Pros**: RESTful, supports multiple representations  
**Cons**: Complex, harder to implement

### 4. Query Parameter Versioning
```
/api/users?version=1
```
**Pros**: Simple to implement  
**Cons**: Not RESTful, can be ignored

## Pagination Patterns

### Offset-Based Pagination
```json
{
  "data": [...],
  "pagination": {
    "offset": 20,
    "limit": 10,
    "total": 150,
    "hasMore": true
  }
}
```

### Cursor-Based Pagination
```json
{
  "data": [...],
  "pagination": {
    "nextCursor": "eyJpZCI6MTIzfQ==",
    "hasMore": true
  }
}
```

### Page-Based Pagination
```json
{
  "data": [...],
  "pagination": {
    "page": 3,
    "pageSize": 10,
    "totalPages": 15,
    "totalItems": 150
  }
}
```

## Error Response Formats

### Standard Error Structure
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "The request contains invalid parameters",
    "details": [
      {
        "field": "email",
        "code": "INVALID_FORMAT",
        "message": "Email address is not valid"
      }
    ],
    "requestId": "req-123456",
    "timestamp": "2024-02-16T13:00:00Z"
  }
}
```

### HTTP Status Code Usage
- **400 Bad Request**: Invalid request syntax or parameters
- **401 Unauthorized**: Authentication required
- **403 Forbidden**: Access denied (authenticated but not authorized)
- **404 Not Found**: Resource not found
- **409 Conflict**: Resource conflict (duplicate, version mismatch)
- **422 Unprocessable Entity**: Valid syntax but semantic errors
- **429 Too Many Requests**: Rate limit exceeded
- **500 Internal Server Error**: Unexpected server error

## Authentication and Authorization Patterns

### Bearer Token Authentication
```
Authorization: Bearer <token>
```

### API Key Authentication
```
X-API-Key: <api-key>
Authorization: Api-Key <api-key>
```

### OAuth 2.0 Flow
```
Authorization: Bearer <oauth-access-token>
```

### Role-Based Access Control (RBAC)
```json
{
  "user": {
    "id": "123",
    "roles": ["admin", "editor"],
    "permissions": ["read:users", "write:orders"]
  }
}
```

## Rate Limiting Implementation

### Headers
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640995200
```

### Response on Limit Exceeded
```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Too many requests",
    "retryAfter": 3600
  }
}
```

## HATEOAS (Hypermedia as the Engine of Application State)

### Example Implementation
```json
{
  "id": "123",
  "name": "John Doe",
  "email": "john@example.com",
  "_links": {
    "self": { "href": "/api/v1/users/123" },
    "orders": { "href": "/api/v1/users/123/orders" },
    "profile": { "href": "/api/v1/users/123/profile" },
    "deactivate": { 
      "href": "/api/v1/users/123/deactivate",
      "method": "POST"
    }
  }
}
```

## Idempotency

### Idempotent Methods
- **GET**: Always safe and idempotent
- **PUT**: Should be idempotent (replace entire resource)
- **DELETE**: Should be idempotent (same result)
- **PATCH**: May or may not be idempotent

### Idempotency Keys
```
POST /api/v1/payments
Idempotency-Key: 123e4567-e89b-12d3-a456-426614174000
```

## Backward Compatibility Guidelines

### Safe Changes (Non-Breaking)
- Adding optional fields to requests
- Adding fields to responses
- Adding new endpoints
- Making required fields optional
- Adding new enum values (with graceful handling)

### Breaking Changes (Require Version Bump)
- Removing fields from responses
- Making optional fields required
- Changing field types
- Removing endpoints
- Changing URL structures
- Modifying error response formats

## OpenAPI/Swagger Validation

### Required Components
- **API Information**: Title, description, version
- **Server Information**: Base URLs and descriptions
- **Path Definitions**: All endpoints with methods
- **Parameter Definitions**: Query, path, header parameters
- **Request/Response Schemas**: Complete data models
- **Security Definitions**: Authentication schemes
- **Error Responses**: Standard error formats

### Best Practices
- Use consistent naming conventions
- Provide detailed descriptions for all components
- Include examples for complex objects
- Define reusable components and schemas
- Validate against OpenAPI specification

## Performance Considerations

### Caching Strategies
```
Cache-Control: public, max-age=3600
ETag: "123456789"
Last-Modified: Wed, 21 Oct 2015 07:28:00 GMT
```

### Efficient Data Transfer
- Use appropriate HTTP methods
- Implement field selection (`?fields=id,name,email`)
- Support compression (gzip)
- Implement efficient pagination
- Use ETags for conditional requests

### Resource Optimization
- Avoid N+1 queries
- Implement batch operations
- Use async processing for heavy operations
- Support partial updates (PATCH)

## Security Best Practices

### Input Validation
- Validate all input parameters
- Sanitize user data
- Use parameterized queries
- Implement request size limits

### Authentication Security
- Use HTTPS everywhere
- Implement secure token storage
- Support token expiration and refresh
- Use strong authentication mechanisms

### Authorization Controls
- Implement principle of least privilege
- Use resource-based permissions
- Support fine-grained access control
- Audit access patterns

## Tools and Scripts

### api_linter.py
Analyzes API specifications for compliance with REST conventions and best practices.

**Features:**
- OpenAPI/Swagger spec validation
- Naming convention checks
- HTTP method usage validation
- Error format consistency
- Documentation completeness analysis

### breaking_change_detector.py
Compares API specification versions to identify breaking changes.

**Features:**
- Endpoint comparison
- Schema change detection
- Field removal/modification tracking
- Migration guide generation
- Impact severity assessment

### api_scorecard.py
Provides comprehensive scoring of API design quality.

**Features:**
- Multi-dimensional scoring
- Detailed improvement recommendations
- Letter grade assessment (A-F)
- Benchmark comparisons
- Progress tracking

## Integration Examples

### CI/CD Integration
```yaml
- name: API Linting
  run: python scripts/api_linter.py openapi.json

- name: Breaking Change Detection
  run: python scripts/breaking_change_detector.py openapi-v1.json openapi-v2.json

- name: API Scorecard
  run: python scripts/api_scorecard.py openapi.json
```

### Pre-commit Hooks
```bash
#!/bin/bash
python engineering/api-design-reviewer/scripts/api_linter.py api/openapi.json
if [ $? -ne 0 ]; then
  echo "API linting failed. Please fix the issues before committing."
  exit 1
fi
```

## Best Practices Summary

1. **Consistency First**: Maintain consistent naming, response formats, and patterns
2. **Documentation**: Provide comprehensive, up-to-date API documentation
3. **Versioning**: Plan for evolution with clear versioning strategies
4. **Error Handling**: Implement consistent, informative error responses
5. **Security**: Build security into every layer of the API
6. **Performance**: Design for scale and efficiency from the start
7. **Backward Compatibility**: Minimize breaking changes and provide migration paths
8. **Testing**: Implement comprehensive testing including contract testing
9. **Monitoring**: Add observability for API usage and performance
10. **Developer Experience**: Prioritize ease of use and clear documentation

## Common Anti-Patterns to Avoid

1. **Verb-based URLs**: Use nouns for resources, not actions
2. **Inconsistent Response Formats**: Maintain standard response structures
3. **Over-nesting**: Avoid deeply nested resource hierarchies
4. **Ignoring HTTP Status Codes**: Use appropriate status codes for different scenarios
5. **Poor Error Messages**: Provide actionable, specific error information
6. **Missing Pagination**: Always paginate list endpoints
7. **No Versioning Strategy**: Plan for API evolution from day one
8. **Exposing Internal Structure**: Design APIs for external consumption, not internal convenience
9. **Missing Rate Limiting**: Protect your API from abuse and overload
10. **Inadequate Testing**: Test all aspects including error cases and edge conditions

## Conclusion

The API Design Reviewer skill provides a comprehensive framework for building, reviewing, and maintaining high-quality REST APIs. By following these guidelines and using the provided tools, development teams can create APIs that are consistent, well-documented, secure, and maintainable.

Regular use of the linting, breaking change detection, and scoring tools ensures continuous improvement and helps maintain API quality throughout the development lifecycle.

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| Linter reports false positives on action endpoints (e.g., `/activate`) | Verb detection flags action segments as REST anti-patterns | Action endpoints are acceptable for non-CRUD operations; suppress with caution or restructure as `POST /resource/{id}/activations` |
| Breaking change detector misses schema-level changes | Input specs lack `components/schemas` definitions or use inline schemas | Ensure both old and new specs define reusable schemas under `components/schemas` for accurate comparison |
| Scorecard gives low security score despite auth being implemented | Security schemes are defined but not applied globally or per-operation | Add a top-level `security` array in the OpenAPI spec and reference `securitySchemes` under `components` |
| Linter exits with code 1 on specs with no endpoints | Zero endpoints with any structural error triggers a non-zero exit | Verify the spec contains at least one path under `paths`; the linter requires endpoints to produce a meaningful score |
| JSON parse error on valid YAML OpenAPI specs | All three tools accept JSON input only | Convert YAML specs to JSON before running tools: `python -c "import yaml,json,sys; json.dump(yaml.safe_load(open(sys.argv[1])),open(sys.argv[2],'w'),indent=2)" spec.yaml spec.json` |
| Naming convention warnings on legacy APIs with snake_case fields | Linter enforces camelCase for properties and kebab-case for URL segments | For brownfield APIs, address naming in new endpoints first and plan a migration for existing fields across a major version bump |
| Scorecard reports 0% for performance category | Spec contains no caching headers, pagination, or compression references | Add `Cache-Control` response headers, define pagination query parameters (`limit`, `offset` or `cursor`), and document compression support |

## Success Criteria

- Zero breaking changes detected between consecutive minor or patch releases (semver compliance)
- API consistency score (from `api_scorecard.py`) above 90 across all reviewed specifications
- Overall scorecard grade of B or higher (80+) before any API ships to production
- 100% of endpoints include at least one success response and one error response definition
- All path segments follow kebab-case naming and all schema properties follow camelCase naming with zero linter errors
- Breaking change reports generated and reviewed for every PR that modifies an OpenAPI spec
- Documentation coverage score above 85%, meaning every operation has a summary and every schema has a description

## Scope & Limitations

**This skill covers:**
- Linting OpenAPI 3.x and Swagger 2.0 JSON specifications against REST conventions
- Detecting breaking, potentially-breaking, and non-breaking changes between two spec versions
- Scoring API design quality across consistency, documentation, security, usability, and performance
- Generating actionable migration guides when breaking changes are found

**This skill does NOT cover:**
- Runtime API testing, load testing, or contract testing (see `api-test-suite-builder`)
- GraphQL, gRPC, or WebSocket API design review
- Auto-generation of OpenAPI specs from code or server stubs
- Authentication flow implementation or OAuth server configuration (see `senior-security` in engineering/)

## Integration Points

| Skill | Integration | Data Flow |
|-------|-------------|-----------|
| `engineering/api-test-suite-builder` | Generate test cases from linter findings | Linter issues feed into test plan priorities for endpoint validation |
| `engineering/changelog-generator` | Document breaking changes in release notes | Breaking change detector output provides structured change data for changelogs |
| `engineering/ci-cd-pipeline-builder` | Gate deployments on API quality | Scorecard grade and linter exit codes integrate as pipeline quality gates |
| `engineering/senior-backend` | Review API implementation against design | Scorecard recommendations guide backend refactoring decisions |
| `engineering/code-reviewer` | Enrich PR reviews with API analysis | Linter and breaking change reports attach to PR review comments |
| `engineering/release-manager` | Validate version bumps match change severity | Breaking change detector severity levels inform semver version decisions |

## Tool Reference

### api_linter.py

**Purpose:** Analyzes OpenAPI/Swagger JSON specifications for compliance with REST conventions and best practices. Checks naming conventions, HTTP method usage, URL structure, status codes, error formats, documentation completeness, and security configuration.

**Usage:**
```bash
python api_linter.py [OPTIONS] INPUT_FILE
```

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `input_file` | positional | Yes | -- | Path to OpenAPI/Swagger JSON file or raw endpoints JSON |
| `--format` | option | No | `text` | Output format: `text` or `json` |
| `--raw-endpoints` | flag | No | off | Treat input as raw endpoint definitions instead of an OpenAPI spec |
| `--output` | option | No | stdout | Write report to the specified file path |

**Example:**
```bash
python api_linter.py openapi.json
python api_linter.py --format json openapi.json > report.json
python api_linter.py --raw-endpoints endpoints.json
python api_linter.py --output lint-report.txt openapi.json
```

**Output Formats:**
- **text** -- Human-readable report with issue breakdown by category, severity icons, suggestions, and a scoring summary. Exits with code 1 if any errors are found, 0 otherwise.
- **json** -- Machine-readable JSON object with `summary` (total_endpoints, endpoints_with_issues, total_issues, errors, warnings, info, score) and `issues` array (severity, category, message, path, suggestion).

---

### breaking_change_detector.py

**Purpose:** Compares two versions of an OpenAPI JSON specification and detects breaking changes including removed endpoints, modified response structures, removed fields, type changes, new required fields, parameter changes, and status code changes. Generates migration guides for each breaking change.

**Usage:**
```bash
python breaking_change_detector.py [OPTIONS] OLD_SPEC NEW_SPEC
```

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `old_spec` | positional | Yes | -- | Path to the old (baseline) API specification JSON file |
| `new_spec` | positional | Yes | -- | Path to the new API specification JSON file |
| `--format` | option | No | `text` | Output format: `text` or `json` |
| `--output` | option | No | stdout | Write report to the specified file path |
| `--exit-on-breaking` | flag | No | off | Exit with code 1 if any breaking changes are detected |

**Example:**
```bash
python breaking_change_detector.py v1.json v2.json
python breaking_change_detector.py --format json v1.json v2.json > changes.json
python breaking_change_detector.py --exit-on-breaking --output report.txt v1.json v2.json
```

**Output Formats:**
- **text** -- Human-readable report listing each change with its type (breaking, potentially_breaking, non_breaking, enhancement), severity (critical, high, medium, low, info), category, path, message, impact description, and migration guide.
- **json** -- Machine-readable JSON object with `summary` (total_changes, breaking_changes, potentially_breaking_changes, non_breaking_changes, enhancements, and per-severity counts) and `changes` array (changeType, severity, category, path, message, oldValue, newValue, migrationGuide, impactDescription).

---

### api_scorecard.py

**Purpose:** Generates a comprehensive API design quality scorecard by evaluating an OpenAPI JSON specification across five weighted dimensions: Consistency (30%), Documentation (20%), Security (20%), Usability (15%), and Performance (15%). Produces letter grades (A-F) per category and overall, with actionable improvement recommendations.

**Usage:**
```bash
python api_scorecard.py [OPTIONS] SPEC_FILE
```

**Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `spec_file` | positional | Yes | -- | Path to the OpenAPI/Swagger specification JSON file |
| `--format` | option | No | `text` | Output format: `text` or `json` |
| `--output` | option | No | stdout | Write scorecard to the specified file path |
| `--min-grade` | option | No | none | Minimum acceptable grade (`A`, `B`, `C`, `D`, `F`); exits with code 1 if the overall grade falls below this threshold |

**Example:**
```bash
python api_scorecard.py openapi.json
python api_scorecard.py --format json openapi.json > scorecard.json
python api_scorecard.py --min-grade B --output scorecard.txt openapi.json
```

**Output Formats:**
- **text** -- Human-readable scorecard showing API info, per-category scores with letter grades, issue counts, recommendations, and an overall weighted score with grade.
- **json** -- Machine-readable JSON object with `apiInfo`, `categoryScores` (per category: score, maxScore, weight, letterGrade, weightedScore, issues, recommendations), `overallScore`, `overallGrade`, `totalEndpoints`, and `topRecommendations`.