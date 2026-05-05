# Test Specification Document Template

**Purpose:** Template for generating test specification documents with traceability to requirements.

---

## Document Header

```markdown
# Test Specification Document

**Output Path:** [user-specified or default path]
**Generated:** [current date YYYY-MM-DD]
**Source Requirements:** [path to requirements.md or list of requirement files]
**Test Design Technique:** [EP | BVA | Decision Table | State Transition | Use Case | Error Guessing | Exploratory]
**Coverage Target:** [e.g., 100% requirements coverage]
**Language:** [Python | JavaScript | TypeScript | Go | Java | C/C++]

## Traceability Summary

| Metric | Count | Percentage |
|--------|-------|------------|
| Total Requirements | [N] | 100% |
| Requirements with Tests | [M] | [M/N × 100%] |
| Requirements without Tests | [N-M] | [(N-M)/N × 100%] |
| Total Test Cases | [T] | - |
| Test Cases Passed | [P] | [P/T × 100%] |
| Test Cases Failed | [F] | [F/T × 100%] |

## Coverage Matrix

| Requirement ID | Test Case IDs | Coverage Status | Last Verified |
|----------------|---------------|-----------------|---------------|
| REQ-001 | TC-001, TC-002, TC-003 | ✅ Covered | YYYY-MM-DD |
| REQ-002 | TC-004, TC-005 | ✅ Covered | YYYY-MM-DD |
| REQ-003 | - | ❌ UNCOVERED | - |
```

---

## Test Specification Entry Template

```markdown
### {PREFIX}_{CATEGORY}_##### : [Test Case Title]

**Type:** [Functional | Non-Functional | Integration | Unit | E2E]
**Priority:** [Critical | High | Medium | Low]
**Status:** [Draft | Ready | Passed | Failed | Blocked | Deprecated]

**Traces-To:** [SWR_{CATEGORY}_#####, SWR_{CATEGORY}_#####] - Requirements this test verifies
**Test Implementation:** [file_path.py:test_function (line:column)] - Actual test code
**Last Validated:** [YYYY-MM-DD]
**Last Changed:** [YYYY-MM-DD]

**Test Design Technique:** [Equivalence Partitioning | Boundary Value Analysis | Decision Table | State Transition | Use Case | Error Guessing | Exploratory]

**Preconditions:**
1. [System state before test]
2. [Required data/setup]
3. [Required configurations]

**Test Steps:**
1. **Given:** [Initial state/context]
2. **When:** [Action performed]
3. **Then:** [Expected outcome]

**Test Data:**
| Input Field | Value | Description |
|-------------|-------|-------------|
| [field1] | [value1] | [description1] |
| [field2] | [value2] | [description2] |

**Expected Results:**
- [Expected behavior 1]
- [Expected behavior 2]
- [Expected output/state]

**Actual Results:** (Filled during test execution)
- [Actual behavior observed]
- [Actual output/state]

**Verification Criteria:**
1. Verify [specific check]
2. Verify [specific check]
3. Verify [specific behavior]

**Rationale:**
[Why this test case exists - what defect it's designed to find]

**Dependencies:**
[{PREFIX}_{CATEGORY}_#####, {PREFIX}_{CATEGORY}_#####] - Tests that must run before this one

**Change Log:**
- [YYYY-MM-DD]: [Description of change, why, impact]
```

---

## Coverage Matrix Template (Detailed)

```markdown
## Requirements to Test Cases Traceability Matrix

| Requirement | Description | Test Cases | Technique | Status | Notes |
|-------------|-------------|------------|-----------|--------|-------|
| REQ-001 | [Brief description] | TC-001, TC-002, TC-003 | EP + BVA | ✅ Covered | Full coverage |
| REQ-002 | [Brief description] | TC-004 | Decision Table | ✅ Covered | Missing error cases |
| REQ-003 | [Brief description] | - | - | ❌ UNCOVERED | No tests derived |
| REQ-004 | [Brief description] | TC-005 | State Transition | ⚠️ Partial | Missing invalid transitions |
| REQ-005 | [Brief description] | TC-006 (DEPRECATED) | - | ❌ STALE_TEST | Test references deleted REQ |

## Test Coverage Gaps

### UNCOVERED_REQ (Requirements without tests)
| Requirement | Priority | Risk | Recommended Action |
|-------------|----------|------|-------------------|
| REQ-003 | High | Critical | Derive tests using [technique] |

### STALE_TEST (Tests referencing deleted requirements)
| Test Case | Deleted Requirement | Recommended Action |
|-----------|---------------------|-------------------|
| TC-006 | REQ-005 (deleted) | Remove test or update reference |

### TEST_DRIFT (Tests not updated after requirement change)
| Test Case | Requirement | Change Date | Recommended Action |
|-----------|-------------|-------------|-------------------|
| UTS_AUTH_00007 | SWR_AUTH_00002 | YYYY-MM-DD | Update test to match new requirement |

### ORPHAN_TEST (Test code without specification)
| Test File | Test Function | Recommended Action |
|-----------|---------------|-------------------|
| test_auth.py | test_oauth_login | Create test specification UTS_AUTH_##### |
```

---

## Test Deviation Report Template

