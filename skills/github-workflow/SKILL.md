---
name: github-workflow
description: "Use when user has staged files ready to push, mentions commit/push/branch/PR, or asks what to do before pushing. Triggers: staged, commit, push, branch, PR, pull request, quality gates."
---

# GitHub Workflow

**Core principle:** Run quality gates BEFORE committing. Stop on failure. Never push failing code.

## When to Use

- User has staged files and wants to push
- User asks "what should I do before pushing?"
- User mentions creating PR or feature branch

## When NOT to Use

- No staged changes - user hasn't run `git add`
- Direct commits to main/master - feature branches only
- User explicitly wants to skip checks

## Quick Reference

| Step | Command | Purpose |
|------|---------|---------|
| 0 | `git diff --cached --name-only` | Early exit if no staged files |
| 1 | `git remote -v \| grep github.com` | Verify GitHub remote |
| 2 | Quality gates | Run lint, test, build |
| 3 | `git diff --cached` | Review changes |
| 4 | `gh issue create` | Create tracking issue |
| 5 | `git checkout -b feature/...` | Create feature branch |
| 6 | `git commit -m "..."` | Commit with proper format |
| 7 | `git push -u origin ...` | Push to remote |
| 8 | `gh pr create` | Create pull request |
| 9 | `gh pr view` | Verify PR created |

## Red Flags - STOP

- Skipping quality gates
- Committing directly to main/master
- Missing issue reference in commit
- Adding Co-Authored-By or AI attribution
- Pushing without tests passing

**If any red flag triggered: Stop and fix before proceeding.**

## Step 0: Early Exit Check

```bash
git diff --cached --name-only
```

**No staged files?** Inform user to run `git add` first. Exit immediately.

## Step 1: Verify GitHub Remote

```bash
git remote -v | grep github.com
which gh || echo "Install GitHub CLI: brew install gh"
```

**Multiple remotes?** Ask user which remote to use.

## Step 2: Run Quality Gates

**Run checks. Stop immediately on failure (`|| exit 1`).**

| Language | Commands |
|----------|----------|
| Python | `ruff check . && mypy . && pytest \|\| exit 1` |
| JS/TS | `npm run lint && npm test \|\| exit 1` |
| Go | `go fmt ./... && go vet ./... && go test ./... \|\| exit 1` |
| Java | `mvn test \|\| exit 1` or `./gradlew test \|\| exit 1` |
| C/C++ | `cmake --build build && ctest --test-dir build \|\| exit 1` |

**Report:**
```
Check     Status
───────────────────
Lint      ✅/❌
Test      ✅/❌
Build     ✅/❌
```

## Step 3: Review Changes

```bash
git diff --cached --stat
git diff --cached
```

## Step 4: Create or Reference Issue

**Ask:** "Existing issue number, or create new?"

**Create new:**
```bash
gh issue create --title "<type>: <description>" --body "## Summary"
```

Types: feat, fix, docs, refactor, test, chore

## Step 5: Feature Branch Decision

```dot
digraph branch_decision {
    rankdir=TB
    node [shape=box]
    
    start [label="Check current branch" shape=diamond]
    main [label="On main/master?"]
    create [label="Create: git checkout -b feature/<name>"]
    ask [label="Ask: Stay on current branch\nor create new?"]
    done [label="Proceed to commit"]
    
    start -> main
    main -> create [label="yes"]
    main -> ask [label="no"]
    ask -> done [label="stay"]
    ask -> create [label="new"]
    create -> done
}
```

**Branch naming:** `feature/<type>-short-description`

## Step 6: Commit

```bash
git commit -m "<type>: <description>

<details>

Closes #<issue>"
```

**CRITICAL: Never add Co-Authored-By or AI attribution.**

## Step 7: Push to GitHub

```bash
git push -u origin $(git branch --show-current)
```

**Push rejected?** Handle merge conflicts (see below).

### Merge Conflict Handling

```bash
git pull --rebase origin $(git branch --show-current)
```

**If conflicts:**
1. Edit conflicted files (look for `<<<<<<<` markers)
2. `git add <resolved-files>`
3. `git rebase --continue`
4. Retry push

## Step 8: Create Pull Request

```bash
gh pr create --title "<type>: <description>" --body "Closes #<issue>"
```

**Draft?** Add `--draft` flag if requested.

## Step 9: Verify PR

```bash
gh pr view
```

Confirm:
- PR URL is accessible
- CI checks are running
- Base branch is correct

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Skipping quality gates | Always run Step 2 |
| Committing to main | Create feature branch first |
| Missing issue reference | Include `Closes #N` |
| Adding Co-Authored-By | Never add AI attribution |
| Pushing without tests | Quality gates must pass |
| Ignoring merge conflicts | Resolve before push |
