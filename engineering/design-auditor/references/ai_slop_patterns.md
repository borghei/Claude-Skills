# AI Slop Patterns Reference

Comprehensive catalog of AI-generated UI patterns. Use this reference to distinguish intentional design from generic AI output and to guide remediation.

## What Is "AI Slop"?

AI slop refers to UI/UX patterns produced by AI tools (Midjourney, Figma AI, ChatGPT-generated code, v0, etc.) that are technically functional but lack intentionality, brand specificity, and design thinking. These patterns emerge because AI models converge on the most common training examples, producing statistically average designs.

AI slop is not inherently bad markup. It is design that lacks a reason for its specific choices.

## Visual Patterns

### Generic Hero Sections
**Pattern:** Full-width section with centered heading, subtitle paragraph, and one or two CTA buttons over a gradient or stock image background.

**Detection signals:**
- `text-align: center` on a full-width container
- Large heading (32-64px) followed by a lighter paragraph followed by button(s)
- Background using `linear-gradient` or full-bleed image with overlay
- Content max-width constrained to 600-800px within full-width section

**Why it is slop:** Every AI landing page generator produces this exact layout. It communicates nothing specific about the product.

**Remediation:** Use asymmetric layouts, product screenshots, interactive demos, or video. Place the hero content where it creates tension with supporting visuals.

### Stock Gradient Backgrounds
**Pattern:** Linear gradients using trending color combinations, especially purple-to-blue, pink-to-orange, or teal-to-green.

**Detection signals:**
- `linear-gradient(to right, #667eea, #764ba2)` and similar
- Gradient used as primary background rather than accent
- Same gradient repeated across multiple sections

**Remediation:** Derive gradients from brand colors. Use them sparingly as accents, not as primary backgrounds. Consider solid colors or textures.

### 3-Column Feature Grids
**Pattern:** Exactly three columns, each containing an icon, a heading, and a short paragraph, with equal width and spacing.

**Detection signals:**
- `grid-template-columns: repeat(3, 1fr)` or equivalent flex layout
- Three nearly identical blocks with icon + h3 + p structure
- Icons from mixed sources or generic placeholder icons

**Remediation:** Vary the number of features shown. Use 2, 4, or an asymmetric layout. Add images, screenshots, or interactive elements. Highlight one feature as primary.

### Shadow and Blur Overuse
**Pattern:** Box-shadow applied to nearly every card, container, and interactive element. Backdrop blur used on multiple overlapping layers.

**Detection signals:**
- `box-shadow` on more than 50% of container elements
- `backdrop-filter: blur()` on more than 3 elements
- Shadows with identical values across different component types

**Remediation:** Establish an elevation system with 2-3 shadow levels. Reserve blur for specific interactions (modals, overlays). Let most elements sit flat.

### Rounded Everything
**Pattern:** Large border-radius values (16px+) on nearly all elements, creating an overly soft, toy-like appearance.

**Detection signals:**
- `border-radius` values >= 16px on more than 60% of elements
- Cards, buttons, inputs, images all sharing the same large radius
- No variation in radius values across element types

**Remediation:** Create a radius scale (e.g., 2px, 4px, 8px, 16px) and apply intentionally. Buttons may be fully rounded while cards use subtle rounding. Variation creates visual interest.

### Meaningless Illustrations
**Pattern:** Abstract SVG decorations (blobs, waves, geometric shapes) placed in backgrounds or between sections with no semantic connection to content.

**Detection signals:**
- SVG shapes with no alt text or ARIA label
- Decorative elements that could be removed without information loss
- Abstract shapes that do not relate to the product domain

**Remediation:** Replace with product-specific imagery, data visualizations, or functional illustrations that communicate something concrete.

### Inconsistent Icon Styles
**Pattern:** Icons mixed from multiple libraries or styles (some outlined, some filled, different stroke widths, different visual metaphors).

**Detection signals:**
- Multiple icon library class prefixes (fa-, bi-, material-, etc.)
- SVG icons with varying stroke-width values
- Mix of outlined and filled icons in the same context

**Remediation:** Standardize on one icon library and one style (outlined OR filled, consistent weight). Audit every icon for metaphor accuracy.

## Copy Patterns

### Vague Call-to-Action Text
**Pattern:** Generic button labels that do not specify what will happen when clicked.

**Common offenders:** "Get Started", "Learn More", "Try It Free", "Sign Up Now", "Join Today", "Book a Demo", "Contact Us"

