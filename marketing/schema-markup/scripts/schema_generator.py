#!/usr/bin/env python3
"""
Schema JSON-LD Generator

Generates copy-paste-ready JSON-LD structured data for common page types.
Supports Article, FAQPage, HowTo, Product, Organization, Person,
LocalBusiness, BreadcrumbList, Event, and more.

Usage:
    python schema_generator.py --type Article --title "My Post" --author "Jane"
    python schema_generator.py --type FAQPage --questions "What is X?|Answer" "How does Y?|Answer"
    python schema_generator.py --type Organization --name "Acme Inc" --url "https://acme.com" --json
    python schema_generator.py --list-types
"""

import argparse
import json
import sys
from datetime import date


SUPPORTED_TYPES = {
    "Article": "Blog posts, news articles, guides",
    "FAQPage": "FAQ sections with Q&A pairs",
    "HowTo": "Step-by-step tutorials and guides",
    "Product": "Product pages with pricing",
    "Organization": "Company/brand homepage",
    "Person": "Author or team member pages",
    "LocalBusiness": "Local business with physical location",
    "BreadcrumbList": "Navigation breadcrumb trail",
    "Event": "Events with dates and locations",
    "WebSite": "Site-level with search action",
    "SoftwareApplication": "Software or app listings",
    "VideoObject": "Video content pages",
    "Course": "Online courses and training",
}


def generate_article(args):
    """Generate Article schema."""
    today = date.today().isoformat()
    return {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": args.get("title", "[Article Title]"),
        "description": args.get("description", "[Article description in 150-160 chars]"),
        "author": {
            "@type": "Person",
            "name": args.get("author", "[Author Name]"),
            "url": args.get("author_url", "[https://example.com/authors/name]"),
        },
        "datePublished": args.get("date", today),
        "dateModified": args.get("date", today),
        "image": args.get("image", "[https://example.com/images/article-hero.jpg]"),
        "publisher": {
            "@type": "Organization",
            "name": args.get("publisher", "[Publisher Name]"),
            "logo": {
                "@type": "ImageObject",
                "url": args.get("logo", "[https://example.com/logo.png]"),
            },
        },
    }


def generate_faq(args):
    """Generate FAQPage schema."""
    questions = args.get("questions", [])
    if not questions:
        questions = [
            {"question": "[What is X?]", "answer": "[Direct answer to the question]"},
            {"question": "[How does Y work?]", "answer": "[Step-by-step explanation]"},
        ]

    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": q["question"],
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": q["answer"],
                },
            }
            for q in questions
        ],
    }


def generate_howto(args):
    """Generate HowTo schema."""
    steps = args.get("steps", [])
    if not steps:
        steps = [
            {"name": "[Step 1 Title]", "text": "[Step 1 description]"},
            {"name": "[Step 2 Title]", "text": "[Step 2 description]"},
            {"name": "[Step 3 Title]", "text": "[Step 3 description]"},
        ]

    return {
        "@context": "https://schema.org",
        "@type": "HowTo",
        "name": args.get("title", "[How to Do Something]"),
        "description": args.get("description", "[Brief description of the process]"),
        "totalTime": args.get("time", "PT30M"),
        "step": [
            {
                "@type": "HowToStep",
                "name": s["name"],
                "text": s["text"],
            }
            for s in steps
        ],
    }


def generate_product(args):
    """Generate Product schema."""
    return {
        "@context": "https://schema.org",
        "@type": "Product",
        "name": args.get("title", "[Product Name]"),
        "description": args.get("description", "[Product description]"),
        "image": args.get("image", "[https://example.com/product.jpg]"),
        "brand": {
            "@type": "Brand",
            "name": args.get("brand", "[Brand Name]"),
        },
        "offers": {
            "@type": "Offer",
            "price": args.get("price", "0.00"),
            "priceCurrency": args.get("currency", "USD"),
            "availability": "https://schema.org/InStock",
            "url": args.get("url", "[https://example.com/product]"),
        },
        "aggregateRating": {
            "@type": "AggregateRating",
            "ratingValue": args.get("rating", "4.5"),
            "reviewCount": args.get("reviews", "100"),
        },
    }


def generate_organization(args):
    """Generate Organization schema."""
    return {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": args.get("name", "[Company Name]"),
        "url": args.get("url", "[https://example.com]"),
        "logo": args.get("logo", "[https://example.com/logo.png]"),
        "description": args.get("description", "[Company description]"),
        "sameAs": [
            "[https://www.linkedin.com/company/name]",
            "[https://twitter.com/name]",
            "[https://www.wikidata.org/wiki/QXXXXXXX]",
        ],
        "contactPoint": {
            "@type": "ContactPoint",
            "contactType": "customer service",
            "email": args.get("email", "[support@example.com]"),
        },
    }


def generate_person(args):
    """Generate Person schema."""
    return {
        "@context": "https://schema.org",
        "@type": "Person",
        "name": args.get("author", "[Person Name]"),
        "url": args.get("url", "[https://example.com/about]"),
        "jobTitle": args.get("job_title", "[Job Title]"),
        "worksFor": {
            "@type": "Organization",
            "name": args.get("company", "[Company Name]"),
        },
        "sameAs": [
            "[https://linkedin.com/in/name]",
            "[https://twitter.com/name]",
        ],
    }


