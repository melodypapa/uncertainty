# DOORS CSV Format Specification

## Overview

DOORS (Dynamic Object Oriented Requirements System) requires specific CSV structure for requirements import.

## Column Structure

### Required Columns

| Column | Data Type | Format | Required | Example |
|--------|-----------|--------|----------|---------|
| ID | String | REQ-### format | Yes | REQ-001 |
| Text | String | Full requirement description | Yes | "System shall authenticate users" |
| Type | String | Functional/Non-Functional/Interface/Data | Yes | Functional |
| Priority | String | Critical/High/Medium/Low | Yes | Critical |
| Status | String | Draft/Approved/Implemented/Rejected | Yes | Draft |
| Verification | String | Acceptance criteria | Yes | "Verify login with valid credentials" |

### Optional Columns

| Column | Data Type | Format | Required | Example |
|--------|-----------|--------|----------|---------|
| Parent_ID | String | Parent requirement ID | No | REQ-001 |
| Source | String | Code file path or "manual" | No | src/auth/login.py |
| Rationale | String | Business justification | No | "Security requirement" |

## CSV Formatting Rules

### Character Encoding

- **Mandatory:** UTF-8
- **Supports:** International characters, emojis, special symbols

### Field Delimiters

- **Delimiter:** Comma (`,`)
- **Quote Character:** Double quote (`"`)
- **Escape Character:** Double double quote (`""`)

### Quoting Rules

- **Always quote fields containing:**
  - Comma (`,`)
  - Newline (`\n`)
  - Double quote (`"`)
  - Leading/trailing spaces

### Line Endings

- **Required:** Unix line endings (`\n`)
- **Not allowed:** Windows line endings (`\r\n`)
- **Not allowed:** Old Mac line endings (`\r`)

### Whitespace

- **No trailing spaces** in any field
- **No leading spaces** unless intentional
- **Trim** fields before export

## Example Records

```csv
ID,Text,Type,Priority,Status,Verification,Parent_ID,Source,Rationale
REQ-001,"System shall authenticate users via username and password",Functional,Critical,Draft,"Verify login with valid credentials",,src/auth.py,"Security requirement"
REQ-002,"Authentication response time shall be less than 2 seconds",Non-Functional,High,Draft,"Measure API response time under load",,src/auth.py,"Performance SLA"
REQ-003,"Passwords shall be hashed using bcrypt with minimum 12 rounds",Non-Functional,Critical,Draft,"Verify bcrypt hash in database",,src/auth.py,"Security standard"
```

## Special Cases

### Multi-line Requirements

```csv
REQ-004,"System shall support the following authentication methods:
- Username/password
- LDAP
- OAuth 2.0",Functional,High,Draft,"Test each authentication method",,src/auth.py,"Multi-factor support"
```

### Quoted Fields with Quotes

```csv
REQ-005,"Error message shall display ""Invalid credentials"" on failed login",Functional,Medium,Draft,"Verify error message text",,src/auth.py,"User feedback"
```

### Unicode Characters

```csv
REQ-006,"System shall support user names with international characters (é, ñ, ö)",Functional,Medium,Draft,"Test with Unicode names",,src/auth.py,"Internationalization"
```

## Import Process

### Step 1: Generate CSV

Follow the formatting rules above.

### Step 2: Verify Encoding

Ensure file is UTF-8 encoded:
```bash
file -I requirements.csv
# Output: requirements.csv: text/plain; charset=utf-8
```

### Step 3: Import to DOORS

1. Open DOORS database
2. Navigate to target module
3. Select `File → Import → CSV...`
4. Select the CSV file
5. Map columns to DOORS attributes:
   - ID → Object Identifier
   - Text → Object Text
   - Type → Type (custom attribute)
   - Priority → Priority (custom attribute)
   - Status → Status (custom attribute)
   - Verification → Verification (custom attribute)
   - Parent_ID → Parent (custom attribute)
   - Source → Source (custom attribute)
   - Rationale → Rationale (custom attribute)
6. Set import options:
   - Delimiter: Comma
   - Quote: Double quote
   - Encoding: UTF-8
7. Preview and verify column mapping
8. Execute import
9. Review imported requirements

### Step 4: Post-Import Validation

- Check all requirements imported correctly
- Verify ID format and numbering
- Confirm attribute values match source
- Validate parent-child relationships
- Review special character rendering

## Common Import Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Wrong encoding | File not UTF-8 | Convert to UTF-8 using `iconv` |
| Missing columns | CSV header mismatch | Verify column names match specification |
| Truncated text | Newlines not quoted | Quote fields containing newlines |
| Wrong delimiter | Semicolon or tab used | Use comma delimiter |
| Quote errors | Unescaped quotes | Escape quotes as `""` |
| Garbled characters | Non-UTF-8 encoding | Convert to UTF-8 with iconv |

## Template File

Reference: `templates/doors-csv-template.csv`