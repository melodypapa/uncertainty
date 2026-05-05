# AGENTS.md

## Repo Overview
Claude Code plugin `uncertainty-skills` (marketplace: `uncertainty`) with automation skills (GitHub workflow, requirements engineering). No build/lint/test scripts (package.json has no scripts).

## Testing
No automated test runner. All validation uses subagents in gitignored workspaces:
- `skills/<name>/<name>-workspace/` (iter-/eval- splits)
- Each eval has `with_skill/` and `without_skill/` dirs
- Evaluation is manual/subagent-driven

## CI
- Triggers on pushes/PRs to main modifying `skills/**/SKILL.md`
- Runs `skills-check` (audit, lint, budget) + secrets scan for hardcoded credentials/unsafe exec patterns

## Critical Rules
- Never read `SKILL.md` directly — invoke skills via `Skill` tool
- Skill frontmatter: `name` only [a-z0-9-]; `description` third person, starts with "Use when...", max 1024 chars (trigger conditions only, no workflow summary)
- Skill TDD: RED (baseline without skill) → GREEN (minimal fix) → REFACTOR (close loopholes). Details in `skills/README.md`
- Commit format: `<type>: <description>` with `Closes #<issue>`. No `Co-Authored-By`
- **NEVER commit directly to main branch** — Always create a feature branch, then PR for review
- Publishing: Update version in `.claude-plugin/marketplace.json` AND `.claude-plugin/plugin.json` → commit to main

## References
Full conventions: `CLAUDE.md`
Skill creation: `skills/README.md`, `/superpowers:writing-skills`
