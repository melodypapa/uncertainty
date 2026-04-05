---
name: sync-req
description: Use when creating or maintaining ISO/IEC/IEEE 29148 compliant requirements that track code implementation over time. Triggered by need for requirements traceability, code documentation, or maintaining specifications alongside code. Supports bidirectional traceability between requirements and code locations, verification criteria validation, and change management workflows.
---

# Sync-Req: Living Requirements with Traceability

## Overview

Create and maintain ISO/IEC/IEEE 29148 compliant requirements that serve as a **single source of truth** for what the code implements. Unlike one-time documentation, these requirements are:

- **Traced back to code**: Each requirement links to specific code locations
- **Verifiable**: Can be checked against current implementation
- **Maintainable**: Updated when code changes, keeping spec and code in sync
- **Bidirectional**: Requirements ↔ Code traceability matrix

Core principle: **Requirements live alongside code** - not as a separate document that drifts apart.

## When to Use

```dot
digraph when_flowchart {
    "Need traceability?" [shape=diamond];
    "Code changed?" [shape=diamond];
    "Need verification?" [shape=diamond];
    "Use sync-req" [shape=doublecircle];
    "Skip" [shape=box];

    "Need traceability?" -> "Use sync-req" [label="yes"];
    "Need traceability?" -> "Skip" [label="no"];
    "Code changed?" -> "Use sync-req" [label="yes"];
    "Code changed?" -> "Skip" [label="no"];
    "Need verification?" -> "Use sync-req" [label="yes"];
    "Need verification?" -> "Skip" [label="no"];
}
```

**Use when:**
- Creating requirements that need to track code implementation
- Code has changed and requirements need updating
- Verifying implementation matches requirements
- Auditing code for compliance with requirements
- Managing traceability for regulated systems
- Needs requirements that can be validated against code
- Maintaining specifications over long-lived projects

## Core Concept: Bidirectional Traceability

```
┌─────────────────────────────────────────────────────────┐
│                  Requirements Document                       │
│  REQ-001: System shall authenticate users via email        │
│  └─→ Implementation: src/auth.py:login() line 45           │
│      Verification: Verify login() returns session token    │
│      Last Validated: 2026-04-05                          │
└─────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────┐
│                  Code Implementation                       │
│  def login(email, password):                              │
│      if not validate_email(email):                       │
│          raise InvalidEmailError()                         │
│      user = authenticate(email, password)                  │
│      return create_session(user)                           │
└─────────────────────────────────────────────────────────┘
```

**Benefits:**
- When code changes, you know which requirements to update
- When requirements change, you know which code to modify
- Auditors can verify implementation matches requirements
- Developers can understand business intent from code
- Risk management: track which requirements impact which modules

## Workflow: Creating Living Requirements

### Phase 1: Code → Requirements (Initial Creation)

**For each meaningful code unit:**

1. **Locate the code**: Identify file, function/class, line numbers
2. **Understand purpose**: What does this code actually do?
3. **Write requirement**: "System shall [behavior] using [mechanism]"
4. **Add traceability**: Link to `source_file:line:column`
5. **Define verification**: How to verify this requirement in the code
6. **Set validation status**: When was this requirement last validated?

**Example:**

```python
# src/auth.py:45
def authenticate_user(email, password):
    if not validate_email_format(email):
        raise InvalidEmailError()
    user = get_user_by_email(email)
    if not user or not verify_password(password, user.password_hash):
        raise AuthenticationError()
    return create_session(user)
```

```markdown
### REQ-001: User Authentication
**Type:** Functional
**Priority:** Critical
**Status:** Implemented
**Implementation:** src/auth.py:authenticate_user (line 45)
**Last Validated:** 2026-04-05

**Description:**
System shall authenticate users using email and password credentials.

**Verification:**
1. Verify function exists at src/auth.py:45
2. Verify email validation is performed (test with invalid email)
3. Verify password verification against stored hash
4. Verify session is created on successful authentication
5. Verify appropriate exceptions are raised on failure

**Source Rationale:**
Authentication is the primary security mechanism for user access control.
```

### Phase 2: Requirements → Code (Change Management)

**When requirements change:**

1. **Trace to code**: Find `Implementation:` field
2. **Update code**: Modify implementation to match new requirement
3. **Mark requirement**: Update `Status:` and `Last Validated:`
4. **Document changes**: Note what changed and why
5. **Verify**: Run verification criteria

**Example:**

