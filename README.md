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

### xdm-schema-req

Generate structured software requirements markdown from EB Tresos XDM schema files for AUTOSAR model-layer documentation.

**Features:**
- XDM schema extraction to compact JSON (~10x smaller than raw XML)
- Type mapping: schema types → Python class types
- Numbered requirements (`SWR_<MODULE_ABBR>_MODELS_<NNNNN>`) per model class
- MAP containers, choice containers, sub-containers, root module class
- Traceability table linking requirements to implementation and test cases
- Handles ENABLE conditions, RANGE constraints, ENUM defaults, ORIGIN tracking
- Skip disabled fields, include conditional fields without annotation

## Installation

### Using npx skills (Recommended)

Install skills directly into your project:

```bash
# Install all skills from this repository
npx skills install github:melodypapa/uncertainty

# Or install specific skills
npx skills install github:melodypapa/uncertainty --skills github-workflow
npx skills install github:melodypapa/uncertainty --skills req-traceability
npx skills install github:melodypapa/uncertainty --skills xdm-schema-req
```

### Manual Installation

Copy skills to your project:

```bash
# Clone the repository
git clone https://github.com/melodypapa/uncertainty.git

# Copy specific skills to your project
cp -r uncertainty/skills/github-workflow /path/to/your/project/skills/
cp -r uncertainty/skills/req-traceability /path/to/your/project/skills/
cp -r uncertainty/skills/xdm-schema-req /path/to/your/project/skills/
```

### Verify Installation

```bash
# List installed skills
npx skills list

# Check skill details
npx skills show github-workflow
npx skills show req-traceability
npx skills show xdm-schema-req
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
├── req-traceability/
│   ├── SKILL.md           # Main skill definition
│   ├── evals/
│   │   └── evals.json     # Test cases and assertions
│   ├── references/        # Reference documentation
│   │   ├── iso-29148.md
│   │   ├── test-design-techniques.md
│   │   ├── test-spec-template.md
│   │   └── security-checks.md
│   └── tools/             # Utility scripts
│       └── extract_requirements.py
└── xdm-schema-req/
    ├── SKILL.md           # Main skill definition
    ├── evals/
    │   ├── evals.json     # Test cases and assertions
    │   └── trigger_evals.json  # Trigger condition tests
    ├── references/        # Type mapping and anti-patterns
    ├── scripts/           # XDM schema extractor
    └── templates/         # Requirements output templates
```

Each skill is a self-contained directory with:
- `SKILL.md` - Main reference document with frontmatter (required)
- `evals/evals.json` - Test cases for verification
- `references/` - Supporting documentation (loaded as needed)
- `scripts/` - Utility/automation scripts (optional)
- `templates/` - Output templates (optional)

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
- **xdm-schema-req**: Triggers when you need to:
  - Generate requirements documents from XDM schema files
  - Create or update SWR_*_MODELS.md documentation
  - Extract AUTOSAR configuration parameter specifications
  - Analyze EB Tresos schema definitions for structured output

## Development

### Testing Skills

Each skill includes evaluation tests in `evals/evals.json` (and optionally `trigger_evals.json` for trigger-condition testing):

```bash
# Validate skill passes all checks
npx skills-check lint ./skills/<skill-name>
npx skills-check budget ./skills/<skill-name>
```

Validation uses subagents in gitignored workspaces at `skills/<skill-name>/<skill-name>-workspace/`.

### Evals Structure

Each eval in `evals.json` contains:
- `id`: Unique identifier
- `prompt`: Test prompt to evaluate
- `expected_output`: Description of expected behavior
- `assertions`: List of assertion objects with `id` and `text`

```json
{
  "skill_name": "example-skill",
  "evals": [
    {
      "id": 1,
      "prompt": "User's task prompt...",
      "expected_output": "Description of expected result",
      "files": [],
      "assertions": [
        {"id": "output-exists", "text": "Output file is generated"}
      ]
    }
  ]
}
```

Skills may also include `trigger_evals.json` for testing when the skill should or should not trigger, using `should_trigger: true/false` queries.

### Creating New Skills

See `skills/README.md` for the TDD methodology (RED → GREEN → REFACTOR) and frontmatter requirements.

## License

MIT License - see [LICENSE](LICENSE)

## Contributing

Contributions welcome! Ensure skills are tested with subagents before submitting.

## Resources

- [Skill Specification](https://agentskills.io/specification)
- [Claude Code Documentation](https://docs.anthropic.com/claude-code)
