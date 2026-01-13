---
name: senior-backend
description: Expert backend development covering API design, database architecture, microservices, message queues, caching, and system scalability.
version: 1.0.0
author: Claude Skills
category: engineering
tags: [backend, api, database, microservices, nodejs, python]
---

# Senior Backend Developer

Expert-level backend development for scalable systems.

## Core Competencies

- API design (REST, GraphQL, gRPC)
- Database design and optimization
- Microservices architecture
- Message queues and event-driven systems
- Caching strategies
- Authentication and authorization
- Performance optimization
- System observability

## API Design

### RESTful API Standards

**URL Structure:**
```
GET    /api/v1/users              # List
POST   /api/v1/users              # Create
GET    /api/v1/users/:id          # Read
PUT    /api/v1/users/:id          # Update (full)
PATCH  /api/v1/users/:id          # Update (partial)
DELETE /api/v1/users/:id          # Delete

# Nested resources
GET    /api/v1/users/:id/orders   # User's orders
POST   /api/v1/users/:id/orders   # Create order for user

# Actions
POST   /api/v1/users/:id/activate # Custom action
```

**Response Codes:**
```
200 OK              - Successful GET, PUT, PATCH
201 Created         - Successful POST
204 No Content      - Successful DELETE
400 Bad Request     - Validation error
401 Unauthorized    - Missing/invalid auth
403 Forbidden       - Insufficient permissions
404 Not Found       - Resource doesn't exist
409 Conflict        - Resource conflict
422 Unprocessable   - Semantic error
429 Too Many        - Rate limit exceeded
500 Internal Error  - Server error
```

**Standard Response Format:**
```json
{
  "data": {},
  "meta": {
    "timestamp": "2024-01-15T10:30:00Z",
    "requestId": "req_abc123"
  },
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 100,
    "hasMore": true
  }
}
```

**Error Response Format:**
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": [
      {
        "field": "email",
        "message": "Must be a valid email address"
      }
    ]
  },
  "meta": {
    "timestamp": "2024-01-15T10:30:00Z",
    "requestId": "req_abc123"
  }
}
```

### GraphQL Schema Design

```graphql
type Query {
  user(id: ID!): User
  users(filter: UserFilter, pagination: PaginationInput): UserConnection!
}

type Mutation {
  createUser(input: CreateUserInput!): UserPayload!
  updateUser(id: ID!, input: UpdateUserInput!): UserPayload!
  deleteUser(id: ID!): DeletePayload!
}

type User {
  id: ID!
  email: String!
  name: String!
  role: Role!
  posts(first: Int, after: String): PostConnection!
  createdAt: DateTime!
}

type UserConnection {
  edges: [UserEdge!]!
  pageInfo: PageInfo!
  totalCount: Int!
}

input CreateUserInput {
  email: String!
  name: String!
  role: Role
}

type UserPayload {
  user: User
  errors: [Error!]
}
```

## Database Design

### Schema Design Principles

**Normalization Levels:**
- 1NF: Atomic values, no repeating groups
- 2NF: No partial dependencies
- 3NF: No transitive dependencies
- Consider denormalization for read performance

**Naming Conventions:**
```sql
-- Tables: plural, snake_case
users, order_items, product_categories

-- Columns: singular, snake_case
user_id, created_at, is_active

-- Primary keys: id or table_id
id, user_id

-- Foreign keys: referenced_table_id
user_id, order_id

-- Indexes: idx_table_column
idx_users_email, idx_orders_created_at
```

### PostgreSQL Patterns

**Table Design:**
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(100) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'user',
    is_active BOOLEAN NOT NULL DEFAULT true,
    metadata JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_created_at ON users(created_at);
CREATE INDEX idx_users_metadata ON users USING GIN(metadata);

-- Updated_at trigger
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at();
```

**Common Queries:**
```sql
-- Pagination with cursor
SELECT * FROM users
WHERE created_at < $cursor_timestamp
ORDER BY created_at DESC
LIMIT $limit + 1;

-- Full-text search
SELECT * FROM products
WHERE search_vector @@ plainto_tsquery('english', $query)
ORDER BY ts_rank(search_vector, plainto_tsquery('english', $query)) DESC;

-- Aggregation with window functions
SELECT
    user_id,
    amount,
    SUM(amount) OVER (PARTITION BY user_id ORDER BY created_at) as running_total
FROM orders;
```

