---
name: senior-fullstack
description: Expert full-stack development covering frontend frameworks, backend services, databases, APIs, and deployment for modern web applications.
version: 1.0.0
author: Claude Skills
category: engineering
tags: [fullstack, react, node, typescript, api, database]
---

# Senior Full-Stack Developer

Expert-level full-stack development for modern web applications.

## Core Competencies

- Frontend frameworks (React, Vue, Next.js)
- Backend services (Node.js, Python, Go)
- Database design (SQL, NoSQL)
- API development (REST, GraphQL)
- Authentication and authorization
- Performance optimization
- Testing strategies
- Deployment and DevOps

## Tech Stack Recommendations

### Modern Full-Stack (2024+)

**Frontend:**
- Framework: Next.js 14+ (App Router)
- Styling: Tailwind CSS
- State: Zustand or Jotai
- Forms: React Hook Form + Zod
- Data Fetching: TanStack Query

**Backend:**
- Runtime: Node.js or Bun
- Framework: Next.js API Routes or Hono
- ORM: Prisma or Drizzle
- Validation: Zod

**Database:**
- Primary: PostgreSQL
- Cache: Redis
- Search: Elasticsearch or Typesense

**Infrastructure:**
- Hosting: Vercel, Railway, or AWS
- CDN: Cloudflare
- Storage: S3-compatible

## Project Structure

### Next.js App Router Structure

```
project/
├── src/
│   ├── app/
│   │   ├── (auth)/
│   │   │   ├── login/
│   │   │   └── register/
│   │   ├── (dashboard)/
│   │   │   ├── layout.tsx
│   │   │   └── page.tsx
│   │   ├── api/
│   │   │   └── [...route]/
│   │   ├── layout.tsx
│   │   └── page.tsx
│   ├── components/
│   │   ├── ui/
│   │   └── features/
│   ├── lib/
│   │   ├── db.ts
│   │   ├── auth.ts
│   │   └── utils.ts
│   ├── hooks/
│   ├── types/
│   └── styles/
├── prisma/
│   └── schema.prisma
├── public/
├── tests/
└── config files
```

## Frontend Patterns

### Component Architecture

**Atomic Design:**
```
components/
├── atoms/        # Button, Input, Label
├── molecules/    # FormField, SearchBar
├── organisms/    # Header, ProductCard
├── templates/    # PageLayout, DashboardLayout
└── pages/        # Assembled pages
```

**Feature-Based:**
```
features/
├── auth/
│   ├── components/
│   ├── hooks/
│   ├── api/
│   └── types/
├── products/
│   ├── components/
│   ├── hooks/
│   ├── api/
│   └── types/
```

### React Patterns

**Custom Hook Pattern:**
```typescript
function useUser(userId: string) {
  const { data, isLoading, error } = useQuery({
    queryKey: ['user', userId],
    queryFn: () => fetchUser(userId),
    staleTime: 5 * 60 * 1000,
  });

  return { user: data, isLoading, error };
}
```

**Compound Component Pattern:**
```typescript
const Card = ({ children }: Props) => (
  <div className="card">{children}</div>
);
Card.Header = ({ children }: Props) => (
  <div className="card-header">{children}</div>
);
Card.Body = ({ children }: Props) => (
  <div className="card-body">{children}</div>
);
Card.Footer = ({ children }: Props) => (
  <div className="card-footer">{children}</div>
);

// Usage
<Card>
  <Card.Header>Title</Card.Header>
  <Card.Body>Content</Card.Body>
</Card>
```

### State Management

**Zustand Store:**
```typescript
interface Store {
  user: User | null;
  setUser: (user: User) => void;
  logout: () => void;
}

const useStore = create<Store>((set) => ({
  user: null,
  setUser: (user) => set({ user }),
  logout: () => set({ user: null }),
}));
```

## Backend Patterns

### API Design

**RESTful Endpoints:**
```
GET    /api/users          # List users
POST   /api/users          # Create user
GET    /api/users/:id      # Get user
PUT    /api/users/:id      # Update user
DELETE /api/users/:id      # Delete user
GET    /api/users/:id/posts # User's posts
```

**Response Format:**
```typescript
// Success
{
  "data": { ... },
  "meta": {
    "page": 1,
    "limit": 20,
    "total": 100
  }
}

// Error
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input",
    "details": [
      { "field": "email", "message": "Invalid email format" }
    ]
  }
}
```

### Request Validation

```typescript
import { z } from 'zod';

const CreateUserSchema = z.object({
  email: z.string().email(),
  name: z.string().min(2).max(100),
  role: z.enum(['user', 'admin']).default('user'),
});

async function createUser(req: Request) {
  const body = await req.json();
  const result = CreateUserSchema.safeParse(body);

  if (!result.success) {
    return Response.json(
      { error: { code: 'VALIDATION_ERROR', details: result.error.issues } },
      { status: 400 }
    );
  }

  const user = await db.user.create({ data: result.data });
  return Response.json({ data: user }, { status: 201 });
}
```

### Error Handling

```typescript
class AppError extends Error {
  constructor(
    public code: string,
    public message: string,
    public statusCode: number = 400,
    public details?: unknown
  ) {
    super(message);
  }
}

// Middleware
function errorHandler(error: Error) {
  if (error instanceof AppError) {
    return Response.json(
      { error: { code: error.code, message: error.message, details: error.details } },
      { status: error.statusCode }
    );
  }

  console.error(error);
  return Response.json(
    { error: { code: 'INTERNAL_ERROR', message: 'Something went wrong' } },
    { status: 500 }
  );
}
```

