# Verification and Traceability Reference

This reference covers traceability matrix creation and verification practices for requirements.

## Creating a Traceability Matrix

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

## Manual Verification Checklist

For each requirement, verify:

- [ ] Code location exists and is accessible
- [ ] Code behavior matches requirement description
- [ ] Verification criteria can be executed/tested
- [ ] Edge cases are handled appropriately
- [ ] Error conditions are documented
- [ ] Security considerations are addressed
- [ ] Performance requirements are measurable
- [ ] Data integrity is maintained

## Automated Verification

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

## Tool Support

### Deviation Detection Tool

The deviation detection workflow analyzes requirements against current code:

```bash
# Check for deviations (interactive workflow)
# This is a guided process - ask user for requirements path, detect deviations, generate report

# Typical flow:
1. Ask user: "Where is your requirements file?"
2. Parse requirements and analyze code
3. Generate sync report with deviation types (DRIFT, ORPHAN_CODE, ORPHAN_REQ)
4. Present report to user
5. Ask user for synchronization choices
6. Execute approved actions
7. Generate post-sync report
```

**What it detects:**
- Code locations referenced in requirements that don't exist (ORPHAN_REQ)
- Requirements that describe behavior not matching current code (DRIFT)
- Code that exists but has no corresponding requirements (ORPHAN_CODE)
- Requirements with stale `Last Validated:` dates (> 90 days)

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
