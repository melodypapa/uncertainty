# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Claude Code plugin repository called "uncertainty" that provides reusable skills for automation workflows. The plugin is published to the Claude Code marketplace and includes skills for GitHub workflow management and ISO 29148 requirements engineering.

## Plugin Structure

```
.claude-plugin/
├── plugin.json          # Plugin manifest (owner, description, plugins list)
└── marketplace.json     # Marketplace metadata (author, repo, license)

skills/
├── README.md            # Skill development guidelines
├── github-workflow/     # Pre-push workflow skill
│   └── SKILL.md         # Skill definition with frontmatter
└── sync-req/            # Requirements engineering skill
    └── SKILL.md         # Skill definition with frontmatter
```

## Skill Development Workflow

This project follows the **TDD approach for skills**:

1. **RED Phase** - Run baseline scenarios WITHOUT the skill using subagents, document exact behavior and rationalizations
2. **GREEN Phase** - Write minimal skill addressing specific baseline failures, verify agents comply
3. **REFACTOR Phase** - Close loopholes, identify new rationalizations, add explicit counters, re-test until bulletproof

### Skill Frontmatter Requirements

Each SKILL.md must have YAML frontmatter:
```yaml
---
name: skill-name-with-hyphens
description: Use when [specific triggering conditions and symptoms]
---
```

- `name`: Only letters, numbers, hyphens (no parentheses/special chars)
- `description`: Third person, starts with "Use when...", includes specific triggers, max 1024 characters

## Available Skills

### github-workflow

Triggers when user has staged files ready to push to a feature branch or asks about proper commit workflow.

**Auto-detects project type** from config files:
- Python: `pyproject.toml`, `requirements.txt`, `setup.py`
- JS/TS: `package.json`, `tsconfig.json`
- Go: `go.mod`
- Java: `pom.xml`, `build.gradle`, `build.gradle.kts`
- C/C++: `CMakeLists.txt`, `Makefile`

**Quality gates by language:**
- Python: `ruff check`, `mypy`, `pytest`, `pip install -e .`
- JS/TS: `eslint`, `prettier`, `npm test`
- Go: `go fmt`, `go vet`, `go test`, `go build`
- Java (Maven): `mvn checkstyle:check`, `mvn test`, `mvn package`
- Java (Gradle): `./gradlew checkstyleMain`, `./gradlew test`, `./gradlew build`
- C/C++: `cmake --build build`, `ctest --test-dir build`, `clang-format --dry-run`

**Commit format:** `<type>: <description>` with `Closes #<issue-number>` reference. No Co-Authored-By lines.

**Branch naming:** `feature/<type>-short-description` or `feature/<requirement-id>-short-description`

### sync-req

Triggers when user mentions requirements specification, ISO standards, or needs to document what code implements.

**Supports two workflows:**
- **Reverse engineering**: Extract requirements from code (Python, JS/TS, Go, Java, C/C++)
- **Forward engineering**: Create requirements from user stories

**Output formats:** Markdown (.md), Excel (.xlsx), DOORS-compatible CSV

**ISO 29148 sections:** Functional, Non-Functional, Interface, Data, Verification Criteria

## Testing and Evaluation

Skills should be tested using TDD approach with subagents. The `github-workflow-workspace/` directory contains local test workspaces (gitignored) for structured evaluation including baseline scenarios without skills, iterations with skills, and benchmarking analysis.

## Plugin Publishing

To publish updates to Claude Code marketplace:

1. Update version in `.claude-plugin/marketplace.json`
2. Update version in `.claude-plugin/plugin.json` (if applicable)
3. Commit changes to main branch
4. Claude Code marketplace will auto-discover via the plugin.json structure

## Important Conventions

- Skills are invoked via the `Skill` tool, never by reading SKILL.md directly
- Skill descriptions must never summarize workflow - only describe triggering conditions
- All skill development follows TDD process with subagent testing
- Rationalization is the enemy of reliable skills - be explicit in instructions
- Use Graphviz dot syntax for flowcharts in skills
- Follow the skill specification at https://agentskills.io/specification

## When Working on This Repository

- **Adding a new skill:** Create directory under `skills/`, run `/superpowers:writing-skills`
- **Testing an existing skill:** Use subagents in `github-workflow-workspace/` following TDD phases
- **Updating plugin metadata:** Edit `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json`
- **Reviewing skill behavior:** Read the SKILL.md files - they contain complete workflow definitions