#!/usr/bin/env python3
"""SaaS Project Scaffolder — Generate production-ready SaaS project structure.

Creates a complete SaaS project directory tree with authentication, billing,
multi-tenancy, and dashboard boilerplate. Outputs the file tree and generates
key configuration/boilerplate files on disk.

Uses ONLY Python standard library. No LLM or API calls.
"""

import argparse
import json
import os
import sys
import textwrap
from datetime import datetime, timezone


# ---------------------------------------------------------------------------
# Templates for generated files
# ---------------------------------------------------------------------------

ENV_EXAMPLE = """\
# ─── App ───
NEXT_PUBLIC_APP_URL=http://localhost:3000
NEXTAUTH_SECRET=           # openssl rand -base64 32
NEXTAUTH_URL=http://localhost:3000

# ─── Database ───
DATABASE_URL=              # postgresql://user:pass@host/db?sslmode=require

# ─── OAuth Providers ───
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GITHUB_CLIENT_ID=
GITHUB_CLIENT_SECRET=

# ─── Stripe ───
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_PRO_MONTHLY_PRICE_ID=price_...
STRIPE_PRO_YEARLY_PRICE_ID=price_...

# ─── Email ───
RESEND_API_KEY=re_...
"""

PACKAGE_JSON_TMPL = """\
{{
  "name": "{name}",
  "version": "0.1.0",
  "private": true,
  "scripts": {{
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint",
    "db:push": "drizzle-kit push",
    "db:generate": "drizzle-kit generate",
    "db:seed": "tsx db/seed.ts"
  }},
  "dependencies": {{
    "next": "^15.0.0",
    "react": "^19.0.0",
    "react-dom": "^19.0.0",
    "@auth/drizzle-adapter": "^1.0.0",
    "next-auth": "^5.0.0",
    "drizzle-orm": "^0.35.0",
    "stripe": "^17.0.0",
    "zod": "^3.23.0",
    "@paralleldrive/cuid2": "^2.2.0"
  }},
  "devDependencies": {{
    "typescript": "^5.6.0",
    "drizzle-kit": "^0.27.0",
    "tailwindcss": "^3.4.0",
    "postcss": "^8.4.0",
    "autoprefixer": "^10.4.0",
    "@types/node": "^22.0.0",
    "@types/react": "^19.0.0",
    "tsx": "^4.0.0",
    "eslint": "^9.0.0",
    "prettier": "^3.3.0"
  }}
}}
"""

MIDDLEWARE_TS = """\
import { auth } from '@/lib/auth'
import { NextResponse } from 'next/server'

export default auth((req) => {
  const { pathname } = req.nextUrl
  const isAuthenticated = !!req.auth

  if (pathname.startsWith('/dashboard') || pathname.startsWith('/settings')) {
    if (!isAuthenticated) {
      return NextResponse.redirect(new URL('/login', req.url))
    }
  }

  if ((pathname === '/login' || pathname === '/register') && isAuthenticated) {
    return NextResponse.redirect(new URL('/dashboard', req.url))
  }

  return NextResponse.next()
})

export const config = {
  matcher: ['/dashboard/:path*', '/settings/:path*', '/login', '/register'],
}
"""

DB_SCHEMA_TS = """\
import { pgTable, text, timestamp, integer, boolean, uniqueIndex, index } from 'drizzle-orm/pg-core'
import { createId } from '@paralleldrive/cuid2'

export const workspaces = pgTable('workspaces', {
  id: text('id').primaryKey().$defaultFn(createId),
  name: text('name').notNull(),
  slug: text('slug').notNull(),
  plan: text('plan').notNull().default('free'),
  stripeCustomerId: text('stripe_customer_id').unique(),
  stripeSubscriptionId: text('stripe_subscription_id'),
  stripePriceId: text('stripe_price_id'),
  stripeCurrentPeriodEnd: timestamp('stripe_current_period_end'),
  createdAt: timestamp('created_at', { withTimezone: true }).defaultNow().notNull(),
  updatedAt: timestamp('updated_at', { withTimezone: true }).defaultNow().notNull(),
}, (t) => [
  uniqueIndex('workspaces_slug_idx').on(t.slug),
])

export const users = pgTable('users', {
  id: text('id').primaryKey().$defaultFn(createId),
  email: text('email').notNull().unique(),
  name: text('name'),
  avatarUrl: text('avatar_url'),
  emailVerified: timestamp('email_verified', { withTimezone: true }),
  createdAt: timestamp('created_at', { withTimezone: true }).defaultNow().notNull(),
})

export const workspaceMembers = pgTable('workspace_members', {
  id: text('id').primaryKey().$defaultFn(createId),
  workspaceId: text('workspace_id').notNull().references(() => workspaces.id, { onDelete: 'cascade' }),
  userId: text('user_id').notNull().references(() => users.id, { onDelete: 'cascade' }),
  role: text('role').notNull().default('member'),
  joinedAt: timestamp('joined_at', { withTimezone: true }).defaultNow().notNull(),
}, (t) => [
  uniqueIndex('workspace_members_unique').on(t.workspaceId, t.userId),
  index('workspace_members_workspace_idx').on(t.workspaceId),
])
"""


