---
description: Run an SEO audit on web content and HTML files.
---

Perform a technical SEO audit:

1. **Scan HTML files** in the project for SEO elements.
2. **Meta tags check:**
   - `<title>` exists and is 50-60 characters
   - `<meta name="description">` exists and is 150-160 characters
   - `<meta name="viewport">` set for mobile
   - Open Graph tags (og:title, og:description, og:image)
   - Twitter Card tags
3. **Heading structure:**
   - Exactly one `<h1>` per page
   - Headings in correct hierarchy (no skipping levels)
   - Headings contain target keywords
4. **Images:**
   - All `<img>` tags have `alt` attributes
   - Alt text is descriptive (not "image1.png")
   - Images have width/height attributes (CLS prevention)
5. **Links:**
   - Internal links use relative paths
   - No broken links (href="#" or empty)
   - External links have `rel="noopener noreferrer"`
   - Anchor text is descriptive (not "click here")
6. **Technical:**
   - Canonical URL (`<link rel="canonical">`) present
   - Structured data (JSON-LD) present and valid
   - robots.txt exists
   - sitemap.xml exists
   - Page load indicators (large images, unminified CSS/JS)
7. **Output** findings by severity (critical, warning, info) with specific fix instructions and line numbers.
