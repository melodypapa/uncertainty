# ISO/IEC/IEEE 29119-4 Test Design Techniques Reference

**Purpose:** Complete reference for test design technique selection and application in sync-req skill.

**Load this file when:** User requests test derivation from requirements, or test coverage analysis.

## Overview

ISO/IEC/IEEE 29119-4 defines three categories of test design techniques:

| Category | Description | When to Use |
|----------|-------------|-------------|
| **Specification-based** | Derive tests from requirements/specifications | Functional requirements, well-defined behavior |
| **Structure-based** | Derive tests from code structure | Code coverage, white-box testing |
| **Experience-based** | Derive tests from tester knowledge and experience | Non-functional requirements, exploratory testing |

## Three-Step Process (Universal)

Every test design technique follows this three-step process:

```
1. Derive Test Conditions → What to test
2. Derive Coverage Items  → How much to test
3. Derive Test Cases      → Specific test inputs and expected outputs
```

---

## Specification-Based Techniques

### 1. Equivalence Partitioning (EP)

**Purpose:** Divide inputs into classes that should be treated equivalently by the system.

**Three-Step Process:**

| Step | Action | Example |
|------|--------|---------|
| 1. Test Conditions | Identify equivalence classes | Valid emails, invalid emails |
| 2. Coverage Items | One value from each partition | `test@example.com`, `invalid-email` |
| 3. Test Cases | Create test with partition value | Input: `test@example.com` → Expected: Accepted |

**When to Use:**
- Input validation requirements
- Data range requirements
- Configuration options

**Example Requirement:**
```
REQ-001: System shall accept email addresses in format user@domain.com
```

**Derived Tests:**
| Test ID | Partition | Input | Expected |
|---------|-----------|-------|----------|
| TC-001 | Valid email | `user@domain.com` | Accepted |
| TC-002 | Missing @ | `userdomain.com` | Rejected |
| TC-003 | Missing domain | `user@` | Rejected |
| TC-004 | Special chars | `user+tag@domain.com` | Accepted |

---

### 2. Boundary Value Analysis (BVA)

**Purpose:** Test at the boundaries of equivalence partitions where errors are likely.

**Three-Step Process:**

| Step | Action | Example |
|------|--------|---------|
| 1. Test Conditions | Identify boundaries | Min: 1, Max: 100 for age field |
| 2. Coverage Items | Test min, min-1, min+1, max, max-1, max+1 | 0, 1, 2, 99, 100, 101 |
| 3. Test Cases | Create tests for each boundary | Input: 0 → Expected: Error |

**When to Use:**
- Numeric range requirements
- Size/count limitations
- Time/date constraints

**Example Requirement:**
```
REQ-002: System shall accept age values between 18 and 120
```

**Derived Tests:**
| Test ID | Boundary | Input | Expected |
|---------|----------|-------|----------|
| TC-005 | Min - 1 | 17 | Rejected |
| TC-006 | Min | 18 | Accepted |
| TC-007 | Min + 1 | 19 | Accepted |
| TC-008 | Max - 1 | 119 | Accepted |
| TC-009 | Max | 120 | Accepted |
| TC-010 | Max + 1 | 121 | Rejected |

---

### 3. Decision Table Testing

**Purpose:** Test combinations of conditions and resulting actions.

**Three-Step Process:**

| Step | Action | Example |
|------|--------|---------|
| 1. Test Conditions | Identify all conditions and actions | Login: email valid? password valid? locked? |
| 2. Coverage Items | Create decision table with all combinations | 2³ = 8 combinations |
| 3. Test Cases | One test per rule in decision table | Rule 1: Valid email + Valid password + Not locked → Success |

**When to Use:**
- Complex business rules
- Multiple conditions affecting outcome
- Combinatorial logic

**Example Requirement:**
```
REQ-003: Login succeeds if email is valid, password is correct, and account is not locked
```