# ---------------------------------------------------------------------------
# Directory tree definition
# ---------------------------------------------------------------------------

def build_tree(name, auth_provider, db_provider, payment_provider, tenancy, features):
    """Return a nested dict representing the SaaS project tree."""
    tree = {
        "app": {
            "(auth)": {
                "login": {"page.tsx": None},
                "register": {"page.tsx": None},
                "forgot-password": {"page.tsx": None},
                "layout.tsx": None,
            },
            "(dashboard)": {
                "dashboard": {"page.tsx": None},
                "settings": {
                    "page.tsx": None,
                    "billing": {"page.tsx": None},
                    "team": {"page.tsx": None},
                },
                "layout.tsx": None,
            },
            "(marketing)": {
                "page.tsx": None,
                "pricing": {"page.tsx": None},
                "layout.tsx": None,
            },
            "api": {
                "auth": {"[...nextauth]": {"route.ts": None}},
                "webhooks": {"stripe": {"route.ts": None}},
                "billing": {
                    "checkout": {"route.ts": None},
                    "portal": {"route.ts": None},
                },
                "health": {"route.ts": None},
            },
            "layout.tsx": None,
            "not-found.tsx": None,
        },
        "components": {
            "ui": {},
            "auth": {"login-form.tsx": None, "register-form.tsx": None},
            "dashboard": {"sidebar.tsx": None, "header.tsx": None, "stats-card.tsx": None},
            "marketing": {"hero.tsx": None, "features.tsx": None, "pricing-card.tsx": None, "footer.tsx": None},
            "billing": {"plan-card.tsx": None, "usage-meter.tsx": None},
        },
        "lib": {
            "auth.ts": None,
            "db.ts": None,
            "stripe.ts": None,
            "validations.ts": None,
            "utils.ts": None,
        },
        "db": {
            "schema.ts": None,
            "migrations": {},
            "seed.ts": None,
        },
        "hooks": {"use-subscription.ts": None, "use-current-user.ts": None},
        "types": {"index.ts": None},
        "middleware.ts": None,
        ".env.example": None,
        "drizzle.config.ts": None,
        "tailwind.config.ts": None,
        "next.config.ts": None,
        "package.json": None,
        "tsconfig.json": None,
        "README.md": None,
    }

    # Add feature-specific directories
    for feat in features:
        slug = feat.strip().lower().replace(" ", "-")
        if slug:
            tree["app"]["(dashboard)"][slug] = {"page.tsx": None}

    if tenancy == "none":
        tree["app"]["(dashboard)"]["settings"].pop("team", None)

    if payment_provider == "none":
        tree["app"]["api"].pop("billing", None)
        tree["app"]["api"]["webhooks"].pop("stripe", None)
        tree["app"]["(dashboard)"]["settings"].pop("billing", None)
        tree["components"].pop("billing", None)
        tree["lib"].pop("stripe.ts", None)
        tree["hooks"].pop("use-subscription.ts", None)

    return tree


def render_tree(node, prefix="", is_last=True, name=""):
    """Render a nested dict as an ASCII tree string."""
    lines = []
    if name:
        connector = "└── " if is_last else "├── "
        lines.append(f"{prefix}{connector}{name}{'/' if isinstance(node, dict) else ''}")
        prefix += "    " if is_last else "│   "

    if isinstance(node, dict):
        entries = sorted(node.keys())
        for i, key in enumerate(entries):
            last = i == len(entries) - 1
            lines.extend(render_tree(node[key], prefix, last, key))
    return lines


