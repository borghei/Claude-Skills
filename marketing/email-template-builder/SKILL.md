---
name: email-template-builder
description: >
  Build production-grade email template systems with React Email or MJML. Covers
  responsive layouts, dark mode, multi-provider sending (Resend, SendGrid,
  Postmark, SES), i18n, spam score optimization, preview servers, and analytics
  tracking. Use when setting up transactional email infrastructure, building
  email design systems, or debugging deliverability issues.
license: MIT + Commons Clause
metadata:
  version: 1.0.0
  author: borghei
  category: marketing
  domain: email-engineering
  tier: POWERFUL
  updated: 2026-03-09
  frameworks: react-email, mjml, email-deliverability, responsive-email
---
# Email Template Builder

**Tier:** POWERFUL
**Category:** Engineering / Marketing
**Tags:** email templates, React Email, MJML, responsive email, deliverability, transactional email, dark mode

## Overview

Build complete transactional email systems: component-based templates with React Email or MJML, multi-provider sending abstraction, local preview with hot reload, i18n support, dark mode, spam optimization, and UTM tracking. Outputs production-ready code for any major email provider.

This skill builds the email rendering and sending infrastructure. For writing email copy and designing sequences, use email-sequence.

---

## Architecture Decision: React Email vs MJML

| Factor | React Email | MJML |
|--------|-----------|------|
| **Component reuse** | Full React component model | Partial (mj-attributes) |
| **TypeScript** | Native | Requires build step |
| **Preview server** | Built-in (`email dev`) | Requires separate setup |
| **Email client compatibility** | Good (renders to tables) | Excellent (battle-tested) |
| **Dark mode** | CSS media queries | CSS media queries |
| **Learning curve** | Low (if you know React) | Low (HTML-like syntax) |
| **Best for** | Teams already using React | Maximum email client compat |

**Recommendation:** React Email for TypeScript teams shipping SaaS. MJML for marketing teams needing maximum compatibility across Outlook, Gmail, Apple Mail, and legacy clients.

---

## Project Structure

```
emails/
├── components/
│   ├── layout/
│   │   ├── base-layout.tsx          # Shared wrapper: header, footer, styles
│   │   ├── button.tsx               # CTA button component
│   │   └── divider.tsx              # Styled horizontal rule
│   ├── blocks/
│   │   ├── hero.tsx                 # Hero section with heading + text
│   │   ├── feature-row.tsx          # Icon + text feature highlight
│   │   ├── testimonial.tsx          # Quote + attribution
│   │   └── pricing-table.tsx        # Plan comparison
├── templates/
│   ├── welcome.tsx                  # Welcome / confirm email
│   ├── password-reset.tsx           # Password reset link
│   ├── invoice.tsx                  # Payment receipt / invoice
│   ├── trial-expiring.tsx           # Trial expiration warning
│   ├── weekly-digest.tsx            # Activity summary
│   └── team-invite.tsx              # Team invitation
├── lib/
│   ├── send.ts                      # Unified send function
│   ├── providers/
│   │   ├── resend.ts                # Resend adapter
│   │   ├── sendgrid.ts              # SendGrid adapter
│   │   ├── postmark.ts              # Postmark adapter
│   │   └── ses.ts                   # AWS SES adapter
│   ├── tracking.ts                  # UTM parameter injection
│   └── render.ts                    # Template rendering
├── i18n/
│   ├── en.ts                        # English strings
│   ├── de.ts                        # German strings
│   └── types.ts                     # Typed translation keys
└── package.json
```

---

## Base Layout Component

