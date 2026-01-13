---
name: senior-qa
description: Expert quality assurance covering test strategy, automation, performance testing, and quality engineering.
version: 1.0.0
author: Claude Skills
category: engineering
tags: [qa, testing, automation, performance, quality]
---

# Senior QA Engineer

Expert-level quality assurance and test engineering.

## Core Competencies

- Test strategy and planning
- Test automation frameworks
- Performance testing
- API testing
- E2E testing
- CI/CD integration
- Quality metrics
- Test data management

## Test Strategy

### Test Pyramid

```
           /\
          /  \     E2E Tests (10%)
         /----\    - Critical flows
        /      \   - Cross-system
       /--------\  Integration Tests (20%)
      /          \ - API contracts
     /------------\- Service interactions
    /   Unit       \
   /    Tests (70%) \ - Business logic
  /------------------\- Functions/methods
```

### Test Types

| Type | Scope | Speed | Stability | Maintenance |
|------|-------|-------|-----------|-------------|
| Unit | Function | Fast | High | Low |
| Integration | Service | Medium | Medium | Medium |
| E2E | System | Slow | Lower | High |
| Performance | System | Slow | Medium | Medium |

### Test Plan Template

```markdown
# Test Plan: [Feature Name]

## Overview
- Feature: [Brief description]
- Release: [Version]
- Date: [Target date]

## Scope
### In Scope
- [Functionality to test]

### Out of Scope
- [Excluded items]

## Test Approach
- Unit tests: [Coverage target]
- Integration tests: [Key scenarios]
- E2E tests: [Critical paths]

## Entry Criteria
- [ ] Code complete
- [ ] Unit tests passing
- [ ] Environment ready

## Exit Criteria
- [ ] All P1/P2 bugs fixed
- [ ] Test coverage > 80%
- [ ] Performance benchmarks met

## Risk Assessment
| Risk | Impact | Mitigation |
|------|--------|------------|
| [Risk] | [H/M/L] | [Action] |

## Schedule
| Phase | Start | End |
|-------|-------|-----|
| Test prep | | |
| Execution | | |
| Sign-off | | |
```

## Test Automation

### Jest Testing

```typescript
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { LoginForm } from './LoginForm';

describe('LoginForm', () => {
  const mockOnSubmit = jest.fn();

  beforeEach(() => {
    mockOnSubmit.mockClear();
  });

  it('renders email and password fields', () => {
    render(<LoginForm onSubmit={mockOnSubmit} />);

    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument();
  });

  it('validates required fields', async () => {
    render(<LoginForm onSubmit={mockOnSubmit} />);

    fireEvent.click(screen.getByRole('button', { name: /sign in/i }));

    await waitFor(() => {
      expect(screen.getByText(/email is required/i)).toBeInTheDocument();
      expect(screen.getByText(/password is required/i)).toBeInTheDocument();
    });

    expect(mockOnSubmit).not.toHaveBeenCalled();
  });

  it('validates email format', async () => {
    const user = userEvent.setup();
    render(<LoginForm onSubmit={mockOnSubmit} />);

    await user.type(screen.getByLabelText(/email/i), 'invalid-email');
    await user.click(screen.getByRole('button', { name: /sign in/i }));

    await waitFor(() => {
      expect(screen.getByText(/invalid email format/i)).toBeInTheDocument();
    });
  });

  it('submits form with valid data', async () => {
    const user = userEvent.setup();
    render(<LoginForm onSubmit={mockOnSubmit} />);

    await user.type(screen.getByLabelText(/email/i), 'test@example.com');
    await user.type(screen.getByLabelText(/password/i), 'password123');
    await user.click(screen.getByRole('button', { name: /sign in/i }));

    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalledWith({
        email: 'test@example.com',
        password: 'password123',
      });
    });
  });
});
```

### Playwright E2E Testing