```markdown
### REQ-001: User Authentication
**Status:** Draft ← Changed from "Implemented"
**Implementation:** src/auth.py:authenticate_user (line 45)

**Change Log:**
- 2026-04-10: Changed from password to passkey authentication
- Reason: Security requirement to eliminate passwords
- Impact: Requires rewrite of authentication logic
- Migrates: No migration path, new users only

**Description:**
System shall authenticate users using passkey (WebAuthn) instead of passwords.

**Verification:**
1. Verify passkey authentication is implemented
2. Verify old password authentication is removed
3. Verify backup authentication for gradual migration
```

### Phase 3: Verification Loop

**Regular verification process:**

1. **Run verification criteria** for each requirement
2. **Check code location** exists and matches requirement
3. **Update status**: `Implemented` → `Pending Update` → `Implemented`
4. **Document gaps**: Requirements without implementation or code without requirements

**Verification status values:**
- `Draft` - Requirement written, not yet implemented
- `Pending` - Code exists but doesn't fully meet requirement
- `Implemented` - Code meets requirement, recently verified
- `Deprecated` - Requirement no longer applies
- `Blocked` - Dependency not met

## Requirement Template

### Standard Format

```markdown
### REQ-###: [Requirement Title]

**Type:** [Functional | Non-Functional | Interface | Data]
**Priority:** [Critical | High | Medium | Low]
**Status:** [Draft | Pending | Implemented | Deprecated | Blocked]

**Implementation:** [file_path.py:function/class (line:column)]
**Last Validated:** [YYYY-MM-DD]
**Last Changed:** [YYYY-MM-DD]

**Description:**
[Clear, specific description of what the system shall do]

**Verification:**
[Step-by-step verification criteria, each linking back to code]
1. Verify [specific check in code]
2. Verify [specific check in code]
3. Verify [specific behavior with test]

**Source Rationale:**
[Why this requirement exists - business or technical need]

**Dependencies:**
[REQ-###, REQ-###] - Requirements this depends on

**Dependants:**
[REQ-###, REQ-###] - Requirements that depend on this

**Change Log:**
- [YYYY-MM-DD]: [Description of change, why, impact]
```

## Code Analysis Patterns

### Detecting What Requires Requirements

**Analyze code and ask:**

| Code Pattern | Should Generate Requirement? | Why/Why Not |
|-------------|---------------------------|------------|
| Business logic | **Yes** | Core functionality, needs specification |
| Configuration constants | **Yes** | System constraints, thresholds |
| Error handling | **Yes** | Edge cases, failure modes |
| Logging/debug statements | **No** | Implementation detail, not behavior |
| Helper utilities | **Maybe** | If they're business-critical |
| Database queries | **Yes** | Data integrity, performance |
| API endpoints | **Yes** | Interface contracts |
| Validation logic | **Yes** | Data quality, security rules |
| Test fixtures | **No** | Not production behavior |
| Comments/docstrings | **No** | Already in code, redundant |
| Import statements | **No** | Not behavior |

### Handling Different Code Patterns

**Functions:**
```python
# Should document behavior and edge cases
def process_payment(amount, user_id):
    # Business logic + validation + error handling
    pass
```

**Classes:**
```python
# Should document role, methods, and invariants
class PaymentProcessor:
    # Class purpose + interface contracts
    pass
```

**Constants:**
```python
# Should document constraints and thresholds
MAX_PAYMENT_AMOUNT = 10000
PAYMENT_TIMEOUT_SECONDS = 30
```

**Decorators:**
```python
# Should document security rules or cross-cutting concerns
@require_authentication
@rate_limit(max_calls=100)
```

## Traceability Matrix

### Creating a Traceability Matrix

Use this to map requirements to code locations:

```markdown
## Traceability Matrix

| Requirement | Implementation | Files | Status |
|-------------|----------------|-------|--------|
| REQ-001 | src/auth.py:45, src/tests/test_auth.py:23 | src/ | Implemented |
| REQ-002 | src/user.py:78, src/db/user.py:12 | src/db, src/user.py | Implemented |
| REQ-003 | Not implemented | N/A | Draft |
| N/A | src/util/validator.py:15 | src/util/ | Orphan Code |
```

**Or export as CSV for DOORS:**

```csv
Requirement_ID,Code_Location,Files,Status,Validation_Date
REQ-001,src/auth.py:45,src/auth.py,Implemented,2026-04-05
REQ-002,src/user.py:78,src/user.py,Implemented,2026-04-05
REQ-003,,N/A,Draft,
REQ-UNTRACKED,src/util/validator.py:15,src/util.py,Orphan Code,
```

