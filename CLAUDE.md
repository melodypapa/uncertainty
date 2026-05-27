# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Claude Code plugin **uncertainty** (`uncertainty-skills` v1.1.0) — reusable skills for automation workflows. Published to Claude Code marketplace. Three skills: GitHub workflow management, ISO 29148 requirements engineering, XDM schema requirements generation.

## Skills

```
skills/<skill-name>/
├── SKILL.md                 # Main skill definition (required)
├── evals/evals.json         # Test cases with prompts + assertions
├── references/              # On-demand reference docs
├── tools/ or scripts/       # Utility scripts
├── templates/               # Output templates (xdm-schema-req)
└── <skill-name>-workspace/  # Test workspace (gitignored via *-workspace/)
```

- **github-workflow** (`skills/github-workflow/`) — Pre-push quality gates, branch setup, commit/push/PR workflow
- **req-traceability** (`skills/req-traceability/`) — ISO 29148 requirements engineering, traceability, test derivation. 17 reference docs, Python tools
- **xdm-schema-req** (`skills/xdm-schema-req/`) — AUTOSAR/EB Tresos XDM schema to requirements markdown. JSON evals + trigger-based evals

## Commands

### Skill Validation

```bash
# CI-equivalent check (used in .github/workflows/skill-quality.yml)
npx skills-check check,audit,lint,budget --audit-fail-on high --budget-max-tokens 50000

# Single skill check
npx skills-check audit,lint,budget ./skills/<skill-name>
```

### Plugin Publishing

1. Update version in `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json`
2. Commit to main (marketplace auto-discovers via plugin.json)

### Workspace Setup

Workspace rules in `AGENTS.md` — see that file for eval directory structure, iteration naming, output conventions. Key rule: always create workspace at `skills/<skill-name>/<skill-name>-workspace/`.

### Plans

Stored in `docs/plans/` — save implementation plans there before multi-step work.

## CI Pipeline

`.github/workflows/skill-quality.yml` runs on:
- Push/PR to main modifying `skills/**/SKILL.md`
- Weekly schedule (Monday 9am)
- Manual trigger via `workflow_dispatch`

Jobs:
1. **skills-check** — `audit,lint,budget` via `voodootikigod/skills-check@v1` (fail on high-severity audit, >50k tokens)
2. **secrets-scan** — Greps SKILL.md for hardcoded secrets, shell injection (`$()`, backtick `${}`), unsafe exec (`exec`, `eval`, `os.system`, `subprocess.shell/call`)
3. **summary** — Aggregates results into step summary

## Marketplace Config

- `.claude-plugin/plugin.json` — Plugin identity (name, version, author). Version bump required before publishing
- `.claude-plugin/marketplace.json` — CLI marketplace listing. Contains display metadata
- `.claude/settings.local.json` — Local permission allowlist for Bash commands (gh, git, npx, python, etc.)

## Skill Development (TDD)

1. **RED** — Run baseline WITHOUT skill using subagents, document behavior + rationalizations
2. **GREEN** — Write minimal SKILL.md addressing specific failures, verify agents comply
3. **REFACTOR** — Close loopholes, add explicit counters, re-test until bulletproof

Details in `skills/README.md`. Use `/superpowers:writing-skills` for new skills.

## Eval Testing

No automated test runner. All validation uses subagents in gitignored workspaces.

Eval format (`evals/evals.json`):
```json
{
  "id": 17,
  "prompt": "...",
  "expected_output": "...",
  "assertions": ["string that must appear", "another required string"]
}
```

xdm-schema-req also has `trigger_evals.json` for trigger-condition testing.

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
| Full workspace rules | `AGENTS.md` (eval structure, iteration naming) |
| Validate skill | `npx skills-check audit,lint,budget ./skills/<name>` |
| Plugin version bump | `.claude-plugin/plugin.json` + `.claude-plugin/marketplace.json` |
| Save plan | `docs/plans/<plan-name>.md` |