### Query Optimization

**EXPLAIN ANALYZE:**
```sql
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT u.*, COUNT(o.id) as order_count
FROM users u
LEFT JOIN orders o ON o.user_id = u.id
WHERE u.created_at > '2024-01-01'
GROUP BY u.id;
```

**Index Strategies:**
```sql
-- Composite index for common queries
CREATE INDEX idx_orders_user_status ON orders(user_id, status);

-- Partial index for filtered queries
CREATE INDEX idx_orders_pending ON orders(created_at)
WHERE status = 'pending';

-- Covering index to avoid table lookup
CREATE INDEX idx_users_email_name ON users(email) INCLUDE (name, role);
```

## Microservices

### Service Boundaries

**Domain-Driven Design:**
```
Bounded Contexts:
├── User Management
│   ├── Authentication
│   ├── User Profiles
│   └── Permissions
├── Order Processing
│   ├── Cart
│   ├── Checkout
│   └── Order History
├── Inventory
│   ├── Products
│   ├── Stock
│   └── Warehouses
└── Notifications
    ├── Email
    ├── SMS
    └── Push
```

**Communication Patterns:**

Synchronous (HTTP/gRPC):
- Request/Response
- Query operations
- Real-time requirements

Asynchronous (Message Queue):
- Event notification
- Long-running tasks
- Cross-service data sync

### Event-Driven Architecture

**Event Schema:**
```json
{
  "id": "evt_abc123",
  "type": "order.created",
  "source": "order-service",
  "time": "2024-01-15T10:30:00Z",
  "data": {
    "orderId": "ord_xyz789",
    "userId": "usr_def456",
    "total": 99.99,
    "items": []
  },
  "metadata": {
    "correlationId": "corr_123",
    "version": "1.0"
  }
}
```

**Event Handler:**
```typescript
class OrderEventHandler {
  async handle(event: OrderCreatedEvent) {
    switch (event.type) {
      case 'order.created':
        await this.handleOrderCreated(event.data);
        break;
      case 'order.paid':
        await this.handleOrderPaid(event.data);
        break;
    }
  }

  private async handleOrderCreated(data: OrderData) {
    // Reserve inventory
    await this.inventoryService.reserve(data.items);
    // Send confirmation email
    await this.notificationService.sendOrderConfirmation(data);
  }
}
```

## Caching

### Caching Strategies

**Cache-Aside:**
```typescript
async function getUser(id: string): Promise<User> {
  const cacheKey = `user:${id}`;

  // Try cache first
  const cached = await redis.get(cacheKey);
  if (cached) return JSON.parse(cached);

  // Fetch from database
  const user = await db.user.findUnique({ where: { id } });

  // Store in cache
  await redis.set(cacheKey, JSON.stringify(user), 'EX', 3600);

  return user;
}
```

**Write-Through:**
```typescript
async function updateUser(id: string, data: UpdateUserData): Promise<User> {
  // Update database
  const user = await db.user.update({ where: { id }, data });

  // Update cache
  await redis.set(`user:${id}`, JSON.stringify(user), 'EX', 3600);

  return user;
}
```

**Cache Invalidation:**
```typescript
async function invalidateUserCache(userId: string) {
  await redis.del(`user:${userId}`);
  await redis.del(`user:${userId}:orders`);
  await redis.del(`user:${userId}:preferences`);
}
```

### Redis Patterns

```typescript
// Rate limiting
async function rateLimit(key: string, limit: number, window: number): Promise<boolean> {
  const current = await redis.incr(key);
  if (current === 1) {
    await redis.expire(key, window);
  }
  return current <= limit;
}

// Distributed lock
async function acquireLock(key: string, ttl: number): Promise<boolean> {
  const result = await redis.set(key, '1', 'NX', 'EX', ttl);
  return result === 'OK';
}

// Pub/Sub
const publisher = redis.duplicate();
const subscriber = redis.duplicate();

await subscriber.subscribe('events');
subscriber.on('message', (channel, message) => {
  console.log(`Received: ${message}`);
});

await publisher.publish('events', JSON.stringify({ type: 'test' }));
```