## Verification Practices

### Manual Verification Checklist

For each requirement, verify:

- [ ] Code location exists and is accessible
- [ ] Code behavior matches requirement description
- [ ] Verification criteria can be executed/tested
- [ ] Edge cases are handled appropriately
- [ ] Error conditions are documented
- [ ] Security considerations are addressed
- [ ] Performance requirements are measurable
- [ ] Data integrity is maintained

### Automated Verification

Create verification scripts alongside requirements:

```python
# verify_req_001.py
def verify_user_authentication():
    """Verify REQ-001: User Authentication"""

    # Check function exists
    assert os.path.exists("src/auth.py"), "Auth module not found"

    # Verify implementation details
    with open("src/auth.py") as f:
        content = f.read()
        assert "def authenticate_user" in content, "authenticate_user function not found"
        assert "validate_email_format" in content or "validate_email" in content, "Email validation missing"

    # Verify with actual code
    from src.auth import authenticate_user

    # Test with valid credentials
    # result = authenticate_user("valid@example.com", "password")
    # assert result is not None, "Authentication should succeed"

    print("REQ-001: PASS")
```

## Change Management Workflow

### When Code Changes

1. **Identify affected requirements**: Use traceability matrix
2. **Determine action**:
   - **Update requirement** - Code changed, requirement stays same
   - **Mark obsolete** - Code removed, requirement no longer applies
   - **Create new requirement** - New functionality added
3. **Update traceability**: Update `Implementation:` field
4. **Re-verify**: Run verification criteria
5. **Update status**: `Implemented` → `Pending Review` → `Implemented`

### When Requirements Change

1. **Identify code to modify**: Use traceability matrix
2. **Update implementation**:
   - Modify existing code to meet new requirement
   - Add new code for new requirements
3. **Update traceability**: Update `Implementation:` field
4. **Verify**: Run new verification criteria
5. **Document change**: Add to `Change Log:`

## Common Pitfalls

### ❌ Don't Do This

- **Write requirements without code references** - Hard to trace
- **Copy-paste code into requirements** - Redundant, maintenance nightmare
- **Ignore deprecated code** - Creates orphan code and confusion
- **Skip verification** - Requirements drift from implementation
- **Over-specify** - Implementation details in requirements limit flexibility
- **Under-specify** - Ambiguous requirements lead to divergent implementations

### ✓ Do This

- **Link requirements to code locations** - File:path:line format
- **Focus on behavior, not implementation** - WHAT, not HOW
- **Keep requirements and code in sync** - Update both when either changes
- **Make requirements testable** - Verification criteria should be executable
- **Document changes** - Use Change Log for audit trail
- **Review traceability regularly** - Catch drifts early

## Tool Support

### Verification Tool

The `tools/verify_requirements.py` script helps:

```bash
# Verify all requirements match code
python tools/verify_requirements.py requirements.md

# Verify specific requirement
python tools/verify_requirements.py requirements.md --req REQ-001

# Generate traceability matrix
python tools/verify_requirements.py requirements.md --matrix
```

**What it checks:**
- Code locations exist and are accessible
- Function/class/method names match
- Verification criteria are testable
- Orphan code (code without requirements) is identified
- Deprecated requirements are marked

### Requirements from Code (Initial Creation)

To bootstrap requirements from existing code:

```bash
# Analyze code and generate requirement stubs
python tools/analyze_code.py src/ --output requirements.md

# Generates:
# - Requirements with code location references
# - Verification criteria templates
# - Traceability matrix skeleton
# - Change log entries
```

**Then you:**
1. Review and improve requirement descriptions
2. Add verification criteria
3. Fill in rationale and dependencies
4. Remove redundant or overly-detailed requirements

## Examples

### Example 1: Authentication Module

**Code:**
```python
# src/auth.py
def authenticate_user(email, password):
    if not validate_email(email):
        raise InvalidEmailError()
    user = get_user_by_email(email)
    if not user:
        raise UserNotFoundError()
    if not verify_password(password, user.password_hash):
        raise AuthenticationError()
    if user.is_disabled:
        raise AccountDisabledError()
    session = create_session(user)
    return session

MAX_LOGIN_ATTEMPTS = 5
SESSION_TIMEOUT = 3600
```

