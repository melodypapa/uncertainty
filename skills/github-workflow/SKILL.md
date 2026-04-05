---
name: github-workflow
description: Use when preparing to push staged files to a feature branch, about to commit changes that need proper formatting, or asking what to do before pushing to GitHub. This workflow enforces quality gates (language-specific: ruff/mypy/pytest for Python, ESLint/Prettier/Jest for JS/TS, go fmt/go vet/go test for Go, Maven/Gradle test for Java, clang-format/clang-tidy for C/C++), creates GitHub issues and pull requests, sets up feature branches with correct naming, ensures proper commit format (feat/fix types with issue references, no Co-Authored-By), and automatically pushes to GitHub when all checks pass. Use this whenever the user mentions staged changes, wants to push correctly, or needs a complete pre-push workflow including quality checks. Auto-detects project type and source directories (handles missing tools/ dirs).
---

# GitHub Workflow

## Overview

Complete workflow for feature development: quality checks, issue creation, PR creation, branch setup, and commit formatting. Supports multiple project types with auto-detection.

## When to Use

```dot
digraph when_flowchart {
    "Have staged files?" [shape=diamond];
    "About to push to feature branch?" [shape=diamond];
    "Use github-workflow" [shape=box];
    "Skip" [shape=box];

    "Have staged files?" -> "About to push to feature branch?" [label="yes"];
    "About to push to feature branch?" -> "Use github-workflow" [label="yes"];
    "About to push to feature branch?" -> "Skip" [label="no"];
    "Have staged files?" -> "Skip" [label="no"];
}
```

**Use when:**
- Staged files ready for push
- Creating feature branch for work
- Ensuring quality before pushing
- Creating pull request for code review
- Any project type (Python, JS/TS, Go, Java, C/C++)

**NOT for:**
- Quick commits to main branch
- Work without quality gates
- Pushing to gitee (GitHub only)
- Creating PRs without proper issue tracking

## Auto-Detect Project Type

Check for these files to determine project type (check in order):

| Language | Detection Files |
|----------|-----------------|
| Python | `pyproject.toml`, `requirements.txt`, `setup.py` |
| JavaScript/TypeScript | `package.json`, `tsconfig.json` |
| Go | `go.mod` |
| Java | `pom.xml`, `build.gradle`, `build.gradle.kts` |
| C/C++ | `CMakeLists.txt`, `Makefile` |

**If no files match**: Ask user to specify project type.

## Workflow Steps

### 1. Auto-Detect Project Type

Run detection checks in order:

```bash
# Check for Python
ls pyproject.toml requirements.txt setup.py 2>/dev/null | head -1 && echo "python" || \
# Check for JS/TS
ls package.json tsconfig.json 2>/dev/null | head -1 && echo "js" || \
# Check for Go
ls go.mod 2>/dev/null | head -1 && echo "go" || \
# Check for Java
ls pom.xml build.gradle build.gradle.kts 2>/dev/null | head -1 && echo "java" || \
# Check for C/C++
ls CMakeLists.txt Makefile 2>/dev/null | head -1 && echo "cpp" || \
echo "unknown"
```

**If "unknown"**: Ask user to specify project type.

### 2. Quality Gates (All Must Pass)

**Before running quality gates, verify the remote is GitHub:**
```bash
git remote -v | grep github.com
```

If no GitHub remote found, ask user to add it or select correct remote.

#### Python (detected via pyproject.toml, requirements.txt, setup.py)

```bash
# Find Python files to check (auto-detect directories)
PYTHON_FILES=$(find . -name "*.py" -not -path "./.*" -not -path "*/venv/*" -not -path "*/.venv/*" -not -path "*/node_modules/*" -not -path "*/__pycache__/*" | head -c 1000)
PYTHON_DIRS=$(find . -name "*.py" -not -path "./.*" -not -path "*/venv/*" -not -path "*/.venv/*" -not -path "*/node_modules/*" -not -path "*/__pycache__/*" -exec dirname {} \; | sort -u | head -10 | tr '\n' ' ')

ruff check ${PYTHON_DIRS:-.}
mypy ${PYTHON_DIRS:-.}
pytest
pip install -e . 2>/dev/null || true
```

**Requirements:**
- Ruff: No linting errors
- MyPy: No type errors
- Pytest: All tests pass
- Package installs successfully

#### JavaScript/TypeScript (detected via package.json, tsconfig.json)

