# Requirements Document Templates

Use these templates verbatim. Do not add extra sections, columns, or annotations.

---

## Document Header

```markdown
# Software Requirements: <Module Display Name> - Model Layer

## Document Information

| Field | Value |
|-------|-------|
| Document Title | <Module Display Name> Model Layer Requirements |
| Document ID | SWR_<MODULE_ABBR>_MODELS_00001 |
| Version | 1.0 |
| Date | YYYY-MM-DD |
| Project | py-eb-model |
| Module | <Module Display Name> - Model Layer |

---

## Overview

The <Module Display Name> Model Layer provides Python classes representing AUTOSAR <module description> configuration entities extracted from EB Tresos XDM files.

**Implementation:** `src/eb_model/models/<stack>/<module_lower>_xdm.py`

---
```

---

## Entity Requirement (one per container)

```markdown
### SWR_<MODULE_ABBR>_MODELS_<NNNNN> - <Entity Name> Model

The system shall provide an `<EntityName>` model class for <brief description>.

| Field | Multiplicity | Type | Description | Origin |
|-------|--------------|------|-------------|--------|
| fieldName | [min..max] | type | Description with range | AUTOSAR/EB |

**Note:** Multiplicity notation `[min..max]` indicates:
- `[1..1]` — mandatory single instance (may be omitted for brevity)
- `[0..1]` — optional single instance
- `[1..*]` — mandatory list
- `[0..*]` — optional list

**Implementation:** `<module_lower>_xdm.py:<EntityName>`
**Status:** Implemented
**Last Validated:** YYYY-MM-DD

---
```

---

## Choice Container — Grouped Summary (Step 6a)

```markdown
### SWR_<MODULE_ABBR>_MODELS_<NNNNN> - <ChoiceName> Models

The system shall provide choice action model classes.

| Class | Purpose |
|-------|---------|
| ClassName1 | Description |
| ClassName2 | Description |

**Implementation:** `<module_lower>_xdm.py:ClassName1`, `<module_lower>_xdm.py:ClassName2`, etc.
**Status:** Implemented
**Last Validated:** YYYY-MM-DD
```

---

## Choice Container — Per-Variant Requirement (Step 6b)

```markdown
### SWR_<MODULE_ABBR>_MODELS_<NNNNN> - <ClassName1> Model

The system shall provide a `<ClassName1>` model class for <brief description>.

| Field | Type | Description | Origin |
|-------|------|-------------|--------|
| FieldName [min..max] | type | Description | AUTOSAR/EB |

**Implementation:** `<module_lower>_xdm.py:<ClassName1>`
**Status:** Implemented
**Last Validated:** YYYY-MM-DD
```

---

## Root Module Requirement (Step 7 — always last)

```markdown
### SWR_<MODULE_ABBR>_MODELS_<NNNNN> - <ModuleName> Model (Root)

The system shall provide an `<ModuleName>` root model class containing all <module_name> entities.

**Methods:**
- `get<EntityName>List()` - Get all <entity_name_lower>
- ... (one per top-level entity)

**Implementation:** `<module_lower>_xdm.py:<ModuleName>`
**Status:** Implemented
**Last Validated:** YYYY-MM-DD
```

---

## Implementation Notes (Step 8 — always at end)

```markdown
## Implementation Notes

| Requirement ID | Implementation |
|----------------|----------------|
| SWR_<MODULE_ABBR>_MODELS_00001 | <module_lower>_xdm.py:Entity1 |
| SWR_<MODULE_ABBR>_MODELS_00002 | <module_lower>_xdm.py:Entity2 |
| ... | ... |
```

---

## Parser Method Selection Guide

```markdown
## Method Selection Guide

Reference `src/eb_model/parser/core/eb_parser.py` for base methods to handle multiplicity:

| Multiplicity | Field Type | Method | Bullet Format |
|--------------|------------|--------|---------------|
| [1..1] | Value | `read_value()` | `Extract FieldName [1..1] (TYPE, range)` — via `read_value()` |
| [0..1] | Value | `read_optional_value()` | `Extract FieldName [0..1] (TYPE)` — via `read_optional_value()` |
| [1..1] | Choice | `read_choice_value()` | `Extract FieldName [1..1] (ENUMERATION: VAL1/VAL2)` — via `read_choice_value()` |
| [0..1] | Choice | `read_optional_choice_value()` | `Extract FieldName [0..1] (ENUMERATION)` — via `read_optional_choice_value()` |
| [1..1] | Reference | `read_ref_value()` | `Extract FieldName [1..1] (REFERENCE)` — via `read_ref_value()` |
| [0..1] | Reference | `read_optional_ref_value()` | `Extract FieldName [0..1] (REFERENCE)` — via `read_optional_ref_value()` |
| [1..*]/[0..*] | Reference | `read_ref_value_list()` | `Parse FieldName [min..*] (REFERENCE list)` — via `read_ref_value_list()` |
| [0..1] | Container | `find_ctr_tag()` | `Parse FieldName [0..1] sub-container` — via `find_ctr_tag()` |
| [1..*]/[0..*] | Container | `find_ctr_tag_list()` | `Parse FieldName [min..*] sub-containers` — via `find_ctr_tag_list()` |

**Key points:**
- `[1..1]` → mandatory: use `read_*()` methods that raise KeyError if missing
- `[0..1]` → optional: use `read_optional_*()` or `find_ctr_tag()` that return None/default
- `[1..*]` / `[0..*]` → list: use `*_list()` methods for multiple items
```

