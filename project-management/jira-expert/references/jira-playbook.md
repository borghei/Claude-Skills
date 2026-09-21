# Jira Expert Playbook

> Read this when you need the full detail behind the SKILL.md map — competencies, workflows, JQL operators/functions, inline JQL examples, advanced features, reporting templates, decision/handoff protocols, best practices, troubleshooting, and success criteria.

## Core Competencies (detail)

**Project Configuration**
- Create and configure Jira projects (Scrum, Kanban, custom)
- Design and implement custom workflows
- Configure issue types, fields, and screens
- Set up project permissions and security schemes

**JQL Mastery**
- Write advanced JQL queries for any use case
- Create complex filters with multiple conditions
- Optimize query performance
- Build saved filters for team use

**Automation & Integration**
- Design Jira automation rules
- Configure webhooks and integrations
- Set up email notifications
- Integrate with external tools (Confluence, Slack, etc.)

**Reporting & Dashboards**
- Create custom dashboards with gadgets
- Build reports for sprint metrics, velocity, burndown
- Configure portfolio-level reporting
- Export data for executive reporting

## Workflows

### Project Creation
1. Determine project type (Scrum, Kanban, Bug Tracking, etc.)
2. Create project with appropriate template
3. Configure project settings:
   - Name, key, description
   - Project lead and default assignee
   - Notification scheme
   - Permission scheme
4. Set up issue types and workflows
5. Configure custom fields if needed
6. Create initial board/backlog view
7. **HANDOFF TO**: Scrum Master for team onboarding

### Workflow Design
1. Map out process states (To Do → In Progress → Done)
2. Define transitions and conditions
3. Add validators, post-functions, and conditions
4. Configure workflow scheme
5. Associate workflow with project
6. Test workflow with sample issues
7. **USE**: References for complex workflow patterns

### JQL Query Building
**Basic Structure**: `field operator value`

**Common Operators**:
- `=, !=` : equals, not equals
- `~, !~` : contains, not contains
- `>, <, >=, <=` : comparison
- `in, not in` : list membership
- `is empty, is not empty`
- `was, was in, was not`
- `changed`

**Powerful JQL Examples**:

Find overdue issues:
```jql
dueDate < now() AND status != Done
```

Sprint burndown issues:
```jql
sprint = 23 AND status changed TO "Done" DURING (startOfSprint(), endOfSprint())
```

Find stale issues:
```jql
updated < -30d AND status != Done
```

Cross-project epic tracking:
```jql
"Epic Link" = PROJ-123 ORDER BY rank
```

Velocity calculation:
```jql
sprint in closedSprints() AND resolution = Done
```

Team capacity:
```jql
assignee in (user1, user2) AND sprint in openSprints()
```

### Dashboard Creation
1. Create new dashboard (personal or shared)
2. Add relevant gadgets:
   - Filter Results (JQL-based)
   - Sprint Burndown
   - Velocity Chart
   - Created vs Resolved
   - Pie Chart (status distribution)
3. Arrange layout for readability
4. Configure automatic refresh
5. Share with appropriate teams
6. **HANDOFF TO**: Senior PM or Scrum Master for use

### Automation Rules
1. Define trigger (issue created, field changed, scheduled)
2. Add conditions (if applicable)
3. Define actions:
   - Update field
   - Send notification
   - Create subtask
   - Transition issue
   - Post comment
4. Test automation with sample data
5. Enable and monitor
6. **USE**: References for complex automation patterns

## Advanced Features

### Custom Fields
**When to Create**:
- Track data not in standard fields
- Capture process-specific information
- Enable advanced reporting

**Field Types**:
- Text: Short text, paragraph
- Numeric: Number, decimal
- Date: Date picker, date-time
- Select: Single select, multi-select, cascading
- User: User picker, multi-user picker

**Configuration**:
1. Create custom field
2. Configure field context (which projects/issue types)
3. Add to appropriate screens
4. Update search templates if needed

### Issue Linking
**Link Types**:
- Blocks / Is blocked by
- Relates to
- Duplicates / Is duplicated by
- Clones / Is cloned by
- Epic-Story relationship

**Best Practices**:
- Use Epic linking for feature grouping
- Use blocking links to show dependencies
- Document link reasons in comments

### Permissions & Security

**Permission Schemes**:
- Browse Projects
- Create/Edit/Delete Issues
- Administer Projects
- Manage Sprints

**Security Levels**:
- Define confidential issue visibility
- Control access to sensitive data
- Audit security changes

### Bulk Operations
**Bulk Change**:
1. Use JQL to find target issues
2. Select bulk change operation
3. Choose fields to update
4. Preview changes
5. Execute and confirm
6. Monitor background task

**Bulk Transitions**:
- Move multiple issues through workflow
- Useful for sprint cleanup
- Requires appropriate permissions

## JQL Functions Reference

**Date Functions**:
- `startOfDay()`, `endOfDay()`
- `startOfWeek()`, `endOfWeek()`
- `startOfMonth()`, `endOfMonth()`
- `startOfYear()`, `endOfYear()`

**Sprint Functions**:
- `openSprints()`
- `closedSprints()`
- `futureSprints()`

**User Functions**:
- `currentUser()`
- `membersOf("group")`

**Advanced Functions**:
- `issueHistory()`
- `linkedIssues()`
- `issuesWithFixVersions()`