```bash
# Find JS/TS files and directories (auto-detect)
JS_DIRS=$(find . -name "*.js" -o -name "*.ts" -o -name "*.jsx" -o -name "*.tsx" | grep -v node_modules | grep -v ".next" | grep -v "dist" | grep -v "build" | xargs dirname 2>/dev/null | sort -u | head -10 | tr '\n' ' ')

# Check package.json for available scripts
if grep -q "lint" package.json; then npm run lint; fi
if grep -q "format:check" package.json; then npm run format:check; fi
if grep -q "test" package.json; then npm test; fi

# Or fallback to common tools
npx eslint ${JS_DIRS:-.} --max-warnings 0 2>/dev/null || true
npx prettier --check ${JS_DIRS:-.} 2>/dev/null || true
npm test 2>/dev/null || true
```

**Requirements:**
- ESLint: No errors (max-warnings 0)
- Prettier: No formatting changes needed
- Tests: All tests pass

#### Go (detected via go.mod)

```bash
go fmt ./...
go vet ./...
go test ./... -v
go build ./...
```

**Requirements:**
- go fmt: No files need formatting
- go vet: No issues reported
- go test: All tests pass
- go build: Compiles successfully

#### Java (detected via pom.xml, build.gradle, build.gradle.kts)

**Maven:**
```bash
mvn checkstyle:check
mvn test
mvn package
```

**Gradle:**
```bash
./gradlew checkstyleMain
./gradlew test
./gradlew build
```

**Requirements:**
- Checkstyle: No violations
- Tests: All tests pass
- Build: Compiles successfully

#### C/C++ (detected via CMakeLists.txt, Makefile)

```bash
# Find C/C++ source files (auto-detect)
CPP_FILES=$(find . -name "*.c" -o -name "*.cpp" -o -name "*.cc" -o -name "*.cxx" | grep -v build | grep -v ".git" | head -c 2000)

# CMake:
cmake --build build --target all 2>/dev/null || true
ctest --test-dir build 2>/dev/null || true

# Makefile:
make check 2>/dev/null || make test 2>/dev/null || make 2>/dev/null || true

# Format check (auto-detect files)
if [ -n "$CPP_FILES" ]; then
    clang-format --dry-run --Werror $CPP_FILES 2>/dev/null || true
fi
```

**Requirements:**
- Build: Compiles successfully
- Tests: All tests pass (if tests exist)
- Format: No formatting changes needed

#### Display Summary Format

```
Check        Status    Details
─────────────────────────────────
Linting      ✅ Pass    No issues found
Formatting   ✅ Pass    No changes needed
Tests        ✅ Pass    All tests passed
Build        ✅ Pass    Build successful
```

**If any fail:**
- Report errors
- Ask user: abort, fix & retry, or continue
- Don't proceed without confirmation

### 3. Analyze Changes

```bash
git status
git diff
```

Get brief summary from user if diff unclear.

### 4. Create GitHub Issue

```bash
gh issue create \
  --title "<type>: <brief description>" \
  --body "$(cat <<'EOF'
## Summary

## Changes

## Files Modified

## Test Coverage

## Requirements
EOF
)"
```

