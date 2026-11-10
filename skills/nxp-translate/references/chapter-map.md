# Chapter mapping — derived per document

The skill is document-agnostic: it works with any chaptered, NXP-published PDF.
Nothing about a specific document (title, page count, chapter count, outline
shape, storage location) is hardcoded — each target corpus derives its own
chapter map on the first run and records it **next to the articles**. A worked
example (S32G3) lives in `examples/chapter-map-s32g3.md`.

## Inputs of a run

| Parameter | Meaning |
| --- | --- |
| **Source PDF** | the NXP-published document to translate from (any path; LFS-tracked files must be materialised) |
| **Target root** | the directory the articles are written to (`<target>/chNN_<slug>/index.md`) |

Both come from the requester or from the corpus's own ledger on resume — never
from this skill.

## Deriving the map

`scripts/extract_chapter.py <pdf> <chapter> --sections-only` reports the
chapter inventory for the requested chapter; for the full inventory use
`doc.get_toc()` directly (a one-off census script is fine). Rules:

- **One numbered chapter = one article** at
  `<target>/chNN_<slug>/index.md`. Never split a chapter across files, never
  merge two chapters, never append an article at the end of its group.
- A chapter is an outline entry titled `<N> Title` (whitespace right after the
  number — this excludes section entries `N.M …`). Chapters may sit at any
  outline level and may mix levels across one document; `parse_chapters()`
  accepts all such shapes and fails loudly unless the numbers are contiguous.
- Zero-pad `chNN` to the chapter count's width (81 chapters → `ch03`; 111 →
  `ch005`) so lexical file order equals chapter order.
- Chapter page range = outline start → (next chapter's start − 1); the last
  chapter ends before the first trailing-matter entry (appendices, release
  notes, legal information).
- **Droppable chrome** (never an article): cover, `Contents`, appendices,
  release notes, legal information, and the unnumbered **group headers**.
  Group headers are used to group the landing page's `## 文章` list — a group
  header without a `Chapter NN-NN:`-style prefix (e.g. `Debug`) is still a
  group header, not a chapter.

Record in the map, per chapter: number, source title, PDF page range, article
directory. Keep the derivation script snippet in the map file so the inventory
can be regenerated when a new revision lands — chapter numbers, page ranges and
global figure/table numbers all move between revisions. Assert contiguity
before consuming a regenerated inventory.

## Slug rule

`slugify()` in `scripts/extract_chapter.py`: lowercase, every run of
non-alphanumeric characters → `_`, collapse repeats, trim. Identifier
underscores survive (`SRC_0` → `src_0`, `SELFTEST_GPR_TOP` →
`selftest_gpr_top`); hyphens and slashes become separators
(`Network-on-Chip (NoC)` → `network_on_chip_noc`).

## Progress ledger

Full-document runs span many sessions. On the **first** run create a persistent
ledger **inside the target root** so a resumed session never re-asks scope
decisions:

```
<target>/TODO.md             # one row per chapter: ❌ missing / ⚠️ partial / ✅ complete
<target>/sync-todo/index.md  # batch order + resume rule (first unfinished row in chapter order)
<target>/sync-todo/Group-<group>.md  # one row per chapter with a sub-checklist
```

If the target root lives inside an MkDocs `docs/` tree, add the ledger paths to
`exclude_docs` in that site's `mkdocs.yml` — links to chapter pages not yet
written would otherwise emit `--strict` WARNINGs. If the target is outside any
site (offline mode), skip that step. Ledger files are written in English;
quoted Chinese strings only when they name an article heading. Tick a row only
after its commit exists. This map file is the chapter inventory; the ledger is
the **status** record.
