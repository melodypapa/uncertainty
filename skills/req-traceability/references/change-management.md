# Change Management Workflow

This reference covers handling existing requirements files and managing changes when code or requirements evolve.

## Handling Existing Requirements Files

**When requirements file already exists:**

1. **Ask user what action to take:**
   - **Replace** - Delete existing and create new requirements from scratch
   - **Append** - Add new requirements to end of existing file
   - **Update** - Modify existing requirements in place, add new ones
   - **Merge** - Smart merge of new requirements with existing ones
   - **Backup first** - Create backup before modifying

2. **Based on choice:**

   **Replace:**
   - Create backup: `requirements.md.backup_YYYYMMDD_HHMMSS`
   - Write new requirements from scratch
   - Update Output Path in header

   **Append:**
   - Keep existing requirements unchanged
   - Find highest existing requirement ID (e.g., REQ-047)
   - Start new requirements from next ID (REQ-048)
   - Add to end of file
   - Update traceability matrix with new requirements

   **Update:**
   - Read existing requirements
   - Match new requirements to existing ones by title/content
   - Update matching requirements with new information
   - Add unmatched new requirements with new IDs
   - Mark requirements without matching code as "Deprecated"
   - Update all Last Validated dates

   **Merge:**
   - Combine existing and new requirements intelligently
   - Keep existing descriptions when they match
   - Add new Implementation/Verification fields if missing
   - Remove duplicates
   - Update Status and Last Validated dates

## When Code Changes

1. **Identify affected requirements**: Use traceability matrix
2. **Determine action**:
   - **Update requirement** - Code changed, requirement stays same
   - **Mark obsolete** - Code removed, requirement no longer applies
   - **Create new requirement** - New functionality added
3. **Update traceability**: Update `Implementation:` field
4. **Re-verify**: Run verification criteria
5. **Update status**: `Implemented` → `Pending Review` → `Implemented`

## When Requirements Change

1. **Identify code to modify**: Use traceability matrix
2. **Update implementation**:
   - Modify existing code to meet new requirement
   - Add new code for new requirements
3. **Update traceability**: Update `Implementation:` field
4. **Verify**: Run new verification criteria
5. **Document change**: Add to `Change Log:`