## Database Patterns

### Prisma Schema Example

```prisma
model User {
  id        String   @id @default(cuid())
  email     String   @unique
  name      String
  role      Role     @default(USER)
  posts     Post[]
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt
}

model Post {
  id        String   @id @default(cuid())
  title     String
  content   String
  published Boolean  @default(false)
  author    User     @relation(fields: [authorId], references: [id])
  authorId  String
  tags      Tag[]
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt

  @@index([authorId])
}

enum Role {
  USER
  ADMIN
}
```

### Query Optimization

```typescript
// Bad: N+1 query
const users = await db.user.findMany();
for (const user of users) {
  const posts = await db.post.findMany({ where: { authorId: user.id } });
}

// Good: Include relation
const users = await db.user.findMany({
  include: {
    posts: {
      where: { published: true },
      take: 5,
      orderBy: { createdAt: 'desc' },
    },
  },
});

// Pagination
const posts = await db.post.findMany({
  skip: (page - 1) * limit,
  take: limit,
  where: { published: true },
  orderBy: { createdAt: 'desc' },
});
```

## Authentication

### JWT Authentication Flow

```typescript
// Login
async function login(email: string, password: string) {
  const user = await db.user.findUnique({ where: { email } });
  if (!user || !await verifyPassword(password, user.passwordHash)) {
    throw new AppError('INVALID_CREDENTIALS', 'Invalid email or password', 401);
  }

  const token = jwt.sign(
    { userId: user.id, role: user.role },
    process.env.JWT_SECRET,
    { expiresIn: '7d' }
  );

  return { token, user: sanitizeUser(user) };
}

// Middleware
async function authenticate(req: Request) {
  const header = req.headers.get('authorization');
  if (!header?.startsWith('Bearer ')) {
    throw new AppError('UNAUTHORIZED', 'Missing token', 401);
  }

  const token = header.slice(7);
  try {
    const payload = jwt.verify(token, process.env.JWT_SECRET);
    return payload;
  } catch {
    throw new AppError('UNAUTHORIZED', 'Invalid token', 401);
  }
}
```

### Session-Based Auth (Next.js)

```typescript
// Using NextAuth.js
import NextAuth from 'next-auth';
import { PrismaAdapter } from '@auth/prisma-adapter';

export const { handlers, auth, signIn, signOut } = NextAuth({
  adapter: PrismaAdapter(prisma),
  providers: [
    Credentials({
      credentials: {
        email: { type: 'email' },
        password: { type: 'password' },
      },
      authorize: async (credentials) => {
        // Validate credentials
      },
    }),
  ],
  session: { strategy: 'jwt' },
});
```

## Testing Strategy

### Testing Pyramid

```
         /\
        /  \     E2E (Playwright)
       /----\    - Critical user flows
      /      \   - 10% of tests
     /--------\  Integration
    /          \ - API endpoints
   /------------\- 30% of tests
  /    Unit      \
 /----------------\
 - Components, Utils
 - 60% of tests
```

### Test Examples

**Unit Test:**
```typescript
describe('formatCurrency', () => {
  it('formats USD correctly', () => {
    expect(formatCurrency(1234.56, 'USD')).toBe('$1,234.56');
  });

  it('handles zero', () => {
    expect(formatCurrency(0, 'USD')).toBe('$0.00');
  });
});
```

**API Integration Test:**
```typescript
describe('POST /api/users', () => {
  it('creates user with valid data', async () => {
    const response = await app.request('/api/users', {
      method: 'POST',
      body: JSON.stringify({ email: 'test@example.com', name: 'Test' }),
    });

    expect(response.status).toBe(201);
    const data = await response.json();
    expect(data.data.email).toBe('test@example.com');
  });

  it('rejects invalid email', async () => {
    const response = await app.request('/api/users', {
      method: 'POST',
      body: JSON.stringify({ email: 'invalid', name: 'Test' }),
    });

    expect(response.status).toBe(400);
  });
});
```

## Performance Optimization

### Frontend Performance

**Code Splitting:**
```typescript
const Dashboard = lazy(() => import('./Dashboard'));

function App() {
  return (
    <Suspense fallback={<Loading />}>
      <Dashboard />
    </Suspense>
  );
}
```

**Image Optimization:**
```typescript
import Image from 'next/image';

<Image
  src="/hero.jpg"
  alt="Hero"
  width={1200}
  height={600}
  priority
  placeholder="blur"
/>
```

### Backend Performance

**Caching:**
```typescript
import { Redis } from 'ioredis';

const redis = new Redis(process.env.REDIS_URL);

async function getUser(id: string) {
  const cached = await redis.get(`user:${id}`);
  if (cached) return JSON.parse(cached);

  const user = await db.user.findUnique({ where: { id } });
  await redis.set(`user:${id}`, JSON.stringify(user), 'EX', 3600);
  return user;
}
```

## Reference Materials

- `references/react_patterns.md` - React best practices
- `references/api_design.md` - API design guidelines
- `references/database_patterns.md` - Database optimization
- `references/security_checklist.md` - Security best practices

## Scripts

```bash
# Project scaffolder
python scripts/scaffold.py --name my-app --stack nextjs

# Code quality analyzer
python scripts/code_quality.py --path ./src

# Database migration helper
python scripts/db_migrate.py --action generate

# Performance audit
python scripts/perf_audit.py --url https://localhost:3000
```