## Authentication

### JWT Implementation

```typescript
import jwt from 'jsonwebtoken';

interface TokenPayload {
  userId: string;
  role: string;
  sessionId: string;
}

function generateTokens(user: User) {
  const accessToken = jwt.sign(
    { userId: user.id, role: user.role, sessionId: generateId() },
    process.env.JWT_SECRET,
    { expiresIn: '15m' }
  );

  const refreshToken = jwt.sign(
    { userId: user.id, sessionId: generateId() },
    process.env.JWT_REFRESH_SECRET,
    { expiresIn: '7d' }
  );

  return { accessToken, refreshToken };
}

function verifyAccessToken(token: string): TokenPayload {
  return jwt.verify(token, process.env.JWT_SECRET) as TokenPayload;
}

async function refreshAccessToken(refreshToken: string) {
  const payload = jwt.verify(refreshToken, process.env.JWT_REFRESH_SECRET);

  // Verify session still valid
  const session = await redis.get(`session:${payload.sessionId}`);
  if (!session) throw new Error('Session expired');

  const user = await db.user.findUnique({ where: { id: payload.userId } });
  return generateTokens(user);
}
```

### Authorization Middleware

```typescript
function authorize(...allowedRoles: string[]) {
  return async (req: Request, res: Response, next: NextFunction) => {
    const token = req.headers.authorization?.replace('Bearer ', '');

    if (!token) {
      return res.status(401).json({ error: 'No token provided' });
    }

    try {
      const payload = verifyAccessToken(token);

      if (!allowedRoles.includes(payload.role)) {
        return res.status(403).json({ error: 'Insufficient permissions' });
      }

      req.user = payload;
      next();
    } catch (error) {
      return res.status(401).json({ error: 'Invalid token' });
    }
  };
}

// Usage
app.get('/admin/users', authorize('admin'), listUsers);
app.get('/users/me', authorize('user', 'admin'), getProfile);
```

## Observability

### Logging

```typescript
import pino from 'pino';

const logger = pino({
  level: process.env.LOG_LEVEL || 'info',
  formatters: {
    level: (label) => ({ level: label }),
  },
  base: {
    service: 'user-service',
    environment: process.env.NODE_ENV,
  },
});

// Structured logging
logger.info({ userId, action: 'login' }, 'User logged in');
logger.error({ error, requestId }, 'Request failed');

// Request logging middleware
function requestLogger(req: Request, res: Response, next: NextFunction) {
  const start = Date.now();
  const requestId = generateRequestId();

  req.log = logger.child({ requestId });

  res.on('finish', () => {
    const duration = Date.now() - start;
    req.log.info({
      method: req.method,
      path: req.path,
      statusCode: res.statusCode,
      duration,
    }, 'Request completed');
  });

  next();
}
```

### Metrics

```typescript
import { Registry, Counter, Histogram } from 'prom-client';

const registry = new Registry();

const httpRequestsTotal = new Counter({
  name: 'http_requests_total',
  help: 'Total HTTP requests',
  labelNames: ['method', 'path', 'status'],
  registers: [registry],
});

const httpRequestDuration = new Histogram({
  name: 'http_request_duration_seconds',
  help: 'HTTP request duration',
  labelNames: ['method', 'path'],
  buckets: [0.01, 0.05, 0.1, 0.5, 1, 5],
  registers: [registry],
});

// Middleware
function metricsMiddleware(req: Request, res: Response, next: NextFunction) {
  const end = httpRequestDuration.startTimer({ method: req.method, path: req.route?.path });

  res.on('finish', () => {
    end();
    httpRequestsTotal.inc({
      method: req.method,
      path: req.route?.path,
      status: res.statusCode,
    });
  });

  next();
}
```

## Reference Materials

- `references/api_design.md` - API design guidelines
- `references/database_patterns.md` - Database optimization
- `references/microservices.md` - Service architecture
- `references/security.md` - Security best practices

## Scripts

```bash
# API scaffolder
python scripts/api_scaffold.py --name user --crud

# Database migration generator
python scripts/db_migrate.py --name add_user_roles

# Load testing
python scripts/load_test.py --endpoint /api/users --rps 100

# Service health checker
python scripts/health_check.py --services services.yaml
```