```markdown
# Test Deviation Report

**Generated:** [YYYY-MM-DD HH:MM:SS]
**Requirements File:** [path/to/requirements.md]
**Test Specifications File:** [path/to/test-specs.md]
**Test Code Directory:** [path/to/tests/]

## Executive Summary

| Deviation Type | Count | Severity |
|----------------|-------|----------|
| TEST_DRIFT | [N] | 🔴 High |
| UNCOVERED_REQ | [M] | 🟡 Medium |
| STALE_TEST | [P] | 🟡 Medium |
| ORPHAN_TEST | [Q] | 🟢 Low |

## Detailed Findings

### TEST_DRIFT (Requirement Changed, Test Not Updated)

| Test Case | Requirement | Change Description | Impact | Recommended Action |
|-----------|-------------|-------------------|--------|-------------------|
| TC-007 | REQ-002 | Changed from SHA-256 to bcrypt | Test verifies wrong hash | Update test to use bcrypt |

### UNCOVERED_REQ (Requirements Without Tests)

| Requirement | Priority | Type | Risk Level | Recommended Technique |
|-------------|----------|------|------------|----------------------|
| REQ-003 | High | Functional | Critical | Equivalence Partitioning |
| REQ-008 | Medium | Non-Functional | Medium | Error Guessing |

### STALE_TEST (Tests Referencing Deleted Requirements)

| Test Case | Deleted Requirement | Last Run | Recommended Action |
|-----------|---------------------|----------|-------------------|
| UTS_AUTH_00006 | SWR_AUTH_00005 | YYYY-MM-DD | Remove test case |

### ORPHAN_TEST (Test Code Without Specification)

| Test File | Test Function | Lines | Recommended Action |
|-----------|---------------|-------|-------------------|
| test_auth.py | test_oauth_login | 45-67 | Create UTS_AUTH_##### specification |

## Synchronization Actions

### User Decision Required

The following deviations require user approval before synchronization:

#### Decision 1: Update Requirements from Code?

**Context:** Code has changed but requirements have not been updated.

| Requirement | Code Location | Code Change | User Decision |
|-------------|---------------|-------------|---------------|
| SWR_AUTH_00002 | auth.py:45 | Changed hash algorithm | [ ] Yes, update REQ to match code |
| | | | [ ] No, keep REQ unchanged |

**Impact if Yes:** Requirements will reflect current implementation
**Impact if No:** Code deviation will be flagged for manual review

#### Decision 2: Update Test Cases from Requirements?

**Context:** Requirements have changed but test specifications have not been updated.

| Test Case | Requirement | Requirement Change | User Decision |
|-----------|-------------|-------------------|---------------|
| TC-007 | REQ-002 | Hash algorithm changed | [ ] Yes, regenerate tests |
| | | | [ ] No, keep tests unchanged |

**Impact if Yes:** Test specifications will be regenerated from updated requirements
**Impact if No:** Test deviation will be flagged for manual review

## Recommended Actions

### High Priority (Execute Immediately)

1. **[ACTION-001]** Update TC-007 to use bcrypt instead of SHA-256
   - **Type:** TEST_DRIFT fix
   - **Impact:** Test will correctly verify password hashing
   - **Files:** test_auth.py, test-specs.md

2. **[ACTION-002]** Derive tests for REQ-003 using Equivalence Partitioning
   - **Type:** UNCOVERED_REQ fix
   - **Impact:** 100% requirements coverage achieved
   - **Files:** test-specs.md, test_auth.py

### Medium Priority (Execute This Sprint)

3. **[ACTION-003]** Remove TC-006 (references deleted REQ-005)
   - **Type:** STALE_TEST fix
   - **Impact:** Remove obsolete test
   - **Files:** test-specs.md, test_auth.py

### Low Priority (Backlog)

4. **[ACTION-004]** Create specification for test_oauth_login
   - **Type:** ORPHAN_TEST fix
   - **Impact:** Complete traceability
   - **Files:** test-specs.md

## Next Steps

1. User reviews and approves/disapproves each decision
2. Execute approved synchronization actions
3. Update traceability matrix
4. Run test suite to verify changes
5. Generate post-sync report
```

---

## Test Specification Index Template

For multi-file test specifications:

```markdown
# Test Specifications Index

**Generated:** [YYYY-MM-DD]
**Total Test Specifications:** [N] files

## Files

| File | Module/Feature | Test Cases | Requirements | Status |
|------|----------------|------------|--------------|--------|
| [auth-tests.md](auth-tests.md) | Authentication | TC-001 to TC-015 | REQ-001 to REQ-003 | ✅ Complete |
| [payment-tests.md](payment-tests.md) | Payment Processing | TC-016 to TC-030 | REQ-004 to REQ-006 | ⚠️ Partial |
| [user-tests.md](user-tests.md) | User Management | TC-031 to TC-045 | REQ-007 to REQ-009 | ✅ Complete |

## Coverage Summary

- **Total Requirements:** 9
- **Covered Requirements:** 8 (89%)
- **Uncovered Requirements:** 1 (REQ-005)
- **Total Test Cases:** 45

## Quick Links

- [Coverage Matrix](coverage-matrix.md)
- [Deviation Report](deviation-report.md)
- [Test Design Techniques Reference](test-design-techniques.md)
```

---

## Usage Notes

1. **{PREFIX}_{CATEGORY}_##### ID Format:** Use sequential numbering aligned with category (e.g., UTS_AUTH_00001, UTS_AUTH_00002)
2. **Traces-To Field:** Always link back to requirements for bidirectional traceability
3. **Test Implementation Field:** Link to actual test code file and function
4. **Status Values:**
   - Draft: Test case written but not yet implemented
   - Ready: Test implemented and ready to run
   - Passed: Test executed successfully
   - Failed: Test execution failed
   - Blocked: Cannot execute due to dependency
   - Deprecated: Test no longer relevant
5. **User Decisions:** Always ask user before:
   - Updating requirements from code changes
   - Updating test specifications from requirement changes
   - Removing stale tests
   - Creating specifications for orphan tests