```typescript
import { test, expect } from '@playwright/test';

test.describe('Checkout Flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.getByRole('button', { name: 'Accept Cookies' }).click();
  });

  test('complete purchase as guest', async ({ page }) => {
    // Add item to cart
    await page.goto('/products/widget-pro');
    await page.getByRole('button', { name: 'Add to Cart' }).click();
    await expect(page.getByText('Added to cart')).toBeVisible();

    // Go to checkout
    await page.getByRole('link', { name: 'Cart' }).click();
    await page.getByRole('button', { name: 'Checkout' }).click();

    // Fill shipping info
    await page.getByLabel('Email').fill('test@example.com');
    await page.getByLabel('First Name').fill('John');
    await page.getByLabel('Last Name').fill('Doe');
    await page.getByLabel('Address').fill('123 Main St');
    await page.getByLabel('City').fill('New York');
    await page.getByLabel('ZIP').fill('10001');
    await page.getByRole('button', { name: 'Continue to Payment' }).click();

    // Fill payment info (test card)
    const stripeFrame = page.frameLocator('iframe[name*="stripe"]');
    await stripeFrame.getByPlaceholder('Card number').fill('4242424242424242');
    await stripeFrame.getByPlaceholder('MM / YY').fill('12/30');
    await stripeFrame.getByPlaceholder('CVC').fill('123');

    // Complete purchase
    await page.getByRole('button', { name: 'Place Order' }).click();

    // Verify confirmation
    await expect(page.getByText('Order Confirmed')).toBeVisible();
    await expect(page.getByText('Order #')).toBeVisible();
  });

  test('shows error for invalid card', async ({ page }) => {
    // ... add item and go to payment
    const stripeFrame = page.frameLocator('iframe[name*="stripe"]');
    await stripeFrame.getByPlaceholder('Card number').fill('4000000000000002');
    await stripeFrame.getByPlaceholder('MM / YY').fill('12/30');
    await stripeFrame.getByPlaceholder('CVC').fill('123');

    await page.getByRole('button', { name: 'Place Order' }).click();

    await expect(page.getByText('Your card was declined')).toBeVisible();
  });
});

// Page Object Model
class CheckoutPage {
  constructor(private page: Page) {}

  async fillShippingInfo(info: ShippingInfo) {
    await this.page.getByLabel('Email').fill(info.email);
    await this.page.getByLabel('First Name').fill(info.firstName);
    await this.page.getByLabel('Last Name').fill(info.lastName);
    await this.page.getByLabel('Address').fill(info.address);
    await this.page.getByLabel('City').fill(info.city);
    await this.page.getByLabel('ZIP').fill(info.zip);
  }

  async fillPaymentInfo(card: CardInfo) {
    const frame = this.page.frameLocator('iframe[name*="stripe"]');
    await frame.getByPlaceholder('Card number').fill(card.number);
    await frame.getByPlaceholder('MM / YY').fill(card.expiry);
    await frame.getByPlaceholder('CVC').fill(card.cvc);
  }

  async placeOrder() {
    await this.page.getByRole('button', { name: 'Place Order' }).click();
  }

  async expectConfirmation() {
    await expect(this.page.getByText('Order Confirmed')).toBeVisible();
  }
}
```

### API Testing

```typescript
import { test, expect } from '@playwright/test';

test.describe('Users API', () => {
  const baseURL = 'https://api.example.com/v1';
  let authToken: string;

  test.beforeAll(async ({ request }) => {
    const response = await request.post(`${baseURL}/auth/login`, {
      data: { email: 'admin@example.com', password: 'password' },
    });
    const body = await response.json();
    authToken = body.token;
  });

  test('GET /users returns paginated list', async ({ request }) => {
    const response = await request.get(`${baseURL}/users`, {
      headers: { Authorization: `Bearer ${authToken}` },
      params: { page: 1, limit: 10 },
    });

    expect(response.status()).toBe(200);

    const body = await response.json();
    expect(body.data).toHaveLength(10);
    expect(body.pagination).toMatchObject({
      page: 1,
      limit: 10,
      hasMore: expect.any(Boolean),
    });
  });

  test('POST /users creates new user', async ({ request }) => {
    const userData = {
      email: `test-${Date.now()}@example.com`,
      name: 'Test User',
      role: 'user',
    };

    const response = await request.post(`${baseURL}/users`, {
      headers: { Authorization: `Bearer ${authToken}` },
      data: userData,
    });

    expect(response.status()).toBe(201);

    const body = await response.json();
    expect(body.data).toMatchObject({
      id: expect.any(String),
      email: userData.email,
      name: userData.name,
    });
  });

  test('POST /users validates required fields', async ({ request }) => {
    const response = await request.post(`${baseURL}/users`, {
      headers: { Authorization: `Bearer ${authToken}` },
      data: { name: 'Test' }, // Missing email
    });

    expect(response.status()).toBe(400);

    const body = await response.json();
    expect(body.error.code).toBe('VALIDATION_ERROR');
    expect(body.error.details).toContainEqual(
      expect.objectContaining({ field: 'email' })
    );
  });
});
```

