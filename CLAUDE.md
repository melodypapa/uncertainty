# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Claude Code plugin **uncertainty** (`uncertainty-skills` v1.1.0) — reusable skills for automation workflows. Published to Claude Code marketplace. Two skills: GitHub workflow management, ISO 29148 requirements engineering.

## Skill Structure

```
skills/<skill-name>/
├── SKILL.md                 # Main skill definition (required)
├── evals/evals.json         # Test cases with prompts + assertions
├── references/              # On-demand reference docs (req-traceability only)
├── tools/                   # Utility scripts (req-traceability only, empty)
└── <skill-name>-workspace/  # Test workspace (gitignored via *-workspace/)
```

Two skills:
- **github-workflow** (`skills/github-workflow/`) — Pre-push quality gates, branch setup, commit/push/PR workflow
- **req-traceability** (`skills/req-traceability/`) — ISO 29148 requirements engineering, traceability, test derivation

## Commands

### Skill Validation

```bash
# Validate skill metadata, security, and token budget
npx skills-check audit,lint,budget ./skills/<skill-name>

# CI-equivalent check (used in .github/workflows/skill-quality.yml)
npx skills-check check,audit,lint,budget --audit-fail-on high --budget-max-tokens 50000
```

### Eval Runner

```bash
# Setup eval directory structure
python skills/eval_runner.py <skill-name> <iteration> --setup

# Grade existing eval outputs against assertions
python skills/eval_runner.py <skill-name> <iteration> --grade

# Aggregate results into benchmark.json
python skills/eval_runner.py <skill-name> <iteration> --aggregate

# Show completion status
python skills/eval_runner.py <skill-name> <iteration> --status
```

Examples:
```bash
python skills/eval_runner.py req-traceability 2 --setup
python skills/eval_runner.py req-traceability 2 --grade --aggregate
python skills/eval_runner.py req-traceability 2 --status
```

### Plugin Publishing

1. Update version in `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json`
2. Commit to main
3. Marketplace auto-discovers via plugin.json

## CI Pipeline

`.github/workflows/skill-quality.yml` runs on:
- Push/PR to main modifying `skills/**/SKILL.md`
- Weekly schedule (Monday 9am)
- Manual trigger via `workflow_dispatch`

Jobs:
1. **skills-check** — Runs `audit,lint,budget` via `voodootikigod/skills-check@v1` (fail on high-severity audit issues, >50k tokens)
2. **secrets-scan** — Greps SKILL.md files for hardcoded secrets, shell injection patterns (`$()`, backtick `${}`), unsafe exec (`exec`, `eval`, `os.system`, `subprocess.shell/call`)
3. **summary** — Aggregates results into step summary

## Skill Development (TDD)

1. **RED** — Run baseline WITHOUT skill using subagents, document behavior + rationalizations
2. **GREEN** — Write minimal SKILL.md addressing specific failures, verify agents comply
3. **REFACTOR** — Close loopholes, add explicit counters, re-test until bulletproof

Details in `skills/README.md`. Use `/superpowers:writing-skills` for new skills.

## Eval Workspace Convention

```
skills/<skill-name>/<skill-name>-workspace/
├── iteration-1/
│   ├── eval-<id>/
│   │   ├── with_skill/outputs/   # Skill-aided agent output
│   │   ├── without_skill/outputs/# Baseline agent output
│   │   ├── timing.json
│   │   └── grading.json
│   ├── benchmark.json
│   └── benchmark.md
└── iteration-2/
```

All `*-workspace/` dirs gitignored at root level. Workspace MUST go inside skill dir at `skills/<skill>/<skill>-workspace/`.

## Critical Rules

- **Never read SKILL.md directly** — invoke skills via `Skill` tool (system handles loading)
- **Never commit to main** — always feature branch + PR
- **Skill frontmatter**: `name` only `[a-z0-9-]`; `description` third person, starts with "Use when...", max 1024 chars, describes triggers only (never summarizes workflow)
- **Commit format**: `<type>: <description>` with `Closes #<issue-number>`, no `Co-Authored-By`
- **Skill spec**: https://agentskills.io/specification
- **Graphviz dot syntax** for flowcharts

## Quick Reference

| Task | Command |
|------|---------|
| New skill | `mkdir skills/<name>` + `/superpowers:writing-skills` |
| Test skill | Subagents in workspace dirs per TDD phases |
| Review skill | Read the SKILL.md file |
| Full agent instructions | `AGENTS.md` (workspace rules, CI details, commit format) |
