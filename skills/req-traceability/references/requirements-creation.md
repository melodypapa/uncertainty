# Requirements Creation from User Input

**Load ONLY if user selected "From scratch" in Step 2a.**

## Creating Requirements from Scratch

**CRITICAL: This applies when user selected "From scratch" in Step 2a.**

Phase 1 (Code -> Requirements) is SKIPPED. Proceed directly to creating requirements based on user input.

### Process

1. **Gather input**: User provides requirements based on:
   - User stories
   - Specifications
   - Design documents
   - Descriptions
   - Product requirements

2. **Write requirements**: For each requirement:
   - Use "System shall [behavior]" format
   - Be specific and testable
   - Include functional and non-functional requirements

3. **Set implementation status**: Since no code exists yet:
   - `Status: Draft` - Requirement written, not yet implemented
   - Leave `Implementation:` field empty or mark as "TBD"

4. **Define verification**: How will this be verified once implemented?

5. **Add traceability**: For future implementation:
   - Leave `Implementation:` empty
   - Will be filled in when code is written

### Phase 2: Requirements -> Code (Change Management)

When code is eventually written:

1. **Trace to code**: Find implementation and update `Implementation:` field
2. **Update status**: Change from `Draft` to `Pending` or `Implemented`
3. **Mark validated**: Update `Last Validated:` date
4. **Document changes**: Note in Change Log

### Verification Status Values

- `Draft` - Requirement written, not yet implemented
- `Pending` - Code exists but doesn't fully meet requirement
- `Implemented` - Code meets requirement, recently verified
- `Deprecated` - Requirement no longer applies
- `Blocked` - Dependency not met

## Requirement Template

For the complete requirement template with field descriptions, read `references/requirements-template.md`.