## Reporting Templates

**Sprint Report**:
```jql
project = PROJ AND sprint = 23
```

**Team Velocity**:
```jql
assignee in (team) AND sprint in closedSprints() AND resolution = Done
```

**Bug Trend**:
```jql
type = Bug AND created >= -30d
```

**Blocker Analysis**:
```jql
priority = Blocker AND status != Done
```

## Decision Framework

**When to Escalate to Atlassian Admin**:
- Need new project permission scheme
- Require custom workflow scheme across org
- User provisioning or deprovisioning
- License or billing questions
- System-wide configuration changes

**When to Collaborate with Scrum Master**:
- Sprint board configuration
- Backlog prioritization views
- Team-specific filters
- Sprint reporting needs

**When to Collaborate with Senior PM**:
- Portfolio-level reporting
- Cross-project dashboards
- Executive visibility needs
- Multi-project dependencies

## Handoff Protocols

**FROM Senior PM**:
- Project structure requirements
- Workflow and field needs
- Reporting requirements
- Integration needs

**TO Senior PM**:
- Cross-project metrics
- Issue trends and patterns
- Workflow bottlenecks
- Data quality insights

**FROM Scrum Master**:
- Sprint board configuration requests
- Workflow optimization needs
- Backlog filtering requirements
- Velocity tracking setup

**TO Scrum Master**:
- Configured sprint boards
- Velocity reports
- Burndown charts
- Team capacity views

## Best Practices

**Data Quality**:
- Enforce required fields
- Use field validation
- Regular cleanup of stale issues
- Consistent naming conventions

**Performance**:
- Optimize JQL queries
- Limit dashboard gadgets
- Use saved filters
- Archive old projects

**Governance**:
- Document workflow rationale
- Version control for schemes
- Change management for major updates
- Regular permission audits

## Atlassian MCP Integration

**Primary Tool**: Atlassian Rovo MCP Server (Atlassian's official remote MCP server for Cloud; endpoint `https://mcp.atlassian.com/v2/mcp`, OAuth 2.1 or API token). Tool names below are from Atlassian's [supported tools](https://support.atlassian.com/atlassian-rovo-mcp-server/docs/supported-tools/) list as of September 2026 -- re-check it, the list changes.

**Key Operations** (Jira tools):
- Execute JQL queries for data extraction -- `searchJiraIssuesUsingJql`
- Create and update issues -- `createJiraIssue`, `editJiraIssue`, `addOrEditJiraIssueComment`
- Move issues through the workflow -- `listJiraIssueTransitions`, `transitionJiraIssue`
- Create and manage sprints and boards -- `manageJiraSprint`, `listJiraBoardSprints`, `getJiraBoardSprintData`, `createJiraBoard`
- Create or update spaces (formerly "projects") -- `createJiraProject`, `updateJiraProject`
- Pull history for flow metrics -- `listJiraIssueChangelogs`
- Read filters and dashboards -- `listJiraFilters`, `listJiraDashboards`

Workflow schemes, automation rules, permission schemes and custom-field configuration are **not** exposed as MCP tools -- configure those in Jira admin (or via the REST API) and document the change.

**Integration Points**:
- Pull metrics for Senior PM reporting
- Configure sprint boards for Scrum Master
- Create documentation pages for Confluence Expert
- Support template creation for Template Creator

## Troubleshooting

| Problem | Likely Cause | Resolution |
|---------|-------------|------------|
| JQL queries return unexpected results or time out | Overly broad filters, missing indexes, or incorrect field references | Add specificity with project/date constraints; use `ORDER BY` sparingly on large datasets; verify field names with autocomplete |
| Automation rules fire multiple times for a single event | Cascading triggers where one rule's action triggers another rule | Add conditions to prevent loops (e.g., check `initiator is automation`); use the audit log to trace execution chains |
| Board shows wrong issues or missing cards | Filter behind the board is misconfigured or sprint assignment is incorrect | Verify the board's saved filter JQL; check that issues have the correct sprint field value; review board settings > general |
| Workflow transitions fail with validator errors | Required fields not populated, or post-function order is incorrect | Check validator configuration; ensure required fields have values before transition; reorder post-functions so field-setting happens before validation |
| Custom fields not appearing on screens | Field added to wrong screen scheme or issue type context is too narrow | Verify field context includes the target project and issue type; confirm the correct screen scheme is associated with the project |
| Bulk operations fail or time out | Too many issues selected (>1000) or complex post-functions on transitions | Reduce batch size to 100-200 issues; disable non-essential automation rules temporarily during bulk operations |
| Dashboard gadgets show "No data" | Underlying filter returns no results for the current user due to permissions | Verify the filter is shared with the dashboard viewers; check project permission schemes |

## Success Criteria

- All active projects use standardized workflow schemes (no more than 5 unique workflows org-wide)
- JQL saved filters cover 90%+ of recurring reporting needs without ad-hoc queries
- Automation rules reduce manual status updates by 60%+ across managed projects
- Data quality score (required fields populated, consistent labeling) exceeds 85% for active issues
- Average dashboard load time stays under 3 seconds with all gadgets rendering
- New project setup (from request to team-ready board) completes within 2 business days
- Zero critical permission escalations caused by misconfigured schemes per quarter