**Decision Table:**
| Rule | Email Valid | Password Correct | Not Locked | Action |
|------|-------------|------------------|------------|--------|
| 1 | T | T | T | Success |
| 2 | T | T | F | Account Locked |
| 3 | T | F | T | Invalid Password |
| 4 | T | F | F | Invalid Password |
| 5 | F | T | T | Invalid Email |
| 6 | F | T | F | Invalid Email |
| 7 | F | F | T | Invalid Email |
| 8 | F | F | F | Invalid Email |

---

### 4. State Transition Testing

**Purpose:** Test system behavior as it transitions between states.

**Three-Step Process:**

| Step | Action | Example |
|------|--------|---------|
| 1. Test Conditions | Identify states and transitions | Draft → Submitted → Approved → Published |
| 2. Coverage Items | Cover all transitions, invalid transitions | Draft→Submitted (valid), Draft→Published (invalid) |
| 3. Test Cases | Create test for each transition | Start: Draft, Action: Submit, Expected: Submitted |

**When to Use:**
- Workflow requirements
- State machine behavior
- Lifecycle management

**Example Requirement:**
```
REQ-004: Document workflow: Draft → Submitted → Approved → Published
```

**State Transition Table:**
| Current State | Event | Next State | Valid? |
|---------------|-------|------------|--------|
| Draft | Submit | Submitted | ✅ |
| Draft | Approve | Draft | ❌ Invalid |
| Submitted | Approve | Approved | ✅ |
| Submitted | Publish | Submitted | ❌ Invalid |
| Approved | Publish | Published | ✅ |
| Approved | Submit | Approved | ❌ Invalid |

---

### 5. Use Case Testing

**Purpose:** Test user interactions with the system through use case scenarios.

**Three-Step Process:**

| Step | Action | Example |
|------|--------|---------|
| 1. Test Conditions | Identify use case scenarios | Main flow, alternative flows, exceptions |
| 2. Coverage Items | Each scenario path | Happy path, error path, edge case |
| 3. Test Cases | Create test following scenario steps | Step 1: Navigate to login → Step 2: Enter credentials → ... |

**When to Use:**
- User interaction requirements
- End-to-end scenarios
- Business process testing

---

## Structure-Based Techniques

### 6. Statement Testing

**Purpose:** Execute every statement in the code at least once.

**Coverage:** Statement Coverage = (Statements Executed / Total Statements) × 100%

**When to Use:**
- Safety-critical systems
- Regulatory compliance
- Minimum coverage requirements

---

### 7. Decision Testing

**Purpose:** Execute every decision (branch) in the code.

**Coverage:** Decision Coverage = (Decisions Executed / Total Decisions) × 100%

**When to Use:**
- Logic verification
- Branch coverage requirements
- Higher coverage than statement testing

---

### 8. Condition Testing

**Purpose:** Test each atomic condition within a decision.

**Coverage:** Condition Coverage = (Conditions Evaluated True and False / Total Conditions) × 100%

**When to Use:**
- Complex boolean expressions
- Multiple conditions in single decision
- MC/DC coverage requirements

---

## Experience-Based Techniques

### 9. Error Guessing

**Purpose:** Use experience to anticipate likely defects.

**Three-Step Process:**

| Step | Action | Example |
|------|--------|---------|
| 1. Test Conditions | Identify error-prone areas | Input validation, error handling, edge cases |
| 2. Coverage Items | Common error patterns | Empty input, null values, special characters |
| 3. Test Cases | Create tests for guessed errors | Input: Empty string → Expected: Validation error |

**When to Use:**
- Non-functional requirements
- Security testing
- Performance testing
- When specification is incomplete

---

### 10. Exploratory Testing

**Purpose:** Simultaneously learn, design, and execute tests.

**Three-Step Process:**

| Step | Action | Example |
|------|--------|---------|
| 1. Test Conditions | Explore system behavior | What happens if network fails? |
| 2. Coverage Items | Charter-based exploration | 30-minute session on payment flow |
| 3. Test Cases | Document findings as tests | Found: Timeout not handled after 30s |