---

## Parser Layer Document Header

```markdown
# Software Requirements: <Module Display Name> - Parser Layer

## Document Information

| Field | Value |
|-------|-------|
| Document Title | <Module Display Name> Parser Layer Requirements |
| Document ID | SWR_<MODULE_ABBR>_PARSER_00001 |
| Version | 1.0 |
| Date | YYYY-MM-DD |
| Project | py-eb-model |
| Module | <Module Display Name> - Parser Layer |

---

## Overview

The <Module Display Name> Parser Layer provides XDM file parsing for AUTOSAR <module description> configuration data.

**Implementation:** `src/eb_model/parser/<stack>/<module_lower>_xdm_parser.py`

---

## Requirements
```

---

## Parser Entity Requirement (one per container)

```markdown
### SWR_<MODULE_ABBR>_PARSER_<NNNNN> - <Entity Name> Parsing

The parser shall parse <EntityName> elements from XDM.

- Extract FieldName1 [1..1] (INTEGER, min-max) — via `read_value()`
- Extract FieldName2 [1..1] (ENUMERATION: VAL1/VAL2, default VAL1) — via `read_choice_value()`
- Extract FieldName3 [1..1] (BOOLEAN, default true/false) — via `read_value()`
- Extract FieldName4 [1..1] (FLOAT, min-max) — via `read_value()`
- Extract FieldName5 [1..1] (STRING) — via `read_value()`
- Extract FieldName6 [1..1] (REFERENCE) — via `read_ref_value()`
- Parse FieldName7 [1..*] (REFERENCE list) — via `read_ref_value_list()`
- Parse FieldName8 [0..1] sub-container (see SWR_<MODULE_ABBR>_PARSER_XXXXX) — via `find_ctr_tag()`
- Parse FieldName9 [1..*] sub-containers (see SWR_<MODULE_ABBR>_PARSER_XXXXX) — via `find_ctr_tag_list()`
- Raise `ValueError` if required field is missing

**Implementation:** `<module_lower>_xdm_parser.py:read_<entity_name_lower>`
**Status:** Implemented
**Last Validated:** YYYY-MM-DD

---
```

---

## Parser Choice Container Requirement

```markdown
### SWR_<MODULE_ABBR>_PARSER_<NNNNN> - <ChoiceName> Parsing

The parser shall parse <ChoiceName> choice element from XDM.

- Parse <VariantName> variant:
  - Extract FieldName1 [1..1] (TYPE) — via `read_value()` or `read_choice_value()`
  - Extract FieldName2 [1..1] (TYPE) — via `read_value()` or `read_ref_value()`
- Parse <VariantName2> variant:
  - Extract FieldName3 [1..1] (TYPE) — via `read_value()` or `read_ref_value()`
- Raise `ValueError` if choice action is missing or unsupported

**Implementation:** `<module_lower>_xdm_parser.py:read_<entity_name_lower>`
**Status:** Implemented
**Last Validated:** YYYY-MM-DD

---
```

---

## Parser Sub-Container Requirement

```markdown
### SWR_<MODULE_ABBR>_PARSER_<NNNNN> - <SubContainerName> Parsing

The parser shall parse <SubContainerName> sub-container from XDM.

- Extract FieldName1 [1..1] (TYPE, range) — via `read_value()`
- Parse FieldName2 [1..*] (REFERENCE list) — via `read_ref_value_list()`
- Parse FieldName3 [0..1] sub-container (see SWR_<MODULE_ABBR>_PARSER_XXXXX) — via `find_ctr_tag()`

**Implementation:** `<module_lower>_xdm_parser.py:read_<parent_entity_lower>`
**Status:** Implemented
**Last Validated:** YYYY-MM-DD

---
```

---

## Parser Module Validation Requirement (first requirement)

```markdown
### SWR_<MODULE_ABBR>_PARSER_00001 - Module Validation

The parser shall validate that the XDM file contains <Module> module configuration.

- Extract module name from XDM datamodel root element
- Raise `ValueError` if module name is not "<Module>"
- Store namespace map for XPath queries

**Implementation:** `<module_lower>_xdm_parser.py:<Module>XdmParser.parse`
**Status:** Implemented
**Last Validated:** YYYY-MM-DD

---
```

---

## Parser Implementation Notes (always at end)

```markdown
## Implementation Notes

| Requirement ID | Implementation |
|----------------|----------------|
| SWR_<MODULE_ABBR>_PARSER_00001 | <module_lower>_xdm_parser.py:parse |
| SWR_<MODULE_ABBR>_PARSER_00002 | <module_lower>_xdm_parser.py:read_<entity_lower> |
| ... | ... |
```