```tsx
// emails/components/layout/base-layout.tsx
import {
  Body, Container, Head, Html, Img, Preview,
  Section, Text, Hr, Font
} from "@react-email/components";

interface BaseLayoutProps {
  preview: string;
  locale?: string;
  children: React.ReactNode;
}

export function BaseLayout({ preview, locale = "en", children }: BaseLayoutProps) {
  return (
    <Html lang={locale}>
      <Head>
        <Font
          fontFamily="Inter"
          fallbackFontFamily="Arial"
          webFont={{
            url: "https://fonts.gstatic.com/s/inter/v13/UcCO3FwrK3iLTeHuS_nVMrMxCp50SjIw2boKoduKmMEVuLyfAZ9hiJ-Ek-_EeA.woff2",
            format: "woff2",
          }}
          fontWeight={400}
          fontStyle="normal"
        />
        <style>{`
          @media (prefers-color-scheme: dark) {
            .email-body { background-color: #111827 !important; }
            .email-container { background-color: #1f2937 !important; }
            .email-text { color: #e5e7eb !important; }
            .email-heading { color: #f9fafb !important; }
            .email-muted { color: #9ca3af !important; }
          }
          @media only screen and (max-width: 600px) {
            .email-container { width: 100% !important; padding: 16px !important; }
          }
        `}</style>
      </Head>
      <Preview>{preview}</Preview>
      <Body className="email-body" style={body}>
        <Container className="email-container" style={container}>
          <Section style={header}>
            <Img
              src={`${process.env.ASSET_URL}/logo.png`}
              width={120} height={36} alt="[Product]"
            />
          </Section>
          <Section style={content}>{children}</Section>
          <Hr className="email-muted" style={divider} />
          <Section style={footer}>
            <Text className="email-muted" style={footerText}>
              [Company] Inc. - [Address]
            </Text>
            <Text className="email-muted" style={footerText}>
              <a href="{{unsubscribe_url}}" style={link}>Unsubscribe</a>
              {" | "}
              <a href="{{preferences_url}}" style={link}>Email Preferences</a>
              {" | "}
              <a href="{{privacy_url}}" style={link}>Privacy Policy</a>
            </Text>
          </Section>
        </Container>
      </Body>
    </Html>
  );
}

// Styles (inline for email client compatibility)
const body = { backgroundColor: "#f3f4f6", fontFamily: "Inter, Arial, sans-serif", margin: 0, padding: "40px 0" };
const container = { maxWidth: "600px", margin: "0 auto", backgroundColor: "#ffffff", borderRadius: "8px", overflow: "hidden" };
const header = { padding: "24px 32px", borderBottom: "1px solid #e5e7eb" };
const content = { padding: "32px" };
const divider = { borderColor: "#e5e7eb", margin: "0 32px" };
const footer = { padding: "24px 32px" };
const footerText = { fontSize: "12px", color: "#6b7280", textAlign: "center" as const, margin: "4px 0", lineHeight: "1.6" };
const link = { color: "#6b7280", textDecoration: "underline" };
```

---

## Template Examples

### Welcome Email

```tsx
// emails/templates/welcome.tsx
import { Button, Heading, Text } from "@react-email/components";
import { BaseLayout } from "../components/layout/base-layout";

interface WelcomeProps {
  name: string;
  confirmUrl: string;
  trialDays?: number;
}

export default function Welcome({ name, confirmUrl, trialDays = 14 }: WelcomeProps) {
  return (
    <BaseLayout preview={`Welcome, ${name}! Confirm your email to get started.`}>
      <Heading className="email-heading" style={h1}>
        Welcome to [Product], {name}
      </Heading>
      <Text className="email-text" style={text}>
        You have {trialDays} days to explore everything -- no credit card required.
        Confirm your email to activate your account:
      </Text>
      <Button href={confirmUrl} style={button}>
        Confirm Email Address
      </Button>
      <Text className="email-muted" style={muted}>
        Button not working? Paste this link in your browser:{" "}
        <a href={confirmUrl} style={linkStyle}>{confirmUrl}</a>
      </Text>
    </BaseLayout>
  );
}

const h1 = { fontSize: "24px", fontWeight: "700", color: "#111827", margin: "0 0 16px", lineHeight: "1.3" };
const text = { fontSize: "16px", lineHeight: "1.6", color: "#374151", margin: "0 0 24px" };
const button = { backgroundColor: "#4f46e5", color: "#ffffff", borderRadius: "6px", fontSize: "16px", fontWeight: "600", padding: "12px 24px", textDecoration: "none", display: "inline-block" };
const muted = { fontSize: "13px", color: "#6b7280", marginTop: "24px", lineHeight: "1.5" };
const linkStyle = { color: "#4f46e5", wordBreak: "break-all" as const };
```

### Invoice Email

```tsx
// emails/templates/invoice.tsx
import { Row, Column, Section, Heading, Text, Hr, Button } from "@react-email/components";
import { BaseLayout } from "../components/layout/base-layout";

interface LineItem { description: string; amount: number; }

interface InvoiceProps {
  name: string;
  invoiceNumber: string;
  date: string;
  dueDate: string;
  items: LineItem[];
  total: number;
  currency?: string;
  downloadUrl: string;
}

export default function Invoice({
  name, invoiceNumber, date, dueDate, items,
  total, currency = "USD", downloadUrl,
}: InvoiceProps) {
  const fmt = new Intl.NumberFormat("en-US", { style: "currency", currency });

  return (
    <BaseLayout preview={`Invoice ${invoiceNumber} -- ${fmt.format(total / 100)}`}>
      <Heading className="email-heading" style={h1}>
        Invoice #{invoiceNumber}
      </Heading>
      <Text className="email-text" style={text}>Hi {name},</Text>
      <Text className="email-text" style={text}>
        Here is your invoice. Thank you for your business.
      </Text>

      {/* Meta row */}
      <Section style={metaBox}>
        <Row>
          <Column>
            <Text style={metaLabel}>Invoice Date</Text>
            <Text style={metaValue}>{date}</Text>
          </Column>
          <Column>
            <Text style={metaLabel}>Due Date</Text>
            <Text style={metaValue}>{dueDate}</Text>
          </Column>
          <Column>
            <Text style={metaLabel}>Amount Due</Text>
            <Text style={metaValueBold}>{fmt.format(total / 100)}</Text>
          </Column>
        </Row>
      </Section>

      {/* Line items */}
      {items.map((item, i) => (
        <Row key={i} style={i % 2 === 0 ? rowEven : rowOdd}>
          <Column><Text style={cell}>{item.description}</Text></Column>
          <Column><Text style={cellRight}>{fmt.format(item.amount / 100)}</Text></Column>
        </Row>
      ))}
      <Hr style={divider} />
      <Row>
        <Column><Text style={totalLabel}>Total</Text></Column>
        <Column><Text style={totalValue}>{fmt.format(total / 100)}</Text></Column>
      </Row>

      <Button href={downloadUrl} style={button}>
        Download PDF
      </Button>
    </BaseLayout>
  );
}

const h1 = { fontSize: "24px", fontWeight: "700", color: "#111827", margin: "0 0 16px" };
const text = { fontSize: "15px", lineHeight: "1.6", color: "#374151", margin: "0 0 12px" };
const metaBox = { backgroundColor: "#f9fafb", borderRadius: "8px", padding: "16px", margin: "16px 0" };
const metaLabel = { fontSize: "11px", color: "#6b7280", fontWeight: "600", textTransform: "uppercase" as const, margin: "0 0 4px", letterSpacing: "0.05em" };
const metaValue = { fontSize: "14px", color: "#111827", margin: "0" };
const metaValueBold = { fontSize: "18px", fontWeight: "700", color: "#4f46e5", margin: "0" };
const rowEven = { backgroundColor: "#ffffff" };
const rowOdd = { backgroundColor: "#f9fafb" };
const cell = { fontSize: "14px", color: "#374151", padding: "10px 12px" };
const cellRight = { ...cell, textAlign: "right" as const };
const divider = { borderColor: "#e5e7eb", margin: "8px 0" };
const totalLabel = { fontSize: "16px", fontWeight: "700", color: "#111827", padding: "8px 12px" };
const totalValue = { ...totalLabel, textAlign: "right" as const };
const button = { backgroundColor: "#4f46e5", color: "#ffffff", borderRadius: "6px", padding: "12px 24px", fontSize: "15px", fontWeight: "600", textDecoration: "none", display: "inline-block", marginTop: "16px" };
```

---

## Multi-Provider Send Abstraction

```typescript
// emails/lib/send.ts
import { render } from "@react-email/render";

interface EmailPayload {
  to: string;
  subject: string;
  template: React.ReactElement;
  tags?: Record<string, string>;
}

interface EmailProvider {
  send(payload: { to: string; subject: string; html: string; text: string; tags?: Record<string, string> }): Promise<{ id: string }>;
}

// Provider factory
function getProvider(): EmailProvider {
  const provider = process.env.EMAIL_PROVIDER || "resend";
  switch (provider) {
    case "resend": return require("./providers/resend").default;
    case "sendgrid": return require("./providers/sendgrid").default;
    case "postmark": return require("./providers/postmark").default;
    case "ses": return require("./providers/ses").default;
    default: throw new Error(`Unknown email provider: ${provider}`);
  }
}

export async function sendEmail(payload: EmailPayload) {
  const html = addTracking(render(payload.template), { campaign: payload.tags?.type || "transactional" });
  const text = render(payload.template, { plainText: true });

  return getProvider().send({
    to: payload.to,
    subject: payload.subject,
    html,
    text,
    tags: payload.tags,
  });
}
```

---

## UTM Tracking Injection

```typescript
// emails/lib/tracking.ts
interface TrackingConfig {
  campaign: string;
  source?: string;
  medium?: string;
}

export function addTracking(html: string, config: TrackingConfig): string {
  const params = new URLSearchParams({
    utm_source: config.source || "email",
    utm_medium: config.medium || "transactional",
    utm_campaign: config.campaign,
  }).toString();

  // Add UTM to all internal links (skip unsubscribe and external)
  return html.replace(
    /href="(https?:\/\/(?:www\.)?yourdomain\.com[^"]*?)"/g,
    (match, url) => {
      const sep = url.includes("?") ? "&" : "?";
      return `href="${url}${sep}${params}"`;
    }
  );
}
```

---

## i18n System

```typescript
// emails/i18n/types.ts
export interface EmailStrings {
  welcome: {
    preview: (name: string) => string;
    heading: (name: string) => string;
    body: (days: number) => string;
    cta: string;
    fallbackLink: string;
  };
  invoice: {
    preview: (number: string, amount: string) => string;
    heading: (number: string) => string;
    greeting: (name: string) => string;
    downloadCta: string;
  };
  common: {
    unsubscribe: string;
    preferences: string;
    privacy: string;
  };
}

// emails/i18n/en.ts
import type { EmailStrings } from "./types";
export const en: EmailStrings = {
  welcome: {
    preview: (name) => `Welcome, ${name}! Confirm your email to get started.`,
    heading: (name) => `Welcome to [Product], ${name}`,
    body: (days) => `You have ${days} days to explore everything -- no credit card required.`,
    cta: "Confirm Email Address",
    fallbackLink: "Button not working? Paste this link in your browser:",
  },
  // ... other templates
};

// emails/i18n/de.ts
import type { EmailStrings } from "./types";
export const de: EmailStrings = {
  welcome: {
    preview: (name) => `Willkommen, ${name}! Bestaetigen Sie Ihre E-Mail.`,
    heading: (name) => `Willkommen bei [Product], ${name}`,
    body: (days) => `Sie haben ${days} Tage Zeit, alles zu erkunden -- keine Kreditkarte noetig.`,
    cta: "E-Mail-Adresse bestaetigen",
    fallbackLink: "Button funktioniert nicht? Fuegen Sie diesen Link in Ihren Browser ein:",
  },
  // ... other templates
};
```

---

## Deliverability Checklist

### DNS Records (Required)

- [ ] **SPF**: `v=spf1 include:_spf.provider.com ~all` on sending domain
- [ ] **DKIM**: Provider-specific CNAME records configured
- [ ] **DMARC**: `v=DMARC1; p=quarantine; rua=mailto:dmarc@yourdomain.com`
- [ ] **Return-Path**: Matches sending domain (not provider default)

### Content Rules

- [ ] Sender uses own domain (not `@gmail.com`)
- [ ] Subject under 50 characters, no ALL CAPS, no spam triggers
- [ ] Text-to-image ratio: minimum 60% text
- [ ] Plain text version included alongside HTML
- [ ] Unsubscribe link in every email (CAN-SPAM, GDPR, one-click)
- [ ] Physical mailing address in footer (CAN-SPAM requirement)
- [ ] No URL shorteners (use full branded links)
- [ ] Single primary CTA per email
- [ ] All images have alt text
- [ ] HTML validates (no broken/unclosed tags)

### Infrastructure

- [ ] Separate sending domains for transactional vs marketing
- [ ] Warm up new sending domains gradually (start with 50/day, increase 2x weekly)
- [ ] Monitor bounce rates (<2% hard bounces)
- [ ] Process bounces and complaints automatically
- [ ] Test with Mail-Tester.com before production sends (target: 9+/10)

---

## Email Client Compatibility

### Known Quirks

| Client | Quirk | Workaround |
|--------|-------|-----------|
| Outlook (Windows) | No CSS grid/flexbox, ignores margin on images | Use `<table>` layout (React Email handles this) |
| Gmail | Strips `<head>` styles, limits CSS | Inline all styles (React Email handles this) |
| Apple Mail | Best support, renders dark mode well | Standard approach works |
| Yahoo Mail | Limited CSS support | Avoid advanced selectors |
| Outlook.com | Strips background images | Use background-color as fallback |

### Testing Matrix

Test every template on these clients before production:

| Priority | Client | Method |
|----------|--------|--------|
| Critical | Gmail (web) | Send test email |
| Critical | Apple Mail (iOS) | Send test email |
| Critical | Outlook (Windows, latest) | Litmus or Email on Acid |
| High | Outlook.com (web) | Send test email |
| High | Gmail (Android) | Send test email |
| Medium | Yahoo Mail | Litmus |
| Medium | Outlook (Mac) | Send test email |

---

## Dev Workflow

```bash
# Start preview server with hot reload
npx email dev --dir emails/templates --port 3001

# Export to static HTML (for testing with Litmus/Email on Acid)
npx email export --dir emails/templates --outDir emails/dist

# Send test email
npx tsx emails/lib/send-test.ts --template welcome --to test@example.com

# Validate HTML
npx email lint --dir emails/templates
```

---

## Common Pitfalls

| Pitfall | Consequence | Prevention |
|---------|-------------|------------|
| Using CSS grid/flexbox | Layout breaks in Outlook | Use `Row`/`Column` from React Email (renders to tables) |
| Container wider than 600px | Breaks on Gmail mobile | Max-width: 600px on container |
| Missing plain text version | Lower deliverability score | Always generate plain text with `render(template, { plainText: true })` |
| Same domain for transactional + marketing | Marketing complaints tank transactional delivery | Separate sending domains/subdomains |
| Skipping email warm-up | Emails go to spam | Start low, increase gradually over 2-4 weeks |
| Dark mode ignoring | Unreadable emails for 30%+ of users | Add `prefers-color-scheme: dark` media queries with `!important` |

---

## Related Skills

| Skill | Use When |
|-------|----------|
| **email-sequence** | Writing email copy and designing automation flows |
| **analytics-tracking** | Setting up email engagement tracking and attribution |
| **launch-strategy** | Coordinating email templates for product launches |

---

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| Email clipped in Gmail | HTML over 102KB | Run `render_size_analyzer.py`. Remove comments, minify, replace base64 images. |
| Layout broken in Outlook | CSS flexbox/grid used | Use table-based layout. Run `template_validator.py` for compatibility check. |
| Styles stripped in Gmail | Styles in `<head>` only | Inline all CSS. React Email handles this automatically. |
| Unreadable in dark mode | No dark mode CSS | Add `prefers-color-scheme: dark` media queries with `!important`. |
| Low deliverability score | Missing unsubscribe, heavy images | Run `spam_score_checker.py`. Add RFC 8058 one-click unsubscribe headers. |
| Images not loading | Blocked by email client defaults | Add descriptive alt text. Maintain 60%+ text-to-image ratio. |
| Template renders differently across clients | Unsupported CSS properties | Test on Gmail, Apple Mail, Outlook (Windows) before production sends. |

---

## Success Criteria

- Spam score of 9+/10 on mail-tester.com before production sends
- Template renders correctly on Gmail, Apple Mail, and Outlook (Windows)
- HTML under 80KB (well under Gmail's 102KB clip threshold)
- Text-to-image ratio above 60%
- Dark mode tested and readable for 30%+ of users
- All images have alt text and explicit width/height dimensions
- One-click unsubscribe (RFC 8058) implemented in all templates
- Separate sending domains for transactional vs. marketing email

---

## Scope & Limitations

**In Scope:** Email HTML/CSS template engineering, React Email and MJML components, multi-provider sending abstraction, i18n, dark mode, deliverability infrastructure, spam score optimization.

**Out of Scope:** Email copy/sequence writing (use email-sequence), marketing automation workflows, email list management, A/B test statistical analysis.

---

## Python Automation Tools

### 1. Spam Score Checker (`scripts/spam_score_checker.py`)
Analyzes email HTML for spam risk: text-to-image ratio, link density, spam words, unsubscribe presence, HTML structure.

```bash
python scripts/spam_score_checker.py template.html
python scripts/spam_score_checker.py template.html --json
```

### 2. Template Validator (`scripts/template_validator.py`)
Validates email templates for client compatibility (Outlook, Gmail), accessibility, responsive design, and inline styles.

```bash
python scripts/template_validator.py template.html
python scripts/template_validator.py template.html --json
```

### 3. Render Size Analyzer (`scripts/render_size_analyzer.py`)
Analyzes template file size, estimates render weight, and checks against Gmail's 102KB clip threshold with detailed breakdown.

```bash
python scripts/render_size_analyzer.py template.html
python scripts/render_size_analyzer.py --dir templates/ --json
```
