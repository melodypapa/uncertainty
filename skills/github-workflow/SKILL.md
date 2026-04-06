---
name: github-workflow
description: Use when preparing to push staged files to a feature branch, about to commit changes that need proper formatting, or asking what to do before pushing to GitHub. This workflow enforces quality gates (language-specific: ruff/mypy/pytest for Python, ESLint/Prettier/Jest for JS/TS, go fmt/go vet/go test for Go, Maven/Gradle test for Java, clang-format/clang-tidy for C/C++), creates GitHub issues and pull requests, sets up feature branches with correct naming, ensures proper commit format (feat/fix types with issue references, no Co-Authored-By), and automatically pushes to GitHub when all checks pass. Use this whenever the user mentions staged changes, wants to push correctly, or needs a complete pre-push workflow including quality checks. Auto-detects project type and source directories (handles missing tools/ dirs).
---

# GitHub Workflow

Execute this workflow directly - don't create documentation files. Focus on running commands and reporting results.

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

## Step 2: Run Quality Gates

**Run all quality checks and report results.**

**Python:**
```bash
PYTHON_DIRS=$(find . -name "*.py" -not -path "*/venv/*" -not -path "*/.venv/*" -not -path "*/node_modules/*" -not -path "*/__pycache__/*" -exec dirname {} \; 2>/dev/null | sort -u | head -10 | tr '\n' ' ')
ruff check ${PYTHON_DIRS:-.}
mypy ${PYTHON_DIRS:-.}
pytest
pip install -e . 2>/dev/null || true
```

**JavaScript/TypeScript:**
```bash
if grep -q "lint" package.json; then npm run lint; else npx eslint . --max-warnings 0 2>/dev/null || true; fi
if grep -q "format:check" package.json; then npm run format:check; else npx prettier --check . 2>/dev/null || true; fi
npm test
```

**Go:**
```bash
go fmt ./...
go vet ./...
go test ./...
go build ./...
```

**Java (Maven):**
```bash
mvn checkstyle:check
mvn test
mvn package
```

**Java (Gradle):**
```bash
./gradlew checkstyleMain
./gradlew test
./gradlew build
```

**C/C++:**
```bash
cmake --build build 2>/dev/null || make check 2>/dev/null
ctest --test-dir build 2>/dev/null || make test 2>/dev/null
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

**If any checks fail:**
- Report the errors clearly
- **ASK the user**: "Quality checks failed. Would you like to: 1) Fix the issues and re-check, or 2) Continue anyway?"
- If user chooses to fix: Wait for them to fix, then re-run quality checks
- If user chooses to continue: Proceed to Step 3

## Step 3: Review Changes

```bash
git status && git diff --cached
```

## Step 4: Create GitHub Issue

```bash
gh issue create --title "<type>: <brief description>" --body "## Summary\n\n## Changes\n\n## Test Coverage"
```
Types: feat, fix, docs, refactor, test, chore. Capture issue number.

## Step 5: Create Feature Branch

```bash
git checkout -b feature/<requirement-id>-short-description
# or
git checkout -b feature/<type>-short-description
```

## Step 6: Stage and Commit

```bash
git add <relevant-files>
git commit -m "<type>: <description>

<detailed description>

Closes #<issue-number>"
```
**CRITICAL:** No Co-Authored-By line.

## Step 7: Push to GitHub

```bash
git push -u origin $(git branch --show-current)
```

## Step 8: Create Pull Request

```bash
gh pr create --title "<type>: <brief description>" --body "## Summary\n\n## Changes\n\nCloses #<issue-number>"
```

## User Choice Points

The workflow will **ASK the user** to make decisions at these points:

- **After quality checks fail**: User can choose to fix issues OR continue anyway
- User has full control over whether to proceed despite quality gate failures

The workflow encourages fixing quality issues but respects user autonomy to continue if they choose.