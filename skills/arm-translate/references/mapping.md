# Article ↔ source mapping — recorded per corpus

The skill is corpus-agnostic: any Arm document (TRM, Architecture Reference
Manual, SDEN errata) for any core/series can be translated, from a source
corpus at a location given by the run parameters. Each corpus records its own
**article ↔ source-chapter mapping** next to its ledger; a worked example
(cortex) lives in `examples/mapping-cortex.md`.

## What the mapping records

One row per article: article directory, source document + chapter, and the
**evidence** — the figure/table numbers inside the translated page, which carry
the source chapter number (`Figure8-*` ⇒ chapter 8, `TableB3-*` ⇒ appendix B3).
Rows inferred without a numbered figure are marked *(verify)* and confirmed
against the source heading before translating.

- **Source Part/Chapter (when the source has one).** Record the source Part and
  Chapter designators as printed in that document on each mapping row alongside
  the article directory — including the `part-<designator>/` subfolder that
  holds the article; a Part with no numbered Chapter records the Part only.
  Read them from that document's own "Using this manual" / contents, never from
  another corpus, and state the section range when one chapter is split across
  articles. Record the printed page of each Part divider page too — it is the
  source of the Part index page.
- When the numbering does not prove the mapping, match section headings before
  writing.
- Record the source document's doc ID and revision per series, and note when a
  legacy page was translated from an older revision (chapter numbers shifted) —
  confirm a chapter by its heading and table text, never by a legacy filename,
  and never rename existing figure files.
- Keep a coverage backlog list (chapters not yet translated, in chapter order).

## Naming

- Article directory = lower_snake_case topic name (`memory_protection_unit`,
  `system_control`), not the chapter number.
- One source chapter per article; split a chapter only when the user asks, and
  state the split in the PR.
- First level under the target root is the source document series (one
  lower_snake_case folder per document, e.g. the TRM series, the ARM series);
  second level is the topic — or, when the source document has a Part ->
  Chapter hierarchy, `part-<designator>/` with the topic one level deeper
  (`<document>/part-<designator>/<topic>/index.md`). Never file two documents
  in one folder. Propose the directory name when a topic straddles two chapters
  or could be split, and propose a new document folder name (matched to the
  existing series) when opening a source document that has no series yet.
- When a flat series is migrated into Part subfolders, record the old -> new
  path on each mapping row and keep the old URLs alive with `redirect_maps`.
- A topic present in both a TRM and an architecture manual (e.g. exceptions)
  takes the architectural source for behaviour and cites TRM differences
  inline. A merged article stays whole under its implementation document.
