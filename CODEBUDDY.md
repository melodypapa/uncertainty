# CODEBUDDY.md

This file provides guidance to CodeBuddy Code when working with code in this repository.

## Project Overview

Claude Code plugin "uncertainty" — reusable skills for automation workflows. Published to Claude Code marketplace. Contains two skills:
- **github-workflow**: Pre-push workflow with quality gates, issue creation, and proper commit formatting
- **sync-req**: ISO/IEC/IEEE 29148 requirements engineering with bidirectional traceability

## Skill Development Commands

```bash
# Run evals for a skill
python skills/eval_runner.py <skill_name> <iteration> --setup    # Create eval directories
python skills/eval_runner.py <skill_name> <iteration> --grade     # Grade outputs against assertions
python skills/eval_runner.py <skill_name> <iteration> --aggregate # Aggregate into benchmark.json
python skills/eval_runner.py <skill_name> <iteration> --status    # Check completion status

# CI/CD checks (run before pushing skill changes)
npx skills-check lint skills/<skill-name>    # Validate skill structure
npx skills-check audit skills/<skill-name>   # Security audit
npx skills-check budget skills/<skill-name>  # Context budget check
```

Testing is manual/subagent-driven: dispatch subagents to execute skill scenarios in workspace directories. No automated test runner.

## TDD Workflow for Skills

1. **RED** — Run baseline WITHOUT skill using subagents, document behavior and rationalizations
2. **GREEN** — Write minimal skill addressing specific failures, verify agents comply
3. **REFACTOR** — Close loopholes, add explicit counters, re-test until bulletproof

## Skill Structure

```
skill-name/
├── SKILL.md              # Main skill definition (required)
├── evals.json            # Test cases and assertions
└── supporting-file.*     # Reference docs, templates (optional)
```

### Required SKILL.md Frontmatter

```yaml
---
name: skill-name-with-hyphens
description: Use when [specific triggering conditions and symptoms]
---
```

- `name`: Only letters, numbers, hyphens (no parentheses/special chars)
- `description`: Third person, starts with "Use when...", max 1024 chars, NEVER summarizes workflow

## Architecture

```
.claude-plugin/
├── plugin.json          # Plugin manifest
└── marketplace.json     # Marketplace metadata

skills/
├── README.md            # Skill development guidelines
├── eval_runner.py       # Eval framework (442 lines)
├── github-workflow/     # Pre-push workflow skill (340-line SKILL.md, 13 evals)
│   ├── SKILL.md
│   ├── evals.json
│   └── github-workflow-workspace/  # Gitignored test fixtures
└── sync-req/           # Requirements engineering skill (1535-line SKILL.md, 10 evals)
    ├── SKILL.md
    ├── evals.json
    ├── iso-29148.md
    ├── requirements.md
    ├── doors-csv-format.md
    └── sync-req-workspace/  # Gitignored test workspaces

*-workspace/             # Test workspaces (gitignored, not in repo)
```

## Key Conventions

- Invoke skills via `Skill` tool, never read SKILL.md directly
- Commit format: `<type>: <description>` with `Closes #<issue-number>`, no Co-Authored-By
- Graphviz dot syntax for flowcharts
- Skill descriptions only describe triggering conditions, never summarize workflow
- Rationalization is the enemy — be explicit in instructions
- Skill spec: https://agentskills.io/specification

## Security Features

Both skills include robust security:
- Secrets detection (API_KEY, PASSWORD, TOKEN patterns)
- Path traversal protection
- Shell injection protection
- Phishing domain detection (github-workflow)
- Branch name sanitization (github-workflow)

## Plugin Publishing

1. Update version in `.claude-plugin/marketplace.json` and `.claude-plugin/plugin.json`
2. Commit to main
3. Marketplace auto-discovers via plugin.json

## Quick Reference

| Task | How |
|------|-----|
| New skill | `mkdir skills/<name>` + follow TDD workflow |
| Test skill | Dispatch subagents in workspace dirs |
| Lint skill | `npx skills-check lint skills/<name>` |
| Review skill | Read the SKILL.md file |
| Run evals | `python skills/eval_runner.py <name> <iter> --grade` |
