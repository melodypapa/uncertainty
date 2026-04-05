# Skills Collection

A collection of reusable skills for Claude Code automation workflows.

## About

This project contains skills that automate common development workflows, ensuring consistency and quality across projects.

## Skills

### github-workflow

Complete preparation workflow before pushing staged files to a feature branch.

**Features:**
- Quality gates (language-specific: ruff/mypy/pytest for Python, ESLint/Prettier/Jest for JS/TS, go fmt/go vet/go test for Go, Maven/Gradle test for Java, clang-format/clang-tidy for C/C++)
- Auto-detects project type from config files
- Auto-discovers source directories (handles missing src/, tools/ dirs)
- GitHub issue creation
- Feature branch setup with proper naming
- Proper commit formatting (feat/fix types with issue references, no Co-Authored-By)
- **Automatic push to GitHub** when all quality gates pass
- GitHub-only pushes (verifies remote is GitHub.com)

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

## License

MIT License - see [LICENSE](LICENSE)

## Contributing

Contributions welcome! Ensure skills are tested with subagents before submitting.