# Security Checks Reference

This reference covers the security validation steps that must run before saving any requirements file.

## Step 0.5: Validate Output Path Security

**CRITICAL: Validate user-provided output path for security issues.**

**Path Traversal Protection:**

```bash
# Check for parent directory references that could escape intended directory
if echo "$PATH" | grep -qE '\.\./|\.\.\\\\'; then
    echo "ERROR: Path traversal detected. Parent directory references (../ or ..\\\\) are not allowed."
    echo "Please provide a safe output path without directory traversal."
    exit 1
fi

# Check for absolute path access to sensitive system directories
if echo "$PATH" | grep -qE '^/(etc|var|sys|proc|tmp|Users/ray/.*\\.ssh)'; then
    echo "ERROR: Access to sensitive system directories is not allowed."
    echo "Please provide a safe output path."
    exit 1
fi
```

**Rejected patterns:**
- `../` or `..\\` (parent directory traversal)
- Absolute paths to `/etc`, `/var`, `/sys`, `/proc`, `/tmp`
- Paths to `.ssh`, `.aws`, `.kubeconfig` directories
- `./../../` (nested traversal)
- `%2e%2e%2f` (URL-encoded traversal)

**Allowed patterns:**
- Relative paths without parent references: `docs/requirements.md`, `output/`
- Safe absolute paths within project: `/project/docs/`
- Current directory: `./requirements.md`, `requirements.md`

## Step 0.75: Secrets Detection in Requirements

**CRITICAL: Scan generated requirements for hardcoded secrets.**

```bash
# Check for common secret patterns in requirements
grep -lE '(API_KEY|SECRET|PASSWORD|TOKEN|PRIVATE_KEY|CONNECTION_STRING|AWS_ACCESS_KEY|AWS_SECRET_KEY|DATABASE_URL|DB_PASSWORD|AUTH_TOKEN)' requirements.md 2>/dev/null
```

**If secrets found:**

1. **STOP** - Do not save requirements with actual secrets
2. Show user the detected secrets
3. Advise using placeholder values instead

**Secret patterns to detect:**
- `API_KEY=`, `SECRET_KEY=`, `PRIVATE_KEY=`
- `PASSWORD=`, `PASS=`
- `TOKEN=`, `AUTH_TOKEN=`, `JWT=`
- `CONNECTION_STRING=`, `DATABASE_URL=`
- `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`
- Credentials in URLs: `://user:pass@host`

**Replace with placeholders:**
- `API_KEY=sk-12345` → `YOUR_API_KEY_HERE`
- `PASSWORD=secret123` → `your_password_here`
- `CONNECTION_STRING=mongodb://admin:pass@...` → `your_connection_string_here`

## Step 0.875: Injection Protection in Verification Criteria

**CRITICAL: Scan verification criteria for injection vulnerabilities.**

**SQL Injection patterns:**
```bash
grep -lE '(SELECT|INSERT|UPDATE|DELETE).*\+.*user|eval.*\".*user|\\$.*user.*WHERE' requirements.md 2>/dev/null
```

**Shell Injection patterns:**
```bash
grep -lE '(system|exec|eval|popen).*\\$.*user|`.*user.*`|\\$\\(.*user' requirements.md 2>/dev/null
```

**Code Injection patterns:**
```bash
grep -lE 'eval\\(.*user|exec\\(.*user|compile\\(.*user' requirements.md 2>/dev/null
```

**If injection patterns found:**

1. **WARN** user about injection vulnerabilities
2. Advise using parameterized queries/prepared statements
3. Show example of safe alternative

**Safe verification patterns:**
- SQL: Use prepared statements with placeholders: `WHERE id = ?`
- Shell: Avoid user input in commands, use array arguments
- Eval: Never use eval() with user input