## Performance Testing

### k6 Load Testing

```javascript
import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

const errorRate = new Rate('errors');
const responseTime = new Trend('response_time');

export const options = {
  stages: [
    { duration: '2m', target: 100 },  // Ramp up
    { duration: '5m', target: 100 },  // Steady state
    { duration: '2m', target: 200 },  // Spike
    { duration: '5m', target: 200 },  // Steady state at peak
    { duration: '2m', target: 0 },    // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<500', 'p(99)<1000'],
    errors: ['rate<0.01'],
  },
};

export default function () {
  const BASE_URL = 'https://api.example.com';

  // Login
  const loginRes = http.post(`${BASE_URL}/auth/login`, JSON.stringify({
    email: 'test@example.com',
    password: 'password',
  }), {
    headers: { 'Content-Type': 'application/json' },
  });

  check(loginRes, {
    'login successful': (r) => r.status === 200,
  });

  const token = loginRes.json('token');

  // Get products
  const productsRes = http.get(`${BASE_URL}/products`, {
    headers: { Authorization: `Bearer ${token}` },
  });

  check(productsRes, {
    'products status 200': (r) => r.status === 200,
    'products returned': (r) => r.json('data').length > 0,
  });

  errorRate.add(productsRes.status !== 200);
  responseTime.add(productsRes.timings.duration);

  // Add to cart
  const cartRes = http.post(`${BASE_URL}/cart/items`, JSON.stringify({
    productId: productsRes.json('data.0.id'),
    quantity: 1,
  }), {
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
  });

  check(cartRes, {
    'add to cart successful': (r) => r.status === 201,
  });

  sleep(1);
}

export function handleSummary(data) {
  return {
    'summary.json': JSON.stringify(data),
    stdout: textSummary(data, { indent: ' ', enableColors: true }),
  };
}
```

## Quality Metrics

### Test Coverage

```yaml
coverage:
  targets:
    unit:
      statements: 80%
      branches: 75%
      functions: 80%
      lines: 80%

    integration:
      api_endpoints: 100%
      critical_flows: 100%

    e2e:
      user_journeys: 100%
      error_scenarios: 80%
```

### Defect Metrics

```
Defect Density = Defects / KLOC
Defect Detection Rate = Defects Found in Testing / Total Defects
Defect Leakage = Defects Found in Production / Total Defects
Mean Time to Detect = Avg time from introduction to detection
Mean Time to Resolve = Avg time from detection to fix
```

### Quality Dashboard

```
┌─────────────────────────────────────────────────────┐
│                 Quality Dashboard                    │
├─────────────────────────────────────────────────────┤
│  Test Coverage        Build Status     Defects      │
│  ████████░░ 82%      ✓ Passing        Open: 12     │
│                                        P1: 2        │
│  Tests               Last Run          P2: 5        │
│  Total: 1,234        2h ago           P3: 5        │
│  Passing: 1,220                                     │
│  Failing: 14                                        │
├─────────────────────────────────────────────────────┤
│  Performance (p95)   Flaky Tests      Code Quality  │
│  API: 245ms         Rate: 2.1%        A: 85%       │
│  Page Load: 1.2s    Count: 8          Tech Debt: M │
└─────────────────────────────────────────────────────┘
```

## Reference Materials

- `references/test_patterns.md` - Testing patterns and practices
- `references/automation_guide.md` - Automation framework setup
- `references/performance_testing.md` - Load testing guide
- `references/quality_metrics.md` - Metrics and reporting

## Scripts

```bash
# Test suite generator
python scripts/test_gen.py --component UserService --type unit

# Coverage reporter
python scripts/coverage_report.py --threshold 80 --format html

# Flaky test detector
python scripts/flaky_detector.py --runs 10 --threshold 0.1

# Performance baseline
python scripts/perf_baseline.py --scenario checkout --output baseline.json
```