- Capture issue number (e.g., #20)
- Types: feat, fix, docs, refactor, test, chore
- **Skip if issue already exists** - ask user for existing issue number

### 5. Create Feature Branch

```bash
git checkout -b feature/<requirement-id>-short-description
# or
git checkout -b feature/<type>-short-description
```

Examples:
- `feature/swr-writer-00006-class-file-structure`
- `feature/add-new-parser`

### 6. Stage and Commit

```bash
git add <relevant-files>
git commit -m "$(cat <<'EOF'
<type>: <description>

<detailed description of changes>

Closes #<issue-number>
EOF
)"
```

**Commit types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**IMPORTANT:** No Co-Authored-By line

### 7. Push to GitHub (Automatic)

After successful commit with all quality gates passing, automatically push to GitHub:

```bash
git push -u origin $(git branch --show-current)
```

**Push conditions:**
- All quality gates must pass (✅)
- Commit must be created successfully
- Must be on a feature branch (not main/master)
- Remote must be GitHub (check `git remote -v`)

**If push fails:**
- Check remote URL is GitHub.com (not gitee, gitlab, etc.)
- Verify network connectivity
- Check authentication: `gh auth status`
- Ask user before retrying

**Display push result:**
```
✅ All quality checks passed
✅ Committed: <commit-hash>
🚀 Pushing to GitHub...
✅ Pushed to feature/<branch-name>
```

### 8. Create Pull Request (Automatic)

After successful push, automatically create a pull request:

```bash
gh pr create \
  --title "<type>: <brief description>" \
  --body "$(cat <<'EOF'
## Summary

## Changes

## Files Modified

## Test Coverage

Closes #<issue-number>
EOF
)"
```

**PR creation conditions:**
- All quality gates must pass (✅)
- Commit must be created and pushed successfully
- Must be on a feature branch (not main/master)
- Remote must be GitHub

**If PR creation fails:**
- Check if PR already exists: `gh pr list --head $(git branch --show-current)`
- Verify authentication: `gh auth status`
- Ask user before retrying

**Display PR result:**
```
✅ All quality checks passed
✅ Committed: <commit-hash>
🚀 Pushed to feature/<branch-name>
✅ PR created: https://github.com/<org>/<repo>/pull/<pr-number>
```

**PR title format:** `<type>: <brief description>` (same as commit message first line)

**PR body sections:**
- Summary (from issue)
- Changes (from issue or manual input)
- Files Modified (optional)
- Test Coverage (from issue)
- `Closes #<issue-number>` (auto-link to issue)

**Skip PR creation if:**
- User explicitly requests to skip
- PR already exists for this branch
- Work is not ready for review

## Quick Reference

| Step | Action | Required |
|------|--------|----------|
| 1 | Detect project type | ✅ |
| 2 | Run language-specific quality gates | ✅ |
| 3 | Review changes (git diff) | ✅ |
| 4 | Create/Link GitHub issue | ✅ |
| 5 | Create feature branch | ✅ |
| 6 | Stage and commit | ✅ |
| 7 | Push to GitHub (automatic if all pass) | ✅ |
| 8 | Create pull request (automatic after push) | ✅ |

### Quality Gates by Language

| Language | Linting | Type Check | Tests | Build |
|----------|---------|------------|-------|-------|
| Python | ruff | mypy | pytest | pip install |
| JS/TS | eslint | n/a | npm test | n/a |
| Go | go vet | n/a | go test | go build |
| Java (Maven) | checkstyle | n/a | mvn test | mvn package |
| Java (Gradle) | checkstyle | n/a | gradle test | gradle build |
| C/C++ | clang-tidy | n/a | ctest/make test | cmake build |

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Pushing without tests | Run language-specific test command first |
| Missing issue reference | Add `Closes #N` to commit message |
| Using gitee remote | Push to GitHub only |
| Adding Co-Authored-By | Remove Claude attribution |
| Wrong quality gates for project type | Auto-detect and use language-specific commands |
| Not checking format before push | Run format check for your language |
| Assuming directories exist | Use auto-detection with find commands |
| Manually pushing after workflow | Workflow auto-pushes when all checks pass |

## Red Flags - STOP

- [ ] Quality checks failed (any language)
- [ ] No GitHub issue created or linked
- [ ] Commit message doesn't follow format
- [ ] Commit message includes Co-Authored-By line
- [ ] Branch name doesn't follow `feature/<type>-*` or `feature/<requirement-id>-*` convention
- [ ] Commit message missing `Closes #<issue-number>` reference
- [ ] About to push to non-GitHub remote
- [ ] About to push to main/master branch
- [ ] Project type unknown and not specified by user
- [ ] Language-specific build commands not run
- [ ] Push attempted when quality gates failed
- [ ] PR title doesn't match commit message format
- [ ] PR body missing `Closes #<issue-number>` reference

**Any red flag? Fix before proceeding.**

## Related

- Push to GitHub: Use `git push` (manual step after this workflow)
- Full automation: `/gh-workflow` (includes PR creation)
- Language-specific docs: See project-specific sections above for detailed commands

## Supported Project Types Summary

| Language | Config Files Detected | Quality Gates |
|----------|----------------------|---------------|
| Python | pyproject.toml, requirements.txt, setup.py | ruff, mypy, pytest, pip install |
| JavaScript/TypeScript | package.json, tsconfig.json | eslint, prettier, npm test |
| Go | go.mod | go fmt, go vet, go test, go build |
| Java (Maven) | pom.xml | checkstyle, mvn test, mvn package |
| Java (Gradle) | build.gradle, build.gradle.kts | checkstyle, gradle test, gradle build |
| C/C++ | CMakeLists.txt, Makefile | clang-format, ctest/make test, cmake build |