**Why it is slop:** These phrases appear on literally millions of AI-generated pages. They communicate no specific value.

**Remediation:** Describe the specific action and outcome: "Start analyzing your data", "See pricing for teams", "Watch the 2-minute demo", "Talk to an engineer".

### Buzzword Density
**Pattern:** High concentration of marketing buzzwords without specific claims or evidence.

**Common buzzwords:** seamless, powerful, revolutionary, next-gen, cutting-edge, innovative, transform, unlock, leverage, supercharge, streamline, empower, game-changing, world-class, state-of-the-art, frictionless, robust, scalable, holistic

**Detection:** Count buzzwords per 100 words of visible text. Above 2% density is suspicious.

**Remediation:** Replace each buzzword with a specific, measurable claim. "Powerful analytics" becomes "Query 10M rows in under 2 seconds."

### Generic Testimonials
**Pattern:** Testimonial quotes with vague praise and no specific product references.

**Signals:**
- "This product changed everything for our team" (no specifics)
- "Amazing experience, would recommend to anyone" (no context)
- Testimonials with stock photo avatars
- No company names, job titles, or verifiable identities

**Remediation:** Use real quotes that reference specific features, metrics, or outcomes. Include real photos, company logos, and verifiable identities.

### Lorem Ipsum Residue
**Pattern:** Placeholder text fragments or suspiciously uniform paragraph lengths suggesting content was never finalized.

**Signals:** Latin placeholder fragments, paragraphs that are all exactly the same length, content that reads as plausible but contains no specific information.

## Structural Patterns

### Predictable Section Ordering
**Pattern:** Sections arranged in the exact order that every AI landing page uses.

**Standard AI order:** Hero > Features (3-column) > Social Proof/Testimonials > Pricing (3-tier) > CTA Banner > Footer

**Why it is slop:** This ordering is the statistical mode of training data. Real products should order sections based on user needs and conversion data.

**Remediation:** Lead with the user's problem. Show the solution (product). Prove it works (specific evidence). Then convert. The order should follow your narrative, not a template.

### Cookie-Cutter Pricing Tables
**Pattern:** Exactly three pricing tiers with the middle one highlighted as "Most Popular" or "Recommended."

**Signals:**
- Three equal-width columns
- Checkmark lists comparing features
- Middle tier visually elevated or highlighted
- "Popular" or "Best Value" badge on middle tier

**Remediation:** Consider alternative pricing presentations: slider-based pricing, calculator, comparison table, toggle between annual/monthly. If using tiers, differentiate visually beyond just highlighting the middle one.

### Predictable Footer Layout
**Pattern:** 4-column footer with Company/Product/Resources/Legal columns, social icons, and newsletter signup.

**Signals:** Exactly 4 columns with standard category names, identical to hundreds of thousands of other sites.

**Remediation:** Design the footer based on what your users actually need to find. Add product-specific elements (status page link, API docs, changelog).

## Distinguishing AI Slop from Intentional Minimalism

Not every simple design is slop. Genuine minimalism and AI slop look similar but differ in intentionality:

| Aspect | Intentional Minimalism | AI Slop |
|--------|----------------------|---------|
| **Spacing** | Deliberate, consistent scale | Close to consistent but with random variations |
| **Color** | Limited, purposeful palette from brand | Trending colors unrelated to brand |
| **Content** | Concise, specific, high-information density per word | Verbose, generic, low information per word |
| **Layout** | Serves content hierarchy | Follows template structure |
| **Components** | Custom or carefully selected for the use case | Generic components assembled without modification |
| **Empty space** | Creates rhythm and focus | Fills space because there is nothing specific to show |

## Remediation Strategies

### Quick Wins (1-2 hours)
1. Replace generic CTAs with specific action text
2. Swap stock gradients for brand colors
3. Standardize icon set
4. Write specific testimonial quotes
5. Add real product screenshots to hero

### Medium Effort (1-2 days)
1. Redesign hero with asymmetric layout
2. Create custom feature presentation (not 3-column grid)
3. Build component-specific illustrations
4. Establish and apply consistent spacing scale
5. Create intentional elevation/shadow system

### Strategic Changes (1+ weeks)
1. Reorder page sections based on user research
2. Design custom pricing experience
3. Create brand-specific illustration system
4. Build interactive product demos for hero
5. Develop a unique visual language that cannot be replicated by templates
