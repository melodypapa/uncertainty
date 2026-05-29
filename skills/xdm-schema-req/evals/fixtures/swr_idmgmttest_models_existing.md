# Software Requirements: IDManagementTest - Model Layer

## Document Information

| Field | Value |
|-------|-------|
| Document Title | IDManagementTest Model Layer Requirements |
| Document ID | SWR_IDMGMTTEST_MODELS_00001 |
| Version | 1.0 |
| Date | 2026-05-28 |
| Project | py-eb-model |
| Module | IDManagementTest - Model Layer |

---

## Overview

The IDManagementTest Model Layer provides Python classes representing AUTOSAR IDManagementTest configuration entities extracted from EB Tresos XDM files.

**Implementation:** `src/eb_model/models/core/idmgmttest_xdm.py`

---

### SWR_IDMGMTTEST_MODELS_00001 - ExistingEntity Model

The system shall provide an `ExistingEntity` model class for existing entity configuration.

| Field | Type | Description | Origin |
|-------|------|-------------|--------|
| ExistingField | int | Existing field in existing entity | AUTOSAR |

**Implementation:** `idmgmttest_xdm.py:ExistingEntity`
**Status:** Implemented
**Last Validated:** 2026-05-28

---

### SWR_IDMGMTTEST_MODELS_00002 - IDManagementTest Model (Root)

The system shall provide a `IDManagementTest` model class for accessing all IDManagementTest configuration entities.

**Methods:**
- `getExistingEntityList()` — Returns list of ExistingEntity instances

**Implementation:** `idmgmttest_xdm.py:IDManagementTest`
**Status:** Implemented
**Last Validated:** 2026-05-28

---

## Traceability Matrix

| Requirement ID | Implementation | Test Case ID |
|----------------|----------------|--------------|
| SWR_IDMGMTTEST_MODELS_00001 | idmgmttest_xdm.py:ExistingEntity | UTS_IDMGMTTEST_MODEL_00001 |
| SWR_IDMGMTTEST_MODELS_00002 | idmgmttest_xdm.py:IDManagementTest | UTS_IDMGMTTEST_MODEL_00002 |