def generate_local_business(args):
    """Generate LocalBusiness schema."""
    return {
        "@context": "https://schema.org",
        "@type": "LocalBusiness",
        "name": args.get("name", "[Business Name]"),
        "url": args.get("url", "[https://example.com]"),
        "telephone": args.get("phone", "[+1-555-555-5555]"),
        "image": args.get("image", "[https://example.com/storefront.jpg]"),
        "address": {
            "@type": "PostalAddress",
            "streetAddress": "[123 Main St]",
            "addressLocality": "[City]",
            "addressRegion": "[State]",
            "postalCode": "[12345]",
            "addressCountry": "US",
        },
        "geo": {
            "@type": "GeoCoordinates",
            "latitude": "[40.7128]",
            "longitude": "[-74.0060]",
        },
        "openingHoursSpecification": [
            {
                "@type": "OpeningHoursSpecification",
                "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
                "opens": "09:00",
                "closes": "17:00",
            }
        ],
    }


def generate_breadcrumb(args):
    """Generate BreadcrumbList schema."""
    items = args.get("breadcrumbs", [])
    if not items:
        items = [
            {"name": "Home", "url": "https://example.com"},
            {"name": "[Category]", "url": "https://example.com/category"},
            {"name": "[Current Page]", "url": "https://example.com/category/page"},
        ]

    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": i + 1,
                "name": item["name"],
                "item": item["url"],
            }
            for i, item in enumerate(items)
        ],
    }


def generate_event(args):
    """Generate Event schema."""
    return {
        "@context": "https://schema.org",
        "@type": "Event",
        "name": args.get("title", "[Event Name]"),
        "startDate": args.get("date", "2026-06-15T09:00:00-05:00"),
        "endDate": args.get("end_date", "2026-06-15T17:00:00-05:00"),
        "location": {
            "@type": "Place",
            "name": "[Venue Name]",
            "address": {
                "@type": "PostalAddress",
                "addressLocality": "[City]",
                "addressRegion": "[State]",
                "addressCountry": "US",
            },
        },
        "description": args.get("description", "[Event description]"),
        "organizer": {
            "@type": "Organization",
            "name": args.get("organizer", "[Organizer Name]"),
            "url": args.get("url", "[https://example.com]"),
        },
    }


def generate_website(args):
    """Generate WebSite schema with search action."""
    return {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": args.get("name", "[Site Name]"),
        "url": args.get("url", "[https://example.com]"),
        "potentialAction": {
            "@type": "SearchAction",
            "target": {
                "@type": "EntryPoint",
                "urlTemplate": args.get("search_url", "[https://example.com/search?q={search_term_string}]"),
            },
            "query-input": "required name=search_term_string",
        },
    }


GENERATORS = {
    "Article": generate_article,
    "FAQPage": generate_faq,
    "HowTo": generate_howto,
    "Product": generate_product,
    "Organization": generate_organization,
    "Person": generate_person,
    "LocalBusiness": generate_local_business,
    "BreadcrumbList": generate_breadcrumb,
    "Event": generate_event,
    "WebSite": generate_website,
}


def main():
    parser = argparse.ArgumentParser(
        description="Generate JSON-LD structured data templates"
    )
    parser.add_argument("--type", help="Schema type to generate")
    parser.add_argument("--list-types", action="store_true", help="List all supported types")
    parser.add_argument("--title", help="Title/headline")
    parser.add_argument("--name", help="Name (organization, business)")
    parser.add_argument("--author", help="Author name")
    parser.add_argument("--author-url", help="Author URL")
    parser.add_argument("--description", help="Description")
    parser.add_argument("--url", help="Page or site URL")
    parser.add_argument("--image", help="Image URL")
    parser.add_argument("--date", help="Date (ISO 8601)")
    parser.add_argument("--price", help="Product price")
    parser.add_argument("--questions", nargs="+", help="FAQ questions as 'Question|Answer' pairs")
    parser.add_argument("--steps", nargs="+", help="HowTo steps as 'Title|Description' pairs")
    parser.add_argument("--json", action="store_true", help="Raw JSON output (no wrapping)")
    args = parser.parse_args()

    if args.list_types:
        print(f"\n  Supported Schema Types:")
        print(f"  {'Type':<25} Description")
        print(f"  {'-'*25} {'-'*40}")
        for t, desc in SUPPORTED_TYPES.items():
            print(f"  {t:<25} {desc}")
        print()
        return

    if not args.type:
        parser.error("--type is required (or use --list-types)")

    if args.type not in GENERATORS:
        print(f"Error: Unsupported type '{args.type}'. Use --list-types to see options.", file=sys.stderr)
        sys.exit(1)

    # Build params
    params = {
        "title": args.title,
        "name": args.name,
        "author": args.author,
        "author_url": args.author_url,
        "description": args.description,
        "url": args.url,
        "image": args.image,
        "date": args.date,
        "price": args.price,
    }
    # Clean None values
    params = {k: v for k, v in params.items() if v is not None}

    # Parse FAQ questions
    if args.questions:
        params["questions"] = []
        for q in args.questions:
            parts = q.split("|", 1)
            if len(parts) == 2:
                params["questions"].append({"question": parts[0], "answer": parts[1]})

    # Parse HowTo steps
    if args.steps:
        params["steps"] = []
        for s in args.steps:
            parts = s.split("|", 1)
            if len(parts) == 2:
                params["steps"].append({"name": parts[0], "text": parts[1]})

    schema = GENERATORS[args.type](params)

    if args.json:
        print(json.dumps(schema, indent=2))
    else:
        print(f"\n<!-- {args.type} Schema - Copy into <head> -->")
        print('<script type="application/ld+json">')
        print(json.dumps(schema, indent=2))
        print("</script>")
        print()
        print("  Replace all [bracketed] placeholder values with real content.")
        print(f"  Validate at: https://search.google.com/test/rich-results")
        print()


if __name__ == "__main__":
    main()