**Requirements:**
```markdown
### REQ-001: User Email Validation
**Type:** Functional
**Priority:** Critical
**Status:** Implemented
**Implementation:** src/auth.py:validate_email
**Last Validated:** 2026-04-05

**Description:**
System shall validate user email addresses before authentication attempt.

**Verification:**
1. Verify validate_email() function exists in src/auth.py
2. Test with valid email format (RFC 5322 compliant)
3. Test with invalid email formats (missing @, wrong TLD)
4. Verify InvalidEmailError is raised for invalid emails

**Source Rationale:**
Email validation prevents database pollution and improves user experience.

---

### REQ-002: Password Verification
**Type:** Functional
**Priority:** Critical
**Status:** Implemented
**Implementation:** src/auth.py:verify_password (line 45)
**Last Validated:** 2026-04-05

**Description:**
System shall verify user passwords against stored bcrypt hash.

**Verification:**
1. Verify verify_password() function uses bcrypt
2. Test with correct password - should return True
3. Test with incorrect password - should return False
4. Verify work factor is minimum 12 rounds

**Source Rationale:**
Bcrypt provides secure password storage resistant to rainbow table attacks.

---

### REQ-003: Account Status Check
**Type:** Functional
**Priority:** Critical
**Status:** Implemented
**Implementation:** src/auth.py:authenticate_user (line 35)
**Last Validated:** 2026-04-05

**Description:**
System shall verify user account is not disabled before authentication.

**Verification:**
1. Test authentication with active user - should succeed
2. Test authentication with disabled user - should raise AccountDisabledError
3. Verify disabled accounts cannot create sessions

**Source Rationale:**
Account disabled status is important for security and compliance.

---

### REQ-004: Login Attempt Limiting
**Type:** Non-Functional
**Priority:** High
**Status:** Implemented
**Implementation:** src/auth.py:authenticate_user (inferred)
**Last Validated:** 2026-04-05

**Description:**
System shall limit authentication attempts to prevent brute force attacks.

**Verification:**
1. Verify MAX_LOGIN_ATTEMPTS = 5 constant exists
2. Test 5 failed attempts - should be blocked
3. Verify account lockout is temporary or requires admin action

**Source Rationale:**
Rate limiting protects against credential stuffing attacks.
```

### Example 2: API Module

**Code:**
```python
# src/api/payments.py
@app.route('/api/payments', methods=['POST'])
def create_payment(request):
    data = request.get_json()
    amount = data.get('amount')
    if amount > MAX_PAYMENT_AMOUNT:
        raise ValidationError('Amount exceeds maximum')
    payment = PaymentService.process(amount)
    return jsonify(payment.to_dict()), 201

MAX_PAYMENT_AMOUNT = 10000
```

**Requirement:**
```markdown
### REQ-015: Payment Amount Validation
**Type:** Functional
**Priority:** High
**Status:** Implemented
**Implementation:** src/api/payments.py:create_payment (line 12)
**Last Validated:** 2026-04-05

**Description:**
System shall validate payment amounts and reject requests exceeding maximum allowed amount.

**Verification:**
1. Verify MAX_PAYMENT_AMOUNT = 10000 constant exists
2. Test payment with amount = 10000 - should succeed
3. Test payment with amount = 10001 - should raise ValidationError
4. Verify error message is clear and user-friendly

**Source Rationale:**
Amount limits prevent fraud and manage financial exposure.
```

## Change Log Template

```markdown
## Change Log

### [Date]

**REQ-###:** [Requirement Title]
**Change Type:** [New / Modified / Deprecated / Restored]
**Previous:** [Previous requirement text]
**Updated:** [Updated requirement text]
**Reason:** [Why the change was made]
**Impact:** [What code needs to change]
**Affected Files:** [List of affected code files]
**Dependencies:** [Other requirements affected]
```

## Quality Checklist

Before finalizing requirements document:

- [ ] Every requirement has Implementation field with file:line:column
- [ ] Every requirement has verification criteria linking back to code
- [ ] Traceability matrix is complete (all code → requirements, all requirements → code)
- [ ] No orphan code (code without requirements) unless documented as intentional
- [ ] No deprecated requirements without status change
- [ ] Status reflects actual implementation state
- [ ] Last Validated dates are recent (within 90 days for active code)
- [ ] Dependencies are documented
- [ ] Change log entries are complete for recent changes

## Related Skills

- **superpowers:code-review**: Analyze code changes and update requirements
- **superpowers:test-driven-development**: Create tests to verify requirements
- **superpowers:audit**: Verify compliance with requirements