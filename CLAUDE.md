# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Claude Code plugin "uncertainty" — reusable skills for automation workflows. Published to Claude Code marketplace. Skills: GitHub workflow management, ISO 29148 requirements engineering.

## Plugin Structure

```
.claude-plugin/
├── plugin.json          # Plugin manifest
└── marketplace.json     # Marketplace metadata

skills/
├── README.md            # Skill development guidelines + TDD process
├── github-workflow/     # Pre-push workflow skill
│   └── SKILL.md
└── sync-req/            # Requirements engineering skill
    └── SKILL.md
```

## Skill Frontmatter Requirements

```yaml
---
name: skill-name-with-hyphens
description: Use when [specific triggering conditions and symptoms]
---
```

- `name`: Only letters, numbers, hyphens (no parentheses/special chars)
- `description`: Third person, starts with "Use when...", max 1024 chars

## Skill Development Workflow (TDD for Skills)

1. **RED** — Run baseline WITHOUT skill using subagents, document behavior + rationalizations
2. **GREEN** — Write minimal skill addressing specific failures, verify agents comply
3. **REFACTOR** — Close loopholes, add explicit counters, re-test until bulletproof

Details in `skills/README.md`. Use `/superpowers:writing-skills` for new skills.

## Testing and Evaluation

Test workspaces (gitignored, not in repo):
- `skills/github-workflow/github-workflow-workspace/` — iterations (iter-1/, iter-2/, ...), evals (eval-0/, eval-1/, ...), benchmarks
- `sync-req-workspace/` — same structure for sync-req skill

Each eval has `with_skill/` and `without_skill/` dirs. Benchmark files compare them.

**Running tests:** Dispatch subagents to execute skill scenarios in test workspaces. No automated test runner — evaluation is manual/subagent-driven.

## Important Conventions

- Invoke skills via `Skill` tool, never read SKILL.md directly
- Skill descriptions only describe triggering conditions, never summarize workflow
- Rationalization is the enemy — be explicit in instructions
- Graphviz dot syntax for flowcharts
- Skill spec: https://agentskills.io/specification
- Commit format: `<type>: <description>` with `Closes #<issue-number>`, no Co-Authored-By

## Plugin Publishing

1. Update version in `.claude-plugin/marketplace.json` and `plugin.json`
2. Commit to main
3. Marketplace auto-discovers via plugin.json

## Quick Reference

- **New skill:** `mkdir skills/<name>` + `/superpowers:writing-skills`
- **Test skill:** Subagents in workspace dirs following TDD phases
- **Review skill:** Read the SKILL.md file