# Skills Directory

This directory contains custom skills for Claude Code.

## How to Create a Skill

**IMPORTANT: Follow the TDD process - test before writing!**

1. **RED Phase** - Run baseline scenario WITHOUT skill
   - Create pressure scenarios
   - Document exact behavior and rationalizations
   - Use subagents to test

2. **GREEN Phase** - Write minimal skill
   - Address specific baseline failures
   - Verify agents comply

3. **REFACTOR Phase** - Close loopholes
   - Identify new rationalizations
   - Add explicit counters
   - Re-test until bulletproof

## Skill Structure

```
skill-name/
  SKILL.md              # Main reference (required)
  supporting-file.*     # Only if needed (tools, reference docs)
```

## Required SKILL.md Frontmatter

```yaml
---
name: skill-name-with-hyphens
description: Use when [specific triggering conditions and symptoms]
---
```

**Rules:**
- `name`: Only letters, numbers, hyphens (no parentheses/special chars)
- `description`: Third person, starts with "Use when...", includes specific triggers/symptoms, NEVER summarizes workflow
- Max 1024 characters total in frontmatter

## Example Template

```markdown
---
name: example-skill
description: Use when encountering [specific problem] with [symptoms like error X, situation Y]
---

# Skill Name

## Overview
Core principle in 1-2 sentences.

## When to Use
[Small flowchart IF decision non-obvious]

- Symptom 1: Description
- Symptom 2: Description
- Situation: Description

**NOT for:** When [alternative condition]

## Core Pattern
```python
# Before
bad_code()

# After
good_code()
```

## Quick Reference
| Operation | How |
|-----------|-----|
| Common task | Command |

## Common Mistakes
| Mistake | Fix |
|---------|-----|
| Did X | Do Y instead |

## Red Flags - STOP
- [ ] Red flag 1
- [ ] Red flag 2
```

## Getting Started

Run `/superpowers:writing-skills` for complete documentation on skill creation including:
- Testing methodology with subagents
- Bulletproofing against rationalization
- Claude Search Optimization (CSO)
- Anti-patterns to avoid

## Resources

- Skill spec: https://agentskills.io/specification
- Test methodology: @superpowers/marketplace/superpowers/5.0.6/skills/writing-skills/testing-skills-with-subagents.md
- Graphviz conventions: @superpowers/marketplace/superpowers/5.0.6/skills/writing-skills/graphviz-conventions.dot

## Available Skills

### iso-requirements

Generate ISO/IEC/IEEE 29148:2018 compliant software requirements from code implementation or manual entry.

**Features:**
- Reverse engineering: Extract requirements from code
- Forward engineering: Create requirements from scratch
- Multi-format output: Markdown, Excel, DOORS-compatible CSV
- Multi-language support: Python, JavaScript/TypeScript, Go, Java, C/C++

**Usage:**
When you need to create requirements specifications, document what code implements, or generate DOORS import files, Claude will automatically invoke this skill.