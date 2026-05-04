# Requirements Extraction from Code

**Load ONLY if user selected "From current code" in Step 2a.**

## Phase 1: Code -> Requirements (Extract from Scratch)

**CRITICAL: This phase is ONLY executed if user selected "From current code" in Step 2a.**

**If user selected "From scratch":** Skip this entire phase. Proceed to Phase 2.

### Process

**For each meaningful code unit:**

1. **Locate the code**: Identify file, function/class, line numbers
2. **Understand purpose**: What does this code actually do?
3. **Write requirement**: "System shall [behavior] using [mechanism]"
4. **Add traceability**: Link to `source_file:line:column`
5. **Define verification**: How to verify this requirement in the code
6. **Set validation status**: When was this requirement last validated?

### Detecting What Requires Requirements

| Code Pattern | Should Generate Requirement? | Why/Why Not |
|-------------|---------------------------|------------|
| Business logic | **Yes** | Core functionality, needs specification |
| Configuration constants | **Yes** | System constraints, thresholds |
| Error handling | **Yes** | Edge cases, failure modes |
| Logging/debug statements | No | Implementation detail, not behavior |
| Helper utilities | Maybe | If they're business-critical |
| Database queries | **Yes** | Data integrity, performance |
| API endpoints | **Yes** | Interface contracts |
| Validation logic | **Yes** | Data quality, security rules |
| Test fixtures | No | Not production behavior |
| Comments/docstrings | No | Already in code, redundant |
| Import statements | No | Not behavior |

### Handling Different Code Patterns

**Functions:** Document behavior and edge cases
**Classes:** Document role, methods, and invariants
**Constants:** Document constraints and thresholds
**Decorators:** Document security rules or cross-cutting concerns

### Implementation Reference Syntax

Use `file.py:function` (single colon), not `file.py::function` (double colon).

Format: `file_path.py:function/class (line:column)`

Example: `src/auth.py:login (line:45)` or `src/auth.py:UserAuth (line:20)`

## Code Analysis Examples

For complete worked examples (auth module, API, deviation detection, orphan code), read `references/examples.md`.
