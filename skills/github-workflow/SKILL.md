---
name: github-workflow
description: Use when preparing to push staged files to a feature branch, about to commit changes that need proper formatting, or asking what to do before pushing to GitHub. This workflow enforces quality gates (language-specific: ruff/mypy/pytest for Python, ESLint/Prettier/Jest for JS/TS, go fmt/go vet/go test for Go, Maven/Gradle test for Java, clang-format/clang-tidy for C/C++), creates GitHub issues and pull requests, sets up feature branches with correct naming, ensures proper commit format (feat/fix types with issue references, no Co-Authored-By), and automatically pushes to GitHub when all checks pass. Use this whenever the user mentions staged changes, wants to push correctly, or needs a complete pre-push workflow including quality checks. Auto-detects project type and source directories (handles missing tools/ dirs).
---

# GitHub Workflow

Execute this workflow directly - don't create documentation files. Focus on running commands and reporting results.

## Auto-Detect Project Type

Check files in order: `pyproject.toml`/`requirements.txt`/`setup.py` → Python; `package.json`/`tsconfig.json` → JS/TS; `go.mod` → Go; `pom.xml`/`build.gradle` → Java; `CMakeLists.txt`/`Makefile` → C/C++. Ask user if unknown.

## Execute Steps Directly

### 1. Verify GitHub Remote
```bash
git remote -v | grep github.com
```

### 2. Run Quality Gates (All Must Pass)

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
if grep -q "lint" package.json; then npm run lint; else npx eslint . --max-warnings 0 2>/dev/null; fi
if grep -q "format:check" package.json; then npm run format:check; else npx prettier --check . 2>/dev/null; fi
npm test
```

**Go:**
```bash
go fmt ./... && go vet ./... && go test ./... && go build ./...
```

**Java (Maven):**
```bash
mvn checkstyle:check && mvn test && mvn package
```

**Java (Gradle):**
```bash
./gradlew checkstyleMain && ./gradlew test && ./gradlew build
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

If any fail: report errors, ask user to fix before proceeding.

### 3. Review Changes
```bash
git status && git diff
```

### 4. Create GitHub Issue
```bash
gh issue create --title "<type>: <brief description>" --body "## Summary\n\n## Changes\n\n## Test Coverage"
```
Types: feat, fix, docs, refactor, test, chore. Capture issue number.

### 5. Create Feature Branch
```bash
git checkout -b feature/<requirement-id>-short-description
# or
git checkout -b feature/<type>-short-description
```

### 6. Stage and Commit
```bash
git add <relevant-files>
git commit -m "<type>: <description>

<detailed description>

Closes #<issue-number>"
```
**CRITICAL:** No Co-Authored-By line.

### 7. Push to GitHub (Automatic after quality gates pass)
```bash
git push -u origin $(git branch --show-current)
```

### 8. Create Pull Request (Automatic after push)
```bash
gh pr create --title "<type>: <brief description>" --body "## Summary\n\n## Changes\n\nCloses #<issue-number>"
```

## Red Flags - STOP

- [ ] Quality checks failed
- [ ] No GitHub issue linked
- [ ] Commit missing `Closes #<issue-number>`
- [ ] Commit has Co-Authored-By line
- [ ] Branch not `feature/<type>-*` or `feature/<requirement-id>-*`
- [ ] Pushing to main/master or non-GitHub remote