# Change Management Workflow

This reference covers handling existing requirements files and managing changes when code or requirements evolve.

## CRITICAL: ID Preservation Rule

**Requirement IDs and Test Case IDs are permanent traceability identifiers.**

- **NEVER reuse existing IDs** - Each ID represents a unique traceability chain
- **ALWAYS preserve existing IDs when updating** - Content updates do NOT change IDs
- **ONLY assign new IDs to new items** - Increment from highest existing ID
- **ID changes break traceability** - Changing an ID breaks all references (code links, test traces, coverage matrices)

When updating requirements or test specifications:
1. Read all existing IDs first
2. Match new content to existing items by title/description
3. Preserve existing IDs for matched items
4. Assign new IDs only to unmatched new items
5. Update content in place, do NOT recreate with new IDs

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
   - **CRITICAL: ID Preservation** - Read all existing requirement IDs first
   - Match new requirements to existing ones by title/description/content
   - **Preserve existing IDs** for matched requirements - update content in place
   - **Assign new IDs only** to unmatched new requirements (increment from highest existing ID)
   - Mark requirements without matching code as "Deprecated" (keep original ID)
   - Update all `Last Validated:` dates
   - Update traceability matrix with preserved IDs

   **Merge:**
   - **CRITICAL: ID Preservation** - Read all existing requirement IDs first
   - Combine existing and new requirements intelligently
   - Keep existing IDs and descriptions when they match - update in place
   - Add new Implementation/Verification fields if missing (preserve ID)
   - Remove duplicates (keep the ID, remove the duplicate entry)
   - Update Status and Last Validated dates
   - Assign new IDs only to truly new requirements

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
