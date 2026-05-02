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
- Automatic push to GitHub when all quality gates pass
- GitHub-only pushes (verifies remote is GitHub.com)

### sync-req

Generate ISO/IEC/IEEE 29148:2018 compliant software requirements from code implementation or manual entry.

**Features:**
- Reverse engineering: Extract requirements from code
- Forward engineering: Create requirements from scratch
- Multi-format output: Markdown, Excel, DOORS-compatible CSV
- Multi-language support: Python, JavaScript/TypeScript, Go, Java, C/C++

## Installation

### Using npx skills (Recommended)

Install skills directly into your project:

```bash
# Install all skills from this repository
npx skills install github:melodypapa/uncertainty

# Or install specific skills
npx skills install github:melodypapa/uncertainty --skills github-workflow
npx skills install github:melodypapa/uncertainty --skills sync-req
```

### Manual Installation

Copy skills to your project:

```bash
# Clone the repository
git clone https://github.com/melodypapa/uncertainty.git

# Copy specific skills to your project
cp -r uncertainty/skills/github-workflow /path/to/your/project/skills/
cp -r uncertainty/skills/sync-req /path/to/your/project/skills/
```

### Verify Installation

```bash
# List installed skills
npx skills list

# Check skill details
npx skills show github-workflow
npx skills show sync-req
```

## Skill Structure

```
skills/
├── README.md
├── github-workflow/
│   ├── SKILL.md           # Main skill definition
│   └── evals.json         # Test cases and assertions
└── sync-req/
    ├── SKILL.md           # Main skill definition
    ├── evals.json         # Test cases and assertions
    ├── iso-29148.md       # ISO standard reference
    ├── requirements.md    # Requirements template
    └── doors-csv-format.md # DOORS import format
```

Each skill is a self-contained directory with:
- `SKILL.md` - Main reference document with frontmatter (required)
- `evals.json` - Test cases for verification
- Supporting files (reference docs, templates)

## Usage

Skills are automatically invoked by Claude Code based on their descriptions:

- **github-workflow**: Triggers when you have staged files ready to push, need pre-push quality checks, or ask about committing/pushing to GitHub
- **sync-req**: Triggers when you need to create requirements specifications, document what code implements, or generate DOORS import files

## Development

### Testing Skills

```bash
# Run skill evaluations
cd skills/github-workflow
python github-workflow-workspace/iteration-6/verify_evals.py
```

### Creating New Skills

See [skills/README.md](skills/README.md) for the complete guide on creating skills following TDD methodology.

## License

MIT License - see [LICENSE](LICENSE)

## Contributing

Contributions welcome! Ensure skills are tested with subagents before submitting.

## Resources

- [Skill Specification](https://agentskills.io/specification)
- [Claude Code Documentation](https://docs.anthropic.com/claude-code)
