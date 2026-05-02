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
| 1 | `git remote -v \| grep -E 'github\.com[/:]'` | Verify GitHub remote |
| 2 | Quality gates | Run lint, test, build |
| 2.5 | Secrets detection | Check for API keys, tokens |
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
- **Secrets detected in staged files**
- **Branch name contains special characters**
- **Suspicious or phishing remote domain detected**

**If any red flag triggered: Stop and fix before proceeding.**

## Step 0: Early Exit Check

```bash
git diff --cached --name-only
```

**No staged files?** Inform user to run `git add` first. Exit immediately.

## Step 1: Verify GitHub Remote

```bash
git remote -v | grep -E '(^|[^.])github\.com[/:]'
which gh || echo "Install GitHub CLI: brew install gh"
```

**Validate remote URL format:**
- ✅ `git@github.com:owner/repo.git`
- ✅ `https://github.com/owner/repo.git`
- ❌ `git@github.com.malicious.com:owner/repo.git` (phishing domain)

**Check for suspicious patterns:**
```bash
# Extract domain and check for phishing indicators
REMOTE_DOMAIN=$(git remote -v | grep -oP '(?<=@|//)[^:/]+' | head -1)
if echo "$REMOTE_DOMAIN" | grep -qE '\.(com|org|io|net|co|app)\.'; then
    echo "WARNING: Possible phishing domain detected: $REMOTE_DOMAIN"
    read -p "Continue? (y/N) " -n 1 -r
    [[ ! $REPLY =~ ^[Yy]$ ]] && exit 1
fi
```

**Multiple remotes?** Ask user which remote to use.

## Step 2: Run Quality Gates

**Run checks. Stop immediately on failure (`|| exit 1`).**

### Language Projects

| Language | Commands |
|----------|----------|
| Python | `ruff check . && mypy . && pytest \|\| exit 1` |
| JS/TS | `npm run lint && npm test \|\| exit 1` |
| Go | `go fmt ./... && go vet ./... && go test ./... \|\| exit 1` |
| Java | `mvn test \|\| exit 1` or `./gradlew test \|\| exit 1` |
| C/C++ | `cmake --build build && ctest --test-dir build \|\| exit 1` |

### Skills

**If changes include `skills/*/SKILL.md`:**

| Check | Command | Purpose |
|-------|---------|---------|
| YAML frontmatter | `python3 -c "import yaml; yaml.safe_load(open('SKILL.md').read().split('---')[1])"` | Valid syntax |
| Discoverable | `npx skills install . --list` | Can be found |
| Skills audit | `npx skills audit .` | Compliance check |
| Skills check | `npx skills-check .` | Quality validation |
| Evals (if exist) | Run evals.json assertions | Quality gates |
| Security - secrets | `grep -lE '(API_KEY|SECRET|PASSWORD|TOKEN|PRIVATE_KEY)' SKILL.md 2>/dev/null` | No hardcoded secrets |
| Security - shell injection | `grep -lE '\$\(.*\)|`' + '.*\$\{|bash.*-c|sh.*-c' SKILL.md 2>/dev/null` | No command injection in examples |
| Security - unsafe exec | `grep -lE '(exec|eval|system|os\.system|subprocess\.(shell|call))' SKILL.md 2>/dev/null` | No unsafe exec in examples |

**If ANY security check fails:**
1. **STOP immediately** - Do not proceed
2. Fix the security issue (use env vars, input validation, safe APIs)
3. Re-run all checks
4. Only proceed when all security checks pass

**Report:**
```
Check                     Status
───────────────────────────────────────
Lint                      ✅/❌
Test                      ✅/❌
Build                     ✅/❌
Skills - YAML             ✅/❌
Skills - Discoverable     ✅/❌
Skills - Audit            ✅/❌
Skills - Check            ✅/❌
Skills - Evals            ✅/❌
Skills - Security         ✅/❌
```

**Security check failures are blocking.** Fix before committing.

## Step 2.5: Secrets Detection

**CRITICAL: Check for secrets before committing.**

```bash
git diff --cached --name-only | xargs grep -l -E '(API_KEY|SECRET|PASSWORD|TOKEN|PRIVATE_KEY|\.env$)' 2>/dev/null || true
```

**If secrets found:**
1. **STOP immediately**
2. Remove secrets from files
3. Use environment variables or secret management
4. Add patterns to `.gitignore`

**Common secret patterns:**
- `.env` files
- `API_KEY=`, `SECRET=`, `TOKEN=`
- Private keys (`-----BEGIN PRIVATE KEY-----`)
- AWS credentials (`AKIA...`)

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

**Check for unsafe characters before sanitizing:**
```bash
if echo "$USER_INPUT" | grep -qE '[;&|$(\''"` ]'; then
    echo "WARNING: Unsafe characters detected in branch name"
fi
```

**Sanitize branch names:**
```bash
BRANCH_NAME=$(echo "$USER_INPUT" | tr -cd 'a-zA-Z0-9/-' | tr '[:upper:]' '[:lower:]')
[ -z "$BRANCH_NAME" ] && echo "ERROR: Branch name is empty after sanitization" && exit 1
```

**Allowed characters:** letters, numbers, hyphens, forward slashes
**Forbidden:** `;`, `&`, `|`, `$`, backticks, spaces, special chars

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
| Committing secrets | Run Step 2.5, use .gitignore |
| Skill security issues | Fix secrets/injection/unsafe-exec before commit |
| Unsafe branch names | Sanitize with `tr -cd` |
| Suspicious remote domain | Verify URL, reject phishing domains |
