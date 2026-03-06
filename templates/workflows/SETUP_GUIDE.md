# GitHub Workflows Setup Guide

Setup guide for the 12 sample GitHub Actions workflows included in the AI Skills Library. Copy the workflows you need into your project's `.github/workflows/` directory.

---

## Quick Start

### 1. Copy Workflows

```bash
# Copy all workflows
mkdir -p .github/workflows
cp templates/workflows/*.yml .github/workflows/

# Or copy only the ones you need
cp templates/workflows/ci-quality-gate.yml .github/workflows/
cp templates/workflows/skill-validation.yml .github/workflows/
```

### 2. Create Required Secrets

Some workflows require GitHub repository secrets:

| Secret | Required By | How to Get |
|--------|------------|------------|
| `CLAUDE_CODE_OAUTH_TOKEN` | `claude-code-review.yml`, `claude.yml` | [Claude Code settings](https://claude.ai/code) |
| `PROJECTS_TOKEN` | `smart-sync.yml` | GitHub Personal Access Token (see below) |

**Creating PROJECTS_TOKEN:**

1. Go to: https://github.com/settings/tokens/new
2. Configure:
   - **Note**: "Project Board Access"
   - **Expiration**: 90 days (recommended)
   - **Scopes**: `repo` + `project`
3. Generate and copy the token
4. Add to your repo: Settings > Secrets and variables > Actions > New repository secret

### 3. Create Project Board Labels

If using `smart-sync.yml`, create these labels in your repository:

```bash
# Status Labels (6)
gh label create "status: triage" --color "fbca04" --description "To Triage column"
gh label create "status: backlog" --color "d4c5f9" --description "Backlog column"
gh label create "status: ready" --color "0e8a16" --description "Ready column"
gh label create "status: in-progress" --color "1d76db" --description "In Progress column"
gh label create "status: in-review" --color "d876e3" --description "In Review column"
gh label create "status: done" --color "2ea44f" --description "Done column"

# Priority Labels (4)
gh label create "P0" --color "b60205" --description "Critical priority"
gh label create "P1" --color "d93f0b" --description "High priority"
gh label create "P2" --color "fbca04" --description "Medium priority"
gh label create "P3" --color "0e8a16" --description "Low priority"
```

### 4. Configure Project Board

If using `smart-sync.yml`, your GitHub Project board columns must match:

1. **To triage**
2. **Backlog**
3. **Ready**
4. **In Progress**
5. **In Review**
6. **Done**

---

## Testing the Setup

### Test 1: Create Test Issue

```bash
gh issue create \
  --title "Test: Automation Setup" \
  --body "Testing GitHub automation workflows" \
  --label "status: triage"
```

### Test 2: Change Issue Status

```bash
gh issue edit ISSUE_NUMBER --add-label "status: in-progress"
```

### Test 3: Create Test PR

```bash
git checkout -b test/automation-setup
echo "# Test" > TEST.md
git add TEST.md
git commit -m "test: verify automation"
git push origin test/automation-setup

gh pr create \
  --title "test: Verify automation workflows" \
  --body "Fixes #ISSUE_NUMBER"
```

**Expected:** Claude review triggers, CI quality gate runs, issue auto-closes on merge.

---

## Emergency: Kill Switch

All workflows check a `.github/WORKFLOW_KILLSWITCH` file. Copy the included `WORKFLOW_KILLSWITCH` file to your `.github/` directory:

```bash
cp templates/workflows/WORKFLOW_KILLSWITCH .github/WORKFLOW_KILLSWITCH
```

**Disable all workflows:**
```bash
echo "STATUS: DISABLED" > .github/WORKFLOW_KILLSWITCH
git add .github/WORKFLOW_KILLSWITCH
git commit -m "emergency: Disable workflows"
git push
```

**Re-enable:**
```bash
echo "STATUS: ENABLED" > .github/WORKFLOW_KILLSWITCH
git commit -am "chore: Re-enable workflows"
git push
```

---

## Usage Examples

### Auto-Close Issues with PR

In your PR description:
```markdown
Fixes #123
Closes #456
```
When merged, issues #123 and #456 automatically close.

### Sync Issue Status

**Option A — Update label:**
```bash
gh issue edit 123 --add-label "status: in-review"
```
Moves to "In Review" on project board.

**Option B — Update board:**
Drag issue to "In Review" column on project board. Label updates automatically.

---

## Troubleshooting

### Smart Sync Not Working

```bash
# Check if secret exists
gh secret list | grep PROJECTS_TOKEN
```

If missing, add PROJECTS_TOKEN (see step 2 above).

### Claude Review Not Running

```bash
# Check recent workflow runs
gh run list --workflow=claude-code-review.yml --limit 5
```

Verify `CLAUDE_CODE_OAUTH_TOKEN` exists and check workflow logs.

### Rate Limits

```bash
gh api rate_limit --jq '.resources.core.remaining, .resources.graphql.remaining'
```

Workflows require 50+ API calls remaining before executing.

---

## Security

**4-Layer Security Model:**

1. **GitHub Permissions** — Only team members trigger workflows
2. **Tool Restrictions** — Allowlisted commands only
3. **Token Scoping** — Minimal permissions (repo + project)
4. **Branch Protection** — Required reviews and status checks

---

## Maintenance

**Weekly:**
```bash
gh run list --status failure --limit 10
gh secret list
```

**Quarterly:**
- Regenerate PROJECTS_TOKEN (expires every 90 days)
- Review and update workflow versions
