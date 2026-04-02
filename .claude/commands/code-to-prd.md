---
description: Reverse-engineer a Product Requirements Document from existing code.
---

Analyze the codebase and generate a PRD:

1. **Map the codebase** — identify entry points, routes, controllers, models, services, and UI components.
2. **Extract features** — list all user-facing features discovered from routes, pages, API endpoints, and UI flows.
3. **Identify data models** — extract entities, relationships, and key fields from schemas/models.
4. **Trace user flows** — map the primary user journeys through the code (signup, core actions, settings).
5. **Document API surface** — list all endpoints with methods, parameters, and response shapes.
6. **Generate the PRD** with these sections:
   - **Product Overview**: what this product does, inferred from code
   - **User Personas**: inferred from auth roles, permissions, UI patterns
   - **Core Features**: each feature with description, current behavior, and data model
   - **User Stories**: "As a [role], I want [action], so that [outcome]" for each feature
   - **Technical Requirements**: stack, dependencies, infrastructure needs
   - **API Reference**: endpoint summary table
   - **Acceptance Criteria**: testable criteria for each feature based on existing behavior
   - **Known Gaps**: missing tests, incomplete features, TODO/FIXME items found
7. Output as a structured markdown document.
