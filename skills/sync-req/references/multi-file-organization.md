# Multi-File Organization

This reference covers how to organize requirements across multiple files when a single file becomes too large.

## When to Split into Multiple Files

| Situation | Action |
|-----------|--------|
| > 100 requirements | Split by feature or type |
| > 500 KB file size | Split into multiple files |
| Multiple distinct features | Create feature-specific files |
| Different teams own parts | Split by team responsibility |
| Single cohesive feature | Keep in single file |

## Split by Type

```
docs/requirement/
├── index.md
├── functional_requirements.md    # REQ-001 to REQ-050
├── non_functional_requirements.md # REQ-NFR-001 to REQ-NFR-020
├── interface_requirements.md      # REQ-IF-001 to REQ-IF-015
├── data_requirements.md           # REQ-DR-001 to REQ-DR-010
└── traceability_matrix.md
```

## Split by Feature

```
docs/requirement/
├── index.md
├── auth_requirements.md           # Authentication feature
├── user_profile_requirements.md   # User profile feature
├── payment_requirements.md        # Payment processing
├── reporting_requirements.md      # Reporting feature
├── security_requirements.md        # Cross-cutting security
└── traceability_matrix.md
```

## Index.md Template

```markdown
# Requirements Index

This directory contains the ISO 29148 compliant requirements for [Project Name].

## Quick Navigation

- [Functional Requirements](functional_requirements.md) - [X requirements]
- [Non-Functional Requirements](non_functional_requirements.md) - [X requirements]
- [Interface Requirements](interface_requirements.md) - [X requirements]
- [Data Requirements](data_requirements.md) - [X requirements]
- [Traceability Matrix](traceability_matrix.md)

## Statistics

- Total Requirements: X
- Implemented: X
- Draft: X
- Last Updated: YYYY-MM-DD
```

## Multi-File Best Practices

- Always create `index.md` with navigation links
- Keep traceability matrix in a separate file
- Maintain consistent requirement numbering across files or use per-file prefixes
- Include cross-file dependencies in Dependencies/Dependants fields
- Update index when adding/removing files
