# Workflows, Governance & MCP Integration

Read this when you need the full step-by-step processes for creating, modifying, or governing templates — plus handoff protocols, best practices, and Atlassian MCP operations.

## Workflows

### Template Creation Process
1. **Discover**: Interview stakeholders to understand needs
2. **Analyze**: Review existing content patterns
3. **Design**: Create template structure and placeholders
4. **Implement**: Build template with macros and formatting
5. **Test**: Validate with sample data
6. **Document**: Create usage instructions
7. **Publish**: Deploy to appropriate space/project
8. **Train**: Educate users on template usage
9. **Monitor**: Track adoption and gather feedback
10. **Iterate**: Refine based on usage

### Template Modification Process
1. **Assess**: Review change request and impact
2. **Version**: Create new version, keep old available
3. **Modify**: Update template structure/content
4. **Test**: Validate changes don't break existing usage
5. **Migrate**: Provide migration path for existing content
6. **Communicate**: Announce changes to users
7. **Support**: Assist users with migration
8. **Archive**: Deprecate old version after transition

### Blueprint Development
1. Define blueprint scope and purpose
2. Design multi-page structure
3. Create page templates for each section
4. Configure page creation rules
5. Add dynamic content (Jira queries, user data)
6. Test blueprint creation flow
7. **HANDOFF TO**: Atlassian Admin for global deployment

## Best Practices

### Template Design Principles
**Clarity**: Use clear section headers and instructions
**Consistency**: Maintain visual and structural consistency
**Completeness**: Include all necessary sections
**Flexibility**: Allow customization where appropriate
**Guidance**: Provide inline instructions and examples

### Macro Usage Guidelines
**Dynamic Content**: Use macros for auto-updating content (dates, user mentions, Jira queries)
**Visual Hierarchy**: Use panels, infos, and notes to create visual distinction
**Interactivity**: Use expand macros for collapsible sections
**Integration**: Embed Jira charts and tables for live data

### Template Maintenance
**Version Control**: Track template versions and changes
**Deprecation**: Clearly mark outdated templates
**Documentation**: Maintain usage guides for each template
**Feedback Loop**: Regularly gather user feedback and iterate

## Handoff Protocols

**FROM Senior PM**:
- Template requirements for projects
- Reporting template needs
- Executive summary formats
- Portfolio tracking templates

**TO Senior PM**:
- Completed templates ready for use
- Template usage analytics
- Suggestions for new templates
- Template optimization opportunities

**FROM Scrum Master**:
- Sprint ceremony template needs
- Team-specific template requests
- Retrospective format preferences
- Sprint planning layouts

**TO Scrum Master**:
- Sprint-ready templates
- Team documentation templates
- Agile ceremony structures
- Velocity tracking templates

**FROM Jira Expert**:
- Issue template requirements
- Custom field display needs
- Workflow-specific templates
- Reporting template requests

**TO Jira Expert**:
- Issue description templates
- Field configuration templates
- Workflow documentation
- JQL query templates

**FROM Confluence Expert**:
- Space-specific template needs
- Global template requests
- Blueprint requirements
- Macro-based templates

**TO Confluence Expert**:
- Configured page templates
- Blueprint structures
- Template deployment plans
- Usage guidelines

**FROM Atlassian Admin**:
- Org-wide template standards
- Global template deployment
- Template governance requirements
- Compliance templates

**TO Atlassian Admin**:
- Global templates for approval
- Template usage reports
- Template compliance status
- Recommendations for standards

## Template Governance

**Creation Process**:
1. Request and justification
2. Design and review
3. Testing with pilot users
4. Documentation
5. Approval
6. Deployment
7. Training
8. Monitoring

**Review Cycle**:
- Templates reviewed quarterly
- Usage metrics analyzed
- Feedback incorporated
- Updates deployed
- Deprecated templates archived

**Quality Standards**:
- All templates documented
- Clear usage instructions
- Example content provided
- Tested before deployment
- Version controlled
- Feedback mechanism in place

## Atlassian MCP Integration

**Primary Tools**: Atlassian Rovo MCP Server (Atlassian's official remote MCP server for Cloud; endpoint `https://mcp.atlassian.com/v2/mcp`). See Atlassian's [supported tools](https://support.atlassian.com/atlassian-rovo-mcp-server/docs/supported-tools/) list (as of September 2026).

**Template Operations**:
- Read existing Confluence templates -- `listConfluenceTemplates`, `getConfluenceTemplate`
- Create pages from template content -- `createConfluenceContent` (check `getContentFormatGuide` for body format)
- Pre-fill Jira issue descriptions from templates -- `createJiraIssue`, `editJiraIssue`
- Build automated template deployment scripts (Confluence/Jira REST API -- creating or editing templates themselves is not an MCP tool)
- Version control template content

**Integration Points**:
- Support all roles with standardized templates
- Enable Confluence Expert with deployable templates
- Provide Jira Expert with issue templates
- Supply Senior PM with reporting templates
- Give Scrum Master sprint ceremony templates
