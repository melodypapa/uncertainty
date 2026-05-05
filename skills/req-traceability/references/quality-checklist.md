# Quality Checklist

**Purpose:** Detailed checklist for ensuring workflow compliance.

**Load this file when:** You need to verify all steps are completed correctly.

---

## Pre-Work Checklist

**BEFORE YOU DO ANYTHING ELSE:**
- [ ] **Completed Step 1** - Confirmed workflow scope
- [ ] **Completed Step 2** - Got explicit Yes/No for requirements and test cases

---

## Requirements Path Checklist

**Only if Step 2 Q1 = Yes:**

- [ ] **Confirmed requirements source** - From code or from scratch
- [ ] **If from code:** Loaded `references/requirements-extraction.md` and will execute Phase 1
- [ ] **If from scratch:** Loaded `references/requirements-creation.md`, Phase 1 skipped, Phase 2 starts with user input
- [ ] **Asked "Where would you like to save the requirements?"** - Only if creating/regenerating requirements
- [ ] **Asked about file name prefix (Step 2b-1)** - SWR, custom, or none
- [ ] **Waited for user response**
- [ ] **Checked if requirements file exists**
- [ ] **Created backup if needed**
- [ ] **Got explicit confirmation for overwrite**
- [ ] **Determined file organization**

---

## Test Cases Path Checklist

**Only if Step 2 Q2 = Yes:**

- [ ] **Asked "Where would you like to save the test cases?"** - Only if creating/regenerating test cases
- [ ] **Asked about file name prefix (Step 2e-1)** - UTS, ITS, SYTS, ATS, custom, or none
- [ ] **Waited for user response**
- [ ] **Checked if test cases file exists**
- [ ] **Created backup if needed**
- [ ] **Got explicit confirmation for overwrite**

---

## Output Quality Checklist

**Requirements output:**
- [ ] Each requirement has unique ID in `{PREFIX}_{CATEGORY}_#####` format
- [ ] Each requirement has Description field
- [ ] Each requirement has Implementation field (file:line format)
- [ ] Each requirement has Verification Criteria
- [ ] Each requirement has Status field
- [ ] Each requirement has Last Validated date
- [ ] Each requirement has Last Changed date
- [ ] Document header includes Output Path
- [ ] Traceability Matrix is included

**Test specifications output:**
- [ ] Each test spec has unique ID in `{PREFIX}_{CATEGORY}_#####` format
- [ ] Each test spec has Traces-To field linking to requirement
- [ ] Each test spec has Test Design Technique
- [ ] Each test spec has Test Conditions
- [ ] Each test spec has Coverage Items
- [ ] Each test spec has Test Cases
- [ ] Coverage Matrix is included

---

## Security Checklist

**Before saving any file:**
- [ ] Path validated (no traversal, no system directories)
- [ ] No hardcoded secrets detected
- [ ] No injection patterns in verification criteria
- [ ] Backup created if overwriting existing file

---

## Common Pitfalls Checklist

**Workflow pitfalls:**
- [ ] Did NOT ask file location before confirming user wants the work
- [ ] Did NOT proceed with requirements if user said "No" to Q1
- [ ] Did NOT proceed with test cases if user said "No" to Q2
- [ ] Did NOT assume requirements always come from code
- [ ] Did NOT skip Step 1 or make assumptions about user's intent
- [ ] Did NOT skip test derivation for functional requirements

**Output pitfalls:**
- [ ] Used "Implementation:" not "Source:"
- [ ] Included "Last Validated:" and "Last Changed:" dates
- [ ] Included Output Path in document header
- [ ] Created backup before overwriting
- [ ] Split files if >100 requirements

**Security pitfalls:**
- [ ] Rejected paths with directory traversal
- [ ] Blocked access to system directories
- [ ] Detected and replaced hardcoded secrets
- [ ] Flagged injection vulnerabilities