**When to Use:**
- Early development stages
- Requirements not fully specified
- Agile/iterative development

---

## Technique Selection Decision Table

| Requirement Type | Priority | Risk Level | Recommended Technique |
|-----------------|----------|------------|----------------------|
| Functional - Input validation | Any | Any | Equivalence Partitioning + BVA |
| Functional - Business rules | Any | Any | Decision Table Testing |
| Functional - Workflow/States | Any | Any | State Transition Testing |
| Functional - User interactions | Any | Any | Use Case Testing |
| Non-Functional - Performance | High | High | Error Guessing + Exploratory |
| Non-Functional - Security | High | Critical | Error Guessing + BVA |
| Non-Functional - Usability | Medium | Medium | Exploratory Testing |
| Complex conditions | Any | Any | Decision Table + Condition Testing |
| Safety-critical | Any | Critical | All Specification-based + Structure-based |
| Incomplete requirements | Any | Any | Experience-based (Error Guessing) |

---

## Coverage Measurement Methods

### Requirements Coverage

```
Requirements Coverage = (Requirements with Test Cases / Total Requirements) × 100%
```

**Target:** 100% for safety-critical systems

### Traceability Coverage Matrix

| Requirement | Test Cases | Coverage Status |
|-------------|------------|-----------------|
| REQ-001 | TC-001, TC-002, TC-003, TC-004 | ✅ Covered |
| REQ-002 | TC-005, TC-006, TC-007, TC-008, TC-009, TC-010 | ✅ Covered |
| REQ-003 | TC-011 through TC-018 | ✅ Covered |
| REQ-004 | TC-019 through TC-024 | ✅ Covered |
| REQ-005 | - | ❌ UNCOVERED |

### Test Deviation Types

| Deviation Type | Description | Detection Method |
|----------------|-------------|------------------|
| TEST_DRIFT | Requirement changed but test not updated | Compare test spec with current requirement |
| UNCOVERED_REQ | Requirement has no test coverage | Check traceability matrix |
| STALE_TEST | Test references deleted requirement | Validate requirement ID exists |
| ORPHAN_TEST | Test code has no test specification | Scan test files, match to specs |

---

## Common Mistakes to Avoid

1. **Using only one technique** - Different requirements need different techniques
2. **Skipping boundary testing** - Errors cluster at boundaries
3. **Ignoring invalid partitions** - Test both valid and invalid inputs
4. **Missing state transitions** - Test all valid and invalid transitions
5. **Not testing error paths** - Alternative flows need coverage too
6. **Over-reliance on experience-based** - Use specification-based first when requirements exist

---

## Quick Reference: Technique Selection Flowchart

```
                    ┌─────────────────────────────┐
                    │ What type of requirement?   │
                    └─────────────────────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        ▼                       ▼                       ▼
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│  Functional   │     │ Non-Functional│     │ Incomplete/   │
│  (Well-defined)│     │  (Quality)    │     │ Exploratory   │
└───────────────┘     └───────────────┘     └───────────────┘
        │                       │                       │
        ▼                       ▼                       ▼
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│ Specification │     │  Experience-  │     │  Experience-  │
│    -based     │     │    based      │     │    based      │
└───────────────┘     └───────────────┘     └───────────────┘
        │
        ▼
┌─────────────────────────────────────────────┐
│          Analyze requirement nature:        │
│  • Input validation → EP + BVA              │
│  • Business rules → Decision Table          │
│  • Workflow → State Transition              │
│  • User interaction → Use Case              │
└─────────────────────────────────────────────┘
```

---

## References

- ISO/IEC/IEEE 29119-4:2015 - Software Testing - Part 4: Test Techniques
- ISTQB Foundation Level Syllabus - Chapter 4: Test Techniques
- IEEE 829-2008 - Standard for Software Test Documentation
