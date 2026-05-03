# CODEBUDDY.md

This file provides guidance to CodeBuddy Code when working with code in this repository.

## Project Overview

Claude Code plugin "uncertainty" — reusable skills for automation workflows. Published to the Claude Code marketplace. Two skills: `github-workflow` (pre-push quality gates) and `sync-req` (ISO 29148 requirements engineering).

## Commands

### Lint and validate skills
```bash
npx skills-check lint skills/<skill-name>
npx skills-check audit skills/<skill-name>
npx skills-check budget skills/<skill-name>
```

### Run skill evaluations
```bash
# GitHub workflow skill
python skills/github-workflow/github-workflow-workspace/iteration-6/verify_evals.py

# Sync-req skill — manual subagent-driven evaluation in workspace dirs
```

### Install skills locally (for testing)
```bash
npx skills install github:melodypapa/uncertainty
npx skills install github:melodypapa/uncertainty --skills github-workflow
```

## Architecture

### Plugin structure
```
.claude-plugin/
├── plugin.json          # Plugin manifest (name, version, author)
└── marketplace.json     # Marketplace metadata

skills/
├── README.md            # Skill development guidelines + TDD process
├── github-workflow/     # Pre-push workflow skill
│   ├── SKILL.md         # Skill definition with frontmatter
│   ├── evals.json       # Test cases and assertions
│   └── github-workflow-workspace/  # Test workspace (gitignored)
└── sync-req/            # Requirements engineering skill
    ├── SKILL.md         # Skill definition with frontmatter
    ├── evals.json       # Test cases and assertions
    ├── iso-29148.md     # ISO standard reference
    ├── requirements.md  # Requirements template
    ├── doors-csv-format.md / doors-csv-template.csv  # DOORS export format
    ├── tools/           # Supporting scripts
    └── sync-req-workspace/  # Test workspace (gitignored)
```

### Key concepts

- **Skills are Markdown-driven**: Each skill is a `SKILL.md` file with YAML frontmatter + instructions. Skills are invoked via the `Skill` tool, never by reading SKILL.md directly.
- **Frontmatter format**: `name` (hyphens only, no special chars), `description` (third person, starts with "Use when...", max 1024 chars, describes triggers NOT workflow).
- **Workspaces are gitignored**: Test workspaces (`*-workspace/`) contain iterations and evals for TDD but are excluded from the repo.
- **Test workspace structure**: `iteration-N/` folders with `eval-X/` subdirs, each having `with_skill/` and `without_skill/` directories. Benchmark files compare results.

### Skill development workflow (TDD)

1. **RED** — Run baseline WITHOUT skill using subagents, document behavior and rationalizations
2. **GREEN** — Write minimal skill addressing specific failures, verify agents comply
3. **REFACTOR** — Close loopholes, add explicit counters, re-test until bulletproof

Use `/superpowers:writing-skills` when creating new skills.

### CI/CD

`.github/workflows/skill-quality.yml` runs on pushes/PRs touching `skills/**`:
- **Lint**: `npx skills-check lint` on changed skills
- **Audit**: `npx skills-check audit` for security
- **Budget**: `npx skills-check budget` for context window budget
- **Secrets scan**: Checks for hardcoded keys, shell injection, unsafe exec patterns

### Publishing

1. Update version in `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json`
2. Commit to main — marketplace auto-discovers via plugin.json

## Conventions

- Skill descriptions only describe triggering conditions, never summarize the workflow
- Rationalization is the enemy — skill instructions must be explicit
- Use Graphviz dot syntax for flowcharts in SKILL.md
- Commit format: `<type>: <description>` with `Closes #<issue-number>`, no Co-Authored-By
- Skill spec: https://agentskills.io/specification
- New skills go in `skills/<name>/` with a `SKILL.md` (required) and optional supporting files
