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
- Security checks: secrets detection, branch name sanitization, phishing domain detection

### req-traceability

Generate ISO/IEC/IEEE 29148:2018 compliant software requirements with bidirectional traceability between requirements, code, and tests.

**Features:**
- Reverse engineering: Extract requirements from code
- Forward engineering: Create requirements from scratch
- Multi-format output: Markdown, Excel, DOORS-compatible CSV
- Multi-language support: Python, JavaScript/TypeScript, Go, Java, C/C++
- **Three-layer traceability**: Requirements ↔ Code ↔ Test Specifications
- **Test design derivation**: ISO 29119-4 techniques (Equivalence Partitioning, Boundary Value Analysis, Decision Table Testing, State Transition Testing)
- **Deviation detection**: DRIFT, ORPHAN_CODE, ORPHAN_REQ, TEST_DRIFT, UNCOVERED_REQ, STALE_TEST
- **Coverage analysis**: Test coverage matrix and gap identification
- **Workflow scope selection**: 6 options for different use cases
- **Security validation**: Path traversal protection, secrets detection, injection prevention

## Installation

### Using npx skills (Recommended)

Install skills directly into your project:

```bash
# Install all skills from this repository
npx skills install github:melodypapa/uncertainty

# Or install specific skills
npx skills install github:melodypapa/uncertainty --skills github-workflow
npx skills install github:melodypapa/uncertainty --skills req-traceability
```

### Manual Installation

Copy skills to your project:

```bash
# Clone the repository
git clone https://github.com/melodypapa/uncertainty.git

# Copy specific skills to your project
cp -r uncertainty/skills/github-workflow /path/to/your/project/skills/
cp -r uncertainty/skills/req-traceability /path/to/your/project/skills/
```

### Verify Installation

```bash
# List installed skills
npx skills list

# Check skill details
npx skills show github-workflow
npx skills show req-traceability
```

## npx skills Commands

The `npx skills` CLI provides skill management and discovery capabilities:

### Installation & Management

```bash
# Install skills from GitHub
npx skills install github:owner/repo

# Install specific skills
npx skills install github:owner/repo --skills skill-name

# List installed skills
npx skills list

# Show skill details
npx skills show <skill-name>

# Discover skills in a directory
npx skills install . --list
```

### Skill Information

```bash
# View skill metadata
npx skills show <skill-name>

# Check skill compatibility
npx skills check <skill-name>
```

## npx skills-check Commands

The `npx skills-check` CLI provides quality validation for agent skills — freshness, security, quality, and efficiency.

### Quick Start

```bash
# Initialize registry
npx skills-check init

# Run all checks
npx skills-check check,audit,lint,budget
```

### Commands

| Command | Purpose |
|---------|---------|
| `check` | Detect version drift against npm registry |
| `audit` | Scan for hallucinated packages, prompt injection, dangerous commands |
| `lint` | Validate metadata (YAML frontmatter, required fields) |
| `budget` | Measure token cost per skill |
| `verify` | Validate semver bump matches content changes |
| `test` | Run eval test suites for regression detection |
| `refresh` | AI-assisted updates to stale skills |
| `report` | Generate staleness report (markdown/JSON) |
| `init` | Generate skills-check.json registry |
| `doctor` | Validate environment prerequisites |
| `fix` | Apply deterministic autofixes |

### CI/CD Integration

```bash
# Run with thresholds
npx skills-check check,audit,lint,budget \
  --audit-fail-on high \
  --budget-max-tokens 50000
```

### GitHub Action

```yaml
- uses: voodootikigod/skills-check@v1
  with:
    commands: 'audit,lint,budget'
    audit-fail-on: 'high'
    budget-max-tokens: 50000
```

[Full documentation →](https://www.skillscheck.ai/)

## Skill Structure

```
skills/
├── github-workflow/
│   ├── SKILL.md           # Main skill definition
│   └── evals/
│       └── evals.json     # Test cases and assertions
└── req-traceability/
    ├── SKILL.md           # Main skill definition
    ├── evals/
    │   └── evals.json     # Test cases and assertions
    ├── references/        # Reference documentation
    │   ├── iso-29148.md
    │   ├── test-design-techniques.md
    │   ├── test-spec-template.md
    │   └── security-checks.md
    └── tools/             # Utility scripts
        └── extract_requirements.py
```

Each skill is a self-contained directory with:
- `SKILL.md` - Main reference document with frontmatter (required)
- `evals/evals.json` - Test cases for verification
- `references/` - Supporting documentation (loaded as needed)
- `tools/` - Utility scripts for the skill

## Usage

Skills are automatically invoked by Claude Code based on their descriptions:

- **github-workflow**: Triggers when you have staged files ready to push, need pre-push quality checks, or ask about committing/pushing to GitHub
- **req-traceability**: Triggers when you need to:
  - Create requirements specifications
  - Derive test cases from requirements
  - Analyze test coverage
  - Detect deviations between requirements, code, and tests
  - Generate DOORS import files
  - Maintain bidirectional traceability

## Development

### Testing Skills

Each skill includes evaluation tests in `evals/evals.json`:

```bash
# Validate skill passes all checks
npx skills-check lint ./skills/req-traceability
npx skills-check budget ./skills/req-traceability

# Run eval verification script (if available)
python req-traceability-workspace/iteration-2/test_workflow_scope.py
```

### Evals Structure

Each eval in `evals.json` contains:
- `id`: Unique identifier
- `prompt`: Test prompt to evaluate
- `expected_output`: Description of expected behavior
- `assertions`: List of strings that must appear in output

```json
{
  "id": 17,
  "prompt": "I have a Python authentication module...",
  "expected_output": "A response that asks 'Where would you like to save'...",
  "assertions": ["Where would you like to save", "What would you like to do"]
}
```

### Creating New Skills

See [writing-skills](https://github.com/melodypapa/uncertainty/tree/main/skills/writing-skills) for the complete guide on creating skills following TDD methodology.

## License

MIT License - see [LICENSE](LICENSE)

## Contributing

Contributions welcome! Ensure skills are tested with subagents before submitting.

## Resources

- [Skill Specification](https://agentskills.io/specification)
- [Claude Code Documentation](https://docs.anthropic.com/claude-code)
