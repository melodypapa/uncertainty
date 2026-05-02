---
name: github-workflow
description: Use when user has staged files ready to push to a feature branch, needs to run pre-push quality checks, asks what to do before pushing staged changes, or mentions committing/pushing code to GitHub. Triggers on keywords: staged, commit, push, branch, PR, pull request, quality gates, pre-push checks.
---

# GitHub Workflow

Execute this workflow directly - don't create documentation files. Focus on running commands and reporting results.

## Overview

**Core principle:** Run quality gates BEFORE committing. Stop immediately on any failure. Never push failing code.

## When to Use

- User has staged files (`git add` done) and wants to push
- User asks "what should I do before pushing?"
- User mentions creating a PR or feature branch
- User wants quality checks before commit

## When NOT to Use

- **No staged changes** - User hasn't run `git add` yet
- **Direct commits to main/master** - This workflow is for feature branches only
- **Hotfixes on production** - Different urgency, skip quality gates if critical
- **User explicitly wants to skip checks** - Respect user autonomy

## Quick Reference

| Step | Command | Purpose |
|------|---------|---------|
| 0 | `git diff --cached --name-only` | Early exit if no staged files |
| 1 | `git remote -v \| grep github.com` | Verify GitHub remote exists |
| 2 | Quality gates (see below) | Run lint, test, build |
| 3 | `git status && git diff --cached` | Review changes before commit |
| 4 | `gh issue create` | Create tracking issue |
| 5 | `git checkout -b feature/...` | Create feature branch |
| 6 | `git commit -m "..."` | Commit with proper format |
| 7 | `git push -u origin ...` | Push to remote |
| 8 | `gh pr create` | Create pull request |

## Step 0: Early Exit Check (Performance)

**First, check for staged files:**
```bash
git diff --cached --name-only
```

**If no staged files are found:**
- Inform the user: "No staged changes found. Stage files first with `git add <files>`."
- **Exit immediately** - do not proceed with quality gates or any other steps.

This prevents unnecessary test runs and improves performance when there's nothing to commit.

## Step 1: Verify GitHub Remote

```bash
git remote -v | grep github.com
```

If no GitHub remote is found, inform the user and exit.

**Check for `gh` CLI:**
```bash
which gh || echo "GitHub CLI not installed. Install with: brew install gh"
```

## Step 2: Run Quality Gates

**Run all quality checks and report results. STOP immediately if any check fails.**

**Python:**
```bash
PYTHON_DIRS=$(find . -name "*.py" -not -path "*/venv/*" -not -path "*/.venv/*" -not -path "*/node_modules/*" -not -path "*/__pycache__/*" -exec dirname {} \; 2>/dev/null | sort -u | head -10 | tr '\n' ' ')
ruff check ${PYTHON_DIRS:-.} || exit 1
mypy ${PYTHON_DIRS:-.} || exit 1
pytest || exit 1
```

**JavaScript/TypeScript:**
```bash
if grep -q "lint" package.json; then npm run lint || exit 1; else npx eslint . --max-warnings 0 2>/dev/null || true; fi
if grep -q "format:check" package.json; then npm run format:check || exit 1; else npx prettier --check . 2>/dev/null || true; fi
npm test || exit 1
```

**Go:**
```bash
go fmt ./... || exit 1
go vet ./... || exit 1
go test ./... || exit 1
go build ./... || exit 1
```

**Java (Maven):**
```bash
mvn checkstyle:check || exit 1
mvn test || exit 1
mvn package || exit 1
```

**Java (Gradle):**
```bash
./gradlew checkstyleMain || exit 1
./gradlew test || exit 1
./gradlew build || exit 1
```

**C/C++:**
```bash
cmake --build build 2>/dev/null || make check 2>/dev/null || exit 1
ctest --test-dir build 2>/dev/null || make test 2>/dev/null || exit 1
```

**Report summary:**
```
Check        Status
───────────────────────
Linting      ✅ Pass / ❌ Fail
Formatting   ✅ Pass / ❌ Fail
Tests        ✅ Pass / ❌ Fail
Build        ✅ Pass / ❌ Fail
```

**NOTE:** The `|| exit 1` in commands above ensures the workflow stops immediately if any check fails. User must fix issues and re-run the workflow.

## Step 3: Review Changes

```bash
git status && git diff --cached
```

## Step 4: Create or Reference GitHub Issue

**Ask user:** "Do you have an existing issue number, or should I create a new one?"

**If creating new:**
```bash
gh issue create --title "<type>: <brief description>" --body "## Summary\n\n## Changes\n\n## Test Coverage"
```

**If existing:** Capture the issue number for commit message.

Types: feat, fix, docs, refactor, test, chore

## Step 5: Create or Verify Feature Branch

**Check current branch:**
```bash
git branch --show-current
```

**If already on a feature branch:** Ask user if they want to stay on current branch or create a new one.

**If on main/master:**
```bash
git checkout -b feature/<type>-short-description
```

## Step 6: Stage and Commit

```bash
git add <relevant-files>
git commit -m "<type>: <description>

<detailed description>

Closes #<issue-number>"
```

**CRITICAL COMMIT RULES:**
1. **NEVER add Co-Authored-By line** - Do not include any attribution to AI assistants
2. Commit message format: `<type>: <description>` followed by blank line, then details, then `Closes #N`
3. Types: feat, fix, docs, refactor, test, chore

**Verify commit message does NOT contain:**
- "Co-Authored-By:"
- "Signed-off-by:" (unless user explicitly requests)
- Any AI attribution

## Step 7: Push to GitHub

```bash
git push -u origin $(git branch --show-current)
```

## Step 8: Create Pull Request

```bash
gh pr create --title "<type>: <brief description>" --body "## Summary\n\n## Changes\n\nCloses #<issue-number>"
```

**Ask user:** "Should this be a draft PR?" If yes, add `--draft` flag.

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Skipping quality gates | Always run Step 2. Use `|| exit 1` to enforce. |
| Committing to main/master | Always create feature branch first (Step 5) |
| Missing issue reference | Always include `Closes #N` in commit message |
| Adding Co-Authored-By | **NEVER** add AI attribution to commits |
| Pushing without tests | Quality gates must pass before push |
| Forgetting `git add` | Step 0 catches this - early exit |

## Workflow Behavior

**Quality Gate Failures:**
- Workflow stops immediately when any quality check fails (via `|| exit 1`)
- User must fix issues and re-run the workflow
- This ensures only passing code is committed and pushed

**Commit Messages:**
- Never include Co-Authored-By or AI attribution lines
- Format: `<type>: <description>` with `Closes #N` reference
