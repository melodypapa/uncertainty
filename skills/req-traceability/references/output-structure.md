# Output Structure Details

**Purpose:** Detailed output format specifications and examples.

**Load this file when:** You need to see complete output format examples.

---

## ID Format

All IDs follow: `{PREFIX}_{CATEGORY}_#####`

| Document Type | Prefix | Example ID |
|---------------|--------|------------|
| Software Requirements | SWR | `SWR_AUTH_00001` |
| Unit Tests | UTS | `UTS_AUTH_00001` |
| Integration Tests | ITS | `ITS_PAYMENT_00001` |
| System Tests | SYTS | `SYTS_USER_00001` |
| Acceptance Tests | ATS | `ATS_AUTH_00001` |

## Category Naming Rules

- Uppercase short names (AUTH, USER, PAYMENT, API)
- Maximum 10 characters
- No spaces or special characters
- Should represent functional area

## File Naming

**Format:** `{prefix}_{category}_{type}.md` (lowercase)

| Document Type | Filename Example |
|---------------|------------------|
| Requirements | `swr_auth_requirements.md` |
| Test Specs | `uts_auth_test-specs.md` |

**Note:** Filenames are lowercase, IDs use uppercase.

---

## File Organization Example

```
docs/
  requirements/
    swr_auth_requirements.md
    swr_user_requirements.md
    swr_payment_requirements.md

  tests/
    unit/
      uts_auth_test-specs.md
      uts_user_test-specs.md
    integration/
      its_auth_test-specs.md
      its_user_test-specs.md
    system/
      syts_auth_test-specs.md
      syts_user_test-specs.md
    acceptance/
      ats_auth_test-specs.md
      ats_user_test-specs.md
```

---

## Test Type to Folder Mapping

| Test Type | Prefix | Folder |
|-----------|--------|--------|
| Unit Tests | UTS | `docs/tests/unit/` |
| Integration Tests | ITS | `docs/tests/integration/` |
| System Tests | SYTS | `docs/tests/system/` |
| Acceptance Tests | ATS | `docs/tests/acceptance/` |

---

## Default Output Locations

| Output Type | Default Path |
|-------------|--------------|
| Requirements | `docs/requirements/` |
| Unit Tests | `docs/tests/unit/` |
| Integration Tests | `docs/tests/integration/` |
| System Tests | `docs/tests/system/` |
| Acceptance Tests | `docs/tests/acceptance/` |

---

## Custom Output Paths

When user specifies a custom path:
- **File path:** Save directly to specified location
- **Directory:** Create category files inside
- **Absolute path:** Use as-is (after security validation)
- **With category:** Filename includes category

---

## Requirements Output Format

```markdown
# Software Requirements Specification

**Project:** [Project Name]
**Standard:** ISO 29148
**Generated:** [Date]
**Source:** [Source file or description]
**Output Path:** [File path]

---

## 1. Introduction

### 1.1 Purpose
[What this requirements document covers]

### 1.2 Scope
[What is included and excluded]

### 1.3 Definitions
[Key terms used in requirements]

---

## 2. Functional Requirements

### SWR_AUTH_00001: User Authentication

**Description:** The system shall authenticate users via username and password.

**Rationale:** Secure access control requires identity verification.

**Implementation:** `src/auth/login.py:45`

**Verification Criteria:**
- Given valid credentials, when user submits login form, then access is granted
- Given invalid credentials, when user submits login form, then access is denied
- Given locked account, when user attempts login, then appropriate error shown

**Status:** Implemented

**Last Validated:** 2024-01-15
**Last Changed:** 2024-01-10

**Traces-From:** [Parent requirements if any]
**Traces-To:** [Child requirements or test cases]

---

### SWR_AUTH_00002: Password Reset

**Description:** The system shall allow users to reset forgotten passwords via email.

**Implementation:** `src/auth/password_reset.py:23`

**Verification Criteria:**
- Given registered email, when user requests reset, then reset link is sent
- Given valid reset token, when user sets new password, then password is updated
- Given expired token, when user attempts reset, then appropriate error shown

**Status:** Implemented

---

## 3. Non-Functional Requirements

### SWR_PERF_00001: Response Time

**Description:** The system shall respond to user actions within 2 seconds under normal load.

**Implementation:** System-wide

**Verification Criteria:**
- Given normal load (< 1000 concurrent users), when user performs action, then response time < 2s

**Status:** Pending

---

## Traceability Matrix

| Requirement | Implementation | Verification | Status |
|-------------|----------------|--------------|--------|
| SWR_AUTH_00001 | src/auth/login.py:45 | UTS_AUTH_00001, ITS_AUTH_00001 | Implemented |
| SWR_AUTH_00002 | src/auth/password_reset.py:23 | UTS_AUTH_00002, ITS_AUTH_00002 | Implemented |
| SWR_PERF_00001 | System-wide | SYTS_PERF_00001 | Pending |
```

---

## Test Specification Output Format

```markdown
# Unit Test Specifications: Authentication

**Project:** [Project Name]
**Standard:** ISO 29119-4
**Generated:** [Date]
**Source:** swr_auth_requirements.md
**Output Path:** docs/tests/unit/uts_auth_test-specs.md

---

## 1. Introduction

### 1.1 Purpose
Unit test specifications for authentication module.

### 1.2 Scope
Tests derived from SWR_AUTH_* requirements.

---

## 2. Test Specifications

### UTS_AUTH_00001: Valid Login Test

**Description:** Verify successful authentication with valid credentials.

**Traces-To:** SWR_AUTH_00001

**Test Design Technique:** Equivalence Partitioning

**Test Conditions:**
- TC1: Valid username and password combination

**Coverage Items:**
- CI1: Username field accepts valid input
- CI2: Password field accepts valid input
- CI3: Login button triggers authentication

**Test Cases:**
- **UTS_AUTH_00001_TC01:** Enter valid username "testuser", valid password "Test@123", click login → Access granted

**Test Data:**
| Username | Password | Expected Result |
|----------|----------|-----------------|
| testuser | Test@123 | Access granted |

**Status:** Ready for Implementation

---

### UTS_AUTH_00002: Invalid Login Test

**Description:** Verify authentication failure with invalid credentials.

**Traces-To:** SWR_AUTH_00001

**Test Design Technique:** Boundary Value Analysis

**Test Conditions:**
- TC1: Invalid username
- TC2: Invalid password
- TC3: Empty username
- TC4: Empty password

**Coverage Items:**
- CI1: Error message for invalid username
- CI2: Error message for invalid password
- CI3: Error message for empty fields

**Test Cases:**
- **UTS_AUTH_00002_TC01:** Enter invalid username "wronguser", valid password → Access denied
- **UTS_AUTH_00002_TC02:** Enter valid username, invalid password "wrongpass" → Access denied
- **UTS_AUTH_00002_TC03:** Leave username empty → Validation error
- **UTS_AUTH_00002_TC04:** Leave password empty → Validation error

**Status:** Ready for Implementation

---

## 3. Coverage Matrix

| Requirement | Test Specification | Coverage |
|-------------|-------------------|----------|
| SWR_AUTH_00001 | UTS_AUTH_00001, UTS_AUTH_00002 | 100% |
| SWR_AUTH_00002 | UTS_AUTH_00003, UTS_AUTH_00004 | 100% |
```

---

## DOORS CSV Format

For DOORS export, see `references/doors-csv-format.md` and `assets/doors-csv-template.csv`.
