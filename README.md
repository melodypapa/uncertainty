# Skills Collection

A collection of reusable skills for Claude Code automation workflows.

## About

This project contains skills that automate common development workflows, ensuring consistency and quality across projects.

## Skills

### github-workflow

Complete preparation workflow before pushing staged files to a feature branch.

**Features:**
- Quality gates (ruff, mypy, pytest, pip install)
- GitHub issue creation
- Feature branch setup
- Proper commit formatting
- GitHub-only pushes (no gitee)

**Usage:**
When you have staged files ready to push, Claude will automatically invoke this skill via description matching.

## Installation

### For Claude Code

Copy skills to your project:

```bash
cp -r skills/github-workflow /path/to/your/project/skills/
```

Or use as a reference to create project-specific skills.

## Skill Structure

```
skills/
├── README.md
└── github-workflow/
    └── SKILL.md
```

Each skill is a self-contained directory with:
- `SKILL.md` - Main reference document with frontmatter
- Supporting files (if needed)

## Creating New Skills

Follow the TDD process for skills:

1. **RED** - Run baseline scenarios WITHOUT skill
2. **GREEN** - Write minimal skill addressing failures
3. **REFACTOR** - Close loopholes and re-test

See `skills/README.md` for detailed guidelines.

## License

MIT License - see [LICENSE](LICENSE)

## Contributing

Contributions welcome! Ensure skills are tested with subagents before submitting.