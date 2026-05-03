# CODEBUDDY.md This file provides guidance to CodeBuddy when working with code in this repository.

## Project Overview

Claude Code plugin "uncertainty" — a collection of reusable skills for automation workflows, published to the Claude Code marketplace. Two skills: `github-workflow` (pre-push quality gates and PR workflow) and `sync-req` (ISO 29148 requirements engineering from code).

## Common Commands

### Skill Linting and Quality Checks
```bash
npx skills-check lint skills/<skill-name>     # Lint a single skill
npx skills-check audit skills/<skill-name>     # Security audit (non-blocking)
npx skills-check budget skills/<skill-name>    # Context budget check
```

### Eval Runner (Python)
```bash
python3 skills/eval_runner.py <skill-name> <iteration> --setup      # Create eval directory structure
python3 skills/eval_runner.py <skill-name> <iteration> --grade      # Grade existing outputs against assertions
python3 skills/eval_runner.py <skill-name> <iteration> --aggregate  # Aggregate results into benchmark.json
python3 skills/eval_runner.py <skill-name> <iteration> --status     # Show completion status
```

### Plugin Publishing
Update version in both `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json`, then commit to main. Marketplace auto-discovers via plugin.json.

## Architecture

### Skill Structure
Each skill lives under `skills/<name>/` with `SKILL.md` as the required entry point. Supporting files are organized into subdirectories:

```
skills/<name>/
├── SKILL.md              # Required: YAML frontmatter + skill instructions
├── evals/
│   └── evals.json        # Eval definitions: prompts, assertions
├── assets/               # Static resources (e.g., CSV templates)
├── references/           # Reference docs loaded by skill instructions
└── <name>-workspace/     # Gitignored: eval iteration data
```

The `SKILL.md` frontmatter (`name` + `description`) controls skill discovery and auto-invocation. The `description` field uses "Use when..." format to define triggering conditions — it must never summarize the workflow itself.

### Eval System
Skills are tested via a TDD approach using subagents in workspace directories. The `eval_runner.py` framework manages the lifecycle:

1. **Setup** — Reads `evals/evals.json` and creates `iteration-N/eval-X/{with_skill,without_skill}/outputs/` directories
2. **Execution** — Subagents run each eval prompt with and without the skill, producing output transcripts
3. **Grading** — Assertions (keyword presence, multi-keyword) are checked against outputs; results saved as `grading.json`
4. **Aggregation** — Per-configuration pass rates computed into `benchmark.json` with delta between with/without skill

Evals are structured so each eval has both `with_skill/` and `without_skill/` configurations, enabling direct comparison of skill effectiveness.

### CI Pipeline (`.github/workflows/skill-quality.yml`)
On push/PR to main touching `skills/**`, four jobs run: lint (blocking), audit (non-blocking), context budget check, and secrets/shell-injection/unsafe-exec scanning. Only lint failures block merging.

### Conventions

- **Skill invocation**: Skills are invoked via the `Skill` tool by description matching, never by reading SKILL.md directly
- **Commit format**: `<type>: <description>` with `Closes #<issue-number>`, no Co-Authored-By or AI attribution
- **Flowcharts**: Use Graphviz dot syntax within skill docs
- **Skill descriptions**: Third person, starts with "Use when...", max 1024 chars in frontmatter
- **Rationalization is the enemy**: Skill instructions must be explicit; agents will rationalize around vague rules
- **Skill spec**: https://agentskills.io/specification