# ---------------------------------------------------------------------------
# File generation on disk
# ---------------------------------------------------------------------------

FILE_MAP = {
    ".env.example": ENV_EXAMPLE,
    "middleware.ts": MIDDLEWARE_TS,
    "db/schema.ts": DB_SCHEMA_TS,
}


def write_project(output_dir, tree, project_name):
    """Write the project skeleton to disk."""
    files_written = []

    def _walk(node, current_path):
        if isinstance(node, dict):
            os.makedirs(current_path, exist_ok=True)
            for child_name, child_node in node.items():
                _walk(child_node, os.path.join(current_path, child_name))
        else:
            rel = os.path.relpath(current_path, output_dir)
            content = FILE_MAP.get(rel, "")
            if rel == "package.json":
                content = PACKAGE_JSON_TMPL.format(name=project_name)
            os.makedirs(os.path.dirname(current_path), exist_ok=True)
            with open(current_path, "w") as f:
                f.write(content)
            files_written.append(rel)

    _walk(tree, output_dir)
    return files_written


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Generate a production-ready SaaS project structure with auth, billing, and multi-tenancy.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            examples:
              %(prog)s --name my-saas --output ./my-saas
              %(prog)s --name acme --auth clerk --db supabase --payments none --json
              %(prog)s --name startup --features "analytics,reports,integrations"
        """),
    )

    parser.add_argument("--name", required=True, help="Project name (used for directory and package.json)")
    parser.add_argument("--output", default=None, help="Output directory (default: ./<name>)")
    parser.add_argument("--auth", choices=["nextauth", "clerk", "supabase"], default="nextauth",
                        help="Authentication provider (default: nextauth)")
    parser.add_argument("--db", choices=["neondb", "supabase", "planetscale", "turso"], default="neondb",
                        help="Database provider (default: neondb)")
    parser.add_argument("--payments", choices=["stripe", "lemonsqueezy", "none"], default="stripe",
                        help="Payment provider (default: stripe)")
    parser.add_argument("--tenancy", choices=["workspace", "organization", "none"], default="workspace",
                        help="Multi-tenancy model (default: workspace)")
    parser.add_argument("--features", default="", help="Comma-separated list of additional feature pages")
    parser.add_argument("--dry-run", action="store_true", help="Show tree without writing files to disk")
    parser.add_argument("--json", action="store_true", dest="json_output", help="Output results as JSON")

    args = parser.parse_args()

    output_dir = args.output or os.path.join(".", args.name)
    features = [f.strip() for f in args.features.split(",") if f.strip()]

    tree = build_tree(args.name, args.auth, args.db, args.payments, args.tenancy, features)

    tree_lines = render_tree(tree, name=args.name)
    tree_str = "\n".join(tree_lines)

    files_written = []
    if not args.dry_run:
        files_written = write_project(output_dir, tree, args.name)

    # Build result
    result = {
        "project_name": args.name,
        "output_directory": os.path.abspath(output_dir),
        "auth_provider": args.auth,
        "database_provider": args.db,
        "payment_provider": args.payments,
        "tenancy_model": args.tenancy,
        "extra_features": features,
        "dry_run": args.dry_run,
        "files_written": len(files_written),
        "file_list": files_written,
        "tree": tree_str,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }

    if args.json_output:
        print(json.dumps(result, indent=2))
    else:
        print(f"SaaS Scaffolder — Project: {args.name}")
        print("=" * 60)
        print(f"  Auth:       {args.auth}")
        print(f"  Database:   {args.db}")
        print(f"  Payments:   {args.payments}")
        print(f"  Tenancy:    {args.tenancy}")
        if features:
            print(f"  Features:   {', '.join(features)}")
        print(f"  Output:     {os.path.abspath(output_dir)}")
        print(f"  Dry run:    {args.dry_run}")
        print()
        print("Project Tree:")
        print("-" * 60)
        print(tree_str)
        print("-" * 60)
        if not args.dry_run:
            print(f"\n{len(files_written)} files written to {os.path.abspath(output_dir)}")
            key_files = [f for f in files_written if f in (".env.example", "middleware.ts", "db/schema.ts", "package.json")]
            if key_files:
                print("\nKey files with boilerplate content:")
                for kf in key_files:
                    print(f"  - {kf}")
        else:
            print("\n(dry-run mode — no files written)")
        print(f"\nGenerated at {result['generated_at']}")


if __name__ == "__main__":
    main()
