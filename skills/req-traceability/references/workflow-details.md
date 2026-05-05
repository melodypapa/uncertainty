# Workflow Details Reference

**Purpose:** Detailed workflow steps for requirements and test case creation.

**Load this file when:** You need detailed step-by-step instructions for the workflow.

---

## Phase Overview

The req-traceability skill operates in 5 phases:

| Phase | Name | Input | Output |
|-------|------|-------|--------|
| **Phase 1** | Code → Requirements | Source code | Draft requirements |
| **Phase 2** | Requirements → Code | User input/specs | Requirements + Implementation plan |
| **Phase 3** | Verification Loop | Requirements + Code | Validated requirements |
| **Phase 4** | Requirements → Test Specs | Requirements | Test specifications |
| **Phase 5** | Traceability Matrix | Requirements + Tests | Coverage report |

### Phase Details

#### Phase 1: Code → Requirements (Extraction)

**When:** User selects "From current code" in Step 2a

**Process:**
1. Scan codebase for functional modules
2. Identify entry points, APIs, data flows
3. Extract behavior from code
4. Create requirement for each behavior
5. Link requirements to code locations

**Output:** Draft requirements with Implementation references

**Reference:** `references/requirements-extraction.md`

---

#### Phase 2: Requirements → Code (Creation)

**When:** User selects "From scratch" in Step 2a

**Process:**
1. Gather user input (user story, spec, description)
2. Identify functional areas
3. Create requirements for each area
4. Define verification criteria
5. Plan implementation locations

**Output:** Requirements with verification criteria

**Reference:** `references/requirements-creation.md`

---

#### Phase 3: Verification Loop

**When:** After requirements are created/extracted

**Process:**
1. Validate each requirement against code
2. Check for orphan code (no requirements)
3. Check for orphan requirements (no code)
4. Identify conflicts (both changed)
5. Update status fields

**Output:** Validated requirements with status

**Reference:** `references/verification-and-traceability.md`

---

#### Phase 4: Requirements → Test Specs

**When:** User answers "Yes" to "Create test cases?"

**Process:**
1. Read requirements
2. Select ISO 29119-4 test design technique
3. Derive test conditions
4. Derive coverage items
5. Derive test cases
6. Create traceability links

**Output:** Test specifications with Traces-To links

**Reference:** `references/test-design-techniques.md`

---

#### Phase 5: Traceability Matrix

**When:** After test specs are created

**Process:**
1. Build requirements ↔ tests mapping
2. Calculate coverage percentage
3. Identify uncovered requirements
4. Identify orphan tests
5. Generate coverage report

**Output:** Traceability matrix and coverage report

---

## Detailed Workflow Steps

### Requirements Path (Steps 2a-2d)

#### Step 2a: Confirm Requirements Source

**If user answered "Yes" to "Extract requirements from current code?":**
- Load `references/requirements-extraction.md`
- Execute Phase 1 (Code → Requirements)

**If user answered "No" to "Extract requirements from current code?":**
- Load `references/requirements-creation.md`
- Ask: "What are the requirements based on? (user story, specification, design document, description)"
- Execute Phase 2 (Requirements → Code)

---

#### Step 2b: Ask Requirements File Location

Ask: **"Where would you like to save the requirements?"**

**User may specify:**
- A specific file path: `docs/requirements/swr_auth_requirements.md`
- A directory: `docs/requirements/`, `custom_docs/`
- An absolute path: `/path/to/output/swr_auth_requirements.md`

**Default:** `docs/requirements/` (if user declines to specify)

---

#### Step 2b-1: Ask File Name Prefix and Category

**Prefix Options:**
- **SWR** (Software Requirements) → `swr_{category}_requirements.md`
- **Custom** → User provides prefix

**Category Detection (Automatic when extracting from code):**
1. Scan code structure for functional areas
2. Detect categories from modules/directories/namespaces
3. Generate separate file for EACH category

**If no category detected:**
- ASK: "What category should these requirements cover?"
- Options: AUTH, USER, PAYMENT, API, Custom

---

#### Step 2c: Check for Existing Requirements

If file exists, ask: "Requirements already exist at [path]. What would you like to do?"
- **Option A:** Replace completely
- **Option B:** Append new requirements
- **Option C:** Update existing
- **Option D:** Create backup first

**CRITICAL:**
- Create backup: `swr_auth_requirements.md.backup_YYYYMMDD_HHMMSS`
- Require explicit confirmation for overwrite

---

#### Step 2d: Determine File Organization

Ask: Single file, split by feature, or split by type?

**When to split:** >100 requirements, multiple features, file size >500 KB

**Reference:** `references/multi-file-organization.md`

---

### Test Cases Path (Steps 2e-2f)

#### Step 2e: Ask Test Cases File Location

Ask: **"Where would you like to save the test cases?"**

**Default by test type:**
- **UTS** → `docs/tests/unit/`
- **ITS** → `docs/tests/integration/`
- **SYTS** → `docs/tests/system/`
- **ATS** → `docs/tests/acceptance/`
- **Custom** → `docs/tests/`

---

#### Step 2e-1: Determine Test Type and Category

**Category Detection (Automatic from requirements):**
1. Scan requirement IDs for pattern: `{PREFIX}_{CATEGORY}_#####`
2. Extract unique categories
3. Generate separate file for EACH category

**If no category detected:**
- ASK: "What category should these test specifications cover?"

**Test Type Selection:**

Ask: **"What type of test specifications? (Select all that apply)"**

| Type | Prefix | Folder |
|------|--------|--------|
| Unit Tests | UTS | `docs/tests/unit/` |
| Integration Tests | ITS | `docs/tests/integration/` |
| System Tests | SYTS | `docs/tests/system/` |
| Acceptance Tests | ATS | `docs/tests/acceptance/` |
| Custom | User-defined | User-specified |

**User can select multiple types.** Generate separate files for each.

---

#### Step 2f: Check for Existing Test Cases

Similar to Step 2c:
- Check if file exists
- Ask: Replace, Append, Update, or Create backup
- Create backup with timestamp
- Require explicit confirmation

---

## File Naming Format

**Requirements:** `{prefix}_{category}_requirements.md` (lowercase)

**Test Specs:** `{prefix}_{category}_test-specs.md` (lowercase)

**Examples:**
- `swr_auth_requirements.md`
- `uts_auth_test-specs.md`
- `its_payment_test-specs.md`
- `syts_user_test-specs.md`
- `ats_auth_test-specs.md`

---

## Security Validation

**MUST validate before saving:**

1. **Path Traversal Protection** - Reject `../`, `..\\`, system directories
2. **Secrets Detection** - Scan for API_KEY, PASSWORD, TOKEN
3. **Injection Protection** - Flag SQL injection, shell injection, eval()

**Reference:** `references/security-checks.md`
