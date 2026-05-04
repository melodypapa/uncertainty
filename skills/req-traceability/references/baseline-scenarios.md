# Baseline Scenarios - req-traceability WITHOUT Test Design Feature

**Date:** 2026-05-04
**Skill Version:** 1.0.0
**Purpose:** Document current behavior before adding ISO 29119-4 test design integration

## Current Skill Capabilities

### What req-traceability 1.0.0 DOES Have:
- ✅ Requirements extraction from code
- ✅ Bidirectional traceability (Requirements ↔ Code)
- ✅ Deviation detection (DRIFT, ORPHAN_CODE, ORPHAN_REQ, CONFLICT)
- ✅ ISO 29148 compliance
- ✅ Security validation (path traversal, secrets detection, injection protection)
- ✅ Multi-file organization support
- ✅ DOORS CSV export

### What req-traceability 1.0.0 DOES NOT Have:
- ❌ Test design technique derivation
- ❌ Test specification document generation
- ❌ Three-layer traceability (Requirements ↔ Test Specifications ↔ Code)
- ❌ Test deviation detection (TEST_DRIFT, UNCOVERED_REQ, STALE_TEST, ORPHAN_TEST)
- ❌ Test coverage analysis
- ❌ Test synchronization on requirement changes
- ❌ User decision points for test updates

## Baseline Scenarios

### Scenario 1: User Requests Test Derivation from Requirements

**Input:** "Derive test cases from these requirements for the authentication module"

**Current Behavior:**
- Agent may attempt to create ad-hoc test cases
- No structured ISO 29119-4 technique selection
- No three-step process (Conditions → Coverage Items → Test Cases)
- Test cases not linked back to requirements in traceability matrix
- No coverage analysis

**Rationalizations Agent May Use:**
1. "I'll create some basic test cases based on the requirements"
2. "Testing is outside the scope of requirements management"
3. "The user should use a separate testing tool for this"
4. "I'll just list some example test scenarios"

**Gap Identified:** No systematic test design workflow

---

### Scenario 2: Requirements Change - Tests Need Update

**Input:** "REQ-001 changed from 'email login' to 'OAuth login', update related artifacts"

**Current Behavior:**
- Agent updates the requirement
- Agent may suggest updating code
- Agent does NOT identify affected test specifications
- No TEST_DRIFT detection
- No test synchronization workflow

**Rationalizations Agent May Use:**
1. "I've updated the requirement, the code changes are up to you"
2. "Test updates are not part of requirements management"
3. "You should manually review your tests for this change"

**Gap Identified:** No test deviation detection or synchronization

---

### Scenario 3: Code Changed - User Wants to Update Tests

**Input:** "The login function now uses bcrypt instead of SHA-256, what tests need updating?"

**Current Behavior:**
- Agent may detect code change via deviation detection
- Agent reports DRIFT between requirements and code
- Agent does NOT identify test coverage gaps
- No UNCOVERED_REQ detection
- No test impact analysis

**Rationalizations Agent May Use:**
1. "I can see the code changed, but test analysis isn't supported"
2. "You'll need to manually check which tests are affected"
3. "The requirements have drifted from the code"

**Gap Identified:** No test coverage analysis or impact assessment

---

### Scenario 4: User Wants to Know Test Coverage

**Input:** "Which requirements have test coverage and which don't?"

**Current Behavior:**
- Agent cannot answer this question
- No coverage matrix exists
- No UNCOVERED_REQ detection
- No test-to-requirement traceability

**Rationalizations Agent May Use:**
1. "Test coverage tracking isn't part of this skill"
2. "You should use a separate test management tool"
3. "I can only track requirements to code, not to tests"

**Gap Identified:** No test coverage analysis capability

---

### Scenario 5: Orphan Test Code Detection

**Input:** "Find test files that don't have corresponding requirements"

**Current Behavior:**
- Agent cannot detect ORPHAN_TEST
- No test code scanning
- No test specification document to compare against

**Rationalizations Agent May Use:**
1. "I can find orphan production code, but not test code"
2. "Test files aren't tracked in the requirements system"
3. "This would require a separate test management system"

**Gap Identified:** No test deviation detection

---

## Key Findings from Baseline

### Critical Gaps:
1. **No test design workflow** - Agents cannot systematically derive tests from requirements
2. **No three-layer traceability** - Tests are not linked to requirements or code
3. **No test deviation detection** - TEST_DRIFT, UNCOVERED_REQ, STALE_TEST, ORPHAN_TEST not detected
4. **No coverage analysis** - Cannot identify which requirements lack test coverage
5. **No user decision points** - No mechanism to ask user about test updates

### Agent Rationalizations (to Address in SKILL.md):
| Rationalization | Counter to Add |
|-----------------|----------------|
| "Testing is outside scope" | Requirements and testing are naturally related - ISO 29119-4 integration |
| "Use separate testing tool" | Integrated approach prevents traceability gaps |
| "Manually check tests" | Automated test deviation detection |
| "Test coverage isn't tracked" | Three-layer traceability includes test specifications |

### Pressure Points Identified:
1. **Time pressure** - Agent may skip test derivation to save time
2. **Complexity pressure** - Agent may avoid systematic technique selection
3. **Sunk cost** - Agent may resist adding test layer to existing requirements

## Success Criteria for GREEN Phase

After implementing test design feature, agent should:
1. ✅ Derive test conditions using ISO 29119-4 techniques
2. ✅ Select appropriate technique based on requirement type
3. ✅ Generate test specification documents
4. ✅ Maintain three-layer traceability
5. ✅ Detect all 4 test deviation types
6. ✅ Ask user before updating requirements/tests
7. ✅ Provide coverage analysis reports
