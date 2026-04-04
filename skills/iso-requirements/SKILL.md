---
name: iso-requirements
description: Use when generating ISO/IEC/IEEE 29148:2018 compliant software requirements from code implementation or creating new requirements from scratch. Supports reverse engineering (code to requirements) and forward engineering (manual entry) workflows. Outputs to Markdown, Excel, or DOORS-compatible CSV. Handles multiple languages: Python, JavaScript/TypeScript, Go, Java, C/C++. Triggered when user mentions requirements specification, ISO standards, DOORS import, or need to document what code implements.
---

# ISO 29148 Requirements Engineering

## Overview

Generate ISO/IEC/IEEE 29148:2018 compliant software requirements through bidirectional workflows:
- **Reverse engineering**: Extract requirements from existing code implementation
- **Forward engineering**: Create new requirements from scratch
- **Multi-format output**: Markdown (.md), Excel (.xlsx), DOORS-compatible CSV

Core principle: Transform code semantics or user intent into structured requirements following ISO 29148 standard sections.

## When to Use

```dot
digraph when_flowchart {
    "Need requirements?" [shape=diamond];
    "From existing code?" [shape=diamond];
    "From scratch?" [shape=diamond];
    "Use iso-requirements" [shape=doublecircle];
    "Skip" [shape=box];

    "Need requirements?" -> "From existing code?";
    "From existing code?" -> "Use iso-requirements" [label="yes"];
    "From existing code?" -> "From scratch?";
    "From scratch?" -> "Use iso-requirements" [label="yes"];
    "From scratch?" -> "Skip" [label="no"];
    "Need requirements?" -> "Skip" [label="no"];
}
```

**Use when:**
- User mentions "requirements specification" or "ISO standards"
- Need to document what code implements (reverse engineering)
- Creating new requirements from user stories (forward engineering)
- Need DOORS import format for requirement management tools
- Any language: Python, JavaScript/TypeScript, Go, Java, C/C++

**NOT for:**
- Simple code summaries without ISO structure
- Non-technical documentation
- Requirements outside software engineering scope
